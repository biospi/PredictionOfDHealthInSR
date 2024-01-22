from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="fAM",
    version="0.0.1",
    author="Axel Montout",
    description="Accelerometry data famacha prediction pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biospi/PredictionOfDHealthInSR",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7.2",
)
