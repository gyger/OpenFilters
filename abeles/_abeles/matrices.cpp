/*
 *
 *  matrices.cpp
 *
 *
 *  Functions to create, handle and multiply Abeles characteristic
 *  matrices.
 *
 *  Copyright (c) 2002-2009,2012,2013 Stephane Larouche.
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


const double two_pi = 2.0*M_PI;


/*********************************************************************/
/*                                                                   */
/* new_matrices                                                      */
/*                                                                   */
/* Create a new matrices structure to store the characteristic       */
/* matrices of a stack                                               */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the wavelengths at which to calculate the     */
/*                     matrices;                                     */
/* and returns a matrices structure.                                 */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
matrices_type * new_matrices(const wvls_type *wvls)
{
	matrices_type										*M;

	M = (matrices_type *)malloc(sizeof(matrices_type));

	if (!M) return NULL;

	M->wvls = wvls;
	M->matrices = (matrix_type *)malloc(M->wvls->length*sizeof(matrix_type));

	if (!M->matrices)
	{
		del_matrices(M);
		return NULL;
	}

	return M;
}


/*********************************************************************/
/*                                                                   */
/* del_matrices                                                      */
/*                                                                   */
/* Delete a matrices structure                                       */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_matrices(matrices_type *M)
{
	if (!M) return;

	free(M->matrices);
	free(M);
}


/*********************************************************************/
/*                                                                   */
/* set_matrices_unity                                                */
/*                                                                   */
/* Set the caracteristic matrices to unity matrices                  */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the matrices to set to unity.                 */
/*                                                                   */
/*********************************************************************/
void set_matrices_unity(const matrices_type *M)
{
	long														i;

	for (i = 0; i < M->wvls->length; i++)
	{
		M->matrices[i].s[0] = 1.0;
		M->matrices[i].s[1] = 0.0;
		M->matrices[i].s[2] = 0.0;
		M->matrices[i].s[3] = 1.0;

		M->matrices[i].p[0] = 1.0;
		M->matrices[i].p[1] = 0.0;
		M->matrices[i].p[2] = 0.0;
		M->matrices[i].p[3] = 1.0;
	}
}


/*********************************************************************/
/*                                                                   */
/* copy_matrices                                                     */
/*                                                                   */
/* Copy the characteristic matrices                                  */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M1                the original matrices;                        */
/*   M2                the destination matrices.                     */
/*                                                                   */
/*********************************************************************/
void copy_matrices(const matrices_type *M1, const matrices_type *M2)
{
	long														i;

	for (i = 0; i < M1->wvls->length; i++)
	{
		M2->matrices[i].s[0] = M1->matrices[i].s[0];
		M2->matrices[i].s[1] = M1->matrices[i].s[1];
		M2->matrices[i].s[2] = M1->matrices[i].s[2];
		M2->matrices[i].s[3] = M1->matrices[i].s[3];

		M2->matrices[i].p[0] = M1->matrices[i].p[0];
		M2->matrices[i].p[1] = M1->matrices[i].p[1];
		M2->matrices[i].p[2] = M1->matrices[i].p[2];
		M2->matrices[i].p[3] = M1->matrices[i].p[3];
	}
}


/*********************************************************************/
/*                                                                   */
/* set_matrices                                                      */
/*                                                                   */
/* Set the caracteristic matrices of a layer                         */
/*                                                                   */
/* This function takes 4 arguments:                                  */
/*   M                 the structure in which to store the results;  */
/*   N                 the index of refraction of the layer;         */
/*   thickness         the thickness of the layer;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/*********************************************************************/
void set_matrices(const matrices_type *M, const N_type *N, const double thickness, const sin2_type *sin2_theta_0)
{
	long														i;
	double													k;
	std::complex<double>						N_square, N_s, N_p, phi, j_sin_phi;

	for (i = 0; i < M->wvls->length; i++)
	{
		k = two_pi/M->wvls->wvls[i];

		N_square = N->N[i]*N->N[i];
		N_s = sqrt(N_square-sin2_theta_0->sin2[i]);
		N_p = N_square/N_s;

		/* Correct branch selection. */
		if (real(N_s) == 0.0)
		{
			N_s = -N_s;
			N_p = -N_p;
		}

		phi = k*N_s*thickness;

		if (imag(phi) < -100.0) phi = real(phi) + -100.0 * j;

		j_sin_phi = j*sin(phi);

		M->matrices[i].s[0] = M->matrices[i].s[3] = M->matrices[i].p[0] = M->matrices[i].p[3] = cos(phi);
		M->matrices[i].s[1] = j_sin_phi/N_s;
		M->matrices[i].p[1] = j_sin_phi/N_p;
		M->matrices[i].s[2] = N_s*j_sin_phi;
		M->matrices[i].p[2] = N_p*j_sin_phi;
	}
}


/*********************************************************************/
/*                                                                   */
/* multiply_matrices                                                 */
/*                                                                   */
/* Multiply the caracteristic matrices                               */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M1, M2            2 sets of matrices.                           */
/*                                                                   */
/* This function stores M2*M1 in M1.                                 */
/*                                                                   */
/*********************************************************************/
void multiply_matrices(const matrices_type *M1, const matrices_type *M2)
{
	std::complex<double>						temp0, temp1, temp2;
	long														i;

	for (i = 0; i < M1->wvls->length; i++)
	{
		temp0 = M2->matrices[i].s[0]*M1->matrices[i].s[0] + M2->matrices[i].s[1]*M1->matrices[i].s[2];
		temp1 = M2->matrices[i].s[0]*M1->matrices[i].s[1] + M2->matrices[i].s[1]*M1->matrices[i].s[3];
		temp2 = M2->matrices[i].s[2]*M1->matrices[i].s[0] + M2->matrices[i].s[3]*M1->matrices[i].s[2];
		M1->matrices[i].s[3] = M2->matrices[i].s[2]*M1->matrices[i].s[1] + M2->matrices[i].s[3]*M1->matrices[i].s[3];
		M1->matrices[i].s[0] = temp0;
		M1->matrices[i].s[1] = temp1;
		M1->matrices[i].s[2] = temp2;

		temp0 = M2->matrices[i].p[0]*M1->matrices[i].p[0] + M2->matrices[i].p[1]*M1->matrices[i].p[2];
		temp1 = M2->matrices[i].p[0]*M1->matrices[i].p[1] + M2->matrices[i].p[1]*M1->matrices[i].p[3];
		temp2 = M2->matrices[i].p[2]*M1->matrices[i].p[0] + M2->matrices[i].p[3]*M1->matrices[i].p[2];
		M1->matrices[i].p[3] = M2->matrices[i].p[2]*M1->matrices[i].p[1] + M2->matrices[i].p[3]*M1->matrices[i].p[3];
		M1->matrices[i].p[0] = temp0;
		M1->matrices[i].p[1] = temp1;
		M1->matrices[i].p[2] = temp2;
	}
}


#ifdef __cplusplus
}
#endif
