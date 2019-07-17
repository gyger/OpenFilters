/*
 *
 *  interpolation.cpp
 *
 *
 *  Functions to perform interpolation. This file implements the cubic
 *  spline method and functions to search an ordered table.
 *
 *  The cubic spline implementation is an adaptation of the GNU
 *  Scientific Library (GSL) (http://sources.redhat.com/gsl/) spline
 *  and tridiagonal matrix routines.
 *
 *  For more informations about the method to search an ordered table,
 *  see Press et al., Numerical Recipes in C: the Art of Scientific
 *  Computing, 2nd edition, Cambridge University Press, 1997, pp.
 *  117-119.
 *
 *  GSL source code for the spline:
 *    Copyright (c) 1996, 1997, 1998, 1999, 2000 Gerard Jungman.
 *    Copyright (c) 1996, 1997, 1998, 1999, 2000, 2002 Gerard Jungman,
 *    Brian Gough, David Necas.
 *
 *  Copyright (c) 2002-2003,2005,2006,2013,2014 Stephane Larouche.
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

#include "_moremath.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_spline                                                        */
/*                                                                   */
/* Create a new spline structure                                     */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length             the number of points defining the spline;    */
/* and returns a pointer to the new spline structure.                */
/*                                                                   */
/*********************************************************************/
spline_type * new_spline(const long length)
{
  spline_type				*spline;

	spline = (spline_type *)malloc(sizeof(spline_type));

	if (!spline) return NULL;

	spline->length = length;
  spline->c = (double *)malloc(length*sizeof(double));
  spline->offdiag = (double *)malloc((length-2)*sizeof(double));
  spline->diag = (double *)malloc((length-2)*sizeof(double));
  spline->g = (double *)malloc((length-2)*sizeof(double));
  spline->solution = spline->c+1;

	spline->gamma = (double *)malloc((length-2)*sizeof(double));
	spline->alpha = (double *)malloc((length-2)*sizeof(double));
	spline->cc = (double *)malloc((length-2)*sizeof(double));
	spline->z = (double *)malloc((length-2)*sizeof(double));

	if (!spline->c || !spline->offdiag || !spline->diag || !spline->g || !spline->gamma || !spline->alpha || !spline->cc || !spline->z)
	{
		del_spline(spline);
		return NULL;
	}

  return spline;
}


/*********************************************************************/
/*                                                                   */
/* del_spline                                                        */
/*                                                                   */
/* Delete a spline structure                                        */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   spline            a pointer to the spline structure to delete.  */
/*                                                                   */
/*********************************************************************/
void del_spline(spline_type *spline)
{
	free(spline->c);
	free(spline->offdiag);
	free(spline->diag);
	free(spline->g);

	free(spline->gamma);
	free(spline->alpha);
	free(spline->cc);
	free(spline->z);

	free(spline);
}


/*********************************************************************/
/*                                                                   */
/* init_spline                                                       */
/*                                                                   */
/* Initialize the spline structure                                   */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   spline            a pointer to the spline structure to          */
/*                     initialize;                                   */
/*   xa, ya            arrays of the x and y values to initialize    */
/*                     the spline, the x values must be in           */
/*                     increasing order.                             */
/* It then solves the system of equations defined by those points    */
/* using Cholesky decomposition. This function does not make a copy  */
/* of xa and ya, they should not be deleted or modified by the       */
/* caller.                                                           */
/*                                                                   */
/*********************************************************************/
void init_spline(spline_type *spline, const double *xa, const double *ya)
{
  long					i, j;
  long					num_points = spline->length;
  long					max_index = num_points - 1;	/* Engeln-Mullges + Uhlig "n" */
  long					sys_size = max_index - 1;   /* linear system is sys_size * sys_size */

	double				h_i;
	double				h_ip1;
	double				ydiff_i;
	double				ydiff_ip1;

  spline->xa = xa;
  spline->ya = ya;

  spline->c[0] = 0.0;
  spline->c[max_index] = 0.0;

  for (i = 0; i < sys_size; i++)
	{
		h_i   = spline->xa[i + 1] - spline->xa[i];
		h_ip1 = spline->xa[i + 2] - spline->xa[i + 1];
		ydiff_i   = spline->ya[i + 1] - spline->ya[i];
		ydiff_ip1 = spline->ya[i + 2] - spline->ya[i + 1];
		spline->offdiag[i] = h_ip1;
		spline->diag[i] = 2.0 * (h_ip1 + h_i);
		spline->g[i] = 3.0 * (ydiff_ip1 / h_ip1  -  ydiff_i / h_i);
	}

	/* Cholesky decomposition
	 * A = L.D.L^t
	 * lower_diag(L) = gamma
	 * diag(D) = alpha */
	spline->alpha[0] = spline->diag[0];
	spline->gamma[0] = spline->offdiag[0] / spline->alpha[0];

	for (i = 1; i < sys_size - 1; i++)
	{
		spline->alpha[i] = spline->diag[i] - spline->offdiag[i-1]*spline->gamma[i-1];
		spline->gamma[i] = spline->offdiag[i] / spline->alpha[i];
	}

	if (sys_size > 1)
	{
		spline->alpha[sys_size-1] = spline->diag[sys_size-1] - spline->offdiag[sys_size-2]*spline->gamma[sys_size-2];
	}

	/* update RHS */
	spline->z[0] = spline->g[0];
	for (i = 1; i < sys_size; i++)
	{
		spline->z[i] = spline->g[i] - spline->gamma[i-1]*spline->z[i-1];
	}
	for (i = 0; i < sys_size; i++)
	{
		spline->cc[i] = spline->z[i] / spline->alpha[i];
	}

	/* backsubstitution */
	spline->solution[sys_size-1] = spline->cc[sys_size-1];
	if (sys_size >= 2)
	{
		for (i = sys_size - 2, j = 0; j <= sys_size - 2; j++, i--)
		{
			spline->solution[i] = spline->cc[i] - spline->gamma[i] * spline->solution[(i+1)];
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* evaluate_spline                                                   */
/*                                                                   */
/* Evaluate the spline at a series of points                         */
/*                                                                   */
/* Before calling this function, the spline must have been           */
/* initialized. This function takes 5 arguments:                     */
/*   spline            a pointer to the spline structure;            */
/*   x                 an array of the x values at which to evaluate */
/*                     the spline;                                   */
/*   y                 an array in which to write the values         */
/*                     calculated using the spline;                  */
/*   indices           an array of indices indicating in which       */
/*                     intervals of the original data the values of  */
/*                     x are located                                 */
/*   length            the length of x, y and indices arrays.        */
/*                                                                   */
/*********************************************************************/
void evaluate_spline(const spline_type *spline, const double *x, double *y, const long *indices, const long length)
{
	double x_lo, x_hi, y_lo, y_hi;
	double dx, dy;
	double delx;
	long i;
	long index;
	long last_index = -1;
	double c_ip1;
	double b_i, c_i, d_i;

	for (i = 0; i < length; i++)
	{
		index = indices[i];

		/* We expect the data in the x array to be ordered, most of the
		 * time the index won't change and it is possible to save some time
		 * by not calculating the coefficients. */
		if (index != last_index)
		{
			x_hi = spline->xa[index + 1];
			x_lo = spline->xa[index];
			dx = x_hi - x_lo;
      y_lo = spline->ya[index];
      y_hi = spline->ya[index + 1];
      dy = y_hi - y_lo;

			/* Common coefficient determination. */
			c_i = spline->c[index];
			c_ip1 = spline->c[index + 1];
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0;
			d_i = (c_ip1 - c_i) / (3.0 * dx);

			last_index = index;
		}

		/* Evaluate. */
		delx = x[i] - x_lo;
		y[i] = y_lo + delx * (b_i + delx * (c_i + delx * d_i));
	}
}


/*********************************************************************/
/*                                                                   */
/* evaluate_spline_derivative                                        */
/*                                                                   */
/* Evaluate the derivative of the spline at a series of points       */
/*                                                                   */
/* Before calling this function, the spline must have been           */
/* initialized. This function takes 5 arguments:                     */
/*   spline            a pointer to the spline structure;            */
/*   x                 an array of the x values at which to evaluate */
/*                     the spline;                                   */
/*   dery              an array in which to write the derivatives    */
/*                     calculated using the spline;                  */
/*   indices           an array of indices indicating in which       */
/*                     intervals of the original data the values of  */
/*                     x are located                                 */
/*   length            the length of x, dery and indices arrays.     */
/*                                                                   */
/*********************************************************************/
void evaluate_spline_derivative(const spline_type *spline, const double *x, double *dery, const long *indices, const long length)
{
	double x_lo, x_hi, y_lo, y_hi;
	double dx, dy;
	double delx;
	long i;
	long index;
	long last_index = -1;
	double c_ip1;
	double b_i, c_i, d_i;

	for (i = 0; i < length; i++)
	{
		index = indices[i];

		/* I expect the data in the x array to be ordered, most of the time
		 * the index won't change and it is possible to save some time by
		 * not calculating the coefficients. */
		if (index != last_index)
		{
			x_hi = spline->xa[index + 1];
			x_lo = spline->xa[index];
			dx = x_hi - x_lo;
      y_lo = spline->ya[index];
      y_hi = spline->ya[index + 1];
      dy = y_hi - y_lo;

			/* Common coefficient determination. */
			c_i = spline->c[index];
			c_ip1 = spline->c[index + 1];
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0;
			d_i = (c_ip1 - c_i) / (3.0 * dx);

			last_index = index;
		}

		/* Evaluate. */
		delx = x[i] - x_lo;
		dery[i] = b_i + delx * (2.0*c_i + delx * 3.0*d_i);
	}
}


/*********************************************************************/
/*                                                                   */
/* evaluate_spline_inverse                                           */
/*                                                                   */
/* Evaluate the inverse of the spline at a series of points.         */
/*                                                                   */
/* This function allows to find the values of x corresponding to y   */
/* values. Before calling it, the spline must have been initialized. */
/* This function takes 5 arguments:                                  */
/*   spline            a pointer to the spline structure;            */
/*   x                 an array in which to write the values of x    */
/*                     determined using the spline;                  */
/*   y                 an array of the y values at which to evaluate */
/*                     the inverse of the spline;                    */
/*   indices           an array of indices indicating in which       */
/*                     intervals of the original data the values of  */
/*                     y are located                                 */
/*   length            the length of x, y and indices arrays.        */
/*                                                                   */
/*********************************************************************/
void evaluate_spline_inverse(const spline_type *spline, double *x, const double *y, const long *indices, const long length)
{
	double x_lo, x_hi, y_lo, y_hi;
	double dx, dy;
	double delx;
	long i;
	long index;
	long last_index = -1;
	double c_ip1;
	double b_i, c_i, d_i;
	double roots[3];
	int nb_roots;

	for (i = 0; i < length; i++)
	{
		index = indices[i];

		/* I expect the data in the x array to be ordered, most of the time
		 * the index won't change and it is possible to save some time by
		 * not calculating the coefficients. */
		if (index != last_index)
		{
			x_hi = spline->xa[index + 1];
			x_lo = spline->xa[index];
			dx = x_hi - x_lo;
      y_lo = spline->ya[index];
      y_hi = spline->ya[index + 1];
      dy = y_hi - y_lo;

			/* Common coefficient determination. */
			c_i = spline->c[index];
			c_ip1 = spline->c[index + 1];
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0;
			d_i = (c_ip1 - c_i) / (3.0 * dx);

			last_index = index;
		}

		nb_roots = roots_cubic(roots, y_lo-y[i], b_i, c_i, d_i);

		/* Find one solution in the interval. */
		if (nb_roots > 0 && roots[0] >= 0.0 && roots[0] <= dx) delx = roots[0];
		else if (nb_roots > 1 && roots[1] >= 0.0 && roots[1] <= dx) delx = roots[1];
		else if (nb_roots > 2 && roots[2] >= 0.0 && roots[2] <= dx) delx = roots[2];

		/* If no solution is in the interval, we take the closest end. This
		 * should not happen, but numerically, the root might be just out
		 * of the interval. */
		else if ((y[i]-y_lo)/dy < 0.5) delx = 0.0;
		else delx = dx;

		x[i] = x_lo + delx;
	}
}


/*********************************************************************/
/*                                                                   */
/* locate                                                            */
/*                                                                   */
/* Search an ordered table                                           */
/*                                                                   */
/* Locate in what interval of an ordered table X the value x is      */
/* located. This function takes two arguments:                       */
/*   X    a list of ordered values in increasing order;              */
/*   x    the value to localize.                                     */
/* It returns the position of the interval in which x is located by  */
/* the index of the lower value bonding the interval in which x is   */
/* located. It returns -1 or length-1 if x is outsite of X.          */
/*                                                                   */
/*********************************************************************/
long locate(const double *X, const long length, const double x)
{
	long				lim_inf, lim_sup;
	long				middle;

	/* If x falls out of X, return immediatly. */
	if (x < X[0]) return -1;
	if (x > X[length-1]) return length-1;

	/* Otherwise, perform bissection. */
	lim_inf = 0;
	lim_sup = length - 1;
	while (lim_sup-lim_inf > 1)
	{
		middle = (lim_sup+lim_inf)/2;
		if (x <= X[middle]) lim_sup = middle;
		else lim_inf = middle;
	}

	return lim_inf;
}


#ifdef __cplusplus
}
#endif
