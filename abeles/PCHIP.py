# PCHIP.py
# 
# Class to interpolate using piecewise cubic hermite interpolating
# polynomials that allows preservation of monotonicity.
# 
# Copyright (c) 2014 Stephane Larouche.
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



# REMOVE when Python 3.0 will be out.
from __future__ import division

from moremath.limits import epsilon



########################################################################
#                                                                      #
# PCHIP_error                                                          #
#                                                                      #
########################################################################
class PCHIP_error(Exception):
	"""An exception derived class for PCHIP errors."""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "PCHIP error: %s." % self.value



########################################################################
#                                                                      #
# PCHIP                                                                #
#                                                                      #
########################################################################
class PCHIP(object):
	"""Interpolate a function using piecewise cubic hermite interpolating polynomials
	
	This class implements the piecewise cubic hermite interpolating
	polynomial (PCHIP) algorithm as described in
	  James M. Hyman, "Accurate Monotonicity Preserving Cubic
	  Interpolation", SIAM J. Sci. and Stat. Comput., vol. 4, 1983,
	  pp. 645-654.
	
	It allows the preservation of the monoticity of the interpolated
	function."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, xa, ya, preserve_monotonicity = False, allow_extrapolation = False):
		"""Initialize the PCHIP algorithm
		
		This method takes between 2 and 4 arguments:
		  xa, ya                 list of x and y values of the data points
		                         used for interpolation, the values of x
		                         must be in increasing order;
		  preserve_monotonicity  (optional) a boolean indicating if the
		                         monotonocity should be preserved (default
		                         is False);
		  allow_extrapolation    (optional) a boolesn indicating if
		                         extrapolation should be allowed (default
		                         is False).
		Both lists must be of the same length. This class does not make a
		copy of xa and ya. This class calculates the interpolant the first
		time evaluate, evaluate_derivative, or evaluate_inverse are called.
		Before that, xa and ya can be modified without problems. If they
		are modified later, the caller should call the reset method before
		using one of the evaluate methods."""
		
		self.xa = xa
		self.ya = ya
		self.preserve_monotonicity = preserve_monotonicity
		self.allow_extrapolation = allow_extrapolation
		
		self.nb_points = len(self.xa)
		
		# It is impossible to interpolate with a single point.
		if self.nb_points == 1:
			raise PCHIP_error('Cannot interpolate with a single point')
		
		self.prepared = False
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self, xa = None, ya = None):
		"""Reset the PCHIP algorithm
		
		This method can be used to reset the PCHIP algorithm after the
		values of xa and ya have been modified. This method takes up to 2
		arguments
		  xa, ya                 (optional) lists of x and y values of the
		                         data points used for interpolation, the
		                         values of x must be in increasing order.
		If arguments are used, they replace existing lists. In their
		absence, the lists previously given to the class are used, but are
		assumed to have changed. The length of the lists may change, as
		long as both remain of equal length."""
		
		if xa: self.xa = xa
		if ya: self.ya = ya
		
		self.nb_points = len(self.xa)
		
		# It is impossible to interpolate with a single point.
		if self.nb_points == 1:
			raise PCHIP_error('Cannot interpolate with a single point')
		
		self.prepared = False
	
	
	######################################################################
	#                                                                    #
	# prepare                                                            #
	#                                                                    #
	######################################################################
	def prepare(self):
		"""Prepare the PCHIP instance
		
		This method, meant to be used internally, calculates all the
		polynomial coefficients used to evaluate the PCHIP. It does not
		take any argument."""
		
		# Special case for 2 data points.
		if self.nb_points == 2:
			self.a0 = self.ya
			self.a1 = [(self.ya[1]-self.ya[0])/(self.xa[1]-self.xa[0])]*2
			self.a2 = [0.0]
			self.a3 = [0.0]
			
			return
		
		dx = [self.xa[i+1]-self.xa[i] for i in range(self.nb_points-1)]
		S = [(self.ya[i+1]-self.ya[i])/dx[i] for i in range(self.nb_points-1)]
		
		# Parabolic approximation for df.
		df = [((2.0*dx[0]+dx[1])*S[0]-dx[0]*S[1])/(dx[0]+dx[1])] + \
		     [(dx[i-1]*S[i]+dx[i]*S[i-1])/(dx[i-1]+dx[i]) for i in range(1, self.nb_points-1)] + \
		     [((2.0*dx[self.nb_points-2]+dx[self.nb_points-3])*S[self.nb_points-2]-dx[self.nb_points-2]*S[self.nb_points-3])/(dx[self.nb_points-2]+dx[self.nb_points-3])]
		
		# If requested, limit df to make sure monotonicity is preserved.
		if self.preserve_monotonicity:
			if S[0] > 0.0:
				df[0] = min(max(0.0, df[0]), 3.0*S[0])
			elif S[0] < 0.0:
				df[0] = max(min(0.0, df[0]), 3.0*S[0])
			else:
				df[0] = 0.0
			
			for i in range(1, self.nb_points-1):
				S_min = min(S[i-1], S[i])
				S_max = max(S[i-1], S[i])
				
				if S_min > 0.0:
					df[i] = min(max(0.0, df[i]), 3.0*S_min)
				elif S_max < 0.0:
					df[i] = max(min(0.0, df[i]), 3.0*S_max)
				elif df[i] >= 0.0:
					df[i] = min(max(0.0, df[i]), 3.0*min(abs(S[i-1]), abs(S[i])))
				else:
					df[i] = max(min(0.0, df[i]), -3.0*min(abs(S[i-1]), abs(S[i])))
			
			if S[-1] > 0.0:
				df[-1] = min(max(0.0, df[-1]), 3.0*S[-1])
			elif S[-1] < 0.0:
				df[-1] = max(min(0.0, df[-1]), 3.0*S[-1])
			else:
				df[-1] = 0.0
		
		# Calculate the factors on the piecewise polynomial.
		self.a0 = self.ya
		self.a1 = df
		self.a2 = [(3.0*S[i]-df[i+1]-2.0*df[i])/dx[i] for i in range(self.nb_points-1)]
		self.a3 = [-(2.0*S[i]-df[i+1]-df[i])/(dx[i]*dx[i]) for i in range(self.nb_points-1)]
	
	
	######################################################################
	#                                                                    #
	# evaluate                                                           #
	#                                                                    #
	######################################################################
	def evaluate(self, x, y = None, indices = None):
		"""Evaluate the function according the the interpolation
		
		This method takes between 1 and 3 arguments:
		  x                 an array of the x values at which to evaluate
		                    the function;
		  y                 (optional) an array in which to store the
		                    values calculated using the interpolation;
		  indices           (optional) an array of the position of the x
		                    values inside the interpolation points. If not
		                    given, this method will calculate it itself.
		It returns the y list."""

		if not self.prepared: self.prepare()
		
		if y is None: y = [0.0]*len(x)
		
		for i, xi in enumerate(x):
			if indices: index = indices[i]
			else: index = locate(self.xa, xi, self.allow_extrapolation)
			
			dx = xi - self.xa[index]
			y[i] = self.a0[index] + dx * (self.a1[index] + dx * (self.a2[index] + dx * self.a3[index]))
		
		return y
	
	
	######################################################################
	#                                                                    #
	# evaluate_derivative                                                #
	#                                                                    #
	######################################################################
	def evaluate_derivative(self, x, dy = None, indices = None):
		"""Evaluate the derivative of the function according to the interpolation
		
		This method takes between 1 and 2 arguments:
		  x                 an array of the x values at which to evaluate
		                    the derivative;
		  dy                (optional) an array in which to store the
		                    derivatives calculated using the interpolation;
		  indices           (optional) an array of the position of the x
		                    values inside the interpolation points. If not
		                    given, this method will calculate it itself.
		It returns the dy list."""

		if not self.prepared: self.prepare()
		
		if dy is None: dy = [0.0]*len(x)
		
		for i, xi in enumerate(x):
			if indices: index = indices[i]
			else: index = locate(self.xa, xi, self.allow_extrapolation)
			
			dx = xi - self.xa[index]
			dy[i] = self.a1[index] + dx * (2.0*self.a2[index] + dx * 3.0*self.a3[index])
		
		return dy


	######################################################################
	#                                                                    #
	# evaluate_inverse                                                   #
	#                                                                    #
	######################################################################
	def evaluate_inverse(self, y, x = None, indices = None):
		"""Evaluate the inverse of the PCHIP at a series of points
		
		This method allows to find the values of x corresponding to y
		values. This method takes between 1 and 3 arguments:
		  y                 an array of the y values at which to evaluate
		                    the inverse of the PCHIP;
		  x                 (optional) an array in which to write the
		                    values of x determined using the PCHIP;
		  indices           (optional) an array of the position of the x
		                    values inside the interpolation points. If not
		                    given, this method will calculate it itself.
		It returns x.
		
		The values of ya used when creating the PCHIP must be monotonically
		increasing to use this method (the method does not check they are)."""

		if not self.prepared: self.prepare()
		
		if not x: x = [0.0]*len(y)
		
		# We find the roots using the Newton method, secured by bounds to
		# make sure it does not diverge. For details, see
		#   Press et al., Numerical Recipes in C: the Art of Scientific
		#   Computing, 2nd edition, Cambridge University Press, 1997,
		#   pp. 362-368.
		#
		# We don't use the analytical approach because it is unstable when
		# the third order coefficient is close to 0, which happens
		# regularly.
		
		for i in range(len(y)):
			if indices: index = indices[i]
			else: index = locate(self.ya, y[i], self.allow_extrapolation)
			
			# Get end points.
			x_l = 0.0
			y_l = self.ya[index]-y[i]
			
			x_h = self.xa[index+1] - self.xa[index]
			y_h = self.ya[index+1]-y[i]
	
			# Get the coefficients of the polynomial.
			a0 = y_l
			a1 = self.a1[index]
			a2 = self.a2[index]
			a3 = self.a3[index]
			
			# Choose the end point with the smallest value as the starting
			# point.
			if -y_l < y_h:
				x_ = x_l
				y_ = y_l
			else:
				x_ = x_h
				y_ = y_h
			
			while y_:
				# Determine derivative and approximate root using Newton step.
				dy_ = a1 + x_ * (2.0*a2 + x_*3.0*a3)
				if dy_: x_ = x_ - y_/dy_
				
				# If the Newton approximation is outside of the bounds, perform
				# bisection.
				if dy_ == 0.0 or x_ <= x_l or x_ >= x_h:
					x_ = 0.5*(x_l+x_h)
				
				# Calculate the new value.
				y_ = a0 + x_ * (a1 + x_ * (a2 + x_ * a3))
				
				# Replace the limit according to the sign of the value.
				if y_ < 0.0:
					x_l = x_
					y_l = y_
				else:
					x_h = x_
					y_h = y_
				
				# If the difference between the bounds is (numerically) null,
				# terminate loop.
				if (x_h - x_l) <= (x_l + x_h)*epsilon: break
			
			x[i] = self.xa[index]+x_
		
		return x



########################################################################
#                                                                      #
# locate                                                               #
#                                                                      #
########################################################################
def locate(X, x, allow_extrapolation):
	"""Search an ordered table
	
	Locate in what interval of an ordered table X the value x is
	located. This function takes 3 arguments:
	  X                      a list of ordered values in increasing
	                         order;
	  x                      the value to localize;
	  allow_extrapolation    a boolean indicating if extrapolation is
	                         allowed.
	It returns the position of the interval in which x is located by
	the index of the lower value bonding the interval in which x is
	located. If x is outsite of X, it will return the first or the last
	interval if allow_extrapolation is True, or raise a PCHIP_error
	if allow_extrapolation is False."""
	
	# If x falls out of X, return immediatly.
	if x < X[0]:
		if allow_extrapolation: return 0
		else: raise PCHIP_error("Extrapolation not allowed")
	if x > X[-1]:
		if allow_extrapolation: return len(X)-2
		else: raise PCHIP_error("Extrapolation not allowed")
	
	# Otherwise, perform bissection.
	lim_inf = 0
	lim_sup = len(X) - 1
	while lim_sup-lim_inf > 1:
		middle = (lim_sup+lim_inf)//2;
		if x <= X[middle]: lim_sup = middle
		else: lim_inf = middle
	
	return lim_inf;
