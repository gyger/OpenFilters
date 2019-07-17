# optimization_steps.py
# 
# Optimization by refinement with the addition of steps.
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
from optimization_refinement import optimization_refinement, INDEX



########################################################################
#                                                                      #
# optimization_steps                                                   #
#                                                                      #
########################################################################
class optimization_steps(optimization_refinement):
	"""A class to synthesize an optical filter using the step method"""
	
	
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
		
		self.step_spacing = config.NEEDLE_SPACING*self.get_shortest_wavelength()
		self.min_dMF_ratio = config.MIN_DMF_RATIO
		
		self.nb_steps = 1
		
		# In automatic mode, steps are automatically added when it is not
		# further possible to refine the filter.
		self.automatic_mode = False
		
		# Remember if we just added steps and if it is possible to add
		# needles.
		self.just_added_steps = False
		self.could_add_steps_on_last_attempt = True
		self.can_add_steps = True
		
		# Init lists for dMF.
		self.dMF_positions = []
		self.dMF_depths = []
		self.dMF = []
		self.dMF_up = []
		self.dMF_down = []
		
		# Init lists for the selected steps.
		self.steps_up = []
		self.steps_down = []
		self.selected_steps_up = []
		self.selected_steps_down = []
	
	
	######################################################################
	#                                                                    #
	# set_nb_steps                                                       #
	#                                                                    #
	######################################################################
	def set_nb_steps(self, nb_steps = 1):
		"""Set the number of steps
		
		This method takes an optional argument:
		  nb_steps           (optional) the number of steps that are added
		                     at the same time, the default value is 1."""
		
		self.nb_steps = nb_steps
	
	
	######################################################################
	#                                                                    #
	# get_nb_steps                                                       #
	#                                                                    #
	######################################################################
	def get_nb_steps(self):
		"""Get the number of steps
		
		This method returns the number of steps added at once."""
		
		return self.nb_steps
	
	
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
		
		In automatic mode, the refinement, addition of steps and removal
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
	# calculate_steps                                                    #
	#                                                                    #
	######################################################################
	def calculate_steps(self):
		"""Calculate the steps
		
		The attributes used to calculate derivatives in refinement are
		reused. Therefore, after the execution of this method, their
		values should not be used before calling calculate_derivatives()."""
		# If no iteration were done, we need to calculate the values.
		# Otherwise, this is already done.
		if self.iteration == 0:
			self.calculate_values()
		
		# Find a way to avoid that... We only need them when an index is
		# stuck at the limit.
		self.calculate_derivatives()
		
		# Empty the lists for the steps and the selected steps.
		self.steps_up = []
		self.steps_down = []
		self.selected_steps_up = []
		self.selected_steps_down = []
		
		# Calculate the number of steps per layer. Only the layer whose
		# index is fitted are considered for the addition of steps. A
		# minimum of 5 steps are considered per layer because the 2 end
		# intervals will be ignored (see below) and it takes at least 3
		# points to detect a minimum.
		self.nb_steps_per_layer = [0]*self.nb_parameters
 		for i_parameter in range(self.nb_parameters):
			parameter_kind, layer_nb = self.parameters[i_parameter]
			if parameter_kind == INDEX and self.add_steps_in_layer[layer_nb] and self.front_thickness[layer_nb]:
				self.nb_steps_per_layer[i_parameter] = max(int(math.ceil(self.front_thickness[layer_nb]/self.step_spacing))+1, 5)
		
		# Reset the lists for dMF.
		self.dMF_positions = [[0.0]*self.nb_steps_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF_depths = [[0.0]*self.nb_steps_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF = [[0.0]*self.nb_steps_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF_up = [[0.0]*self.nb_steps_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		self.dMF_down = [[0.0]*self.nb_steps_per_layer[i_parameter] for i_parameter in range(self.nb_parameters)]
		
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
		
		# The real calculations...
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
				if self.nb_steps_per_layer[i_parameter] != 0:
					dummy, layer_nb = self.parameters[i_parameter]
					
					dMi_steps = abeles.needle_matrices(self.wvls_[i_target], self.nb_steps_per_layer[i_parameter])
					dMi_steps.set_needle_positions(self.front_thickness[layer_nb]/(self.nb_steps_per_layer[i_parameter]-1))
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.front_index[layer_nb] == self.n_min[self.front_layers[layer_nb]]:
						N = self.N_min[i_target][self.front_layers[layer_nb]].get_N_mixture()
						dn = self.N_min[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					elif self.front_index[layer_nb] == self.n_max[self.front_layers[layer_nb]]:
						N = self.N_max[i_target][self.front_layers[layer_nb]].get_N_mixture()
						dn = self.N_max[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					else:
						self.N[i_target][self.front_layers[layer_nb]].set_N_mixture(self.front_index[layer_nb], self.center_wavelength)
						self.N[i_target][self.front_layers[layer_nb]].set_dN_mixture(self.front_index[layer_nb], self.center_wavelength)
						N = self.N[i_target][self.front_layers[layer_nb]].get_N_mixture()
						dn = self.N[i_target][self.front_layers[layer_nb]].get_dN_mixture()
					dMi_steps.calculate_dMi_steps(N, dn, self.front_thickness[layer_nb], self.sin2_theta_0[i_target])
					
					# Give other threads a chance...
					time.sleep(0)
					
					for i_step in range(self.nb_steps_per_layer[i_parameter]):
						
						self.dMF_positions[i_parameter][i_step] = dMi_steps.get_needle_position(i_step)
						self.dMF_depths[i_parameter][i_step] = thickness_at_beginning[layer_nb] + self.dMF_positions[i_parameter][i_step]
						
						self.dM[i_target][i_parameter].calculate_dM(dMi_steps[i_step], self.pre_and_post_matrices[i_target], layer_nb)
						
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
						
						# Add dMF for this step to the right element.
						starting_pos = self.target_starting_position[i_target]
						for i_value in range(len(self.target_values[i_target])):
							pos = starting_pos + i_value
							if self.all_inequalities[pos] == Levenberg_Marquardt.SMALLER and self.all_calculated_values[pos] < self.all_target_values[pos]:
								continue
							elif self.all_inequalities[pos] == Levenberg_Marquardt.LARGER and self.all_calculated_values[pos] > self.all_target_values[pos]:
								continue
							self.dMF[i_parameter][i_step] -= (self.all_target_values[pos]-self.all_calculated_values[pos])/(self.all_tolerances[pos]*self.all_tolerances[pos]) * derivatives[i_value]
						
						# Give other threads a chance...
						time.sleep(0)
 		
 		# Calculate dMF for a step up or a step down.
 		for i_parameter in range(self.nb_parameters):
			
			# If there is no step for this parameter (it is a thickness, for
			# example), immediatly jump to the next parameter.
			if self.nb_steps_per_layer[i_parameter] == 0:
				continue
			
			# If the index is stuck at a limit, we need the derivative of the
			# merit function upon variation of the index to calculate the
			# derivative of the merit function upon the addition of a step.
 			if self.parameter_values[i_parameter] == self.parameter_min[i_parameter] or self.parameter_values[i_parameter] == self.parameter_max[i_parameter]:
 				dMF_n = 0.0
				for i_target in range(self.nb_targets):
					starting_pos = self.target_starting_position[i_target]
					for i_value in range(len(self.target_values[i_target])):
						pos = starting_pos+i_value
						if self.all_inequalities[pos] == Levenberg_Marquardt.SMALLER and self.all_calculated_values[pos] < self.all_target_values[pos]:
							continue
						elif self.all_inequalities[pos] == Levenberg_Marquardt.LARGER and self.all_calculated_values[pos] > self.all_target_values[pos]:
							continue
						dMF_n -= (self.all_target_values[pos]-self.all_calculated_values[pos])/(self.all_tolerances[pos]*self.all_tolerances[pos]) * self.all_derivatives[i_parameter][pos]
 			
 			if self.parameter_values[i_parameter] == self.parameter_min[i_parameter]:
 				for i_step in range(self.nb_steps_per_layer[i_parameter]):
 					self.dMF_up[i_parameter][i_step]   =  0.5*dMF_n + self.dMF[i_parameter][i_step]
 					self.dMF_down[i_parameter][i_step] =  0.5*dMF_n - self.dMF[i_parameter][i_step]
 			elif self.parameter_values[i_parameter] == self.parameter_max[i_parameter]:
 				for i_step in range(self.nb_steps_per_layer[i_parameter]):
 					self.dMF_up[i_parameter][i_step]   = -0.5*dMF_n + self.dMF[i_parameter][i_step]
 					self.dMF_down[i_parameter][i_step] = -0.5*dMF_n - self.dMF[i_parameter][i_step]
 			else:
 				for i_step in range(self.nb_steps_per_layer[i_parameter]):
 					self.dMF_up[i_parameter][i_step]   =              self.dMF[i_parameter][i_step]
 					self.dMF_down[i_parameter][i_step] =             -self.dMF[i_parameter][i_step]
			
			# Give other threads a chance...
			time.sleep(0)
		
		# Find the minima.
 		for i_parameter in range(self.nb_parameters):
			dummy, layer_nb = self.parameters[i_parameter]
			
			if self.nb_steps_per_layer[i_parameter] >= 3:
				
				# Put a previous position for which we are sure it won't
				# block the detection of the first step.
				previous_pos = -10.0*self.step_spacing
				
				# We do not consider the first and last intervals of the layer.
				# This is done to avoid detecting minima too close to the
				# layer ends. This is required since when the layer thickness
				# is optimal, both ends of the layer are optimal position for
				# the addition of steps.
				for i_step in range(2, self.nb_steps_per_layer[i_parameter]-2):
					# Find the quadratic equation that passes through 3 points
					# using Newton's polynomial.
					b_up   = Newton_polynomials.Newton_quadratic(self.dMF_positions[i_parameter][i_step-1:i_step+2], self.dMF_up[i_parameter][i_step-1:i_step+2])
					b_down = Newton_polynomials.Newton_quadratic(self.dMF_positions[i_parameter][i_step-1:i_step+2], self.dMF_down[i_parameter][i_step-1:i_step+2])
					
					# Localize the extremum only if it is a minimum
					if b_up[2] > 0.0:
						
						# Localize the minimum. Verify that it it is inside the
						# range considered and that is was not already detected in
						# the previous range.
						min_pos = -0.5*b_up[1]/b_up[2]
						if self.dMF_positions[i_parameter][i_step-1] < min_pos and min_pos < self.dMF_positions[i_parameter][i_step+1] and abs(min_pos-previous_pos) > self.step_spacing:
							min_value = b_up[0]+min_pos*(b_up[1]+min_pos*b_up[2])
							if min_value < 0.0:
								self.steps_up.append((layer_nb, min_pos, min_value))
							previous_pos = min_pos
					
					# Localize the extremum only if it is a minimum
					if b_down[2] > 0.0:
						
						# Localize the minimum. Verify that it it is inside the
						# range considered and that is was not already  detected in
						# the previous range.
						min_pos = -0.5*b_down[1]/b_down[2]
						if self.dMF_positions[i_parameter][i_step-1] < min_pos and min_pos < self.dMF_positions[i_parameter][i_step+1] and abs(min_pos-previous_pos) > self.step_spacing:
							min_value = b_down[0]+min_pos*(b_down[1]+min_pos*b_down[2])
							if min_value < 0.0:
								self.steps_down.append((layer_nb, min_pos, min_value))
							previous_pos = min_pos
			
					# Give other threads a chance...
					time.sleep(0)
		
		# Order the steps in order of smallest (most negative) dMF.
		self.steps_up.sort(key = operator.itemgetter(2))
		self.steps_down.sort(key = operator.itemgetter(2))
		
		# Build lists of steps depths and values (for the user interface).
		nb_steps_up = len(self.steps_up)
 		self.step_up_depths = [thickness_at_beginning[self.steps_up[i_step][0]] + self.steps_up[i_step][1]for i_step in range(nb_steps_up)]
 		self.step_up_values = [self.steps_up[i_step][2] for i_step in range(nb_steps_up)]
		nb_steps_down = len(self.steps_down)
 		self.step_down_depths = [thickness_at_beginning[self.steps_down[i_step][0]] + self.steps_down[i_step][1] for i_step in range(nb_steps_down)]
 		self.step_down_values = [self.steps_down[i_step][2] for i_step in range(nb_steps_down)]
		
		if nb_steps_up + nb_steps_down:
			self.could_add_steps_on_last_attempt = True
			self.can_add_steps = True
		else:
			self.could_add_steps_on_last_attempt = False
			self.can_add_steps = False
	
	
	######################################################################
	#                                                                    #
	# select_steps                                                       #
	#                                                                    #
	######################################################################
	def select_steps(self):
		"""Select the steps
		
		Select the most negative steps."""
		
		self.selected_steps_up = []
		self.selected_steps_down = []
		
		nb_steps_up = len(self.steps_up)
		nb_steps_down = len(self.steps_down)
		
		# In case there is no step.
		if nb_steps_up + nb_steps_down == 0:
			return self.selected_steps_up, self.selected_steps_down
		
		# If the number of detected steps is smaller than the maximum
		# number of steps, keep all steps for the moment. Otherwise,
		# select the highest ones.
		if nb_steps_up + nb_steps_down <= self.nb_steps:
			self.selected_steps_up = range(nb_steps_up)
			self.selected_steps_down = range(nb_steps_down)
		else:
			step_up_nb = 0
			step_down_nb = 0
			for i_step in range(self.nb_steps):
				# If we exhausted all steps up, choose a step down.
				if step_up_nb == nb_steps_up:
					self.selected_steps_down.append(step_down_nb)
					step_down_nb += 1
				# If we exhausted all steps down, choose a step up.
				elif step_down_nb == nb_steps_down:
					self.selected_steps_up.append(step_up_nb)
					step_up_nb += 1
				# Otherwise, choose the most negative value.
				elif self.steps_down[step_down_nb][2] < self.steps_up[step_up_nb][2]:
					self.selected_steps_down.append(step_down_nb)
					step_down_nb += 1
				else:
					self.selected_steps_up.append(step_up_nb)
					step_up_nb += 1
		
		# Remove steps whose dMF values are not small enough compared
		# to the smallest dMF value.
		if len(self.selected_steps_up) == 0:
			max_acceptable_dMF = self.min_dMF_ratio * self.steps_down[self.selected_steps_down[0]][2]
		elif len(self.selected_steps_down) == 0:
			max_acceptable_dMF = self.min_dMF_ratio * self.steps_up[self.selected_steps_up[0]][2]
		else:
			max_acceptable_dMF = self.min_dMF_ratio * min(self.steps_up[self.selected_steps_up[0]][2], self.steps_down[self.selected_steps_down[0]][2])
		for i_selected_step in range(len(self.selected_steps_up)):
			if self.steps_up[self.selected_steps_up[i_selected_step]][2] > max_acceptable_dMF:
				self.selected_steps_up = self.selected_steps_up[0:i_selected_step]
				break
		for i_selected_step in range(len(self.selected_steps_down)):
			if self.steps_down[self.selected_steps_down[i_selected_step]][2] > max_acceptable_dMF:
				self.selected_steps_down = self.selected_steps_down[0:i_selected_step]
				break
		
		# Build list of the selected steps including the description of the
		# step, the step number and the direction or the step.
		selection = []
		for i_selected_step in range(len(self.selected_steps_up)):
			selection.append([self.steps_up[self.selected_steps_up[i_selected_step]], i_selected_step, +1])
		for i_selected_step in range(len(self.selected_steps_down)):
			selection.append([self.steps_down[self.selected_steps_down[i_selected_step]], i_selected_step, -1])
		
		# Sort the selection in increasing order of layer and position in
		# a step. First sort by position than by layer.
		selection.sort(key = lambda x: x[0][1])
		selection.sort(key = lambda x: x[0][0])
		
		# If two steps rigth next to each other are in identical direction,
		# remove the one with the less negative dMF.
		for i_selection in range(len(selection)-1-1, 0-1, -1):
			if selection[i_selection][0][0] == selection[i_selection+1][0][0]:
				if selection[i_selection][2] == selection[i_selection+1][2]:
					if selection[i_selection][0][2] < selection[i_selection+1][0][2]:
						selection.pop(i_selection+1)
					else:
						selection.pop(i_selection)
		
		self.selected_steps_up = []
		self.selected_steps_down = []
		
		for i_selection in range(len(selection)):
			if selection[i_selection][2] == +1:
				self.selected_steps_up.append(selection[i_selection][1])
			else:
				self.selected_steps_down.append(selection[i_selection][1])
	
	
	######################################################################
	#                                                                    #
	# add_selected_steps                                                 #
	#                                                                    #
	######################################################################
	def add_selected_steps(self, selected_steps_up = None, selected_steps_down = None):
		"""Add the selected steps
		
		This method takes 2 optional arguments:
		  selected_steps_up  (optional) the selected steps up;
		  selected_steps_up  (optional) the selected steps down.
		
		By default, the steps selected by select_steps are added."""
		
		if selected_steps_up is None:
			selected_steps_up = self.selected_steps_up
		if selected_steps_down is None:
			selected_steps_down = self.selected_steps_down
		
		# If no step is selected, immediatly return
		if selected_steps_up == [] and selected_steps_down == []:
			return
		
		# Make a list of steps to add.
		steps_to_add = []
		for i_step in range(len(selected_steps_up)):
			steps_to_add.append(self.steps_up[selected_steps_up[i_step]])
		for i_step in range(len(selected_steps_down)):
			steps_to_add.append(self.steps_down[selected_steps_down[i_step]])
		
		# Sort the steps in decreasing order of layer and position in
		# a step. First sort by position than by layer. This order
		# greatly simplify the task to insert the steps since the
		# layer numbers of subsequent steps will still be ok.
		steps_to_add.sort(key = operator.itemgetter(1), reverse = True)
		steps_to_add.sort(key = operator.itemgetter(0), reverse = True)
		
		for step in steps_to_add:
			layer_nb = step[0]
			position = step[1]
			
			original_thickness = self.front_thickness[layer_nb]
			
			# Seperate the layer.
			self.front_layers.insert(layer_nb+1, self.front_layers[layer_nb])
			self.front_layer_descriptions.insert(layer_nb+1, [])
			self.front_thickness.insert(layer_nb+1, original_thickness-position)
			self.front_index.insert(layer_nb+1, self.front_index[layer_nb])
			self.front_step_profiles.insert(layer_nb+1, [])
			self.refine_thickness.insert(layer_nb+1, self.refine_thickness[layer_nb])
			self.refine_index.insert(layer_nb+1, 1)
			self.preserve_OT.insert(layer_nb+1, self.preserve_OT[layer_nb])
			self.add_needles_in_layer.insert(layer_nb+1, self.add_needles_in_layer[layer_nb])
			self.add_steps_in_layer.insert(layer_nb+1, 1)
			if self.preserve_OT[layer_nb+1]:
				self.OT.insert(layer_nb+1, self.front_thickness[layer_nb+1]*self.front_index[layer_nb+1])
			else:
				self.OT.insert(layer_nb+1, 0.0)
			
			# Change the remaining part of the layer.
			self.front_layer_descriptions[layer_nb] = []
			self.front_thickness[layer_nb] = position
			if self.preserve_OT[layer_nb]:
				self.OT[layer_nb] = self.front_thickness[layer_nb]*self.front_index[layer_nb]
			
			# Increase the number of front layers.
			self.nb_front_layers += 1
		
		self.add_parameters()
	
	
	######################################################################
	#                                                                    #
	# add_steps_                                                         #
	#                                                                    #
	######################################################################
	def add_steps_(self):
		"""Add steps
		
		This method calculates the steps, select the best ones and add
		them."""
		
		self.calculate_steps()
		self.select_steps()
		self.add_selected_steps()
		
		self.just_added_steps = True
		
		self.just_removed_thin_layers = False
	
	
	######################################################################
	#                                                                    #
	# add_steps                                                          #
	#                                                                    #
	######################################################################
	def add_steps(self):
		"""Add steps
		
		This method calculates the steps, select the best ones and add
		them.
		
		This method calls add_steps_ and updates the user interface."""
		
		self.working = True
		self.can_stop = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		self.add_steps_()
		
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
			self.just_added_steps = False
			self.can_add_steps = True
		
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
			self.just_added_steps = False
			self.can_add_steps = True
	
	
	######################################################################
	#                                                                    #
	# go                                                                 #
	#                                                                    #
	######################################################################
	def go(self):
		"""Optimize the filter
		
		This method optimizes the filter until it is not possible to add
		any more steps.
		
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
				
				self.just_added_steps = False
				
				if self.parent:
					self.parent.update(self.working, self.status)
				
				# If layer with finite thickness were removed, it may now be
				# possible to add steps. Furthermore, the filter it not
				# optimal and needs to be refined again, so we go back to the
				# beginning of the loop.
				if self.min_thickness != 0.0:
					self.can_add_steps = True
					continue
			
			if not self.continue_optimization: break
			if not self.automatic_mode: break
			
			if self.parent:
				self.parent.update(self.working, self.status)
			
			# Add steps
			self.add_steps_()
			
			if not self.can_add_steps: break
			
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
		
		return self.dMF_depths, self.dMF_up, self.dMF_down, self.step_up_depths, self.step_up_values, self.step_down_depths, self.step_down_values
	
	
	######################################################################
	#                                                                    #
	# get_selected_steps                                                 #
	#                                                                    #
	######################################################################
	def get_selected_steps(self):
		"""Get the selected steps
		
		This method returns the selected steps."""
		
		return self.selected_steps_up, self.selected_steps_down
	
	
	######################################################################
	#                                                                    #
	# get_can_add_steps                                                  #
	#                                                                    #
	######################################################################
	def get_can_add_steps(self):
		"""Get if it is possible to add needles
		
		This method returns a boolean indicating if it is possible to add
		steps."""
		
		# If chi square is ok, it is useless to add steps.
		if self.status == Levenberg_Marquardt.CHI_2_IS_OK:
			return False
		
		return self.can_add_steps
	
	
	######################################################################
	#                                                                    #
	# get_just_added_steps                                               #
	#                                                                    #
	######################################################################
	def get_just_added_steps(self):
		"""Get if it steps were just added
		
		This method returns a boolean indicating if the instance just added
		steps and no other operation has been done since."""
		
		return self.just_added_steps
	
	
	######################################################################
	#                                                                    #
	# specific_save                                                      #
	#                                                                    #
	######################################################################
	def specific_save(self, outfile):
		"""Save the derivative of the merit function
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		outfile.write("%10s  %20s  %20s\n" %("depth", "step up", "step down"))
		for i_parameter in range(len(self.nb_steps_per_layer)):
			for i_step in range(self.nb_steps_per_layer[i_parameter]):
				outfile.write("%10.2f  %20.12f  %20.12f\n" %(self.dMF_depths[i_parameter][i_step], self.dMF_up[i_parameter][i_step], self.dMF_down[i_parameter][i_step]))
		
		outfile.write("\n\nSteps up:\n\n")
		outfile.write("%10s  %20s\n" % ("depth(nm)", "value"))
		for i_step in range(len(self.step_up_depths)):
			outfile.write("%10.2f  %20.12f\n" % (self.step_up_depths[i_step], self.step_up_values[i_step]))
		
		outfile.write("\n\nSteps down:\n\n")
		outfile.write("%10s  %20s\n" % ("depth(nm)", "value"))
		for i_step in range(len(self.step_down_depths)):
			outfile.write("%10.2f  %20.12f\n" % (self.step_down_depths[i_step], self.step_down_values[i_step]))
