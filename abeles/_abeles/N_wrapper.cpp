/*
 *
 *  N_wrapper.cpp
 *
 *
 *  Wrapper around functions in N_mixture.cpp to make them available to
 *  Python in a N class.
 *
 *  Copyright (c) 2002-2007,2009,2012,2013 Stephane Larouche.
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
#include <complex>

#include "_abeles.h"
#include "_abeles_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_N_wrapper                                                     */
/*                                                                   */
/*********************************************************************/
static PyObject * new_N_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	N_wrapper_object													*self;

	self = (N_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->N = NULL;

		/* The presence of a parent indicates that this object share its
		 * C content with another Python object. The parent is then
		 * responsible to delete the C content. It is used when the index
		 * represents a mixture. */
		self->parent = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_N_wrapper                                                    */
/*                                                                   */
/*********************************************************************/
static int init_N_wrapper(N_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:N.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of N, if it exists. */
	if (self->N)
	{
		del_N(self->N);
		self->N = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the M. */
	self->N = new_N(self->wvls->wvls);
	if (!self->N)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_N_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static void dealloc_N_wrapper(N_wrapper_object *self)
{
	/* If the index has a parent, the parent is responsible to destroy
	 * the C structures. */
	if (self->parent)
	{
		Py_DECREF(self->parent);
	}
	else
	{
		del_N(self->N);

		Py_XDECREF(self->wvls);

		self->ob_type->tp_free((PyObject*)self);
	}
}


/*********************************************************************/
/*                                                                   */
/* copy_wrapper                                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * copy_wrapper(N_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;

	if (!PyArg_ParseTuple(args, "O:N.copy", &N))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	/* Check the value of the arguments. */
	if (N->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	N_copy(self->N, N->N);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* N_wrapper_length                                                  */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t N_wrapper_length(N_wrapper_object *self)
{
	return self->wvls->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* N_wrapper_item                                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * N_wrapper_item(N_wrapper_object *self, Py_ssize_t i)
{
	std::complex<double>											N;
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	N = self->N->N[i];

	REPLACE_NAN_OR_INF(N, 0.0);

	item = Py_BuildValue("O", PyComplex_FromDoubles(real(N), imag(N)));

	return item;
}


/*********************************************************************/
/*                                                                   */
/* N_wrapper_subscript                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * N_wrapper_subscript(N_wrapper_object* self, PyObject* item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	std::complex<double>											N;
	PyObject																	*result;
	PyObject																	*element;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->wvls->length;
		return N_wrapper_item(self, i);
	}
	else if (PySlice_Check(item))
	{
		if (PySlice_GetIndicesEx((PySliceObject*)item, self->wvls->wvls->length, &start, &stop, &step, &slicelength) < 0)
			return NULL;

		if (slicelength <= 0)
			return PyList_New(0);

		else
		{
			result = PyList_New(slicelength);
			if (!result) return NULL;

			for (cur = start, i = 0; i < slicelength; cur += step, i++)
			{
				N = self->N->N[cur];

				REPLACE_NAN_OR_INF(N, 0.0);

				element = Py_BuildValue("O", PyComplex_FromDoubles(real(N), imag(N)));
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


static PyMethodDef N_wrapper_type_methods[] =
{
	{"copy",																		(PyCFunction)copy_wrapper,																		METH_VARARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods N_wrapper_as_sequence = {
	(lenfunc)N_wrapper_length,													/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)N_wrapper_item,												/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods N_wrapper_as_mapping = {
	(lenfunc)N_wrapper_length,													/* mp_length */
	(binaryfunc)N_wrapper_subscript,										/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject N_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.N",																					/* tp_name */
	sizeof(N_wrapper_object),														/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_N_wrapper,											/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&N_wrapper_as_sequence,															/* tp_as_sequence */
	&N_wrapper_as_mapping,															/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"n class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	N_wrapper_type_methods,															/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_N_wrapper,														/* tp_init */
	0,																									/* tp_alloc */
	new_N_wrapper,																			/* tp_new */
};


#ifdef __cplusplus
}
#endif
