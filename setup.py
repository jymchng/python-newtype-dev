from setuptools import Extension, setup
import sys

# Check if debug printing should be enabled
debug_print = '-D__DEBUG_PRINT__' in sys.argv
if debug_print:
    sys.argv.remove('-D__DEBUG_PRINT__')  # Remove the flag for setuptools to avoid errors

module_newtypemethod = Extension(
    "newtypemethod",
    sources=["newtype_meth.c"],
    include_dirs=["."],
    extra_compile_args=['-D__DEBUG_PRINT__'] if debug_print else []
)

module_newtypeinit = Extension(
    "newtypeinit",
    sources=["newtype_init.c"],
    include_dirs=["."],
    extra_compile_args=['-D__DEBUG_PRINT__'] if debug_print else []
)

setup(
    name="__newtypes_internal__",
    version="1.0",
    description="Module for wrapping methods with special handling.",
    ext_modules=[module_newtypemethod, module_newtypeinit],
)