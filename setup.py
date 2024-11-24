from setuptools import Extension, setup, find_packages
import sys

# Check if debug printing should be enabled
debug_print = '-D__DEBUG_PRINT__' in sys.argv
if debug_print:
    sys.argv.remove('-D__DEBUG_PRINT__')  # Remove the flag for setuptools to avoid errors

module_newtypemethod = Extension(
    "newtype.extensions.newtypemethod",
    sources=["src/newtype/extensions/newtype_meth.c"],
    include_dirs=["src/newtype/extensions"],
    extra_compile_args=['-D__DEBUG_PRINT__'] if debug_print else []
)

module_newtypeinit = Extension(
    "newtype.extensions.newtypeinit",
    sources=["src/newtype/extensions/newtype_init.c"],
    include_dirs=["src/newtype/extensions"],
    extra_compile_args=['-D__DEBUG_PRINT__'] if debug_print else []
)

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-newtype",
    version="0.0.0",  # Let poetry-dynamic-versioning handle this
    author="openhands",
    author_email="openhands@all-hands.dev",
    description="A Python library for extending existing types with additional functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jymchng/python-newtype-dev",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=[module_newtypemethod, module_newtypeinit],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing_extensions",
    ],
    extras_require={
        "dev": [
            "pytest>=3.2",
            "pytest-asyncio",
            "pytest-memray",
            "pandas>=2",
        ],
    },
)