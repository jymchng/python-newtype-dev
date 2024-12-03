#define PY_SSIZE_T_CLEAN
#include "newtype_meth.h"

#include <Python.h>
#include <descrobject.h>
#include <stddef.h>

#include "newtype_debug_print.h"
#include "structmember.h"  // Include for PyMemberDef and related macros

static void set___isabstractmethod__(NewTypeMethodObject* self, PyObject* func)
{
  int res = _PyObject_IsAbstract(func);
  if (res == 1) {
    self->__isabstractmethod__ = Py_True;
  } else {
    self->__isabstractmethod__ = Py_False;
  }
}

// Method to initialize the NewTypeMethod object
static int NewTypeMethod_init(NewTypeMethodObject* self,
                              PyObject* args,
                              PyObject* kwds)
{
  PyObject *func, *wrapped_cls;
  int is_callable;
  if (!PyArg_ParseTuple(args, "OO", &func, &wrapped_cls))
    return -1;

  is_callable = PyCallable_Check(func);

  if (PyObject_HasAttrString(func, "__get__") && is_callable) {
    self->func_get = PyObject_GetAttrString(func, "__get__");
    self->has_get = 1;
  } else if (is_callable) {
    self->func_get = func;
    Py_INCREF(self->func_get);
    self->has_get = 0;
  } else {
    PyErr_SetString(PyExc_TypeError,
                    "expected first argument to be a callable but it is not");
  }
  if (wrapped_cls == NULL) {
    return -1;
  }
  self->wrapped_cls = wrapped_cls;
  Py_INCREF(self->wrapped_cls);

  set___isabstractmethod__(self, func);

  return 0;
}

// Descriptor __get__ method
static PyObject* NewTypeMethod_get(NewTypeMethodObject* self,
                                   PyObject* inst,
                                   PyObject* owner)
{
  Py_XDECREF(self->obj);  // Decrease reference to old object
  Py_XDECREF(self->cls);  // Decrease reference to old class

  self->obj = inst;
  Py_XINCREF(self->obj);  // Increase reference to new object
  self->cls = (PyTypeObject*)owner;
  Py_XINCREF(self->cls);  // Increase reference to new class
  Py_INCREF(self);
  return (PyObject*)self;
}

// Call method to wrap the function call
static PyObject* NewTypeMethod_call(NewTypeMethodObject* self,
                                    PyObject* args,
                                    PyObject* kwargs)
{
  PyObject *func, *result;

  // This causes recursion for pandas DataFrame
  // if (self->obj != NULL) {
  //   DEBUG_PRINT("`self->obj`: %s\n",
  //               PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  // }

  if (self->cls != NULL) {
    DEBUG_PRINT("`self->cls`: %s\n",
                PyUnicode_AsUTF8(PyObject_Repr((PyObject*)self->cls)));
  }

  if (self->has_get) {
    DEBUG_PRINT("`self->has_get` = %d\n", self->has_get);
    if (self->obj == NULL) {
      DEBUG_PRINT("`self->obj` is NULL\n");
      func = PyObject_CallFunctionObjArgs(
          self->func_get, Py_None, self->wrapped_cls, NULL);
    } else {
      DEBUG_PRINT("`self->obj` is not NULL\n");
      func = PyObject_CallFunctionObjArgs(
          self->func_get, self->obj, self->wrapped_cls, NULL);
    }
  } else {
    func = self->func_get;
    DEBUG_PRINT("`self->has_get` = %d\n", self->has_get);
    Py_INCREF(func);
  }

  if (func == NULL) {
    return NULL;
  }

  // This causes recursion for pandas DataFrame
  // DEBUG_PRINT("`func`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(func)));

  result = PyObject_Call(func, args, kwargs);
  Py_DECREF(func);

  if (result == NULL)
    return NULL;
  DEBUG_PRINT("`result` = %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));

  if (self->obj == NULL && self->cls == NULL) {
    // free standing function is being wrapped
    goto done;
  }

  if (self->cls && PyObject_TypeCheck(result, self->cls)) {
    goto done;
  }

  DEBUG_PRINT("`result` is not an instance of `self->cls`\n");
  if (PyObject_IsInstance(result, self->wrapped_cls))
  {  // now we try to build an instance of the subtype
    DEBUG_PRINT("`result` is an instance of `self->wrapped_cls`\n");
    PyObject *init_args, *init_kwargs;
    PyObject *new_inst, *args_combined;

    if (self->obj == NULL) {
      PyObject* first_elem;

      if (self->cls == NULL) {
        goto done;
      }

      if (PyTuple_Size(args) > 0) {  // Got arguments
        first_elem = PyTuple_GetItem(args, 0);
        Py_XINCREF(
            first_elem);  // Increment reference count of the first element

      } else {  // `args` is empty here, then we are done actually
        goto done;
      };
      if (PyObject_IsInstance(first_elem, (PyObject*)self->cls)) {
        init_args = PyObject_GetAttrString(first_elem, NEWTYPE_INIT_ARGS_STR);
        init_kwargs =
            PyObject_GetAttrString(first_elem, NEWTYPE_INIT_KWARGS_STR);
      } else {  // first element is not the subtype, so we are done also
        goto done;
      }
      Py_XDECREF(first_elem);
    } else {  // `self->obj` is not NULL

      init_args = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_ARGS_STR);
      init_kwargs = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR);
    }

    Py_ssize_t args_len = PyTuple_Size(init_args);
    Py_ssize_t combined_args_len = 1 + args_len;
    args_combined = PyTuple_New(combined_args_len);
    if (args_combined == NULL) {
      Py_XDECREF(init_args);
      Py_XDECREF(init_kwargs);
      Py_DECREF(result);
      return NULL;  // Use return NULL instead of Py_RETURN_NONE
    }

    // Set the first item of the new tuple to `result`
    PyTuple_SET_ITEM(args_combined,
                     0,
                     result);  // `result` is now owned by `args_combined`

    // Copy items from `init_args` to `args_combined`
    for (Py_ssize_t i = 0; i < args_len; i++) {
      PyObject* item = PyTuple_GetItem(init_args, i);  // Borrowed reference
      if (item == NULL) {
        Py_DECREF(args_combined);
        Py_XDECREF(init_args);
        Py_XDECREF(init_kwargs);
        return NULL;
      }
      Py_INCREF(item);  // Increase reference count
      PyTuple_SET_ITEM(args_combined,
                       i + 1,
                       item);  // `item` is now owned by `args_combined`
    }
    DEBUG_PRINT("`args_combined`: %s\n",
                PyUnicode_AsUTF8(PyObject_Repr(args_combined)));

    if (init_kwargs != NULL) {
      DEBUG_PRINT("`init_kwargs`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(init_kwargs)));
    };

    // Call the function or constructor
    new_inst = PyObject_Call((PyObject*)self->cls, args_combined, init_kwargs);

    // Clean up
    Py_DECREF(args_combined);  // Decrement reference count of `args_combined`
    Py_XDECREF(init_args);
    Py_XDECREF(init_kwargs);

    // Ensure proper error propagation
    if (new_inst == NULL) {
      return NULL;
    }
    DEBUG_PRINT("`new_inst`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(new_inst)));
    return new_inst;
  }

done:
  Py_XINCREF(result);
  return result;
}

// Deallocation method
static void NewTypeMethod_dealloc(NewTypeMethodObject* self)
{
  Py_XDECREF(self->func_get);
  Py_XDECREF(self->wrapped_cls);
  Py_XDECREF(self->obj);
  Py_XDECREF(self->cls);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

// Method definitions
static PyMethodDef NewTypeMethod_methods[] = {{NULL, NULL, 0, NULL}};

static int NewTypeMethodObject_traverse(PyObject* self,
                                        visitproc visit,
                                        void* arg)
{
  NewTypeMethodObject* pp = (NewTypeMethodObject*)self;
  Py_VISIT(pp->cls);
  Py_VISIT(pp->obj);
  Py_VISIT(pp->wrapped_cls);
  return 0;
}

static int NewTypeMethodObject_clear(PyObject* self)
{
  NewTypeMethodObject* pp = (NewTypeMethodObject*)self;
  Py_CLEAR(pp->cls);
  Py_CLEAR(pp->obj);
  Py_CLEAR(pp->wrapped_cls);
  return 0;
}

static PyMemberDef newtypemethodobject_members[] = {
    {"__isabstractmethod__",
     T_OBJECT,
     offsetof(NewTypeMethodObject, __isabstractmethod__),
     READONLY},
    {0}};

// Type definition
PyTypeObject NewTypeMethodType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "newtypemethod.NewTypeMethod",
    .tp_doc =
        "A descriptor class that wraps around regular methods of a class "
        "to allow instantiation of the subtype if the method returns an "
        "instance of the supertype.",
    .tp_basicsize = sizeof(NewTypeMethodObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)NewTypeMethod_init,
    .tp_dealloc = (destructor)NewTypeMethod_dealloc,
    .tp_call = (ternaryfunc)NewTypeMethod_call,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_members = newtypemethodobject_members,
    .tp_methods = NewTypeMethod_methods,
    .tp_descr_get = (descrgetfunc)NewTypeMethod_get,
    .tp_traverse = NewTypeMethodObject_traverse,
    .tp_clear = NewTypeMethodObject_clear,
};

// Module definition
static struct PyModuleDef newtypemethodmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "newtypemethod",
    .m_doc =
        "A Module that contains `NewTypeMethod` - a descriptor class "
        "that wraps around regular methods of a class to allow instantiation "
        "of the subtype if the method returns an instance of the supertype.",
    .m_size = -1,
    .m_methods = NewTypeMethod_methods,
};

// Module initialization function
PyMODINIT_FUNC PyInit_newtypemethod(void)
{
  if (PyType_Ready(&NewTypeMethodType) < 0)
    return NULL;

  PyObject* m = PyModule_Create(&newtypemethodmodule);
  if (m == NULL)
    return NULL;

  Py_INCREF(&NewTypeMethodType);
  if (PyModule_AddObject(m, "NewTypeMethod", (PyObject*)&NewTypeMethodType) < 0)
  {
    Py_DECREF(&NewTypeMethodType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
