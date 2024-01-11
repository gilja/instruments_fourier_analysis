"""
setup
=====

This module sets up the PyToneAnalyzer package for distribution. It includes package
information, versioning, author details, and other metadata necessary for distribution
on PyPI.
"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PyToneAnalyzer",
    version="0.1.0",
    author="Duje Giljanović",
    author_email="giljanovic.duje@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/gilja/instruments_fourier_analysis",
    license="LICENSE.txt",
    description="A Python package for analyzing musical instruments through Fourier analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "scipy>=1.11.4",
        "ipywidgets>=8.1.1",
        "plotly>=5.18.0",
        "sympy>=1.12",
        "kaleido>=0.2.1",
        "nbformat>=5.9.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Sound/Audio :: Analysis",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
    ],
    python_requires=">=3.9",
)
