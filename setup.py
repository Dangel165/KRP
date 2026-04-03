"""
KRP (Korean Programming Language) - 설치 스크립트
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="krp",
    version="2.0.0",
    author="KRP Team",
    author_email="",
    description="KRP (Korean Programming Language) - 한국어 프로그래밍 언어",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/krp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 기본 의존성 (인터프리터만)
    ],
    extras_require={
        "llvm": ["llvmlite>=0.40.0"],  # LLVM 컴파일 기능
        "ide": [],  # IDE는 tkinter 사용 (Python 기본 포함)
        "all": ["llvmlite>=0.40.0"],  # 모든 기능
    },
    entry_points={
        "console_scripts": [
            "krp=main:main",
            "krp-ide=ide:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.한글", "*.md", "*.txt"],
        "examples": ["*.한글"],
        "grammar": ["*.g4"],
    },
)
