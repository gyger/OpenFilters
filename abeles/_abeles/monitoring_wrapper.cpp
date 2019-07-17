/*
 *
 *  monitoring_wrapper.cpp
 *
 *
 *  Wrapper around functions in monitoring.cpp to make them available to
 *  Python in a monitoring_matrices class.
 *
 *  Copyright (c) 2004-2007,2012,2013 Stephane Larouche.
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


#include <Python.h>

#include "_abeles.h"
#include "_abeles_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_monitoring_matrices_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * new_monitoring_matrices_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	monitoring_matrices_wrapper_object				*self;

	self = (monitoring_matrices_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->matrices = NULL;
		self->wrappers = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_monitoring_matrices_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t init_monitoring_matrices_wrapper(monitoring_matrices_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	Py_ssize_t																length, i;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "On:monitoring_matrices.__init__", &wvls, &length))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}

	/* Delete previous instances of matrice wrappers, if they exist. */
	if (self->wrappers)
	{
		for (i = 0; i < self->matrices->length; i++)
			if (self->wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->wrappers[i]);
		free(self->wrappers);
		self->wrappers = NULL;
	}

	/* Delete previous instance of monitoring_matrices, if it exists. */
	if (self->matrices)
	{
		del_monitoring_matrices(self->matrices);
		self->matrices = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the monitoring_matrices. */
	self->matrices = new_monitoring_matrices(wvls->wvls, length);
	if (!self->matrices)
	{
		PyErr_NoMemory();
		return -1;
	}

	/* Make wrappers around the sublayer matrices. The ref count of the
	 * wrappers is decreased (to 0) so that they can be destroyed when
	 * the ref count of self drops to 0. But the ref count of self is
	 * increased first to avoid immediate destruction. */
	self->wrappers = (matrices_wrapper_object **)malloc(self->matrices->length*sizeof(matrices_wrapper_object *));
	if (!self->wrappers)
	{
		PyErr_NoMemory();
		return -1;
	}
	for (i = 0; i < self->matrices->length; i++)
		self->wrappers[i] = NULL;
	for (i = 0; i < self->matrices->length; i++)
	{
		self->wrappers[i] = (matrices_wrapper_object *)matrices_wrapper_type.tp_alloc(&matrices_wrapper_type, 0);
		if (!self->wrappers[i])
		{
			PyErr_NoMemory();
			return -1;
		}
		self->wrappers[i]->wvls = self->wvls;
		self->wrappers[i]->matrices = self->matrices->matrices[i];
		self->wrappers[i]->parent = (PyObject *)self;

		Py_INCREF(self);
		Py_DECREF(self->wrappers[i]);
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_monitoring_matrices_wrapper                               */
/*                                                                   */
/*********************************************************************/
static void dealloc_monitoring_matrices_wrapper(monitoring_matrices_wrapper_object *self)
{
	Py_ssize_t																i;

	if (self->wrappers)
	{
		for (i = 0; i < self->matrices->length; i++)
			if (self->wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->wrappers[i]);
		free(self->wrappers);
	}

	del_monitoring_matrices(self->matrices);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_monitoring_matrices_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * set_monitoring_matrices_wrapper(monitoring_matrices_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																position;
	N_wrapper_object													*N;
	double																		slice_thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "nOdO:monitoring_matrices.set_monitoring_matrices", &position, &N, &slice_thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (N->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}
	if (position < 0 || position >= self->matrices->length)
	{
		PyErr_SetString(PyExc_ValueError, "position out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_monitoring_matrices(self->matrices, position, N->N, slice_thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* multiply_monitoring_matrices_wrapper                              */
/*                                                                   */
/*********************************************************************/
static PyObject * multiply_monitoring_matrices_wrapper(monitoring_matrices_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M1;

	if (!PyArg_ParseTuple(args, "O:monitoring_matrices.multiply_monitoring_matrices", &M1))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	multiply_monitoring_matrices(M1->matrices, self->matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* multiply_monitoring_matrices_cumulative_wrapper                   */
/*                                                                   */
/*********************************************************************/
static PyObject * multiply_monitoring_matrices_cumulative_wrapper(monitoring_matrices_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M1;

	if (!PyArg_ParseTuple(args, "O:monitoring_matrices.multiply_monitoring_matrices_cumulative", &M1))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	multiply_monitoring_matrices_cumulative(M1->matrices, self->matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* monitoring_matrices_wrapper_length                                */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t monitoring_matrices_wrapper_length(monitoring_matrices_wrapper_object *self)
{
	return self->matrices->length;
}


/*********************************************************************/
/*                                                                   */
/* monitoring_matrices_wrapper_item                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * monitoring_matrices_wrapper_item(monitoring_matrices_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->matrices->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	item = (PyObject *)self->wrappers[i];
	Py_INCREF(self);
	Py_INCREF(item);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* monitoring_matrices_wrapper_subscript                             */
/*                                                                   */
/*********************************************************************/
static PyObject * monitoring_matrices_wrapper_subscript(monitoring_matrices_wrapper_object* self, PyObject* item)
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
			i += self->matrices->length;
		return monitoring_matrices_wrapper_item(self, i);
	}
	else if (PySlice_Check(item))
	{
		if (PySlice_GetIndicesEx((PySliceObject*)item, self->matrices->length, &start, &stop, &step, &slicelength) < 0)
			return NULL;

		if (slicelength <= 0)
			return PyList_New(0);

		else
		{
			result = PyList_New(slicelength);
			if (!result) return NULL;

			for (cur = start, i = 0; i < slicelength; cur += step, i++)
			{
				element = (PyObject *)self->wrappers[cur];
				Py_INCREF(self);
				Py_INCREF(element);
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


static PyMethodDef monitoring_matrices_wrapper_type_methods[] =
{
	{"set_monitoring_matrices",									(PyCFunction)set_monitoring_matrices_wrapper,									METH_VARARGS},
	{"multiply_monitoring_matrices",						(PyCFunction)multiply_monitoring_matrices_wrapper,						METH_VARARGS},
	{"multiply_monitoring_matrices_cumulative",	(PyCFunction)multiply_monitoring_matrices_cumulative_wrapper,	METH_VARARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods monitoring_matrices_wrapper_as_sequence = {
	(lenfunc)monitoring_matrices_wrapper_length,				/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)monitoring_matrices_wrapper_item,			/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods monitoring_matrices_wrapper_as_mapping = {
	(lenfunc)monitoring_matrices_wrapper_length,				/* mp_length */
	(binaryfunc)monitoring_matrices_wrapper_subscript,	/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject monitoring_matrices_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.monitoring_matrices",												/* tp_name */
	sizeof(monitoring_matrices_wrapper_object),					/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_monitoring_matrices_wrapper,		/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&monitoring_matrices_wrapper_as_sequence,						/* tp_as_sequence */
	&monitoring_matrices_wrapper_as_mapping,						/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"monitoring_matrices class",												/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	monitoring_matrices_wrapper_type_methods,						/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_monitoring_matrices_wrapper,					/* tp_init */
	0,																									/* tp_alloc */
	new_monitoring_matrices_wrapper,										/* tp_new */
};


#ifdef __cplusplus
}
#endif
