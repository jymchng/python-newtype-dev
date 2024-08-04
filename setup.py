from setuptools import Extension, setup

module_newtypemethod = Extension(
    "newtypemethod", sources=["newtype_meth.c"], include_dirs=["."]
)

module_newtypeinit = Extension(
    "newtypeinit", sources=["newtype_init.c"], include_dirs=["."]
)

setup(
    name="__newtypes_internal__",
    version="1.0",
    description="Module for wrapping methods with special handling.",
    ext_modules=[module_newtypemethod, module_newtypeinit],
)
