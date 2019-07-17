# -*- coding: UTF-8 -*-

# Levengerg_Marquardt.py
# 
# Fit a non-linear equation using the Levengerg-Marquardt algorithm.
# 
# Copyright (c) 2004-2009,2012 Stephane Larouche.
# 
# This file is part of OpenFilters.
# 
# OpenFilters is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# OpenFilters is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA



from math import sqrt

from linear_algebra import matrix_error
import limits
import QR



# The possible return values of the Lavenberg-Marquardt method.
IMPROVING = 0
MINIMUM_FOUND = 1
CHI_2_IS_OK = 2
CHI_2_CHANGE_TOO_SMALL = 3
DELTA_IS_TOO_SMALL = 4
ALL_PARAMETERS_ARE_STUCK = 5
SINGULAR_MATRIX = -1

# Equality or inequalities.
SMALLER = -1
EQUAL = 0
LARGER = 1

# Infinities are used to indicate that a parameter is not bounded.
INFINITY = float("Inf")



epsilon = limits.epsilon



########################################################################
#                                                                      #
# Levenberg_Marquardt                                                  #
#                                                                      #
########################################################################
class Levenberg_Marquardt(object):
	"""Fit a curve by the Levenberg-Marquardt method
	
	This class implements a trust region version of the	Levenberg-
	Marquardt algorithm.
	
	To fit a curve using the Levenberg-Marquardt method, you must:
	  1 - Initialize the method by providing the appropriate functions
	      and points to fit;
	  2 - Set stopping criteria;
	  3 - Set limits to parameter values, if desired;
	  4 - Set inequalities on targets, if desired;
	  5 - Prepare for optimization;
	  6 - Iterate until a satisfactory solution is found.
	
	See the description of the various methods of this class for an
	explanation on how to do these steps.
	
	This algorithm was first proposed by Marquardt in
	  D. Marquardt, "An algorithm for least squares estimation on
	  nonlinear parameters", SIAM J. Appl. Math., vol. 11, 1963,
	  pp. 431-441.
	
	Basic information about the least square problem and a simple
	description of the Levenberg-Marquardt algorithm can be found in
	  Press et al., Numerical Recipes in C: the Art of Scientific
	  Computing, 2nd edition, Cambridge University Press, 1997,
	  pp. 681-688.
	
	The algorithm used in this file is described in
	  Jorge J. Moré, "The Levenberg-Marquardt algorithm, implementation
	  and theory", Numerical Analysis, edited by G. A. Watson, Lecture
	  Notes in Mathematics, vol. 630, Springer-Verlag, 1977, pp. 105-116
	and is inspired by MINPACK (http://www.netlib.org/minpack/)."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, f, df, a, Yi, sigma, *f_par):
		"""Initialize the Levenberg-Marquardt algorithm
		
		This method takes at least 5 arguments:
		  f, df             functions that return the values of the
		                    function that we fit and the jacobian
		                    according to a list of parameters;
		  a                 starting values of the parameters of the
		                    function to be fitted;
		  Yi                a list of the values of y to which the function
		                    must be fitted;
		  sigma             a list of weights to give to the y points and;
		any supplementary arguments will be passed to f and df."""
		
		self.f = f
		self.df = df
		self.a = a
		self.Yi = Yi
		self.sigma = sigma
		self.f_par = f_par
		
		# The number of parameters and the number of points to fit. The
		# number of rows in the matrix is at least equal to the number
		# of parameters.
		self.nb_par = len(a)
		self.nb_points = len(Yi)
		self.nb_rows = max(self.nb_par, self.nb_points)
		
		# Usually, all parameters are allowed to vary. But if some
		# parameters are bounded, the will be fixed when they hit
		# their bounds.
		self.nb_free_par = self.nb_par
		
		# The number of iteration, function and jacobian evaluations.
		self.iteration = 0
		self.nb_f_eval = 0
		self.nb_df_eval = 0
		
		# Prepare a list to keep old value of a.
		self.previous_a = [0.0]*self.nb_par
		
		# Variables for the values returned by f and df.
		self.Y = []
		self.dY = []
		
		# Delta is the trust region and alpha is the Levenberg-Marquard
		# parameter. The trust region is automatically selected on the
		# first iteration and the Levenberg-Marquard parameter alpha is
		# used to keep steps smaller than Delta.
		self.Delta = 0.0
		self.alpha = 0.0
		
		# Default values of trust region.
		self.factor = 0.01
		
		# Prepare alpha matrix, beta, da, D and use.
		self.A = [[0.0]*self.nb_rows for par in range(self.nb_par)]
		self.b = [0.0]*self.nb_rows
		self.beta = [0.0]*self.nb_par
		self.da = [0.0]*self.nb_par
		self.D = [0.0]*self.nb_par
		self.alpha_D = [0.0]*self.nb_par
		self.use_par = [True]*self.nb_par
		self.column_norms = [0.0]*self.nb_par
		self.scaled_da = [0.0]*self.nb_par
		self.temp_array = [0.0]*self.nb_par
		self.use_point = [True]*self.nb_points
		
		# Variables for the QR factorization.
		self.diag = [0.0]*self.nb_par
		self.perm = [0]*self.nb_par
		
		# The stop criteria. By default, there is no stop criteria.
		self.min_gradient = 0.0
		self.acceptable_chi_2 = 0.0
		self.min_chi_2_change = 0.0
		
		# chi_2 is the sum of the squared residuals.
		self.chi_2 = 0.0
		
		# The norm of the gradient is kept if the user want's to know it.
		self.norm_gradient = 0.0
		
		# The norm of the scaled parameter vector.
		self.norm_scaled_a = 0.0
		
		# Vectors for parameter bounds. By default, the parameters are not
		# bounded.
		self.a_min = [-INFINITY]*self.nb_par
		self.a_max = [+INFINITY]*self.nb_par
		
		# By default, all targets are equalities.
		self.inequalities = [EQUAL]*self.nb_points
	
	
	######################################################################
	#                                                                    #
	# set_stop_criteria                                                  #
	#                                                                    #
	######################################################################
	def set_stop_criteria(self, min_gradient = 0.0, acceptable_chi_2 = 0.0, min_chi_2_change = 0.0):
		"""Set stop criteria
		
		This method takes 3 arguments:
		  min_gradient      the criteria to determine if the value of the
		                    gradient is zero;
		  acceptable_chi_2  the value of chi_2 for an acceptable fit (it
		                    can be set to 0 to avoid stopping of the fit);
		  min_chi_2_change  the minimum relative change in chi_2 (it can be
		                    set to 0 to avoid stopping of the fit)."""
		
		self.min_gradient = min_gradient
		self.acceptable_chi_2 = acceptable_chi_2
		self.min_chi_2_change = min_chi_2_change
	
	
	######################################################################
	#                                                                    #
	# set_limits                                                         #
	#                                                                    #
	######################################################################
	def set_limits(self, a_min = None, a_max = None):
		"""Set limits to fitted parameters
		
		This method takes two arguments:
		  a_min and a_max   lists of minimum and maximum acceptable values
		                    of the parameters (use None for no limit)."""
		
		if a_min:
			self.a_min = a_min
		else:
			self.a_min = [-INFINITY]*self.nb_par
		
		if a_max:
			self.a_max = a_max
		else:
			self.a_max = [+INFINITY]*self.nb_par
	
	
	######################################################################
	#                                                                    #
	# set_inequalities                                                   #
	#                                                                    #
	######################################################################
	def set_inequalities(self, inequalities = None):
		"""Set targets to inequalities
		
		This method takes one argument:
		  inequalities      list describing if targets are equalities or
		                    inequalities (use None for all equalities)."""
		
		if inequalities:
			self.inequalities = inequalities
		else:
			self.inequalities = [EQUAL]*self.nb_points
	
	
	######################################################################
	#                                                                    #
	# prepare                                                            #
	#                                                                    #
	######################################################################
	def prepare(self):
		"""Prepare for optimization
		
		This method simply calculates chi square before the first
		iteration.
		
		This method takes no argument and returns no argument."""
		
		# Get Y.
		self.Y = self.f(self.a, *self.f_par)
		self.nb_f_eval += 1
		
		# Build b.
		for i in range(self.nb_points):
			self.b[i] = (self.Yi[i]-self.Y[i])/self.sigma[i]
		
		# Determine which points are used considering the inequalities.
		for i in range(self.nb_points):
			if self.inequalities[i] == SMALLER and self.b[i] > 0.0:
				self.use_point[i] = False
			elif self.inequalities[i] == LARGER and self.b[i] < 0.0:
				self.use_point[i] = False
			else:
				self.use_point[i] = True
		
		# Calculate chi square.
		self.chi_2 = 0.0
		for i in range(self.nb_points):
			if self.use_point[i]:
				self.chi_2 += self.b[i]*self.b[i]
	
	
	######################################################################
	#                                                                    #
	# iterate                                                            #
	#                                                                    #
	######################################################################
	def iterate(self):
		"""Do one iteration of the Levenberg-Marquardt algorithm
		
		This method takes no arguments. It returns a single argument giving
		the status of the solution. Possible values are:
		  IMPROVING                 the solution is improving;
			MINIMUM_FOUND             the gradient is null (or close enough);
		  CHI_2_IS_OK               the value of chi square is acceptable;
		  CHI_2_CHANGE_TOO_SMALL    the change in chi square is small;
		  ALL_PARAMETERS_ARE_STUCK  all the parameters are stuck at their
		                            limits.
		When this method returns, MINIMUM_FOUND, CHI_2_IS_OK 
		CHI_2_CHANGE_TOO_SMALL or ALL_PARAMETERS_ARE_STUCK, the calling
		function should stop the fit."""
		
		self.iteration += 1
		
		# Keep a copy of the old parameter values in case we need to revert
		# to them.
		for par in range(self.nb_par):
			self.previous_a[par] = self.a[par]
		
		# Build b.
		for i in range(self.nb_points):
			self.b[i] = (self.Yi[i]-self.Y[i])/self.sigma[i]
		
		# Determine which points are used considering the inequalities.
		for i in range(self.nb_points):
			if self.inequalities[i] == SMALLER and self.b[i] > 0.0:
				self.use_point[i] = False
			elif self.inequalities[i] == LARGER and self.b[i] < 0.0:
				self.use_point[i] = False
			else:
				self.use_point[i] = True
		
		# Get the derivative at this point.
		self.dY = self.df(self.a, *self.f_par)
		self.nb_df_eval += 1
		
		# Calculate the gradient.
		for par in range(self.nb_par):
			self.beta[par] = 0.0
			for i in range(self.nb_points):
				if self.use_point[i]:
					self.beta[par] += (self.Yi[i]-self.Y[i])/(self.sigma[i]*self.sigma[i]) * self.dY[par][i]
		
		# If a parameter is stuck at one of its limits, remove it from the
		# fit.
		self.nb_free_par = self.nb_par
		for par in range(self.nb_par):
			if self.a[par] == self.a_min[par] and self.beta[par] < 0.0:
				self.use_par[par] = False
				self.beta[par] = 0.0
				self.nb_free_par -= 1
			elif self.a[par] == self.a_max[par] and self.beta[par] > 0.0:
				self.use_par[par] = False
				self.beta[par] = 0.0
				self.nb_free_par -= 1
			else:
				self.use_par[par] = True
		
		if self.nb_free_par == 0:
			return ALL_PARAMETERS_ARE_STUCK
		
		# Calculate the norm of the gradient.
		self.norm_gradient = 0.0
		for par in range(self.nb_par):
			self.norm_gradient += self.beta[par]*self.beta[par]
		self.norm_gradient = sqrt(self.norm_gradient)
		
		# Check if the minimum is reached (norm of the gradient is 0).
		if self.norm_gradient < self.min_gradient:
			return MINIMUM_FOUND
		
		# Build the jacobian matrix.
		for par in range(self.nb_par):
			if self.use_par[par]:
				for i in range(self.nb_points):
					if self.use_point[i]:
						self.A[par][i] = self.dY[par][i]/self.sigma[i]
					else:
						self.A[par][i] = 0.0
				for i in range(self.nb_points, self.nb_par):
					self.A[par][i] = 0.0
			else:
				for i in range(self.nb_rows):
					self.A[par][i] = 0.0
		
		# Factorize the system using QR factorization and calculate inv(Q)*b.
		rank = QR.QR(self.A, self.diag, self.perm, self.column_norms)
		QR.QTb(self.A, self.diag, self.perm, self.b)
		
		# On the first iteration, initialize D and the trust region to a
		# fraction of the scaled length of a. And calculate the norm of a
		# for a first time.
		if self.iteration == 1:
			for par in range(self.nb_par):
				self.D[par] = self.column_norms[par]
				if self.D[par] == 0.0:
					self.D[par] = 1.0
			
			norm = 0.0
			for par in range(self.nb_par):
				temp = self.D[par]*self.a[par]
				norm += temp*temp
			norm = sqrt(norm)
			self.Delta = self.factor * norm
			if self.Delta == 0.0:
				self.Delta = self.factor
			
			# Calculate the norm of the scaled a. This is used to check if
			# Delta gets too small.
			self.norm_scaled_a = 0.0
			for par in range(self.nb_par):
				temp = self.D[par]*self.a[par]
				self.norm_scaled_a += temp*temp
			self.norm_scaled_a = sqrt(self.norm_scaled_a)
		
		# Update D if the norm of the columns has increased.
		for par in range(self.nb_par):
			self.D[par] = max(self.D[par], self.column_norms[par])
		
		# Iterate until a an improving step is found.
		while True:
			
			# Compute the Gauss-Newton iteration. Here, and in the rest of
			# the method, the matrix will be considerer to have full rank
			# if the rank is equal to the number of free parameters. This
			# works because the QR method ignores rows with null norms.
			if rank == self.nb_free_par:
				QR.R_solve(self.A, self.diag, self.perm, self.b, self.da)
			else:
				QR.rank_deficient_R_solve(self.A, self.diag, self.perm, self.b, self.da)
			
			# Calculate the norm of the scaled Gauss-Newton step.
			norm_scaled_da = 0.0
			for par in range(self.nb_par):
				self.scaled_da[par] = self.D[par]*self.da[par]
				norm_scaled_da += self.scaled_da[par]*self.scaled_da[par]
			norm_scaled_da = sqrt(norm_scaled_da)
			
			# If the Gauss-Newton step is accepted, set the Levenberg-
			# Marquardt parameter to 0.
			phi = norm_scaled_da - self.Delta
			if phi <= 0.1*self.Delta:
				self.alpha = 0.0
			
			# Otherwise, search the Levenberg-Marquardt parameter for which
			# phi = 0.
			else:
				
				# Set the lower bound of alpha to -phi(0)/phi'(0). If the
				# matrix is rank deficient, set the lower bound to 0.
				if rank == self.nb_free_par:
					for par in range(self.nb_par):
						self.temp_array[par] = self.D[self.perm[par]] * (self.scaled_da[self.perm[par]]/norm_scaled_da)
					
					norm_square = 0.0
					for par in range(self.nb_par):
						if self.use_par[self.perm[par]]:
							sum = 0.0
							for i in range(par):
								sum += self.temp_array[i] * self.A[par][i]
							self.temp_array[par] = (self.temp_array[par] - sum) / self.diag[par]
							norm_square += self.temp_array[par]*self.temp_array[par]
					
					l = ( phi / self.Delta ) / norm_square
				
				else:
					l = 0.0
				
				# Choose an upper bound. The upper bound is norm([J inv(D)]'b)
				# = norm(inv(D) R' Q'b). We already have Q'b, so let's use it.
				norm = 0.0
				for par in range(self.nb_par):
					if self.use_par[self.perm[par]]:
						temp = self.diag[par]*self.b[par]
						for i in range(par):
							temp += self.A[par][i]*self.b[i]
						temp /= self.D[self.perm[par]]
						norm += temp*temp
				norm = sqrt(norm)
				u = norm / self.Delta
				
				# If alpha is outside bounds, set it to the closest bound.
				self.alpha = max(self.alpha, l)
				self.alpha = min(self.alpha, u)
				
				# Guess an appropriate starting value for alpha.
				if self.alpha == 0.0:
					self.alpha = norm / norm_scaled_da
				
				# Search for a maximum of 10 iterations.
				for internal_iteration in range(10):
					
					# Protect ourselves against very small values of alpha (in
					# particular 0).
					if self.alpha == 0.0:
						self.alpha = 0.001 * u
					
					# Compute the step for the current value of alpha.
					for par in range(self.nb_par):
						if self.use_par[par]:
							self.alpha_D[par] = sqrt(self.alpha) * self.D[par]
						else:
							self.alpha_D[par] = 0.0
					
					QR.R_solve_with_update(self.A, self.diag, self.perm, self.b, self.alpha_D, self.da)
					
					# Calculate the norm of the scaled step.
					norm_scaled_da = 0.0
					for par in range(self.nb_par):
						self.scaled_da[par] = self.D[par]*self.da[par]
						norm_scaled_da += self.scaled_da[par]*self.scaled_da[par]
					norm_scaled_da = sqrt(norm_scaled_da)
					phi = norm_scaled_da - self.Delta
					
					# If phi is small enough, accept the step.
					if abs(phi) <= 0.1*self.Delta:
						break
					
					for par in range(self.nb_par):
						if self.use_par[par]:
							self.temp_array[par] = self.D[self.perm[par]] * (self.scaled_da[self.perm[par]]/norm_scaled_da)
					
					# Calculate the correction.
					norm_square = 0.0
					for par in range(self.nb_par):
						if self.use_par[self.perm[par]]:
							sum = 0.0
							for i in range(par):
								sum += self.temp_array[i] * self.A[i][par]
							self.temp_array[par] = (self.temp_array[par] - sum) / self.A[par][par]
							norm_square += self.temp_array[par]*self.temp_array[par]
					
					correction = ( phi / self.Delta ) / norm_square
					
					# Change the bounds according to the sign of phi.
					if phi > 0.0:
						l = max(l, self.alpha)
					else:
						u = min(u, self.alpha)
					
					self.alpha = max(self.alpha+correction, l)
			
			# Change the parameters a by the amount suggested by da.
			for par in range(self.nb_par):
				self.a[par] += self.da[par]
			
			# Check if parameters fell outside of acceptable range. Change
			# both da and a since we want to be able to compare expected and
			# predicted results.
			bounded = False
			for par in range(self.nb_par):
				if self.a[par] < self.a_min[par]:
					self.da[par] += self.a_min[par] - self.a[par]
					self.a[par] = self.a_min[par]
					bounded = True
				elif self.a[par] > self.a_max[par]:
					self.da[par] += self.a_max[par] - self.a[par]
					self.a[par] = self.a_max[par]
					bounded = True
			
			# If one of the parameter was bounded during this iteration,
			# recalculate the scaled norm of da.
			if bounded:
				norm_scaled_da = 0.0
				for par in range(self.nb_par):
					self.scaled_da[par] = self.D[par]*self.da[par]
					norm_scaled_da += self.scaled_da[par]*self.scaled_da[par]
				norm_scaled_da = sqrt(norm_scaled_da)
			
			# Evaluation the function at the new point.
			self.Y = self.f(self.a, *self.f_par)
			self.nb_f_eval += 1
			
			# Calculate chi_2.
			new_chi_2 = 0.0
			for i in range(self.nb_points):
				if self.inequalities[i] == SMALLER and self.Y[i] < self.Yi[i]:
					continue
				elif self.inequalities[i] == LARGER and self.Y[i] > self.Yi[i]:
					continue
				temp = (self.Yi[i]-self.Y[i])/self.sigma[i]
				new_chi_2 += temp*temp
			
			# Calculate the normalized actual reduction.
			actual_reduction = 1.0 - (new_chi_2 / self.chi_2)
			
			# Calculate the normalized predicted reduction of chi square and
			# gamma.
			part1 = 0.0
			for i in range(self.nb_points):
				if self.use_point[i]:
					temp = 0.0
					for par in range(self.nb_par):
						if self.use_par[par]:
							temp += self.dY[par][i]*self.da[par]/self.sigma[i]
					part1 += temp*temp
			part1 /= self.chi_2
			
			part2 = self.alpha * norm_scaled_da * norm_scaled_da / self.chi_2
			
			predicted_reduction = part1 + 2.0*part2
			gamma = - (part1 + part2)
			
			# Compare the actual and the predicted reduction.
			rho = actual_reduction/predicted_reduction
			
			# If the ratio is low (or negative), reduce the trust region.
			if rho <= 0.25:
				
				if actual_reduction >= 0.0:
					mu = 0.5*gamma / (gamma + 0.5*actual_reduction )
				else:
					mu = 0.5
				
				if ( 0.1 * new_chi_2 >= self.chi_2 or mu < 0.1 ):
					mu = 0.1
				
				self.Delta = mu * min (self.Delta, 10.0 * norm_scaled_da)
				self.alpha /= mu
			
			# If the ratio is high, augment the trust region.
			elif rho >= 0.75 or self.alpha == 0.0:
				self.Delta = 2.0 * norm_scaled_da
				self.alpha *= 0.5
			
			# If there has been improvement, accept the solution and verify if
			# one of the stopping criteria is met.
			if new_chi_2 < self.chi_2:
				self.chi_2 = new_chi_2
				
				# Calculate the norm of the scaled a. This is used to check if
				# Delta gets too small.
				self.norm_scaled_a = 0.0
				for par in range(self.nb_par):
					if self.use_par[par]:
						temp = self.D[par]*self.a[par]
						self.norm_scaled_a += temp*temp
				self.norm_scaled_a = sqrt(self.norm_scaled_a)
				
				# Verify if step criteria are met.
				if self.chi_2 <= self.acceptable_chi_2:
					return CHI_2_IS_OK
				elif actual_reduction < self.min_chi_2_change and predicted_reduction < self.min_chi_2_change:
					return CHI_2_CHANGE_TOO_SMALL
				
				return IMPROVING
			
			# Otherwise revert to the previous solution and try again.
			else:
				for par in range(self.nb_par):
					self.a[par] = self.previous_a[par]
				
				# If Delta is smaller than the machine precision, we cannot do
				# any better!
				if self.norm_scaled_a == 0.0:
					if self.Delta < epsilon:
						return DELTA_IS_TOO_SMALL
				else:
					if self.Delta/self.norm_scaled_a < epsilon:
						return DELTA_IS_TOO_SMALL
	
	
	######################################################################
	#                                                                    #
	# get_correlation_matrix                                             #
	#                                                                    #
	######################################################################
	def get_correlation_matrix(self):
		"""Get the correlation matrix
	  
	  This method takes no arguments and simply return the value of
	  correlation matrix between the various parameters. When the norm
	  of a column is zero, all correlation elements related to it are
	  undefined and set to zero (including the diagonal element)."""
		
		# Determine which points are used considering the inequalities.
		for i in range(self.nb_points):
			if self.inequalities[i] == SMALLER and self.b[i] > 0.0:
				self.use_point[i] = False
			elif self.inequalities[i] == LARGER and self.b[i] < 0.0:
				self.use_point[i] = False
			else:
				self.use_point[i] = True
		
		# Get the derivatives matrix.
		self.dY = self.df(self.a, *self.f_par)
		sums = [0.0]*self.nb_par
		sums_squares = [0.0]*self.nb_par
		
		for par in range(self.nb_par):
			for i in range(self.nb_points):
				if self.use_point[i]:
					temp = self.dY[par][i] / self.sigma[i]
					sums[par] += temp
					sums_squares[par] += temp * temp
		
		# Create the covariance matrix.
		C = [[0.0]*self.nb_par for par in range(self.nb_par)]
		
		# Calculate cross products.
		for par_1 in range(self.nb_par):
			for par_2 in range(par_1, self.nb_par):
				for i in range(self.nb_points):
					if self.use_point[i]:
						C[par_1][par_2] += (self.dY[par_1][i]/self.sigma[i])*(self.dY[par_2][i]/self.sigma[i])
		
		# Calculate the covariance.
		for par_1 in range(self.nb_par):
			a = self.nb_points*sums_squares[par_1] - sums[par_1]*sums[par_1]
			for par_2 in range(par_1, self.nb_par):
				b = self.nb_points*sums_squares[par_2] - sums[par_2]*sums[par_2]
				numerator = self.nb_points*C[par_1][par_2] - sums[par_1]*sums[par_2]
				# Catch all kinds of problems including division by zero, ab
				# being negative (numerically) or overflow of the sums.
				try:
					C[par_1][par_2] = C[par_2][par_1] = numerator/sqrt(a*b)
				except (ZeroDivisionError, OverflowError, ValueError):
					C[par_1][par_2] = C[par_2][par_1] = 0.0
		
		return C
	
	
	######################################################################
	#                                                                    #
	# get_chi_2                                                          #
	#                                                                    #
	######################################################################
	def get_chi_2(self):
		"""Get the value of chi square
	  
	  This method takes no arguments and simply return the value of
	  chi square."""
		
		return self.chi_2
	
	
	######################################################################
	#                                                                    #
	# get_norm_gradient                                                  #
	#                                                                    #
	######################################################################
	def get_norm_gradient(self):
		"""Get the norm of the gradient
	  
	  This method takes no arguments and simply return the norm of the
	  gradient."""
		
		return self.norm_gradient
	
	
	######################################################################
	#                                                                    #
	# get_stats                                                          #
	#                                                                    #
	######################################################################
	def get_stats(self):
		"""Get the value of some statistics.
	  
	  This method takes no arguments and returns:
	    nb_f_eval               the number of function evaluation done
	                            during the fit;
	    nb_df_eval              the number of jacobian evaluation done
	                            during the fit."""
		
		return self.nb_f_eval, self.nb_df_eval
