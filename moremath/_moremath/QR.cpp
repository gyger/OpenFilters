/*
 *
 *  QR.cpp
 *
 *  This file provides functions to solve linear equation systems using
 *  systems QR orthogonalization. Both rank deficient and
 *  overdetermined are accepted.
 *
 *  For details on the QR algorigthm, see
 *    Gene H. Golub and Charles F. van Loan, Matrix Computations, John
 *    Hopkins University Press, 1983.
 *
 *  Copyright (c) 2005,2006,2008,2013,2014 Stephane Larouche.
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
#include <cfloat>
#include <algorithm>

#include "_moremath.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* QR                                                                */
/*                                                                   */
/* Perform QR factorization of a matrix with column pivoting.        */
/*                                                                   */
/* Perform the QR factorization of a n by m matrix using Householder */
/* transformations. The Q matrix is orthogonal and the R matrix is   */
/* upper triangular. The function takes six arguments:               */
/*   n, m       the number of columns and rows in the A matrix;      */
/*   A          the matrix;                                          */
/*   diag       a vector of length n to store the diagonal of the R  */
/*              matrix;                                              */
/*   perm       a vector of length n to store the column             */
/*              permutations;                                        */
/*   norms      a vector of length n to store the norms of the       */
/*              columns of A (usefull in the Levenberg-Marquardt     */
/*              method) or the NULL pointer if the norms are not     */
/*              needed.                                              */
/*                                                                   */
/* On output, the upper triangular part of the A matrix is replaced  */
/* by the R matrix except for its diagonal while the lower           */
/* triangular part stores a factored form of the Q matrix. The       */
/* diagonal elements of R are returned in diag and the column        */
/* permutations in perm.                                             */
/*                                                                   */
/* The function returns the rank of the matrix or -1 if a malloc     */
/* fails.                                                            */
/*                                                                   */
/*********************************************************************/
long QR(const long n, const long m, double **A, double *diag, long *perm, double *norms)
{
	long							i, j, k, col;
	long							rank;
	double						*gamma, *original_gamma;
	double						criteria, norm, dot_product;
	long							temp_long;
	double						temp_double;

	gamma = (double *)malloc(n*sizeof(double));
	original_gamma = (double *)malloc(n*sizeof(double));

	if (!gamma || !original_gamma)
	{
		free(gamma);
		free(original_gamma);

		return -1;
	}

	/* Permutations. */
	for (j = 0; j < n; j++)
		perm[j] = j;

	/* Calculate the norm of each column. Remember the original norm of
	 * each column.*/
	for (j = 0; j < n; j++)
	{
		gamma[j] = 0.0;
		for (i = 0; i < m; i++)
			gamma[j] += A[j][i]*A[j][i];
		original_gamma[j] = gamma[j];
	}

	/* Save the norm of the columns. */
	if (norms)
		for (j = 0; j < n; j++)
			norms[j] = sqrt(gamma[j]);

	/* Establish a criteria for singular matrices. To obtain a scale
	 * independant determination of the rank, the criteria is applied on
	 * the norms of the columns of the original matrix. */
	criteria = 2.0 * std::max(n, m) * DBL_EPSILON;

	/* If the loop doesn't abnormaly terminate, the rank is the smallest
	 * dimension of the matrix. */
	rank = std::min(n, m);

	for (k = 0; k < rank; k++)
	{
		/* Find the unprocessed column with the largest norm. */
		col = k;
		for (j = k+1; j < n; j++)
			if (gamma[j] > gamma[col])
				col = j;

		/* If the largest norm or the remaining column is 0, all columns are
		 * 0 and the matrix is rank deficient. Return immediatly, the rank
		 * of the matrix is k. */
		if (gamma[col] == 0.0 || gamma[col] < criteria * original_gamma[col])
		{
			rank = k;
			break;
		}

		/* Permute gammas, perms and a_ij's. */
		if (col != k)
		{
			temp_double = gamma[k];
			gamma[k] = gamma[col];
			gamma[col] = temp_double;
			temp_double = original_gamma[k];
			original_gamma[k] = original_gamma[col];
			original_gamma[col] = temp_double;
			temp_long = perm[k];
			perm[k] = perm[col];
			perm[col]= temp_long;
			for (i = 0; i < m; i++)
			{
				temp_double = A[k][i];
				A[k][i] = A[col][i];
				A[col][i] =  temp_double;
			}
		}

		/* Compute the norm of the actual column, A[k][k:]. */
		norm = 0.0;
		for (i = k; i < m; i++)
			norm += A[k][i]*A[k][i];
		norm = sqrt(norm);

		/* Use the same sign for the normalization and A[k][k] to reduce
		 * numerical errors. */
		if (A[k][k] < 0.0)
			norm = -norm;

		/* The Householder vector u is any multiple of
		 *   A[k][k:] ± norm(A[k][k:])*e_1
		 * where e_1 is a unit vector and the sign is chosen in fonction of
		 * the sign of A[k][k] to avoid the substraction of two similar
		 * values. The Householder matrix, acting on the n - k last columns
		 * is P_k =  1 - 2*u*u'/u'*u. To save some calculation time, it
		 * would be good to store u'*u. A clever way to do that is to divide
		 * all elements of u by ±norm(A[k][k:]); the first element of this
		 * vector is then equal to half its norm. The u vector is stored in
		 * the lower triangular part of A since the elements of the R matrix
		 * at those positions are null; The diagonal elements of the R
		 * matrix are kept in diag. */
		for (i = k; i < m; i++)
			A[k][i] /= norm;
		A[k][k] += 1.0;

		/* To understand how the Householder matrix acts, let's look at the
		 * case of a 3 by 3 matrix:
		 *
		 *                |u1|                    |A11 A12 A13|
		 *   PA = ( I - 2 |u2| |u1 u2 u3| / u'*u) |A21 A22 A23|
		 *                |u3|                    |A31 A32 A33|
		 *
		 *                |u1*u1 u1*u2 u1*u3|         |A11 A12 A13|
		 *      = ( I - 2 |u2*u1 u2*u2 u2*u3| / u'*u) |A21 A22 A23|
		 *                |u3*u1 u3*u2 u3*u3|         |A31 A32 A33|
		 *
		 *                |u1*u1 u1*u2 u1*u3|         |A11 A12 A13|
		 *      = ( I - 2 |u2*u1 u2*u2 u2*u3| / u'*u) |A21 A22 A23|.
		 *                |u3*u1 u3*u2 u3*u3|         |A31 A32 A33|
		 *
		 * Elements of PA are
		 *
		 *                                      |A1i|
		 *   PAji = Aji - 2 |uj*u1 uj*u2 uj*u3| |A2i| / u'*u
		 *                                      |A3i|
		 *
		 *                                |A1i|
		 *        = Aji - 2 uj |u1 u2 u3| |A2i| / u'*u.
		 *                                |A3i|
		 *
		 * Therefore we calculate PA column by column to calculate only once
		 * the dot product between u and the i'th column of the A matrix.
		 *
		 * Remember that the first element of the u vector, stored in
		 * A[k][k] is equal to u'*u/2. */

		/* Apply the transformation on A[k][k]. */
		diag[k] = -norm;

		/* Apply the transformation on the other columns. */
		for (j = k+1; j < n; j++)
		{
			/* Calculate the dot product. */
			dot_product = 0.0;
			for (i = k; i < m; i++)
				dot_product += A[k][i] * A[j][i];

			temp_double = dot_product / A[k][k];

			/* Update A. */
			for (i = k; i < m; i++)
				A[j][i] -= A[k][i] * temp_double;
		}

		/* Update the norms. */
		for (j = k+1; j < n; j++)
			gamma[j] -= A[j][k]*A[j][k];
	}

	/* Set all elements in positions greater than the rank in the diagonal
	 * of the R matrix to 0. */
	for (i = rank; i < n; i++)
		diag[i] = 0.0;

	/* Free the gamma and original_gamma vectors. */
	free(gamma);
	free(original_gamma);

	return rank;
}


/*********************************************************************/
/*                                                                   */
/* QTb                                                               */
/*                                                                   */
/* Compute inv(Q) * b = Q' * b.                                      */
/*                                                                   */
/* Make the first step in the solving of a linear system of          */
/* equations Ax = b from the QR factorization: calculating           */
/* inv(Q) * b. The function takes six arguments:                     */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal) and a    */
/*          factored form of the Q matrix;                           */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   b      the b vector, on exit, it is replaced by inv(Q)*b.       */
/*                                                                   */
/* If the matrix is rank deficient, a solution is returned having    */
/* rank non-nul components at positions corresponding to the columns */
/* with the largest norms.                                           */
/*                                                                   */
/*********************************************************************/
void QTb(const long n, const long m, double **A, double *diag, long *perm, double *b)
{
	long							i, k;
	long							rank;
	double						dot_product;
	double						temp_double;

	/* Determine the rank. */
	for (rank = n; rank > 0; rank--)
		if (diag[rank-1] != 0.0)
			break;

	/* Calculate inv(Q)*b = Q'*b = ... Q3' Q2' Q1' b. */

	/* Calculate Q'b by successively applying the Qi' matrices. The
	 * details of calculation are identical to that in the QR
	 * factorization function. */
	for (k = 0; k < rank; k++)
	{
		/* Calculation the dot product of the u vector and the c vector. */
		dot_product = 0.0;
		for (i = k; i < m; i++)
			dot_product += A[k][i] * b[i];

		temp_double = dot_product / A[k][k];

		/* Multiply by the matrix. */
		for (i = k; i < m; i++)
			b[i] -= A[k][i] * temp_double;
	}
}


/*********************************************************************/
/*                                                                   */
/* Qb                                                                */
/*                                                                   */
/* Compute inv(Q') * b = Q * b.                                      */
/*                                                                   */
/* Calculate inv(Q') * b that is used in the solution of rank        */
/* deficient systems of equations. The function takes six arguments: */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal) and a    */
/*          factored form of the Q matrix;                           */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   b      the b vector, on exit, it is replaced by inv(Q')*b.      */
/*                                                                   */
/* If the matrix is rank deficient, a solution is returned having    */
/* rank non-nul components at positions corresponding to the         */
/* columns with the largest norms.                                   */
/*                                                                   */
/*********************************************************************/
void Qb(const long n, const long m, double **A, double *diag, long *perm, double *b)
{
	long							i, k;
	long							rank;
	double						dot_product;
	double						temp_double;

	/* Determine the rank. */
	for (rank = n; rank > 0; rank--)
		if (diag[rank-1] != 0.0)
			break;

	/* Calculate inv(Q')*b = Q*b = Q1 Q2 Q3 ... b. */

	/* Calculate Q'b by successively applying the Q matrices. The details
	 * of calculation are identical to that in the QR factorization
	 * function. */
	for (k = rank - 1; k > -1; k--)
	{
		/* Calculation the dot product of the u vector and the c vector. */
		dot_product = 0.0;
		for (i = k; i < m; i++)
			dot_product += A[k][i] * b[i];

		temp_double = dot_product / A[k][k];

		/* Multiply by the matrix. */
		for (i = k; i < m; i++)
			b[i] -= A[k][i] * temp_double;
	}
}


/*********************************************************************/
/*                                                                   */
/* R_solve                                                           */
/*                                                                   */
/* Solve the upper triangular system R * x = c.                      */
/*                                                                   */
/* Make the second step in the solving of a linear system of         */
/* equations Ax = b from the QR factorization: solving the upper     */
/* triangular system R * x = c where c = inv(Q) * b. The function    */
/* takes seven arguments:                                             */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal) and a    */
/*          factored form of the Q matrix;                           */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   c      the inv(Q)*b vector;                                     */
/*   x      a vector to store the solution x.                        */
/* It returns a moremath_error_type, either:                         */
/*   MOREMATH_SUCCESS        the function succeeded;                 */
/*   MOREMATH_OUT_OF_MEMORY  a malloc failed and it was impossible   */
/*                           to perform the calculation.             */
/*                                                                   */
/* If the matrix is rank deficient, a solution is returned having    */
/* rank non-nul components at positions corresponding to the columns */
/* with the largest norms.                                           */
/*                                                                   */
/*********************************************************************/
moremath_error_type R_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *x)
{
	long							j, k;
	long							rank;
	double						sum;
	double						*x_perm;

	/* Create a vector for x with permutations. */
	x_perm = (double *)malloc(n*sizeof(double));

	if (!x_perm)
		return MOREMATH_OUT_OF_MEMORY;

	/* Determine the rank. */
	for (rank = n; rank > 0; rank--)
		if (diag[rank-1] != 0.0)
			break;

	/* Solve the triangular system Rx = c. Put zeros in the solution
	 * if the system is rank deficient. */
	for (k = n-1; k > rank-1; k--) x_perm[k] = 0.0;
	for (k = rank-1; k > -1; k--)
	{
		/* Calculate the sum for parameters already determined. */
		sum = 0.0;
		for (j = k+1; j < n; j++)
			sum += A[j][k] * x_perm[j];

		/* Find the unknown parameter. */
		x_perm[k] = (c[k] - sum) / diag[k];
	}

	/* Replace in the right order. */
	for (j = 0; j < n; j++)
		x[perm[j]] = x_perm[j];

	/* Free the x_perm vector. */
	free(x_perm);

	return MOREMATH_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* RT_solve                                                          */
/*                                                                   */
/* Solve the lower triangular system R' * z = c.                     */
/*                                                                   */
/* Solve the lower triangular system R' * z = c that is used in rank */
/* deficient systems of equations. The function takes seven          */
/* arguments:                                                        */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal) and a    */
/*          factored form of the Q matrix;                           */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   c      the c vector;                                            */
/*   z      a vector to store the solution z.                        */
/* It returns a moremath_error_type, either:                         */
/*   MOREMATH_SUCCESS        the function succeeded;                 */
/*   MOREMATH_OUT_OF_MEMORY  a malloc failed and it was impossible   */
/*                           to perform the calculation.             */
/*                                                                   */
/* If the matrix is rank deficient, a solution is returned having    */
/* rank non-nul components at positions corresponding to the columns */
/* with the largest norms.                                           */
/*                                                                   */
/*********************************************************************/
moremath_error_type RT_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *z)
{
	long							j, k;
	long							rank;
	double						sum;
	double						*c_perm;

	/* Create a vector for c with permutations. */
	c_perm = (double *)malloc(n*sizeof(double));

	if (!c_perm)
		return MOREMATH_OUT_OF_MEMORY;

	/* Determine the rank. */
	for (rank = n; rank > 0; rank--)
		if (diag[rank-1] != 0.0)
			break;

	/* Permute c. */
	for (j = 0; j < n; j++)
		c_perm[j] = c[perm[j]];

	/* Solve the triangular system R'z = c. Put zeros in the solution if
	 * the system is rank deficient. */
	for (k = 0; k < rank; k++)
	{
		/* Calculate the sum for parameters already determined. */
		sum = 0.0;
		for (j = 0; j < k; j++)
			sum += A[k][j] * z[j];

		/* Find the unknown parameter. */
		z[k] = (c_perm[k] - sum) / diag[k];
	}
	for (k = rank; k < n; k++)
		z[k] = 0.0;

	/* Free the c_perm vector. */
	free(c_perm);

	return MOREMATH_SUCCESS;
}


/*********************************************************************/
/*                                                                   */
/* rank_deficient_R_solve                                            */
/*                                                                   */
/* Solve the upper trapezoidal system R * x = c in the least squares */
/* sense.                                                            */
/*                                                                   */
/* Make the second step in the solution of a rank deficient linear   */
/* system of equations Ax = b from the QR factorization: solving the */
/* upper trapezoidal system R * x = c where c = inv(Q) * b in the    */
/* least squares sense. That is the solution having the smallest     */
/* norm. The function takes seven arguments:                         */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal);         */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   c      the inv(Q)*b vector;                                     */
/*   x      a vector to store the solution x.                        */
/* It returns a moremath_error_type, either:                         */
/*   MOREMATH_SUCCESS        the function succeeded;                 */
/*   MOREMATH_OUT_OF_MEMORY  a malloc failed and it was impossible   */
/*                           to perform the calculation.             */
/*                                                                   */
/*********************************************************************/
moremath_error_type rank_deficient_R_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *x)
{
	long									i, j;
	long									rank, rank_RT;
	double								**RT, *diagRT, *z;
	long									*permRT;
	moremath_error_type		return_value;

	/* Determine the rank. */
	for (rank = n; rank > 0; rank--)
		if (diag[rank-1] != 0.0)
			break;

	/* Create the R' matrix. */
	RT = (double **)malloc(rank*sizeof(double *));

	if (!RT)
		return MOREMATH_OUT_OF_MEMORY;

	for (j = 0; j < rank; j++)
	{
		RT[j] = (double *)malloc(n*sizeof(double));
		if (!RT[j])
		{
			for (j--; j >= 0; j--)
				free(RT[j]);
			free(RT);
			return MOREMATH_OUT_OF_MEMORY;
		}
	}

	/* Create vectors for the diagonal and permutations of the QR
	 * decomposition of the R' matrix and for intermediate results. */
	diagRT = (double *)malloc(rank*sizeof(double));
	permRT = (long *)malloc(rank*sizeof(long));
	z = (double *)malloc(n*sizeof(double));

	if (!diagRT || !permRT || !z)
	{
		return_value = MOREMATH_OUT_OF_MEMORY;
		goto finally;
	}

	/* Fill the R' matrix. */
	for (i = 0; i < rank; i++)
	{
		for (j = 0; j < i; j++)
			RT[i][j] = 0.0;
		RT[i][i] = diag[i];
		for (j = i+1; j < n; j++)
			RT[i][j] = A[j][i];
	}

	/* Calculate the QR decomposition of the R' matrix. */
	rank_RT = QR(rank, n, RT, diagRT, permRT, (double *)NULL);

	if (rank_RT == -1)
	{
		return_value = MOREMATH_OUT_OF_MEMORY;
		goto finally;
	}

	/* Solve the triangular system R(RT)'z = inv(Q)*b. */
	return_value = RT_solve(rank, n, RT, diagRT, permRT, c, z);

	if (return_value)
		goto finally;

	/* Pad the end of z with zeros. */
	for (j = rank; j < n; j++) z[j] = 0.0;

	/* Calculate inv(Q(RT)')*z. */
	Qb(rank, n, RT, diagRT, permRT, z);

	/* Replace in the right order. */
	for (j = 0; j < n; j++)
		x[perm[j]] = z[j];

	finally:

	/* Free the different tables and vectors that were internaly used. */
	for (j = 0; j < rank; j++)
		free(RT[j]);
	free(RT);
	free(diagRT);
	free(permRT);
	free(z);

	return return_value;
}


/*********************************************************************/
/*                                                                   */
/* QR_solve                                                          */
/*                                                                   */
/* Solve a linear system of equations using a QR factorization.      */
/*                                                                   */
/* Solve a linear system of equations Ax = b using the QR            */
/* factorization of a n by m matrix given by the QR function. The    */
/* function takes seven arguments:                                   */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal) and a    */
/*          factored form of the Q matrix;                           */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   b      the b vector, on exit, it is replaced by inv(Q)*b;       */
/*   x      a vector to store the solution x.                        */
/* It returns a moremath_error_type, either:                         */
/*   MOREMATH_SUCCESS        the function succeeded;                 */
/*   MOREMATH_OUT_OF_MEMORY  a malloc failed and it was impossible   */
/*                           to perform the calculation.             */
/*                                                                   */
/* If the system is rank deficient, the least squares solution is    */
/* found using further factorization. If this property is undesired, */
/* one should call QTb than R_solve.                                 */
/*                                                                   */
/*********************************************************************/
moremath_error_type QR_solve(const long n, const long m, double **A, double *diag, long *perm, double *b, double *x)
{
	/* The system
	 *   Ax = b
	 * is equivalent to
	 *   Rx = c
	 * where
	 *   c = inv(Q)b. */

	/* Calculate c = inv(Q) * b (c is stored in b). */
	QTb(n, m, A, diag, perm, b);

	/* If the system has full rank, simply solve the upper triangular
	 * system R * x = c. */
	if (diag[n-1] != 0.0)
		return R_solve(n, m, A, diag, perm, b, x);

	/* If the system does not have full rank, further factorization is
	 * necessary to obtain the least squares solution. */
	else
		return rank_deficient_R_solve(n, m, A, diag, perm, b, x);
}


/*********************************************************************/
/*                                                                   */
/* R_solve_with_update                                               */
/*                                                                   */
/* Update QR factorization and solve R * x = c for the updated       */
/* system.                                                           */
/*                                                                   */
/* Solve the augmented system of equations                           */
/*   A * x = b                                                       */
/*   D * x = 0                                                       */
/* where D is a diagonal n by n matrix using the R matrix and        */
/* c = inv(Q) * b of the original system. The function takes eight   */
/* arguments:                                                        */
/*   n, m   the number of columns and rows in the A matrix;          */
/*   A      a matrix containing R (except for its diagonal);         */
/*   diag   a vector containing the diagonal of the R matrix;        */
/*   perm   a vector containing the column permutations done during  */
/*          the QR factorization;                                    */
/*   c      the result of inv(Q) * b;                                */
/*   D      a vector containing the diagonal elements of the matrix  */
/*          D;                                                       */
/*   x      a vector to store the solution x.                        */
/* It returns a moremath_error_type, either:                         */
/*   MOREMATH_SUCCESS        the function succeeded;                 */
/*   MOREMATH_OUT_OF_MEMORY  a malloc failed and it was impossible   */
/*                           to perform the calculation.             */
/*                                                                   */
/* On exit, the R matrix (upper part of input A), its diagonal       */
/* elements (diag), perm and c are left intact to allow solutions    */
/* for other updates. However, the Q matrix (lower part of A         */
/* including diagonal) is replaced by the transpose of the updated R */
/* matrix.                                                           */
/*                                                                   */
/*********************************************************************/
moremath_error_type R_solve_with_update(const long n, const long m, double **A, double *diag, long *perm, double *c, double *D, double *x)
{
	long							i, j, k, row;
	double						*c_;
	double						*temp;
	double						ck;
	double						sin, cos, tan;
	double						v, w;
	double						sum;

	/* Allocate vectors to copy c and a temporary array of the row that
	 * is eliminated. */
	c_ = (double *)malloc(m*sizeof(double));
	temp = (double *)malloc(n*sizeof(double));

	if (!c_ || !temp)
	{
		free(c_);
		free(temp);

		return MOREMATH_OUT_OF_MEMORY;
	}

	/* Create a copy of the c vector. We will work on the copy to keep c
	 * intact for further updates. */
	for (i = 0; i < m; i++)
		c_[i] = c[i];

	/* The transpose of the updated R matrix is stored in the lower part
	 * of A, destroying the Q matrix. */
	for (i = 0; i < n; i++)
	{
		A[i][i] = diag[i];
		for (j = 0; j < i; j++)
			A[j][i] = A[i][j];
	}

	/* Update R with diagonal elements included in D. */
	for (i = 0; i < n; i++)
	{
		/* Determine on which row to operate using the permutation matrix. */
		row = perm[i];

		/* If the diagonal element is null, it's not necessary to eliminate
		 * it. */
		if (D[row] == 0.0) continue;

		/* Initialize the row to be eliminated. We don't care about the i
		 * first elements. */
		temp[i] = D[row];
		for (j = i+1; j < n; j++)
			temp[j] = 0.0;
		ck = 0.0;

		/* Do a serie of Givens rotation to elimate the diagonal element.
		 * Every rotation will only affect elements in columns at left of
		 * the currently eleminated element. */
		for (j = i; j < n; j++)
		{
			if (A[j][j] == 0.0)
			{
				sin = 1.0;
				cos = 0.0;
			}
			else if (fabs(temp[j]) >= fabs(A[j][j]))
			{
				tan = A[j][j]/temp[j];
				sin = 1.0/sqrt(1.0+tan*tan);
				cos = sin*tan;
			}
			else
			{
				tan = temp[j]/A[j][j];
				cos = 1.0/sqrt(1.0+tan*tan);
				sin = cos*tan;
			}

			for (k = j; k < n; k++)
			{
				v = A[j][k];
				w = temp[k];
				A[j][k] =  cos*v + sin*w;
				temp[k] = -sin*v + cos*w;
			}
			v = c_[j];
			w = ck;
			c_[j] =  cos*v + sin*w;
			ck    = -sin*v + cos*w;
		}
	}

	/* Solve the triangular system Rx = c. */
	for (k = n-1; k > -1; k--)
	{
		/* If the diagonal element of the A[k][k] matrix is null set the
		 * corresponding element of the solution to 0. */
		if (A[k][k] == 0.0)
		{
			temp[k] = 0.0;
			continue;
		}

		/* Calculate the sum for parameters already determined. */
		sum = 0.0;
		for (j = k+1; j < n; j++)
			sum += A[k][j] * temp[j];

		/* Find the unknown parameter. */
		temp[k] = (c_[k] - sum) / A[k][k];
	}

	/* Replace in the right order. */
	for (j = 0; j < n; j++)
		x[perm[j]] = temp[j];

	/* Free the different vectors that were internaly used. */
	free(c_);
	free(temp);

	return MOREMATH_SUCCESS;
}


#ifdef __cplusplus
}
#endif
