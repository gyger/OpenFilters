/*
 *
 *  _abeles_wrapper.h
 *
 *
 *  Header files for Python wrapper functions of the abeles DLL.
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


#ifndef __ABELES_WRAPPER
#define __ABELES_WRAPPER


/* Make sure that Python.h is loaded. */
#include <Python.h>

/* Make sure that _abeles.h is loaded. */
#include "_abeles.h"


/* Define template inline function to replace NANs and INFs. */
template <typename T, typename U>
inline void REPLACE_NAN_OR_INF(T &x, const U default_value) {if (x-x != (T)0.0) x = (T)default_value;}


#ifdef __cplusplus
extern "C" {
#endif


/* The various Python objects defined in abeles. */

typedef struct {
	PyObject_HEAD
	wvls_type															*wvls;
} wvls_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	N_type																*N;
	PyObject															*parent;
} N_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	PyObject															*dispersion;
	N_mixture_type												*N_mixture;
	N_wrapper_object											*N_wrapper;
	N_wrapper_object											*dN_wrapper;
	N_wrapper_object											**N_graded_wrappers;
} N_mixture_wrapper_object;

typedef struct {
	PyObject_HEAD
	constant_type													*dispersion;
} constant_wrapper_object;

typedef struct {
	PyObject_HEAD
	Cauchy_type														*dispersion;
} Cauchy_wrapper_object;

typedef struct {
	PyObject_HEAD
	Sellmeier_type												*dispersion;
} Sellmeier_wrapper_object;

typedef struct {
	PyObject_HEAD
	table_type														*dispersion;
} table_wrapper_object;

typedef struct {
	PyObject_HEAD
	constant_mixture_type									*dispersion;
} constant_mixture_wrapper_object;

typedef struct {
	PyObject_HEAD
	Cauchy_mixture_type										*dispersion;
} Cauchy_mixture_wrapper_object;

typedef struct {
	PyObject_HEAD
	Sellmeier_mixture_type								*dispersion;
} Sellmeier_mixture_wrapper_object;

typedef struct {
	PyObject_HEAD
	table_mixture_type										*dispersion;
} table_mixture_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	sin2_type															*sin2;
} sin2_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	matrices_type													*matrices;
	PyObject															*parent;
} matrices_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	r_and_t_type													*r_and_t;
} r_and_t_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	spectrum_type													*spectrum;
} spectrum_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	Psi_and_Delta_type										*Psi_and_Delta;
} Psi_and_Delta_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	admittance_type												*admittance;
} admittance_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	circle_type														*circle;
} circle_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	monitoring_matrices_type							*matrices;
	matrices_wrapper_object								**wrappers;
} monitoring_matrices_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	pre_and_post_matrices_type						*pre_and_post_matrices;
	matrices_wrapper_object								*M_wrapper;
	matrices_wrapper_object								**Mi_wrappers;
} pre_and_post_matrices_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	psi_matrices_type											*psi_matrices;
} psi_matrices_wrapper_object;

typedef struct {
	PyObject_HEAD
	wvls_wrapper_object										*wvls;
	needle_matrices_type									*needle_matrices;
	matrices_wrapper_object								**needle_matrices_wrappers;
} needle_matrices_wrapper_object;


/* The types related with those objects. */

extern PyTypeObject wvls_wrapper_type;
extern PyTypeObject N_wrapper_type;
extern PyTypeObject N_mixture_wrapper_type;
extern PyTypeObject constant_wrapper_type;
extern PyTypeObject table_wrapper_type;
extern PyTypeObject Cauchy_wrapper_type;
extern PyTypeObject Sellmeier_wrapper_type;
extern PyTypeObject constant_mixture_wrapper_type;
extern PyTypeObject table_mixture_wrapper_type;
extern PyTypeObject Cauchy_mixture_wrapper_type;
extern PyTypeObject Sellmeier_mixture_wrapper_type;
extern PyTypeObject sin2_wrapper_type;
extern PyTypeObject matrices_wrapper_type;
extern PyTypeObject r_and_t_wrapper_type;
extern PyTypeObject spectrum_wrapper_type;
extern PyTypeObject R_wrapper_type;
extern PyTypeObject T_wrapper_type;
extern PyTypeObject A_wrapper_type;
extern PyTypeObject phase_wrapper_type;
extern PyTypeObject Psi_and_Delta_wrapper_type;
extern PyTypeObject GD_wrapper_type;
extern PyTypeObject GDD_wrapper_type;
extern PyTypeObject admittance_wrapper_type;
extern PyTypeObject circle_wrapper_type;
extern PyTypeObject electric_field_wrapper_type;
extern PyTypeObject monitoring_matrices_wrapper_type;
extern PyTypeObject pre_and_post_matrices_wrapper_type;
extern PyTypeObject dM_wrapper_type;
extern PyTypeObject psi_matrices_wrapper_type;
extern PyTypeObject dr_and_dt_wrapper_type;
extern PyTypeObject dR_wrapper_type;
extern PyTypeObject dT_wrapper_type;
extern PyTypeObject dA_wrapper_type;
extern PyTypeObject dphase_wrapper_type;
extern PyTypeObject dGD_wrapper_type;
extern PyTypeObject dGDD_wrapper_type;
extern PyTypeObject needle_matrices_wrapper_type;


/* Macros the check the type of objects. */

#define wvls_wrapper_Check(op) PyObject_TypeCheck(op, &wvls_wrapper_type)
#define N_wrapper_Check(op) PyObject_TypeCheck(op, &N_wrapper_type)
#define N_mixture_wrapper_Check(op) PyObject_TypeCheck(op, &N_mixture_wrapper_type)
#define constant_wrapper_Check(op) PyObject_TypeCheck(op, &constant_wrapper_type)
#define table_wrapper_Check(op) PyObject_TypeCheck(op, &table_wrapper_type)
#define Cauchy_wrapper_Check(op) PyObject_TypeCheck(op, &Cauchy_wrapper_type)
#define Sellmeier_wrapper_Check(op) PyObject_TypeCheck(op, &Sellmeier_wrapper_type)
#define constant_mixture_wrapper_Check(op) PyObject_TypeCheck(op, &constant_mixture_wrapper_type)
#define table_mixture_wrapper_Check(op) PyObject_TypeCheck(op, &table_mixture_wrapper_type)
#define Cauchy_mixture_wrapper_Check(op) PyObject_TypeCheck(op, &Cauchy_mixture_wrapper_type)
#define Sellmeier_mixture_wrapper_Check(op) PyObject_TypeCheck(op, &Sellmeier_mixture_wrapper_type)
#define sin2_wrapper_Check(op) PyObject_TypeCheck(op, &sin2_wrapper_type)
#define matrices_wrapper_Check(op) PyObject_TypeCheck(op, &matrices_wrapper_type)
#define r_and_t_wrapper_Check(op) PyObject_TypeCheck(op, &r_and_t_wrapper_type)
#define spectrum_wrapper_Check(op) PyObject_TypeCheck(op, &spectrum_wrapper_type)
#define R_wrapper_Check(op) PyObject_TypeCheck(op, &R_wrapper_type)
#define T_wrapper_Check(op) PyObject_TypeCheck(op, &T_wrapper_type)
#define A_wrapper_Check(op) PyObject_TypeCheck(op, &A_wrapper_type)
#define phase_wrapper_Check(op) PyObject_TypeCheck(op, &phase_wrapper_type)
#define Psi_and_Delta_wrapper_Check(op) PyObject_TypeCheck(op, &Psi_and_Delta_wrapper_type)
#define GD_wrapper_Check(op) PyObject_TypeCheck(op, &GD_wrapper_type)
#define GDD_wrapper_Check(op) PyObject_TypeCheck(op, &GD_wrapper_type)
#define admittance_wrapper_Check(op) PyObject_TypeCheck(op, &admittance_wrapper_type)
#define circle_wrapper_Check(op) PyObject_TypeCheck(op, &circle_wrapper_type)
#define electric_field_wrapper_Check(op) PyObject_TypeCheck(op, &electric_field_wrapper_type)
#define monitoring_matrices_wrapper_Check(op) PyObject_TypeCheck(op, &monitoring_matrices_wrapper_type)
#define pre_and_post_matrices_wrapper_Check(op) PyObject_TypeCheck(op, &pre_and_post_matrices_wrapper_type)
#define dM_wrapper_Check(op) PyObject_TypeCheck(op, &dM_wrapper_type)
#define psi_matrices_wrapper_Check(op) PyObject_TypeCheck(op, &psi_matrices_wrapper_type)
#define dr_and_dt_wrapper_Check(op) PyObject_TypeCheck(op, &dr_and_dt_wrapper_type)
#define dR_wrapper_Check(op) PyObject_TypeCheck(op, &dR_wrapper_type)
#define dT_wrapper_Check(op) PyObject_TypeCheck(op, &dT_wrapper_type)
#define dA_wrapper_Check(op) PyObject_TypeCheck(op, &dA_wrapper_type)
#define dphase_wrapper_Check(op) PyObject_TypeCheck(op, &dphase_wrapper_type)
#define dGD_wrapper_Check(op) PyObject_TypeCheck(op, &dGD_wrapper_type)
#define dGDD_wrapper_Check(op) PyObject_TypeCheck(op, &dGDD_wrapper_type)
#define needle_matrices_wrapper_Check(op) PyObject_TypeCheck(op, &needle_matrices_wrapper_type)


#ifdef __cplusplus
}
#endif

#endif /* #ifndef __ABELES_WRAPPER */
