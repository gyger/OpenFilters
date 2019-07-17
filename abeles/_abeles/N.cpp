/*
 *
 *  N.cpp
 *
 *
 *  Functions to manage an array of index of refraction.
 *
 *  Copyright (c) 2002-2007,2012-2014 Stephane Larouche.
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


/*********************************************************************/
/*                                                                   */
/* new_N                                                             */
/*                                                                   */
/* Create a new index structure to store the index of refraction of  */
/* a material                                                        */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     index of refraction;                          */
/* and returns an index structure.                                   */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
N_type * new_N(const wvls_type *wvls)
{
	N_type													*N;

	N = (N_type *)malloc(sizeof(N_type));

	if (!N) return NULL;

	N->wvls = wvls;
	N->N = (std::complex<double> *)malloc(N->wvls->length*sizeof(std::complex<double>));

	if (!N->N)
	{
		del_N(N);
		return NULL;
	}

	return N;
}


/*********************************************************************/
/*                                                                   */
/* del_N                                                             */
/*                                                                   */
/* Delete an index structure                                         */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   N                 the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_N(N_type *N)
{
	if (!N) return;

	free(N->N);

	free(N);
}


/*********************************************************************/
/*                                                                   */
/* N_copy                                                            */
/*                                                                   */
/* Copy an index structure                                           */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   N_copy            the copy;                                     */
/*   N_original        the original index of refraction.             */
/*                                                                   */
/*********************************************************************/
void N_copy(N_type *N_copy, const N_type *N_original)
{
	long														i;

	for(i = 0; i < N_copy->wvls->length; i++)
		N_copy->N[i] = N_original->N[i];
}


#ifdef __cplusplus
}
#endif
