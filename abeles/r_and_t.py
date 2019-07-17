# r_and_t.py
# 
# A class to calculate the reflexion and transmission in amplitude
# and intensity, with or without the backside.
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



########################################################################
#                                                                      #
# r_and_t                                                              #
#                                                                      #
########################################################################
class r_and_t(object):
	"""A class to calculate the reflexion and transmission in amplitude
	and intensity, with or without the backside."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the r_and_t class to store the
		amplitude reflection and transmission coefficient of a stack for s
		and p polarization
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    coefficients."""
	
		self.wvls = wvls
		
		self.r_s = [0.0+0.0j]*self.wvls.length
		self.t_s = [0.0+0.0j]*self.wvls.length
		self.r_p = [0.0+0.0j]*self.wvls.length
		self.t_p = [0.0+0.0j]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# calculate_r_and_t                                                  #
	#                                                                    #
	######################################################################
	def calculate_r_and_t(self, M, N_m, N_s, sin2_theta_0):
		"""Calculate amplitude reflection and transmission
		
		This method takes 4 arguments:
		  M                 the characteristics matrices describing the
		                    stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			N_square = N_m.N[i]*N_m.N[i]
			N_m_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			N_m_p = N_square/N_m_s
			N_square = N_s.N[i]*N_s.N[i]
			N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			N_s_p = N_square/N_s_s
			
			# Correct branch selection.
			if N_m_s.real == 0.0:
				N_m_s = -N_m_s
				N_m_p = -N_m_p
			if N_s_s.real == 0.0:
				N_s_s = -N_s_s
				N_s_p = -N_s_p
			
			denominator = N_m_s*M.s[i][0] + N_s_s*M.s[i][3] + N_s_s*N_m_s*M.s[i][1] + M.s[i][2]
			self.r_s[i] = (N_m_s*M.s[i][0] - N_s_s*M.s[i][3] + N_s_s*N_m_s*M.s[i][1] - M.s[i][2]) / denominator
			self.t_s[i] = 2.0*N_m_s/denominator
	
			denominator = N_m_p*M.p[i][0] + N_s_p*M.p[i][3] + N_s_p*N_m_p*M.p[i][1] + M.p[i][2]
			self.r_p[i] = (N_m_p*M.p[i][0] - N_s_p*M.p[i][3] + N_s_p*N_m_p*M.p[i][1] - M.p[i][2]) / denominator
			self.t_p[i] = 2.0*N_m_p/denominator
	
	
	######################################################################
	#                                                                    #
	# calculate_r_and_t_reverse                                          #
	#                                                                    #
	######################################################################
	def calculate_r_and_t_reverse(self, M, N_m, N_s, sin2_theta_0):
		"""Calculate amplitude reflection and transmission in reverse
		direction
		
		This method takes 4 arguments:
		  M                 the characteristics matrices describing the
		                    stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		# When calculating in reverse direction we inverse N_m and N_s and
		# use the fact that Abeles matrices are persymmetric; therefore if
		# M1*M2*M3*... = A
		# then ...*M3*M2*M1 can be obtained by rotating A about the
		# diagonal going from the upper-right corner to the lower left
		# corner.
		
		for i in range(self.wvls.length):
			N_square = N_m.N[i]*N_m.N[i]
			N_m_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			N_m_p = N_square/N_m_s
			N_square = N_s.N[i]*N_s.N[i]
			N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			N_s_p = N_square/N_s_s
			
			# Correct branch selection.
			if N_m_s.real == 0.0:
				N_m_s = -N_m_s
				N_m_p = -N_m_p
			if N_s_s.real == 0.0:
				N_s_s = -N_s_s
				N_s_p = -N_s_p
			
			denominator = N_s_s*M.s[i][3] + N_m_s*M.s[i][0] + N_m_s*N_s_s*M.s[i][1] + M.s[i][2]
			self.r_s[i] = (N_s_s*M.s[i][3] - N_m_s*M.s[i][0] + N_m_s*N_s_s*M.s[i][1] - M.s[i][2]) / denominator
			self.t_s[i] = 2.0*N_s_s/denominator
	
			denominator = N_s_p*M.p[i][3] + N_m_p*M.p[i][0] + N_m_p*N_s_p*M.p[i][1] + M.p[i][2]
			self.r_p[i] = (N_s_p*M.p[i][3] - N_m_p*M.p[i][0] + N_m_p*N_s_p*M.p[i][1] - M.p[i][2]) / denominator
			self.t_p[i] = 2.0*N_s_p/denominator
