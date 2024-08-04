#define PY_SSIZE_T_CLEAN
#include "newtype_meth.h"
#include "structmember.h" // Include for PyMemberDef and related macros
#include <Python.h>
#include <stddef.h>

// Method to initialize the NewTypeMethod object
static int NewTypeMethod_init(NewTypeMethodObject *self, PyObject *args,
                              PyObject *kwds) {
  PyObject *func, *wrapped_cls;
  if (!PyArg_ParseTuple(args, "OO", &func, &wrapped_cls))
    return -1;

  if (PyObject_HasAttrString(func, "__get__")) {
    self->func_get = PyObject_GetAttrString(func, "__get__");
    self->has_get = 1;
  } else {
    self->func_get = func;
    Py_INCREF(self->func_get);
    self->has_get = 0;
  }
  if (wrapped_cls == NULL) {
    return -1;
  }
  self->wrapped_cls = wrapped_cls;
  Py_INCREF(self->wrapped_cls);

  return 0;
}

// Descriptor __get__ method
static PyObject *NewTypeMethod_get(NewTypeMethodObject *self, PyObject *inst,
                                   PyObject *owner) {
  Py_XDECREF(self->obj); // Decrease reference to old object
  Py_XDECREF(self->cls); // Decrease reference to old class

  self->obj = inst;
  Py_XINCREF(self->obj); // Increase reference to new object
  self->cls = (PyTypeObject *)owner;
  Py_XINCREF(self->cls); // Increase reference to new class

  // if (self->obj == NULL) {
  //   // printf("`self->obj` is NULL\n");
  //   if (self->func_get != NULL) {
  //     // printf("`self->func_get`: %s\n",
  //     PyUnicode_AsUTF8(PyObject_Repr(self->func_get))); if (self->has_get) {
  //       return PyObject_CallFunctionObjArgs(self->func_get, Py_None,
  //                                           self->wrapped_cls, NULL);
  //     } else {
  //       PyObject *func;
  //       func = self->func_get;
  //       Py_INCREF(func);
  //       return func;
  //     }
  //   }
  // }

  Py_INCREF(self);
  return (PyObject *)self;
}

// Call method to wrap the function call
static PyObject *NewTypeMethod_call(NewTypeMethodObject *self, PyObject *args,
                                    PyObject *kwargs) {
  PyObject *func, *result;

  // printf("`self->obj`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
  // printf("`self->cls`: %s\n", PyUnicode_AsUTF8(PyObject_Repr((PyObject *)self->cls)));


  if (self->has_get) {
    // printf("`self->has_get` = %d\n", self->has_get);
    if (self->obj == NULL) {
      // printf("`self->obj` is NULL\n");
      func = PyObject_CallFunctionObjArgs(self->func_get, Py_None,
                                          self->wrapped_cls, NULL);
      // printf("`func`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(func)));
    } else {
      // printf("`self->obj` is not NULL\n");
      func = PyObject_CallFunctionObjArgs(self->func_get, self->obj,
                                          self->wrapped_cls, NULL);
      // printf("`func`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(func)));
    }
  } else {
    func = self->func_get;
    // printf("`self->has_get` = %d\n", self->has_get);
    Py_INCREF(func);
  }

  if (func == NULL) {
    return NULL;
  }

  result = PyObject_Call(func, args, kwargs);
  Py_DECREF(func);

  if (result == NULL)
    return NULL;
  // printf("`result` = %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));

  if (self->obj == NULL && self->cls == NULL) {
    // free standing function is being wrapped
    goto done;
  }

  if (PyObject_TypeCheck(result, self->cls)) {
    goto done;
  }
  
  // printf("`result` is not an instance of `self->cls`\n");
  if (PyObject_IsInstance(result, self->wrapped_cls)) {
    // printf("`result` is an instance of `self->wrapped_cls`\n");
    PyObject *init_args, *init_kwargs;
    if (self->obj == NULL) {
      PyObject *first_elem;
      if (PyTuple_Size(args) > 0) { // Got arguments
        first_elem = PyTuple_GetItem(args, 0);
        Py_XINCREF(
            first_elem); // Increment reference count of the first element
        // Now you have the first element in `first_elem` and the rest of the
        // elements in `rest_tuple` Do something with `first_elem` and
        // `rest_tuple`
      } else { // `self->obj` is NULL, expect at least one `arg` in `args`
        PyErr_SetString(
            PyExc_TypeError,
            "Expected at least one argument, which is the instance object");

        return NULL;
      };
      init_args = PyObject_GetAttrString(first_elem, NEWTYPE_INIT_ARGS_STR);
      init_kwargs = PyObject_GetAttrString(first_elem, NEWTYPE_INIT_KWARGS_STR);
      Py_XDECREF(first_elem);
    } else { // `self->obj` is not NULL

      init_args = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_ARGS_STR);
      init_kwargs = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR);
    }

    PyObject *new_inst;

    PyObject *args_combined;
    Py_ssize_t args_len = PyTuple_Size(init_args);
    Py_ssize_t combined_args_len = 1 + args_len;
    args_combined = PyTuple_New(combined_args_len);
    if (args_combined == NULL) {
      Py_XDECREF(init_args);
      Py_XDECREF(init_kwargs);
      Py_DECREF(result);
      return NULL; // Use return NULL instead of Py_RETURN_NONE
    }

    // Set the first item of the new tuple to `result`
    PyTuple_SET_ITEM(args_combined, 0,
                     result); // `result` is now owned by `args_combined`

    // Copy items from `init_args` to `args_combined`
    for (Py_ssize_t i = 0; i < args_len; i++) {
      PyObject *item = PyTuple_GetItem(init_args, i); // Borrowed reference
      if (item == NULL) {
        Py_DECREF(args_combined);
        Py_XDECREF(init_args);
        Py_XDECREF(init_kwargs);
        return NULL;
      }
      Py_INCREF(item); // Increase reference count
      PyTuple_SET_ITEM(args_combined, i + 1,
                       item); // `item` is now owned by `args_combined`
    }
    // printf("`args_combined`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(args_combined)));
    // printf("`init_kwargs`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(init_kwargs)));

    // Call the function or constructor
    new_inst = PyObject_Call((PyObject *)self->cls, args_combined, init_kwargs);
    // printf("`new_inst`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(new_inst)));
    // Clean up
    Py_DECREF(args_combined); // Decrement reference count of `args_combined`
    Py_XDECREF(init_args);
    Py_XDECREF(init_kwargs);

    // Ensure proper error propagation
    if (new_inst == NULL) {
      return NULL;
    }
    return new_inst;
  }

done:
  return result;
}

// Member definitions; MUST REMOVE
// static PyMemberDef NewTypeMethod_members[] = {
//     {"obj", T_OBJECT_EX, offsetof(NewTypeMethodObject, obj), READONLY,
//      "Instance object"},
//     {"cls", T_OBJECT_EX, offsetof(NewTypeMethodObject, cls), READONLY,
//      "Owner class"},
//     {NULL} // Sentinel
// };

// Deallocation method
static void NewTypeMethod_dealloc(NewTypeMethodObject *self) {
  Py_XDECREF(self->func_get);
  Py_XDECREF(self->wrapped_cls);
  Py_XDECREF(self->obj);
  Py_XDECREF(self->cls);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

// Method definitions
static PyMethodDef NewTypeMethod_methods[] = {{NULL, NULL, 0, NULL}};

// Type definition
PyTypeObject NewTypeMethodType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "newtypemethod.NewTypeMethod",
    .tp_doc = "A descriptor class that wraps around regular methods of a class "
              "to allow instantiation of the subtype if the method returns an "
              "instance of the supertype.",
    .tp_basicsize = sizeof(NewTypeMethodObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)NewTypeMethod_init,
    .tp_dealloc = (destructor)NewTypeMethod_dealloc,
    // .tp_members = NewTypeMethod_members,
    .tp_call = (ternaryfunc)NewTypeMethod_call,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_methods = NewTypeMethod_methods,
    .tp_descr_get = (descrgetfunc)NewTypeMethod_get,
};

// Module definition
static struct PyModuleDef newtypemethodmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "newtypemethod",
    .m_doc =
        "A Module that contains `NewTypeMethod` which is a descriptor class "
        "that wraps around regular methods of a class to allow instantiation "
        "of the subtype if the method returns an instance of the supertype.",
    .m_size = -1,
};

// Module initialization function
PyMODINIT_FUNC PyInit_newtypemethod(void) {
  PyObject *m;
  if (PyType_Ready(&NewTypeMethodType) < 0)
    return NULL;

  m = PyModule_Create(&newtypemethodmodule);
  if (m == NULL)
    return NULL;

  Py_INCREF(&NewTypeMethodType);
  if (PyModule_AddObject(m, "NewTypeMethod", (PyObject *)&NewTypeMethodType) <
      0) {
    Py_DECREF(&NewTypeMethodType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
