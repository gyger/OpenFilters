/*
 *
 *  derivatives.cpp
 *
 *
 *  Functions to calculate the derivatives of various optical
 *  parameters (R, T, ...) with regard to the thickness or the index of
 *  refraction of the layers.
 *
 *  Copyright (c) 2004-2009,2012,2013,2016 Stephane Larouche.
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


const std::complex<double> j = std::complex<double>(0.0, 1.0);


#ifdef __cplusplus
extern "C" {
#endif


extern void _calculate_GD(const spectrum_type *GD, const spectrum_type *phase, const bool unwrap);
extern void _calculate_GDD(const spectrum_type *GDD, const spectrum_type *phase, const bool unwrap);


const double two_pi = 2.0*M_PI;



/*********************************************************************/
/*                                                                   */
/* new_pre_and_post_matrices                                         */
/*                                                                   */
/* Create a new structure to store pre and post matrices             */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   wvls              the wavelengths at which to calculate the     */
/*                     pre and post matrices;                        */
/*   length            the number of layers;                         */
/* and returns a pre_and_post_matrices structure.                    */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/* Pre and post matrices are the product of the caracteristic        */
/* matrices before and after a layer, which are used in the          */
/* calculation of derivatives. The pre and post matrix structure     */
/* stores all the individual layer matrices and all the pre and post */
/* matrices for a stack.                                             */
/*                                                                   */
/*********************************************************************/
pre_and_post_matrices_type * new_pre_and_post_matrices(const wvls_type *wvls, const long length)
{
	pre_and_post_matrices_type			*M;
	long														i;

	M = (pre_and_post_matrices_type *)malloc(sizeof(pre_and_post_matrices_type));

	if (!M) return NULL;

	M->wvls = wvls;
	M->length = length;
	M->M = new_matrices(M->wvls);
	M->Mi = (matrices_type **)malloc(M->length*sizeof(matrices_type *));
	M->pre_M = (matrices_type **)malloc(M->length*sizeof(matrices_type *));
	M->post_M = (matrices_type **)malloc(M->length*sizeof(matrices_type *));

	if (!M->M || !M->Mi || !M->pre_M || !M->post_M)
	{
		del_pre_and_post_matrices(M);
		return NULL;
	}

	/* Allocate the matrices and set the changed values all to 1. */
	for (i = 0; i < M->length; i++)
	{
		M->Mi[i] = new_matrices(M->wvls);
		M->pre_M[i] = new_matrices(M->wvls);
		M->post_M[i] = new_matrices(M->wvls);
	}

	for (i = 0; i < M->length; i++)
	{
		if (!M->Mi[i] || !M->pre_M[i] || !M->post_M[i])
		{
			del_pre_and_post_matrices(M);
			return NULL;
		}
	}

	return M;
}


/*********************************************************************/
/*                                                                   */
/* del_pre_and_post_matrices                                         */
/*                                                                   */
/* Delete a pre_and_post_matrices structure                          */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_pre_and_post_matrices(pre_and_post_matrices_type *M)
{
	long														i;

	if (!M) return;

	if (M->Mi)
		for (i = 0; i < M->length; i++)
			del_matrices(M->Mi[i]);
	if (M->pre_M)
		for (i = 0; i < M->length; i++)
			del_matrices(M->pre_M[i]);
	if (M->post_M)
		for (i = 0; i < M->length; i++)
			del_matrices(M->post_M[i]);

	del_matrices(M->M);
	free(M->Mi);
	free(M->pre_M);
	free(M->post_M);

	free(M);
}


/*********************************************************************/
/*                                                                   */
/* new_psi_matrices                                                  */
/*                                                                   */
/* Create a new psi_matrices structure to store the matrices used    */
/* when calculating the derivatives of amplitude reflection or       */
/* transmission.                                                     */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     psi matrices;                                 */
/* and returns a psi_matrices structure.                             */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
psi_matrices_type * new_psi_matrices(const wvls_type *wvls)
{
	psi_matrices_type								*psi;

	psi = (psi_matrices_type *)malloc(sizeof(psi_matrices_type));

	if (!psi) return NULL;

	psi->wvls = wvls;
	psi->psi_r = new_matrices(psi->wvls);
	psi->psi_t = new_matrices(psi->wvls);

	if (!psi->psi_r || !psi->psi_t)
	{
		del_psi_matrices(psi);
		return NULL;
	}

	return psi;
}


/*********************************************************************/
/*                                                                   */
/* del_psi_matrices                                                  */
/*                                                                   */
/* Delete a psi_matrices structure                                   */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   psi               the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_psi_matrices(psi_matrices_type *psi)
{
	if (!psi) return;

	del_matrices(psi->psi_r);
	del_matrices(psi->psi_t);

	free(psi);
}


/*********************************************************************/
/*                                                                   */
/* set_pre_and_post_matrices                                         */
/*                                                                   */
/* Set the characteristic matrix of a single layer in the pre and    */
/* post matrices structure                                           */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   M                 a pointer to the pre and post matrix          */
/*                     structure in which to store the matrices;     */
/*   layer_nb          the position of the layer whose matrices are  */
/*                     being set;                                    */
/*   N                 the index of refraction of the layer;         */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/*********************************************************************/
void set_pre_and_post_matrices(const pre_and_post_matrices_type *M, const long layer_nb, const N_type *N, const double thickness, const sin2_type *sin2_theta_0)
{
	set_matrices(M->Mi[layer_nb], N, thickness, sin2_theta_0);
}


/*********************************************************************/
/*                                                                   */
/* multiply_pre_and_post_matrices                                    */
/*                                                                   */
/* Multiply the layer characteristic matrices to determine all the   */
/* pre and post matrices of a stack                                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the pre and post matrices.                    */
/*                                                                   */
/* All the individual layer matrices must have been set before       */
/* calculating the pre and post matrices.                            */
/*                                                                   */
/*********************************************************************/
void multiply_pre_and_post_matrices(const pre_and_post_matrices_type *M)
{
	long														i;

	/* Calculate the global matrices and pre matrices. */
	set_matrices_unity(M->M);
	for (i = 0; i < M->length; i++)
	{
		/* For a layer i, the pre-matrice is the global matrix after the
		 * previous layer. */
		copy_matrices(M->M, M->pre_M[i]);

		multiply_matrices(M->M, M->Mi[i]);
	}

	/* The last layer has not layer after it. */
	set_matrices_unity(M->post_M[M->length-1]);

	/* For post-matrices, the multiplication must be made in reverse order. */
	for (i = M->length-2; i > -1; i--)
	{
		copy_matrices(M->Mi[i+1], M->post_M[i]);
		multiply_matrices(M->post_M[i], M->post_M[i+1]);
	}
}


/*********************************************************************/
/*                                                                   */
/* get_global_matrices                                               */
/*                                                                   */
/* Get the global matrices of the stack stored in a pre and post     */
/* matrix structure                                                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the pre and post matrices;                    */
/* and returns the global matrices of the stack.                     */
/*                                                                   */
/* The global matrices are calculated at the same moment than the    */
/* pre and post matrices, so they must have been calculated before   */
/* calling this function.                                            */
/*                                                                   */
/*********************************************************************/
matrices_type * get_global_matrices(const pre_and_post_matrices_type *M)
{
	matrices_type										*global_matrices;

	global_matrices = M->M;

	return global_matrices;
}


/*********************************************************************/
/*                                                                   */
/* get_layer_matrices                                                */
/*                                                                   */
/* Get the matrices of a layer stored in a pre and post matrix       */
/* structure                                                         */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M                 the pre and post matrix structure;            */
/*   layer_nb          the position of the layer;                    */
/* and returns the matrices of the layer.                            */
/*                                                                   */
/*********************************************************************/
matrices_type * get_layer_matrices(const pre_and_post_matrices_type *M, const long layer_nb)
{
	matrices_type										*layer_matrices;

	layer_matrices = M->Mi[layer_nb];

	return layer_matrices;
}


/*********************************************************************/
/*                                                                   */
/* set_dMi_thickness                                                 */
/*                                                                   */
/* Calculate the derivative of the characteristic matrices of a      */
/* layer with regard to its thickness                                */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   dMi               the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void set_dMi_thickness(const matrices_type *dMi, const N_type *N, const double thickness, const sin2_type *sin2_theta_0)
{
	long														i;
	double													k;
	std::complex<double>						N_square, N_s, N_p, dphi, phi, j_cos_phi_dphi;

	for (i = 0; i < dMi->wvls->length; i++)
	{
		k = two_pi/dMi->wvls->wvls[i];

		N_square = N->N[i]*N->N[i];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		dphi = k*N_s;
		phi = dphi*thickness;
		j_cos_phi_dphi = j*cos(phi)*dphi;

		dMi->matrices[i].s[0] = dMi->matrices[i].s[3] = dMi->matrices[i].p[0] = dMi->matrices[i].p[3] = -sin(phi)*dphi;
		dMi->matrices[i].s[1] = j_cos_phi_dphi/N_s;
		dMi->matrices[i].p[1] = j_cos_phi_dphi/N_p;
		dMi->matrices[i].s[2] = N_s*j_cos_phi_dphi;
		dMi->matrices[i].p[2] = N_p*j_cos_phi_dphi;
	}
}


/*********************************************************************/
/*                                                                   */
/* set_dMi_index                                                     */
/*                                                                   */
/* Calculate the derivative of the characteristic matrices of a      */
/* layer with regard to its index of refraction                      */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   dMi               the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   dN                the derivative of the index of refraction of  */
/*                     the layer;                                    */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/* The derivative of the index of refraction, dN, is with regard to  */
/* the real part of the index of refraction at the reference         */
/* wavelength and is calculated from the dispersion relation of the  */
/* mixture considered (see N_mixture).                               */
/*                                                                   */
/*********************************************************************/
void set_dMi_index(const matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0)
{
	long														i;
	double													k;
	std::complex<double>						N_square, N_s, N_p, phi;
	std::complex<double>						dN_s, dN_p, dphi;
	std::complex<double>						sin_phi, j_sin_phi_dN_s, j_sin_phi_dN_p, j_cos_phi_dphi;

	for (i = 0; i < dMi->wvls->length; i++)
	{
		k = two_pi/dMi->wvls->wvls[i];

		N_square = N->N[i]*N->N[i];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		phi = k*thickness*N_s;
		dN_s = N->N[i]/N_s;
		dN_p = dN_s * (2.0 - dN_s*dN_s);
		dphi = k*thickness*dN_s;
		sin_phi = sin(phi);
		j_sin_phi_dN_s = j*sin_phi*dN_s;
		j_sin_phi_dN_p = j*sin_phi*dN_p;
		j_cos_phi_dphi = j*cos(phi)*dphi;

		dMi->matrices[i].s[0] = dMi->matrices[i].s[3] = dMi->matrices[i].p[0] = dMi->matrices[i].p[3] = -sin_phi*dphi * dN->N[i];
		dMi->matrices[i].s[1] = (j_cos_phi_dphi/N_s - j_sin_phi_dN_s/(N_s*N_s)) * dN->N[i];
		dMi->matrices[i].p[1] = (j_cos_phi_dphi/N_p - j_sin_phi_dN_p/(N_p*N_p)) * dN->N[i];
		dMi->matrices[i].s[2] = (N_s*j_cos_phi_dphi + j_sin_phi_dN_s) * dN->N[i];
		dMi->matrices[i].p[2] = (N_p*j_cos_phi_dphi + j_sin_phi_dN_p) * dN->N[i];
	}
}


/*********************************************************************/
/*                                                                   */
/* set_dMi_index_with_constant_OT                                    */
/*                                                                   */
/* Calculate the derivative of the characteristic matrices of a      */
/* layer with regard to its index of refraction while preserving a   */
/* constant optical thickness                                        */
/*                                                                   */
/* This function takes 7 arguments:                                  */
/*   dMi               the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   dN                the derivative of the index of refraction of  */
/*                     the layer;                                    */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   N_0               the index of refraction at the reference      */
/*                     wavelength                                    */
/*   sin2_theta_0_0    the normalized sinus squared of the           */
/*                     propagation angle at the reference            */
/*                     wavelength.                                   */
/*                                                                   */
/* The optical thickness is kept constant at the reference           */
/* wavelength where the index of refraction is N_0.                  */
/*                                                                   */
/* The derivative of the index of refraction, dN, is with regard to  */
/* the real part of the index of refraction at the reference         */
/* wavelength and is calculated from the dispersion relation of the  */
/* mixture considered (see N_mixture).                               */
/*                                                                   */
/*********************************************************************/
void set_dMi_index_with_constant_OT(const matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0, const std::complex<double> N_0, const std::complex<double> sin2_theta_0_0)
{
	long														i;
	double													k;
	double													n_0, k_0;
	std::complex<double>						N_s_0;
	double													real_N_s_0, imag_N_s_0, norm_N_s_0_square;
	double													dd_dn_0;
	std::complex<double>						N_square, N_s, N_p, phi;
	std::complex<double>						dN_s, dN_p, dphi_dN, dphi_dd, dphi_dn_0;
	std::complex<double>						sin_phi, j_sin_phi_dN_s_dn_0, j_sin_phi_dN_p_dn_0, j_cos_phi_dphi_dn_0;

	n_0 = real(N_0);
	k_0 = -imag(N_0);
	N_s_0 = sqrt(N_0*N_0-sin2_theta_0_0);

	/* Correct branch selection. */
	if (real(N_s_0) == 0.0)
		N_s_0 = -N_s_0;

	real_N_s_0 = real(N_s_0);
	imag_N_s_0 = imag(N_s_0);
	norm_N_s_0_square = real_N_s_0*real_N_s_0 + imag_N_s_0*imag_N_s_0;

	dd_dn_0 = -thickness/norm_N_s_0_square * (n_0 - (imag_N_s_0/real_N_s_0)*k_0);

	for (i = 0; i < dMi->wvls->length; i++)
	{
		k = two_pi/dMi->wvls->wvls[i];

		N_square = N->N[i]*N->N[i];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		phi = k*thickness*N_s;
		dN_s = N->N[i]/N_s;
		dN_p = dN_s * (2.0 - dN_s*dN_s);
		dphi_dN = k*thickness*dN_s;
		dphi_dd = k*N_s;
		dphi_dn_0 = dphi_dN*dN->N[i] + dphi_dd*dd_dn_0;
		sin_phi = sin(phi);
		j_sin_phi_dN_s_dn_0 = j*sin_phi*dN_s*dN->N[i];
		j_sin_phi_dN_p_dn_0 = j*sin_phi*dN_p*dN->N[i];
		j_cos_phi_dphi_dn_0 = j*cos(phi)*dphi_dn_0;

		dMi->matrices[i].s[0] = dMi->matrices[i].s[3] = dMi->matrices[i].p[0] = dMi->matrices[i].p[3] = -sin_phi*dphi_dn_0;
		dMi->matrices[i].s[1] = j_cos_phi_dphi_dn_0/N_s - j_sin_phi_dN_s_dn_0/(N_s*N_s);
		dMi->matrices[i].p[1] = j_cos_phi_dphi_dn_0/N_p - j_sin_phi_dN_p_dn_0/(N_p*N_p);
		dMi->matrices[i].s[2] = N_s*j_cos_phi_dphi_dn_0 + j_sin_phi_dN_s_dn_0;
		dMi->matrices[i].p[2] = N_p*j_cos_phi_dphi_dn_0 + j_sin_phi_dN_p_dn_0;
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dM                                                      */
/*                                                                   */
/* Calculate the derivative of the characteristic matrices of the    */
/* stack from that of a layer and pre and post matrices              */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   dM                the structure in which to store the results;  */
/*   dMi               the derivative of the characteristic matrices */
/*                     of a layer;                                   */
/*   M                 the pre and post matrices of the stack;       */
/*   layer_nb          the position of the layer.                    */
/*                                                                   */
/*********************************************************************/
void calculate_dM(const matrices_type *dM, const matrices_type *dMi, const pre_and_post_matrices_type *M, const long layer_nb)
{
	set_matrices_unity(dM);
	multiply_matrices(dM, M->pre_M[layer_nb]);
	multiply_matrices(dM, dMi);
	multiply_matrices(dM, M->post_M[layer_nb]);
}


/*********************************************************************/
/*                                                                   */
/* calculate_psi_matrices                                            */
/*                                                                   */
/* Calculate the psi matrices of a stack                             */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   psi               the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the stack;                                    */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/* Calculation of the psi_r matrices follow                          */
/*   Verly et al., "Efficient refinement algorithm for the synthesis */
/*   for inhomogeneous optical coatings", Appl. Opt., vol. 36, 1997, */
/*   pp. 1487-1495.                                                  */
/* The psi_t matrix was constructed to be similar to psi_r.          */
/*                                                                   */
/*********************************************************************/
void calculate_psi_matrices(const psi_matrices_type *psi, const r_and_t_type *r_and_t, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						one_minus_r_s, one_plus_r_s, one_minus_r_p, one_plus_r_p;
	std::complex<double>						mult_r_s, mult_r_p, mult_t_s, mult_t_p;
	long														i;


	/* Calculate the psi matrices. */
	for (i = 0; i < psi->wvls->length; i++)
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

		/* Some usefull partial results. */
		one_minus_r_s = 1.0 - r_and_t->r_s[i];
		one_plus_r_s  = 1.0 + r_and_t->r_s[i];
		one_minus_r_p = 1.0 - r_and_t->r_p[i];
		one_plus_r_p  = 1.0 + r_and_t->r_p[i];

		/* Multiplier for the reflexion matrix t/(2 N_m). */
		mult_r_s = 0.5*r_and_t->t_s[i]/N_m_s;
		mult_r_p = 0.5*r_and_t->t_p[i]/N_m_p;

		/* Multiplier for the transmission matrix. */
		mult_t_s = - mult_r_s*r_and_t->t_s[i];
		mult_t_p = - mult_r_p*r_and_t->t_p[i];

		/* Reflexion psi matrices. */
		psi->psi_r->matrices[i].s[0] =   mult_r_s * N_m_s       * one_minus_r_s;
		psi->psi_r->matrices[i].s[1] = - mult_r_s               * one_plus_r_s;
		psi->psi_r->matrices[i].s[2] =   mult_r_s * N_m_s*N_s_s * one_minus_r_s;
		psi->psi_r->matrices[i].s[3] = - mult_r_s * N_s_s       * one_plus_r_s;

		psi->psi_r->matrices[i].p[0] =   mult_r_p * N_m_p       * one_minus_r_p;
		psi->psi_r->matrices[i].p[1] = - mult_r_p               * one_plus_r_p;
		psi->psi_r->matrices[i].p[2] =   mult_r_p * N_m_p*N_s_p * one_minus_r_p;
		psi->psi_r->matrices[i].p[3] = - mult_r_p * N_s_p       * one_plus_r_p;

		/* Transmission psi matrices. */
		psi->psi_t->matrices[i].s[0] = mult_t_s * N_m_s;
		psi->psi_t->matrices[i].s[1] = mult_t_s;
		psi->psi_t->matrices[i].s[2] = mult_t_s * N_m_s*N_s_s;
		psi->psi_t->matrices[i].s[3] = mult_t_s * N_s_s;

		psi->psi_t->matrices[i].p[0] = mult_t_p * N_m_p;
		psi->psi_t->matrices[i].p[1] = mult_t_p;
		psi->psi_t->matrices[i].p[2] = mult_t_p * N_m_p*N_s_p;
		psi->psi_t->matrices[i].p[3] = mult_t_p * N_s_p;
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_psi_matrices_reverse                                    */
/*                                                                   */
/* Calculate the psi matrices of a stack in reverse direction        */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   psi               the structure in which to store the results;  */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the stack;                                    */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/* Calculation of the psi_r matrices follow                          */
/*   Verly et al., "Efficient refinement algorithm for the synthesis */
/*   for inhomogeneous optical coatings", Appl. Opt., vol. 36, 1997, */
/*   pp. 1487-1495.                                                  */
/* The psi_t matrix was constructed to be similar to psi_r.          */
/*                                                                   */
/*********************************************************************/
void calculate_psi_matrices_reverse(const psi_matrices_type *psi, const r_and_t_type *r_and_t, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						one_minus_r_s, one_plus_r_s, one_minus_r_p, one_plus_r_p;
	std::complex<double>						mult_r_s, mult_r_p, mult_t_s, mult_t_p;
	long														i;

	/* Calculate the psi matrices. */
	for (i = 0; i < psi->wvls->length; i++)
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

		/* Some usefull partial results. */
		one_minus_r_s = 1.0 - r_and_t->r_s[i];
		one_plus_r_s  = 1.0 + r_and_t->r_s[i];
		one_minus_r_p = 1.0 - r_and_t->r_p[i];
		one_plus_r_p  = 1.0 + r_and_t->r_p[i];

		/* Multiplier for the reflexion matrix t/(2 N_s). */
		mult_r_s = 0.5*r_and_t->t_s[i]/N_s_s;
		mult_r_p = 0.5*r_and_t->t_p[i]/N_s_p;

		/* Multiplier for the transmission matrix. */
		mult_t_s = - mult_r_s*r_and_t->t_s[i];
		mult_t_p = - mult_r_p*r_and_t->t_p[i];

		/* Reflexion psi matrices. */
		psi->psi_r->matrices[i].s[0] =   mult_r_s * N_s_s       * one_minus_r_s;
		psi->psi_r->matrices[i].s[1] = - mult_r_s               * one_plus_r_s;
		psi->psi_r->matrices[i].s[2] =   mult_r_s * N_s_s*N_m_s * one_minus_r_s;
		psi->psi_r->matrices[i].s[3] = - mult_r_s * N_m_s       * one_plus_r_s;

		psi->psi_r->matrices[i].p[0] =   mult_r_p * N_s_p       * one_minus_r_p;
		psi->psi_r->matrices[i].p[1] = - mult_r_p               * one_plus_r_p;
		psi->psi_r->matrices[i].p[2] =   mult_r_p * N_s_p*N_m_p * one_minus_r_p;
		psi->psi_r->matrices[i].p[3] = - mult_r_p * N_m_p       * one_plus_r_p;

		/* Transmission psi matrices. */
		psi->psi_t->matrices[i].s[0] = mult_t_s * N_s_s;
		psi->psi_t->matrices[i].s[1] = mult_t_s;
		psi->psi_t->matrices[i].s[2] = mult_t_s * N_s_s*N_m_s;
		psi->psi_t->matrices[i].s[3] = mult_t_s * N_m_s;

		psi->psi_t->matrices[i].p[0] = mult_t_p * N_s_p;
		psi->psi_t->matrices[i].p[1] = mult_t_p;
		psi->psi_t->matrices[i].p[2] = mult_t_p * N_s_p*N_m_p;
		psi->psi_t->matrices[i].p[3] = mult_t_p * N_m_p;
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dr_and_dt                                               */
/*                                                                   */
/* Calculate the derivative of the amplitude reflection and          */
/* transmission                                                      */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   dr_and_dt         the structure in which to store the results;  */
/*   dM                the derivative of the characteristic matrices */
/*                     of the stack;                                 */
/*   psi               the psi matrices of the stack.                */
/*                                                                   */
/*********************************************************************/
void calculate_dr_and_dt(const r_and_t_type *dr_and_dt, const matrices_type *dM, const psi_matrices_type *psi)
{
	matrices_type										*M_dr, *M_dt;
	long														i;

	/* Create the M_dr and M_dt matrices. */
	M_dr = new_matrices(dr_and_dt->wvls);
	M_dt = new_matrices(dr_and_dt->wvls);

	/* Copy psi matrices in M_dr and M_dt matrices. */
	copy_matrices(psi->psi_r, M_dr);
	copy_matrices(psi->psi_t, M_dt);

	/* Calculate M_dr and M_dt matrices.. */
	multiply_matrices(M_dr, dM);
	multiply_matrices(M_dt, dM);

	/* The trace of the matrices are dr and dt. */
	for (i = 0; i < dr_and_dt->wvls->length; i++)
	{
		dr_and_dt->r_s[i] = M_dr->matrices[i].s[0]+M_dr->matrices[i].s[3];
		dr_and_dt->r_p[i] = M_dr->matrices[i].p[0]+M_dr->matrices[i].p[3];

		dr_and_dt->t_s[i] = M_dt->matrices[i].s[0]+M_dt->matrices[i].s[3];
		dr_and_dt->t_p[i] = M_dt->matrices[i].p[0]+M_dt->matrices[i].p[3];
	}

	/* Delete matrices that are not necessary anymore. */
	del_matrices(M_dr);
	del_matrices(M_dt);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dr_and_dt_reverse                                       */
/*                                                                   */
/* Calculate the derivative of the amplitude reflection and          */
/* transmission in reverse direction                                 */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   dr_and_dt         the structure in which to store the results;  */
/*   dM                the derivative of the characteristic matrices */
/*                     of the stack;                                 */
/*   psi               the psi matrices of the stack.                */
/*                                                                   */
/*********************************************************************/
void calculate_dr_and_dt_reverse(const r_and_t_type *dr_and_dt, const matrices_type *dM, const psi_matrices_type *psi)
{
	matrices_type										*dM_reverse;
	matrices_type										*M_dr, *M_dt;
	long														i;

	/* When calculating in reverse direction we interchange n1 and n2 and
	 * use the fact that Abeles matrices are persymmetric; therefore if
	 *   M1*M2*M3*... = A
	 * then ...*M3*M2*M1 can be obtained by rotating A about the
	 * diagonal going from the upper-right corner to the lower left
	 * corner. */

	dM_reverse = new_matrices(dr_and_dt->wvls);
	for (i = 0; i < dr_and_dt->wvls->length; i++)
	{
		dM_reverse->matrices[i].s[0] = dM->matrices[i].s[3];
		dM_reverse->matrices[i].s[1] = dM->matrices[i].s[1];
		dM_reverse->matrices[i].s[2] = dM->matrices[i].s[2];
		dM_reverse->matrices[i].s[3] = dM->matrices[i].s[0];

		dM_reverse->matrices[i].p[0] = dM->matrices[i].p[3];
		dM_reverse->matrices[i].p[1] = dM->matrices[i].p[1];
		dM_reverse->matrices[i].p[2] = dM->matrices[i].p[2];
		dM_reverse->matrices[i].p[3] = dM->matrices[i].p[0];
	}

	/* Create the M_dr and M_dt matrices. */
	M_dr = new_matrices(dr_and_dt->wvls);
	M_dt = new_matrices(dr_and_dt->wvls);

	/* Copy psi matrices in M_dr and M_dt matrices. */
	copy_matrices(psi->psi_r, M_dr);
	copy_matrices(psi->psi_t, M_dt);

	/* Calculate M_dr and M_dt matrices. */
	multiply_matrices(M_dr, dM_reverse);
	multiply_matrices(M_dt, dM_reverse);

	/* The trace of the matrices are dr and dt. */
	for (i = 0; i < dr_and_dt->wvls->length; i++)
	{
		dr_and_dt->r_s[i] = M_dr->matrices[i].s[0]+M_dr->matrices[i].s[3];
		dr_and_dt->r_p[i] = M_dr->matrices[i].p[0]+M_dr->matrices[i].p[3];

		dr_and_dt->t_s[i] = M_dt->matrices[i].s[0]+M_dt->matrices[i].s[3];
		dr_and_dt->t_p[i] = M_dt->matrices[i].p[0]+M_dt->matrices[i].p[3];
	}

	/* Delete matrices that are not necessary anymore. */
	del_matrices(dM_reverse);
	del_matrices(M_dr);
	del_matrices(M_dt);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dR                                                      */
/*                                                                   */
/* Calculate the derivative of the reflectance                       */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   dR                the structure in which to store the results;  */
/*   dr_and_dt         the derivative of amplitude reflection and    */
/*                     transmission;                                 */
/*   r_and_t           the amplitude reflection and transmission of  */
/*                     the stack;                                    */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_dR(const spectrum_type *dR, const r_and_t_type *dr_and_dt, const r_and_t_type *r_and_t, const double polarization)
{
	double													Psi, sin_Psi, sin_Psi_square;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < dR->wvls->length; i++)
			dR->data[i] = 2.0*real(conj(r_and_t->r_s[i])*dr_and_dt->r_s[i]);
	}
	else if (polarization == P)
	{
		for (i = 0; i < dR->wvls->length; i++)
			dR->data[i] = 2.0*real(conj(r_and_t->r_p[i])*dr_and_dt->r_p[i]);
	}
	else
	{
		Psi = polarization*M_PI/180.0;
		sin_Psi = sin(Psi);
		sin_Psi_square = sin_Psi*sin_Psi;
		for (i = 0; i < dR->wvls->length; i++)
			dR->data[i] = 2.0*real(conj(r_and_t->r_s[i])*dr_and_dt->r_s[i])*sin_Psi_square + 2.0*real(conj(r_and_t->r_p[i])*dr_and_dt->r_p[i])*(1.0-sin_Psi_square);
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dT                                                      */
/*                                                                   */
/* Calculate the derivative of the transmittance                     */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   dT                the structure in which to store the results;  */
/*   dr_and_dt         the derivative of amplitude reflection and    */
/*                     transmission;                                 */
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
void calculate_dT(const spectrum_type *dT, const r_and_t_type *dr_and_dt, const r_and_t_type *r_and_t, const N_type *N_i, const N_type *N_e, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_i_s, N_i_p, N_e_s, N_e_p;
	double													Psi, sin_Psi, sin_Psi_square;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < dT->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_e->N[i]*N_e->N[i];
			N_e_s = sqrt(N_square - sin2_theta_0->sin2[i]);

			dT->data[i] = 2.0*(real(N_e_s)/real(N_i_s))*real(conj(r_and_t->t_s[i])*dr_and_dt->t_s[i]);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < dT->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);
			N_square = N_e->N[i]*N_e->N[i];
			N_e_p = N_square/sqrt(N_square - sin2_theta_0->sin2[i]);

			dT->data[i] = 2.0*(real(N_e_p)/real(N_i_p))*real(conj(r_and_t->t_p[i])*dr_and_dt->t_p[i]);
		}
	}
	else
	{
		Psi = polarization*M_PI/180.0;
		sin_Psi = sin(Psi);
		sin_Psi_square = sin_Psi*sin_Psi;
		for (i = 0; i < dT->wvls->length; i++)
		{
			N_square = N_i->N[i]*N_i->N[i];
			N_i_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_i_p = N_square/N_i_s;
			N_square = N_e->N[i]*N_e->N[i];
			N_e_s = sqrt(N_square - sin2_theta_0->sin2[i]);
			N_e_p = N_square/N_e_s;

			dT->data[i] = 2.0*(real(N_e_s)/real(N_i_s))*real(conj(r_and_t->t_s[i])*dr_and_dt->t_s[i])*sin_Psi_square + 2.0*(real(N_e_p)/real(N_i_p))*real(conj(r_and_t->t_p[i])*dr_and_dt->t_p[i])*(1.0-sin_Psi_square);
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dA                                                      */
/*                                                                   */
/* Calculate the derivative of the absorptance from that of the      */
/* reflectance and the transmittance.                                */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   dA                the structure in which to store the results;  */
/*   dR                the derivative of the reflectance;            */
/*   dT                the derivative of the transmittance.          */
/*                                                                   */
/*********************************************************************/
void calculate_dA(const spectrum_type *dA, const spectrum_type *dR, const spectrum_type *dT)
{
	long														i;

	for (i = 0; i < dA->wvls->length; i++)
		dA->data[i] = -(dR->data[i]+dT->data[i]);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dR_with_backside                                        */
/*                                                                   */
/* Calculate the derivative of the reflectance with consideration    */
/* of the backside                                                   */
/*                                                                   */
/* This function takes 12 arguments:                                 */
/*   dR                the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   dT_front          the derivative of the transmittance of the    */
/*                     front side;                                   */
/*   dR_front          the derivative of the reflectance of the      */
/*                     front side;                                   */
/*   T_front_reverse   the transmittance of the front side in        */
/*                     reverse direction;                            */
/*   dT_front_reverse  the derivative of the transmittance of the    */
/*                     front side in reverse direction;              */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   dR_front_reverse  the derivative of the reflectance of the      */
/*                     front side in reverse direction;              */
/*   R_back            the reflectance of the back side;             */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_dR_with_backside(const spectrum_type *dR, const spectrum_type *T_front, const spectrum_type *dT_front, const spectrum_type *dR_front, const spectrum_type *T_front_reverse, const spectrum_type *dT_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *dR_front_reverse, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag, exp_4_beta_imag;
	double													denominator, common_factor;
	long														i;

	for (i = 0; i < dR->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/dR->wvls->wvls[i]);
		exp_4_beta_imag = exp(4.0*beta_imag);

		denominator = 1.0 - R_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag;
		common_factor = T_front->data[i]*T_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag/denominator;
		dR->data[i] = dR_front->data[i] + common_factor * (dT_front->data[i]/T_front->data[i] + dT_front_reverse->data[i]/T_front_reverse->data[i] + dR_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag/denominator);
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dR_with_backside_2                                      */
/*                                                                   */
/* Calculate the derivative of the reflectance with regard to a      */
/* variation in the stack on the backside and with consideration     */
/* consideration of the backside                                     */
/*                                                                   */
/* This function takes 9 arguments:                                  */
/*   dR                the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   T_front_reverse   the transmittance of the front side in        */
/*                     reverse direction;                            */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   R_back            the reflectance of the back side;             */
/*   dR_back           the derivative of the reflectance of the back */
/*                     side;                                         */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_dR_with_backside_2(const spectrum_type *dR, const spectrum_type *T_front, const spectrum_type *T_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *R_back, const spectrum_type *dR_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag, exp_4_beta_imag;
	double													denominator, common_factor;
	long														i;

	for (i = 0; i < dR->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/dR->wvls->wvls[i]);
		exp_4_beta_imag = exp(4.0*beta_imag);

		denominator = 1.0 - R_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag;
		common_factor = T_front->data[i]*T_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag/denominator;
		dR->data[i] = common_factor * (1.0/R_back->data[i] + R_front_reverse->data[i]*exp_4_beta_imag/denominator) * dR_back->data[i];
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dT_with_backside                                        */
/*                                                                   */
/* Calculate the derivative of the transmittance with consideration  */
/* of the backside                                                   */
/*                                                                   */
/* This function takes 10 arguments:                                 */
/*   dT                the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   dT_front          the derivative of the transmittance of the    */
/*                     front side;                                   */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   dR_front_reverse  the derivative of the reflectance of the      */
/*                     front side in reverse direction;              */
/*   T_back            the transmittance of the back side;           */
/*   R_back            the reflectance of the back side;             */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_dT_with_backside(const spectrum_type *dT, const spectrum_type *T_front, const spectrum_type *dT_front, const spectrum_type *R_front_reverse, const spectrum_type *dR_front_reverse, const spectrum_type *T_back, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag, exp_4_beta_imag;
	double													denominator, T;
	long														i;

	for (i = 0; i < dT->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/dT->wvls->wvls[i]);
		exp_4_beta_imag = exp(4.0*beta_imag);

		denominator = 1.0 - R_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag;
		T = T_front->data[i]*T_back->data[i]*exp(2.0*beta_imag)/denominator;
		dT->data[i] = T * (dT_front->data[i]/T_front->data[i] + dR_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag/denominator);
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dT_with_backside_2                                      */
/*                                                                   */
/* Calculate the derivative of the transmittance with regard to a    */
/* variation in the stack on the backside and with consideration     */
/* of the backside                                                   */
/*                                                                   */
/* This function takes 10 arguments:                                 */
/*   dT                the structure in which to store the results;  */
/*   T_front           the transmittance of the front side;          */
/*   R_front_reverse   the reflectance of the front side in reverse  */
/*                     direction;                                    */
/*   T_back            the transmittance of the back side;           */
/*   dT_back           the derivative of the transmittance of the    */
/*                     back side;                                    */
/*   R_back            the reflectance of the back side;             */
/*   dR_back           the derivative of the reflectance of the back */
/*                     side;                                         */
/*   N_s               the index of refraction of the substrate;     */
/*   thickness         the thickness of the substrate;               */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle.                            */
/*                                                                   */
/*********************************************************************/
void calculate_dT_with_backside_2(const spectrum_type *dT, const spectrum_type *T_front, const spectrum_type *R_front_reverse, const spectrum_type *T_back, const spectrum_type *dT_back, const spectrum_type *R_back, const spectrum_type *dR_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0)
{
	std::complex<double>						N_square, N_s_s;
	double													beta_imag, exp_4_beta_imag;
	double													denominator, T;
	long														i;

	for (i = 0; i < dT->wvls->length; i++)
	{
		N_square = N_s->N[i]*N_s->N[i];
		N_s_s = sqrt(N_square - sin2_theta_0->sin2[i]);

		/* Correct branch selection. */
		if (real(N_s_s) == 0.0)
			N_s_s = -N_s_s;

		beta_imag = imag(two_pi*thickness*N_s_s/dT->wvls->wvls[i]);
		exp_4_beta_imag = exp(4.0*beta_imag);

		denominator = 1.0 - R_front_reverse->data[i]*R_back->data[i]*exp_4_beta_imag;
		T = T_front->data[i]*T_back->data[i]*exp(2.0*beta_imag)/denominator;
		dT->data[i] = T * (1.0/T_back->data[i]*dT_back->data[i] + R_front_reverse->data[i]*exp_4_beta_imag/denominator*dR_back->data[i]);
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dr_phase                                                */
/*                                                                   */
/* Calculate the derivative of the phase shift upon reflection       */
/*                                                                   */
/* This function takes 7 arguments:                                  */
/*   dphase            the structure in which to store the results;  */
/*   M                 the characteristic matrices of the stack;     */
/*   dM                the derivative of the characteristic matrices */
/*                     of the stack;                                 */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_dr_phase(const spectrum_type *dphase, const matrices_type *M, const matrices_type *dM, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						B, C, B_conj, C_conj;
	std::complex<double>						dB, dC, dB_conj, dC_conj;
	double													numerator, denominator, ratio;
	double													dnumerator, ddenominator;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < dphase->wvls->length; i++)
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

			/* Admittance of s polarisation and its derivative. */
			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;
			C = M->matrices[i].s[2] + M->matrices[i].s[3]*N_s_s;
			dB = dM->matrices[i].s[0] + dM->matrices[i].s[1]*N_s_s;
			dC = dM->matrices[i].s[2] + dM->matrices[i].s[3]*N_s_s;
			B_conj = conj(B);
			C_conj = conj(C);
			dB_conj = conj(dB);
			dC_conj = conj(dC);

			/* s reflection phase derivative. */
			numerator = imag(N_m_s*(B*C_conj-C*B_conj));
			denominator = real(N_m_s*N_m_s*B*B_conj-C*C_conj);
			dnumerator = imag(N_m_s*(dB*C_conj+B*dC_conj-dC*B_conj-C*dB_conj));
			ddenominator = 2.0*real(N_m_s*N_m_s*dB*B_conj-dC*C_conj);
			ratio = numerator/denominator;
			dphase->data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < dphase->wvls->length; i++)
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

			/* Admittance of p polarisation and its derivative. */
			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;
			C = M->matrices[i].p[2] + M->matrices[i].p[3]*N_s_p;
			dB = dM->matrices[i].p[0] + dM->matrices[i].p[1]*N_s_p;
			dC = dM->matrices[i].p[2] + dM->matrices[i].p[3]*N_s_p;
			B_conj = conj(B);
			C_conj = conj(C);
			dB_conj = conj(dB);
			dC_conj = conj(dC);

			/* p reflection phase derivative. */
			numerator = imag(N_m_p*(B*C_conj-C*B_conj));
			denominator = real(N_m_p*N_m_p*B*B_conj-C*C_conj);
			dnumerator = imag(N_m_p*(dB*C_conj+B*dC_conj-dC*B_conj-C*dB_conj));
			ddenominator = 2.0*real(N_m_p*N_m_p*dB*B_conj-dC*C_conj);
			ratio = numerator/denominator;
			dphase->data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator);
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dt_phase                                                */
/*                                                                   */
/* Calculate the derivative of the phase shift upon transmission     */
/*                                                                   */
/* This function takes 7 arguments:                                  */
/*   dphase            the structure in which to store the results;  */
/*   M                 the characteristic matrices of the stack;     */
/*   dM                the derivative of the characteristic matrices */
/*                     of the stack;                                 */
/*   N_m               the index of refraction of the medium;        */
/*   N_s               the index of refraction of the substrate;     */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*   polarization      the polarization of light.                    */
/*                                                                   */
/*********************************************************************/
void calculate_dt_phase(const spectrum_type *dphase, const matrices_type *M, const matrices_type *dM, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization)
{
	std::complex<double>						N_square, N_m_s, N_m_p, N_s_s, N_s_p;
	std::complex<double>						B, C;
	std::complex<double>						dB, dC;
	std::complex<double>						temp;
	std::complex<double>						dtemp;
	double													numerator, denominator, ratio;
	double													dnumerator, ddenominator;
	long														i;

	if (polarization == S)
	{
		for (i = 0; i < dphase->wvls->length; i++)
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

			/* Admittance of s polarisation and its derivative. */
			B = M->matrices[i].s[0] + M->matrices[i].s[1]*N_s_s;
			C = M->matrices[i].s[2] + M->matrices[i].s[3]*N_s_s;
			dB = dM->matrices[i].s[0] + dM->matrices[i].s[1]*N_s_s;
			dC = dM->matrices[i].s[2] + dM->matrices[i].s[3]*N_s_s;

			/* s transmission phase derivative. */
			temp = N_m_s*B+C;
			dtemp = N_m_s*dB+dC;
			numerator = -imag(temp);
			denominator = real(temp);
			dnumerator = -imag(dtemp);
			ddenominator = real(dtemp);
			ratio = numerator/denominator;
			dphase->data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator);
		}
	}
	else if (polarization == P)
	{
		for (i = 0; i < dphase->wvls->length; i++)
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

			/* Admittance of p polarisation and its derivative. */
			B = M->matrices[i].p[0] + M->matrices[i].p[1]*N_s_p;
			C = M->matrices[i].p[2] + M->matrices[i].p[3]*N_s_p;
			dB = dM->matrices[i].p[0] + dM->matrices[i].p[1]*N_s_p;
			dC = dM->matrices[i].p[2] + dM->matrices[i].p[3]*N_s_p;

			/* p transmission phase derivative. */
			temp = N_m_p*B+C;
			dtemp = N_m_p*dB+dC;
			numerator = -imag(temp);
			denominator = real(temp);
			dnumerator = -imag(dtemp);
			ddenominator = real(dtemp);
			ratio = numerator/denominator;
			dphase->data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator);
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* calculate_dGD                                                     */
/*                                                                   */
/* Calculate the derivative of the group delay                       */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   dGD               the structure in which to store the results;  */
/*   dphase            the derivative of the phase shift of the      */
/*                     filter.                                       */
/*                                                                   */
/* The derivative of the group delay is calculated exactly like the  */
/* group delay, except that it is calculated from the derivative of  */
/* the phase instead of the phase.                                   */
/*                                                                   */
/*********************************************************************/
void calculate_dGD(const spectrum_type *dGD, const spectrum_type *dphase)
{
	_calculate_GD(dGD, dphase, false);
}


/*********************************************************************/
/*                                                                   */
/* calculate_dGDD                                                    */
/*                                                                   */
/* Calculate the derivative of the group delay dispersion            */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   dGDD              the structure in which to store the results;  */
/*   dphase            the derivative of the phase shift of the      */
/*                     filter.                                       */
/*                                                                   */
/* The derivative of the group delay dispersion is calculated        */
/* exactly like the group delay, except that it is calculated from   */
/* the derivative of the phase instead of the phase.                 */
/*                                                                   */
/*********************************************************************/
void calculate_dGDD(const spectrum_type *dGDD, const spectrum_type *dphase)
{
	_calculate_GDD(dGDD, dphase, false);
}


#ifdef __cplusplus
}
#endif
