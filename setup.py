from setuptools import setup, find_packages

from CloudStorageFileSystem import PACKAGE_NAME, __version__


with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()

setup(name=PACKAGE_NAME,
      version=__version__,
      install_requires=[],  # TODO requirements
      packages=find_packages(),
      entry_points={
          "console_scripts": [
              "csfs = CloudStorageFileSystem.main:main"
          ]
      },

      # Metadata for PyPi
      author="BananaLoaf",
      author_email="bananaloaf@protonmail.com",
      # maintainer="BananaLoaf",
      # maintainer_email="bananaloaf@protonmail.com",
      license="MIT",

      description="CloudStorageFileSystem",
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      keywords=[],

      url="https://github.com/BananaLoaf/CloudStorageFileSystem",
      # download_url=None,
      # project_urls={
      #     "Lord and Saviour": "https://stackoverflow.com/"
      # },

      # https://pypi.org/classifiers/
      # classifiers=[
      #     "Development Status :: 5 - Production/Stable",
      #     "Programming Language :: Python :: 3",
      #     "License :: OSI Approved :: MIT License",
      #     "Operating System :: OS Independent"
      # ]
      )
