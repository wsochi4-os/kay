#!/usr/bin/env python3
"""
Setup script for Kutti
"""

from setuptools import setup, find_packages
import os

# Read the requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read the long description from README if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="kutti",
    version="0.1.0",
    description="Your Personal AI CLI Agent - OpenCode-compatible authentication & provider system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kutti Team",
    author_email="",
    url="https://github.com/wsochi4-os/kay",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "cryptography>=41.0.0", 
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "macos": [
            "keyring>=24.0.0",
        ],
        "linux": [
            "secretstorage>=3.3.0",
        ],
        "windows": [
            "win32credentialmanager>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kutti=kutti:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md"],
    },
)