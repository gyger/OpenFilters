/*
 *
 *  dispersion_mixtures.cpp
 *
 *
 *  Functions to manage the optical properties of material mixtures.
 *
 *  Material mixtures, or any material with adjustable index of
 *  refraction, are represented by a structure accounting for its real
 *  dispersion (as opposed to an effective medium approximation). To do
 *  so, the dispersion curves of multiple mixtures must be given, and
 *  the index of refraction of intermediate mixtures is calculated
 *  using piecewise cubic Hermite interpolant polynomials.
 *
 *  It is also possible to consider the limited precision of deposition
 *  systems (for example the resolution of IO card). To do so, every
 *  dispersion curve used to define the mixture is assigned a number,
 *  and, when requested by the user, the software considers that only
 *  intermediate mixtures with integer mixture number are possible to
 *  fabricate.
 *
 *  Copyright (c) 2005-2008,2012-2014 Stephane Larouche.
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
#include <cmath>
#include <complex>
#include <algorithm>

#include "_abeles.h"


void set_mixture_center_wvl(table_mixture_type *material, const double x, const double wvl);
void set_mixture_other_wvl(table_mixture_type *material, const double x, const double wvl);
abeles_error_type prepare_and_set_mixture_PCHIPs(table_mixture_type *material, wvls_type const * const wvls);

void set_mixture_center_wvl(Cauchy_mixture_type *material, const double x, const double wvl);
void set_mixture_other_wvl(Cauchy_mixture_type *material, const double x, const double wvl);
abeles_error_type prepare_and_set_mixture_PCHIPs(Cauchy_mixture_type *material, wvls_type const * const wvls);

void set_mixture_center_wvl(Sellmeier_mixture_type *material, const double x, const double wvl);
void set_mixture_other_wvl(Sellmeier_mixture_type *material, const double x, const double wvl);
abeles_error_type prepare_and_set_mixture_PCHIPs(Sellmeier_mixture_type *material, wvls_type const * const wvls);


/*********************************************************************/
/*                                                                   */
/* new_mixture                                                       */
/*                                                                   */
/* Create a new dispersion mixture structure                         */
/*                                                                   */
/* This function takes 1 arguments:                                  */
/*   length            the number of dispersion curves defining the  */
/*                     mixture;                                      */
/* and returns a dispersion mixture structure.                       */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline mixture_type * new_mixture(const long length)
{
	mixture_type* material = (mixture_type *)malloc(sizeof(mixture_type));

	if (!material) return NULL;

	material->length = length;
	material->X = (double *)malloc(material->length*sizeof(double));
	material->_wvls = NULL;
	material->_nb_wvls = 0;
	material->_n = NULL;
	material->_k = NULL;
	material->_n_PCHIPs = NULL;
	material->_k_PCHIPs = NULL;
	material->_center_wvl = 0.0;
	material->_n_center_wvl = (double *)malloc(material->length*sizeof(double));
	material->_n_center_wvl_PCHIP = NULL;
	material->_other_wvl = 0.0;
	material->_n_other_wvl = (double *)malloc(material->length*sizeof(double));
	material->_n_other_wvl_PCHIP = NULL;

	if (!material->X || !material->_n_center_wvl || !material->_n_other_wvl)
	{
		del_mixture(material);
		return NULL;
	}

	try
	{
		material->_n_center_wvl_PCHIP = new PCHIP(material->length, material->X, material->_n_center_wvl, true, false);
		material->_n_other_wvl_PCHIP = new PCHIP(material->length, material->X, material->_n_other_wvl, true, false);
	}
	catch (const std::bad_alloc&)
	{
		del_mixture(material);
		return NULL;
	}

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_mixture                                                       */
/*                                                                   */
/* Delete a dispersion mixture structure                             */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline void del_mixture(mixture_type *material)
{
	long														i;

	if (!material) return;

	if (material->_n_PCHIPs)
		for (i = 0; i < material->_nb_wvls; i++)
			delete material->_n_PCHIPs[i];
	if (material->_k_PCHIPs)
		for (i = 0; i < material->_nb_wvls; i++)
			delete material->_k_PCHIPs[i];
	if (material->_n)
		for (i = 0; i < material->_nb_wvls; i++)
			free(material->_n[i]);
	if (material->_k)
		for (i = 0; i < material->_nb_wvls; i++)
			free(material->_k[i]);

	delete material->_n_center_wvl_PCHIP;
	free(material->_n_center_wvl);
	delete material->_n_other_wvl_PCHIP;
	free(material->_n_other_wvl);
	delete[] material->_n_PCHIPs;
	delete[] material->_k_PCHIPs;
	free(material->_n);
	free(material->_k);
	free(material->X);

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* swap_center_and_other_wvls                                        */
/*                                                                   */
/* Swap the center and the other wavelengths                         */
/*                                                                   */
/* This function takes 1 arguments:                                  */
/*   material          the dispersion mixture structure.             */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline void swap_center_and_other_wvls(mixture_type *material)
{
	double _wvl = material->_center_wvl;
	double *_n = material->_n_center_wvl;
	PCHIP *_n_PCHIP = material->_n_center_wvl_PCHIP;
	material->_center_wvl = material->_other_wvl;
	material->_n_center_wvl = material->_n_other_wvl;
	material->_n_center_wvl_PCHIP = material->_n_other_wvl_PCHIP;
	material->_other_wvl = _wvl;
	material->_n_other_wvl = _n;
	material->_n_other_wvl_PCHIP = _n_PCHIP;
}


/*********************************************************************/
/*                                                                   */
/* prepare_mixture_PCHIPs                                            */
/*                                                                   */
/* Prepare the PCHIPs to calculate the refractive index at all       */
/* wavelengths                                                       */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   wvls              the list of wavelengths at which to prepare   */
/*                     the PCHIPs.                                   */
/* It returns a abeles_error_type, either:                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         prepare all the PCHIPs.                   */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline abeles_error_type prepare_mixture_PCHIPs(mixture_type *material, wvls_type const * const wvls)
{
	long														i_wvl;

	/* Delete previous PCHIPs, if any. */
	for (i_wvl = 0; i_wvl < material->_nb_wvls; i_wvl++)
	{
		delete material->_n_PCHIPs[i_wvl];
		delete material->_k_PCHIPs[i_wvl];
		free(material->_n[i_wvl]);
		free(material->_k[i_wvl]);
	}
	free(material->_n);
	free(material->_k);
	delete[] material->_n_PCHIPs;
	delete[] material->_k_PCHIPs;

	material->_wvls = NULL;
	material->_nb_wvls = 0;
	material->_n = NULL;
	material->_k = NULL;
	material->_n_PCHIPs = NULL;
	material->_k_PCHIPs = NULL;

	/* Create n, k, and PCHIP lists. */
	double **_n = (double **)malloc(wvls->length*sizeof(double *));
	double **_k = (double **)malloc(wvls->length*sizeof(double *));
	PCHIP **_n_PCHIPs = NULL;
	PCHIP **_k_PCHIPs = NULL;

	if (!_n || !_k)
	{
		free(_n);
		free(_k);

		return ABELES_OUT_OF_MEMORY;
	}

	try
	{
		_n_PCHIPs = new PCHIP*[wvls->length];
		_k_PCHIPs = new PCHIP*[wvls->length];
	}
	catch (const std::bad_alloc&)
	{
		free(_n);
		free(_k);
		delete[] _n_PCHIPs;
		delete[] _k_PCHIPs;

		return ABELES_OUT_OF_MEMORY;
	}

	for (i_wvl = 0; i_wvl < wvls->length; i_wvl++)
	{
		_n[i_wvl] = (double *)malloc(material->length*sizeof(double));
		_k[i_wvl] = (double *)malloc(material->length*sizeof(double));
		_n_PCHIPs[i_wvl] = NULL;
		_k_PCHIPs[i_wvl] = NULL;
	}

	for (i_wvl = 0; i_wvl < wvls->length; i_wvl++)
	{
		if (!_n[i_wvl] || !_k[i_wvl])
		{
			for (i_wvl = 0; i_wvl < wvls->length; i_wvl++)
			{
				free(_n[i_wvl]);
				free(_k[i_wvl]);
			}
			free(_n);
			free(_k);
			delete[] _n_PCHIPs;
			delete[] _k_PCHIPs;

			return ABELES_OUT_OF_MEMORY;
		}
	}

	try
	{
		for (i_wvl = 0; i_wvl < wvls->length; i_wvl++)
		{
			_n_PCHIPs[i_wvl] = new PCHIP(material->length, material->X, _n[i_wvl], true, false);
			_k_PCHIPs[i_wvl] = new PCHIP(material->length, material->X, _k[i_wvl], true, false);
		}
	}
	catch (const std::bad_alloc&)
	{
		for (i_wvl = 0; i_wvl < wvls->length; i_wvl++)
		{
			delete _n_PCHIPs[i_wvl];
			delete _k_PCHIPs[i_wvl];
			free(_n[i_wvl]);
			free(_k[i_wvl]);
		}
		free(_n);
		free(_k);
		delete[] _n_PCHIPs;
		delete[] _k_PCHIPs;

		return ABELES_OUT_OF_MEMORY;
	}

	material->_wvls = wvls;
	material->_nb_wvls = material->_wvls->length;
	material->_n = _n;
	material->_k = _k;
	material->_n_PCHIPs = _n_PCHIPs;
	material->_k_PCHIPs = _k_PCHIPs;

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* get_mixture_monotonicity                                          */
/*                                                                   */
/* Determine if the index of refraction of a mixture is monotone at  */
/* a given wavelength                                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   wvl               the wavelength;                               */
/* and returns a boolean that is true if the index of refraction is  */
/* monotonic, and false otherwise.                                   */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline bool get_mixture_monotonicity(mixture_type *material, const double wvl)
{
	double													*n_wvl;

	/* If the center wavelength is not defined, it is probably the first
	 * time this material is used and the center wavelength will be
	 * reused. Otherwise, the wavelength is probably about to be changed
	 * and the other wavelength will be reused. */
	if (material->_center_wvl == 0.0)
	{
		set_mixture_center_wvl(material, wvl);
		n_wvl = material->_n_center_wvl;
	}
	else
	{
		if (wvl != material->_other_wvl) set_mixture_other_wvl(material, wvl);
		n_wvl = material->_n_other_wvl;
	}

	/* Check monotonicity. */
	for (long i = 1; i < material->length; i++)
	{
		if (n_wvl[i] <= n_wvl[i-1])
			return false;
	}

	return true;
}


/*********************************************************************/
/*                                                                   */
/* get_mixture_index                                                 */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a         */
/* dispersion mixture                                                */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   x                 the number of the mixture;                    */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline double get_mixture_index(mixture_type *material, const double x, const double wvl)
{
	double													n;

	/* If the wavelength is different from the last time a calculation
	 * was done, recalculate the index and reset the PCHIP. */
	if (wvl != material->_center_wvl) set_mixture_center_wvl(material, wvl);

	/* Get the index by using the PCHIP. */
	material->_n_center_wvl_PCHIP->evaluate(1, &x, &n);

	return n;
}


/*********************************************************************/
/*                                                                   */
/* get_mixture_index_range                                           */
/*                                                                   */
/* Get the range of index of refraction at a single wavelength from  */
/* a dispersion mixture                                              */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   wvl               the wavelength;                               */
/*   n_min, n_max      pointers to floats to return the values of    */
/*                     the minimal and maximal indices.              */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline void get_mixture_index_range(mixture_type *material, const double wvl, double *n_min, double *n_max)
{
	/* If the wavelength is different from the last time a calculation
	 * was done, recalculate the index and reset the PCHIP. */
	if (wvl != material->_center_wvl) set_mixture_center_wvl(material, wvl);

	*n_min = material->_n_center_wvl[0];
	*n_max = material->_n_center_wvl[material->length-1];
}


/*********************************************************************/
/*                                                                   */
/* change_mixture_index_wvl                                          */
/*                                                                   */
/* Get the index of refraction at a given wavelength from that at    */
/* another wavelength from the dispersion curves of a mixture        */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   old_n             the real part of index of refraction at the   */
/*                     original wavelength;                          */
/*   old_wvl           the original wavelength;                      */
/*   new_wvl           the new wavelength;                           */
/* and returns the real part of the index of refraction at the new   */
/* wavelength.                                                       */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline double change_mixture_index_wvl(mixture_type *material, const double old_n, const double old_wvl, const double new_wvl)
{
	long														i_mix;
	double													x;
	double													new_n;

	/* If the wavelength is different from the last time a calculation
	 * was done, recalculate the index and reset the PCHIP. */
	if (old_wvl != material->_center_wvl) set_mixture_center_wvl(material, old_wvl);

	/* If the other wavelength is different from the last time a
	 * calculation was done, recalculate the index and reset the PCHIP. */
	if (new_wvl != material->_other_wvl) set_mixture_other_wvl(material, new_wvl);

	/* Locate the interval where the mixture is located. */
	i_mix = locate(material->length, material->_n_center_wvl, old_n, false);

	/* Get the mixture by using the inverse of the PCHIP. */
	material->_n_center_wvl_PCHIP->evaluate_inverse(1, &old_n, &x, &i_mix);

	/* Evaluate the PCHIP at the new wavelength. */
	material->_n_other_wvl_PCHIP->evaluate(1, &x, &new_n, &i_mix);

	return new_n;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture                                                     */
/*                                                                   */
/* Set an index structure according the the dispersion of a mixture  */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   N                 the structure in which to store the index;    */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline abeles_error_type set_N_mixture(mixture_type *material, const N_type *N, const double n_wvl, const double wvl)
{
	long														i_mix, i_wvl;
	double													x;
	double													n, k;
	abeles_error_type								result;

	/* If the wavelength is different from the last time a calculation
	 * was done, recalculate the index and reset the PCHIP. */
	if (wvl != material->_center_wvl) set_mixture_center_wvl(material, wvl);

	/* Prepare and set PCHIPs at every wavelength, if necessary. */
	if (N->wvls != material->_wvls)
	{
		result = prepare_and_set_mixture_PCHIPs(material, N->wvls);
		if (result) return result;
	}

	/* Locate the interval where the mixture is located. */
	i_mix = locate(material->length, material->_n_center_wvl, n_wvl, false);

	/* Get the mixture by using the inverse of the PCHIP. */
	material->_n_center_wvl_PCHIP->evaluate_inverse(1, &n_wvl, &x, &i_mix);

	/* Evaluate n and k using the PCHIPs. Make sure k does not get bellow
	 * zero because of the PCHIP. */
	for (i_wvl = 0; i_wvl < N->wvls->length; i_wvl++)
	{
		material->_n_PCHIPs[i_wvl]->evaluate(1, &x, &n, &i_mix);
		material->_k_PCHIPs[i_wvl]->evaluate(1, &x, &k, &i_mix);
		N->N[i_wvl] = std::complex<double>(n, std::min(k, 0.0));
	}

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_by_x                                                */
/*                                                                   */
/* Set an index structure according the the dispersion of a mixture  */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   N                 the structure in which to store the index;    */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline abeles_error_type set_N_mixture_by_x(mixture_type *material, const N_type *N, const double x)
{
	long														i_mix, i_wvl;
	double													n, k;
	abeles_error_type								result;

	/* Prepare and set PCHIPs at every wavelength, if necessary. */
	if (N->wvls != material->_wvls)
	{
		result = prepare_and_set_mixture_PCHIPs(material, N->wvls);
		if (result) return result;
	}

	/* Locate the interval where the mixture is located. */
	i_mix = locate(material->length, material->X, x, false);

	/* Evaluate n and k using the PCHIPs. Make sure k does not get bellow
	 * zero because of the PCHIP. */
	for (i_wvl = 0; i_wvl < N->wvls->length; i_wvl++)
	{
		material->_n_PCHIPs[i_wvl]->evaluate(1, &x, &n, &i_mix);
		material->_k_PCHIPs[i_wvl]->evaluate(1, &x, &k, &i_mix);
		N->N[i_wvl] = std::complex<double>(n, std::min(k, 0.0));
	}

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_mixture                                                    */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a mixture               */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the dispersion mixture structure;             */
/*   dN                the structure in which to store the           */
/*                     derivative;                                   */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It returns  */
/* a abeles_error_type, either:                                      */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
template<typename mixture_type> inline abeles_error_type set_dN_mixture(mixture_type *material, const N_type *dN, const double n_wvl, const double wvl)
{
	long														i_mix, i_wvl;
	double													x;
	double													dn_wvl, dn, dk, k;
	abeles_error_type								result;

	/* If the wavelength is different from the last time a calculation
	 * was done, recalculate the index and reset the PCHIP. */
	if (wvl != material->_center_wvl) set_mixture_center_wvl(material, wvl);

	/* Prepare and set PCHIPs at every wavelength, if necessary. */
	if (dN->wvls != material->_wvls)
	{
		result = prepare_and_set_mixture_PCHIPs(material, dN->wvls);
		if (result) return result;
	}

	/* Locate the interval where the mixture is located. */
	i_mix = locate(material->length, material->_n_center_wvl, n_wvl, false);

	/* Get the mixture by using the inverse of the PCHIP. */
	material->_n_center_wvl_PCHIP->evaluate_inverse(1, &n_wvl, &x, &i_mix);

	/* The derivative of the real part at the definition wavelength. */
	material->_n_center_wvl_PCHIP->evaluate_derivative(1, &x, &dn_wvl, &i_mix);

	/* Evaluate dn and dk using the PCHIPs and normalize. */
	for (i_wvl = 0; i_wvl < dN->wvls->length; i_wvl++)
	{
		material->_n_PCHIPs[i_wvl]->evaluate_derivative(1, &x, &dn, &i_mix);
		material->_k_PCHIPs[i_wvl]->evaluate_derivative(1, &x, &dk, &i_mix);

		/* Evaluate k using the PCHIP. If k is larger than 0, set the
		 * derivative to 0. */
		material->_k_PCHIPs[i_wvl]->evaluate(1, &x, &k, &i_mix);
		if (k > 0.0)
			dk = 0.0;

		dN->N[i_wvl] = std::complex<double>(dn/dn_wvl, dk/dn_wvl);
	}

	return ABELES_SUCCESS;
}


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_constant_mixture                                              */
/*                                                                   */
/* Create a new constant dispersion mixture structure                */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length            the number of dispersion curves defining the  */
/*                     mixture;                                      */
/* and returns a constant dispersion mixture structure.              */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
constant_mixture_type * new_constant_mixture(const long length)
{
	constant_mixture_type						*material;

	material = (constant_mixture_type *)malloc(sizeof(Cauchy_mixture_type));

	if (!material) return NULL;

	material->length = length;
	material->X = (double *)malloc(material->length*sizeof(double));
	material->n = (double *)malloc(material->length*sizeof(double));
	material->k = (double *)malloc(material->length*sizeof(double));
	material->_n_PCHIP = NULL;
	material->_k_PCHIP = NULL;

	if (!material->X || !material->n || !material->k)
	{
		del_constant_mixture(material);
		return NULL;
	}

	try
	{
		material->_n_PCHIP = new PCHIP(material->length, material->X, material->n, true, false);
		material->_k_PCHIP = new PCHIP(material->length, material->X, material->k, true, false);
	}
	catch (const std::bad_alloc&)
	{
		del_constant_mixture(material);
		return NULL;
	}


	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_constant_mixture                                              */
/*                                                                   */
/* Delete a constant dispersion mixture structure                    */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_constant_mixture(constant_mixture_type *material)
{
	if (!material) return;

	delete material->_n_PCHIP;
	delete material->_k_PCHIP;
	free(material->X);
	free(material->n);
	free(material->k);

	free(material);
}


/*********************************************************************/
/*                                                                   */
/* set_constant_mixture                                              */
/*                                                                   */
/* Set the value of the index of refraction for constant dispersion  */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   i                 the position of the dispersion curve in the   */
/*                     structure;                                    */
/*   x                 the number associated with the mixture (used  */
/*                     to determine what mixtures are fabricable);   */
/*   N                 the index of refraction.                      */
/*                                                                   */
/*********************************************************************/
void set_constant_mixture(const constant_mixture_type *material, const long i, const double x, const std::complex<double> N)
{
	material->X[i] = x;
	material->n[i] = real(N);
	material->k[i] = imag(N);
}


/*********************************************************************/
/*                                                                   */
/* prepare_constant_mixture                                          */
/*                                                                   */
/* This function is deprecated                                       */
/*                                                                   */
/*********************************************************************/
void prepare_constant_mixture(const constant_mixture_type *material)
{
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_monotonicity                                 */
/*                                                                   */
/* Determine if the index of refraction of a mixture is monotone at  */
/* a given wavelength                                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   wvl               the wavelength;                               */
/* and returns a boolean that is true if the index of refraction is  */
/* monotonic, and false otherwise.                                   */
/*                                                                   */
/*********************************************************************/
bool get_constant_mixture_monotonicity(const constant_mixture_type *material, const double wvl)
{
	long														i_mix;

	for (i_mix = 1; i_mix < material->length; i_mix++)
	{
		if (material->n[i_mix] <= material->n[i_mix-1])
			return false;
	}

	return true;
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_index                                        */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a         */
/* constant dispersion mixture                                       */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   x                 the number of the mixture;                    */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
double get_constant_mixture_index(const constant_mixture_type *material, const double x, const double wvl)
{
	double													n;

	/* Get the index by using the PCHIP. */
	material->_n_PCHIP->evaluate(1, &x, &n);

	return n;
}


/*********************************************************************/
/*                                                                   */
/* get_constant_mixture_index_range                                  */
/*                                                                   */
/* Get the range of index of refraction at a single wavelength from  */
/* a constant dispersion mixture                                     */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   wvl               the wavelength;                               */
/*   n_min, n_max      pointers to floats to return the values of    */
/*                     the minimal and maximal indices.              */
/*                                                                   */
/*********************************************************************/
void get_constant_mixture_index_range(const constant_mixture_type *material, const double wvl, double *n_min, double *n_max)
{
	*n_min = material->n[0];
	*n_max = material->n[material->length-1];
}


/*********************************************************************/
/*                                                                   */
/* change_constant_mixture_index_wvl                                 */
/*                                                                   */
/* Get the index of refraction at a given wavelength from that at    */
/* another wavelength from the dispersion curves of a constant       */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   old_n             the real part of index of refraction at the   */
/*                     original wavelength;                          */
/*   old_wvl           the original wavelength;                      */
/*   new_wvl           the new wavelength;                           */
/* and returns the real part of the index of refraction at the new   */
/* wavelength.                                                       */
/*                                                                   */
/*********************************************************************/
double change_constant_mixture_index_wvl(const constant_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl)
{
	return old_n;
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture                                            */
/*                                                                   */
/* Set an index structure according the the dispersion of a constant */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   N                 the structure in which to store the index;    */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_constant_mixture(const constant_mixture_type *material, const N_type *N, const double n_wvl, const double wvl)
{
	long														i;
	double													x;
	double													k;
	std::complex<double>						nk;

	/* Locate the interval where the mixture is located. */
	i = locate(material->length, material->n, n_wvl, false);

	/* Get the mixture by using the inverse of the PCHIP. */
	material->_n_PCHIP->evaluate_inverse(1, &n_wvl, &x, &i);

	/* Evaluate k using the PCHIP. */
	material->_k_PCHIP->evaluate(1, &x, &k, &i);

	/* Set the index. */
	nk = std::complex<double>(n_wvl, std::min(k, 0.0));
	for (i = 0; i < N->wvls->length; i++)
		N->N[i] = nk;

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture_by_x                                       */
/*                                                                   */
/* Set an index structure according the the dispersion of a constant */
/* mixture                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   N                 the structure in which to store the index;    */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_constant_mixture_by_x(const constant_mixture_type *material, const N_type *N, const double x)
{
	long														i;
	double													n, k;
	std::complex<double>						nk;

	/* Locate the interval where the mixture is located. */
	i = locate(material->length, material->X, x, false);

	/* Evaluate n and k using the PCHIPs. */
	material->_n_PCHIP->evaluate(1, &x, &n, &i);
	material->_k_PCHIP->evaluate(1, &x, &k, &i);

	/* Set the index. */
	nk = std::complex<double>(n, std::min(k, 0.0));
	for (i = 0; i < N->wvls->length; i++)
		N->N[i] = nk;

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* set_dN_constant_mixture                                           */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a constant mixture      */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   dN                the structure in which to store the           */
/*                     derivative;                                   */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_constant_mixture(const constant_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl)
{
	long														i;
	double													x;
	double													_dn, _dk, k;
	std::complex<double>						dnk;

	/* Locate the interval where the mixture is located. */
	i = locate(material->length, material->n, n_wvl, false);

	/* Get the mixture by using the inverse of the PCHIP. */
	material->_n_PCHIP->evaluate_inverse(1, &n_wvl, &x, &i);

	/* Evaluate dN and dk using the PCHIPs. */
	material->_n_PCHIP->evaluate_derivative(1, &x, &_dn, &i);
	material->_k_PCHIP->evaluate_derivative(1, &x, &_dk, &i);

	/* Evaluate k using the PCHIP. If k is larger than 0, set the
	 * derivative to 0. */
	material->_k_PCHIP->evaluate(1, &x, &k, &i);
	if (k > 0.0)
		_dk = 0.0;

	/* The derivative is the same for all wavelengths. When normalized
	 * by dN at the center wavelength, dN equals 1. */
	dnk = std::complex<double>(1.0, _dk/_dn);
	for (i = 0; i < dN->wvls->length; i++)
		dN->N[i] = dnk;

	return ABELES_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* new_table_mixture                                                 */
/*                                                                   */
/* Create a new table dispersion mixture structure                   */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   length            the number of dispersion curves defining the  */
/*                     mixture;                                      */
/*   nb_wvls           the number of wavelengths in every            */
/*                     dispersion curve;                             */
/* and returns a table dispersion mixture structure.                 */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
table_mixture_type * new_table_mixture(const long length, const long nb_wvls)
{
	table_mixture_type* material = new_mixture<table_mixture_type>(length);
	if (!material) return NULL;

	material->nb_wvls = nb_wvls;
	material->wvls = (double *)malloc(material->nb_wvls*sizeof(double));
	material->n = (double **)malloc(material->length*sizeof(double *));
	material->k = (double **)malloc(material->length*sizeof(double *));
	material->_table_n_PCHIPs = NULL;
	material->_table_k_PCHIPs = NULL;

	if (!material->wvls || !material->n || !material->k)
	{
		del_table_mixture(material);
		return NULL;
	}

	try
	{
		material->_table_n_PCHIPs = new (std::nothrow) PCHIP*[material->length];
		material->_table_k_PCHIPs = new (std::nothrow) PCHIP*[material->length];
	}
	catch (const std::bad_alloc&)
	{
		del_table_mixture(material);
		return NULL;
	}

	for (long i_mix = 0; i_mix < material->length; i_mix++)
	{
		material->n[i_mix] = (double *)malloc(material->nb_wvls*sizeof(double));
		material->k[i_mix] = (double *)malloc(material->nb_wvls*sizeof(double));
		material->_table_n_PCHIPs[i_mix] = NULL;
		material->_table_k_PCHIPs[i_mix] = NULL;
	}
	for (long i_mix = 0; i_mix < material->length; i_mix++)
	{
		if (!material->n[i_mix] || !material->k[i_mix])
		{
			del_table_mixture(material);
			return NULL;
		}
	}

	try
	{
		for (long i_mix = 0; i_mix < material->length; i_mix++)
		{
			material->_table_n_PCHIPs[i_mix] = new PCHIP(material->nb_wvls, material->wvls, material->n[i_mix], true, true);
			material->_table_k_PCHIPs[i_mix] = new PCHIP(material->nb_wvls, material->wvls, material->k[i_mix], true, true);
		}
	}
	catch (const std::bad_alloc&)
	{
		del_table_mixture(material);
		return NULL;
	}

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_table_mixture                                                 */
/*                                                                   */
/* Delete a table dispersion mixture structure                       */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_table_mixture(table_mixture_type *material)
{
	if (!material) return;

	if (material->_table_n_PCHIPs)
		for (long i = 0; i < material->length; i++)
			delete material->_table_n_PCHIPs[i];
	if (material->_table_k_PCHIPs)
		for (long i = 0; i < material->length; i++)
			delete material->_table_k_PCHIPs[i];
	if (material->n)
		for (long i = 0; i < material->length; i++)
			free(material->n[i]);
	if (material->k)
		for (long i = 0; i < material->length; i++)
			free(material->k[i]);

	delete[] material->_table_n_PCHIPs;
	delete[] material->_table_k_PCHIPs;
	free(material->n);
	free(material->k);
	free(material->wvls);

	del_mixture(material);
}


/*********************************************************************/
/*                                                                   */
/* set_table_mixture                                                 */
/*                                                                   */
/* Set the value of the index of refraction for table dispersion     */
/*                                                                   */
/* This function takes 6 arguments:                                  */
/*   material          the constant dispersion mixture structure;    */
/*   i_mix, i_wvl      the position of the dispersion curve in the   */
/*                     structure;                                    */
/*   x                 the number associated with the mixture (used  */
/*                     to determine what mixtures are fabricable);   */
/*   wvl               the wavelength;                               */
/*   N                 the index of refraction.                      */
/*                                                                   */
/*********************************************************************/
void set_table_mixture(const table_mixture_type *material, const long i_mix, const long i_wvl, const double x, const double wvl, const std::complex<double> N)
{
	material->X[i_mix] = x;
	material->wvls[i_wvl] = wvl;
	material->n[i_mix][i_wvl] = real(N);
	material->k[i_mix][i_wvl] = imag(N);
}


/*********************************************************************/
/*                                                                   */
/* prepare_table_mixture                                             */
/*                                                                   */
/* This function is deprecated                                       */
/*                                                                   */
/*********************************************************************/
void prepare_table_mixture(const table_mixture_type *material)
{
}


#ifdef __cplusplus
}
#endif


/*********************************************************************/
/*                                                                   */
/* set_mixture_center_wvl                                            */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_center_wvl(table_mixture_type *material, const double wvl)
{
	/* If the new center wavelength is the previous other wavelength,
	 * simply swap them. */
	if (wvl == material->_other_wvl)
	{
		swap_center_and_other_wvls(material);
		return;
	}

	/* Otherwise, recalculate the index at the center wavelength and
	 * reset the PCHIP. */
	long index = locate(material->nb_wvls, material->wvls, wvl, true);
	material->_center_wvl = wvl;
	for (long i = 0; i < material->length; i++)
		material->_table_n_PCHIPs[i]->evaluate(1, &(material->_center_wvl), &(material->_n_center_wvl[i]), &index);
	material->_n_center_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* set_mixture_other_wvl                                             */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_other_wvl(table_mixture_type *material, const double wvl)
{
	long index = locate(material->nb_wvls, material->wvls, wvl, true);
	material->_other_wvl = wvl;
	for (long i = 0; i < material->length; i++)
		material->_table_n_PCHIPs[i]->evaluate(1, &(material->_other_wvl), &(material->_n_other_wvl[i]));
	material->_n_other_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* prepare_and_set_mixture_PCHIPs                                    */
/*                                                                   */
/* Prepare and set the PCHIPs to calculate the refractive index at   */
/* all wavelengths                                                   */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   wvls              the list of wavelengths at which to prepare   */
/*                     the PCHIPs.                                   */
/* It returns a abeles_error_type, either:                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         prepare all the PCHIPs.                   */
/*                                                                   */
/*********************************************************************/
abeles_error_type prepare_and_set_mixture_PCHIPs(table_mixture_type *material, wvls_type const * const wvls)
{
	abeles_error_type								result;
	long														position;
	double													wvl;

	/* Prepare the PCHIPs. */
	result = prepare_mixture_PCHIPs(material, wvls);
	if (result) return result;

	/* Set the PCHIPs. */
	for (long i_wvl = 0, position = 0; i_wvl < material->_nb_wvls; i_wvl++)
	{
		wvl = material->_wvls->wvls[i_wvl];

		/* The position of the wavelength in the table is determined by
		 * simply going through the whole table. This method works because
		 * the wavelengths are in increasing order. It is only effective
		 * if the number of wavelengths is similar to that in the table
		 * and are uniformly distributed. This is usually the case. */
		while (wvl >= material->wvls[position+1] and position < material->nb_wvls-2)
			position += 1;

		/* Calculate n and k at this wavelength for all mixtures. */
		for (long i_mix = 0; i_mix < material->length; i_mix++)
		{
			material->_table_n_PCHIPs[i_mix]->evaluate(1, &(wvl), &(material->_n[i_wvl][i_mix]), &position);
			material->_table_k_PCHIPs[i_mix]->evaluate(1, &(wvl), &(material->_k[i_wvl][i_mix]), &position);
		}

		/* Reset the PCHIPs. */
		material->_n_PCHIPs[i_wvl]->reset();
		material->_k_PCHIPs[i_wvl]->reset();
	}

	return ABELES_SUCCESS;
}


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_monotonicity                                    */
/*                                                                   */
/* Determine if the index of refraction of a mixture is monotone at  */
/* a given wavelength                                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   wvl               the wavelength;                               */
/* and returns a boolean that is true if the index of refraction is  */
/* monotonic, and false otherwise.                                   */
/*                                                                   */
/*********************************************************************/
bool get_table_mixture_monotonicity(table_mixture_type *material, const double wvl)
{
	return get_mixture_monotonicity(material, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_index                                           */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a table   */
/* dispersion mixture.                                               */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   x                 the number of the mixture;                    */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
double get_table_mixture_index(table_mixture_type *material, const double x, const double wvl)
{
	return get_mixture_index(material, x, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_table_mixture_index_range                                     */
/*                                                                   */
/* Get the range of index of refraction at a single wavelength from  */
/* a table dispersion mixture                                        */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   wvl               the wavelength;                               */
/*   n_min, n_max      pointers to floats to return the values of    */
/*                     the minimal and maximal indices.              */
/*                                                                   */
/*********************************************************************/
void get_table_mixture_index_range(table_mixture_type *material, const double wvl, double *n_min, double *n_max)
{
	get_mixture_index_range(material, wvl, n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_table_mixture_index_wvl                                    */
/*                                                                   */
/* Get the index of refraction at a given wavelength from that at    */
/* another wavelength from the dispersion curves of a table mixture  */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   old_n             the real part of index of refraction at the   */
/*                     original wavelength;                          */
/*   old_wvl           the original wavelength;                      */
/*   new_wvl           the new wavelength;                           */
/* and returns the real part of the index of refraction at the new   */
/* wavelength.                                                       */
/*                                                                   */
/*********************************************************************/
double change_table_mixture_index_wvl(table_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl)
{
	return change_mixture_index_wvl(material, old_n, old_wvl, new_wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture                                               */
/*                                                                   */
/* Set an index structure according the the dispersion of a table    */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   N                 the structure in which to store the index;    */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_table_mixture(table_mixture_type *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_mixture(material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture_by_x                                          */
/*                                                                   */
/* Set an index structure according the the dispersion of a table    */
/* mixture                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   N                 the structure in which to store the index;    */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_table_mixture_by_x(table_mixture_type *material, const N_type *N, const double x)
{
	return set_N_mixture_by_x(material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_table_mixture                                              */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a table mixture         */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the table dispersion mixture structure;       */
/*   dN                the structure in which to store the           */
/*                     derivative;                                   */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It returns  */
/* a abeles_error_type, either:                                      */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_table_mixture(table_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_mixture(material, dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* new_Cauchy_mixture                                                */
/*                                                                   */
/* Create a new Cauchy dispersion mixture structure                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length            the number of dispersion curves defining the  */
/*                     mixture;                                      */
/* and returns a Cauchy dispersion mixture structure.                */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
Cauchy_mixture_type * new_Cauchy_mixture(const long length)
{
	Cauchy_mixture_type* material = new_mixture<Cauchy_mixture_type>(length);
	if (!material) return NULL;

	material->A = (double *)malloc(material->length*sizeof(double));
	material->B = (double *)malloc(material->length*sizeof(double));
	material->C = (double *)malloc(material->length*sizeof(double));
	material->Ak = (double *)malloc(material->length*sizeof(double));
	material->exponent = (double *)malloc(material->length*sizeof(double));
	material->edge = (double *)malloc(material->length*sizeof(double));

	if (!material->A || !material->B || !material->C
	    || !material->Ak || !material->exponent || !material->edge)
	{
		del_Cauchy_mixture(material);
		return NULL;
	}

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_Cauchy_mixture                                                */
/*                                                                   */
/* Delete a Cauchy dispersion mixture structure                      */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_Cauchy_mixture(Cauchy_mixture_type *material)
{
	if (!material) return;

	free(material->A);
	free(material->B);
	free(material->C);
	free(material->Ak);
	free(material->exponent);
	free(material->edge);

	del_mixture(material);
}


/*********************************************************************/
/*                                                                   */
/* set_Cauchy_mixture                                                */
/*                                                                   */
/* Set the dispersion formula for Cauchy dispersion mixture          */
/*                                                                   */
/* This function takes 9 arguments:                                  */
/*   material            the Cauchy dispersion mixture structure;    */
/*   i                   the position of the dispersion curve in the */
/*                       structure;                                  */
/*   x                   the number associated with the mixture      */
/*                       (used to determine what mixtures are        */
/*                       fabricable);                                */
/*   A, B, C             the parameters of the Cauchy dispersion     */
/*                       model;                                      */
/*   Ak, exponent, edge  the parameters of the Urbach absorption     */
/*                       tail.                                       */
/*                                                                   */
/*********************************************************************/
void set_Cauchy_mixture(const Cauchy_mixture_type *material, const long i, const double x, const double A, const double B, const double C, const double Ak, const double exponent, const double edge)
{
	material->X[i] = x;
	material->A[i] = A;
	material->B[i] = B;
	material->C[i] = C;
	material->Ak[i] = Ak;
	material->exponent[i] = exponent;
	material->edge[i] = edge;
}


/*********************************************************************/
/*                                                                   */
/* prepare_Cauchy_mixture                                            */
/*                                                                   */
/* This function is deprecated                                       */
/*                                                                   */
/*********************************************************************/
void prepare_Cauchy_mixture(const Cauchy_mixture_type *material)
{
}


#ifdef __cplusplus
}
#endif


/*********************************************************************/
/*                                                                   */
/* set_mixture_center_wvl                                            */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_center_wvl(Cauchy_mixture_type *material, const double wvl)
{
	double													wvl_micron, wvl_micron_square;

	/* If the new center wavelength is the previous other wavelength,
	 * simply swap them. */
	if (wvl == material->_other_wvl)
	{
		swap_center_and_other_wvls(material);
		return;
	}

	/* Otherwise, recalculate the index at the center wavelength and
	 * reset the PCHIP. */
	material->_center_wvl = wvl;
	wvl_micron = 0.001*material->_center_wvl;
	wvl_micron_square = wvl_micron*wvl_micron;
	for (long i = 0; i < material->length; i++)
		material->_n_center_wvl[i] = material->A[i] + material->B[i]/wvl_micron_square + material->C[i]/(wvl_micron_square*wvl_micron_square);
	material->_n_center_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* set_mixture_other_wvl                                             */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_other_wvl(Cauchy_mixture_type *material, const double wvl)
{
	double													wvl_micron, wvl_micron_square;

	material->_other_wvl = wvl;
	wvl_micron = 0.001*material->_other_wvl;
	wvl_micron_square = wvl_micron*wvl_micron;
	for (long i = 0; i < material->length; i++)
		material->_n_other_wvl[i] = material->A[i] + material->B[i]/wvl_micron_square + material->C[i]/(wvl_micron_square*wvl_micron_square);
	material->_n_other_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* prepare_and_set_mixture_PCHIPs                                    */
/*                                                                   */
/* Prepare and set the PCHIPs to calculate the refractive index at   */
/* all wavelengths.                                                  */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   wvls              the list of wavelengths at which to prepare   */
/*                     the PCHIPs.                                   */
/* It returns a abeles_error_type, either:                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         prepare all the PCHIPs.                   */
/*                                                                   */
/*********************************************************************/
abeles_error_type prepare_and_set_mixture_PCHIPs(Cauchy_mixture_type *material, wvls_type const * const wvls)
{
	double													wvl_micron, wvl_micron_square;
	abeles_error_type								result;

	/* Prepare the PCHIPs. */
	result = prepare_mixture_PCHIPs(material, wvls);
	if (result) return result;

	/* Set the PCHIPs. */
	for (long i_wvl = 0; i_wvl < material->_nb_wvls; i_wvl++)
	{
		wvl_micron = 0.001*material->_wvls->wvls[i_wvl];
		wvl_micron_square = wvl_micron*wvl_micron;
		for (long i_mix = 0; i_mix < material->length; i_mix++)
		{
			material->_n[i_wvl][i_mix] = material->A[i_mix] + material->B[i_mix]/wvl_micron_square + material->C[i_mix]/(wvl_micron_square*wvl_micron_square);
			material->_k[i_wvl][i_mix] = -material->Ak[i_mix]*exp(12400.0*material->exponent[i_mix]*((1.0/(10000.0*wvl_micron))-(1.0/material->edge[i_mix])));
		}

		/* Reset the PCHIPs. */
		material->_n_PCHIPs[i_wvl]->reset();
		material->_k_PCHIPs[i_wvl]->reset();
	}

	return ABELES_SUCCESS;
}


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_monotonicity                                   */
/*                                                                   */
/* Determine if the index of refraction of a mixture is monotone at  */
/* a given wavelength                                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   wvl               the wavelength;                               */
/* and returns a boolean that is true if the index of refraction is  */
/* monotonic, and false otherwise.                                   */
/*                                                                   */
/*********************************************************************/
bool get_Cauchy_mixture_monotonicity(Cauchy_mixture_type *material, const double wvl)
{
	return get_mixture_monotonicity(material, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_index                                          */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a Cauchy  */
/* dispersion mixture                                                */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   x                 the number of the mixture;                    */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
double get_Cauchy_mixture_index(Cauchy_mixture_type *material, const double x, const double wvl)
{
	return get_mixture_index(material, x, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_Cauchy_mixture_index_range                                    */
/*                                                                   */
/* Get the range of index of refraction at a single wavelength from  */
/* a Cauchy dispersion mixture                                       */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   wvl               the wavelength;                               */
/*   n_min, n_max      pointers to floats to return the values of    */
/*                     the minimal and maximal indices.              */
/*                                                                   */
/*********************************************************************/
void get_Cauchy_mixture_index_range(Cauchy_mixture_type *material, const double wvl, double *n_min, double *n_max)
{
	get_mixture_index_range(material, wvl, n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_Cauchy_mixture_index_wvl                                   */
/*                                                                   */
/* Get the index of refraction at a given wavelength from that at an */
/* other wavelength from the dispersion curves of a Cauchy mixture   */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   old_n             the real part of index of refraction at the   */
/*                     original wavelength;                          */
/*   old_wvl           the original wavelength;                      */
/*   new_wvl           the new wavelength;                           */
/* and returns the real part of the index of refraction at the new   */
/* wavelength.                                                       */
/*                                                                   */
/*********************************************************************/
double change_Cauchy_mixture_index_wvl(Cauchy_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl)
{
	return change_mixture_index_wvl(material, old_n, old_wvl, new_wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture                                              */
/*                                                                   */
/* Set an index structure according the the dispersion of a Cauchy   */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   N                 the structure in which to store the index;    */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Cauchy_mixture(Cauchy_mixture_type *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_mixture(material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture_by_x                                         */
/*                                                                   */
/* Set an index structure according the the dispersion of a Cauchy   */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   N                 the structure in which to store the index;    */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Cauchy_mixture_by_x(Cauchy_mixture_type *material, const N_type *N, const double x)
{
	return set_N_mixture_by_x(material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Cauchy_mixture                                             */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a Cauchy mixture        */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Cauchy dispersion mixture structure;      */
/*   dN                the structure in which to store the           */
/*                     derivative;                                   */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_Cauchy_mixture(Cauchy_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_mixture(material, dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* new_Sellmeier_mixture                                             */
/*                                                                   */
/* Create a new Sellmeier dispersion mixture structure               */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length            the number of dispersion curves defining the  */
/*                     mixture;                                      */
/* and returns a Sellmeier dispersion mixture structure.             */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
Sellmeier_mixture_type * new_Sellmeier_mixture(const long length)
{
	Sellmeier_mixture_type* material = new_mixture<Sellmeier_mixture_type>(length);
	if (!material) return NULL;

	material->B1 = (double *)malloc(material->length*sizeof(double));
	material->C1 = (double *)malloc(material->length*sizeof(double));
	material->B2 = (double *)malloc(material->length*sizeof(double));
	material->C2 = (double *)malloc(material->length*sizeof(double));
	material->B3 = (double *)malloc(material->length*sizeof(double));
	material->C3 = (double *)malloc(material->length*sizeof(double));
	material->Ak = (double *)malloc(material->length*sizeof(double));
	material->exponent = (double *)malloc(material->length*sizeof(double));
	material->edge = (double *)malloc(material->length*sizeof(double));

	if (!material->B1 || !material->C1 || !material->B2
	    || !material->C2 || !material->B3 || !material->C3
	    || !material->Ak || !material->exponent || !material->edge)
	{
		del_Sellmeier_mixture(material);
		return NULL;
	}

	return material;
}


/*********************************************************************/
/*                                                                   */
/* del_Sellmeier_mixture                                             */
/*                                                                   */
/* Delete a Sellmeier dispersion mixture structure                   */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   material          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_Sellmeier_mixture(Sellmeier_mixture_type *material)
{
	if (!material) return;

	free(material->B1);
	free(material->C1);
	free(material->B2);
	free(material->C2);
	free(material->B3);
	free(material->C3);
	free(material->Ak);
	free(material->exponent);
	free(material->edge);

	del_mixture(material);
}


/*********************************************************************/
/*                                                                   */
/* set_Sellmeier_mixture                                             */
/*                                                                   */
/* Set the dispersion formula for Sellmeier dispersion mixture       */
/*                                                                   */
/* This function takes 12 arguments:                                 */
/*   material                the Sellmeier dispersion mixture        */
/*                           structure;                              */
/*   i                       the position of the dispersion curve in */
/*                           the structure;                          */
/*   x                       the number associated with the mixture  */
/*                           (used to determine what mixtures are    */
/*                           fabricable);                            */
/*   B1, C1, B2, C2, B3, C3  the parameters of the Sellmeier         */
/*                           dispersion model.                       */
/*   Ak, exponent, edge      the parameters of the Urbach absorption */
/*                           tail.                                   */
/*                                                                   */
/*********************************************************************/
void set_Sellmeier_mixture(const Sellmeier_mixture_type *material, const long i, const double x, const double B1, const double C1, const double B2, const double C2, const double B3, const double C3, const double Ak, const double exponent, const double edge)
{
	material->X[i] = x;
	material->B1[i] = B1;
	material->C1[i] = C1;
	material->B2[i] = B2;
	material->C2[i] = C2;
	material->B3[i] = B3;
	material->C3[i] = C3;
	material->Ak[i] = Ak;
	material->exponent[i] = exponent;
	material->edge[i] = edge;
}


/*********************************************************************/
/*                                                                   */
/* prepare_Sellmeier_mixture                                         */
/*                                                                   */
/* This function is deprecated                                       */
/*                                                                   */
/*********************************************************************/
void prepare_Sellmeier_mixture(const Sellmeier_mixture_type *material)
{
}


#ifdef __cplusplus
}
#endif


/*********************************************************************/
/*                                                                   */
/* set_mixture_center_wvl                                            */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_center_wvl(Sellmeier_mixture_type *material, const double wvl)
{
	double													wvl_micron, wvl_micron_square;
	double													n_square;

	/* If the new center wavelength is the previous other wavelength,
	 * simply swap them. */
	if (wvl == material->_other_wvl)
	{
		swap_center_and_other_wvls(material);
		return;
	}

	/* Otherwise, recalculate the index at the center wavelength and
	 * reset the PCHIP. */
	material->_center_wvl = wvl;
	wvl_micron = 0.001*material->_center_wvl;
	wvl_micron_square = wvl_micron*wvl_micron;
	for (long i = 0; i < material->length; i++)
	{
		n_square = 1.0+material->B1[i]*wvl_micron_square/(wvl_micron_square-material->C1[i])\
		              +material->B2[i]*wvl_micron_square/(wvl_micron_square-material->C2[i])\
		              +material->B3[i]*wvl_micron_square/(wvl_micron_square-material->C3[i]);
		material->_n_center_wvl[i] = (n_square > 0.0 && std::isfinite(n_square)) ? sqrt(n_square) : 0.0;
	}
	material->_n_center_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* set_mixture_other_wvl                                             */
/*                                                                   */
/* Recalculate some internal variables for a new wavelength          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_mixture_other_wvl(Sellmeier_mixture_type *material, const double wvl)
{
	double													wvl_micron, wvl_micron_square;
	double													n_square;

	material->_other_wvl = wvl;
	wvl_micron = 0.001*material->_other_wvl;
	wvl_micron_square = wvl_micron*wvl_micron;
	for (long i = 0; i < material->length; i++)
	{
		n_square = 1.0+material->B1[i]*wvl_micron_square/(wvl_micron_square-material->C1[i])\
		              +material->B2[i]*wvl_micron_square/(wvl_micron_square-material->C2[i])\
		              +material->B3[i]*wvl_micron_square/(wvl_micron_square-material->C3[i]);
		material->_n_other_wvl[i] = (n_square > 0.0 && std::isfinite(n_square)) ? sqrt(n_square) : 0.0;
	}
	material->_n_other_wvl_PCHIP->reset();
}


/*********************************************************************/
/*                                                                   */
/* prepare_and_set_mixture_PCHIPs                                    */
/*                                                                   */
/* Prepare and set the PCHIPs to calculate the refractive index at   */
/* all wavelengths.                                                  */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   wvls              the list of wavelengths at which to prepare   */
/*                     the PCHIPs.                                   */
/* It returns a abeles_error_type, either:                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         prepare all the PCHIPs.                   */
/*                                                                   */
/*********************************************************************/
abeles_error_type prepare_and_set_mixture_PCHIPs(Sellmeier_mixture_type *material, wvls_type const * const wvls)
{
	double													wvl_micron, wvl_micron_square;
	double													n_square;
	abeles_error_type								result;

	/* Prepare the PCHIPs. */
	result = prepare_mixture_PCHIPs(material, wvls);
	if (result) return result;

	/* Set the PCHIPs. */
	for (long i_wvl = 0; i_wvl < material->_nb_wvls; i_wvl++)
	{
		wvl_micron = 0.001*material->_wvls->wvls[i_wvl];
		wvl_micron_square = wvl_micron*wvl_micron;
		for (long i_mix = 0; i_mix < material->length; i_mix++)
		{
			n_square = 1.0+material->B1[i_mix]*wvl_micron_square/(wvl_micron_square-material->C1[i_mix])\
		                +material->B2[i_mix]*wvl_micron_square/(wvl_micron_square-material->C2[i_mix])\
		                +material->B3[i_mix]*wvl_micron_square/(wvl_micron_square-material->C3[i_mix]);
			material->_n[i_wvl][i_mix] = (n_square > 0.0 && std::isfinite(n_square)) ? sqrt(n_square) : 0.0;
			material->_k[i_wvl][i_mix] = -material->Ak[i_mix]*exp(12400.0*material->exponent[i_mix]*((1.0/(10000.0*wvl_micron))-(1.0/material->edge[i_mix])));
		}

		/* Reset the PCHIPs. */
		material->_n_PCHIPs[i_wvl]->reset();
		material->_k_PCHIPs[i_wvl]->reset();
	}

	return ABELES_SUCCESS;
}


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_monotonicity                                */
/*                                                                   */
/* Determine if the index of refraction of a mixture is monotone at  */
/* a given wavelength                                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   wvl               the wavelength;                               */
/* and returns a boolean that is true if the index of refraction is  */
/* monotonic, and false otherwise.                                   */
/*                                                                   */
/*********************************************************************/
bool get_Sellmeier_mixture_monotonicity(Sellmeier_mixture_type *material, const double wvl)
{
	return get_mixture_monotonicity(material, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_index                                       */
/*                                                                   */
/* Get the index of refraction at a single wavelength from a         */
/* Sellmeier dispersion mixture                                      */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   x                 the number of the mixture;                    */
/*   wvl               the wavelength;                               */
/* and returns the real part of the index of refraction.             */
/*                                                                   */
/*********************************************************************/
double get_Sellmeier_mixture_index(Sellmeier_mixture_type *material, const double x, const double wvl)
{
	return get_mixture_index(material, x, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_Sellmeier_mixture_index_range                                 */
/*                                                                   */
/* Get the range of index of refraction at a single wavelength from  */
/* a Sellmeier dispersion mixture                                    */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   wvl               the wavelength;                               */
/*   n_min, n_max      pointers to floats to return the values of    */
/*                     the minimal and maximal indices.              */
/*                                                                   */
/*********************************************************************/
void get_Sellmeier_mixture_index_range(Sellmeier_mixture_type *material, const double wvl, double *n_min, double *n_max)
{
	get_mixture_index_range(material, wvl, n_min, n_max);
}


/*********************************************************************/
/*                                                                   */
/* change_Sellmeier_mixture_index_wvl                                */
/*                                                                   */
/* Get the index of refraction at a given wavelength from that at an */
/* other wavelength from the dispersion curves of a Sellmeier        */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   old_n             the real part of index of refraction at the   */
/*                     original wavelength;                          */
/*   old_wvl           the original wavelength;                      */
/*   new_wvl           the new wavelength;                           */
/* and returns the real part of the index of refraction at the new   */
/* wavelength.                                                       */
/*                                                                   */
/*********************************************************************/
double change_Sellmeier_mixture_index_wvl(Sellmeier_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl)
{
	return change_mixture_index_wvl(material, old_n, old_wvl, new_wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture                                           */
/*                                                                   */
/* Set an index structure according the the dispersion of a          */
/* Sellmeier mixture                                                 */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   N                 the structure in which to store the index;    */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Sellmeier_mixture(Sellmeier_mixture_type *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_mixture(material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture_by_x                                      */
/*                                                                   */
/* Set an index structure according the the dispersion of a          */
/* Sellmeier mixture                                                 */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   N                 the structure in which to store the index;    */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Sellmeier_mixture_by_x(Sellmeier_mixture_type *material, const N_type *N, const double x)
{
	return set_N_mixture_by_x(material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Sellmeier_mixture                                          */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a Sellmeier mixture     */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          the Sellmeier dispersion mixture structure;   */
/*   dN                the structure in which to store the           */
/*                     derivative;                                   */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_Sellmeier_mixture(Sellmeier_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_mixture(material, dN, n_wvl, wvl);
}


#ifdef __cplusplus
}
#endif
