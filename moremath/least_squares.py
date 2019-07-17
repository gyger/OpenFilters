# least_squares.py
# 
# Linear, quadratic, cubic and general least square fits.
# 
# Copyright (c) 2003 Bill Baloukas.
# Copyright (c) 2002,2003,2005,2006,2008 Stephane Larouche.
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



import QR



########################################################################
#                                                                      #
# least_squares_linear                                                 #
#                                                                      #
########################################################################
def least_squares_linear(X, Y):
	"""Least squares linear regression
	
	The equation y = a_0 + a_1*x is fitted following the method presented
	in Press et al. Numerical Recipes in C, Cambridge University Press,
	1992, pp. 661-666.
	
	The function takes two arguments:
	  X and Y         lists containing x and y values;
	and returns two arguments:
		a_0 and a_1     the parameters of the equation."""
	
	# Since we don't know the the measurement errors, we will simply use
	# S = N.
	
	N = len(X)
	
	S_x = 0.0
	S_y = 0.0
	S_xx = 0.0
	S_xy = 0.0
	x_mean = 0.0
	y_mean = 0.0
	
	for j in range(N):
		S_x += X[j]
		S_y += Y[j]
		S_xx += X[j]*X[j]
		S_xy += X[j]*Y[j]
		x_mean += X[j]
		y_mean += Y[j]
	
	x_mean /= N
	y_mean /= N
	
	Delta = N*S_xx - S_x*S_x
	a_0 = (S_xx*S_y - S_x*S_xy) / Delta
	a_1 = (N*S_xy - S_x*S_y) / Delta
	
	return a_0, a_1



########################################################################
#                                                                      #
# least_squares_quadratic                                              #
#                                                                      #
########################################################################
def least_squares_quadratic(X, Y):
	"""Least squares quadratic regression
	
	The equation y = a_0 + a_1*x + a_2*x^2 is fitted following the method
	presented in Press et al. Numerical Recipes in C, Cambridge University
	Press, 1992, pp. 671-681.
	
	The function takes two arguments:
	  X and Y              lists containing x and y values;
	and returns three arguments:
		a_0, a_1 and a_2     the parameters of the equation."""
	
	N = len(X)
	
	S_x = 0.0    # Contains the summation of x values
	S_x2 = 0.0   # Contains the summation of the square of the x values
	S_x3 = 0.0   # Contains the summation of x^3
	S_x4 = 0.0   # Contains the summation of x^4
	S_y = 0.0    # Contains the summation of y values
	S_xy = 0.0   # Contains the summation of xy
	S_x2y = 0.0  # Contains the summation of (x^2)y
	
	# The individual summations are calculated
	for i in range(N):
		Xi_square = X[i]*X[i]
		S_x += X[i]
		S_x2 += Xi_square
		S_x3 += Xi_square*X[i]
		S_x4 += Xi_square*Xi_square
		S_y += Y[i]
		S_xy += Y[i]*X[i]
		S_x2y += Y[i]*Xi_square
	
	# Once the least squares parameters have been calculated, a system of
	# 3 equations is obtained.  
	# 0 = S_y   - a_0*N    - a_1*S_x  - a_2*S_x2
	# 0 = S_xy  - a_0*S_x  - a_1*S_x2 - a_2*S_x3
	# 0 = S_x2y - a_0*S_x2 - a_1*S_x3 - a_2*S_x4
	# where a_0,a_1 and a_2 are the coefficients of the second order
	# polynomial equation that will fit the data and N is the number of
	# data points. We therefore use a LU decomposition to solve this
	# system of equations.
	
	# LU decomposition - Crout (the diagonal elements of the U matrix are equal to 1)
	#			A            x   X   =    B    =        L         x     U         x   X
	# |S_x2 S_x3 S_x4|   |a_0|   |S_x2y|   |L_11  0    0  |   |1 U_12 U_13|   |a_0|
	# |S_x  S_x2 S_x3| x |a_1| = |S_xy | = |L_21 L_22  0  | x |0  1   U_23| x |a_1|
	# |N    S_x  S_x2|   |a_2|   |S_y  |   |L_31 L_32 L_33|   |0  0   1   |   |a_2|
	# 
	# Please note that X is not the argument of the function.
	
	# By direct comparison we obtain...
	# First column of L
	L_11 = S_x2
	L_21 = S_x
	L_31 = N
	
	# First line of U
	U_12 = S_x3/L_11
	U_13 = S_x4/L_11
	
	# The rest ...
	L_22 = S_x2 - L_21*U_12
	L_32 = S_x - L_31*U_12
	
	U_23 = (S_x3 - L_21*U_13)/L_22 
	
	L_33 = S_x2 - L_31*U_13 - L_32*U_23
	
	# By posing U x X = Y, we obtain L x Y = B
	# 
	# Please note that X and Y are not the arguments of the function.
	Y_1 = S_x2y/L_11
	Y_2 = (S_xy - L_21*Y_1)/L_22
	Y_3 = (S_y - L_31*Y_1 - L_32*Y_2)/L_33
	
	# We can than solve for X : U x X = Y
	a_2 = Y_3
	a_1 = Y_2 - U_23*a_2
	a_0 = Y_1 - U_12*a_1 - U_13*a_2
	
	return a_0, a_1, a_2



########################################################################
#                                                                      #
# least_squares_cubic                                                  #
#                                                                      #
########################################################################
def least_squares_cubic(X, Y):
	"""Least squares cubic regression
	
	The equation y = a_0 + a_1*x + a_2*x^2 + a_3*x^3 is fitted following
	the method presented in Press et al. Numerical Recipes in C, Cambridge
	University Press, 1992, pp. 671-681.
	
	The function takes two arguments:
	  X and Y                  lists containing x and y values;
	and returns four arguments:
		a_0, a_1, a_2 and a_3    the parameters of the equation."""
	
	N = len(X)
	
	S_x = 0.0    # Contains the summation of x values
	S_x2 = 0.0   # Contains the summation of the square of the x values
	S_x3 = 0.0   # Contains the summation of x^3
	S_x4 = 0.0   # Contains the summation of x^4
	S_x5 = 0.0   # Contains the summation of x^5
	S_x6 = 0.0   # Contains the summation of x^6
	S_y = 0.0    # Contains the summation of y values
	S_xy = 0.0   # Contains the summation of xy
	S_x2y = 0.0  # Contains the summation of (x^2)y
	S_x3y = 0.0  # Contains the summation of (x^3)y
	
	# The individual summations are calculated
	for i in range(N):
		Xi_square = X[i]*X[i]
		Xi_cube = Xi_square*X[i]
		S_x += X[i]
		S_x2 += Xi_square
		S_x3 += Xi_cube
		S_x4 += Xi_square*Xi_square
		S_x5 += Xi_square*Xi_cube
		S_x6 += Xi_cube*Xi_cube
		S_y += Y[i]
		S_xy += Y[i]*X[i]
		S_x2y += Y[i]*Xi_square
		S_x3y += Y[i]*Xi_cube
	
	# Once the least squares parameters have been calculated, a system of
	# 4 equations is obtained.  
	# 0 = S_y   - a_0*N    - a_1*S_x  - a_2*S_x2 - a_3*S_x3
	# 0 = S_xy  - a_0*S_x  - a_1*S_x2 - a_2*S_x3 - a_3*S_x4
	# 0 = S_x2y - a_0*S_x2 - a_1*S_x3 - a_2*S_x4 - a_3*S_x5
	# 0 = S_x3y - a_0*S_x3 - a_1*S_x4 - a_2*S_x5 - a_3*S_x6
	# where a_0,a_1, a_2 and a_3 are the coefficients of the third order
	# polynomial equation that will fit the data and N is the number of
	# data points. We therefore use LU Decomposition to solve this
	# system of equations.
	
	# LU decomposition - Crout (the diagonal elements of the U matrix are equal to 1)
	# Define variables
	#			      A          x  X  =   B   =          L          x       U          x  X
	# |S_x3 S_x4 S_x5 S_x6| |a_0| |S_x3y| |L_11   0   0    0  | |1 U_12 U_13 U_14| |a_0|
	# |S_x2 S_x3 S_x4 S_x5|x|a_1|=|S_x2y|=|L_21 L_22  0    0  |x|0  1   U_23 U_24|x|a_1|
	# |S_x  S_x2 S_x3 S_x4| |a_2| |S_xy | |L_31 L_32 L_33  0  | |0  0    1   U_34| |a_2|
	# |N    S_x  S_x2 S_x3| |a_3| |S_y  | |L_41 L_42 L_43 L_44| |0  0    0     1 | |a_3|
	# 
	# Please note that X is not the argument of the function.
	
	# By direct comparison we obtain...
	
	# First column of L
	L_11 = S_x3
	L_21 = S_x2
	L_31 = S_x
	L_41 = N
	
	# First line of U
	iL_11 = 1.0/L_11  # Saves computing time
	U_12 = S_x4*iL_11
	U_13 = S_x5*iL_11
	U_14 = S_x6*iL_11
	
	# The rest ...
	L_22 = S_x3 - L_21*U_12
	L_32 = S_x2 - L_31*U_12
	L_42 = S_x - L_41*U_12
	
	iL_22 = 1.0/L_22
	U_23 = (S_x4 - L_21*U_13)*iL_22 
	U_24 = (S_x5 - L_21*U_14)*iL_22
	
	L_33 = S_x3 - L_31*U_13 - L_32*U_23
	L_43 = S_x2 - L_41*U_13 - L_42*U_23
	
	iL_33 = 1.0/L_33
	U_34 = (S_x4 - L_31*U_14 - L_32*U_24)*iL_33
	
	L_44 = S_x3 - L_41*U_14 - L_42*U_24 - L_43*U_34
	
	# By posing U x X = Y, we obtain L x Y = B
	# 
	# Please note that X and Y are not the arguments of the function.
	Y_1 = S_x3y*iL_11 
	Y_2 = (S_x2y - L_21*Y_1)*iL_22
	Y_3 = (S_xy - L_31*Y_1 - L_32*Y_2)*iL_33
	Y_4 = (S_y - L_41*Y_1 - L_42*Y_2 - L_43*Y_3)/L_44
	
	# We can than solve for X : U x X = Y
	a_3 = Y_4
	a_2 = Y_3 - U_34*a_3
	a_1 = Y_2 - U_23*a_2 - U_24*a_3
	a_0 = Y_1 - U_12*a_1 - U_13*a_2 - U_14*a_3
	
	return a_0, a_1, a_2, a_3



########################################################################
#                                                                      #
# least_squares                                                        #
#                                                                      #
########################################################################
def least_squares(X, Y, order):
	"""Least squares polynomial regression or arbitrary order
	
	The equation y = a_0 + a_1*x + a_2*x^2 + ... is fitted to a series of
	data points using the Vandermonde matrix and QR decomposition.
	
	This function takes 3 arguments:
	  X      the x values of the points to fit
	  Y      the y values of the points to fit;
	  order  the order of the polynomial to fit;
	and returns
	  a      the solution vector [a_0, a_1, ...]."""
	
	nb_points = len(X)
	
	# Build the Vandermonde matrix.
	V = [[1.0]*nb_points for i in range(order+1)]
	for i_point in range(nb_points):
		for i_order in range(order):
			V[i_order+1][i_point] = V[i_order][i_point] * X[i_point]
	
	# Create vectors to store elements of the QR factorization.
	diag = [0.0]*(order+1)
	perm = [0.0]*(order+1)
	
	# Solve by QR factorization.
	QR.QR(V, diag, perm)
	a = QR.QR_solve(V, diag, perm, Y)
	
	return a
