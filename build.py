import logging
from logging import getLogger
import os
from pathlib import Path
import shutil
import sys
from tomli import load

from setuptools import Extension  # noqa: I001
from setuptools.command.build_ext import build_ext  # noqa: I001
from setuptools.dist import Distribution  # noqa: I001


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)s] %(message)s",
    stream=sys.stdout,
)
LOGGER = getLogger(__name__)
LOGGER.info("Running `build.py`...")

debug_print = (os.getenv('__PYNT_DEBUG__') == 'true') or False
LOGGER.info(f"`debug_print` = {debug_print}")

def list_dir_contents(directory, depth, level=0):
    if level > depth:
        return
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                print("  " * level + f"- {entry.name}")
                if entry.is_dir(follow_symlinks=False):
                    list_dir_contents(entry.path, depth, level + 1)
    except PermissionError as e:
        print(f"PermissionError: {e}")


def get_package_name(
    default_name=None,
) -> str:  # put a default name if there is
    """Retrieves the package name from setup.py or setup.cfg, or returns a default name."""
    if default_name is not None:
        return default_name

    # # Check for pyproject.toml
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "rb") as f:  # Open in binary mode for tomlib
            pyproject = load(f)  # Use tomlib's loads function
        return pyproject.get("tool", {}).get("poetry", {}).get("name", None)

    raise Exception(
        "Unable to determine what is the `PACKAGE_NAME` for this repository, set `default_name` parameter to a default name"
    )

# Constants
# Set `PROJECT_ROOT_DIR` to the directory of the current file, if in doubt with regards to path, always use relative to `PROJECT_ROOT_DIR`
PROJECT_ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_NAME = get_package_name()
# Uncomment if library can still function if extensions fail to compile
# (e.g. slower, python fallback).
# Don't allow failure if cibuildwheel is running.
# ALLOWED_TO_FAIL = os.environ.get("CIBUILDWHEEL", "0") != "1"
ALLOWED_TO_FAIL = False
REMOVE_HTML_ANNOTATION_FILES = True
PACKAGE_DIR = PROJECT_ROOT_DIR / PACKAGE_NAME
PROJECT_C_SOURCE_DIR_NAME = "src/newtype/extensions"
PROJECT_C_SOURCE_DIR = PROJECT_ROOT_DIR / PROJECT_C_SOURCE_DIR_NAME
C_SOURCE_FILES = [str(x) for x in PROJECT_C_SOURCE_DIR.rglob("*.c")]

INCLUDE_DIR_NAME = PROJECT_C_SOURCE_DIR_NAME
INCLUDE_DIR = PROJECT_ROOT_DIR / INCLUDE_DIR_NAME
INCLUDE_FILES = [str(x) for x in INCLUDE_DIR.rglob("*.h")]

LANGUAGE = "C"
C_EXTENSION_MODULE_NAME = "extensions"

# Log the constants
LOGGER.info(f"`PACKAGE_NAME` = {PACKAGE_NAME}")
LOGGER.info(f"`ALLOWED_TO_FAIL` = {ALLOWED_TO_FAIL}")
LOGGER.info(f"`C_SOURCE_FILES` = {C_SOURCE_FILES}")


def where_am_i() -> "Path":
    """Checks if the script is being run in the correct directory (`PROJECT_ROOT_DIR`)."""
    current_dir = Path.cwd()
    if current_dir != PROJECT_ROOT_DIR:
        raise RuntimeError(f"Please run this script in the directory: {PROJECT_ROOT_DIR}")

    # Check for at least one required file in `PROJECT_ROOT_DIR`
    required_files = [
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt",
    ]
    if not any((PROJECT_ROOT_DIR / file).exists() for file in required_files):
        raise RuntimeError("`build.py` should be located at the root directory of the project")

    LOGGER.info(f"Running in the correct directory: {current_dir}")
    return PROJECT_ROOT_DIR

def extra_compile_args():
    """A function to get all the extra compile arguments for the extension modules.
    Define your own arguments here.
    """
    if os.name == "nt":  # Windows
        extra_compile_args = [
            "/O2",
        ]
    else:  # UNIX-based systems
        extra_compile_args = [
            "-O3",
            "-Werror",
            "-Wno-unreachable-code-fallthrough",
            "-Wno-deprecated-declarations",
            "-Wno-parentheses-equality",
            "-Wno-unreachable-code",  # TODO: This should no longer be necessary with Cython>=3.0.3
        ]
    extra_compile_args.append("-UNDEBUG")  # Cython disables asserts by default.
    return extra_compile_args


def get_extension_modules():
    # Relative to project root directory
    include_dirs = [str(INCLUDE_DIR)]
    LOGGER.info(f"in function `get_extension_modules`; `include_dirs` = {include_dirs}")

    module_newtypemethod = Extension(
    "newtype.extensions.newtypemethod",
    sources=["src/newtype/extensions/newtype_meth.c"],
    include_dirs=["src/newtype/extensions"],
    extra_compile_args=["-D__DEBUG_PRINT__"] if debug_print else [],
)

    module_newtypeinit = Extension(
        "newtype.extensions.newtypeinit",
        sources=["src/newtype/extensions/newtype_init.c"],
        include_dirs=["src/newtype/extensions"],
        extra_compile_args=["-D__DEBUG_PRINT__"] if debug_print else [],
    )

    extensions = [
        module_newtypeinit,
        module_newtypemethod,
    ]
    return extensions


def copy_output_to_cmd_buildlib(cmd):
    build_outputs = cmd.get_outputs()
    build_outputs_str = {str(output) for output in build_outputs}
    LOGGER.info(f"Outputs produced by `build` are: {build_outputs_str}")
    for output in build_outputs:
        output = Path(output)
        relative_extension = output.relative_to(cmd.build_lib)
        relative_extension_path = PROJECT_ROOT_DIR / 'src' / relative_extension
        LOGGER.info(f"Copying file from `{output}` to `{relative_extension_path}`")
        shutil.copyfile(output, relative_extension_path)
        LOGGER.info("File copied successfully")



def build_c_extensions():
    """Builds the extension modules using pure C without Cython."""
    extensions = get_extension_modules()
    include_dirs = set()
    for extension in extensions:
        include_dirs.update(extension.include_dirs)
    include_dirs = list(include_dirs)

    dist = Distribution({"ext_modules": extensions})
    cmd = build_ext(dist)
    cmd.ensure_finalized()
    cmd.run()
    LOGGER.info(f"`cmd.build_lib` = {cmd.build_lib}")

    copy_output_to_cmd_buildlib(cmd)


if __name__ == "__main__":
    # actual build
    # pre-build checks; making sure `build.py` is in `PROJECT_ROOT_DIR`
    where_am_i()
    try:
        build_c_extensions()  # Call the new function for pure C builds
    except Exception as err:
        LOGGER.exception(f"`build.py` has failed: error = {err}")
        if not ALLOWED_TO_FAIL:
            raise