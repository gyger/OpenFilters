/*
 *
 *  N_mixture.cpp
 *
 *
 *  Functions to manage the index of a mixture of material.
 *
 *  The index of refraction of mixtures of material is adjustable.
 *  It cannot be set once and for all, but rather must be associated
 *  with a dispersion formula. Furthermore, when the index of
 *  refraction of a layer is refined, it is necessary to calculate the
 *  wavelength dependant derivative of the index of refraction with
 *  regard to a variation of the index of refraction at the reference
 *  wavelength. Finally, material mixtures can be used in graded-index
 *  layers, in which the index profile is discretized according to
 *  predefined levels.
 *
 *  The structure representing the index of refraction of material
 *  mixtures therefore consists of a mixture dispersion structure,
 *  one index structure for the index of refraction, one for its
 *  derivative, and, when necessary, an array of index of refraction
 *  structures for the predefined levels of the graded-index layer.
 *
 *  Copyright (c) 2005,2007,2009,2012-2014 Stephane Larouche.
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

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/* Declaration of model specific functions with void* material
 * argument. They are used in the N_mixture_type structure to avoid
 * the necessity to build a different structure for every model.
 * These are not in abeles.h since we only use them internally. */
static abeles_error_type set_N_constant_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl);
static abeles_error_type set_N_table_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl);
static abeles_error_type set_N_Cauchy_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl);
static abeles_error_type set_N_Sellmeier_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl);
static abeles_error_type set_N_constant_mixture_by_x_(const void *material, const N_type *N, const double x);
static abeles_error_type set_N_table_mixture_by_x_(const void *material, const N_type *N, const double x);
static abeles_error_type set_N_Cauchy_mixture_by_x_(const void *material, const N_type *N, const double x);
static abeles_error_type set_N_Sellmeier_mixture_by_x_(const void *material, const N_type *N, const double x);
static abeles_error_type set_dN_constant_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl);
static abeles_error_type set_dN_table_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl);
static abeles_error_type set_dN_Cauchy_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl);
static abeles_error_type set_dN_Sellmeier_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl);


/*********************************************************************/
/*                                                                   */
/* new_N_mixture_constant                                            */
/*                                                                   */
/* Create a new index structure to store the index of refraction of  */
/* a mixture with constant dispersion                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          a constant dispersion mixture structure;      */
/*   wvls              the wavelengths at which to calculate the     */
/*                     index of refraction;                          */
/* and returns a mixture index structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_mixture_type * new_N_mixture_constant(const constant_mixture_type *material, const wvls_type *wvls)
{
	N_mixture_type									*mixture;

	mixture = (N_mixture_type *)malloc(sizeof(N_mixture_type));

	if (!mixture) return NULL;

	mixture->material = (void *)material;
	mixture->f_N = set_N_constant_mixture_;
	mixture->f_N_x = set_N_constant_mixture_by_x_;
	mixture->f_dN = set_dN_constant_mixture_;
	mixture->N = new_N(wvls);
	mixture->dN = new_N(wvls);
	mixture->length = 0;
	mixture->N_graded = NULL;

	if (!mixture->N || !mixture->dN)
	{
		del_N_mixture(mixture);
		return NULL;
	}

	return mixture;
}


/*********************************************************************/
/*                                                                   */
/* new_N_mixture_table                                               */
/*                                                                   */
/* Create a new index structure to store the index of refraction of  */
/* a mixture with table dispersion                                   */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          a table dispersion mixture structure;         */
/*   wvls              the wavelengths at which to calculate the     */
/*                     index of refraction;                          */
/* and returns a mixture index structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_mixture_type * new_N_mixture_table(const table_mixture_type *material, const wvls_type *wvls)
{
	N_mixture_type									*mixture;

	mixture = (N_mixture_type *)malloc(sizeof(N_mixture_type));

	if (!mixture) return NULL;

	mixture->material = (void *)material;
	mixture->f_N = set_N_table_mixture_;
	mixture->f_N_x = set_N_table_mixture_by_x_;
	mixture->f_dN = set_dN_table_mixture_;
	mixture->N = new_N(wvls);
	mixture->dN = new_N(wvls);
	mixture->length = 0;
	mixture->N_graded = NULL;

	if (!mixture->N || !mixture->dN)
	{
		del_N_mixture(mixture);
		return NULL;
	}

	return mixture;
}


/*********************************************************************/
/*                                                                   */
/* new_N_mixture_Cauchy                                              */
/*                                                                   */
/* Create a new index structure to store the index of refraction of  */
/* a mixture with Cauchy dispersion                                  */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          a constant dispersion mixture structure;      */
/*   wvls              the wavelengths at which to calculate the     */
/*                     index of refraction;                          */
/* and returns a mixture index structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_mixture_type * new_N_mixture_Cauchy(const Cauchy_mixture_type *material, const wvls_type *wvls)
{
	N_mixture_type									*mixture;

	mixture = (N_mixture_type *)malloc(sizeof(N_mixture_type));

	if (!mixture) return NULL;

	mixture->material = (void *)material;
	mixture->f_N = set_N_Cauchy_mixture_;
	mixture->f_N_x = set_N_Cauchy_mixture_by_x_;
	mixture->f_dN = set_dN_Cauchy_mixture_;
	mixture->N = new_N(wvls);
	mixture->dN = new_N(wvls);
	mixture->length = 0;
	mixture->N_graded = NULL;

	if (!mixture->N || !mixture->dN)
	{
		del_N_mixture(mixture);
		return NULL;
	}

	return mixture;
}


/*********************************************************************/
/*                                                                   */
/* new_N_mixture_Sellmeier                                           */
/*                                                                   */
/* Create a new index structure to store the index of refraction of  */
/* a mixture with Sellmeier dispersion                               */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   material          a constant dispersion mixture structure;      */
/*   wvls              the wavelengths at which to calculate the     */
/*                     index of refraction;                          */
/* and returns a mixture index structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_mixture_type * new_N_mixture_Sellmeier(const Sellmeier_mixture_type *material, const wvls_type *wvls)
{
	N_mixture_type									*mixture;

	mixture = (N_mixture_type *)malloc(sizeof(N_mixture_type));

	if (!mixture) return NULL;

	mixture->material = (void *)material;
	mixture->f_N = set_N_Sellmeier_mixture_;
	mixture->f_N_x = set_N_Sellmeier_mixture_by_x_;
	mixture->f_dN = set_dN_Sellmeier_mixture_;
	mixture->N = new_N(wvls);
	mixture->dN = new_N(wvls);
	mixture->length = 0;
	mixture->N_graded = NULL;

	if (!mixture->N || !mixture->dN)
	{
		del_N_mixture(mixture);
		return NULL;
	}

	return mixture;
}


/*********************************************************************/
/*                                                                   */
/* del_N_mixture                                                     */
/*                                                                   */
/* Delete a mixture index structure                                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   mixture           the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_N_mixture(N_mixture_type *mixture)
{
	long														i;

	if (!mixture) return;

	if (mixture->N_graded)
		for (i = 0; i < mixture->length; i++)
			free(mixture->N_graded[i].N);

	del_N(mixture->N);
	del_N(mixture->dN);
	free(mixture->N_graded);

	free(mixture);
}


/*********************************************************************/
/*                                                                   */
/* prepare_N_mixture_graded                                          */
/*                                                                   */
/* Prepare a mixture index structure to represent graded-index       */
/* layers                                                            */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   length            the number of index levels to prepare,        */
/* and returns a pointer to the list of index structures.            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_type * prepare_N_mixture_graded(N_mixture_type *mixture, const long length)
{
	long														i;

	if (mixture->N_graded)
	{
		for (i = 0; i < mixture->length; i++)
			free(mixture->N_graded[i].N);
		free(mixture->N_graded);
		mixture->length = 0;
		mixture->N_graded = NULL;
	}

	mixture->N_graded = (N_type *)malloc(length*sizeof(N_type));

	if (!mixture->N_graded) return NULL;

	mixture->length = length;

	for (i = 0; i < mixture->length; i++)
	{
		mixture->N_graded[i].wvls = mixture->N->wvls;
		mixture->N_graded[i].N = (std::complex<double> *)malloc(mixture->N_graded[i].wvls->length*sizeof(std::complex<double>));
	}

	for (i = 0; i < mixture->length; i++)
	{
		if (!mixture->N_graded[i].N)
		{
			for (i = 0; i < mixture->length; i++)
				free(mixture->N_graded[i].N);
			free(mixture->N_graded);
			mixture->length = 0;
			mixture->N_graded = NULL;

			return NULL;
		}
	}

	return mixture->N_graded;
}


/*********************************************************************/
/*                                                                   */
/* N_mixture_graded_is_prepared                                      */
/*                                                                   */
/* Determine if a mixture index structure was prepared to use in     */
/* graded-index layers                                               */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   mixture           the mixture index structure;                  */
/* and returns a boolean indicating if the structure is ready to be  */
/* used to represent graded-index layers.                            */
/*                                                                   */
/*********************************************************************/
bool N_mixture_graded_is_prepared(N_mixture_type *mixture)
{
	if (mixture->length > 0) return true;
	else return false;
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture                                                     */
/*                                                                   */
/* Set the index of refraction of a mixture                          */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   n_wvl             the index of refraction at a given            */
/*                     wavelength;                                   */
/*   wavelength        the wavelength;                               */
/* and sets the index of refraction using the dispersion formula     */
/* associated with the structure. It returns a abeles_error_type,    */
/* either:                                                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_mixture(const N_mixture_type *mixture, const double n_wvl, const double wvl)
{
	return mixture->f_N(mixture->material, mixture->N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_by_x                                                */
/*                                                                   */
/* Set the index of refraction of a mixture                          */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   x                 the number of the mixture;                    */
/* and sets the index of refraction using the dispersion formula     */
/* associated with the structure. It returns a abeles_error_type,    */
/* either:                                                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_mixture_by_x(const N_mixture_type *mixture, const double x)
{
	return mixture->f_N_x(mixture->material, mixture->N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_mixture                                                    */
/*                                                                   */
/* Set the derivative of the index of refraction of a mixture        */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   n_wvl             the index of refraction at a given            */
/*                     wavelength;                                   */
/*   wavelength        the wavelength;                               */
/* and sets the derivative of the index of refraction using the      */
/* dispersion formula associated with the structure. It returns a    */
/* abeles_error_type, either:                                        */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_mixture(const N_mixture_type *mixture, const double n_wvl, const double wvl)
{
	return mixture->f_dN(mixture->material, mixture->dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_mixture_graded                                              */
/*                                                                   */
/* Set the index of refraction of one mixture when the material is   */
/* used in graded-index layers                                       */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   position          the position of the index in the graded-index */
/*                     structure;                                    */
/*   n_wvl             the index of refraction at a given            */
/*                     wavelength;                                   */
/*   wavelength        the wavelength;                               */
/* and sets the index of refraction using the dispersion formula     */
/* associated with the structure. It returns a abeles_error_type,    */
/* either:                                                           */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_mixture_graded(const N_mixture_type *mixture, const long position, const double n_wvl, const double wvl)
{
	return mixture->f_N(mixture->material, &(mixture->N_graded[position]), n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* get_N_mixture                                                     */
/*                                                                   */
/* Get the index of refraction of a mixture                          */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   mixture           the mixture index structure;                  */
/* and returns the index structure representing the index of         */
/* refraction of the mixture.                                        */
/*                                                                   */
/*********************************************************************/
N_type * get_N_mixture(const N_mixture_type *mixture)
{
	return mixture->N;
}


/*********************************************************************/
/*                                                                   */
/* get_dN_mixture                                                    */
/*                                                                   */
/* Get the index of refraction of a mixture                          */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   mixture           the mixture index structure;                  */
/* and returns the index structure representing the derivative of    */
/* the index of refraction of the mixture.                           */
/*                                                                   */
/*********************************************************************/
N_type * get_dN_mixture(const N_mixture_type *mixture)
{
	return mixture->dN;
}


/*********************************************************************/
/*                                                                   */
/* get_N_mixture_graded                                              */
/*                                                                   */
/* Get the index of refraction of one level when a mixture is used   */
/* in graded-index layers                                            */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   mixture           the mixture index structure;                  */
/*   position          the position of the index in the graded-index */
/*                     structure;                                    */
/* and returns the index structure representing the index of         */
/* refraction of one level of the mixture.                           */
/*                                                                   */
/*********************************************************************/
N_type * get_N_mixture_graded(const N_mixture_type *mixture, const long position)
{
	return &(mixture->N_graded[position]);
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture_                                           */
/*                                                                   */
/* Set an index structure according the the dispersion of a constant */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the constant dispersion     */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_constant_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_constant_mixture((constant_mixture_type *)material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture_                                              */
/*                                                                   */
/* Set an index structure according the the dispersion of a table    */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a voic pointer to the table dispersion        */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_table_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_table_mixture((table_mixture_type *)material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture_                                             */
/*                                                                   */
/* Set an index structure according the the dispersion of a Cauchy   */
/* mixture                                                           */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the Cauchy dispersion       */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Cauchy_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_Cauchy_mixture((Cauchy_mixture_type *)material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture_                                          */
/*                                                                   */
/* Set an index structure according the the dispersion of a          */
/* Sellmeier mixture                                                 */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the Sellmeier dispersion    */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Sellmeier_mixture_(const void *material, const N_type *N, const double n_wvl, const double wvl)
{
	return set_N_Sellmeier_mixture((Sellmeier_mixture_type *)material, N, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_N_constant_mixture_by_x_                                      */
/*                                                                   */
/* Set an index structure according the the dispersion of a constant */
/* mixture                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          a void pointer to the constant dispersion     */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_constant_mixture_by_x_(const void *material, const N_type *N, const double x)
{
	return set_N_constant_mixture_by_x((constant_mixture_type *)material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_N_table_mixture_by_x_                                         */
/*                                                                   */
/* Set an index structure according the the dispersion of a table    */
/* mixture                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          a voic pointer to the table dispersion        */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It returns a abeles_error_type, either:                  */
/*   ABELES_SUCCESS        the function succeeded;                   */
/*   ABELES_OUT_OF_MEMORY  a malloc failed and it was impossible to  */
/*                         calculate the index.                      */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_table_mixture_by_x_(const void *material, const N_type *N, const double x)
{
	return set_N_table_mixture_by_x((table_mixture_type *)material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Cauchy_mixture_by_x_                                        */
/*                                                                   */
/* Set an index structure according the the dispersion of a Cauchy   */
/* mixture                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          a void pointer to the Cauchy dispersion       */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Cauchy_mixture_by_x_(const void *material, const N_type *N, const double x)
{
	return set_N_Cauchy_mixture_by_x((Cauchy_mixture_type *)material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_N_Sellmeier_mixture_by_x_                                     */
/*                                                                   */
/* Set an index structure according the the dispersion of a          */
/* Sellmeier mixture                                                 */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   material          a void pointer to the Sellmeier dispersion    */
/*                     mixture structure;                            */
/*   N                 the index structure being set;                */
/*   x                 the number of the mixture;                    */
/* and sets the index structure according to the dispersion of the   */
/* mixture. It always returns ABELES_SUCCESS.                        */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_N_Sellmeier_mixture_by_x_(const void *material, const N_type *N, const double x)
{
	return set_N_Sellmeier_mixture_by_x((Sellmeier_mixture_type *)material, N, x);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_constant_mixture_                                          */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a constant mixture      */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the constant dispersion     */
/*                     mixture structure;                            */
/*   dN                the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_constant_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_constant_mixture((constant_mixture_type *)material, dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_table_mixture_                                             */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a table mixture         */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the table dispersion        */
/*                     mixture structure;                            */
/*   dN                the index structure being set;                */
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
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_table_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_table_mixture((table_mixture_type *)material, dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Cauchy_mixture_                                            */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a Cauchy mixture        */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the Cauchy dispersion       */
/*                     mixture structure;                            */
/*   dN                the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_Cauchy_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_Cauchy_mixture((Cauchy_mixture_type *)material, dN, n_wvl, wvl);
}


/*********************************************************************/
/*                                                                   */
/* set_dN_Sellmeier_mixture_                                         */
/*                                                                   */
/* Set the derivative of the index of refraction in a index          */
/* structure according the the dispersion of a Sellmeier mixture     */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   material          a void pointer to the Sellmeier dispersion    */
/*                     mixture structure;                            */
/*   dN                the index structure being set;                */
/*   n_wvl             the real part of index of refraction at a     */
/*                     given wavelength;                             */
/*   wvl               the wavelength;                               */
/* and stores the derivative of the index of refraction in the index */
/* structure according to the dispersion of the mixture. It always   */
/* returns ABELES_SUCCESS.                                           */
/*                                                                   */
/* This function is only meant to be used internally.                */
/*                                                                   */
/*********************************************************************/
abeles_error_type set_dN_Sellmeier_mixture_(const void *material, const N_type *dN, const double n_wvl, const double wvl)
{
	return set_dN_Sellmeier_mixture((Sellmeier_mixture_type *)material, dN, n_wvl, wvl);
}


#ifdef __cplusplus
}
#endif
