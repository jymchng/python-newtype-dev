#define PY_SSIZE_T_CLEAN
#include "newtype_init.h"
#include "newtype_meth.h"
#include "structmember.h"
#include <Python.h>
#include <stddef.h>

static int NewInit_init(NewInitObject *self, PyObject *args, PyObject *kwds) {
  PyObject *func;

  if (!PyArg_ParseTuple(args, "O", &func)) {
    return -1;
  }

  if (PyObject_HasAttrString(func, "__get__")) {
    self->func_get = PyObject_GetAttrString(func, "__get__");
    self->has_get = 1;
  } else {
    self->func_get = func;
    self->has_get = 0;
  }

  if (PyErr_Occurred()) {
    return -1;
  }

  // Print initial values
  // printf("NewInit_init: `self->obj`: %s\n",
  // PyUnicode_AsUTF8(PyObject_Repr(self->obj))); printf("NewInit_init:
  // `self->cls`: %s\n", PyUnicode_AsUTF8(PyObject_Repr((PyObject
  // *)self->cls)));

  return 0;
}

static PyObject *NewInit_get(NewInitObject *self, PyObject *inst,
                             PyObject *owner) {
  Py_XDECREF(self->obj); // Decrease reference to old object
  Py_XDECREF(self->cls); // Decrease reference to old class
  // printf("NewInit_get is called\n");

  // Check current values
  // printf("NewInit_get: `inst`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(inst)));
  // printf("NewInit_get: `owner`: %s\n",
  // PyUnicode_AsUTF8(PyObject_Repr(owner))); printf("NewInit_get: `self->obj`:
  // %s\n", PyUnicode_AsUTF8(PyObject_Repr(self->obj))); printf("NewInit_get:
  // `self->cls`: %s\n", PyUnicode_AsUTF8(PyObject_Repr((PyObject
  // *)self->cls)));

  // Py_XINCREF(inst);
  self->obj = inst;
  Py_XINCREF(self->obj);
  // Py_XINCREF(owner);
  self->cls = (PyTypeObject *)owner;
  Py_XINCREF(self->cls);

  // Print new values
  // printf("NewInit_get updated: `self->obj`: %s\n",
  // PyUnicode_AsUTF8(PyObject_Repr(self->obj))); printf("NewInit_get updated:
  // `self->cls`: %s\n", PyUnicode_AsUTF8(PyObject_Repr((PyObject
  // *)self->cls)));

  if (self->obj == NULL) {
    // printf("`self->obj` is NULL\n");
    if (self->func_get != NULL) {
      // printf("`self->func_get`: %s\n",
      // PyUnicode_AsUTF8(PyObject_Repr(self->func_get)));
      if (self->has_get) {
        // printf("`self->has_get`: %d\n", self->has_get);
        return PyObject_CallFunctionObjArgs(self->func_get, Py_None, self->cls,
                                            NULL);
      }
      return self->func_get;
    }
    PyErr_SetString(
        PyExc_TypeError,
        "`NewTypeMethod` object has no `func_get`; this is an internal C-API "
        "error - please report this as an issue to the author on GitHub");
  }

  Py_XINCREF(self);
  return (PyObject *)self;
}

static PyObject *NewInit_call(NewInitObject *self, PyObject *args,
                              PyObject *kwds) {
  // printf("NewInit_call is called\n");

  printf("NewInit_call: `self->obj`: %s\n",
         PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  printf("NewInit_call: `self->cls`: %s\n",
         PyUnicode_AsUTF8(PyObject_Repr((PyObject *)self->cls)));

  PyObject *result;
  PyObject *func;
  PyObject *args_tuple = PyTuple_New(0);

  // if (self->obj == NULL) {
  //   printf("`self->obj` is NULL\n");
  //   self->obj = Py_None;
  // }

  if (self->has_get) {
    if (self->obj == NULL && self->cls == NULL) {
      // free standing function
      PyErr_SetString(PyExc_TypeError,
                      "NewInit object has no `obj` or `cls`, it cannot be used "
                      "to wrap a free standing function; this is an internal "
                      "C-API error - please report this");
      return NULL;
    } else if (self->obj == NULL) {
      func = PyObject_CallFunctionObjArgs(self->func_get, Py_None, self->cls,
                                          NULL);
    } else {
      func = PyObject_CallFunctionObjArgs(self->func_get, self->obj, self->cls,
                                          NULL);
    }
  } else {
    func = self->func_get;
  }

  if (func == NULL) {
    printf("`func` is NULL\n");
    return NULL;
  }
  printf("`func`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(func)));
  if (args_tuple == NULL) {
    return NULL;
  }

  if (self->obj &&
      (PyObject_HasAttrString(self->obj, NEWTYPE_INIT_ARGS_STR) != 1)) {
    // printf("Setting `%s` attribute on `%s` to `%s`\n", NEWTYPE_INIT_ARGS_STR,
    // PyUnicode_AsUTF8(PyObject_Repr(self->obj)),
    // PyUnicode_AsUTF8(PyObject_Repr(args)));
    PyObject *args_slice = PyTuple_GetSlice(args, 1, PyTuple_Size(args));
    if (args_slice == NULL) {
      Py_DECREF(args_tuple);
      return NULL;
    }
    if (PyObject_SetAttrString(self->obj, NEWTYPE_INIT_ARGS_STR, args_slice) <
        0) {
      Py_DECREF(args_slice);
      Py_DECREF(args_tuple);
      return NULL;
    }
    Py_DECREF(args_slice);
  }

  if (self->obj &&
      (PyObject_HasAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR) != 1)) {
    // printf("Setting `%s` attribute on `%s` to `%s`\n", NEWTYPE_INIT_ARGS_STR,
    // PyUnicode_AsUTF8(PyObject_Repr(self->obj)),
    // PyUnicode_AsUTF8(PyObject_Repr(kwds)));
    if (kwds == NULL) {
      kwds = (PyObject *)PyDict_New();
    }
    if (PyObject_SetAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR, kwds) < 0) {
      Py_DECREF(args_tuple);
      return NULL;
    }
  }

  printf("`args`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(args)));
  printf("`kwds`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(kwds)));

  // Ensure `self->cls` is a valid type object
  if (self->cls && PyType_Check(self->cls)) {
    result = PyObject_Call(func, args, kwds);
  } else {
    PyErr_SetString(PyExc_TypeError, "Invalid type object in descriptor");
    result = NULL;
  }
  printf("`result`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));

  if (PyErr_Occurred()) {
    Py_DECREF(args_tuple);
    return NULL;
  }

  Py_DECREF(args_tuple);
  Py_DECREF(func);
  // printf("`result`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));
  return result;
}

static void NewInit_dealloc(NewInitObject *self) {
  Py_XDECREF(self->cls);
  Py_XDECREF(self->obj);
  Py_XDECREF(self->func_get);

  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyMethodDef NewInit_methods[] = {{NULL, NULL, 0, NULL}};

static PyTypeObject NewInitType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "newinit.NewInit",
    .tp_doc = "Descriptor class that wraps methods for instantiating subtypes.",
    .tp_basicsize = sizeof(NewInitObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)NewInit_init,
    .tp_dealloc = (destructor)NewInit_dealloc,
    .tp_call = (ternaryfunc)NewInit_call,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_setattro = NULL,
    .tp_methods = NewInit_methods,
    .tp_descr_get = (descrgetfunc)NewInit_get,
};

static struct PyModuleDef newinitmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "newinit",
    .m_doc = "A module containing `NewInit` descriptor class.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_newtypeinit(void) {
  PyObject *m;
  if (PyType_Ready(&NewInitType) < 0)
    return NULL;

  m = PyModule_Create(&newinitmodule);
  if (m == NULL)
    return NULL;

  // #define NEWTYPE_INIT_ARGS_STR "_newtype_init_args_"
  // #define NEWTYPE_INIT_KWARGS_STR "_newtype_init_kwargs_"

  PyObject *PY_NEWTYPE_INIT_KWARGS_STR =
      PyUnicode_FromString(NEWTYPE_INIT_KWARGS_STR);
  if (PY_NEWTYPE_INIT_KWARGS_STR == NULL) {
    Py_DECREF(m);
    return NULL;
  }
  PyModule_AddObject(m, "NEWTYPE_INIT_KWARGS_STR", PY_NEWTYPE_INIT_KWARGS_STR);

  PyObject *PY_NEWTYPE_INIT_ARGS_STR =
      PyUnicode_FromString(NEWTYPE_INIT_ARGS_STR);
  if (PY_NEWTYPE_INIT_ARGS_STR == NULL) {
    Py_DECREF(m);
    return NULL;
  }
  PyModule_AddObject(m, "NEWTYPE_INIT_ARGS_STR", PY_NEWTYPE_INIT_ARGS_STR);

  Py_INCREF(&NewInitType);
  if (PyModule_AddObject(m, "NewInit", (PyObject *)&NewInitType) < 0) {
    Py_DECREF(&NewInitType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
