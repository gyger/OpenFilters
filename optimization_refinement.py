# optimization_refinement.py
# 
# Optimization by refinement.
#
# Copyright (c) 2004-2009,2012,2013,2015 Stephane Larouche.
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
import time

import config
from definitions import *
import abeles
import color
from optical_filter import one_hundred_eighty_over_pi
import optimization
import targets
from moremath import Levenberg_Marquardt



# Constants for the description of fit parameters.
THICKNESS = 0
INDEX = 1



########################################################################
#                                                                      #
# optimization_refinement                                              #
#                                                                      #
########################################################################
class optimization_refinement(optimization.optimization):
	"""A class to optimize an optical filter using refinement"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, targets, parent = None):
		"""Initialize an instance of the optimization class
		
		This method takes 2 or 3 arguments:
		  filter             the filter being optimized;
		  targets            the targets used in the optimization;
		  parent             (optional) the user interface used to do the
		                     optimization.
		
		If given, the parent must implement an update method taking two
		arguments (working, status)."""
		
		optimization.optimization.__init__(self, filter, targets, parent)
		
		# Stop criteria.
		self.max_iterations = config.REFINEMENT_MAX_ITERATIONS
		self.min_gradient = config.REFINEMENT_MIN_GRADIENT
		self.acceptable_chi_2 = config.REFINEMENT_ACCEPTABLE_CHI_2
		self.min_chi_2_change = config.REFINEMENT_MIN_CHI_2_CHANGE
		
		# Initial maximum number of iteration, used to increase the maximum
		# number of iteration when the user wants to continue the
		# refinement.
		self.initial_max_iterations = self.max_iterations
		
		# Minimal thickness and minimal index difference used when the
		# design is cleaned.
		self.min_thickness = 0.0
		self.min_delta_n = 0.0
		
		# Indicates if the last operation was the removal of thin layers.
		self.just_removed_thin_layers = False
		
		# Indicates if the filter must be fully recreated. For example,
		# when the number or materials of the layer have changed (this is
		# the case in the needle and step methods). 
		self.need_to_reset_filter = False
		
		self.prepare()
	
	
	######################################################################
	#                                                                    #
	# prepare                                                            #
	#                                                                    #
	######################################################################
	def prepare(self):
		"""Prepare for optimization
		
		Prepare instance attributes."""
		
		# Get all the actual properties of the filter.
		center_wavelength = self.filter.get_center_wavelength()
		materials = self.filter.get_materials()
		front_medium_name, back_medium_name = self.filter.get_medium()
		front_medium = self.filter.get_material_nb(front_medium_name)
		back_medium = self.filter.get_material_nb(back_medium_name)
		substrate_name = self.filter.get_substrate()
		substrate = self.filter.get_material_nb(substrate_name)
		substrate_thickness = self.filter.get_substrate_thickness()
		front_layers, front_layer_descriptions, front_thickness, front_index, front_step_profiles = self.filter.get_layers(FRONT)
		back_layers, back_layer_descriptions, back_thickness, back_index, back_step_profiles = self.filter.get_layers(BACK)
		consider_backside = self.filter.get_consider_backside()
		
		# Then make copies of the properties that may be modified during
		# the refinement in order to leave originals unchanged to allow
		# the user to cancel the operation. Since the back layers are
		# not fitted, there is no need to make a copy. It is important to
		# don't make a copy of materials since the needle method might
		# augment it inside the optical_filter object.
		self.center_wavelength = center_wavelength
		self.materials = materials
		self.front_medium = front_medium
		self.back_medium = back_medium
		self.substrate = substrate
		self.substrate_thickness = substrate_thickness
		self.front_layers = front_layers[:]
		self.front_layer_descriptions = front_layer_descriptions[:]
		self.front_thickness = front_thickness[:]
		self.front_index = front_index[:]
		self.front_step_profiles = front_step_profiles[:]
		self.back_layers = back_layers[:]
		self.back_layer_descriptions = back_layer_descriptions[:]
		self.back_thickness = back_thickness[:]
		self.back_index = back_index[:]
		self.back_step_profiles = back_step_profiles[:]
		
		# Calculate the number of layers and of materials.
		self.nb_front_layers = len(self.front_layers)
		self.nb_back_layers = len(self.back_layers)
		self.nb_materials = len(self.materials)
		
		# Local copy of the list of layers to fit and where to add needles
		# and steps. We keep the lists for the addition of needles and
		# steps in this class instead of children classes because we want
		# to remember the setting whether we use the needle or the step
		# methods. This is kept locally because it will be modified when
		# layers are added and we want to be able to cancel.
		self.refine_thickness = [self.filter.get_refine_layer_thickness(i_layer, FRONT) for i_layer in range(self.nb_front_layers)]
		self.refine_index = [self.filter.get_refine_layer_index(i_layer, FRONT) for i_layer in range(self.nb_front_layers)]
		self.preserve_OT = [self.filter.get_preserve_OT(i_layer, FRONT) for i_layer in range(self.nb_front_layers)]
		self.add_needles_in_layer = [self.filter.get_add_needles(i_layer, FRONT) for i_layer in range(self.nb_front_layers)]
		self.add_steps_in_layer = [self.filter.get_add_steps(i_layer, FRONT) for i_layer in range(self.nb_front_layers)]
		
		# Determine which materials are used in graded-index layers.
		used_in_graded_index_layer = [False]*self.nb_materials
		for i_layer in range(len(self.front_layers)):
			if self.filter.is_graded(i_layer, FRONT):
				used_in_graded_index_layer[self.front_layers[i_layer]] = True
		for i_layer in range(len(self.back_layers)):
			if self.filter.is_graded(i_layer, BACK):
				used_in_graded_index_layer[self.back_layers[i_layer]] = True
		
		# Determine which materials are used in layers whose OT is
		# preserved.
		used_in_preserve_OT_layer = [False]*self.nb_materials
		for i_layer in range(len(self.front_layers)):
			if self.filter.get_preserve_OT(i_layer, FRONT):
				used_in_preserve_OT_layer[self.front_layers[i_layer]] = True
		for i_layer in range(len(self.back_layers)):
			if self.filter.get_preserve_OT(i_layer, BACK):
				used_in_preserve_OT_layer[self.back_layers[i_layer]] = True
		
		# Create lists with the minimum and maximum indices. They will be
		# usefull in multiple occasions.
		self.n_min = [0.0]*self.nb_materials
		self.n_max = [0.0]*self.nb_materials
		for i_material in range(self.nb_materials):
			if self.materials[i_material].is_mixture():
				self.n_min[i_material], self.n_max[i_material] = self.materials[i_material].get_index_range(self.center_wavelength)
		
		# Calculate the number of parameters and build a list relating
		# an ordered parameter number with the parameter it represents,
		# a list of their values and lists of their minimum and
		# maximum values.
		self.nb_parameters = 0
		self.parameters = []
		self.parameter_values = []
		self.parameter_min = []
		self.parameter_max = []
		for i_layer in range(len(self.front_layers)):
			if self.refine_thickness[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((THICKNESS, i_layer))
				self.parameter_values.append(self.front_thickness[i_layer])
				self.parameter_min.append(0.0)
				self.parameter_max.append(Levenberg_Marquardt.INFINITY)
			if self.refine_index[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((INDEX, i_layer))
				self.parameter_values.append(self.front_index[i_layer])
				self.parameter_min.append(self.n_min[self.front_layers[i_layer]])
				self.parameter_max.append(self.n_max[self.front_layers[i_layer]])
		self.old_parameter_values = self.parameter_values[:]
		
		# Determine the number of targets.
		self.nb_targets = len(self.targets)
		
		# For every target, determine if the backside is considered and the
		# direction of propagation. At this moment, the consideration of
		# backside applies to the whole filter, but keeping it seperatly
		# for every target simplifies the structure of the methods in this
		# class. Furthermore it will simplify an inventual addition of the
		# possibility for the user to specify target by target when the
		# backside should be considered.
		self.consider_backside = [False]*self.nb_targets
		self.direction = [FORWARD]*self.nb_targets
		for i_target in range(self.nb_targets):
			target = self.targets[i_target]
			kind = target.get_kind()
			
			if kind not in targets.DISPERSIVE_TARGETS:
				self.consider_backside[i_target] = consider_backside
			
			if kind in targets.REVERSIBLE_TARGETS:
				self.direction[i_target] = target.get_direction()
		
		# Make objects for the center wavelength and the normalized sin
		# square at center wavelength; this is used when the OT of a layer
		# is preserved.
		self.center_wavelength_ = abeles.wvls(1)
		self.center_wavelength_.set_wvl(0, self.center_wavelength)
		N_front_medium_center_wvl = self.materials[self.front_medium].get_N(self.center_wavelength_)
		self.sin2_theta_0_center_wvl = abeles.sin2(self.center_wavelength_)
		self.sin2_theta_0_center_wvl.set_sin2_theta_0(N_front_medium_center_wvl, 0.0)
		
		# If a material is used in a layer whose OT is preserved, we need a
		# N object at the center wavelength.
		self.N_center_wvl = [None]*self.nb_materials
		for i_material in range(self.nb_materials):
			if used_in_preserve_OT_layer[i_material]:
				self.N_center_wvl[i_material] = self.materials[i_material].get_N(self.center_wavelength_)
		
		# When the OT of a layer is kept constant, we calculate it at the
		# beginning and use it to calculate the thickness at every
		# iteration to avoid numerical errors.
		self.OT = [0.0]*self.nb_front_layers
		for i_layer in range(len(self.front_layers)):
			if self.filter.get_preserve_OT(i_layer, FRONT):
				self.OT[i_layer] = self.front_thickness[i_layer] * self.front_index[i_layer]
		
		# For every target, we need some of the following objects:
		#   - the target values (wvls + values + tolerances +
		#     inequalities), and we keep the number of wvls since it will
		#     be used often;
		#   - one wvls object;
		#   - N objects:
		#     - for all materials,
		#     - for the minimum index (mixtures),
		#     - for the maximum index (mixtures);
		#   - one sin2 object;
		#   - one pre_and_post_matrices object, that includes the global
		#     matrix of the coating on the frontside;
		#   - matrices for the backside (Rb, Tb);
		#   - r_and_t objects for:
		#     - front side in forward direction (T, Tb, R, Rb, A, Ab),
		#     - front side in reverse direction (Rb, Tb, rR, rT, rRb, rTb, rA, rAb),
		#     - back side in forward direction (Rb, Tb, rRb, rTb, Ab, rAb);
		#     - back side in reverse direction (rRb, rTb, rAb);
		#   - R, T, or A objects for:
		#     - R of front side in forward direction (R, Rb, A, Ab),
		#     - T of front side in forward direction (T, Tb, Rb, A, Ab),
		#     - R of front side in reverse direction (Tb, Rb, rR, rRb, rTb, Ab, rA, rAb),
		#     - T of front side in reverse direction (Rb, Ab, rA, rAb),
		#     - R of the backside (Tb, Rb, rRb, rTb, Ab, rAb),
		#     - T of the backside (Tb, rRb, Ab, rAb),
		#     - R of the backside in reverse direction (rRb, rAb),
		#     - T of the backside in reverse direction (rRb, rTb, rAb),
		#     - R of the sample (R, Rb, rR, rRb, A, Ab, rA, rAb),
		#     - T of the sample (T, Tb, rTb, A, Ab, rAb);
		#     - A of the sample (A, Ab, rA, rAb)
		#   - phase objects for:
		#     - reflection phase of the front side (phi_t, GD_t, GDD_t),
		#     - transmission phase of the front side (phi_t, GD_t, GDD_t);
		#   - appropriate objects to hold the values of the derived
		#     targets (such as color, GD, and GDD);
		#   - matrices objects for psi matrices (R, T, Rb, Tb, A, Ab);
		#   - matrices objects for psi matrices in reverse direction
		#     (Rb, Tb, rR, rRb, Ab, rAb);
		#   - for every variable parameter:
		#     - a dM object for dMi,
		#     - a dM object for dM,
		#     - dr_and_dt objects for
		#       - dr and dt (R, T, Rb, Tb, A, Ab),
		#       - dr and dt in reverse direction (Rb, Tb, rR, rRb, Ab, rA, rAb),
		#     - dR or dT objects for:
		#       - dR of the front side in forward direction (R, Rb, A, Ab),
		#       - dT of the front side in forward direction (T, Rb, Tb, A, Ab),
		#       - dR of the front side in reverse direction (Rb, Tb, rR, rRb, Ab, rA, rAb),
		#       - dT of the front side in reverse direction (Rb, Ab, rA, rAb),
		#       - dR of the sample (R, Rb, rR, rRb, A, Ab, rA, rAb),
		#       - dT of the sample (T, Tb, A, Ab, rA, rAb),
		#       - dA of the sample (A, Ab, rA, rAb),
		#     - dphase objects for:
		#       - dphi_r (phi_r, GD_r, GDD_r),
		#       - dphi_t (phi_t, GD_t, GDD_t);
		#     - appropriate objects to hold the derivatives of the
		#       derived targets (such as color, GD, and GDD).
		# 
		# Content of the parenthesis indicates that an object is needed
		# only for a particular kind of target:
		#    R    reflection without the backside;
		#    T    transmission without the backside;
		#    A    absorption without the backside;
		#    Rb   reflection with the backside;
		#    Tb   transmission with the backside;
		#    Ab   absorption with the backside;
		#   rR    reflection without the backside in reverse direction;
		#   rT    transmission without the backside in reverse direction;
		#   rA    absorption without the backside in reverse direction;
		#   rRb   reflection with the backside in reverse direction;
		#   rTb   transmission with the backside in reverse direction;
		#   rAb   absorption with the backside in reverse direction;
		#   phi_r reflection phase;
		#   phi_r transmission phase;
		#   GD_r  reflection GD;
		#   GD_r  transmission GD;
		#   GDD_r reflection GDD;
		#   GDD_r transmission GDD.
		# Color calculations are based on photometric values and fit in one
		# of the categories R, T, Rb, Tb, rB, or rRb.
		# 
		# To simplify the structure of the program, lists of None are 
		# created for all objects and populated with the appropriate
		# objects only if needed.
		# 
		# Also, when the index of materials is fitted, the optimal index is
		# often the minimum of maximum index possible for the material.
		# Therefore, multiple layers will be of those indices and the index
		# and its derivative will be needed repeatedly. To avoid a lot of
		# repeatitive calculations, these indices and derivatives are
		# calculated only once and saved.
		
		# We therefore: (1) Create empty lists.
		self.wvls = [None]*self.nb_targets
		self.target_values = [None]*self.nb_targets
		self.tolerances = [None]*self.nb_targets
		self.inequalities = [None]*self.nb_targets
		self.nb_wvls = [0]*self.nb_targets
		self.wvls_ = [None]*self.nb_targets
		self.N = [None]*self.nb_targets
		self.N_min = [None]*self.nb_targets
		self.N_max = [None]*self.nb_targets
		for i_target in range(self.nb_targets):
			self.N[i_target] = [None]*self.nb_materials
			self.N_min[i_target] = [None]*self.nb_materials
			self.N_max[i_target] = [None]*self.nb_materials
		self.sin2_theta_0 = [None]*self.nb_targets
		self.pre_and_post_matrices = [None]*self.nb_targets
		self.matrices_front = [None]*self.nb_targets
		self.matrices_back = [None]*self.nb_targets
		self.r_and_t_front = [None]*self.nb_targets
		self.r_and_t_front_reverse = [None]*self.nb_targets
		self.r_and_t_back = [None]*self.nb_targets
		self.r_and_t_back_reverse = [None]*self.nb_targets
		self.R_front = [None]*self.nb_targets
		self.T_front = [None]*self.nb_targets
		self.R_front_reverse = [None]*self.nb_targets
		self.T_front_reverse = [None]*self.nb_targets
		self.R_back = [None]*self.nb_targets
		self.T_back = [None]*self.nb_targets
		self.R_back_reverse = [None]*self.nb_targets
		self.T_back_reverse = [None]*self.nb_targets
		self.R = [None]*self.nb_targets
		self.T = [None]*self.nb_targets
		self.A = [None]*self.nb_targets
		self.phi_r = [None]*self.nb_targets
		self.phi_t = [None]*self.nb_targets
		self.derived_values = [None]*self.nb_targets
		self.psi = [None]*self.nb_targets
		self.psi_reverse = [None]*self.nb_targets
		self.dMi = [None]*self.nb_targets
		self.dM = [None]*self.nb_targets
		self.dr_and_dt_front = [None]*self.nb_targets
		self.dr_and_dt_front_reverse = [None]*self.nb_targets
		self.dR_front = [None]*self.nb_targets
		self.dT_front = [None]*self.nb_targets
		self.dR_front_reverse = [None]*self.nb_targets
		self.dT_front_reverse = [None]*self.nb_targets
		self.dR = [None]*self.nb_targets
		self.dT = [None]*self.nb_targets
		self.dA = [None]*self.nb_targets
		self.dphi_r = [None]*self.nb_targets
		self.dphi_t = [None]*self.nb_targets
		self.dderived_values = [None]*self.nb_targets
		for i_target in range(self.nb_targets):
			self.dMi[i_target] = [None]*self.nb_parameters
			self.dM[i_target] = [None]*self.nb_parameters
			self.dr_and_dt_front[i_target] = [None]*self.nb_parameters
			self.dr_and_dt_front_reverse[i_target] = [None]*self.nb_parameters
			self.dR_front[i_target] = [None]*self.nb_parameters
			self.dT_front[i_target] = [None]*self.nb_parameters
			self.dR_front_reverse[i_target] = [None]*self.nb_parameters
			self.dT_front_reverse[i_target] = [None]*self.nb_parameters
			self.dR[i_target] = [None]*self.nb_parameters
			self.dT[i_target] = [None]*self.nb_parameters
			self.dA[i_target] = [None]*self.nb_parameters
			self.dphi_r[i_target] = [None]*self.nb_parameters
			self.dphi_t[i_target] = [None]*self.nb_parameters
			self.dderived_values[i_target] = [None]*self.nb_parameters
		
		# (2) Fill them with the appropriate objects, when needed.
		for i_target in range(self.nb_targets):
			target = self.targets[i_target]
			kind = target.get_kind()
			
			if kind in targets.DISCRETE_TARGETS or kind in targets.SPECTRUM_TARGETS:
				self.wvls[i_target], self.target_values[i_target], self.tolerances[i_target] = target.get_values()
			elif kind in targets.COLOR_TARGETS:
				# For color calculations, the observer wavelengths are used.
				illuminant_name, observer_name = target.get_illuminant_and_observer()
				observer = color.get_observer(observer_name)
				self.wvls[i_target], dummy, dummy, dummy = observer.get_functions()
				self.target_values[i_target], self.tolerances[i_target] = target.get_values()
			self.inequalities[i_target] = target.get_inequality()
			
			# In order to numerically determine the GD or the GDD, it is
			# necessary to calculate the phase at three points.
			if kind in [targets.R_GD_TARGET, targets.T_GD_TARGET, targets.R_GDD_TARGET, targets.T_GDD_TARGET]:
				self.nb_wvls[i_target] = 3
			# Otherwise, we simply use the wavelengths of the target.
			else:
				self.nb_wvls[i_target] = len(self.wvls[i_target])
			
			self.wvls_[i_target] = abeles.wvls(self.nb_wvls[i_target])
			self.sin2_theta_0[i_target] = abeles.sin2(self.wvls_[i_target])
			
			# We only get the global matrices once since we get a pointer
			# that will always point to the right matrices.
			self.pre_and_post_matrices[i_target] = abeles.pre_and_post_matrices(self.wvls_[i_target], self.nb_front_layers)
			self.matrices_front[i_target] = self.pre_and_post_matrices[i_target].get_global_matrices()
			if self.consider_backside[i_target]:
				self.matrices_back[i_target] = abeles.matrices(self.wvls_[i_target])
			
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
				if self.direction[i_target] == FORWARD:
					self.r_and_t_front[i_target] = abeles.r_and_t(self.wvls_[i_target])
					if self.consider_backside[i_target]:
						self.r_and_t_front_reverse[i_target] = abeles.r_and_t(self.wvls_[i_target])
						self.r_and_t_back[i_target] = abeles.r_and_t(self.wvls_[i_target])
				else:
					self.r_and_t_front_reverse[i_target] = abeles.r_and_t(self.wvls_[i_target])
					if self.consider_backside[i_target]:
						self.r_and_t_back[i_target] = abeles.r_and_t(self.wvls_[i_target])
						self.r_and_t_back_reverse[i_target] = abeles.r_and_t(self.wvls_[i_target])
				
				if kind in targets.REFLECTION_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.R_front[i_target] = abeles.R(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.T_front[i_target] = abeles.T(self.wvls_[i_target])
							self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.T_front_reverse[i_target] = abeles.T(self.wvls_[i_target])
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.R[i_target] = abeles.R(self.wvls_[i_target])
						else:
							# When the backside is not considered, the reflection of the
							# sample is simply that of the front side.
							self.R[i_target] = self.R_front[i_target]
					else:
						self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back[i_target] = abeles.T(self.wvls_[i_target])
							self.R_back_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back_reverse[i_target] = abeles.T(self.wvls_[i_target])
							self.R[i_target] = abeles.R(self.wvls_[i_target])
						else:
							# When the backside is not considered, the reflection of the
							# sample is simply that of the front side.
							self.R[i_target] = self.R_front_reverse[i_target]
				
				elif kind in targets.TRANSMISSION_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.T_front[i_target] = abeles.T(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back[i_target] = abeles.T(self.wvls_[i_target])
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.T[i_target] = abeles.T(self.wvls_[i_target])
						else:
							# When the backside is not considered, the transmission of the
							# sample is simply that of the front side.
							self.T[i_target] = self.T_front[i_target]
					else:
						self.T_front_reverse[i_target] = abeles.T(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back_reverse[i_target] = abeles.T(self.wvls_[i_target])
							self.T[i_target] = abeles.T(self.wvls_[i_target])
						else:
							# When the backside is not considered, the transmission of the
							# sample is simply that of the front side.
							self.T[i_target] = self.T_front_reverse[i_target]
				
				else:
					if self.direction[i_target] == FORWARD:
						self.R_front[i_target] = abeles.R(self.wvls_[i_target])
						self.T_front[i_target] = abeles.T(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.T_front_reverse[i_target] = abeles.T(self.wvls_[i_target])
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back[i_target] = abeles.T(self.wvls_[i_target])
							self.R[i_target] = abeles.R(self.wvls_[i_target])
							self.T[i_target] = abeles.T(self.wvls_[i_target])
						else:
							# When the backside is not considered, the derivative of
							# the reflection and the transmission of the sample are
							# simply those of the front side.
							self.R[i_target] = self.R_front[i_target]
							self.T[i_target] = self.T_front[i_target]
					else:
						self.R_front_reverse[i_target] = abeles.R(self.wvls_[i_target])
						self.T_front_reverse[i_target] = abeles.T(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.T_back[i_target] = abeles.T(self.wvls_[i_target])
							self.R_back[i_target] = abeles.R(self.wvls_[i_target])
							self.R_back_reverse[i_target] = abeles.R(self.wvls_[i_target])
							self.T_back_reverse[i_target] = abeles.T(self.wvls_[i_target])
							self.R[i_target] = abeles.R(self.wvls_[i_target])
							self.T[i_target] = abeles.T(self.wvls_[i_target])
						else:
							# When the backside is not considered, the derivative of
							# the reflection and the transmission of the sample are
							# simply those of the front side.
							self.R[i_target] = self.R_front_reverse[i_target]
							self.T[i_target] = self.T_front_reverse[i_target]
					self.A[i_target] = abeles.A(self.wvls_[i_target])
				
				if kind in targets.COLOR_TARGETS:
					illuminant_name, observer_name = target.get_illuminant_and_observer()
					illuminant = color.get_illuminant(illuminant_name)
					observer = color.get_observer(observer_name)
					self.derived_values[i_target] = color.color(observer, illuminant)
			
			elif kind in targets.DISPERSIVE_TARGETS:
				if kind in targets.REFLECTION_TARGETS:
					self.phi_r[i_target] = abeles.phase(self.wvls_[i_target])
				else:
					self.phi_t[i_target] = abeles.phase(self.wvls_[i_target])
				
				if kind in targets.GD_TARGETS:
					self.derived_values[i_target] = abeles.GD(self.wvls_[i_target])
				elif kind in targets.GDD_TARGETS:
					self.derived_values[i_target] = abeles.GDD(self.wvls_[i_target])
			
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
				if self.direction[i_target] == FORWARD:
					self.psi[i_target] = abeles.psi_matrices(self.wvls_[i_target])
					if self.consider_backside[i_target] or self.direction[i_target] == BACKWARD:
						self.psi_reverse[i_target] = abeles.psi_matrices(self.wvls_[i_target])
				else:
					self.psi_reverse[i_target] = abeles.psi_matrices(self.wvls_[i_target])
			
			for i_parameter in range(self.nb_parameters):
				self.dMi[i_target][i_parameter] = abeles.dM(self.wvls_[i_target])
				self.dM[i_target][i_parameter] = abeles.dM(self.wvls_[i_target])
				
				if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.dr_and_dt_front[i_target][i_parameter] = abeles.dr_and_dt(self.wvls_[i_target])
						if self.consider_backside[i_target]:
							self.dr_and_dt_front_reverse[i_target][i_parameter] = abeles.dr_and_dt(self.wvls_[i_target])
					else:
						self.dr_and_dt_front_reverse[i_target][i_parameter] = abeles.dr_and_dt(self.wvls_[i_target])
					
					if kind in targets.REFLECTION_TARGETS:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dT_front[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
								self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT_front_reverse[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
								self.dR[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							else:
								# When the backside is not considered, the derivative of
								# the reflection of the sample is simply that of the front
								# side.
								self.dR[i_target][i_parameter] = self.dR_front[i_target][i_parameter]
						else:
							self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dR[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							else:
								# When the backside is not considered, the reflection of the
								# sample is simply that of the front side.
								self.dR[i_target][i_parameter] = self.dR_front_reverse[i_target][i_parameter]
					
					elif kind in targets.TRANSMISSION_TARGETS:
						if self.direction[i_target] == FORWARD:
							self.dT_front[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							else:
								# When the backside is not considered, the derivative of
								# the transmission of the sample is simply that of the
								# front side.
								self.dT[i_target][i_parameter] = self.dT_front[i_target][i_parameter]
						else:
							self.dT_front_reverse[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							else:
								# When the backside is not considered, the derivative of
								# the transmission of the sample is simply that of the
								# front side.
								self.dT[i_target][i_parameter] = self.dT_front_reverse[i_target][i_parameter]
					
					else:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							self.dT_front[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT_front_reverse[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
								self.dR[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							else:
								# When the backside is not considered, the derivative of
								# the reflection and the transmission of the sample are
								# simply those of the front side.
								self.dR[i_target][i_parameter] = self.dR_front[i_target]
								self.dT[i_target][i_parameter] = self.dT_front[i_target]
						else:
							self.dR_front_reverse[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
							self.dT_front_reverse[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							if self.consider_backside[i_target]:
								self.dR[i_target][i_parameter] = abeles.dR(self.wvls_[i_target])
								self.dT[i_target][i_parameter] = abeles.dT(self.wvls_[i_target])
							else:
								# When the backside is not considered, the derivative of
								# the reflection and the transmission of the sample are
								# simply those of the front side.
								self.dR[i_target][i_parameter] = self.dR_front_reverse[i_target]
								self.dT[i_target][i_parameter] = self.dT_front_reverse[i_target]
						self.dA[i_target][i_parameter] = abeles.dA(self.wvls_[i_target])
					
					if kind in targets.COLOR_TARGETS:
						self.dderived_values[i_target][i_parameter] = color.color_derivative(self.derived_values[i_target])
				
				elif kind in targets.DISPERSIVE_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.dphi_r[i_target][i_parameter] = abeles.dphase(self.wvls_[i_target])
					else:
						self.dphi_t[i_target][i_parameter] = abeles.dphase(self.wvls_[i_target])
					
					if kind in targets.GD_TARGETS:
						self.dderived_values[i_target][i_parameter] = abeles.dGD(self.wvls_[i_target])
					elif kind in targets.GDD_TARGETS:
						self.dderived_values[i_target][i_parameter] = abeles.dGDD(self.wvls_[i_target])
		
		# And (3) set the values for what is known.
		for i_target in range(self.nb_targets):
			target = self.targets[i_target]
			kind = target.get_kind()
			angle = target.get_angle()
			polarization = target.get_polarization()
			
			# In order to numerically determine the GD or the GDD, it is
			# necessary to calculate the phase at three points.
			if kind in [targets.R_GD_TARGET, targets.T_GD_TARGET, targets.R_GDD_TARGET, targets.T_GDD_TARGET]:
				wvl = self.wvls[i_target][0]
				self.wvls_[i_target].set_wvl(0, (1.0-config.DISPERSIVE_DIFF)*wvl)
				self.wvls_[i_target].set_wvl(1, wvl)
				self.wvls_[i_target].set_wvl(2, (1.0+config.DISPERSIVE_DIFF)*wvl)
			# Otherwise, we simply use the wavelengths of the target.
			else:
				for i_wvl in range(len(self.wvls[i_target])):
					self.wvls_[i_target].set_wvl(i_wvl, self.wvls[i_target][i_wvl])
			
			for i_material in range(self.nb_materials):
				self.N[i_target][i_material] = self.materials[i_material].get_N(self.wvls_[i_target])
				# Calculate the values on the minimum and maximum indices.
				if self.materials[i_material].is_mixture():
					self.N_min[i_target][i_material] = self.materials[i_material].get_N(self.wvls_[i_target])
					self.N_max[i_target][i_material] = self.materials[i_material].get_N(self.wvls_[i_target])
					self.N_min[i_target][i_material].set_N_mixture(self.n_min[i_material], self.center_wavelength)
					self.N_max[i_target][i_material].set_N_mixture(self.n_max[i_material], self.center_wavelength)
					self.N_min[i_target][i_material].set_dN_mixture(self.n_min[i_material], self.center_wavelength)
					self.N_max[i_target][i_material].set_dN_mixture(self.n_max[i_material], self.center_wavelength)
				# If the material is used in a graded-index layer, prepare the
				# list of indices.
				if used_in_graded_index_layer[i_material]:
					steps = self.filter.get_material_index(i_material)
					self.N[i_target][i_material].prepare_N_mixture_graded(len(steps))
					for i_mixture in range(len(steps)):
						self.N[i_target][i_material].set_N_mixture_graded(i_mixture, steps[i_mixture], self.center_wavelength)
			
			if self.direction[i_target] == FORWARD:
				self.sin2_theta_0[i_target].set_sin2_theta_0(self.N[i_target][self.front_medium], angle)
			else:
				if self.consider_backside[i_target]:
					self.sin2_theta_0[i_target].set_sin2_theta_0(self.N[i_target][self.back_medium], angle)
				else:
					self.sin2_theta_0[i_target].set_sin2_theta_0(self.N[i_target][self.substrate], angle)
			
			for i_layer in range(self.nb_front_layers):
				if isinstance(self.front_thickness[i_layer], list):
					layer_matrices = self.pre_and_post_matrices[i_target][i_layer]
					layer_matrices.set_matrices_unity()
					temp_matrices = abeles.matrices(self.wvls_[i_target])
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						sublayer_n = self.N[i_target][self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(sublayer_n, self.front_thickness[i_layer][i_sublayer], self.sin2_theta_0[i_target])
						layer_matrices.multiply_matrices(temp_matrices)
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						if self.front_index[i_layer] == self.n_min[self.front_layers[i_layer]]:
							N = self.N_min[i_target][self.front_layers[i_layer]].get_N_mixture()
						elif self.front_index[i_layer] == self.n_max[self.front_layers[i_layer]]:
							N = self.N_max[i_target][self.front_layers[i_layer]].get_N_mixture()
						else:
							self.N[i_target][self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
							N = self.N[i_target][self.front_layers[i_layer]].get_N_mixture()
					else:
						N = self.N[i_target][self.front_layers[i_layer]]
					self.pre_and_post_matrices[i_target].set_pre_and_post_matrices(i_layer, N, self.front_thickness[i_layer], self.sin2_theta_0[i_target])
			
			# When the backside is considered, all its properties can be
			# calculated a single time here since the backside is not
			# optimized.
			if self.consider_backside[i_target]:
				# Multiply matrices.
				self.matrices_back[i_target].set_matrices_unity()
				temp_matrices = abeles.matrices(self.wvls_[i_target])
				for i_layer in range(self.nb_back_layers):
					if isinstance(self.back_thickness[i_layer], list):
						for i_sublayer in range(len(self.back_thickness[i_layer])):
							sublayer_n = self.N[i_target][self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
							temp_matrices.set_matrices(sublayer_n, self.back_thickness[i_layer][i_sublayer], self.sin2_theta_0[i_target])
							self.matrices_back[i_target].multiply_matrices(temp_matrices)
					else:
						if self.materials[self.back_layers[i_layer]].is_mixture():
							if self.back_index[i_layer] == self.n_min[self.back_layers[i_layer]]:
								N = self.N_min[i_target][self.back_layers[i_layer]].get_N_mixture()
							elif self.back_index[i_layer] == self.n_max[self.back_layers[i_layer]]:
								N = self.N_max[i_target][self.back_layers[i_layer]].get_N_mixture()
							else:
								self.N[i_target][self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
								N = self.N[i_target][self.back_layers[i_layer]].get_N_mixture()
						else:
							N = self.N[i_target][self.back_layers[i_layer]]
						temp_matrices.set_matrices(N, self.back_thickness[i_layer], self.sin2_theta_0[i_target])
						self.matrices_back[i_target].multiply_matrices(temp_matrices)
				
				# Calculate r and t of the backside.
				self.r_and_t_back[i_target].calculate_r_and_t_reverse(self.matrices_back[i_target], self.N[i_target][self.back_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
				if self.direction[i_target] == BACKWARD:
					self.r_and_t_back_reverse[i_target].calculate_r_and_t(self.matrices_back[i_target], self.N[i_target][self.back_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
				
				# Calculate R and/or T of the backside.
				if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.R_back[i_target].calculate_R(self.r_and_t_back[i_target], polarization)
						if self.direction[i_target] == BACKWARD:
							self.T_back[i_target].calculate_T(self.r_and_t_back[i_target], self.N[i_target][self.substrate], self.N[i_target][self.back_medium], self.sin2_theta_0[i_target], polarization)
							self.R_back_reverse[i_target].calculate_R(self.r_and_t_back_reverse[i_target], polarization)
							self.T_back_reverse[i_target].calculate_T(self.r_and_t_back_reverse[i_target], self.N[i_target][self.back_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
					elif kind in targets.TRANSMISSION_TARGETS:
						self.R_back[i_target].calculate_R(self.r_and_t_back[i_target], polarization)
						if self.direction[i_target] == FORWARD:
							self.T_back[i_target].calculate_T(self.r_and_t_back[i_target], self.N[i_target][self.substrate], self.N[i_target][self.back_medium], self.sin2_theta_0[i_target], polarization)
						else:
							self.T_back_reverse[i_target].calculate_T(self.r_and_t_back[i_target], self.N[i_target][self.substrate], self.N[i_target][self.back_medium], self.sin2_theta_0[i_target], polarization)
					else:
						self.T_back[i_target].calculate_T(self.r_and_t_back[i_target], self.N[i_target][self.substrate], self.N[i_target][self.back_medium], self.sin2_theta_0[i_target], polarization)
						self.R_back[i_target].calculate_R(self.r_and_t_back[i_target], polarization)
						if self.direction[i_target] == BACKWARD:
							self.R_back_reverse[i_target].calculate_R(self.r_and_t_back_reverse[i_target], polarization)
							self.T_back_reverse[i_target].calculate_T(self.r_and_t_back_reverse[i_target], self.N[i_target][self.back_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
		
		# Finally, to feed the Levenberg-Marquardt algorithm, we need lists
		# of:
		#   - all calculated values;
		#   - for every variable parameter:
		#     - all derivatives;
		#   - all target values;
		#   - all tolerances;
		#   - all inequalities.
		
		# First, calculate the total nb of values and, at the same time
		# determine where each target begins in the list of all target
		# values; self.nb_wvls is not used since for derived targets, the
		# number of targets value might be different than the number of
		# wavelengths.
		self.total_nb_of_target_values = 0
		self.nb_target_values = [0]*self.nb_targets
		self.target_starting_position = [0]*self.nb_targets
		for i_target in range(self.nb_targets):
			self.target_starting_position[i_target] = self.total_nb_of_target_values
			self.nb_target_values[i_target] = len(self.target_values[i_target])
			self.total_nb_of_target_values += self.nb_target_values[i_target]
		
		# Create the lists.
		self.all_calculated_values = [0.0]*self.total_nb_of_target_values
		self.all_derivatives = [[0.0]*self.total_nb_of_target_values for i_parameter in range(self.nb_parameters)]
		self.all_target_values = [0.0]*self.total_nb_of_target_values
		self.all_tolerances = [0.0]*self.total_nb_of_target_values
		self.all_inequalities = [0]*self.total_nb_of_target_values		
		
		# And fill the target and tolerance lists with their values.
		for i_target in range(self.nb_targets):
			start_position = self.target_starting_position[i_target]
			end_position = start_position + self.nb_target_values[i_target]
			self.all_target_values[start_position:end_position] = self.target_values[i_target]
			self.all_tolerances[start_position:end_position] = self.tolerances[i_target]
			self.all_inequalities[start_position:end_position] = [self.inequalities[i_target]]*len(self.target_values[i_target])
		
		# Finally, create a Levenberg-Marquardt optimization object and
		# provide it with fit parameters. During preparation, it will
		# calculate the values for a first time.
		self.optimizer = Levenberg_Marquardt.Levenberg_Marquardt(self.calculate_values, self.calculate_derivatives, self.parameter_values[:], self.all_target_values, self.all_tolerances)
 		self.optimizer.set_stop_criteria(self.min_gradient, self.acceptable_chi_2, self.min_chi_2_change)
		self.optimizer.set_limits(self.parameter_min, self.parameter_max)
		self.optimizer.set_inequalities(self.all_inequalities)
		self.optimizer.prepare()
 		self.status = Levenberg_Marquardt.IMPROVING
 		self.chi_2 = self.optimizer.get_chi_2()
	
	
	######################################################################
	#                                                                    #
	# get_shortest_wavelength                                            #
	#                                                                    #
	######################################################################
	def get_shortest_wavelength(self):
		"""Get the shortest wavelength used by targets
		
		This method takes no argument and returns the shortest wavelength
		used by the targets. It is useful in the needle and step method to
		determine the spacing between needles or steps. It must be called
		after the prepare method."""
		
		return min(min(wvls) for wvls in self.wvls)
	
	
	######################################################################
	#                                                                    #
	# set_min_thickness                                                  #
	#                                                                    #
	######################################################################
	def set_min_thickness(self, min_thickness = 0.0):
		"""Set the minimum thickness
		
		This method takes an optional argument:
		  min_thickness      (optional) the minimal thickness of the
		                     layers, the default value is 0;
		
		The layers with a thickness smaller than the minimum thickness can
		be removed using remove_thin_layers."""
		
		self.min_thickness = min_thickness
	
	
	######################################################################
	#                                                                    #
	# get_min_thickness                                                  #
	#                                                                    #
	######################################################################
	def get_min_thickness(self):
		"""Get the minimum thickness
		
		This method returns the minimal thickness of the layers."""
		
		return self.min_thickness
	
	
	######################################################################
	#                                                                    #
	# set_min_delta_n                                                    #
	#                                                                    #
	######################################################################
	def set_min_delta_n(self, min_delta_n = 0.0):
		"""Set the minimum delta n
		
		This method takes an optional argument:
		  delta_n            (optional) the minimal index difference
		                     between two adjacent layers, the default value
		                     is 0;
		
		Adjacent layers with a index difference smaller than the minimum
		index difference are merged when remove_thin_layers is called."""
		
		self.min_delta_n = min_delta_n
	
	
	######################################################################
	#                                                                    #
	# get_min_delta_n                                                    #
	#                                                                    #
	######################################################################
	def get_min_delta_n(self):
		"""Get the minimum delta n
		
		This method return the minimal index difference between two
		adjacent layers"""
		
		return self.min_delta_n
	
	
	######################################################################
	#                                                                    #
	# calculate_values                                                   #
	#                                                                    #
	######################################################################
	def calculate_values(self, parameter_values = None):
		"""Calculate the value of the optimized properties
		
		This method takes an optional argument:
		  parameter_values   (optional) the values of the parameters of the
		                     filter.
		
		By default, the parameters kept in the instance attributes are
		used."""
 		
 		# Change the parameter values.
 		if parameter_values and parameter_values != self.parameter_values:
			self.parameter_values[:] = parameter_values
			
	 		for i_parameter in range(self.nb_parameters):
				parameter_kind, layer_nb = self.parameters[i_parameter]
				if parameter_kind == THICKNESS:
					self.front_thickness[layer_nb] = self.parameter_values[i_parameter]
				elif parameter_kind == INDEX:
					self.front_index[layer_nb] = self.parameter_values[i_parameter]
					if self.preserve_OT[layer_nb]:
						self.front_thickness[layer_nb] = self.OT[layer_nb] / self.front_index[layer_nb]
				for i_target in range(self.nb_targets):
					if self.materials[self.front_layers[layer_nb]].is_mixture():
						if self.front_index[layer_nb] == self.n_min[self.front_layers[layer_nb]]:
							N = self.N_min[i_target][self.front_layers[layer_nb]].get_N_mixture()
						elif self.front_index[layer_nb] == self.n_max[self.front_layers[layer_nb]]:
							N = self.N_max[i_target][self.front_layers[layer_nb]].get_N_mixture()
						else:
							self.N[i_target][self.front_layers[layer_nb]].set_N_mixture(self.front_index[layer_nb], self.center_wavelength)
							N = self.N[i_target][self.front_layers[layer_nb]].get_N_mixture()
					else:
						N = self.N[i_target][self.front_layers[layer_nb]]
					self.pre_and_post_matrices[i_target].set_pre_and_post_matrices(layer_nb, N, self.front_thickness[layer_nb], self.sin2_theta_0[i_target])
				
				# Give other threads a chance...
				time.sleep(0)
		
		for i_target in range(self.nb_targets):
			target= self.targets[i_target]
			kind = target.get_kind()
			polarization = target.get_polarization()
			
			# Multiply all the matrices in the front stack and generate
			# pre and post matrices. This does modify self.matrices_front.
			self.pre_and_post_matrices[i_target].multiply_pre_and_post_matrices()
			
			# Give other threads a chance...
			time.sleep(0)
			
			# Calculate amplitude reflexion and transmission.
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
				if self.direction[i_target] == FORWARD:
					self.r_and_t_front[i_target].calculate_r_and_t(self.matrices_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
					if self.consider_backside[i_target]:
						self.r_and_t_front_reverse[i_target].calculate_r_and_t_reverse(self.matrices_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
				else:
					self.r_and_t_front_reverse[i_target].calculate_r_and_t_reverse(self.matrices_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
			
			# Give other threads a chance...
			time.sleep(0)
			
			# Calculate the values.
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
				if kind in targets.REFLECTION_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.R_front[i_target].calculate_R(self.r_and_t_front[i_target], polarization)
						if self.consider_backside[i_target]:
							self.T_front[i_target].calculate_T(self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
							self.T_front_reverse[i_target].calculate_T(self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
							self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
							self.R[i_target].calculate_R_with_backside(self.T_front[i_target], self.R_front[i_target], self.T_front_reverse[i_target], self.R_front_reverse[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					else:
						self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
						if self.consider_backside[i_target]:
							self.R[i_target].calculate_R_with_backside(self.T_back_reverse[i_target], self.R_back_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.R_front_reverse[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
				elif kind in targets.TRANSMISSION_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.T_front[i_target].calculate_T(self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
							self.T[i_target].calculate_T_with_backside(self.T_front[i_target], self.R_front_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					else:
						self.T_front_reverse[i_target].calculate_T(self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
							self.T[i_target].calculate_T_with_backside(self.T_back_reverse[i_target], self.R_back[i_target], self.T_front_reverse[i_target], self.R_front_reverse[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
				else:
					if self.direction[i_target] == FORWARD:
						self.R_front[i_target].calculate_R(self.r_and_t_front[i_target], polarization)
						self.T_front[i_target].calculate_T(self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
						if self.consider_backside[i_target]:
							self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
							self.T_front_reverse[i_target].calculate_T(self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
							self.R[i_target].calculate_R_with_backside(self.T_front[i_target], self.R_front[i_target], self.T_front_reverse[i_target], self.R_front_reverse[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
							self.T[i_target].calculate_T_with_backside(self.T_front[i_target], self.R_front_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					else:
						self.R_front_reverse[i_target].calculate_R(self.r_and_t_front_reverse[i_target], polarization)
						self.T_front_reverse[i_target].calculate_T(self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
						if self.consider_backside[i_target]:
							self.R[i_target].calculate_R_with_backside(self.T_back_reverse[i_target], self.R_back_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.R_front_reverse[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
							self.T[i_target].calculate_T_with_backside(self.T_back_reverse[i_target], self.R_back[i_target], self.T_front_reverse[i_target], self.R_front_reverse[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					self.A[i_target].calculate_A(self.R[i_target], self.T[i_target])
				
				# Give other threads a chance...
				time.sleep(0)
				
				# Calculate derived values.
				if kind == targets.R_COLOR_TARGET:
					self.derived_values[i_target].calculate_color(self.wvls[i_target], self.R[i_target])
				elif kind == targets.T_COLOR_TARGET:
					self.derived_values[i_target].calculate_color(self.wvls[i_target], self.T[i_target])
			
			elif kind in targets.DISPERSIVE_TARGETS:
				if kind in targets.REFLECTION_TARGETS:
					self.phi_r[i_target].calculate_r_phase(self.matrices_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
				else:
					self.phi_t[i_target].calculate_t_phase(self.matrices_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
				
				# Give other threads a chance...
				time.sleep(0)
				
				# Calculate derived values.
				if kind in targets.GD_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.derived_values[i_target].calculate_GD(self.phi_r[i_target])
					else:
						self.derived_values[i_target].calculate_GD(self.phi_t[i_target])
				elif kind in targets.GDD_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.derived_values[i_target].calculate_GDD(self.phi_r[i_target])
					else:
						self.derived_values[i_target].calculate_GDD(self.phi_t[i_target])
			
			# Give other threads a chance...
			time.sleep(0)
			
			# Put the values for this target in a single list of all
			# calculated values that is used by the Levenberg-Marquardt
			# algorithm.
			if kind in targets.PHOTOMETRIC_TARGETS:
				if kind in targets.REFLECTION_TARGETS:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.R[i_target]
				elif kind in targets.TRANSMISSION_TARGETS:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.T[i_target]
				else:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.A[i_target]
			elif kind in targets.PHASE_TARGETS:
				if kind in targets.REFLECTION_TARGETS:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = (phi*one_hundred_eighty_over_pi for phi in self.phi_r[i_target])
				else:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = (phi*one_hundred_eighty_over_pi for phi in self.phi_t[i_target])
			elif kind in targets.GD_TARGETS or kind in targets.GDD_TARGETS:
				if kind in targets.DISCRETE_TARGETS:
					self.all_calculated_values[self.target_starting_position[i_target]] = self.derived_values[i_target][1]
				else:
					self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.derived_values[i_target]
			elif kind in targets.COLOR_TARGETS:
				self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+3] = self.derived_values[i_target].color(target.get_color_space())
			
			# Give other threads a chance...
			time.sleep(0)
		
		return self.all_calculated_values
	
	
	######################################################################
	#                                                                    #
	# calculate_derivatives                                              #
	#                                                                    #
	######################################################################
	def calculate_derivatives(self, parameter_values = None):
		"""Calculate the derivatives of the optimized properties
		
		This method takes an optional argument:
		  parameter_values   (optional) the values of the parameters of the
		                     filter.
		
		By default, the parameters kept in the instance attributes are
		used."""
 		
 		# If parameters changed, recalculate values.
 		if parameter_values and parameter_values != self.parameter_values:
	 		self.calculate_values(parameter_values)
		
		# Calculate derivatives.
		for i_target in range(self.nb_targets):
			target = self.targets[i_target]
			kind = target.get_kind()
			polarization = target.get_polarization()
			
			# Calculate the psi matrices.
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
				if self.direction[i_target] == FORWARD:
					self.psi[i_target].calculate_psi_matrices(self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
					if self.consider_backside[i_target]:
						self.psi_reverse[i_target].calculate_psi_matrices_reverse(self.r_and_t_front_reverse[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
				else:
					self.psi_reverse[i_target].calculate_psi_matrices_reverse(self.r_and_t_front_reverse[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target])
			
			# Give other threads a chance...
			time.sleep(0)
			
			for i_parameter in range(self.nb_parameters):
				parameter_kind, layer_nb = self.parameters[i_parameter]
				
				# Get the index of the layer depending if it is a mixture or a
				# normal material.
				if self.materials[self.front_layers[layer_nb]].is_mixture():
					if self.front_index[layer_nb] == self.n_min[self.front_layers[layer_nb]]:
						N = self.N_min[i_target][self.front_layers[layer_nb]].get_N_mixture()
					elif self.front_index[layer_nb] == self.n_max[self.front_layers[layer_nb]]:
						N = self.N_max[i_target][self.front_layers[layer_nb]].get_N_mixture()
					else:
						self.N[i_target][self.front_layers[layer_nb]].set_N_mixture(self.front_index[layer_nb], self.center_wavelength)
						N = self.N[i_target][self.front_layers[layer_nb]].get_N_mixture()
				else:
					N = self.N[i_target][self.front_layers[layer_nb]]
				
				# Give other threads a chance...
				time.sleep(0)
				
				# Calculate the derivative of the layer matrices, and that
				# of the global matrices, depending on the kind of parameter.
				if parameter_kind == THICKNESS:
					self.dMi[i_target][i_parameter].set_dMi_thickness(N, self.front_thickness[layer_nb], self.sin2_theta_0[i_target])
				elif parameter_kind == INDEX:
					if self.front_index[layer_nb] == self.n_min[self.front_layers[layer_nb]]:
						dN = self.N_min[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					elif self.front_index[layer_nb] == self.n_max[self.front_layers[layer_nb]]:
						dN = self.N_max[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					else:
						self.N[i_target][self.front_layers[layer_nb]].set_dN_mixture(self.front_index[layer_nb], self.center_wavelength)
						dN = self.N[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					if self.preserve_OT[layer_nb]:
						self.N_center_wvl[self.front_layers[layer_nb]].set_N_mixture(self.front_index[layer_nb], self.center_wavelength)
						N_center_wvl = self.N_center_wvl[self.front_layers[layer_nb]].get_N_mixture()
						self.dMi[i_target][i_parameter].set_dMi_index_with_constant_OT(N, dN, self.front_thickness[layer_nb], self.sin2_theta_0[i_target], N_center_wvl, self.sin2_theta_0_center_wvl)
					else:
						self.dMi[i_target][i_parameter].set_dMi_index(N, dN, self.front_thickness[layer_nb], self.sin2_theta_0[i_target])
				self.dM[i_target][i_parameter].calculate_dM(self.dMi[i_target][i_parameter], self.pre_and_post_matrices[i_target], layer_nb)
				
				# Give other threads a chance...
				time.sleep(0)
				
				# Calculate the derivative of amplitude reflection and transmission.
				if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.dr_and_dt_front[i_target][i_parameter].calculate_dr_and_dt(self.dM[i_target][i_parameter], self.psi[i_target])
						if self.consider_backside[i_target]:
							self.dr_and_dt_front_reverse[i_target][i_parameter].calculate_dr_and_dt_reverse(self.dM[i_target][i_parameter], self.psi_reverse[i_target])
					else:
						self.dr_and_dt_front_reverse[i_target][i_parameter].calculate_dr_and_dt_reverse(self.dM[i_target][i_parameter], self.psi_reverse[i_target])
					
					# Give other threads a chance...
					time.sleep(0)
					
					# Calculate the derivative of the values.
					if kind in targets.REFLECTION_TARGETS:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target][i_parameter].calculate_dR(self.dr_and_dt_front[i_target][i_parameter], self.r_and_t_front[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dT_front[i_target][i_parameter].calculate_dT(self.dr_and_dt_front[i_target][i_parameter], self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
								self.dT_front_reverse[i_target][i_parameter].calculate_dT(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
								self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
								self.dR[i_target][i_parameter].calculate_dR_with_backside(self.T_front[i_target], self.dT_front[i_target][i_parameter], self.dR_front[i_target][i_parameter], self.T_front_reverse[i_target], self.dT_front_reverse[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
						else:
							self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dR[i_target][i_parameter].calculate_dR_with_backside_2(self.T_back_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					elif kind in targets.TRANSMISSION_TARGETS:
						if self.direction[i_target] == FORWARD:
							self.dT_front[i_target][i_parameter].calculate_dT(self.dr_and_dt_front[i_target][i_parameter], self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
								self.dT[i_target][i_parameter].calculate_dT_with_backside(self.T_front[i_target], self.dT_front[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.T_back[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
						else:
							self.dT_front_reverse[i_target][i_parameter].calculate_dT(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
								self.dT[i_target][i_parameter].calculate_dT_with_backside_2(self.T_back_reverse[i_target], self.R_back[i_target], self.T_front_reverse[i_target], self.dT_front_reverse[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
					else:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target][i_parameter].calculate_dR(self.dr_and_dt_front[i_target][i_parameter], self.r_and_t_front[i_target], polarization)
							self.dT_front[i_target][i_parameter].calculate_dT(self.dr_and_dt_front[i_target][i_parameter], self.r_and_t_front[i_target], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
								self.dT_front_reverse[i_target][i_parameter].calculate_dT(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
								self.dR[i_target][i_parameter].calculate_dR_with_backside(self.T_front[i_target], self.dT_front[i_target][i_parameter], self.dR_front[i_target][i_parameter], self.T_front_reverse[i_target], self.dT_front_reverse[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
								self.dT[i_target][i_parameter].calculate_dT_with_backside(self.T_front[i_target], self.dT_front[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.T_back[i_target], self.R_back[i_target], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
						else:
							self.dR_front_reverse[i_target][i_parameter].calculate_dR(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], polarization)
							self.dT_front_reverse[i_target][i_parameter].calculate_dT(self.dr_and_dt_front_reverse[i_target][i_parameter], self.r_and_t_front_reverse[i_target], self.N[i_target][self.substrate], self.N[i_target][self.front_medium], self.sin2_theta_0[i_target], polarization)
							if self.consider_backside[i_target]:
								self.dR[i_target][i_parameter].calculate_dR_with_backside_2(self.T_back_reverse[i_target], self.T_back[i_target], self.R_back[i_target], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
								self.dT[i_target][i_parameter].calculate_dT_with_backside_2(self.T_back_reverse[i_target], self.R_back[i_target], self.T_front_reverse[i_target], self.dT_front_reverse[i_target][i_parameter], self.R_front_reverse[i_target], self.dR_front_reverse[i_target][i_parameter], self.N[i_target][self.substrate], self.substrate_thickness, self.sin2_theta_0[i_target])
						self.dA[i_target][i_parameter].calculate_dA(self.dR[i_target][i_parameter], self.dT[i_target][i_parameter])
					
					# Give other threads a chance...
					time.sleep(0)
					
					# Calculate the derivative of the derived values.
					if kind == targets.R_COLOR_TARGET:
						self.dderived_values[i_target][i_parameter].calculate_color_derivative(self.wvls[i_target], self.R[i_target], self.dR[i_target][i_parameter])
					elif kind == targets.T_COLOR_TARGET:
						self.dderived_values[i_target][i_parameter].calculate_color_derivative(self.wvls[i_target], self.T[i_target], self.dT[i_target][i_parameter])
				
				elif kind in targets.DISPERSIVE_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.dphi_r[i_target][i_parameter].calculate_dr_phase(self.matrices_front[i_target], self.dM[i_target][i_parameter], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
					else:
						self.dphi_t[i_target][i_parameter].calculate_dt_phase(self.matrices_front[i_target], self.dM[i_target][i_parameter], self.N[i_target][self.front_medium], self.N[i_target][self.substrate], self.sin2_theta_0[i_target], polarization)
					
					# Give other threads a chance...
					time.sleep(0)
					
					# Calculate the derivative of the derived values.
					if kind in targets.GD_TARGETS:
						if kind in targets.REFLECTION_TARGETS:
							self.dderived_values[i_target][i_parameter].calculate_dGD(self.dphi_r[i_target][i_parameter])
						else:
							self.dderived_values[i_target][i_parameter].calculate_dGD(self.dphi_t[i_target][i_parameter])
					elif kind in targets.GDD_TARGETS:
						if kind in targets.REFLECTION_TARGETS:
							self.dderived_values[i_target][i_parameter].calculate_dGDD(self.dphi_r[i_target][i_parameter])
						else:
							self.dderived_values[i_target][i_parameter].calculate_dGDD(self.dphi_t[i_target][i_parameter])
				
				# Give other threads a chance...
				time.sleep(0)
				
				# Put the derivatives for this target in a single list of all
				# derivatives that is used by the Levenberg-Marquardt
				# algorithm.
				if kind in targets.PHOTOMETRIC_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.dR[i_target][i_parameter]
					elif kind in targets.TRANSMISSION_TARGETS:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.dT[i_target][i_parameter]
					else:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.dA[i_target][i_parameter]
				elif kind in targets.PHASE_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = (dphi*one_hundred_eighty_over_pi for dphi in self.dphi_r[i_target][i_parameter])
					else:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = (dphi*one_hundred_eighty_over_pi for dphi in self.dphi_t[i_target][i_parameter])
				elif kind in targets.GD_TARGETS or kind in targets.GDD_TARGETS:
					if kind in targets.DISCRETE_TARGETS:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]] = self.dderived_values[i_target][i_parameter][1]
					else:
						self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]] = self.dderived_values[i_target][i_parameter]
				elif kind in targets.COLOR_TARGETS:
					self.all_derivatives[i_parameter][self.target_starting_position[i_target]:self.target_starting_position[i_target]+3] = self.dderived_values[i_target][i_parameter].dcolor(target.get_color_space())
				
				# Give other threads a chance...
				time.sleep(0)
		
		return self.all_derivatives
	
	
	######################################################################
	#                                                                    #
	# remove_thin_layers_                                                #
	#                                                                    #
	######################################################################
	def remove_thin_layers_(self):
		"""Remove thin layer
		
		Remove layers that are thinner than the mimimal thickness and merge
		layer that have an index difference smaller than the minimal index
		difference. This method takes no argument and return a boolean
		indicating if layers were removed.
		
		This method is the one that actually does the work."""
		
		old_nb_front_layers = self.nb_front_layers
		
		# Remove layers which are too thin, starting at the end of
		# the list to consider every layers and not go behond the length
		# of the shortened list.
		for i_layer in range(self.nb_front_layers-1, 0-1, -1):
			if self.front_thickness[i_layer] < self.min_thickness or self.front_thickness[i_layer] == 0.0:
				# Try to distribute the optical thickness of the layer on
				# adjacent layers.
				optical_thickness = self.front_thickness[i_layer]*self.front_index[i_layer]
				can_add_to_previous_layer = i_layer > 0 and not isinstance(self.front_thickness[i_layer-1], list) 
				can_add_to_next_layer = i_layer < self.nb_front_layers-1 and not isinstance(self.front_thickness[i_layer+1], list) 
				if can_add_to_previous_layer and can_add_to_next_layer:
					self.front_thickness[i_layer-1] += 0.5*optical_thickness/self.front_index[i_layer-1]
					self.front_thickness[i_layer+1] += 0.5*optical_thickness/self.front_index[i_layer+1]
				elif can_add_to_previous_layer:
					self.front_thickness[i_layer-1] += optical_thickness/self.front_index[i_layer-1]
				elif can_add_to_next_layer:
					self.front_thickness[i_layer+1] += optical_thickness/self.front_index[i_layer+1]
				
				# Remove layer.
				self.front_layers.pop(i_layer)
				self.front_layer_descriptions.pop(i_layer)
				self.front_thickness.pop(i_layer)
				self.front_index.pop(i_layer)
				self.front_step_profiles.pop(i_layer)
				self.refine_thickness.pop(i_layer)
				self.refine_index.pop(i_layer)
				self.preserve_OT.pop(i_layer)
				self.add_needles_in_layer.pop(i_layer)
				self.add_steps_in_layer.pop(i_layer)
				self.nb_front_layers -= 1
		
		# Merge identical layers.
		for i_layer in range(self.nb_front_layers-1, 1-1, -1):
			if self.front_layers[i_layer] == self.front_layers[i_layer-1]:
				# If the layer is graded, extend the lists.
				if isinstance(self.front_thickness[i_layer], list):
					self.front_layers.pop(i_layer)
					self.front_layer_descriptions[i_layer-1] = []
					self.front_layer_descriptions.pop(i_layer)
					self.front_thickness[i_layer-1] += self.front_thickness[i_layer]
					self.front_thickness.pop(i_layer)
					self.front_index[i_layer-1] += self.front_index[i_layer]
					self.front_index.pop(i_layer)
					self.front_step_profiles[i_layer-1] += self.front_step_profiles[i_layer]
					self.front_step_profiles.pop(i_layer)
					self.refine_thickness.pop(i_layer)
					self.refine_index.pop(i_layer)
					self.preserve_OT.pop(i_layer)
					self.add_needles_in_layer.pop(i_layer)
					self.add_steps_in_layer.pop(i_layer)
					self.nb_front_layers -= 1
				# If the layer is not a mixture, it is sure that it is
				# identical. If it is a mixture, we must verify that the index
				# of both layers are identical.
				elif not self.materials[self.front_layers[i_layer]].is_mixture() or abs(self.front_index[i_layer] - self.front_index[i_layer-1]) < self.min_delta_n or self.front_index[i_layer] - self.front_index[i_layer-1] == 0.0:
					self.front_layers.pop(i_layer)
					self.front_layer_descriptions[i_layer-1] = []
					self.front_layer_descriptions.pop(i_layer)
					self.front_thickness[i_layer-1] += self.front_thickness[i_layer]
					self.front_thickness.pop(i_layer)
					self.front_index.pop(i_layer)
					self.front_step_profiles.pop(i_layer)
					self.refine_thickness.pop(i_layer)
					self.refine_index.pop(i_layer)
					self.preserve_OT.pop(i_layer)
					self.add_needles_in_layer.pop(i_layer)
					self.add_steps_in_layer.pop(i_layer)
					self.nb_front_layers -= 1
		
		if self.nb_front_layers == old_nb_front_layers:
			return False
		
		old_nb_parameters = self.nb_parameters
		
		# Rebuild the list of parameters
		self.nb_parameters = 0
		self.parameters = []
		self.parameter_values = []
		self.parameter_min = []
		self.parameter_max = []
		for i_layer in range(len(self.front_layers)):
			if self.refine_thickness[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((THICKNESS, i_layer))
				self.parameter_values.append(self.front_thickness[i_layer])
				self.parameter_min.append(0.0)
				self.parameter_max.append(Levenberg_Marquardt.INFINITY)
			if self.refine_index[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((INDEX, i_layer))
				self.parameter_values.append(self.front_index[i_layer])
				min_index, max_index = self.materials[self.front_layers[i_layer]].get_index_range(self.center_wavelength)
				self.parameter_min.append(min_index)
				self.parameter_max.append(max_index)
		self.old_parameter_values = self.parameter_values[:]
		
		# Create new objects for new number of parameters and delete
		# superfluous objects.
		for i_target in range(self.nb_targets):
			# Create a new object for pre and post matrices
			self.pre_and_post_matrices[i_target] = abeles.pre_and_post_matrices(self.wvls_[i_target], self.nb_front_layers)
			self.matrices_front[i_target] = self.pre_and_post_matrices[i_target].get_global_matrices()
			
			# Shorten lists.
			del self.dMi[i_target][self.nb_parameters:old_nb_parameters]
			del self.dM[i_target][self.nb_parameters:old_nb_parameters]
			del self.dr_and_dt_front[i_target][self.nb_parameters:old_nb_parameters]
			del self.dr_and_dt_front_reverse[i_target][self.nb_parameters:old_nb_parameters]
			del self.dR_front[i_target][self.nb_parameters:old_nb_parameters]
			del self.dT_front[i_target][self.nb_parameters:old_nb_parameters]
			del self.dR_front_reverse[i_target][self.nb_parameters:old_nb_parameters]
			del self.dT_front_reverse[i_target][self.nb_parameters:old_nb_parameters]
			del self.dR[i_target][self.nb_parameters:old_nb_parameters]
			del self.dT[i_target][self.nb_parameters:old_nb_parameters]
			del self.dA[i_target][self.nb_parameters:old_nb_parameters]
			del self.dphi_r[i_target][self.nb_parameters:old_nb_parameters]
			del self.dphi_t[i_target][self.nb_parameters:old_nb_parameters]
			del self.dderived_values[i_target][self.nb_parameters:old_nb_parameters]
		
		# Shorten the list of derivatives.
		del self.all_derivatives[self.nb_parameters:old_nb_parameters]
		
		# Reset values
		for i_target in range(self.nb_targets):
			for i_layer in range(self.nb_front_layers):
				if isinstance(self.front_thickness[i_layer], list):
					layer_matrices = self.pre_and_post_matrices[i_target][i_layer]
					layer_matrices.set_matrices_unity()
					temp_matrices = abeles.matrices(self.wvls_[i_target])
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						sublayer_n = self.N[i_target][self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(sublayer_n, self.front_thickness[i_layer][i_sublayer], self.sin2_theta_0[i_target])
						layer_matrices.multiply_matrices(temp_matrices)
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						if self.front_index[i_layer] == self.n_min[self.front_layers[i_layer]]:
							N = self.N_min[i_target][self.front_layers[i_layer]].get_N_mixture()
						elif self.front_index[i_layer] == self.n_max[self.front_layers[i_layer]]:
							N = self.N_max[i_target][self.front_layers[i_layer]].get_N_mixture()
						else:
							self.N[i_target][self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
							N = self.N[i_target][self.front_layers[i_layer]].get_N_mixture()
					else:
						N = self.N[i_target][self.front_layers[i_layer]]
					self.pre_and_post_matrices[i_target].set_pre_and_post_matrices(i_layer, N, self.front_thickness[i_layer], self.sin2_theta_0[i_target])
		
		self.just_removed_thin_layers = True
		
		# Create a new instance of the Levenberg-Marquardt optimization
		# class.
		self.optimizer = Levenberg_Marquardt.Levenberg_Marquardt(self.calculate_values, self.calculate_derivatives, self.parameter_values[:], self.all_target_values, self.all_tolerances)
 		self.optimizer.set_stop_criteria(self.min_gradient, self.acceptable_chi_2, self.min_chi_2_change)
		self.optimizer.set_limits(self.parameter_min, self.parameter_max)
		self.optimizer.set_inequalities(self.all_inequalities)
		self.optimizer.prepare()
 		self.status = Levenberg_Marquardt.IMPROVING
 		self.chi_2 = self.optimizer.get_chi_2()
		
		# Reset the number of iterations.
		self.reset_iterations()
		
		# Remember that the filter must be fully recreated.
		self.need_to_reset_filter = True
		
		return True
	
	
	######################################################################
	#                                                                    #
	# remove_thin_layers                                                 #
	#                                                                    #
	######################################################################
	def remove_thin_layers(self):
		"""Remove thin layer
		
		Remove layers that are thinner than the mimimal thickness and merge
		layer that have an index difference smaller than the minimal index
		difference.
		
		This method calls remove_thin_layers_ and updates the user
		interface."""
		
		self.working = True
		self.can_stop = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		self.remove_thin_layers_()
		
		self.working = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
	
	
	######################################################################
	#                                                                    #
	# add_parameters                                                     #
	#                                                                    #
	######################################################################
	def add_parameters(self):
		"""Add parameters
		
		Rebuild the instance variables after the number of parameters has
		been increased.
		
		This method is not used during refinement, but is implemented here
		to be used by the needle and step methods."""
		
		old_nb_parameters = self.nb_parameters
		
		# Rebuild the list of parameters
		self.nb_parameters = 0
		self.parameters = []
		self.parameter_values = []
		self.parameter_min = []
		self.parameter_max = []
		for i_layer in range(len(self.front_layers)):
			if self.refine_thickness[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((THICKNESS, i_layer))
				self.parameter_values.append(self.front_thickness[i_layer])
				self.parameter_min.append(0.0)
				self.parameter_max.append(Levenberg_Marquardt.INFINITY)
			if self.refine_index[i_layer]:
				self.nb_parameters += 1
				self.parameters.append((INDEX, i_layer))
				self.parameter_values.append(self.front_index[i_layer])
				min_index, max_index = self.materials[self.front_layers[i_layer]].get_index_range(self.center_wavelength)
				self.parameter_min.append(min_index)
				self.parameter_max.append(max_index)
		self.old_parameter_values = self.parameters[:]
		
		# Give other threads a chance...
		time.sleep(0)
		
		# Create new objects for the new parameters.
		for i_target in range(self.nb_targets):
			target = self.targets[i_target]
			kind = target.get_kind()
			
			# Make a new object of pre and post matrices.
			self.pre_and_post_matrices[i_target] = abeles.pre_and_post_matrices(self.wvls_[i_target], self.nb_front_layers)
			self.matrices_front[i_target] = self.pre_and_post_matrices[i_target].get_global_matrices()
			
			for i_parameter in range(old_nb_parameters, self.nb_parameters):
				
				self.dMi[i_target].append(abeles.dM(self.wvls_[i_target]))
				self.dM[i_target].append(abeles.dM(self.wvls_[i_target]))
				
				if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
					if self.direction[i_target] == FORWARD:
						self.dr_and_dt_front[i_target].append(abeles.dr_and_dt(self.wvls_[i_target]))
						if self.consider_backside[i_target]:
							self.dr_and_dt_front_reverse[i_target].append(abeles.dr_and_dt(self.wvls_[i_target]))
					else:
						self.dr_and_dt_front_reverse[i_target].append(abeles.dr_and_dt(self.wvls_[i_target]))
					
					if kind in targets.REFLECTION_TARGETS:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target].append(abeles.dR(self.wvls_[i_target]))
							if self.consider_backside[i_target]:
								self.dT_front[i_target].append(abeles.dT(self.wvls_[i_target]))
								self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT_front_reverse[i_target].append(abeles.dT(self.wvls_[i_target]))
								self.dR[i_target].append(abeles.dR(self.wvls_[i_target]))
							else:
								self.dT_front[i_target].append(None)
								self.dR_front_reverse[i_target].append(None)
								self.dT_front_reverse[i_target].append(None)
								# When the backside is not considered, the derivative of
								# the reflection of the sample is simply that of the front
								# side.
								self.dR[i_target].append(self.dR_front[i_target][i_parameter])
						else:
							self.dR_front[i_target].append(None)
							self.dT_front[i_target].append(None)
							self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
							self.dT_front_reverse[i_target].append(None)
							if self.consider_backside[i_target]:
								self.dR[i_target].append(abeles.dR(self.wvls_[i_target]))
							else:
								# When the backside is not considered, the derivative of
								# the reflection of the sample is simply that of the front
								# side.
								self.dR[i_target].append(self.dR_front_reverse[i_target][i_parameter])
						self.dT[i_target].append(None)
						self.dA[i_target].append(None)
					
					elif kind in targets.TRANSMISSION_TARGETS:
						self.dR_front[i_target].append(None)
						self.dR[i_target].append(None)
						if self.direction[i_target] == FORWARD:
							self.dT_front[i_target].append(abeles.dT(self.wvls_[i_target]))
							self.dT_front_reverse[i_target].append(None)
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT[i_target].append(abeles.dT(self.wvls_[i_target]))
							else:
								self.dR_front_reverse[i_target].append(None)
								# When the backside is not considered, the derivative of
								# the transmission of the sample is simply that of the
								# front side.
								self.dT[i_target].append(self.dT_front[i_target][i_parameter])
						else:
							self.dT_front[i_target].append(None)
							self.dT_front_reverse[i_target].append(abeles.dT(self.wvls_[i_target]))
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT[i_target].append(abeles.dT(self.wvls_[i_target]))
							else:
								self.dR_front_reverse[i_target].append(None)
								# When the backside is not considered, the derivative of
								# the transmission of the sample is simply that of the
								# front side.
								self.dT[i_target].append(self.dT_front_reverse[i_target][i_parameter])
						self.dA[i_target].append(None)
					
					else:
						if self.direction[i_target] == FORWARD:
							self.dR_front[i_target].append(abeles.dR(self.wvls_[i_target]))
							self.dT_front[i_target].append(abeles.dT(self.wvls_[i_target]))
							if self.consider_backside[i_target]:
								self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT_front_reverse[i_target].append(abeles.dT(self.wvls_[i_target]))
								self.dR[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT[i_target].append(abeles.dT(self.wvls_[i_target]))
							else:
								self.dR_front_reverse[i_target].append(None)
								self.dT_front_reverse[i_target].append(None)
								# When the backside is not considered, the derivative of
								# the reflection and the transmission of the sample are
								# simply those of the front side.
								self.dR[i_target].append(self.dR_front[i_target])
								self.dT[i_target].append(self.dT_front[i_target])
						else:
							self.dR_front[i_target].append(None)
							self.dT_front[i_target].append(None)
							self.dR_front_reverse[i_target].append(abeles.dR(self.wvls_[i_target]))
							self.dT_front_reverse[i_target].append(abeles.dT(self.wvls_[i_target]))
							if self.consider_backside[i_target]:
								self.dR[i_target].append(abeles.dR(self.wvls_[i_target]))
								self.dT[i_target].append(abeles.dT(self.wvls_[i_target]))
							else:
								# When the backside is not considered, the derivative of
								# the reflection and the transmission of the sample are
								# simply those of the front side.
								self.dR[i_target].append(self.dR_front_reverse[i_target])
								self.dT[i_target].append(self.dT_front_reverse[i_target])
						self.dA[i_target].append(abeles.dA(self.wvls_[i_target]))
					
					if kind in targets.COLOR_TARGETS:
						self.dderived_values[i_target].append(color.color_derivative(self.derived_values[i_target]))
					else:
						self.dderived_values[i_target].append(None)
				
				elif kind in targets.DISPERSIVE_TARGETS:
					if kind in targets.REFLECTION_TARGETS:
						self.dphi_r[i_target].append(abeles.dphase(self.wvls_[i_target]))
					else:
						self.dphi_t[i_target].append(abeles.dphase(self.wvls_[i_target]))
					
					if kind in targets.GD_TARGETS:
						self.dderived_values[i_target].append(abeles.dGD(self.wvls_[i_target]))
					elif kind in targets.GDD_TARGETS:
						self.dderived_values[i_target].append(abeles.dGDD(self.wvls_[i_target]))
			
			# Give other threads a chance...
			time.sleep(0)
		
		# Add lists for the derivatives of the new parameters.
		for i_parameter in range(old_nb_parameters, self.nb_parameters):
			self.all_derivatives.append([0.0]*self.total_nb_of_target_values)
		
		# Reset values
		for i_target in range(self.nb_targets):
			for i_layer in range(self.nb_front_layers):
				if isinstance(self.front_thickness[i_layer], list):
					layer_matrices = self.pre_and_post_matrices[i_target][i_layer]
					layer_matrices.set_matrices_unity()
					temp_matrices = abeles.matrices(self.wvls_[i_target])
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						sublayer_n = self.N[i_target][self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(sublayer_n, self.front_thickness[i_layer][i_sublayer], self.sin2_theta_0[i_target])
						layer_matrices.multiply_matrices(temp_matrices)
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						if self.front_index[i_layer] == self.n_min[self.front_layers[i_layer]]:
							N = self.N_min[i_target][self.front_layers[i_layer]].get_N_mixture()
						elif self.front_index[i_layer] == self.n_max[self.front_layers[i_layer]]:
							N = self.N_max[i_target][self.front_layers[i_layer]].get_N_mixture()
						else:
							self.N[i_target][self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
							N = self.N[i_target][self.front_layers[i_layer]].get_N_mixture()
					else:
						N = self.N[i_target][self.front_layers[i_layer]]
					self.pre_and_post_matrices[i_target].set_pre_and_post_matrices(i_layer, N, self.front_thickness[i_layer], self.sin2_theta_0[i_target])
			
			# Give other threads a chance...
			time.sleep(0)
		
		# Create a new instance of the Levenberg-Marquardt optimization
		# class.
		self.optimizer = Levenberg_Marquardt.Levenberg_Marquardt(self.calculate_values, self.calculate_derivatives, self.parameter_values[:], self.all_target_values, self.all_tolerances)
 		self.optimizer.set_stop_criteria(self.min_gradient, self.acceptable_chi_2, self.min_chi_2_change)
		self.optimizer.set_limits(self.parameter_min, self.parameter_max)
		self.optimizer.set_inequalities(self.all_inequalities)
		self.optimizer.prepare()
 		self.status = Levenberg_Marquardt.IMPROVING
 		self.chi_2 = self.optimizer.get_chi_2()
		
		# Reset the number of iterations.
		self.reset_iterations()
		
		# Remember that the filter must be fully recreated.
		self.need_to_reset_filter = True
	
	
	######################################################################
	#                                                                    #
	# iterate_                                                           #
	#                                                                    #
	######################################################################
	def iterate_(self):
		"""Do one iteration"""
		
		# Execute one Levenberg-Marquardt iteration.
 		self.status = self.optimizer.iterate()
		
		# Get chi square.
 		self.chi_2 = self.optimizer.get_chi_2()
		
		self.iteration += 1
 		
 		# Stop if the solution is not improving.
 		if self.status != Levenberg_Marquardt.IMPROVING:
			self.stop_criteria_met = True
 		
 		# Verify if the maximum number of iterations has been reached (when
 		# specified).
 		if self.max_iterations and self.iteration >= self.max_iterations:
 			self.max_iterations_reached = True
		
		self.just_removed_thin_layers = False
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters
		
		This method returns the value of the parameters."""
		
		return self.parameters
	
	
	######################################################################
	#                                                                    #
	# get_target_values                                                  #
	#                                                                    #
	######################################################################
	def get_target_values(self):
		"""Get the value of the targets
		
		This method returns the value of the targets (wvls, values)."""
		
		return self.wvls, self.target_values
	
	
	######################################################################
	#                                                                    #
	# get_calculated_values                                              #
	#                                                                    #
	######################################################################
	def get_calculated_values(self):
		"""Get the calculated values
		
		This method returns the current value of the optical properties
		(wvls, values)."""
		
		calculated_values = []
		for i_target in range(self.nb_targets):
			calculated_values.append(self.all_calculated_values[self.target_starting_position[i_target]:self.target_starting_position[i_target]+self.nb_target_values[i_target]])
		
		return self.wvls, calculated_values
	
	
	######################################################################
	#                                                                    #
	# get_inequalities                                                   #
	#                                                                    #
	######################################################################
	def get_inequalities(self):
		"""Get the inequatities
		
		This method returns the inequalities used during the optimization."""
		
		return self.inequalities
	
	
	######################################################################
	#                                                                    #
	# get_index_profile                                                  #
	#                                                                    #
	######################################################################
	def get_index_profile(self):
		"""Get the index profile
		
		This method returns the index profile."""
		
		depth = []
		index_profile = []
		
		total_thickness = 0.0
		for i_layer in range(self.nb_front_layers):
			if isinstance(self.front_thickness[i_layer], list):
				for i_sublayer in range(len(self.front_thickness[i_layer])):
					depth.append(total_thickness)
					N = self.front_index[i_layer][i_sublayer]
					index_profile.append(N)
					total_thickness += self.front_thickness[i_layer][i_sublayer]
					depth.append(total_thickness)
					index_profile.append(N)
			else:
				depth.append(total_thickness)
				N = self.front_index[i_layer]
				index_profile.append(N)
				total_thickness += self.front_thickness[i_layer]
				depth.append(total_thickness)
				index_profile.append(N)
		
		return depth, index_profile
	
	
	######################################################################
	#                                                                    #
	# get_nb_front_layers                                                #
	#                                                                    #
	######################################################################
	def get_nb_front_layers(self):
		"""Get the number of front layers
		
		This method returns the number of front layers."""
		
		return self.nb_front_layers
	
	
	######################################################################
	#                                                                    #
	# get_nb_back_layers                                                 #
	#                                                                    #
	######################################################################
	def get_nb_back_layers(self):
		"""Get the number of back layers
		
		This method returns the number of back layers."""
		
		return self.nb_back_layers
	
	
	######################################################################
	#                                                                    #
	# get_norm_gradient                                                  #
	#                                                                    #
	######################################################################
	def get_norm_gradient(self):
		"""Get the gradient norm
		
		This method returns the gradient norm."""
		
		return self.optimizer.get_norm_gradient()
	
	
	######################################################################
	#                                                                    #
	# get_correlation_matrix                                             #
	#                                                                    #
	######################################################################
	def get_correlation_matrix(self):
		"""Get the correlation matrix
		
		This method returns the correlation matrix."""
		
		return self.optimizer.get_correlation_matrix()
	
	
	######################################################################
	#                                                                    #
	# get_just_removed_thin_layers                                       #
	#                                                                    #
	######################################################################
	def get_just_removed_thin_layers(self):
		"""Get if thin layers were just removed
		
		This method returns a boolean indicating if the instance just
		removed thin layers and no other operation has been done since."""
		
		return self.just_removed_thin_layers
	
	
	######################################################################
	#                                                                    #
	# copy_to_filter                                                     #
	#                                                                    #
	######################################################################
	def copy_to_filter(self):
		"""Copy the optimized filter to the filter instance"""
		
		# If necessary, delete all layer and reconstruct the filter.
		if self.need_to_reset_filter:
			self.filter.clear_design(FRONT)
			for i_layer in range(self.nb_front_layers):
				if isinstance(self.front_thickness[i_layer], list):
					self.filter.add_graded_layer_from_steps_with_material_nb(self.front_layers[i_layer], self.front_step_profiles[i_layer], self.front_thickness[i_layer], TOP, FRONT)
				else:
					self.filter.add_layer(self.materials[self.front_layers[i_layer]].get_name(), self.front_thickness[i_layer], TOP, FRONT, index = self.front_index[i_layer])
				# Remember which layers to fit and where to add needles and
				# steps.
				self.filter.set_refine_layer_thickness(i_layer, self.refine_thickness[i_layer], FRONT)
				self.filter.set_refine_layer_index(i_layer, self.refine_index[i_layer], FRONT)
				self.filter.set_add_needles(i_layer, self.add_needles_in_layer[i_layer], FRONT)
				self.filter.set_add_steps(i_layer, self.add_steps_in_layer[i_layer], FRONT)
		
		# Otherwise, simply change the thicknesses and indices.
		else:
			for i_layer in range(self.nb_front_layers):
				if self.refine_thickness[i_layer] or self.preserve_OT[i_layer]:
					self.filter.change_layer_thickness(self.front_thickness[i_layer], i_layer, FRONT)
				if self.refine_index[i_layer]:
					self.filter.change_layer_index(self.front_index[i_layer], i_layer, FRONT)
	
	
	######################################################################
	#                                                                    #
	# save_index_profile                                                 #
	#                                                                    #
	######################################################################
	def save_index_profile(self, outfile):
		"""Save the index profile
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		depth, index_profile = self.get_index_profile()
		
		outfile.write("%10s  %7s\n" %("depth", "N"))
		for i in range(len(depth)):
			outfile.write("%10.2f  %7.4f\n" %(depth[i], index_profile[i]))
	
	
	######################################################################
	#                                                                    #
	# save_values                                                        #
	#                                                                    #
	######################################################################
	def save_values(self, outfile):
		"""Save the current values of the optimized properties
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		wvls, target_values = self.get_target_values()
		wvls, calculated_values = self.get_calculated_values()
		
		outfile.write("%10s  %10s  %10s  %10s\n" %("target nb", "wvl", "target", "result"))
		for i_target, target in enumerate(self.targets):
			kind = target.get_kind()
			
			if target.kind in targets.COLOR_TARGETS:
				for i_component in range(3):
					outfile.write("%10i  %10s  %10.4f  %10.4f\n" %(i_target, "", target_values[i_target][i_component], calculated_values[i_target][i_component]))
			
			else:
				for i_wvl in range(self.nb_wvls[i_target]):
					outfile.write("%10i  %10.3f  %10.4f  %10.4f\n" %(i_target, wvls[i_target][i_wvl], target_values[i_target][i_wvl], calculated_values[i_target][i_wvl]))
