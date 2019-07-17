/*
 *
 *  Levenberg_Marquardt_wrapper.cpp
 *
 *
 *  Wrapper around functions in Levenberg_Marquardt.cpp to make them
 *  available to Python.
 *
 *  Copyright (c) 2006,2007,2012,2013 Stephane Larouche.
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
#include <new>

#include "_moremath.h"
#include "_moremath_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


/* This type is used by the Levenberg-Marquardt wrapper and the
 * callback class to save the thread state and an eventual error, to be
 * able to restore it later. */
typedef struct
{
  PyThreadState		*_save;
	PyObject				*_type;
	PyObject				*_value;
	PyObject				*_traceback;
} state_type;

class Levenberg_Marquardt_Python_callback_exception : std::exception {};


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_Python_callback::                             */
/*                                                                   */
/*********************************************************************/
class Levenberg_Marquardt_Python_callback : Levenberg_Marquardt_callback
{
	private:

	Py_ssize_t														const nb_par;
	Py_ssize_t														const nb_points;
	PyObject															* const f_;
	PyObject															* const df_;
	PyObject															* const pars_;
	PyObject															* const f_par;
	state_type														* const state;
	double																*Y;
	double																**dY;

	public:

	Levenberg_Marquardt_Python_callback(const Py_ssize_t nb_par, const Py_ssize_t nb_points, PyObject * const f, PyObject * const df, PyObject * const pars_, PyObject * const f_par, state_type * const state);
	~Levenberg_Marquardt_Python_callback();
	double const * const f(double const * const pars) const;
	double const ** const df(double const * const pars) const;
};


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_Python_callback::                             */
/* Levenberg_Marquardt_Python_callback                               */
/*                                                                   */
/* Initialize the Levenberg-Marquardt callback for Python.           */
/*                                                                   */
/*********************************************************************/
Levenberg_Marquardt_Python_callback::Levenberg_Marquardt_Python_callback(const Py_ssize_t nb_par, const Py_ssize_t nb_points, PyObject *f_, PyObject *df_, PyObject *pars_, PyObject *f_par, state_type * const state)
	:	nb_par(nb_par),
		nb_points(nb_points),
		f_(f_),
		df_(df_),
		pars_(pars_),
		f_par(f_par),
		state(state),
		Y(NULL),
		dY(NULL)
{
	Py_ssize_t														par;

	try
	{
		this->Y = new double[this->nb_points];
		this->dY = new double*[this->nb_par];
		for (par = 0; par < this->nb_par; par++)
			this->dY[par] = NULL;
		for (par = 0; par < this->nb_par; par++)
			this->dY[par] = new double[this->nb_points];
	}
	catch (const std::bad_alloc&)
	{
		delete[] this->Y;
		if (this->dY)
			for (par = 0; par < this->nb_par; par++)
				delete[] this->dY[par];
		delete[] this->dY;

		throw;
	}
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_Python_callback::                             */
/* ~Levenberg_Marquardt_Python_callback                              */
/*                                                                   */
/* Destroy the Levenberg-Marquardt callback for Python.              */
/*                                                                   */
/*********************************************************************/
Levenberg_Marquardt_Python_callback::~Levenberg_Marquardt_Python_callback()
{
	Py_ssize_t														par;

	delete[] this->Y;
	for (par = 0; par < this->nb_par; par++)
		delete[] this->dY[par];
	delete[] this->dY;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_Python_callback::f                            */
/*                                                                   */
/* Call the Python method to get Y                       .           */
/*                                                                   */
/*********************************************************************/
double const * const Levenberg_Marquardt_Python_callback::f(double const * const pars) const
{
	PyObject															*args;
	PyObject															*arg;
	PyObject															*answer;
	PyObject															*item;
	Py_ssize_t														par, point;
	Py_ssize_t														nargs, i;
	double																*Y;
	bool																	error = false;

	PyEval_RestoreThread(this->state->_save);

	nargs = 1;
	if (this->f_par)
		nargs += PyTuple_Size(this->f_par);

	args = PyTuple_New(nargs);

	if (!args)
	{
		if (!this->state->_type)
			PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
		this->state->_save = PyEval_SaveThread();

		throw Levenberg_Marquardt_Python_callback_exception();
	}

	for (par = 0; par < this->nb_par; par++)
	{
		arg = PyFloat_FromDouble(pars[par]);

		if (!arg)
		{
			Py_DECREF(args);

			if (!this->state->_type)
				PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
			this->state->_save = PyEval_SaveThread();

			throw Levenberg_Marquardt_Python_callback_exception();
		}

		PyList_SetItem(this->pars_, par, arg);
	}

	Py_INCREF(this->pars_);
	PyTuple_SetItem(args, 0, this->pars_);

	for (i = 1; i < nargs; i++)
	{
		arg = PyTuple_GetItem(this->f_par, i-1);
		Py_INCREF(arg);
		PyTuple_SetItem(args, i, arg);
	}

	answer = PyObject_CallObject(this->f_, args);

	if (answer)
	{
		if (PyCObject_Check(answer))
		{
			Y = (double *)PyCObject_AsVoidPtr(answer);
			for (point = 0; point < this->nb_points; point++)
				this->Y[point] = Y[point];
		}
		else if (PyList_Check(answer) && PyList_Size(answer) == this->nb_points)
		{
			for (point = 0; point < this->nb_points; point++)
			{
				item = PyList_GetItem(answer, point);
				this->Y[point] = PyFloat_AsDouble(item);
			}
		}
		else
		{
			PyErr_SetString(PyExc_TypeError, "callback f must return a list of nb_points floats");
		}
	}

	Py_DECREF(args);
	Py_XDECREF(answer);

	if (PyErr_Occurred())
		error = true;

	if (!this->state->_type)
		PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
	this->state->_save = PyEval_SaveThread();

	if (error)
		throw Levenberg_Marquardt_Python_callback_exception();

	return (double const * const)this->Y;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_Python_callback::df                           */
/*                                                                   */
/* Call the Python method to get dY                      .           */
/*                                                                   */
/*********************************************************************/
double const ** const Levenberg_Marquardt_Python_callback::df(double const * const pars) const
{
	PyObject															*args;
	PyObject															*arg;
	PyObject															*answer;
	PyObject															*column, *item;
	Py_ssize_t														par, point;
	Py_ssize_t														nargs, i;
	double																**dY;
	bool																	error = false;

	PyEval_RestoreThread(this->state->_save);

	nargs = 1;
	if (this->f_par)
		nargs += PyTuple_Size(this->f_par);

	args = PyTuple_New(nargs);

	if (!args)
	{
		if (!this->state->_type)
			PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
		this->state->_save = PyEval_SaveThread();

		throw Levenberg_Marquardt_Python_callback_exception();
	}

	for (par = 0; par < this->nb_par; par++)
	{
		arg = PyFloat_FromDouble(pars[par]);

		if (!arg)
		{
			Py_DECREF(args);

			if (!this->state->_type)
				PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
			this->state->_save = PyEval_SaveThread();

			throw Levenberg_Marquardt_Python_callback_exception();
		}

		PyList_SetItem(this->pars_, par, arg);
	}

	Py_INCREF(this->pars_);
	PyTuple_SetItem(args, 0, this->pars_);

	for (i = 1; i < nargs; i++)
	{
		item = PyTuple_GetItem(this->f_par, i-1);
		Py_INCREF(item);
		PyTuple_SetItem(args, i, item);
	}

	answer = PyObject_CallObject(this->df_, args);

	if (answer)
	{
		if (PyCObject_Check(answer))
		{
			dY = (double **)PyCObject_AsVoidPtr(answer);
			for (par = 0; par < this->nb_par; par++)
				for (point = 0; point < this->nb_points; point++)
					this->dY[par][point] = dY[par][point];
		}
		else if (PyList_Check(answer) && PyList_Size(answer) == this->nb_par)
		{
			for (par = 0; par < this->nb_par; par++)
			{
				column = PyList_GetItem(answer, par);
				if (!PyList_Check(column) || PyList_Size(column) != this->nb_points)
				{
					PyErr_SetString(PyExc_TypeError, "callback df must return a list of nb_par lists of nb_points floats");
					break;
				}
				for (point = 0; point < this->nb_points; point++)
				{
					item = PyList_GetItem(column, point);
					this->dY[par][point] = PyFloat_AsDouble(item);
				}
			}
		}
		else
		{
			PyErr_SetString(PyExc_TypeError, "callback df must return a list of nb_par lists of nb_points floats");
		}
	}

	Py_DECREF(args);
	Py_XDECREF(answer);

	if (PyErr_Occurred())
		error = true;

	if (!this->state->_type)
		PyErr_Fetch(&(this->state->_type), &(this->state->_value), &(this->state->_traceback));
	this->state->_save = PyEval_SaveThread();

	if (error)
		throw Levenberg_Marquardt_Python_callback_exception();

	return (const double **)this->dY;
}


typedef struct {
	PyObject_HEAD
	PyObject															*f;
	PyObject															*df;
	PyObject															*a_;
	double																*a;
	double																*Yi;
	double																*sigma;
	PyObject															*f_par;
	Py_ssize_t														nb_par;
	Py_ssize_t														nb_points;
	Levenberg_Marquardt_Python_callback		*callback;
	Levenberg_Marquardt										*instance;
	state_type														state;
} Levenberg_Marquardt_object;


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_new                                           */
/*                                                                   */
/*********************************************************************/
static PyObject * Levenberg_Marquardt_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Levenberg_Marquardt_object						*self;

	self = (Levenberg_Marquardt_object *)type->tp_alloc(type, 0);

	if (self != NULL)
	{
		self->f = NULL;
		self->df = NULL;
		self->a_= NULL;
		self->a = NULL;
		self->Yi = NULL;
		self->sigma = NULL;
		self->f_par = NULL;
		self->callback = NULL;
		self->instance = NULL;
		self->state._type = NULL;
		self->state._value = NULL;
		self->state._traceback = NULL;
	}

	return (PyObject *)self;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_init                                          */
/*                                                                   */
/*********************************************************************/
static int Levenberg_Marquardt_init(Levenberg_Marquardt_object *self, PyObject *args)
{
	PyObject															*f;
	PyObject															*df;
	PyObject															*a_;
	double																*a;
	PyObject															*Yi_;
	double																*Yi;
	PyObject															*sigma_;
	double																*sigma;
	PyObject															*f_par = NULL;
	Py_ssize_t														nargs;
	Py_ssize_t														nb_par, nb_points;
	Py_ssize_t														i;

	/* The number of input arguments. */
	nargs = PyTuple_Size(args);

	/* Check that the number of arguments is at least five. */
	if (nargs < 5)
	{
		PyErr_Format(PyExc_TypeError, "__init__() takes at least 5 arguments (%zd given)", nargs);
		return -1;
	}

	f = PyTuple_GetItem(args, 0);
	df = PyTuple_GetItem(args, 1);
	a_ = PyTuple_GetItem(args, 2);
	Yi_ = PyTuple_GetItem(args, 3);
	sigma_ = PyTuple_GetItem(args, 4);

	/* Verify the content of the variables. */
	if (!PyCallable_Check(f))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be callable");
		return -1;
	}
	if (!PyCallable_Check(df))
	{
		PyErr_SetString(PyExc_TypeError, "2nd argument must be callable");
		return -1;
	}
	if (!PyList_Check(a_))
	{
		PyErr_SetString(PyExc_TypeError, "3rd argument must be a list");
		return -1;
	}
	if (!PyList_Check(Yi_))
	{
		PyErr_SetString(PyExc_TypeError, "4th argument must be a list");
		return -1;
	}
	if (!PyList_Check(sigma_))
	{
		PyErr_SetString(PyExc_TypeError, "5th argument must be a list");
		return -1;
	}

	/* If there are remaining arguments, keep them in a tuple. */
	if (nargs > 5)
		f_par = PyTuple_GetSlice(args, 5, nargs);

	/* Get the number of parameters and points. */
	nb_par = PyList_Size(a_);
	nb_points = PyList_Size(Yi_);

	/* Create new C lists. */
	a = (double *)malloc(nb_par*sizeof(double));
	Yi = (double *)malloc(nb_points*sizeof(double));
	sigma = (double *)malloc(nb_points*sizeof(double));

	if (!a || !Yi || !sigma)
	{
		free(a);
		free(Yi);
		free(sigma);

		PyErr_NoMemory();
		return -1;
	}

	/* Get the numbers out of the lists. */
	for (i = 0; i < nb_par; i++)
		a[i] = PyFloat_AsDouble(PyList_GetItem(a_, i));
	for (i = 0; i < nb_points; i++)
	{
		Yi[i] = PyFloat_AsDouble(PyList_GetItem(Yi_, i));
		sigma[i] = PyFloat_AsDouble(PyList_GetItem(sigma_, i));
	}

	/* Increment the refcount of the new members. */
	Py_INCREF(f);
	Py_INCREF(df);
	Py_INCREF(a_);

	/* Delete old members (in case __init__ is called twice.). */
	Py_XDECREF(self->f);
	Py_XDECREF(self->df);
	Py_XDECREF(self->a_);
	free(self->a);
	free(self->Yi);
	free(self->sigma);
	Py_XDECREF(self->f_par);

	/* Save the new members. */
	self->f = f;
	self->df = df;
	self->a_ = a_;
	self->a = a;
	self->Yi = Yi;
	self->sigma = sigma;
	self->f_par = f_par;
	self->nb_par = nb_par;
	self->nb_points = nb_points;

	/* Delete the old callback and the C++ Levenberg-Marquardt instance
	 * (ok if it is NULL). */
	delete self->callback;
	delete self->instance;

	self->callback = NULL;
	self->instance = NULL;

	/* Create a new callback and a new instance. */
	try
	{
		self->callback = new Levenberg_Marquardt_Python_callback(self->nb_par, self->nb_points, self->f, self->df, self->a_, self->f_par, &(self->state));
		self->instance = new Levenberg_Marquardt(self->nb_par, self->nb_points, (Levenberg_Marquardt_callback *)self->callback, self->a, self->Yi, self->sigma);
	}
	catch (const std::bad_alloc&)
	{
		delete self->callback;
		delete self->instance;

		self->callback = NULL;
		self->instance = NULL;

		PyErr_NoMemory();
		return -1;
	}

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_traverse                                      */
/*                                                                   */
/*********************************************************************/
static int Levenberg_Marquardt_traverse(Levenberg_Marquardt_object *self, visitproc visit, void *arg)
{
	Py_VISIT(self->f);
	Py_VISIT(self->df);
	Py_VISIT(self->f_par);

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_clear                                         */
/*                                                                   */
/*********************************************************************/
static int Levenberg_Marquardt_clear(Levenberg_Marquardt_object *self)
{
	Py_CLEAR(self->f);
	Py_CLEAR(self->df);
	Py_CLEAR(self->a_);
	Py_CLEAR(self->f_par);

	return 0;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt_dealloc                                       */
/*                                                                   */
/*********************************************************************/
static void Levenberg_Marquardt_dealloc(Levenberg_Marquardt_object *self)
{
	Levenberg_Marquardt_clear(self);

	free(self->a);
	free(self->Yi);
	free(self->sigma);

	delete self->callback;
	delete self->instance;

	self->ob_type->tp_free((PyObject*)self);
}


/*********************************************************************/
/*                                                                   */
/* set_stop_criteria_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * set_stop_criteria_wrapper(Levenberg_Marquardt_object *self, PyObject *args, PyObject *kwds)
{
	double																min_gradient = 0.0;
	double																acceptable_chi_2 = 0.0;
	double																min_chi_2_change = 0.0;

	static const char *kwlist[] = {"min_gradient", "acceptable_chi_2", "min_chi_2_change", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ddd:Levenberg_Marquardt.set_stop_criteria", (char **)kwlist, &min_gradient, &acceptable_chi_2, &min_chi_2_change))
		return NULL;

	Py_BEGIN_ALLOW_THREADS
	self->instance->set_stop_criteria(min_gradient, acceptable_chi_2, min_chi_2_change);
	Py_END_ALLOW_THREADS

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_limits_wrapper                                                */
/*                                                                   */
/*********************************************************************/
static PyObject * set_limits_wrapper(Levenberg_Marquardt_object *self, PyObject *args, PyObject *kwds)
{
	PyObject															*a_min_ = Py_None;
	double																*a_min;
	PyObject															*a_max_ = Py_None;
	double																*a_max;
	Py_ssize_t														par;
	PyObject															*item;

	static const char *kwlist[] = {"a_min", "a_max", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO:Levenberg_Marquardt.set_limits", (char **)kwlist, &a_min_, &a_max_))
		return NULL;

	if (!(a_min_ == Py_None || ((PyList_Check(a_min_) && PyList_Size(a_min_) == self->nb_par))))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be None or a list of nb_par floats");
		return NULL;
	}
	if (!(a_max_ == Py_None || ((PyList_Check(a_max_) && PyList_Size(a_max_) == self->nb_par))))
	{
		PyErr_SetString(PyExc_TypeError, "second argument must be None or a list of nb_par floats");
		return NULL;
	}

	if (a_min_ == Py_None)
	{
		a_min = NULL;
	}
	else
	{
		a_min = (double *)malloc(self->nb_par*sizeof(double));

		if (!a_min)
			return PyErr_NoMemory();

		for (par = 0; par < self->nb_par; par++)
		{
			item = PyList_GetItem(a_min_, par);
			a_min[par] = PyFloat_AsDouble(item);
		}
	}

	if (a_max_ == Py_None)
	{
		a_max = NULL;
	}
	else
	{
		a_max = (double *)malloc(self->nb_par*sizeof(double));

		if (!a_max)
		{
			free(a_min);

			return PyErr_NoMemory();
		}

		for (par = 0; par < self->nb_par; par++)
		{
			item = PyList_GetItem(a_max_, par);
			a_max[par] = PyFloat_AsDouble(item);
		}
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
	{
		free(a_min);
		free(a_max);

		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	self->instance->set_limits(a_min, a_max);
	Py_END_ALLOW_THREADS

	free(a_min);
	free(a_max);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* set_inequalities_wrapper                                          */
/*                                                                   */
/*********************************************************************/
static PyObject * set_inequalities_wrapper(Levenberg_Marquardt_object *self, PyObject *args)
{
	PyObject															*inequalities_ = Py_None;
	char																	*inequalities;
	Py_ssize_t														i;
	PyObject															*item;

	if (!PyArg_ParseTuple(args, "|O:Levenberg_Marquardt.set_inequalities", &inequalities_))
		return NULL;

	if (!(inequalities_ == Py_None || PyList_Check(inequalities_)))
	{
		PyErr_SetString(PyExc_TypeError, "first argument must be None or a list");
		return NULL;
	}

	if (inequalities_ == Py_None)
	{
		inequalities = NULL;
	}
	else
	{
		inequalities = (char *)malloc(self->nb_points*sizeof(char));

		if (!inequalities)
			return PyErr_NoMemory();

		for (i = 0; i < self->nb_points; i++)
		{
			item = PyList_GetItem(inequalities_, i);
			inequalities[i] = PyInt_AsLong(item);
		}
	}

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
	{
		free(inequalities);

		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS
	self->instance->set_inequalities(inequalities);
	Py_END_ALLOW_THREADS

	free(inequalities);

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* prepare_wrapper                                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * prepare_wrapper(Levenberg_Marquardt_object *self)
{
	self->state._save = PyEval_SaveThread();
	try
	{
		self->instance->prepare();
	}
	catch (const Levenberg_Marquardt_Python_callback_exception&)
	{}
	PyEval_RestoreThread(self->state._save);

	if (self->state._type)
	{
		PyErr_Restore(self->state._type, self->state._value, self->state._traceback);
		return NULL;
	}

	Py_RETURN_NONE;
}


/*********************************************************************/
/*                                                                   */
/* iterate_wrapper                                                   */
/*                                                                   */
/*********************************************************************/
static PyObject * iterate_wrapper(Levenberg_Marquardt_object *self)
{
	int																	answer;
	bool																out_of_memory = false;

	self->state._save = PyEval_SaveThread();
	try
	{
		answer = self->instance->iterate();
	}
	catch (const Levenberg_Marquardt_Python_callback_exception&)
	{}
	catch (const std::bad_alloc&)
	{
		out_of_memory = true;
	}
	PyEval_RestoreThread(self->state._save);

	if (self->state._type)
	{
		PyErr_Restore(self->state._type, self->state._value, self->state._traceback);
		return NULL;
	}

	if (out_of_memory)
		return PyErr_NoMemory();

	return Py_BuildValue("i", answer);
}


/*********************************************************************/
/*                                                                   */
/* get_correlation_matrix_wrapper                                    */
/*                                                                   */
/*********************************************************************/
static PyObject * get_correlation_matrix_wrapper(Levenberg_Marquardt_object *self)
{
	PyObject															*C_;
	double																**C;
	PyObject															*column, *element;
	Py_ssize_t														par_1, par_2;
	bool																	out_of_memory = false;

	self->state._save = PyEval_SaveThread();
	try
	{
		C = self->instance->get_correlation_matrix();
	}
	catch (const Levenberg_Marquardt_Python_callback_exception&)
	{}
	catch (const std::bad_alloc&)
	{
		out_of_memory = true;
	}
	PyEval_RestoreThread(self->state._save);

	if (self->state._type)
	{
		PyErr_Restore(self->state._type, self->state._value, self->state._traceback);
		return NULL;
	}

	if (out_of_memory)
		return PyErr_NoMemory();

	/* Create the Python C matrix. */
	C_ = PyList_New(self->nb_par);
	if (!C_)
		return NULL;

	for (par_1 = 0; par_1 < self->nb_par; par_1++)
	{
		column = PyList_New(self->nb_par);

		if (!column)
		{
			Py_DECREF(C_);

			return NULL;
		}

		PyList_SetItem(C_, par_1, column);
	}

	/* Copy the matrix and vectors to the Python structures. */
	for (par_1 = 0; par_1 < self->nb_par; par_1++)
	{
		column = PyList_GetItem(C_, par_1);
		for (par_2 = 0; par_2 < self->nb_par; par_2++)
		{
			element = PyFloat_FromDouble(C[par_1][par_2]);
			PyList_SetItem(column, par_2, element);
		}
	}

	/* Delete the C matrix. */
	for (par_1 = 0; par_1 < self->nb_par; par_1++)
		delete[] C[par_1];
	delete[] C;

	/* Check if one of the conversions failed. */
	if (PyErr_Occurred())
	{
		Py_DECREF(C_);

		return NULL;
	}

	return C_;
}


/*********************************************************************/
/*                                                                   */
/* get_chi_2_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * get_chi_2_wrapper(Levenberg_Marquardt_object *self)
{
	double																answer;

	Py_BEGIN_ALLOW_THREADS
	answer = self->instance->get_chi_2();
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", answer);
}


/*********************************************************************/
/*                                                                   */
/* get_norm_gradient_wrapper                                         */
/*                                                                   */
/*********************************************************************/
static PyObject * get_norm_gradient_wrapper(Levenberg_Marquardt_object *self)
{
	double																answer;

	Py_BEGIN_ALLOW_THREADS
	answer = self->instance->get_norm_gradient();
	Py_END_ALLOW_THREADS

	return Py_BuildValue("d", answer);
}


/*********************************************************************/
/*                                                                   */
/* get_stats_wrapper                                                 */
/*                                                                   */
/*********************************************************************/
static PyObject * get_stats_wrapper(Levenberg_Marquardt_object *self)
{
	long																	nb_f_eval, nb_df_eval;

	Py_BEGIN_ALLOW_THREADS
	self->instance->get_stats(&nb_f_eval, &nb_df_eval);
	Py_END_ALLOW_THREADS

	return Py_BuildValue("ll", nb_f_eval, nb_df_eval);
}


static PyMethodDef Levenberg_Marquardt_type_methods[] =
{
	{"set_stop_criteria",							(PyCFunction)set_stop_criteria_wrapper,			METH_VARARGS|METH_KEYWORDS},
	{"set_limits",										(PyCFunction)set_limits_wrapper,						METH_VARARGS|METH_KEYWORDS},
	{"set_inequalities",							(PyCFunction)set_inequalities_wrapper,			METH_VARARGS},
	{"prepare",												(PyCFunction)prepare_wrapper,								METH_NOARGS},
	{"iterate",												(PyCFunction)iterate_wrapper,								METH_NOARGS},
	{"get_correlation_matrix",				(PyCFunction)get_correlation_matrix_wrapper,METH_NOARGS},
	{"get_chi_2",											(PyCFunction)get_chi_2_wrapper,							METH_NOARGS},
	{"get_norm_gradient",							(PyCFunction)get_norm_gradient_wrapper,			METH_NOARGS},
	{"get_stats",											(PyCFunction)get_stats_wrapper,							METH_NOARGS},
	{NULL} /* Sentinel */
};


static PyTypeObject Levenberg_Marquardt_type = {
	PyObject_HEAD_INIT(NULL)
	0,																					/* ob_size */
	"Levenberg_Marquardt.Levenberg_Marquardt",	/* tp_name */
	sizeof(Levenberg_Marquardt_object),					/* tp_basicsize */
	0,																					/* tp_itemsize */
	(destructor)Levenberg_Marquardt_dealloc,		/* tp_dealloc */
	0,																					/* tp_print */
	0,																					/* tp_getattr */
	0,																					/* tp_setattr */
	0,																					/* tp_compare */
	0,																					/* tp_repr */
	0,																					/* tp_as_number */
	0,																					/* tp_as_sequence */
	0,																					/* tp_as_mapping */
	0,																					/* tp_hash */
	0,																					/* tp_call */
	0,																					/* tp_str */
	0,																					/* tp_getattro */
	0,																					/* tp_setattro */
	0,																					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,			/* tp_flags */
	"Levenberg-Marquardt class",								/* tp_doc */
	(traverseproc)Levenberg_Marquardt_traverse,	/* tp_traverse */
	(inquiry)Levenberg_Marquardt_clear,					/* tp_clear */
	0,																					/* tp_richcompare */
	0,																					/* tp_weaklistoffset */
	0,																					/* tp_iter */
	0,																					/* tp_iternext */
	Levenberg_Marquardt_type_methods,						/* tp_methods */
	0,																					/* tp_members */
	0,																					/* tp_getset */
	0,																					/* tp_base */
	0,																					/* tp_dict */
	0,																					/* tp_descr_get */
	0,																					/* tp_descr_set */
	0,																					/* tp_dictoffset */
	(initproc)Levenberg_Marquardt_init,					/* tp_init */
	0,																					/* tp_alloc */
	Levenberg_Marquardt_new,										/* tp_new */
};


static PyMethodDef Levenberg_Marquardt_methods[] =
{
	{NULL} /* Sentinel */
};


/*********************************************************************/
/*                                                                   */
/* init_Levenberg_Marquardt                                          */
/*                                                                   */
/*                                                                   */
/* Init this module so that it can be called from Python.            */
/*                                                                   */
/*********************************************************************/
PyObject * init_Levenberg_Marquardt()
{
	PyObject															*module;

	if (PyType_Ready(&Levenberg_Marquardt_type) < 0) return NULL;

	module = Py_InitModule("moremath.Levenberg_Marquardt", Levenberg_Marquardt_methods);

	if (!module) return NULL;

	/* Add the Levenberg-Marquardt type to the module. */
	PyModule_AddObject(module, "Levenberg_Marquardt", (PyObject *)&Levenberg_Marquardt_type);

	/* Add the return values of Levenberg-Marquardt's iterate method to
	 * the module. */
	PyModule_AddIntConstant(module, "IMPROVING", IMPROVING);
	PyModule_AddIntConstant(module, "MINIMUM_FOUND", MINIMUM_FOUND);
	PyModule_AddIntConstant(module, "CHI_2_IS_OK", CHI_2_IS_OK);
	PyModule_AddIntConstant(module, "CHI_2_CHANGE_TOO_SMALL", CHI_2_CHANGE_TOO_SMALL);
	PyModule_AddIntConstant(module, "DELTA_IS_TOO_SMALL", DELTA_IS_TOO_SMALL);
	PyModule_AddIntConstant(module, "ALL_PARAMETERS_ARE_STUCK", ALL_PARAMETERS_ARE_STUCK);
	PyModule_AddIntConstant(module, "SINGULAR_MATRIX", SINGULAR_MATRIX);
	PyModule_AddIntConstant(module, "SMALLER", SMALLER);
	PyModule_AddIntConstant(module, "EQUAL", EQUAL);
	PyModule_AddIntConstant(module, "LARGER", LARGER);
	PyModule_AddObject(module, "INFINITY", PyFloat_FromDouble(INFINITY));

	if (PyErr_Occurred()) return NULL;

	return module;
}


#ifdef __cplusplus
}
#endif
