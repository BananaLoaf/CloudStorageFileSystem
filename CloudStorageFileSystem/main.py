from argparse import ArgumentParser
import sys

from pathlib import Path

from CloudStorageFileSystem import PACKAGE_NAME, __version__
from CloudStorageFileSystem.service import SERVICES
from CloudStorageFileSystem.utils.exceptions import *
from CloudStorageFileSystem.utils.profile import Profile
from CloudStorageFileSystem.logger import LOGGER, configure_logger


PROFILE_NAME = "PROFILE_NAME"
SERVICE_NAME = "SERVICE_NAME"
VERBOSE = "VERBOSE"
READ_ONLY = "READ_ONLY"


class Starter:
    app_path: Path = Path.home().joinpath(".csfs")

    def __init__(self):
        self.parser = ArgumentParser()  # TODO help
        self.parser.set_defaults(func=lambda args: self.parser.print_help())
        subparser = self.parser.add_subparsers()

        self.parser.add_argument("--version", action="store_true", help="Application version")
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logs", dest=VERBOSE)

        list_services = subparser.add_parser("list-services")
        list_services.set_defaults(func=self.list_services)

        list_profiles = subparser.add_parser("list-profiles")
        list_profiles.set_defaults(func=self.list_profiles)

        create_profile = subparser.add_parser("create-profile")
        create_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        create_profile.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        create_profile.set_defaults(func=self.create_profile)

        # TODO remove-profile

        start_profile = subparser.add_parser("start-profile")
        self.parser.add_argument("-ro", "--read-only", action="store_true", help="", dest=READ_ONLY)  # TODO help
        start_profile.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        start_profile.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        start_profile.set_defaults(func=self.start_profile)

    def __call__(self):
        self.app_path.mkdir(exist_ok=True, parents=True)
        args = self.parser.parse_args()

        if args.version:
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

    # Commands
    def list_services(self, args):
        for service in SERVICES.keys():
            print(service)

    def list_profiles(self, args):
        print("--------------------------------")
        for service_path in self.app_path.glob("*"):
            for profile_path in service_path.glob("*"):
                profile = self.get_profile(service_name=service_path.stem, profile_name=profile_path.stem)
                print(f"Service label: '{profile.SERVICE_LABEL}'\n"
                      f"Service name: '{profile.SERVICE_NAME}'\n"
                      f"Profile name: '{profile.profile_name}'")
                print("--------------------------------")

    def create_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)

        profile = self.get_profile(service_name=service_name, profile_name=profile_name)
        try:
            profile.create()
            LOGGER.info(f"Created profile '{service_name}' - '{profile_name}' in {profile.profile_path}")
        except ProfileCreationError as err:
            LOGGER.error(err)
            profile.remove()

    def remove_profile(self, args):
        pass  # TODO

    def start_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)
        verbose = getattr(args, VERBOSE)
        read_only = getattr(args, READ_ONLY)

        ss = self.get_profile(service_name=service_name, profile_name=profile_name)
        try:
            ss.start(verbose=verbose, read_only=read_only)
        except ProfileStartingError as err:
            LOGGER.error(err)
            sys.exit()


def main():
    starter = Starter()
    starter()


if __name__ == '__main__':
    main()
