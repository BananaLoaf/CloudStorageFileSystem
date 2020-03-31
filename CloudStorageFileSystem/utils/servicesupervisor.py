import json

from pathlib import Path

from CloudStorageFileSystem.utils.validator import Validator
from CloudStorageFileSystem.logger import LOGGER, configure_logger


class ServiceSupervisor:
    SERVICE_NAME: str = "default-service"
    SERVICE_LABEL: str = "Default Service"

    config: dict = {}

    def __init__(self, app_path: Path, profile_name: str):
        assert "/" not in profile_name, "Slash in profile name is not allowed!"
        assert "None" != profile_name, "Profile name can not be 'None'!"

        self.service_path = app_path.joinpath(self.SERVICE_NAME)
        self.profile_path = self.service_path.joinpath(profile_name)
        self.cache_path = self.profile_path.joinpath("cache")

    def save_config(self):
        Validator(self.schema).validate(self.config)
        with self.profile_path.joinpath("config.json").open("w") as file:
            json.dump(self.config, file, indent=4)

    @property
    def profile_name(self):
        return self.profile_path.stem

    @property
    def default_config(self) -> dict:
        raise NotImplementedError

    @property
    def schema(self) -> dict:
        raise NotImplementedError

    def exists(self):
        return self.profile_path.exists()

    def create_profile(self):
        assert not self.exists(), f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' already exists"

        self.service_path.mkdir(exist_ok=True)
        self.profile_path.mkdir()
        self.cache_path.mkdir(exist_ok=True)

        self._create_profile()

        self.config.update(self.default_config)
        self.save_config()

    def _create_profile(self):
        """User input, authentication, save credentials, etc"""
        raise NotImplementedError

    def start(self, verbose: bool):
        assert self.exists(), f"Profile '{self.SERVICE_NAME}' - '{self.profile_name}' does not exist"
        configure_logger(verbose=verbose, service_label=self.SERVICE_LABEL, profile_name=self.profile_name)
        self._preload()

        # TODO get threads
        # TODO start threads
        # TODO get FS, start FS

    def _preload(self):
        """Load credentials, etc"""
        raise NotImplementedError
