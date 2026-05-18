#!/usr/bin/env python3
"""
Setup script for Vengeance Bot
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vengeance-bot",
    version="1.0.0",
    author="Ian Carter Kulani",
    author_email="ian@vengeance-bot.com",
    description="Ultimate Cybersecurity Command Center with Multi-Platform Bot Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vengeance-bot/vengeance-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vengeance=vengeance:main",
            "vengeance-health=healthcheck:main",
            "vengeance-security=security_scan:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)