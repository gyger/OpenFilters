/*
 *
 *  wvls_wrapper.c
 *
 *
 *  Wrapper around functions in wvls.cpp to make them available to
 *  Python in a wvls class.
 *
 *  Copyright (c) 2002-2007,2012,2015 Stephane Larouche.
 *
 *  This file is part of OpenFilters.
 *
 *  OpenFilters is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or (at
 *  your option) any later version.
 *
 *  OpenFilters is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 *  USA
 *
 */


#include "Python.h"

#include "_abeles.h"
#include "_abeles_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_wvls_wrapper                                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * new_wvls_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*self;

	self = (wvls_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_wvls_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static int init_wvls_wrapper(wvls_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length;

	if (!PyArg_ParseTuple(args, "n:wvls.__init__", &length))
		return -1;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}

	/* Delete previous instance of spectrum, if it exists. */
	if (self->wvls)
	{
		del_wvls(self->wvls);
		self->wvls = NULL;
	}

	/* Create the wvls. */
	self->wvls = new_wvls(length);
	if (!self->wvls)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_wvls_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static void dealloc_wvls_wrapper(wvls_wrapper_object *self)
{
	del_wvls(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_wvl_wrapper                                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * set_wvl_wrapper(wvls_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																position;
	double																		wvl;

	if (!PyArg_ParseTuple(args, "nd:wvls.set_wvl", &position, &wvl))
		return NULL;

	/* Check the value of the arguments. */
	if (position < 0 || position >= self->wvls->length)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_wvl(self->wvls, position, wvl);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_wvls_by_range_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * set_wvls_by_range_wrapper(wvls_wrapper_object *self, PyObject *args)
{
	double																		from, by;

	if (!PyArg_ParseTuple(args, "dd:wvls.set_wvls_by_range", &from, &by))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	set_wvls_by_range(self->wvls, from, by);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* wvl_wrapper_index                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * wvl_wrapper_index(wvls_wrapper_object *self, PyObject *args)
{
	double																		wavelength;
	Py_ssize_t																i;

	if (!PyArg_ParseTuple(args, "d:index", &wavelength))
		return NULL;

	for (i = 0; i < self->wvls->length; i++)
	{
		if (wavelength == self->wvls->wvls[i])
			return PyInt_FromLong((long)i);
	}

	PyErr_SetString(PyExc_ValueError, "wvls.index(wvl): wvl not in wvls");
	return NULL;
}


/*********************************************************************/
/*                                                                   */
/* wvls_wrapper_length                                               */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t wvls_wrapper_length(wvls_wrapper_object *self)
{
	return self->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* wvls_wrapper_item                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * wvls_wrapper_item(wvls_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	item = PyFloat_FromDouble(self->wvls->wvls[i]);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* wvls_wrapper_contains                                             */
/*                                                                   */
/*********************************************************************/
static int wvls_wrapper_contains(wvls_wrapper_object *self, PyObject *element)
{
	double																		wavelength;
	Py_ssize_t																i;
	int 																			cmp;

	if (!PyFloat_Check(element))
		return 0;

	wavelength = PyFloat_AsDouble(element);

	for (i = 0, cmp = 0; cmp == 0 && i < self->wvls->length; i++)
		cmp = (wavelength == self->wvls->wvls[i]);

	return cmp;
}


/*********************************************************************/
/*                                                                   */
/* wvls_wrapper_subscript                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * wvls_wrapper_subscript(wvls_wrapper_object* self, PyObject* item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	PyObject																	*result;
	PyObject																	*element;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->length;
		return wvls_wrapper_item(self, i);
	}
	else if (PySlice_Check(item))
	{
		if (PySlice_GetIndicesEx((PySliceObject*)item, self->wvls->length, &start, &stop, &step, &slicelength) < 0)
			return NULL;

		if (slicelength <= 0)
			return PyList_New(0);

		else
		{
			result = PyList_New(slicelength);
			if (!result) return NULL;

			for (cur = start, i = 0; i < slicelength; cur += step, i++)
			{
				element = PyFloat_FromDouble(self->wvls->wvls[cur]);
				PyList_SetItem(result, i, element);
			}

			return result;
		}
	}
	else
	{
		PyErr_SetString(PyExc_TypeError, "indices must be integers");
		return NULL;
	}
}


/*********************************************************************/
/*                                                                   */
/* wvls_wrapper_richcompare                                          */
/*                                                                   */
/*********************************************************************/
static PyObject * wvls_wrapper_richcompare(wvls_wrapper_object* self, wvls_wrapper_object* other, int op)
{
	if (!wvls_wrapper_Check(self) || !wvls_wrapper_Check(other))
	{
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}

	/* Only equality and non-equality operators are allowed. */
	if (!(op == Py_EQ || op == Py_NE))
	{
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}

	/* If the length of the two objects is different, they are not equal. */
	if (self->wvls->length != other->wvls->length)
	{
		if (op == Py_EQ) Py_RETURN_FALSE;
		else Py_RETURN_TRUE;
	}

	/* Otherwise, check item by item. If one item is not equal, the
	 * objects are not equal. */
	for (Py_ssize_t i = 0; i < self->wvls->length; i++)
	{
		if (self->wvls->wvls[i] != other->wvls->wvls[i])
		{
			if (op == Py_EQ) Py_RETURN_FALSE;
			else Py_RETURN_TRUE;
		}
	}

	/* The objects are equal. */
	if (op == Py_EQ) Py_RETURN_TRUE;
	else Py_RETURN_FALSE;
}


static PyMethodDef wvls_wrapper_type_methods[] =
{
	{"set_wvl",																	(PyCFunction)set_wvl_wrapper,																	METH_VARARGS},
	{"set_wvls_by_range",												(PyCFunction)set_wvls_by_range_wrapper,												METH_VARARGS},
	{"index",																		(PyCFunction)wvl_wrapper_index,																METH_VARARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods wvls_wrapper_as_sequence = {
	(lenfunc)wvls_wrapper_length,												/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)wvls_wrapper_item,										/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0,																									/* sq_ass_slice */
	(objobjproc)wvls_wrapper_contains,									/* sq_contains */
	0,																									/* sq_inplace_concat */
	0,																									/* sq_inplace_repeat */
};


static PyMappingMethods wvls_wrapper_as_mapping = {
	(lenfunc)wvls_wrapper_length,												/* mp_length */
	(binaryfunc)wvls_wrapper_subscript,									/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject wvls_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.wvls",																			/* tp_name */
	sizeof(wvls_wrapper_object),												/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_wvls_wrapper,										/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&wvls_wrapper_as_sequence,													/* tp_as_sequence */
	&wvls_wrapper_as_mapping,														/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"wvls class",																				/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	(richcmpfunc)wvls_wrapper_richcompare,							/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	wvls_wrapper_type_methods,													/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_wvls_wrapper,												/* tp_init */
	0,																									/* tp_alloc */
	new_wvls_wrapper,																		/* tp_new */
};


#ifdef __cplusplus
}
#endif
