"""Setup configuration for YTP3 package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ytp3",
    version="3.0.0",
    author="YTP3 Development Team",
    description="Modern YouTube downloader with GUI and CLI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hedd404ew/ytp3",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.11.16",
        "requests>=2.31.0",
        "mutagen>=1.46.0",
        "customtkinter>=5.2.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ytp3=ytp3.cli:main",
        ],
    },
)
