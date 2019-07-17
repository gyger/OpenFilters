/*
 *
 *  Newton_polynomials.cpp
 *
 *
 *  Linear, quadratic and cubic polynomials using Newton's method.
 *
 *  Copyright (c) 2006 Stephane Larouche.
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


#include "_moremath.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* Newton_linear                                                     */
/*                                                                   */
/* Get the linear polynomial passing by 2 points using Newton's      */
/* method.                                                           */
/*                                                                   */
/* The function takes three arguments:                               */
/*   X and Y                  lists containing x and y values;       */
/*   a                        a list to return the parameters of the */
/*                            equation.                              */
/* and returns no argument.                                          */
/*                                                                   */
/*********************************************************************/
void Newton_linear(const double *X, const double *Y, double *a)
{
	double						f_01;

	f_01 = (Y[1]-Y[0]) / (X[1]-X[0]);

	a[0] = Y[0] - f_01*X[0];
	a[1] = f_01;
}


/*********************************************************************/
/*                                                                   */
/* Newton_quadratic                                                  */
/*                                                                   */
/* Get the quadratic polynomial passing by 3 points using Newton's   */
/* method.                                                           */
/*                                                                   */
/* The function takes three arguments:                               */
/*   X and Y                  lists containing x and y values;       */
/*   a                        a list to return the parameters of the */
/*                            equation.                              */
/* and returns no argument.                                          */
/*                                                                   */
/*********************************************************************/
void Newton_quadratic(const double *X, const double *Y, double *a)
{
	double						f_01, f_12;
	double						f_012;

	f_01 = (Y[1]-Y[0]) / (X[1]-X[0]);
	f_12 = (Y[2]-Y[1]) / (X[2]-X[1]);
	f_012 = (f_12-f_01) / (X[2]-X[0]);

	a[0] = Y[0] - f_01*X[0] + f_012*X[0]*X[1];
	a[1] = f_01 - f_012*(X[0]+X[1]);
	a[2] = f_012;
}


/*********************************************************************/
/*                                                                   */
/* Newton_cubic                                                      */
/*                                                                   */
/* Get the cubic polynomial passing by 4 points using Newton's       */
/* method.                                                           */
/*                                                                   */
/* The function takes three arguments:                               */
/*   X and Y                  lists containing x and y values;       */
/*   a                        a list to return the parameters of the */
/*                            equation.                              */
/* and returns no argument.                                          */
/*                                                                   */
/*********************************************************************/
void Newton_cubic(const double *X, const double *Y, double *a)
{
	double						f_01, f_12, f_23;
	double						f_012, f_123;
	double						f_0123;

	f_01 = (Y[1]-Y[0]) / (X[1]-X[0]);
	f_12 = (Y[2]-Y[1]) / (X[2]-X[1]);
	f_23 = (Y[3]-Y[2]) / (X[3]-X[2]);
	f_012 = (f_12-f_01) / (X[2]-X[0]);
	f_123 = (f_23-f_12) / (X[3]-X[1]);
	f_0123 = (f_123-f_012) / (X[3]-X[0]);

	a[0] = Y[0] - f_01*X[0] + f_012*X[0]*X[1] - f_0123*X[0]*X[1]*X[2];
	a[1] = f_01 - f_012*(X[0]+X[1]) + f_0123*(X[0]*X[1]+X[0]*X[2]+X[1]*X[2]);
	a[2] = f_012 - f_0123*(X[0]+X[1]+X[2]);
	a[3] = f_0123;
}


#ifdef __cplusplus
}
#endif
