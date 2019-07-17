# ellipso.py
# 
# A class to calculate ellipsometric variables Psi and Delta from
# reflexion and transmission values.
# 
# Copyright (c) 2000-2004,2006-2008,2012 Stephane Larouche.
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
one_hundred_eighty_over_pi = 180.0/math.pi



########################################################################
#                                                                      #
# Psi_and_Delta                                                        #
#                                                                      #
########################################################################
class Psi_and_Delta(object):
	"""A class to calculate ellipsometric variables Psi and Delta from
	reflexion and transmission values"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the Psi_and_Delta class
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    ellipsometric variables."""
		
		self.wvls = wvls
		
		self.Psi = [0.0]*self.wvls.length
		self.Delta = [0.0]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# calculate_Psi_and_Delta                                            #
	#                                                                    #
	######################################################################
	def calculate_Psi_and_Delta(self, r_and_t):
		"""Calculate the ellipsometric variables of a filter
		
		This method takes 1 argument:
		  r_and_t           the amplitude reflection and transmission of
		                    the filter.
		
		In the ellipsometry convention, the sign of r_p has to be
		changed. This is inconsistant since it provokes a difference
		between r_p and r_s at normal incidence, but it is usually
		prefered in ellipsometry because adopting the "natural"
		convention would need to have rotating elements before and after
		the sample turning in opposite directions. See Rolf H. Muller,
		"Definitions and conventions in ellipsometry", Surface Science,
		V. 16, 14-33 (1969) for details on ellipsometric conventions."""
		
		for i in range(self.wvls.length):
			
			# atan2 fails if both arguments are 0, consider Psi to be 45
			# degres and Delta to be 180 degres, that is usually acceptable.
			if r_and_t.r_s[i] == 0.0 and r_and_t.r_p[i] == 0.0:
				self.Psi[i] = 45.0
				self.Delta[i] = 180.0
			
			else:
				abs_r_p = abs(r_and_t.r_p[i])
				abs_r_s = abs(r_and_t.r_s[i])
				
				self.Psi[i] = math.atan2(abs_r_p, abs_r_s)*one_hundred_eighty_over_pi
				
				arg_r_p = math.atan2(-r_and_t.r_p[i].imag, -r_and_t.r_p[i].real)
				arg_r_s = math.atan2(r_and_t.r_s[i].imag, r_and_t.r_s[i].real)
				
				self.Delta[i] = (arg_r_p-arg_r_s)*one_hundred_eighty_over_pi
	
	
	######################################################################
	#                                                                    #
	# calculate_Psi_and_Delta_with_backside                              #
	#                                                                    #
	######################################################################
	def calculate_Psi_and_Delta_with_backside(self, r_and_t_front, r_and_t_front_reverse, r_and_t_back, N_s, thickness, sin2_theta_0):
		"""Calculate the ellipsometric variables of a filter with
		consideration of the backside
		
		This method takes 6 arguments:
		  r_and_t_front         the amplitude reflection of the front
		                        side;
		  r_and_t_front_reverse the amplitude reflection of the front
		                        side in reverse direction;
		  r_and_t_back          the amplitude reflection of the back
		                        side;
		  N_s                   the index of refraction of the substrate;
		  thickness             the thickness of the substrate;
		  sin2_theta_0          the normalized sinus squared of the
		                        propagation angle.
		
		To consider the backside, we have to consider the incoherent
		reflexion on the back of the substrate. We adopt the approach
		proposed in Y. H. Yang et al. "Spectroscopic ellipsometry of thin
		films on transparent substrates: A formalism for data
		interpretation", J. Vac. Sc. Technol., V. 13, No 3, 1995,
		pp. 1145-1149."""
		
		for i in range(self.wvls.length):
			N_s_square = N_s.N[i]*N_s.N[i]
			N_s_s = cmath.sqrt(N_s_square-sin2_theta_0.sin2[i])
			
			# Correct branch selection.
			if N_s_s.real == 0.0:
				N_s_s = -N_s_s
			
			exp_minus_4_abs_beta_imag = math.exp(-4.0*(abs((two_pi*thickness*N_s_s/self.wvls.wvls[i]).imag)));
			
			norm_r_p_front = (r_and_t_front.r_p[i]*r_and_t_front.r_p[i].conjugate()).real
			norm_t_p_front = (r_and_t_front.t_p[i]*r_and_t_front.t_p[i].conjugate()).real
			norm_r_p_reverse = (r_and_t_front_reverse.r_p[i]*r_and_t_front_reverse.r_p[i].conjugate()).real
			norm_t_p_reverse = (r_and_t_front_reverse.t_p[i]*r_and_t_front_reverse.t_p[i].conjugate()).real
			norm_r_p_back = (r_and_t_back.r_p[i]*r_and_t_back.r_p[i].conjugate()).real
			
			norm_r_s_front = (r_and_t_front.r_s[i]*r_and_t_front.r_s[i].conjugate()).real
			norm_t_s_front = (r_and_t_front.t_s[i]*r_and_t_front.t_s[i].conjugate()).real
			norm_r_s_reverse = (r_and_t_front_reverse.r_s[i]*r_and_t_front_reverse.r_s[i].conjugate()).real
			norm_t_s_reverse = (r_and_t_front_reverse.t_s[i]*r_and_t_front_reverse.t_s[i].conjugate()).real
			norm_r_s_back = (r_and_t_back.r_s[i]*r_and_t_back.r_s[i].conjugate()).real
			
			norm_r_mixed_front = -r_and_t_front.r_p[i]*r_and_t_front.r_s[i].conjugate()
			norm_t_mixed_front = r_and_t_front.t_p[i]*r_and_t_front.t_s[i].conjugate()
			norm_r_mixed_reverse = -r_and_t_front_reverse.r_p[i]*r_and_t_front_reverse.r_s[i].conjugate()
			norm_t_mixed_reverse = r_and_t_front_reverse.t_p[i]*r_and_t_front_reverse.t_s[i].conjugate()
			norm_r_mixed_back = -r_and_t_back.r_p[i]*r_and_t_back.r_s[i].conjugate()
			
			Ri_p = norm_t_p_front*norm_t_p_reverse*norm_r_p_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_p_reverse*norm_r_p_back*exp_minus_4_abs_beta_imag)
			Ri_s = norm_t_s_front*norm_t_s_reverse*norm_r_s_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_s_reverse*norm_r_s_back*exp_minus_4_abs_beta_imag)
			Bi_2 = (norm_t_mixed_front*norm_t_mixed_reverse*norm_r_mixed_back*exp_minus_4_abs_beta_imag / (1.0 - norm_r_mixed_reverse*norm_r_mixed_back*exp_minus_4_abs_beta_imag)).real
			
			sqrt_norm_r_p_front_plus_Ri_p = math.sqrt(norm_r_p_front + Ri_p);
			sqrt_norm_r_s_front_plus_Ri_s = math.sqrt(norm_r_s_front + Ri_s);
			
			# atan2 fails if both arguments are 0, consider Psi to be 45
			# degres, that is usually acceptable.
			if sqrt_norm_r_p_front_plus_Ri_p == 0.0 and sqrt_norm_r_s_front_plus_Ri_s == 0.0:
				self.Psi[i] = 45.0;
			else:
				self.Psi[i] = math.atan2(sqrt_norm_r_p_front_plus_Ri_p, sqrt_norm_r_s_front_plus_Ri_s) * one_hundred_eighty_over_pi
			
			# acos is only defined between -1 and 1. Numerical calculations,
			# with limited precision, can provoke a value a little bit
			# outside of this interval. The value to be given to acos
			# is verified to avoid a bug.
			cos_Delta = (norm_r_mixed_front.real + Bi_2) / math.sqrt((norm_r_p_front + Ri_p) * (norm_r_s_front + Ri_s))
			cos_Delta = min(max(cos_Delta, -1.0), 1.0)
			self.Delta[i] = math.acos(cos_Delta) * one_hundred_eighty_over_pi
	
	
	######################################################################
	#                                                                    #
	# get_Psi                                                            #
	#                                                                    #
	######################################################################
	def get_Psi(self):
		"""Get the Psi values
		
		This method returns the list of Psi values."""
		
		return self.Psi
	
	
	######################################################################
	#                                                                    #
	# get_Delta                                                          #
	#                                                                    #
	######################################################################
	def get_Delta(self):
		"""Get the Delta values
		
		This method returns the list of Delta values."""
		
		return self.Delta
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the ellipsometric
		variables are calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the ellipsometric variable are
		calculated."""
	
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the ellipsometric variables
		
		This method is called when instance[key] is used. It returns the
		items requested by the key. If a single item is requested it is
		returned as a tuple (Psi, Delta). When multiple items are
		requested, they are returned as a list of tuples."""
		
		if isinstance(key, int):
			return (self.Psi[key], self.Delta[key])
		else:
			return [(Psi, Delta) for Psi in self.Psi[key] for Delta in self.Delta[key]]
