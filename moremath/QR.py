# -*- coding: UTF-8 -*-

# QR.py
# 
# This file provides functions to solve linear equation systems using
# QR orthogonalization. Both rank deficient and overdetermined systems
# are accepted.
#	
# For details on the QR algorigthm, see 
#   Gene H. Golub and Charles F. van Loan, Matrix Computations, John
#   Hopkins University Press, 1983.
# 
# Copyright (c) 2005,2006,2008,2009 Stephane Larouche.
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

import limits



epsilon = limits.epsilon



########################################################################
#                                                                      #
# QR                                                                   #
#                                                                      #
########################################################################
def QR(A, diag, perm, norms = None):
	"""Perform QR factorization of a matrix with column pivoting.
	
	Perform the QR factorization of a n by m matrix using Householder
	transformations. The Q matrix is orthogonal and the R matrix is upper
	triangular. The function takes three or four arguments:
	  A          the matrix;
	  diag       a vector of length n to store the diagonal of the R
	             matrix;
	  perm       a vector of length n to store the column permutations;
	  norms      (optional) a vector of length n to store the norms of
	             the columns of A (usefull in the Levenberg-Marquardt
	             method).
	
	On output, the upper triangular part of the A matrix is replaced by
	the R matrix except for its diagonal while the lower triangular part
	stores a factored form of the Q matrix. The diagonal elements of R
	are returned in diag and the column permutations in perm.
	
	The function returns the rank of the matrix."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	m = len(A[0])
	
	# Permutations.
	for j in range(n):
		perm[j] = j
	
	# Calculate the norm of each column.
	gamma = [0.0]*n
	for j in range(n):
		for i in range(m):
			gamma[j] += A[j][i]*A[j][i]
	
	# Remember the original norm of each column.
	original_gamma = gamma[:]
	
	# Save the norm of the columns.
	if norms:
		for j in range(n):
			norms[j] = sqrt(gamma[j])
	
	# Establish a criteria for singular matrices. To obtain a scale
	# independant determination of the rank, the criteria is applied on
	# the norms of the columns of the original matrix.
	criteria = 2.0 * max(n, m) * epsilon
	
	# If the loop doesn't abnormaly terminate, the rank is the smallest
	# dimension of the matrix.
	rank = min(n, m)
	
	for k in range(rank):
		
		# Find the unprocessed column with the largest norm.
		col = k
		for j in range(k+1, n):
			if gamma[j] > gamma[col]:
				col = j
		
		# If the largest norm or the remaining column is 0, all columns are
		# 0 and the matrix is rank deficient. Return immediatly, the rank
		# of the matrix is k.
		if gamma[col] == 0.0 or gamma[col] < criteria * original_gamma[col]:
			rank = k
			break
		
		# Permute gammas, perms and a_ij's.
		if col != k:
			gamma[k], gamma[col] = gamma[col], gamma[k]
			original_gamma[k], original_gamma[col] = original_gamma[col], original_gamma[k]
			perm[k], perm[col] = perm[col], perm[k]
			for i in range(m):
				A[k][i], A[col][i] = A[col][i], A[k][i]
		
		# Compute the norm of the actual column, A[k][k:].
		norm = 0.0
		for i in range(k, m):
			norm += A[k][i]*A[k][i]
		norm = sqrt(norm)
		
		# Use the same sign for the normalization and A[k][k] to reduce
		# numerical errors.
		if A[k][k] < 0.0:
			norm = -norm
		
		# The Householder vector u is any multiple of
		#   A[k][k:] ± norm(A[k][k:])*e_1
		# where e_1 is a unit vector and the sign is chosen in fonction of
		# the sign of A[k][k] to avoid the substraction of two similar
		# values. The Householder matrix, acting on the n - k last columns
		# is P_k =  1 - 2*u*u'/u'*u. To save some calculation time, it
		# would be good to store u'*u. A clever way to do that is to divide
		# all elements of u by ±norm(A[k][k:]); the first element of this
		# vector is then equal to half its norm. The u vector is stored in
		# the lower triangular part of A since the elements of the R matrix
		# at those positions are null; The diagonal elements of the R
		# matrix are kept in diag.
		for i in range(k, m):
			A[k][i] /= norm
		A[k][k] += 1.0
		
		# To understand how the Householder matrix acts, let's look at the
		# case of a 3 by 3 matrix:
		# 
		#                |u1|                    |A11 A12 A13|
		#   PA = ( I - 2 |u2| |u1 u2 u3| / u'*u) |A21 A22 A23|
		#                |u3|                    |A31 A32 A33|
		#   
		#                |u1*u1 u1*u2 u1*u3|         |A11 A12 A13|
		#      = ( I - 2 |u2*u1 u2*u2 u2*u3| / u'*u) |A21 A22 A23|
		#                |u3*u1 u3*u2 u3*u3|         |A31 A32 A33|
		#   
		#                |u1*u1 u1*u2 u1*u3|         |A11 A12 A13|
		#      = ( I - 2 |u2*u1 u2*u2 u2*u3| / u'*u) |A21 A22 A23|.
		#                |u3*u1 u3*u2 u3*u3|         |A31 A32 A33|
		# 
		# Elements of PA are
		# 
		#                                      |A1i|
		#   PAji = Aji - 2 |uj*u1 uj*u2 uj*u3| |A2i| / u'*u
		#                                      |A3i|
		#   
		#                                |A1i|
		#        = Aji - 2 uj |u1 u2 u3| |A2i| / u'*u.
		#                                |A3i|
		# 
		# Therefore we calculate PA column by column to calculate only once
		# the dot product between u and the i'th column of the A matrix.
		# 
		# Remember that the first element of the u vector, stored in
		# A[k][k] is equal to u'*u/2.
		
		# Apply the transformation on A[k][k].
		diag[k] = -norm
		
		# Apply the transformation on the other columns.
		for j in range(k+1, n):
			
			# Calculate the dot product.
			dot_product = 0.0
			for i in range(k, m):
				dot_product += A[k][i] * A[j][i]
			
			temp = dot_product / A[k][k]
			
			# Update A.
			for i in range(k, m):
				A[j][i] -= A[k][i] * temp
		
		# Update the norms.
		for j in range(k+1, n):
			gamma[j] -= A[j][k]*A[j][k]
	
	# Set all elements in positions greater than the rank in the diagonal
	# of the R matrix to 0.
	for i in range(rank, n):
		diag[i] = 0.0
	
	return rank



########################################################################
#                                                                      #
# QTb                                                                  #
#                                                                      #
########################################################################
def QTb(A, diag, perm, b):
	"""Compute inv(Q) * b = Q' * b.
	
	Make the first step in the solving of a linear system of equations 
	Ax = b from the QR factorization: calculating inv(Q) * b. The
	function takes four arguments:
	  A      a matrix containing R (except for its diagonal) and a
	         factored form of the Q matrix;
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  b      the b vector, on exit, it is replaced by inv(Q)*b.
	
	If the matrix is rank deficient, a solution is returned having rank
	non-nul components at positions corresponding to the columns with the
	largest norms."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	m = len(A[0])
	
	# Determine the rank.
	for rank in range(n, 0, -1):
		if diag[rank-1] != 0.0:
			break
	
	# Calculate inv(Q)*b = Q'*b = ... Q3' Q2' Q1' b.
	
	# Calculate Q'b by successively applying the Qi' matrices. The
	# details of calculation are identical to that in the QR
	# factorization function.
	for k in range(rank):
		
		# Calculation the dot product of the u vector and the c vector.
		dot_product = 0.0
		for i in range(k, m):
			dot_product += A[k][i] * b[i]
		
		temp = dot_product / A[k][k]
		
		# Multiply by the matrix.
		for i in range(k, m):
			b[i] -= A[k][i] * temp



########################################################################
#                                                                      #
# Qb                                                                   #
#                                                                      #
########################################################################
def Qb(A, diag, perm, b):
	"""Compute inv(Q') * b = Q * b.
	
	Calculate inv(Q') * b that is used in the solution of rank deficient
	systems of equations. The function takes four arguments:
	  A      a matrix containing R (except for its diagonal) and a
	         factored form of the Q matrix;
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  b      the b vector, on exit, it is replaced by inv(Q')*b.
	
	If the matrix is rank deficient, a solution is returned having rank
	non-nul components at positions corresponding to the columns with the
	largest norms."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	m = len(A[0])
	
	# Determine the rank.
	for rank in range(n, 0, -1):
		if diag[rank-1] != 0.0:
			break
	
	# Calculate inv(Q')*b = Q*b = Q1 Q2 Q3 ... b.
	
	# Calculate Q'b by successively applying the Q matrices. The details
	# of calculation are identical to that in the QR factorization
	# function.
	for k in range(rank-1, -1, -1):
		
		# Calculation the dot product of the u vector and the c vector.
		dot_product = 0.0
		for i in range(k, m):
			dot_product += A[k][i] * b[i]
		
		temp = dot_product / A[k][k]
		
		# Multiply by the matrix.
		for i in range(k, m):
			b[i] -= A[k][i] * temp



########################################################################
#                                                                      #
# R_solve                                                              #
#                                                                      #
########################################################################
def R_solve(A, diag, perm, c, x):
	"""Solve the upper triangular system R * x = c.
	
	Make the second step in the solving of a linear system of equations 
	Ax = b from the QR factorization: solving the upper triangular system
	R * x = c where c = inv(Q) * b. The function takes five arguments:
	  A      a matrix containing R (except for its diagonal) and a
	         factored form of the Q matrix;
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  c      the inv(Q)*b vector;
	  x      a vector to store the solution x.
	
	If the matrix is rank deficient, a solution is returned having rank
	non-nul components at positions corresponding to the columns with the
	largest norms."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	
	# Determine the rank.
	for rank in range(n, 0, -1):
		if diag[rank-1] != 0.0:
			break
	
	# Create a vector for x with permutations.
	x_perm = [0.0]*n
	
	# Solve the triangular system Rx = c.
	for k in range(rank-1, -1, -1):
		
		# Calculate the sum for parameters already determined.
		sum = 0.0
		for j in range(k+1, n):
			sum += A[j][k] * x_perm[j]
		
		# Find the unknown parameter.
		x_perm[k] = (c[k] - sum) / diag[k]
	
	# Replace in the right order.
	for j in range(n):
		x[perm[j]] = x_perm[j]



########################################################################
#                                                                      #
# RT_solve                                                             #
#                                                                      #
########################################################################
def RT_solve(A, diag, perm, c, z):
	"""Solve the lower triangular system R' * z = c.
	
	Solve the lower triangular system R' * z = c that is used in rank
	deficient systems of equations. The function takes five arguments:
	  A      a matrix containing R (except for its diagonal) and a
	         factored form of the Q matrix;
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  c      the c vector;
	  z      a vector to store the solution z.
	
	If the matrix is rank deficient, a solution is returned having rank
	non-nul components at positions corresponding to the columns with the
	largest norms."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	
	# Determine the rank.
	for rank in range(n, 0, -1):
		if diag[rank-1] != 0.0:
			break
	
	# Permute c.
	c_perm = [c[perm[j]] for j in range(n)]
	
	# Solve the triangular system R'z = c.
	for k in range(rank):
		
		# Calculate the sum for parameters already determined.
		sum = 0.0
		for j in range(k):
			sum += A[k][j] * z[j]
		
		# Find the unknown parameter.
		z[k] = (c_perm[k] - sum) / diag[k]



########################################################################
#                                                                      #
# rank_deficient_R_solve                                               #
#                                                                      #
########################################################################
def rank_deficient_R_solve(A, diag, perm, c, x = None):
	"""Solve the upper trapezoidal system R * x = c in the least squares
	sense.
	
	Make the second step in the solution of a rank deficient linear
	system of equations Ax = b from the QR factorization: solving the
	upper trapezoidal system R * x = c where c = inv(Q) * b in the least
	squares sense. That is the solution having the smallest norm. The
	function takes four or five arguments:
	  A      a matrix containing R (except for its diagonal);
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  c      the inv(Q)*b vector;
	  x      (optional) a vector to store the solution x;
	and returns the solution vector x."""
	
	n = len(A)
	
	if x is None:
		x = [0.0]*n
	
	# Determine the rank.
	for rank in range(n, 0, -1):
		if diag[rank-1] != 0.0:
			break
	
	# Create the R' matrix and fill it.
	RT = [[0.0]*n for j in range(rank)]
	for i in range(rank):
		RT[i][i] = diag[i]
		for j in range(i+1, n):
			RT[i][j] = A[j][i]
	
	# Create vectors for the diagonal and permutations of the QR
	# decomposition of the R' matrix and for intermediate results.
	diagRT = [0.0]*rank
	permRT = [0]*rank
	z = [0.0]*n
	
	# Calculate the QR decomposition of the R' matrix.
	QR(RT, diagRT, permRT)
	
	# Solve the triangular system R(RT)'z = inv(Q)*b.
	RT_solve(RT, diagRT, permRT, c, z)
	
	# Calculate inv(Q(RT)')*z.
	Qb(RT, diagRT, permRT, z)
	
	# Replace in the right order.
	for j in range(n):
		x[perm[j]] = z[j]
	
	return x



########################################################################
#                                                                      #
# QR_solve                                                             #
#                                                                      #
########################################################################
def QR_solve(A, diag, perm, b, x = None):
	"""Solve a linear system of equations using a QR factorization.
	
	Solve a linear system of equations Ax = b using the QR factorization
	of a n by m matrix given by the QR function. The function takes four
	or five arguments:
	  A      a matrix containing R (except for its diagonal) and a
	         factored form of the Q matrix;
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  b      the b vector, on exit, it is replaced by inv(Q)*b;
	  x      (optional) a vector to store the solution x;
	and returns a single argument:
	  x      the solution.
	
	If the system is rank deficient, the least squares solution is found
	using further factorization. If this property is undesired, one
	should call QTb than R_solve."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	
	# Create the x vector only if necessary.
	if x is None:
		x = [0.0]*n
	
	# The system
	#   Ax = b
	# is equivalent to
	#   Rx = c
	# where
	#   c = inv(Q)b.
	
	# Calculate c = inv(Q) * b (c is stored in b).
	QTb(A, diag, perm, b)
	
	# If the system has full rank, simply solve the upper triangular
	# system R * x = c.
	if diag[n-1] != 0.0:
		R_solve(A, diag, perm, b, x)
	
	# If the system does not have full rank, further factorization is
	# necessary to obtain the least squares solution.
	else:
		rank_deficient_R_solve(A, diag, perm, b, x)
	
	return x



########################################################################
#                                                                      #
# R_solve_with_update                                                  #
#                                                                      #
########################################################################
def R_solve_with_update(A, diag, perm, c, D, x = None):
	"""Update QR factorization and solve R * x = c for the updated system.
	
	Solve the augmented system of equations
	  A * x = b
	  D * x = 0
	where D is a diagonal n by n matrix using the R matrix and
	c = inv(Q) * b of the original system. The function takes five or six
	arguments:
	  A      a matrix containing R (except for its diagonal);
	  diag   a vector containing the diagonal of the R matrix;
	  perm   a vector containing the column permutations done during the
	         QR factorization;
	  c      the result of inv(Q) * b;
	  D      a vector containing the diagonal elements of the matrix D;
	  x      (optional) a vector to store the solution x;
	and returns a single argument:
	  x      the solution.
	
	On exit, the R matrix (upper part of input A), its diagonal elements
	(diag), perm and c are left intact to allow solutions for other
	updates. However, the Q matrix (lower part of A including diagonal)
	is replaced by the transpose of the updated R matrix."""
	
	# n is the number of columns, m is the number of rows.
	n = len(A)
	m = len(A[0])
	
	# Create the x vector only if necessary.
	if x is None:
		x = [0.0]*n
	
	# Create a copy of the c vector. We will work on the copy to keep c
	# intact for further updates.
	c_ = c[:]
	
	# Create a temporary array for the row that is eliminated.
	temp = [0.0]*n
	
	# The transpose of the updated R matrix is stored in the lower part
	# of A, destroying the Q matrix.
	for i in range(n):
		A[i][i] = diag[i]
		for j in range(i):
			A[j][i] = A[i][j]
	
	# Update R with diagonal elements included in D.
	for i in range(n):
		
		# Determine on which row to operate using the permutation matrix.
		row = perm[i]
		
		# If the diagonal element is null, it's not necessary to eliminate
		# it.
		if D[row] == 0.0: continue
		
		# Initialize the row to be eliminated. We don't care about the i
		# first elements.
		temp[i] = D[row]
		for j in range(i+1, n):
			temp[j] = 0.0
		ck = 0.0
		
		# Do a serie of Givens rotation to elimate the diagonal element.
		# Every rotation will only affect elements in columns at left of
		# the currently eleminated element.
		for j in range(i, n):
			if A[j][j] == 0.0:
				sin = 1.0
				cos = 0.0
			elif abs(temp[j]) >= abs(A[j][j]):
				tan = A[j][j]/temp[j]
				sin = 1.0/sqrt(1.0+tan*tan)
				cos = sin*tan
			else:
				tan = temp[j]/A[j][j]
				cos = 1.0/sqrt(1.0+tan*tan)
				sin = cos*tan
			
			for k in range(j, n):
				v = A[j][k]
				w = temp[k]
				A[j][k] =  cos*v + sin*w
				temp[k] = -sin*v + cos*w
			v = c_[j]
			w = ck
			c_[j] =  cos*v + sin*w
			ck    = -sin*v + cos*w
	
	# Solve the triangular system Rx = c.
	for k in range(n-1, -1, -1):
		
		# If the diagonal element of the A[k][k] matrix is null set the
		# corresponding element of the solution to 0.
		if A[k][k] == 0.0:
			temp[k] = 0.0
			continue
		
		# Calculate the sum for parameters already determined.
		sum = 0.0
		for j in range(k+1, n):
			sum += A[k][j] * temp[j]
		
		# Find the unknown parameter.
		temp[k] = (c_[k] - sum) / A[k][k]
	
	# Replace in the right order.
	for j in range(n):
		x[perm[j]] = temp[j]
	
	return x
