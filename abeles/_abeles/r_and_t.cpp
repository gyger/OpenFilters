/*
 *
 *  r_and_t.cpp
 *
 *
 *  Functions calculate amplitude reflexion and transmission from
 *  Abeles matrices.
 *
 *  Copyright (c) 2002-2007,2012,2013 Stephane Larouche.
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
/* new_r_and_t                                                       */
/*                                                                   */
/* Create a new r_and_t structure to store the amplitude reflection  */
/* and transmission coefficient of a stack for s and p polarization  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     coefficients;                                 */
/* and returns a r_and_t structure.                                  */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
r_and_t_type * new_r_and_t(const wvls_type *wvls)
{
	r_and_t_type										*r_and_t;

	r_and_t = (r_and_t_type *)malloc(sizeof(r_and_t_type));

	if (!r_and_t) return NULL;

	r_and_t->wvls = wvls;
	r_and_t->r_s = (std::complex<double> *)malloc(r_and_t->wvls->length*sizeof(std::complex<double>));
	r_and_t->t_s = (std::complex<double> *)malloc(r_and_t->wvls->length*sizeof(std::complex<double>));
	r_and_t->r_p = (std::complex<double> *)malloc(r_and_t->wvls->length*sizeof(std::complex<double>));
	r_and_t->t_p = (std::complex<double> *)malloc(r_and_t->wvls->length*sizeof(std::complex<double>));

	if (!r_and_t->r_s || !r_and_t->t_s || !r_and_t->r_p || !r_and_t->t_p)
	{
		del_r_and_t(r_and_t);
		return NULL;
	}

	return r_and_t;
}


/*********************************************************************/
/*                                                                   */
/* del_r_and_t                                                       */
/*                                                                   */
/* Delete a r_and_t structure                                        */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   r_and_t           the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_r_and_t(r_and_t_type *r_and_t)
{
	if (!r_and_t) return;

	free(r_and_t->r_s);
	free(r_and_t->t_s);
	free(r_and_t->r_p);
	free(r_and_t->t_p);

	free(r_and_t);
}


/*********************************************************************/
/*                                                                   */
/* calculate_r_and_t                                                 */
/*                                                                   */
/* Calculate amplitude reflection and transmission                   */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   r_and_t           the structure in which to store the results;  */
/*   M                 the characteristics matrices describing the   */
/*                     stack;                                        */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_r_and_t(const r_and_t_type *r_and_t, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						denominator;
	long														i;

	for (i = 0; i < r_and_t->wvls->length; i++)
	{
		N_square = N_m->N[i]*N_m->N[i];
		N_m_s = sqrt(N_square - sin2_theta_0->sin2[i]);
		N_m_p = N_square/N_m_s;
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);
		N_s_p = N_square/N_s_s;

		/* Correct branch selection. */
		if (real(N_m_s) == 0.0)
		{
			N_m_s = -N_m_s;
			N_m_p = -N_m_p;
		}
		if (real(N_s_s) == 0.0)
		{
			N_s_s = -N_s_s;
			N_s_p = -N_s_p;
		}

		denominator = N_m_s*M->matrices[i].s[0] + N_s_s*M->matrices[i].s[3] + N_s_s*N_m_s*M->matrices[i].s[1] + M->matrices[i].s[2];
		r_and_t->r_s[i] = (N_m_s*M->matrices[i].s[0] - N_s_s*M->matrices[i].s[3] + N_s_s*N_m_s*M->matrices[i].s[1] - M->matrices[i].s[2]) / denominator;
		r_and_t->t_s[i] = 2.0*N_m_s/denominator;

		denominator = N_m_p*M->matrices[i].p[0] + N_s_p*M->matrices[i].p[3] + N_s_p*N_m_p*M->matrices[i].p[1] + M->matrices[i].p[2];
		r_and_t->r_p[i] = (N_m_p*M->matrices[i].p[0] - N_s_p*M->matrices[i].p[3] + N_s_p*N_m_p*M->matrices[i].p[1] - M->matrices[i].p[2]) / denominator;
		r_and_t->t_p[i] = 2.0*N_m_p/denominator;
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_r_and_t_reverse                                         */
/*                                                                   */
/* Calculate amplitude reflection and transmission in reverse        */
/* direction                                                         */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   r_and_t           the structure in which to store the results;  */
/*   M                 the characteristics matrices describing the   */
/*                     stack;                                        */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_r_and_t_reverse(const r_and_t_type *r_and_t, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						denominator;
	long														i;

	/* When calculating in reverse direction we interchange N_m and N_s and
	 * use the fact that Abeles matrices are persymmetric; therefore if
	 *   M1*M2*M3*... = A
	 * then ...*M3*M2*M1 can be obtained by rotating A about the
	 * diagonal going from the upper-right corner to the lower left
	 * corner. */

	for (i = 0; i < r_and_t->wvls->length; i++)
	{
		N_square = N_m->N[i]*N_m->N[i];
		N_m_s = sqrt(N_square - sin2_theta_0->sin2[i]);
		N_m_p = N_square/N_m_s;
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);
		N_s_p = N_square/N_s_s;

		/* Correct branch selection. */
		if (real(N_m_s) == 0.0)
		{
			N_m_s = -N_m_s;
			N_m_p = -N_m_p;
		}
		if (real(N_s_s) == 0.0)
		{
			N_s_s = -N_s_s;
			N_s_p = -N_s_p;
		}

		denominator = N_s_s*M->matrices[i].s[3] + N_m_s*M->matrices[i].s[0] + N_m_s*N_s_s*M->matrices[i].s[1] + M->matrices[i].s[2];
		r_and_t->r_s[i] = (N_s_s*M->matrices[i].s[3] - N_m_s*M->matrices[i].s[0] + N_m_s*N_s_s*M->matrices[i].s[1] - M->matrices[i].s[2]) / denominator;
		r_and_t->t_s[i] = 2.0*N_s_s/denominator;

		denominator = N_s_p*M->matrices[i].p[3] + N_m_p*M->matrices[i].p[0] + N_m_p*N_s_p*M->matrices[i].p[1] + M->matrices[i].p[2];
		r_and_t->r_p[i] = (N_s_p*M->matrices[i].p[3] - N_m_p*M->matrices[i].p[0] + N_m_p*N_s_p*M->matrices[i].p[1] - M->matrices[i].p[2]) / denominator;
		r_and_t->t_p[i] = 2.0*N_s_p/denominator;
	}
}


#ifdef __cplusplus
}
#endif
