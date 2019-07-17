/*
 *
 *  _moremath.h
 *
 *
 *  Header file for functions and structures of the moremath DLL.
 *
 *  Copyright (c) 2006-2009,2012,2013 Stephane Larouche.
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


#ifndef __MOREMATH
#define __MOREMATH


/* Error codes and error type. */
typedef enum
{
	MOREMATH_SUCCESS = 0,
	MOREMATH_OUT_OF_MEMORY
} moremath_error_type;


#ifdef __cplusplus
extern "C" {
#endif


/* Functions and structures from interpolation.cpp. */

typedef struct
{
  long						length;
  const double		*xa;
  const double		*ya;
  double					*c;
  double					*offdiag;
  double					*diag;
  double					*g;
  double					*solution;
	/* Variables for the tridiagonal algorigthm. */
	double					*gamma;
	double					*alpha;
	double					*cc;
	double					*z;
} spline_type;

/* Cubic spline. */
spline_type * new_spline(const long length);
void del_spline(spline_type *spline);
void init_spline(spline_type *spline, const double *xa, const double *ya);
void evaluate_spline(const spline_type *spline, const double *x, double *y, const long *indices, const long length);
void evaluate_spline_derivative(const spline_type *spline, const double *x, double *dery, const long *indices, const long length);
void evaluate_spline_inverse(const spline_type *spline, double *x, const double *y, const long *indices, const long length);

/* Search an ordered table. */
long locate(const double *X, const long length, const double x);


/* Constants and classes for and from Levenberg_Marquardt.cpp. */

const int IMPROVING = 0;
const int MINIMUM_FOUND = 1;
const int CHI_2_IS_OK = 2;
const int CHI_2_CHANGE_TOO_SMALL = 3;
const int DELTA_IS_TOO_SMALL = 4;
const int ALL_PARAMETERS_ARE_STUCK = 5;
const int SINGULAR_MATRIX = -1;

const char SMALLER = -1;
const char EQUAL = 0;
const char LARGER = 1;

class Levenberg_Marquardt_callback
{
	public:

	virtual ~Levenberg_Marquardt_callback() {};
	virtual double const * const f(double const * const pars) const = 0;
	virtual double const ** const df(double const * const pars) const = 0;
};

class Levenberg_Marquardt
{
	private:

	const long													nb_par, nb_points, nb_rows;
	const Levenberg_Marquardt_callback	*callback;
	double															*a;
	const double												*Yi, *sigma;
	/* Usually, all parameters are allowed to vary. But if some
	 * parameters are bounded, the will be fixed when they hit
	 * their bounds. */
	long																nb_free_par;
	/* The number of iterations, function and jacobian evaluations. */
	long																iteration, nb_f_eval, nb_df_eval;
	/* A list to keep old value of a. */
	double															*previous_a;
	/* Variables for the values returned by f and df. */
	const double												*Y, **dY;
	/* Delta is the trust region and alpha is the Levenberg-Marquard
	 * parameter. The trust region is automatically selected on the
	 * first iteration and the Levenberg-Marquard parameter alpha is
	 * used to keep steps smaller than Delta. */
	double															Delta, alpha;
	/* Trust region. */
	double															factor;
	/* alpha matrix, beta, da, D and use. */
	double															**A, *b;
	double															*beta, *da, *D, *alpha_D;
	bool																*use_par;
	double															*column_norms, *scaled_da, *temp_array;
	bool																*use_point;
	/* Variables for the QR factorization. */
	double															*diag;
	long																*perm;
	/* The stop criteria. By default, there is no stop criteria. */
	double															min_gradient, acceptable_chi_2, min_chi_2_change;
	/* chi_2 is the sum of the squared residuals. The norm of the
	 * gradient is kept if the user want's to know it. The norm of the
	 * scaled parameter vector. */
	double															chi_2, norm_gradient, norm_scaled_a;
	/* Parameter bounds. */
	double															*a_min, *a_max;
	/* [In]equalities. */
	char																*inequalities;

	public:

	Levenberg_Marquardt(const long nb_par, const long nb_points, const Levenberg_Marquardt_callback *callback, double *a, const double *Yi, const double *sigma);
	~Levenberg_Marquardt();
	void set_stop_criteria(const double min_gradient, const double acceptable_chi_2, const double min_chi_2_change);
	void set_limits(const double *a_min, const double *a_max);
	void set_inequalities(const char *inequalities);
	void prepare();
	int iterate();
	double ** get_correlation_matrix();
	double get_chi_2() const;
	double get_norm_gradient() const;
	void get_stats(long *nb_f_eval, long *nb_df_eval) const;
};


/* Functions from Newton_polynomials.cpp. */

void Newton_linear(const double *X, const double *Y, double *a);
void Newton_quadratic(const double *X, const double *Y, double *a);
void Newton_cubic(const double *X, const double *Y, double *a);


/* Functions from QR.cpp. */

long QR(const long n, const long m, double **A, double *diag, long *perm, double *norms);
void QTb(const long n, const long m, double **A, double *diag, long *perm, double *b);
void Qb(const long n, const long m, double **A, double *diag, long *perm, double *b);
moremath_error_type R_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *x);
moremath_error_type RT_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *z);
moremath_error_type rank_deficient_R_solve(const long n, const long m, double **A, double *diag, long *perm, double *c, double *x);
moremath_error_type QR_solve(const long n, const long m, double **A, double *diag, long *perm, double *b, double *x);
moremath_error_type R_solve_with_update(const long n, const long m, double **A, double *diag, long *perm, double *c, double *D, double *x);


/* Functions from roots.cpp. */

int roots_linear(double *roots, const double a_0, const double a_1);
int roots_quadratic(double *roots, const double a_0, const double a_1, const double a_2);
int roots_cubic(double *roots, const double a_0, const double a_1, const double a_2, const double a_3);


#ifdef __cplusplus
}
#endif


#endif /* #ifndef __MOREMATH */
