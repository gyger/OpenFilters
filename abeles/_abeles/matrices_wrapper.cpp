/*
 *
 *  matrices_wrapper.cpp
 *
 *
 *  Wrap the object and functions provided in matrices.cpp to make them
 *  available to Python in an matrices class.
 *
 *  Copyright (c) 2002-2007,2012,2013 Stephane Larouche.
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
/* new_matrices_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * new_matrices_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	matrices_wrapper_object										*self;

	self = (matrices_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->matrices = NULL;

		/* The presence of a parent indicates that this object share its
		 * C content with another Python object. The parent is then
		 * responsible to delete the C content. It is used when the
		 * matrices are used in monitoring , pre and post matrices or
		 * needles. */
		self->parent = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_matrices_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static int init_matrices_wrapper(matrices_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:matrices.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of matrices, if it exists. */
	if (self->matrices)
	{
		del_matrices(self->matrices);
		self->matrices = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the matrices. */
	self->matrices = new_matrices(self->wvls->wvls);
	if (!self->matrices)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_matrices_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static void dealloc_matrices_wrapper(matrices_wrapper_object *self)
{
	/* If the index has a parent, the parent is responsible to destroy
	 * the C structures. */
	if (self->parent)
	{
		Py_DECREF(self->parent);
	}
	else
	{
		del_matrices(self->matrices);

		Py_XDECREF(self->wvls);

		self->ob_type->tp_free((PyObject*)self);
	}
}


/*********************************************************************/
/*                                                                   */
/* set_matrices_unity_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * set_matrices_unity_wrapper(matrices_wrapper_object *self)
{
	Py_BEGIN_ALLOW_THREADS
	set_matrices_unity(self->matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_matrices_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * set_matrices_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OdO:matrices.set_matrices", &N, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "First argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (N->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_matrices(self->matrices, N->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* multiply_matrices_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * multiply_matrices_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;

	if (!PyArg_ParseTuple(args, "O:matrices.multiply_matrices", &M))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "First argument must be matrices");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	multiply_matrices(self->matrices, M->matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* copy_matrices_wrapper                                             */
/*                                                                   */
/*********************************************************************/
PyObject * copy_matrices_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;

	if (!PyArg_ParseTuple(args, "O:abeles.copy_matrices", &M))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "First argument must be matrices");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	copy_matrices(M->matrices, self->matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef matrices_wrapper_type_methods[] =
{
	{"set_matrices_unity",											(PyCFunction)set_matrices_unity_wrapper,											METH_NOARGS},
	{"set_matrices",														(PyCFunction)set_matrices_wrapper,														METH_VARARGS},
	{"multiply_matrices",												(PyCFunction)multiply_matrices_wrapper,												METH_VARARGS},
	{"copy_matrices",														(PyCFunction)copy_matrices_wrapper,														METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject matrices_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.matrices",																	/* tp_name */
	sizeof(matrices_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_matrices_wrapper,								/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	0,																									/* tp_as_sequence */
	0,																									/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"matrices class",																		/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	matrices_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_matrices_wrapper,										/* tp_init */
	0,																									/* tp_alloc */
	new_matrices_wrapper,																/* tp_new */
};


#ifdef __cplusplus
}
#endif
