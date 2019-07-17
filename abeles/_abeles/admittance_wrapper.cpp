/*
 *
 *  admittance_wrapper.cpp
 *
 *
 *  Wrapper around functions in admittance.cpp to make them available to
 *  Python in an admittance class.
 *
 *  Copyright (c) 2004-2007,2009,2012,2013 Stephane Larouche.
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
/* new_admittance_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * new_admittance_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	admittance_wrapper_object									*self;

	self = (admittance_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->admittance = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_admittance_wrapper                                           */
/*                                                                   */
/*********************************************************************/
static int init_admittance_wrapper(admittance_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:admittance.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of admittance, if it exists. */
	if (self->admittance)
	{
		del_admittance(self->admittance);
		self->admittance = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the admittance. */
	self->admittance = new_admittance(self->wvls->wvls);
	if (!self->admittance)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_admittance_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static void dealloc_admittance_wrapper(admittance_wrapper_object *self)
{
	del_admittance(self->admittance);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free(self);
}


/*********************************************************************/
/*                                                                   */
/* calculate_admittance_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_admittance_wrapper(admittance_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOd:admittance.calculate_admittance", &M, &N_s, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_admittance(self->admittance, M->matrices, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* admittance_wrapper_length                                         */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t admittance_wrapper_length(admittance_wrapper_object *self)
{
	return self->wvls->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* admittance_wrapper_item                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * admittance_wrapper_item(admittance_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;
	std::complex<double>											admittance;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	admittance = self->admittance->data[i];

	REPLACE_NAN_OR_INF(admittance, 0.0);

	item = PyComplex_FromDoubles(real(admittance), imag(admittance));

	return item;
}


/*********************************************************************/
/*                                                                   */
/* admittance_wrapper_subscript                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * admittance_wrapper_subscript(admittance_wrapper_object *self, PyObject *item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	PyObject																	*result;
	PyObject																	*element;
	std::complex<double>											admittance;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->wvls->length;
		return admittance_wrapper_item(self, i);
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
				admittance = self->admittance->data[cur];

				REPLACE_NAN_OR_INF(admittance, 0.0);

				element = PyComplex_FromDoubles(real(admittance), imag(admittance));
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


static PySequenceMethods admittance_wrapper_as_sequence = {
	(lenfunc)admittance_wrapper_length,									/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)admittance_wrapper_item,							/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods admittance_wrapper_as_mapping = {
	(lenfunc)admittance_wrapper_length,									/* mp_length */
	(binaryfunc)admittance_wrapper_subscript,						/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


static PyMethodDef admittance_wrapper_type_methods[] =
{
	{"calculate_admittance",										(PyCFunction)calculate_admittance_wrapper,										METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject admittance_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.admittance",																/* tp_name */
	sizeof(admittance_wrapper_object),									/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_admittance_wrapper,							/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&admittance_wrapper_as_sequence,										/* tp_as_sequence */
	&admittance_wrapper_as_mapping,											/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"admittance class",																	/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	admittance_wrapper_type_methods,										/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_admittance_wrapper,									/* tp_init */
	0,																									/* tp_alloc */
	new_admittance_wrapper,															/* tp_new */
};


#ifdef __cplusplus
}
#endif
