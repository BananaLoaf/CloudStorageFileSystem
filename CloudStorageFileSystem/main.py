from argparse import ArgumentParser
import sys

from pathlib import Path

from CloudStorageFileSystem import NAME, __version__
from CloudStorageFileSystem.service import SERVICES
from CloudStorageFileSystem.utils.exceptions import *
from CloudStorageFileSystem.utils.servicesupervisor import ServiceSupervisor
from CloudStorageFileSystem.logger import LOGGER, configure_logger


PROFILE_NAME = "PROFILE_NAME"
SERVICE_NAME = "SERVICE_NAME"
VERBOSE = "VERBOSE"


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

        start = subparser.add_parser("start")
        start.add_argument(SERVICE_NAME, type=str, choices=list(SERVICES.keys()), help="")  # TODO help
        start.add_argument(PROFILE_NAME, type=str, help="")  # TODO help
        start.set_defaults(func=self.start)

    def __call__(self):
        self.app_path.mkdir(exist_ok=True, parents=True)
        args = self.parser.parse_args()

        if args.version:
            print(f"{NAME} v{__version__}")
        else:
            configure_logger(verbose=getattr(args, VERBOSE))
            args.func(args)

    def get_ss(self, service_name: str, profile_name: str) -> ServiceSupervisor:
        try:
            return SERVICES[service_name](app_path=self.app_path, profile_name=profile_name)
        except ServiceCreationError as err:
            LOGGER.error(err)
            sys.exit()

    @property
    def profiles(self):
        for service_path in self.app_path.glob("*"):
            for profile_path in service_path.glob("*"):
                ss = self.get_ss(service_name=service_path.stem, profile_name=profile_path.stem)
                yield ss, profile_path.stem

    def list_services(self, args):
        for service in SERVICES.keys():
            print(service)

    def list_profiles(self, args):
        for ss, profile in self.profiles:
            print(f"{ss.SERVICE_LABEL}: '{ss.SERVICE_NAME}' - '{profile}'")

    def create_profile(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)

        ss = self.get_ss(service_name=service_name, profile_name=profile_name)
        try:
            ss.create_profile()
            LOGGER.info(f"Created profile '{service_name}' - '{profile_name}' in {ss.profile_path}")
        except ProfileCreationError as err:
            LOGGER.error(err)
            ss.remove_profile()
            sys.exit()

    def start(self, args):
        service_name = getattr(args, SERVICE_NAME)
        profile_name = getattr(args, PROFILE_NAME)
        verbose = getattr(args, VERBOSE)

        ss = self.get_ss(service_name=service_name, profile_name=profile_name)
        try:
            ss.start(verbose=verbose)
        except ProfileStartingError as err:
            LOGGER.error(err)
            sys.exit()


def main():
    starter = Starter()
    starter()


if __name__ == '__main__':
    main()
