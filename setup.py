from setuptools import setup, find_packages

setup(
    name='logsim',
    version='0.1',
    packages=find_packages(where='final'),
    package_dir={'': 'final'},
)