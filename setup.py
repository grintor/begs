import pathlib
from setuptools import setup

# pip install twine
# pip install wheel
# rd /s /q dist
# python setup.py sdist bdist_wheel
# twine check dist/*
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# twine upload dist/*


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="beg",
    version="0.0.1",
    description="A partial rewrite of the famous requests library with a better defaults and certificate handling",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/grintor/beg",
    author="Chris Wheeler",
    author_email="grintor@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    py_modules=["beg"],
    include_package_data=False,
    install_requires=[],
)