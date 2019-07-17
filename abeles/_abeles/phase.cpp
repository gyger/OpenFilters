/*
 *
 *  phase.cpp
 *
 *
 *  Functions to calculate the phase of the reflected or transmitted
 *  light from Abeles matrices.
 *
 *  Copyright (c) 2005-2008,2012,2013,2016 Stephane Larouche.
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


void _calculate_GD(const spectrum_type *GD, const spectrum_type *phase, const bool unwrap);
void _calculate_GDD(const spectrum_type *GDD, const spectrum_type *phase, const bool unwrap);


static const double two_pi = 2.0*M_PI;

/* The speed of light in nm/s. */
static const double c = 299792458.0 * 1e9;
static const double two_pi_c = two_pi*c;


/*********************************************************************/
/*                                                                   */
/* Newton_quadratic                                                  */
/*                                                                   */
/* Get the quadratic polynomial passing by 3 points using Newton's   */
/*	method.                                                          */
/*                                                                   */
/* The function takes three arguments:                               */
/*   X and Y                  lists containing x and y values;       */
/*   a                        a list to return the parameters of the */
/*                            equation;                              */
/* and returns no argument.                                          */
/*                                                                   */
/*********************************************************************/
static void Newton_quadratic(const double *X, const double *Y, double *a)
{
	double													f_01, f_12;
	double													f_012;

	f_01 = (Y[1]-Y[0]) / (X[1]-X[0]);
	f_12 = (Y[2]-Y[1]) / (X[2]-X[1]);
	f_012 = (f_12-f_01) / (X[2]-X[0]);

	a[0] = Y[0] - f_01*X[0] + f_012*X[0]*X[1];
	a[1] = f_01 - f_012*(X[0]+X[1]);
	a[2] = f_012;
}


/*********************************************************************/
/*                                                                   */
/* calculate_r_phase                                                 */
/*                                                                   */
/* Calculate the phase shift upon reflection                         */
/*                                                                   */
/* This function takes 6 arguments:                                  */
/*   phase             the structure in which to store the results;  */
/*   M                 the characteristic matrices of the stack;     */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_r_phase(const spectrum_type *phase, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						B, C, B_conj, C_conj;
	double													numerator, denominator;
	long														i;

	/* atan2 fails if both arguments are 0, consider the phase to be 0,
	 * this is usually acceptable. */

	if (polarization == S)
	{
		for (i = 0; i < phase->wvls->length; i++)
		{
			N_square = N_m->N[i]*N_m->N[i];
			N_m_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_s->N[i]*N_s->N[i];
			N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_m_s) == 0.0)
				N_m_s = -N_m_s;
			if (real(N_s_s) == 0.0)
				N_s_s = -N_s_s;

			/* Admittance of s polarisation. */
			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;
			C = M->matrices[i].s[2] + M->matrices[i].s[3]*N_s_s;
			B_conj = conj(B);
			C_conj = conj(C);

			/* s reflection phase. */
			numerator = imag(N_m_s*(B*C_conj-C*B_conj));
			denominator = real(N_m_s*N_m_s*B*B_conj-C*C_conj);
			if (numerator == 0.0 && denominator == 0.0)
				phase->data[i] = 0.0;
			else
				phase->data[i] = atan2(numerator, denominator);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < phase->wvls->length; i++)
		{
			N_square = N_m->N[i]*N_m->N[i];
			N_m_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_s->N[i]*N_s->N[i];
			N_s_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_m_p) == 0.0)
				N_m_p = -N_m_p;
			if (real(N_s_p) == 0.0)
				N_s_p = -N_s_p;

			/* Admittance of p polarisation. */
			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;
			C = M->matrices[i].p[2] + M->matrices[i].p[3]*N_s_p;
			B_conj = conj(B);
			C_conj = conj(C);

			/* p reflection phase. */
			numerator = imag(N_m_p*(B*C_conj-C*B_conj));
			denominator = real(N_m_p*N_m_p*B*B_conj-C*C_conj);
			if (numerator == 0.0 && denominator == 0.0)
				phase->data[i] = 0.0;
			else
				phase->data[i] = atan2(numerator, denominator);
		}
	}

	/* Put the range between 0 and 2 pi. */
	for (i = 0; i < phase->wvls->length; i++)
		if (phase->data[i] < 0.0)
			phase->data[i] += two_pi;
}


/*********************************************************************/
/*                                                                   */
/* calculate_t_phase                                                 */
/*                                                                   */
/* Calculate the phase shift upon transmission                       */
/*                                                                   */
/* This function takes 6 arguments:                                  */
/*   phase             the structure in which to store the results;  */
/*   M                 the characteristic matrices of the stack;     */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_t_phase(const spectrum_type *phase, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						B, C;
	std::complex<double>						temp;
	double													numerator, denominator;
	long														i;

	/* atan2 fails if both arguments are 0, consider the phase to be 0,
	 * this is usually acceptable. */

	if (polarization == S)
	{
		for (i = 0; i < phase->wvls->length; i++)
		{
			N_square = N_m->N[i]*N_m->N[i];
			N_m_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_s->N[i]*N_s->N[i];
			N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_m_s) == 0.0)
				N_m_s = -N_m_s;
			if (real(N_s_s) == 0.0)
				N_s_s = -N_s_s;

			/* Admittance of s polarisation. */
			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;
			C = M->matrices[i].s[2] + M->matrices[i].s[3]*N_s_s;

			/* s transmission phase. */
			temp = N_m_s*B+C;
			numerator = -imag(temp);
			denominator = real(temp);
			if (numerator == 0.0 && denominator == 0.0)
				phase->data[i] = 0.0;
			else
				phase->data[i] = atan2(numerator, denominator);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < phase->wvls->length; i++)
		{
			N_square = N_m->N[i]*N_m->N[i];
			N_m_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_s->N[i]*N_s->N[i];
			N_s_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);

			/* Correct branch selection. */
			if (real(N_m_p) == 0.0)
				N_m_p = -N_m_p;
			if (real(N_s_p) == 0.0)
				N_s_p = -N_s_p;

			/* Admittance of p polarisation. */
			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;
			C = M->matrices[i].p[2] + M->matrices[i].p[3]*N_s_p;

			/* p transmission phase. */
			temp = N_m_p*B+C;
			numerator = -imag(temp);
			denominator = real(temp);
			if (numerator == 0.0 && denominator == 0.0)
				phase->data[i] = 0.0;
			else
				phase->data[i] = atan2(numerator, denominator);
		}
	}

	/* Put the range between 0 and 2 pi. */
	for (i = 0; i < phase->wvls->length; i++)
		if (phase->data[i] < 0.0)
			phase->data[i] += two_pi;

}


/*********************************************************************/
/*                                                                   */
/* calculate_GD                                                      */
/*                                                                   */
/* Calculate the group delay                                         */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   GD                the structure in which to store the results;  */
/*   phase             the phase shift of the filter.                */
/*                                                                   */
/* The group delay is determined from the numerical first derivative */
/* of the phase shift with regard to angular frequency.              */
/*                                                                   */
/*********************************************************************/
void calculate_GD(const spectrum_type *GD, const spectrum_type *phase)
{
	_calculate_GD(GD, phase, true);
}


/*********************************************************************/
/*                                                                   */
/* _calculate_GD                                                     */
/*                                                                   */
/* Calculate the group delay                                         */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   GD                the structure in which to store the results;  */
/*   phase             the phase shift of the filter;                */
/*   unwrap            a boolean indicating if the values of phase   */
/*                     should be unwrapped allowing to use this      */
/*                     funtion to calculate both the group delay     */
/*                     (where is should be unwrapped) and its        */
/*                     derivative (where it should not).             */
/*                                                                   */
/* The group delay is determined from the numerical first derivative */
/* of the phase shift with regard to angular frequency.              */
/*                                                                   */
/*********************************************************************/
void _calculate_GD(const spectrum_type *GD, const spectrum_type *phase, const bool unwrap)
{
	long														i;
	double													*omega;
	double													y[3];
	double													a[3];

	/* Create a vector for the angular frequency. */
	omega = (double *)malloc(GD->wvls->length*sizeof(double));

	/* Calculate the angular frequency. */
	for (i = 0; i < GD->wvls->length; i++)
		omega[i] = two_pi_c / GD->wvls->wvls[i];

	/* Since we cannot identify the absolute value of the phase but only
	 * its residue when divided by 2 pi, we choose the difference that
	 * gives the smallest GD. This is reasonable since the phase should
	 * not change too rapidly with the wavelength. If errors occurs, the
	 * user should increase the number of points. */

	/* To calculate the GD for the first point, we fit a polynomial on
	 * the first three points giving a results similar to forward
	 * difference. */
	y[0] = phase->data[0];
	y[1] = phase->data[1];
	y[2] = phase->data[2];
	if (unwrap)
	{
		if (y[1]-y[0] > M_PI) y[1] -= two_pi;
		else if (y[1]-y[0] < -M_PI) y[1] += two_pi;
		if (y[2]-y[1] > M_PI) y[2] -= two_pi;
		else if (y[2]-y[1] < -M_PI) y[2] += two_pi;
	}
	Newton_quadratic(omega, y, a);
	GD->data[0] = -(a[1] + 2.0*a[2]*omega[0]);

	/* To calculate the GD for the second point, we reuse the same
	 * polynomial now giving a formula similar to centered difference. */
	GD->data[1] = -(a[1] + 2.0*a[2]*omega[1]);

	/* To calculate the GD for the third to second to last points, we use
	 * polynomials centered on these points. */
	for (i = 2; i < GD->wvls->length-1; i++)
	{
		y[0] = phase->data[i-1];
		y[1] = phase->data[i];
		y[2] = phase->data[i+1];
		if (unwrap)
		{
			if (y[1]-y[0] > M_PI) y[1] -= two_pi;
			else if (y[1]-y[0] < -M_PI) y[1] += two_pi;
			if (y[2]-y[1] > M_PI) y[2] -= two_pi;
			else if (y[2]-y[1] < -M_PI) y[2] += two_pi;
		}
		Newton_quadratic(&(omega[i-1]), y, a);
		GD->data[i] = -(a[1] + 2.0*a[2]*omega[i]);
	}

	/* To calculate the GD for the last point, we reuse the polynomial
	 * used for the second to last point, now giving a formula similar
	 * to backward difference. */
	GD->data[GD->wvls->length-1] = -(a[1] + 2.0*a[2]*omega[GD->wvls->length-1]);

	/* Free the angular frequency vector. */
	free(omega);
}


/*********************************************************************/
/*                                                                   */
/* calculate_GDD                                                     */
/*                                                                   */
/* Calculate the group delay dispersion                              */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   GDD               the structure in which to store the results;  */
/*   phase             the phase shift of the filter.                */
/*                                                                   */
/* The group delay dispersion is determined from the numerical       */
/* second derivative of the phase shift with regard to angular       */
/* frequency.                                                        */
/*                                                                   */
/*********************************************************************/
void calculate_GDD(const spectrum_type *GDD, const spectrum_type *phase)
{
	_calculate_GDD(GDD, phase, true);
}


/*********************************************************************/
/*                                                                   */
/* _calculate_GDD                                                    */
/*                                                                   */
/* Calculate the group delay dispersion                              */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   GDD               the structure in which to store the results;  */
/*   phase             the phase shift of the filter.                */
/*   unwrap            a boolean indicating if the values of phase   */
/*                     should be unwrapped allowing to use this      */
/*                     funtion to calculate both the group delay     */
/*                     dispersion (where is should be unwrapped)     */
/*                     and its derivative (where it should not).     */
/*                                                                   */
/* The group delay dispersion is determined from the numerical       */
/* second derivative of the phase shift with regard to angular       */
/* frequency.                                                        */
/*                                                                   */
/*********************************************************************/
void _calculate_GDD(const spectrum_type *GDD, const spectrum_type *phase, const bool unwrap)
{
	long														i;
	double													*omega;
	double													y[3];
	double													a[3];

	/* Create a vector for the wavenumbers. */
	omega = (double *)malloc(GDD->wvls->length*sizeof(double));

	/* Calculate the wavenumbers. */
	for (i = 0; i < GDD->wvls->length; i++)
		omega[i] = two_pi_c / GDD->wvls->wvls[i];

	/* Since we cannot identify the absolute value of the phase but only
	 * its residue when divided by 2 pi, we choose the difference that
	 * gives the smallest GDD. This is reasonable since the phase should
	 * not change too rapidly with the wavelength. If errors occurs, the
	 * user should increase the number of points. */

	/* To calculate the GDD for the first point, we fit a polynomial on
	 * the first three points giving a results similar to forward
	 * difference. */
	y[0] = phase->data[0];
	y[1] = phase->data[1];
	y[2] = phase->data[2];
	if (unwrap)
	{
		if (y[1]-y[0] > M_PI) y[1] -= two_pi;
		else if (y[1]-y[0] < -M_PI) y[1] += two_pi;
		if (y[2]-y[1] > M_PI) y[2] -= two_pi;
		else if (y[2]-y[1] < -M_PI) y[2] += two_pi;
	}
	Newton_quadratic(omega, y, a);
	GDD->data[0] = -2.0*a[2];

	/* To calculate the GDD for the second point, we reuse the same
	 * polynomial now giving a formula similar to centered difference. */
	GDD->data[1] = -2.0*a[2];

	/* To calculate the GDD for the third to second to last points, we use
	 * polynomials centered on these points. */
	for (i = 2; i < GDD->wvls->length-1; i++)
	{
		y[0] = phase->data[i-1];
		y[1] = phase->data[i];
		y[2] = phase->data[i+1];
		if (unwrap)
		{
			if (y[1]-y[0] > M_PI) y[1] -= two_pi;
			else if (y[1]-y[0] < -M_PI) y[1] += two_pi;
			if (y[2]-y[1] > M_PI) y[2] -= two_pi;
			else if (y[2]-y[1] < -M_PI) y[2] += two_pi;
		}
		Newton_quadratic(&(omega[i-1]), y, a);
		GDD->data[i] = -2.0*a[2];
	}

	/* To calculate the GDD for the last point, we reuse the polynomial
	 * used for the second to last point, now giving a formula similar
	 * to backward difference. */
	GDD->data[GDD->wvls->length-1] = -2.0*a[2];

	/* Free the wavenumber vector. */
	free(omega);
}


#ifdef __cplusplus
}
#endif
