/*
 *
 *  ellipso_wrapper.cpp
 *
 *
 *  Wrapper around functions in ellipso.cpp to make them available to
 *  Python in a Psi_and_Delta class.
 *
 *  Copyright (c) 2003-2007,2009,2012 Stephane Larouche.
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
/* new_Psi_and_Delta_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * new_Psi_and_Delta_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Psi_and_Delta_wrapper_object							*self;

	self = (Psi_and_Delta_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->Psi_and_Delta = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_Psi_and_Delta_wrapper                                        */
/*                                                                   */
/*********************************************************************/
static int init_Psi_and_Delta_wrapper(Psi_and_Delta_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:Psi_and_Delta.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of Psi_and_Delta, if it exists. */
	if (self->Psi_and_Delta)
	{
		del_Psi_and_Delta(self->Psi_and_Delta);
		self->Psi_and_Delta = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the Psi_and_Delta. */
	self->Psi_and_Delta = new_Psi_and_Delta(self->wvls->wvls);
	if (!self->Psi_and_Delta)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_Psi_and_Delta_wrapper                                     */
/*                                                                   */
/*********************************************************************/
static void dealloc_Psi_and_Delta_wrapper(Psi_and_Delta_wrapper_object *self)
{
	del_Psi_and_Delta(self->Psi_and_Delta);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* calculate_Psi_and_Delta_wrapper                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_Psi_and_Delta_wrapper(Psi_and_Delta_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t;

	if (!PyArg_ParseTuple(args, "O:Psi_and_Delta.calculate_Psi_and_Delta", &r_and_t))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_Psi_and_Delta(self->Psi_and_Delta, r_and_t->r_and_t);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_Psi_and_Delta_with_backside_wrapper                     */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_Psi_and_Delta_with_backside_wrapper(Psi_and_Delta_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t_front;
	r_and_t_wrapper_object										*r_and_t_front_reverse;
	r_and_t_wrapper_object										*r_and_t_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOdO:Psi_and_Delta.calculate_Psi_and_Delta_with_backside", &r_and_t_front, &r_and_t_front_reverse, &r_and_t_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
		return NULL;
	}
	if (!r_and_t_wrapper_Check(r_and_t_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be r_and_t");
		return NULL;
	}
	if (!r_and_t_wrapper_Check(r_and_t_back))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be r_and_t");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
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
	if (r_and_t_front->wvls != self->wvls || r_and_t_front_reverse->wvls != self->wvls || r_and_t_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_Psi_and_Delta_with_backside(self->Psi_and_Delta, r_and_t_front->r_and_t, r_and_t_front_reverse->r_and_t, r_and_t_back->r_and_t, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* get_Psi                                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Psi(Psi_and_Delta_wrapper_object *self)
{
	Py_ssize_t																i;
	PyObject																	*result;
	PyObject																	*element;
	double																		Psi;

	result = PyList_New(self->wvls->wvls->length);
	if (!result) return NULL;

	for (i = 0; i < self->wvls->wvls->length; i++)
	{
		Psi = self->Psi_and_Delta->Psi[i];

		REPLACE_NAN_OR_INF(Psi, 0.0);

		element = PyFloat_FromDouble(Psi);

		PyList_SetItem(result, i, element);
	}

	return result;
}


/*********************************************************************/
/*                                                                   */
/* get_Delta                                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * get_Delta(Psi_and_Delta_wrapper_object *self)
{
	Py_ssize_t																i;
	PyObject																	*result;
	PyObject																	*element;
	double																		Delta;

	result = PyList_New(self->wvls->wvls->length);
	if (!result) return NULL;

	for (i = 0; i < self->wvls->wvls->length; i++)
	{
		Delta = self->Psi_and_Delta->Delta[i];

		REPLACE_NAN_OR_INF(Delta, 0.0);

		element = PyFloat_FromDouble(Delta);

		PyList_SetItem(result, i, element);
	}

	return result;
}


/*********************************************************************/
/*                                                                   */
/* Psi_and_Delta_wrapper_length                                      */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t Psi_and_Delta_wrapper_length(Psi_and_Delta_wrapper_object *self)
{
	return self->wvls->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* Psi_and_Delta_wrapper_item                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * Psi_and_Delta_wrapper_item(Psi_and_Delta_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;
	double																		Psi, Delta;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	Psi = self->Psi_and_Delta->Psi[i];
	Delta = self->Psi_and_Delta->Delta[i];

	REPLACE_NAN_OR_INF(Psi, 0.0);
	REPLACE_NAN_OR_INF(Delta, 0.0);

	item = Py_BuildValue("dd", Psi, Delta);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* Psi_and_Delta_wrapper_subscript                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * Psi_and_Delta_wrapper_subscript(Psi_and_Delta_wrapper_object* self, PyObject* item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	PyObject																	*result;
	PyObject																	*element;
	double																		Psi, Delta;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->wvls->length;
		return Psi_and_Delta_wrapper_item(self, i);
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
				Psi = self->Psi_and_Delta->Psi[cur];
				Delta = self->Psi_and_Delta->Delta[cur];

				REPLACE_NAN_OR_INF(Psi, 0.0);
				REPLACE_NAN_OR_INF(Delta, 0.0);

				element = Py_BuildValue("dd", Psi, Delta);

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


static PySequenceMethods Psi_and_Delta_wrapper_as_sequence = {
	(lenfunc)Psi_and_Delta_wrapper_length,							/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)Psi_and_Delta_wrapper_item,						/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods Psi_and_Delta_wrapper_as_mapping = {
	(lenfunc)Psi_and_Delta_wrapper_length,							/* mp_length */
	(binaryfunc)Psi_and_Delta_wrapper_subscript,				/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


static PyMethodDef Psi_and_Delta_wrapper_type_methods[] =
{
	{"calculate_Psi_and_Delta",									(PyCFunction)calculate_Psi_and_Delta_wrapper,									METH_VARARGS},
	{"calculate_Psi_and_Delta_with_backside",		(PyCFunction)calculate_Psi_and_Delta_with_backside_wrapper,		METH_VARARGS},
	{"get_Psi",																	(PyCFunction)get_Psi,																					METH_NOARGS},
	{"get_Delta",																(PyCFunction)get_Delta,																				METH_NOARGS},
	{NULL} /* Sentinel */
};


PyTypeObject Psi_and_Delta_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.Psi_and_Delta",															/* tp_name */
	sizeof(Psi_and_Delta_wrapper_object),								/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_Psi_and_Delta_wrapper,					/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&Psi_and_Delta_wrapper_as_sequence,									/* tp_as_sequence */
	&Psi_and_Delta_wrapper_as_mapping,									/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"Psi_and_Delta class",															/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	Psi_and_Delta_wrapper_type_methods,									/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_Psi_and_Delta_wrapper,								/* tp_init */
	0,																									/* tp_alloc */
	new_Psi_and_Delta_wrapper,													/* tp_new */
};


#ifdef __cplusplus
}
#endif
