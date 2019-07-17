/*
 *
 *  Levengerg_Marquardt.cpp
 *
 *  Fit a non-linear equation using the Levengerg-Marquardt algorithm.
 *
 *  Copyright (c) 2004-2009,2012-2014 Stephane Larouche.
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


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt                                               */
/*                                                                   */
/* Fit a curve by the Levenberg-Marquardt method                     */
/*                                                                   */
/* This class implements a trust region version of the Levenberg-    */
/* Marquardt algorithm.                                              */
/*                                                                   */
/* To fit a curve using the Levenberg-Marquardt method, you must:    */
/*   1 - Initialize the method by providing the appropriate          */
/*       functions and targets to fit;                               */
/*   2 - Set stopping criteria;                                      */
/*   3 - Set limits to parameter values, if desired;                 */
/*   4 - Set inequalities on targets, if desired;                    */
/*	 5 - Prepare for optimization;                                   */
/*   6 - Iterate until a satisfactory solution is found.             */
/*                                                                   */
/* See the description of the various methods of this class for an   */
/* explanation on how to do these steps.                             */
/*                                                                   */
/* This algorithm was first proposed by Marquardt in                 */
/*   D. Marquardt, "An algorithm for least squares estimation on     */
/*   nonlinear parameters", SIAM J. Appl. Math., vol. 11, 1963,      */
/*   pp. 431-441.                                                    */
/*                                                                   */
/* Basic information about the least square problem and a simple     */
/* description of the Levenberg-Marquardt algorithm can be found in  */
/*   Press et al., Numerical Recipes in C: the Art of Scientific     */
/*   Computing, 2nd edition, Cambridge University Press, 1997,       */
/*   pp. 681-688.                                                    */
/*                                                                   */
/* The algorithm used in this file is described in                   */
/*   Jorge J. Moré, "The Levenberg-Marquardt algorithm,              */
/*   implementation and theory", Numerical Analysis, edited by G. A. */
/*   Watson, Lecture  Notes in Mathematics, vol. 630, Springer-      */
/*   Verlag, 1977, pp. 105-116                                       */
/* and is inspired by MINPACK (http://www.netlib.org/minpack/).      */
/*                                                                   */
/*********************************************************************/



/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::Levenberg_Marquardt                          */
/*                                                                   */
/* Initialize the Levenberg-Marquardt algorithm                      */
/*                                                                   */
/* This method takes 6 arguments:                                    */
/*   nb_par            the number of parameters;                     */
/*   nb_points         the number of points;                         */
/*   callback          a Levenberg_Marquardt_callback instance       */
/*                     implementing functions that return the values */
/*                     of the function that we fit and the jacobian  */
/*                     according to a list of parameters;            */
/*   a                 starting values of the parameters of the      */
/*                     function to be fitted;                        */
/*   Yi                a list of the values of y to which the        */
/*                     function must be fitted;                      */
/*   sigma             a list of the weights to give to the y        */
/*                     points.                                       */
/*                                                                   */
/*********************************************************************/
Levenberg_Marquardt::Levenberg_Marquardt(const long nb_par, const long nb_points, const Levenberg_Marquardt_callback *callback, double *a, const double *Yi, const double *sigma)
	:	nb_par(nb_par),
		nb_points(nb_points),
		nb_rows(std::max(nb_par, nb_points)),
		callback(callback),
		a(a),
		Yi(Yi),
		sigma(sigma),
		nb_free_par(nb_par),
		iteration(0),
		nb_f_eval(0),
		nb_df_eval(0),
		previous_a(NULL),
		Y(NULL),
		dY(NULL),
		Delta(0.0),
		alpha(0.0),
		factor(0.01),
		A(NULL),
		b(NULL),
		beta(NULL),
		da(NULL),
		D(NULL),
		alpha_D(NULL),
		use_par(NULL),
		column_norms(NULL),
		scaled_da(NULL),
		temp_array(NULL),
		use_point(NULL),
		diag(NULL),
		perm(NULL),
		min_gradient(0.0),
		acceptable_chi_2(0.0),
		min_chi_2_change(0.0),
		chi_2(0.0),
		norm_gradient(0.0),
		norm_scaled_a(0.0),
		a_min(NULL),
		a_max(NULL),
		inequalities(NULL)
{
	long																par, i;

	try
	{
		this->previous_a = new double[this->nb_par];
		this->A = new double*[this->nb_par];
		for (par = 0; par < this->nb_par; par++)
			this->A[par] = NULL;
		for (par = 0; par < this->nb_par; par++)
			this->A[par] = new double[this->nb_rows];
		this->b = new double[this->nb_rows];
		this->beta = new double[this->nb_par];
		this->da = new double[this->nb_par];
		this->D = new double[this->nb_par];
		this->alpha_D = new double[this->nb_par];
		this->use_par = new bool[this->nb_par];
		this->column_norms = new double[this->nb_par];
		this->scaled_da = new double[this->nb_par];
		this->temp_array = new double[this->nb_par];
		this->use_point = new bool[this->nb_points];
		this->diag = new double[this->nb_par];
		this->perm = new long[this->nb_par];
		this->a_min = new double[this->nb_par];
		this->a_max = new double[this->nb_par];
		this->inequalities = new char[this->nb_points];
	}
	catch (const std::bad_alloc&)
	{
		delete[] this->previous_a;
		if (this->A)
			for (par = 0; par < this->nb_par; par++)
				delete[] this->A[par];
		delete[] this->A;
		delete[] this->b;
		delete[] this->beta;
		delete[] this->da;
		delete[] this->D;
		delete[] this->alpha_D;
		delete[] this->use_par;
		delete[] this->column_norms;
		delete[] this->scaled_da;
		delete[] this->temp_array;
		delete[] this->use_point;
		delete[] this->diag;
		delete[] this->perm;
		delete[] this->a_min;
		delete[] this->a_max;
		delete[] this->inequalities;

		throw;
	}

	/* By default, all parameters are used and they are not bounded. */
	for (par = 0; par < this->nb_par; par++)
	{
		this->use_par[par] = true;
		this->a_min[par] = -INFINITY;
		this->a_max[par] = +INFINITY;
	}

	/* By default, all targets are equalities. */
	for (i = 0; i < this->nb_points; i++)
	{
		this->inequalities[i] = EQUAL;
	}
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::~Levenberg_Marquardt                         */
/*                                                                   */
/*********************************************************************/
Levenberg_Marquardt::~Levenberg_Marquardt()
{
	long																par;

	delete[] this->previous_a;
	for (par = 0; par < this->nb_par; par++)
		delete[] this->A[par];
	delete[] this->A;
	delete[] this->b;
	delete[] this->beta;
	delete[] this->da;
	delete[] this->D;
	delete[] this->alpha_D;
	delete[] this->use_par;
	delete[] this->column_norms;
	delete[] this->scaled_da;
	delete[] this->temp_array;
	delete[] this->diag;
	delete[] this->perm;
	delete[] this->a_min;
	delete[] this->a_max;
	delete[] this->inequalities;
}



/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::set_stop_criteria                            */
/*                                                                   */
/* Set stop criteria                                                 */
/*                                                                   */
/* This method takes 3 arguments:                                    */
/*   min_gradient      the criteria to determine if the value of the */
/*                     gradient is zero;                             */
/*   acceptable_chi_2  the value of chi_2 for an acceptable fit (it  */
/*                     can be set to 0 to avoid stopping of the      */
/*                     fit);                                         */
/*   min_chi_2_change  the minimum relative change in chi_2 (it can  */
/*                     be set to 0 to avoid stopping of the fit).    */
/*                                                                   */
/*********************************************************************/
void Levenberg_Marquardt::set_stop_criteria(const double min_gradient, const double acceptable_chi_2, const double min_chi_2_change)
{
	this->min_gradient = min_gradient;
	this->acceptable_chi_2 = acceptable_chi_2;
	this->min_chi_2_change = min_chi_2_change;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::set_limits                                   */
/*                                                                   */
/* Set limits to fitted parameters                                   */
/*                                                                   */
/* This method takes two arguments:                                  */
/*   a_min and a_max   lists of minimum and maximum acceptable       */
/*                     values of the parameters (use NULL for no     */
/*                     limit).                                       */
/*                                                                   */
/*********************************************************************/
void Levenberg_Marquardt::set_limits(const double *a_min, const double *a_max)
{
	long																par;

	if (a_min == NULL)
		for (par = 0; par < this->nb_par; par++)
			this->a_min[par] = -INFINITY;
	else
		for (par = 0; par < this->nb_par; par++)
			this->a_min[par] = a_min[par];
	if (a_max == NULL)
		for (par = 0; par < this->nb_par; par++)
			this->a_max[par] = +INFINITY;
	else
		for (par = 0; par < this->nb_par; par++)
				this->a_max[par] = a_max[par];
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::set_inequalities                             */
/*                                                                   */
/* Set targets to inequalities                                       */
/*                                                                   */
/* This method takes one argument:                                   */
/*   inequalities      list describing if targets are equalities or  */
/*                     inequalities (use NULL for all equalities).   */
/*                                                                   */
/*********************************************************************/
void Levenberg_Marquardt::set_inequalities(const char *inequalities)
{
	long																i;

	if (inequalities == NULL)
		for (i = 0; i < this->nb_points; i++)
			this->inequalities[i] = EQUAL;

	else
		for (i = 0; i < this->nb_points; i++)
			this->inequalities[i] = inequalities[i];
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::prepare                                      */
/*                                                                   */
/* Prepare for optimization                                          */
/*                                                                   */
/* This method simply calculates chi square before the first         */
/* iteration.                                                        */
/*                                                                   */
/* This method takes no argument and returns no argument.            */
/*                                                                   */
/*********************************************************************/
void Levenberg_Marquardt::prepare()
{
	long																i;

	/* Get Y. */
	this->Y = this->callback->f(this->a);
	this->nb_f_eval += 1;

	/* Build b. */
	for (i = 0; i < this->nb_points; i++)
		this->b[i] = (this->Yi[i]-this->Y[i])/this->sigma[i];

	/* Determine which points are used considering the inequalities. */
	for (i = 0; i < this->nb_points; i++)
	{
		if (this->inequalities[i] == SMALLER && this->b[i] > 0.0)
			this->use_point[i] = false;
		else if (this->inequalities[i] == LARGER && this->b[i] < 0.0)
			this->use_point[i] = false;
		else
			this->use_point[i] = true;
	}

	/* Calculate chi square. */
	this->chi_2 = 0.0;
	for (i = 0; i < this->nb_points; i++)
		if (this->use_point[i])
			this->chi_2 += this->b[i]*this->b[i];
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::iterate                                      */
/*                                                                   */
/* Do one iteration of the Levenberg-Marquardt algorithm             */
/*                                                                   */
/* This method takes no arguments. It returns a single argument      */
/* giving the status of the solution. Possible values are:           */
/*   IMPROVING                 the solution is improving;            */
/*   MINIMUM_FOUND             the gradient is null (or close        */
/*                             enough);                              */
/*   CHI_2_IS_OK               the value of chi square is            */
/*                             acceptable;                           */
/*   CHI_2_CHANGE_TOO_SMALL    the change in chi square is small;    */
/*   ALL_PARAMETERS_ARE_STUCK  all the parameters are stuck at the   */
/*                             limits.                               */
/* When this method returns, MINIMUM_FOUND, CHI_2_IS_OK              */
/* CHI_2_CHANGE_TOO_SMALL or ALL_PARAMETERS_ARE_STUCK, the calling   */
/* function should stop the fit.                                     */
/*                                                                   */
/* This method throws a std::bad_alloc if the return value of one of */
/* the functions doing QR factorization indicates that it ran out of */
/* memory.                                                           */
/*                                                                   */
/*********************************************************************/
int Levenberg_Marquardt::iterate()
{
	long																i, internal_iteration;
	long																par;
	long																rank;
	double															norm, norm_scaled_da, norm_square, sum;
	double															u, l, phi;
	double															correction;
	double															temp;
	double															new_chi_2, actual_reduction, predicted_reduction;
	double															part1, part2, gamma, rho, mu;
	bool																bounded;
	moremath_error_type									return_value;

	this->iteration += 1;

	/* Keep a copy of the old parameter values in case we need to revert
	 * to them. */
	for (par = 0; par < this->nb_par; par++)
		this->previous_a[par] = this->a[par];

	/* Build b. */
	for (i = 0; i < this->nb_points; i++)
		this->b[i] = (this->Yi[i]-this->Y[i])/this->sigma[i];

	/* Determine which points are used considering the inequalities. */
	for (i = 0; i < this->nb_points; i++)
	{
		if (this->inequalities[i] == SMALLER && this->b[i] > 0.0)
			this->use_point[i] = false;
		else if (this->inequalities[i] == LARGER && this->b[i] < 0.0)
			this->use_point[i] = false;
		else
			this->use_point[i] = true;
	}

	/* Get the derivative at this point. */
	this->dY = this->callback->df(this->a);
	this->nb_df_eval += 1;

	/* Calculate the gradient. */
	for (par = 0; par < this->nb_par; par++)
	{
		this->beta[par] = 0.0;
		for (i = 0; i < this->nb_points; i++)
			if (this->use_point[i])
				this->beta[par] += (this->Yi[i]-this->Y[i])/(this->sigma[i]*this->sigma[i]) * this->dY[par][i];
	}

	/* If a parameter is stuck at one of its limits, remove it from the
	 * fit. */
	this->nb_free_par = this->nb_par;
	for (par = 0; par < this->nb_par; par++)
	{
		if (this->a[par] == this->a_min[par] && this->beta[par] < 0.0)
		{
			this->use_par[par] = false;
			this->beta[par] = 0.0;
			this->nb_free_par -= 1;
		}
		else if (this->a[par] == this->a_max[par] && this->beta[par] > 0.0)
		{
			this->use_par[par] = false;
			this->beta[par] = 0.0;
			this->nb_free_par -= 1;
		}
		else
		{
			this->use_par[par] = true;
		}
	}

	if (this->nb_free_par == 0) return ALL_PARAMETERS_ARE_STUCK;

	/* Calculate the norm of the gradient. */
	this->norm_gradient = 0.0;
	for (par = 0; par < this->nb_par; par++)
		this->norm_gradient += this->beta[par]*this->beta[par];
	this->norm_gradient = sqrt(this->norm_gradient);

	/* Check if the minimum is reached (norm of the gradient is 0). */
	if (this->norm_gradient < this->min_gradient) return MINIMUM_FOUND;

	/* Build the jacobian matrix. */
	for (par = 0; par < this->nb_par; par++)
	{
		if (this->use_par[par])
		{
			for (i = 0; i < this->nb_points; i++)
			{
				if (this->use_point[i])
					this->A[par][i] = this->dY[par][i]/this->sigma[i];
				else
					this->A[par][i] = 0.0;
			}
			for (i = this->nb_points; i < this->nb_par; i++)
				this->A[par][i] = 0.0;
		}
		else
		{
			for (i = 0; i < this->nb_rows; i++)
				this->A[par][i] = 0.0;
		}
	}

	/* Factorize the system using QR factorization. */
	rank = QR(this->nb_par, this->nb_rows, this->A, this->diag, this->perm, this->column_norms);

	if (rank == -1) throw std::bad_alloc();

	/* Calculate inv(Q)*b. */
	QTb(this->nb_par, this->nb_rows, this->A, this->diag, this->perm, this->b);

	/* On the first iteration, initialize D and the trust region to a
	 * fraction of the scaled length of a. And calculate the norm of a
	 * for a first time. */
	if (this->iteration == 1)
	{
		for (par = 0; par < this->nb_par; par++)
		{
			this->D[par] = this->column_norms[par];;
			if (this->D[par] == 0.0)
				this->D[par] = 1.0;
		}

		norm = 0.0;
		for (par = 0; par < this->nb_par; par++)
		{
			temp = this->D[par]*this->a[par];
			norm += temp*temp;
		}
		norm = sqrt(norm);
		this->Delta = this->factor * norm;
		if (this->Delta == 0.0)
			this->Delta = this->factor;

		/* Calculate the norm of the scaled a. This is used to check if
		 * Delta gets too small. */
		this->norm_scaled_a = 0.0;
		for (par = 0; par < this->nb_par; par++)
		{
			temp = this->D[par]*this->a[par];
			this->norm_scaled_a += temp*temp;
		}
		this->norm_scaled_a = sqrt(this->norm_scaled_a);
	}

	/* Update D if the norm of the columns has increased. */
	for (par = 0; par < this->nb_par; par++)
		this->D[par] = std::max(this->D[par], this->column_norms[par]);

	/* Iterate until a an improving step is found. */
	while(true)
	{
		/* Compute the Gauss-Newton iteration. Here, and in the rest of
		 * the method, the matrix will be considerer to have full rank
		 * if the rank is equal to the number of free parameters. This
		 * works because the QR method ignores rows with null norms. */
		if (rank == this->nb_free_par)
			return_value = R_solve(this->nb_par, this->nb_rows, this->A, this->diag, this->perm, this->b, this->da);
		else
			return_value = rank_deficient_R_solve(this->nb_par, this->nb_rows, this->A, this->diag, this->perm, this->b, this->da);

		if (return_value == MOREMATH_OUT_OF_MEMORY) throw std::bad_alloc();

		/* Calculate the norm of the scaled Gauss-Newton step. */
		norm_scaled_da = 0.0;
		for (par = 0; par < this->nb_par; par++)
		{
			this->scaled_da[par] = this->D[par]*this->da[par];
			norm_scaled_da += this->scaled_da[par]*this->scaled_da[par];
		}
		norm_scaled_da = sqrt(norm_scaled_da);

		/* If the Gauss-Newton step is accepted, set the Levenberg-
		 * Marquardt parameter to 0. */
		phi = norm_scaled_da - this->Delta;
		if (phi <= 0.1*this->Delta)
		{
			this->alpha = 0.0;
		}

		/* Otherwise, search the Levenberg-Marquardt parameter for which
		 * phi = 0. */
		else
		{
			/* Set the lower bound of alpha to -phi(0)/phi'(0). If the
			 * matrix is rank deficient, set the lower bound to 0. */
			if (rank == this->nb_free_par)
			{
				for (par = 0; par < this->nb_par; par++)
					this->temp_array[par] = this->D[this->perm[par]] * (this->scaled_da[this->perm[par]]/norm_scaled_da);

				norm_square = 0.0;
				for (par = 0; par < this->nb_par; par++)
				{
					if (this->use_par[this->perm[par]])
					{
						sum = 0.0;
						for (i = 0; i < par; i++) sum += this->temp_array[i] * this->A[par][i];
						this->temp_array[par] = (this->temp_array[par] - sum) / this->diag[par];
						norm_square += this->temp_array[par]*this->temp_array[par];
					}
				}

				l = ( phi / this->Delta ) / norm_square;
			}

			else
			{
				l = 0.0;
			}

			/* Choose an upper bound. The upper bound is norm([J inv(D)]'b)
			 * = norm(inv(D) R' Q'b). We already have Q'b, so let's use it. */
			norm = 0.0;
			for (par = 0; par < this->nb_par; par++)
			{
				if (this->use_par[this->perm[par]])
				{
					temp = this->diag[par]*this->b[par];
					for (i = 0; i < par; i++) temp += this->A[par][i]*this->b[i];
					temp /= this->D[this->perm[par]];
					norm += temp*temp;
				}
			}
			norm = sqrt(norm);
			u = norm / this->Delta;

			/* If alpha is outside bounds, set it to the closest bound. */
			this->alpha = std::max(this->alpha, l);
			this->alpha = std::min(this->alpha, u);

			/* Guess an appropriate starting value for alpha. */
			if (this->alpha == 0.0) this->alpha = norm / norm_scaled_da;

			/* Search for a maximum of 10 iterations. */
			for (internal_iteration = 0; internal_iteration < 10; internal_iteration++)
			{
				/* Protect ourselves against very small values of alpha (in
				 * particular 0. */
				if (this->alpha == 0.0)
					this->alpha = 0.001 * u;

				/* Compute the step for the current value of alpha. */
				for (par = 0; par < this->nb_par; par++)
				{
					if (this->use_par[par])
						this->alpha_D[par] = sqrt(this->alpha) * this->D[par];
					else
						this->alpha_D[par] = 0.0;
				}

				return_value = R_solve_with_update(this->nb_par, this->nb_rows, this->A, this->diag, this->perm, this->b, this->alpha_D, this->da);

				if (return_value == MOREMATH_OUT_OF_MEMORY) throw std::bad_alloc();

				/* Calculate the norm of the scaled step. */
				norm_scaled_da = 0.0;
				for (par = 0; par < this->nb_par; par++)
				{
					this->scaled_da[par] = this->D[par]*this->da[par];
					norm_scaled_da += this->scaled_da[par]*this->scaled_da[par];
				}
				norm_scaled_da = sqrt(norm_scaled_da);
				phi = norm_scaled_da - this->Delta;

				/* If phi is small enough, accept the step. */
				if (fabs(phi) <= 0.1*this->Delta)
					break;

				for (par = 0; par < this->nb_par; par++)
					this->temp_array[par] = this->D[this->perm[par]] * (this->scaled_da[this->perm[par]]/norm_scaled_da);

				/* Calculate the correction. */
				norm_square = 0.0;
				for (par = 0; par < this->nb_par; par++)
				{
					if (this->use_par[this->perm[par]])
					{
						sum = 0.0;
						for (i = 0; i < par; i++)
							sum += this->temp_array[i] * this->A[i][par];
						this->temp_array[par] = (this->temp_array[par] - sum) / this->A[par][par];
						norm_square += this->temp_array[par]*this->temp_array[par];
					}
				}

				correction = ( phi / this->Delta ) / norm_square;

				/* Change the bounds according to the sign of phi. */
				if (phi > 0.0)
					l = std::max(l, this->alpha);
				else
					u = std::min(u, this->alpha);

				this->alpha = std::max(this->alpha+correction, l);
			}
		}

		/* Change the parameters a by the amount suggested by da. */
		for (par = 0; par < this->nb_par; par++)
			this->a[par] += this->da[par];

		/* Check if parameters fell outside of acceptable range. Change
		 * both da and a since we want to be able to compare expected and
		 * predicted results. */
		bounded = false;
		for (par = 0; par < this->nb_par; par++)
		{
			if (this->a[par] < this->a_min[par])
			{
				this->da[par] += this->a_min[par] - this->a[par];
				this->a[par] = this->a_min[par];
				bounded = true;
			}
			else if (this->a[par] > this->a_max[par])
			{
				this->da[par] += this->a_max[par] - this->a[par];
				this->a[par] = this->a_max[par];
				bounded = true;
			}
		}

		/* If one of the parameter was bounded during this iteration,
		 * recalculate the scaled norm of da. */
		if (bounded)
		{
			norm_scaled_da = 0.0;
			for (par = 0; par < this->nb_par; par++)
			{
				this->scaled_da[par] = this->D[par]*this->da[par];
				norm_scaled_da += this->scaled_da[par]*this->scaled_da[par];
			}
			norm_scaled_da = sqrt(norm_scaled_da);
		}

		/* Evaluation the function at the new point. */
		this->Y = this->callback->f(this->a);
		this->nb_f_eval += 1;

		/* Calculate chi_2. */
		new_chi_2 = 0.0;
		for (i = 0; i < this->nb_points; i++)
		{
			if (this->inequalities[i] == SMALLER && this->Y[i] < this->Yi[i])
				continue;
			else if (this->inequalities[i] == LARGER && this->Y[i] > this->Yi[i])
				continue;
			temp = (this->Yi[i]-this->Y[i])/this->sigma[i];
			new_chi_2 += temp*temp;
		}

		/* Calculate the normalized actual reduction. */
		actual_reduction = 1.0 - (new_chi_2 / this->chi_2);

		/* Calculate the normalized predicted reduction of chi square and
		 * gamma. */
		part1 = 0.0;
		for (i  = 0; i < this->nb_points; i++)
		{
			if (this->use_point[i])
			{
				temp = 0.0;
				for (par = 0; par < this->nb_par; par++)
					if (this->use_par[par])
						temp += this->dY[par][i]*this->da[par]/this->sigma[i];
				part1 += temp*temp;
			}
		}
		part1 /= this->chi_2;

		part2 = this->alpha * norm_scaled_da * norm_scaled_da / this->chi_2;

		predicted_reduction = part1 + 2.0*part2;
		gamma = - (part1 + part2);

		/* Compare the actual and the predicted reduction. */
		rho = actual_reduction/predicted_reduction;

		/* If the ratio is low (or negative), reduce the trust region. */
		if (rho <= 0.25)
		{
			if (actual_reduction >= 0.0)
				mu = 0.5*gamma / (gamma + 0.5*actual_reduction);
			else
				mu = 0.5;

			if ( 0.1 * new_chi_2 >= this->chi_2 || mu < 0.1 )
				mu = 0.1;

			this->Delta = mu * std::min(this->Delta, 10.0 * norm_scaled_da);
			this->alpha /= mu;
		}

		/* If the ratio is high, augment the trust region. */
		else if (rho >= 0.75 || this->alpha == 0.0)
		{
			this->Delta = 2.0 * norm_scaled_da;
			this->alpha *= 0.5;
		}

		/* If there has been improvement, accept the solution and verify if
		 * one of the stopping criteria is met. */
		if (new_chi_2 < this->chi_2)
		{
			this->chi_2 = new_chi_2;

			/* Calculate the norm of the scaled a. This is used to check if
			 * Delta gets too small. */
			this->norm_scaled_a = 0.0;
			for (par = 0; par < this->nb_par; par++)
			{
				temp = this->D[par]*this->a[par];
				this->norm_scaled_a += temp*temp;
			}
			this->norm_scaled_a = sqrt(this->norm_scaled_a);

			/* Verify if one of the stop criteria is met, but don't stop
			 * after a short step if it is the result of one of the bounds. */
			if (this->chi_2 <= this->acceptable_chi_2)
				return CHI_2_IS_OK;
			else if (!bounded && actual_reduction < this->min_chi_2_change && predicted_reduction < this->min_chi_2_change)
				return CHI_2_CHANGE_TOO_SMALL;

			return IMPROVING;
		}

		/* Otherwise revert to the previous solution and try again. */
		else
		{
			for (par = 0; par < this->nb_par; par++)
				this->a[par] = this->previous_a[par];

			/* If Delta is smaller than the machine precision, we cannot do
			 * any better! */
			if (this->norm_scaled_a == 0.0)
			{
				if (this->Delta < DBL_EPSILON)
					return DELTA_IS_TOO_SMALL;
			}
			else if (this->Delta/this->norm_scaled_a < DBL_EPSILON)
			{
				return DELTA_IS_TOO_SMALL;
			}
		}
	}
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::get_correlation_matrix                       */
/*                                                                   */
/* Get the correlation matrix                                        */
/*                                                                   */
/* This method takes no arguments and simply return the value of     */
/* correlation matrix between the various parameters. When the norm  */
/* of a column is zero, all correlation elements related to it are   */
/* undefined and set to zero (including the diagonal element).       */
/*                                                                   */
/*********************************************************************/
double ** Levenberg_Marquardt::get_correlation_matrix()
{
	long																i;
	long																par, par_1, par_2;
	double															*sums = NULL, *sums_squares = NULL;
	double															**C = NULL;
	double															temp, a, b, numerator;
	double															ab, denominator;

	/* Make the necessary structures. */
	try
	{
		sums = new double[this->nb_par];
		sums_squares = new double [this->nb_par];
		C = new double*[this->nb_par];
		for (par = 0; par < this->nb_par; par++)
			C[par] = NULL;
		for (par = 0; par < this->nb_par; par++)
			C[par] = new double[this->nb_par];
	}
	catch (const std::bad_alloc&)
	{
		delete[] sums;
		delete[] sums_squares;
		if (C)
			for (par = 0; par < this->nb_par; par++)
				delete[] C[par];
		delete[] C;

		throw;
	}

	/* Determine which points are used considering the inequalities. */
	for (i = 0; i < this->nb_points; i++)
	{
		if (this->inequalities[i] == SMALLER && this->b[i] > 0.0)
			this->use_point[i] = false;
		else if (this->inequalities[i] == LARGER && this->b[i] < 0.0)
			this->use_point[i] = false;
		else
			this->use_point[i] = true;
	}

	/* Get the derivatives matrix. */
	this->dY = this->callback->df(this->a);

	for (par = 0; par < this->nb_par; par++)
	{
		sums[par] = 0.0;
		sums_squares[par] = 0.0;
		for (i = 0; i < this->nb_points; i++)
		{
			if (this->use_point[i])
			{
				temp = this->dY[par][i] / this->sigma[i];
				sums[par] += temp;
				sums_squares[par] += temp * temp;
			}
		}
	}

	/* Calculate cross products. */
	for (par_1 = 0; par_1 < this->nb_par; par_1++)
	{
		for (par_2 = par_1; par_2 < this->nb_par; par_2++)
		{
			C[par_1][par_2] = 0.0;
			for (i = 0; i < this->nb_points; i++)
				if (this->use_point[i])
					C[par_1][par_2] += (this->dY[par_1][i]/this->sigma[i])*(this->dY[par_2][i]/this->sigma[i]);
		}
	}

	/* Calculate the covariance. */
	for (par_1 = 0; par_1 < this->nb_par; par_1++)
	{
		a = this->nb_points*sums_squares[par_1] - sums[par_1]*sums[par_1];

		for (par_2 = par_1; par_2 < this->nb_par; par_2++)
		{
			b = this->nb_points*sums_squares[par_2] - sums[par_2]*sums[par_2];
			numerator = this->nb_points*C[par_1][par_2] - sums[par_1]*sums[par_2];

			/* Catch all kinds of problems including overflows, division by
			 * zero or ab being numerically negative. */
			ab = a*b;
			if (ab - ab != 0.0) {C[par_1][par_2] = C[par_2][par_1] = 0.0; continue;}
			if (ab <= 0.0) {C[par_1][par_2] = C[par_2][par_1] = 0.0; continue;}
			denominator = sqrt(ab);
			if (denominator == 0.0) {C[par_1][par_2] = C[par_2][par_1] = 0.0; continue;}
			C[par_1][par_2] = C[par_2][par_1] = numerator/denominator;
		}
	}

	delete[] sums;
	delete[] sums_squares;

	return C;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::get_chi_2                                    */
/*                                                                   */
/* Get the value of chi square                                       */
/*                                                                   */
/* This method takes no arguments and simply return the value of     */
/* chi square.                                                       */
/*                                                                   */
/*********************************************************************/
double Levenberg_Marquardt::get_chi_2() const
{
	return this->chi_2;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::get_norm_gradient                            */
/*                                                                   */
/* Get the norm of the gradient                                      */
/*                                                                   */
/* This method takes no arguments and simply return the norm of the  */
/* gradient.                                                         */
/*                                                                   */
/*********************************************************************/
double Levenberg_Marquardt::get_norm_gradient() const
{
	return this->norm_gradient;
}


/*********************************************************************/
/*                                                                   */
/* Levenberg_Marquardt::get_stats                                    */
/*                                                                   */
/* Get the value of some statistics.                                 */
/*                                                                   */
/* This method takes 2 arguments:                                    */
/*   nb_f_eval               a pointer to a long to store the number */
/*                           of function evaluation done during the  */
/*                           fit;                                    */
/*   nb_df_eval              a pointer to a long to store the number */
/*                           of jacobian evaluation done during the  */
/*                           fit.                                    */
/*                                                                   */
/*********************************************************************/
void Levenberg_Marquardt::get_stats(long *nb_f_eval, long *nb_df_eval) const
{
	*nb_f_eval = this->nb_f_eval;
	*nb_df_eval = this->nb_df_eval;
}
