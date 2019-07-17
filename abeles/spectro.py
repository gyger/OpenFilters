# spectro.py
# 
# Classes to calculate the reflectance, transmittance and
# absorptance, with or without the backside.
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



import math
import cmath

from definitions import *



two_pi = 2.0*math.pi



########################################################################
#                                                                      #
# spectrum                                                             #
#                                                                      #
########################################################################
class spectrum(object):
	"""An abstract class for various kinds of spectra"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the spectrum class to store a spectrum
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    spectrum."""
		
		self.wvls = wvls
		self.data = [0.0]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the spectrum is
		calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the spectrum is calculated."""
		
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the spectrum
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
		
		return self.data[key]



########################################################################
#                                                                      #
# R                                                                    #
#                                                                      #
########################################################################
class R(spectrum):
	"""An class to calculate reflectance"""
	
	
	######################################################################
	#                                                                    #
	# calculate_R                                                        #
	#                                                                    #
	######################################################################
	def calculate_R(self, r_and_t, polarization):
		"""Calculate reflectance from amplitude reflection
		
		This method takes 2 arguments:
		  r_and_t           the amplitude reflection and transmission of
		                    the stack;
		  polarization      the polarization of light."""
		
		if polarization == S:
			for i in range(self.wvls.length):
				self.data[i] = (r_and_t.r_s[i]*r_and_t.r_s[i].conjugate()).real
		elif polarization == P:
			for i in range(self.wvls.length):
				self.data[i] = (r_and_t.r_p[i]*r_and_t.r_p[i].conjugate()).real
		else:
			Psi = polarization*math.pi/180.0;
			sin_Psi = math.sin(Psi);
			sin_Psi_square = sin_Psi*sin_Psi;
			cos_Psi_square = 1.0-sin_Psi_square;
			for i in range(self.wvls.length):
				self.data[i] = (r_and_t.r_s[i]*r_and_t.r_s[i].conjugate()).real * sin_Psi_square\
				             + (r_and_t.r_p[i]*r_and_t.r_p[i].conjugate()).real * cos_Psi_square
	
	
	######################################################################
	#                                                                    #
	# calculate_R_with_backside                                          #
	#                                                                    #
	######################################################################
	def calculate_R_with_backside(self, T_front, R_front, T_front_reverse, R_front_reverse, R_back, N_s, thickness, sin2_theta_0):
		"""Calculate reflectance with consideration of the backside
		
		This method takes 8 arguments:
		  T_front           the transmittance of the front side;
		  R_front           the reflectance of the front side;
		  T_front_reverse   the transmittance of the front side in reverse
		                    direction;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  R_back            the reflectance of the back side;
		  N_s               the index of refraction of the substrate;
		  thickness         the thickness of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			N_square = N_s.N[i]*N_s.N[i]
			N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			
			# Correct branch selection.
			if N_s_s.real == 0.0:
				N_s_s = -N_s_s
			
			beta_imag = (two_pi*thickness*N_s_s/self.wvls.wvls[i]).imag
			exp_4_beta_imag = math.exp(4.0*beta_imag)
			
			self.data[i] = R_front.data[i] + ((T_front.data[i]*T_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag)/(1.0-R_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag))



########################################################################
#                                                                      #
# T                                                                    #
#                                                                      #
########################################################################
class T(spectrum):
	"""An class to calculate transmittance"""
	
	
	######################################################################
	#                                                                    #
	# calculate_T                                                        #
	#                                                                    #
	######################################################################
	def calculate_T(self, r_and_t, N_i, N_e, sin2_theta_0, polarization):
		"""Calculate transmittance from amplitude transmission
		
		This method takes 5 arguments:
		  r_and_t           the amplitude reflection and transmission of
		                    the stack;
		  N_i               the index of refraction of the incidence
		                    medium;
		  N_e               the index of refraction of the exit medium;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
		
		if polarization == S:
			for i in range(self.wvls.length):
				N_square = N_i.N[i]*N_i.N[i]
				N_i_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_e.N[i]*N_e.N[i]
				N_e_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				self.data[i] = (N_e_s.real/N_i_s.real) * (r_and_t.t_s[i]*r_and_t.t_s[i].conjugate()).real
		
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_i.N[i]*N_i.N[i]
				N_i_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_e.N[i]*N_e.N[i]
				N_e_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				self.data[i] = (N_e_p.real/N_i_p.real) * (r_and_t.t_p[i]*r_and_t.t_p[i].conjugate()).real
		
		else:
			Psi = polarization*math.pi/180.0;
			sin_Psi = math.sin(Psi);
			sin_Psi_square = sin_Psi*sin_Psi;
			cos_Psi_square = 1.0-sin_Psi_square;
			for i in range(self.wvls.length):
				N_square = N_i.N[i]*N_i.N[i]
				N_i_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_i_p = N_square/N_i_s
				N_square = N_e.N[i]*N_e.N[i]
				N_e_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_e_p = N_square/N_e_s
				
				self.data[i] = ((N_e_s.real/N_i_s.real) * (r_and_t.t_s[i]*r_and_t.t_s[i].conjugate()).real) * sin_Psi_square\
				             + ((N_e_p.real/N_i_p.real) * (r_and_t.t_p[i]*r_and_t.t_p[i].conjugate()).real) * cos_Psi_square
	
	
	######################################################################
	#                                                                    #
	# calculate_T_with_backside                                          #
	#                                                                    #
	######################################################################
	def calculate_T_with_backside(self, T_front, R_front_reverse, T_back, R_back, N_s, thickness, sin2_theta_0):
		"""Calculate transmittance with consideration of the backside
		
		This method takes 7 arguments:
		  T_front           the transmittance of the front side;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  T_back            the transmittance of the back side;
		  R_back            the reflectance of the back side;
		  N_s               the index of refraction of the substrate;
		  thickness         the thickness of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			N_square = N_s.N[i]*N_s.N[i]
			N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			
			# Correct branch selection.
			if N_s_s.real == 0.0:
				N_s_s = -N_s_s
			
			beta_imag = (two_pi*thickness*N_s_s/self.wvls.wvls[i]).imag
			
			self.data[i] = (T_front.data[i]*T_back.data[i]*math.exp(2.0*beta_imag))/(1.0-R_back.data[i]*R_front_reverse.data[i]*math.exp(4.0*beta_imag));



########################################################################
#                                                                      #
# A                                                                    #
#                                                                      #
########################################################################
class A(spectrum):
	"""A class to calculate absorptance"""
	
	
	######################################################################
	#                                                                    #
	# calculate_A                                                        #
	#                                                                    #
	######################################################################
	def calculate_A(self, R, T):
		"""Calculate absorptance from the reflectance and the transmittance
		
		This method takes 2 arguments:
		  R                 the reflectance of the filter;
		  T                 the transmittance of the filter."""
		
		for i in range(self.wvls.length):
			self.data[i] = 1.0 - R.data[i] - T.data[i]
