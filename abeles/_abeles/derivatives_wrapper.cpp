/*
 *
 *  derivatives_wrapper.cpp
 *
 *
 *  Wrapper around functions in derivatives.cpp to make them available to
 *  Python in multiple classes.
 *
 *  Copyright (c) 2004-2009,2012,2013 Stephane Larouche.
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
/* new_pre_and_post_matrices_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * new_pre_and_post_matrices_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	pre_and_post_matrices_wrapper_object			*self;

	self = (pre_and_post_matrices_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->pre_and_post_matrices = NULL;
		self->M_wrapper = NULL;
		self->Mi_wrappers = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_pre_and_post_matrices_wrapper                                */
/*                                                                   */
/*********************************************************************/
static int init_pre_and_post_matrices_wrapper(pre_and_post_matrices_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	Py_ssize_t																length, i;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "On:pre_and_post_matrices.__init__", &wvls, &length))
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
	if (self->Mi_wrappers)
	{
		for (i = 0; i < self->pre_and_post_matrices->length; i++)
			if (self->Mi_wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->Mi_wrappers[i]);
		free(self->Mi_wrappers);
		self->Mi_wrappers = NULL;
	}
	if (self->M_wrapper)
	{
		matrices_wrapper_type.tp_free((PyObject*)self->M_wrapper);
		self->M_wrapper = NULL;
	}

	/* Delete previous instance of pre_and_post_matrices, if it exist. */
	if (self->pre_and_post_matrices)
	{
		del_pre_and_post_matrices(self->pre_and_post_matrices);
		self->pre_and_post_matrices = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the pre_and_post_matrices. */
	self->pre_and_post_matrices = new_pre_and_post_matrices(wvls->wvls, length);
	if (!self->pre_and_post_matrices)
	{
		PyErr_NoMemory();
		return -1;
	}

	/* Make wrappers around the layer matrices. The ref count of the
	 * wrappers is decreased (to 0) so that they can be destroyed when
	 * the ref count of self drops to 0. But the ref count of self is
	 * increased first to avoid immediate destruction. */

	self->M_wrapper = (matrices_wrapper_object *)matrices_wrapper_type.tp_alloc(&matrices_wrapper_type, 0);
	if (!self->M_wrapper)
	{
		PyErr_NoMemory();
		return -1;
	}
	self->M_wrapper->wvls = self->wvls;
	self->M_wrapper->matrices = self->pre_and_post_matrices->M;
	self->M_wrapper->parent = (PyObject *)self;

	Py_INCREF(self);
	Py_DECREF(self->M_wrapper);

	self->Mi_wrappers = (matrices_wrapper_object **)malloc(self->pre_and_post_matrices->length*sizeof(matrices_wrapper_object *));
	if (!self->Mi_wrappers)
	{
		PyErr_NoMemory();
		return -1;
	}
	for (i = 0; i < self->pre_and_post_matrices->length; i++)
		self->Mi_wrappers[i] = NULL;
	for (i = 0; i < self->pre_and_post_matrices->length; i++)
	{
		self->Mi_wrappers[i] = (matrices_wrapper_object *)matrices_wrapper_type.tp_alloc(&matrices_wrapper_type, 0);
		if (!self->Mi_wrappers[i])
		{
			PyErr_NoMemory();
			return -1;
		}
		self->Mi_wrappers[i]->wvls = self->wvls;
		self->Mi_wrappers[i]->matrices = self->pre_and_post_matrices->Mi[i];
		self->Mi_wrappers[i]->parent = (PyObject *)self;

		Py_INCREF(self);
		Py_DECREF(self->Mi_wrappers[i]);
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_pre_and_post_matrices_wrapper                             */
/*                                                                   */
/*********************************************************************/
static void dealloc_pre_and_post_matrices_wrapper(pre_and_post_matrices_wrapper_object *self)
{
	Py_ssize_t																i;

	if (self->Mi_wrappers)
	{
		for (i = 0; i < self->pre_and_post_matrices->length; i++)
			if (self->Mi_wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->Mi_wrappers[i]);
		free(self->Mi_wrappers);
	}
	if (self->M_wrapper)
		matrices_wrapper_type.tp_free((PyObject*)self->M_wrapper);

	del_pre_and_post_matrices(self->pre_and_post_matrices);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_pre_and_post_matrices_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * set_pre_and_post_matrices_wrapper(pre_and_post_matrices_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																layer_nb;
	N_wrapper_object													*N;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "nOdO:pre_and_post_matrices.set_pre_and_post_matrices", &layer_nb, &N, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
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
	if (layer_nb < 0 || layer_nb > self->pre_and_post_matrices->length)
	{
		PyErr_SetString(PyExc_ValueError, "layer_nb out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_pre_and_post_matrices(self->pre_and_post_matrices, layer_nb, N->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* multiply_pre_and_post_matrices_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * multiply_pre_and_post_matrices_wrapper(pre_and_post_matrices_wrapper_object *self)
{
	Py_BEGIN_ALLOW_THREADS
	multiply_pre_and_post_matrices(self->pre_and_post_matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_global_matrices_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * get_global_matrices_wrapper(pre_and_post_matrices_wrapper_object *self)
{
	Py_INCREF(self);
	Py_INCREF(self->M_wrapper);

	return (PyObject *)self->M_wrapper;
}


/*********************************************************************/
/*                                                                   */
/* pre_and_post_matrices_wrapper_length                              */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t pre_and_post_matrices_wrapper_length(pre_and_post_matrices_wrapper_object *self)
{
	return self->pre_and_post_matrices->length;
}


/*********************************************************************/
/*                                                                   */
/* pre_and_post_matrices_wrapper_item                                */
/*                                                                   */
/*********************************************************************/
static PyObject * pre_and_post_matrices_wrapper_item(pre_and_post_matrices_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->pre_and_post_matrices->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	item = (PyObject *)self->Mi_wrappers[i];
	Py_INCREF(self);
	Py_INCREF(item);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* pre_and_post_matrices_wrapper_subscript                           */
/*                                                                   */
/*********************************************************************/
static PyObject * pre_and_post_matrices_wrapper_subscript(pre_and_post_matrices_wrapper_object* self, PyObject* item)
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
			i += self->pre_and_post_matrices->length;
		return pre_and_post_matrices_wrapper_item(self, i);
	}
	else if (PySlice_Check(item))
	{
		if (PySlice_GetIndicesEx((PySliceObject*)item, self->pre_and_post_matrices->length, &start, &stop, &step, &slicelength) < 0)
			return NULL;

		if (slicelength <= 0)
			return PyList_New(0);

		else
		{
			result = PyList_New(slicelength);
			if (!result) return NULL;

			for (cur = start, i = 0; i < slicelength; cur += step, i++)
			{
				element = (PyObject *)self->Mi_wrappers[cur];
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


static PyMethodDef pre_and_post_matrices_wrapper_type_methods[] =
{
	{"set_pre_and_post_matrices",								(PyCFunction)set_pre_and_post_matrices_wrapper,								METH_VARARGS},
	{"multiply_pre_and_post_matrices",					(PyCFunction)multiply_pre_and_post_matrices_wrapper,					METH_NOARGS},
	{"get_global_matrices",											(PyCFunction)get_global_matrices_wrapper,											METH_NOARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods pre_and_post_matrices_wrapper_as_sequence = {
	(lenfunc)pre_and_post_matrices_wrapper_length,			/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)pre_and_post_matrices_wrapper_item,		/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods pre_and_post_matrices_wrapper_as_mapping = {
	(lenfunc)pre_and_post_matrices_wrapper_length,			/* mp_length */
	(binaryfunc)pre_and_post_matrices_wrapper_subscript,/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject pre_and_post_matrices_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.pre_and_post_matrices",											/* tp_name */
	sizeof(pre_and_post_matrices_wrapper_object),				/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_pre_and_post_matrices_wrapper,	/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&pre_and_post_matrices_wrapper_as_sequence,					/* tp_as_sequence */
	&pre_and_post_matrices_wrapper_as_mapping,					/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"pre_and_post_matrices class",											/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	pre_and_post_matrices_wrapper_type_methods,					/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_pre_and_post_matrices_wrapper,				/* tp_init */
	0,																									/* tp_alloc */
	new_pre_and_post_matrices_wrapper,									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* set_dMi_thickness_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dMi_thickness_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OdO:dM.set_dMi_thickness", &N, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
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
	set_dMi_thickness(self->matrices, N->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dMi_index_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dMi_index_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	N_wrapper_object													*dN;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOdO:dM.set_dMi_index", &N, &dN, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(dN))
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
	if (N->wvls != self->wvls || dN->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_dMi_index(self->matrices, N->N, dN->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_dMi_index_with_constant_OT_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * set_dMi_index_with_constant_OT_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	N_wrapper_object													*dN;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;
	PyObject																	*N_0_;
	Py_complex																N_0;
	std::complex<double>											N_0__;
	PyObject																	*sin2_theta_0_0_;
	Py_complex																sin2_theta_0_0;
	std::complex<double>											sin2_theta_0_0__;

	if (!PyArg_ParseTuple(args, "OOdOOO:dM.set_dMi_index_with_constant_OT", &N, &dN, &thickness, &sin2_theta_0, &N_0_, &sin2_theta_0_0_))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(dN))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be sin2");
		return NULL;
	}
	if (!(N_wrapper_Check(N_0_) || PyComplex_Check(N_0_) || PyFloat_Check(N_0_)))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be N, a complex number or a float");
		return NULL;
	}
	if (!(sin2_wrapper_Check(sin2_theta_0_0_) || PyComplex_Check(sin2_theta_0_0_) || PyFloat_Check(sin2_theta_0_0_)))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be sin2, a complex number or a float");
		return NULL;
	}

	/* If N_0_ and sin2_theta_0_0_ are N_wrapper and sin2_wrapper
	 * objects, check that they are of length one. */
	if (N_wrapper_Check(N_0_))
	{
		if (((N_wrapper_object *)N_0_)->N->wvls->length != 1)
		{
			PyErr_SetString(PyExc_ValueError, "4th argument must be of lenght 1");
			return NULL;
		}
	}
	if (sin2_wrapper_Check(sin2_theta_0_0_))
	{
		if (((sin2_wrapper_object *)sin2_theta_0_0_)->sin2->wvls->length != 1)
		{
			PyErr_SetString(PyExc_ValueError, "5th argument must be of lenght 1");
			return NULL;
		}
	}

	/* Convert the Python complex to a C complex. */
	if (N_wrapper_Check(N_0_))
	{
		N_0__ = ((N_wrapper_object *)N_0_)->N->N[0];
	}
	else if (PyComplex_Check(N_0_))
	{
		/* It is necessary to do it in two steps because there is a problem
		 * with the reference to PyComplex_ImagAsDouble in the Python dll. */
		N_0 = PyComplex_AsCComplex(N_0_);
		N_0__ = std::complex<double>(N_0.real, N_0.imag);
	}
	else
	{
		N_0__ = std::complex<double>(PyFloat_AsDouble(N_0_), 0.0);
	}

	/* Convert the Python complex to a C complex. */
	if (sin2_wrapper_Check(sin2_theta_0_0_))
	{
		sin2_theta_0_0__ = ((sin2_wrapper_object *)sin2_theta_0_0_)->sin2->sin2[0];
	}
	else if (PyComplex_Check(sin2_theta_0_0_))
	{
		/* It is necessary to do it in two steps because there is a problem
		 * with the reference to PyComplex_ImagAsDouble in the Python dll. */
		sin2_theta_0_0 = PyComplex_AsCComplex(sin2_theta_0_0_);
		sin2_theta_0_0__ = std::complex<double>(sin2_theta_0_0.real, sin2_theta_0_0.imag);
	}
	else
	{
		sin2_theta_0_0__ = std::complex<double>(PyFloat_AsDouble(sin2_theta_0_0_), 0.0);
	}

	/* Check the value of arguments. */
	if (N->wvls != self->wvls || dN->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_dMi_index_with_constant_OT(self->matrices, N->N, dN->N, thickness, sin2_theta_0->sin2, N_0__, sin2_theta_0_0__);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dM_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dM_wrapper(matrices_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*dMi;
	pre_and_post_matrices_wrapper_object			*M;
	long																			layer_nb;

	if (!PyArg_ParseTuple(args, "OOl:dM.calculate_dM", &dMi, &M, &layer_nb))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(dMi))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!pre_and_post_matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be pre_and_post_matrices");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dMi->wvls != self->wvls || M->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}
	if (layer_nb < 0 || layer_nb >= M->pre_and_post_matrices->length)
	{
		PyErr_SetString(PyExc_ValueError, "layer_nb out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dM(self->matrices, dMi->matrices, M->pre_and_post_matrices, layer_nb);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dM_wrapper_type_methods[] =
{
	{"set_dMi_thickness",												(PyCFunction)set_dMi_thickness_wrapper,												METH_VARARGS},
	{"set_dMi_index",														(PyCFunction)set_dMi_index_wrapper,														METH_VARARGS},
	{"set_dMi_index_with_constant_OT",					(PyCFunction)set_dMi_index_with_constant_OT_wrapper,					METH_VARARGS},
	{"calculate_dM",														(PyCFunction)calculate_dM_wrapper,														METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dM_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dM",																				/* tp_name */
	sizeof(matrices_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dM class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dM_wrapper_type_methods,														/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&matrices_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* new_psi_matrices_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static PyObject * new_psi_matrices_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	psi_matrices_wrapper_object								*self;

	self = (psi_matrices_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->psi_matrices = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_psi_matrices_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static int init_psi_matrices_wrapper(psi_matrices_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:psi_matrices.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of psi_matrices, if it exists. */
	if (self->psi_matrices) del_psi_matrices(self->psi_matrices);

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the psi_matrices. */
	self->psi_matrices = new_psi_matrices(wvls->wvls);
	if (!self->psi_matrices)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_psi_matrices_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static void dealloc_psi_matrices_wrapper(psi_matrices_wrapper_object *self)
{
	if (self->psi_matrices) del_psi_matrices(self->psi_matrices);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* calculate_psi_matrices_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_psi_matrices_wrapper(psi_matrices_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOO:psi_matrices.calculate_psi_matrices", &r_and_t, &N_m, &N_s, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
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
	if (r_and_t->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_psi_matrices(self->psi_matrices, r_and_t->r_and_t, N_m->N, N_s->N, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_psi_matrices_reverse_wrapper                            */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_psi_matrices_reverse_wrapper(psi_matrices_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOO:psi_matrices.calculate_psi_matrices_reverse", &r_and_t, &N_m, &N_s, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
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
	if (r_and_t->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_psi_matrices_reverse(self->psi_matrices, r_and_t->r_and_t, N_m->N, N_s->N, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef psi_matrices_wrapper_type_methods[] =
{
	{"calculate_psi_matrices",									(PyCFunction)calculate_psi_matrices_wrapper,									METH_VARARGS},
	{"calculate_psi_matrices_reverse",					(PyCFunction)calculate_psi_matrices_reverse_wrapper,					METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject psi_matrices_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.psi_matrices",															/* tp_name */
	sizeof(psi_matrices_wrapper_object),								/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_psi_matrices_wrapper,						/* tp_dealloc */
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
	"psi_matrices class",																/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	psi_matrices_wrapper_type_methods,									/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_psi_matrices_wrapper,								/* tp_init */
	0,																									/* tp_alloc */
	new_psi_matrices_wrapper,														/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dr_and_dt_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dr_and_dt_wrapper(r_and_t_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*dM;
	psi_matrices_wrapper_object								*psi;

	if (!PyArg_ParseTuple(args, "OO:dr_and_dt.calculate_dr_and_dt", &dM, &psi))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(dM))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!psi_matrices_wrapper_Check(psi))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be psi_matrices");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dM->wvls != self->wvls || psi->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dr_and_dt(self->r_and_t, dM->matrices, psi->psi_matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dr_and_dt_reverse_wrapper                               */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dr_and_dt_reverse_wrapper(r_and_t_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*dM;
	psi_matrices_wrapper_object								*psi;

	if (!PyArg_ParseTuple(args, "OO:dr_and_dt.calculate_dr_and_dt_reverse", &dM, &psi))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(dM))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!psi_matrices_wrapper_Check(psi))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be psi_matrices");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dM->wvls != self->wvls || psi->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dr_and_dt_reverse(self->r_and_t, dM->matrices, psi->psi_matrices);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dr_and_dt_wrapper_type_methods[] =
{
	{"calculate_dr_and_dt",											(PyCFunction)calculate_dr_and_dt_wrapper,											METH_VARARGS},
	{"calculate_dr_and_dt_reverse",							(PyCFunction)calculate_dr_and_dt_reverse_wrapper,							METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dr_and_dt_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dr_and_dt",																	/* tp_name */
	0,																									/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dr_and_dt class",																	/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dr_and_dt_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&r_and_t_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dR_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dR_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*dr_and_dt;
	r_and_t_wrapper_object										*r_and_t;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOd:dR.calculate_dR", &dr_and_dt, &r_and_t, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!dr_and_dt_wrapper_Check(dr_and_dt))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be dr_and_dt");
		return NULL;
	}
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be r_and_t");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dr_and_dt->wvls != self->wvls || r_and_t->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dR(self->spectrum, dr_and_dt->r_and_t, r_and_t->r_and_t, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dR_with_backside_wrapper                                */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dR_with_backside_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*dT_front;
	spectrum_wrapper_object										*dR_front;
	spectrum_wrapper_object										*T_front_reverse;
	spectrum_wrapper_object										*dT_front_reverse;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*dR_front_reverse;
	spectrum_wrapper_object										*R_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOOOOOdO:dR.calculate_dR_with_backside", &T_front, &dT_front, &dR_front, &T_front_reverse, &dT_front_reverse, &R_front_reverse, &dR_front_reverse, &R_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!T_wrapper_Check(T_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be T");
		return NULL;
	}
	if (!dT_wrapper_Check(dT_front))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be dT");
		return NULL;
	}
	if (!dR_wrapper_Check(dR_front))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be dR");
		return NULL;
	}
	if (!T_wrapper_Check(T_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be T");
		return NULL;
	}
	if (!dT_wrapper_Check(dT_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be dT");
		return NULL;
	}
	if (!R_wrapper_Check(R_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "6th argument must be R");
		return NULL;
	}
	if (!dR_wrapper_Check(dR_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "7th argument must be dR");
		return NULL;
	}
	if (!R_wrapper_Check(R_back))
	{
		PyErr_SetString(PyExc_TypeError, "8th argument must be R");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "9th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "11th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (T_front->wvls != self->wvls || dT_front->wvls != self->wvls || dR_front->wvls != self->wvls || T_front_reverse->wvls != self->wvls || dT_front_reverse->wvls != self->wvls || R_front_reverse->wvls != self->wvls || dR_front_reverse->wvls != self->wvls || R_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dR_with_backside(self->spectrum, T_front->spectrum, dT_front->spectrum, dR_front->spectrum, T_front_reverse->spectrum, dT_front_reverse->spectrum, R_front_reverse->spectrum, dR_front_reverse->spectrum, R_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dR_with_backside_2_wrapper                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dR_with_backside_2_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*T_front_reverse;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*R_back;
	spectrum_wrapper_object										*dR_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOOdO:dR.calculate_dR_with_backside_2", &T_front, &T_front_reverse, &R_front_reverse, &R_back, &dR_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!T_wrapper_Check(T_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be T");
		return NULL;
	}
	if (!T_wrapper_Check(T_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be T");
		return NULL;
	}
	if (!R_wrapper_Check(R_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be R");
		return NULL;
	}
	if (!R_wrapper_Check(R_back))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be R");
		return NULL;
	}
	if (!dR_wrapper_Check(dR_back))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be R");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "6th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "8th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (T_front->wvls != self->wvls || T_front_reverse->wvls != self->wvls || R_front_reverse->wvls != self->wvls || R_back->wvls != self->wvls || dR_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dR_with_backside_2(self->spectrum, T_front->spectrum, T_front_reverse->spectrum, R_front_reverse->spectrum, R_back->spectrum, dR_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dR_wrapper_type_methods[] =
{
	{"calculate_dR",														(PyCFunction)calculate_dR_wrapper,														METH_VARARGS},
	{"calculate_dR_with_backside",							(PyCFunction)calculate_dR_with_backside_wrapper,							METH_VARARGS},
	{"calculate_dR_with_backside_2",						(PyCFunction)calculate_dR_with_backside_2_wrapper,						METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dR_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dR",																				/* tp_name */
	0,																									/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dR class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dR_wrapper_type_methods,														/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dT_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dT_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*dr_and_dt;
	r_and_t_wrapper_object										*r_and_t;
	N_wrapper_object													*N_i;
	N_wrapper_object													*N_e;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOOd:dT.calculate_dT", &dr_and_dt, &r_and_t, &N_i, &N_e, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!dr_and_dt_wrapper_Check(dr_and_dt))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be dr_and_dt");
		return NULL;
	}
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be r_and_t");
		return NULL;
	}
	if (!N_wrapper_Check(N_i))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_e))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dr_and_dt->wvls != self->wvls || r_and_t->wvls != self->wvls || N_i->wvls != self->wvls || N_e->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dT(self->spectrum, dr_and_dt->r_and_t, r_and_t->r_and_t, N_i->N, N_e->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dT_with_backside_wrapper                                */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dT_with_backside_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*dT_front;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*dR_front_reverse;
	spectrum_wrapper_object										*T_back;
	spectrum_wrapper_object										*R_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOOOdO:dT.calculate_dT_with_backside", &T_front, &dT_front, &R_front_reverse, &dR_front_reverse, &T_back, &R_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!T_wrapper_Check(T_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be T");
		return NULL;
	}
	if (!dT_wrapper_Check(dT_front))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be dT");
		return NULL;
	}
	if (!R_wrapper_Check(R_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be R");
		return NULL;
	}
	if (!dR_wrapper_Check(dR_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be dR");
		return NULL;
	}
	if (!T_wrapper_Check(T_back))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be T");
		return NULL;
	}
	if (!R_wrapper_Check(R_back))
	{
		PyErr_SetString(PyExc_TypeError, "6th argument must be R");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "7th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "9th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (T_front->wvls != self->wvls || dT_front->wvls != self->wvls || R_front_reverse->wvls != self->wvls || dR_front_reverse->wvls != self->wvls || T_back->wvls != self->wvls || R_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dT_with_backside(self->spectrum, T_front->spectrum, dT_front->spectrum, R_front_reverse->spectrum, dR_front_reverse->spectrum, T_back->spectrum, R_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dT_with_backside_2_wrapper                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dT_with_backside_2_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*T_back;
	spectrum_wrapper_object										*dT_back;
	spectrum_wrapper_object										*R_back;
	spectrum_wrapper_object										*dR_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOOOdO:dT.calculate_dT_with_backside", &T_front, &R_front_reverse, &T_back, &dT_back, &R_back, &dR_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!T_wrapper_Check(T_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be T");
		return NULL;
	}
	if (!R_wrapper_Check(R_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be R");
		return NULL;
	}
	if (!T_wrapper_Check(T_back))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be T");
		return NULL;
	}
	if (!dT_wrapper_Check(dT_back))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be dT");
		return NULL;
	}
	if (!R_wrapper_Check(R_back))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be R");
		return NULL;
	}
	if (!dR_wrapper_Check(dR_back))
	{
		PyErr_SetString(PyExc_TypeError, "6th argument must be dR");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "7th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "9th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (T_front->wvls != self->wvls || R_front_reverse->wvls != self->wvls  || T_back->wvls != self->wvls || dT_back->wvls != self->wvls || R_back->wvls != self->wvls || dR_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dT_with_backside_2(self->spectrum, T_front->spectrum, R_front_reverse->spectrum, T_back->spectrum, dT_back->spectrum, R_back->spectrum, dR_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dT_wrapper_type_methods[] =
{
	{"calculate_dT",														(PyCFunction)calculate_dT_wrapper,														METH_VARARGS},
	{"calculate_dT_with_backside",							(PyCFunction)calculate_dT_with_backside_wrapper,							METH_VARARGS},
	{"calculate_dT_with_backside_2",						(PyCFunction)calculate_dT_with_backside_2_wrapper,						METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dT_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dT",																				/* tp_name */
	0,																									/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dT class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dT_wrapper_type_methods,														/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dA_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dA_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*dR;
	spectrum_wrapper_object										*dT;

	if (!PyArg_ParseTuple(args, "OO:dA.calculate_dA", &dR, &dT))
		return NULL;

	/* Check the type of the arguments. */
	if (!spectrum_wrapper_Check(dR))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be dR");
		return NULL;
	}
	if (!spectrum_wrapper_Check(dT))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be dT");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dA(self->spectrum, dR->spectrum, dT->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dA_wrapper_type_methods[] =
{
	{"calculate_dA",														(PyCFunction)calculate_dA_wrapper,														METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dA_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dA",																				/* tp_name */
	0,																									/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dA class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dA_wrapper_type_methods,														/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dr_phase_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dr_phase_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	matrices_wrapper_object										*dM;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOOd:phase.calculate_r_phase", &M, &dM, &N_m, &N_s, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!matrices_wrapper_Check(dM))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_m))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be dN");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls || dM->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dr_phase(self->spectrum, M->matrices, dM->matrices, N_m->N, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dt_phase_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dt_phase_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	matrices_wrapper_object										*dM;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOOd:phase.calculate_t_phase", &M, &dM, &N_m, &N_s, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!matrices_wrapper_Check(dM))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_m))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be dN");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (M->wvls != self->wvls || dM->wvls != self->wvls || N_m->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dt_phase(self->spectrum, M->matrices, dM->matrices, N_m->N, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dphase_wrapper_type_methods[] =
{
	{"calculate_dr_phase",											(PyCFunction)calculate_dr_phase_wrapper,											METH_VARARGS},
	{"calculate_dt_phase",											(PyCFunction)calculate_dt_phase_wrapper,											METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dphase_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dphase",																		/* tp_name */
	sizeof(spectrum_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dphase class",																			/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dphase_wrapper_type_methods,												/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dGD_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dGD_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*dphase;

	if (!PyArg_ParseTuple(args, "O", &dphase))
		return NULL;

	/* Check the type of the arguments. */
	if (!dphase_wrapper_Check(dphase))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be dphase");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dphase->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "argument must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dGD(self->spectrum, dphase->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dGD_wrapper_type_methods[] =
{
	{"calculate_dGD",														(PyCFunction)calculate_dGD_wrapper,												METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dGD_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dGD",																				/* tp_name */
	sizeof(spectrum_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dGD class",																				/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dGD_wrapper_type_methods,														/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_dGDD_wrapper                                            */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_dGDD_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*dphase;

	if (!PyArg_ParseTuple(args, "O", &dphase))
		return NULL;

	/* Check the type of the arguments. */
	if (!dphase_wrapper_Check(dphase))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be dphase");
		return NULL;
	}

	/* Check the value of arguments. */
	if (dphase->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "argument must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dGDD(self->spectrum, dphase->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef dGDD_wrapper_type_methods[] =
{
	{"calculate_dGDD",													(PyCFunction)calculate_dGDD_wrapper,											METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject dGDD_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.dGDD",																			/* tp_name */
	sizeof(spectrum_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	0,																									/* tp_dealloc */
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
	"dGDD class",																				/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	dGDD_wrapper_type_methods,													/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	&spectrum_wrapper_type,															/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	0,																									/* tp_init */
	0,																									/* tp_alloc */
	0,																									/* tp_new */
};


#ifdef __cplusplus
}
#endif
