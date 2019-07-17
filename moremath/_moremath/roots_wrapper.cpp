/*
 *
 *  roots_wrapper.cpp
 *
 *
 *  Wrapper around functions in roots.cpp to make them available to
 *  Python.
 *
 *  Copyright (c) 2006,2007,2013 Stephane Larouche.
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

#include "_moremath.h"
#include "_moremath_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* roots_linear_wrapper                                              */
/*                                                                   */
/*********************************************************************/
static PyObject * roots_linear_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*roots_;
	double												*roots;
	PyObject											*a_0_;
	double												a_0;
	PyObject											*a_1_;
	double												a_1;
	int														nb_roots;
	Py_ssize_t										i;
	PyObject											*root;

	if (!PyArg_ParseTuple(args, "OOO:roots.roots_linear", &roots_, &a_0_, &a_1_))
		return NULL;

	a_0 = PyFloat_AsDouble(a_0_);
	a_1 = PyFloat_AsDouble(a_1_);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	/* Create an array for roots. */
	roots = (double *)malloc(1*sizeof(double));

	if (!roots)
		return PyErr_NoMemory();

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	nb_roots = roots_linear(roots, a_0, a_1);
	Py_END_ALLOW_THREADS

	/* Copy the matrix and vectors to the Python structures. */
	for (i = 0; i < nb_roots; i++)
	{
		root = PyFloat_FromDouble(roots[i]);
		if (root)
			PyList_SetItem(roots_, i, root);
	}

	/* Free the C structures. */
	free(roots);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	return Py_BuildValue("i", nb_roots);
}


/*********************************************************************/
/*                                                                   */
/* roots_quadratic_wrapper                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * roots_quadratic_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*roots_;
	double												*roots;
	PyObject											*a_0_;
	double												a_0;
	PyObject											*a_1_;
	double												a_1;
	PyObject											*a_2_;
	double												a_2;
	int														nb_roots;
	Py_ssize_t										i;
	PyObject											*root;

	if (!PyArg_ParseTuple(args, "OOOO:roots.roots_quadratic", &roots_, &a_0_, &a_1_, &a_2_))
		return NULL;

	a_0 = PyFloat_AsDouble(a_0_);
	a_1 = PyFloat_AsDouble(a_1_);
	a_2 = PyFloat_AsDouble(a_2_);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	/* Create an array for roots. */
	roots = (double *)malloc(2*sizeof(double));

	if (!roots)
		return PyErr_NoMemory();

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	nb_roots = roots_quadratic(roots, a_0, a_1, a_2);
	Py_END_ALLOW_THREADS

	/* Copy the matrix and vectors to the Python structures. */
	for (i = 0; i < nb_roots; i++)
	{
		root = PyFloat_FromDouble(roots[i]);
		if (root)
			PyList_SetItem(roots_, i, root);
	}

	/* Free the C structures. */
	free(roots);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	return Py_BuildValue("i", nb_roots);
}


/*********************************************************************/
/*                                                                   */
/* roots_cubic_wrapper                                               */
/*                                                                   */
/*********************************************************************/
static PyObject * roots_cubic_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*roots_;
	double												*roots;
	PyObject											*a_0_;
	double												a_0;
	PyObject											*a_1_;
	double												a_1;
	PyObject											*a_2_;
	double												a_2;
	PyObject											*a_3_;
	double												a_3;
	int														nb_roots;
	Py_ssize_t										i;
	PyObject											*root;

	if (!PyArg_ParseTuple(args, "OOOOO:roots.roots_cubic", &roots_, &a_0_, &a_1_, &a_2_, &a_3_))
		return NULL;

	a_0 = PyFloat_AsDouble(a_0_);
	a_1 = PyFloat_AsDouble(a_1_);
	a_2 = PyFloat_AsDouble(a_2_);
	a_3 = PyFloat_AsDouble(a_3_);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	/* Create an array for roots. */
	roots = (double *)malloc(3*sizeof(double));

	if (!roots)
		return PyErr_NoMemory();

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	nb_roots = roots_cubic(roots, a_0, a_1, a_2, a_3);
	Py_END_ALLOW_THREADS

	/* Copy the matrix and vectors to the Python structures. */
	for (i = 0; i < nb_roots; i++)
	{
		root = PyFloat_FromDouble(roots[i]);
		if (root)
			PyList_SetItem(roots_, i, root);
	}

	/* Free the C structures. */
	free(roots);

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
		return NULL;

	return Py_BuildValue("i", nb_roots);
}


static PyMethodDef roots_methods[] =
{
	{"roots_linear",									roots_linear_wrapper,									METH_VARARGS},
	{"roots_quadratic",								roots_quadratic_wrapper,							METH_VARARGS},
	{"roots_cubic",										roots_cubic_wrapper,									METH_VARARGS},
	{NULL} /* Sentinel */
};


/*********************************************************************/
/*                                                                   */
/* init_roots                                                        */
/*                                                                   */
/*                                                                   */
/* Init this module so that it can be called from Python.            */
/*                                                                   */
/*********************************************************************/
PyObject * init_roots()
{
	PyObject					*roots_module;

	roots_module = Py_InitModule("moremath.roots", roots_methods);

	return roots_module;
}


#ifdef __cplusplus
}
#endif
