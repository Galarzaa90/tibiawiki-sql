import os
import re

from setuptools import setup, find_packages


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(
    name='tibiawikisql',
    version=get_version("tibiawikisql"),
    author='Galarzaa90',
    author_email="allan.galarza@gmail.com",
    url='https://github.com/Galarzaa90/tibiawiki-sql',
    license='Apache 2.0',
    install_requires=requirements,
    description="Python script that generates a SQLite database from TibiaWiki articles",
    long_description=readme,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tibiawiki = tibiawikisql.tibiawikisql:main',
        ],
    },
    include_package_data=True
)
