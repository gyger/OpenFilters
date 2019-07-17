/*
 *
 *  dispersion_mixtures_wrapper.cpp
 *
 *
 *  Wrapper around functions in dispersion_mixtures.cpp to make them
 *  available to Python as one class for each dispersion model.
 *
 *  Copyright (c) 2005-2007,2012-2014 Stephane Larouche.
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
/* new_constant_mixture_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * new_constant_mixture_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	constant_mixture_wrapper_object						*self;

	self = (constant_mixture_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_constant_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static int init_constant_mixture_wrapper(constant_mixture_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length;

	if (!PyArg_ParseTuple(args, "n:constant_mixture.__init__", &length))
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
		del_constant_mixture(self->dispersion);
		self->dispersion = NULL;
	}

	/* Create the constant_mixture. */
	self->dispersion = new_constant_mixture(length);
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_constant_mixture_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static void dealloc_constant_mixture_wrapper(constant_mixture_wrapper_object *self)
{
	del_constant_mixture(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_constant_mixture_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * set_constant_mixture_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i;
	double																		x;
	PyObject																	*N_;
	Py_complex																N;
	std::complex<double>											N__;

	if (!PyArg_ParseTuple(args, "ndO:constant_mixture.set_constant_mixture", &i, &x, &N_))
		return NULL;

	/* Check the type of the arguments. */
	if (!(PyComplex_Check(N_) || PyFloat_Check(N_)))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a complex number or a float");
		return NULL;
	}

	/* Check the value of arguments. */
	if (i < 0 || i >= self->dispersion->length)
	{
		PyErr_SetString(PyExc_ValueError, "i out of range");
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
	set_constant_mixture(self->dispersion, i, x, N__);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_constant_mixture_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_constant_mixture_wrapper(constant_mixture_wrapper_object *self)
{
	PyErr_WarnEx(PyExc_DeprecationWarning, "it is no longer necessary to call prepare_constant_mixture", 0);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_monotonicity                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * get_constant_mixture_monotonicity_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	bool																			monotonic;

	if (!PyArg_ParseTuple(args, "d:constant_mixture.get_constant_mixture_monotonicity", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	monotonic = get_constant_mixture_monotonicity(self->dispersion, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("O", monotonic ? Py_True: Py_False);
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_index_wrapper                                */
/*                                                                   */
/*********************************************************************/
static PyObject * get_constant_mixture_index_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	double																		x, wvl;
	double																		n;

	if (!PyArg_ParseTuple(args, "dd:constant_mixture.get_constant_mixture_index", &x, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	n = get_constant_mixture_index(self->dispersion, x, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", n);
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_index_range_wrapper                          */
/*                                                                   */
/*********************************************************************/
static PyObject * get_constant_mixture_index_range_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	double																		n_min, n_max;

	if (!PyArg_ParseTuple(args, "d:constant_mixture.get_constant_mixture_index_range", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	get_constant_mixture_index_range(self->dispersion, wvl, &n_min, &n_max);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("dd", n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_constant_mixture_index_wvl_wrapper                         */
/*                                                                   */
/*********************************************************************/
static PyObject * change_constant_mixture_index_wvl_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	double																		old_n, old_wvl, new_wvl;
	double																		new_n;

	if (!PyArg_ParseTuple(args, "ddd:constant_mixture.change_constant_mixture_index_wvl", &old_n, &old_wvl, &new_wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	new_n = change_constant_mixture_index_wvl(self->dispersion, old_n, old_wvl, new_wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", new_n);
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_constant_mixture_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:constant_mixture.set_N_constant_mixture", &N, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_constant_mixture(self->dispersion, N->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
	{
		PyErr_NoMemory();
		return NULL;
	}

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture_by_x_wrapper                               */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_constant_mixture_by_x_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		x;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Od:constant_mixture.set_N_constant_mixture_by_x", &N, &x))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_constant_mixture_by_x(self->dispersion, N->N, x);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
	{
		PyErr_NoMemory();
		return NULL;
	}

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_constant_mixture_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dN_constant_mixture_wrapper(constant_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*dN;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:constant_mixture.set_dN_constant_mixture", &dN, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(dN))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_dN_constant_mixture(self->dispersion, dN->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
	{
		PyErr_NoMemory();
		return NULL;
	}

	Py_RETURN_NONE;
}


static PyMethodDef constant_mixture_wrapper_type_methods[] =
{
	{"set_constant_mixture",										(PyCFunction)set_constant_mixture_wrapper,										METH_VARARGS},
	{"prepare_constant_mixture",								(PyCFunction)prepare_constant_mixture_wrapper,								METH_NOARGS},
	{"get_constant_mixture_monotonicity",				(PyCFunction)get_constant_mixture_monotonicity_wrapper,				METH_VARARGS},
	{"get_constant_mixture_index",							(PyCFunction)get_constant_mixture_index_wrapper,							METH_VARARGS},
	{"get_constant_mixture_index_range",				(PyCFunction)get_constant_mixture_index_range_wrapper,				METH_VARARGS},
	{"change_constant_mixture_index_wvl",				(PyCFunction)change_constant_mixture_index_wvl_wrapper,				METH_VARARGS},
	{"set_N_constant_mixture",									(PyCFunction)set_N_constant_mixture_wrapper,									METH_VARARGS},
	{"set_N_constant_mixture_by_x",							(PyCFunction)set_N_constant_mixture_by_x_wrapper,							METH_VARARGS},
	{"set_dN_constant_mixture_wrapper",					(PyCFunction)set_dN_constant_mixture_wrapper,									METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject constant_mixture_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.constant_mixture",													/* tp_name */
	sizeof(constant_mixture_wrapper_object),						/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_constant_mixture_wrapper,				/* tp_dealloc */
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
	"constant_mixture class",														/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	constant_mixture_wrapper_type_methods,							/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_constant_mixture_wrapper,						/* tp_init */
	0,																									/* tp_alloc */
	new_constant_mixture_wrapper,												/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_table_mixture_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * new_table_mixture_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	table_mixture_wrapper_object						*self;

	self = (table_mixture_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_table_mixture_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static int init_table_mixture_wrapper(table_mixture_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length, nb_wvls;

	if (!PyArg_ParseTuple(args, "nn:table_mixture.__init__", &length, &nb_wvls))
		return -1;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}
	if (nb_wvls < 1)
	{
		PyErr_SetString(PyExc_TypeError, "nb_wvls must be positive");
		return -1;
	}

	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion) del_table_mixture(self->dispersion);

	/* Create the table_mixture. */
	self->dispersion = new_table_mixture(length, nb_wvls);
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_table_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static void dealloc_table_mixture_wrapper(table_mixture_wrapper_object *self)
{
	if (self->dispersion) del_table_mixture(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_table_mixture_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * set_table_mixture_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i_mix, i_wvl;
	double																		x, wvl;
	PyObject																	*N_;
	Py_complex																N;
	std::complex<double>											N__;

	if (!PyArg_ParseTuple(args, "nnddO:table_mixture.set_table_mixture", &i_mix, &i_wvl, &x, &wvl, &N_))
		return NULL;

	/* Check the type of the arguments. */
	if (!(PyComplex_Check(N_) || PyFloat_Check(N_)))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a complex number or a float");
		return NULL;
	}

	/* Check the value of arguments. */
	if (i_mix < 0 || i_mix >= self->dispersion->length)
	{
		PyErr_SetString(PyExc_ValueError, "i_mix out of range");
		return NULL;
	}
	if (i_wvl < 0 || i_wvl >= self->dispersion->nb_wvls)
	{
		PyErr_SetString(PyExc_ValueError, "i_wvl out of range");
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
	set_table_mixture(self->dispersion, i_mix, i_wvl, x, wvl, N__);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_table_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_table_mixture_wrapper(table_mixture_wrapper_object *self)
{
	PyErr_WarnEx(PyExc_DeprecationWarning, "it is no longer necessary to call prepare_table_mixture", 0);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_monotonicity_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * get_table_mixture_monotonicity_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	bool																			monotonic;

	if (!PyArg_ParseTuple(args, "d:table_mixture.get_table_mixture_monotonicity", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	monotonic = get_table_mixture_monotonicity(self->dispersion, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("O", monotonic ? Py_True: Py_False);
}


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_index_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * get_table_mixture_index_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	double																		x, wvl;
	double																		n;

	if (!PyArg_ParseTuple(args, "dd:table_mixture.get_table_mixture_index", &x, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	n = get_table_mixture_index(self->dispersion, x, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", n);
}


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_index_range_wrapper                             */
/*                                                                   */
/*********************************************************************/
static PyObject * get_table_mixture_index_range_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	double																		n_min, n_max;

	if (!PyArg_ParseTuple(args, "d:table_mixture.get_table_mixture_index_range", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	get_table_mixture_index_range(self->dispersion, wvl, &n_min, &n_max);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("dd", n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_table_mixture_index_wvl_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * change_table_mixture_index_wvl_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	double																		old_n, old_wvl, new_wvl;
	double																		new_n;

	if (!PyArg_ParseTuple(args, "ddd:table_mixture.change_table_mixture_index_wvl", &old_n, &old_wvl, &new_wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	new_n = change_table_mixture_index_wvl(self->dispersion, old_n, old_wvl, new_wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", new_n);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_table_mixture_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:table_mixture.set_N_table_mixture", &N, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_table_mixture(self->dispersion, N->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture_by_x_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_table_mixture_by_x_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		x;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Od:table_mixture.set_N_table_mixture_by_x", &N, &x))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_table_mixture_by_x(self->dispersion, N->N, x);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_table_mixture_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dN_table_mixture_wrapper(table_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*dN;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:table_mixture.set_dN_table_mixture", &dN, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(dN))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_dN_table_mixture(self->dispersion, dN->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef table_mixture_wrapper_type_methods[] =
{
	{"set_table_mixture",												(PyCFunction)set_table_mixture_wrapper,												METH_VARARGS},
	{"prepare_table_mixture",										(PyCFunction)prepare_table_mixture_wrapper,										METH_NOARGS},
	{"get_table_mixture_monotonicity",					(PyCFunction)get_table_mixture_monotonicity_wrapper,					METH_VARARGS},
	{"get_table_mixture_index",									(PyCFunction)get_table_mixture_index_wrapper,									METH_VARARGS},
	{"get_table_mixture_index_range",						(PyCFunction)get_table_mixture_index_range_wrapper,						METH_VARARGS},
	{"change_table_mixture_index_wvl",					(PyCFunction)change_table_mixture_index_wvl_wrapper,					METH_VARARGS},
	{"set_N_table_mixture",											(PyCFunction)set_N_table_mixture_wrapper,											METH_VARARGS},
	{"set_N_table_mixture_by_x",								(PyCFunction)set_N_table_mixture_by_x_wrapper,								METH_VARARGS},
	{"set_dN_table_mixture_wrapper",						(PyCFunction)set_dN_table_mixture_wrapper,										METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject table_mixture_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.table_mixture",															/* tp_name */
	sizeof(table_mixture_wrapper_object),								/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_table_mixture_wrapper,					/* tp_dealloc */
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
	"table_mixture class",															/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	table_mixture_wrapper_type_methods,									/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_table_mixture_wrapper,								/* tp_init */
	0,																									/* tp_alloc */
	new_table_mixture_wrapper,													/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_Cauchy_mixture_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * new_Cauchy_mixture_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Cauchy_mixture_wrapper_object						*self;

	self = (Cauchy_mixture_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_Cauchy_mixture_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static int init_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length;

	if (!PyArg_ParseTuple(args, "n:Cauchy_mixture.__init__", &length))
		return -1;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}

	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion) del_Cauchy_mixture(self->dispersion);

	/* Create the Cauchy_mixture. */
	self->dispersion = new_Cauchy_mixture(length);
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_Cauchy_mixture_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static void dealloc_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self)
{
	if (self->dispersion) del_Cauchy_mixture(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_Cauchy_mixture_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * set_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i;
	double																		x;
	double																		A, B, C, Ak, exponent, edge;

	if (!PyArg_ParseTuple(args, "nddddddd:Cauchy_mixture.set_Cauchy_mixture", &i, &x, &A, &B, &C, &Ak, &exponent, &edge))
		return NULL;

	/* Check the value of arguments. */
	if (i < 0 || i >= self->dispersion->length)
	{
		PyErr_SetString(PyExc_ValueError, "i out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_Cauchy_mixture(self->dispersion, i, x, A, B, C, Ak, exponent, edge);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_Cauchy_mixture_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self)
{
	PyErr_WarnEx(PyExc_DeprecationWarning, "it is no longer necessary to call prepare_Cauchy_mixture", 0);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_monotonicity_wrapper                           */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Cauchy_mixture_monotonicity_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	bool																			monotonic;

	if (!PyArg_ParseTuple(args, "d:Cauchy_mixture.get_Cauchy_mixture_monotonicity", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	monotonic = get_Cauchy_mixture_monotonicity(self->dispersion, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("O", monotonic ? Py_True: Py_False);
}


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_index_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Cauchy_mixture_index_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	double																		x, wvl;
	double																		n;

	if (!PyArg_ParseTuple(args, "dd:Cauchy_mixture.get_Cauchy_mixture_index", &x, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	n = get_Cauchy_mixture_index(self->dispersion, x, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", n);
}


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_index_range_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Cauchy_mixture_index_range_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	double																		n_min, n_max;

	if (!PyArg_ParseTuple(args, "d:Cauchy_mixture.get_Cauchy_mixture_index_range", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	get_Cauchy_mixture_index_range(self->dispersion, wvl, &n_min, &n_max);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("dd", n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_Cauchy_mixture_index_wvl_wrapper                           */
/*                                                                   */
/*********************************************************************/
static PyObject * change_Cauchy_mixture_index_wvl_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	double																		old_n, old_wvl, new_wvl;
	double																		new_n;

	if (!PyArg_ParseTuple(args, "ddd:Cauchy_mixture.change_Cauchy_mixture_index_wvl", &old_n, &old_wvl, &new_wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	new_n = change_Cauchy_mixture_index_wvl(self->dispersion, old_n, old_wvl, new_wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", new_n);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:Cauchy_mixture.set_N_Cauchy_mixture", &N, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Cauchy_mixture(self->dispersion, N->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture_by_x_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Cauchy_mixture_by_x_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		x;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Od:Cauchy_mixture.set_N_Cauchy_mixture_by_x", &N, &x))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Cauchy_mixture_by_x(self->dispersion, N->N, x);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Cauchy_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dN_Cauchy_mixture_wrapper(Cauchy_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*dN;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:Cauchy_mixture.set_dN_Cauchy_mixture", &dN, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(dN))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_dN_Cauchy_mixture(self->dispersion, dN->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef Cauchy_mixture_wrapper_type_methods[] =
{
	{"set_Cauchy_mixture",											(PyCFunction)set_Cauchy_mixture_wrapper,											METH_VARARGS},
	{"prepare_Cauchy_mixture",									(PyCFunction)prepare_Cauchy_mixture_wrapper,									METH_NOARGS},
	{"get_Cauchy_mixture_monotonicity",					(PyCFunction)get_Cauchy_mixture_monotonicity_wrapper,					METH_VARARGS},
	{"get_Cauchy_mixture_index",								(PyCFunction)get_Cauchy_mixture_index_wrapper,								METH_VARARGS},
	{"get_Cauchy_mixture_index_range",					(PyCFunction)get_Cauchy_mixture_index_range_wrapper,					METH_VARARGS},
	{"change_Cauchy_mixture_index_wvl",					(PyCFunction)change_Cauchy_mixture_index_wvl_wrapper,					METH_VARARGS},
	{"set_N_Cauchy_mixture",										(PyCFunction)set_N_Cauchy_mixture_wrapper,										METH_VARARGS},
	{"set_N_Cauchy_mixture_by_x",								(PyCFunction)set_N_Cauchy_mixture_by_x_wrapper,								METH_VARARGS},
	{"set_dN_Cauchy_mixture_wrapper",						(PyCFunction)set_dN_Cauchy_mixture_wrapper,										METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject Cauchy_mixture_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.Cauchy_mixture",														/* tp_name */
	sizeof(Cauchy_mixture_wrapper_object),							/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_Cauchy_mixture_wrapper,					/* tp_dealloc */
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
	"Cauchy_mixture class",															/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	Cauchy_mixture_wrapper_type_methods,								/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_Cauchy_mixture_wrapper,							/* tp_init */
	0,																									/* tp_alloc */
	new_Cauchy_mixture_wrapper,													/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_Sellmeier_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static PyObject * new_Sellmeier_mixture_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Sellmeier_mixture_wrapper_object						*self;

	self = (Sellmeier_mixture_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
		self->dispersion = NULL;

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_Sellmeier_mixture_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static int init_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	Py_ssize_t																length;

	if (!PyArg_ParseTuple(args, "n:Sellmeier_mixture.__init__", &length))
		return -1;

	/* Check the value of the arguments. */
	if (length < 1)
	{
		PyErr_SetString(PyExc_TypeError, "length must be positive");
		return -1;
	}

	/* Delete previous instance of dispersion, if it exists. */
	if (self->dispersion) del_Sellmeier_mixture(self->dispersion);

	/* Create the Sellmeier_mixture. */
	self->dispersion = new_Sellmeier_mixture(length);
	if (!self->dispersion)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_Sellmeier_mixture_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static void dealloc_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self)
{
	if (self->dispersion) del_Sellmeier_mixture(self->dispersion);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_Sellmeier_mixture_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static PyObject * set_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i;
	double																		x;
	double																		B1, C1, B2, C2, B3, C3, Ak, exponent, edge;

	if (!PyArg_ParseTuple(args, "ndddddddddd:Sellmeier_mixture.set_Sellmeier_mixture", &i, &x, &B1, &C1, &B2, &C2, &B3, &C3, &Ak, &exponent, &edge))
		return NULL;

	/* Check the value of arguments. */
	if (i < 0 || i >= self->dispersion->length)
	{
		PyErr_SetString(PyExc_ValueError, "i out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_Sellmeier_mixture(self->dispersion, i, x, B1, C1, B2, C2, B3, C3, Ak, exponent, edge);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_Sellmeier_mixture_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self)
{
	PyErr_WarnEx(PyExc_DeprecationWarning, "it is no longer necessary to call prepare_Sellmeier_mixture", 0);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_monotonicity_wrapper                        */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Sellmeier_mixture_monotonicity_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	bool																			monotonic;

	if (!PyArg_ParseTuple(args, "d:Sellmeier_mixture.get_Sellmeier_mixture_monotonicity", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	monotonic = get_Sellmeier_mixture_monotonicity(self->dispersion, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("O", monotonic ? Py_True: Py_False);
}


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_index_wrapper                               */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Sellmeier_mixture_index_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	double																		x, wvl;
	double																		n;

	if (!PyArg_ParseTuple(args, "dd:Sellmeier_mixture.get_Sellmeier_mixture_index", &x, &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	n = get_Sellmeier_mixture_index(self->dispersion, x, wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", n);
}


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_index_range_wrapper                         */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Sellmeier_mixture_index_range_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	double																		wvl;
	double																		n_min, n_max;

	if (!PyArg_ParseTuple(args, "d:Sellmeier_mixture.get_Sellmeier_mixture_index_range", &wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	get_Sellmeier_mixture_index_range(self->dispersion, wvl, &n_min, &n_max);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("dd", n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_Sellmeier_mixture_index_wvl_wrapper                        */
/*                                                                   */
/*********************************************************************/
static PyObject * change_Sellmeier_mixture_index_wvl_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	double																		old_n, old_wvl, new_wvl;
	double																		new_n;

	if (!PyArg_ParseTuple(args, "ddd:Sellmeier_mixture.change_Sellmeier_mixture_index_wvl", &old_n, &old_wvl, &new_wvl))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	new_n = change_Sellmeier_mixture_index_wvl(self->dispersion, old_n, old_wvl, new_wvl);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", new_n);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:Sellmeier_mixture.set_N_Sellmeier_mixture", &N, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Sellmeier_mixture(self->dispersion, N->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture_by_x_wrapper                              */
/*                                                                   */
/*********************************************************************/
static PyObject * set_N_Sellmeier_mixture_by_x_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		x;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Od:Sellmeier_mixture.set_N_Sellmeier_mixture_by_x", &N, &x))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_N_Sellmeier_mixture_by_x(self->dispersion, N->N, x);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Sellmeier_mixture_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dN_Sellmeier_mixture_wrapper(Sellmeier_mixture_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*dN;
	double																		n_wvl, wvl;
	abeles_error_type													return_value;

	if (!PyArg_ParseTuple(args, "Odd:Sellmeier_mixture.set_dN_Sellmeier_mixture", &dN, &n_wvl, &wvl))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(dN))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	return_value = set_dN_Sellmeier_mixture(self->dispersion, dN->N, n_wvl, wvl);
	Py_END_ALLOW_THREADS

	if (return_value == ABELES_OUT_OF_MEMORY)
		return PyErr_NoMemory();

	Py_RETURN_NONE;
}


static PyMethodDef Sellmeier_mixture_wrapper_type_methods[] =
{
	{"set_Sellmeier_mixture",										(PyCFunction)set_Sellmeier_mixture_wrapper,										METH_VARARGS},
	{"prepare_Sellmeier_mixture",								(PyCFunction)prepare_Sellmeier_mixture_wrapper,								METH_NOARGS},
	{"get_Sellmeier_mixture_monotonicity",			(PyCFunction)get_Sellmeier_mixture_monotonicity_wrapper,			METH_VARARGS},
	{"get_Sellmeier_mixture_index",							(PyCFunction)get_Sellmeier_mixture_index_wrapper,							METH_VARARGS},
	{"get_Sellmeier_mixture_index_range",				(PyCFunction)get_Sellmeier_mixture_index_range_wrapper,				METH_VARARGS},
	{"change_Sellmeier_mixture_index_wvl",			(PyCFunction)change_Sellmeier_mixture_index_wvl_wrapper,			METH_VARARGS},
	{"set_N_Sellmeier_mixture",									(PyCFunction)set_N_Sellmeier_mixture_wrapper,									METH_VARARGS},
	{"set_N_Sellmeier_mixture_by_x",						(PyCFunction)set_N_Sellmeier_mixture_by_x_wrapper,						METH_VARARGS},
	{"set_dN_Sellmeier_mixture_wrapper",				(PyCFunction)set_dN_Sellmeier_mixture_wrapper,								METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject Sellmeier_mixture_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.Sellmeier_mixture",													/* tp_name */
	sizeof(Sellmeier_mixture_wrapper_object),						/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_Sellmeier_mixture_wrapper,			/* tp_dealloc */
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
	"Sellmeier_mixture class",													/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	Sellmeier_mixture_wrapper_type_methods,							/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_Sellmeier_mixture_wrapper,						/* tp_init */
	0,																									/* tp_alloc */
	new_Sellmeier_mixture_wrapper,											/* tp_new */
};


#ifdef __cplusplus
}
#endif
