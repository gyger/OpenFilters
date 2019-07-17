# electric_field.py
# 
# A class to calculate the electric field of the coating from
# abeles matrices.
# 
# Copyright (c) 2000-2007,2012 Stephane Larouche.
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



import cmath

from definitions import *
from spectro import spectrum



########################################################################
#                                                                      #
# electric_field                                                       #
#                                                                      #
########################################################################
class electric_field(spectrum):
	"""A class to calculate the electric field of the coating from
	abeles matrices"""
	
	
	######################################################################
	#                                                                    #
	# calculate_electric_field                                           #
	#                                                                    #
	######################################################################
	def calculate_electric_field(self, M, N_s, sin2_theta_0, polarization):
		"""Calculate the electric in stack from its characteristic matrix
		
		This method takes 4 arguments:
		  M                 the characteristics matrices describing the
		                    stack;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
				
		if polarization == S:
			for i in range(self.wvls.length):
				N_square = N_s.N[i]*N_s.N[i]
				N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_s_s.real == 0.0:
					N_s_s = -N_s_s
				
				B = M.s[i][0] + M.s[i][1]*N_s_s
				
				self.data[i] = abs(B)
		
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_s.N[i]*N_s.N[i]
				N_s_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_s_p.real == 0.0:
					N_s_p = -N_s_p
				
				B = M.p[i][0] + M.p[i][1]*N_s_p
				
				self.data[i] = abs(B)
