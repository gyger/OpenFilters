# optimization_needles.py
# 
# Optimization by refinement with the addition of needles.
#
# Copyright (c) 2005-2009,2013,2015 Stephane Larouche.
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
import operator

import config
from definitions import *
import abeles
import targets
import color
from optical_filter import one_hundred_eighty_over_pi
from moremath import Levenberg_Marquardt, Newton_polynomials
from optimization_refinement import optimization_refinement, THICKNESS



########################################################################
#                                                                      #
# optimization_needles                                                 #
#                                                                      #
########################################################################
class optimization_needles(optimization_refinement):
	"""A class to synthesize an optical filter using the needle method"""
	
	
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
		
		optimization_refinement.__init__(self, filter, targets, parent)
		
		self.needle_spacing = config.NEEDLE_SPACING*self.get_shortest_wavelength()
		self.min_dMF_ratio = config.MIN_DMF_RATIO
		
		self.nb_needles = 1
		
		# In automatic mode, needles are automatically added when it is not
		# further possible to refine the filter.
		self.automatic_mode = False
		
		# Remember if we just added needles and if it is possible to add
		# needles.
		self.just_added_needles = False
		self.could_add_needles_on_last_attempt = True
		self.can_add_needles = True
		
		self.last_attempt_material_set = set()
		
		# Init lists for dMF.
		self.dMF_positions = []
		self.dMF_depths = []
		self.dMF = []
		
		# Init lists for the selected needles.
		self.needles = []
		self.selected_needles = []
	
	
	######################################################################
	#                                                                    #
	# prepare                                                            #
	#                                                                    #
	######################################################################
	def prepare(self):
		"""Prepare for optimization
		
		Prepare instance attributes."""
		
		# Get the needle materials from the filter. If they are not
		# specified, the materials present on the front side of the filter
		# are used by default, except if these materials are mixtures. I
		# don't use set_needle_materials since this init method is executed
		# before the prepare method that will take care to prepare objects
		# from the abeles package.
		needle_materials = self.filter.get_needle_materials()
		if needle_materials:
			self.needle_material_nbs = [self.filter.get_material_nb(needle_material) for needle_material in needle_materials]
		else:
			front_layers, front_layer_descriptions, front_thickness, front_index, front_step_profiles = self.filter.get_layers(FRONT)
			front_layers_unique = set(front_layers)
			self.needle_material_nbs = [material_nb for material_nb in front_layers_unique if self.filter.get_material(material_nb).get_kind() == MATERIAL_REGULAR]
		
		self.nb_needle_materials = len(self.needle_material_nbs)
		
		# Preparation of the refinement is done at the end because we want
		# it to take care of the needle materials.
		optimization_refinement.prepare(self)
	
	
	######################################################################
	#                                                                    #
	# set_nb_needles                                                     #
	#                                                                    #
	######################################################################
	def set_nb_needles(self, nb_needles = 1):
		"""Set the number of needles
		
		This method takes an optional argument:
		  nb_needle          (optional) the number of needles that are
		                     added at the same time, the default value is
		                     1."""
		
		self.nb_needles = nb_needles
	
	
	######################################################################
	#                                                                    #
	# get_nb_needles                                                     #
	#                                                                    #
	######################################################################
	def get_nb_needles(self):
		"""Get the number of needles
		
		This method returns the number of needles added at once."""
		
		return self.nb_needles
	
	
	######################################################################
	#                                                                    #
	# set_needle_materials                                               #
	#                                                                    #
	######################################################################
	def set_needle_materials(self, material_names):
		"""Set the needle materials
		
		This method takes 1 argument:
		  material_names     the name of the needle materials."""
		
		self.nb_needle_materials = len(material_names)
		
		self.needle_material_nbs = [0]*self.nb_needle_materials
		
		for i_material in range(self.nb_needle_materials):
			
			# Get the material number.
			material_nb = self.filter.get_material_nb(material_names[i_material])
			self.needle_material_nbs[i_material] = material_nb
			
			# If this is a new material for this filter, expand the index
			# list.
			if material_nb >= self.nb_materials:
				for i_target in range(self.nb_targets):
					self.N[i_target].append(self.materials[material_nb].get_N(self.wvls_[i_target]))
				self.nb_materials += 1
	
	
	######################################################################
	#                                                                    #
	# get_needle_materials                                               #
	#                                                                    #
	######################################################################
	def get_needle_materials(self):
		"""Get the needle materials
		
		This method returns the name of the needle materials."""
		
		return [self.materials[self.needle_material_nbs[i_material]].get_name() for i_material in range(len(self.needle_material_nbs))]
	
	
	######################################################################
	#                                                                    #
	# add_needle_materials                                               #
	#                                                                    #
	######################################################################
	def add_needle_materials(self, material_names):
		"""Add needle materials to the present list
		
		This method takes 1 argument:
		  material_names     the name of the needle materials."""
		
		for material_name in material_names:
			
			# Get the material number.
			material_nb = self.filter.get_material_nb(material_name)
			if material_nb not in self.needle_material_nbs:
				self.needle_material_nbs.append(material_nb)
				self.nb_needle_materials += 1
				
				# If this is a new material for this filter, expand the index
				# list. Since only regular materials can be used for the needle
				# method, we don't need to consider n_min and n_max.
				if material_nb >= self.nb_materials:
					for i_target in range(self.nb_targets):
						self.N[i_target].append(self.materials[material_nb].get_N(self.wvls_[i_target]))
						self.N_min[i_target].append(None)
						self.N_max[i_target].append(None)
					self.nb_materials += 1
		
		# It might be possible to add needles if new materials were added.
		if not set(self.needle_material_nbs) <= self.last_attempt_material_set:
			self.can_add_needles = True
		
		# If it was possible to add needles on the last attemps, it might
		# still possible even if no new material is available.
		elif self.could_add_needles_on_last_attempt:
			self.can_add_needles = True
	
	
	######################################################################
	#                                                                    #
	# remove_needle_materials                                            #
	#                                                                    #
	######################################################################
	def remove_needle_materials(self, material_names):
		"""Remove needle materials from the present list
		
		This method takes 1 argument:
		  material_names     the name of the needle materials."""
		
		for material_name in material_names:
			
			# Get the material number.
			material_nb = self.filter.get_material_nb(material_name)
			try:
				self.needle_material_nbs.remove(material_nb)
				self.nb_needle_materials -= 1
			except ValueError:
				pass
		
		# When no material is selected, it is impossible to add needles.
		if self.nb_needle_materials == 0:
			self.can_add_needles = False
		
		# If it was impossible to add needles on the last attempt and the
		# current set of material is a subset of the set on last attempt,
		# it will still be impossible to add needles.
		elif not self.could_add_needles_on_last_attempt and set(self.needle_material_nbs) <= self.last_attempt_material_set:
			self.can_add_needles = False
	
	
	######################################################################
	#                                                                    #
	# set_automatic_mode                                                 #
	#                                                                    #
	######################################################################
	def set_automatic_mode(self, automatic_mode = True):
		"""Set the automatic mode
		
		This method takes an optional argument:
		  automatic_mode     (optional) a boolean indicating if the
		                     automatic mode is used, the default value is
		                     True.
		
		In automatic mode, the refinement, addition of needles and removal
		of thin layers is automatically done."""
		
		self.automatic_mode = automatic_mode
	
	
	######################################################################
	#                                                                    #
	# get_automatic_mode                                                 #
	#                                                                    #
	######################################################################
	def get_automatic_mode(self):
		"""Get the automatic mode
		
		This method returns a boolean indicating if the automatic mode is
		used."""
		
		return self.automatic_mode
	
	
	######################################################################
	#                                                                    #
	# calculate_needles                                                  #
	#                                                                    #
	######################################################################
	def calculate_needles(self):
		"""Calculate the needles
		
		The attributes used to calculate derivatives in refinement are
		reused. Therefore, after the execution of this method, their
		values should not be used before calling calculate_derivatives()."""
		
		# If no iteration were done, we need to calculate the values.
		# Otherwise, this is already done.
		if self.iteration == 0:
			self.calculate_values()
		
		self.needles = []
		self.selected_needles = []
		
		# Calculate the number of needles per layer. A minimum of 3 needles
		# are considered per layer because it takes 3 points to detect a
		# minimum.
		self.nb_needles_per_layer = [0]*self.nb_parameters
 		for i_parameter in range(self.nb_parameters):
			parameter_kind, layer_nb = self.parameters[i_parameter]
			if parameter_kind == THICKNESS and self.add_needles_in_layer[layer_nb] and self.front_thickness[layer_nb]:
				self.nb_needles_per_layer[i_parameter] = max(int(math.ceil(self.front_thickness[layer_nb]/self.needle_spacing)) + 1, 3)
		
		# Prepare lists for dMF.
		self.dMF_positions = [[0.0]*self.nb_needles_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF_depths = [[0.0]*self.nb_needles_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF = [[[0.0]*self.nb_needles_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)] for i_material in range(self.nb_needle_materials)]
		
		# Calculate the thickness at the beginning of every layer to be
		# used when calculating depth.
		total_thickness = 0.0
		thickness_at_beginning = [0.0]*self.nb_front_layers
		for i_layer in range(self.nb_front_layers):
			thickness_at_beginning[i_layer] = total_thickness
			if isinstance(self.front_thickness[i_layer], list):
				for i_sublayer in range(len(self.front_thickness[i_layer])):
					total_thickness += self.front_thickness[i_layer][i_sublayer]
			else:
				total_thickness += self.front_thickness[i_layer]
		
		# Give other threads a chance...
		time.sleep(0)
		
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
				
				if self.nb_needles_per_layer[i_parameter] == 0:
					continue
				
				dummy, layer_nb = self.parameters[i_parameter]
				
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
				
				dMi_needles = abeles.needle_matrices(self.wvls_[i_target], self.nb_needles_per_layer[i_parameter])
				dMi_needles.set_needle_positions(self.front_thickness[layer_nb]/(self.nb_needles_per_layer[i_parameter]-1))
				
				# Give other threads a chance...
				time.sleep(0)
				
				for i_needle in range(self.nb_needles_per_layer[i_parameter]):
					self.dMF_positions[i_parameter][i_needle] = dMi_needles.get_needle_position(i_needle)			
					self.dMF_depths[i_parameter][i_needle] = thickness_at_beginning[layer_nb] + self.dMF_positions[i_parameter][i_needle]
				
				# Give other threads a chance...
				time.sleep(0)
				
				for i_material in range(self.nb_needle_materials):
					needle_material_nb = self.needle_material_nbs[i_material]
					
					# Only try to add needles of a different material. Adding
					# a needle of the same material is equivalent to change the
					# thickness. If the refinement was done properly before
					# adding needles, the derivative should be 0 anyway.
					if needle_material_nb == self.front_layers[layer_nb]:
						continue
					
					dMi_needles.calculate_dMi_needles(N, self.N[i_target][needle_material_nb], self.front_thickness[layer_nb], self.sin2_theta_0[i_target])
					
					# Give other threads a chance...
					time.sleep(0)
					
					for i_needle in range(self.nb_needles_per_layer[i_parameter]):
						self.dM[i_target][i_parameter].calculate_dM(dMi_needles[i_needle], self.pre_and_post_matrices[i_target], layer_nb)
						
						# Give other threads a chance...
						time.sleep(0)
						
						if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.COLOR_TARGETS:
							# Calculate the derivative of amplitude reflection and transmission.
							if self.direction[i_target] == FORWARD:
								self.dr_and_dt_front[i_target][i_parameter].calculate_dr_and_dt(self.dM[i_target][i_parameter], self.psi[i_target])
								if self.consider_backside[i_target]:
									self.dr_and_dt_front_reverse[i_target][i_parameter].calculate_dr_and_dt_reverse(self.dM[i_target][i_parameter], self.psi_reverse[i_target])
							else:
								self.dr_and_dt_front_reverse[i_target][i_parameter].calculate_dr_and_dt_reverse(self.dM[i_target][i_parameter], self.psi_reverse[i_target])
							
							# Give other threads a chance...
							time.sleep(0)
							
							# Calculate the derivative of the target.
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
						
						# Get the values.
						if kind in targets.PHOTOMETRIC_TARGETS:
							if kind in targets.REFLECTION_TARGETS:
								derivatives = self.dR[i_target][i_parameter]
							elif kind in targets.TRANSMISSION_TARGETS:
								derivatives = self.dT[i_target][i_parameter]
							else:
								derivatives = self.dA[i_target][i_parameter]
						elif kind in targets.PHASE_TARGETS:
							if kind in targets.REFLECTION_TARGETS:
								derivatives = [dphi*one_hundred_eighty_over_pi for dphi in self.dphi_r[i_target][i_parameter]]
							else:
								derivatives = [dphi*one_hundred_eighty_over_pi for dphi in self.dphi_t[i_target][i_parameter]]
						elif kind in targets.GD_TARGETS or kind in targets.GDD_TARGETS:
							if kind in targets.DISCRETE_TARGETS:
								derivatives = [self.dderived_values[i_target][i_parameter][1]]
							else:
								derivatives = self.dderived_values[i_target][i_parameter]
						elif kind in targets.COLOR_TARGETS:
							derivatives = self.dderived_values[i_target][i_parameter].dcolor(target.get_color_space())
						
						# Give other threads a chance...
						time.sleep(0)
						
						# Add dF for this needle to the right element.
						starting_pos = self.target_starting_position[i_target]
						for i_value in range(len(self.target_values[i_target])):
							pos = starting_pos+i_value
							if self.all_inequalities[pos] == Levenberg_Marquardt.SMALLER and self.all_calculated_values[pos] < self.all_target_values[pos]:
								continue
							elif self.all_inequalities[pos] == Levenberg_Marquardt.LARGER and self.all_calculated_values[pos] > self.all_target_values[pos]:
								continue
							self.dMF[i_material][i_parameter][i_needle] -= (self.all_target_values[pos]-self.all_calculated_values[pos])/(self.all_tolerances[pos]*self.all_tolerances[pos]) * derivatives[i_value]
						
						# Give other threads a chance...
						time.sleep(0)
		
		# Find the minima that are under 0.
		for i_material in range(self.nb_needle_materials):
			material_nb = self.needle_material_nbs[i_material]
 			
 			for i_parameter in range(self.nb_parameters):
				dummy, layer_nb = self.parameters[i_parameter]
				
				# It takes a minimum of three points to do quadratic
				# interpolation. This also limits the possibility to put
				# needles in very thin layers. Also verify that the lowest point
				# is below 0. Otherwise it is not necessary to search the
				# minimum.
				if self.nb_needles_per_layer[i_parameter] >= 3:
					
					# Put a previous position for which we are sure it won't
					# block the detection of the first needle.
					previous_pos = -10.0*self.needle_spacing
					
					for i_needle in range(1, self.nb_needles_per_layer[i_parameter]-1):
						# Localize the minimum only if this material is the one
						# providing the lowest dMF value at this point. If 2
						# materials give the same dMF value, keep the first one in
						# the list.
						for i_alt_material in range(self.nb_needle_materials):
							if i_alt_material != i_material:
								if self.dMF[i_material][i_parameter][i_needle] == self.dMF[i_alt_material][i_parameter][i_needle]:
									if i_material > i_alt_material:
										break
								elif self.dMF[i_material][i_parameter][i_needle] > self.dMF[i_alt_material][i_parameter][i_needle]:
									break
						
						else:
							# Find the quadratic equation that passes through 3
							# points using Newton's polynomial.
							b = Newton_polynomials.Newton_quadratic(self.dMF_positions[i_parameter][i_needle-1:i_needle+2], self.dMF[i_material][i_parameter][i_needle-1:i_needle+2])
							
							# Localize the extremum only if it is a minimum
							if b[2] > 0.0:
								
								# Localize the minimum. Verify that it it is negative,
								# inside the range considered and that is was not
								# already detected in the previous range.
								min_pos = -0.5*b[1]/b[2]
								min_value = b[0]+min_pos*(b[1]+min_pos*b[2])
								if min_value < 0.0 and self.dMF_positions[i_parameter][i_needle-1] < min_pos and min_pos < self.dMF_positions[i_parameter][i_needle+1] and abs(min_pos-previous_pos) > self.needle_spacing:
									self.needles.append((layer_nb, min_pos, material_nb, min_value))
									previous_pos = min_pos
						
						# Give other threads a chance...
						time.sleep(0)
		
		# Order the needles in order of smallest (most negative) dMF.
		self.needles.sort(key = operator.itemgetter(3))
		
		# Build lists of needle depths and values (for the user interface).
		nb_needles = len(self.needles)
 		self.needle_depths = [thickness_at_beginning[self.needles[i_needle][0]] + self.needles[i_needle][1] for i_needle in range(nb_needles)]
 		self.needle_values = [self.needles[i_needle][3] for i_needle in range(nb_needles)]
		
		self.last_attempt_material_set = set(self.needle_material_nbs)
		
		if nb_needles:
			self.could_add_needles_on_last_attempt = True
			self.can_add_needles = True
		else:
			self.could_add_needles_on_last_attempt = False
			self.can_add_needles = False
	
	
	######################################################################
	#                                                                    #
	# select_needles                                                     #
	#                                                                    #
	######################################################################
	def select_needles(self):
		"""Select the needles
		
		Select the most negative needles."""
		
		# In case there is no needle.
		if len(self.needles) == 0:
			self.selected_needles = []
			return
		
		# If the number of detected needles is larger than the maximum
		# number of needles, limit the list of selected needles.
		if len(self.needles) > self.nb_needles:
			self.selected_needles = range(self.nb_needles)
		else:
			self.selected_needles = range(len(self.needles))
		
		# Remove needles whose dMF values are not small enough compared
		# to the smallest dMF value.
		max_acceptable_dMF = self.min_dMF_ratio * self.needles[self.selected_needles[0]][3]
		for i_selected_needle in range(1, len(self.selected_needles)):
			if self.needles[self.selected_needles[i_selected_needle]][3] > max_acceptable_dMF:
				self.selected_needles = self.selected_needles[0:i_selected_needle]
				break
	
	
	######################################################################
	#                                                                    #
	# add_selected_needles                                               #
	#                                                                    #
	######################################################################
	def add_selected_needles(self, selected_needles = None):
		"""Add the selected needles
		
		This method takes an optional argument:
		  selected_needles   (optional) the selected needles.
		  
		By default, the needles selected by select_needles are added."""
		
		if selected_needles is None:
			selected_needles = self.selected_needles
		
		# If no needle is selected, immediatly return
		if selected_needles == []:
			return
		
		# Make a list of needles to add.
		needles_to_add = []
		for i_needle in range(len(selected_needles)):
			needles_to_add.append(self.needles[selected_needles[i_needle]])
		
		# Sort the needles in decreasing order of layer and position in
		# a needle. First sort by position than by layer. This order
		# greatly simplify the task to insert the needles since the
		# layer numbers of subsequent needles will still be ok.
		needles_to_add.sort(key = operator.itemgetter(1), reverse=True)
		needles_to_add.sort(key = operator.itemgetter(0), reverse=True)
		
		for needle in needles_to_add:
			layer_nb = needle[0]
			position = needle[1]
			material_nb = needle[2]
			
			original_thickness = self.front_thickness[layer_nb]
			original_material_nb = self.front_layers[layer_nb]
			
			# Seperate the the layer.
			self.front_layers.insert(layer_nb+1, original_material_nb)
			self.front_layer_descriptions.insert(layer_nb+1, [])
			self.front_thickness.insert(layer_nb+1, original_thickness-position)
			self.front_index.insert(layer_nb+1, self.front_index[layer_nb])
			self.front_step_profiles.insert(layer_nb+1, [])
			self.refine_thickness.insert(layer_nb+1, 1)
			self.refine_index.insert(layer_nb+1, self.refine_index[layer_nb])
			self.preserve_OT.insert(layer_nb+1, self.preserve_OT[layer_nb])
			self.add_needles_in_layer.insert(layer_nb+1, 1)
			self.add_steps_in_layer.insert(layer_nb+1, self.add_steps_in_layer[layer_nb])
			if self.preserve_OT[layer_nb+1]:
				self.OT.insert(layer_nb+1, self.front_thickness[layer_nb+1]*self.front_index[layer_nb+1])
			else:
				self.OT.insert(layer_nb+1, 0.0)
			
			# Add the needle.
			self.front_layers.insert(layer_nb+1, material_nb)
			self.front_layer_descriptions.insert(layer_nb+1, [])
			self.front_thickness.insert(layer_nb+1, 0.0)
			self.front_index.insert(layer_nb+1, self.materials[self.front_layers[layer_nb+1]].get_index(self.center_wavelength))
			self.front_step_profiles.insert(layer_nb+1, [])
			self.refine_thickness.insert(layer_nb+1, 1)
			self.refine_index.insert(layer_nb+1, self.materials[self.front_layers[layer_nb+1]].is_mixture())
			self.preserve_OT.insert(layer_nb+1, 0)
			self.add_needles_in_layer.insert(layer_nb+1, 1)
			self.add_steps_in_layer.insert(layer_nb+1, self.materials[self.front_layers[layer_nb+1]].is_mixture())
			self.OT.insert(layer_nb+1, 0.0)
			
			# Change the remaining part of the layer.
			self.front_layer_descriptions[layer_nb] = []
			self.front_thickness[layer_nb] = position
			if self.preserve_OT[layer_nb]:
				self.OT[layer_nb] = self.front_thickness[layer_nb]*self.front_index[layer_nb]
			
			# Increase the number of front layers.
			self.nb_front_layers += 2
		
		self.add_parameters()
	
	
	######################################################################
	#                                                                    #
	# add_needles_                                                       #
	#                                                                    #
	######################################################################
	def add_needles_(self):
		"""Add needles
		
		This method calculates the needles, select the best ones and add
		them."""
		
		self.calculate_needles()
		self.select_needles()
		self.add_selected_needles()
		
		self.just_added_needles = True
		
		self.just_removed_thin_layers = False
	
	
	######################################################################
	#                                                                    #
	# add_needles                                                        #
	#                                                                    #
	######################################################################
	def add_needles(self):
		"""Add needles
		
		This method calculates the needles, select the best ones and add
		them.
		
		This method calls add_needles_ and updates the user interface."""
		
		self.working = True
		self.can_stop = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		self.add_needles_()
		
		self.working = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
	
	
	######################################################################
	#                                                                    #
	# remove_thin_layers_                                                #
	#                                                                    #
	######################################################################
	def remove_thin_layers_(self):
		"""Remove thin layer
		
		Remove layers that are thinner than the mimimal thickness and merge
		layer that have an index difference smaller than the minimal index
		difference."""
		
		answer = optimization_refinement.remove_thin_layers_(self)
		
		if answer and (self.min_thickness or self.min_delta_n):
			self.just_added_needles = False
			self.can_add_needles = True
		
		return answer
	
	
	######################################################################
	#                                                                    #
	# iterate_                                                           #
	#                                                                    #
	######################################################################
	def iterate_(self):
		"""Do one iteration
		
		The refinement method is not called because it significantly slows
		down the optimization."""
		
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
		
		# If the iteration changed the solution, it may now possible to
		# add needles.
		if self.status == Levenberg_Marquardt.IMPROVING or self.status == Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL or self.status == Levenberg_Marquardt.CHI_2_IS_OK:
			self.just_added_needles = False
			self.can_add_needles = True
	
	
	######################################################################
	#                                                                    #
	# go                                                                 #
	#                                                                    #
	######################################################################
	def go(self):
		"""Optimize the filter
		
		This method optimizes the filter until it is not possible to add
		any more needle.
		
		To implement the automatic mode, the optimization go method cannot
		be used."""
		
		self.continue_optimization = True
		self.working = True
		self.can_stop = True
		
		# Increase the number of iteration when asked to continue.
		if self.max_iterations_reached:
			self.increase_max_iterations()
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		while self.continue_optimization:
			
			# Refine the filter.
			while self.continue_optimization:
				self.iterate_()
				
				if self.stop_criteria_met or self.max_iterations_reached:
					break
				
				if self.parent:
					self.parent.update(self.working, self.status)
			
			# If chi square is sufficiently small, stop optimization.
			if self.status == Levenberg_Marquardt.CHI_2_IS_OK:
				break
			
			if not self.continue_optimization: break
			if not self.automatic_mode: break
			
			if self.parent:
				self.parent.update(self.working, self.status)
			
			# Remove thin layers.
			if self.remove_thin_layers_():
				
				self.just_added_needles = False
				
				if self.parent:
					self.parent.update(self.working, self.status)
				
				# If layer with finite thickness were removed, it may now be
				# possible to add needles. Furthermore, the filter it not
				# optimal and needs to be refined again, so we go back to the
				# beginning of the loop.
				if self.min_thickness != 0.0:
					self.can_add_needles = True
					continue
			
			if not self.continue_optimization: break
			if not self.automatic_mode: break
			
			if self.parent:
				self.parent.update(self.working, self.status)
			
			# Add needles
			self.add_needles_()
			
			if not self.can_add_needles: break
			
			if self.parent:
				self.parent.update(self.working, self.status)
		
		self.working = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
	
	
	######################################################################
	#                                                                    #
	# get_dMF_profile                                                    #
	#                                                                    #
	######################################################################
	def get_dMF_profile(self):
		"""Get the derivative of the merit function
		
		This method returns the derivative of the merit function."""
		
		return self.dMF_depths, self.dMF, self.needle_depths, self.needle_values
	
	
	######################################################################
	#                                                                    #
	# get_selected_needles                                               #
	#                                                                    #
	######################################################################
	def get_selected_needles(self):
		"""Get the selected needles
		
		This method returns the selected needles."""
		
		return self.selected_needles
	
	
	######################################################################
	#                                                                    #
	# get_can_add_needles                                                #
	#                                                                    #
	######################################################################
	def get_can_add_needles(self):
		"""Get if it is possible to add needles
		
		This method returns a boolean indicating if it is possible to add
		needles."""
		
		# If chi square is ok, it is useless to add needles.
		if self.status == Levenberg_Marquardt.CHI_2_IS_OK:
			return False
		
		return self.can_add_needles
	
	
	######################################################################
	#                                                                    #
	# get_could_add_needles_on_last_attempt                              #
	#                                                                    #
	######################################################################
	def get_could_add_needles_on_last_attempt(self):
		"""Get if it was possible to add needles on the last attemps
		
		This method returns a boolean indicating if it was possible to add
		needles on the last attempt."""
		
		return self.could_add_needles_on_last_attempt
	
	
	######################################################################
	#                                                                    #
	# get_just_added_needles                                             #
	#                                                                    #
	######################################################################
	def get_just_added_needles(self):
		"""Get if needles were just added
		
		This method returns a boolean indicating if the instance just added
		needles and no other operation has been done since."""
		
		return self.just_added_needles
	
	
	######################################################################
	#                                                                    #
	# copy_to_filter                                                     #
	#                                                                    #
	######################################################################
	def copy_to_filter(self):
		"""Copy the optimized filter to the filter instance"""
		
		# Let the parent class do most of the work.
		optimization_refinement.copy_to_filter(self)
		
		# Set the needle materials.
		needle_materials = [self.filter.get_material(material_nb).get_name() for material_nb in self.needle_material_nbs]
		self.filter.set_needle_materials(needle_materials)
	
	
	######################################################################
	#                                                                    #
	# specific_save                                                      #
	#                                                                    #
	######################################################################
	def specific_save(self, outfile):
		"""Save the derivative of the merit function
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		outfile.write("%10s" % "depth")
		for material_nb in self.needle_material_nbs:
			outfile.write("  %20s" % self.filter.get_material(material_nb).get_name())
		outfile.write("\n")
		for i_parameter in range(len(self.nb_needles_per_layer)):
			for i_needle in range(self.nb_needles_per_layer[i_parameter]):
				outfile.write("%10.2f" % self.dMF_depths[i_parameter][i_needle])
				for i_material in range(self.nb_needle_materials):
					outfile.write("  %20.12f" % self.dMF[i_material][i_parameter][i_needle])
				outfile.write("\n")
		
		outfile.write("\n\nNeedles:\n\n")
		outfile.write("%10s  %15s  %20s\n" % ("depth(nm)", "Material", "value"))
		for i_needle in range(len(self.needles)):
			material_name = self.filter.get_material(self.needles[i_needle][2]).get_name()
			outfile.write("%10.2f  %15s  %20.12f\n" % (self.needle_depths[i_needle], material_name, self.needle_values[i_needle]))
