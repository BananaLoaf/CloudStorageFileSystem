from setuptools import find_packages

__version__ = "1.0"


PAYLOAD = {
    "name": "CloudStorageFileSystem",
    "version": __version__,
    "install_requires": [],
    "packages": find_packages(),
    "entry_points": {
        "console_scripts": [
            "csfs = CloudStorageFileSystem.main:main"
        ]
    },

    # Metadata for PyPi
    "author": "BananaLoaf",
    "author_email": "bananaloaf@protonmail.com",
    "maintainer": "BananaLoaf",
    "maintainer_email": "bananaloaf@protonmail.com",
    "license": "MIT",

    "description": "CloudStorageFileSystem",
    "long_description": None,
    "long_description_content_type": "text/markdown",
    "keywords": [],

    "url": "https://github.com/BananaLoaf/CloudStorageFileSystem",
    # "download_url": None,
    # "classifiers": [
    #     "Development Status :: 5 - Production/Stable",
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent"
    # ]
}
