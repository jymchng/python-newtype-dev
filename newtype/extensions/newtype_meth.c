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
      DEBUG_PRINT("`self->wrapped_cls`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(self->wrapped_cls)));
      DEBUG_PRINT("`self->obj`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(self->obj)));
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

  // Need to save `result.__dict__` so that we can copy over the attributes
  // from `self->obj` to `new_inst`, if `self->obj` is not NULL because
  // constructor will remove the `__dict__` attribute from `result`
  PyObject* result_dict = NULL;
  if (PyObject_HasAttrString(result, "__dict__")) {
    result_dict = PyObject_GetAttrString(result, "__dict__");
  }

  PyObject* result_slots = NULL;
  if (PyObject_HasAttrString(result, "__slots__")) {
    result_slots = PyObject_GetAttrString(result, "__slots__");
  }

  if (self->obj == NULL && self->cls == NULL) {
    Py_XDECREF(result_dict);  // Clean up before goto
    goto done;
  }

  if (self->cls && PyObject_TypeCheck(result, self->cls)) {
    Py_XDECREF(result_dict);  // Clean up before goto
    goto done;
  }

  DEBUG_PRINT("`result` is not an instance of `self->cls`\n");
  if (PyObject_IsInstance(result, self->wrapped_cls))
  {  // now we try to build an instance of the subtype
    DEBUG_PRINT("`result` is an instance of `self->wrapped_cls`\n");
    PyObject *init_args, *init_kwargs;
    PyObject* new_inst;
    PyObject* args_combined = NULL;
    Py_ssize_t args_len = 0;

    if (self->obj == NULL) {
      PyObject* first_elem;

      if (self->cls == NULL) {
        goto done;
      }

      if (PyTuple_Size(args) > 0) {  // Got arguments
        first_elem = PyTuple_GetItem(args, 0);
        Py_XINCREF(
            first_elem);  // Increment reference count of the first element
        DEBUG_PRINT("`first_elem`: %s\n",
                    PyUnicode_AsUTF8(PyObject_Repr(first_elem)));
      } else {  // `args` is empty here, then we are done actually
        DEBUG_PRINT("`args` is empty\n");
        goto done;
      };
      if (PyObject_IsInstance(first_elem, (PyObject*)self->cls)) {
        init_args = PyObject_GetAttrString(first_elem, NEWTYPE_INIT_ARGS_STR);
        init_kwargs =
            PyObject_GetAttrString(first_elem, NEWTYPE_INIT_KWARGS_STR);
        DEBUG_PRINT("`init_args`: %s\n",
                    PyUnicode_AsUTF8(PyObject_Repr(init_args)));
        DEBUG_PRINT("`init_kwargs`: %s\n",
                    PyUnicode_AsUTF8(PyObject_Repr(init_kwargs)));
      } else {  // first element is not the subtype, so we are done also
        DEBUG_PRINT("`first_elem` is not the subtype\n");
        goto done;
      }
      Py_XDECREF(first_elem);
    } else {  // `self->obj` is not NULL

      DEBUG_PRINT("`self->obj` is not NULL\n");
      init_args = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_ARGS_STR);
      init_kwargs = PyObject_GetAttrString(self->obj, NEWTYPE_INIT_KWARGS_STR);
      DEBUG_PRINT("`init_args`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(init_args)));
      DEBUG_PRINT("`init_kwargs`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(init_kwargs)));
    }

    if (init_args != NULL) {
      DEBUG_PRINT("`init_args` is not NULL\n");
      args_len = PyTuple_Size(init_args);
      DEBUG_PRINT("`args_len`: %zd\n", args_len);
      Py_ssize_t combined_args_len = 1 + args_len;
      DEBUG_PRINT("`combined_args_len`: %zd\n", combined_args_len);
      args_combined = PyTuple_New(combined_args_len);
      DEBUG_PRINT("`args_combined`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(args_combined)));
      if (args_combined == NULL) {
        Py_XDECREF(init_args);
        Py_XDECREF(init_kwargs);
        Py_DECREF(result);
        DEBUG_PRINT("`args_combined` is NULL\n");
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
          DEBUG_PRINT("`item` is NULL\n");
          Py_DECREF(args_combined);
          Py_XDECREF(init_args);
          Py_XDECREF(init_kwargs);
          return NULL;
        }
        DEBUG_PRINT("`item`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(item)));
        Py_INCREF(item);  // Increase reference count
        PyTuple_SET_ITEM(args_combined,
                         i + 1,
                         item);  // `item` is now owned by `args_combined`
      }
      DEBUG_PRINT("`args_combined`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(args_combined)));
    }

    if (init_args == NULL || init_kwargs == NULL) {
      DEBUG_PRINT("`init_args` or `init_kwargs` is NULL\n");
    };

    if (init_kwargs != NULL) {
      DEBUG_PRINT("`init_kwargs`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(init_kwargs)));
    };

    // If `args_combined` is NULL, create a new tuple with one item
    // and set `result` as the first item of the tuple
    if (init_args == NULL) {
      DEBUG_PRINT("`init_args` is NULL\n");

      if (PyObject_SetAttrString(
              self->obj, NEWTYPE_INIT_ARGS_STR, PyTuple_New(0))
          < 0)
      {
        result = NULL;
        goto done;
      }
      if (PyObject_SetAttrString(
              self->obj, NEWTYPE_INIT_KWARGS_STR, PyDict_New())
          < 0)
      {
        result = NULL;
        goto done;
      }

      args_combined = PyTuple_New(1);  // Allocate tuple with one element
      Py_INCREF(result);
      PyTuple_SET_ITEM(args_combined, 0, result);
      DEBUG_PRINT("`args_combined`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(args_combined)));
      new_inst =
          PyObject_Call((PyObject*)self->cls, args_combined, init_kwargs);
      if (new_inst == NULL) {
        DEBUG_PRINT("`new_inst` is NULL\n");
        Py_DECREF(result);
        Py_DECREF(self->obj);
        Py_DECREF(args_combined);
        return NULL;
      }
      Py_DECREF(result);
      Py_DECREF(self->obj);
      Py_DECREF(args_combined);
      DEBUG_PRINT("`new_inst`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_inst)));
      return new_inst;
    }

    new_inst = PyObject_Call((PyObject*)self->cls, args_combined, init_kwargs);

    // Clean up
    Py_XDECREF(args_combined);  // Decrement reference count of `args_combined`
    Py_XDECREF(init_args);
    Py_XDECREF(init_kwargs);

    DEBUG_PRINT("`new_inst`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(new_inst)));

    // Only proceed if we have all required objects and dictionaries
    if (self->obj != NULL && result != NULL && new_inst != NULL
        && result_dict != NULL)
    {
      PyObject* key = NULL;
      PyObject* value = NULL;

      // Get new_inst's dictionary
      if (!PyObject_HasAttrString(new_inst, "__dict__")) {
        goto cleanup;
      }

      PyObject* new_dict = NULL;
      new_dict = PyObject_GetAttrString(new_inst, "__dict__");
      if (new_dict == NULL) {
        Py_XDECREF(new_dict);
        goto cleanup;
      }

      DEBUG_PRINT("`new_dict`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_dict)));
      DEBUG_PRINT("`result_dict`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(result_dict)));

      // Get the keys from new_dict
      PyObject* new_keys = NULL;
      new_keys = PyDict_Keys(new_dict);
      if (new_keys == NULL) {
        Py_XDECREF(new_keys);
        goto cleanup;
      }

      DEBUG_PRINT("`new_keys`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_keys)));

      PyObject* iter = NULL;
      iter = PyObject_GetIter(new_keys);
      if (iter == NULL) {
        Py_XDECREF(iter);
        goto cleanup;
      }

      while ((key = PyIter_Next(iter)) != NULL) {
        DEBUG_PRINT("`key`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(key)));

        if (PyDict_GetItem(result_dict, key) == NULL) {
          DEBUG_PRINT("Key: %s is not in result_dict\n",
                      PyUnicode_AsUTF8(PyObject_Repr(key)));

          if (PyObject_HasAttr(self->obj, key)) {
            value = PyObject_GetAttr(self->obj, key);
            if (value != NULL) {
              if (PyObject_SetAttr(new_inst, key, value) >= 0) {
                DEBUG_PRINT("`key` = `%s`, `value` = `%s` has been set\n",
                            PyUnicode_AsUTF8(PyObject_Repr(key)),
                            PyUnicode_AsUTF8(PyObject_Repr(value)));
              }
              Py_DECREF(value);
            }
          }
        }
        Py_DECREF(key);
        key = NULL;  // Reset for next iteration
      }

    cleanup:
      Py_XDECREF(key);  // In case loop exited with error
    }  // end of if (self->obj != NULL && result != NULL && new_inst != NULL
    // && result_dict != NULL)

    // if instance of the subtype has `__slots__` (and/or has `__dict__`)
    // but result does not
    if (self->obj != NULL && result != NULL && new_inst != NULL
        && result_slots != NULL)
    {
      PyObject* new_slots = NULL;
      PyObject* new_dict = NULL;
      PyObject* new_keys = NULL;

      PyObject* iter_slots = NULL;
      PyObject* iter_dict = NULL;
      PyObject* key = NULL;
      PyObject* value = NULL;

      // Get new_inst's slots
      if (!PyObject_HasAttrString(new_inst, "__slots__")) {
        goto cleanup_for_slots;
      }
      new_slots = PyObject_GetAttrString(new_inst, "__slots__");
      if (new_slots == NULL) {
        goto cleanup_for_slots;
      }

      DEBUG_PRINT("`new_slots`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_slots)));
      DEBUG_PRINT("`result_dict`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(result_slots)));

      DEBUG_PRINT("`new_slots`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_slots)));

      iter_slots = PyObject_GetIter(new_slots);
      if (iter_slots == NULL) {
        goto cleanup_for_slots;
      }

      while ((key = PyIter_Next(iter_slots)) != NULL) {
        DEBUG_PRINT("`key`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(key)));

        // Check if key is not in result_slots
        if (PySequence_Contains(result_slots, key) == 0) {
          DEBUG_PRINT("Key: %s is not in result_slots = %s\n",
                      PyUnicode_AsUTF8(PyObject_Repr(key)),
                      PyUnicode_AsUTF8(PyObject_Repr(result_slots)));

          if (PyObject_HasAttr(self->obj, key)) {
            value = PyObject_GetAttr(self->obj, key);
            if (value != NULL) {
              if (PyObject_SetAttr(new_inst, key, value) >= 0) {
                DEBUG_PRINT("`key` = `%s`, `value` = `%s` has been set\n",
                            PyUnicode_AsUTF8(PyObject_Repr(key)),
                            PyUnicode_AsUTF8(PyObject_Repr(value)));
              }
              Py_DECREF(value);
              value = NULL;  // Reset value for next iteration
            }
          }
        }
        Py_DECREF(key);
        key = NULL;  // Reset key for next iteration
      }  // end of while ((key = PyIter_Next(iter_slots)) != NULL), slots are
         // successfully copied

      // Get `new_inst`'s dictionary
      if (!PyObject_HasAttrString(new_inst, "__dict__")) {
        goto cleanup_for_slots;
      }
      new_dict = PyObject_GetAttrString(new_inst, "__dict__");
      if (new_dict == NULL) {
        goto cleanup_for_slots;
      }

      DEBUG_PRINT("`new_dict`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_dict)));

      // Get the keys from new_dict
      new_keys = PyDict_Keys(new_dict);
      if (new_keys == NULL) {
        goto cleanup_for_slots;
      }

      DEBUG_PRINT("`new_keys`: %s\n",
                  PyUnicode_AsUTF8(PyObject_Repr(new_keys)));

      iter_dict = PyObject_GetIter(new_keys);
      if (iter_dict == NULL) {
        goto cleanup_for_slots;
      }

      while ((key = PyIter_Next(iter_dict)) != NULL) {
        DEBUG_PRINT("`key`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(key)));

        if (PySequence_Contains(result_slots, key) == 0) {
          DEBUG_PRINT("Key: %s is not in result_dict\n",
                      PyUnicode_AsUTF8(PyObject_Repr(key)));

          if (PyObject_HasAttr(self->obj, key)) {
            value = PyObject_GetAttr(self->obj, key);
            if (value != NULL) {
              if (PyObject_SetAttr(new_inst, key, value) >= 0) {
                DEBUG_PRINT("`key` = `%s`, `value` = `%s` has been set\n",
                            PyUnicode_AsUTF8(PyObject_Repr(key)),
                            PyUnicode_AsUTF8(PyObject_Repr(value)));
              }
              Py_DECREF(value);
            }
          }
        }
        Py_DECREF(key);
        key = NULL;  // Reset for next iteration
      }  // end of while ((key = PyIter_Next(iter_dict)) != NULL), dict is
         // successfully copied

    cleanup_for_slots:
      Py_XDECREF(new_dict);
      Py_XDECREF(new_keys);
      Py_XDECREF(new_slots);

      Py_XDECREF(key);  // In case loop exited with error
      Py_XDECREF(iter_slots);
      Py_XDECREF(iter_dict);
    }  // end of if (self->obj != NULL && result != NULL && new_inst != NULL
    // && result_slots != NULL)

    Py_XDECREF(result_dict);
    DEBUG_PRINT("`new_inst`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(new_inst)));
    return new_inst;
  }

done:
  Py_XINCREF(result);
  DEBUG_PRINT("DONE! `result`: %s\n", PyUnicode_AsUTF8(PyObject_Repr(result)));
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
