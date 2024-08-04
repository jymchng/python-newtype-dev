#ifndef NEWTYPEMETHOD_H
#define NEWTYPEMETHOD_H

#include <Python.h>



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
