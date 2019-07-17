/*
 *
 *  circle.cpp
 *
 *
 *  Functions to calculate the circle diagram of the coating from
 *  amplitude reflection.
 *
 *  Copyright (c) 2006,2007.2012 Stephane Larouche.
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
#include <complex>

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_circle                                                        */
/*                                                                   */
/* Create a new circle structure                                     */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     circle;                                       */
/* and returns a circle structure.                                   */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
circle_type * new_circle(const wvls_type *wvls)
{
	circle_type											*circle;

	circle = (circle_type *)malloc(sizeof(circle_type));

	if (!circle) return NULL;

	circle->wvls = wvls;
	circle->data = (std::complex<double> *)malloc(circle->wvls->length*sizeof(std::complex<double>));

	if (!circle->data)
	{
		del_circle(circle);
		return NULL;
	}

	return circle;
}


/*********************************************************************/
/*                                                                   */
/* del_circle                                                        */
/*                                                                   */
/* Delete a circle structure                                         */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   circle            the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_circle(circle_type *circle)
{
	if (!circle) return;

	free(circle->data);

	free(circle);
}


/*********************************************************************/
/*                                                                   */
/* calculate_circle                                                  */
/*                                                                   */
/* Determine the value of amplitude reflection for the circle        */
/* diagram                                                           */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   circle            the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission;    */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_circle(const circle_type *circle, const r_and_t_type *r_and_t, const double polarization)
{
	long													i;

	if (polarization == S)
		for (i = 0; i < circle->wvls->length; i++)
			circle->data[i] = r_and_t->r_s[i];
	else if (polarization == P)
		for (i = 0; i < circle->wvls->length; i++)
			circle->data[i] = r_and_t->r_p[i];
}


#ifdef __cplusplus
}
#endif
