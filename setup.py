from setuptools import find_packages, setup

setup(
    name="songdb",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=['tinydb', 'tinydb_serialization'],
    entry_points={
        'console_scripts': [
            "songdb=songdb.cli:main",
        ]
    },
)
