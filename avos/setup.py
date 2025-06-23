#!/usr/bin/env python3
"""
AgentVerse OS (AVOS) Setup
"""
from setuptools import setup, find_packages

setup(
    name="avos",
    version="0.1.0",
    description="AgentVerse Operating System - CLI for AI Agent Management",
    author="A\V",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "asyncio",
        "aiohttp",
        "python-dotenv",
        "tabulate",
        "watchdog",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "av=avos.cli:main",
        ],
    },
    python_requires=">=3.8",
)