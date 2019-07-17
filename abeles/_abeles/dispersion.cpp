/*
 *
 *  dispersion.cpp
 *
 *
 *  Functions to manage various dispersion models.
 *
 *  Copyright (c) 2002-2008,2012-2014 Stephane Larouche.
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


#include <cstdlib>
#include <algorithm>
#include <cmath>

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_constant                                                      */
/*                                                                   */
/* Create a new constant dispersion structure                        */
/*                                                                   */
/* This function takes no argument and returns a constant dispersion */
/* structure.                                                        */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
constant_type * new_constant()
{
	constant_type										*material;

	material = (constant_type *)malloc(sizeof(constant_type));
	if (!material) return NULL;

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_constant                                                      */
/*                                                                   */
/* Delete a constant dispersion structure                            */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_constant(constant_type *material)
{
	if (!material) return;

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* set_constant                                                      */
/*                                                                   */
/* Set the value of the index of refraction for constant dispersion  */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the constant dispersion structure;            */
/*   N                 the index of refraction.                      */
/*                                                                   */
/*********************************************************************/
void set_constant(constant_type *material, const std::complex<double> N)
{
	material->N = N;
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant                                                    */
/*                                                                   */
/* Set the index of refraction from a constant dispersion            */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the constant dispersion structure;            */
/*   N                 the index of refraction structure that must   */
/*                     be set.                                       */
/* It always returns ABELES_SUCCESS.                                 */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_constant(const constant_type *material, const N_type *N)
{
	long														i;

	for (i = 0; i < N->wvls->length; i++)
	{
		N->N[i] = material->N;
	}

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* new_table                                                         */
/*                                                                   */
/* Create a new table dispersion structure                           */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length            the number of points in the table;            */
/* and returns a table dispersion structure.                         */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
table_type * new_table(const long length)
{
	table_type											*material;

	material = (table_type *)malloc(sizeof(table_type));

	if (!material) return NULL;

	material->length = length;
	material->wvls = (double *)malloc(material->length*sizeof(double));
	material->n = (double *)malloc(material->length*sizeof(double));
	material->k = (double *)malloc(material->length*sizeof(double));
	material->_n_PCHIP = NULL;
	material->_k_PCHIP = NULL;

	if (!material->wvls || !material->n || !material->k)
	{
		del_table(material);
		return NULL;
	}

	try
	{
		material->_n_PCHIP = new PCHIP(material->length, material->wvls, material->n, true, true);
		material->_k_PCHIP = new PCHIP(material->length, material->wvls, material->k, true, true);
	}
	catch (const std::bad_alloc&)
	{
		del_table(material);
		return NULL;
	}

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_table                                                         */
/*                                                                   */
/* Delete a table dispersion structure                               */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_table(table_type *material)
{
	if (!material) return;

	delete material->_n_PCHIP;
	delete material->_k_PCHIP;
	free(material->wvls);
	free(material->n);
	free(material->k);

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* set_table                                                         */
/*                                                                   */
/* Set one value of the index of refraction for table dispersion     */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the table dispersion structure;               */
/*   pos               the position in the table;                    */
/*   wlv               the wavelength;                               */
/*   N                 the index of refraction.                      */
/*                                                                   */
/*********************************************************************/
void set_table(const table_type *material, const long pos, const double wvl, const std::complex<double> N)
{
	material->wvls[pos] = wvl;
	material->n[pos] = real(N);
	material->k[pos] = imag(N);
}


/*********************************************************************/
/*                                                                   */
/* prepare_table                                                     */
/*                                                                   */
/* This function is deprecated                                       */
/*                                                                   */
/*********************************************************************/
void prepare_table(const table_type *material)
{
}


/*********************************************************************/
/*                                                                   */
/* get_table_index                                                   */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a table   */
/* dispersion                                                        */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion structure;               */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
double get_table_index(const table_type *material, const double wvl)
{
	double													n;

	/* Calculate real part of the index using PCHIP. */
	material->_n_PCHIP->evaluate(1, &wvl, &n);

	return n;
}


/*********************************************************************/
/*                                                                   */
/* set_N_table                                                       */
/*                                                                   */
/* Set the index of refraction from a table dispersion               */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion structure;               */
/*   N                 the index of refraction structure that must   */
/*                     be set.                                       */
/* It returns a abeles_error_type, either:                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_table(const table_type *material, const N_type *N)
{
	long														i_wvl, i_wvl_material;
	long														*positions;
	double													*n, *k;

	positions = (long *)malloc(N->wvls->length*sizeof(long));
	n = (double *)malloc(N->wvls->length*sizeof(double));
	k = (double *)malloc(N->wvls->length*sizeof(double));

	if (!positions || !n || !k)
	{
		free(positions);
		free(n);
		free(k);

		return ABELES_OUT_OF_MEMORY;
	}

	/* Find the positions of the wavelengths of n in the intervals
	 * of basis. The search method supposes that wavelengths are in
	 * increasing order. It simply goes through all of the table which
	 * is only effective if the number of interpolated wavelengths
	 * is similar or higher than the number of wavelengths in the
	 * table and if they are uniformly distributed. This is
	 * usually the case, so I don't bother creating a more complex
	 * algorithm. */
	i_wvl = 0;
	for (i_wvl_material = 0; i_wvl_material < material->length-1; i_wvl_material++)
	{
		for(; i_wvl < N->wvls->length && N->wvls->wvls[i_wvl] < material->wvls[i_wvl_material+1]; i_wvl++)
		{
			positions[i_wvl] = i_wvl_material;
		}
	}
	/* A special case must be done for the data extrapolated at the
	 * end of the basis. */
	for(; i_wvl < N->wvls->length; i_wvl++)
	{
		positions[i_wvl] = material->length-2;
	}

	/* Evaluate the PCHIPs. */
	material->_n_PCHIP->evaluate(N->wvls->length, N->wvls->wvls, n, positions);
	material->_k_PCHIP->evaluate(N->wvls->length, N->wvls->wvls, k, positions);

	/* Convert it back to complex numbers and put it in N. Eliminate
	 * positive values of k. */
	for (i_wvl = 0; i_wvl < N->wvls->length; i_wvl++)
		N->N[i_wvl] = std::complex<double>(n[i_wvl], std::min(k[i_wvl], 0.0));

	free(positions);
	free(n);
	free(k);

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* new_Cauchy                                                        */
/*                                                                   */
/* Create a new Cauchy dispersion structure                          */
/*                                                                   */
/* This function takes no argument and returns a Cauchy dispersion   */
/* structure.                                                        */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
Cauchy_type * new_Cauchy()
{
	Cauchy_type											*material;

	material = (Cauchy_type *)malloc(sizeof(Cauchy_type));

	if (!material) return NULL;

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_Cauchy                                                        */
/*                                                                   */
/* Delete a Cauchy dispersion structure                              */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_Cauchy(Cauchy_type *material)
{
	if (!material) return;

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* set_Cauchy                                                        */
/*                                                                   */
/* Set the dispersion formula for Cauchy dispersion                  */
/*                                                                   */
/* This function takes 7 arguments:                                  */
/*   material            the Cauchy dispersion structure;            */
/*   A, B, C             the parameters of the Cauchy dispersion     */
/*                       model;                                      */
/*   Ak, exponent, edge  the parameters of the Urbach absorption     */
/*                       tail.                                       */
/*                                                                   */
/*********************************************************************/
void set_Cauchy(Cauchy_type *material, const double A, const double B, const double C, const double Ak, const double exponent, const double edge)
{
	material->A = A;
	material->B = B;
	material->C = C;
	material->Ak = Ak;
	material->exponent = exponent;
	material->edge = edge;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy                                                      */
/*                                                                   */
/* Set the index of refraction from a Cauchy dispersion              */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Cauchy dispersion structure;              */
/*   N                 the index of refraction structure that must   */
/*                     be set.                                       */
/* It always returns ABELES_SUCCESS.                                 */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Cauchy(const Cauchy_type *material, const N_type *N)
{
	long														i;
	double													wvl_micron, wvl_micron_square;

	for (i = 0; i < N->wvls->length; i++)
	{
		wvl_micron = 0.001*N->wvls->wvls[i];
		wvl_micron_square = wvl_micron*wvl_micron;
		N->N[i] = std::complex<double>(material->A + material->B/wvl_micron_square + material->C/(wvl_micron_square*wvl_micron_square),\
		                               -material->Ak*exp(12400.0*material->exponent*((1.0/(10000.0*wvl_micron))-(1.0/material->edge))));
	}

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* new_Sellmeier                                                     */
/*                                                                   */
/* Create a new Sellmeier dispersion structure                       */
/*                                                                   */
/* This function takes no argument and returns a Sellmeier           */
/* dispersion structure.                                             */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
Sellmeier_type * new_Sellmeier()
{
	Sellmeier_type									*material;

	material = (Sellmeier_type *)malloc(sizeof(Sellmeier_type));

	if (!material) return NULL;

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_Sellmeier                                                     */
/*                                                                   */
/* Delete a Sellmeier dispersion structure                           */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_Sellmeier(Sellmeier_type *material)
{
	if (!material) return;

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* set_Sellmeier                                                     */
/*                                                                   */
/* Set the dispersion formula for Sellmeier dispersion               */
/*                                                                   */
/* This function takes 10 arguments:                                  */
/*   material               the Sellmeier dispersion structure;      */
/*   B1, C1, B2, C2, B3, C3 the parameters of the Sellmeier          */
/*                          dispersion model;                        */
/*   Ak, exponent, edge     the parameters of the Urbach absorption  */
/*                          tail.                                    */
/*                                                                   */
/*********************************************************************/
void set_Sellmeier(Sellmeier_type *material, const double B1, const double C1, const double B2, const double C2, const double B3, const double C3, const double Ak, const double exponent, const double edge)
{
	material->B1 = B1;
	material->C1 = C1;
	material->B2 = B2;
	material->C2 = C2;
	material->B3 = B3;
	material->C3 = C3;
	material->Ak = Ak;
	material->exponent = exponent;
	material->edge = edge;
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier                                                   */
/*                                                                   */
/* Set the index of refraction from a Sellmeier dispersion           */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Sellmeier dispersion structure;           */
/*   N                 the index of refraction structure that must   */
/*                     be set.                                       */
/* It always returns ABELES_SUCCESS.                                 */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Sellmeier(const Sellmeier_type *material, const N_type *N)
{
	long														i;
	double													wvl_micron, wvl_micron_square;
	double													n_square;

	for (i = 0; i < N->wvls->length; i++)
	{
		wvl_micron = 0.001*N->wvls->wvls[i];
		wvl_micron_square = wvl_micron*wvl_micron;
		n_square = 1.0+material->B1*wvl_micron_square/(wvl_micron_square-material->C1)\
		              +material->B2*wvl_micron_square/(wvl_micron_square-material->C2)\
		              +material->B3*wvl_micron_square/(wvl_micron_square-material->C3);
		N->N[i] = std::complex<double>((n_square > 0.0 && std::isfinite(n_square)) ? sqrt(n_square) : 0.0,\
		                               -material->Ak*exp(12400.0*material->exponent*((1.0/(10000.0*wvl_micron))-(1.0/material->edge))));
	}

	return ABELES_SUCCESS;
}


#ifdef __cplusplus
}
#endif


