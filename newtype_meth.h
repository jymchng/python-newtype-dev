#ifndef NEWTYPEMETHOD_H
#define NEWTYPEMETHOD_H

#include <Python.h>

// Constants for initialization arguments
#define NEWTYPE_INIT_ARGS_STR "_newtype_init_args_"
#define NEWTYPE_INIT_KWARGS_STR "_newtype_init_kwargs_"

// Struct for the NewTypeMethod object
typedef struct {
  PyObject_HEAD PyObject *func_get;
  int has_get;
  PyObject *wrapped_cls;
  PyObject *obj;
  PyTypeObject *cls;
} NewTypeMethodObject;

// Method declarations
PyMODINIT_FUNC PyInit_newtypemethod(void);

// Type definition
extern PyTypeObject NewTypeMethodType;

#endif // NEWTYPEMETHOD_H
