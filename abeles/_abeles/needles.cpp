/*
 *
 *  needles.cpp
 *
 *
 *  Functions to calculate the derivative of the Abeles matrices upon
 *  the addition of needles or steps.
 *
 *  Copyright (c) 2005-2009,2012,2013 Stephane Larouche.
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


static const std::complex<double> j = std::complex<double>(0.0, 1.0);


#ifdef __cplusplus
extern "C" {
#endif


static const double two_pi = 2.0*M_PI;


/*********************************************************************/
/*                                                                   */
/* new_needle_matrices                                               */
/*                                                                   */
/* Create a structure to store the derivatives of the characteristic */
/* matrices used in the needle method                                */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   wvls              the wavelengths at which to calculate the     */
/*                     derivatives;                                  */
/*   length            the number of positions;                      */
/* and returns a needle matrix structure.                            */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/* When using the needle method, one needs to calculate the          */
/* derivative of the characteristic matrices of a layer as a         */
/* of the position where the needle is added. The needle matrix      */
/* structure allows to store all the derivatives of the              */
/* characteristic matrices at multiple positions in a layer.         */
/*                                                                   */
/*********************************************************************/
needle_matrices_type * new_needle_matrices(const wvls_type *wvls, const long length)
{
	needle_matrices_type						*M;
	long														i;

	M = (needle_matrices_type *)malloc(sizeof(needle_matrices_type));

	if (!M) return NULL;

	M->length = length;
	M->wvls = wvls;
	M->positions = (double *)malloc(M->length*sizeof(double));
	M->M = (matrices_type **)malloc(M->length*sizeof(matrices_type *));

	if (!M->positions || !M->M)
	{
		del_needle_matrices(M);
		return NULL;
	}

	for (i = 0; i < M->length; i++)
		M->M[i] = new_matrices(M->wvls);

	for (i = 0; i < M->length; i++)
	{
		if (!M->M[i])
		{
			del_needle_matrices(M);
			return NULL;
		}
	}

	return M;
}


/*********************************************************************/
/*                                                                   */
/* del_needle_matrices                                               */
/*                                                                   */
/* Delete a needle matrix structure                                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_needle_matrices(needle_matrices_type *M)
{
	long														i;

	if (!M) return;

	if (M->M)
		for (i = 0; i < M->length; i++)
			del_matrices(M->M[i]);

	free(M->M);
	free(M->positions);

	free(M);
}


/*********************************************************************/
/*                                                                   */
/* set_needle_position                                               */
/*                                                                   */
/* Set the position of one needle in a needle matrix structure       */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   M                 the needle matrix structure;                  */
/*   i_needle          the number of the needle;                     */
/*   position          its position (with regard to the buttom of    */
/*                     the layer).                                   */
/*                                                                   */
/*********************************************************************/
void set_needle_position(const needle_matrices_type *M, const long i_needle, const double position)
{
	M->positions[i_needle] = position;
}


/*********************************************************************/
/*                                                                   */
/* set_needle_positions                                              */
/*                                                                   */
/* Set the positions of all needles in a needle matrix structure     */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M                 the needle matrix structure;                  */
/*   spacing           the spacing between needles.                  */
/*                                                                   */
/* The first needle is located at 0 and the needles are equally      */
/* seperated of spacing.                                             */
/*                                                                   */
/*********************************************************************/
void set_needle_positions(const needle_matrices_type *M, const double spacing)
{
	long														i_needle;

	for (i_needle = 0; i_needle < M->length; i_needle++)
		M->positions[i_needle] = i_needle*spacing;
}


/*********************************************************************/
/*                                                                   */
/* get_needle_position                                               */
/*                                                                   */
/* Get the position of one needle in a needle matrix structure       */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M                 the needle matrix structure;                  */
/*   i_needle          the number of the needle.                     */
/* and returns the position of the needle.                           */
/*                                                                   */
/*********************************************************************/
double get_needle_position(const needle_matrices_type *M, const long i_needle)
{
	return M->positions[i_needle];
}


/*********************************************************************/
/*                                                                   */
/* get_one_needle_matrices                                           */
/*                                                                   */
/* Get the matrices of one needle in a needle matrix structure       */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M                 the needle matrix structure;                  */
/*   i_needle          the number of the needle.                     */
/* and returns the matrices representing the needle.                 */
/*                                                                   */
/*********************************************************************/
matrices_type * get_one_needle_matrices(const needle_matrices_type *M, const long i_needle)
{
	return M->M[i_needle];
}


/*********************************************************************/
/*                                                                   */
/* calculate_dMi_needles                                             */
/*                                                                   */
/* Calculate the derivative of the characteristic matrix with regard */
/* to the addition of a needle as a function of its position         */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   dMi               the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   N_n               the index of refraction of the needle;        */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/* This function calculates the derivative of the characteristic     */
/* matrix at the positions already set in the needle matrix          */
/* structure.                                                        */
/*                                                                   */
/*********************************************************************/
void calculate_dMi_needles(const needle_matrices_type *dMi, const N_type *N, const N_type *N_n, const double thickness, const sin2_type *sin2_theta_0)
{
	long														i_wvl, i_pos;
	double													k;
	std::complex<double>						N_square, N_s, N_p;
	std::complex<double>						N_n_square, N_n_s, N_n_p;
	std::complex<double>						phi, d_phi, j_cos_phi;
	std::complex<double>						delta_phi, j_cos_delta_phi;
	std::complex<double>						sum_ratio_s, diff_ratio_s, sum_ratio_p, diff_ratio_p;
	matrix_type											dM_phi, dM_delta_phi;

	/* For details and demonstration, see:
	 *   Stephane Larouche, Derivatives of the optical properties of
	 *   interference filters, 2005. */

	for (i_wvl = 0; i_wvl < dMi->wvls->length; i_wvl++)
	{
		k = two_pi/dMi->wvls->wvls[i_wvl];

		N_square = N->N[i_wvl]*N->N[i_wvl];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i_wvl]);
		N_p = N_square/N_s;

		N_n_square = N_n->N[i_wvl]*N_n->N[i_wvl];
		N_n_s = sqrt(N_n_square-sin2_theta_0->sin2[i_wvl]);
		N_n_p = N_n_square/N_n_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}
		if (real(N_n_s) == 0.0)
		{
			N_n_s = -N_n_s;
			N_n_p = -N_n_p;
		}

		phi = k*N_s*thickness;
		j_cos_phi = j*cos(phi);

		d_phi = k*N_n_s;

		sum_ratio_s  = 0.5 * (N_s/N_n_s + N_n_s/N_s);
		diff_ratio_s = 0.5 * (N_s/N_n_s - N_n_s/N_s);
		sum_ratio_p  = 0.5 * (N_p/N_n_p + N_n_p/N_p);
		diff_ratio_p = 0.5 * (N_p/N_n_p - N_n_p/N_p);

		/* Calculate the constant part of dMi. */
		dM_phi.s[0] = dM_phi.s[3] = dM_phi.p[0] = dM_phi.p[3] = -sin(phi);
		dM_phi.s[1] = j_cos_phi/N_s;
		dM_phi.p[1] = j_cos_phi/N_p;
		dM_phi.s[2] = N_s*j_cos_phi;
		dM_phi.p[2] = N_p*j_cos_phi;

		for (i_pos = 0; i_pos < dMi->length; i_pos++)
		{
			delta_phi = k*N_s*(2.0*dMi->positions[i_pos] - thickness);
			j_cos_delta_phi = j*cos(delta_phi);

			/* Calculate the variable part of dMi. */
			dM_delta_phi.s[0] = dM_delta_phi.s[3] = dM_delta_phi.p[0] = dM_delta_phi.p[3] = -sin(delta_phi);
			dM_delta_phi.s[1] = j_cos_delta_phi/N_s;
			dM_delta_phi.p[1] = j_cos_delta_phi/N_p;
			dM_delta_phi.s[2] = N_s*j_cos_delta_phi;
			dM_delta_phi.p[2] = N_p*j_cos_delta_phi;

			/* Add the constant and variable parts. */
			dMi->M[i_pos]->matrices[i_wvl].s[0] = (sum_ratio_s*dM_phi.s[0] + diff_ratio_s*dM_delta_phi.s[0]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].s[1] = (sum_ratio_s*dM_phi.s[1] + diff_ratio_s*dM_delta_phi.s[1]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].s[2] = (sum_ratio_s*dM_phi.s[2] - diff_ratio_s*dM_delta_phi.s[2]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].s[3] = (sum_ratio_s*dM_phi.s[3] - diff_ratio_s*dM_delta_phi.s[3]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].p[0] = (sum_ratio_p*dM_phi.p[0] + diff_ratio_p*dM_delta_phi.p[0]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].p[1] = (sum_ratio_p*dM_phi.p[1] + diff_ratio_p*dM_delta_phi.p[1]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].p[2] = (sum_ratio_p*dM_phi.p[2] - diff_ratio_p*dM_delta_phi.p[2]) * d_phi;
			dMi->M[i_pos]->matrices[i_wvl].p[3] = (sum_ratio_p*dM_phi.p[3] - diff_ratio_p*dM_delta_phi.p[3]) * d_phi;
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dMi_needles_fast                                        */
/*                                                                   */
/* Calculate the derivative of the characteristic matrix with regard */
/* to the addition of a needle as a function of its position and     */
/* multiple materials                                                */
/*                                                                   */
/* This function takes 6 arguments:                                  */
/*   dMi               a list structures in which to store the       */
/*                     results;                                      */
/*   N                 the index of refraction of the layer;         */
/*   N_n               a list possible index of refraction of the    */
/*                     needle;                                       */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   length            the number of materials considered.           */
/*                                                                   */
/* Some elements of the calculation of the derivative of the         */
/* characteristic matrix with regard to the addition of a needle     */
/* do not depend on the needle material. It is therefore posssible   */
/* to speed up the calculation by calculating the derivative for     */
/* multiple materials at once. To work, this function supposes       */
/* (without verifying it) that the position of the needles are the   */
/* same in all the needle matrix structures it receives.             */
/*                                                                   */
/*********************************************************************/
void calculate_dMi_needles_fast(const needle_matrices_type **dMi, const N_type *N, const N_type **N_n, const double thickness, const sin2_type *sin2_theta_0, const long length)
{
	long														i_wvl, i_pos, i_mat;
	double													k;
	std::complex<double>						N_square, N_s, N_p;
	std::complex<double>						N_n_square, N_n_s, N_n_p;
	std::complex<double>						phi, *d_phi, j_cos_phi;
	std::complex<double>						delta_phi, j_cos_delta_phi;
	std::complex<double>						*sum_ratio_s, *diff_ratio_s, *sum_ratio_p, *diff_ratio_p;
	matrix_type											dM_phi, dM_delta_phi;

	/* This function calculates dMi for needles for multiple materials at
	 * once to accelerate calculations. */

	/* For details and demonstration, see:
	 *   Stephane Larouche, Derivatives of the optical properties of
	 *   interference filters, 2005. */

	d_phi = (std::complex<double> *)malloc(length*sizeof(std::complex<double>));
	sum_ratio_s  = (std::complex<double> *)malloc(length*sizeof(std::complex<double>));
	diff_ratio_s = (std::complex<double> *)malloc(length*sizeof(std::complex<double>));
	sum_ratio_p  = (std::complex<double> *)malloc(length*sizeof(std::complex<double>));
	diff_ratio_p = (std::complex<double> *)malloc(length*sizeof(std::complex<double>));

	for (i_wvl = 0; i_wvl < dMi[0]->wvls->length; i_wvl++)
	{
		k = two_pi/dMi[0]->wvls->wvls[i_wvl];

		N_square = N->N[i_wvl]*N->N[i_wvl];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i_wvl]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		phi = k*N_s*thickness;
		j_cos_phi = j*cos(phi);

		/* Calculate the sum and difference of ratios for all the needle
		 * materials at once. */
		for (i_mat = 0; i_mat < length; i_mat++)
		{
			N_n_square = N_n[i_mat]->N[i_wvl]*N_n[i_mat]->N[i_wvl];
			N_n_s = sqrt(N_n_square-sin2_theta_0->sin2[i_wvl]);
			N_n_p = N_n_square/N_n_s;

			/* Correct branch selection. */
			if (real(N_n_s) == 0.0)
			{
				N_n_s = -N_n_s;
				N_n_p = -N_n_p;
			}

			d_phi[i_mat] = k*N_n_s;

			sum_ratio_s[i_mat]  = 0.5 * (N_s/N_n_s + N_n_s/N_s);
			diff_ratio_s[i_mat] = 0.5 * (N_s/N_n_s - N_n_s/N_s);
			sum_ratio_p[i_mat]  = 0.5 * (N_p/N_n_p + N_n_p/N_p);
			diff_ratio_p[i_mat] = 0.5 * (N_p/N_n_p - N_n_p/N_p);
		}

		/* Calculate the constant part of dMi. */
		dM_phi.s[0] = dM_phi.s[3] = dM_phi.p[0] = dM_phi.p[3] = -sin(phi);
		dM_phi.s[1] = j_cos_phi/N_s;
		dM_phi.p[1] = j_cos_phi/N_p;
		dM_phi.s[2] = N_s*j_cos_phi;
		dM_phi.p[2] = N_p*j_cos_phi;

		for (i_pos = 0; i_pos < dMi[0]->length; i_pos++)
		{
			delta_phi = k*N_s*(2.0*dMi[0]->positions[i_pos] - thickness);
			j_cos_delta_phi = j*cos(delta_phi);

			/* Calculate the variable part of dMi. */
			dM_delta_phi.s[0] = dM_delta_phi.s[3] = dM_delta_phi.p[0] = dM_delta_phi.p[3] = -sin(delta_phi);
			dM_delta_phi.s[1] = j_cos_delta_phi/N_s;
			dM_delta_phi.p[1] = j_cos_delta_phi/N_p;
			dM_delta_phi.s[2] = N_s*j_cos_delta_phi;
			dM_delta_phi.p[2] = N_p*j_cos_delta_phi;

			/* Add the constant and variable parts for all materials. */
			for (i_mat = 0; i_mat < length; i_mat++)
			{
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].s[0] = (sum_ratio_s[i_mat]*dM_phi.s[0] + diff_ratio_s[i_mat]*dM_delta_phi.s[0]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].s[1] = (sum_ratio_s[i_mat]*dM_phi.s[1] + diff_ratio_s[i_mat]*dM_delta_phi.s[1]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].s[2] = (sum_ratio_s[i_mat]*dM_phi.s[2] - diff_ratio_s[i_mat]*dM_delta_phi.s[2]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].s[3] = (sum_ratio_s[i_mat]*dM_phi.s[3] - diff_ratio_s[i_mat]*dM_delta_phi.s[3]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].p[0] = (sum_ratio_p[i_mat]*dM_phi.p[0] + diff_ratio_p[i_mat]*dM_delta_phi.p[0]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].p[1] = (sum_ratio_p[i_mat]*dM_phi.p[1] + diff_ratio_p[i_mat]*dM_delta_phi.p[1]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].p[2] = (sum_ratio_p[i_mat]*dM_phi.p[2] - diff_ratio_p[i_mat]*dM_delta_phi.p[2]) * d_phi[i_mat];
				dMi[i_mat]->M[i_pos]->matrices[i_wvl].p[3] = (sum_ratio_p[i_mat]*dM_phi.p[3] - diff_ratio_p[i_mat]*dM_delta_phi.p[3]) * d_phi[i_mat];
			}
		}
	}

	free(d_phi);
	free(sum_ratio_s);
	free(diff_ratio_s);
	free(sum_ratio_p);
	free(diff_ratio_p);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dMi_steps                                               */
/*                                                                   */
/* Calculate the derivative of the characteristic matrix with regard */
/* to the addition of a step as a function of its position           */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   dMi               the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   dN                the derivative of the index of refraction of  */
/*                     the layer;                                    */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/* This function calculates the derivative of the characteristic     */
/* matrix at the position already set in the needle matrix           */
/* structure.                                                        */
/*                                                                   */
/*********************************************************************/
void calculate_dMi_steps(const needle_matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0)
{
	long														i_wvl, i_pos;
	double													k;
	std::complex<double>						N_square, N_s, N_p;
	std::complex<double>						d_N_s, d_N_p;
	std::complex<double>						inverse_N_s, inverse_N_p;
	std::complex<double>						phi, cos_phi, j_cos_phi;
	double													k_delta_thickness;
	std::complex<double>						delta_phi, j_sin_delta_phi, d_delta_phi;
	matrix_type											dM_phi, M_delta_phi;

	/* For details and demonstration, see:
	 *   Stephane Larouche, Derivatives of the optical properties of
	 *   interference filters, 2006. */

	for (i_wvl = 0; i_wvl < dMi->wvls->length; i_wvl++)
	{
		k = two_pi/dMi->wvls->wvls[i_wvl];

		N_square = N->N[i_wvl]*N->N[i_wvl];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i_wvl]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		d_N_s = N->N[i_wvl]/N_s;
		d_N_p = d_N_s * (2.0 - d_N_s*d_N_s);
		inverse_N_s = 1.0/N_s;
		inverse_N_p = 1.0/N_p;
		phi = k*N_s*thickness;
		cos_phi = cos(phi);
		j_cos_phi = j*cos_phi;

		/* Calculate the constant parts of dMi. */
		dM_phi.s[0] = dM_phi.s[3] = dM_phi.p[0] = dM_phi.p[3] = -sin(phi);
		dM_phi.s[1] = j_cos_phi/N_s;
		dM_phi.p[1] = j_cos_phi/N_p;
		dM_phi.s[2] = N_s*j_cos_phi;
		dM_phi.p[2] = N_p*j_cos_phi;

		for (i_pos = 0; i_pos < dMi->length; i_pos++)
		{
			/********** Why do I have to put a minus sign here!? **********/
			k_delta_thickness = -k*(2.0*dMi->positions[i_pos] - thickness);
			delta_phi = N_s*k_delta_thickness;
			d_delta_phi = d_N_s*k_delta_thickness;
			j_sin_delta_phi = j*sin(delta_phi);

			/* Calculate the variable part of dMi. */
			M_delta_phi.s[0] = M_delta_phi.p[0] = M_delta_phi.s[3] = M_delta_phi.p[3] = cos(delta_phi);
			M_delta_phi.s[1] = j_sin_delta_phi/N_s;
			M_delta_phi.p[1] = j_sin_delta_phi/N_p;
			M_delta_phi.s[2] = N_s*j_sin_delta_phi;
			M_delta_phi.p[2] = N_p*j_sin_delta_phi;

			/* Calculate dMi for the constant and variable parts. */
			dMi->M[i_pos]->matrices[i_wvl].s[0] = 0.5 * (dM_phi.s[0]*d_delta_phi + inverse_N_s*(M_delta_phi.s[0]-cos_phi)*d_N_s) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].s[1] = 0.5 * (dM_phi.s[1]*d_delta_phi - inverse_N_s*(M_delta_phi.s[1]        )*d_N_s) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].s[2] = 0.5 * (dM_phi.s[2]*d_delta_phi + inverse_N_s*(M_delta_phi.s[2]        )*d_N_s) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].s[3] = 0.5 * (dM_phi.s[3]*d_delta_phi - inverse_N_s*(M_delta_phi.s[3]-cos_phi)*d_N_s) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].p[0] = 0.5 * (dM_phi.p[0]*d_delta_phi + inverse_N_p*(M_delta_phi.p[0]-cos_phi)*d_N_p) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].p[1] = 0.5 * (dM_phi.p[1]*d_delta_phi - inverse_N_p*(M_delta_phi.p[1]        )*d_N_p) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].p[2] = 0.5 * (dM_phi.p[2]*d_delta_phi + inverse_N_p*(M_delta_phi.p[2]        )*d_N_p) * dN->N[i_wvl];
			dMi->M[i_pos]->matrices[i_wvl].p[3] = 0.5 * (dM_phi.p[3]*d_delta_phi - inverse_N_p*(M_delta_phi.p[3]-cos_phi)*d_N_p) * dN->N[i_wvl];
		}
	}
}


#ifdef __cplusplus
}
#endif
