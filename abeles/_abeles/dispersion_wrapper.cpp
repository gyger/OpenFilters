/*
 *
 *  dispersion_wrapper.cpp
 *
 *
 *  Wrap the object and functions provided in dispersion.cpp to make
 *  them available to Python as one class for each dispersion model.
 *
 *  Copyright (c) 2002-2007,2012-2014 Stephane Larouche.
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
/* new_constant_wrapper                                              */
/*                                                                   */
/*********************************************************************/
PyObject * new_constant_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	constant_wrapper_object										*self;

	self = (constant_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_constant_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static int init_constant_wrapper(constant_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion)
	{
		del_constant(self->dispersion);
		self->dispersion = NULL;
	}

	/* Create the dispersion. */
	self->dispersion = new_constant();
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_constant_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static void dealloc_constant_wrapper(constant_wrapper_object *self)
{
	del_constant(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_constant_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * set_constant_wrapper(constant_wrapper_object *self, PyObject *args)
{
	PyObject																	*N_;
	Py_complex																N;
	std::complex<double>											N__;

	if (!PyArg_ParseTuple(args, "O:constant.set_constant", &N_))
		return NULL;

	/* Check the type of the arguments. */
	if (!(PyComplex_Check(N_) || PyFloat_Check(N_)))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be a complex number or a float");
		return NULL;
	}

	/* Convert the Python complex to a C complex. */
	if (PyComplex_Check(N_))
	{
		/* It is necessary to do it in two steps because there is a problem
		 * with the reference to PyComplex_ImagAsDouble in the Python dll. */
		N = PyComplex_AsCComplex(N_);
		N__ = std::complex<double>(N.real, N.imag);
	}
	else
	{
		N__ = std::complex<double>(PyFloat_AsDouble(N_), 0.0);
	}

	Py_BEGIN_ALLOW_THREADS
	set_constant(self->dispersion, N__);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_constant_wrapper(constant_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "O:constant.set_N_constant", &N))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_constant(self->dispersion, N->N);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef constant_wrapper_type_methods[] =
{
	{"set_constant",														(PyCFunction)set_constant_wrapper,														METH_VARARGS},
	{"set_N_constant",													(PyCFunction)set_N_constant_wrapper,													METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject constant_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.constant",																	/* tp_name */
	sizeof(constant_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_constant_wrapper,								/* tp_dealloc */
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
	"constant class",																		/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	constant_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_constant_wrapper,										/* tp_init */
	0,																									/* tp_alloc */
	new_constant_wrapper,																/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_table_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
PyObject * new_table_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	table_wrapper_object											*self;

	self = (table_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_table_wrapper                                                */
/*                                                                   */
/*********************************************************************/
static int init_table_wrapper(table_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length;

	if (!PyArg_ParseTuple(args, "n:table.__init__", &length))
		return -1;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}

	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion)
	{
		del_table(self->dispersion);
		self->dispersion = NULL;
	}

	/* Create the dispersion. */
	self->dispersion = new_table(length);
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_table_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static void dealloc_table_wrapper(table_wrapper_object *self)
{
	del_table(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_table_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * set_table_wrapper(table_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																position;
	double																		wvl;
	PyObject																	*N_;
	Py_complex																N;
	std::complex<double>											N__;

	if (!PyArg_ParseTuple(args, "ndO:table.set_table", &position, &wvl, &N_))
		return NULL;

	/* Check the type of the arguments. */
	if (!(PyComplex_Check(N_) || PyFloat_Check(N_)))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a complex number or a float");
		return NULL;
	}

	/* Check the value of the arguments. */
	if (position < 0)
	{
		PyErr_SetString(PyExc_TypeError, "position must be positive");
		return NULL;
	}
	else if (position >= self->dispersion->length)
	{
		PyErr_SetString(PyExc_TypeError, "position is too large");
		return NULL;
	}

	/* Convert the Python complex to a C complex. */
	if (PyComplex_Check(N_))
	{
		/* It is necessary to do it in two steps because there is a problem
		 * with the reference to PyComplex_ImagAsDouble in the Python dll. */
		N = PyComplex_AsCComplex(N_);
		N__ = std::complex<double>(N.real, N.imag);
	}
	else
	{
		N__ = std::complex<double>(PyFloat_AsDouble(N_), 0.0);
	}

	Py_BEGIN_ALLOW_THREADS
	set_table(self->dispersion, position, wvl, N__);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_table_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_table_wrapper(table_wrapper_object *self)
{
	PyErr_WarnEx(PyExc_DeprecationWarning, "it is no longer necessary to call prepare_table", 0);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_table_index_wrapper                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * get_table_index_wrapper(table_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	double																		n;

	if (!PyArg_ParseTuple(args, "d:table.get_table_index", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	n = get_table_index(self->dispersion, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", n);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_table_wrapper(table_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "O:table.set_N_table", &N))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_table(self->dispersion, N->N);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef table_wrapper_type_methods[] =
{
	{"set_table",																(PyCFunction)set_table_wrapper,																METH_VARARGS},
	{"prepare_table",														(PyCFunction)prepare_table_wrapper,														METH_NOARGS},
	{"get_table_index",													(PyCFunction)get_table_index_wrapper,													METH_VARARGS},
	{"set_N_table",															(PyCFunction)set_N_table_wrapper,															METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject table_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.table",																			/* tp_name */
	sizeof(table_wrapper_object),												/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_table_wrapper,									/* tp_dealloc */
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
	"table class",																			/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	table_wrapper_type_methods,													/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_table_wrapper,												/* tp_init */
	0,																									/* tp_alloc */
	new_table_wrapper,																	/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_Cauchy_wrapper                                                */
/*                                                                   */
/*********************************************************************/
PyObject * new_Cauchy_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Cauchy_wrapper_object											*self;

	self = (Cauchy_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_Cauchy_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static int init_Cauchy_wrapper(Cauchy_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion)
	{
		del_Cauchy(self->dispersion);
		self->dispersion = NULL;
	}

	/* Create the dispersion. */
	self->dispersion = new_Cauchy();
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_Cauchy_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static void dealloc_Cauchy_wrapper(Cauchy_wrapper_object *self)
{
	del_Cauchy(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_Cauchy_wrapper                                                */
/*                                                                   */
/*********************************************************************/
static PyObject * set_Cauchy_wrapper(Cauchy_wrapper_object *self, PyObject *args)
{
	double																		A, B, C, Ak, exponent, edge;

	if (!PyArg_ParseTuple(args, "dddddd:Cauchy.set_Cauchy", &A, &B, &C, &Ak, &exponent, &edge))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	set_Cauchy(self->dispersion, A, B, C, Ak, exponent, edge);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Cauchy_wrapper(Cauchy_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "O:Cauchy.set_N_Cauchy", &N))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Cauchy(self->dispersion, N->N);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef Cauchy_wrapper_type_methods[] =
{
	{"set_Cauchy",															(PyCFunction)set_Cauchy_wrapper,															METH_VARARGS},
	{"set_N_Cauchy",														(PyCFunction)set_N_Cauchy_wrapper,														METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject Cauchy_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.Cauchy",																		/* tp_name */
	sizeof(Cauchy_wrapper_object),											/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_Cauchy_wrapper,									/* tp_dealloc */
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
	"Cauchy class",																			/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	Cauchy_wrapper_type_methods,												/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_Cauchy_wrapper,											/* tp_init */
	0,																									/* tp_alloc */
	new_Cauchy_wrapper,																	/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_Sellmeier_wrapper                                             */
/*                                                                   */
/*********************************************************************/
PyObject * new_Sellmeier_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Sellmeier_wrapper_object									*self;

	self = (Sellmeier_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_Sellmeier_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static int init_Sellmeier_wrapper(Sellmeier_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion)
	{
		del_Sellmeier(self->dispersion);
		self->dispersion = NULL;
	}

	/* Create the dispersion. */
	self->dispersion = new_Sellmeier();
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_Sellmeier_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static void dealloc_Sellmeier_wrapper(Sellmeier_wrapper_object *self)
{
	del_Sellmeier(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_Sellmeier_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * set_Sellmeier_wrapper(Sellmeier_wrapper_object *self, PyObject *args)
{
	double																		B1, C1, B2, C2, B3, C3, Ak, exponent, edge;

	if (!PyArg_ParseTuple(args, "ddddddddd:Sellmeier.set_Sellmeier", &B1, &C1, &B2, &C2, &B3, &C3, &Ak, &exponent, &edge))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	set_Sellmeier(self->dispersion, B1, C1, B2, C2, B3, C3, Ak, exponent, edge);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_wrapper                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Sellmeier_wrapper(Sellmeier_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "O:Sellmeier.set_N_Sellmeier", &N))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Sellmeier(self->dispersion, N->N);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef Sellmeier_wrapper_type_methods[] =
{
	{"set_Sellmeier",														(PyCFunction)set_Sellmeier_wrapper,														METH_VARARGS},
	{"set_N_Sellmeier",													(PyCFunction)set_N_Sellmeier_wrapper,													METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject Sellmeier_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.Sellmeier",																	/* tp_name */
	sizeof(Sellmeier_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_Sellmeier_wrapper,							/* tp_dealloc */
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
	"Sellmeier class",																	/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	Sellmeier_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_Sellmeier_wrapper,										/* tp_init */
	0,																									/* tp_alloc */
	new_Sellmeier_wrapper,															/* tp_new */
};


#ifdef __cplusplus
}
#endif
