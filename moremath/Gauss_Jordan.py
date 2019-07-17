# Gauss_Jordan.py
# 
# This file defines a function that solve square linear equation system
# by Gauss-Jordan elimination.
# 
# Copyright (c) 2004-2006,2009 Stephane Larouche.
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



import limits
import linear_algebra



epsilon = limits.epsilon



########################################################################
#                                                                      #
# Gauss_Jordan                                                         #
#                                                                      #
########################################################################
def Gauss_Jordan(A, b = [], use = None):
	"""Perform Gauss-Jordan elimination with full pivoting.
	
	Solve the systems Ax=b where A is a n*n matrix and b is a set of m
	vector of length n. The function takes two or three arguments
	  A    the matrix;
	  b    (optional) a set of right side vectors;
	  use  (optional) a vector of length n indicating which rows and
	       columns to use, allowing the use of the same memory when
	       fixing one value in a system of equations.
	
	The solutions x are returned in the space used for b while A is
	replaced by its inverse. Use without b to simply get the inverse
	of A. The function does not return any output arguments. It will
	raise a matrix_error if the matrix is singular. A matrix is
	considered singular when a scaled pivot is smaller than machine
	precision.
	
	The values in the unused rows and columns of A and b are untouched.
	
	For a detailed description of the Gauss-Jordan method, see 
	  Press et al., Numerical Recipes in C: the Art of Scientific
	  Computing, 2nd edition, Cambridge University Press, 1997,
	  pp. 32-50."""
	
	n = len(A)
	m = len(b)
	
	# Determine the system size considering fixed values.
	if use:
		size = 0
		for i in range(n):
			if use[i]:
				size += 1
	else:
		use = [1]*n
		size = n
	
	# Find the implicit scaling values for each row.
	scaling = [0.0]*n
	for row in range(n):
		if not use[row]: continue
		largest_value = 0.0
		for col in range(n):
			if not use[col]: continue
			if abs(A[col][row]) > largest_value:
				largest_value = abs(A[col][row])
		
		# If the largest value on a row is 0 (all the elements of the
		# row are 0), the matrix is singular.
		if largest_value == 0.0:
			raise linear_algebra.matrix_error("Singular matrix")
		
		scaling[row] = 1.0/largest_value
	
	# Make lists to keep track of columns that have been used and
	# rows that have been permutated. At first, no column have been
	# used and the rows are in their original order.
	pivot_usage = [0]*n
	perm = [0]*n
	for i in range(n):
		perm[i] = i
	
	for i in range(size):
		
		# We do a full pivot with implicit scaling. We therefore have to
		# find the largest scaled value in the rows and columns not already
		# used.
		largest_value = 0.0
		for col in range(n):
			if not use[col]: continue
			if not pivot_usage[col]:
				for row in range(n):
					if not use[row]: continue
					if not pivot_usage[row]:
						value = abs(scaling[row]*A[col][row])
						if value > largest_value:
							largest_value = value
							pivot_col = col
							pivot_row = row
		
		# If the found pivot is 0, the matrix is singular. The machine
		# precision is taken as 0 to avoid numerical errors.
		if largest_value < epsilon:
			raise linear_algebra.matrix_error("Singular matrix")
		
		pivot_usage[pivot_col] = 1
		
		# If the pivot is not on the diagonal, interchange rows.
		if pivot_row != pivot_col:
			for col in range(n):
				if not use[col]: continue
				temp_float = A[col][pivot_col]
				A[col][pivot_col] = A[col][pivot_row]
				A[col][pivot_row] = temp_float
			for vec in range(m):
				temp_float = b[vec][pivot_col]
				b[vec][pivot_col] = b[vec][pivot_row]
				b[vec][pivot_row] = temp_float
			
			# Also interchange scaling factors.
			temp_float = scaling[pivot_row]
			scaling[pivot_row] = scaling[pivot_col]
			scaling[pivot_col] = temp_float
		
		# Keep track of row interchanges.
		temp_int = perm[pivot_col]
		perm[pivot_col] = perm[pivot_row]
		perm[pivot_row] = temp_int
		
		inverse_pivot = 1.0/A[pivot_col][pivot_col]
		
		# Setting the pivot to 1 correspond to changing its value to the one
		# in the identity matrix.
		A[pivot_col][pivot_col] = 1.0
		
		# Divide the row by the pivot to set the diagonal element of A to 1.
		for col in range(n):
			if not use[col]: continue
			A[col][pivot_col] *= inverse_pivot
		for vec in range(m):
			b[vec][pivot_col] *= inverse_pivot
		
		# Reduce the rows. All element of the column, except for the pivot,
		# will be 0 at the end of this operation, therefore they are replaced
		# by the elements of the (not anymore) identity matrix that will be
		# 0 - A[col][row]*I[col][col]. I[col][col] has been determined at the
		# previous step and is stored in A[col][col].
		for row in range(n):
			if not use[row]: continue
			if row != pivot_col:
				
				# We keep the value of the present column and replace it by 0,
				# so that this now represents the value in the (not anymore)
				# identity matrix.
				temp_float = A[pivot_col][row]
				A[pivot_col][row] = 0.0
				
				# We then proceed with the reducing of the row. elements in the
				# (not anymore) identity matrix are reduced as well.
				for col in range(n):
					if not use[col]: continue
					A[col][row] -= temp_float*A[col][pivot_col]
				for vec in range(m):
					b[vec][row] -= temp_float*b[vec][pivot_col]
	
	# Get the column of the inverse matrix in the correct order.
	for col in range(n):
		while perm[col] != col:
			for row in range(n):
				if not use[row]: continue
				A[col][row], A[perm[col]][row] = A[perm[col]][row], A[col][row]
			perm[perm[col]], perm[col] = perm[col], perm[perm[col]]
