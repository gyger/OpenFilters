/*
 *
 *  ellipso.cpp
 *
 *
 *  Functions to calculate ellipsometric variables Psi and Delta from
 *  reflexion and transmission values.
 *
 *  Copyright (c) 2003-2008,2012,2013 Stephane Larouche.
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


#ifdef __cplusplus
extern "C" {
#endif


const double two_pi = 2.0*M_PI;
const double one_hundred_eighty_over_pi = 180.0/M_PI;


/*********************************************************************/
/*                                                                   */
/* new_Psi_and_Delta                                                 */
/*                                                                   */
/* Create a new Psi_and_Delta structure                              */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     ellipsometric variables;                      */
/* and returns a Psi_and_Delta structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
Psi_and_Delta_type * new_Psi_and_Delta(const wvls_type *wvls)
{
	Psi_and_Delta_type							*Psi_and_Delta;

	Psi_and_Delta = (Psi_and_Delta_type *)malloc(sizeof(Psi_and_Delta_type));

	if (!Psi_and_Delta) return NULL;

	Psi_and_Delta->wvls = wvls;
	Psi_and_Delta->Psi = (double *)malloc(Psi_and_Delta->wvls->length*sizeof(double));
	Psi_and_Delta->Delta = (double *)malloc(Psi_and_Delta->wvls->length*sizeof(double));

	if (!Psi_and_Delta->Psi || !Psi_and_Delta->Delta)
	{
		del_Psi_and_Delta(Psi_and_Delta);
		return NULL;
	}

	return Psi_and_Delta;
}


/*********************************************************************/
/*                                                                   */
/* del_Psi_and_Delta                                                 */
/*                                                                   */
/* Delete an Psi_and_Delta structure                                 */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   Psi_and_Delta     the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_Psi_and_Delta(Psi_and_Delta_type *Psi_and_Delta)
{
	if (!Psi_and_Delta) return;

	free(Psi_and_Delta->Psi);
	free(Psi_and_Delta->Delta);

	free(Psi_and_Delta);
}


/*********************************************************************/
/*                                                                   */
/* calculate_Psi_and_Delta                                           */
/*                                                                   */
/* Calculate the ellipsometric variables of a filter                 */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   Psi_and_Delta     the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the filter.                                   */
/*                                                                   */
/* In the ellipsometry convention, the sign of r_p has to be         */
/* changed. This is inconsistant since it provokes a difference      */
/* between r_p and r_s at normal incidence, but it is usually        */
/* prefered in ellipsometry because adopting the "natural"           */
/* convention would need to have rotating elements before and after  */
/* the sample turning in opposite directions. See Rolf H. Muller,    */
/* "Definitions and conventions in ellipsometry", Surface Science,   */
/* V. 16, 14-33 (1969) for details on ellipsometric conventions.     */
/*                                                                   */
/*********************************************************************/
void calculate_Psi_and_Delta(const Psi_and_Delta_type *Psi_and_Delta, const r_and_t_type *r_and_t)
{
	long														i;
	double													abs_r_p, abs_r_s;
	double													arg_r_p, arg_r_s;

	for (i = 0; i < Psi_and_Delta->wvls->length; i++)
	{
		/* atan2 fails if both arguments are 0, consider Psi to be 45
		 * degres and Delta to be 180 degres, that is usually acceptable. */
		if (r_and_t->r_p[i] == 0.0 && r_and_t->r_s[i] == 0.0)
		{
			Psi_and_Delta->Psi[i] = 45.0;
			Psi_and_Delta->Delta[i] = 180.0;
		}
		else
		{
			abs_r_p = abs(r_and_t->r_p[i]);
			abs_r_s = abs(r_and_t->r_s[i]);

			Psi_and_Delta->Psi[i] = atan2(abs_r_p, abs_r_s)*one_hundred_eighty_over_pi;

			arg_r_p = atan2(imag(-r_and_t->r_p[i]), real(-r_and_t->r_p[i]));
			arg_r_s = atan2(imag(r_and_t->r_s[i]), real(r_and_t->r_s[i]));

			Psi_and_Delta->Delta[i] = (arg_r_p-arg_r_s)*one_hundred_eighty_over_pi;
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_Psi_and_Delta_with_backside                             */
/*                                                                   */
/* Calculate the ellipsometric variables of a filter with            */
/* consideration of the backside                                     */
/*                                                                   */
/* This function takes 7 arguments:                                  */
/*   Psi_and_Delta         the structure in which to store the       */
/*                         results;                                  */
/*   r_and_t_front         the amplitude reflection of the front     */
/*                         side;                                     */
/*   r_and_t_front_reverse the amplitude reflection of the front     */
/*                         side in reverse direction;                */
/*   r_and_t_back          the amplitude reflection of the back      */
/*                         side;                                     */
/*   N_s                   the index of refraction of the substrate; */
/*   thickness             the thickness of the substrate;           */
/*   sin2_theta_0          the normalized sinus squared of the       */
/*                         propagation angle.                        */
/*                                                                   */
/* To consider the backside, we have to consider the incoherent      */
/* reflexion on the back of the substrate. We adopt the approach     */
/* proposed in Y. H. Yang et al. "Spectroscopic ellipsometry of thin */
/* films on transparent substrates: A formalism for data             */
/* interpretation", J. Vac. Sc. Technol., V. 13, No 3, 1995,         */
/* pp. 1145-1149.                                                    */
/*                                                                   */
/*********************************************************************/
void calculate_Psi_and_Delta_with_backside(const Psi_and_Delta_type *Psi_and_Delta, const r_and_t_type *r_and_t_front, const r_and_t_type *r_and_t_front_reverse, const r_and_t_type *r_and_t_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_s_square, N_s_s;
	double													exp_minus_4_abs_beta_imag;
	double													norm_r_p_front, norm_t_p_front, norm_r_p_front_reverse, norm_t_p_front_reverse, norm_r_p_back;
	double													norm_r_s_front, norm_t_s_front, norm_r_s_front_reverse, norm_t_s_front_reverse, norm_r_s_back;
	std::complex<double>						norm_r_mixed_front, norm_t_mixed_front, norm_r_mixed_reverse, norm_t_mixed_reverse, norm_r_mixed_back;
	double													Ri_p, Ri_s, Bi_2;
	double													sqrt_norm_r_p_front_plus_Ri_p, sqrt_norm_r_s_front_plus_Ri_s;
	double													cos_Delta;
	long														i;

	for (i = 0; i < Psi_and_Delta->wvls->length; i++)
	{
		N_s_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_s_square-sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		exp_minus_4_abs_beta_imag = exp(-4.0*(fabs(imag(two_pi*thickness*N_s_s/Psi_and_Delta->wvls->wvls[i]))));

		norm_r_p_front = norm(r_and_t_front->r_p[i]);
		norm_t_p_front = norm(r_and_t_front->t_p[i]);
		norm_r_p_front_reverse = norm(r_and_t_front_reverse->r_p[i]);
		norm_t_p_front_reverse = norm(r_and_t_front_reverse->t_p[i]);
		norm_r_p_back = norm(r_and_t_back->r_p[i]);

		norm_r_s_front = norm(r_and_t_front->r_s[i]);
		norm_t_s_front = norm(r_and_t_front->t_s[i]);
		norm_r_s_front_reverse = norm(r_and_t_front_reverse->r_s[i]);
		norm_t_s_front_reverse = norm(r_and_t_front_reverse->t_s[i]);
		norm_r_s_back = norm(r_and_t_back->r_s[i]);

		norm_r_mixed_front = -r_and_t_front->r_p[i]*conj(r_and_t_front->r_s[i]);
		norm_t_mixed_front = r_and_t_front->t_p[i]*conj(r_and_t_front->t_s[i]);
		norm_r_mixed_reverse = -r_and_t_front_reverse->r_p[i]*conj(r_and_t_front_reverse->r_s[i]);
		norm_t_mixed_reverse = r_and_t_front_reverse->t_p[i]*conj(r_and_t_front_reverse->t_s[i]);
		norm_r_mixed_back = -r_and_t_back->r_p[i]*conj(r_and_t_back->r_s[i]);

		Ri_p = norm_t_p_front*norm_t_p_front_reverse*norm_r_p_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_p_front_reverse*norm_r_p_back*exp_minus_4_abs_beta_imag);
		Ri_s = norm_t_s_front*norm_t_s_front_reverse*norm_r_s_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_s_front_reverse*norm_r_s_back*exp_minus_4_abs_beta_imag);
		Bi_2 = real(norm_t_mixed_front*norm_t_mixed_reverse*norm_r_mixed_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_mixed_reverse*norm_r_mixed_back*exp_minus_4_abs_beta_imag));

		sqrt_norm_r_p_front_plus_Ri_p = sqrt(norm_r_p_front + Ri_p);
		sqrt_norm_r_s_front_plus_Ri_s = sqrt(norm_r_s_front + Ri_s);

		/* atan2 fails if both arguments are 0, consider Psi to be 45
		 * degres, that is usually acceptable. */
		if (sqrt_norm_r_p_front_plus_Ri_p == 0.0 && sqrt_norm_r_s_front_plus_Ri_s == 0.0)
			Psi_and_Delta->Psi[i] = 45.0;
		else
			Psi_and_Delta->Psi[i] = atan2(sqrt_norm_r_p_front_plus_Ri_p, sqrt_norm_r_s_front_plus_Ri_s) * one_hundred_eighty_over_pi;

		/* acos is only defined between -1 and 1. Numerical calculations,
		 * with limited precision, can provoke a value a little bit
		 * outside of this interval. The value to be given to acos
		 * is verified to avoid a bug. */
		cos_Delta = (real(norm_r_mixed_front) + Bi_2) / sqrt((norm_r_p_front + Ri_p) * (norm_r_s_front + Ri_s));
		cos_Delta = std::min(std::max(cos_Delta, -1.0), 1.0);
		Psi_and_Delta->Delta[i] = acos(cos_Delta) * one_hundred_eighty_over_pi;
	}
}


#ifdef __cplusplus
}
#endif
