from setuptools import find_packages, setup

setup(
    name="songdb",
    packages=find_packages(),
    install_requires=['tinydb', ],
    entry_points={
        'console_scripts': [
            "songdb=src.__main__:main",
        ]
    },
)
