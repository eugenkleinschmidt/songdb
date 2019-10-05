from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
    name="songdb",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=['tinydb', 'tinydb_serialization'],
    entry_points={
        'console_scripts': [
            "songdb=cli:main",
        ]
    },
)
