import os
import re
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')


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
    extras_require={
        'docs': [
            'Sphinx']
    },
    description="Python script that generates a SQLite database from TibiaWiki articles",
    entry_points='''
        [console_scripts]
        tibiawikisql=tibiawikisql.__main__:cli
    ''',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Internet',
        'Topic :: Utilities'
    ]
)
