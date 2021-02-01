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

    def __init__(self):
        self.parser = ArgumentParser()
        self.parser.set_defaults(func=lambda args: self.parser.print_help())
        subparser = self.parser.add_subparsers()

        self.parser.add_argument("--version", action="store_true", help="Application version", dest=VERSION)
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logs", dest=VERBOSE)

        list_services = subparser.add_parser("list-services")
        list_services.set_defaults(func=self.list_services)

        list_profiles = subparser.add_parser("list-profiles")
        list_profiles.set_defaults(func=self.list_profiles)

        create_profile = subparser.add_parser("create-profile")
        create_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()))
        create_profile.add_argument(PROFILE_NAME, type=str, help="Desired profile name")
        create_profile.set_defaults(func=self.create_profile)

        remove_profile = subparser.add_parser("remove-profile")
        remove_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()))
        remove_profile.add_argument(PROFILE_NAME, type=str, help="Name of profile to remove")
        remove_profile.set_defaults(func=self.remove_profile)

        start_profile = subparser.add_parser("start-profile")
        start_profile.add_argument("-ro", "--read-only", action="store_true", dest=READ_ONLY)
        start_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")
        start_profile.add_argument(PROFILE_NAME, type=str, help="Profile to start")
        start_profile.set_defaults(func=self.start_profile)

    def __call__(self):
        self.app_path.mkdir(exist_ok=True, parents=True)
        args = self.parser.parse_args()

        if getattr(args, VERSION):
            print(f"{PACKAGE_NAME} v{__version__}")
        else:
            configure_logger(verbose=getattr(args, VERBOSE))
            args.func(args)

    # Helpers
    def get_profile(self, service_name: str, profile_name: str) -> Profile:
        try:
            return SERVICES[service_name](app_path=self.app_path, profile_name=profile_name)
        except ProfileInitializationError as err:
            LOGGER.error(err)
            sys.exit()

    def profile_exists(self, profile: Profile):
        return self.app_path.joinpath(profile.service_name).joinpath(profile.profile_name).exists()

    # Commands
    def list_services(self, args):
        for service in SERVICES.keys():
            print(service)

    def list_profiles(self, args):
        print("--------------------------------")
        for service in self.app_path.glob("*"):
            for profile in service.glob("*"):
                service_name_line = f"Service name: '{service.name}'"
                profile_name_line = f"Profile name: '{profile.name}'"

                version_file = profile.joinpath('VERSION')
                if version_file.exists():
                    with version_file.open("r") as file:
                        version_line = f"Version: v{file.read()}"
                else:
                    version_line = f"Version: ???"

                # Is service valid
                if service.name in SERVICES.keys():
                    profile = self.get_profile(service_name=service.name,
                                               profile_name=profile.name)
                    version_line += f" (latest version: v{profile.version})"

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
