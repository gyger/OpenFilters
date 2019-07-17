/*
 *
 *  phase_wrapper.cpp
 *
 *
 *  Wrapper around functions in phase.cpp to make them available to
 *  Python in an phase class.
 *
 *  Copyright (c) 2005-2007 Stephane Larouche.
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
/* calculate_r_phase_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_r_phase_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOd:phase.calculate_r_phase", &M, &N_m, &N_s, &sin2_theta_0, &polarization))
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
		PyErr_SetString(PyExc_TypeError, "3rd argument must be dN");
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
	calculate_r_phase(self->spectrum, M->matrices, N_m->N, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* calculate_t_phase_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_t_phase_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_m;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOOd:phase.calculate_t_phase", &M, &N_m, &N_s, &sin2_theta_0, &polarization))
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
		PyErr_SetString(PyExc_TypeError, "3rd argument must be dN");
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
	calculate_t_phase(self->spectrum, M->matrices, N_m->N, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef phase_wrapper_type_methods[] =
{
	{"calculate_r_phase",												(PyCFunction)calculate_r_phase_wrapper,												METH_VARARGS},
	{"calculate_t_phase",												(PyCFunction)calculate_t_phase_wrapper,												METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject phase_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.phase",																			/* tp_name */
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
	"phase class",																			/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	phase_wrapper_type_methods,													/* tp_methods */
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
/* calculate_GD_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_GD_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*phase;

	if (!PyArg_ParseTuple(args, "O", &phase))
		return NULL;

	/* Check the type of the arguments. */
	if (!phase_wrapper_Check(phase))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be phase");
		return NULL;
	}

	/* Check the value of arguments. */
	if (phase->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_GD(self->spectrum, phase->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef GD_wrapper_type_methods[] =
{
	{"calculate_GD",														(PyCFunction)calculate_GD_wrapper,												METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject GD_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.GD",																				/* tp_name */
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
	"GD class",																					/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	GD_wrapper_type_methods,														/* tp_methods */
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
/* calculate_GDD_wrapper                                             */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_GDD_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	spectrum_wrapper_object										*phase;

	if (!PyArg_ParseTuple(args, "O", &phase))
		return NULL;

	/* Check the type of the arguments. */
	if (!phase_wrapper_Check(phase))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be phase");
		return NULL;
	}

	/* Check the value of arguments. */
	if (phase->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_GDD(self->spectrum, phase->spectrum);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef GDD_wrapper_type_methods[] =
{
	{"calculate_GDD",														(PyCFunction)calculate_GDD_wrapper,												METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject GDD_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.GDD",																				/* tp_name */
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
	"GDD class",																				/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	GDD_wrapper_type_methods,														/* tp_methods */
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
