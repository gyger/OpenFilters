/*
 *
 *  electric_field.cpp
 *
 *
 *  Functions to calculate the electric field of the coating from
 *  abeles matrices.
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


#include <cmath>
#include <complex>

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* calculate_electric_field                                          */
/*                                                                   */
/* Calculate the electric in stack from its characteristic matrix    */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   electric_field    the structure in which to store the results;  */
/*   M                 the characteristics matrices describing the   */
/*                     stack;                                        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_electric_field(const spectrum_type *electric_field, const matrices_type *M, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_s_s, N_s_p;
	std::complex<double>						B;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < electric_field->wvls->length; i++)
		{
			N_square = N_s->N[i]*N_s->N[i];
			N_s_s = sqrt(N_square - (*sin2_theta_0).sin2[i]);

			/* Correct branch selection. */
			if (real(N_s_s) == 0.0)
				N_s_s = -N_s_s;

			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;

			electric_field->data[i] = abs(B);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < electric_field->wvls->length; i++)
		{
			N_square = N_s->N[i]*N_s->N[i];
			N_s_p = N_square/sqrt(N_square - (*sin2_theta_0).sin2[i]);

			/* Correct branch selection. */
			if (real(N_s_p) == 0.0)
				N_s_p = -N_s_p;

			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;

			electric_field->data[i] = abs(B);
		}
	}
}


#ifdef __cplusplus
}
#endif
