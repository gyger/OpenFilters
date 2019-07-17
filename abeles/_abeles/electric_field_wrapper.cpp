/*
 *
 *  electric_field_wrapper.cpp
 *
 *
 *  Wrapper around functions in electric_field.cpp to make them
 *  available to Python in an electric_field class.
 *
 *  Copyright (c) 2004-2007,2013 Stephane Larouche.
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
/* calculate_electric_field_wrapper                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * calculate_electric_field_wrapper(spectrum_wrapper_object *self, PyObject *args)
{
	matrices_wrapper_object										*M;
	N_wrapper_object													*N_s;
	sin2_wrapper_object												*sin2_theta_0;
	double																		polarization;

	if (!PyArg_ParseTuple(args, "OOOd:electric_field.calculate_electric_field", &M, &N_s, &sin2_theta_0, &polarization))
		return NULL;

	/* Check the type of the arguments. */
	if (!matrices_wrapper_Check(M))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be matrices");
		return NULL;
	}
	if (!N_wrapper_Check(N_s))
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
	if (M->wvls != self->wvls || N_s->wvls != self->wvls || sin2_theta_0->wvls != self->wvls)
	{
		PyErr_SetString(PyExc_ValueError, "arguments must share wvls of the object");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	calculate_electric_field(self->spectrum, M->matrices, N_s->N, sin2_theta_0->sin2, polarization);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


static PyMethodDef electric_field_wrapper_type_methods[] =
{
	{"calculate_electric_field",								(PyCFunction)calculate_electric_field_wrapper,								METH_VARARGS},
	{NULL} /* Sentinel */
};


PyTypeObject electric_field_wrapper_type = {
	PyObject_HEAD_INIT(NULL)
	0,																									/* ob_size */
	"abeles.electric_field",														/* tp_name */
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
	"electric_field class",															/* tp_doc */
	0,																									/* tp_traverse */
	0,																									/* tp_clear */
	0,																									/* tp_richcompare */
	0,																									/* tp_weaklistoffset */
	0,																									/* tp_iter */
	0,																									/* tp_iternext */
	electric_field_wrapper_type_methods,								/* tp_methods */
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
