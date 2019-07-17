/*
 *
 *  sin2.cpp
 *
 *
 *  Functions to handle the squared sinus of an angle. This is useful
 *  when calculating the effective index of refraction at oblique
 *  incidence
 *
 *  Copyright (c) 2002,2004-2007,2013 Stephane Larouche.
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

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_sin2                                                          */
/*                                                                   */
/* Create a new sin2 structure to store the normalized sinus squared */
/* of the propagation angle                                          */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     sinus squared;                                */
/* and returns a sin2 structure.                                     */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/* This structure is used to store (N*sin(theta))^2 which, according */
/* to Snell-Descartes' law, is constant in the whole filter and      */
/* which is necessary in the calculation of the effective indices.   */
/*                                                                   */
/*********************************************************************/
sin2_type * new_sin2(const wvls_type *wvls)
{
	sin2_type												*sin2;

	sin2 = (sin2_type *)malloc(sizeof(sin2_type));

	if (!sin2) return NULL;

	sin2->wvls = wvls;
	sin2->sin2 = (std::complex<double> *)malloc(sin2->wvls->length*sizeof(std::complex<double>));

	if (!sin2->sin2)
	{
		del_sin2(sin2);
		return NULL;
	}

	return sin2;
}


/*********************************************************************/
/*                                                                   */
/* del_sin2                                                          */
/*                                                                   */
/* Delete a sin2 structure                                           */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   sin2              the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_sin2(sin2_type *sin2)
{
	if (!sin2) return;

	free(sin2->sin2);

	free(sin2);
}


/*********************************************************************/
/*                                                                   */
/* set_sin2_theta_0                                                  */
/*                                                                   */
/* Set the value of the normalized sinus squared of the propagation  */
/* angle                                                             */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   sin2              the structure in which to store the results;  */
/*   N                 the index of refraction of the medium where   */
/*                     the angle of incidence is defined;            */
/*   theta_0           the angle of propagation in that medium.      */
/*                                                                   */
/*********************************************************************/
void set_sin2_theta_0(const sin2_type *sin2, const N_type *N, const double theta)
{
	double													sin_theta;
	std::complex<double>						n_sin_theta;
	long														i;

	sin_theta = sin(theta*M_PI/180.0);

	for (i = 0; i < sin2->wvls->length; i++)
	{
		n_sin_theta = N->N[i]*sin_theta;
		sin2->sin2[i] = n_sin_theta*n_sin_theta;
	}
}


#ifdef __cplusplus
}
#endif
