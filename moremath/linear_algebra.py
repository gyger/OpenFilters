# linear_algebra.py
# 
# This file provides basic linear algebra functions. It also defines an
# exception for matrix calculations and a function to show matrices in
# a format similar to that of Matlab.
# 
# Copyright (c) 2004-2007 Stephane Larouche.
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



import math



########################################################################
#                                                                      #
# matrix_error                                                         #
#                                                                      #
########################################################################
class matrix_error(Exception):
	"""An exception for errors in matrix calculations."""
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return self.value



########################################################################
#                                                                      #
# dot_product                                                          #
#                                                                      #
########################################################################
def dot_product(a, b):
	"""Compute the dot product of two vectors.
	
	This function takes two arguments:
	  a, b    two vectors of the same length.
	It returns their dot product."""
	
	# Sum the multiplication of elements.
	dot_product = 0.0
	for i in range(len(a)):
		dot_product += a[i] * b[i]
	
	return dot_product



########################################################################
#                                                                      #
# norm                                                                 #
#                                                                      #
########################################################################
def norm(a):
	"""Compute the norm of a vector.
	
	This function takes a single argument:
	  a        the vector.
	It returns its norm."""
	
	# Sum the multiplication of elements.
	norm = 0.0
	for i in range(len(a)):
		norm += a[i] * a[i]
	
	norm = math.sqrt(norm)
	
	return norm



########################################################################
#                                                                      #
# matrix_sum                                                           #
#                                                                      #
########################################################################
def matrix_sum(A, B, M = None):
	"""Compute the sum of two matrices or vector.
	
	The functions takes two or three arguments:
	  A, B    the two matrices to sum;
	  M       optional argument for the answer.
	It returns the sum.
	
	A, B and M must all be of the same size."""
	
	nb_col = len(A)
	nb_row = len(A[0])
	
	# If necessary, make an answer matrix of the right size.
	if M is None:
		M = [[0.0]*nb_row for col in range(nb_col)]
	
	# Compute the sum.
	for col in range(nb_col):
		for row in range(nb_row):
			M[col][row] = A[col][row] + B[col][row]
	
	return M



########################################################################
#                                                                      #
# matrix_difference                                                    #
#                                                                      #
########################################################################
def matrix_difference(A, B, M = None):
	"""Substract two matrices or vector.
	
	The functions takes two or three arguments:
	  A, B    the two matrices to substract;
	  M       optional argument for the answer.
	It returns the difference.
	
	A, B and M must all be of the same size."""
	
	nb_col = len(A)
	nb_row = len(A[0])
	
	# If necessary, make an answer matrix of the right size.
	if M is None:
		M = [[0.0]*nb_row for col in range(nb_col)]
	
	# Compute the sum.
	for col in range(nb_col):
		for row in range(nb_row):
			M[col][row] = A[col][row] - B[col][row]
	
	return M



########################################################################
#                                                                      #
# matrix_product                                                       #
#                                                                      #
########################################################################
def matrix_product(A, B, M = None):
	"""Compute the product of two matrices or vector.
	
	The functions takes two or three arguments:
	  A, B    the two matrices to multiply;
	  M       optional argument for the answer.
	It returns the product.
	
	The number of rows in A must equal the number of columns in B. If M
	is given it must have the same number of rows than A and the same
	number of columns than B."""
	
	nb_col = len(B)
	nb_row = len(A[0])
	length = len(A)
	
	# If necessary, make an answer matrix of the right size.
	if M is None:
		M = [[0.0]*nb_row for col in range(nb_col)]
	
	# Otherwise, set all the elements of the user supplied matrice to 0.
	else:
		for col in range(nb_col):
			for row in range(nb_row):
				M[col][row] = 0.0
	
	# Compute the matrix.
	for col in range(nb_col):
		for row in range(nb_row):
			for i in range(length):	
				M[col][row] += A[i][row] * B[col][i]
	
	return M		



######################################################################
#                                                                    #
# show_matrix                                                        #
#                                                                    #
######################################################################
def show_matrix(A):
	"""Show a matrix in a friendly form (similar to Matlab)."""
	
	nb_col = len(A)
	nb_row = len(A[0])
	for row in range(nb_row):
		for col in range(nb_col):
			print " %16.12f" % A[col][row],
		print ""
