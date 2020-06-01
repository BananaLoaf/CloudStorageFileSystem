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


class Profile:
    SERVICE_NAME: str = "default-service"
    SERVICE_LABEL: str = "Default Service"

    config: dict

    def __init__(self, app_path: Path, profile_name: str):
        if "/" in profile_name:
            raise ProfileInitializationError("'/' in profile name is not allowed!")
        if "None" == profile_name:
            raise ProfileInitializationError("Profile name can not be 'None'!")

        self.profile_path = app_path.joinpath(self.SERVICE_NAME).joinpath(profile_name)
        self.profile_name = self.profile_path.stem
        self.cache_path = self.profile_path.joinpath("cache")

    # Config management
    @property
    def default_config(self) -> dict:
        raise NotImplementedError

    @property
    def schema(self) -> dict:
        raise NotImplementedError

    def save_config(self):
        """Validating config and saving it"""
        Validator(self.schema).validate(self.config)
        with self.profile_path.joinpath("config.json").open("w") as file:
            json.dump(self.config, file, indent=4)

    def load_config(self):
        """Loading config and validating it"""
        with self.profile_path.joinpath("config.json").open("r") as file:
            self.config = json.load(file)
        Validator(self.schema).validate(self.config)

    # Profile management
    @property
    def exists(self):
        return self.profile_path.exists()

    def create(self):
        if self.exists:
            raise ProfileCreationError(f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' already exists")

        self.config = self.default_config
        self._create()

        self.profile_path.mkdir(parents=True)
        self.cache_path.mkdir()
        self.save_config()

    def _create(self):
        """
        Called after config initialization for user input, authentication, saving credentials, adding something to config, etc.
        Raising ProfileCreationError(message) would delete the profile and log the message
        """
        raise NotImplementedError

    def remove(self, cleanup: bool = False):
        """Clean up and remove the files"""
        if cleanup:
            self._remove()
        shutil.rmtree(str(self.profile_path), ignore_errors=True)

    def _remove(self):
        """Called for removing credentials, etc"""
        raise NotImplementedError

    def start(self, verbose: bool, read_only: bool):
        if not self.exists:
            raise ProfileStartingError(f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' does not exist")
        configure_logger(verbose=verbose, service_label=self.SERVICE_LABEL, profile_name=self.profile_name)

        self.load_config()
        ops, mountpoint, ths = self._start()
        self.check_mountpoint(mountpoint)

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
        FUSE(ops, str(mountpoint), foreground=True, intr=True, ro=read_only, uid=os.getuid(), gid=os.getgid())

    def check_mountpoint(self, mountpoint: Path):
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
            raise ProfileStartingError(f"{err}, unmount manually with \"fusermount -u '{mountpoint}'\"")

    def _start(self) -> Tuple[CustomOperations, Path, List[ThreadHandler]]:
        """
        Load credentials, init whatever is needed
        Returns CustomOperations, mountpoint, list of thread handlers
        """
        raise NotImplementedError
