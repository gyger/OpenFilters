# phase.py
#
# A class to calculate the phase of the reflected or transmitted
# light from Abeles matrices.
#
# Copyright (c) 2005-2008,2012,2016 Stephane Larouche.
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
from spectro import spectrum

from moremath.Newton_polynomials import Newton_quadratic



two_pi = 2.0*math.pi

# The speed of light in nm/s.
c = 299792458.0 * 1e9
two_pi_c = two_pi*c



########################################################################
#                                                                      #
# phase                                                                #
#                                                                      #
########################################################################
class phase(spectrum):
	"""A class to calculate the phase of the reflected or transmitted
	light from Abeles matrices"""
	
	
	######################################################################
	#                                                                    #
	# calculate_r_phase                                                  #
	#                                                                    #
	######################################################################
	def calculate_r_phase(self, M, N_m, N_s, sin2_theta_0, polarization):
		"""Calculate the phase shift upon reflection
		
		This method takes 5 arguments:
		  M                 the characteristic matrices of the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
			
		# atan2 fails if both arguments are 0, consider the phase to be 0,
		# this is usually acceptable.
		
		if polarization == S:
			for i in range(self.wvls.length):
				N_square = N_m.N[i]*N_m.N[i]
				N_m_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_s.N[i]*N_s.N[i]
				N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_m_s.real == 0.0:
					N_m_s = -N_m_s
				if N_s_s.real == 0.0:
					N_s_s = -N_s_s
				
				# Admittance of s polarisation.
				B = M.s[i][0] + M.s[i][1]*N_s_s
				C = M.s[i][2] + M.s[i][3]*N_s_s
				B_conj = B.conjugate()
				C_conj = C.conjugate()
				
				# s reflection phase.
				numerator = (N_m_s*(B*C_conj-C*B_conj)).imag
				denominator = (N_m_s*N_m_s*B*B_conj-C*C_conj).real
				if numerator == 0.0 and denominator == 0.0:
					self.data[i] = 0.0
				else:
					self.data[i] = math.atan2(numerator, denominator)
		
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_m.N[i]*N_m.N[i]
				N_m_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_s.N[i]*N_s.N[i]
				N_s_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_m_p.real == 0.0:
					N_m_p = -N_m_p
				if N_s_p.real == 0.0:
					N_s_p = -N_s_p
				
				# Admittance of p polarisation.
				B = M.p[i][0] + M.p[i][1]*N_s_p
				C = M.p[i][2] + M.p[i][3]*N_s_p
				B_conj = B.conjugate()
				C_conj = C.conjugate()
				
				# p reflection phase.
				numerator = (N_m_p*(B*C_conj-C*B_conj)).imag
				denominator = (N_m_p*N_m_p*B*B_conj-C*C_conj).real
				if numerator == 0.0 and denominator == 0.0:
					self.data[i] = 0.0
				else:
					self.data[i] = math.atan2(numerator, denominator)
		
		# Put the range between 0 and 2 pi. 
		for i in range(self.wvls.length):		
			if self.data[i] < 0.0:
				self.data[i] += two_pi
	
	
	######################################################################
	#                                                                    #
	# calculate_t_phase                                                  #
	#                                                                    #
	######################################################################
	def calculate_t_phase(self, M, N_m, N_s, sin2_theta_0, polarization):
		"""Calculate the phase shift upon transmission
		
		This method takes 5 arguments:
		  M                 the characteristic matrices of the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
		
		# atan2 fails if both arguments are 0, consider the phase to be 0,
		# this is usually acceptable.
		
		if polarization == S:
			for i in range(self.wvls.length):
				N_square = N_m.N[i]*N_m.N[i]
				N_m_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_s.N[i]*N_s.N[i]
				N_s_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_m_s.real == 0.0:
					N_m_s = -N_m_s
				if N_s_s.real == 0.0:
					N_s_s = -N_s_s
				
				# Admittance of s polarisation.
				B = M.s[i][0] + M.s[i][1]*N_s_s
				C = M.s[i][2] + M.s[i][3]*N_s_s
				
				# s transmission phase.
				temp = N_m_s*B+C
				numerator = -temp.imag
				denominator = temp.real
				if numerator == 0.0 and denominator == 0.0:
					self.data[i] = 0.0
				else:
					self.data[i] = math.atan2(numerator, denominator)
		
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_m.N[i]*N_m.N[i]
				N_m_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_s.N[i]*N_s.N[i]
				N_s_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				# Correct branch selection.
				if N_m_p.real == 0.0:
					N_m_p = -N_m_p
				if N_s_p.real == 0.0:
					N_s_p = -N_s_p
				
				# Admittance of p polarisation.
				B = M.p[i][0] + M.p[i][1]*N_s_p
				C = M.p[i][2] + M.p[i][3]*N_s_p
				
				# p transmission phase.
				temp = N_m_p*B+C
				numerator = -temp.imag
				denominator = temp.real
				if numerator == 0.0 and denominator == 0.0:
					self.data[i] = 0.0
				else:
					self.data[i] = math.atan2(numerator, denominator)
		
		# Put the range between 0 and 2 pi. 
		for i in range(self.wvls.length):		
			if self.data[i] < 0.0:
				self.data[i] += two_pi



########################################################################
#                                                                      #
# GD                                                                   #
#                                                                      #
########################################################################
class GD(spectrum):
	"""A class to calculate the group delay"""
	
	
	######################################################################
	#                                                                    #
	# calculate_GD                                                       #
	#                                                                    #
	######################################################################
	def calculate_GD(self, phase):
		"""Calculate the group delay
		
		This method takes 1 argument:
		  phase             the phase shift of the filter.
		
		The group delay is determined from the numerical first derivative
		of the phase shift with regard to angular frequency."""
		
		y = [0.0]*3;
		
		# Calculate the angular frequency.
		omega = [two_pi_c / self.wvls.wvls[i] for i in range(self.wvls.length)]
		
		# Since we cannot identify the absolute value of the phase but only
		# its residue when divided by 2 pi, we choose the difference that
		# gives the smallest GD. This is reasonable since the phase should
		# not change too rapidly with the wavelength. If errors occurs, the
		# user should increase the number of points.
		
		# To calculate the GD for the first point, we fit a polynomial on
		# the first three points giving a results similar to forward
		# difference.
		y[0] = phase.data[0]
		y[1] = phase.data[1]
		y[2] = phase.data[2]
		if type(self) == GD:
			if y[1]-y[0] > math.pi: y[1] -= two_pi
			elif y[1]-y[0] < -math.pi: y[1] += two_pi
			if y[2]-y[1] > math.pi: y[2] -= two_pi
			elif y[2]-y[1] < -math.pi: y[2] += two_pi
		a0, a1, a2 = Newton_quadratic(omega, y)
		self.data[0] = -(a1 + 2.0*a2*omega[0])
		
		# To calculate the GD for the second point, we reuse the same
		# polynomial now giving a formula similar to centered difference.
		self.data[1] = -(a1 + 2.0*a2*omega[1])
		
		# To calculate the GD for the third to second to last points, we use
		# polynomials centered on these points.
		for i in range(2, self.wvls.length-1):
			y[0] = phase.data[i-1]
			y[1] = phase.data[i]
			y[2] = phase.data[i+1]
			if type(self) == GD:
				if y[1]-y[0] > math.pi: y[1] -= two_pi
				elif y[1]-y[0] < -math.pi: y[1] += two_pi
				if y[2]-y[1] > math.pi: y[2] -= two_pi
				elif y[2]-y[1] < -math.pi: y[2] += two_pi
			a0, a1, a2 = Newton_quadratic(omega[i-1:i+2], y)
			self.data[i] = -(a1 + 2.0*a2*omega[i])
		
		# To calculate the GD for the last point, we reuse the polynomial
		# used for the second to last point, now giving a formula similar
		# to backward difference.
		self.data[-1] = -(a1 + 2.0*a2*omega[-1])



########################################################################
#                                                                      #
# GDD                                                                  #
#                                                                      #
########################################################################
class GDD(spectrum):
	"""A class to calculate the group delay dispersion"""
	
	
	######################################################################
	#                                                                    #
	# calculate_GDD                                                      #
	#                                                                    #
	######################################################################
	def calculate_GDD(self, phase):
		"""Calculate the group delay dispersion
		
		This method takes 1 argument:
		  phase             a pointer to the phase shift of the filter.
		
		The group delay dispersion is determined from the numerical
		second derivative of the phase shift with regard to angular
		frequency."""
		
		y = [0.0]*3;
		
		# Calculate the angular frequency.
		omega = [two_pi_c / self.wvls.wvls[i] for i in range(self.wvls.length)]
		
		# Since we cannot identify the absolute value of the phase but only
		# its residue when divided by 2 pi, we choose the difference that
		# gives the smallest GDD. This is reasonable since the phase should
		# not change too rapidly with the wavelength. If errors occurs, the
		# user should increase the number of points.
		
		# To calculate the GDD for the first point, we fit a polynomial on
		# the first three points giving a results similar to forward
		# difference.
		y[0] = phase.data[0]
		y[1] = phase.data[1]
		y[2] = phase.data[2]
		if type(self) == GDD:
			if y[1]-y[0] > math.pi: y[1] -= two_pi
			elif y[1]-y[0] < -math.pi: y[1] += two_pi
			if y[2]-y[1] > math.pi: y[2] -= two_pi
			elif y[2]-y[1] < -math.pi: y[2] += two_pi
		a0, a1, a2 = Newton_quadratic(omega, y)
		self.data[0] = -2.0*a2
		
		# To calculate the GDD for the second point, we reuse the same
		# polynomial now giving a formula similar to centered difference.
		self.data[1] = -2.0*a2
		
		# To calculate the GDD for the third to second to last points, we use
		# polynomials centered on these points.
		for i in range(2, self.wvls.length-1):
			y[0] = phase.data[i-1]
			y[1] = phase.data[i]
			y[2] = phase.data[i+1]
			if type(self) == GDD:
				if y[1]-y[0] > math.pi: y[1] -= two_pi
				elif y[1]-y[0] < -math.pi: y[1] += two_pi
				if y[2]-y[1] > math.pi: y[2] -= two_pi
				elif y[2]-y[1] < -math.pi: y[2] += two_pi
			a0, a1, a2 = Newton_quadratic(omega[i-1:i+2], y)
			self.data[i] = -2.0*a2
		
		# To calculate the GDD for the last point, we reuse the polynomial
		# used for the second to last point, now giving a formula similar
		# to backward difference.
		self.data[-1] = -2.0*a2
