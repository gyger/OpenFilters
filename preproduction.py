# preproduction.py
# 
# This file implements classes to predict the effect of deposition
# errors on the properties of a filter.
# 
# Copyright (c) 2007-2009,2013 Stephane Larouche.
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
import random
import time

from definitions import *
import config
import optical_filter
import data_holder
import export
import color



UNIFORM = 0
NORMAL = 1

RELATIVE_THICKNESS = 0
PHYSICAL_THICKNESS = 1



########################################################################
#                                                                      #
# random_errors                                                        #
#                                                                      #
########################################################################
class random_errors(object):
	"""A class to simulate the effect of random errors on the properties
	of an optical filter."""
	
	
	methods_by_data_type = {data_holder.REFLECTION: optical_filter.optical_filter.reflection,
	                        data_holder.TRANSMISSION: optical_filter.optical_filter.transmission,
	                        data_holder.ABSORPTION: optical_filter.optical_filter.absorption,
	                        data_holder.REFLECTION_PHASE: optical_filter.optical_filter.reflection_phase,
	                        data_holder.TRANSMISSION_PHASE: optical_filter.optical_filter.transmission_phase,
	                        data_holder.REFLECTION_GD: optical_filter.optical_filter.reflection_GD,
	                        data_holder.TRANSMISSION_GD: optical_filter.optical_filter.transmission_GD,
	                        data_holder.REFLECTION_GDD: optical_filter.optical_filter.reflection_GDD,
	                        data_holder.TRANSMISSION_GDD: optical_filter.optical_filter.transmission_GDD,
	                        data_holder.COLOR: optical_filter.optical_filter.color}
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, original_filter):
		"""Initialize the error analysis.
		
		This method takes a single input argument:
		  original_filter        the filter to study."""
		
		self.original_filter = original_filter
		
		self.data_types = [data_holder.REFLECTION, data_holder.TRANSMISSION]
		
		self.angle = 0.0
		self.polarization = S
		self.illuminant_name = self.original_filter.get_illuminant()
		self.observer_name = self.original_filter.get_observer()
		
		self.thickness_error_type = config.THICKNESS_ERROR_TYPE
		self.relative_thickness_error = config.RELATIVE_THICKNESS_ERROR
		self.physical_thickness_error = config.PHYSICAL_THICKNESS_ERROR
		self.distribution = config.DISTRIBUTION
		self.nb_tests = config.NB_TESTS
		
		self.wavelengths = self.original_filter.get_wavelengths()
		self.nb_wavelengths = len(self.wavelengths)
		self.nb_layers = self.original_filter.get_nb_layers(FRONT)
		self.original_thicknesses = [self.original_filter.get_layer_thickness(i_layer, FRONT) for i_layer in range(self.nb_layers)]
		
		self.expected_result = []
		self.results = []
		self.mean = []
		self.std_dev = []
		self.min = []
		self.max = []
		
		self.progress = 0.0
		
		self.stop_ = False
	
	
	######################################################################
	#                                                                    #
	# set_data_types                                                     #
	#                                                                    #
	######################################################################
	def set_data_types(self, data_types):
		"""Set the data type
		
		This method takes a single input argument:
		  data_types             a sequence of the data types to simulate."""
		
		self.data_types = data_types
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_angle                                                          #
	#                                                                    #
	######################################################################
	def set_angle(self, angle):
		"""Set the angle
		
		This method takes a single input argument:
		  angle                  the angle of incidence."""
		
		self.angle = angle
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_polarization                                                   #
	#                                                                    #
	######################################################################
	def set_polarization(self, polarization):
		"""Set polarization
		
		This method takes a single input argument:
		  polarization           the polarization."""
		
		self.polarization = polarization
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_illuminant                                                     #
	#                                                                    #
	######################################################################
	def set_illuminant(self, illuminant_name):
		"""Set illuminant
		
		This method takes a single input argument:
		  illuminant_name        the name of the illuminant."""
		
		self.illuminant_name = illuminant_name
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_observer                                                       #
	#                                                                    #
	######################################################################
	def set_observer(self, observer_name):
		"""Set observer
		
		This method takes a single input argument:
		  observer_name          the name of the observer."""
		
		self.observer_name = observer_name
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_thickness_error_type                                           #
	#                                                                    #
	######################################################################
	def set_thickness_error_type(self, thickness_error_type):
		"""Set the thickness error type
		
		This method takes a single input argument:
		  thickness_error_type   the error type (either RELATIVE_THICKNESS
		                         or PHYSICAL_THICKNESS)."""
		
		self.thickness_error_type = thickness_error_type
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_relative_thickness_error                                       #
	#                                                                    #
	######################################################################
	def set_relative_thickness_error(self, relative_thickness_error):
		"""Set the relative thickness error
		
		This method takes a single input argument:
		  relative_thickness_error   the relative thickness error."""
		
		self.relative_thickness_error = relative_thickness_error
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_physical_thickness_error                                       #
	#                                                                    #
	######################################################################
	def set_physical_thickness_error(self, physical_thickness_error):
		"""Set the absolute physical thickness error
		
		This method takes a single input argument:
		  physical_thickness_error   the physical thickness error in nm."""
		
		self.physical_thickness_error = physical_thickness_error
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_distribution                                                   #
	#                                                                    #
	######################################################################
	def set_distribution(self, distribution):
		"""Set the distribution
		
		This method takes a single input argument:
		  distribution           the distribution to use (either UNIFORM or
		                         NORMAL)."""
		
		self.distribution = distribution
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_nb_tests                                                       #
	#                                                                    #
	######################################################################
	def set_nb_tests(self, nb_tests):
		"""Set the number of tests
		
		This method takes a single input argument:
		  nb_tests               the number of tests to perform."""
		
		self.nb_tests = nb_tests
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# get_data_types                                                     #
	#                                                                    #
	######################################################################
	def get_data_types(self):
		"""Get the data types
		
		This method returns a list of the properties that are simulated."""
		
		return self.data_types
	
	
	######################################################################
	#                                                                    #
	# get_angle                                                          #
	#                                                                    #
	######################################################################
	def get_angle(self):
		"""Get the angle
		
		This method returns the incidence angle."""
		
		return self.angle
	
	
	######################################################################
	#                                                                    #
	# get_polarization                                                   #
	#                                                                    #
	######################################################################
	def get_polarization(self):
		"""Get polarization
		
		This method returns the polarization."""
		
		return self.polarization
	
	
	######################################################################
	#                                                                    #
	# get_observer                                                       #
	#                                                                    #
	######################################################################
	def get_observer(self):
		"""Get observer
		
		This method returns the name of the observer."""
		
		return self.observer_name
	
	
	######################################################################
	#                                                                    #
	# get_illuminant                                                     #
	#                                                                    #
	######################################################################
	def get_illuminant(self):
		"""Get illuminant
		
		This method returns the name of the illuminant."""
		
		return self.illuminant_name
	
	
	######################################################################
	#                                                                    #
	# get_thickness_error_type                                           #
	#                                                                    #
	######################################################################
	def get_thickness_error_type(self):
		"""Get the thickness error type
		
		This method returns the thickness error type."""
		
		return self.thickness_error_type
	
	
	######################################################################
	#                                                                    #
	# get_relative_thickness_error                                       #
	#                                                                    #
	######################################################################
	def get_relative_thickness_error(self):
		"""Get the relative thickness error
		
		This method returns the relative thickness error."""
		
		return self.relative_thickness_error
	
	
	######################################################################
	#                                                                    #
	# get_physical_thickness_error                                       #
	#                                                                    #
	######################################################################
	def get_physical_thickness_error(self):
		"""Get the absolute error in physical thickness
		
		This method returns the absolute physical thickness error."""
		
		return self.physical_thickness_error
	
	
	######################################################################
	#                                                                    #
	# get_distribution                                                   #
	#                                                                    #
	######################################################################
	def get_distribution(self):
		"""Get the distribution
		
		This method returns the distribution used in the simulation."""
		
		return self.distribution
	
	
	######################################################################
	#                                                                    #
	# get_nb_tests                                                       #
	#                                                                    #
	######################################################################
	def get_nb_tests(self):
		"""Get the number of tests
		
		This method returns the number of tests to perform."""
		
		return self.nb_tests
	
	
	######################################################################
	#                                                                    #
	# simulate                                                           #
	#                                                                    #
	######################################################################
	def simulate(self):
		"""Simulate the effect of errors
		
		This method neither takes nor return any argument. It is possible
		to stop its execution by calling the stop method. The attributes of
		the instance are only modified if the calculation was not stopped."""
		
		self.stop_ = False
		self.progress = 0.0
		
		nb_data_types = len(self.data_types)
		
		# Calculate the expected properties of the design.
		expected_result = [None]*nb_data_types
		for i_data_type, data_type in enumerate(self.data_types):
			if data_type is data_holder.COLOR:
				expected_result[i_data_type] = self.original_filter.color(self.angle, self.polarization, self.illuminant_name, self.observer_name)
			else:
				expected_result[i_data_type] = self.methods_by_data_type[data_type](self.original_filter, self.angle, self.polarization)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
		
		self.progress = 1/(self.nb_tests + 1)
		
		modified_filter = self.original_filter.clone()
		
		results = [[None]*self.nb_tests for _ in range(nb_data_types)]
		for i_test in range(self.nb_tests):
			
			# Vary the thicknesses of homogeneous layers.
			for i_layer in range(self.nb_layers):
				
				# In the case of graded layers, all the sublayers are modified
				# identically.
				if self.original_filter.is_graded(i_layer, FRONT):
					material_nb = self.original_filter.get_layer_material_nb(i_layer, FRONT)
					sublayer_thicknesses, sublayer_steps = self.original_filter.get_layer_step_profile(i_layer, FRONT)
					sublayer_thicknesses = sublayer_thicknesses[:]
					sublayer_steps = sublayer_steps[:]
					nb_sublayers = len(sublayer_thicknesses)
					
					if self.thickness_error_type == RELATIVE_THICKNESS:
						error = self.relative_thickness_error*self.original_thicknesses[i_layer]
					elif self.thickness_error_type == PHYSICAL_THICKNESS:
						error = self.physical_thickness_error
					if self.distribution == UNIFORM:
						sublayer_thickness_variation = random.uniform(-error, +error)/nb_sublayers
					elif self.distribution == NORMAL:
						sublayer_thickness_variation = random.gauss(0.0, error)/nb_sublayers
					
					# Change all sublayer thicknesses while avoiding negative
					# thicknesses.
					for i_sublayer in range(nb_sublayers):
						sublayer_thicknesses[i_sublayer] = max(sublayer_thicknesses[i_sublayer]+sublayer_thickness_variation, 0.0)
					
					# Replace the layer.
					modified_filter.remove_layer(i_layer, FRONT)
					modified_filter.add_graded_layer_from_steps_with_material_nb(material_nb, sublayer_steps, sublayer_thicknesses, i_layer, FRONT)
					
				else:
					if self.thickness_error_type == RELATIVE_THICKNESS:
						error = self.relative_thickness_error*self.original_thicknesses[i_layer]
					elif self.thickness_error_type == PHYSICAL_THICKNESS:
						error = self.physical_thickness_error
					if self.distribution == UNIFORM:
						thickness = random.uniform(self.original_thicknesses[i_layer]-error, self.original_thicknesses[i_layer]+error)
					elif self.distribution == NORMAL:
						thickness = random.gauss(self.original_thicknesses[i_layer], error)
					
					# Avoid negative thickness.
					thickness = max(thickness, 0.0)
					
					modified_filter.change_layer_thickness(thickness, i_layer, FRONT)
			
			for i_data_type, data_type in enumerate(self.data_types):
				if data_type is data_holder.COLOR:
					results[i_data_type][i_test] = modified_filter.color(self.angle, self.polarization, self.illuminant_name, self.observer_name)
				else:
					results[i_data_type][i_test] = self.methods_by_data_type[data_type](modified_filter, self.angle, self.polarization)
			
			# Give other threads a chance...
			time.sleep(0)
			
			if self.stop_: return
			
			self.progress = (i_test + 2)/(self.nb_tests + 1)
		
		# Calculate statistics.
		
		mean = [None]*nb_data_types
		std_dev = [None]*nb_data_types
		min_ = [None]*nb_data_types
		max_ = [None]*nb_data_types
		
		for i_data_type, data_type in enumerate(self.data_types):
			if data_type is data_holder.COLOR:
				illuminant = color.get_illuminant(self.illuminant_name)
				observer = color.get_observer(self.observer_name)
				
				expected_Lab_R = expected_result[i_data_type][0].Lab()
				expected_Lab_T = expected_result[i_data_type][1].Lab()
				
				Lab_R = [results[i_data_type][i_test][0].Lab() for i_test in range(self.nb_tests)]
				Lab_T = [results[i_data_type][i_test][1].Lab() for i_test in range(self.nb_tests)]
				
				mean_Lab_R = [sum(Lab_R[i_test][0] for i_test in range(self.nb_tests))/self.nb_tests,
				              sum(Lab_R[i_test][1] for i_test in range(self.nb_tests))/self.nb_tests,
				              sum(Lab_R[i_test][2] for i_test in range(self.nb_tests))/self.nb_tests]
				mean_Lab_T = [sum(Lab_T[i_test][0] for i_test in range(self.nb_tests))/self.nb_tests,
				              sum(Lab_T[i_test][1] for i_test in range(self.nb_tests))/self.nb_tests,
				              sum(Lab_T[i_test][2] for i_test in range(self.nb_tests))/self.nb_tests]
				
				mean_color_R = color.color(observer, illuminant)
				mean_color_T = color.color(observer, illuminant)
				mean_color_R.set_color(mean_Lab_R, color.Lab)
				mean_color_T.set_color(mean_Lab_T, color.Lab)
				
				mean[i_data_type] = [mean_color_R, mean_color_T]
				
				# Calculate the standard deviation.
				std_dev[i_data_type] = [math.sqrt(sum((lambda Delta_E: Delta_E*Delta_E)(color.Delta_E_2000(Lab_R_i, mean_Lab_R)) for Lab_R_i in Lab_R)/(self.nb_tests-1)),
				                        math.sqrt(sum((lambda Delta_E: Delta_E*Delta_E)(color.Delta_E_2000(Lab_T_i, mean_Lab_T)) for Lab_T_i in Lab_T)/(self.nb_tests-1))]
				
				# Identify test with the largest color difference with respect
				# to the design.
				max_Lab_R = max(Lab_R, key = lambda Lab_R_i: color.Delta_E_2000(Lab_R_i, expected_Lab_R))
				max_Lab_T = max(Lab_T, key = lambda Lab_T_i: color.Delta_E_2000(Lab_T_i, expected_Lab_T))
				
				max_color_R = color.color(observer, illuminant)
				max_color_T = color.color(observer, illuminant)
				max_color_R.set_color(max_Lab_R, color.Lab)
				max_color_T.set_color(max_Lab_T, color.Lab)
				
				# Determine maximum difference.
				max_[i_data_type] = [max_color_R, max_color_T]
			
			else:
				mean[i_data_type] = [0.0]*self.nb_wavelengths
				std_dev[i_data_type] = [0.0]*self.nb_wavelengths
				min_[i_data_type] = [0.0]*self.nb_wavelengths
				max_[i_data_type] = [0.0]*self.nb_wavelengths
				
				for i_wavelength in range(self.nb_wavelengths):
					
					# Calculate the mean.
					mean[i_data_type][i_wavelength] = sum(results[i_data_type][i_test][i_wavelength] for i_test in range(self.nb_tests))/self.nb_tests
					
					# Calculate the standard deviation.
					std_dev[i_data_type][i_wavelength] = math.sqrt(sum((lambda diff: diff*diff)(results[i_data_type][i_test][i_wavelength]-mean[i_data_type][i_wavelength]) for i_test in range(self.nb_tests))/(self.nb_tests-1))
					
					# Determine minimal and maximal values.
					min_[i_data_type][i_wavelength] = min(results[i_data_type][i_test][i_wavelength] for i_test in range(self.nb_tests))
					max_[i_data_type][i_wavelength] = max(results[i_data_type][i_test][i_wavelength] for i_test in range(self.nb_tests))
				
				# Give other threads a chance...
				time.sleep(0)
				
				if self.stop_: return
		
		self.expected_result = expected_result
		self.results = results
		self.mean = mean
		self.std_dev = std_dev
		self.min = min_
		self.max = max_
	
	
	######################################################################
	#                                                                    #
	# stop                                                               #
	#                                                                    #
	######################################################################
	def stop(self):
		"""Stop the simulation
		
		This method neither takes nor return any argument."""
		
		self.stop_ = True
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Reset the results
		
		This method neither takes nor return any argument."""
		
		self.expected_result = []
		self.results = []
		self.mean = []
		self.std_dev = []
		self.min = []
		self.max = []
	
	
	######################################################################
	#                                                                    #
	# get_wavelengths                                                    #
	#                                                                    #
	######################################################################
	def get_wavelengths(self):
		"""Get the wavelengths
		
		This method returns the wavelengths used in the simulation."""
		
		return self.wavelengths
	
	
	######################################################################
	#                                                                    #
	# get_expected_result                                                #
	#                                                                    #
	######################################################################
	def get_expected_result(self):
		"""Get the expected result
		
		This method returns the properties of the designed filter, without
		any errors."""
		
		return self.expected_result
	
	
	######################################################################
	#                                                                    #
	# get_results                                                        #
	#                                                                    #
	######################################################################
	def get_results(self):
		"""Get the results of the simulation
		
		This method returns the results of all individual simulations in
		a list of property objects."""
		
		return self.results
	
	
	######################################################################
	#                                                                    #
	# get_mean                                                           #
	#                                                                    #
	######################################################################
	def get_mean(self):
		"""Get the mean of the results of the simulation
		
		This method returns the average of the the results of the
		simulations in a list."""
		
		return self.mean
	
	
	######################################################################
	#                                                                    #
	# get_std_dev                                                        #
	#                                                                    #
	######################################################################
	def get_std_dev(self):
		"""Get the stardard deviation of the results of the simulation
		
		This method returns the stardard deviation of the the results of
		the simulations in a list."""
		
		return self.std_dev
	
	
	######################################################################
	#                                                                    #
	# get_min_max                                                        #
	#                                                                    #
	######################################################################
	def get_min_max(self):
		"""Get the minimal and maximal results of the simulation
		
		This method returns the minimal and maximal results of the
		simulations in two lists."""
		
		return self.min, self.max
	
	
	######################################################################
	#                                                                    #
	# get_progress                                                       #
	#                                                                    #
	######################################################################
	def get_progress(self):
		"""Get the progress of the simulation
		
		This method returns the progress of the simulation."""
		
		return self.progress
	
	
	######################################################################
	#                                                                    #
	# save                                                               #
	#                                                                    #
	######################################################################
	def save(self, outfile):
		"""Save the results of the analysis
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		if self.thickness_error_type == RELATIVE_THICKNESS:
			thickness_error = "%.2f %%" % (100.0*self.relative_thickness_error)
		elif self.thickness_error_type == PHYSICAL_THICKNESS:
			thickness_error = "%.2f nm" % self.physical_thickness_error
		
		if self.distribution == UNIFORM:
			distribution = "uniform"
		elif self.distribution == NORMAL:
			distribution = "normal"
		
		# Write the header.
		outfile.write("Simulation of %s random thickness errors (%s distribution, %i tests)\n" % (thickness_error, distribution, self.nb_tests))
		
		for i_data_type, data_type in enumerate(self.data_types):
			if data_type is data_holder.COLOR:
				# Write the type specific header.
				outfile.write("%s at %.2f degrees for %s (%s, %s)\n" % (data_holder.DATA_TYPE_NAMES[data_type], self.angle, export.polarization_text(self.polarization), self.illuminant_name, self.observer_name))
				outfile.write("%15s %15s %15s %15s %15s %15s %15s\n" % ("", "design R", "design T", "mean R", "mean T", "maximum R", "maximum T"))
				
				# Write results.
				XYZ_R_expected = self.expected_result[i_data_type][0].XYZ()
				XYZ_T_expected = self.expected_result[i_data_type][1].XYZ()
				xyY_R_expected = self.expected_result[i_data_type][0].xyY()
				xyY_T_expected = self.expected_result[i_data_type][1].xyY()
				Luv_R_expected = self.expected_result[i_data_type][0].Luv()
				Luv_T_expected = self.expected_result[i_data_type][1].Luv()
				Lab_R_expected = self.expected_result[i_data_type][0].Lab()
				Lab_T_expected = self.expected_result[i_data_type][1].Lab()
				LChuv_R_expected = self.expected_result[i_data_type][0].LChuv()
				LChuv_T_expected = self.expected_result[i_data_type][1].LChuv()
				LChab_R_expected = self.expected_result[i_data_type][0].LChab()
				LChab_T_expected = self.expected_result[i_data_type][1].LChab()
				XYZ_R_mean = self.mean[i_data_type][0].XYZ()
				XYZ_T_mean = self.mean[i_data_type][1].XYZ()
				xyY_R_mean = self.mean[i_data_type][0].xyY()
				xyY_T_mean = self.mean[i_data_type][1].xyY()
				Luv_R_mean = self.mean[i_data_type][0].Luv()
				Luv_T_mean = self.mean[i_data_type][1].Luv()
				Lab_R_mean = self.mean[i_data_type][0].Lab()
				Lab_T_mean = self.mean[i_data_type][1].Lab()
				LChuv_R_mean = self.mean[i_data_type][0].LChuv()
				LChuv_T_mean = self.mean[i_data_type][1].LChuv()
				LChab_R_mean = self.mean[i_data_type][0].LChab()
				LChab_T_mean = self.mean[i_data_type][1].LChab()
				XYZ_R_max = self.max[i_data_type][0].XYZ()
				XYZ_T_max = self.max[i_data_type][1].XYZ()
				xyY_R_max = self.max[i_data_type][0].xyY()
				xyY_T_max = self.max[i_data_type][1].xyY()
				Luv_R_max = self.max[i_data_type][0].Luv()
				Luv_T_max = self.max[i_data_type][1].Luv()
				Lab_R_max = self.max[i_data_type][0].Lab()
				Lab_T_max = self.max[i_data_type][1].Lab()
				LChuv_R_max = self.max[i_data_type][0].LChuv()
				LChuv_T_max = self.max[i_data_type][1].LChuv()
				LChab_R_max = self.max[i_data_type][0].LChab()
				LChab_T_max = self.max[i_data_type][1].LChab()
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("X" , XYZ_R_expected[0], XYZ_T_expected[0], XYZ_R_mean[0], XYZ_T_mean[0], XYZ_R_max[0], XYZ_T_max[0]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("Y" , XYZ_R_expected[1], XYZ_T_expected[1], XYZ_R_mean[1], XYZ_T_mean[1], XYZ_R_max[1], XYZ_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("Z" , XYZ_R_expected[2], XYZ_T_expected[2], XYZ_R_mean[2], XYZ_T_mean[2], XYZ_R_max[2], XYZ_T_max[2]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("x" , xyY_R_expected[0], xyY_T_expected[0], xyY_R_mean[0], xyY_T_mean[0], xyY_R_max[0], xyY_T_max[0]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("y" , xyY_R_expected[1], xyY_T_expected[1], xyY_R_mean[1], xyY_T_mean[1], xyY_R_max[1], xyY_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("L" , Luv_R_expected[0], Luv_T_expected[0], Luv_R_mean[0], Luv_T_mean[0], Luv_R_max[0], Luv_T_max[0]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("u*", Luv_R_expected[1], Luv_T_expected[1], Luv_R_mean[1], Luv_T_mean[1], Luv_R_max[1], Luv_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("v*", Luv_R_expected[2], Luv_T_expected[2], Luv_R_mean[2], Luv_T_mean[2], Luv_R_max[2], Luv_T_max[2]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("a*", Lab_R_expected[1], Lab_T_expected[1], Lab_R_mean[1], Lab_T_mean[1], Lab_R_max[1], Lab_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("b*", Lab_R_expected[2], Lab_T_expected[2], Lab_R_mean[2], Lab_T_mean[2], Lab_R_max[2], Lab_T_max[2]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("C*(u*v*)", LChuv_R_expected[1], LChuv_T_expected[1], LChuv_R_mean[1], LChuv_T_mean[1], LChuv_R_max[1], LChuv_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("h(u*v*)", LChuv_R_expected[2], LChuv_T_expected[2], LChuv_R_mean[2], LChuv_T_mean[2], LChuv_R_max[2], LChuv_T_max[2]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("C*(a*b*)", LChab_R_expected[1], LChab_T_expected[1], LChab_R_mean[1], LChab_T_mean[1], LChab_R_max[1], LChab_T_max[1]))
				outfile.write("%15s %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % ("h(a*b*)", LChab_R_expected[2], LChab_T_expected[2], LChab_R_mean[2], LChab_T_mean[2], LChab_R_max[2], LChab_T_max[2]))
				outfile.write("std. dev. R: %.6f, max Delta E R: %.6f\n" % (self.std_dev[i_data_type][0], color.Delta_E_2000(self.max[i_data_type][0], Lab_R_expected)))
				outfile.write("std. dev. T: %.6f, max Delta E T: %.6f\n" % (self.std_dev[i_data_type][1], color.Delta_E_2000(self.max[i_data_type][1], Lab_T_expected)))
			
			else:
				# Write the type specific header.
				outfile.write("%s at %.2f degrees for %s\n" % (data_holder.DATA_TYPE_NAMES[data_type], self.angle, export.polarization_text(self.polarization)))
				outfile.write("%15s %15s %15s %15s %15s %15s\n" % ("wavelength (nm)", "design", "mean", "std. dev.", "minimum", "maximum"))
				
				for i_wvl in range(self.nb_wavelengths):
					
					if self.expected_result[i_data_type][i_wvl] < 1.0e-2:
						outfile.write("%15.6f %15.6e %15.6e %15.6e %15.6e %15.6e\n" % (self.wavelengths[i_wvl], self.expected_result[i_data_type][i_wvl], self.mean[i_data_type][i_wvl], self.std_dev[i_data_type][i_wvl], self.min[i_data_type][i_wvl], self.max[i_data_type][i_wvl]))
					else:
						outfile.write("%15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % (self.wavelengths[i_wvl], self.expected_result[i_data_type][i_wvl], self.mean[i_data_type][i_wvl], self.std_dev[i_data_type][i_wvl], self.min[i_data_type][i_wvl], self.max[i_data_type][i_wvl]))
	
	
	######################################################################
	#                                                                    #
	# save_all_results                                                   #
	#                                                                    #
	######################################################################
	def save_all_results(self, outfile):
		"""Save all the results of the analysis
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		if self.thickness_error_type == RELATIVE_THICKNESS:
			thickness_error = "%.2f %%" % (100.0*self.relative_thickness_error)
		elif self.thickness_error_type == PHYSICAL_THICKNESS:
			thickness_error = "%.2f nm" % self.physical_thickness_error
		
		if self.distribution == UNIFORM:
			distribution = "uniform"
		elif self.distribution == NORMAL:
			distribution = "normal"
		
		# Write the header.
		outfile.write("Simulation of %s random thickness errors (%s distribution, %i tests)\n" % (thickness_error, distribution, self.nb_tests))
		
		for i_data_type, data_type in enumerate(self.data_types):
			if data_type is data_holder.COLOR:
				# Prepare all data.
				XYZ_R = [self.results[i_data_type][i_test][0].XYZ() for i_test in range(self.nb_tests)]
				XYZ_T = [self.results[i_data_type][i_test][1].XYZ() for i_test in range(self.nb_tests)]
				xyY_R = [self.results[i_data_type][i_test][0].xyY() for i_test in range(self.nb_tests)]
				xyY_T = [self.results[i_data_type][i_test][1].xyY() for i_test in range(self.nb_tests)]
				Luv_R = [self.results[i_data_type][i_test][0].Luv() for i_test in range(self.nb_tests)]
				Luv_T = [self.results[i_data_type][i_test][1].Luv() for i_test in range(self.nb_tests)]
				Lab_R = [self.results[i_data_type][i_test][0].Lab() for i_test in range(self.nb_tests)]
				Lab_T = [self.results[i_data_type][i_test][1].Lab() for i_test in range(self.nb_tests)]
				LChuv_R = [self.results[i_data_type][i_test][0].LChuv() for i_test in range(self.nb_tests)]
				LChuv_T = [self.results[i_data_type][i_test][1].LChuv() for i_test in range(self.nb_tests)]
				LChab_R = [self.results[i_data_type][i_test][0].LChab() for i_test in range(self.nb_tests)]
				LChab_T = [self.results[i_data_type][i_test][1].LChab() for i_test in range(self.nb_tests)]
				
				# Write the type specific header.
				outfile.write("%s at %.2f degrees for %s (%s, %s)\n" % (data_holder.DATA_TYPE_NAMES[data_type], self.angle, export.polarization_text(self.polarization), self.illuminant_name, self.observer_name))
				outfile.write("%15s" % "" + "".join(" %15s %15s" % ("test %i R" % (i_test+1), "test %i T" % (i_test+1)) for i_test in range(self.nb_tests)) + "\n")
				
				# Write the result of all tests.
				outfile.write("%15s" % "X"  + "".join(" %15.6f %15.6f" % (XYZ_R[i_test][1], XYZ_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "Y"  + "".join(" %15.6f %15.6f" % (XYZ_R[i_test][1], XYZ_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "Z"  + "".join(" %15.6f %15.6f" % (XYZ_R[i_test][2], XYZ_T[i_test][2]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "x"  + "".join(" %15.6f %15.6f" % (xyY_R[i_test][0], xyY_T[i_test][0]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "y"  + "".join(" %15.6f %15.6f" % (xyY_R[i_test][1], xyY_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "L"  + "".join(" %15.6f %15.6f" % (Luv_R[i_test][0], Luv_T[i_test][0]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "u*" + "".join(" %15.6f %15.6f" % (Luv_R[i_test][1], Luv_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "v*" + "".join(" %15.6f %15.6f" % (Luv_R[i_test][2], Luv_T[i_test][2]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "a*" + "".join(" %15.6f %15.6f" % (Lab_R[i_test][1], Lab_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "b*" + "".join(" %15.6f %15.6f" % (Lab_R[i_test][2], Lab_T[i_test][2]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "C*(u*v*)" + "".join(" %15.6f %15.6f" % (LChuv_R[i_test][1], LChuv_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "h(u*v*)" + "".join(" %15.6f %15.6f" % (LChuv_R[i_test][2], LChuv_T[i_test][2]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "C*(a*b*)" + "".join(" %15.6f %15.6f" % (LChab_R[i_test][1], LChab_T[i_test][1]) for i_test in range(self.nb_tests)) + "\n")
				outfile.write("%15s" % "h(a*b*)" + "".join(" %15.6f %15.6f" % (LChab_R[i_test][2], LChab_T[i_test][2]) for i_test in range(self.nb_tests)) + "\n")
			
			else:
				# Write the type specific header.
				outfile.write("%s at %.2f degrees for %s\n" % (data_holder.DATA_TYPE_NAMES[data_type], self.angle, export.polarization_text(self.polarization)))
				outfile.write("%15s " % "wavelength (nm)" + " ".join("%15s" % ("test %i" % (i_test+1)) for i_test in range(self.nb_tests)) + "\n")
				
				for i_wavelength in range(self.nb_wavelengths):
					outfile.write("%15.6f" % self.wavelengths[i_wavelength])
					for i_test in range(self.nb_tests):
						if self.results[i_data_type][i_test][i_wavelength] < 1.0e-2:
							outfile.write(" %15.6e" % self.results[i_data_type][i_test][i_wavelength])
						else:
							outfile.write(" %15.6f" % self.results[i_data_type][i_test][i_wavelength])
					outfile.write("\n")
