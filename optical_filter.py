# optical_filter.py
# 
# optical_filter class for Filters and helpers functions to read
# and write a filter file.
#
# Copyright (c) 2000-2010,2012,2014,2015 Stephane Larouche.
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



# REMOVE when Python 3.0 will be out.
from __future__ import division

import math
import cmath
import array
import string
import copy
import warnings
import time
try:
	from ast import literal_eval as _eval
except ImportError:
	_eval = eval


from definitions import *
import config
import abeles
import materials
import stack
import graded
import simple_parser
import color
import optimization_Fourier



one_hundred_eighty_over_pi = 180.0/math.pi



########################################################################
#                                                                      #
# filter_error                                                         #
#                                                                      #
########################################################################
class filter_error(Exception):
	"""Exception class for filter errors"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Filter error: %s." % self.value
		else:
			return "Filter error."



########################################################################
#                                                                      #
# optical_filter                                                       #
#                                                                      #
########################################################################
class optical_filter(object):
	"""A class to define an optical filter and calculate its properties."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, material_catalog = None):
		"""Initialize the optical filter
		
		This method takes a single optional input argument:
		  material_catalog   (optional) the catalog of materials to use in
		                     the filter, if omitted, the default materials
		                     are used."""
		
		# If a material catalog is given, use it. Otherwise, use the default
		# materials.
		if material_catalog:
			self.material_catalog = material_catalog
		else:
			self.material_catalog = materials.material_catalog()
		
		# A description of the filter.
		self.description = ""
		
		# Materials used in the filter. If the analysis was done, the
		# indices structures are kept for later use. The 3 different kind
		# of structures are kept in 3 different lists.
		self.materials = []
		self.material_indices = []
		self.N = []
		
		# The angles at which the analysis have already been done and the
		# matrices for the front and back coatings.
		self.sin2_theta_0 = []
		self.matrices_front = []
		self.matrices_back = []
		
		# The center wavelength is the wavelength at which the index
		# profile is defined. By default, the center wavelength is 550nm.
		self.center_wavelength = 550.0
		
		# By default, the analysis is done at every nm betwenn 300 nm and
		# 1000 nm.
		self.from_wavelength = 0.0
		self.to_wavelength = 0.0
		self.by_wavelength = 0.0
		self.wvls = None
		self.set_wavelengths_by_range(300.0, 1000.0, 1.0)
		
		# By default, steps of inhomogeneous layers are separated by
		# index steps of 0.01 and have a minimal thickness of 0 nm.
		self.step_spacing = 0.01
		self.minimum_thickness = 0.0
		
		# Does the analysis consider the back side of the substrate. By
		# default, it does.
		self.consider_backside = True
		
		# Same thing, for monitoring.
		self.consider_backside_on_monitoring = True
		
		# Ellipsometer type is used to determine Delta. Possible values
		# are RAE for a rotating analyser, RPE for a rotating polarizer
		# ellipsometer and RCE for a rotating compensator ellipsometer. By
		# default, a RAE is used as a J. A. Woollam VASE. The minimum
		# possible value of Delta, this is used to express Delta between 0
		# degres and 360 degres, -180 degres and +180 degres or any other
		# values between -180 and 0 degres. By default, the minimum value
		# is -90 degres as for J. A. Woollam Co. ellipsometers.
		self.ellipsometer_type = RAE
		self.Delta_min = -90.0
		
		# Same thing, for monitoring.
		self.monitoring_ellipsometer_type = RAE
		self.monitoring_Delta_min = -90.0
		
		# What illuminant and what colorimetric observer are used to
		# calculate the color.
		self.observer_name = config.OBSERVER
		self.illuminant_name = config.ILLUMINANT
		
		# The maximum thickness of the sublayers for the monitoring and
		# for the circle and admitance diagrams. By default, 1nm.
		self.monitoring_sublayer_thickness = 1.0
		
		# For special cases where you don't want to consider the substrate.
		self.dont_consider_substrate = False
		
		# The stack formula and its list of materials.
		self.front_stack_formula = ""
		self.front_stack_materials = {}
		self.back_stack_formula = ""
		self.back_stack_materials = {}
		
		# The materials of the medium, the substrate and the coating, the
		# thickness of the layers of the coating (a list for an
		# inhomogeneous layer) and the index of mixture layers (at the
		# center wavelength, only the real part) or a lists of steps for
		# graded-index layers. By default, there is no coating, the
		# substate is fused silica and 1mm (1000000nm) thick and the medium
		# is void. The descriptions allows the possibility to describe each
		# layer so that the module used to create it can be re-executed to
		# recreate it. The description of each layer can be an empty list,
		# or a list of two elements, the first one being the name of the
		# module that was used to create the layer and the second one being
		# a tuple of the parematers used by the module to create the layer.
		self.substrate = self.get_material_nb("FusedSilica")
		self.substrate_thickness = 1000000.0
		self.front_medium = self.get_material_nb("void")
		self.front_layers = []
		self.front_layer_descriptions = []
		self.front_thickness = []
		self.front_step_profiles = []
		self.front_index = []
		self.back_medium = self.get_material_nb("void")
		self.back_layers = []
		self.back_layer_descriptions = []
		self.back_thickness = []
		self.back_step_profiles = []
		self.back_index = []
		
		# Lists indicating if the thickness and the index should be refined
		# and if needles and steps should be added in a layer. 
		self.front_refine_thickness = []
		self.back_refine_thickness = []
		self.front_refine_index = []
		self.back_refine_index = []
		self.front_preserve_OT = []
		self.back_preserve_OT = []
		self.front_add_needles = []
		self.back_add_needles = []
		self.front_add_steps = []
		self.back_add_steps = []
		
		# The wavelengths at which the monitoring have been calculated and
		# the refractive indices at those wavelengths.
		self.monitoring_wvls = []
		self.monitoring_n = []
		
		# Saved matrices for monitoring conditions and the thicknesses for
		# those matrices.
		self.monitoring_sin2_theta_0 = []
		self.monitoring_thicknesses = []
		self.monitoring_matrices_front = []
		self.monitoring_matrices_back = []
		
		# The materials to use for needles and for the Fourier transform
		# method.
		self.needle_materials = None
		self.Fourier_parameters = None
		
		# The progress of the current operation.
		self.progress = 0.0
		
		# Set this true if you want to cancel an operation.
		self.stop_ = False
		
		# Remember if the filter was modified.
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the filter
		
		This method returns a clone of the filter."""
		
		clone = self.__class__(self.material_catalog)
		
		clone.set_description(self.description)
		clone.set_center_wavelength(self.center_wavelength)
		if self.from_wavelength:
			clone.set_wavelengths_by_range(self.from_wavelength, self.to_wavelength, self.by_wavelength)
		else:
			clone.set_wavelengths(self.wvls)
		clone.set_step_spacing(self.step_spacing)
		clone.set_minimum_thickness(self.minimum_thickness)
		clone.set_consider_backside(self.consider_backside)
		clone.set_consider_backside_on_monitoring(self.consider_backside_on_monitoring)
		clone.set_ellipsometer_type(self.ellipsometer_type)
		clone.set_Delta_min(self.Delta_min)
		clone.set_monitoring_ellipsometer_type(self.monitoring_ellipsometer_type)
		clone.set_monitoring_Delta_min(self.monitoring_Delta_min)
		clone.set_observer(self.observer_name)
		clone.set_illuminant(self.illuminant_name)
		clone.set_monitoring_sublayer_thickness(self.monitoring_sublayer_thickness)
		clone.set_dont_consider_substrate(self.dont_consider_substrate)
		clone.set_substrate(self.materials[self.substrate].get_name())
		clone.set_substrate_thickness(self.substrate_thickness)
		clone.set_medium(self.materials[self.front_medium].get_name(), FRONT)
		clone.set_medium(self.materials[self.back_medium].get_name(), BACK)
		if self.front_stack_formula:
			clone.set_stack_formula(self.front_stack_formula, self.front_stack_materials, FRONT)
		if self.back_stack_formula:
			clone.set_stack_formula(self.back_stack_formula, self.back_stack_materials, BACK)
		for i in range(len(self.front_layers)):
			material = self.materials[self.front_layers[i]]
			material_name = material.get_name()
			if self.front_step_profiles[i]:
				clone.add_graded_layer_from_steps(material_name, self.front_step_profiles[i], self.front_thickness[i], TOP, FRONT, description = self.front_layer_descriptions[i])
			elif material.is_mixture():	
				clone.add_layer(material_name, self.front_thickness[i], TOP, FRONT, index = self.front_index[i], description = self.front_layer_descriptions[i])
				clone.set_refine_layer_thickness(i, self.front_refine_thickness[i], FRONT)
				clone.set_refine_layer_index(i, self.front_refine_index[i], FRONT)
				clone.set_preserve_OT(i, self.front_preserve_OT[i], FRONT)
				clone.set_add_needles(i, self.front_add_needles[i], FRONT)
				clone.set_add_steps(i, self.front_add_steps[i], FRONT)
			else:
				clone.add_layer(material_name, self.front_thickness[i], TOP, FRONT, description = self.front_layer_descriptions[i])
				clone.set_refine_layer_thickness(i, self.front_refine_thickness[i], FRONT)
				clone.set_add_needles(i, self.front_add_needles[i], FRONT)
		for i in range(len(self.back_layers)):
			material = self.materials[self.back_layers[i]]
			material_name = material.get_name()
			if self.back_step_profiles[i]:
				clone.add_graded_layer_from_steps(material_name, self.back_step_profiles[i], self.back_thickness[i], TOP, BACK, description = self.back_layer_descriptions[i])
			elif material.is_mixture():	
				clone.add_layer(material_name, self.back_thickness[i], TOP, BACK, index = self.back_index[i], description = self.back_layer_descriptions[i])
				clone.set_refine_layer_thickness(i, self.back_refine_thickness[i], BACK)
				clone.set_refine_layer_index(i, self.back_refine_index[i], BACK)
				clone.set_preserve_OT(i, self.back_preserve_OT[i], BACK)
				clone.set_add_needles(i, self.back_add_needles[i], BACK)
				clone.set_add_steps(i, self.back_add_steps[i], BACK)
			else:
				clone.add_layer(material_name, self.back_thickness[i], TOP, BACK, description = self.back_layer_descriptions[i])
				clone.set_refine_layer_thickness(i, self.back_refine_thickness[i], BACK)
				clone.set_add_needles(i, self.back_add_needles[i], BACK)
		if self.needle_materials:
			clone.set_needle_materials(self.needle_materials)
		if self.Fourier_parameters:
			clone.set_Fourier_parameters(self.Fourier_parameters)
		
		clone.set_modified(False)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# get_material_catalog                                               #
	#                                                                    #
	######################################################################
	def get_material_catalog(self):
		"""Get the material catalog used by the filter
		
		This method returns the material catalog of the filter."""
		
		return self.material_catalog
	
	
	######################################################################
	#                                                                    #
	# set_description                                                    #
	#                                                                    #
	######################################################################
	def set_description(self, description):
		"""Set the description of the filter
		
		This method takes a single input argument:
		  description        the description."""
		
		if description != self.description:
			self.description = description
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_description                                                    #
	#                                                                    #
	######################################################################
	def get_description(self):
		"""Get the description of the filter
		
		This method returns the description of the filter."""
		
		return self.description
	
	
	######################################################################
	#                                                                    #
	# set_center_wavelength                                              #
	#                                                                    #
	######################################################################
	def set_center_wavelength(self, center_wavelength):
		"""Set the center wavelength of the filter
		
		This method takes a single input argument:
		  center_wavelength  the center wavelength.
		
		The center wavelengths serves as a reference when giving the index
		of refraction of a layer and to calculate its optical thickness.
		
		It is necessary that all the mixtures used are monotone at the new
		center wavelength. Thie method checks this and raises an error if
		the refractive index is not monotone. An error may also occur when
		graded-index layers are converted to a new center wavelength. If
		either errors are raised, this method guaranties that the optical
		filter instance is not modified. The caller is left responsible to
		decide what to do with the error."""
		
		if center_wavelength != self.center_wavelength:
			
			new_material_indices = [None]*len(self.materials)
			
			# Calculate new material indices.
			for i_mat in range(len(self.materials)):
				if self.materials[i_mat].is_mixture():
					if not self.materials[i_mat].check_monotonicity(center_wavelength):
						raise materials.material_error("Refractive index is not monotonic at reference wavelength")
					new_material_indices[i_mat] = graded.calculate_steps(self.materials[i_mat], self.step_spacing, center_wavelength)
				else:
					new_material_indices[i_mat] = self.materials[i_mat].get_index(center_wavelength)
			
			# Try to convert step profiles.
			
			filter_has_graded_index_layers = False
			
			nb_front_layers = len(self.front_layers)
			new_front_thickness = [None]*nb_front_layers
			new_front_step_profiles = [None]*nb_front_layers
			new_front_index = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
				if self.is_graded(i_layer, FRONT):
					filter_has_graded_index_layers = True
					new_front_step_profiles[i_layer], new_front_thickness[i_layer] = graded.change_step_profile(self.materials[self.front_layers[i_layer]], self.front_step_profiles[i_layer], self.front_thickness[i_layer], self.material_indices[self.front_layers[i_layer]], self.center_wavelength, new_material_indices[self.front_layers[i_layer]], center_wavelength, self.minimum_thickness)
					new_front_index[i_layer] = graded.steps_to_index(new_front_step_profiles[i_layer], new_material_indices[self.front_layers[i_layer]])
				elif self.materials[self.front_layers[i_layer]].is_mixture():
					new_front_thickness[i_layer] = self.front_thickness[i_layer]
					new_front_index[i_layer] = self.materials[self.front_layers[i_layer]].change_index_wavelength(self.front_index[i_layer], self.center_wavelength, center_wavelength)
				else:
					new_front_thickness[i_layer] = self.front_thickness[i_layer]
					new_front_index[i_layer] = new_material_indices[self.front_layers[i_layer]]
			
			nb_back_layers = len(self.back_layers)
			new_back_thickness = [None]*nb_back_layers
			new_back_step_profiles = [None]*nb_back_layers
			new_back_index = [None]*nb_back_layers
			for i_layer in range(nb_back_layers):
				if self.is_graded(i_layer, BACK):
					filter_has_graded_index_layers = True
					new_back_step_profiles[i_layer], new_back_thickness[i_layer] = graded.change_step_profile(self.materials[self.back_layers[i_layer]], self.back_step_profiles[i_layer], self.back_thickness[i_layer], self.material_indices[self.back_layers[i_layer]], self.center_wavelength, new_material_indices[self.back_layers[i_layer]], center_wavelength, self.minimum_thickness)
					new_back_index[i_layer] = graded.steps_to_index(new_back_step_profiles[i_layer], new_material_indices[self.back_layers[i_layer]])
				elif self.materials[self.back_layers[i_layer]].is_mixture():
					new_back_thickness[i_layer] = self.back_thickness[i_layer]
					self.back_index[i_layer] = self.materials[self.back_layers[i_layer]].change_index_wavelength(self.back_index[i_layer], old_center_wavelength, self.center_wavelength)
				else:
					new_back_thickness[i_layer] = self.back_thickness[i_layer]
					self.back_index[i_layer] = self.material_indices[self.back_layers[i_layer]]
			
			# If no error occured, we can now safely save modified values in
			# class attributes.
			self.center_wavelength = center_wavelength
			self.material_indices = new_material_indices
			self.front_thickness = new_front_thickness
			self.front_step_profiles = new_front_step_profiles
			self.front_index = new_front_index
			self.back_thickness = new_back_thickness
			self.back_step_profiles = new_back_step_profiles
			self.back_index = new_back_index
			
			# If there are graded-index layers, their steps have been
			# modified: indices, monitoring and analysis must be
			# recalculated.
			if filter_has_graded_index_layers:
				self.reset_n()
				self.reset_analysis()
				self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_center_wavelength                                              #
	#                                                                    #
	######################################################################
	def get_center_wavelength(self):
		"""Get the center wavelength of the filter
		
		This method returns the center wavelength."""
		
		return self.center_wavelength
	
	
	######################################################################
	#                                                                    #
	# set_wavelengths                                                    #
	#                                                                    #
	######################################################################
	def set_wavelengths(self, wavelengths):
		"""Set the wavelengths of the filter
		
		This method takes a single input argument:
		  wavelengths        a list of wavelengths.
		
		The wavelengths are used in the calculation of all the properties
		of the filter, except color."""
		
		if wavelengths != self.wvls:
			self.from_wavelength = 0.0
			self.to_wavelength = 0.0
			self.by_wavelength = 0.0
			
			self.reset_n()
			self.reset_analysis()
			
			nb_wvls = len(wavelengths)
			self.wvls = abeles.wvls(nb_wvls)
			for i in range(nb_wvls):
				self.wvls.set_wvl(i, wavelengths[i])
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_wavelengths                                                    #
	#                                                                    #
	######################################################################
	def get_wavelengths(self):
		"""Get the wavelengths of the filter
		
		This method returns the list of the wavelengths used in
		calculations."""
		
		return self.wvls
	
	
	######################################################################
	#                                                                    #
	# set_wavelengths_by_range                                           #
	#                                                                    #
	######################################################################
	def set_wavelengths_by_range(self, from_wavelength, to_wavelength, by_wavelength):
		"""Set the wavelengths of the filter using a range
		
		This method takes 3 arguments:
		  from_wavelength    the lowest limit of the range;
		  to_wavelength      the largets limit of the range;
		  by_wavelength      the increment inside of the range.
		
		If the range is not exactly divisible by the increment, the last
		interval will be smaller."""
		
		if from_wavelength != self.from_wavelength or to_wavelength != self.to_wavelength or by_wavelength != self.by_wavelength:
			self.from_wavelength = from_wavelength
			self.to_wavelength = to_wavelength
			self.by_wavelength = by_wavelength
			
			self.reset_n()
			self.reset_analysis()
			
			nb_wvls = int(math.ceil((self.to_wavelength-self.from_wavelength)/self.by_wavelength)+1)
			self.wvls = abeles.wvls(nb_wvls)
			self.wvls.set_wvls_by_range(self.from_wavelength, self.by_wavelength)
			self.wvls.set_wvl(nb_wvls-1, self.to_wavelength)
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_wavelengths_by_range                                           #
	#                                                                    #
	######################################################################
	def get_wavelengths_by_range(self):
		"""Set the range of wavelengths
		
		This method returns 3 arguments:
		  from_wavelength    the lowest limit of the range;
		  to_wavelength      the largets limit of the range;
		  by_wavelength      the increment inside of the range."""
		
		return self.from_wavelength, self.to_wavelength, self.by_wavelength
	
	
	######################################################################
	#                                                                    #
	# set_step_spacing                                                   #
	#                                                                    #
	######################################################################
	def set_step_spacing(self, step_spacing):
		"""Set the step spacing used in graded-index layers
		
		This method takes a single input argument:
		  step_spacing       the step spacing.
		
		The step spacing is the spacing, in index of refraction, used in
		the discretization of graded-index layers. When a material is used
		in a graded-index layers, a list of index of refraction exactly
		divisible and seperated by the step spacing is done. Depending on
		the range of index of refraction of the material, the first and
		last steps might not be divisible by the step spacing.
		
		The discretization is done to this list of index of refraction
		instead of creating a list of layers of all the same thickness to
		speed up the calculation. This way, it is only necessary to
		calculate the dispersion of the index of refraction of a limited
		number of mixtures instead of having to calculate it for every
		step.
		
		An error may occur when graded-index layers are converted to a new
		step spacing. If such an error is raised, this method guaranties
		that the optical filter instance is not modified. The caller is
		left responsible to decide what to do with the error."""
		
		if step_spacing != self.step_spacing:
			
			new_material_indices = [None]*len(self.materials)
			
			for i_mat in range(len(self.materials)):
				if self.materials[i_mat].is_mixture():
					new_material_indices[i_mat] = graded.calculate_steps(self.materials[i_mat], step_spacing, self.center_wavelength)
				else:
					new_material_indices[i_mat] = self.material_indices[i_mat]
			
			# Try to convert step profiles.
			
			filter_has_graded_index_layers = False
			
			nb_front_layers = len(self.front_layers)
			new_front_thickness = [None]*nb_front_layers
			new_front_step_profiles = [None]*nb_front_layers
			new_front_index = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
				if self.is_graded(i_layer, FRONT):
					filter_has_graded_index_layers = True
					new_front_step_profiles[i_layer], new_front_thickness[i_layer] = graded.change_step_profile(self.materials[self.front_layers[i_layer]], self.front_step_profiles[i_layer], self.front_thickness[i_layer], self.material_indices[self.front_layers[i_layer]], self.center_wavelength, new_material_indices[self.front_layers[i_layer]], self.center_wavelength, self.minimum_thickness)
					new_front_index[i_layer] = graded.steps_to_index(new_front_step_profiles[i_layer], new_material_indices[self.front_layers[i_layer]])
				else:
					new_front_thickness[i_layer] = self.front_thickness[i_layer]
					new_front_index[i_layer] = self.front_index[i_layer]
			
			nb_back_layers = len(self.back_layers)
			new_back_thickness = [None]*nb_back_layers
			new_back_step_profiles = [None]*nb_back_layers
			new_back_index = [None]*nb_back_layers
			for i_layer in range(nb_back_layers):
				if self.is_graded(i_layer, BACK):
					filter_has_graded_index_layers = True
					new_back_step_profiles[i_layer], new_back_thickness[i_layer] = graded.change_step_profile(self.materials[self.back_layers[i_layer]], self.back_step_profiles[i_layer], self.back_thickness[i_layer], self.material_indices[self.back_layers[i_layer]], self.center_wavelength, new_material_indices[self.back_layers[i_layer]], self.center_wavelength, self.minimum_thickness)
					new_back_index[i_layer] = graded.steps_to_index(new_back_step_profiles[i_layer], new_material_indices[self.back_layers[i_layer]])
				else:
					new_back_thickness[i_layer] = self.back_thickness[i_layer]
					new_back_index[i_layer] = self.back_index[i_layer]
			
			# If no error occured, we can now safely save modified values in
			# class attributes.
			self.step_spacing = step_spacing
			self.material_indices = new_material_indices
			self.front_thickness = new_front_thickness
			self.front_step_profiles = new_front_step_profiles
			self.front_index = new_front_index
			self.back_thickness = new_back_thickness
			self.back_step_profiles = new_back_step_profiles
			self.back_index = new_back_index
			
			# If there are graded-index layers, their steps have been
			# modified: indices, monitoring and analysis must be
			# recalculated.
			if filter_has_graded_index_layers:
				self.reset_n()
				self.reset_analysis()
				self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_step_spacing                                                   #
	#                                                                    #
	######################################################################
	def get_step_spacing(self):
		"""Set the step spacing used in graded-index layers
		
		This methon returns the step spacing used in graded-index layers."""
		
		return self.step_spacing
	
	
	######################################################################
	#                                                                    #
	# set_minimum_thickness                                              #
	#                                                                    #
	######################################################################
	def set_minimum_thickness(self, minimum_thickness):
		"""Set the minimum thickness of sublayers in graded-indexlayers
		
		This function takes a singler input argument:
		  minimum_thickness  the minimum thickness.
		
		Since the discretization of graded-index layer is done by index, it
		might create very thin layers in the regions where the index
		changes rapidly. By imposing a minimal thickness, it is possible to
		avoid this problem.
		
		An error may occur when graded-index layers are converted to a new
		minimum thickness. If such an error is raised, this method
		guaranties that the optical filter instance is not modified. The
		caller is left responsible to decide what to do with the error."""
		
		if minimum_thickness != self.minimum_thickness:
			
			# Try to convert step profiles.
			
			filter_has_graded_index_layers = False
			
			nb_front_layers = len(self.front_layers)
			new_front_thickness = [None]*nb_front_layers
			new_front_step_profiles = [None]*nb_front_layers
			new_front_index = [None]*nb_front_layers
			for i_layer in range(len(self.front_layers)):
				if self.is_graded(i_layer, FRONT):
					filter_has_graded_index_layers = True
					new_front_step_profiles[i_layer], new_front_thickness[i_layer] = graded.change_step_profile(self.materials[self.front_layers[i_layer]], self.front_step_profiles[i_layer], self.front_thickness[i_layer], self.material_indices[self.front_layers[i_layer]], self.center_wavelength, self.material_indices[self.front_layers[i_layer]], self.center_wavelength, minimum_thickness)
					new_front_index[i_layer] = graded.steps_to_index(new_front_step_profiles[i_layer], self.material_indices[self.front_layers[i_layer]])
				else:
					new_front_thickness[i_layer] = self.front_thickness[i_layer]
					new_front_index[i_layer] = self.front_index[i_layer]
			
			nb_back_layers = len(self.back_layers)
			new_back_thickness = [None]*nb_back_layers
			new_back_step_profiles = [None]*nb_back_layers
			new_back_index = [None]*nb_back_layers
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					filter_has_graded_index_layers = True
					new_back_step_profiles[i_layer], new_back_thickness[i_layer] = graded.change_step_profile(self.materials[self.back_layers[i_layer]], self.back_step_profiles[i_layer], self.back_thickness[i_layer], self.material_indices[self.back_layers[i_layer]], self.center_wavelength, self.material_indices[self.back_layers[i_layer]], self.center_wavelength, minimum_thickness)
					new_back_index[i_layer] = graded.steps_to_index(new_back_step_profiles[i_layer], self.material_indices[self.back_layers[i_layer]])
				else:
					new_back_thickness[i_layer] = self.back_thickness[i_layer]
					new_back_index[i_layer] = self.back_index[i_layer]
			
			# If no error occured, we can now safely save modified values in
			# class attributes.
			self.minimum_thickness = minimum_thickness
			self.front_thickness = new_front_thickness
			self.front_step_profiles = new_front_step_profiles
			self.front_index = new_front_index
			self.back_thickness = new_back_thickness
			self.back_step_profiles = new_back_step_profiles
			self.back_index = new_back_index
			
			# If there are graded-index layers, their steps have been
			# modified: monitoring and analysis must be recalculated.
			if filter_has_graded_index_layers:
				self.reset_analysis()
				self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_minimum_thickness                                              #
	#                                                                    #
	######################################################################
	def get_minimum_thickness(self):
		"""Get the minimum thickness of sublayers in graded-index layers
		
		This method returns the mimimum thickness of sublayer in
		graded-index layers."""
		
		return self.minimum_thickness
	
	
	######################################################################
	#                                                                    #
	# set_monitoring_sublayer_thickness                                  #
	#                                                                    #
	######################################################################
	def set_monitoring_sublayer_thickness(self, monitoring_sublayer_thickness):
		"""Set the monitoring sublayer thickness
		
		This function takes a singler input argument:
		  monitoring_sublayer_thickness   the sublayer thickness.
		
		When calculating a monitoring curve, the homogeneous layers are
		calculated every sublayer thickess."""
		
		if monitoring_sublayer_thickness != self.monitoring_sublayer_thickness:
			self.monitoring_sublayer_thickness = monitoring_sublayer_thickness
			
			self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_monitoring_sublayer_thickness                                  #
	#                                                                    #
	######################################################################
	def get_monitoring_sublayer_thickness(self):
		"""Get the monitoring sublayer thickness
		
		This method returns the sublayer thickness used in the calculation
		of monitoring curves."""
		
		return self.monitoring_sublayer_thickness
	
	
	######################################################################
	#                                                                    #
	# set_consider_backside                                              #
	#                                                                    #
	######################################################################
	def set_consider_backside(self, consider_backside):
		"""Set the consideration of backside
		
		This method takes a single input argument:
		  consider backside     a boolean indicating if the backside should
		                        be considered during the calculation of the
		                        properties.
		
		If the backside is not considered, the substate is considered
		semi-infinite."""
		
		if self.dont_consider_substrate:
			return
		
		if consider_backside != self.consider_backside:
			self.consider_backside = consider_backside
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_consider_backside                                              #
	#                                                                    #
	######################################################################
	def get_consider_backside(self):
		"""Get the consideration of backside
		
		This function returns a boolean value indicating if the backside is
		considered during calculations."""
		
		return self.consider_backside
	
	
	######################################################################
	#                                                                    #
	# set_consider_backside_on_monitoring                                #
	#                                                                    #
	######################################################################
	def set_consider_backside_on_monitoring(self, consider_backside_on_monitoring):
		"""Set the consideration of backside on monitoring
		
		This method takes a single input argument:
		  consider_backside_on_monitoring     a boolean indicating if the
		                                      backside should be considered
		                                      during the calculation of the
		                                      monitoring curves.
		
		If the backside is not considered, the substate is considered
		semi-infinite."""
		
		if self.dont_consider_substrate:
			return
		
		if consider_backside_on_monitoring != self.consider_backside_on_monitoring:
			self.consider_backside_on_monitoring = consider_backside_on_monitoring
			
			self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_consider_backside_on_monitoring                                #
	#                                                                    #
	######################################################################
	def get_consider_backside_on_monitoring(self):
		"""Get the consideration of backside on monitoring
		
		This function returns a boolean value indicating if the backside is
		considered during monitoring."""
		
		return self.consider_backside_on_monitoring
	
	
	######################################################################
	#                                                                    #
	# set_ellipsometer_type                                              #
	#                                                                    #
	######################################################################
	def set_ellipsometer_type(self, ellipsometer_type):
		"""Set the ellipsometer type
		
		This method takes a single input argument:
		  ellipsometer_type       the type of ellipsometer (RAE, RPE or
		                          RCE).
		
		Depending on the type of ellipsometer, Delta is defined over a full
		360 degres (RCE), or over only 180 degres (RAE or RCE)."""
		
		if ellipsometer_type != self.ellipsometer_type:
			self.ellipsometer_type = ellipsometer_type
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_ellipsometer_type                                              #
	#                                                                    #
	######################################################################
	def get_ellipsometer_type(self):
		"""Get the ellipsometer type
		
		This method returns the ellipsometer type."""
		
		return self.ellipsometer_type
	
	
	######################################################################
	#                                                                    #
	# set_Delta_min                                                      #
	#                                                                    #
	######################################################################
	def set_Delta_min(self, Delta_min):
		"""Set the minimum Delta for ellipsometric calculations
		
		This method takes a single input argument:
		  Delta_min          the minimum Delta.
		
		When Delta is defined over a 360 degres range, different
		conventions define it between -180 and +180 degres or 0 and 360
		degres."""
		
		if Delta_min != self.Delta_min:
			self.Delta_min = Delta_min
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_Delta_min                                                      #
	#                                                                    #
	######################################################################
	def get_Delta_min(self):
		"""Get the minimum Delta for ellipsometric calculations
		
		This method returns the mimimun Delta used for ellipsometric
		calculations."""
		
		return self.Delta_min
	
	
	######################################################################
	#                                                                    #
	# set_monitoring_ellipsometer_type                                   #
	#                                                                    #
	######################################################################
	def set_monitoring_ellipsometer_type(self, monitoring_ellipsometer_type):
		"""Set the monitoring ellipsometer type
		
		This method takes a single input argument:
		  monitoring_ellipsometer_type   the type of ellipsometer (RAE, RPE
		                                 or RCE).
		
		Depending on the type of ellipsometer, Delta is defined over a full
		360 degres (RCE), or over only 180 degres (RAE or RCE)."""
		
		if monitoring_ellipsometer_type != self.monitoring_ellipsometer_type:
			self.monitoring_ellipsometer_type = monitoring_ellipsometer_type
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_monitoring_ellipsometer_type                                   #
	#                                                                    #
	######################################################################
	def get_monitoring_ellipsometer_type(self):
		"""Get the monitoring ellipsometer type
		
		This method returns the monitoring ellipsometer type."""
		
		return self.monitoring_ellipsometer_type
	
	
	######################################################################
	#                                                                    #
	# set_monitoring_Delta_min                                           #
	#                                                                    #
	######################################################################
	def set_monitoring_Delta_min(self, monitoring_Delta_min):
		"""Set the minimum Delta for ellipsometric monitoring
		
		This method takes a single input argument:
		  monitoring_Delta_min     the minimum Delta.
		
		When Delta is defined over a 360 degres range, different
		conventions define it between -180 and +180 degres or 0 and 360
		degres."""
		
		if monitoring_Delta_min != self.monitoring_Delta_min:
			self.monitoring_Delta_min = monitoring_Delta_min
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_monitoring_Delta_min                                           #
	#                                                                    #
	######################################################################
	def get_monitoring_Delta_min(self):
		"""Get the minimum Delta for ellipsometric monitoring
		
		This method returns the mimimun Delta used for ellipsometric
		monitoring."""
		
		return self.monitoring_Delta_min
	
	
	######################################################################
	#                                                                    #
	# set_dont_consider_substrate                                        #
	#                                                                    #
	######################################################################
	def set_dont_consider_substrate(self, dont_consider_substrate):
		"""Set the consideration of substrate and medium
		
		This method takes a single input argument:
		  dont_consider_substrate    a boolean value indicating if the
		                             substrate and medium should be
		                             considered during the calculation.
		
		It is sometimes usefull to neglect the effect of the boundaries
		between the filter and the substate and the medium. Particularly
		for graded-index filters.
		
		Evidently, when the substrate and medium are not considered, the
		backside cannot be considered, and this method also adjust these
		values."""
		
		if dont_consider_substrate != self.dont_consider_substrate:
			self.dont_consider_substrate = dont_consider_substrate
			if self.dont_consider_substrate:
				self.consider_backside = False
				self.consider_backside_on_monitoring = False
 			
			self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_dont_consider_substrate                                        #
	#                                                                    #
	######################################################################
	def get_dont_consider_substrate(self):
		"""Get the consideration of substrate and medium
		
		This method returns a boolean value indicating if the substrate and
		mediums are considered."""
		
		return self.dont_consider_substrate
	
	
	######################################################################
	#                                                                    #
	# set_illuminant                                                     #
	#                                                                    #
	######################################################################
	def set_illuminant(self, illuminant_name):
		"""Set the default illuminant
		
		This method takes a single input argument:
		  illuminant_name    the name of the default illuminant used for
		                     color calculations.
		
		This illuminant is used when no illuminant is given to the methods
		calculating the color."""
		
		if illuminant_name != self.illuminant_name:
			self.illuminant_name = illuminant_name
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_illuminant                                                     #
	#                                                                    #
	######################################################################
	def get_illuminant(self):
		"""Get the default illuminant
		
		This method returns the name of the default illuminant."""
		
		return self.illuminant_name
	
	
	######################################################################
	#                                                                    #
	# set_observer                                                       #
	#                                                                    #
	######################################################################
	def set_observer(self, observer_name):
		"""Set the default observer
		
		This method takes a single input argument:
		  observer_name      the name of the default observer used for
		                     color calculations.
		
		This observer is used when no observer is given to the methods
		calculating the color."""
		
		if observer_name != self.observer_name:
			self.observer_name = observer_name
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_observer                                                       #
	#                                                                    #
	######################################################################
	def get_observer(self):
		"""Get the default observer
		
		This method returns the name of the default observer."""
		
		return self.observer_name
	
	
	######################################################################
	#                                                                    #
	# get_material_nb                                                    #
	#                                                                    #
	######################################################################
	def get_material_nb(self, material_name):
		"""Get the number of a material in the internal list
		
		This method takes a single input argument:
		  material_name      the name of the material
		and returns the material number.
		
		A list of the material used in the filter is kept to avoid repeated
		calculation of the optical properties. This function returns the
		position in this list of a material. If that material is not in the
		list, it is added to the list.
		
		If the material does not exist or the file is malformed, a
		material_error is raised."""
		
		# Check if the material is already used in this filter. Also check
		# if the steps used in the material correspond to the actual
		# settings. Add the material if necessary. Note the position in
		# the list.
		for material_nb in range(len(self.materials)):
			if material_name == self.materials[material_nb].get_name():
				break
		else:
			# The following operation might raise exceptions. this is why we
			# perform them seperatly from adding them to the properties of
			# the filter. Do not catch errors, let the calling function take
			# care of that.
			new_material = self.material_catalog.get_material(material_name)
			if new_material.is_mixture():
				if not new_material.check_monotonicity(self.center_wavelength):
					raise materials.material_error("Refractive index is not monotonic at reference wavelength")
				new_material_indices = graded.calculate_steps(new_material, self.step_spacing, self.center_wavelength)
			else:
				new_material_indices = new_material.get_index(self.center_wavelength)
			
			self.materials.append(new_material)
			self.material_indices.append(new_material_indices)
			self.N.append(None)
			
			material_nb = len(self.materials) - 1
		
		return material_nb
	
	
	######################################################################
	#                                                                    #
	# get_material                                                       #
	#                                                                    #
	######################################################################
	def get_material(self, material_nb):
		"""Get the material corresponding to a material number
		
		This method takes a single input argument:
		  material_nb        the material number;
		and returns the material."""
		
		return self.materials[material_nb]
	
	
	######################################################################
	#                                                                    #
	# get_material_index                                                 #
	#                                                                    #
	######################################################################
	def get_material_index(self, material_nb):
		"""Get the index of a material in the internal list
		
		This method takes a single input argument:
		  material_nb        the material number;
		and returns the index of refraction of this material. If the
		material is a mixture, the list of steps used for the
		discretization of graded-index filters with this material is used."""
		
		return self.material_indices[material_nb]
	
	
	######################################################################
	#                                                                    #
	# get_materials                                                      #
	#                                                                    #
	######################################################################
	def get_materials(self):
		"""Get the internal list of materials
		
		This method returns the internal list of materials."""
		
		return self.materials
	
	
	######################################################################
	#                                                                    #
	# set_substrate                                                      #
	#                                                                    #
	######################################################################
	def set_substrate(self, substrate_name):
		"""Set the substrate
		
		This method takes a single input argument:
		  substrate_name     the name of the substrate."""
		
		new_substrate = self.get_material_nb(substrate_name)
		
		if self.materials[new_substrate].get_name() != self.materials[self.substrate].get_name():
			self.substrate = new_substrate
			
			self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_substrate                                                      #
	#                                                                    #
	######################################################################
	def get_substrate(self):
		"""Get the substrate
		
		This method returns the name of the substrate."""
		
		return self.materials[self.substrate].get_name()
	
	
	######################################################################
	#                                                                    #
	# set_substrate_thickness                                            #
	#                                                                    #
	######################################################################
	def set_substrate_thickness(self, thickness):
		"""Set the substrate thickness
		
		This method takes a single argument:
		  thickness          the thickness of the substrate."""
		
		if thickness != self.substrate_thickness:
			self.substrate_thickness = thickness
			
			# Reset the monitoring only if the backside is considered.
			if self.consider_backside_on_monitoring:
				self.reset_monitoring()
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_substrate_thickness                                            #
	#                                                                    #
	######################################################################
	def get_substrate_thickness(self):
		"""Get the substrate thickness
		
		This method returns the thickness of the substrate."""
		
		return self.substrate_thickness
	
	
	######################################################################
	#                                                                    #
	# set_medium                                                         #
	#                                                                    #
	######################################################################
	def set_medium(self, medium_name, side = BOTH):
		"""Set one or the two medium
		
		This methon takes 1 or 2 arguments:
		  medium_name        the name of the medium;
		  side               (optional) the side of the medium (FRONT, BACK
		                     or BOTH), the default value is BOTH."""
		
		new_medium = self.get_material_nb(medium_name)
		
		changed = False
		
		if side == FRONT or side == BOTH:
			if self.materials[new_medium].name != self.materials[self.front_medium].name:
				self.front_medium = new_medium
				
				self.reset_monitoring()
				
				changed = True
		
		if side == BACK or side == BOTH:
			if self.materials[new_medium].name != self.materials[self.back_medium].name:
				self.back_medium = new_medium
				
				# Reset the monitoring only if the backside is considered.
				if self.consider_backside_on_monitoring:
					self.reset_monitoring()
				
				changed = True
		
		return changed
	
	
	######################################################################
	#                                                                    #
	# get_medium                                                         #
	#                                                                    #
	######################################################################
	def get_medium(self, side = BOTH):
		"""Get one or the two medium
		
		This methon takes 1 or 2 arguments:
		  side               (optional) the side of the medium (FRONT, BACK
		                     or BOTH), the default value is BOTH;
		and returns the name of the medium(s)."""
		
		if side == FRONT:
			return self.materials[self.front_medium].get_name()
		elif side == BACK:
			return self.materials[self.back_medium].get_name()
		else:
			return self.materials[self.front_medium].get_name(), self.materials[self.back_medium].get_name()
	
	
	######################################################################
	#                                                                    #
	# set_stack_formula                                                  #
	#                                                                    #
	######################################################################
	def set_stack_formula(self, formula, materials, side = FRONT):
		"""Set the stack formula
		
		This method takes 2 to 3 arguments:
		  formula            a string representing the stack formula;
		  materials          a dictionnary of the materials corresponding
		                     to the symbols used in the stack formula;
		  side               (optional) the side of the stack formula
		                     (FRONT or BACK), the default value is FRONT.
		
		This method set the stack formula, but does not actually apply it.
		For that, apply_stack_formula must be called."""
		
		if side == FRONT:
			self.front_stack_formula = formula
			self.front_stack_materials = materials
		elif side == BACK:
			self.back_stack_formula = formula
			self.back_stack_materials = materials
	
	
	######################################################################
	#                                                                    #
	# get_stack_formula                                                  #
	#                                                                    #
	######################################################################
	def get_stack_formula(self, side = FRONT):
		"""Get the stack formula
		
		This method takes an optional argument:
		  side               (optional) the side of the stack formula
		                     (FRONT or BACK), the default value is FRONT;
		and returns 2 output arguments:
		  formula            a string representing the stack formula;
		  materials          a dictionnary of the materials corresponding
		                     to the symbols used in the stack formula."""
	
		if side == FRONT:
			return self.front_stack_formula, self.front_stack_materials
		elif side == BACK:
			return self.back_stack_formula, self.back_stack_materials
	
	
	######################################################################
	#                                                                    #
	# apply_stack_formula                                                #
	#                                                                    #
	######################################################################
	def apply_stack_formula(self, side = FRONT):
		"""Apply the stack formula
		
		This method takes an optional argument:
		  side               (optional) the side of the stack formula
		                     (FRONT or BACK), the default value is FRONT.
		
		It applies the stack formula that was set by set_stack_formula."""
		
		if side == FRONT:
			stack.stack(self, self.front_stack_formula, self.front_stack_materials, FRONT)
		elif side == BACK:
			stack.stack(self, self.back_stack_formula, self.back_stack_materials, BACK)
	
	
	######################################################################
	#                                                                    #
	# add_layer                                                          #
	#                                                                    #
	######################################################################
	def add_layer(self, material_name, thickness, position = TOP, side = FRONT, index = None, OT = False, description = []):
		"""Add an homogeneous layer
		
		This method takes 2 to 7 arguments:
		  material_name      the name of the material of the layer;
		  thickness          the thickness of the layer;
		  position           (optional) the position at which to add the
		                     layer (BOTTOM, TOP or the numeric position);
		  side               (optional) the side on which to add the layer
		                     (FRONT or BACK), the default value is FRONT;
		  index              (optional) the index refraction of the layer
		                     if the material is a mixture;
		  OT                 (optional) a boolean indicating if the
		                     thickness is given in optical thickness, the
		                     default value is False;
		  description        (optional) a description of the layer when
		                     it is created with a module."""
		
		material_nb = self.get_material_nb(material_name)
		
		# If the material is not a mixture, get its index.
		if not self.materials[material_nb].is_mixture():
			index = self.materials[material_nb].get_index(self.center_wavelength)
		
		# If the OT flag is set true, the thickness is an optical
		# thickness.
		if OT:
			thickness /= index
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)
			elif side == BACK:
				position = len(self.back_layers)
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			self.front_layers.insert(position, material_nb)
			self.front_layer_descriptions.insert(position, description)
			self.front_thickness.insert(position, thickness)
			self.front_step_profiles.insert(position, None)
			self.front_index.insert(position, index)
			self.front_refine_thickness.insert(position, True)
			if self.materials[material_nb].is_mixture():
				self.front_refine_index.insert(position, True)
			else:
				self.front_refine_index.insert(position, False)
			self.front_preserve_OT.insert(position, False)
			self.front_add_needles.insert(position, True)
			if self.materials[material_nb].is_mixture():
				self.front_add_steps.insert(position, True)
			else:
				self.front_add_steps.insert(position, False)
 		
		elif side == BACK:
			self.back_layers.insert(position, material_nb)
			self.back_layer_descriptions.insert(position, description)
			self.back_thickness.insert(position, thickness)
			self.back_step_profiles.insert(position, None)
			self.back_index.insert(position, index)
			self.back_refine_thickness.insert(position, False)
			if self.materials[material_nb].is_mixture():
				self.back_refine_index.insert(position, False)
			else:
				self.back_refine_index.insert(position, False)
			self.back_preserve_OT.insert(position, False)
			self.back_add_needles.insert(position, False)
			if self.materials[material_nb].is_mixture():
				self.back_add_steps.insert(position, False)
			else:
				self.back_add_steps.insert(position, False)
		
		self.reset_analysis(side)
		self.reset_monitoring(side)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# add_graded_layer                                                   #
	#                                                                    #
	######################################################################
	def add_graded_layer(self, material_name, index_profile, thickness, position = TOP, side = FRONT, OT = False, description = []):
		"""Add a graded-index layer
		
		This method takes 3 to 7 arguments:
		  material_name      the name of the material of the layer;
		  index_profile      a list of the index of the sublayers;
		  thickness          a list of the thickness of the sublayers;
		  position           (optional) the position at which to add the
		                     layer (BOTTOM, TOP or the numeric position);
		  side               (optional) the side on which to add the layer
		                     (FRONT or BACK), the default value is FRONT;
		  OT                 (optional) a boolean indicating if the
		                     thickness is given in optical thickness, the
		                     default value is False;
		  description        (optional) a description of the layer when
		                     it is created with a module.
		
		The layer is discretized according to steps spacing before
		being added to the filter."""
		
		material_nb = self.get_material_nb(material_name)
		
		# Convert the index profile to a step profile.
		if OT:
			step_profile, modified_thickness = graded.index_profile_in_OT_to_steps(index_profile, thickness, self.material_indices[material_nb], self.minimum_thickness)
		else:
			step_profile, modified_thickness = graded.index_profile_to_steps(index_profile, thickness, self.material_indices[material_nb], self.minimum_thickness)
		
		self.add_graded_layer_from_steps_with_material_nb(material_nb, step_profile, modified_thickness, position, side, description)
	
	
	######################################################################
	#                                                                    #
	# add_graded_layer_from_steps                                        #
	#                                                                    #
	######################################################################
	def add_graded_layer_from_steps(self, material_name, step_profile, thickness, position = TOP, side = FRONT, description = []):
		"""Add a graded-index layer using a step profile
		
		This method takes 3 to 7 arguments:
		  material_name      the name of the material of the layer;
		  step_profile       a list of the steps in the profile;
		  thickness          a list of the thickness of the steps;
		  position           (optional) the position at which to add the
		                     layer (BOTTOM, TOP or the numeric position);
		  side               (optional) the side on which to add the layer
		                     (FRONT or BACK), the default value is FRONT;
		  OT                 (optional) a boolean indicating if the
		                     thickness is given in optical thickness, the
		                     default value is False;
		  description        (optional) a description of the layer when
		                     it is created with a module.
		
		This method takes a list of the steps instead of a list of indices.
		It is mainly usefull to set a graded-index layers that was saved."""
		
		material_nb = self.get_material_nb(material_name)
		
		self.add_graded_layer_from_steps_with_material_nb(material_nb, step_profile, thickness, position, side, description)
	
	
	######################################################################
	#                                                                    #
	# add_graded_layer_from_steps_with_material_nb                       #
	#                                                                    #
	######################################################################
	def add_graded_layer_from_steps_with_material_nb(self, material_nb, step_profile, thickness, position = TOP, side = FRONT, description = []):
		"""Add a graded-index layer using a step profile and the material
		number
		
		This method takes 3 to 7 arguments:
		  material_nb        the number of the material of the layer;
		  step_profile       a list of the steps in the profile;
		  thickness          a list of the thickness of the steps;
		  position           (optional) the position at which to add the
		                     layer (BOTTOM, TOP or the numeric position);
		  side               (optional) the side on which to add the layer
		                     (FRONT or BACK), the default value is FRONT;
		  OT                 (optional) a boolean indicating if the
		                     thickness is given in optical thickness, the
		                     default value is False;
		  description        (optional) a description of the layer when
		                     it is created with a module."""
		
		# Calculate the index profile.
		index_profile = graded.steps_to_index(step_profile, self.material_indices[material_nb])
		
		# If the options TOP or BOTTOM are used, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)
			elif side == BACK:
				position = len(self.back_layers)
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			self.front_layers.insert(position, material_nb)
			self.front_layer_descriptions.insert(position, description)
			self.front_thickness.insert(position, thickness)
			self.front_step_profiles.insert(position, step_profile)
			self.front_index.insert(position, index_profile)
			self.front_refine_thickness.insert(position, 0)
			self.front_refine_index.insert(position, 0)
			self.front_preserve_OT.insert(position, 0)
			self.front_add_needles.insert(position, 0)
			self.front_add_steps.insert(position, 0)
		
		if side == BACK:
			self.back_layers.insert(position, material_nb)
			self.back_layer_descriptions.insert(position, description)
			self.back_thickness.insert(position, thickness)
			self.back_step_profiles.insert(position, step_profile)
			self.back_index.insert(position, index_profile)
			self.back_refine_thickness.insert(position, 0)
			self.back_refine_index.insert(position, 0)
			self.back_preserve_OT.insert(position, 0)
			self.back_add_needles.insert(position, 0)
			self.back_add_steps.insert(position, 0)
		
		self.reset_analysis(side)
		self.reset_monitoring(side)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# change_layer_thickness                                             #
	#                                                                    #
	######################################################################
	def change_layer_thickness(self, thickness, position, side = FRONT, OT = False):
		"""Change the thickness of a layer
		
		This method takes 2 to 4 arguments:
		  thickness          the thickness of the layer;
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		  OT                 (optional) a boolean indicating if the
		                     thickness is given in optical thickness, the
		                     default value is False."""
		
		# This doesn't work for graded-index layers.
		if self.is_graded(position, side):
			return
		
		# If the keyword top or bottom are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)
			if side == BACK:
				position = len(self.back_layers)
		elif position == BOTTOM:
			position = 0
		
		# If the OT flag is set true, the thickness is an optical
		# thickness.
		if OT:
			if side == FRONT:
				thickness /= self.front_index[position]
			else:
				thickness /= self.back_index[position]
		
		if side == FRONT:
			self.front_layer_descriptions[position] = []
			self.front_thickness[position] = thickness
		
		if side == BACK:
			self.back_layer_descriptions[position] = []
			self.back_thickness[position] = thickness
		
		self.reset_analysis(side)
		self.reset_monitoring(side)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# change_layer_index                                                 #
	#                                                                    #
	######################################################################
	def change_layer_index(self, index, position, side = FRONT):
		"""Change the index of refraction of a layer
		
		This method takes 2 or 3 arguments:
		  index              the index of the layer;
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT."""
		
		# This doesn't work for graded-index layers.
		if self.is_graded(position, side):
			return
		
		# If the keyword top or bottom are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)
			if side == BACK:
				position = len(self.back_layers)
		elif position == BOTTOM:
			position = 0
		
		# It only works for mixtures.
		if side == FRONT:
			if not self.materials[self.front_layers[position]].is_mixture():
				return
		elif side == BACK:
			if not self.materials[self.back_layers[position]].is_mixture():
				return
		
		if side == FRONT:
			self.front_layer_descriptions[position] = []
			self.front_index[position] = index
		
		if side == BACK:
			self.back_layer_descriptions[position] = []
			self.back_index[position] = index
		
		self.reset_analysis(side)
		self.reset_monitoring(side)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# merge_layers                                                       #
	#                                                                    #
	######################################################################
	def merge_layers(self):
		"""Merge identical layers
		
		Merge adjacent layers made of the same material. In the case of
		mixtures used in homogeneous layers, they must also have the same
		index. In the case of graded-index layers, the step profiles are
		joined."""
		
		old_nb_front_layers = len(self.front_layers)
		old_nb_back_layers = len(self.back_layers)
		
		# Remove layers with with null thickness, starting at the end of
		# the list to consider every layers and not go behond the length
		# of the shortened list.
		for i_layer in range(len(self.front_layers)-1, 0-1, -1):
			if self.front_thickness[i_layer] == 0.0:
				self.front_layers.pop(i_layer)
				self.front_thickness.pop(i_layer)
				self.front_index.pop(i_layer)
				self.front_step_profiles.pop(i_layer)
				self.front_layer_descriptions.pop(i_layer)
				self.front_refine_thickness.pop(i_layer)
				self.front_refine_index.pop(i_layer)
				self.front_preserve_OT.pop(i_layer)
				self.front_add_needles.pop(i_layer)
				self.front_add_steps.pop(i_layer)
		for i_layer in range(len(self.back_layers)-1, 0-1, -1):
			if self.back_thickness[i_layer] == 0.0:
				self.back_layers.pop(i_layer)
				self.back_thickness.pop(i_layer)
				self.back_index.pop(i_layer)
				self.back_step_profiles.pop(i_layer)
				self.back_layer_descriptions.pop(i_layer)
				self.back_refine_thickness.pop(i_layer)
				self.back_refine_index.pop(i_layer)
				self.back_preserve_OT.pop(i_layer)
				self.back_add_needles.pop(i_layer)
				self.back_add_steps.pop(i_layer)
		
		# Merge identical front layers.
		for i_layer in range(len(self.front_layers)-1, 1-1, -1):
			if self.front_layers[i_layer] == self.front_layers[i_layer-1]:
				# If both layers are graded, extend the lists.
				if self.is_graded(i_layer, FRONT) and self.is_graded(i_layer-1, FRONT):
					self.front_layers.pop(i_layer)
					self.front_layer_descriptions[i_layer-1] = []
					self.front_layer_descriptions.pop(i_layer)
					self.front_refine_thickness.pop(i_layer)
					self.front_refine_index.pop(i_layer)
					self.front_preserve_OT.pop(i_layer)
					self.front_add_needles.pop(i_layer)
					self.front_add_steps.pop(i_layer)
					self.front_thickness[i_layer-1] += self.front_thickness[i_layer]
					self.front_thickness.pop(i_layer)
					self.front_index[i_layer-1] += self.front_index[i_layer]
					self.front_index.pop(i_layer)
					self.front_step_profiles[i_layer-1] += self.front_step_profiles[i_layer]
					self.front_step_profiles.pop(i_layer)
				# If the layer is not a mixture, it is sure that it is
				# identical. If it is a mixture, we must verify that the index
				# of both layers are identical.
				elif not self.materials[self.front_layers[i_layer]].is_mixture() or self.front_index[i_layer] == self.front_index[i_layer-1]:
					self.front_layers.pop(i_layer)
					self.front_layer_descriptions[i_layer-1] = []
					self.front_layer_descriptions.pop(i_layer)
					self.front_refine_thickness.pop(i_layer)
					self.front_refine_index.pop(i_layer)
					self.front_preserve_OT.pop(i_layer)
					self.front_add_needles.pop(i_layer)
					self.front_add_steps.pop(i_layer)
					self.front_thickness[i_layer-1] += self.front_thickness[i_layer]
					self.front_thickness.pop(i_layer)
					self.front_index.pop(i_layer)
					self.front_step_profiles.pop(i_layer)
		
		# Merge identical back layers.
		for i_layer in range(len(self.back_layers)-1, 1-1, -1):
			if self.back_layers[i_layer] == self.back_layers[i_layer-1]:
				# If the layer is graded, extend the lists.
				if self.is_graded(i_layer, BACK) and self.is_graded(i_layer-1, BACK):
					self.back_layers.pop(i_layer)
					self.back_layer_descriptions[i_layer-1] = []
					self.back_layer_descriptions.pop(i_layer)
					self.back_refine_thickness.pop(i_layer)
					self.back_refine_index.pop(i_layer)
					self.back_preserve_OT.pop(i_layer)
					self.back_add_needles.pop(i_layer)
					self.back_add_steps.pop(i_layer)
					self.back_thickness[i_layer-1] += self.back_thickness[i_layer]
					self.back_thickness.pop(i_layer)
					self.back_index[i_layer-1] += self.back_index[i_layer]
					self.back_index.pop(i_layer)
					self.back_step_profiles[i_layer-1] += self.back_step_profiles[i_layer]
					self.back_step_profiles.pop(i_layer)
				# If the layer is not a mixture, it is sure that it is
				# identical. If it is a mixture, we must verify that the index
				# of both layers are identical.
				elif not self.materials[self.back_layers[i_layer]].is_mixture() or self.back_index[i_layer] == self.back_index[i_layer-1]:
					self.back_layers.pop(i_layer)
					self.back_layer_descriptions[i_layer-1] = []
					self.back_layer_descriptions.pop(i_layer)
					self.back_refine_thickness.pop(i_layer)
					self.back_refine_index.pop(i_layer)
					self.back_preserve_OT.pop(i_layer)
					self.back_add_needles.pop(i_layer)
					self.back_add_steps.pop(i_layer)
					self.back_thickness[i_layer-1] += self.back_thickness[i_layer]
					self.back_thickness.pop(i_layer)
					self.back_index.pop(i_layer)
					self.back_step_profiles.pop(i_layer)
		
		# If the number of front layers has changed, this will affect the
		# monitoring curves.
		if len(self.front_layers) != old_nb_front_layers:
			self.reset_monitoring(FRONT)
		
		if len(self.front_layers) != old_nb_front_layers or len(self.back_layers) != old_nb_back_layers:
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# convert_mixtures_to_steps                                          #
	#                                                                    #
	######################################################################
	def convert_mixtures_to_steps(self):
		"""Convert intermediate indices layers to steps
		
		Convert homogeneous layers made of mixtures to steps."""
		
		front_modified = False
		back_modified = False
		
		for i_layer in range(len(self.front_layers)):
			
			# If the layer is not graded but made of a mixture, remove the
			# layer and add it as a graded-index layer.
			if not self.is_graded(i_layer, FRONT) and self.materials[self.front_layers[i_layer]].is_mixture():
				material_name = self.materials[self.front_layers[i_layer]].get_name()
				thickness = self.front_thickness[i_layer]
				index = self.front_index[i_layer]
				self.remove_layer(i_layer, FRONT)
				self.add_graded_layer(material_name, [index], [thickness], i_layer, FRONT)
				
				front_modified = True
		
		for i_layer in range(len(self.back_layers)):
			
			# If the layer is not graded but made of a mixture, remove the
			# layer and add it as a graded-index layer.
			if not self.is_graded(i_layer, BACK) and self.materials[self.back_layers[i_layer]].is_mixture():
				material_name = self.materials[self.back_layers[i_layer]].get_name()
				thickness = self.back_thickness[i_layer]
				index = self.back_index[i_layer]
				self.remove_layer(i_layer, BACK)
				self.add_graded_layer(material_name, [index], [thickness], i_layer, BACK)
				
				back_modified = True
		
		if front_modified and back_modified:
			self.reset_analysis()
			self.reset_monitoring()
		elif front_modified:
			self.reset_analysis(FRONT)
			self.reset_monitoring(FRONT)
		elif back_modified:
			self.reset_analysis(BACK)
			self.reset_monitoring(BACK)
		
		if front_modified or back_modified:
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# remove_layer                                                       #
	#                                                                    #
	######################################################################
	def remove_layer(self, position = TOP, side = FRONT):
		"""Remove a layer
		
		This method takes 0 to 2 arguments:
		  position           (optional) the position of the layer (BOTTOM,
		                     TOP or the numeric position), the default is
		                     TOP;
		  side               (optional) the side on which to remove the
		                     layer (FRONT or BACK), the default value is
		                     FRONT."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			self.front_layers.pop(position)
			self.front_layer_descriptions.pop(position)
			self.front_thickness.pop(position)
			self.front_index.pop(position)
			self.front_step_profiles.pop(position)
			self.front_refine_thickness.pop(position)
			self.front_refine_index.pop(position)
			self.front_preserve_OT.pop(position)
			self.front_add_needles.pop(position)
			self.front_add_steps.pop(position)
		
		elif side == BACK:
			self.back_layers.pop(position)
			self.back_layer_descriptions.pop(position)
			self.back_thickness.pop(position)
			self.back_index.pop(position)
			self.back_step_profiles.pop(position)
			self.back_refine_thickness.pop(position)
			self.back_refine_index.pop(position)
			self.back_preserve_OT.pop(position)
			self.back_add_needles.pop(position)
			self.back_add_steps.pop(position)
		
		self.reset_analysis(side)
		self.reset_monitoring(side)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# swap_sides                                                         #
	#                                                                    #
	######################################################################
	def swap_sides(self):
		"""Swap the sides
		
		Swap the front and back sides."""
		
		if self.front_layers == [] and self.back_layers == []:
			return
		
		self.front_layers, self.back_layers = self.back_layers, self.front_layers
		self.front_layer_descriptions, self.back_layer_descriptions = self.back_layer_descriptions, self.front_layer_descriptions
		self.front_thickness, self.back_thickness = self.back_thickness, self.front_thickness
		self.front_index, self.back_index = self.back_index, self.front_index
		self.front_step_profiles, self.back_step_profiles = self.back_step_profiles, self.front_step_profiles
		self.front_refine_thickness, self.back_refine_thickness = self.back_refine_thickness, self.front_refine_thickness
		self.front_refine_index, self.back_refine_index = self.back_refine_index, self.front_refine_index
		self.front_preserve_OT, self.back_preserve_OT = self.back_preserve_OT, self.front_preserve_OT
		self.front_add_needles, self.back_add_needles = self.back_add_needles, self.front_add_needles
		self.front_add_steps, self.back_add_steps = self.back_add_steps, self.front_add_steps
		self.front_stack_formula, self.back_stack_formula = self.back_stack_formula, self.front_stack_formula
		self.front_stack_materials, self.back_stack_materials = self.back_stack_materials, self.front_stack_materials
		self.matrices_front, self.matrices_back = self.matrices_back, self.matrices_front
		
		# REMOVE when it will be possible to refine back layers.
		# Since it is not possible now, don't refine back layers and refine
		# all front layers.
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				self.front_refine_thickness[i_layer] = False
				self.front_refine_index[i_layer] = False
				self.front_preserve_OT[i_layer] = False
				self.front_add_needles[i_layer] = False
				self.front_add_steps[i_layer] = False
			else:
				self.front_refine_thickness[i_layer] = True
				if self.materials[self.front_layers[i_layer]].is_mixture():
					self.front_refine_index[i_layer] = True
				else:
					self.front_refine_index[i_layer] = False
				self.front_preserve_OT[i_layer] = False
				self.front_add_needles[i_layer] = True
				if self.materials[self.front_layers[i_layer]].is_mixture():
					self.front_add_steps[i_layer] = True
				else:
					self.front_add_steps[i_layer] = False
		for i_layer in range(len(self.back_layers)):
			self.back_refine_thickness[i_layer] = False
			self.back_refine_index[i_layer] = False
			self.back_preserve_OT[i_layer] = False
			self.back_add_needles[i_layer] = False
			self.back_add_steps[i_layer] = False
		
		# It is not possible to simply swap the matrices used for
		# monitoring, so we have to reset it.
		self.reset_monitoring()
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# clear_design                                                       #
	#                                                                    #
	######################################################################
	def clear_design(self, side = BOTH):
		"""Clear the design
		
		This method takes a single optional argument:
		  side               (optional) the side of the design to clear
		                     (FRONT or BACK), the default value is BOTH."""
		
		if self.front_layers == [] and self.back_layers == []:
			return
		
		if side == FRONT or side == BOTH:
			self.front_layers = []
			self.front_layer_descriptions = []
			self.front_thickness = []
			self.front_index = []
			self.front_step_profiles = []
			self.front_refine_thickness = []
			self.front_refine_index = []
			self.front_preserve_OT = []
			self.front_add_needles = []
			self.front_add_steps = []
		
		if side == BACK or side == BOTH:
			self.back_layers = []
			self.back_layer_descriptions = []
			self.back_thickness = []
			self.back_index = []
			self.back_step_profiles = []
			self.back_refine_thickness = []
			self.back_refine_index = []
			self.back_preserve_OT = []
			self.back_add_needles = []
			self.back_add_steps = []
		
		self.reset_analysis()
		self.reset_monitoring()
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_refinable_layer_thickness                                      #
	#                                                                    #
	######################################################################
	def get_refinable_layer_thickness(self, position, side = FRONT):
		"""Get if it is possible to refine the thickness of a layer
		
		This method takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side or the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if it is possible to refine the
		thickness of that layer."""
		
		if side == FRONT and not self.is_graded(position, side) and not self.front_preserve_OT[position]:
			return True
		else:
			return False
	
	
	######################################################################
	#                                                                    #
	# get_refinable_layer_index                                          #
	#                                                                    #
	######################################################################
	def get_refinable_layer_index(self, position, side = FRONT):
		"""Get if it is possible to refine the index of a layer
		
		This method takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side or the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if it is possible to refine the
		index of that layer."""
		
		if side == FRONT and self.materials[self.front_layers[position]].is_mixture() and not self.is_graded(position, side):
			return True
		else:
			return False
	
	
	######################################################################
	#                                                                    #
	# set_refine_layer_thickness                                         #
	#                                                                    #
	######################################################################
	def set_refine_layer_thickness(self, position, refine, side = FRONT):
		"""Set if the thickness of a layer is refined
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  refine             a boolean indicating if the thickness of the
		                     layer must be refined;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT"""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		# Change the settings. Also, it is impossible to add needles when
		# the thickness is not refined.
		if side == FRONT:
			if refine != self.front_refine_thickness[position]:
				self.front_refine_thickness[position] = refine
				if not refine:
					self.front_add_needles[position] = False
				
				self.modified = True
		
		elif side == BACK:
			if refine != self.back_refine_thickness[position]:
				self.back_refine_thickness[position] = refine
				if not refine:
					self.back_add_needles[position] = False
				
				self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_refine_layer_thickness                                         #
	#                                                                    #
	######################################################################
	def get_refine_layer_thickness(self, position, side = FRONT):
		"""Get if the thickness of a layer is refined
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if the thickness of the layer is
		refined."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_refine_thickness[position]
		elif side == BACK:
			return self.back_refine_thickness[position]
	
	
	######################################################################
	#                                                                    #
	# set_refine_layer_index                                             #
	#                                                                    #
	######################################################################
	def set_refine_layer_index(self, position, refine, side = FRONT):
		"""Set if the index of a layer is refined
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  refine             a boolean indicating if the index of the layer
		                     must be refined;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT"""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		# Change the settings. Also, it is impossible to add steps or to
		# preserve OT when the index is not refined.
		if side == FRONT:
			self.front_refine_index[position] = refine
			if not refine:
				self.front_add_steps[position] = False
				self.front_preserve_OT[position] = False
		elif side == BACK:
			self.back_refine_index[position] = refine
			if not refine:
				self.back_add_steps[position] = False
				self.back_preserve_OT[position] = False
	
	
	######################################################################
	#                                                                    #
	# get_refine_layer_index                                             #
	#                                                                    #
	######################################################################
	def get_refine_layer_index(self, position, side = FRONT):
		"""Get if the index of a layer is refined
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if the index of the layer is
		refined."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_refine_index[position]
		elif side == BACK:
			return self.back_refine_index[position]
	
	
	######################################################################
	#                                                                    #
	# set_preserve_OT                                                    #
	#                                                                    #
	######################################################################
	def set_preserve_OT(self, position, preserve_OT, side = FRONT):
		"""Set if the optical thicknes of a layer is preserved
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  preserve_OT        a boolean indicating if the optical thicknes
		                     of the layer must be preserved;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT"""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			if preserve_OT != self.front_preserve_OT[position]:
				self.front_preserve_OT[position] = preserve_OT
				
				self.modified = True
		
		elif side == BACK:
			if preserve_OT != self.back_preserve_OT[position]:
				self.back_preserve_OT[position] = preserve_OT
				
				self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_preserve_OT                                                    #
	#                                                                    #
	######################################################################
	def get_preserve_OT(self, position, side = FRONT):
		"""Get if the optical thicknes of a layer is preserved
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if the optical thickness of the
		layer is preserved."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_preserve_OT[position]
		elif side == BACK:
			return self.back_preserve_OT[position]
	
	
	######################################################################
	#                                                                    #
	# set_add_needles                                                    #
	#                                                                    #
	######################################################################
	def set_add_needles(self, position, add_needles, side = FRONT):
		"""Set if needles are added in a layer
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  add_needles        a boolean indicating if needles are added in
		                     the layer;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT"""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			if add_needles != self.front_add_needles[position]:
				self.front_add_needles[position] = add_needles
				
				self.modified = True
		
		elif side == BACK:
			if add_needles != self.back_add_needles[position]:
				self.back_add_needles[position] = add_needles
				
				self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_add_needles                                                    #
	#                                                                    #
	######################################################################
	def get_add_needles(self, position, side = FRONT):
		"""Get if needles are added in a layer
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if needles are added in a layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_add_needles[position]
		elif side == BACK:
			return self.back_add_needles[position]
	
	
	######################################################################
	#                                                                    #
	# set_add_steps                                                      #
	#                                                                    #
	######################################################################
	def set_add_steps(self, position, add_steps, side = FRONT):
		"""Set if steps are added in a layer
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  add_steps          a boolean indicating if steps are added in the
		                     layer;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT"""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			if add_steps != self.front_add_steps[position]:
				self.front_add_steps[position] = add_steps
				
				self.modified = True
		
		elif side == BACK:
			if add_steps != self.back_add_steps[position]:
				self.back_add_steps[position] = add_steps
				
				self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_add_steps                                                      #
	#                                                                    #
	######################################################################
	def get_add_steps(self, position, side = FRONT):
		"""Get if steps are added in a layer
		
		This method takes 2 or 3 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if steos are added in a layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_add_steps[position]
		elif side == BACK:
			return self.back_add_steps[position]
	
	
	######################################################################
	#                                                                    #
	# set_needle_materials                                               #
	#                                                                    #
	######################################################################
	def set_needle_materials(self, needle_materials):
		"""Set the materials of the needles
		
		This method takes a single input argument:
		  needle_materials   a list of the names of the needle materials."""
		
		if needle_materials != self.needle_materials:
			self.needle_materials = needle_materials
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_needle_materials                                               #
	#                                                                    #
	######################################################################
	def get_needle_materials(self):
		"""Get the materials of the needles
		
		This method returns a list of the names of the needle materials."""
		
		return self.needle_materials
	
	
	######################################################################
	#                                                                    #
	# set_Fourier_parameters                                             #
	#                                                                    #
	######################################################################
	def set_Fourier_parameters(self, Fourier_parameters):
		"""Set the parameters of the Fourier tranform method
		
		This method takes a single input argument:
		  Fourier_parameters   the parameters of the Fourier transform
		                       method."""
		
		if Fourier_parameters != self.Fourier_parameters:
			self.Fourier_parameters = Fourier_parameters
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_Fourier_parameters                                             #
	#                                                                    #
	######################################################################
	def get_Fourier_parameters(self):
		"""Get the parameters of the Fourier tranform method
		
		This method returns the parameters of the Fourier transform method."""
		
		return self.Fourier_parameters
	
	
	######################################################################
	#                                                                    #
	# get_nb_layers                                                      #
	#                                                                    #
	######################################################################
	def get_nb_layers(self, side = FRONT):
		"""Get the number of layers
		
		This function takes an optional argument:
		  side               (optional) the side (FRONT or BACK), the
		                     default value is FRONT."""
		
		if side == FRONT:
			return len(self.front_layers)
		elif side == BACK:
			return len(self.back_layers)
		elif side == BOTH:
			return len(self.front_layers) + len(self.back_layers)
	
	
	######################################################################
	#                                                                    #
	# get_total_thickness                                                #
	#                                                                    #
	######################################################################
	def get_total_thickness(self, side = FRONT):
		"""Get the total thickness
		
		This function takes an optional argument:
		  side               (optional) the side (FRONT or BACK), the
		                     default value is FRONT."""
		
		total_thickness = 0.0
		
		if side == FRONT:
			for i_layer in range(len(self.front_layers)):
				if self.is_graded(i_layer, FRONT):
					for i_sublayer in range(len(self.front_thickness[i_layer])):
						total_thickness += self.front_thickness[i_layer][i_sublayer]
				else:
					total_thickness += self.front_thickness[i_layer]
		elif side == BACK:
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					for i_sublayer in range(len(self.back_thickness[i_layer])):
						total_thickness += self.back_thickness[i_layer][i_sublayer]
				else:
					total_thickness += self.back_thickness[i_layer]
		
		return total_thickness
	
	
	######################################################################
	#                                                                    #
	# get_layer_material                                                 #
	#                                                                    #
	######################################################################
	def get_layer_material(self, position, side = FRONT):
		"""Get the the material of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the material of the layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			material = self.materials[self.front_layers[position]]
		elif side == BACK:
			material = self.materials[self.back_layers[position]]
		
		return material
	
	
	######################################################################
	#                                                                    #
	# get_layer_material_nb                                              #
	#                                                                    #
	######################################################################
	def get_layer_material_nb(self, position, side = FRONT):
		"""Get the number of the material of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the number of the material of the layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			material_nb = self.front_layers[position]
		elif side == BACK:
			material_nb = self.back_layers[position]
		
		return material_nb
	
	
	######################################################################
	#                                                                    #
	# get_layer_material_name                                            #
	#                                                                    #
	######################################################################
	def get_layer_material_name(self, position, side = FRONT):
		"""Get the name of the material of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the name of the material of the layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			material_name = self.materials[self.front_layers[position]].get_name()
		elif side == BACK:
			material_name = self.materials[self.back_layers[position]].get_name()
		
		return material_name
	
	
	######################################################################
	#                                                                    #
	# get_layer_description                                              #
	#                                                                    #
	######################################################################
	def get_layer_description(self, position, side = FRONT):
		"""Get the description of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the description of the layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			return self.front_layer_descriptions[position]
		elif side == BACK:
			return self.back_layer_descriptions[position]
	
	
	######################################################################
	#                                                                    #
	# get_layer_thickness                                                #
	#                                                                    #
	######################################################################
	def get_layer_thickness(self, position, side = FRONT):
		"""Get the thickness of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the thickness of the layer."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT:
			if self.is_graded(position, FRONT):
				thickness = 0.0
				for i_sublayer in range(len(self.front_thickness[position])):
					thickness += self.front_thickness[position][i_sublayer]
			else:
				thickness = self.front_thickness[position]
		elif side == BACK:
			if self.is_graded(position, BACK):
				thickness = 0.0
				for i_sublayer in range(len(self.back_thickness[position])):
					thickness += self.back_thickness[position][i_sublayer]
			else:
				thickness = self.back_thickness[position]
		
		return thickness
	
	
	######################################################################
	#                                                                    #
	# get_layer_index                                                    #
	#                                                                    #
	######################################################################
	def get_layer_index(self, position, side = FRONT):
		"""Get the index of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the index of refraction of the layer.
		
		This method cannot be used for graded-index layers."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if position == SUBSTRATE:
			return self.materials[self.substrate].get_index(self.center_wavelength)
		
		if side == FRONT:
			if position == MEDIUM:
				return self.materials[self.front_medium].get_index(self.center_wavelength)
			
			return self.front_index[position]
		
		elif side == BACK:
			if position == MEDIUM:
				return self.materials[self.back_medium].get_index(self.center_wavelength)
			
			return self.back_index[position]
	
	
	######################################################################
	#                                                                    #
	# get_layer_OT                                                       #
	#                                                                    #
	######################################################################
	def get_layer_OT(self, position, wavelength = None, side = FRONT):
		"""Get the optical thickness of a layer
		
		This function takes 1 to 3 argument:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  wavelength         (optional) the wavelength at which to
		                     calculate the optical thickness, by default it
		                     is the center wavelength;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the optical thickness of the layer at that wavelength.
		
		This method is quite slow when the wavelength is not the center
		wavelength."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		if wavelength is None or wavelength == self.center_wavelength:
			if side == FRONT:
				if self.is_graded(position, FRONT):
					OT = 0.0
					for i_sublayer in range(len(self.front_thickness[position])):
						OT += self.front_thickness[position][i_sublayer] * self.front_index[position][i_sublayer]
				else:
					OT = self.front_thickness[position] * self.front_index[position]
			elif side == BACK:
				if self.is_graded(position, BACK):
					OT = 0.0
					for i_sublayer in range(len(self.back_thickness[position])):
						OT += self.back_thickness[position][i_sublayer] * self.back_index[position][i_sublayer]
				else:
					OT = self.back_thickness[position] * self.back_index[position]
			
			OT /= self.center_wavelength
		
		else:
			if side == FRONT:
				if self.is_graded(position, FRONT):
					OT = 0.0
					for i_sublayer in range(len(self.front_thickness[position])):
						index = self.materials[self.front_layers[position]].change_index_wavelength(self.front_index[position][i_sublayer], self.center_wavelength, wavelength)
						OT += self.front_thickness[position][i_sublayer] * index
				else:
					index = self.materials[self.front_layers[position]].get_index(wavelength)
					OT = self.front_thickness[position] * index
			elif side == BACK:
				if self.is_graded(position, BACK):
					OT = 0.0
					for i_sublayer in range(len(self.back_thickness[position])):
						index = self.materials[self.back_layers[position]].change_index_wavelength(self.back_index[position][i_sublayer], self.center_wavelength, wavelength)
						OT += self.back_thickness[position][i_sublayer] * index
				else:
					index = self.materials[self.back_layers[position]].get_index(wavelength)
					OT = self.back_thickness[position] * index
			
			OT /= wavelength
		
		return OT
	
	
	######################################################################
	#                                                                    #
	# get_layer_step_profile                                             #
	#                                                                    #
	######################################################################
	def get_layer_step_profile(self, position, side = FRONT):
		"""Get the step profile of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the step profile of the layer (thickness, step_profile).
		
		This method cannot be used for homogeneous layers."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		# Get the material and profile describing the layer.
		if side == FRONT:
			thickness = self.front_thickness[position]
			step_profile = self.front_step_profiles[position]
		elif side == BACK:
			thickness = self.back_thickness[position]
			step_profile = self.back_step_profiles[position]
		
		return thickness, step_profile
	
	
	######################################################################
	#                                                                    #
	# get_layer_index_profile                                            #
	#                                                                    #
	######################################################################
	def get_layer_index_profile(self, position, side = FRONT):
		"""Get the index profile of a layer
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the index profile of the layer (thickness,
		index_profile).
		
		This method cannot be used for homogeneous layers."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = len(self.front_layers)-1
			elif side == BACK:
				position = len(self.back_layers)-1
		elif position == BOTTOM:
			position = 0
		
		# Special case for the substrate and the mediums:
		if position == SUBSTRATE:
			return [self.substrate_thickness], [self.materials[self.substrate].get_index(self.center_wavelength)]
		elif position == MEDIUM:
			if side == FRONT:
				return [0], [self.materials[self.front_medium].get_index(self.center_wavelength)]
			elif side == BACK:
				return [0], [self.materials[self.back_medium].get_index(self.center_wavelength)]
		
		if side == FRONT:
			if self.is_graded(position, FRONT):
				return self.front_thickness[position], self.front_index[position]
			else:
				return [self.front_thickness[position]], [self.front_index[position]]
		if side == BACK:
			if self.is_graded(position, BACK):
				return self.back_thickness[position], self.back_index[position]
			else:
				return [self.back_thickness[position]], [self.back_index[position]]
	
	
	######################################################################
	#                                                                    #
	# get_layers                                                         #
	#                                                                    #
	######################################################################
	def get_layers(self, side = FRONT):
		"""Get the layers
		
		This method takes an optional argument:
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns:
		  layers             a list of the numbers of the materials of the
		                     layers
		  descriptions       a list of the descriptions of the layers;
		  thickness          a list of the thickness of the layers;
		  index              a list of the index of the layers;
		  step_profiles      a list of the step profiles of the layers"""
		
		if side == FRONT:
			return self.front_layers, self.front_layer_descriptions, self.front_thickness, self.front_index, self.front_step_profiles
		
		elif side == BACK:
			return self.back_layers, self.back_layer_descriptions, self.back_thickness, self.back_index, self.back_step_profiles
	
	
	######################################################################
	#                                                                    #
	# get_total_OT                                                       #
	#                                                                    #
	######################################################################
	def get_total_OT(self, nb_layer = None, wavelength = None, side = FRONT):
		"""Get the total optical thickness (up to a given layer)
		
		This method takes 3 optional arguments:
		  nb_layer           (optional) the number of layers, starting from
		                     the substrate to calculate the optical
		                     thickness, by default, it is calculated for
		                     the whole filter;
		  wavelength         (optional) the wavelength at which to
		                     calculate the optical thickness, by default it
		                     is the center wavelength;
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns the total optical thickness upt to that layer."""
		
		if nb_layer is None:
			if side == FRONT:
				nb_layer = len(self.front_layers)
			elif side == BACK:
				nb_layer = len(self.back_layers)
		
		total_OT = 0.0
		
		for i in range(nb_layer+1):
			total_OT += self.get_layer_OT(i, wavelength, side)
		
		return total_OT
	
	
	######################################################################
	#                                                                    #
	# is_graded                                                          #
	#                                                                    #
	######################################################################
	def is_graded(self, position, side = FRONT):
		"""Get if a layer is graded
		
		This function takes 1 or 2 arguments:
		  position           the position of the layer (BOTTOM, TOP or the
		                     numeric position);
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns a boolean indicating if a layer is graded."""
		
		# If the keyword TOP or BOTTOM are use, convert them to their
		# numerical values.
		if position == TOP:
			if side == FRONT:
				position = -1
			elif side == BACK:
				position = -1
		elif position == BOTTOM:
			position = 0
		
		if side == FRONT and isinstance(self.front_thickness[position], list):
				return True
		if side == BACK and isinstance(self.back_thickness[position], list):
				return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# get_index_profile                                                  #
	#                                                                    #
	######################################################################
	def get_index_profile(self, side = FRONT):
		"""Get the index profile of the filter
		
		This function takes an optional argument:
		  side               (optional) the side of the layer (FRONT or
		                     BACK), the default value is FRONT;
		and returns:
		  thickness          the thickness of index profile
		  profile            the index of the index profile."""
		
		thickness = []
		profile = []
		
		total_thickness = 0.0
		
		if side == FRONT:
			nb_layers = len(self.front_layers)
		else:
			nb_layers = len(self.back_layers)
		
		for i in range(nb_layers):
			this_layer_thickness, this_layer_profile = self.get_layer_index_profile(i, side)
			for i_sublayer in range(len(this_layer_thickness)):
				thickness.append(total_thickness)
				profile.append(this_layer_profile[i_sublayer])
				total_thickness += this_layer_thickness[i_sublayer]
				thickness.append(total_thickness)
				profile.append(this_layer_profile[i_sublayer])
		
		return thickness, profile
	
	
	######################################################################
	#                                                                    #
	# reset_n                                                            #
	#                                                                    #
	######################################################################
	def reset_n(self):
		"""Reset the internal list of indices"""
		
		self.N = [None]*len(self.materials)
	
	
	######################################################################
	#                                                                    #
	# reset_analysis                                                     #
	#                                                                    #
	######################################################################
	def reset_analysis(self, side = BOTH):
		"""Reset the internal variables used to save the analysis
		
		This method takes a single optional argument:
		  side               (optional) the side(s) that needs to be reset,
		                     the default value is BOTH."""
		
		if side == BOTH:
			self.sin2_theta_0 = []
			self.matrices_front = []
			self.matrices_back = []
		elif side == FRONT:
			self.matrices_front = [None]*len(self.sin2_theta_0)
		elif side == BACK:
			self.matrices_back = [None]*len(self.sin2_theta_0)

	
	######################################################################
	#                                                                    #
	# prepare_indices                                                    #
	#                                                                    #
	######################################################################
	def prepare_indices(self, N = None, wvls_ = None):
		"""Prepare the dispersion curves to be used in the calculations
		
		This method takes 2 optional arguments:
		  N                  (optional) a list in which to put the indices,
		                     by default it is kept in an internal variable;
		  wvls_              (optional) the wavelengths at which to
		                     calculate the indices, by default, the
		                     wavelengths of the filter are used."""
		
		if N is None:
			N = self.N
		if wvls_ is None:
			wvls_ = self.wvls
		
		nb_materials = len(self.materials)
		
		# Determine which materials are used in graded-index layers.
		used_in_graded_index_layer = [False]*nb_materials
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				used_in_graded_index_layer[self.front_layers[i_layer]] = True
		for i_layer in range(len(self.back_layers)):
			if self.is_graded(i_layer, BACK):
				used_in_graded_index_layer[self.back_layers[i_layer]] = True
		
		# Collect the indices of all materials.
		for i_mat in range(nb_materials):
			if not N[i_mat]:
				N[i_mat] = self.materials[i_mat].get_N(wvls_)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			# If the material is used in a graded-index layer, prepare the
			# list of indices (if it is not already done).
			if used_in_graded_index_layer[i_mat] and not N[i_mat].N_mixture_graded_is_prepared():
				N[i_mat].prepare_N_mixture_graded(len(self.material_indices[i_mat]))
				for i_mixture in range(len(self.material_indices[i_mat])):
					N[i_mat].set_N_mixture_graded(i_mixture, self.material_indices[i_mat][i_mixture], self.center_wavelength)
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
	
	
	######################################################################
	#                                                                    #
	# get_substrate_and_medium_indices                                   #
	#                                                                    #
	######################################################################
	def get_substrate_and_medium_indices(self, N = None):
		"""Get the dispersion of the substrate and mediums.
		
		This method takes an optional argument:
		  N                  (optional) the list in which to get the indices,
		                     by default the internal list is used;
		and returns:
		  N_substrate        the dispersion curve of the substrate;
		  N_front_medium     the dispersion curve of the front medium;
		  N_back_medium      the dispersion curve of the back medium.
		
		The method returns the indices of the inermost and outermost layers
		of the front stack when the substrate and medium are not
		considered."""
		
		if N is None:
			N = self.N
		
		# If the substrate and the medium are not considered, their index
		# are the one of the inermost and outermost layers.
		if self.dont_consider_substrate:
			if self.is_graded(0, FRONT):
				N_substrate = N[self.front_layers[0]].get_N_mixture_graded(self.front_step_profiles[0][0])
			elif self.materials[self.front_layers[0]].is_mixture():
				N[self.front_layers[0]].set_N_mixture(self.front_index[0], self.center_wavelength)
				N_layer = N[self.front_layers[0]].get_N_mixture()
				N_substrate = abeles.N(self.wvls)
				N_substrate.copy(N_layer)
			else:
				N_substrate = N[self.front_layers[0]]
			
			if self.is_graded(TOP, FRONT):
				N_front_medium = N[self.front_layers[-1]].get_N_mixture_graded(self.front_step_profiles[-1][-1])
			elif self.materials[self.front_layers[-1]].is_mixture():
				N[self.front_layers[-1]].set_N_mixture(self.front_index[-1], self.center_wavelength)
				N_layer = N[self.front_layers[-1]].get_N_mixture()
				N_front_medium = abeles.N(self.wvls)
				N_front_medium.copy(N_layer)
			else:
				N_front_medium = N[self.front_layers[-1]]
			
			# Not considering the substrate and medium is only possible if
			# the backside is not considered.
			N_back_medium = None
		
		else:
			N_substrate = N[self.substrate]
			N_front_medium = N[self.front_medium]
			N_back_medium = N[self.back_medium]
		
		return N_substrate, N_front_medium, N_back_medium
	
	
	######################################################################
	#                                                                    #
	# analyse                                                            #
	#                                                                    #
	######################################################################
	def analyse(self, angle, N):
		"""Calculate the matrices representing the filter
		
		The method takes 2 arguments:
		  angle              the angle at which the optical properties have
		                     to be calculated;
		  N                  the refractive index of the material in which
		                     the angle is defined;
		and returns a position indicating where to find the results of the
		calculations in class attributes. If the matrices have already been
		calculated at this angle, the calculations are not repeated and the
		method simply returns the position.
		
		Calculation are done using the Abeles method first described in
		  Florin Abeles, "Recherche sur la propagation des ondes
		  electriques sinusoidales dans le milieux stratifies,
		  applications aux couches minces", Annales de physique, vol. 5,
		  1950, pp. 596-640 and pp. 706-782.
		This implementation is inspired by the formula found in
		  Alexander Tikhonravov, Theorical and practical aspects of
		  optical coating design and characterization, notes for a short
		  course given at the Optical Interference Coatings conference
		  held in Banff (Canada) in July 2001.
		These formula, equivalent to those given by Abeles, are faster
		to compute."""
		
		# The angle of the incident light is normalized to vaccuum to speed
		# up the calculation.
		sin2_theta_0 = abeles.sin2(self.wvls)
		sin2_theta_0.set_sin2_theta_0(N, angle)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# If some analysis has been done for this angle, find the position
		# of the matrices in the list and recalculate only what has not
		# already been calculated (this can happen when layers are added on
		# one side, the front and back side are reversed, or when the
		# consideration of the backside is changed, for example).
		try:
			position = self.sin2_theta_0.index(sin2_theta_0)
		except ValueError:
			position = None
		
		# Determine the total number of layers (including sublayers of
		# graded index layers) to determine the progress of the
		# calculation.
		total_nb_layers = 0
		if position is None or self.matrices_front[position] is None:
			for i_layer in range(len(self.front_layers)):
				if self.is_graded(i_layer, FRONT):
					total_nb_layers += len(self.front_step_profiles[i_layer])
				else:
					total_nb_layers += 1
		if self.consider_backside and (position is None or self.matrices_back[position] is None):
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					total_nb_layers += len(self.back_step_profiles[i_layer])
				else:
					total_nb_layers += 1
		
		done_layers = 0
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Calculate and multiply the matrices of the front side.
		if position is None or self.matrices_front[position] is None:
			global_matrices_front = abeles.matrices(self.wvls)
			global_matrices_front.set_matrices_unity()
			temp_matrices = abeles.matrices(self.wvls)
			for i_layer in range(len(self.front_layers)):
				
				if self.is_graded(i_layer, FRONT):
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						
						n_sublayer = self.N[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_front.multiply_matrices(temp_matrices)
						
						done_layers += 1
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
						
						self.progress = done_layers/total_nb_layers
				
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						self.N[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
						N_layer = self.N[self.front_layers[i_layer]].get_N_mixture()
					else:
						N_layer = self.N[self.front_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.front_thickness[i_layer], sin2_theta_0)
					global_matrices_front.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
		
		if self.consider_backside and (position is None or self.matrices_back[position] is None):
			
			# Multiply the matrices of the back side.
			global_matrices_back = abeles.matrices(self.wvls)
			global_matrices_back.set_matrices_unity()
			temp_matrices = abeles.matrices(self.wvls)
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					for i_sublayer in range(len(self.back_step_profiles[i_layer])):
						n_sublayer = self.N[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						done_layers += 1
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
						
						self.progress = done_layers/total_nb_layers
				
				else:
					if self.materials[self.back_layers[i_layer]].is_mixture():
						self.N[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
						N_layer = self.N[self.back_layers[i_layer]].get_N_mixture()
					else:
						N_layer = self.N[self.back_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
					global_matrices_back.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
		
		# Append the results for this angle to the results already
		# saved.
		if position is None:
			self.sin2_theta_0.append(sin2_theta_0)
			self.matrices_front.append(global_matrices_front)
			if self.consider_backside:
				self.matrices_back.append(global_matrices_back)
			else:
				self.matrices_back.append(None)
			position = len(self.sin2_theta_0)-1
		else:
			if self.matrices_front[position] is None:
				self.matrices_front[position] = global_matrices_front
			if self.consider_backside and self.matrices_back[position] is None:
				self.matrices_back[position] = global_matrices_back
		
		# Return the position of the matrices in the list.
		return position
	
	
	######################################################################
	#                                                                    #
	# transmission                                                       #
	#                                                                    #
	######################################################################
	def transmission(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front = abeles.r_and_t(self.wvls)
		T_front = abeles.T(self.wvls)
		
		if self.consider_backside:
			r_and_t_front_reverse = abeles.r_and_t(self.wvls)
			R_front_reverse = abeles.R(self.wvls)
			
			r_and_t_back = abeles.r_and_t(self.wvls)
			T_back = abeles.T(self.wvls)
			R_back = abeles.R(self.wvls)
			
			T_total = abeles.T(self.wvls)
		else:
			T_total = T_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front.calculate_r_and_t(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		if self.consider_backside:
			r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
			R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
			
			# Since the matrices were calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, self.sin2_theta_0[i_angle], polarization)
			R_back.calculate_R(r_and_t_back, polarization)
			
			T_total.calculate_T_with_backside(T_front, R_front_reverse, T_back, R_back, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle])
		
		return T_total
	
	
	######################################################################
	#                                                                    #
	# transmission_reverse                                               #
	#                                                                    #
	######################################################################
	def transmission_reverse(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission of the filter in reverse direction
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission of the filter in reverse direction."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		if self.consider_backside:
			i_angle = self.analyse(angle, N_back_medium)
		else:
			i_angle = self.analyse(angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front_reverse = abeles.r_and_t(self.wvls)
		T_front_reverse = abeles.T(self.wvls)
		
		if self.consider_backside:
			R_front_reverse = abeles.R(self.wvls)
			
			r_and_t_back = abeles.r_and_t(self.wvls)
			R_back = abeles.R(self.wvls)
			
			r_and_t_back_reverse = abeles.r_and_t(self.wvls)
			T_back_reverse = abeles.T(self.wvls)
			
			T_total_reverse = abeles.T(self.wvls)
		else:
			T_total_reverse = T_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Since the matrices was calculated starting at the substrate, we
		# have to calculate the reverse r and t.
		r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, self.sin2_theta_0[i_angle], polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		if self.consider_backside:
			R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
			
			r_and_t_back_reverse.calculate_r_and_t(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
			
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			R_back.calculate_R(r_and_t_back, polarization)
			
			T_total_reverse.calculate_T_with_backside(T_back_reverse, R_back, T_front_reverse, R_front_reverse, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle])
		
		return T_total_reverse
	
	
	######################################################################
	#                                                                    #
	# reflection                                                         #
	#                                                                    #
	######################################################################
	def reflection(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front = abeles.r_and_t(self.wvls)
		R_front = abeles.R(self.wvls)
		if self.consider_backside:
			T_front = abeles.T(self.wvls)
			
			r_and_t_front_reverse = abeles.r_and_t(self.wvls)
			T_front_reverse = abeles.T(self.wvls)
			R_front_reverse = abeles.R(self.wvls)
			
			r_and_t_back = abeles.r_and_t(self.wvls)
			R_back = abeles.R(self.wvls)
			
			R_total = abeles.R(self.wvls)
		
		else:
			R_total = R_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front.calculate_r_and_t(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		R_front.calculate_R(r_and_t_front, polarization)
		if self.consider_backside:
			T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
			
			r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
			T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, self.sin2_theta_0[i_angle], polarization)
			R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
			
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			R_back.calculate_R(r_and_t_back, polarization)
			
			R_total.calculate_R_with_backside(T_front, R_front, T_front_reverse, R_front_reverse, R_back, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle])
		
		return R_total
	
	
	######################################################################
	#                                                                    #
	# reflection_reverse                                                 #
	#                                                                    #
	######################################################################
	def reflection_reverse(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection of the filter in reverse direction
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection of the filter in reverse direction."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		if self.consider_backside:
			i_angle = self.analyse(angle, N_back_medium)
		else:
			i_angle = self.analyse(angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front_reverse = abeles.r_and_t(self.wvls)
		R_front_reverse = abeles.R(self.wvls)
		
		if self.consider_backside:
			r_and_t_back_reverse = abeles.r_and_t(self.wvls)
			R_back_reverse = abeles.R(self.wvls)
			T_back_reverse = abeles.T(self.wvls)
			
			r_and_t_back = abeles.r_and_t(self.wvls)
			T_back = abeles.T(self.wvls)
			R_back = abeles.R(self.wvls)
			
			R_total_reverse = abeles.R(self.wvls)
		
		else:
			R_total_reverse = R_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Since the matrices was calculated starting at the substrate, we
		# have to calculate the reverse r and t.
		r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
		
		if self.consider_backside:
			r_and_t_back_reverse.calculate_r_and_t(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			R_back_reverse.calculate_R(r_and_t_back_reverse, polarization)
			T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
			
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, self.sin2_theta_0[i_angle], polarization)
			R_back.calculate_R(r_and_t_back, polarization)
			
			R_total_reverse.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle])
		
		return R_total_reverse
	
	
	######################################################################
	#                                                                    #
	# reflection_phase                                                   #
	#                                                                    #
	######################################################################
	def reflection_phase(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection phase of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection phase of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		
		phase.calculate_r_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		
		return [phase_i*one_hundred_eighty_over_pi for phase_i in phase]
	
	
	######################################################################
	#                                                                    #
	# transmission_phase                                                 #
	#                                                                    #
	######################################################################
	def transmission_phase(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission phase of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission phase of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		
		phase.calculate_t_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		
		return [phase_i*one_hundred_eighty_over_pi for phase_i in phase]
	
	
	######################################################################
	#                                                                    #
	# reflection_GD                                                      #
	#                                                                    #
	######################################################################
	def reflection_GD(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection GD of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection GD of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		GD = abeles.GD(self.wvls)
		
		phase.calculate_r_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		GD.calculate_GD(phase)
		
		return GD
	
	
	######################################################################
	#                                                                    #
	# transmission_GD                                                    #
	#                                                                    #
	######################################################################
	def transmission_GD(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission GD of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission GD of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		GD = abeles.GD(self.wvls)
		
		phase.calculate_t_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		GD.calculate_GD(phase)
		
		return GD
	
	
	######################################################################
	#                                                                    #
	# reflection_GDD                                                     #
	#                                                                    #
	######################################################################
	def reflection_GDD(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection GDD of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection GDD of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		GDD = abeles.GDD(self.wvls)
		
		phase.calculate_r_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		GDD.calculate_GDD(phase)
		
		return GDD
	
	
	######################################################################
	#                                                                    #
	# transmission_GDD                                                   #
	#                                                                    #
	######################################################################
	def transmission_GDD(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission GDD of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission GDD of the filter."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		phase = abeles.phase(self.wvls)
		GDD = abeles.GDD(self.wvls)
		
		phase.calculate_t_phase(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle], polarization)
		GDD.calculate_GDD(phase)
		
		return GDD


	######################################################################
	#                                                                    #
	# absorption                                                         #
	#                                                                    #
	######################################################################
	def absorption(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the absorption of the filter
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the absorption of the filter."""
		
		self.stop_ = False
		
		A = abeles.A(self.wvls)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		T = self.transmission(angle, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		R = self.reflection(angle, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		A.calculate_A(R, T)
		
		return A


	######################################################################
	#                                                                    #
	# absorption_reverse                                                 #
	#                                                                    #
	######################################################################
	def absorption_reverse(self, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the absorption of the filter in reverse direction
		
		The function takes 2 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the absorption of the filter in reverse direction."""
		
		self.stop_ = False
		
		A_reverse = abeles.A(self.wvls)
		
		T_reverse = self.transmission_reverse(angle, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		R_reverse = self.reflection_reverse(angle, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		A_reverse.calculate_A(R_reverse, T_reverse)
		
		return A_reverse
	
	
	######################################################################
	#                                                                    #
	# ellipsometry                                                       #
	#                                                                    #
	######################################################################
	def ellipsometry(self, angle = 0.0):
		"""Calculate Psi and Delta of the filter
		
		The function takes an optional argument:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		and returns Psi and Delta of the filter.
		
		When the backside is considered, the calculation follows:
		  Y. H. Yang et al. "Spectroscopic ellipsometry of thin films on
		  transparent substrates: A formalism for data interpretation",
		  J. Vac. Sc. Technol., V. 13, No 3, 1995, pp. 1145-1149."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		i_angle = self.analyse(angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front = abeles.r_and_t(self.wvls)
		if self.consider_backside:
			r_and_t_front_reverse = abeles.r_and_t(self.wvls)
			r_and_t_back = abeles.r_and_t(self.wvls)
		
		Psi_and_Delta = abeles.Psi_and_Delta(self.wvls)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front.calculate_r_and_t(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		if self.consider_backside:
			r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
			
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		if self.consider_backside:
			Psi_and_Delta.calculate_Psi_and_Delta_with_backside(r_and_t_front, r_and_t_front_reverse, r_and_t_back, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle]);
		else:
			Psi_and_Delta.calculate_Psi_and_Delta(r_and_t_front)
		
		Psi = Psi_and_Delta.get_Psi()
		Delta = Psi_and_Delta.get_Delta()
		
		nb_wvls = len(self.wvls)
		
		# Express Delta according to Delta_min.
		for i in range(nb_wvls):
			if Delta[i] < self.Delta_min:
				Delta[i] += 360.0
			elif Delta[i] > (self.Delta_min + 360.0):
				Delta[i] -= 360.0
		
		# In the case of a RAE of a RPE, Delta is defined between
		# 0 and 180 degres.
		if self.ellipsometer_type == RAE or self.ellipsometer_type == RPE:
			for i in range(nb_wvls):		
				if Delta[i] < 0.0:
					Delta[i] = -Delta[i]
				elif Delta[i] > 180.0:
					Delta[i] = 360.0 - Delta[i]
		# In the case of RCE, Delta is defined over a 360 degres range and
		# doesn't need to be ajusted.
		
		return Psi, Delta
	
	
	######################################################################
	#                                                                    #
	# ellipsometry_reverse                                               #
	#                                                                    #
	######################################################################
	def ellipsometry_reverse(self, angle = 0.0):
		"""Calculate Psi and Delta of the filter in reverse direction
		
		The function takes an optional argument:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		and returns Psi and Delta of the filter in reverse direction.
		
		When the backside is considered, the calculation follows:
		  Y. H. Yang et al. "Spectroscopic ellipsometry of thin films on
		  transparent substrates: A formalism for data interpretation",
		  J. Vac. Sc. Technol., V. 13, No 3, 1995, pp. 1145-1149."""
		
		self.stop_ = False
		
		self.prepare_indices()
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and get the position on this angle
		# in the list.
		if self.consider_backside:
			i_angle = self.analyse(angle, N_back_medium)
		else:
			i_angle = self.analyse(angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front_reverse = abeles.r_and_t(self.wvls)
		
		if self.consider_backside:
			r_and_t_back_reverse = abeles.r_and_t(self.wvls)
			r_and_t_back = abeles.r_and_t(self.wvls)
		
		Psi_and_Delta_reverse = abeles.Psi_and_Delta(self.wvls)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		if self.consider_backside:
			r_and_t_back_reverse.calculate_r_and_t(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
			r_and_t_back.calculate_r_and_t_reverse(self.matrices_back[i_angle], N_back_medium, N_substrate, self.sin2_theta_0[i_angle])
		
		# Since the matrices was calculated starting at the substrate, we
		# have to calculate the reverse r and t.
		r_and_t_front_reverse.calculate_r_and_t_reverse(self.matrices_front[i_angle], N_front_medium, N_substrate, self.sin2_theta_0[i_angle])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		if self.consider_backside:
			Psi_and_Delta_reverse.calculate_Psi_and_Delta_with_backside(r_and_t_back_reverse, r_and_t_back, r_and_t_front_reverse, N_substrate, self.substrate_thickness, self.sin2_theta_0[i_angle]);
		else:
			Psi_and_Delta_reverse.calculate_Psi_and_Delta(r_and_t_front_reverse)
		
		Psi_reverse = Psi_and_Delta_reverse.get_Psi()
		Delta_reverse = Psi_and_Delta_reverse.get_Delta()
		
		nb_wvls = len(self.wvls)
		
		# Express Delta according to Delta_min.
		for i in range(nb_wvls):
			if Delta_reverse[i] < self.Delta_min:
				Delta_reverse[i] += 360.0
			elif Delta_reverse[i] > (self.Delta_min + 360.0):
				Delta_reverse[i] -= 360.0
		
		# In the case of a RAE of a RPE, Delta is defined between
		# 0 and 180 degres.
		if self.ellipsometer_type == RAE or self.ellipsometer_type == RPE:
			for i in range(nb_wvls):		
				if Delta_reverse[i] < 0.0:
					Delta_reverse[i] = -Delta_reverse[i]
				elif Delta_reverse[i] > 180.0:
					Delta_reverse[i] = 360.0 - Delta_reverse[i]
		# In the case of RCE, Delta is defined over a 360 degres range and
		# doesn't need to be ajusted.
		
		return Psi_reverse, Delta_reverse
	
	
	######################################################################
	#                                                                    #
	# color                                                              #
	#                                                                    #
	######################################################################
	def color(self, angle = 0.0, polarization = UNPOLARIZED, illuminant_name = None, observer_name = None):
		"""Calculate the color of the filter
		
		The function takes 4 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		  illuminant         (optional) the name of the illuminant, if it
		                     is omitted, the default illuminant for this
		                     filter will be used;
		  observer           (optional) the name of the observer, if it is
		                     omitted, the default observer for this filter
		                     will be used;
		and returns 2 arguments:
		  R_color            a color object for the reflection;
		  T_color            a color object for the transmission."""
		
		self.stop_ = False
		
		if illuminant_name is None:
			illuminant_name = self.illuminant_name
		if observer_name is None:
			observer_name = self.observer_name
		
		# Read the observer and the illuminant.
		observer = color.get_observer(observer_name)
		illuminant = color.get_illuminant(illuminant_name)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Get the observer wavelengths.
		observer_wvls, x_function, y_function, z_function = observer.get_functions()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Set the wavelengths to those of the observer.
		nb_wvls = len(observer_wvls)
		wvls_ = abeles.wvls(nb_wvls)
		for i_wvl in range(nb_wvls):
			wvls_.set_wvl(i_wvl, observer_wvls[i_wvl])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# First collect the indices of all materials.
		nb_materials = len(self.materials)
		n = [None]*nb_materials
		self.prepare_indices(n, wvls_)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# The angle of the incident light is normalized to vaccuum to speed
		# up the calculation.
		sin2_theta_0 = abeles.sin2(wvls_)
		sin2_theta_0.set_sin2_theta_0(N_front_medium, angle)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Determine the total number of layers (including sublayers of
		# graded index layers) to determine the progress of the
		# calculation.
		total_nb_layers = 0
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				total_nb_layers += len(self.front_step_profiles[i_layer])
			else:
				total_nb_layers += 1
		if self.consider_backside:
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					total_nb_layers += len(self.back_step_profiles[i_layer])
				else:
					total_nb_layers += 1
		
		done_layers = 0
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Calculate and multiply the matrices of the front side.
		global_matrices_front = abeles.matrices(wvls_)
		global_matrices_front.set_matrices_unity()
		temp_matrices = abeles.matrices(wvls_)
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				for i_sublayer in range(len(self.front_step_profiles[i_layer])):
					n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
					temp_matrices.set_matrices(n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
					global_matrices_front.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
			else:
				if self.materials[self.front_layers[i_layer]].is_mixture():
					n[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
					N_layer = n[self.front_layers[i_layer]].get_N_mixture()
				else:
					N_layer = n[self.front_layers[i_layer]]
				temp_matrices.set_matrices(N_layer, self.front_thickness[i_layer], sin2_theta_0)
				global_matrices_front.multiply_matrices(temp_matrices)
				
				done_layers += 1
				
				# Give other threads a chance...
				time.sleep(0)
				
				if self.stop_: return
				
				self.progress = done_layers/total_nb_layers
		
		if self.consider_backside:
			
			# Multiply the matrices of the back side.
			global_matrices_back = abeles.matrices(wvls_)
			global_matrices_back.set_matrices_unity()
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					for i_sublayer in range(len(self.back_step_profiles[i_layer])):
						n_sublayer = n[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						done_layers += 1
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
						
						self.progress = done_layers/total_nb_layers
				else:
					if self.materials[self.back_layers[i_layer]].is_mixture():
						n[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
						N_layer = n[self.back_layers[i_layer]].get_N_mixture()
					else:
						N_layer = n[self.back_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
					global_matrices_back.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front = abeles.r_and_t(wvls_)
		T_front = abeles.T(wvls_)
		R_front = abeles.R(wvls_)
		
		if self.consider_backside:
			r_and_t_front_reverse = abeles.r_and_t(wvls_)
			R_front_reverse = abeles.R(wvls_)
			T_front_reverse = abeles.T(wvls_)
			
			r_and_t_back = abeles.r_and_t(wvls_)
			T_back = abeles.T(wvls_)
			R_back = abeles.R(wvls_)
			
			R_total = abeles.R(wvls_)
			T_total = abeles.T(wvls_)
		
		else:
			R_total = R_front
			T_total = T_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front.calculate_r_and_t(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
		T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, sin2_theta_0, polarization)
		R_front.calculate_R(r_and_t_front, polarization)
		
		if self.consider_backside:
			r_and_t_front_reverse.calculate_r_and_t_reverse(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
			R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
			T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, sin2_theta_0, polarization)
			
			# Since the matrices were calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, sin2_theta_0, polarization)
			R_back.calculate_R(r_and_t_back, polarization)
			
			R_total.calculate_R_with_backside(T_front, R_front, T_front_reverse, R_front_reverse, R_back, N_substrate, self.substrate_thickness, sin2_theta_0)
			T_total.calculate_T_with_backside(T_front, R_front_reverse, T_back, R_back, N_substrate, self.substrate_thickness, sin2_theta_0)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create the color objects.
		R_color = color.color(observer, illuminant)
		T_color = color.color(observer, illuminant)
		
		R_color.calculate_color(observer_wvls, R_total)
		T_color.calculate_color(observer_wvls, T_total)
		
		return R_color, T_color
	
	
	######################################################################
	#                                                                    #
	# color_reverse                                                      #
	#                                                                    #
	######################################################################
	def color_reverse(self, angle = 0.0, polarization = UNPOLARIZED, illuminant_name = None, observer_name = None):
		"""Calculate the color of the filter in reverse direction
		
		The function takes 4 optional arguments:
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		  illuminant         (optional) the name of the illuminant, if it
		                     is omitted, the default illuminant for this
		                     filter will be used;
		  observer           (optional) the name of the observer, if it is
		                     omitted, the default observer for this filter
		                     will be used;
		and returns 2 arguments:
		  R_color_reverse    a color object for the reflection;
		  T_color_reverse    a color object for the transmission."""
		
		self.stop_ = False
		
		if illuminant_name is None:
			illuminant_name = self.illuminant_name
		if observer_name is None:
			observer_name = self.observer_name
		
		# Read the observer and the illuminant.
		observer = color.get_observer(observer_name)
		illuminant = color.get_illuminant(illuminant_name)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Get the observer wavelengths.
		observer_wvls, x_function, y_function, z_function = observer.get_functions()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Set the wavelengths to those of the observer.
		nb_wvls = len(observer_wvls)
		wvls_ = abeles.wvls(nb_wvls)
		for i_wvl in range(nb_wvls):
			wvls_.set_wvl(i_wvl, observer_wvls[i_wvl])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# First collect the indices of all materials.
		nb_materials = len(self.materials)
		n = [None]*nb_materials
		self.prepare_indices(n, wvls_)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# The angle of the incident light is normalized to vaccuum to speed
		# up the calculation.
		sin2_theta_0 = abeles.sin2(wvls_)
		if self.consider_backside:
			sin2_theta_0.set_sin2_theta_0(N_back_medium, angle)
		else:
			sin2_theta_0.set_sin2_theta_0(N_substrate, angle)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Determine the total number of layers (including sublayers of
		# graded index layers) to determine the progress of the
		# calculation.
		total_nb_layers = 0
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				total_nb_layers += len(self.front_step_profiles[i_layer])
			else:
				total_nb_layers += 1
		if self.consider_backside:
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					total_nb_layers += len(self.back_step_profiles[i_layer])
				else:
					total_nb_layers += 1
		
		done_layers = 0
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Calculate and multiply the matrices of the front side.
		global_matrices_front = abeles.matrices(wvls_)
		global_matrices_front.set_matrices_unity()
		temp_matrices = abeles.matrices(wvls_)
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				for i_sublayer in range(len(self.front_step_profiles[i_layer])):
					n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
					temp_matrices.set_matrices(n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
					global_matrices_front.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
			else:
				if self.materials[self.front_layers[i_layer]].is_mixture():
					n[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
					N_layer = n[self.front_layers[i_layer]].get_N_mixture()
				else:
					N_layer = n[self.front_layers[i_layer]]
				temp_matrices.set_matrices(N_layer, self.front_thickness[i_layer], sin2_theta_0)
				global_matrices_front.multiply_matrices(temp_matrices)
				
				done_layers += 1
				
				# Give other threads a chance...
				time.sleep(0)
				
				if self.stop_: return
				
				self.progress = done_layers/total_nb_layers
		
		if self.consider_backside:
			
			# Multiply the matrices of the back side.
			global_matrices_back = abeles.matrices(wvls_)
			global_matrices_back.set_matrices_unity()
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					for i_sublayer in range(len(self.back_step_profiles[i_layer])):
						n_sublayer = n[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						done_layers += 1
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
						
						self.progress = done_layers/total_nb_layers
				else:
					if self.materials[self.back_layers[i_layer]].is_mixture():
						n[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
						N_layer = n[self.back_layers[i_layer]].get_N_mixture()
					else:
						N_layer = n[self.back_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
					global_matrices_back.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front_reverse = abeles.r_and_t(wvls_)
		R_front_reverse = abeles.R(wvls_)
		T_front_reverse = abeles.T(wvls_)
		
		if self.consider_backside:
			r_and_t_back_reverse = abeles.r_and_t(wvls_)
			T_back_reverse = abeles.T(wvls_)
			R_back_reverse = abeles.R(wvls_)
			
			r_and_t_back = abeles.r_and_t(wvls_)
			T_back = abeles.T(wvls_)
			R_back = abeles.R(wvls_)
			
			R_total_reverse = abeles.R(wvls_)
			T_total_reverse = abeles.T(wvls_)
		
		else:
			R_total_reverse = R_front_reverse
			T_total_reverse = T_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		r_and_t_front_reverse.calculate_r_and_t_reverse(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
		R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
		T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, sin2_theta_0, polarization)
		
		if self.consider_backside:
			r_and_t_back_reverse.calculate_r_and_t(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
			T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, sin2_theta_0, polarization)
			R_back_reverse.calculate_R(r_and_t_back_reverse, polarization)
			
			# Since the matrices were calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, sin2_theta_0, polarization)
			R_back.calculate_R(r_and_t_back, polarization)
			
			R_total_reverse.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse, N_substrate, self.substrate_thickness, sin2_theta_0)
			T_total_reverse.calculate_T_with_backside(T_back_reverse, R_back, T_front_reverse, R_front_reverse, N_substrate, self.substrate_thickness, sin2_theta_0)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create the color objects.
		R_color_reverse = color.color(observer, illuminant)
		T_color_reverse = color.color(observer, illuminant)
		
		R_color_reverse.calculate_color(observer_wvls, R_total_reverse)
		T_color_reverse.calculate_color(observer_wvls, T_total_reverse)
		
		return R_color_reverse, T_color_reverse
	
	
	######################################################################
	#                                                                    #
	# color_trajectory                                                   #
	#                                                                    #
	######################################################################
	def color_trajectory(self, angles, polarization = UNPOLARIZED, illuminant_name = None, observer_name = None):
		"""Calculate the color trajectory of the filter
		
		The function takes between 1 and 4 arguments:
		  angles					   a list of the angles of incidence (in degres);
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		  illuminant         (optional) the name of the illuminant, if it
		                     is omitted, the default illuminant for this
		                     filter will be used;
		  observer           (optional) the name of the observer, if it is
		                     omitted, the default observer for this filter
		                     will be used;
		and returns 2 arguments:
		  R_color            a list of color object for the reflection;
		  T_color            a list of color object for the transmission."""
		
		self.stop_ = False
		
		if illuminant_name is None:
			illuminant_name = self.illuminant_name
		if observer_name is None:
			observer_name = self.observer_name
		
		# Read the observer and the illuminant.
		observer = color.get_observer(observer_name)
		illuminant = color.get_illuminant(illuminant_name)
		
		# Get the observer wavelengths.
		observer_wvls, x_function, y_function, z_function = observer.get_functions()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_angles = len(angles)
		
		# Create lists for the color objects.
		R_colors = [None]*nb_angles
		T_colors = [None]*nb_angles
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Set the wavelengths to those of the observer.
		nb_wvls = len(observer_wvls)
		wvls_ = abeles.wvls(nb_wvls)
		for i_wvl in range(nb_wvls):
			wvls_.set_wvl(i_wvl, observer_wvls[i_wvl])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create all the necessary objects that will be reused for all
		# angles.
		global_matrices_front = abeles.matrices(wvls_)
		temp_matrices = abeles.matrices(wvls_)
		if self.consider_backside:
			global_matrices_back = abeles.matrices(wvls_)
		r_and_t_front = abeles.r_and_t(wvls_)
		T_front = abeles.T(wvls_)
		R_front = abeles.R(wvls_)
		if self.consider_backside:
			r_and_t_front_reverse = abeles.r_and_t(wvls_)
			R_front_reverse = abeles.R(wvls_)
			T_front_reverse = abeles.T(wvls_)
			r_and_t_back = abeles.r_and_t(wvls_)
			T_back = abeles.T(wvls_)
			R_back = abeles.R(wvls_)
			R_total = abeles.R(wvls_)
			T_total = abeles.T(wvls_)
		else:
			R_total = R_front
			T_total = T_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# First collect the indices of all materials.
		nb_materials = len(self.materials)
		n = [None]*nb_materials
		self.prepare_indices(n, wvls_)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		for i_angle in range(nb_angles):
			
			angle = angles[i_angle]
		
			R_colors[i_angle] = color.color(observer, illuminant)
			T_colors[i_angle] = color.color(observer, illuminant)
			
			# The angle of the incident light is normalized to vaccuum to speed
			# up the calculation.
			sin2_theta_0 = abeles.sin2(wvls_)
			sin2_theta_0.set_sin2_theta_0(N_front_medium, angle)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			# Calculate and multiply the matrices of the front side.
			global_matrices_front.set_matrices_unity()
			for i_layer in range(len(self.front_layers)):
				if self.is_graded(i_layer, FRONT):
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_front.multiply_matrices(temp_matrices)
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						n[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
						N_layer = n[self.front_layers[i_layer]].get_N_mixture()
					else:
						N_layer = n[self.front_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.front_thickness[i_layer], sin2_theta_0)
					global_matrices_front.multiply_matrices(temp_matrices)
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
			
			if self.consider_backside:
				
				# Multiply the matrices of the back side.
				global_matrices_back.set_matrices_unity()
				for i_layer in range(len(self.back_layers)):
					if self.is_graded(i_layer, BACK):
						for i_sublayer in range(len(self.back_step_profiles[i_layer])):
							n_sublayer = n[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
							temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
							global_matrices_back.multiply_matrices(temp_matrices)
							
							# Give other threads a chance...
							time.sleep(0)
							
							if self.stop_: return
					else:
						if self.materials[self.back_layers[i_layer]].is_mixture():
							n[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
							N_layer = n[self.back_layers[i_layer]].get_N_mixture()
						else:
							N_layer = n[self.back_layers[i_layer]]
						temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			r_and_t_front.calculate_r_and_t(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
			T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, sin2_theta_0, polarization)
			R_front.calculate_R(r_and_t_front, polarization)
			
			if self.consider_backside:
				r_and_t_front_reverse.calculate_r_and_t_reverse(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
				R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
				T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, sin2_theta_0, polarization)
				
				# Since the matrices were calculated starting at the substrate, we
				# have to calculate the reverse r and t.
				r_and_t_back.calculate_r_and_t_reverse(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
				T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, sin2_theta_0, polarization)
				R_back.calculate_R(r_and_t_back, polarization)
				
				R_total.calculate_R_with_backside(T_front, R_front, T_front_reverse, R_front_reverse, R_back, N_substrate, self.substrate_thickness, sin2_theta_0)
				T_total.calculate_T_with_backside(T_front, R_front_reverse, T_back, R_back, N_substrate, self.substrate_thickness, sin2_theta_0)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			R_colors[i_angle].calculate_color(observer_wvls, R_total)
			T_colors[i_angle].calculate_color(observer_wvls, T_total)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			self.progress = (i_angle+1)/nb_angles
		
		return R_colors, T_colors
	
	
	######################################################################
	#                                                                    #
	# color_trajectory_reverse                                           #
	#                                                                    #
	######################################################################
	def color_trajectory_reverse(self, angles, polarization = UNPOLARIZED, illuminant_name = None, observer_name = None):
		"""Calculate the color trajectory of the filter in reverse direction
		
		The function takes between 1 and 4 arguments:
		  angles					   a list of the angles of incidence (in degres);
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		  illuminant         (optional) the name of the illuminant, if it
		                     is omitted, the default illuminant for this
		                     filter will be used;
		  observer           (optional) the name of the observer, if it is
		                     omitted, the default observer for this filter
		                     will be used;
		and returns 2 arguments:
		  R_color_reverse    a list of color object for the reflection;
		  T_color_reverse    a list of color object for the transmission."""
		
		self.stop_ = False
		
		if illuminant_name is None:
			illuminant_name = self.illuminant_name
		if observer_name is None:
			observer_name = self.observer_name
		
		# Read the observer and the illuminant.
		observer = color.get_observer(observer_name)
		illuminant = color.get_illuminant(illuminant_name)
		
		# Get the observer wavelengths.
		observer_wvls, x_function, y_function, z_function = observer.get_functions()
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_angles = len(angles)
		
		# Create lists for the color objects.
		R_colors_reverse = [None]*nb_angles
		T_colors_reverse = [None]*nb_angles
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Set the wavelengths to those of the observer.
		nb_wvls = len(observer_wvls)
		wvls_ = abeles.wvls(nb_wvls)
		for i_wvl in range(nb_wvls):
			wvls_.set_wvl(i_wvl, observer_wvls[i_wvl])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create all the necessary objects that will be reused for all
		# angles.
		sin2_theta_0 = abeles.sin2(wvls_)
		global_matrices_front = abeles.matrices(wvls_)
		temp_matrices = abeles.matrices(wvls_)
		if self.consider_backside:
			global_matrices_back = abeles.matrices(wvls_)
		r_and_t_front_reverse = abeles.r_and_t(wvls_)
		R_front_reverse = abeles.R(wvls_)
		T_front_reverse = abeles.T(wvls_)
		if self.consider_backside:
			r_and_t_back = abeles.r_and_t(wvls_)
			T_back = abeles.T(wvls_)
			R_back = abeles.R(wvls_)
			r_and_t_back_reverse = abeles.r_and_t(wvls_)
			T_back_reverse = abeles.T(wvls_)
			R_back_reverse = abeles.R(wvls_)
			R_total_reverse = abeles.R(wvls_)
			T_total_reverse = abeles.T(wvls_)
		else:
			R_total_reverse = R_front_reverse
			T_total_reverse = T_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# First collect the indices of all materials.
		nb_materials = len(self.materials)
		n = [None]*nb_materials
		self.prepare_indices(n, wvls_)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		for i_angle in range(nb_angles):
			
			angle = angles[i_angle]
		
			R_colors_reverse[i_angle] = color.color(observer, illuminant)
			T_colors_reverse[i_angle] = color.color(observer, illuminant)
			
			# The angle of the incident light is normalized to vaccuum to speed
			# up the calculation.
			if self.consider_backside:
				sin2_theta_0.set_sin2_theta_0(N_back_medium, angle)
			else:
				sin2_theta_0.set_sin2_theta_0(N_substrate, angle)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			# Calculate and multiply the matrices of the front side.
			global_matrices_front.set_matrices_unity()
			for i_layer in range(len(self.front_layers)):
				if self.is_graded(i_layer, FRONT):
					for i_sublayer in range(len(self.front_step_profiles[i_layer])):
						n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_front.multiply_matrices(temp_matrices)
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
				else:
					if self.materials[self.front_layers[i_layer]].is_mixture():
						n[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
						N_layer = n[self.front_layers[i_layer]].get_N_mixture()
					else:
						N_layer = n[self.front_layers[i_layer]]
					temp_matrices.set_matrices(N_layer, self.front_thickness[i_layer], sin2_theta_0)
					global_matrices_front.multiply_matrices(temp_matrices)
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
			
			if self.consider_backside:
				
				# Multiply the matrices of the back side.
				global_matrices_back.set_matrices_unity()
				for i_layer in range(len(self.back_layers)):
					if self.is_graded(i_layer, BACK):
						for i_sublayer in range(len(self.back_step_profiles[i_layer])):
							n_sublayer = n[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
							temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
							global_matrices_back.multiply_matrices(temp_matrices)
							
							# Give other threads a chance...
							time.sleep(0)
							
							if self.stop_: return
					else:
						if self.materials[self.back_layers[i_layer]].is_mixture():
							n[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
							N_layer = n[self.back_layers[i_layer]].get_N_mixture()
						else:
							N_layer = n[self.back_layers[i_layer]]
						temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			r_and_t_front_reverse.calculate_r_and_t_reverse(global_matrices_front, N_front_medium, N_substrate, sin2_theta_0)
			R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
			T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, sin2_theta_0, polarization)
			
			if self.consider_backside:
				r_and_t_back_reverse.calculate_r_and_t(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
				T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, sin2_theta_0, polarization)
				R_back_reverse.calculate_R(r_and_t_back_reverse, polarization)
				
				# Since the matrices were calculated starting at the substrate, we
				# have to calculate the reverse r and t.
				r_and_t_back.calculate_r_and_t_reverse(global_matrices_back, N_back_medium, N_substrate, sin2_theta_0)
				T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, sin2_theta_0, polarization)
				R_back.calculate_R(r_and_t_back, polarization)
				
				R_total_reverse.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse, N_substrate, self.substrate_thickness, sin2_theta_0)
				T_total_reverse.calculate_T_with_backside(T_back_reverse, R_back, T_front_reverse, R_front_reverse, N_substrate, self.substrate_thickness, sin2_theta_0)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			R_colors_reverse[i_angle].calculate_color(observer_wvls, R_total_reverse)
			T_colors_reverse[i_angle].calculate_color(observer_wvls, T_total_reverse)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			self.progress = (i_angle+1)/nb_angles
		
		return R_colors_reverse, T_colors_reverse
	
	
	######################################################################
	#                                                                    #
	# reset_monitoring                                                   #
	#                                                                    #
	######################################################################
	def reset_monitoring(self, side = BOTH):
		"""Reset the internal variables used to save the monitoring
		
		This method takes a single optional argument:
		  side               (optional) the side(s) that needs to be reset,
		                     the default value is BOTH.
		
		At this time, the argument is ignored."""
		
		self.monitoring_wvls = []
		self.monitoring_n = []
		self.monitoring_sin2_theta_0 = []
		self.monitoring_thicknesses = []
		self.monitoring_matrices_front = []
		self.monitoring_matrices_back = []
	
	
	######################################################################
	#                                                                    #
	# prepare_monitoring_wvls_and_n                                      #
	#                                                                    #
	######################################################################
	def prepare_monitoring_wvls_and_n(self, wavelengths):
		"""Prepare wavelength and refractive index structure for monitoring
		
		The method takes 1 argument:
		  wavelengths        a list of wavelengths;
		and returns the wvls structure and a list of refractive index
		structures."""
		
		# Create a wvls object and assign it the wavelength value.
		nb_wvls = len(wavelengths)
		wvls = abeles.wvls(nb_wvls)
		for i_wvl in range(nb_wvls):
			wvls.set_wvl(i_wvl, wavelengths[i_wvl])
		
		# If wvls already exist, use previously calculated structures.
		if wvls in self.monitoring_wvls:
			i = self.monitoring_wvls.index(wvls)
			return self.monitoring_wvls[i], self.monitoring_n[i]
		
		# Otherwise prepare all the n.
		n = [None]*len(self.materials)
		self.prepare_indices(n, wvls)
		self.monitoring_wvls.append(wvls)
		self.monitoring_n.append(n)
		
		return wvls, n
	
	
	######################################################################
	#                                                                    #
	# monitoring                                                         #
	#                                                                    #
	######################################################################
	def monitoring(self, wvls, angle, N):
		"""Calculate the matrices representing the filter for monitoring
		
		The method takes 3 arguments:
		  wvls               the wavelengths at which to calculate the
		                     matrices;
		  angle              the angle of incidence;
		  N                  the refractive index of the material in which
		                     the angle is defined;
		and returns a position indicating where to find the results	of the
		calculations in class attributes. If the matrices have already been
		calculated at this angle, the calculation are not repeated and the
		method simply returns the position."""
		
		# The angle of the incident light is normalized to vaccuum to speed
		# up the calculation.
		sin2_theta_0 = abeles.sin2(wvls)
		sin2_theta_0.set_sin2_theta_0(N, angle)
		
		# If the analysis is already done for these conditions, simply
		# return the position of the matrices in the list.
		if sin2_theta_0 in self.monitoring_sin2_theta_0:
			return self.monitoring_sin2_theta_0.index(sin2_theta_0)
		
		n = self.monitoring_n[self.monitoring_wvls.index(wvls)]
		
		nb_front_layers = len(self.front_layers)
		
		# Determine the total number of layers (including sublayers of
		# graded index layers) to determine the progress of the
		# calculation.
		total_nb_layers = 0
		for i_layer in range(len(self.front_layers)):
			if self.is_graded(i_layer, FRONT):
				total_nb_layers += len(self.front_step_profiles[i_layer])
			else:
				total_nb_layers += 1
		if self.consider_backside:
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					total_nb_layers += len(self.back_step_profiles[i_layer])
				else:
					total_nb_layers += 1
		
		done_layers = 0
		
		# Create matrices for the front side.
		global_matrices_front = abeles.matrices(wvls)
		temp_matrices = abeles.matrices(wvls)
		global_matrices_front.set_matrices_unity()
		
		matrices = [None]*nb_front_layers
		thickness = [None]*nb_front_layers
		total_thickness = 0.0
		
		for i_layer in range(nb_front_layers):
			
			if self.is_graded(i_layer):
				nb_sublayers = len(self.front_step_profiles[i_layer])
				thickness[i_layer] = [0.0]*(nb_sublayers+1)
				layer_matrices = abeles.monitoring_matrices(wvls, nb_sublayers+1)
				thickness[i_layer][0] = total_thickness
				n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][0])
				layer_matrices.set_monitoring_matrices(0, n_sublayer, 0.0, sin2_theta_0)
				for i_sublayer in range(nb_sublayers):
					total_thickness += self.front_thickness[i_layer][i_sublayer]
					thickness[i_layer][i_sublayer+1] = total_thickness
					n_sublayer = n[self.front_layers[i_layer]].get_N_mixture_graded(self.front_step_profiles[i_layer][i_sublayer])
					layer_matrices.set_monitoring_matrices(i_sublayer+1, n_sublayer, self.front_thickness[i_layer][i_sublayer], sin2_theta_0)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
				
				layer_matrices.multiply_monitoring_matrices_cumulative(global_matrices_front)
			
			else:
				if self.materials[self.front_layers[i_layer]].is_mixture():
					n[self.front_layers[i_layer]].set_N_mixture(self.front_index[i_layer], self.center_wavelength)
					N_layer = n[self.front_layers[i_layer]].get_N_mixture()
				else:
					N_layer = n[self.front_layers[i_layer]]
				
				nb_sublayers = int(math.ceil((self.front_thickness[i_layer]-0.0)/self.monitoring_sublayer_thickness)+1)
				thickness[i_layer] = [0.0]*nb_sublayers
				layer_matrices = abeles.monitoring_matrices(wvls, nb_sublayers)
				for i_sublayer in range(nb_sublayers-1):
					sublayer_thickness = i_sublayer*self.monitoring_sublayer_thickness
					thickness[i_layer][i_sublayer] = total_thickness + sublayer_thickness
					layer_matrices.set_monitoring_matrices(i_sublayer, N_layer, sublayer_thickness, sin2_theta_0)
				total_thickness += self.front_thickness[i_layer]
				thickness[i_layer][-1] = total_thickness
				layer_matrices.set_monitoring_matrices(nb_sublayers-1, N_layer, self.front_thickness[i_layer], sin2_theta_0)
				layer_matrices.multiply_monitoring_matrices(global_matrices_front)
				
				done_layers += 1
				
				# Give other threads a chance...
				time.sleep(0)
				
				if self.stop_: return
				
				self.progress = done_layers/total_nb_layers
			
			# The global matrix up to this layer is the matrix of the last
			# sublayer.
			global_matrices_front.copy_matrices(layer_matrices[-1])
			
			matrices[i_layer] = layer_matrices
		
		if self.consider_backside_on_monitoring:
			
			# Multiply the matrices of the back side.
			global_matrices_back = abeles.matrices(wvls)
			global_matrices_back.set_matrices_unity()
			done_layers = 0
			for i_layer in range(len(self.back_layers)):
				if self.is_graded(i_layer, BACK):
					for i_sublayer in range(len(self.back_step_profiles[i_layer])):
						n_sublayer = n[self.back_layers[i_layer]].get_N_mixture_graded(self.back_step_profiles[i_layer][i_sublayer])
						temp_matrices.set_matrices(n_sublayer, self.back_thickness[i_layer][i_sublayer], sin2_theta_0)
						global_matrices_back.multiply_matrices(temp_matrices)
						
						done_layers += 1
						
						# Give other threads a chance...
						time.sleep(0)
						
						if self.stop_: return
						
						self.progress = done_layers/total_nb_layers
				
				else:
					if self.materials[self.back_layers[i_layer]].is_mixture():
						n[self.back_layers[i_layer]].set_N_mixture(self.back_index[i_layer], self.center_wavelength)
						N_layer = n[self.back_layers[i_layer]].get_N_mixture()
					else:
						N_layer = n[self.back_layers[i_layer]]
					
					temp_matrices.set_matrices(N_layer, self.back_thickness[i_layer], sin2_theta_0)
					global_matrices_back.multiply_matrices(temp_matrices)
					
					done_layers += 1
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
					
					self.progress = done_layers/total_nb_layers
		
		# Save the results in internal variables.
		self.monitoring_sin2_theta_0.append(sin2_theta_0)
		self.monitoring_thicknesses.append(thickness)
		self.monitoring_matrices_front.append(matrices)
		if self.consider_backside_on_monitoring:
			self.monitoring_matrices_back.append(global_matrices_back)
		
		# Return the position of the matrices in the list.
		return len(self.monitoring_sin2_theta_0)-1
	
	
	######################################################################
	#                                                                    #
	# reflection_monitoring                                              #
	#                                                                    #
	######################################################################
	def reflection_monitoring(self, wavelengths, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection monitoring of the filter
		
		The function takes 1 to 3 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection monitoring of the filter (thickness, R)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection and transmission in amplitude and
		# in intensity.
		r_and_t_front = abeles.r_and_t(wvls)
		R_front = abeles.R(wvls)
		if self.consider_backside_on_monitoring:
			T_front = abeles.T(wvls)
			r_and_t_front_reverse = abeles.r_and_t(wvls)
			T_front_reverse = abeles.T(wvls)
			R_front_reverse = abeles.R(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
			R_back = abeles.R(wvls)
			R_total = abeles.R(wvls)
		
		# When the backside is not considered, the reflection is that
		# of the front side.
		else:
			R_total = R_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare the reflection and transmission of the backside since they
		# will be use repeatedly.
		if self.consider_backside_on_monitoring:
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			R_back.calculate_R(r_and_t_back, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the reflection.
		R = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			R[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					R[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Calculate reflection for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front.calculate_r_and_t(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					R_front.calculate_R(r_and_t_front, polarization)
					if self.consider_backside_on_monitoring:
						T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
						r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
						T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, self.monitoring_sin2_theta_0[i_conditions], polarization)
						R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
						R_total.calculate_R_with_backside(T_front, R_front, T_front_reverse, R_front_reverse, R_back, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions])
					
					for i_wvl in range(nb_wvls):
						R[i_wvl][i_layer][i_sublayer] = R_total[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		return self.monitoring_thicknesses[i_conditions], R
	
	
	######################################################################
	#                                                                    #
	# reflection_reverse_monitoring                                      #
	#                                                                    #
	######################################################################
	def reflection_monitoring_reverse(self, wavelengths, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the reflection monitoring of the filter in reverse direction
		
		The function takes 1 to 3 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the reflection monitoring of the filter (thickness, R)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		if self.consider_backside_on_monitoring:
			i_conditions = self.monitoring(wvls, angle, N_back_medium)
		else:
			i_conditions = self.monitoring(wvls, angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection and transmission in amplitude and
		# in intensity.
		r_and_t_front_reverse = abeles.r_and_t(wvls)
		R_front_reverse = abeles.R(wvls)
		if self.consider_backside_on_monitoring:
			r_and_t_back_reverse = abeles.r_and_t(wvls)
			T_back_reverse = abeles.T(wvls)
			R_back_reverse = abeles.R(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
			T_back = abeles.T(wvls)
			R_back = abeles.R(wvls)
			R_total_reverse = abeles.R(wvls)
		
		# When the backside is not considered, the reflection is that
		# of the front side.
		else:
			R_total_reverse = R_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare the reflection and transmission of the backside since they
		# will be use repeatedly.
		if self.consider_backside_on_monitoring:
			r_and_t_back_reverse.calculate_r_and_t(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			R_back_reverse.calculate_R(r_and_t_back_reverse, polarization)
			T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
			
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, self.monitoring_sin2_theta_0[i_conditions], polarization)
			R_back.calculate_R(r_and_t_back, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the reflection.
		R = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			R[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					R[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Calculate reflection for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
					if self.consider_backside_on_monitoring:
						R_total_reverse.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions])
					
					for i_wvl in range(nb_wvls):
						R[i_wvl][i_layer][i_sublayer] = R_total_reverse[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		return self.monitoring_thicknesses[i_conditions], R
	
	
	######################################################################
	#                                                                    #
	# transmission_monitoring                                            #
	#                                                                    #
	######################################################################
	def transmission_monitoring(self, wavelengths, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission monitoring of the filter
		
		The function takes 1 to 3 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission monitoring of the filter (thickness,
		T)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection and transmission in amplitude and
		# in intensity.
		r_and_t_front = abeles.r_and_t(wvls)
		T_front = abeles.T(wvls)
		if self.consider_backside_on_monitoring:
			r_and_t_front_reverse = abeles.r_and_t(wvls)
			R_front_reverse = abeles.R(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
			T_back = abeles.T(wvls)
			R_back = abeles.R(wvls)
			T_total = abeles.T(wvls)
		
		# When the backside is not considered, the transmission is that
		# of the front side.
		else:
			T_total = T_front
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare the reflection and transmission of the backside since they
		# will be use repeatedly.
		if self.consider_backside_on_monitoring:
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			T_back.calculate_T(r_and_t_back, N_substrate, N_back_medium, self.monitoring_sin2_theta_0[i_conditions], polarization)
			R_back.calculate_R(r_and_t_back, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the transmission.
		T = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			T[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					T[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Calculate transmission for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front.calculate_r_and_t(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					T_front.calculate_T(r_and_t_front, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
					if self.consider_backside_on_monitoring:
						r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
						R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
						T_total.calculate_T_with_backside(T_front, R_front_reverse, T_back, R_back, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions])
					
					for i_wvl in range(nb_wvls):
						T[i_wvl][i_layer][i_sublayer] = T_total[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		return self.monitoring_thicknesses[i_conditions], T
	
	
	######################################################################
	#                                                                    #
	# transmission_monitoring_reverse                                    #
	#                                                                    #
	######################################################################
	def transmission_monitoring_reverse(self, wavelengths, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the transmission monitoring of the filter in reverse direction
		
		The function takes 1 to 3 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light, it
		                     can take a numerical value between 0 and 90 or
		                     the values S, P, or UNPOLARIZED, the default
		                     value is UNPOLARIZED;
		and returns the transmission monitoring of the filter (thickness,
		T)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		if self.consider_backside_on_monitoring:
			i_conditions = self.monitoring(wvls, angle, N_back_medium)
		else:
			i_conditions = self.monitoring(wvls, angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection and transmission in amplitude and
		# in intensity.
		r_and_t_front_reverse = abeles.r_and_t(wvls)
		T_front_reverse = abeles.T(wvls)
		if self.consider_backside_on_monitoring:
			R_front_reverse = abeles.R(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
			R_back = abeles.R(wvls)
			r_and_t_back_reverse = abeles.r_and_t(wvls)
			T_back_reverse = abeles.T(wvls)
			T_total_reverse = abeles.T(wvls)
		
		# When the backside is not considered, the transmission is that
		# of the front side.
		else:
			T_total_reverse = T_front_reverse
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare the reflection and transmission of the backside since they
		# will be use repeatedly.
		if self.consider_backside_on_monitoring:
			r_and_t_back_reverse.calculate_r_and_t(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			T_back_reverse.calculate_T(r_and_t_back_reverse, N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			R_back.calculate_R(r_and_t_back, polarization)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the transmission.
		T = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			T[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					T[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Calculate transmission for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					T_front_reverse.calculate_T(r_and_t_front_reverse, N_substrate, N_front_medium, self.monitoring_sin2_theta_0[i_conditions], polarization)
					if self.consider_backside_on_monitoring:
						R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
						T_total_reverse.calculate_T_with_backside(T_back_reverse, R_back, T_front_reverse, R_front_reverse, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions])
					
					for i_wvl in range(nb_wvls):
						T[i_wvl][i_layer][i_sublayer] = T_total_reverse[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		return self.monitoring_thicknesses[i_conditions], T
	
	
	######################################################################
	#                                                                    #
	# ellipsometry_monitoring                                            #
	#                                                                    #
	######################################################################
	def ellipsometry_monitoring(self, wavelengths, angle):
		"""Calculate Psi and Delta monitoring of the filter
		
		The function takes 2 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		and returns Psi and Delta monitoring of the filter (thickness, Psi
		and Delta)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create objects.
		r_and_t_front = abeles.r_and_t(wvls)
		if self.consider_backside_on_monitoring:
			r_and_t_front_reverse = abeles.r_and_t(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
		Psi_and_Delta = abeles.Psi_and_Delta(wvls)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare reflection and transmission for the backside since they
		# will be used repeatadly.
		if self.consider_backside_on_monitoring:
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the transmission.
		Psi = [None]*nb_wvls
		Delta = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			Psi[i_wvl] = [None]*nb_front_layers
			Delta[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					Psi[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
					Delta[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Calculate Psi and Delta for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front.calculate_r_and_t(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					if self.consider_backside_on_monitoring:
						r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
						Psi_and_Delta.calculate_Psi_and_Delta_with_backside(r_and_t_front, r_and_t_front_reverse, r_and_t_back, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions]);
					
					else:
						Psi_and_Delta.calculate_Psi_and_Delta(r_and_t_front)
					
					Psi_ = Psi_and_Delta.get_Psi()
					Delta_ = Psi_and_Delta.get_Delta()
					
					for i_wvl in range(nb_wvls):
						Psi[i_wvl][i_layer][i_sublayer] = Psi_[i_wvl]
						Delta[i_wvl][i_layer][i_sublayer] = Delta_[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		for i_wvl in range(nb_wvls):
			for i_layer in range(nb_front_layers):
				if Delta[i_wvl][i_layer]:
					nb_sublayers = len(Delta[i_wvl][i_layer])
					# Express Delta according to Delta_min.
					for i_sublayer in range(nb_sublayers):		
						if Delta[i_wvl][i_layer][i_sublayer] < self.monitoring_Delta_min:
							Delta[i_wvl][i_layer][i_sublayer] += 360.0
						elif Delta[i_wvl][i_layer][i_sublayer] > (self.monitoring_Delta_min + 360.0):
							Delta[i_wvl][i_layer][i_sublayer] -= 360.0
					
					# In the case of a RAE of a RPE, Delta is defined between
					# 0 and 180 degres.
					if self.monitoring_ellipsometer_type == RAE or self.monitoring_ellipsometer_type == RPE:
						for i_sublayer in range(nb_sublayers):		
							if Delta[i_wvl][i_layer][i_sublayer] < 0.0:
								Delta[i_wvl][i_layer][i_sublayer] = -Delta[i_wvl][i_layer][i_sublayer]
							elif Delta[i_wvl][i_layer][i_sublayer] > 180.0:
								Delta[i_wvl][i_layer][i_sublayer] = 360.0 - Delta[i_wvl][i_layer][i_sublayer]
					# In the case of RCE, Delta is defined over a 360 degres range and
					# doesn't need to be ajusted.
		
		return self.monitoring_thicknesses[i_conditions], Psi, Delta
	
	
	######################################################################
	#                                                                    #
	# ellipsometry_monitoring_reverse                                    #
	#                                                                    #
	######################################################################
	def ellipsometry_monitoring_reverse(self, wavelengths, angle):
		"""Calculate Psi and Delta monitoring of the filter in reverse direction
		
		The function takes 2 arguments:
		  wavelengths        a list of wavelengths at which to calculate
		                     the monitoring curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		and returns Psi and Delta monitoring of the filter (thickness, Psi
		and Delta)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n(wavelengths)
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		if self.consider_backside_on_monitoring:
			i_conditions = self.monitoring(wvls, angle, N_back_medium)
		else:
			i_conditions = self.monitoring(wvls, angle, N_substrate)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create objects.
		r_and_t_front_reverse = abeles.r_and_t(wvls)
		if self.consider_backside_on_monitoring:
			r_and_t_back_reverse = abeles.r_and_t(wvls)
			r_and_t_back = abeles.r_and_t(wvls)
		Psi_and_Delta_reverse = abeles.Psi_and_Delta(wvls)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Prepare reflection and transmission for the backside since they
		# will be used repeatadly.
		if self.consider_backside_on_monitoring:
			r_and_t_back_reverse.calculate_r_and_t(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
			# Since the matrices was calculated starting at the substrate, we
			# have to calculate the reverse r and t.
			r_and_t_back.calculate_r_and_t_reverse(self.monitoring_matrices_back[i_conditions], N_back_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		nb_wvls = len(wvls)
		nb_front_layers = len(self.front_layers)
		
		# Create a structure to keep the transmission.
		Psi_reverse = [None]*nb_wvls
		Delta_reverse = [None]*nb_wvls
		for i_wvl in range(nb_wvls):
			Psi_reverse[i_wvl] = [None]*nb_front_layers
			Delta_reverse[i_wvl] = [None]*nb_front_layers
			for i_layer in range(nb_front_layers):
					nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
					Psi_reverse[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
					Delta_reverse[i_wvl][i_layer] = array.array("d", [0.0]*nb_sublayers)
		
		# Calculate Psi and Delta for every sublayers.
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front_reverse.calculate_r_and_t_reverse(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					
					if self.consider_backside_on_monitoring:
						Psi_and_Delta_reverse.calculate_Psi_and_Delta_with_backside(r_and_t_back_reverse, r_and_t_back, r_and_t_front_reverse, N_substrate, self.substrate_thickness, self.monitoring_sin2_theta_0[i_conditions]);
					else:
						Psi_and_Delta_reverse.calculate_Psi_and_Delta(r_and_t_front_reverse)
					
					Psi_reverse_ = Psi_and_Delta_reverse.get_Psi()
					Delta_reverse_ = Psi_and_Delta_reverse.get_Delta()
					
					for i_wvl in range(nb_wvls):
						Psi_reverse[i_wvl][i_layer][i_sublayer] = Psi_reverse_[i_wvl]
						Delta_reverse[i_wvl][i_layer][i_sublayer] = Delta_reverse_[i_wvl]
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		for i_wvl in range(nb_wvls):
			for i_layer in range(nb_front_layers):
				if Delta_reverse[i_wvl][i_layer]:
					nb_sublayers = len(Delta_reverse[i_wvl][i_layer])
					# Express Delta according to Delta_min.
					for i_sublayer in range(nb_sublayers):		
						if Delta_reverse[i_wvl][i_layer][i_sublayer] < self.monitoring_Delta_min:
							Delta_reverse[i_wvl][i_layer][i_sublayer] += 360.0
						elif Delta_reverse[i_wvl][i_layer][i_sublayer] > (self.monitoring_Delta_min + 360.0):
							Delta_reverse[i_wvl][i_layer][i_sublayer] -= 360.0
					
					# In the case of a RAE of a RPE, Delta is defined between
					# 0 and 180 degres.
					if self.monitoring_ellipsometer_type == RAE or self.monitoring_ellipsometer_type == RPE:
						for i_sublayer in range(nb_sublayers):		
							if Delta_reverse[i_wvl][i_layer][i_sublayer] < 0.0:
								Delta_reverse[i_wvl][i_layer][i_sublayer] = -Delta_reverse[i_wvl][i_layer][i_sublayer]
							elif Delta_reverse[i_wvl][i_layer][i_sublayer] > 180.0:
								Delta_reverse[i_wvl][i_layer][i_sublayer] = 360.0 - Delta_reverse[i_wvl][i_layer][i_sublayer]
					# In the case of RCE, Delta is defined over a 360 degres range and
					# doesn't need to be ajusted.
		
		return self.monitoring_thicknesses[i_conditions], Psi_reverse, Delta_reverse
	
	
	######################################################################
	#                                                                    #
	# admittance                                                         #
	#                                                                    #
	######################################################################
	def admittance(self, wavelength, angle = 0.0, polarization = S):
		"""Calculate the admittance diagram of the filter
		
		The function takes 1 to 3 arguments:
		  wavelength         that wavelengths at which to calculate the
		                     curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light only
		                     S or P are accepted, the default value is S;
		and returns the admittance diagram of the filter (thickness,
		real_part, imag_part)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n([wavelength])
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		admittance = abeles.admittance(wvls)
		
		nb_front_layers = len(self.front_layers)
		
		# Calculate admittance for every sublayers.
		real_part = [None]*nb_front_layers
		imag_part = [None]*nb_front_layers
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				real_part[i_layer] = array.array("d", [0.0]*nb_sublayers)
				imag_part[i_layer] = array.array("d", [0.0]*nb_sublayers)
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					admittance.calculate_admittance(sublayer_matrices, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
					answer = admittance[0]
					real_part[i_layer][i_sublayer] = answer.real
					imag_part[i_layer][i_sublayer] = answer.imag
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		# The admittance cannot be defined for arbitrary polarization
		# since a change in amplitude, phase, and state of polarization
		# needs 4 values to be described while the admittance, a complex
		# number, only defines two values.
		
		return self.monitoring_thicknesses[i_conditions], real_part, imag_part
	
	
	######################################################################
	#                                                                    #
	# circle                                                             #
	#                                                                    #
	######################################################################
	def circle(self, wavelength, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the circle diagram of the filter
		
		The function takes 1 to 3 arguments:
		  wavelength         that wavelengths at which to calculate the
		                     curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light only
		                     S or P are accepted, the default value is S;
		and returns the circle diagram of the filter (thickness, real_part,
		imag_part)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n([wavelength])
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection in amplitude.
		r_and_t_front = abeles.r_and_t(wvls)
		circle = abeles.circle(wvls)
		
		nb_front_layers = len(self.front_layers)
		
		# Calculate reflection for every sublayers.
		real_part = [None]*nb_front_layers
		imag_part = [None]*nb_front_layers
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				real_part[i_layer] = array.array("d", [0.0]*nb_sublayers)
				imag_part[i_layer] = array.array("d", [0.0]*nb_sublayers)
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					r_and_t_front.calculate_r_and_t(sublayer_matrices, N_front_medium, N_substrate, self.monitoring_sin2_theta_0[i_conditions])
					circle.calculate_circle(r_and_t_front, polarization)
					r = circle[0]
					real_part[i_layer][i_sublayer] = r.real
					imag_part[i_layer][i_sublayer] = r.imag
					
					# Give other threads a chance...
					time.sleep(0)
					
					if self.stop_: return
		
		return self.monitoring_thicknesses[i_conditions], real_part, imag_part
	
	
	######################################################################
	#                                                                    #
	# electric_field                                                     #
	#                                                                    #
	######################################################################
	def electric_field(self, wavelength, angle = 0.0, polarization = UNPOLARIZED):
		"""Calculate the electric field in the filter
		
		The function takes 1 to 3 arguments:
		  wavelength         that wavelengths at which to calculate the
		                     curve;
		  angle              (optional) the angle of incidence (in degres),
		                     the default value is 0;
		  polarization       (optional) the polarization of the light only
		                     S or P are accepted, the default value is S;
		and returns the electric field the filter (thickness,
		electric_field)."""
		
		self.stop_ = False
		
		wvls, n = self.prepare_monitoring_wvls_and_n([wavelength])
		
		N_substrate, N_front_medium, N_back_medium = self.get_substrate_and_medium_indices(n)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Do the analysis (if necessary) and find the position for these
		# conditions in tables.
		i_conditions = self.monitoring(wvls, angle, N_front_medium)
		
		# Give other threads a chance...
		time.sleep(0)
		
		if self.stop_: return
		
		# Create structures for the reflection in amplitude.
		electric_field = abeles.electric_field(wvls)
		
		nb_front_layers = len(self.front_layers)
		
		# Calculate reflection for every sublayers.
		E = [None]*nb_front_layers
		for i_layer in range(nb_front_layers):
			if self.monitoring_matrices_front[i_conditions][i_layer]:
				nb_sublayers = len(self.monitoring_matrices_front[i_conditions][i_layer])
				E[i_layer] = array.array("d", [0.0]*nb_sublayers)
				for i_sublayer in range(nb_sublayers):
					sublayer_matrices = self.monitoring_matrices_front[i_conditions][i_layer][i_sublayer]
					electric_field.calculate_electric_field(sublayer_matrices, N_substrate, self.monitoring_sin2_theta_0[i_conditions], polarization)
					E[i_layer][i_sublayer] = electric_field[0]
		
		return self.monitoring_thicknesses[i_conditions], E
	
	
	######################################################################
	#                                                                    #
	# stop                                                               #
	#                                                                    #
	######################################################################
	def stop(self):
		"""Stop the current operation
		
		An internal variable is set that will stop the calculation shortly."""
		
		self.stop_ = True
	
	
	######################################################################
	#                                                                    #
	# get_progress                                                       #
	#                                                                    #
	######################################################################
	def get_progress(self):
		"""Get the progress of the current calculation
		
		This method returns the progress of the current calculation on a
		scale of 0 to 1."""
		
		return self.progress
	
	
	######################################################################
	#                                                                    #
	# set_modified                                                       #
	#                                                                    #
	######################################################################
	def set_modified(self, modified):
		"""Set the modification status of the filter
		
		Use this method when the filter is saved in order to track
		modifications between saves. This method takes a single input
		argument:
		  modified     indication of the modification status."""
		
		self.modified = modified
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the filter was modified
		
		This method returns a boolean indicating if the filter has been
		modified since it was created or last saved."""
		
		return self.modified



########################################################################
#                                                                      #
# parse_filter                                                         #
#                                                                      #
########################################################################
def parse_filter(lines, file_version, material_catalog = None):
	"""Parse a filter file
	
	This function takes 2 or 3 arguments:
	  lines             a list of the lines of the filter file;
	  file_version      the version of the file;
	  material_catalog  (optional) the material catalog to use with this
		                  filter, if omitted, the default materials are
		                  used;
	and returns a single output argument:
	  filter            the filter.
	
	If the filter is not properly formatted, a filter_error is raised."""
	
	if not material_catalog:
		material_catalog = materials.material_catalog()
	
	# Parse the file.
	try:
		keywords, values = simple_parser.parse(lines)
	except simple_parser.parsing_error, error:
		raise filter_error("Cannot parse filter because %s" % error.get_value())
	
	description = None
	substrate = None
	substrate_thickness = None
	front_medium = None
	back_medium = None
	dont_consider_substrate = None
	center_wavelength = None
	wavelengths = []
	wavelength_range_from = None
	wavelength_range_to = None
	wavelength_range_by = None
	step_spacing = None
	minimum_thickness = None
	illuminant = None
	observer = None
	consider_backside = None
	ellipsometer_type = None
	Delta_min = None
	consider_backside_on_monitoring = None
	monitoring_ellipsometer_type = None
	monitoring_Delta_min = None
	monitoring_sublayer_thickness = None
	needle_materials = None
	Fourier_parameters = None
	front_stack_formula = ""
	front_stack_materials = {}
	back_stack_formula = ""
	back_stack_materials = {}
	front_layers = []
	front_thickness = []
	front_index = []
	front_step_profiles = []
	front_layer_descriptions = []
	front_refine_thickness = []
	front_refine_index = []
	front_preserve_OT = []
	front_add_needles = []
	front_add_steps = []
	back_layers = []
	back_thickness = []
	back_index = []
	back_step_profiles = []
	back_layer_descriptions = []
	back_refine_thickness = []
	back_refine_index = []
	back_preserve_OT = []
	back_add_needles = []
	back_add_steps = []
	
	last_layer_added = None
	
	# Analyse the elements
	for i in range(len(keywords)):
		keyword = keywords[i]
		value = values[i]
		
		# In the case of the description, the values are simply considered
		# as lines of the description. The description can be empty.
		if keyword == "Description":
			if description is not None:
				raise filter_error("Multiple definition in filter")
			if not isinstance(value, str):
				raise filter_error("Filter definition must be a single line")
			description = value
		
		# The substrate is a string for the name of the material and
		# a float for the thickness.
		elif keyword == "Substrate":
			if substrate is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("Substrate description must be on a single line")
			elements = value.split()
			if len(elements) != 2:
				raise filter_error("Substrate must provide material and thickness")
			substrate = elements[0]
			try:
				substrate_thickness = float(elements[1])
			except ValueError:
				raise filter_error("Substrate thickness must be a float")
			if material_catalog.get_material(substrate).is_mixture():
				raise filter_error("Substrate cannot be a mixture")
			if substrate_thickness <= 0.0:
				raise filter_error("Substrate thickness must be positive")
		
		# The front medium is a string for the name of the material.
		elif keyword == "FrontMedium":
			if front_medium is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("FrontMedium value must be on a single line")
			front_medium = value
			if material_catalog.get_material(front_medium).is_mixture():
				raise filter_error("Front medium cannot be a mixture")
		
		# The back medium is a string for the name of the material.
		elif keyword == "BackMedium":
			if back_medium is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("BackMedium value must be on a single line")
			back_medium = value
			if material_catalog.get_material(back_medium).is_mixture():
				raise filter_error("Back mediu, cannot be a mixture")
		
		# dont_consider_substrate is an integer that takes a value
		# convertible to a boolean.
		elif keyword == "DontConsiderSubstrate":
			if dont_consider_substrate is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("DontConsiderSubstrate description must be on a single line")
			try:
				dont_consider_substrate = bool(int(value))
			except ValueError:
				raise filter_error("Invalid DontConsiderSubstrate value")
		
		# The center wavelength has to be interpreted as a float.
		elif keyword == "CenterWavelength":
			if center_wavelength is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("CenterWavelength value must be on a single line")
			try:
				center_wavelength = float(value)
			except ValueError:
				raise filter_error("CenterWavelength must be a float")
			if center_wavelength <= 0.0:
				raise filter_error("CenterWavelength must be positive")
		
		# The wavelengths can by a list of wavelengths, the number of
		# wavelengths defined by line of the file is not imposed.
		elif keyword == "Wavelengths":
			if wavelengths != []:
				raise filter_error("Multiple definition in filter")
			if not isinstance(value, list):
				value = [value]
			while value:
				line = value.pop(0)
				elements = line.split()
				for element in elements:
					try:
						wavelengths.append(float(element))
					except ValueError:
						raise filter_error("Wavelengths values must be floats")
			if len(wavelengths) == 0:
				raise filter_error("Wavelengths must provide at least one wavelength")
		
		# The wavelengths can be specified by a range, this range is
		# specified by a triplet consisting of the lowest wavelength,
		# the highest wavelength and the step.
		elif keyword == "WavelengthRange":
			if wavelength_range_from is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("WavelengthRange values must be on a single line")
			elements = value.split()
			if len(elements) != 3:
				raise filter_error("WavelengthRange must provide three values for the wavelength range and step")
			try:
				wavelength_range_from = float(elements[0])
				wavelength_range_to = float(elements[1])
				wavelength_range_by = float(elements[2])
			except ValueError:
				raise filter_error("WavelengthRange values must be floats")
			if wavelength_range_to < wavelength_range_from:
				raise filter_error("WavelengthRange upper value must be greater the the lower value")
			if wavelength_range_by >= (wavelength_range_to - wavelength_range_from):
				raise filter_error("WavelengthRange step must be smaller than the difference between the upper and lower values")
		
		# The sublayer thickness has to be interpreted as a float.
		elif keyword == "StepSpacing":
			if step_spacing is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("StepSpacing value must be on a single line")
			try:
				step_spacing = float(value)
			except ValueError:
				raise filter_error("StepSpacing must be a float")
			if step_spacing <= 0.0 and step_spacing != -1.0:
				raise filter_error("StepSpacing must be positive (or -1 to indicate deposition step spacing).")
		
		# The minimum thickness has to be interpreted as a float (if the
		# MinimumOT keyword is used, as in file in the 1.0 branch, it is
		# interpreted as a minimum thickness).
		elif keyword == "MinimumThickness" or keyword == "MinimumOT":
			if minimum_thickness is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("%s value must be on a single line" % keyword)
			try:
				minimum_thickness = float(value)
			except ValueError:
				raise filter_error("%s must be an float" % keyword)
			if minimum_thickness < 0.0:
				raise filter_error("%s must be positive on zero" % keyword)
		
		# The illuminant is a string. Check that this illuminant exist.
		elif keyword == "Illuminant":
			if illuminant is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("Illuminant value must be on a single line")
			illuminant = value
			if not color.illuminant_exists(illuminant):
				raise filter_error("Unknown illuminant")
		
		# The observer is a string. Check that this observer exist.
		elif keyword == "Observer":
			if observer is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("Observer value must be on a single line")
			observer = value
			if not color.observer_exists(observer):
				raise filter_error("Unknown observer")
		
		# consider_backside is an integer that takes either 0 or 1.
		elif keyword == "ConsiderBackside":
			if consider_backside is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("ConsiderBackside must be on a single line")
			try:
				consider_backside = bool(int(value))
			except ValueError:
				raise filter_error("Invalid ConsiderBackside")
		
		# The ellipsometer type is an integer.
		elif keyword == "EllipsometerType":
			if ellipsometer_type is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("EllipsometerType value must be on a single line")
			try:
				ellipsometer_type = int(value)
			except ValueError:
				raise filter_error("EllipsometerType must be an integer")
			if not (ellipsometer_type == RAE or ellipsometer_type == RPE or ellipsometer_type == RCE):
				raise filter_error("EllipsometerType must %i, %i or %i" % (RAE, RPE, RCE))
		
		# The Delta_min has to be interpreted as a float.
		elif keyword == "DeltaMin":
			if Delta_min is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("DeltaMin value must be on a single line")
			try:
				Delta_min = float(value)
			except ValueError:
				raise filter_error("DeltaMin must be a float")
			if Delta_min < -360.0 or Delta_min > 360.0:
				raise filter_error("DeltaMin must be between -360 and +360")
		
		# consider_backside_on_monitoring is an integer that takes either 0 or 1.
		elif keyword == "ConsiderBacksideOnMonitoring":
			if consider_backside_on_monitoring is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("ConsiderBacksideOnMonitoring value must be on a single line")
			try:
				consider_backside_on_monitoring = bool(int(value))
			except ValueError:
				raise filter_error("Invalid ConsiderBacksideOnMonitoring")
		
		# The ellipsometer type is an integer.
		elif keyword == "MonitoringEllipsometerType":
			if monitoring_ellipsometer_type is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("MonitoringEllipsometerType value must be on a single line")
			try:
				monitoring_ellipsometer_type = int(value)
			except ValueError:
				raise filter_error("MonitoringEllipsometerType must be an integer")
			if not (monitoring_ellipsometer_type == RAE or monitoring_ellipsometer_type == RPE or monitoring_ellipsometer_type == RCE):
				raise filter_error("MonitoringEllipsometerType must %i, %i or %i" % (RAE, RPE, RCE))
		
		# The Delta_min has to be interpreted as a float.
		elif keyword == "MonitoringDeltaMin":
			if monitoring_Delta_min is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("MonitoringDeltaMin value must be on a single line")
			try:
				monitoring_Delta_min = float(value)
			except ValueError:
				raise filter_error("Invalid MonitoringDeltaMin value")
			if monitoring_Delta_min < -360.0 or monitoring_Delta_min > 360.0:
				raise filter_error("MonitoringDeltaMin must be between -360 and +360")
		
		# The sublayer thickness has to be interpreted as a float.
		elif keyword == "MonitoringSublayerThickness":
			if monitoring_sublayer_thickness is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("MonitoringSublayerThickness value must be on a single line")
			try:
				monitoring_sublayer_thickness = float(value)
			except ValueError:
				raise filter_error("MonitoringSublayerThickness must be a float")
			if monitoring_sublayer_thickness <= 0.0:
				raise filter_error("MonitoringSublayerThickness must be positive")
		
		# Needle materials are strings. We verify that these materials
		# exist and that they are not mixtures.
		elif keyword == "NeedleMaterials":
			if needle_materials is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("NeedleMaterials value must be on a single line")
			needle_materials = value.split()
			for needle_material in needle_materials:
				if material_catalog.get_material(needle_material).is_mixture():
					raise filter_error("NeedleMaterials cannot be mixtures")
		
		# Fourier parameters are a mixture material, a Q function and an
		# optical thickness.
		elif keyword == "FourierParameters":
			if Fourier_parameters is not None:
				raise filter_error("Multiple definition in filter")
			if isinstance(value, list):
				raise filter_error("FourierParameters value must be on a single line")
			elements = value.split()
			if len(elements) != 3:
				raise filter_error("FourierParameters must provide material, Q function and optical thickness")
			Fourier_material = elements[0]
			Q_function = elements[1]
			try:
				OT = float(elements[2])
			except ValueError:
				raise filter_error("Optical thickness in FourierParameters must be a float")
			if not material_catalog.get_material(Fourier_material).is_mixture():
				raise filter_error("Material in FourierParameters must be a mixture")
			if not Q_function in optimization_Fourier.Q_function_choices:
				raise filter_error("Unknown Q function in FourierParameters")
			if OT <= 0.0:
				raise filter_error("Optical thickness in FourierParameters must be positive")
			Fourier_parameters = (Fourier_material, Q_function, OT)
		
		# Stack formula include a formula and a list of materials.
		elif keyword == "FrontStackFormula" or keyword == "BackStackFormula":
			try:
				sub_keywords, sub_values = simple_parser.parse(value)
			except simple_parser.parsing_error, error:
				raise filter_error(str(error))
			if sub_keywords[0] != "Formula":
				raise filter_error("%s must begin by the formula" % keyword)
			if isinstance(sub_values[0], list):
				stack_formula = sub_values[0][0]
				for line in sub_values[0][1:]:
					stack_formula += "\n" + line
			else:
				stack_formula = sub_values[0]
			try:
				stack.analyse_stack_formula(stack_formula)
			except stack.stack_error:
				raise filter_error("Invalid formula in %s" % keyword)
			stack_materials = {}
			for i in range(1, len(sub_keywords)):
				symbol = sub_keywords[i]
				if len(symbol) != 1 or not symbol in string.ascii_letters:
					raise filter_error("Symbols in stack formula must be a single letter")
				elements = sub_values[i].split()
				if len(elements) < 1:
					raise filter_error("Missing symbol description %s" % keyword)
				material_name = elements[0]
				if material_catalog.get_material(material_name).is_mixture():
					if len(elements) < 2 or len(elements) > 2:
						raise filter_error("The index of mixtures must be provided in %s" % keyword)
					if elements[1] == "min":
						stack_materials[symbol] = (material_name, stack.MIN)
					elif elements[1] == "max":
						stack_materials[symbol] = (material_name, stack.MAX)
					else:
						try:
							index = float(elements[1])
						except ValueError:
							raise filter_error("Invalid index provided in %s" % keyword)
						stack_materials[symbol] = (material_name, index)
				else:
					if len(elements) > 1:
						raise filter_error("Cannot provide an index for regular materials in %s" % keyword)
					stack_materials[symbol] = (material_name, None)
			symbols = stack_materials.keys()
			for char in stack_formula:
				if char in string.ascii_letters and not char in symbols:
					raise filter_error("Undefined symbol in %s" % keyword)
			if keyword == "FrontStackFormula":
				if front_stack_formula:
					raise filter_error("Can only provide one FrontStackFormula")
				front_stack_formula = stack_formula
				front_stack_materials = stack_materials
			else:
				if back_stack_formula:
					raise filter_error("Can only provide one BackStackFormula")
				back_stack_formula = stack_formula
				back_stack_materials = stack_materials
		
		# A homogeneous layer is defined by the material name, a thickness
		# and an index in the case of mixtures.
		elif keyword == "FrontLayer" or keyword == "BackLayer":
			if isinstance(value, list):
				raise filter_error("FrontLayer or BackLayer description must be on a single line")
			elements = value.split()
			layer_material = elements[0]
			if material_catalog.get_material(layer_material).is_mixture():
				if len(elements) != 3:
					raise filter_error("If the material of FrontLayer or BackLayer is a mixture, thickness and index must be provided")
				try:
					layer_thickness = float(elements[1])
					layer_index = float(elements[2])
				except ValueError:
					raise filter_error("FrontLayer or BackLayer thickness and index must be floats")
			else:	
				if len(elements) != 2:
					raise filter_error("If the material of FrontLayer or BackLayer is a regular material, the thickness must be provided")
				try:
					layer_thickness = float(elements[1])
				except ValueError:
					raise filter_error("FrontLayer or BackLayer thickness must be a float")
				layer_index = None
			if layer_thickness < 0.0:
				raise filter_error("FrontLayer or BackLayer thickness must be positive")
			
			if keyword == "FrontLayer":
				front_layers.append(layer_material)
				front_thickness.append(layer_thickness)
				front_index.append(layer_index)
				front_step_profiles.append([])
				front_layer_descriptions.append([])
				front_refine_thickness.append(None)
				front_refine_index.append(None)
				front_preserve_OT.append(None)
				front_add_needles.append(None)
				front_add_steps.append(None)
				last_layer_added = FRONT
			else:
				back_layers.append(layer_material)
				back_thickness.append(layer_thickness)
				back_index.append(layer_index)
				back_step_profiles.append([])
				back_layer_descriptions.append([])
				back_refine_thickness.append(None)
				back_refine_index.append(None)
				back_preserve_OT.append(None)
				back_add_needles.append(None)
				back_add_steps.append(None)
				last_layer_added = BACK
		
		# An inhomogeneous layer is defined by the material name, on
		# the first line, and by sublayer thickness and index on the
		# other lines.
		elif keyword == "FrontGradedLayer" or keyword == "BackGradedLayer":
			if (not isinstance(value, list)) or len(value) < 2:
				raise filter_error("FrontGradedLayer or BackGradedLayer must provide material and at least one step")
			layer_material = value.pop(0)
			if not material_catalog.get_material(layer_material).is_mixture():
				raise filter_error("Material in FrontGradedLayer or BackGradedLayer must be a mixture")
			layer_thickness = []
			profile = []
			while value:
				sublayer = value.pop(0).split()
				if len(sublayer) != 2:
					raise filter_error("Each step in FrontGradedLayer or BackGradedLayer must provide step thickness and number")
				try:
					layer_thickness.append(float(sublayer[0]))
					profile.append(int(sublayer[1]))
				except ValueError:
					raise filter_error("FrontGradedLayer or BackGradedLayer step number must be an integer and thickness must be a float")
			if min(profile) < 0:
				raise filter_error("Steps in FrontGradedLayer or BackGradedLayer must be positive integers")
			if min(layer_thickness) < 0.0:
				raise filter_error("Step thickness in FrontGradedLayer or BackGradedLayer must be positive")
			
			if keyword == "FrontGradedLayer":
				front_layers.append(layer_material)
				front_thickness.append(layer_thickness)
				front_index.append([])
				front_step_profiles.append(profile)
				front_layer_descriptions.append([])
				front_refine_thickness.append(None)
				front_refine_index.append(None)
				front_preserve_OT.append(None)
				front_add_needles.append(None)
				front_add_steps.append(None)
				last_layer_added = FRONT
			else:
				back_layers.append(layer_material)
				back_thickness.append(layer_thickness)
				back_index.append([])
				back_step_profiles.append(profile)
				back_layer_descriptions.append([])
				back_refine_thickness.append(None)
				back_refine_index.append(None)
				back_preserve_OT.append(None)
				back_add_needles.append(None)
				back_add_steps.append(None)
				last_layer_added = BACK
		
		# A layer description can be provided after a layer.
		elif keyword == "LayerDescription":
			# A layer description must happen after a layer.
			if last_layer_added is None:
				raise filter_error("LayerDescription provided without a layer")
			# Interpret the description. 
			try:
				layer_description = _eval(value)
			except Exception:
				raise filter_error("Invalid LayerDescription")
			# Only one layer description is allowed for each layer.
			if last_layer_added == FRONT:
				if front_layer_descriptions[-1] != []:
					raise filter_error("Only one LayerDescription by layer is allowed")
				front_layer_descriptions[-1] = layer_description
			else:
				if back_layer_descriptions[-1] != []:
					raise filter_error("Only one LayerDescription by layer is allowed")
				back_layer_descriptions[-1] = layer_description
		
		# An indication to refine the thickness of the layer can be
		# provided after the layer.
		elif keyword == "RefineThickness":
			# A refine indication must happen after a layer.
			if last_layer_added is None:
				raise filter_error("RefineThickness provided without a layer")
			try:
				refine = bool(int(value))
			except ValueError:
				raise filter_error("Invalid RefineThickness value")
			# Only one indication is allowed for each layer.
			if last_layer_added == FRONT:
				if front_refine_thickness[-1] is not None:
					raise filter_error("Only one RefineThickness by layer is allowed")
				else:
					front_refine_thickness[-1] = refine
			else:
				if back_refine_thickness[-1] is not None:
					raise filter_error("Only one RefineThickness by layer is allowed")
				else:
					back_refine_thickness[-1] = refine
		
		# An indication to refine the index of the layer can be
		# provided after the layer.
		elif keyword == "RefineIndex":
			# A refine indication must happen after a layer.
			if last_layer_added is None:
				raise filter_error("RefineIndex provided without a layer")
			try:
				refine = bool(int(value))
			except ValueError:
				raise filter_error("Invalid RefineIndex")
			# Only one indication is allowed for each layer.
			if last_layer_added == FRONT:
				if front_refine_index[-1] is not None:
					raise filter_error("Only one RefineIndex by layer is allowed")
				front_refine_index[-1] = refine
			else:
				if back_refine_index[-1] is not None:
					raise filter_error("Only one RefineIndex by layer is allowed")
				back_refine_index[-1] = refine
		
		# An indication to preserve the OT of the layer can be provided
		# after the layer.
		elif keyword == "PreserveOT":
			# A preserve OT indication must happen after a layer.
			if last_layer_added is None:
				raise filter_error("PreserveOT provided without a layer")
			try:
				preserve_OT = bool(int(value))
			except ValueError:
				raise filter_error("Invalid PreserveOT")
			# Only one indication is allowed for each layer.
			if last_layer_added == FRONT:
				if front_preserve_OT[-1] is not None:
					raise filter_error("Only one PreserveOT by layer is allowed")
				front_preserve_OT[-1] = preserve_OT
			else:
				if back_preserve_OT[-1] is not None:
					raise filter_error("Only one PreserveOT by layer is allowed")
				back_preserve_OT[-1] = preserve_OT
		
		# An indication to add needles in the layer can be provided after
		# the layer.
		elif keyword == "AddNeedles":
			# A add_needles indication must happen after a layer.
			if last_layer_added is None:
				raise filter_error("AddNeedles provided without a layer")
			try:
				add_needles = bool(int(value))
			except ValueError:
				raise filter_error("Invalid AddNeedles value")
			# Only one indication is allowed for each layer.
			if last_layer_added == FRONT:
				if front_add_needles[-1] is not None:
					raise filter_error("Only one AddNeedles by layer is allowed")
				front_add_needles[-1] = add_needles
			else:
				if back_add_needles[-1] is not None:
					raise filter_error("Only one AddNeedles by layer is allowed")
				back_add_needles[-1] = add_needles
		
		# An indication to add steps in the layer can be provided after
		# the layer.
		elif keyword == "AddSteps":
			# A add_steps indication must happen after a layer.
			if last_layer_added is None:
				raise filter_error("AddSteps provided without a layer")
			try:
				add_steps = bool(int(value))
			except ValueError:
				raise filter_error("Invalid AddSteps value")
			# Only one indication is allowed for each layer.
			if last_layer_added == FRONT:
				if front_add_steps[-1] is not None:
					raise filter_error("Only one AddSteps by layer is allowed")
				front_add_steps[-1] = add_steps
			else:
				if back_add_steps[-1] is not None:
					raise filter_error("Only one AddSteps by layer is allowed")
				back_add_steps[-1] = add_steps
		
		else:
			raise filter_error("Unknown keyword %s while reading filter" % keyword)
	
	new_filter = optical_filter(material_catalog)
	
	# Set the properties of the filter.
	if description is not None:
		new_filter.set_description(description)
	if consider_backside is not None:
		new_filter.set_consider_backside(consider_backside)
	if dont_consider_substrate is not None:
		new_filter.set_dont_consider_substrate(dont_consider_substrate)
	if wavelengths != []:
		new_filter.set_wavelengths(wavelengths)
	if wavelength_range_from is not None:
		new_filter.set_wavelengths_by_range(wavelength_range_from, wavelength_range_to, wavelength_range_by)
	if center_wavelength is not None:
		new_filter.set_center_wavelength(center_wavelength)
	if step_spacing is not None:
		new_filter.set_step_spacing(step_spacing)
	if minimum_thickness is not None:
		new_filter.set_minimum_thickness(minimum_thickness)
	if ellipsometer_type is not None:
		new_filter.set_ellipsometer_type(ellipsometer_type)
	if Delta_min is not None:
		new_filter.set_Delta_min(Delta_min)
	if monitoring_sublayer_thickness is not None:
		new_filter.set_monitoring_sublayer_thickness(monitoring_sublayer_thickness)
	if consider_backside_on_monitoring is not None:
		new_filter.set_consider_backside_on_monitoring(consider_backside_on_monitoring)
	if monitoring_ellipsometer_type is not None:
		new_filter.set_monitoring_ellipsometer_type(monitoring_ellipsometer_type)
	if monitoring_Delta_min is not None:
		new_filter.set_monitoring_Delta_min(monitoring_Delta_min)
	if illuminant is not None:
		new_filter.set_illuminant(illuminant)
	if observer is not None:
		new_filter.set_observer(observer)
	if needle_materials is not None:
		new_filter.set_needle_materials(needle_materials)
	if Fourier_parameters is not None:
		new_filter.set_Fourier_parameters(Fourier_parameters)
	if front_medium is not None:
		new_filter.set_medium(front_medium, FRONT)
	if back_medium is not None:
		new_filter.set_medium(back_medium, BACK)
	if substrate is not None:
		new_filter.set_substrate(substrate)
	if substrate_thickness is not None:
		new_filter.set_substrate_thickness(substrate_thickness)
	if front_stack_formula:
		new_filter.set_stack_formula(front_stack_formula, front_stack_materials, FRONT)
	if back_stack_formula:
		new_filter.set_stack_formula(back_stack_formula, back_stack_materials, BACK)
	for i in range(len(front_layers)):
		material_nb = new_filter.get_material_nb(front_layers[i])
		material = new_filter.get_material(material_nb)
		if front_step_profiles[i] == []:
			if material.is_mixture():
				n_min, n_max = material.get_index_range(new_filter.get_center_wavelength())
				if front_index[i] < 0.999999 * n_min or front_index[i] > 1.000001 * n_max:
					raise filter_error("%f is outside the range of available indices for material %s" % (front_index[i], front_layers[i]))
			new_filter.add_layer(front_layers[i], front_thickness[i], TOP, FRONT, index = front_index[i], description = front_layer_descriptions[i])
			if front_refine_thickness[i] is not None:
				new_filter.set_refine_layer_thickness(i, front_refine_thickness[i], FRONT)
			if front_refine_index[i] is not None:
				new_filter.set_refine_layer_index(i, front_refine_index[i], FRONT)
			if front_preserve_OT[i] is not None:
				if front_preserve_OT[i]:
					if new_filter.get_refine_layer_thickness(i, FRONT):
						raise filter_error("To preserve the OT of a layer, its thickness cannot be refined.")
					if not new_filter.get_refine_layer_index(i, FRONT):
						raise filter_error("To preserve the OT of a layer, its index must is refined.")
				new_filter.set_preserve_OT(i, front_preserve_OT[i], FRONT)
			if front_add_needles[i] is not None:
				if front_add_needles[i] and not new_filter.get_refine_layer_thickness(i, FRONT):
					raise filter_error("It is not possible to add needles in a layer if its thickness is not refined.")
				new_filter.set_add_needles(i, front_add_needles[i], FRONT)
			if front_add_steps[i] is not None:
				if front_add_steps[i] and not new_filter.get_refine_layer_index(i, FRONT):
					raise filter_error("It is not possible to add steps in a layer if its index is not refined.")
				new_filter.set_add_steps(i, front_add_steps[i], FRONT)
		else:
			if max(front_step_profiles[i]) > len(new_filter.get_material_index(material_nb)):
				raise filter_error("Step(s) outside of range for material %s" % front_layers[i])
			new_filter.add_graded_layer_from_steps_with_material_nb(material_nb, front_step_profiles[i], front_thickness[i], TOP, FRONT, description = front_layer_descriptions[i])
			if front_refine_thickness[i] or front_refine_index[i] or front_preserve_OT[i]:
				raise filter_error("It is not possible to refine graded-index layers.")
			if front_add_needles[i] or front_add_steps[i]:
				raise filter_error("It is not possible to add needles or steps in graded-index layers.")
	
	for i in range(len(back_layers)):
		material_nb = new_filter.get_material_nb(back_layers[i])
		material = new_filter.get_material(material_nb)
		if back_step_profiles[i] == []:
			if material.is_mixture():
				n_min, n_max = material.get_index_range(new_filter.set_center_wavelength())
				if back_index[i] < n_min or back_index[i] > n_max:
					raise filter_error("%f is outside the range of available indices for material %s" % (back_index[i], back_layers[i]))
			new_filter.add_layer(back_layers[i], back_thickness[i], TOP, BACK, index = back_index[i], description = back_layer_descriptions[i])
			if back_refine_thickness[i] is not None:
				new_filter.set_refine_layer_thickness(i, back_refine_thickness[i], BACK)
			if back_refine_index[i] is not None:
				new_filter.set_refine_layer_index(i, back_refine_index[i], BACK)
			if back_preserve_OT[i] is not None:
				if back_preserve_OT[i]:
					if new_filter.get_refine_layer_thickness(i, BACK):
						raise filter_error("To preserve the OT of a layer, its thickness cannot be refined.")
					if not new_filter.get_refine_layer_index(i, BACK):
						raise filter_error("To preserve the OT of a layer, its index must is refined.")
				new_filter.set_preserve_OT(i, back_preserve_OT[i], BACK)
			if back_add_needles[i] is not None:
				if back_add_needles[i] and not new_filter.get_refine_layer_thickness(i, BACK):
					raise filter_error("It is not possible to add needles in a layer if its thickness is not refined.")
				new_filter.set_add_needles(i, back_add_needles[i], BACK)
			if back_add_steps[i] is not None:
				if back_add_steps[i] and not new_filter.get_refine_layer_index(i, BACK):
					raise filter_error("It is not possible to add steps in a layer if its index is not refined.")
				new_filter.set_add_steps(i, back_add_steps[i], BACK)
		else:
			if max(back_step_profiles[i]) > len(new_filter.get_material_index(material_nb)):
				raise filter_error("Step(s) outside of range for material %s" % back_layers[i])
			new_filter.add_graded_layer_from_steps_with_material_nb(material_nb, back_step_profiles[i], back_thickness[i], TOP, BACK, description = back_layer_descriptions[i])
			if back_refine_thickness[i] or back_refine_index[i]:
				raise filter_error("It is not possible to refine graded-index layers.")
			if back_add_needles[i] or back_add_steps[i]:
				raise filter_error("It is not possible to add needles or steps in graded-index layers.")
	
	new_filter.set_modified(False)
	
	return new_filter



########################################################################
#                                                                      #
# read_filter                                                          #
#                                                                      #
########################################################################
def read_filter(filename, material_catalog = None):
	"""Read a filter file
	
	This function takes a single argument:
	  filename          the full name of the file containing the filter;
	  material_catalog  (optional) the material catalog to use with this
		                  project;
	and returns a single output argument:
	  filter            the filter.
	
	If the filter is not properly formatted, a parsing error is raised."""
	
	file = open(filename)
	lines = file.readlines()
	file.close()
	
	filter = parse_filter(lines, material_catalog)
	
	return filter


######################################################################
#                                                                    #
# write_filter                                                       #
#                                                                    #
######################################################################
def write_filter(filter, outfile, prefix = ""):
	"""Write the filter to a file
	
	This function takes 2 or 3 arguments:
	  filter     the filter to write
	  outfile    the file in which to write and
	  prefix     a prefix to add to every line in the output file, mainly
	             usefull to add a tab when the filter is written in a
	             project file.
	It returns no argument."""
	
	if filter.get_description():
		outfile.write(prefix + "Description: %s\n" % filter.get_description())
	outfile.write(prefix + "Substrate: %s %f\n" % (filter.get_substrate(), filter.get_substrate_thickness()))
	outfile.write(prefix + "FrontMedium: %s\n" % filter.get_medium(FRONT))
	outfile.write(prefix + "BackMedium: %s\n" % filter.get_medium(BACK))
	outfile.write(prefix + "CenterWavelength: %f\n" % filter.get_center_wavelength())
	if filter.get_wavelengths_by_range()[0] == 0.0:
		outfile.write(prefix + "Wavelengths:\n" + prefix +"\t")
		i = 1
		for wavelength in filter.get_wavelengths():
			if i > 8:
				outfile.write("\n" + prefix + "\t")
				i = 1
			outfile.write("%f " % wavelength)
			i += 1
		outfile.write("\n" + prefix + "End\n")
	else:
		outfile.write(prefix + "WavelengthRange: %f %f %f\n" % filter.get_wavelengths_by_range())
	outfile.write(prefix + "DontConsiderSubstrate: %i\n" % filter.get_dont_consider_substrate())
	outfile.write(prefix + "StepSpacing: %f\n" % filter.get_step_spacing())
	outfile.write(prefix + "MinimumThickness: %f\n" % filter.get_minimum_thickness())
	outfile.write(prefix + "Illuminant: %s\n" % filter.get_illuminant())
	outfile.write(prefix + "Observer: %s\n" % filter.get_observer())
	outfile.write(prefix + "ConsiderBackside: %i\n" % filter.get_consider_backside())
	outfile.write(prefix + "EllipsometerType: %s\n" % filter.get_ellipsometer_type())
	outfile.write(prefix + "DeltaMin: %f\n" % filter.get_Delta_min())
	outfile.write(prefix + "ConsiderBacksideOnMonitoring: %i\n" % filter.get_consider_backside_on_monitoring())
	outfile.write(prefix + "MonitoringEllipsometerType: %s\n" % filter.get_monitoring_ellipsometer_type())
	outfile.write(prefix + "MonitoringDeltaMin: %f\n" % filter.get_monitoring_Delta_min())
	outfile.write(prefix + "MonitoringSublayerThickness: %f\n" % filter.get_monitoring_sublayer_thickness())
	needle_materials = filter.get_needle_materials()
	if needle_materials:
		outfile.write(prefix + "NeedleMaterials:")
		for i in range(len(needle_materials)):
			outfile.write(" %s" % needle_materials[i])
		outfile.write("\n")
	Fourier_parameters = filter.get_Fourier_parameters()
	if Fourier_parameters:
		outfile.write(prefix + "FourierParameters: %s %s %s\n" % Fourier_parameters)
	stack_formula, stack_materials = filter.get_stack_formula(FRONT)
	if stack_formula:
		outfile.write(prefix + "FrontStackFormula:\n")
		lines = stack_formula.splitlines()
		if len(lines) == 1:
			outfile.write(prefix + "\tFormula: %s\n" % stack_formula)
		else:
			outfile.write(prefix + "\tFormula:\n")
			for line in lines:
				outfile.write(prefix + "\t\t%s\n" % line)
			outfile.write(prefix + "\tEnd\n")
		for (symbol, material) in stack_materials.iteritems():
			if material[1] is None:
				outfile.write(prefix + "\t%s: %s\n" % (symbol, material[0]))
			elif material[1] == stack.MIN:
				outfile.write(prefix + "\t%s: %s min\n" % (symbol, material[0]))
			elif material[1] == stack.MAX:
				outfile.write(prefix + "\t%s: %s max\n" % (symbol, material[0]))
			else:
				outfile.write(prefix + "\t%s: %s %.10f\n" % (symbol, material[0], material[1]))
		outfile.write(prefix + "End\n")
	stack_formula, stack_materials = filter.get_stack_formula(BACK)
	if stack_formula:
		outfile.write(prefix + "BackStackFormula:\n")
		outfile.write(prefix + "\tFormula: %s\n" % stack_formula)
		for (symbol, material) in stack_materials.iteritems():
			if material[1] is None:
				outfile.write(prefix + "\t%s: %s\n" % (symbol, material[0]))
			elif material[1] == stack.MIN:
				outfile.write(prefix + "\t%s: %s min\n" % (symbol, material[0]))
			elif material[1] == stack.MAX:
				outfile.write(prefix + "\t%s: %s max\n" % (symbol, material[0]))
			else:
				outfile.write(prefix + "\t%s: %s %.6f\n" % (symbol, material[0], material[1]))
		outfile.write(prefix + "End\n")
	for i in range(filter.get_nb_layers(FRONT)):
		if filter.is_graded(i, FRONT):
			outfile.write(prefix + "FrontGradedLayer:\n")
			outfile.write(prefix + "\t%s\n" % filter.get_layer_material_name(i, FRONT))
			thickness, step_profile = filter.get_layer_step_profile(i, FRONT)
			for j in range(len(thickness)):
				outfile.write(prefix + "\t%.10f %i\n" % (thickness[j], step_profile[j]))
			outfile.write(prefix + "End\n")
		else:
			if filter.get_layer_material(i, FRONT).is_mixture():
				outfile.write(prefix + "FrontLayer: %s %.6f %.6f\n" % (filter.get_layer_material_name(i, FRONT), filter.get_layer_thickness(i, FRONT), filter.get_layer_index(i, FRONT)))
			else:
				outfile.write(prefix + "FrontLayer: %s %.6f\n" % (filter.get_layer_material_name(i, FRONT), filter.get_layer_thickness(i, FRONT)))
			outfile.write(prefix + "RefineThickness: %i\n" % filter.get_refine_layer_thickness(i, FRONT))
			if filter.materials[filter.front_layers[i]].is_mixture():
				outfile.write(prefix + "RefineIndex: %i\n" % filter.get_refine_layer_index(i, FRONT))
				outfile.write(prefix + "PreserveOT: %i\n" % filter.get_preserve_OT(i, FRONT))
			outfile.write(prefix + "AddNeedles: %i\n" % filter.get_add_needles(i, FRONT))
			if filter.materials[filter.front_layers[i]].is_mixture():
				outfile.write(prefix + "AddSteps: %i\n" % filter.get_add_steps(i, FRONT))
		if filter.front_layer_descriptions[i] != []:
			outfile.write(prefix + "LayerDescription: %s\n" % filter.get_layer_description(i, FRONT))
	for i in range(filter.get_nb_layers(BACK)):
		if filter.is_graded(i, BACK):
			outfile.write(prefix + "BackGradedLayer:\n")
			outfile.write(prefix + "\t%s\n" % filter.get_layer_material_name(i, BACK))
			thickness, step_profile = filter.get_layer_step_profile(i, BACK)
			for j in range(len(filter.back_thickness[i])):
				outfile.write(prefix + "\t%.10f %i\n" % (thickness[j], step_profile[j]))
			outfile.write(prefix + "End\n")
		else:
			if filter.get_layer_material(i, BACK).is_mixture():
				outfile.write(prefix + "BackLayer: %s %.6f %.6f\n" % (filter.get_layer_material_name(i, BACK), filter.get_layer_thickness(i, BACK), filter.get_layer_index(i, BACK)))
			else:
				outfile.write(prefix + "BackLayer: %s %.6f\n" % (filter.get_layer_material_name(i, BACK), filter.get_layer_thickness(i, BACK)))
			outfile.write(prefix + "RefineThickness: %i\n" % filter.get_refine_layer_thickness(i, BACK))
			if filter.materials[filter.back_layers[i]].is_mixture():
				outfile.write(prefix + "RefineIndex: %i\n" % filter.get_refine_layer_index(i, BACK))
				outfile.write(prefix + "PreserveOT: %i\n" % filter.get_preserve_OT(i, BACK))
			outfile.write(prefix + "AddNeedles: %i\n" % filter.get_add_needles(i, BACK))
			if filter.materials[filter.back_layers[i]].is_mixture():
				outfile.write(prefix + "AddSteps: %i\n" % filter.get_add_steps(i, BACK))
		if filter.back_layer_descriptions[i] != []:
			outfile.write(prefix + "Description: %s\n" % filter.get_layer_description(i, BACK))
	
	filter.set_modified(False)
