/*
 *
 *  _abeles.cpp
 *
 *
 *  This is the central file of the _abeles module. It initializes the
 *  module and adds all the objects to it.
 *
 *  Copyright (c) 2002-2009,2012 Stephane Larouche.
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


static PyMethodDef abeles_methods[] =
{
	{NULL} /* Sentinel */
};


/*********************************************************************/
/*                                                                   */
/* init_abeles                                                       */
/*                                                                   */
/*                                                                   */
/* Initialize this module so that it can be called from Python.      */
/*                                                                   */
/*********************************************************************/
PyMODINIT_FUNC init_abeles()
{
	PyObject*					module;

	/* Make sure that all types are ready. */
	if (PyType_Ready(&wvls_wrapper_type) < 0) return;
	if (PyType_Ready(&N_wrapper_type) < 0) return;
	if (PyType_Ready(&N_mixture_wrapper_type) < 0) return;
	if (PyType_Ready(&constant_wrapper_type) < 0) return;
	if (PyType_Ready(&table_wrapper_type) < 0) return;
	if (PyType_Ready(&Cauchy_wrapper_type) < 0) return;
	if (PyType_Ready(&Sellmeier_wrapper_type) < 0) return;
	if (PyType_Ready(&constant_mixture_wrapper_type) < 0) return;
	if (PyType_Ready(&table_mixture_wrapper_type) < 0) return;
	if (PyType_Ready(&Cauchy_mixture_wrapper_type) < 0) return;
	if (PyType_Ready(&Sellmeier_mixture_wrapper_type) < 0) return;
	if (PyType_Ready(&sin2_wrapper_type) < 0) return;
	if (PyType_Ready(&matrices_wrapper_type) < 0) return;
	if (PyType_Ready(&r_and_t_wrapper_type) < 0) return;
	if (PyType_Ready(&spectrum_wrapper_type) < 0) return;
	if (PyType_Ready(&R_wrapper_type) < 0) return;
	if (PyType_Ready(&T_wrapper_type) < 0) return;
	if (PyType_Ready(&A_wrapper_type) < 0) return;
	if (PyType_Ready(&phase_wrapper_type) < 0) return;
	if (PyType_Ready(&GD_wrapper_type) < 0) return;
	if (PyType_Ready(&GDD_wrapper_type) < 0) return;
	if (PyType_Ready(&Psi_and_Delta_wrapper_type) < 0) return;
	if (PyType_Ready(&admittance_wrapper_type) < 0) return;
	if (PyType_Ready(&circle_wrapper_type) < 0) return;
	if (PyType_Ready(&electric_field_wrapper_type) < 0) return;
	if (PyType_Ready(&monitoring_matrices_wrapper_type) < 0) return;
	if (PyType_Ready(&pre_and_post_matrices_wrapper_type) < 0) return;
	if (PyType_Ready(&dM_wrapper_type) < 0) return;
	if (PyType_Ready(&psi_matrices_wrapper_type) < 0) return;
	if (PyType_Ready(&dr_and_dt_wrapper_type) < 0) return;
	if (PyType_Ready(&dR_wrapper_type) < 0) return;
	if (PyType_Ready(&dT_wrapper_type) < 0) return;
	if (PyType_Ready(&dA_wrapper_type) < 0) return;
	if (PyType_Ready(&dphase_wrapper_type) < 0) return;
	if (PyType_Ready(&dGD_wrapper_type) < 0) return;
	if (PyType_Ready(&dGDD_wrapper_type) < 0) return;
	if (PyType_Ready(&needle_matrices_wrapper_type) < 0) return;


	module = Py_InitModule("_abeles", abeles_methods);

	if (!module) return;

	/* Define a few constants. */
	PyModule_AddObject(module, "S", PyFloat_FromDouble(S));
	PyModule_AddObject(module, "P", PyFloat_FromDouble(P));

	/* Add the various objects to the module. */

	Py_INCREF(&wvls_wrapper_type);
	PyModule_AddObject(module, "wvls", (PyObject *)&wvls_wrapper_type);

	Py_INCREF(&N_wrapper_type);
	PyModule_AddObject(module, "N", (PyObject *)&N_wrapper_type);

	Py_INCREF(&N_mixture_wrapper_type);
	PyModule_AddObject(module, "N_mixture", (PyObject *)&N_mixture_wrapper_type);

	Py_INCREF(&constant_wrapper_type);
	PyModule_AddObject(module, "constant", (PyObject *)&constant_wrapper_type);

	Py_INCREF(&table_wrapper_type);
	PyModule_AddObject(module, "table", (PyObject *)&table_wrapper_type);

	Py_INCREF(&Cauchy_wrapper_type);
	PyModule_AddObject(module, "Cauchy", (PyObject *)&Cauchy_wrapper_type);

	Py_INCREF(&Sellmeier_wrapper_type);
	PyModule_AddObject(module, "Sellmeier", (PyObject *)&Sellmeier_wrapper_type);

	Py_INCREF(&constant_mixture_wrapper_type);
	PyModule_AddObject(module, "constant_mixture", (PyObject *)&constant_mixture_wrapper_type);

	Py_INCREF(&table_mixture_wrapper_type);
	PyModule_AddObject(module, "table_mixture", (PyObject *)&table_mixture_wrapper_type);

	Py_INCREF(&Cauchy_mixture_wrapper_type);
	PyModule_AddObject(module, "Cauchy_mixture", (PyObject *)&Cauchy_mixture_wrapper_type);

	Py_INCREF(&Sellmeier_mixture_wrapper_type);
	PyModule_AddObject(module, "Sellmeier_mixture", (PyObject *)&Sellmeier_mixture_wrapper_type);

	Py_INCREF(&sin2_wrapper_type);
	PyModule_AddObject(module, "sin2", (PyObject *)&sin2_wrapper_type);

	Py_INCREF(&matrices_wrapper_type);
	PyModule_AddObject(module, "matrices", (PyObject *)&matrices_wrapper_type);

	Py_INCREF(&r_and_t_wrapper_type);
	PyModule_AddObject(module, "r_and_t", (PyObject *)&r_and_t_wrapper_type);

	Py_INCREF(&spectrum_wrapper_type);
	PyModule_AddObject(module, "spectrum", (PyObject *)&spectrum_wrapper_type);

	Py_INCREF(&R_wrapper_type);
	PyModule_AddObject(module, "R", (PyObject *)&R_wrapper_type);

	Py_INCREF(&T_wrapper_type);
	PyModule_AddObject(module, "T", (PyObject *)&T_wrapper_type);

	Py_INCREF(&A_wrapper_type);
	PyModule_AddObject(module, "A", (PyObject *)&A_wrapper_type);

	Py_INCREF(&phase_wrapper_type);
	PyModule_AddObject(module, "phase", (PyObject *)&phase_wrapper_type);

	Py_INCREF(&GD_wrapper_type);
	PyModule_AddObject(module, "GD", (PyObject *)&GD_wrapper_type);

	Py_INCREF(&GDD_wrapper_type);
	PyModule_AddObject(module, "GDD", (PyObject *)&GDD_wrapper_type);

	Py_INCREF(&Psi_and_Delta_wrapper_type);
	PyModule_AddObject(module, "Psi_and_Delta", (PyObject *)&Psi_and_Delta_wrapper_type);

	Py_INCREF(&admittance_wrapper_type);
	PyModule_AddObject(module, "admittance", (PyObject *)&admittance_wrapper_type);

	Py_INCREF(&circle_wrapper_type);
	PyModule_AddObject(module, "circle", (PyObject *)&circle_wrapper_type);

	Py_INCREF(&electric_field_wrapper_type);
	PyModule_AddObject(module, "electric_field", (PyObject *)&electric_field_wrapper_type);

	Py_INCREF(&monitoring_matrices_wrapper_type);
	PyModule_AddObject(module, "monitoring_matrices", (PyObject *)&monitoring_matrices_wrapper_type);

	Py_INCREF(&pre_and_post_matrices_wrapper_type);
	PyModule_AddObject(module, "pre_and_post_matrices", (PyObject *)&pre_and_post_matrices_wrapper_type);

	Py_INCREF(&dM_wrapper_type);
	PyModule_AddObject(module, "dM", (PyObject *)&dM_wrapper_type);

	Py_INCREF(&psi_matrices_wrapper_type);
	PyModule_AddObject(module, "psi_matrices", (PyObject *)&psi_matrices_wrapper_type);

	Py_INCREF(&dr_and_dt_wrapper_type);
	PyModule_AddObject(module, "dr_and_dt", (PyObject *)&dr_and_dt_wrapper_type);

	Py_INCREF(&dR_wrapper_type);
	PyModule_AddObject(module, "dR", (PyObject *)&dR_wrapper_type);

	Py_INCREF(&dT_wrapper_type);
	PyModule_AddObject(module, "dT", (PyObject *)&dT_wrapper_type);

	Py_INCREF(&dA_wrapper_type);
	PyModule_AddObject(module, "dA", (PyObject *)&dA_wrapper_type);

	Py_INCREF(&dphase_wrapper_type);
	PyModule_AddObject(module, "dphase", (PyObject *)&dphase_wrapper_type);

	Py_INCREF(&dGD_wrapper_type);
	PyModule_AddObject(module, "dGD", (PyObject *)&dGD_wrapper_type);

	Py_INCREF(&dGDD_wrapper_type);
	PyModule_AddObject(module, "dGDD", (PyObject *)&dGDD_wrapper_type);

	Py_INCREF(&needle_matrices_wrapper_type);
	PyModule_AddObject(module, "needle_matrices", (PyObject *)&needle_matrices_wrapper_type);
}


#ifdef __cplusplus
}
#endif
