/*
 *
 *  admittance.cpp
 *
 *
 *  Functions to calculate the admittance of the coating from abeles
 *  matrices.
 *
 *  Copyright (c) 2004,2006,2007,2012,2013 Stephane Larouche.
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
/* new_admittance                                                    */
/*                                                                   */
/* Create a new admittance structure                                 */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     admittance;                                   */
/* and returns an admittance structure.                              */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
admittance_type * new_admittance(const wvls_type *wvls)
{
	admittance_type									*admittance;

	admittance = (admittance_type *)malloc(sizeof(admittance_type));

	if (!admittance) return NULL;

	admittance->wvls = wvls;
	admittance->data = (std::complex<double> *)malloc(admittance->wvls->length*sizeof(std::complex<double>));

	if (!admittance->data)
	{
		del_admittance(admittance);
		return NULL;
	}

	return admittance;
}


/*********************************************************************/
/*                                                                   */
/* del_admittance                                                    */
/*                                                                   */
/* Delete an admittance structure                                    */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   admittance        the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_admittance(admittance_type *admittance)
{
	if (!admittance) return;

	free(admittance->data);

	free(admittance);
}


/*********************************************************************/
/*                                                                   */
/* calculate_admittance                                              */
/*                                                                   */
/* Calculate the admittance of a stack from its characteristic       */
/* matrix                                                            */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   admittance        the structure in which to store the results;  */
/*   M                 the characteristics matrices describing the   */
/*                     stack;                                        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_admittance(const admittance_type *admittance, const matrices_type *M, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_s_s, N_s_p;
	std::complex<double>						B, C;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < admittance->wvls->length; i++)
		{
			N_square = N_s->N[i]*N_s->N[i];
			N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_s_s) == 0.0)
				N_s_s = -N_s_s;

			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;
			C = M->matrices[i].s[2] + M->matrices[i].s[3]*N_s_s;

			admittance->data[i] = C/B;
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < admittance->wvls->length; i++)
		{
			N_square = N_s->N[i]*N_s->N[i];
			N_s_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_s_p) == 0.0)
				N_s_p = -N_s_p;

			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;
			C = M->matrices[i].p[2] + M->matrices[i].p[3]*N_s_p;

			admittance->data[i] = C/B;
		}
	}
}


#ifdef __cplusplus
}
#endif
