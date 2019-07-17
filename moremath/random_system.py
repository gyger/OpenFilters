# random_system.py
# 
# Generate a random linear system of equations to verify solve tools.
# 
# Copyright (c) 2005,2006 Stephane Larouche.
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



import random
import array

from linear_algebra import *



########################################################################
#                                                                      #
# random_system                                                        #
#                                                                      #
########################################################################
def random_system(nb_cols, nb_rows, rank, correct_b = False):
	"""Generate a random system of equations.
	
	The functions takes three or four arguments:
	  nb_cols   the number of columns;
	  nb_rows   the number of rows;
	  rank      the rank of the system;
	  correct_b (optional) wether b should be adjusted according to the
	            rank;
	and returns a random system with those properties:
	  A         the matrix
	  b         the vector."""
	
	# Make the matrix and the vector with random elements.
	A = [[random.uniform(-1.0, 1.0) for row in range(nb_rows)] for col in range(nb_cols)]
	b = [random.uniform(-1.0, 1.0) for row in range(nb_rows)]
	
	if rank < min(nb_cols, nb_rows):
		# Select random combination of the previous rows for the remaining
		# rows.
		temp = [[random.uniform(-1.0, 1.0) for row in range(nb_rows - rank)] for col in range(rank)]
		
		# Get a linear combination of the first columns to determine the last
		# ones.
		dependant_rows = matrix_product(temp, A)
		
		# Put these rows in the matrix.
		for col in range(nb_cols):
			for row in range(nb_rows - rank):
				A[col][row+rank] = dependant_rows[col][row]
		
		# Correct b to make a rank deficient system, if requested.
		if correct_b:
			dependant_rows = matrix_product(temp, [b])
			for row in range(nb_rows - rank):
				b[row+rank] = dependant_rows[0][row]
	
	return A, b
