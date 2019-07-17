/*
 *
 *  N_mixture_wrapper.cpp
 *
 *
 *  Wrapper around functions in N_mixture.cpp to make them available to
 *  Python in a N_mixture class.
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

#include "_abeles.h"
#include "_abeles_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_N_mixture_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * new_N_mixture_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	N_mixture_wrapper_object									*self;

	self = (N_mixture_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->dispersion = NULL;
		self->N_mixture = NULL;
		self->N_wrapper = NULL;
		self->dN_wrapper = NULL;
		self->N_graded_wrappers = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_N_mixture_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static int init_N_mixture_wrapper(N_mixture_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	PyObject																	*dispersion;
	wvls_wrapper_object												*wvls;
	Py_ssize_t																i;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "OO:N_mixture.__init__", &dispersion, &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!(constant_mixture_wrapper_Check(dispersion) || table_mixture_wrapper_Check(dispersion) || Cauchy_mixture_wrapper_Check(dispersion) || Sellmeier_mixture_wrapper_Check(dispersion)))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be a mixture");
		return -1;
	}
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be wvls");
		return -1;
	}

	/* Delete previous instances of N_graded wrappers, if they exist. */
	if (self->N_graded_wrappers)
	{
		for (i = 0; i < self->N_mixture->length; i++)
			if (self->N_graded_wrappers[i])
				N_wrapper_type.tp_free((PyObject*)self->N_graded_wrappers[i]);
		free(self->N_graded_wrappers);
		self->N_graded_wrappers = NULL;
	}

	/* Decrease ref count for N and dN wrappers, if they exist. */
	Py_XDECREF(self->N_wrapper);
	Py_XDECREF(self->dN_wrapper);

	/* Keep a local copies of dispersion and wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);
	tmp = (PyObject *)self->dispersion;
	Py_INCREF(dispersion);
	self->dispersion = dispersion;
	Py_XDECREF(tmp);

	/* Create the appropriate N_mixture. */
	if (constant_mixture_wrapper_Check(self->dispersion))
		self->N_mixture = new_N_mixture_constant(((constant_mixture_wrapper_object *)self->dispersion)->dispersion, self->wvls->wvls);
	else if (table_mixture_wrapper_Check(self->dispersion))
		self->N_mixture = new_N_mixture_table(((table_mixture_wrapper_object *)self->dispersion)->dispersion, self->wvls->wvls);
	else if (Cauchy_mixture_wrapper_Check(self->dispersion))
		self->N_mixture = new_N_mixture_Cauchy(((Cauchy_mixture_wrapper_object *)self->dispersion)->dispersion, self->wvls->wvls);
	else if (Sellmeier_mixture_wrapper_Check(self->dispersion))
		self->N_mixture = new_N_mixture_Sellmeier(((Sellmeier_mixture_wrapper_object *)self->dispersion)->dispersion, self->wvls->wvls);
	if (!self->N_mixture)
	{
		PyErr_NoMemory();
		return -1;
	}

	/* Create N_wrapper objects to access directly N and dN. The steps
	 * for graded-index layers are only defined on demand. */
	self->N_wrapper = (N_wrapper_object *)N_wrapper_type.tp_alloc(&N_wrapper_type, 0);
	if (!self->N_wrapper)
	{
		PyErr_NoMemory();
		return -1;
	}
	self->N_wrapper->wvls = wvls;
	self->N_wrapper->N = get_N_mixture(self->N_mixture);
	self->N_wrapper->parent = (PyObject *)self;
	self->dN_wrapper = (N_wrapper_object *)N_wrapper_type.tp_alloc(&N_wrapper_type, 0);;
	if (!self->dN_wrapper)
	{
		PyErr_NoMemory();
		return -1;
	}
	self->dN_wrapper->wvls = wvls;
	self->dN_wrapper->N = get_dN_mixture(self->N_mixture);
	self->dN_wrapper->parent = (PyObject *)self;
	self->N_graded_wrappers = NULL;

	/* Decrease the ref count of N and dN (to 0) so that they can be
	 * destroyed with the ref count of self drops to 0. But first
	 * increase the ref count of self to avoid immediate destruction. */
	Py_INCREF(self);
	Py_DECREF(self->N_wrapper);
	Py_INCREF(self);
	Py_DECREF(self->dN_wrapper);

	return 0;
}

/*********************************************************************/
/*                                                                   */
/* dealloc_N_mixture_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static void dealloc_N_mixture_wrapper(N_mixture_wrapper_object *self)
{
	Py_ssize_t																i;

	if (self->N_wrapper)
		N_wrapper_type.tp_free((PyObject*)self->N_wrapper);
	if (self->dN_wrapper)
		N_wrapper_type.tp_free((PyObject*)self->dN_wrapper);
	if (self->N_graded_wrappers)
	{
		for (i = 0; i < self->N_mixture->length; i++)
			if (self->N_graded_wrappers[i])
				N_wrapper_type.tp_free((PyObject*)self->N_graded_wrappers[i]);
		free(self->N_graded_wrappers);
	}

	del_N_mixture(self->N_mixture);

	Py_XDECREF(self->wvls);
	Py_XDECREF(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* prepare_N_mixture_graded_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_N_mixture_graded_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																length, i;
	N_type																		*N_graded;

	if (!PyArg_ParseTuple(args, "n:N_mixture.prepare_N_mixture_graded", &length))
		return NULL;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return NULL;
	}

	/* Delete previous instances of N_graded wrappers, if they exist. */
	if (self->N_graded_wrappers)
	{
		for (i = 0; i < self->N_mixture->length; i++)
			if (self->N_graded_wrappers[i])
				N_wrapper_type.tp_free((PyObject*)self->N_graded_wrappers[i]);
		free(self->N_graded_wrappers);
		self->N_graded_wrappers = NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	N_graded = prepare_N_mixture_graded(self->N_mixture, length);
	Py_END_ALLOW_THREADS

	if (!N_graded)
		return PyErr_NoMemory();

	/* Make a permanent list of N_wrapper objects to furnish them faster.*/
	self->N_graded_wrappers = (N_wrapper_object **)malloc(self->N_mixture->length*sizeof(N_wrapper_object *));
	if (!self->N_graded_wrappers)
		return PyErr_NoMemory();
	for (i = 0; i < self->N_mixture->length; i++)
		self->N_graded_wrappers[i] = NULL;
	for (i = 0; i < self->N_mixture->length; i++)
	{
		self->N_graded_wrappers[i] = (N_wrapper_object *)N_wrapper_type.tp_alloc(&N_wrapper_type, 0);
		if (!self->N_graded_wrappers[i])
			return PyErr_NoMemory();
		self->N_graded_wrappers[i]->wvls = self->wvls;
		self->N_graded_wrappers[i]->N = &(N_graded[i]);
		self->N_graded_wrappers[i]->parent = (PyObject *)self;

		/* Decrease the ref count of N_graded[i] (to 0) so that they can be
		 * destroyed when the ref count of self drops to 0. But first
		 * increase the ref count of self to avoid immediate destruction. */
		Py_INCREF(self);
		Py_DECREF(self->N_graded_wrappers[i]);
	}

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* N_mixture_graded_is_prepared_wrapper                              */
/*                                                                   */
/*********************************************************************/
static PyObject * N_mixture_graded_is_prepared_wrapper(N_mixture_wrapper_object *self)
{
	if (N_mixture_graded_is_prepared(self->N_mixture))
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_mixture_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "dd:N_mixture.set_N_mixture", &n_wvl, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_mixture(self->N_mixture, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_by_x_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_mixture_by_x_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	double																		x;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "d:N_mixture.set_N_mixture_by_x", &x))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_mixture_by_x(self->N_mixture, x);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_mixture_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dN_mixture_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "dd:N_mixture.set_dN_mixture", &n_wvl, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	return_value = set_dN_mixture(self->N_mixture, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_graded_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_mixture_graded_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																position;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "ndd:N_mixture.set_N_mixture_graded", &position, &n_wvl, &wvl))
		return NULL;

	/* Check the value of the arguments. */
	if (position < 0 || position >= self->N_mixture->length)
	{
		PyErr_SetString(PyExc_TypeError, "position out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_mixture_graded(self->N_mixture, position, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_N_mixture_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * get_N_mixture_wrapper(N_mixture_wrapper_object *self)
{
	Py_INCREF(self->N_wrapper);
	Py_INCREF(self);

	return (PyObject *)self->N_wrapper;
}


/*********************************************************************/
/*                                                                   */
/* get_dN_mixture_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * get_dN_mixture_wrapper(N_mixture_wrapper_object *self)
{
	Py_INCREF(self->dN_wrapper);
	Py_INCREF(self);

	return (PyObject *)self->dN_wrapper;
}


/*********************************************************************/
/*                                                                   */
/* get_N_mixture_graded_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * get_N_mixture_graded_wrapper(N_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																position;

	if (!PyArg_ParseTuple(args, "n:N_mixture.get_N_mixture_graded", &position))
		return NULL;

	/* Check the value of the arguments. */
	if (position < 0 || position >= self->N_mixture->length)
	{
		PyErr_SetString(PyExc_TypeError, "position out of range");
		return NULL;
	}

	Py_INCREF(self->N_graded_wrappers[position]);
	Py_INCREF(self);

	return (PyObject *)self->N_graded_wrappers[position];;
}


static PyMethodDef N_mixture_wrapper_type_methods[] =
{
	{"prepare_N_mixture_graded",								(PyCFunction)prepare_N_mixture_graded_wrapper,								METH_VARARGS},
	{"N_mixture_graded_is_prepared",						(PyCFunction)N_mixture_graded_is_prepared_wrapper,						METH_NOARGS},
	{"set_N_mixture",														(PyCFunction)set_N_mixture_wrapper,														METH_VARARGS},
	{"set_N_mixture_by_x",											(PyCFunction)set_N_mixture_by_x_wrapper,											METH_VARARGS},
	{"set_dN_mixture",													(PyCFunction)set_dN_mixture_wrapper,													METH_VARARGS},
	{"set_N_mixture_graded",										(PyCFunction)set_N_mixture_graded_wrapper,										METH_VARARGS},
	{"get_N_mixture",														(PyCFunction)get_N_mixture_wrapper,														METH_NOARGS},
	{"get_dN_mixture",													(PyCFunction)get_dN_mixture_wrapper,													METH_NOARGS},
	{"prepare_N_mixture_graded",								(PyCFunction)prepare_N_mixture_graded_wrapper,								METH_VARARGS},
	{"get_N_mixture_graded",										(PyCFunction)get_N_mixture_graded_wrapper,										METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject N_mixture_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.N_mixture",																	/* tp_name */
	sizeof(N_mixture_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_N_mixture_wrapper,							/* tp_dealloc */
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
	"N_mixture class",																	/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	N_mixture_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_N_mixture_wrapper,										/* tp_init */
	0,																									/* tp_alloc */
	new_N_mixture_wrapper,															/* tp_new */
};


#ifdef __cplusplus
}
#endif
