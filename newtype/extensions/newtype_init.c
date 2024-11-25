#define PY_SSIZE_T_CLEAN
#include "newtype_init.h"

#include <Python.h>
#include <stddef.h>

#include "newtype_debug_print.h"
#include "newtype_meth.h"
#include "structmember.h"

static int NewTypeInit_init(NewTypeInitObject* self,
                            PyObject* args,
                            PyObject* kwds)
{
  PyObject* func;

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
  DEBUG_PRINT("NewTypeInit_init: `self->obj`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  DEBUG_PRINT("NewTypeInit_init: `self->cls`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr((PyObject*)self->cls)));

  return 0;
}

static PyObject* NewTypeInit_get(NewTypeInitObject* self,
                                 PyObject* inst,
                                 PyObject* owner)
{
  Py_XDECREF(self->obj);  // Decrease reference to old object
  Py_XDECREF(self->cls);  // Decrease reference to old class
  DEBUG_PRINT("NewTypeInit_get is called\n");

  // Check current values
  DEBUG_PRINT("NewTypeInit_get: `inst`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr(inst)));
  DEBUG_PRINT("NewTypeInit_get: `owner`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr(owner)));

  self->obj = inst;
  Py_XINCREF(self->obj);
  self->cls = (PyTypeObject*)owner;
  Py_XINCREF(self->cls);

  // Print new values
  DEBUG_PRINT("NewTypeInit_get updated: `self->obj`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  DEBUG_PRINT("NewTypeInit_get updated: `self->cls`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr((PyObject*)self->cls)));

  if (self->obj == NULL) {
    DEBUG_PRINT("`self->obj` is NULL\n");
    if (self->func_get != NULL) {
      DEBUG_PRINT("`self->func_get`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(self->func_get)));
      if (self->has_get) {
        DEBUG_PRINT("`self->has_get`: %d\n", self->has_get);
        return PyObject_CallFunctionObjArgs(
            self->func_get, Py_None, self->cls, NULL);
      }
      return self->func_get;
    }
    PyErr_SetString(
        PyExc_TypeError,
        "`NewTypeInit` object has no `func_get`; this is an internal C-API "
        "error - please report this as an issue to the author on GitHub");
  }

  Py_XINCREF(self);
  return (PyObject*)self;
}

static PyObject* NewTypeInit_call(NewTypeInitObject* self,
                                  PyObject* args,
                                  PyObject* kwds)
{
  DEBUG_PRINT("NewTypeInit_call is called\n");

  DEBUG_PRINT("NewTypeInit_call: `self->obj`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  DEBUG_PRINT("NewTypeInit_call: `self->cls`: %s\n",
              PyUnicode_AsUTF8(PyObject_Repr((PyObject*)self->cls)));

  PyObject* result;  // return this
  PyObject* func;

  if (self->has_get) {
    if (self->obj == NULL && self->cls == NULL) {
      // free standing function
      PyErr_SetString(
          PyExc_TypeError,
          "`NewTypeInit` object has no `obj` (internal attribute) or "
          "`cls` (internal attribute),"
          "it cannot be used to wrap a free standing function");
      return NULL;  // allocated nothing so no need to free
    } else if (self->obj == NULL) {
      func = PyObject_CallFunctionObjArgs(
          self->func_get, Py_None, self->cls, NULL);
    } else {
      func = PyObject_CallFunctionObjArgs(
          self->func_get, self->obj, self->cls, NULL);
    }
  } else {
    func = self->func_get;
  }

  if (func == NULL) {
    DEBUG_PRINT("`func` is NULL\n");
    result = NULL;
    goto done;
  }

  if (self->obj
      && (PyObject_HasAttrString(self->obj, NEWTYPE_INIT_ARGS_STR) != 1))
  {
    DEBUG_PRINT("Setting `%s` attribute on `%s` to `%s`\n",
                NEWTYPE_INIT_ARGS_STR,
                PyUnicode_AsUTF8(PyObject_Repr(self->obj)),
                PyUnicode_AsUTF8(PyObject_Repr(args)));
    PyObject* args_slice;
    if (PyTuple_Size(args) > 1) {
      args_slice = PyTuple_GetSlice(args, 1, PyTuple_Size(args));
      if (args_slice == NULL) {
        // Py_DECREF(args_tuple);
        return NULL;
      }
    } else {
      args_slice = PyTuple_New(0);
    }
    if (PyObject_SetAttrString(self->obj, NEWTYPE_INIT_ARGS_STR, args_slice)
        < 0) {
      Py_DECREF(args_slice);
      result = NULL;
      goto done;
    }
    Py_XDECREF(args_slice);
  }

  if (self->obj
      && (PyObject_HasAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR) != 1))
  {
    DEBUG_PRINT("Setting `%s` attribute on `%s` to `%s`\n",
                NEWTYPE_INIT_ARGS_STR,
                PyUnicode_AsUTF8(PyObject_Repr(self->obj)),
                PyUnicode_AsUTF8(PyObject_Repr(kwds)));
    if (kwds == NULL) {  // `kwds` is `NULL`, first time the constructor is
                         // called, so we make a new `dict`.
      kwds = PyDict_New();
    } else {  // `kwds` is borrowed here, so we increase its ref count
      Py_INCREF(kwds);
    }
    if (PyObject_SetAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR, kwds) < 0) {
      result = NULL;
      goto done;
    }
  }

  DEBUG_PRINT("`args`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(args)));
  DEBUG_PRINT("`kwds`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(kwds)));

  // Ensure `self->cls` is a valid type object
  if (self->cls && PyType_Check(self->cls)) {
    result = PyObject_Call(func, args, kwds);
  } else {
    PyErr_SetString(PyExc_TypeError, "Invalid type object in descriptor");
    result = NULL;
  }

  if (PyErr_Occurred()) {
    // Py_DECREF(args_tuple);
    goto done;
  }

done:
  Py_XDECREF(func);
  Py_XDECREF(kwds);
  DEBUG_PRINT("`result`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));
  return result;
}

static void NewTypeInit_dealloc(NewTypeInitObject* self)
{
  Py_XDECREF(self->cls);
  Py_XDECREF(self->obj);
  Py_XDECREF(self->func_get);

  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyMethodDef NewTypeInit_methods[] = {{NULL, NULL, 0, NULL}};

static PyTypeObject NewTypeInitType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "NewTypeInit.NewTypeInit",
    .tp_doc = "Descriptor class that wraps methods for instantiating subtypes.",
    .tp_basicsize = sizeof(NewTypeInitObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)NewTypeInit_init,
    .tp_dealloc = (destructor)NewTypeInit_dealloc,
    .tp_call = (ternaryfunc)NewTypeInit_call,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_setattro = NULL,
    .tp_methods = NewTypeInit_methods,
    .tp_descr_get = (descrgetfunc)NewTypeInit_get,
};

static struct PyModuleDef NewTypeInitmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "NewTypeInit",
    .m_doc = "A module containing `NewTypeInit` descriptor class.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_newtypeinit(void)
{
  PyObject* m;
  if (PyType_Ready(&NewTypeInitType) < 0)
    return NULL;

  m = PyModule_Create(&NewTypeInitmodule);
  if (m == NULL)
    return NULL;

  PyObject* PY_NEWTYPE_INIT_KWARGS_STR =
      PyUnicode_FromString(NEWTYPE_INIT_KWARGS_STR);
  if (PY_NEWTYPE_INIT_KWARGS_STR == NULL) {
    Py_DECREF(m);
    return NULL;
  }
  PyModule_AddObject(m, "NEWTYPE_INIT_KWARGS_STR", PY_NEWTYPE_INIT_KWARGS_STR);

  PyObject* PY_NEWTYPE_INIT_ARGS_STR =
      PyUnicode_FromString(NEWTYPE_INIT_ARGS_STR);
  if (PY_NEWTYPE_INIT_ARGS_STR == NULL) {
    Py_DECREF(m);
    return NULL;
  }
  PyModule_AddObject(m, "NEWTYPE_INIT_ARGS_STR", PY_NEWTYPE_INIT_ARGS_STR);

  Py_INCREF(&NewTypeInitType);
  if (PyModule_AddObject(m, "NewTypeInit", (PyObject*)&NewTypeInitType) < 0) {
    Py_DECREF(&NewTypeInitType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
