/*
 *
 *  needles_wrapper.cpp
 *
 *
 *  Wrapper around functions in needles.cpp to make them available to
 *  Python in various classes.
 *
 *  Copyright (c) 2005-2007,2012,2013 Stephane Larouche.
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
/* new_needle_matrices_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * new_needle_matrices_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	needle_matrices_wrapper_object						*self;

	self = (needle_matrices_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->needle_matrices = NULL;
		self->needle_matrices_wrappers = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_needle_matrices_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static int init_needle_matrices_wrapper(needle_matrices_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	Py_ssize_t																length, i;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "On:needle_matrices.__init__", &wvls, &length))
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
	if (self->needle_matrices_wrappers)
	{
		for (i = 0; i < self->needle_matrices->length; i++)
			if (self->needle_matrices_wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->needle_matrices_wrappers[i]);
		free(self->needle_matrices_wrappers);
		self->needle_matrices_wrappers = NULL;
	}

	/* Delete previous instance of needle_matrices, if it exists. */
	if (self->needle_matrices)
	{
		del_needle_matrices(self->needle_matrices);
		self->needle_matrices = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the needle_matrices. */
	self->needle_matrices = new_needle_matrices(self->wvls->wvls, length);
	if (!self->needle_matrices)
	{
		PyErr_NoMemory();
		return -1;
	}

	/* Make wrappers around the needle matrices. The ref count of the
	 * wrappers is decreased (to 0) so that they can be destroyed when
	 * the ref count of self drops to 0. But the ref count of self is
	 * increased first to avoid immediate destruction. */
	self->needle_matrices_wrappers = (matrices_wrapper_object **)malloc(self->needle_matrices->length*sizeof(matrices_wrapper_object *));
	if (!self->needle_matrices_wrappers)
	{
		PyErr_NoMemory();
		return -1;
	}
	for (i = 0; i < self->needle_matrices->length; i++)
		self->needle_matrices_wrappers[i] = NULL;
	for (i = 0; i < self->needle_matrices->length; i++)
	{
		self->needle_matrices_wrappers[i] = (matrices_wrapper_object *)matrices_wrapper_type.tp_alloc(&matrices_wrapper_type, 0);
		if (!self->needle_matrices_wrappers[i])
		{
			PyErr_NoMemory();
			return -1;
		}
		self->needle_matrices_wrappers[i]->wvls = self->wvls;
		self->needle_matrices_wrappers[i]->matrices = self->needle_matrices->M[i];
		self->needle_matrices_wrappers[i]->parent = (PyObject *)self;

		Py_INCREF(self);
		Py_DECREF(self->needle_matrices_wrappers[i]);
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_needle_matrices_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static void dealloc_needle_matrices_wrapper(needle_matrices_wrapper_object *self)
{
	Py_ssize_t																i;

	if (self->needle_matrices_wrappers)
	{
		for (i = 0; i < self->needle_matrices->length; i++)
			if (self->needle_matrices_wrappers[i])
				matrices_wrapper_type.tp_free((PyObject*)self->needle_matrices_wrappers[i]);
		free(self->needle_matrices_wrappers);
	}

	del_needle_matrices(self->needle_matrices);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_needle_position_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * set_needle_position_wrapper(needle_matrices_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i_needle;
	double																		position;

	if (!PyArg_ParseTuple(args, "nd:needle_matrices.set_needle_position", &i_needle, &position))
		return NULL;

	/* Check the value of the arguments. */
	if (i_needle < 0 || i_needle >= self->needle_matrices->length)
	{
		PyErr_SetString(PyExc_TypeError, "i_needle out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	set_needle_position(self->needle_matrices, i_needle, position);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_needle_positions_wrapper                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * set_needle_positions_wrapper(needle_matrices_wrapper_object *self, PyObject *args)
{
	double																		spacing;

	if (!PyArg_ParseTuple(args, "d:needle_matrices.set_needle_positions", &spacing))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	set_needle_positions(self->needle_matrices, spacing);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_needle_position_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * get_needle_position_wrapper(needle_matrices_wrapper_object *self, PyObject *args)
{
	Py_ssize_t																i_needle;
	double																		position;

	if (!PyArg_ParseTuple(args, "n:needle_matrices.get_needle_position", &i_needle))
		return NULL;

	/* Check the value of the arguments. */
	if (i_needle < 0 || i_needle >= self->needle_matrices->length)
	{
		PyErr_SetString(PyExc_TypeError, "i_needle out of range");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	position = get_needle_position(self->needle_matrices, i_needle);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", position);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dMi_needles_wrapper                                     */
/*                                                                   */
/*********************************************************************/
PyObject * calculate_dMi_needles_wrapper(needle_matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	N_wrapper_object													*N_n;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOdO:needle_matrices.calculate_dMi_needles", &N, &N_n, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!N_wrapper_Check(N))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_n))
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
	if (N->wvls != self->wvls || N_n->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dMi_needles(self->needle_matrices, N->N, N_n->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_dMi_steps_wrapper                                       */
/*                                                                   */
/*********************************************************************/
PyObject * calculate_dMi_steps_wrapper(needle_matrices_wrapper_object *self, PyObject *args)
{
	N_wrapper_object													*N;
	N_wrapper_object													*dN;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOdO:needle_matrices.calculate_dMi_steps", &N, &dN, &thickness, &sin2_theta_0))
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
		PyErr_SetString(PyExc_TypeError, "4th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (N->wvls != self->wvls || dN->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_dMi_steps(self->needle_matrices, N->N, dN->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* needle_matrices_wrapper_length                                    */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t needle_matrices_wrapper_length(needle_matrices_wrapper_object *self)
{
	return self->needle_matrices->length;
}


/*********************************************************************/
/*                                                                   */
/* needle_matrices_wrapper_item                                      */
/*                                                                   */
/*********************************************************************/
static PyObject * needle_matrices_wrapper_item(needle_matrices_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;

	/* Verify the index. */
	if (i < 0 || i >= (self->needle_matrices->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	item = (PyObject *)self->needle_matrices_wrappers[i];
	Py_INCREF(self);
	Py_INCREF(item);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* needle_matrices_wrapper_subscript                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * needle_matrices_wrapper_subscript(needle_matrices_wrapper_object* self, PyObject* item)
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
			i += self->needle_matrices->length;
		return needle_matrices_wrapper_item(self, i);
	}
	else if (PySlice_Check(item))
	{
		if (PySlice_GetIndicesEx((PySliceObject*)item, self->needle_matrices->length, &start, &stop, &step, &slicelength) < 0)
			return NULL;

		if (slicelength <= 0)
			return PyList_New(0);

		else
		{
			result = PyList_New(slicelength);
			if (!result) return NULL;

			for (cur = start, i = 0; i < slicelength; cur += step, i++)
			{
				element = (PyObject *)self->needle_matrices_wrappers[i];
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


static PyMethodDef needle_matrices_wrapper_type_methods[] =
{
	{"set_needle_position",											(PyCFunction)set_needle_position_wrapper,											METH_VARARGS},
	{"set_needle_positions",										(PyCFunction)set_needle_positions_wrapper,										METH_VARARGS},
	{"get_needle_position",											(PyCFunction)get_needle_position_wrapper,											METH_VARARGS},
	{"calculate_dMi_needles",										(PyCFunction)calculate_dMi_needles_wrapper,										METH_VARARGS},
	{"calculate_dMi_steps",											(PyCFunction)calculate_dMi_steps_wrapper,											METH_VARARGS},
	{NULL} /* Sentinel */
};


static PySequenceMethods needle_matrices_wrapper_as_sequence = {
	(lenfunc)needle_matrices_wrapper_length,						/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)needle_matrices_wrapper_item,					/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods needle_matrices_wrapper_as_mapping = {
	(lenfunc)needle_matrices_wrapper_length,						/* mp_length */
	(binaryfunc)needle_matrices_wrapper_subscript,			/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject needle_matrices_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.needle_matrices",														/* tp_name */
	sizeof(needle_matrices_wrapper_object),							/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_needle_matrices_wrapper,				/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&needle_matrices_wrapper_as_sequence,								/* tp_as_sequence */
	&needle_matrices_wrapper_as_mapping,								/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"needle_matrices class",														/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	needle_matrices_wrapper_type_methods,								/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_needle_matrices_wrapper,							/* tp_init */
	0,																									/* tp_alloc */
	new_needle_matrices_wrapper,												/* tp_new */
};


#ifdef __cplusplus
}
#endif
