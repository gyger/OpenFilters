/*
 *
 *  spectro_wrapper.cpp
 *
 *
 *  Wrapper around functions in spectro.cpp to make them available to
 *  Python in various classes.
 *
 *  Copyright (c) 2002-2007,2009,2012 Stephane Larouche.
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
/* new_spectrum_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * new_spectrum_wrapper(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	spectrum_wrapper_object										*self;

	self = (spectrum_wrapper_object *)type->tp_alloc(type, 0);

	if (self)
	{
		self->wvls = NULL;
		self->spectrum = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* init_spectrum_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static int init_spectrum_wrapper(spectrum_wrapper_object *self, PyObject *args, PyObject *kwds)
{
	wvls_wrapper_object												*wvls;
	PyObject																	*tmp;

	if (!PyArg_ParseTuple(args, "O:spectrum.__init__", &wvls))
		return -1;

	/* Check the type of the arguments. */
	if (!wvls_wrapper_Check(wvls))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be wvls");
		return -1;
	}

	/* Delete previous instance of spectrum, if it exists. */
	if (self->spectrum)
	{
		del_spectrum(self->spectrum);
		self->spectrum = NULL;
	}

	/* Keep a local copy of wvls. */
	tmp = (PyObject *)self->wvls;
	Py_INCREF(wvls);
	self->wvls = wvls;
	Py_XDECREF(tmp);

	/* Create the spectrum. */
	self->spectrum = new_spectrum(self->wvls->wvls);
	if (!self->spectrum)
	{
		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* dealloc_spectrum_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static void dealloc_spectrum_wrapper(spectrum_wrapper_object *self)
{
	del_spectrum(self->spectrum);

	Py_XDECREF(self->wvls);

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* spectrum_wrapper_length                                           */
/*                                                                   */
/*********************************************************************/
static Py_ssize_t spectrum_wrapper_length(spectrum_wrapper_object *self)
{
	return self->wvls->wvls->length;
}


/*********************************************************************/
/*                                                                   */
/* spectrum_wrapper_item                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * spectrum_wrapper_item(spectrum_wrapper_object *self, Py_ssize_t i)
{
	PyObject																	*item;
	double																		spectrum;

	/* Verify the index. */
	if (i < 0 || i >= (self->wvls->wvls->length))
	{
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	spectrum = self->spectrum->data[i];

	REPLACE_NAN_OR_INF(spectrum, 0.0);

	item = PyFloat_FromDouble(spectrum);

	return item;
}


/*********************************************************************/
/*                                                                   */
/* spectrum_wrapper_subscript                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * spectrum_wrapper_subscript(spectrum_wrapper_object* self, PyObject* item)
{
	Py_ssize_t																start, stop, step, slicelength, cur, i;
	PyObject																	*result;
	PyObject																	*element;
	double																		spectrum;

	if (PyIndex_Check(item))
	{
		i = PyNumber_AsSsize_t(item, PyExc_IndexError);
		if (i == -1 && PyErr_Occurred())
			return NULL;
		if (i < 0)
			i += self->wvls->wvls->length;
		return spectrum_wrapper_item(self, i);
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
				spectrum = self->spectrum->data[cur];

				REPLACE_NAN_OR_INF(spectrum, 0.0);

				element = PyFloat_FromDouble(spectrum);
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


static PyMethodDef spectrum_wrapper_type_methods[] =
{
	{NULL} /* Sentinel */
};


static PySequenceMethods spectrum_wrapper_as_sequence = {
	(lenfunc)spectrum_wrapper_length,										/* sq_length */
	0,																									/* sq_concat */
	0,																									/* sq_repeat */
	(ssizeargfunc)spectrum_wrapper_item,								/* sq_item */
	0,																									/* sq_slice */
	0,																									/* sq_ass_item */
	0																										/* sq_ass_slice */
};


static PyMappingMethods spectrum_wrapper_as_mapping = {
	(lenfunc)spectrum_wrapper_length,										/* mp_length */
	(binaryfunc)spectrum_wrapper_subscript,							/* mp_subscript */
	0,																									/* mp_ass_subscript */
};


PyTypeObject spectrum_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.spectrum",																	/* tp_name */
	sizeof(spectrum_wrapper_object),										/* tp_basicsize */
	0,																									/* tp_itemsize */
	(destructor)dealloc_spectrum_wrapper,								/* tp_dealloc */
	0,																									/* tp_print */
	0,																									/* tp_getattr */
	0,																									/* tp_setattr */
	0,																									/* tp_compare */
	0,																									/* tp_repr */
	0,																									/* tp_as_number */
	&spectrum_wrapper_as_sequence,											/* tp_as_sequence */
	&spectrum_wrapper_as_mapping,												/* tp_as_mapping */
	0,																									/* tp_hash */
	0,																									/* tp_call */
	0,																									/* tp_str */
	0,																									/* tp_getattro */
	0,																									/* tp_setattro */
	0,																									/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,																	/* tp_flags */
	"spectrum class",																		/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	spectrum_wrapper_type_methods,											/* tp_methods */
	0,																									/* tp_members */
	0,																									/* tp_getset */
	0,																									/* tp_base */
	0,																									/* tp_dict */
	0,																									/* tp_descr_get */
	0,																									/* tp_descr_set */
	0,																									/* tp_dictoffset */
	(initproc)init_spectrum_wrapper,										/* tp_init */
	0,																									/* tp_alloc */
	new_spectrum_wrapper,																/* tp_new */
};


/*********************************************************************/
/*                                                                   */
/* calculate_R_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_R_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "Od:spectrum.calculate_R", &r_and_t, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
		return NULL;
	}

	/* Check the value of arguments. */
	if (r_and_t->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_R(self->spectrum, r_and_t->r_and_t, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_R_with_backside_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_R_with_backside_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*R_front;
	spectrum_wrapper_object										*T_front_reverse;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*R_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOOdO:spectrum.calculate_R_with_backside", &T_front, &R_front, &T_front_reverse, &R_front_reverse, &R_back, &N_s, &thickness, &sin2_theta_0))
		return NULL;

	/* Check the type of the arguments. */
	if (!T_wrapper_Check(T_front))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be T");
		return NULL;
	}
	if (!R_wrapper_Check(R_front))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be R");
		return NULL;
	}
	if (!T_wrapper_Check(T_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be T");
		return NULL;
	}
	if (!R_wrapper_Check(R_front_reverse))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be R");
		return NULL;
	}
	if (!R_wrapper_Check(R_back))
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
	if (T_front->wvls != self->wvls || R_front->wvls != self->wvls || T_front_reverse->wvls != self->wvls || R_front_reverse->wvls != self->wvls || R_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_R_with_backside(self->spectrum, T_front->spectrum, R_front->spectrum, T_front_reverse->spectrum, R_front_reverse->spectrum, R_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef R_wrapper_type_methods[] =
{
	{"calculate_R",															(PyCFunction)calculate_R_wrapper,															METH_VARARGS},
	{"calculate_R_with_backside",								(PyCFunction)calculate_R_with_backside_wrapper,								METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject R_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.R",																					/* tp_name */
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
	"R class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	R_wrapper_type_methods,															/* tp_methods */
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
/* calculate_T_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_T_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	r_and_t_wrapper_object										*r_and_t;
	N_wrapper_object													*N_i;
	N_wrapper_object													*N_e;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOd:spectrum.calculate_T", &r_and_t, &N_i, &N_e, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!r_and_t_wrapper_Check(r_and_t))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be r_and_t");
		return NULL;
	}
	if (!N_wrapper_Check(N_i))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be N");
		return NULL;
	}
	if (!N_wrapper_Check(N_e))
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
	if (r_and_t->wvls != self->wvls || N_i->wvls != self->wvls || N_e->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_T(self->spectrum, r_and_t->r_and_t, N_i->N, N_e->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_T_with_backside_wrapper                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_T_with_backside_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*T_front;
	spectrum_wrapper_object										*R_front_reverse;
	spectrum_wrapper_object										*T_back;
	spectrum_wrapper_object										*R_back;
	N_wrapper_object													*N_s;
	double																		thickness;
	sin2_wrapper_object												*sin2_theta_0;

	if (!PyArg_ParseTuple(args, "OOOOOdO", &T_front, &R_front_reverse, &T_back, &R_back, &N_s, &thickness, &sin2_theta_0))
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
	if (!R_wrapper_Check(R_back))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be R");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be N");
		return NULL;
	}
	if (!sin2_wrapper_Check(sin2_theta_0))
	{
		PyErr_SetString(PyExc_TypeError, "7th argument must be sin2");
		return NULL;
	}

	/* Check the value of arguments. */
	if (T_front->wvls != self->wvls || R_front_reverse->wvls != self->wvls || T_back->wvls != self->wvls || R_back->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_T_with_backside(self->spectrum, T_front->spectrum, R_front_reverse->spectrum, T_back->spectrum, R_back->spectrum, N_s->N, thickness, sin2_theta_0->sin2);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef T_wrapper_type_methods[] =
{
	{"calculate_T",															(PyCFunction)calculate_T_wrapper,															METH_VARARGS},
	{"calculate_T_with_backside",								(PyCFunction)calculate_T_with_backside_wrapper,								METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject T_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.T",																					/* tp_name */
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
	"T class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	T_wrapper_type_methods,															/* tp_methods */
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
/* calculate_A_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_A_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*R;
	spectrum_wrapper_object										*T;

	if (!PyArg_ParseTuple(args, "OO", &R, &T))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	calculate_A(self->spectrum, R->spectrum, T->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef A_wrapper_type_methods[] =
{
	{"calculate_A",															(PyCFunction)calculate_A_wrapper,															METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject A_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.A",																					/* tp_name */
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
	"A class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	A_wrapper_type_methods,															/* tp_methods */
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
