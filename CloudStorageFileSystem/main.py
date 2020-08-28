from argparse import ArgumentParser
import sys
from typing import List
import json

from pathlib import Path

from CloudStorageFileSystem import PACKAGE_NAME, __version__
from CloudStorageFileSystem.service import SERVICES
from CloudStorageFileSystem.utils.exceptions import *
from CloudStorageFileSystem.utils.profile import Profile
from CloudStorageFileSystem.logger import LOGGER, configure_logger


PROFILE_NAME = "PROFILE_NAME"
SERVICE_NAME = "SERVICE_NAME"
VERSION = "VERSION"
VERBOSE = "VERBOSE"
READ_ONLY = "READ_ONLY"


def ask(message: str) -> bool:
    while True:
        resp = input(f"{message} [y/n] ")
        if resp == "y":
            return True
        elif resp == "n":
            return False


class Starter:
    app_path: Path = Path.home().joinpath(".csfs")
    profile_reg = app_path.joinpath("profiles.json")
    profile_dicts: List[dict]

    def __init__(self):
        self.parser = ArgumentParser()  # TODO help
        self.parser.set_defaults(func=lambda args: self.parser.print_help())
        subparser = self.parser.add_subparsers()

        self.parser.add_argument("--version", action="store_true", help="Application version", dest=VERSION)
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logs", dest=VERBOSE)

        list_services = subparser.add_parser("list-services")
        list_services.set_defaults(func=self.list_services)

        list_profiles = subparser.add_parser("list-profiles")
        list_profiles.set_defaults(func=self.list_profiles)

        create_profile = subparser.add_parser("create-profile")
        create_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        create_profile.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        create_profile.set_defaults(func=self.create_profile)

        remove_profile = subparser.add_parser("remove-profile")
        remove_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        remove_profile.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        remove_profile.set_defaults(func=self.remove_profile)

        start_profile = subparser.add_parser("start-profile")
        start_profile.add_argument("-ro", "--read-only", action="store_true", help="", dest=READ_ONLY)  # TODO help
        start_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        start_profile.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        start_profile.set_defaults(func=self.start_profile)

    def __call__(self):
        self.app_path.mkdir(exist_ok=True, parents=True)
        args = self.parser.parse_args()

        if getattr(args, VERSION):
            print(f"{PACKAGE_NAME} v{__version__}")
        else:
            configure_logger(verbose=getattr(args, VERBOSE))
            self._load_profiles()
            args.func(args)

    # Helpers
    def get_profile(self, service_name: str, profile_name: str) -> Profile:
        try:
            return SERVICES[service_name](app_path=self.app_path, profile_name=profile_name)
        except ProfileInitializationError as err:
            LOGGER.error(err)
            sys.exit()

    def profile2dict(self, profile: Profile) -> dict:
        return {SERVICE_NAME: profile.SERVICE_NAME,
                PROFILE_NAME: profile.PROFILE_NAME,
                VERSION: profile.VERSION}

    def _load_profiles(self):
        if self.profile_reg.exists():
            with self.profile_reg.open("r") as file:
                self.profile_dicts = json.load(file)
        else:
            self.profile_dicts = []

    def _save_profiles(self):
        with self.profile_reg.open("w") as file:
            json.dump(self.profile_dicts, file, indent=4)

    def profile_exists(self, profile: Profile):
        for profile_dict in self.profile_dicts:
            if profile_dict[SERVICE_NAME] == profile.SERVICE_NAME and profile_dict[PROFILE_NAME] == profile.PROFILE_NAME:
                return True
        return False

    # Commands
    def list_services(self, args):
        for service in SERVICES.keys():
            print(service)

    def list_profiles(self, args):
        print("--------------------------------")
        for profile_dict in self.profile_dicts:
            valid_service = profile_dict[SERVICE_NAME] in SERVICES.keys()

            service_name_line = f"Service name: '{profile_dict[SERVICE_NAME]}'"
            profile_name_line = f"Profile name: '{profile_dict[PROFILE_NAME]}'"
            version_line = f"Version: v{profile_dict[VERSION]}"

            if valid_service:
                profile = self.get_profile(service_name=profile_dict[SERVICE_NAME],
                                           profile_name=profile_dict[PROFILE_NAME])
                version_line += f" (latest version: v{profile.VERSION})"

            else:
                service_name_line += " (invalid service!)"
                version_line += " (latest version: ???)"

            print(service_name_line)
            print(profile_name_line)
            print(version_line)
            print("--------------------------------")

    def create_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)

        profile = self.get_profile(service_name=service_name, profile_name=profile_name)
        try:
            if self.profile_exists(profile):
                raise ProfileExistsError(f"Profile {profile} already exists")

            profile.create()
            self.profile_dicts.append(self.profile2dict(profile))
            self._save_profiles()
            LOGGER.info(f"Created profile {profile}")

        except ProfileCreationError as err:
            LOGGER.error(err)
            profile.remove()

        except ProfileExistsError as err:
            LOGGER.error(err)

    def remove_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)

        profile = self.get_profile(service_name=service_name, profile_name=profile_name)
        try:
            if not self.profile_exists(profile):
                raise ProfileNotExistsError(f"Profile {profile} does not exist")

            if ask(f"Are you sure you want to remove profile {profile}?"):
                profile.remove()
                # TODO remove from dict
                LOGGER.info(f"Removed profile {profile}")

        except ProfileRemovalError as err:
            LOGGER.error(err)

        except ProfileNotExistsError as err:
            LOGGER.error(err)

    def start_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)
        verbose = getattr(args, VERBOSE)
        read_only = getattr(args, READ_ONLY)

        profile = self.get_profile(service_name=service_name, profile_name=profile_name)
        try:
            if not self.profile_exists(profile):
                raise ProfileNotExistsError(f"Profile {profile} does not exist")

            profile.start(verbose=verbose, read_only=read_only)

        except ProfileStartingError as err:
            LOGGER.error(err)

        except ProfileNotExistsError as err:
            LOGGER.error(err)


def main():
    starter = Starter()
    starter()


if __name__ == '__main__':
    main()
