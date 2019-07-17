# admittance.py
# 
# A class to calculate the admittance of the coating from abeles
# matrices.
# 
# Copyright (c) 2000-2008,2012 Stephane Larouche.
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



########################################################################
#                                                                      #
# admittance                                                           #
#                                                                      #
########################################################################
class admittance(object):
	"""A class to calculate the admittance of the coating from abeles
	matrices"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the admittance class
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    admittance."""
		
		self.wvls = wvls
		
		self.data = [0.0]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# calculate_admittance                                               #
	#                                                                    #
	######################################################################
	def calculate_admittance(self, M, N_s, sin2_theta_0, polarization):
		"""Calculate the admittance of a stack from its characteristic
		matrix
		
		This method takes 4 arguments:
		  M                 the characteristics matrices describing the
		                    stack;
		  N_s               the index of the substrate;
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
				C = M.s[i][2] + M.s[i][3]*N_s_s
				self.data[i] = C/B
		
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_s.N[i]*N_s.N[i]
				N_s_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_s_p.real == 0.0:
					N_s_p = -N_s_p
				
				B = M.p[i][0] + M.p[i][1]*N_s_p
				C = M.p[i][2] + M.p[i][3]*N_s_p
				self.data[i] = C/B
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the admittance is
		calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the admittance is calculated."""
	
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the admittance
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
	
		return self.data[key]
