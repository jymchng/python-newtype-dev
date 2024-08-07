#ifndef NEWTYPE_INIT_H
#define NEWTYPE_INIT_H

#include <Python.h>

// Constants for initialization arguments
#define NEWTYPE_INIT_ARGS_STR "_newtype_init_args_"
#define NEWTYPE_INIT_KWARGS_STR "_newtype_init_kwargs_"

// Structure definition for NewInitObject
typedef struct {
  PyObject_HEAD PyObject *func_get;
  int has_get;
  PyObject *obj;
  PyTypeObject *cls;
} NewInitObject;

// Module initialization function
PyMODINIT_FUNC PyInit_newtypeinit(void);

#endif // NEWTYPE_INIT_H
