import shutil
from threading import Thread
from typing import Tuple, List
import os

from pathlib import Path
import pyfuse3
import trio
import yaml
import yamale

from CloudStorageFileSystem.utils.exceptions import *
from CloudStorageFileSystem.logger import configure_logger, LOGGER


class ThreadHandler:
    def __init__(self, t: Thread, join: bool):
        self.thread = t
        self.join = join


class Profile:
    service_name = "default-service"
    service_label = "Default Service"
    version = "1.0"

    config: dict

    def __init__(self, app_path: Path, profile_name: str):
        """Raise ProfileInitializationError in case of anything"""
        if "/" in profile_name:
            raise ProfileInitializationError("'/' in profile name is not allowed!")

        self._profile_name = profile_name

        self.profile_path = app_path.joinpath(self.service_name).joinpath(profile_name)
        self.cache_path = self.profile_path.joinpath("cache")

    def __repr__(self):
        return f"'{self.service_name}' - '{self.profile_name}'"

    ################################################################
    @property
    def profile_name(self) -> str:
        return self._profile_name

    ################################################################
    # Config management
    @property
    def schema(self) -> dict:
        """Scheme for yamale validator"""
        raise NotImplementedError

    @property
    def default_config(self) -> dict:
        """Default yaml config"""
        raise NotImplementedError

    def _save_config(self):
        """Validate config and save it"""
        yamale.validate(schema=yamale.make_schema(content=yaml.dump(self.schema)),
                        data=yamale.make_data(content=yaml.dump(self.config)))
        with self.profile_path.joinpath("config.json").open("w") as file:
            yaml.dump(self.config, file)

    def _load_config(self):
        """Load config and validate it"""
        with self.profile_path.joinpath("config.json").open("r") as file:
            self.config = yaml.load(file, Loader=yaml.SafeLoader)
        yamale.validate(schema=yamale.make_schema(content=yaml.dump(self.schema)),
                        data=yamale.make_data(content=yaml.dump(self.config)))

    ################################################################
    # Profile management
    def create(self):
        self.profile_path.mkdir(parents=True)
        self.cache_path.mkdir()

        with self.profile_path.joinpath("VERSION").open("w") as file:
            file.write(self.version)

        self.config = self.default_config
        self._create()

        self._save_config()

    def _create(self):
        """
        Called after config initialization for user input, authentication, saving credentials, adding something to config, etc.
        Raising ProfileCreationError(message) would log the message and call self.remove()
        """
        raise NotImplementedError

    def remove(self):
        """Clean up and remove the files"""
        self._remove()
        shutil.rmtree(str(self.profile_path), ignore_errors=True)

    def _remove(self):
        """
        Called for removing credentials, etc
        Raise ProfileRemovalError in case of anything
        """
        raise NotImplementedError

    def start(self, verbose: bool, read_only: bool):
        configure_logger(verbose=verbose, service_label=self.service_label, profile_name=self.profile_name)

        self._load_config()
        ops, mountpoint, ths = self._start()
        self.check_mountpoint(mountpoint)

        ################################################################
        # Start all threads
        for th in ths:
            th.thread.start()
        # Join threads before mounting, if needed
        for th in ths:
            if th.join:
                th.thread.join()

        ################################################################
        # Mount
        options = set(pyfuse3.default_options)
        options.add(f"fsname={ops.__class__.__name__}")
        options.discard("default_permissions")
        options.add("auto_unmount")
        if read_only:
            options.add("ro")
        else:
            options.add("rw")

        pyfuse3.init(ops, str(mountpoint), options)
        try:
            trio.run(pyfuse3.main)
        except:
            pyfuse3.close(unmount=True)
            raise

    def _start(self) -> Tuple[pyfuse3.Operations, Path, List[ThreadHandler]]:
        """
        Load credentials, init whatever is needed
        Returns CustomOperations, mountpoint, list of thread handlers
        Raise ProfileStartingError in case of anything
        """
        raise NotImplementedError

    def check_mountpoint(self, mountpoint: Path):
        try:
            if not mountpoint.exists():
                LOGGER.info(f"Mountpoint '{mountpoint}' does not exist, creating...")
                mountpoint.mkdir(parents=True)

            assert mountpoint.is_dir(), f"Mountpoint '{mountpoint}' is not a directory"
            assert mountpoint.absolute(), f"Mountpoint '{mountpoint}' must be absolute"
            assert len(list(mountpoint.iterdir())) == 0, f"Mountpoint '{mountpoint}' is not empty"
            try:
                assert not mountpoint.is_mount(), f"Mountpoint '{mountpoint}' is already a mountpoint"
            except AttributeError:
                assert not os.path.ismount(str(mountpoint)), f"Mountpoint '{mountpoint}' is already a mountpoint"

        except AssertionError as err:
            raise ProfileStartingError(err)
        except OSError as err:
            raise ProfileStartingError(f"{err}, unmount manually with \"fusermount -u '{mountpoint}'\"")
