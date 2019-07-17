/*
 *
 *  r_and_t_wrapper.cpp
 *
 *
 *  Wrapper around functions in r_and_t.cpp to make them available to
 *  Python in a r_and_t class.
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

#include "_abeles.h"
#include "_abeles_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_r_and_t_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * new_r_and_t_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	r_and_t_wrapper_object										*self;

	self = (r_and_t_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->r_and_t = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_r_and_t_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static int init_r_and_t_wrapper(r_and_t_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:r_and_t.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of r_and_t, if it exists. */
	if (self->r_and_t)
	{
		del_r_and_t(self->r_and_t);
		self->r_and_t = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the r_and_t. */
	self->r_and_t = new_r_and_t(self->wvls->wvls);
	if (!self->r_and_t)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_r_and_t_wrapper                                           */
/*                                                                   */
/*********************************************************************/
static void dealloc_r_and_t_wrapper(r_and_t_wrapper_object *self)
{
	del_r_and_t(self->r_and_t);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* calculate_r_and_t_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_r_and_t_wrapper(r_and_t_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOO:r_and_t.calculate_r_and_t", &M, &N_m, &N_s, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_m))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_r_and_t(self->r_and_t, M->matrices, N_m->N, N_s->N, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_r_and_t_reverse_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_r_and_t_reverse_wrapper(r_and_t_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOO:r_and_t.calculate_r_and_t_reverse", &M, &N_m, &N_s, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_m))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_r_and_t_reverse(self->r_and_t, M->matrices, N_m->N, N_s->N, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef r_and_t_wrapper_type_methods[] =
{
	{"calculate_r_and_t",												(PyCFunction)calculate_r_and_t_wrapper,												METH_VARARGS},
	{"calculate_r_and_t_reverse",								(PyCFunction)calculate_r_and_t_reverse_wrapper,								METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject r_and_t_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.r_and_t",																		/* tp_name */
	sizeof(r_and_t_wrapper_object),											/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_r_and_t_wrapper,								/* tp_dealloc */
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
	"r_and_t class",																		/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	r_and_t_wrapper_type_methods,												/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_r_and_t_wrapper,											/* tp_init */
	0,																									/* tp_alloc */
	new_r_and_t_wrapper,																/* tp_new */
};


#ifdef __cplusplus
}
#endif
