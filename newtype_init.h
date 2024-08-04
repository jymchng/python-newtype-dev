#ifndef NEWTYPE_INIT_H
#define NEWTYPE_INIT_H

#include <Python.h>

// Structure definition for NewInitObject
typedef struct {
  PyObject_HEAD PyObject *func_get;
  int has_get;
  PyObject *obj;
  PyTypeObject *cls;
} NewInitObject;

// Function declarations
static int NewInit_init(NewInitObject *self, PyObject *args, PyObject *kwds);
static PyObject *NewInit_get(NewInitObject *self, PyObject *inst,
                             PyObject *owner);
static PyObject *NewInit_call(NewInitObject *self, PyObject *args,
                              PyObject *kwds);
static void NewInit_dealloc(NewInitObject *self);

// Method definitions
static PyMethodDef NewInit_methods[];

// Type object definition
static PyTypeObject NewInitType;

// Module definition
static struct PyModuleDef newinitmodule;

// Module initialization function
PyMODINIT_FUNC PyInit_newtypeinit(void);

#endif // NEWTYPE_INIT_H
