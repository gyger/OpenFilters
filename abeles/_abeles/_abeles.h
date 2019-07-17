/*
 *
 *  _abeles.h
 *
 *
 *  Header files for functions and structures of the abeles DLL.
 *
 *  Copyright (c) 2002-2009,2012-2014 Stephane Larouche.
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


#ifndef __ABELES
#define __ABELES


/* Make sure that complex and stdexcept are loaded. */
#include <complex>
#include <stdexcept>


/* With gcc, allow the use of the deprecated attribute. On other
 * compilers, leave declaration unchanged. */
#if defined(__GNUC__) || defined(__clang__)
	#define DEPRECATED(declaration) declaration __attribute__ ((deprecated))
#else
	#define DEPRECATED(declaration) declaration
#endif


/* Define constants for s and p polarisations. */
const double S = 90.0;
const double P = 0.0;


/* Error codes and error type. */
typedef enum
{
	ABELES_SUCCESS = 0,
	ABELES_OUT_OF_MEMORY
} abeles_error_type;


#ifdef __cplusplus
extern "C" {
#endif


/* Classes from PCHIP.cpp */

class PCHIP_error : public std::runtime_error
{
    public:

    PCHIP_error();
    PCHIP_error(std::string const& message);
};

class PCHIP
{
	private:

	const long							nb_points;
	const double						*xa, *ya;
	const bool							preserve_monotonicity, allow_extrapolation;
	const double						*a0;
	double									*a1, *a2, *a3;
	double									*dx, *S;
	bool										prepared;

	void prepare();

	public:

	PCHIP(const long nb_points, double const * const xa, double const * const ya, const bool preserve_monotonicity = false, const bool allow_extrapolation = false);
	~PCHIP();
	void reset(double const * const xa = NULL, double const * const ya = NULL);
	void evaluate(const long length, double const * const x, double * const y, long const * const indices = NULL);
	void evaluate_derivative(const long length, double const * const x, double * const dy, long const * const indices = NULL);
	void evaluate_inverse(const long length, double const * const y, double * const x, long const * const indices = NULL);
};


/* Type definitions. */

typedef struct
{
	long										length;
	double									*wvls;
} wvls_type;

typedef struct
{
	const wvls_type					*wvls;
	std::complex<double>		*N;
} N_type;

typedef abeles_error_type (mixture_f_type)(const void *, const N_type *, const double, const double);
typedef abeles_error_type (mixture_f_x_type)(const void *, const N_type *, const double);

typedef struct
{
	void										*material;
	mixture_f_type					*f_N;
	mixture_f_x_type				*f_N_x;
	mixture_f_type					*f_dN;
	N_type									*N;
	N_type									*dN;
	long										length;
	N_type									*N_graded;
} N_mixture_type;

typedef struct
{
	std::complex<double>		N;
} constant_type;

typedef struct
{
	long										length;
	double									*wvls;
	double									*n;
	double									*k;
	/* The following elements are saved in the structure to speed up the
	 * calculations . */
	PCHIP				             *_n_PCHIP;
	PCHIP				             *_k_PCHIP;
} table_type;

typedef struct
{
	double									A;
	double									B;
	double									C;
	double									Ak;
	double									exponent;
	double									edge;
} Cauchy_type;

typedef struct
{
	double									B1;
	double									C1;
	double									B2;
	double									C2;
	double									B3;
	double									C3;
	double									Ak;
	double									exponent;
	double									edge;
} Sellmeier_type;

typedef struct
{
	long										length;
	double									*X;
	double									*n;
	double									*k;
	/* The following elements are saved in the structure to speed up the
	 * calculations . */
	PCHIP				            *_n_PCHIP;
	PCHIP				            *_k_PCHIP;
} constant_mixture_type;

typedef struct
{
	long										length;
	long										nb_wvls;
	double									*X;
	double									*wvls;
	double									**n;
	double									**k;
	/* The following elements are saved in the structure to speed up the
	 * calculations . */
	PCHIP				            **_table_n_PCHIPs;
	PCHIP				            **_table_k_PCHIPs;
	const wvls_type					*_wvls;
	long										_nb_wvls;
	double									**_n;
	double									**_k;
	PCHIP				            **_n_PCHIPs;
	PCHIP				            **_k_PCHIPs;
	double									_center_wvl;
	double									*_n_center_wvl;
	PCHIP				            *_n_center_wvl_PCHIP;
	double									_other_wvl;
	double									*_n_other_wvl;
	PCHIP				            *_n_other_wvl_PCHIP;
} table_mixture_type;

typedef struct
{
	long										length;
	double									*X;
	double									*A;
	double									*B;
	double									*C;
	double									*Ak;
	double									*exponent;
	double									*edge;
	/* The following elements are saved in the structure to speed up the
	 * calculations . */
	const wvls_type					*_wvls;
	long										_nb_wvls;
	double									**_n;
	double									**_k;
	PCHIP				            **_n_PCHIPs;
	PCHIP				            **_k_PCHIPs;
	double									_center_wvl;
	double									*_n_center_wvl;
	PCHIP				            *_n_center_wvl_PCHIP;
	double									_other_wvl;
	double									*_n_other_wvl;
	PCHIP				            *_n_other_wvl_PCHIP;
} Cauchy_mixture_type;

typedef struct
{
	long										length;
	double									*X;
	double									*B1;
	double									*C1;
	double									*B2;
	double									*C2;
	double									*B3;
	double									*C3;
	double									*Ak;
	double									*exponent;
	double									*edge;
	/* The following elements are saved in the structure to speed up the
	 * calculations . */
	const wvls_type					*_wvls;
	long										_nb_wvls;
	double									**_n;
	double									**_k;
	PCHIP				            **_n_PCHIPs;
	PCHIP				            **_k_PCHIPs;
	double									_center_wvl;
	double									*_n_center_wvl;
	PCHIP				            *_n_center_wvl_PCHIP;
	double									_other_wvl;
	double									*_n_other_wvl;
	PCHIP				            *_n_other_wvl_PCHIP;
} Sellmeier_mixture_type;

typedef struct
{
	const wvls_type					*wvls;
	std::complex<double>		*sin2;
} sin2_type;

typedef struct
{
	std::complex<double>		s[4];
	std::complex<double>		p[4];
} matrix_type;

typedef struct
{
	const wvls_type					*wvls;
	matrix_type							*matrices;
} matrices_type;

typedef struct
{
	const wvls_type					*wvls;
	std::complex<double>		*r_s;
	std::complex<double>		*t_s;
	std::complex<double>		*r_p;
	std::complex<double>		*t_p;
} r_and_t_type;

typedef struct
{
	const wvls_type					*wvls;
	double									*data;
} spectrum_type;

typedef struct
{
	const wvls_type					*wvls;
	double									*Psi;
	double									*Delta;
} Psi_and_Delta_type;

typedef struct
{
	const wvls_type					*wvls;
	std::complex<double>		*data;
} admittance_type;

typedef struct
{
	const wvls_type					*wvls;
	std::complex<double>		*data;
} circle_type;

typedef struct
{
	long										length;
	const wvls_type					*wvls;
	matrices_type						**matrices;
} monitoring_matrices_type;

typedef struct
{
	long										length;
	const wvls_type					*wvls;
	matrices_type						*M;
	matrices_type						**Mi;
	matrices_type						**pre_M;
	matrices_type						**post_M;
} pre_and_post_matrices_type;

typedef struct
{
	const wvls_type					*wvls;
	matrices_type						*psi_r;
	matrices_type						*psi_t;
} psi_matrices_type;

typedef struct
{
	long										length;
	const wvls_type					*wvls;
	double									*positions;
	matrices_type						**M;
} needle_matrices_type;



/* Functions from PCHIP.cpp */

long locate(const long length, const double *X, const double x, bool allow_extrapolation = false);


/* Functions from wavelengths.cpp */

/* Constructors and destructors. */
wvls_type * new_wvls(const long length);
void del_wvls(wvls_type *wvls);

/* Set wavelengths. */
void set_wvl(const wvls_type *wvls, const long position, const double wvl);
void set_wvls_by_range(const wvls_type *wvls, const double from, const double by);


/* Functions from N.cpp */

/* Constructors and destructors. */
N_type * new_N(const wvls_type *wvls);
void del_N(N_type *N);

/* Copy the index. */
void N_copy(N_type *N_copy, const N_type *N_original);


/* Functions from N_mixture.cpp */

/* Constructors and destructors. */
N_mixture_type * new_N_mixture_constant(const constant_mixture_type *material, const wvls_type *wvls);
N_mixture_type * new_N_mixture_table(const table_mixture_type *material, const wvls_type *wvls);
N_mixture_type * new_N_mixture_Cauchy(const Cauchy_mixture_type *material, const wvls_type *wvls);
N_mixture_type * new_N_mixture_Sellmeier(const Sellmeier_mixture_type *material, const wvls_type *wvls);
void del_N_mixture(N_mixture_type *mixture);

/* Set the index of the mixture and its derivative. */
N_type * prepare_N_mixture_graded(N_mixture_type *mixture, const long length);
bool N_mixture_graded_is_prepared(N_mixture_type *mixture);
abeles_error_type set_N_mixture(const N_mixture_type *mixture, const double n_wvl, const double wvl);
abeles_error_type set_N_mixture_by_x(const N_mixture_type *mixture, const double x);
abeles_error_type set_dN_mixture(const N_mixture_type *mixture, const double n_wvl, const double wvl);
abeles_error_type set_N_mixture_graded(const N_mixture_type *mixture, const long position, const double n_wvl, const double wvl);

/* Get the index of the mixture and its derivative. */
N_type * get_N_mixture(const N_mixture_type *mixture);
N_type * get_dN_mixture(const N_mixture_type *mixture);
N_type * get_N_mixture_graded(const N_mixture_type *mixture, const long position);


/* Functions from dispersion.cpp */

/* Constant dispersion. */
constant_type * new_constant();
void del_constant(constant_type *material);
void set_constant(constant_type *material, const std::complex<double> N);
abeles_error_type set_N_constant(const constant_type *material, const N_type *N);

/* Table dispersion. */
table_type * new_table(const long length);
void del_table(table_type *material);
void set_table(const table_type *material, const long pos, const double wvl, const std::complex<double> n);
DEPRECATED(void prepare_table(const table_type *material));
double get_table_index(const table_type *material, const double wvl);
abeles_error_type set_N_table(const table_type *material, const N_type *N);

/* Cauchy dispersion. */
Cauchy_type * new_Cauchy();
void del_Cauchy(Cauchy_type *material);
void set_Cauchy(Cauchy_type *material, const double A, const double B, const double C, const double Ak, const double exponent, const double edge);
abeles_error_type set_N_Cauchy(const Cauchy_type *material, const N_type *N);

/* Sellmeier dispersion. */
Sellmeier_type * new_Sellmeier();
void del_Sellmeier(Sellmeier_type *material);
void set_Sellmeier(Sellmeier_type *material,  double B1, const double C1, const double B2, const double C2, const double B3, const double C3, const double Ak, const double exponent, const double edge);
abeles_error_type set_N_Sellmeier(const Sellmeier_type *material, const N_type *N);


/* Functions from dispersion_mixtures.cpp */

/* Constant dispersion. */
constant_mixture_type * new_constant_mixture(const long length);
void del_constant_mixture(constant_mixture_type *material);
void set_constant_mixture(const constant_mixture_type *material, const long i, const double x, const std::complex<double> N);
DEPRECATED(void prepare_constant_mixture(const constant_mixture_type *material));
bool get_constant_mixture_monotonicity(const constant_mixture_type *material, const double wvl);
double get_constant_mixture_index(const constant_mixture_type *material, const double x, const double wvl);
void get_constant_mixture_index_range(const constant_mixture_type *material, const double wvl, double *n_min, double *n_max);
double change_constant_mixture_index_wvl(const constant_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl);
abeles_error_type set_N_constant_mixture(const constant_mixture_type *material, const N_type *N, const double n_wvl, const double wvl);
abeles_error_type set_N_constant_mixture_by_x(const constant_mixture_type *material, const N_type *N, const double x);
abeles_error_type set_dN_constant_mixture(const constant_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl);

/* Table dispersion. */
table_mixture_type * new_table_mixture(const long length, const long nb_wvls);
void del_table_mixture(table_mixture_type *material);
void set_table_mixture(const table_mixture_type *material, const long i_mix, const long i_wvl, const double x, const double wvl, const std::complex<double> N);
DEPRECATED(void prepare_table_mixture(const table_mixture_type *material));
bool get_table_mixture_monotonicity(table_mixture_type *material, const double wvl);
double get_table_mixture_index(table_mixture_type *material, const double x, const double wvl);
void get_table_mixture_index_range(table_mixture_type *material, const double wvl, double *n_min, double *n_max);
double change_table_mixture_index_wvl(table_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl);
abeles_error_type set_N_table_mixture(table_mixture_type *material, const N_type *N, const double n_wvl, const double wvl);
abeles_error_type set_N_table_mixture_by_x(table_mixture_type *material, const N_type *N, const double x);
abeles_error_type set_dN_table_mixture(table_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl);

/* Cauchy dispersion. */
Cauchy_mixture_type * new_Cauchy_mixture(const long length);
void del_Cauchy_mixture(Cauchy_mixture_type *material);
void set_Cauchy_mixture(const Cauchy_mixture_type *material, const long i, const double x, const double A, const double B, const double C, const double Ak, const double exponent, const double edge);
DEPRECATED(void prepare_Cauchy_mixture(const Cauchy_mixture_type *material));
bool get_Cauchy_mixture_monotonicity(Cauchy_mixture_type *material, const double wvl);
double get_Cauchy_mixture_index(Cauchy_mixture_type *material, const double x, const double wvl);
void get_Cauchy_mixture_index_range(Cauchy_mixture_type *material, const double wvl, double *n_min, double *n_max);
double change_Cauchy_mixture_index_wvl(Cauchy_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl);
abeles_error_type set_N_Cauchy_mixture(Cauchy_mixture_type *material, const N_type *N, const double n_wvl, const double wvl);
abeles_error_type set_N_Cauchy_mixture_by_x(Cauchy_mixture_type *material, const N_type *N, const double x);
abeles_error_type set_dN_Cauchy_mixture(Cauchy_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl);

/* Sellmeier dispersion. */
Sellmeier_mixture_type * new_Sellmeier_mixture(const long length);
void del_Sellmeier_mixture(Sellmeier_mixture_type *material);
void set_Sellmeier_mixture(const Sellmeier_mixture_type *material, const long i, const double x, const double B1, const double C1, const double B2, const double C2, const double B3, const double C3, const double Ak, const double exponent, const double edge);
DEPRECATED(void prepare_Sellmeier_mixture(const Sellmeier_mixture_type *material));
bool get_Sellmeier_mixture_monotonicity(Sellmeier_mixture_type *material, const double wvl);
double get_Sellmeier_mixture_index(Sellmeier_mixture_type *material, const double x, const double wvl);
void get_Sellmeier_mixture_index_range(Sellmeier_mixture_type *material, const double wvl, double *n_min, double *n_max);
double change_Sellmeier_mixture_index_wvl(Sellmeier_mixture_type *material, const double old_n, const double old_wvl, const double new_wvl);
abeles_error_type set_N_Sellmeier_mixture(Sellmeier_mixture_type *material, const N_type *N, const double n_wvl, const double wvl);
abeles_error_type set_N_Sellmeier_mixture_by_x(Sellmeier_mixture_type *material, const N_type *N, const double x);
abeles_error_type set_dN_Sellmeier_mixture(Sellmeier_mixture_type *material, const N_type *dN, const double n_wvl, const double wvl);


/* Functions from sin2.cpp */

/* Constructors and destructors. */
sin2_type * new_sin2(const wvls_type *wvls);
void del_sin2(sin2_type *sin2);

/* Set sin2 in vacuum from angle of indicence. */
void set_sin2_theta_0(const sin2_type *sin_s, const N_type *N, const double theta);


/* Functions from matrices.cpp */

/* Constructors and destructors. */
matrices_type * new_matrices(const wvls_type *wvls);
void del_matrices(matrices_type *M);

/* Matrix manipulation. */
void set_matrices_unity(const matrices_type *M);
void copy_matrices(const matrices_type *M1, const matrices_type *M2);
void set_matrices(const matrices_type *M, const N_type *N, const double thickness, const sin2_type *sin2_theta_0);
void multiply_matrices(const matrices_type *M1, const matrices_type *M2);


/* Functions from r_and_t.cpp */

/* Constructors and destructors. */
r_and_t_type * new_r_and_t(const wvls_type *wvls);
void del_r_and_t(r_and_t_type *r_and_t);

/* Calculate transmission and reflexion. */
void calculate_r_and_t(const r_and_t_type *r_and_t, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0);
void calculate_r_and_t_reverse(const r_and_t_type *r_and_t, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0);


/* Functions from spectro.cpp */

/* Constructors and destructors. */
spectrum_type * new_spectrum(const wvls_type *wvls);
void del_spectrum(spectrum_type *spectrum);

/* Calculate transmission and reflexion. */
void calculate_R(const spectrum_type *R, const r_and_t_type *r_and_t, const double polarization);
void calculate_R_with_backside(const spectrum_type *R, const spectrum_type *T_front, const spectrum_type *R_front, const spectrum_type *T_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_T(const spectrum_type *T, const r_and_t_type *r_and_t, const N_type *N_i, const N_type *N_e, const sin2_type *sin2_theta_0, const double polarization);
void calculate_T_with_backside(const spectrum_type *T, const spectrum_type *T_front, const spectrum_type *R_front_reverse, const spectrum_type *T_back, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_A(const spectrum_type *A, const spectrum_type *R, const spectrum_type *T);


/* Functions from phase.cpp */

/* Calculate phase. */
void calculate_r_phase(const spectrum_type *phase, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);
void calculate_t_phase(const spectrum_type *phase, const matrices_type *M, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);

/* Calculate the group delay and group delay dispersion. */
void calculate_GD(const spectrum_type *GD, const spectrum_type *phase);
void calculate_GDD(const spectrum_type *GDD, const spectrum_type *phase);


/* Functions from ellipso.cpp */

/* Constructors and destructors. */
Psi_and_Delta_type * new_Psi_and_Delta(const wvls_type *wvls);
void del_Psi_and_Delta(Psi_and_Delta_type *Psi_and_Delta);

/* Calculate ellipsometric variables. */
void calculate_Psi_and_Delta(const Psi_and_Delta_type *Psi_and_Delta, const r_and_t_type *r_and_t);
void calculate_Psi_and_Delta_with_backside(const Psi_and_Delta_type *Psi_and_Delta, const r_and_t_type *r_and_t_front, const r_and_t_type *r_and_t_reverse, const r_and_t_type *r_and_t_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);


/* Function from admittance.cpp */

/* Constructors and destructors. */
admittance_type * new_admittance(const wvls_type *wvls);
void del_admittance(admittance_type *admittance);

/* Calculate admittance. */
void calculate_admittance(const admittance_type *admittance, const matrices_type *M, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);


/* Function from circle.cpp */

/* Constructors and destructors. */
circle_type * new_circle(const wvls_type *wvls);
void del_circle(circle_type *circle);

/* Calculate circle. */
void calculate_circle(const circle_type *circle, const r_and_t_type *r_and_t, const double polarization);


/* Function from electric_field.cpp */

/* Calculate admittance. */
void calculate_electric_field(const spectrum_type *electric_field, const matrices_type *M, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);


/* Functions from monitoring.cpp */

/* Constructors and destructors. */
monitoring_matrices_type * new_monitoring_matrices(const wvls_type *wvls, const long length);
void del_monitoring_matrices(monitoring_matrices_type *M);

/* Set the slices. */
void set_monitoring_matrices(const monitoring_matrices_type *M, const long slice, const N_type *N, const double slice_thickness, const sin2_type *sin2_theta_0);

/* Operate on slices. */
void multiply_monitoring_matrices(const matrices_type *M1, const monitoring_matrices_type *M2);
void multiply_monitoring_matrices_cumulative(const matrices_type *M1, const monitoring_matrices_type *M2);

/* Get information about slices. */
matrices_type * get_slice_matrices(const monitoring_matrices_type *M, const long nb);


/* Functions from derivatives.cpp */

/* Constructors and destructors. */
pre_and_post_matrices_type * new_pre_and_post_matrices(const wvls_type *wvls, const long length);
void del_pre_and_post_matrices(pre_and_post_matrices_type *M);
psi_matrices_type * new_psi_matrices(const wvls_type *wvls);
void del_psi_matrices(psi_matrices_type *psi);

/* Set layer matrices and calculate pre and post matrices. */
void set_pre_and_post_matrices(const pre_and_post_matrices_type *M, const long layer_nb, const N_type *N, const double thickness, const sin2_type *sin2_theta_0);
void multiply_pre_and_post_matrices(const pre_and_post_matrices_type *M);

/* Get the global matrices or the matrices of a single layer. */
matrices_type * get_global_matrices(const pre_and_post_matrices_type *M);
matrices_type * get_layer_matrices(const pre_and_post_matrices_type *M, const long layer_nb);

/* Calculate the derivative of layer matrices. */
void set_dMi_thickness(const matrices_type *dMi, const N_type *N, const double thickness, const sin2_type *sin2_theta_0);
void set_dMi_index(const matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0);
void set_dMi_index_with_constant_OT(const matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0, const std::complex<double> N_0, const std::complex<double> sin2_theta_0_0);

/* Calculate the derivative of global matrices. */
void calculate_dM(const matrices_type *dM, const matrices_type *dMi, const pre_and_post_matrices_type *M, const long layer_nb);

/* Calculation psi matrices, usefull in the calculation of dr and dt. */
void calculate_psi_matrices(const psi_matrices_type *psi, const r_and_t_type *r_and_t, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0);
void calculate_psi_matrices_reverse(const psi_matrices_type *psi, const r_and_t_type *r_and_t, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0);

/* Calculate the derivative of r and t. */
void calculate_dr_and_dt(const r_and_t_type *dr_and_dt, const matrices_type *dM, const psi_matrices_type *psi);
void calculate_dr_and_dt_reverse(const r_and_t_type *dr_and_dt, const matrices_type *dM, const psi_matrices_type *psi);

/* Calculate the derivative of the different values of interest. */
void calculate_dR(const spectrum_type *dR, const r_and_t_type *dr_and_dt, const r_and_t_type *r_and_t, const double polarization);
void calculate_dT(const spectrum_type *dT, const r_and_t_type *dr_and_dt, const r_and_t_type *r_and_t, const N_type *N1, const N_type *N2, const sin2_type *sin2_theta_0, const double polarization);
void calculate_dA(const spectrum_type *dA, const spectrum_type *dR, const spectrum_type *dT);
void calculate_dR_with_backside(const spectrum_type *dR, const spectrum_type *T_front, const spectrum_type *dT_front, const spectrum_type *dR_front, const spectrum_type *T_front_reverse, const spectrum_type *dT_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *dR_front_reverse, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_dT_with_backside(const spectrum_type *dT, const spectrum_type *T_front, const spectrum_type *dT_front, const spectrum_type *R_front_reverse, const spectrum_type *dR_front_reverse, const spectrum_type *T_back, const spectrum_type *R_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_dR_with_backside_2(const spectrum_type *dR, const spectrum_type *T_front, const spectrum_type *T_front_reverse, const spectrum_type *R_front_reverse, const spectrum_type *R_back, const spectrum_type *dR_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_dT_with_backside_2(const spectrum_type *dT, const spectrum_type *T_front, const spectrum_type *R_front_reverse, const spectrum_type *T_back, const spectrum_type *dT_back, const spectrum_type *R_back, const spectrum_type *dR_back, const N_type *N_s, const double thickness, const sin2_type *sin2_theta_0);
void calculate_dr_phase(const spectrum_type *dphase, const matrices_type *M, const matrices_type *dM, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);
void calculate_dt_phase(const spectrum_type *dphase, const matrices_type *M, const matrices_type *dM, const N_type *N_m, const N_type *N_s, const sin2_type *sin2_theta_0, const double polarization);
void calculate_dGD(const spectrum_type *dGD, const spectrum_type *dphase);
void calculate_dGDD(const spectrum_type *dGDD, const spectrum_type *dphase);


/* Functions from needles.cpp */

/* Constructors and destructors. */
needle_matrices_type * new_needle_matrices(const wvls_type *wvls, const long length);
void del_needle_matrices(needle_matrices_type *M);

/* Set and get the position of the needles. */
void set_needle_position(const needle_matrices_type *M, const long i_needle, const double position);
void set_needle_positions(const needle_matrices_type *M, const double spacing);
double get_needle_position(const needle_matrices_type *M, const long i_needle);

/* Get the matrices related to one needle. */
matrices_type * get_one_needle_matrices(const needle_matrices_type *M, const long i_needle);

/* Calculate the derivative of matrices upon the addition of a needle
 * or a step. */
void calculate_dMi_needles(const needle_matrices_type *dMi, const N_type *N, const N_type *N_n, const double thickness, const sin2_type *sin2_theta_0);
void calculate_dMi_needles_fast(const needle_matrices_type **dMi, const N_type *N, const N_type **N_n, const double thickness, const sin2_type *sin2_theta_0, const long length);
void calculate_dMi_steps(const needle_matrices_type *dMi, const N_type *N, const N_type *dN, const double thickness, const sin2_type *sin2_theta_0);


#ifdef __cplusplus
}
#endif


#endif /* #ifndef __ABELES */
