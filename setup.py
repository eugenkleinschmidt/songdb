from setuptools import find_packages
from setuptools import setup

setup(
    name="songdb",
    packages=find_packages(exclude='tests'),
    package_dir={},
    include_package_data=True,
    zip_safe=False,
    install_requires=['tinydb', 'tinydb_serialization'],
    entry_points={
        'console_scripts': [
            "songdb=songdb.cli:main",
        ]
    },
)
