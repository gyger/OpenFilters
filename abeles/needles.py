# needles.py
# 
# A class to calculate the derivative of the Abeles matrices upon
# the addition of needles or steps.
# 
# Copyright (c) 2005-2009,2012 Stephane Larouche.
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

from matrices import *



two_pi = 2.0*math.pi



########################################################################
#                                                                      #
# needle_matrices                                                      #
#                                                                      #
########################################################################
class needle_matrices(object):
	"""A class to calculate the derivative of the Abeles matrices upon
	the addition of needles or steps"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls, length):
		"""Create an instance to store the derivatives of the characteristic
		matrices used in the needle method
		
		This method takes 2 arguments:
		  wvls              the wavelengths at which to calculate the
		                    needle matrices;
		  length            the number of positions.
		
		When using the needle method, one needs to calculate the
		derivative of the characteristic matrices of a layer as a
		of the position where the needle is added. The needle matrix
		instance allows to store all the derivatives of the
		characteristic matrices at multiple positions in a layer."""
	
		self.length = length
		
		self.wvls = wvls
		self.positions = [0.0]*self.length
		self.M = [matrices(wvls) for i in range(self.length)]
	
	
	######################################################################
	#                                                                    #
	# set_needle_position                                                #
	#                                                                    #
	######################################################################
	def set_needle_position(M, i_needle, position):
		"""Set the position of one needle in a needle matrix instance
		
		This method takes 2 arguments:
		  i_needle          the number of the needle;
		  position          its position (with regard to the buttom of
		                    the layer)."""
		
		M.positions[i_needle] = position
	
	
	######################################################################
	#                                                                    #
	# set_needle_positions                                               #
	#                                                                    #
	######################################################################
	def set_needle_positions(M, spacing):
		"""Set the positions of all needles in a needle matrix instance
		
		This method takes 1 argument:
		  spacing           the spacing between needles.
		
		The first needle is located at 0 and the needles are equally
		seperated of spacing."""
		
		for i_needle in range(M.length):
			M.positions[i_needle] = i_needle*spacing
	
	
	######################################################################
	#                                                                    #
	# get_needle_position                                                #
	#                                                                    #
	######################################################################
	def get_needle_position(M, i_needle):
		"""Get the position of one needle in a needle matrix instance
		
		This method takes 1 argument:
		  i_needle          the number of the needle.
		and returns the position of the needle."""
	
		return M.positions[i_needle]
	
	
	######################################################################
	#                                                                    #
	# calculate_dMi_needles                                              #
	#                                                                    #
	######################################################################
	def calculate_dMi_needles(self, N, N_n, thickness, sin2_theta_0):
		"""Calculate the derivative of the characteristic matrix with regard
		to the addition of a needle as a function of its position
		
		This method takes 4 arguments:
		  N                 the index of refraction of the layer;
		  N_n               the index of refraction of the needle;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle.
		
		This method calculates the derivative of the characteristic
		matrix at the positions already set in the needle matrix
		instance."""
	
		# For details and demonstration, see:
		#   Stephane Larouche, Derivatives of the optical properties of
		#   interference filters, 2005.
		
		# This function calculates dMi for needles for multiple materials at
		# once to accelerate calculations.
		
		# Create objects for dM_phi and dM_delta_phi.
		dM_phi_s = [0.0+0.0j]*4
		dM_phi_p = [0.0+0.0j]*4
		dM_delta_phi_s = [0.0+0.0j]*4
		dM_delta_phi_p = [0.0+0.0j]*4
		
		for i_wvl in range(self.wvls.length):
			k = two_pi/self.wvls.wvls[i_wvl]
	
			N_square = N.N[i_wvl]*N.N[i_wvl]
			N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i_wvl])
			N_p = N_square/N_s
			
			N_n_square = N_n.N[i_wvl]*N_n.N[i_wvl]
			N_n_s = cmath.sqrt(N_n_square-sin2_theta_0.sin2[i_wvl])
			N_n_p = N_n_square/N_n_s
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
				N_p = -N_p
			if N_n_s.real == 0.0:
				N_n_s = -N_n_s
				N_n_p = -N_n_p
			
			phi = k*N_s*thickness
			j_cos_phi = 1.0j*cmath.cos(phi)
			
			d_phi = k*N_n_s
			
			sum_ratio_s  = 0.5 * (N_s/N_n_s + N_n_s/N_s)
			diff_ratio_s = 0.5 * (N_s/N_n_s - N_n_s/N_s)
			sum_ratio_p  = 0.5 * (N_p/N_n_p + N_n_p/N_p)
			diff_ratio_p = 0.5 * (N_p/N_n_p - N_n_p/N_p)
			
			# Calculate the constant part of dMi.
			dM_phi_s[0] = dM_phi_s[3] = dM_phi_p[0] = dM_phi_p[3] = -cmath.sin(phi)
			dM_phi_s[1] = j_cos_phi/N_s
			dM_phi_p[1] = j_cos_phi/N_p
			dM_phi_s[2] = N_s*j_cos_phi
			dM_phi_p[2] = N_p*j_cos_phi
			
			for i_pos in range(self.length):
				delta_phi = k*N_s*(2.0*self.positions[i_pos] - thickness)
				j_cos_delta_phi = 1.0j*cmath.cos(delta_phi)
				
				# Calculate the variable part of dMi.
				dM_delta_phi_s[0] = dM_delta_phi_s[3] = dM_delta_phi_p[0] = dM_delta_phi_p[3] = -cmath.sin(delta_phi)
				dM_delta_phi_s[1] = j_cos_delta_phi/N_s
				dM_delta_phi_p[1] = j_cos_delta_phi/N_p
				dM_delta_phi_s[2] = N_s*j_cos_delta_phi
				dM_delta_phi_p[2] = N_p*j_cos_delta_phi
				
				# Calculate dMi for the constant and variable parts.
				self.M[i_pos].s[i_wvl][0] = (sum_ratio_s*dM_phi_s[0] + diff_ratio_s*dM_delta_phi_s[0]) * d_phi
				self.M[i_pos].s[i_wvl][1] = (sum_ratio_s*dM_phi_s[1] + diff_ratio_s*dM_delta_phi_s[1]) * d_phi
				self.M[i_pos].s[i_wvl][2] = (sum_ratio_s*dM_phi_s[2] - diff_ratio_s*dM_delta_phi_s[2]) * d_phi
				self.M[i_pos].s[i_wvl][3] = (sum_ratio_s*dM_phi_s[3] - diff_ratio_s*dM_delta_phi_s[3]) * d_phi
				self.M[i_pos].p[i_wvl][0] = (sum_ratio_p*dM_phi_p[0] + diff_ratio_p*dM_delta_phi_p[0]) * d_phi
				self.M[i_pos].p[i_wvl][1] = (sum_ratio_p*dM_phi_p[1] + diff_ratio_p*dM_delta_phi_p[1]) * d_phi
				self.M[i_pos].p[i_wvl][2] = (sum_ratio_p*dM_phi_p[2] - diff_ratio_p*dM_delta_phi_p[2]) * d_phi
				self.M[i_pos].p[i_wvl][3] = (sum_ratio_p*dM_phi_p[3] - diff_ratio_p*dM_delta_phi_p[3]) * d_phi
	
	
	######################################################################
	#                                                                    #
	# calculate_dMi_steps                                                #
	#                                                                    #
	######################################################################
	def calculate_dMi_steps(self, N, dN, thickness, sin2_theta_0):
		"""Calculate the derivative of the characteristic matrix with regard
		to the addition of a step as a function of its position
		
		This method takes 4 arguments:
		  N                 the index of refraction of the layer;
		  dN                the derivative of the index of refraction of
		                    the layer;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle.
		
		This function calculates the derivative of the characteristic
		matrix at the position already set in the needle matrix
		instance."""
		
		# Create objects for dM_phi and M_delta_phi.
		dM_phi_s = [0.0+0.0j]*4
		dM_phi_p = [0.0+0.0j]*4
		M_delta_phi_s = [0.0+0.0j]*4
		M_delta_phi_p = [0.0+0.0j]*4
		
		# For details and demonstration, see:
		#   Stephane Larouche, Derivatives of the optical properties of
		#   interference filters, 2006.
		
		for i_wvl in range(self.wvls.length):
			k = two_pi/self.wvls.wvls[i_wvl]
	
			N_square = N.N[i_wvl]*N.N[i_wvl]
			N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i_wvl])
			N_p = N_square/N_s
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
				N_p = -N_p
			
			d_N_s = N.N[i_wvl]/N_s
			d_N_p = d_N_s * (2.0 - d_N_s*d_N_s)
			inverse_N_s = 1.0/N_s
			inverse_N_p = 1.0/N_p
			phi = k*N_s*thickness
			cos_phi = cmath.cos(phi)
			j_cos_phi = 1.0j*cos_phi
	
			# Calculate the constant parts of dMi.
			dM_phi_s[0] = dM_phi_s[3] = dM_phi_p[0] = dM_phi_p[3] = -cmath.sin(phi)
			dM_phi_s[1] = j_cos_phi/N_s
			dM_phi_p[1] = j_cos_phi/N_p
			dM_phi_s[2] = N_s*j_cos_phi
			dM_phi_p[2] = N_p*j_cos_phi
	
			for i_pos in range(self.length):
				########### Why do I have to put a minus sign here!? ###########
				k_delta_thickness = -k*(2.0*self.positions[i_pos] - thickness)
				delta_phi = N_s*k_delta_thickness
				d_delta_phi = d_N_s*k_delta_thickness
				j_sin_delta_phi = 1.0j*cmath.sin(delta_phi)
	
				# Calculate the variable part of dMi.
				M_delta_phi_s[0] = M_delta_phi_p[0] = M_delta_phi_s[3] = M_delta_phi_p[3] = cmath.cos(delta_phi)
				M_delta_phi_s[1] = j_sin_delta_phi/N_s
				M_delta_phi_p[1] = j_sin_delta_phi/N_p
				M_delta_phi_s[2] = N_s*j_sin_delta_phi
				M_delta_phi_p[2] = N_p*j_sin_delta_phi
	
				# Calculate dMi for the constant and variable parts.
				self.M[i_pos].s[i_wvl][0] = 0.5 * (dM_phi_s[0]*d_delta_phi + inverse_N_s*(M_delta_phi_s[0]-cos_phi)*d_N_s) * dN.N[i_wvl]
				self.M[i_pos].s[i_wvl][1] = 0.5 * (dM_phi_s[1]*d_delta_phi - inverse_N_s*(M_delta_phi_s[1]        )*d_N_s) * dN.N[i_wvl]
				self.M[i_pos].s[i_wvl][2] = 0.5 * (dM_phi_s[2]*d_delta_phi + inverse_N_s*(M_delta_phi_s[2]        )*d_N_s) * dN.N[i_wvl]
				self.M[i_pos].s[i_wvl][3] = 0.5 * (dM_phi_s[3]*d_delta_phi - inverse_N_s*(M_delta_phi_s[3]-cos_phi)*d_N_s) * dN.N[i_wvl]
				self.M[i_pos].p[i_wvl][0] = 0.5 * (dM_phi_p[0]*d_delta_phi + inverse_N_p*(M_delta_phi_p[0]-cos_phi)*d_N_p) * dN.N[i_wvl]
				self.M[i_pos].p[i_wvl][1] = 0.5 * (dM_phi_p[1]*d_delta_phi - inverse_N_p*(M_delta_phi_p[1]        )*d_N_p) * dN.N[i_wvl]
				self.M[i_pos].p[i_wvl][2] = 0.5 * (dM_phi_p[2]*d_delta_phi + inverse_N_p*(M_delta_phi_p[2]        )*d_N_p) * dN.N[i_wvl]
				self.M[i_pos].p[i_wvl][3] = 0.5 * (dM_phi_p[3]*d_delta_phi - inverse_N_p*(M_delta_phi_p[3]-cos_phi)*d_N_p) * dN.N[i_wvl]


	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of needle positions
		
		This method is called when len(instance) is used. It returns the
		number of positions at which the addition of a needle is
		calculated."""
	
		return self.length


	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the needle matrices
		
		This method is called when instance[key] is used. It returns the
		derivatives of the characteristic matrices requested by the key."""
	
		return self.M[key]



########################################################################
#                                                                      #
# calculate_dMi_needles_fast                                           #
#                                                                      #
########################################################################
def calculate_dMi_needles_fast(dMi, N, N_n, thickness, sin2_theta_0):
	"""Calculate the derivative of the characteristic matrix with regard
	to the addition of a needle as a function of its position and
	multiple materials
	
	This function takes 4 arguments:
	  N                 the index of refraction of the layer;
	  N_n               a list of possible index of refraction of the
	                    needle;
	  thickness         the thickness of the layer;
	  sin2_theta_0      the normalized sinus squared of the propagation
	                    angle..
	
	Some elements of the calculation of the derivative of the
	characteristic matrix with regard to the addition of a needle
	do not depend on the needle material. It is therefore posssible
	to speed up the calculation by calculating the derivative for
	multiple materials at once. To work, this function supposes
	(without verifying it) that the position of the needles are the
	same in all the needle matrix instance it receives."""

	# For details and demonstration, see:
	#   Stephane Larouche, Derivatives of the optical properties of
	#   interference filters, 2005.
	
	length = length(dMi)
	
	# Create objects for dM_phi and dM_delta_phi.
	dM_phi_s = [0.0+0.0j]*4
	dM_phi_p = [0.0+0.0j]*4
	dM_delta_phi_s = [0.0+0.0j]*4
	dM_delta_phi_p = [0.0+0.0j]*4
	
	d_phi = [0.0+0.0j]*length
	sum_ratio_s  = [0.0+0.0j]*length
	diff_ratio_s = [0.0+0.0j]*length
	sum_ratio_p  = [0.0+0.0j]*length
	diff_ratio_p = [0.0+0.0j]*length
	
	for i_wvl in range(dMi[0].wvls.length):
		k = two_pi/dMi.wvls.wvls[i_wvl]

		N_square = N.N[i_wvl]*N.N[i_wvl]
		N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i_wvl])
		N_p = N_square/N_s
		
		# Correct branch selection.
		if N_s.real == 0.0:
			N_s = -N_s
			N_p = -N_p
		
		phi = k*N_s*thickness
		j_cos_phi = 1.0j*cmath.cos(phi)
		
		# Calculate the sum and difference of ratios for all the needle
		# materials at once.
		for i_mat in range(length):
			N_n_square = N_n[i_mat].n[i_wvl]*N_n[i_mat].n[i_wvl]
			N_n_s = cmath.sqrt(N_n_square-sin2_theta_0.sin2[i_wvl])
			N_n_p = N_n_square/N_n_s
			
			# Correct branch selection.
			if N_n_s.real == 0.0:
				N_n_s = -N_n_s
				N_n_p = -N_n_p
			
			d_phi[i_mat] = k*N_n_s
			
			sum_ratio_s[i_mat]  = 0.5 * (N_s/N_n_s + N_n_s/N_s)
			diff_ratio_s[i_mat] = 0.5 * (N_s/N_n_s - N_n_s/N_s)
			sum_ratio_p[i_mat]  = 0.5 * (N_p/N_n_p + N_n_p/N_p)
			diff_ratio_p[i_mat] = 0.5 * (N_p/N_n_p - N_n_p/N_p)
		
		# Calculate the constant part of dMi.
		dM_phi_s[0] = dM_phi_s[3] = dM_phi_p[0] = dM_phi_p[3] = -cmath.sin(phi)
		dM_phi_s[1] = j_cos_phi/N_s
		dM_phi_p[1] = j_cos_phi/N_p
		dM_phi_s[2] = N_s*j_cos_phi
		dM_phi_p[2] = N_p*j_cos_phi
		
		for i_pos in range(dMi.length):
			delta_phi = k*N_s*(2.0*dMi[0].positions[i_pos] - thickness)
			j_cos_delta_phi = 1.0j*cmath.cos(delta_phi)
			
			# Calculate the variable part of dMi.
			dM_delta_phi_s[0] = dM_delta_phi_s[3] = dM_delta_phi_p[0] = dM_delta_phi_p[3] = -cmath.sin(delta_phi)
			dM_delta_phi_s[1] = j_cos_delta_phi/N_s
			dM_delta_phi_p[1] = j_cos_delta_phi/N_p
			dM_delta_phi_s[2] = N_s*j_cos_delta_phi
			dM_delta_phi_p[2] = N_p*j_cos_delta_phi
			
			# Add the constant and variable parts for all materials.
			for i_mat in range(length):
				dMi[i_mat].M[i_pos].s[i_wvl][0] = (sum_ratio_s[i_mat]*dM_phi_s[0] + diff_ratio_s[i_mat]*dM_delta_phi_s[0]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].s[i_wvl][1] = (sum_ratio_s[i_mat]*dM_phi_s[1] + diff_ratio_s[i_mat]*dM_delta_phi_s[1]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].s[i_wvl][2] = (sum_ratio_s[i_mat]*dM_phi_s[2] - diff_ratio_s[i_mat]*dM_delta_phi_s[2]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].s[i_wvl][3] = (sum_ratio_s[i_mat]*dM_phi_s[3] - diff_ratio_s[i_mat]*dM_delta_phi_s[3]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].p[i_wvl][0] = (sum_ratio_p[i_mat]*dM_phi_p[0] + diff_ratio_p[i_mat]*dM_delta_phi_p[0]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].p[i_wvl][1] = (sum_ratio_p[i_mat]*dM_phi_p[1] + diff_ratio_p[i_mat]*dM_delta_phi_p[1]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].p[i_wvl][2] = (sum_ratio_p[i_mat]*dM_phi_p[2] - diff_ratio_p[i_mat]*dM_delta_phi_p[2]) * d_phi[i_mat]
				dMi[i_mat].M[i_pos].p[i_wvl][3] = (sum_ratio_p[i_mat]*dM_phi_p[3] - diff_ratio_p[i_mat]*dM_delta_phi_p[3]) * d_phi[i_mat]
