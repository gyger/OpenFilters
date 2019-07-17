/*
 *
 *  sin2_wrapper.cpp
 *
 *
 *  Wrapper around functions in sin2.cpp to make them available to
 *  Python in a sin2 class.
 *
 *  Copyright (c) 2002-2007,2009,2012,2013,2015 Stephane Larouche.
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
/* new_sin2_wrapper                                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * new_sin2_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	sin2_wrapper_object												*self;

	self = (sin2_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->sin2 = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_sin2_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static int init_sin2_wrapper(sin2_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:sin2.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of sin2, if it exists. */
	if (self->sin2)
	{
		del_sin2(self->sin2);
		self->sin2 = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the sin2. */
	self->sin2 = new_sin2(self->wvls->wvls);
	if (!self->sin2)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_sin2_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static void dealloc_sin2_wrapper(sin2_wrapper_object *self)
{
	del_sin2(self->sin2);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_sin2_theta_0_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static PyObject * set_sin2_theta_0_wrapper(sin2_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		theta;

	if (!PyArg_ParseTuple(args, "Od:sin2.set_sin2_theta_0", &N, &theta))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	/* Check the value of arguments. */
	if (N->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_sin2_theta_0(self->sin2, N->N, theta);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* sin2_wrapper_length                                               */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t sin2_wrapper_length(sin2_wrapper_object *self)
{
	return self->wvls->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* sin2_wrapper_item                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * sin2_wrapper_item(sin2_wrapper_object *self, Py_ssize_t i)
{
	std::complex<double>											sin2;
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	sin2 = self->sin2->sin2[i];

	REPLACE_NAN_OR_INF(sin2, 0.0);

	item = Py_BuildValue("O", PyComplex_FromDoubles(real(sin2), imag(sin2)));

	return item;
}


/*********************************************************************/
/*                                                                   */
/* sin2_wrapper_subscript                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * sin2_wrapper_subscript(sin2_wrapper_object* self, PyObject* item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	std::complex<double>											sin2;
	PyObject																	*result;
	PyObject																	*element;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->wvls->length;
		return sin2_wrapper_item(self, i);
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
				sin2 = self->sin2->sin2[cur];

				REPLACE_NAN_OR_INF(sin2, 0.0);

				element = Py_BuildValue("O", PyComplex_FromDoubles(real(sin2), imag(sin2)));
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
/* sin2_wrapper_richcompare                                          */
/*                                                                   */
/*********************************************************************/
static PyObject * sin2_wrapper_richcompare(sin2_wrapper_object* self, sin2_wrapper_object* other, int op)
{
	if (!sin2_wrapper_Check(self) || !sin2_wrapper_Check(other))
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
	if (self->wvls->wvls->length != other->wvls->wvls->length)
	{
		if (op == Py_EQ) Py_RETURN_FALSE;
		else Py_RETURN_TRUE;
	}

	/* Otherwise, check item by item. If one item is not equal, the
	 * objects are not equal. */
	for (Py_ssize_t i = 0; i < self->wvls->wvls->length; i++)
	{
		if (self->wvls->wvls->wvls[i] != other->wvls->wvls->wvls[i] || self->sin2->sin2[i] != other->sin2->sin2[i])
		{
			if (op == Py_EQ) Py_RETURN_FALSE;
			else Py_RETURN_TRUE;
		}
	}

	/* The objects are equal. */
	if (op == Py_EQ) Py_RETURN_TRUE;
	else Py_RETURN_FALSE;
}


static PyMethodDef sin2_wrapper_type_methods[] =
{
	{"set_sin2_theta_0",												(PyCFunction)set_sin2_theta_0_wrapper,												METH_VARARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods sin2_wrapper_as_sequence = {
	(lenfunc)sin2_wrapper_length,												/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)sin2_wrapper_item,										/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods sin2_wrapper_as_mapping = {
	(lenfunc)sin2_wrapper_length,												/* mp_length */
	(binaryfunc)sin2_wrapper_subscript,									/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject sin2_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.sin2",																			/* tp_name */
	sizeof(sin2_wrapper_object),												/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_sin2_wrapper,										/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&sin2_wrapper_as_sequence,													/* tp_as_sequence */
	&sin2_wrapper_as_mapping,														/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"sin2 class",																				/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	(richcmpfunc)sin2_wrapper_richcompare,							/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	sin2_wrapper_type_methods,													/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_sin2_wrapper,												/* tp_init */
	0,																									/* tp_alloc */
	new_sin2_wrapper,																		/* tp_new */
};


#ifdef __cplusplus
}
#endif
