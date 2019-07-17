/*
 *
 *  monitoring.cpp
 *
 *
 *  Function to calculate characteristic matrices adapted for
 *  monitoring purposes.
 *
 *  Copyright (c) 2004-2007,2012,2013 Stephane Larouche.
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
/* new_monitoring_matrices                                           */
/*                                                                   */
/* Create a structure to store the characteristic matrix necessary   */
/* to calculate monitoring curves                                    */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   wvls              the wavelengths at which to calculate the     */
/*                     monitoring matrices;                          */
/*   length            the number of slices;                         */
/* and returns a monitoring matrix structure.                        */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/* When calculating a monitoring curve, a layer must be seperated in */
/* multiple slices and the property being monitored calculated       */
/* after the addition of each of these slices. The monitoring        */
/* matrices structure keeps the characteristic matrices              */
/* corresponding to all the slices to allow the calculation of the   */
/* curves.                                                           */
/*                                                                   */
/*********************************************************************/
monitoring_matrices_type * new_monitoring_matrices(const wvls_type *wvls, const long length)
{
	monitoring_matrices_type				*M;
	long														i;

	M = (monitoring_matrices_type *)malloc(sizeof(monitoring_matrices_type));

	if (!M) return NULL;

	M->length = length;
	M->wvls = wvls;
	M->matrices = (matrices_type **)malloc(M->length*sizeof(matrices_type *));

	if (!M->matrices)
	{
		del_monitoring_matrices(M);
		return NULL;
	}

	for (i = 0; i < M->length; i++)
	{
		M->matrices[i] = new_matrices(M->wvls);
	}

	for (i = 0; i < M->length; i++)
	{
		if (!M->matrices[i])
		{
			del_monitoring_matrices(M);
			return NULL;
		}
	}

	return M;
}


/*********************************************************************/
/*                                                                   */
/* del_monitoring_matrices                                           */
/*                                                                   */
/* Delete a monitoring matrix structure                              */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   M                 the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_monitoring_matrices(monitoring_matrices_type *M)
{
	long														i;

	if (!M) return;

	if (M->matrices)
		for (i = 0; i < M->length; i++)
			del_matrices(M->matrices[i]);

	free(M->matrices);

	free(M);
}


/*********************************************************************/
/*                                                                   */
/* set_monitoring_matrices                                           */
/*                                                                   */
/* Set the caracteristic matrices of one slice                       */
/*                                                                   */
/* This function takes 5 arguments:                                  */
/*   M                 the structure in which to store the results;  */
/*   slice             the number of the sublayer;                   */
/*   N                 the index of refraction of the sublayer;      */
/*   slice_thickness   the thickness of the slice;                   */
/*   sin2_theta_0      the normalized sinus squared of the           */
/*                     propagation angle;                            */
/*                                                                   */
/*********************************************************************/
void set_monitoring_matrices(const monitoring_matrices_type *M, const long slice, const N_type *N, const double slice_thickness, const sin2_type *sin2_theta_0)
{
	set_matrices(M->matrices[slice], N, slice_thickness, sin2_theta_0);
}


/*********************************************************************/
/*                                                                   */
/* multiply_monitoring_matrices                                      */
/*                                                                   */
/* Multiply the monitoring matrices                                  */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M1                the matrices corresponding to the layers      */
/*                     below the one currently being monitored;      */
/*   M2                the monitoring matrix structure.              */
/*                                                                   */
/* This function calculates the product of M1 with the matrix of     */
/* every slice in M2 and stores the result in M2. This function      */
/* is meant to be used for homogeneous layers.                       */
/*                                                                   */
/*********************************************************************/
void multiply_monitoring_matrices(const matrices_type *M1, const monitoring_matrices_type *M2)
{
	matrices_type										*M;
	std::complex<double>						temp0, temp1, temp2;
	long														i_slice, i_wvl;

	/* multiply_matrices is not used because the answer must be kept in
	 * M2 (multiply_matrices keeps it in M1) and the supplementary
	 * copy_matrices operation would increase the calculation time by
	 * about 10% (I tried it). */

	for (i_slice = 0; i_slice < M2->length; i_slice++)
	{
		M = M2->matrices[i_slice];

		for (i_wvl = 0; i_wvl < M1->wvls->length; i_wvl++)
		{
			temp0 = M->matrices[i_wvl].s[0]*M1->matrices[i_wvl].s[0] + M->matrices[i_wvl].s[1]*M1->matrices[i_wvl].s[2];
			temp1 = M->matrices[i_wvl].s[0]*M1->matrices[i_wvl].s[1] + M->matrices[i_wvl].s[1]*M1->matrices[i_wvl].s[3];
			temp2 = M->matrices[i_wvl].s[2]*M1->matrices[i_wvl].s[0] + M->matrices[i_wvl].s[3]*M1->matrices[i_wvl].s[2];
			M->matrices[i_wvl].s[3] = M->matrices[i_wvl].s[2]*M1->matrices[i_wvl].s[1] + M->matrices[i_wvl].s[3]*M1->matrices[i_wvl].s[3];
			M->matrices[i_wvl].s[0] = temp0;
			M->matrices[i_wvl].s[1] = temp1;
			M->matrices[i_wvl].s[2] = temp2;

			temp0 = M->matrices[i_wvl].p[0]*M1->matrices[i_wvl].p[0] + M->matrices[i_wvl].p[1]*M1->matrices[i_wvl].p[2];
			temp1 = M->matrices[i_wvl].p[0]*M1->matrices[i_wvl].p[1] + M->matrices[i_wvl].p[1]*M1->matrices[i_wvl].p[3];
			temp2 = M->matrices[i_wvl].p[2]*M1->matrices[i_wvl].p[0] + M->matrices[i_wvl].p[3]*M1->matrices[i_wvl].p[2];
			M->matrices[i_wvl].p[3] = M->matrices[i_wvl].p[2]*M1->matrices[i_wvl].p[1] + M->matrices[i_wvl].p[3]*M1->matrices[i_wvl].p[3];
			M->matrices[i_wvl].p[0] = temp0;
			M->matrices[i_wvl].p[1] = temp1;
			M->matrices[i_wvl].p[2] = temp2;
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* multiply_monitoring_matrices_cumulative                           */
/*                                                                   */
/* Multiply the monitoring matrices cumulatively                     */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M1                the matrices corresponding to the layers      */
/*                     below the one currently being monitored;      */
/*   M2                the monitoring matrix structure.              */
/*                                                                   */
/* This function calculates the product of M1 with the matrix of     */
/* every slice in M2 cumulatively and stores the result in M2. This  */
/* function is meant to be used for graded-index layers.             */
/*                                                                   */
/*********************************************************************/
void multiply_monitoring_matrices_cumulative(const matrices_type *M1, const monitoring_matrices_type *M2)
{
	const matrices_type							*M, *M_pre;
	std::complex<double>						temp0, temp1, temp2;
	long														i_slice, i_wvl;

	M_pre = M1;

	for (i_slice = 0; i_slice < M2->length; i_slice++)
	{
		M = M2->matrices[i_slice];

		for (i_wvl = 0; i_wvl < M1->wvls->length; i_wvl++)
		{
			temp0 = M->matrices[i_wvl].s[0]*M_pre->matrices[i_wvl].s[0] + M->matrices[i_wvl].s[1]*M_pre->matrices[i_wvl].s[2];
			temp1 = M->matrices[i_wvl].s[0]*M_pre->matrices[i_wvl].s[1] + M->matrices[i_wvl].s[1]*M_pre->matrices[i_wvl].s[3];
			temp2 = M->matrices[i_wvl].s[2]*M_pre->matrices[i_wvl].s[0] + M->matrices[i_wvl].s[3]*M_pre->matrices[i_wvl].s[2];
			M->matrices[i_wvl].s[3] = M->matrices[i_wvl].s[2]*M_pre->matrices[i_wvl].s[1] + M->matrices[i_wvl].s[3]*M_pre->matrices[i_wvl].s[3];
			M->matrices[i_wvl].s[0] = temp0;
			M->matrices[i_wvl].s[1] = temp1;
			M->matrices[i_wvl].s[2] = temp2;

			temp0 = M->matrices[i_wvl].p[0]*M_pre->matrices[i_wvl].p[0] + M->matrices[i_wvl].p[1]*M_pre->matrices[i_wvl].p[2];
			temp1 = M->matrices[i_wvl].p[0]*M_pre->matrices[i_wvl].p[1] + M->matrices[i_wvl].p[1]*M_pre->matrices[i_wvl].p[3];
			temp2 = M->matrices[i_wvl].p[2]*M_pre->matrices[i_wvl].p[0] + M->matrices[i_wvl].p[3]*M_pre->matrices[i_wvl].p[2];
			M->matrices[i_wvl].p[3] = M->matrices[i_wvl].p[2]*M_pre->matrices[i_wvl].p[1] + M->matrices[i_wvl].p[3]*M_pre->matrices[i_wvl].p[3];
			M->matrices[i_wvl].p[0] = temp0;
			M->matrices[i_wvl].p[1] = temp1;
			M->matrices[i_wvl].p[2] = temp2;
		}

		M_pre = M;
	}
}


/*********************************************************************/
/*                                                                   */
/* get_slice_matrices                                                */
/*                                                                   */
/* Get the matrices of one of the slice                              */
/*                                                                   */
/* This function takes 2 arguments:                                  */
/*   M                 the monitoring matrix structure;              */
/*   nb                the number of the slice.                      */
/* and returns the matrices of the slice.                            */
/*                                                                   */
/*********************************************************************/
matrices_type * get_slice_matrices(const monitoring_matrices_type *M, const long nb)
{
	return M->matrices[nb];
}


#ifdef __cplusplus
}
#endif
