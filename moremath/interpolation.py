# interpolation.py
# 
# 
# Functions to perform interpolation. This file implements the cubic
# spline method, linear interpolation and functions to search an
# ordered table.
# 
# The cubic spline implementation is an adaptation of the GNU
# Scientific Library (GSL) (http://sources.redhat.com/gsl/) spline
# and tridiagonal matrix routines.
# 
# For more informations about the method to search an ordered table,
# see Press et al., Numerical Recipes in C: the Art of Scientific
# Computing, 2nd edition, Cambridge University Press, 1997, pp.
# 117-119.
# 
# GSL source code for the spline:
#   Copyright (c) 1996, 1997, 1998, 1999, 2000 Gerard Jungman.
#   Copyright (c) 1996, 1997, 1998, 1999, 2000, 2002 Gerard Jungman,
#   Brian Gough, David Necas.
# 
# Copyright (c) 2002-2003,2005,2008,2014 Stephane Larouche.
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

import math
import array

from roots import roots_cubic



########################################################################
#                                                                      #
# new_spline                                                           #
#                                                                      #
########################################################################
class new_spline(object):
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Create a new spline structure
		
		This method takes 1 argument:
		  length             the number of points defining the spline."""
		
		self.xa = []
		self.ya = []
		
		self.length = length;
		self.c = array.array("d", [0.0]*length)
		self.offdiag = array.array("d", [0.0]*(length-2))
		self.diag = array.array("d", [0.0]*(length-2))
		self.g = array.array("d", [0.0]*(length-2))
		
		self.gamma = array.array("d", [0.0]*(length-2))
		self.alpha = array.array("d", [0.0]*(length-2))
		self.cc = array.array("d", [0.0]*(length-2))
		self.z = array.array("d", [0.0]*(length-2))



########################################################################
#                                                                      #
# del_spline                                                           #
#                                                                      #
########################################################################
def del_spline(spline):
	"""Delete a spline structure
	
	This function takes 1 argument:
	  spline            a pointer to the spline structure to delete."""
	
	del spline



########################################################################
#                                                                      #
# init_spline                                                          #
#                                                                      #
########################################################################
def init_spline(spline, xa, ya):
	"""Initialize the spline structure
	
	This function takes 3 arguments:
	  spline            a pointer to the spline structure to
	                    initialize;
	  xa, ya            arrays of the x and y values to initialize
	                    the spline, the x values must be in
	                    increasing order.
	It then solves the system of equations defined by those points
	using Cholesky decomposition. This function does not make a copy
	of xa and ya, they should not be deleted or modified by the caller."""
	
	num_points = spline.length
	max_index = num_points - 1  # Engeln-Mullges + Uhlig "n"
	sys_size = max_index - 1    # linear system is sys_size x sys_size
	
	spline.xa = xa
	spline.ya = ya
	
	spline.c[0] = 0.0
	spline.c[max_index] = 0.0
	
	for i in range(sys_size):
		h_i   = spline.xa[i + 1] - spline.xa[i]
		h_ip1 = spline.xa[i + 2] - spline.xa[i + 1]
		ydiff_i   = spline.ya[i + 1] - spline.ya[i]
		ydiff_ip1 = spline.ya[i + 2] - spline.ya[i + 1]
		spline.offdiag[i] = h_ip1
		spline.diag[i] = 2.0 * (h_ip1 + h_i)
		spline.g[i] = 3.0 * (ydiff_ip1 / h_ip1  -  ydiff_i / h_i)
	
	# Cholesky decomposition
	# A = L.D.L^t
	# lower_diag(L) = gamma
	# diag(D) = alpha
	spline.alpha[0] = spline.diag[0]
	spline.gamma[0] = spline.offdiag[0] / spline.alpha[0]
	
	for i in range(1, sys_size - 1):
		spline.alpha[i] = spline.diag[i] - spline.offdiag[i-1]*spline.gamma[i-1]
		spline.gamma[i] = spline.offdiag[i] / spline.alpha[i]
	
	if sys_size > 1:
		spline.alpha[sys_size-1] = spline.diag[sys_size-1] - spline.offdiag[sys_size-2]*spline.gamma[sys_size-2]
	
	# update RHS
	spline.z[0] = spline.g[0]
	for i in range(1, sys_size):
		spline.z[i] = spline.g[i] - spline.gamma[i-1]*spline.z[i-1]
	for i in range(sys_size):
		spline.cc[i] = spline.z[i] / spline.alpha[i]
	
	# backsubstitution
	spline.c[sys_size-1+1] = spline.cc[sys_size-1];
	if sys_size >= 2:
		i = sys_size - 2
		for j in range( sys_size - 2 + 1):
			spline.c[i+1] = spline.cc[i] - spline.gamma[i] * spline.c[(i+1)+1]
			i -= 1
	
	return 0



########################################################################
#                                                                      #
# evaluate_spline                                                      #
#                                                                      #
########################################################################
def evaluate_spline(spline, x, y, indices, length):
	"""Evaluate the spline at a series of points
	
	Before calling this function, the spline must have been
	initialized. This function takes 5 arguments:
	  spline            a pointer to the spline structure;
	  x                 an array of the x values at which to evaluate
	                    the spline;
	  y                 an array in which to write the values
	                    calculated using the spline;
	  indices           an array of indices indicating in which
	                    intervals of the original data the values of
	                    x are located
	  length            the length of x, y and indices arrays."""
	
	last_index = -1
	
	for i in range(length):
		index = indices[i]
		
		# I expect the data in the x array to be ordered, most of the time
		# the index won't change and it is possible to save some time by
		# not calculating the coefficients.
		if index != last_index:
			x_hi = spline.xa[index + 1]
			x_lo = spline.xa[index]
			dx = x_hi - x_lo
			y_lo = spline.ya[index]
			y_hi = spline.ya[index + 1]
			dy = y_hi - y_lo
			
			# Common coefficient determination.
			c_i = spline.c[index]
			c_ip1 = spline.c[index + 1]
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0
			d_i = (c_ip1 - c_i) / (3.0 * dx)
			
			last_index = index;
		
		# Evaluate.
		delx = x[i] - x_lo
		y[i] = y_lo + delx * (b_i + delx * (c_i + delx * d_i))
	
	return



########################################################################
#                                                                      #
# evaluate_spline_derivative                                           #
#                                                                      #
########################################################################
def evaluate_spline_derivative(spline, x, dery, indices, length):
	"""Evaluate the derivative of the spline at a series of points
	
	Before calling this function, the spline must have been
	initialized. This function takes 5 arguments:
	  spline            a pointer to the spline structure;
	  x                 an array of the x values at which to evaluate
	                    the spline;
	  dery              an array in which to write the derivatives
	                    calculated using the spline;
	  indices           an array of indices indicating in which
	                    intervals of the original data the values of
	                    x are located
	  length            the length of x, dery and indices arrays."""
	
	last_index = -1
	
	for i in range(length):
		index = indices[i]
		
		# I expect the data in the x array to be ordered, most of the time
		# the index won't change and it is possible to save some time by
		# not calculating the coefficients.
		if index != last_index:
			x_hi = spline.xa[index + 1]
			x_lo = spline.xa[index]
			dx = x_hi - x_lo
			y_lo = spline.ya[index]
			y_hi = spline.ya[index + 1]
			dy = y_hi - y_lo
			
			# common coefficient determination.
			c_i = spline.c[index]
			c_ip1 = spline.c[index + 1]
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0
			d_i = (c_ip1 - c_i) / (3.0 * dx)
			
			last_index = index
		
		# Evaluate.
		delx = x[i] - x_lo
		dery[i] = b_i + delx * (2.0*c_i + delx * 3.0*d_i)
	
	return


########################################################################
#                                                                      #
# evaluate_spline_inverse                                              #
#                                                                      #
########################################################################
def evaluate_spline_inverse(spline, x, y, indices, length):
	"""Evaluate the inverse of the spline at a series of points.
	
	This function allows to find the values of x corresponding to y
	values. Before calling it, the spline must have been initialized.
	This function takes 5 arguments:
	  spline            a pointer to the spline structure;
	  x                 an array in which to write the values of x
	                    determined using the spline;
	  y                 an array of the y values at which to evaluate
	                    the inverse of the spline;
	  indices           an array of indices indicating in which
	                    intervals of the original data the values of
	                    y are located
	  length            the length of x, y and indices arrays."""
	
	last_index = -1
	roots = [0.0]*3
	
	for i in range(length):
		index = indices[i]
		
		# I expect the data in the x array to be ordered, most of the time
		# the index won't change and it is possible to save some time by
		# not calculating the coefficients.
		if index != last_index:
			x_hi = spline.xa[index + 1]
			x_lo = spline.xa[index]
			dx = x_hi - x_lo
			y_lo = spline.ya[index]
			y_hi = spline.ya[index + 1]
			dy = y_hi - y_lo
			
			# Common coefficient determination.
			c_i = spline.c[index]
			c_ip1 = spline.c[index + 1]
			b_i = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0
			d_i = (c_ip1 - c_i) / (3.0 * dx)
			
			last_index = index
		
		nb_roots = roots_cubic(roots, y_lo-y[i], b_i, c_i, d_i)
		
		# Find one solution in the interval.
		if nb_roots > 0 and roots[0] >= 0.0 and roots[0] <= dx: delx = roots[0]
		elif nb_roots > 1 and roots[1] >= 0.0 and roots[1] <= dx: delx = roots[1]
		elif nb_roots > 2 and roots[2] >= 0.0 and roots[2] <= dx: delx = roots[2]
		
		# If no solution is in the interval, we take the closest end. This
		# should not happen, but numerically, the root might be just out
		# of the interval.
		elif (y[i]-y_lo)/dy < 0.5: delx = 0.0
		else: delx = dx
		
		x[i] = x_lo + delx
	
	return



########################################################################
#                                                                      #
# locate                                                               #
#                                                                      #
########################################################################
def locate(X, length, x):
	"""Search an ordered table.
	
	Locate in what interval of an ordered table X the value x is
	located. This function takes two arguments:
	  X    a list of ordered values in increasing order;
	  x    the value to localize.
	It returns the position of the interval in which x is located by
	the index of the lower value bonding the interval in which x is
	located. It returns -1 or length-1 if x is outsite of X."""
	
	# If x falls out of X, return immediatly.
	if x < X[0]: return -1
	if x > X[-1]: return length-1
	
	# Otherwise, perform bissection.
	lim_inf = 0
	lim_sup = length - 1
	while lim_sup-lim_inf > 1:
		middle = (lim_sup+lim_inf)//2;
		if x <= X[middle]: lim_sup = middle
		else: lim_inf = middle
	
	return lim_inf;



########################################################################
#                                                                      #
# spline                                                               #
#                                                                      #
########################################################################
def spline(xa, ya, x):
	"""Interpolate some points using a cubic spline
	
	This function takes 3 arguments:
	  xa, ya               the points between which to interpolate;
	  x                    the x values at which to interpolate."""
	
	# Create and init the spline.
	length = len(xa)
	my_spline = new_spline(length)
	init_spline(my_spline, xa, ya)
	
	# Locate the interpolation intervals.
	nb_points = len(x)
	positions = [0]*nb_points
	for i in range(nb_points):
		positions[i] = locate(xa, length, x[i])
		
		# Accept extrapolation.
		if positions[i] < 0: positions[i] = 0
		elif positions[i] > length-2: positions[i] = length-2
	
	# Evaluate the spline.
	y = [0.0]*nb_points
	evaluate_spline(my_spline, x, y, positions, nb_points)
	
	# Delete the spline
	del_spline(my_spline)
	
	return y



########################################################################
#                                                                      #
# linear_interpolation                                                 #
#                                                                      #
########################################################################
def linear_interpolation(xa, ya, x):
	"""Interpolate some points using a linear interpolation
	
	This function takes 3 arguments:
	  xa, ya               the points between which to interpolate;
	  x                    the x values at which to interpolate."""
	
	length = len(xa)
	nb_points = len(x)
	
	# Locate the interpolation intervals.
	positions = [0]*nb_points
	for i in range(nb_points):
		positions[i] = locate(xa, length, x[i])
		
		# Accept extrapolation.
		if positions[i] < 0: positions[i] = 0
		elif positions[i] > length-2: positions[i] = length-2
	
	# Evaluate the interpolation.
	y = [0.0]*nb_points
	for i in range(nb_points):
		K_i_plus_1 = (x[i]-xa[positions[i]]) / (xa[positions[i]+1]-xa[positions[i]])
		K_i = 1.0 - K_i_plus_1
		
		y[i] = K_i*ya[positions[i]] + K_i_plus_1*ya[positions[i]+1]
	
	return y
	