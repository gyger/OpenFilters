/*
 *
 *  _moremath.cpp
 *
 *
 *  Implements some mathematical tools for the Filters software.
 *
 *  This package is written to be compiled as a DLL compatible with
 *  normal software as well as Python.
 *
 *  Copyright (c) 2006,2013 Stephane Larouche.
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

#include "_moremath_wrapper.h"


#ifdef __cplusplus
extern "C" {
#endif


static PyMethodDef moremath_methods[] =
{
	{NULL} /* Sentinel */
};


/*********************************************************************/
/*                                                                   */
/* init_moremath                                                     */
/*                                                                   */
/*                                                                   */
/* Init this package so that it can be called from Python.           */
/*                                                                   */
/*********************************************************************/
PyMODINIT_FUNC init_moremath()
{
	PyObject					*package;
	PyObject					*Levenberg_Marquardt_module, *QR_module, *roots_module;

	/* Init the package. */
	package = Py_InitModule("_moremath", moremath_methods);

	if (!package) return;

	/* Init all the modules. */
	Levenberg_Marquardt_module = init_Levenberg_Marquardt();
	QR_module = init_QR();
	roots_module = init_roots();

	if (PyErr_Occurred()) return;

	/* Add the modules to the package. */
	PyModule_AddObject(package, "Levenberg_Marquardt", Levenberg_Marquardt_module);
	PyModule_AddObject(package, "QR", QR_module);
	PyModule_AddObject(package, "roots", roots_module);
}


#ifdef __cplusplus
}
#endif
