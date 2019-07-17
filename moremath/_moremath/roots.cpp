/*
 *
 *  roots.cpp
 *
 *
 *  Calculate real roots of linear, quadratic and cubic polynomials.
 *
 *  Copyright (c) 2005,2007,2013,2014 Stephane Larouche.
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


#include <cmath>

#include "_moremath.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* roots_linear                                                      */
/*                                                                   */
/* Find the root of a linear polynomial                              */
/*                                                                   */
/* The function takes three arguments:                               */
/*   *roots                  a pointer to a double to store the      */
/*                           root;                                   */
/*   a_0 and a_1             the coefficients of the polynomial;     */
/* and returns the number of roots found.                            */
/*                                                                   */
/*********************************************************************/
int roots_linear(double *roots, const double a_0, const double a_1)
{

	/* If the polynomial is of order 0, there is no root. */
	if (a_1 == 0.0) return 0;

	roots[0] = -a_0/a_1;

	return 1;
}


/*********************************************************************/
/*                                                                   */
/* roots_quadratic                                                   */
/*                                                                   */
/* Find the real roots of a quadratic polynomial                     */
/*                                                                   */
/* The function takes four arguments:                                */
/*   *roots                  a pointer to a double vector to store   */
/*                           the roots;                              */
/*   a_0, a_1, and a_2       the coefficients of the polynomial;     */
/* and returns the number of roots found. If the polynomial is       */
/* quadratic and the two roots are identical, both are returned and  */
/* the function returns 2 to distinguish this result from the linear */
/* case.                                                             */
/*                                                                   */
/*********************************************************************/
int roots_quadratic(double *roots, const double a_0, const double a_1, const double a_2)
{
	double			discriminant;
	double			sqrt_discriminant;

	/* If a_2 is 0, the polynomial is not quadratic. */
	if (a_2 == 0.0) return roots_linear(roots, a_0, a_1);

	discriminant = a_1*a_1 - 4.0*a_2*a_0;

	/* If the determinant is negative, the is no real roots. */
	if (discriminant < 0.0) return 0;

	/* If the discriminant is 0, there is a two identical real roots. */
	if (discriminant == 0.0)
	{
		roots[0] = roots[1] = -0.5 * a_1/a_2;

		return 2;
	}

	/* If the discriminant is positive, there is two different real roots.
	 * Depending on the sign of a_1, we use different formula to avoid
	 * numerical instatility coming from cancelation (see David Goldberg,
	 * "What Every Computer Scientist Should Know About Floating-Point
	 * Arithmetic", ACM Computing Surveys, vol 23, 1991, pp. 5-48 for
	 * details). */
	sqrt_discriminant = sqrt(discriminant);
	if (a_1 >= 0.0)
	{
		roots[0] = -2.0 * a_0 / (a_1+sqrt_discriminant);
		roots[1] = -0.5 * (a_1+sqrt_discriminant) / a_2;
	}
	else
	{
		roots[0] = 0.5 * (-a_1+sqrt_discriminant) / a_2;
		roots[1] = 2.0 * a_0 / (-a_1+sqrt_discriminant);
	}

	return 2;
}


/*********************************************************************/
/*                                                                   */
/* roots_cubic                                                       */
/*                                                                   */
/* Find the real roots of a cubic polynomial                         */
/*                                                                   */
/* The function takes five arguments:                                */
/*   *roots                  a pointer to a double vector to store   */
/*                           the roots;                              */
/*   a_0, a_1, a_2, and a_3  the coefficients of the polynomial;     */
/* and returns the number of roots found. If two of the roots are    */
/* identical, both are returned and the function returns 3 to        */
/* distinguish this result from the quadratic case. However, if      */
/* there is only one root, the function returns 1.                   */
/*                                                                   */
/*********************************************************************/
int roots_cubic(double *roots, const double a_0, const double a_1, const double a_2, const double a_3)
{
	double			discriminant;
	double			p, q;
	double			alpha, beta;
	double			root_alpha, root_beta;
	double			cos_theta, theta;
	double			temp_1, temp_2;

	/* If a_3 is 0, the polynomial is not cubic. */
	if (a_3 == 0.0) return roots_quadratic(roots, a_0, a_1, a_2);

	/* Calculate the roots of the cubic polynomial. See Standard
	 * Mathematical Tables and Formulae, 30th Edition, Daniel Zwillinger,
	 * ed, CRC Press, 1996, p.82. */

	p = (3.0*a_3*a_1-a_2*a_2)/(9.0*a_3*a_3);
	q = (2.0*a_2*a_2*a_2-9.0*a_3*a_2*a_1+27.0*a_3*a_3*a_0)/(27.0*a_3*a_3*a_3);

	/* A special case when p and q are null. */
	if (p == 0.0 && q == 0.0)
	{
		roots[0] = roots[1] = roots[2] = -a_2/(3.0*a_3);
		return 3;
	}

	discriminant = 4.0*p*p*p + q*q;

	/* If the discriminant is positive, there is only one real root.
	 * Special treatment must be done since pow(x,y) doesn't handle
	 * negative x values. */
	if (discriminant > 0.0)
	{
		if (q >= 0.0)
		{
			beta = -0.5*(q + sqrt(discriminant));
			alpha = -p*p*p/beta;
		}
		else
		{
			alpha = 0.5*(sqrt(discriminant) - q);
			beta = -p*p*p/alpha;
		}

		if (alpha >= 0) root_alpha = pow(alpha, 1.0/3.0);
		else root_alpha = -pow(-alpha, 1.0/3.0);
		if (beta >= 0) root_beta = pow(beta, 1.0/3.0);
		else root_beta = -pow(-beta, 1.0/3.0);

		roots[0] = root_alpha + root_beta - a_2/(3.0*a_3);

		return 1;
	}

	/* If the discriminant is null, there is three real roots, of which
	 * two are equal. If the discriminant is negative, there are three
	 * different real roots. To work with real numbers, we calculate them
	 * by the trigonometric solution. */

	/* A quick check to be sure that we don't fall out of acos range
	 * because of numerical errors. */
	cos_theta = -0.5*q/sqrt(-p*p*p);
	if (cos_theta < -1.0) cos_theta = -1.0;
	else if (cos_theta > 1.0) cos_theta = 1.0;

	theta = acos(cos_theta);

	/* The 3 solutions. */
	temp_1 = 2.0*sqrt(-p);
	temp_2 = a_2/(3.0*a_3);
	roots[0] = temp_1 * cos(theta/3.0) - temp_2;
	roots[1] = temp_1 * cos((theta + 2.0*M_PI)/3.0) - temp_2;
	roots[2] = temp_1 * cos((theta + 4.0*M_PI)/3.0) - temp_2;

	return 3;
}


#ifdef __cplusplus
}
#endif
