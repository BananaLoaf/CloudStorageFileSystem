import json
import shutil
from threading import Thread
from typing import Tuple, List
import os

from pathlib import Path
from refuse.high import FUSE

from CloudStorageFileSystem.utils.validator import Validator
from CloudStorageFileSystem.utils.operations import CustomOperations
from CloudStorageFileSystem.utils.exceptions import *
from CloudStorageFileSystem.logger import configure_logger, LOGGER


class ThreadHandler:
    def __init__(self, t: Thread, if_join: bool):
        self.thread = t
        self.if_join = if_join


class ServiceSupervisor:
    SERVICE_NAME: str = "default-service"
    SERVICE_LABEL: str = "Default Service"

    config: dict

    def __init__(self, app_path: Path, profile_name: str):
        if "/" in profile_name:
            raise ServiceCreationError("Slash in profile name is not allowed!")
        if "None" == profile_name:
            raise ServiceCreationError("Profile name can not be 'None'!")

        self.service_path = app_path.joinpath(self.SERVICE_NAME)
        self.profile_path = self.service_path.joinpath(profile_name)
        self.cache_path = self.profile_path.joinpath("cache")

    def save_config(self):
        Validator(self.schema).validate(self.config)
        with self.profile_path.joinpath("config.json").open("w") as file:
            json.dump(self.config, file, indent=4)

    def load_config(self):
        with self.profile_path.joinpath("config.json").open("r") as file:
            self.config = json.load(file)
        Validator(self.schema).validate(self.config)

    @property
    def profile_name(self):
        return self.profile_path.stem

    @property
    def default_config(self) -> dict:
        raise NotImplementedError

    @property
    def schema(self) -> dict:
        raise NotImplementedError

    @property
    def exists(self):
        return self.profile_path.exists()

    def create_profile(self):
        if self.exists:
            raise ProfileCreationError(f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' already exists")

        self.service_path.mkdir(exist_ok=True)
        self.profile_path.mkdir()
        self.cache_path.mkdir(exist_ok=True)

        self._create_profile()

        self.config = self.default_config
        self.save_config()

    def _create_profile(self):
        """User input, authentication, save credentials, etc.
        raising ProfileCreationError(message) would delete the profile and log the message
        """
        raise NotImplementedError

    def remove_profile(self):
        shutil.rmtree(str(self.profile_path), ignore_errors=True)

    def start(self, verbose: bool):
        if not self.exists:
            raise ProfileStartingError(f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' does not exist")
        configure_logger(verbose=verbose, service_label=self.SERVICE_LABEL, profile_name=self.profile_name)

        self.load_config()
        ops, mountpoint, ths = self._start()

        ################################################################
        # Check mountpoint
        try:
            if not mountpoint.exists():
                LOGGER.info(f"Mountpoint '{mountpoint}' does not exist, creating...")
                mountpoint.mkdir(parents=True)

            assert mountpoint.is_dir(), f"Mountpoint '{mountpoint}' is not a directory"
            assert len(list(mountpoint.iterdir())) == 0, f"Mountpoint '{mountpoint}' is not empty"
            try:
                assert not mountpoint.is_mount(), f"Mountpoint '{mountpoint}' is already a mountpoint"
            except AttributeError:
                assert not os.path.ismount(str(mountpoint)), f"Mountpoint '{mountpoint}' is already a mountpoint"

        except AssertionError as err:
            raise ProfileStartingError(err)
        except OSError as err:
            raise ProfileStartingError(f"{err}, To fix this run \"fusermount -u '{mountpoint}'\"")

        ################################################################
        # Start all threads
        for th in ths:
            th.thread.start()
        # Join threads before mounting, if needed
        for th in ths:
            if th.if_join:
                th.thread.join()

        ################################################################
        # Mount
        FUSE(ops, str(mountpoint), foreground=True, intr=True, uid=os.getuid(), gid=os.getgid())

    def _start(self) -> Tuple[CustomOperations, Path, List[ThreadHandler]]:
        """Load credentials, init whatever is needed"""
        raise NotImplementedError
