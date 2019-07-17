/*
 *
 *  spectro.cpp
 *
 *
 *  Functions to calculate the reflectance, transmittance and
 *  absorptance, with or without the backside.
 *
 *  Copyright (c) 2002-2008,2012,2013 Stephane Larouche.
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


const double two_pi = 2.0*M_PI;


/*********************************************************************/
/*                                                                   */
/* new_spectrum                                                      */
/*                                                                   */
/* Create a new spectrum structure to store a spectrum               */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     spectrum;                                     */
/* and returns a spectrum structure.                                 */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
spectrum_type * new_spectrum(const wvls_type *wvls)
{
	spectrum_type										*spectrum;

	spectrum = (spectrum_type *)malloc(sizeof(spectrum_type));

	if (!spectrum) return NULL;

	spectrum->wvls = wvls;
	spectrum->data = (double *)malloc(spectrum->wvls->length*sizeof(double));

	if (!spectrum->data)
	{
		del_spectrum(spectrum);
		return NULL;
	}

	return spectrum;
}


/*********************************************************************/
/*                                                                   */
/* del_spectrum                                                      */
/*                                                                   */
/* Delete a spectrum structure                                       */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   spectrum          the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_spectrum(spectrum_type *spectrum)
{
	if (!spectrum) return;

	free(spectrum->data);

	free(spectrum);
}


/*********************************************************************/
/*                                                                   */
/* calculate_R                                                       */
/*                                                                   */
/* Calculate reflectance from amplitude reflection                   */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   R                 the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the stack;                                    */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_R(const spectrum_type *R, const r_and_t_type *r_and_t, const double polarization)
{
	long														i;
	double													Psi, sin_Psi, sin_Psi_square, cos_Psi_square;

	if (polarization == S)
	{
		for (i = 0; i < R->wvls->length; i++)
			R->data[i] = norm(r_and_t->r_s[i]);
	}
	else if (polarization == P)
	{
		for (i = 0; i < R->wvls->length; i++)
			R->data[i] = norm(r_and_t->r_p[i]);
	}
	else
	{
		Psi = polarization*M_PI/180.0;
		sin_Psi = sin(Psi);
		sin_Psi_square = sin_Psi*sin_Psi;
		cos_Psi_square = 1.0-sin_Psi_square;
		for (i = 0; i < R->wvls->length; i++)
			R->data[i] = norm(r_and_t->r_s[i]) * sin_Psi_square\
			           + norm(r_and_t->r_p[i]) * cos_Psi_square;
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_T                                                       */
/*                                                                   */
/* Calculate transmittance from amplitude transmission               */
/*                                                                   */
/* This function takes 6 arguments:                                  */
/*   T                 the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the stack;                                    */
/*   N_i               the index of refraction of the incidence      */
/*                     medium;                                       */
/*   N_e               the index of refraction of the exit medium;   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_T(const spectrum_type *T, const r_and_t_type *r_and_t, const N_type *N_i, const N_type *N_e, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_i_s, N_i_p, N_e_s, N_e_p;
	long														i;
	double													Psi, sin_Psi, sin_Psi_square, cos_Psi_square;

	if (polarization == S)
	{
		for (i = 0; i < T->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_e->N[i]*N_e->N[i];
			N_e_s = sqrt(N_square - sin2_theta_0->sin2[i]);

			T->data[i] = (real(N_e_s)/real(N_i_s)) * norm(r_and_t->t_s[i]);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < T->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_e->N[i]*N_e->N[i];
			N_e_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);

			T->data[i] = (real(N_e_p)/real(N_i_p)) * norm(r_and_t->t_p[i]);
		}
	}
	else
	{
		Psi = polarization*M_PI/180.0;
		sin_Psi = sin(Psi);
		sin_Psi_square = sin_Psi*sin_Psi;
		cos_Psi_square = 1.0-sin_Psi_square;
		for (i = 0; i < T->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_i_p = N_square/N_i_s;
			N_square = N_e->N[i]*N_e->N[i];
			N_e_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_e_p = N_square/N_e_s;

			T->data[i] = ((real(N_e_s)/real(N_i_s)) * norm(r_and_t->t_s[i])) * sin_Psi_square\
			           + ((real(N_e_p)/real(N_i_p)) * norm(r_and_t->t_p[i])) * cos_Psi_square;
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_R_with_backside                                         */
/*                                                                   */
/* Calculate reflectance with consideration of the backside          */
/*                                                                   */
/* This function takes 9 arguments:                                  */
/*   R                 the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   R_front           the reflectance of the front side;            */
/*   T_front_reverse   the transmittance of the front side in        */
/*                     reverse direction;                            */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   R_back            the reflectance of the back side;             */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/*********************************************************************/
void calculate_R_with_backside(const spectrum_type *R, const spectrum_type *T_front, const spectrum_type *R_front, const spectrum_type *T_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag, exp_4_beta_imag;
	long														i;

	for (i = 0; i < R->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/R->wvls->wvls[i]);
		exp_4_beta_imag = exp(4.0*beta_imag);

		R->data[i] = R_front->data[i] + ((T_front->data[i]*T_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag)/(1.0-R_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag));
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_T_with_backside                                         */
/*                                                                   */
/* Calculate transmittance with consideration of the backside        */
/*                                                                   */
/* This function takes 8 arguments:                                  */
/*   T                 the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   T_back            the transmittance of the back side;           */
/*   R_back            the reflectance of the back side;             */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/*********************************************************************/
void calculate_T_with_backside(const spectrum_type *T, const spectrum_type *T_front, const spectrum_type *R_front_reverse, const spectrum_type *T_back, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag;
	long														i;

	for (i = 0; i < T->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/T->wvls->wvls[i]);

		T->data[i] = (T_front->data[i]*T_back->data[i]*exp(2.0*beta_imag))/(1.0-R_back->data[i]*R_front_reverse->data[i]*exp(4.0*beta_imag));
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_A                                                       */
/*                                                                   */
/* Calculate absorptance from the reflectance and the transmittance  */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   A                 the structure in which to store the results;  */
/*   R                 the reflectance of the filter;                */
/*   T                 the transmittance of the filter.              */
/*                                                                   */
/*********************************************************************/
void calculate_A(const spectrum_type *A, const spectrum_type *R, const spectrum_type *T)
{
	long														i;

	for (i = 0; i < A->wvls->length; i++)
		A->data[i] = 1.0 - R->data[i] - T->data[i];
}


#ifdef __cplusplus
}
#endif
