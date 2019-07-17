/*
 *
 *  QR_wrapper.cpp
 *
 *
 *  Wrapper around functions in QR.cpp to make them available to
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
/* QR_wrapper                                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * QR_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*norms_ = NULL;
	double												*norms = NULL;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	long													rank;
	PyObject											*column, *element;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOO|O:QR.QR", &A_, &diag_, &perm_, &norms_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (norms_ && (!PyList_Check(norms_) || PyList_Size(norms_) != n))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument, if present, must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm and norms. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	if (norms_) norms = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || (norms_ && !norms))
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix into the C one. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	rank = QR(n, m, A, diag, perm, norms);
	Py_END_ALLOW_THREADS

	if (rank == -1)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the matrix and vectors to the Python structures. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyFloat_FromDouble(A[j][i]);
			PyList_SetItem(column, i, element);
		}
		element = PyFloat_FromDouble(diag[j]);
		PyList_SetItem(diag_, j, element);
		element = PyLong_FromLong(perm[j]);
		PyList_SetItem(perm_, j, element);
	}
	if (norms)
	{
		for (j = 0; j < n; j++)
		{
			element = PyFloat_FromDouble(norms[j]);
			PyList_SetItem(norms_, j, element);
		}
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(norms);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	return Py_BuildValue("l", rank);
}


/*********************************************************************/
/*                                                                   */
/* QTb_wrapper                                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * QTb_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*b_;
	double												*b;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOO:QR.QTb", &A_, &diag_, &perm_, &b_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(b_) || PyList_Size(b_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm and b. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	b = (double *)malloc(m*sizeof(double));

	if (!diag || !perm || !b)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(b_, i);
		b[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	QTb(n, m, A, diag, perm, b);
	Py_END_ALLOW_THREADS

	/* Copy the solution to the Python list. */
	for (i = 0; i < m; i++)
	{
		element = PyFloat_FromDouble(b[i]);
		PyList_SetItem(b_, i, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(b);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* Qb_wrapper                                                        */
/*                                                                   */
/*********************************************************************/
static PyObject * Qb_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*b_;
	double												*b;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOO:QR.Qb", &A_, &diag_, &perm_, &b_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(b_) || PyList_Size(b_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm and b. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	b = (double *)malloc(m*sizeof(double));

	if (!diag || !perm || !b)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(b_, i);
		b[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	Qb(n, m, A, diag, perm, b);
	Py_END_ALLOW_THREADS

	/* Copy the solution to the Python list. */
	for (i = 0; i < m; i++)
	{
		element = PyFloat_FromDouble(b[i]);
		PyList_SetItem(b_, i, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(b);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* R_solve_wrapper                                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * R_solve_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*c_;
	double												*c;
	PyObject											*x_;
	double												*x;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	moremath_error_type						return_value;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOOO:QR.R_solve", &A_, &diag_, &perm_, &c_, &x_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(c_) || PyList_Size(c_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	if (!PyList_Check(x_) || PyList_Size(x_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm, c and x. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	c = (double *)malloc(m*sizeof(double));
	x = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || !c || !x)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(c_, i);
		c[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	return_value = R_solve(n, m, A, diag, perm, c, x);
	Py_END_ALLOW_THREADS

	if (return_value == MOREMATH_OUT_OF_MEMORY)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the solution to the Python list. */
	for (j = 0; j < n; j++)
	{
		element = PyFloat_FromDouble(x[j]);
		PyList_SetItem(x_, j, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(c);
	free(x);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* RT_solve_wrapper                                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * RT_solve_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*c_;
	double												*c;
	PyObject											*z_;
	double												*z;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	moremath_error_type						return_value;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOOO:QR.RT_solve", &A_, &diag_, &perm_, &c_, &z_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(c_) || PyList_Size(c_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	if (!PyList_Check(z_) || PyList_Size(z_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm, c and z. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	c = (double *)malloc(m*sizeof(double));
	z = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || !c || !z)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(c_, i);
		c[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	return_value = RT_solve(n, m, A, diag, perm, c, z);
	Py_END_ALLOW_THREADS

	if (return_value == MOREMATH_OUT_OF_MEMORY)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the solution to the Python list. */
	for (j = 0; j < n; j++)
	{
		element = PyFloat_FromDouble(z[j]);
		PyList_SetItem(z_, j, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(c);
	free(z);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* rank_deficient_R_solve_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * rank_deficient_R_solve_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*c_;
	double												*c;
	PyObject											*x_;
	double												*x;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	moremath_error_type						return_value;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOOO:QR.rank_deficient_R_solve", &A_, &diag_, &perm_, &c_, &x_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(c_) || PyList_Size(c_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	if (!PyList_Check(x_) || PyList_Size(x_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A) return PyErr_NoMemory();

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm, c and x. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	c = (double *)malloc(m*sizeof(double));
	x = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || !c || !x)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(c_, i);
		c[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	return_value = rank_deficient_R_solve(n, m, A, diag, perm, c, x);
	Py_END_ALLOW_THREADS

	if (return_value == MOREMATH_OUT_OF_MEMORY)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the solution to the Python list. */
	for (j = 0; j < n; j++)
	{
		element = PyFloat_FromDouble(x[j]);
		PyList_SetItem(x_, j, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(c);
	free(x);

	if (PyErr_Occurred()) return NULL;
	if (out_of_memory) return PyErr_NoMemory();

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* QR_solve_wrapper                                                  */
/*                                                                   */
/*********************************************************************/
static PyObject * QR_solve_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*b_;
	double												*b;
	PyObject											*x_ = NULL;
	double												*x;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	moremath_error_type						return_value;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOO|O:QR.QR_solve", &A_, &diag_, &perm_, &b_, &x_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(b_) || PyList_Size(b_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	if (x_ && (!PyList_Check(x_) || PyList_Size(x_) != n))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument, if present, must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* If necessary, create a list of x otherwise increase the reference
	 * since it will be returned at the end of the function. */
	if (x_ == NULL)
	{
		x_ = PyList_New(n);
		if (!x_) return NULL;
	}
	else
		Py_INCREF(x_);

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A)
	{
		Py_DECREF(x_);
		return PyErr_NoMemory();
	}

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			Py_DECREF(x_);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm, b and x. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	b = (double *)malloc(m*sizeof(double));
	x = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || !b || !x)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(b_, i);
		b[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	return_value = QR_solve(n, m, A, diag, perm, b, x);
	Py_END_ALLOW_THREADS

	if (return_value == MOREMATH_OUT_OF_MEMORY)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the solution to the Python list. */
	for (j = 0; j < n; j++)
	{
		element = PyFloat_FromDouble(x[j]);
		PyList_SetItem(x_, j, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++) free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(b);
	free(x);

	if (PyErr_Occurred())
	{
		Py_DECREF(x_);
		return NULL;
	}
	if (out_of_memory)
	{
		Py_DECREF(x_);
		return PyErr_NoMemory();
	}

	return x_;
}


/*********************************************************************/
/*                                                                   */
/* R_solve_with_update_wrapper                                       */
/*                                                                   */
/*********************************************************************/
static PyObject * R_solve_with_update_wrapper(PyObject *self, PyObject *args)
{
	PyObject											*A_;
	double												**A;
	PyObject											*diag_;
	double												*diag;
	PyObject											*perm_;
	long													*perm;
	PyObject											*c_;
	double												*c;
	PyObject											*D_;
	double												*D;
	PyObject											*x_ = NULL;
	double												*x;
	Py_ssize_t										n, m;
	Py_ssize_t										i, j;
	PyObject											*column, *element;
	moremath_error_type						return_value;
	bool													out_of_memory = false;

	if (!PyArg_ParseTuple(args, "OOOOO|O:QR.R_solve_with_update", &A_, &diag_, &perm_, &c_, &D_, &x_))
		return NULL;

	/* Check the input arguments and get the size of the matrix. */
	if (!PyList_Check(A_) || (n = PyList_Size(A_)) < 1 || !PyList_Check(column = PyList_GetItem(A_, 0)) || (m = PyList_Size(column)) < 1)
	{
		PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
		return NULL;
	}
	for (j = 1; j < n; j++)
	{
		if (!PyList_Check(column = PyList_GetItem(A_, j)) || PyList_Size(column) != m)
		{
			PyErr_SetString(PyExc_TypeError, "1st argument must be a list of lists defining a rectangular matrix");
			return NULL;
		}
	}

	if (!PyList_Check(diag_) || PyList_Size(diag_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(perm_) || PyList_Size(perm_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (!PyList_Check(c_) || PyList_Size(c_) != m)
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list of same size than the number of rows in the first argument");
		return NULL;
	}

	if (!PyList_Check(D_) || PyList_Size(D_) != n)
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	if (x_ && (!PyList_Check(x_) || PyList_Size(x_) != n))
	{
		PyErr_SetString(PyExc_TypeError, "6th argument must be a list of same size than the number of columns in the first argument");
		return NULL;
	}

	/* If necessary, create a list of x otherwise increase the reference
	 * since it will be returned at the end of the function. */
	if (x_ == NULL)
	{
		x_ = PyList_New(n);
		if (!x_) return NULL;
	}
	else
		Py_INCREF(x_);

	/* Create array for A. */
	A = (double **)malloc(n*sizeof(double *));

	if (!A)
	{
		Py_DECREF(x_);
		return PyErr_NoMemory();
	}

	for (j = 0; j < n; j++)
	{
		A[j] = (double *)malloc(m*sizeof(double));
		if (!A[j])
		{
			for(j--; j >= 0; j--)
				free(A[j]);
			free(A);
			Py_DECREF(x_);
			return PyErr_NoMemory();
		}
	}

	/* Create arrays for diag, perm, c, D and x. */
	diag = (double *)malloc(n*sizeof(double));
	perm = (long *)malloc(n*sizeof(long));
	c = (double *)malloc(m*sizeof(double));
	D = (double *)malloc(n*sizeof(double));
	x = (double *)malloc(n*sizeof(double));

	if (!diag || !perm || !c || !D || !x)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the Python A matrix and vectors into the C ones. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyList_GetItem(column, i);
			A[j][i] = PyFloat_AsDouble(element);
		}
		element = PyList_GetItem(diag_, j);
		diag[j] = PyFloat_AsDouble(element);
		element = PyList_GetItem(perm_, j);
		perm[j] = PyLong_AsLong(element);
		element = PyList_GetItem(D_, j);
		D[j] = PyFloat_AsDouble(element);
	}
	for (i = 0; i < m; i++)
	{
		element = PyList_GetItem(c_, i);
		c[i] = PyFloat_AsDouble(element);
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred()) goto finally;

	/* Execute the function. */
	Py_BEGIN_ALLOW_THREADS
	return_value = R_solve_with_update(n, m, A, diag, perm, c, D, x);
	Py_END_ALLOW_THREADS

	if (return_value == MOREMATH_OUT_OF_MEMORY)
	{
		out_of_memory = true;
		goto finally;
	}

	/* Copy the solution and the modified matrix to the Python lists. */
	for (j = 0; j < n; j++)
	{
		column = PyList_GetItem(A_, j);
		for (i = 0; i < m; i++)
		{
			element = PyFloat_FromDouble(A[j][i]);
			PyList_SetItem(column, i, element);
		}
	}
	for (j = 0; j < n; j++)
	{
		element = PyFloat_FromDouble(x[j]);
		PyList_SetItem(x_, j, element);
	}

	finally:

	/* Free the C structures. */
	for (j = 0; j < n; j++)
		free(A[j]);
	free(A);
	free(diag);
	free(perm);
	free(c);
	free(D);
	free(x);

	if (PyErr_Occurred())
	{
		Py_DECREF(x_);
		return NULL;
	}
	if (out_of_memory)
	{
		Py_DECREF(x_);
		return PyErr_NoMemory();
	}

	return x_;
}


static PyMethodDef QR_methods[] =
{
	{"QR",														QR_wrapper,														METH_VARARGS},
	{"QTb",														QTb_wrapper,													METH_VARARGS},
	{"Qb",														Qb_wrapper,														METH_VARARGS},
	{"R_solve",												R_solve_wrapper,											METH_VARARGS},
	{"RT_solve",											RT_solve_wrapper,											METH_VARARGS},
	{"rank_deficient_R_solve",				rank_deficient_R_solve_wrapper,				METH_VARARGS},
	{"QR_solve",											QR_solve_wrapper,											METH_VARARGS},
	{"R_solve_with_update",						R_solve_with_update_wrapper,					METH_VARARGS},
	{NULL} /* Sentinel */
};


/*********************************************************************/
/*                                                                   */
/* init_QR                                                           */
/*                                                                   */
/*                                                                   */
/* Init this module so that it can be called from Python.            */
/*                                                                   */
/*********************************************************************/
PyObject * init_QR()
{
	PyObject					*QR_module;

	QR_module = Py_InitModule("moremath.QR", QR_methods);

	return QR_module;
}


#ifdef __cplusplus
}
#endif
