/*
 *
 *  PCHIP.cpp
 *
 *
 *  Class to interpolate using piecewise cubic hermite interpolating
 *  polynomials that allows preservation of monotonicity.
 *
 *  Copyright (c) 2014 Stephane Larouche.
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
#include <cfloat>
#include <stdexcept>

#include "_abeles.h"


/*********************************************************************/
/*                                                                   */
/* PCHIP_error                                                       */
/*                                                                   */
/* Exception derived class for PCHIP errors                          */
/*                                                                   */
/*********************************************************************/
PCHIP_error::PCHIP_error() : std::runtime_error("PCHIP error") {}
PCHIP_error::PCHIP_error(std::string const& message) : std::runtime_error("PCHIP error: " + message) {}


/*********************************************************************/
/*                                                                   */
/* PCHIP                                                             */
/*                                                                   */
/* Interpolate a function using piecewise cubic hermite              */
/* interpolating polynomials                                         */
/*                                                                   */
/* This class implements the piecewise cubic hermite interpolating   */
/* polynomial (PCHIP) algorithm as described in                      */
/*  James M. Hyman, "Accurate Monotonicity Preserving Cubic          */
/*  Interpolation", SIAM J. Sci. and Stat. Comput., vol. 4, 1983,    */
/*  pp. 645–654.                                                     */
/*                                                                   */
/* It allows the preservation of the monoticity of the interpolated  */
/* function.                                                         */
/*                                                                   */
/*********************************************************************/


/*********************************************************************/
/*                                                                   */
/* PCHIP::PCHIP                                                      */
/*                                                                   */
/* Initialize the PCHIP algorithm                                    */
/*                                                                   */
/* This method takes between 3 and 5 arguments:                      */
/*   nb_points              the number of points in the data;        */
/*   xa, ya                 list of x and y values of the data       */
/*                          points used for interpolation, the       */
/*                          values of x must be in increasing order; */
/*   preserve_monotonicity  (optional) a boolean indicating if the   */
/*                          monotonocity should be preserved         */
/*                          (default is false);                      */
/*   allow_extrapolation    (optional) a boolesn indicating if       */
/*                          extrapolation should be allowed (default */
/*                          is false).                               */
/* Both lists must be of the same length. This class does not make a */
/* copy of xa and ya. This class calculates the interpolant the      */
/* first time evaluate, evaluate_derivative, or evaluate_inverse are */
/* called. Before that, xa and ya can be modified without problems.  */
/* If they are modified later, the caller should call the reset      */
/* method before using one of the evaluate methods.                  */
/*                                                                   */
/* This method may throw a std::bad_alloc or PCHIP_error exception.  */
/*                                                                   */
/*********************************************************************/
PCHIP::PCHIP(const long nb_points, double const * const xa, double const * const ya, const bool preserve_monotonicity, const bool allow_extrapolation)
	:	nb_points(nb_points),
	  xa(xa),
		ya(ya),
		preserve_monotonicity(preserve_monotonicity),
		allow_extrapolation(allow_extrapolation),
		a0(NULL),
		a1(NULL),
		a2(NULL),
		a3(NULL),
		prepared(false),
		dx(NULL),
		S(NULL)
{
	/* It is impossible to interpolate with a single point. */
	if (this->nb_points == 1)
		throw PCHIP_error("Cannot interpolate with a single point");

	try
	{
		this->a1 = new double[this->nb_points];
		this->a2 = new double[this->nb_points-1];
		this->a3 = new double[this->nb_points-1];
		this->dx = new double[this->nb_points-1];
		this->S = new double[this->nb_points-1];
	}
	catch (const std::bad_alloc&)
	{
		delete[] this->a1;
		delete[] this->a2;
		delete[] this->a3;
		delete[] this->dx;
		delete[] this->S;

		throw;
	}
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::~PCHIP                                                     */
/*                                                                   */
/*********************************************************************/
PCHIP::~PCHIP()
{
	delete[] this->a1;
	delete[] this->a2;
	delete[] this->a3;
	delete[] this->dx;
	delete[] this->S;
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::reset                                                      */
/*                                                                   */
/* Reset the PCHIP algorithm                                         */
/*                                                                   */
/* This method can be used to reset the PCHIP algorithm after the    */
/* values of xa and ya have been modified. This method takes up to 2 */
/* arguments:                                                        */
/*   xa, ya                 (optional) lists of x and y values of    */
/*                          the data points used for interpolation,  */
/*                          the values of x must be in increasing    */
/*                          order.                                   */
/* If arguments are used, they replace existing lists. In their      */
/* absence, the lists previously given to the class are used, but    */
/* are assumed to have changed. The length of the lists must not be  */
/* different from the number of points given to the constructor.     */
/*                                                                   */
/*********************************************************************/
void PCHIP::reset(double const * const xa, double const * const ya)
{
	if (xa) this->xa = xa;
	if (ya) this->ya = ya;

	this->prepared = false;
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::prepare                                                    */
/*                                                                   */
/* Prepare the PCHIP instance                                        */
/*                                                                   */
/* This private method calculates all the polynomial coefficients    */
/* used to evaluate the PCHIP. It does not take any argument.        */
/*                                                                   */
/*********************************************************************/
void PCHIP::prepare()
{
	double															*df = this->a1, *dx = this->dx, *S = this->S;
	long																i;
	double															S_min, S_max;

	/* Special case for 2 data points. */
	if (this->nb_points == 2)
	{
		this->a0 = this->ya;
		this->a1[0] = this->a1[1] = (this->ya[1]-this->ya[0])/(this->xa[1]-this->xa[0]);
		this->a2[0] = 0.0;
		this->a3[0] = 0.0;

		return;
	}

	for (i = 0; i < this->nb_points-1; i++)
	{
		dx[i] = xa[i+1]-this->xa[i];
		S[i] = (this->ya[i+1]-this->ya[i])/dx[i];
	}

	/* Parabolic approximation for df. */
	df[0] = ((2.0*dx[0]+dx[1])*S[0]-dx[0]*S[1])/(dx[0]+dx[1]);
	for (i = 1; i < this->nb_points-1; i++)
		df[i] = (dx[i-1]*S[i]+dx[i]*S[i-1])/(dx[i-1]+dx[i]);
	df[this->nb_points-1] = ((2.0*dx[this->nb_points-2]+dx[this->nb_points-3])*S[this->nb_points-2]-dx[this->nb_points-2]*S[this->nb_points-3])/(dx[this->nb_points-2]+dx[this->nb_points-3]);

	/* If requested, limit df to make sure monotonicity is preserved. */
	if (this->preserve_monotonicity)
	{
		if (S[0] > 0.0)
			df[0] = std::min(std::max(0.0, df[0]), 3.0*S[0]);
		else if (S[0] < 0.0)
			df[0] = std::max(std::min(0.0, df[0]), 3.0*S[0]);
		else
			df[0] = 0.0;

		for (i = 1; i < this->nb_points-1; i++)
		{
			S_min = std::min(S[i-1], S[i]);
			S_max = std::max(S[i-1], S[i]);

			if (S_min > 0.0)
				df[i] = std::min(std::max(0.0, df[i]), 3.0*S_min);
			else if (S_max < 0.0)
				df[i] = std::max(std::min(0.0, df[i]), 3.0*S_max);
			else if (df[i] >= 0.0)
				df[i] = std::min(std::max(0.0, df[i]), 3.0*std::min(std::abs(S[i-1]), std::abs(S[i])));
			else
				df[i] = std::max(std::min(0.0, df[i]), -3.0*std::min(std::abs(S[i-1]), std::abs(S[i])));
		}

		if (S[this->nb_points-2] > 0.0)
			df[this->nb_points-1] = std::min(std::max(0.0, df[this->nb_points-1]), 3.0*S[this->nb_points-2]);
		else if (S[this->nb_points-2] < 0.0)
			df[this->nb_points-1] = std::max(std::min(0.0, df[this->nb_points-1]), 3.0*S[this->nb_points-2]);
		else
			df[this->nb_points-1] = 0.0;
	}

	/* Calculate the factors on the piecewise polynomial. */
	this->a0 = this->ya;
	this->a1 = df;
	for (i = 0; i < this->nb_points-1; i++)
	{
		this->a2[i] = (3.0*S[i]-df[i+1]-2.0*df[i])/dx[i];
		this->a3[i] = -(2.0*S[i]-df[i+1]-df[i])/(dx[i]*dx[i]);
	}

	this->prepared = true;
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::evaluate                                                   */
/*                                                                   */
/* Evaluate the function according the the interpolation             */
/*                                                                   */
/* This method takes 3 or 4 arguments:                               */
/*   length            the length of the x array                     */
/*   x                 an array of the x values at which to evaluate */
/*                     the function;                                 */
/*   y                 an array in which to store the values         */
/*                     calculated using the interpoaltion.           */
/*   indices           (optional) an array of the position of the x  */
/*                     values inside the interpolation points. If    */
/*                     not given, this method will calculate it      */
/*                     itself.                                       */
/*                                                                   */
/* This method may throw a PCHIP_error exception.                    */
/*                                                                   */
/*********************************************************************/
void PCHIP::evaluate(const long length, double const * const x, double * const y, long const * const indices)
{
	long  															index;
	double															dx;

	if (!this->prepared) this->prepare();

	for (long i = 0; i < length; i++)
	{
		if (indices) index = indices[i];
		else index = locate(this->nb_points, this->xa, x[i], this->allow_extrapolation);

		dx = x[i] - this->xa[index];
		y[i] = this->a0[index] + dx * (this->a1[index] + dx * (this->a2[index] + dx * this->a3[index]));
	}
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::evaluate_derivative                                        */
/*                                                                   */
/* Evaluate the derivative of the function according to the          */
/* interpolation                                                     */
/*                                                                   */
/* This method takes 3 or 4 arguments:                               */
/*   length            the length of the x array                     */
/*   x                 an array of the x values at which to evaluate */
/*                     the function;                                 */
/*   y                 an array in which to store the derivatives    */
/*                     calculated using the interpolation;           */
/*   indices           (optional) an array of the position of the x  */
/*                     values inside the interpolation points. If    */
/*                     not given, this method will calculate it      */
/*                     itself.                                       */
/*                                                                   */
/* This method may throw a PCHIP_error exception.                    */
/*                                                                   */
/*********************************************************************/
void PCHIP::evaluate_derivative(const long length, double const * const x, double * const dy, long const * const indices)
{
	long  															i, index;
	double															dx;

	if (!this->prepared) this->prepare();

	for (i = 0; i < length; i++)
	{
		if (indices) index = indices[i];
		else index = locate(this->nb_points, this->xa, x[i], this->allow_extrapolation);

		dx = x[i] - this->xa[index];
		dy[i] = this->a1[index] + dx * (2.0*this->a2[index] + dx * 3.0*this->a3[index]);
	}
}


/*********************************************************************/
/*                                                                   */
/* PCHIP::evaluate_inverse                                           */
/*                                                                   */
/* Evaluate the inverse of the PCHIP at a series of points           */
/*                                                                   */
/* This method allows to find the values of x corresponding to y     */
/* values. This method takes 3 or 4 arguments:                       */
/*   length            the length of the x array                     */
/*	 y                 an array of the y values at which to evaluate */
/*                     the inverse of the PCHIP;                     */
/*   x                 an array in which to write the values of x    */
/*                     determined using the PCHIP.                   */
/*   indices           (optional) an array of the position of the x  */
/*                     values inside the interpolation points. If    */
/*                     not given, this method will calculate it      */
/*                     itself.                                       */
/*                                                                   */
/* The values of ya used when creating the PCHIP must be             */
/* monotonically increasing to use this method (the method does not  */
/* check they are).                                                  */
/*                                                                   */
/* This method may throw a PCHIP_error exception.                    */
/*                                                                   */
/*********************************************************************/
void PCHIP::evaluate_inverse(const long length, double const * const y, double * const x, long const * const indices)
{
	long																index;
	double															a0, a1, a2, a3;
	double															x_, y_, x_l, y_l, x_h, y_h, dy_;

	if (!this->prepared) this->prepare();

	/* We find the roots using the Newton method, secured by bounds to
	 * make sure it does not diverge. For details, see
	 *   Press et al., Numerical Recipes in C: the Art of Scientific
	 *   Computing, 2nd edition, Cambridge University Press, 1997,
	 *   pp. 362-368.
	 *
	 * We don't use the analytical approach because it is unstable when
	 * the third order coefficient is close to 0, which happens
	 * regularly. */

	for (long i = 0; i < length; i++)
	{
		if (indices) index = indices[i];
		else index = locate(this->nb_points, this->ya, y[i], this->allow_extrapolation);

		/* Get end points. */
		x_l = 0.0;
		y_l = this->ya[index]-y[i];

		x_h = this->xa[index+1] - this->xa[index];
		y_h = this->ya[index+1]-y[i];

		/* Get the coefficients of the polynomial. */
		a0 = y_l;
		a1 = this->a1[index];
		a2 = this->a2[index];
		a3 = this->a3[index];

		/* Choose the end point with the smallest value as the starting
		 * point. */
		if (-y_l < y_h)
		{
			x_ = x_l;
			y_ = y_l;
		}
		else
		{
			x_ = x_h;
			y_ = y_h;
		}

		while (y_)
		{
			/* Determine derivative and approximate root using Newton step. */
			dy_ = a1 + x_ * (2.0*a2 + x_*3.0*a3);
			if (dy_) x_ = x_ - y_/dy_;

			/* If the Newton approximation is outside of the bounds, perform
			 * bisection. */
			if (dy_ == 0.0 || x_ <= x_l || x_ >= x_h)
				x_ = 0.5*(x_l+x_h);

			/* Calculate the new value. */
			y_ = a0 + x_ * (a1 + x_ * (a2 + x_ * a3));

			/* Replace the limit according to the sign of the value. */
			if (y_ < 0.0)
			{
				x_l = x_;
				y_l = y_;
			}
			else
			{
				x_h = x_;
				y_h = y_;
			}

			/* If the difference between the bounds is (numerically) null,
			 * terminate loop. */
			if ((x_h - x_l) <= (x_l + x_h) * DBL_EPSILON) break;
		}

		x[i] = this->xa[index]+x_;
	}
}


/*********************************************************************/
/*                                                                   */
/* locate                                                            */
/*                                                                   */
/* Search an ordered table                                           */
/*                                                                   */
/* Locate in what interval of an ordered table X the value x is      */
/* located. This function takes 4 arguments:                         */
/*   length                 the length of X;                         */
/*   X                      a list of ordered values in increasing   */
/*                          order;                                   */
/*   x                      the value to localize;                   */
/*   allow_extrapolation    a boolean indicating if extrapolation is */
/*                          allowed                                  */
/* It returns the position of the interval in which x is located by  */
/* the index of the lower value bonding the interval in which x is   */
/* located. If x is outsite of X, it will raturn the first or the    */
/* last interval if allow_extrapolation is True, or throws a         */
/* PCHIP_error if allow_extrapolation is false.                      */
/*                                                                   */
/* This function may throw a PCHIP_error exceptions.                 */
/*                                                                   */
/*********************************************************************/
long locate(const long length, const double *X, const double x, bool allow_extrapolation)
{
	long				lim_inf, lim_sup;
	long				middle;

	/* If x falls out of X, return immediatly. */
	if (x < X[0])
	{
		if (allow_extrapolation) return 0;
		else throw PCHIP_error("Extrapolation not allowed");
	}
	if (x > X[length-1])
	{
		if (allow_extrapolation) return length-2;
		else throw PCHIP_error("Extrapolation not allowed");
	}

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
