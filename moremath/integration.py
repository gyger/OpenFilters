# integration.py
# 
# 
# Numerically integrate functions.
# 
# Copyright (c) 2006,2007 Stephane Larouche.
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


	
three_eighth = 0.375
seven_sixth = 7.0/6.0
twenty_three_twenty_forth = 23.0/24.0



########################################################################
#                                                                      #
# trapezoidal                                                          #
#                                                                      #
########################################################################
def trapezoidal(f, xa, xb, n):
	"""Numerically integrate a function using the trapezoidal method
	
	This function takes 4 input arguments:
	  f                    the function to integrate, when given a value
	                       x, this function must return the y value;
	  xa, xb               the integration limits;
	  n                    the number of points used in the integration;
	and returns the value of the integral."""
	
	h = (xb-xa)/(n-1)
	
	# The first point.
	y = 0.5*h*f(xa)
	
	# All internal points.
	for i in range(1,n-1):
		y += h*f(xa+i*h)
	
	# The last point.
	y += 0.5*h*f(xb)
	
	return y



########################################################################
#                                                                      #
# cubic                                                                #
#                                                                      #
########################################################################
def cubic(f, xa, xb, n):
	"""Numerically integrate a function using the cubic polynomials
	
	This function takes 4 input arguments:
	  f                    the function to integrate, when given a value
	                       x, this function must return the y value;
	  xa, xb               the integration limits;
	  n                    the number of points used in the integration;
	and returns the value of the integral.
	
	For details on this method, see:
	  Press et al. Numerical Recipes in C, Cambridge University Press,
	  1992, pp. 130-136."""
	
	h = (xb-xa)/(n-1)
	
	# The first three points.
	y = h * (three_eighth*f(xa) + seven_sixth*f(xa+h) + twenty_three_twenty_forth*f(xa+2*h))
	
	# Internal points.
	for i in range(3,n-3):
		y += h*f(xa+i*h)
	
	# The last three points.
	y += h * (twenty_three_twenty_forth*f(xb-2*h) + seven_sixth*f(xb-h) + three_eighth*f(xb))
	
	return y
