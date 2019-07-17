# Newton_polynomials.py
# 
# Linear, quadratic and cubic polynomials using Newton's method.
# 
# Copyright (c) 2006 Stephane Larouche.
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



########################################################################
#                                                                      #
# Newton_linear                                                        #
#                                                                      #
########################################################################
def Newton_linear(X, Y):
	"""Get the linear polynomial passing by 2 points using Newton's
	method.
	
	The function takes two arguments:
	  X and Y                  lists containing x and y values;
	and returns two arguments:
	  a_0 and a_1              the parameters of the equation."""
	
	f_01 = (Y[1]-Y[0]) / (X[1]-X[0])
	
	a_0 = Y[0] - f_01*X[0]
	a_1 = f_01
	
	return a_0, a_1



########################################################################
#                                                                      #
# Newton_quadratic                                                     #
#                                                                      #
########################################################################
def Newton_quadratic(X, Y):
	"""Get the quadratic polynomial passing by 3 points using Newton's
	method.
	
	The function takes two arguments:
	  X and Y                  lists containing x and y values;
	and returns three arguments:
	  a_0, a_1 and a_2         the parameters of the equation."""
	
	f_01 = (Y[1]-Y[0]) / (X[1]-X[0])
	f_12 = (Y[2]-Y[1]) / (X[2]-X[1])
	f_012 = (f_12-f_01) / (X[2]-X[0])
	
	a_0 = Y[0] - f_01*X[0] + f_012*X[0]*X[1]
	a_1 = f_01 - f_012*(X[0]+X[1])
	a_2 = f_012
	
	return a_0, a_1, a_2



########################################################################
#                                                                      #
# Newton_cubic                                                         #
#                                                                      #
########################################################################
def Newton_cubic(X, Y):
	"""Get the cubic polynomial passing by 4 points using Newton's
	method.
	
	The function takes two arguments:
	  X and Y                  lists containing x and y values;
	and returns four arguments:
	  a_0, a_1, a_2 and a_3    the parameters of the equation."""
	
	f_01 = (Y[1]-Y[0]) / (X[1]-X[0])
	f_12 = (Y[2]-Y[1]) / (X[2]-X[1])
	f_23 = (Y[3]-Y[2]) / (X[3]-X[2])
	f_012 = (f_12-f_01) / (X[2]-X[0])
	f_123 = (f_23-f_12) / (X[3]-X[1])
	f_0123 = (f_123-f_012) / (X[3]-X[0])
	
	a_0 = Y[0] - f_01*X[0] + f_012*X[0]*X[1] - f_0123*X[0]*X[1]*X[2]
	a_1 = f_01 - f_012*(X[0]+X[1]) + f_0123*(X[0]*X[1]+X[0]*X[2]+X[1]*X[2])
	a_2 = f_012 - f_0123*(X[0]+X[1]+X[2])
	a_3 = f_0123
	
	return a_0, a_1, a_2, a_3
