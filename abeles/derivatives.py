# derivatives.py
# 
# Classes to calculate the derivatives of various optical
# parameters (R, T, ...) with regard to the thickness or the index of
# refraction of the layers.
# 
# Copyright (c) 2004-2009,2011,2012,2016 Stephane Larouche.
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

# Import seperatly the elements of the abeles module to avoid the
# loading of the dll if it exists.
from definitions import *
from N import N
from sin2 import sin2
from matrices import matrices
from r_and_t import r_and_t
from spectro import spectrum
from phase import GD, GDD



# Clone the N class to avoid name conflict.
N_class = N



two_pi = 2.0*math.pi



########################################################################
#                                                                      #
# pre_and_post_matrices                                                #
#                                                                      #
########################################################################
class pre_and_post_matrices(object):
	"""A class to store pre and post matrices"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls, nb_layers):
		"""Initialize an instance of the class to store pre and post matrices
		
		This method takes 2 arguments:
		  wvls              the wavelengths at which to calculate the
		                    pre and post matrices;
		  length            the number of layers.
		
		Pre and post matrices are the product of the caracteristic
		matrices before and after a layer, which are used in the
		calculation of derivatives. The pre and post matrix class
		stores all the individual layer matrices and all the pre and post
		matrices for a stack."""
		
		self.wvls = wvls
		self.nb_layers = nb_layers
		
		self.M = matrices(self.wvls)
		
		# Matrices for every layer.
		self.Mi = [matrices(self.wvls) for i in range(self.nb_layers)]
		
		# Pre and post matrices.
		self.pre_M = [matrices(self.wvls) for i in range(self.nb_layers)]
		self.post_M = [matrices(self.wvls) for i in range(self.nb_layers)]
	
	
	######################################################################
	#                                                                    #
	# set_pre_and_post_matrices                                          #
	#                                                                    #
	######################################################################
	def set_pre_and_post_matrices(self, layer_nb, N, thickness, sin2_theta_0):
		"""Set the characteristic matrix of a single layer
		
		This method takes 4 arguments:
		  layer_nb          the position of the layer whose matrices are
		                    being set;
		  N                 the index of refraction of the layer;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		self.Mi[layer_nb].set_matrices(N, thickness, sin2_theta_0)
	
	
	######################################################################
	#                                                                    #
	# multiply_pre_and_post_matrices                                     #
	#                                                                    #
	######################################################################
	def multiply_pre_and_post_matrices(self):
		"""Multiply the layer characteristic matrices to determine all the
		pre and post matrices of a stack
		
		This method takes and returns no argument.
		
		All the individual layer matrices must have been set before
		calculating the pre and post matrices."""
		
		# Calculate the global matrices and pre matrices.
		self.M.set_matrices_unity()
		for i in range(self.nb_layers):
			# For a layer i, the pre-matrix is the global matrix after the
			# previous layer.
			self.pre_M[i].copy_matrices(self.M)
			
			self.M.multiply_matrices(self.Mi[i])
		
		# The last layer has no layer after it.
		self.post_M[-1].set_matrices_unity()
		
		# For post-matrices, the multiplication must be made in reverse order.
		for i in range(self.nb_layers-2, 0-1, -1):
			self.post_M[i].copy_matrices(self.Mi[i+1])
			self.post_M[i].multiply_matrices(self.post_M[i+1])
	
	
	######################################################################
	#                                                                    #
	# get_global_matrices                                                #
	#                                                                    #
	######################################################################
	def get_global_matrices(self):
		"""Get the global matrices of the stack stored in a pre and post
		matrix instance
		
		This returns the global matrices of the stack.
		
		The global matrices are calculated at the same moment than the
		pre and post matrices, so they must have been calculated before
		calling this function."""
		
		return self.M


	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
	
		return self.nb_layers


	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
	
		return self.Mi[key]



########################################################################
#                                                                      #
# dM                                                                   #
#                                                                      #
########################################################################
class dM(matrices):
	"""A class to calculate the derivative of the characteristic matrices
	with regard the thickness and index of layers"""
	
	
	######################################################################
	#                                                                    #
	# set_dMi_thickness                                                  #
	#                                                                    #
	######################################################################
	def set_dMi_thickness(self, N, thickness, sin2_theta_0):
		"""Calculate the derivative of the characteristic matrices of a
		layer with regard to its thickness
		
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
			
			dphi = k*N_s
			phi = dphi*thickness
			j_cos_phi_dphi = 1.0j*cmath.cos(phi)*dphi
			
			self.s[i][0] = self.s[i][3] = self.p[i][0] = self.p[i][3] = -cmath.sin(phi)*dphi
			self.s[i][1] = j_cos_phi_dphi/N_s
			self.p[i][1] = j_cos_phi_dphi/N_p
			self.s[i][2] = N_s*j_cos_phi_dphi
			self.p[i][2] = N_p*j_cos_phi_dphi
	
	
	######################################################################
	#                                                                    #
	# set_dMi_index                                                      #
	#                                                                    #
	######################################################################
	def set_dMi_index(self, N, dN, thickness, sin2_theta_0):
		"""Calculate the derivative of the characteristic matrices of a
		layer with regard to its index of refraction
		
		This method takes 4 arguments:
		  N                 the index of refraction of the layer;
		  dN                the derivative of the index of refraction of
		                    the layer;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle.
		
		The derivative of the index of refraction, dN, is with regard to
		the real part of the index of refraction at the reference
		wavelength and is calculated from the dispersion relation of the
		mixture considered (see N_mixture)."""
		
		for i in range(self.wvls.length):
			k = two_pi/self.wvls.wvls[i]
			
			N_square = N.N[i]*N.N[i]
			N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i])
			N_p = N_square/N_s
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
				N_p = -N_p
			
			phi = k*thickness*N_s
			dN_s = N.N[i]/N_s
			dN_p = dN_s * (2.0 - dN_s*dN_s)
			dphi = k*thickness*dN_s
			sin_phi = cmath.sin(phi)
			j_sin_phi_dN_s = 1.0j*sin_phi*dN_s
			j_sin_phi_dN_p = 1.0j*sin_phi*dN_p
			j_cos_phi_dphi = 1.0j*cmath.cos(phi)*dphi
			
			self.s[i][0] = self.s[i][3] = self.p[i][0] = self.p[i][3] = -sin_phi*dphi * dN.N[i]
			self.s[i][1] = (j_cos_phi_dphi/N_s - j_sin_phi_dN_s/(N_s*N_s)) * dN.N[i]
			self.p[i][1] = (j_cos_phi_dphi/N_p - j_sin_phi_dN_p/(N_p*N_p)) * dN.N[i]
			self.s[i][2] = (N_s*j_cos_phi_dphi + j_sin_phi_dN_s) * dN.N[i]
			self.p[i][2] = (N_p*j_cos_phi_dphi + j_sin_phi_dN_p) * dN.N[i]
	
	
	######################################################################
	#                                                                    #
	# set_dMi_index_with_constant_OT                                     #
	#                                                                    #
	######################################################################
	def set_dMi_index_with_constant_OT(self, N, dN, thickness, sin2_theta_0, N_0, sin2_theta_0_0):
		"""Calculate the derivative of the characteristic matrices of a
		layer with regard to its index of refraction while preserving a
		constant optical thickness
		
		This method takes 6 arguments:
		  N                 the index of refraction of the layer;
		  dN                the derivative of the index of refraction of
		                    the layer;
		  thickness         the thickness of the layer;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  N_0               the index of refraction at the reference
		                    wavelength
		  sin2_theta_0_0    the normalized sinus squared of the
		                    propagation angle at the reference
		                    wavelength.
		
		The optical thickness is kept constant at the reference
		wavelength where the index of refraction is N_0.
		
		The derivative of the index of refraction, dN, is with regard to
		the real part of the index of refraction at the reference
		wavelength and is calculated from the dispersion relation of the
		mixture considered (see N_mixture)."""
		
		if isinstance(N_0, N_class):
			N_0 = N_0[0]
		
		if isinstance(sin2_theta_0_0, sin2):
			sin2_theta_0_0 = sin2_theta_0_0[0]
		
		n_0 = N_0.real;
		k_0 = -N_0.imag;
		N_s_0 = cmath.sqrt(N_0*N_0-sin2_theta_0_0);
		
		# Correct branch selection.
		if N_s_0.real == 0.0:
			N_s_0 = -N_s_0
		
		real_N_s_0 = N_s_0.real;
		imag_N_s_0 = N_s_0.imag;
		norm_N_s_0_square = real_N_s_0*real_N_s_0 + imag_N_s_0*imag_N_s_0;
		
		dd_dn_0 = -thickness/norm_N_s_0_square * (n_0 - (imag_N_s_0/real_N_s_0)*k_0);
		
		for i in range(self.wvls.length):
			k = two_pi/self.wvls.wvls[i]

			N_square = N.N[i]*N.N[i]
			N_s = cmath.sqrt(N_square-sin2_theta_0.sin2[i])
			N_p = N_square/N_s
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
				N_p = -N_p
			
			phi = k*thickness*N_s
			dN_s = N.N[i]/N_s
			dN_p = dN_s * (2.0 - dN_s*dN_s)
			dphi_dN = k*thickness*dN_s;
			dphi_dd = k*N_s;
			dphi_dn_0 = dphi_dN*dN.N[i] + dphi_dd*dd_dn_0;
			sin_phi = cmath.sin(phi);
			j_sin_phi_dN_s_dn_0 = 1.0j*sin_phi*dN_s*dN.N[i];
			j_sin_phi_dN_p_dn_0 = 1.0j*sin_phi*dN_p*dN.N[i];
			j_cos_phi_dphi_dn_0 = 1.0j*cmath.cos(phi)*dphi_dn_0;

			self.s[i][0] = self.s[i][3] = self.p[i][0] = self.p[i][3] = -sin_phi*dphi_dn_0;
			self.s[i][1] = j_cos_phi_dphi_dn_0/N_s - j_sin_phi_dN_s_dn_0/(N_s*N_s);
			self.p[i][1] = j_cos_phi_dphi_dn_0/N_p - j_sin_phi_dN_p_dn_0/(N_p*N_p);
			self.s[i][2] = N_s*j_cos_phi_dphi_dn_0 + j_sin_phi_dN_s_dn_0;
			self.p[i][2] = N_p*j_cos_phi_dphi_dn_0 + j_sin_phi_dN_p_dn_0;
	
	
	######################################################################
	#                                                                    #
	# calculate_dM                                                       #
	#                                                                    #
	######################################################################
	def calculate_dM(self, dMi, M, layer_nb):
		"""Calculate the derivative of the characteristic matrices of the
		stack from that of a layer and pre and post matrices
		
		This method takes 3 arguments:
		  dMi               the derivative of the characteristic matrices
		                    of a layer;
		  M                 the pre and post matrices of the stack;
		  layer_nb          the position of the layer."""
		
		self.set_matrices_unity()
		self.multiply_matrices(M.pre_M[layer_nb])
		self.multiply_matrices(dMi)
		self.multiply_matrices(M.post_M[layer_nb])



########################################################################
#                                                                      #
# psi_matrices                                                         #
#                                                                      #
########################################################################
class psi_matrices(object):
	"""A class to calculate psi matrices
	
	The psi matrices are used to calculate the derivative of amplitude
	reflection and transmission coefficients."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Create a new psi_matrices instance to store the matrices used
		when calculating the derivatives of amplitude reflection or
		transmission.
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    psi matrices."""
		
		self.wvls = wvls
		
		self.psi_r = matrices(self.wvls)
		self.psi_t = matrices(self.wvls)
	
	
	######################################################################
	#                                                                    #
	# calculate_psi_matrices                                             #
	#                                                                    #
	######################################################################
	def calculate_psi_matrices(self, r_and_t, N_m, N_s, sin2_theta_0):
		"""Calculate the psi matrices of a stack
		
		This method takes 4 arguments:
		  r_and_t           the amplitude reflection and transmission of
		                    the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle.
		
		Calculation of the psi_r matrices follow
		  Verly et al., "Efficient refinement algorithm for the synthesis
		  for inhomogeneous optical coatings", Appl. Opt., vol. 36, 1997,
		  pp. 1487-1495.
		The psi_t matrix was constructed to be similar to psi_r."""
		
		# Calculate the psi matrices.
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
			
			# Some usefull partial results.
			one_minus_r_s = 1.0 - r_and_t.r_s[i]
			one_plus_r_s =  1.0 + r_and_t.r_s[i]
			one_minus_r_p = 1.0 - r_and_t.r_p[i]
			one_plus_r_p =  1.0 + r_and_t.r_p[i]
			
			# Multiplier for the reflexion matrix t/(2 N_m).
			mult_r_s = 0.5*r_and_t.t_s[i]/N_m_s
			mult_r_p = 0.5*r_and_t.t_p[i]/N_m_p
			
			# Multiplier for the transmission matrix.
			mult_t_s = - mult_r_s*r_and_t.t_s[i]
			mult_t_p = - mult_r_p*r_and_t.t_p[i]
			
			# Reflexion psi matrices.
			self.psi_r.s[i][0] =   mult_r_s * N_m_s       * one_minus_r_s
			self.psi_r.s[i][1] = - mult_r_s               * one_plus_r_s
			self.psi_r.s[i][2] =   mult_r_s * N_m_s*N_s_s * one_minus_r_s
			self.psi_r.s[i][3] = - mult_r_s * N_s_s       * one_plus_r_s
			
			self.psi_r.p[i][0] =   mult_r_p * N_m_p       * one_minus_r_p
			self.psi_r.p[i][1] = - mult_r_p               * one_plus_r_p
			self.psi_r.p[i][2] =   mult_r_p * N_m_p*N_s_p * one_minus_r_p
			self.psi_r.p[i][3] = - mult_r_p * N_s_p       * one_plus_r_p
			
			# Transmission psi matrices.
			self.psi_t.s[i][0] = mult_t_s * N_m_s
			self.psi_t.s[i][1] = mult_t_s
			self.psi_t.s[i][2] = mult_t_s * N_m_s*N_s_s
			self.psi_t.s[i][3] = mult_t_s * N_s_s
			
			self.psi_t.p[i][0] = mult_t_p * N_m_p
			self.psi_t.p[i][1] = mult_t_p
			self.psi_t.p[i][2] = mult_t_p * N_m_p*N_s_p
			self.psi_t.p[i][3] = mult_t_p * N_s_p
	
	
	######################################################################
	#                                                                    #
	# calculate_psi_matrices_reverse                                     #
	#                                                                    #
	######################################################################
	def calculate_psi_matrices_reverse(self, r_and_t, N_m, N_s, sin2_theta_0):
		"""Calculate the psi matrices of a stack in reverse direction
		
		This method takes 4 arguments:
		  r_and_t           the amplitude reflection and transmission of
		                    the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle.
		
		Calculation of the psi_r matrices follow
		  Verly et al., "Efficient refinement algorithm for the synthesis
		  for inhomogeneous optical coatings", Appl. Opt., vol. 36, 1997,
		  pp. 1487-1495.
		The psi_t matrix was constructed to be similar to psi_r."""
		
		# Calculate the psi matrices.
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
			
			# Some usefull partial results.
			one_minus_r_s = 1.0 - r_and_t.r_s[i]
			one_plus_r_s =  1.0 + r_and_t.r_s[i]
			one_minus_r_p = 1.0 - r_and_t.r_p[i]
			one_plus_r_p =  1.0 + r_and_t.r_p[i]
			
			# Multiplier for the reflexion matrix t/(2 N_s).
			mult_r_s = 0.5*r_and_t.t_s[i]/N_s_s
			mult_r_p = 0.5*r_and_t.t_p[i]/N_s_p
			
			# Multiplier for the transmission matrix.
			mult_t_s = - mult_r_s*r_and_t.t_s[i]
			mult_t_p = - mult_r_p*r_and_t.t_p[i]
	
			# Reflexion psi matrices.
			self.psi_r.s[i][0] =   mult_r_s * N_s_s       * one_minus_r_s
			self.psi_r.s[i][1] = - mult_r_s               * one_plus_r_s
			self.psi_r.s[i][2] =   mult_r_s * N_s_s*N_m_s * one_minus_r_s
			self.psi_r.s[i][3] = - mult_r_s * N_m_s       * one_plus_r_s
	
			self.psi_r.p[i][0] =   mult_r_p * N_s_p       * one_minus_r_p
			self.psi_r.p[i][1] = - mult_r_p               * one_plus_r_p
			self.psi_r.p[i][2] =   mult_r_p * N_s_p*N_m_p * one_minus_r_p
			self.psi_r.p[i][3] = - mult_r_p * N_m_p       * one_plus_r_p
	
			# Transmission psi matrices.
			self.psi_t.s[i][0] = mult_t_s * N_s_s
			self.psi_t.s[i][1] = mult_t_s
			self.psi_t.s[i][2] = mult_t_s * N_s_s*N_m_s
			self.psi_t.s[i][3] = mult_t_s * N_m_s
	
			self.psi_t.p[i][0] = mult_t_p * N_s_p
			self.psi_t.p[i][1] = mult_t_p
			self.psi_t.p[i][2] = mult_t_p * N_s_p*N_m_p
			self.psi_t.p[i][3] = mult_t_p * N_m_p



########################################################################
#                                                                      #
# dr_and_dt                                                            #
#                                                                      #
########################################################################
class dr_and_dt(r_and_t):
	"""A class to calculate amplitude reflection and transmission
	derivatives"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dr_and_dt                                                #
	#                                                                    #
	######################################################################
	def calculate_dr_and_dt(self, dM, psi):
		"""Calculate the derivative of the amplitude reflection and
		transmission
		
		This method takes 2 arguments:
		  dM                the derivative of the characteristic matrices
		                    of the stack;
		  psi               the psi matrices of the stack."""
		
		# Create the M_dr and M_dt matrices.
		M_dr = matrices(self.wvls)
		M_dt = matrices(self.wvls)
		
		# Copy psi matrices in M_dr and M_dt matrices.
		M_dr.copy_matrices(psi.psi_r)
		M_dt.copy_matrices(psi.psi_t)
	
		# Calculate M_dr and M_dt matrices.
		M_dr.multiply_matrices(dM)
		M_dt.multiply_matrices(dM)
		
		# The trace of the matrices are dr and dt.
		for i in range(self.wvls.length):
			self.r_s[i] = M_dr.s[i][0]+M_dr.s[i][3]
			self.r_p[i] = M_dr.p[i][0]+M_dr.p[i][3]
			
			self.t_s[i] = M_dt.s[i][0]+M_dt.s[i][3]
			self.t_p[i] = M_dt.p[i][0]+M_dt.p[i][3]
	
	
	######################################################################
	#                                                                    #
	# calculate_dr_and_dt_reverse                                        #
	#                                                                    #
	######################################################################
	def calculate_dr_and_dt_reverse(self, dM, psi):
		"""Calculate the derivative of the amplitude reflection and
		transmission in reverse direction
		
		This method takes 2 arguments:
		  dM                the derivative of the characteristic matrices
		                    of the stack;
		  psi               the psi matrices of the stack."""
		
		# When calculating in reverse direction we interchange n1 and n2 and
		# use the fact that Abeles matrices are persymmetric; therefore if
		#   M1*M2*M3*.. = A
		# then ..*M3*M2*M1 can be obtained by rotating A about the
		# diagonal going from the upper-right corner to the lower left
		# corner.
		
		dM_reverse = matrices(self.wvls);
		for i in range(self.wvls.length):
			dM_reverse.s[i][0] = dM.s[i][3]
			dM_reverse.s[i][1] = dM.s[i][1]
			dM_reverse.s[i][2] = dM.s[i][2]
			dM_reverse.s[i][3] = dM.s[i][0]
	
			dM_reverse.p[i][0] = dM.p[i][3]
			dM_reverse.p[i][1] = dM.p[i][1]
			dM_reverse.p[i][2] = dM.p[i][2]
			dM_reverse.p[i][3] = dM.p[i][0]
		
		# Create the M_dr and M_dt matrices.
		M_dr = matrices(self.wvls)
		M_dt = matrices(self.wvls)
		
		# Copy psi matrices in M_dr and M_dt matrices.
		M_dr.copy_matrices(psi.psi_r)
		M_dt.copy_matrices(psi.psi_t)
	
		# Calculate M_dr and M_dt matrices.
		M_dr.multiply_matrices(dM_reverse)
		M_dt.multiply_matrices(dM_reverse)
		
		# The trace of the matrices are dr and dt.
		for i in range(self.wvls.length):
			self.r_s[i] = M_dr.s[i][0]+M_dr.s[i][3]
			self.r_p[i] = M_dr.p[i][0]+M_dr.p[i][3]
			
			self.t_s[i] = M_dt.s[i][0]+M_dt.s[i][3]
			self.t_p[i] = M_dt.p[i][0]+M_dt.p[i][3]



########################################################################
#                                                                      #
# dR                                                                   #
#                                                                      #
########################################################################
class dR(spectrum):
	"""A class to calculate the reflectance derivative"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dR                                                       #
	#                                                                    #
	######################################################################
	def calculate_dR(self, dr_and_dt, r_and_t, polarization):
		"""Calculate the derivative of the reflectance
		
		This method takes 3 arguments:
		  dr_and_dt         the derivative of amplitude reflection and
		                    transmission;
		  r_and_t           the amplitude reflection and transmission of
		                    the stack;
		  polarization      the polarization of light."""
		
		if polarization == S:
			for i in range(self.wvls.length):
				self.data[i] = 2.0*(r_and_t.r_s[i].conjugate()*dr_and_dt.r_s[i]).real
		elif polarization == S:
			for i in range(self.wvls.length):
				self.data[i] = 2.0*(r_and_t.r_p[i].conjugate()*dr_and_dt.r_p[i]).real
		else:
			Psi = polarization*math.pi/180.0;
			sin_Psi = math.sin(Psi);
			sin_Psi_square = sin_Psi*sin_Psi;
			for i in range(self.wvls.length):
				self.data[i] = 2.0*(r_and_t.r_s[i].conjugate()*dr_and_dt.r_s[i]).real * sin_Psi_square\
										 + 2.0*(r_and_t.r_p[i].conjugate()*dr_and_dt.r_p[i]).real * (1.0-sin_Psi_square)
	
	
	######################################################################
	#                                                                    #
	# calculate_dR_with_backside                                         #
	#                                                                    #
	######################################################################
	def calculate_dR_with_backside(self, T_front, dT_front, dR_front, T_front_reverse, dT_front_reverse, R_front_reverse, dR_front_reverse, R_back, N_substrate, thickness, sin2_theta_0):
		"""Calculate the derivative of the reflectance with consideration
		of the backside
		
		This method takes 11 arguments:
		  T_front           the transmittance of the front side;
		  dT_front          the derivative of the transmittance of the
		                    front side;
		  dR_front          the derivative of the reflectance of the front
		                    side;
		  T_front_reverse   the transmittance of the front side in reverse
		                    direction;
		  dT_front_reverse  the derivative of the transmittance of the
		                    front side in reverse direction;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  dR_front_reverse  the derivative of the reflectance of the front
		                    side in reverse direction;
		  R_back            the reflectance of the back side;
		  N_s               the index of refraction of the substrate;
		  thickness         the thickness of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			N_square = N_substrate.N[i]*N_substrate.N[i]
			N_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
			
			beta_imag = (two_pi*thickness*N_s/self.wvls.wvls[i]).imag
			exp_4_beta_imag = math.exp(4.0*beta_imag)
			
			denominator = 1.0 - R_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag;
			common_factor = T_front.data[i]*T_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag/denominator
			self.data[i] = dR_front.data[i] + common_factor * (dT_front.data[i]/T_front.data[i] + dT_front_reverse.data[i]/T_front_reverse.data[i] + dR_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag/denominator)
	
	
	######################################################################
	#                                                                    #
	# calculate_dR_with_backside_2                                       #
	#                                                                    #
	######################################################################
	def calculate_dR_with_backside_2(self, T_front, T_front_reverse, R_front_reverse, R_back, dR_back, N_substrate, thickness, sin2_theta_0):
		"""Calculate the derivative of the reflectance with regard to a
		variation in the stack on the backside and with consideration
		consideration of the backside
		
		This method takes 8 arguments:
		  T_front           the transmittance of the front side;
		  T_front_reverse   the transmittance of the front side in reverse
		                    direction;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  R_back            the reflectance of the back side;
		  dR_back           the derivative of the reflectance of the back
		                    side;
		  N_s               the index of refraction of the substrate;
		  thickness         the thickness of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		for i in range(self.wvls.length):
			N_square = N_substrate.N[i]*N_substrate.N[i]
			N_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
			
			# Correct branch selection.
			if N_s.real == 0.0:
				N_s = -N_s
			
			beta_imag = (two_pi*thickness*N_s/self.wvls.wvls[i]).imag
			exp_4_beta_imag = math.exp(4.0*beta_imag)
			
			denominator = 1.0 - R_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag;
			common_factor = T_front.data[i]*T_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag/denominator
			self.data[i] = common_factor * (1.0/R_back.data[i] + R_front_reverse.data[i]*exp_4_beta_imag/denominator) * dR_back.data[i]



########################################################################
#                                                                      #
# dT                                                                   #
#                                                                      #
########################################################################
class dT(spectrum):
	"""A class to calculate the transmittance derivative"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dT                                                       #
	#                                                                    #
	######################################################################
	def calculate_dT(self, dr_and_dt, r_and_t, N_i, N_e, sin2_theta_0, polarization):
		"""Calculate the derivative of the transmittance
		
		This method takes 3 arguments:
		  dr_and_dt         the derivative of amplitude reflection and
		                    transmission;
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
				
				self.data[i] = 2.0*(N_e_s.real/N_i_s.real)*(r_and_t.t_s[i].conjugate()*dr_and_dt.t_s[i]).real
		elif polarization == P:
			for i in range(self.wvls.length):
				N_square = N_i.N[i]*N_i.N[i]
				N_i_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_square = N_e.N[i]*N_e.N[i]
				N_e_p = N_square/cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				
				self.data[i] = 2.0*(N_e_p.real/N_i_p.real)*(r_and_t.t_p[i].conjugate()*dr_and_dt.t_p[i]).real
		else:
			Psi = polarization*math.pi/180.0;
			sin_Psi = math.sin(Psi);
			sin_Psi_square = sin_Psi*sin_Psi;
			for i in range(self.wvls.length):
				N_square = N_i.N[i]*N_i.N[i]
				N_i_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_i_p = N_square/N_i_s
				N_square = N_e.N[i]*N_e.N[i]
				N_e_s = cmath.sqrt(N_square - sin2_theta_0.sin2[i])
				N_e_p = N_square/N_e_s
				
				self.data[i] = 2.0*(N_e_s.real/N_i_s.real)*(r_and_t.t_s[i].conjugate()*dr_and_dt.t_s[i]).real * sin_Psi_square\
				             + 2.0*(N_e_p.real/N_i_p.real)*(r_and_t.t_p[i].conjugate()*dr_and_dt.t_p[i]).real * (1.0-sin_Psi_square)
	
	
	######################################################################
	#                                                                    #
	# calculate_dT_with_backside                                         #
	#                                                                    #
	######################################################################
	def calculate_dT_with_backside(self, T_front, dT_front, R_front_reverse, dR_front_reverse, T_back, R_back, N_s, thickness, sin2_theta_0):
		"""Calculate the derivative of the transmittance with consideration
		of the backside
		
		This method takes 9 arguments:
		  T_front           the transmittance of the front side;
		  dT_front          the derivative of the transmittance of the
		                    front side;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  dR_front_reverse  the derivative of the reflectance of the front
		                    side in reverse direction;
		  T_back            the transmitrance of the back side;
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
			
			denominator = 1.0 - R_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag;
			T = T_front.data[i]*T_back.data[i]*math.exp(2.0*beta_imag)/denominator;
			self.data[i] = T * (dT_front.data[i]/T_front.data[i] + dR_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag/denominator);
	
	
	######################################################################
	#                                                                    #
	# calculate_dT_with_backside_2                                       #
	#                                                                    #
	######################################################################
	def calculate_dT_with_backside_2(self, T_front, R_front_reverse, T_back, dT_back, R_back, dR_back, N_s, thickness, sin2_theta_0):
		"""Calculate the derivative of the transmittance with regard to a
		variation in the stack on the backside and with consideration
		of the backside
		
		This method takes 9 arguments:
		  T_front           the transmittance of the front side;
		  R_front_reverse   the reflectance of the front side in reverse
		                    direction;
		  T_back            the transmittance of the back side;
		  dT_back           the derivative of the transmittance of the back
		                    side;
		  R_back            the reflectance of the back side;
		  dR_back           the derivative of the reflectance of the back
		                    side;
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
			
			denominator = 1.0 - R_front_reverse.data[i]*R_back.data[i]*exp_4_beta_imag;
			T = T_front.data[i]*T_back.data[i]*math.exp(2.0*beta_imag)/denominator;
			self.data[i] = T * (1.0/T_back.data[i]*dT_back.data[i] + R_front_reverse.data[i]*exp_4_beta_imag/denominator*dR_back.data[i])



########################################################################
#                                                                      #
# dA                                                                   #
#                                                                      #
########################################################################
class dA(spectrum):
	"""A class to calculate the absorptance derivative"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dA                                                       #
	#                                                                    #
	######################################################################
	def calculate_dA(self, dR, dT):
		"""Calculate the derivative of the absorptance from that of the
		reflectance and the transmittance
		
		This method takes 2 arguments:
		  dR                the derivative of the reflectance;
		  dT                the derivative of the transmittance."""
		
		for i in range(self.wvls.length):
			self.data[i] = -(dR.data[i]+dT.data[i])



########################################################################
#                                                                      #
# dphase                                                               #
#                                                                      #
########################################################################
class dphase(spectrum):
	"""A class to calculate the derivative of the phase of the reflected
	or transmitted light"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dr_phase                                                 #
	#                                                                    #
	######################################################################
	def calculate_dr_phase(self, M, dM, N_m, N_s, sin2_theta_0, polarization):
		"""Calculate the derivative of the phase shift upon reflection
		
		This method takes 6 arguments:
		  M                 the characteristic matrices of the stack;
		  dM                the derivative of the characteristic matrices
		                    of the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
		
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
				
				# Admittance of s polarisation and its derivative.
				B = M.s[i][0] + M.s[i][1]*N_s_s
				C = M.s[i][2] + M.s[i][3]*N_s_s
				dB = dM.s[i][0] + dM.s[i][1]*N_s_s
				dC = dM.s[i][2] + dM.s[i][3]*N_s_s
				B_conj = B.conjugate()
				C_conj = C.conjugate()
				dB_conj = dB.conjugate()
				dC_conj = dC.conjugate()
				
				# s reflection phase derivative.
				numerator = (N_m_s*(B*C_conj-C*B_conj)).imag
				denominator = (N_m_s*N_m_s*B*B_conj-C*C_conj).real
				dnumerator = (N_m_s*(dB*C_conj+B*dC_conj-dC*B_conj-C*dB_conj)).imag
				ddenominator = 2.0*(N_m_s*N_m_s*dB*B_conj-dC*C_conj).real
				ratio = numerator/denominator
				self.data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator)
		
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
				
				# Admittance of p polarisation and its derivative.
				B = M.p[i][0] + M.p[i][1]*N_s_p
				C = M.p[i][2] + M.p[i][3]*N_s_p
				dB = dM.p[i][0] + dM.p[i][1]*N_s_p
				dC = dM.p[i][2] + dM.p[i][3]*N_s_p
				B_conj = B.conjugate()
				C_conj = C.conjugate()
				dB_conj = dB.conjugate()
				dC_conj = dC.conjugate()
				
				# p reflection phase derivative.
				numerator = (N_m_p*(B*C_conj-C*B_conj)).imag
				denominator = (N_m_p*N_m_p*B*B_conj-C*C_conj).real
				dnumerator = (N_m_p*(dB*C_conj+B*dC_conj-dC*B_conj-C*dB_conj)).imag
				ddenominator = 2.0*(N_m_p*N_m_p*dB*B_conj-dC*C_conj).real
				ratio = numerator/denominator
				self.data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator)
	
	
	######################################################################
	#                                                                    #
	# calculate_dt_phase                                                 #
	#                                                                    #
	######################################################################
	def calculate_dt_phase(self, M, dM, N_m, N_s, sin2_theta_0, polarization):
		"""Calculate the derivative of the phase shift upon transmission
		
		This method takes 6 arguments:
		  M                 the characteristic matrices of the stack;
		  dM                the derivative of the characteristic matrices
		                    of the stack;
		  N_m               the index of refraction of the medium;
		  N_s               the index of refraction of the substrate;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle;
		  polarization      the polarization of light."""
		
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
				dB = dM.s[i][0] + dM.s[i][1]*N_s_s
				dC = dM.s[i][2] + dM.s[i][3]*N_s_s
				
				# s transmission phase.
				temp = N_m_s*B+C
				dtemp = N_m_s*dB+dC
				numerator = -temp.imag
				denominator = temp.real
				dnumerator = -dtemp.imag
				ddenominator = dtemp.real
				ratio = numerator/denominator
				self.data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator)
		
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
				dB = dM.p[i][0] + dM.p[i][1]*N_s_p
				dC = dM.p[i][2] + dM.p[i][3]*N_s_p
				
				# p transmission phase.
				temp = N_m_p*B+C
				dtemp = N_m_p*dB+dC
				numerator = -temp.imag
				denominator = temp.real
				dnumerator = -dtemp.imag
				ddenominator = dtemp.real
				ratio = numerator/denominator
				self.data[i] = ratio/(1.0+ratio*ratio) * (dnumerator/numerator - ddenominator/denominator)



########################################################################
#                                                                      #
# dGD                                                                  #
#                                                                      #
########################################################################
class dGD(GD):
	"""A class to calculate the derivative of the group delay"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dGD                                                      #
	#                                                                    #
	######################################################################
	def calculate_dGD(self, dphase):
		"""Calculate the derivative of the group delay
		
		This method takes 1 argument:
		  dphase            the derivative of the phase shift of the
		                    filter.
		
		The derivative of the group delay is calculated exactly like the
		group delay, except that it is calculated from the derivative of
		the phase instead of the phase."""
		
		GD.calculate_GD(self, dphase)



########################################################################
#                                                                      #
# dGDD                                                                 #
#                                                                      #
########################################################################
class dGDD(GDD):
	"""A class to calculate the derivative of the group delay dispersion"""
	
	
	######################################################################
	#                                                                    #
	# calculate_dGDD                                                     #
	#                                                                    #
	######################################################################
	def calculate_dGDD(self, dphase):
		"""Calculate the derivative of the group delay dispersion
		
		This method takes 1 argument:
		  dphase            the derivative of the phase shift of the
		                    filter.
		
		The derivative of the group delay dispersion is calculated
		exactly like the group delay, except that it is calculated from
		the derivative of the phase instead of the phase."""
		
		GDD.calculate_GDD(self, dphase)
