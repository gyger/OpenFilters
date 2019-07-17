# matrices.py
# 
# A class to create, handle and multiply Abeles characteristic
# matrices.
# 
# Copyright (c) 2000-2007,2009,2012 Stephane Larouche.
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
import cmath



two_pi = 2.0*math.pi



########################################################################
#                                                                      #
# matrices                                                             #
#                                                                      #
########################################################################
class matrices(object):
	"""A class to create, handle and multiply Abeles characteristic
	matrices"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the matrices class to store the
		characteristic matrices of a stack
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    characteristic matrices."""
	
		self.wvls = wvls
		
		# The correspondance between the position in the vector and the
		# position in the 2 by 2 Abeles matrix is:
		#   0 -> 1,1
		#   1 -> 1,2
		#   2 -> 2,1
		#   3 -> 2,2
		self.s = []
		self.p = []
		for i in range(self.wvls.length):
			self.s.append([0.0+0.0j, 0.0+0.0j, 0.0+0.0j, 0.0+0.0j])
			self.p.append([0.0+0.0j, 0.0+0.0j, 0.0+0.0j, 0.0+0.0j])
	
	
	######################################################################
	#                                                                    #
	# set_matrices_unity                                                 #
	#                                                                    #
	######################################################################
	def set_matrices_unity(self):
		"""Set the caracteristic matrices to unity matrices"""
		
		for i in range(self.wvls.length):
			self.s[i][0] = 1.0+0.0j
			self.s[i][1] = 0.0+0.0j
			self.s[i][2] = 0.0+0.0j
			self.s[i][3] = 1.0+0.0j
			self.p[i][0] = 1.0+0.0j
			self.p[i][1] = 0.0+0.0j
			self.p[i][2] = 0.0+0.0j
			self.p[i][3] = 1.0+0.0j
		
		
	######################################################################
	#                                                                    #
	# copy_matrices                                                      #
	#                                                                    #
	######################################################################
	def copy_matrices(self, M):
		"""Copy the characteristic matrices
		
		This method takes 1 argument:
		  M                the original matrices;
		and copies them to the instance used to call the method."""
		
		for i in range(self.wvls.length):
			self.s[i][0] = M.s[i][0]
			self.s[i][1] = M.s[i][1]
			self.s[i][2] = M.s[i][2]
			self.s[i][3] = M.s[i][3]
	
			self.p[i][0] = M.p[i][0]
			self.p[i][1] = M.p[i][1]
			self.p[i][2] = M.p[i][2]
			self.p[i][3] = M.p[i][3]
	
	
	######################################################################
	#                                                                    #
	# set_matrices                                                       #
	#                                                                    #
	######################################################################
	def set_matrices(self, N, thickness, sin2_theta_0):
		"""Set the caracteristic matrices of a layer
		
		This method takes 3 arguments:
		  N                 the index of refraction of the layer;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			k = two_pi/self.wvls.wvls[i]
			
			N_square = N.N[i]*N.N[i]
			N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i])
			N_p = N_square/N_s
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
				N_p = -N_p
			
			phi = k*N_s*thickness
			
			if phi.imag < -100.0:
				phi = phi.real + -100.0j;
			
			j_sin_phi = 1.0j*cmath.sin(phi)
			
			self.s[i][0] = self.s[i][3] = self.p[i][0] = self.p[i][3] = cmath.cos(phi)
			self.s[i][1] = j_sin_phi/N_s
			self.p[i][1] = j_sin_phi/N_p
			self.s[i][2] = N_s*j_sin_phi
			self.p[i][2] = N_p*j_sin_phi
	
	
	######################################################################
	#                                                                    #
	# multiply_matrices                                                  #
	#                                                                    #
	######################################################################
	def multiply_matrices(self, M):
		"""Multiply the caracteristic matrices
		
		This method takes 1 argument:
		  M                 a pointer to the a second set of matrices.
		
		This method multiply M by the matrices kept in the instance used
		to call the method and stores the result in that instance."""
		
		for i in range(self.wvls.length):
			temp0 = M.s[i][0]*self.s[i][0] + M.s[i][1]*self.s[i][2]
			temp1 = M.s[i][0]*self.s[i][1] + M.s[i][1]*self.s[i][3]
			temp2 = M.s[i][2]*self.s[i][0] + M.s[i][3]*self.s[i][2]
			self.s[i][3] = M.s[i][2]*self.s[i][1] + M.s[i][3]*self.s[i][3]
			self.s[i][0] = temp0
			self.s[i][1] = temp1
			self.s[i][2] = temp2
			
			temp0 = M.p[i][0]*self.p[i][0] + M.p[i][1]*self.p[i][2]
			temp1 = M.p[i][0]*self.p[i][1] + M.p[i][1]*self.p[i][3]
			temp2 = M.p[i][2]*self.p[i][0] + M.p[i][3]*self.p[i][2]
			self.p[i][3] = M.p[i][2]*self.p[i][1] + M.p[i][3]*self.p[i][3]
			self.p[i][0] = temp0
			self.p[i][1] = temp1
			self.p[i][2] = temp2
