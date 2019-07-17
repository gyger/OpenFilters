# materials.py
# 
# Classes for defining the optical properties of materials and a
# function to read the properties of a material in a material_file.
#
# Copyright (c) 2000-2003,2005-2008,2010-2015 Stephane Larouche.
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



import os
import os.path
import re
import math
import cmath
import copy

import config
from definitions import *
import abeles
import main_directory
import simple_parser
import units



# The various models for the optical properties.
CONSTANT = 0
CAUCHY = 1
TABLE = 2
SELLMEIER = 3


# A few useful dictionaries.
KINDS = {MATERIAL_REGULAR: "Regular",
         MATERIAL_MIXTURE: "Mixture"}
MODELS = {CONSTANT: "Constant",
          CAUCHY: "Cauchy",
          TABLE: "Table",
          SELLMEIER: "Sellmeier"}


# The material directory is relative to the filters directory.
base_directory = main_directory.get_main_directory()
default_material_directory = os.path.join(base_directory, *config.MATERIALS_DIRECTORY)



########################################################################
#                                                                      #
# material_error                                                       #
#                                                                      #
########################################################################
class material_error(Exception):
	"""An exception derived class for material errors."""
	
	def __init__(self, name, value = ""):
		self.name = name
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Material error (%s): %s." % (self.name, self.value)
		else:
			return "Material error (%s)." % self.name



########################################################################
#                                                                      #
# material_does_not_exist_error                                        #
# material_parsing_error                                               #
#                                                                      #
########################################################################
class material_does_not_exist_error(material_error):
	"""An exception derived class for materials that do not exist."""
	
	def __init__(self, name):
		self.name = name
		self.value = "Material does not exist"

class material_parsing_error(material_error):
	"""An exception derived class for material with malformed files."""



########################################################################
#                                                                      #
# material                                                             #
#                                                                      #
########################################################################
class material(object):
	"""A generic class to define materials
	
	All material class derive from this class."""
	
	kind = MATERIAL_REGULAR
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		# The name and description of the material
		self.name = ""
		self.description = ""
		
		# An object for the dispersion.
		self.dispersion = None
		
		# Deposition rate.
		self.rate = None
		
		# Parameters used during deposition, if specified. constants
		# contain names of these parameters while constant_values contain
		# values of these parameters.
		self.constants = []
		self.constant_values = []
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the material
		
		This method returns a clone of the material."""
		
		clone = self.__class__()
		
		clone.__init__()
		
		clone.name = self.name
		clone.description = self.description
		
		clone.rate = copy.copy(self.rate)
		
		clone.constants = self.constants[:]
		clone.constant_values = self.constant_values[:]
		
		clone.set_properties(*copy.deepcopy(self.get_properties()))
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# set_name                                                           #
	#                                                                    #
	######################################################################
	def set_name(self, name):
		"""Set the name of the material
		
		This method takes a single argument:
		  name               the name of the material."""
		
		self.name = name
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the material
		
		This method returns the name of the material."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# set_description                                                    #
	#                                                                    #
	######################################################################
	def set_description(self, description):
		"""Set the description of the material
		
		This method takes a single argument:
		  description        the description of the material."""
		
		self.description = description
	
	
	######################################################################
	#                                                                    #
	# get_description                                                    #
	#                                                                    #
	######################################################################
	def get_description(self):
		"""Get the description of the material
		
		This method returns the description of the material."""
		
		return self.description
	
	
	######################################################################
	#                                                                    #
	# get_kind                                                           #
	#                                                                    #
	######################################################################
	def get_kind(self):
		"""Get the kind of material
		
		This method returns the kind of material (MATERIAL_REGULAR or
		MATERIAL_MIXTURE)."""
		
		return self.kind
	
	
	######################################################################
	#                                                                    #
	# is_mixture                                                         #
	#                                                                    #
	######################################################################
	def is_mixture(self):
		"""Get if the material is a mixture
		
		This method returns a boolean indicating if the material is a
		mixture."""
		
		if self.kind == MATERIAL_MIXTURE:
			return True
		
		else:
			return False
	
	
	######################################################################
	#                                                                    #
	# get_model                                                          #
	#                                                                    #
	######################################################################
	def get_model(self):
		"""Get the model of the material
		
		This method returns the model used to define the dispersion curve
		of the material."""
		
		return self.model
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self):
		"""Set the properties of the material
		
		The derived class implement this method according to the
		dispersion model used."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		The derived class implement this method according to the
		dispersion model used."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# get_index                                                          #
	#                                                                    #
	######################################################################
	def get_index(self, wvl):
		"""Get the index of refraction of the material
		
		This method takes a single argument:
		  wvl                a wavelength
		and returns the real part of the index of refraction at this
		wavelength. This method is not implement for mixtures.
		
		The derived class implement this method according to the
		dispersion model used."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an index structure with the dispersion curve of the
		material at those wavelengths.
		
		The derived class implement this method according to the
		dispersion model used."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# set_deposition_rate                                                #
	#                                                                    #
	######################################################################
	def set_deposition_rate(self, rate):
		"""Set the deposition rate of the material
		
		This method takes a single argument:
		  rate               the deposition rate of the material."""
		
		self.rate = rate
	
	
	######################################################################
	#                                                                    #
	# get_deposition_rate                                                #
	#                                                                    #
	######################################################################
	def get_deposition_rate(self):
		"""Get the deposition rate of the material
		
		This method returns the deposition rate of the material."""
		
		return self.rate
	
	
	######################################################################
	#                                                                    #
	# set_deposition_constants                                           #
	#                                                                    #
	######################################################################
	def set_deposition_constants(self, constants, constant_values):
		"""Set the constant deposition conditions of the material
		
		This method takes 2 arguments:
		  constants          the name of the deposition properties;
		  constant_values    their values.
		
		Regular materials only have constant deposition conditions.
		Mixtures have variable deposition conditions and might also have
		constant deposition conditions."""
		
		self.constants = constants
		self.constant_values = constant_values
	
	
	######################################################################
	#                                                                    #
	# get_deposition_constants                                           #
	#                                                                    #
	######################################################################
	def get_deposition_constants(self):
		"""Get the deposition conditions of the material
		
		This method returns the deposition condition of the material:
		  constants          the name of the deposition properties;
		  constant_values    their values."""
		
		return self.constants, self.constant_values



########################################################################
#                                                                      #
# material_mixture                                                     #
#                                                                      #
########################################################################
class material_mixture(material):
	"""A generic class to define material mixtures
	
	All mixture materials class are derived from this class.
	
	Mixtures class are implemented with the deposition process in mind.
	The deposition systems have a limited resolution and cannot deposit
	any arbitrary index of refraction, but rather a large, but finite,
	number of mixtures. The mixtures are therefore represented by integer
	mixture numbers called x values.
	
	When the dispersion of the mixtures is defined in set_properties, it
	is not possible to define it for all x values. They are rather
	defined by at least 3 x values between 0 and the number of
	depositable mixtures minus one. The dispersion of the other mixtures
	is interpolated using cubic splines."""
	
	kind = MATERIAL_MIXTURE
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material.__init__(self)
		
		# Deposition conditions are described by a number.
		self.X = []
		
		# Parameters used during deposition, if specified. constants and
		# variables contain names of these parameters while constants_values
		# and variables_values contain values of these parameters.
		self.variables = []
		self.variable_values = []
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the material
		
		This method returns a clone of the material."""
		
		clone = material.clone(self)
		
		clone.variables = copy.deepcopy(self.variables)
		clone.variable_values = copy.deepcopy(self.variable_values)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# set_deposition_variables                                           #
	#                                                                    #
	######################################################################
	def set_deposition_variables(self, variables, variable_values):
		"""Set the variable deposition conditions of the material
		
		This method takes 2 arguments:
		  variables          the name of the deposition properties;
		  variable_values    a list of lists of their values."""
		
		self.variables = variables
		self.variable_values = variable_values
	
	
	######################################################################
	#                                                                    #
	# get_deposition_variables                                           #
	#                                                                    #
	######################################################################
	def get_deposition_variables(self):
		"""Get the variable deposition conditions of the material
		
		This method returns the variable deposition conditions:
		  variables          the name of the deposition properties;
		  variable_values    a list of lists of their values."""
		
		return self.variables, self.variable_values
	
	
	######################################################################
	#                                                                    #
	# get_deposition_steps                                               #
	#                                                                    #
	######################################################################
	def get_deposition_steps(self, wvl):
		"""Get the deposition steps
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns a list of the index of refraction of all the mixtures
		that can be deposited at this wavelength.
		
		The derived class must implement this method according to the
		dispersion model."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# get_index_range                                                    #
	#                                                                    #
	######################################################################
	def get_index_range(self, wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction.
		
		The derived class must implement this method according to the
		dispersion model."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# change_index_wavelength                                            #
	#                                                                    #
	######################################################################
	def change_index_wavelength(self, old_n, old_wvl, new_wvl):
		"""Convert the index of refraction to another wavelength
		
		This method takes 3 argument:
		  old_n              an index of refraction;
		  old_wvl            the wavelength at which old_n is defined;
		  new_wvl            the wavelength at which the index is desired;
		and returns the index of refraction at new_wvl using the dispersion
		relations of the mixture.
		
		The derived class must implement this method according to the
		dispersion model."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# change_index_profile_wavelength                                    #
	#                                                                    #
	######################################################################
	def change_index_profile_wavelength(self, index_profile, old_wvl, new_wvl):
		"""Change the wavelength at which an index profile is defined
		
		This method takes 3 arguments:
		  index_profile     a list containing the index profile;
		  old_wvl           the wavelength at which the index profile is
		                    defined;
		  new_wvl           the wavelength at which the index profile
		                    must be defined;
		and modifies index_profile to the new_wvl.
		
		The wavelength of the index profile is changed by repeatadly
		calling change_index_wavelength on every element of the index
		profile. It is possible to accelerate the execution of this
		method by making a dispersion model specific method that does not
		call change_index_wavelength."""
		
		if new_wvl != old_wvl:
			for i in range(len(index_profile)):
				index_profile[i] = self.change_index_wavelength(index_profile[i], old_wvl, new_wvl)
	
	
	######################################################################
	#                                                                    #
	# check_monotonicity                                                 #
	#                                                                    #
	######################################################################
	def check_monotonicity(self, wvl):
		"""Check if the refractive index is monotonic at a wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean value.
		
		This method allows one to make sure that the refractive index is
		monotonic at a given wavelength. This monotonicity is necessary for
		the interpolation methods to work correctly."""
		
		raise NotImplementedError("Subclass must implement this method")



########################################################################
#                                                                      #
# material_constant                                                    #
#                                                                      #
########################################################################
class material_constant(material):
	"""A class for dispersion-less materials"""
	
	model = CONSTANT
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material.__init__(self)
		
		# Value of the index.
		self.N = 0.0+0.0j
		
		# The dispersion object.
		self.dispersion = abeles.constant()
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, N):
		"""Set the properties of the material
		
		This method takes a single argument:
		  N                  the complex index of refraction of the
		                     material."""
		
		self.N = N
		
		# Set the dispersion object.
		self.dispersion.set_constant(self.N)
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the complex index of refraction of the
		material."""
		
		return self.N,
	
	
	######################################################################
	#                                                                    #
	# get_index                                                          #
	#                                                                    #
	######################################################################
	def get_index(self, wvl):
		"""Get the index of refraction of the material
		
		This method takes a single argument:
		  wvl                a wavelength
		and returns the real part of the index of refraction at this
		wavelength."""
		
		return self.N.real
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an index structure with the dispersion curve of the
		material at those wavelengths."""
		
		N = abeles.N(wvls)
		self.dispersion.set_N_constant(N)
		
		return N



########################################################################
#                                                                      #
# material_table                                                       #
#                                                                      #
########################################################################
class material_table(material):
	"""A class to define the dispersion curve of material with a table of
	data"""
	
	model = TABLE
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material.__init__(self)
		
		# Wavelengths and index where the dispersion is defined
		self.wvls = []
		self.N = []
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, wvls, N):
		"""Set the properties of the material
		
		This method takes 2 arguments:
		  wvls               a list of wavelengths;
		  N                  a list of the complex index of refraction at
		                     those wavelengths."""
		
		self.wvls = wvls
		self.N = N
		
		length = len(self.wvls)
		
		# Set the dispersion object.
		self.dispersion = abeles.table(length)
		for i in range(length):
			self.dispersion.set_table(i, self.wvls[i], self.N[i])
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  wvls               a list of wavelengths;
		  N                  a list of the complex index of refraction at
		                     those wavelengths."""
		
		return self.wvls, self.N
	
	
	######################################################################
	#                                                                    #
	# get_index                                                          #
	#                                                                    #
	######################################################################
	def get_index(self, wvl):
		"""Get the index of refraction of the material
		
		This method takes a single argument:
		  wvl                a wavelength
		and returns the real part of the index of refraction at this
		wavelength."""
		
		n = self.dispersion.get_table_index(wvl)
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an index structure with the dispersion curve of the
		material at those wavelengths."""
		
		N = abeles.N(wvls)
		self.dispersion.set_N_table(N)
		
		return N



########################################################################
#                                                                      #
# material_Cauchy                                                      #
#                                                                      #
########################################################################
class material_Cauchy(material):
	"""A class to define the dispersion curve of material with a Cauchy
	dispersion formula and an Urbach absorption tail"""
	
	model = CAUCHY
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material.__init__(self)
		
		# Values of A, B and C in the Cauchy model if it is used. And,
		# eventually the values of A_k, exponent and edge for the Urbach
		# absorbtion tail. The exponent and the edge are not set to 0.0
		# to avoit math range errors.
		self.A = 0.0
		self.B = 0.0
		self.C = 0.0
		self.A_k = 0.0
		self.exponent = 1.0
		self.edge = 4000.0
		
		# Create the dispersion object.
		self.dispersion = abeles.Cauchy()
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, A, B, C, A_k, exponent, edge):
		"""Set the properties of the material
		
		This method takes 6 arguments:
		  A, B, C               the parameters of the Cauchy model;
		  A_k, exponent, edge   the parameters of the Urbach absorption
		                        tail."""
		
		self.A = A
		self.B = B
		self.C = C
		self.A_k = A_k
		self.exponent = exponent
		self.edge = edge
		
		# Set the dispersion object.
		self.dispersion.set_Cauchy(self.A, self.B, self.C, self.A_k, self.exponent, self.edge)
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  A, B, C               the parameters of the Cauchy model;
		  A_k, exponent, edge   the parameters of the Urbach absorption
		                        tail."""
		
		return self.A, self.B, self.C, self.A_k, self.exponent, self.edge
	
	
	######################################################################
	#                                                                    #
	# get_index                                                          #
	#                                                                    #
	######################################################################
	def get_index(self, wvl):
		"""Get the index of refraction of the material
		
		This method takes a single argument:
		  wvl                a wavelength
		and returns the real part of the index of refraction at this
		wavelength."""
		
		wvl_micron = wvl/1000.0
		wvl_micron_square = wvl_micron*wvl_micron
		n = self.A + self.B/wvl_micron_square + self.C/(wvl_micron_square*wvl_micron_square)
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an index structure with the dispersion curve of the
		material at those wavelengths."""
		
		N = abeles.N(wvls)
		self.dispersion.set_N_Cauchy(N)
		
		return N



########################################################################
#                                                                      #
# material_Sellmeier                                                   #
#                                                                      #
########################################################################
class material_Sellmeier(material):
	"""A class to define the dispersion curve of material with a Sellmeier
	dispersion formula"""
	
	model = SELLMEIER
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material.__init__(self)
		
		# Values of Bs and Cs in the Sellmeier model.
		self.B1 = 0.0
		self.C1 = 0.0
		self.B2 = 0.0
		self.C2 = 0.0
		self.B3 = 0.0
		self.C3 = 0.0
		self.A_k = 0.0
		self.exponent = 1.0
		self.edge = 4000.0
		
		# Create the dispersion object.
		self.dispersion = abeles.Sellmeier()
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, B1, C1, B2, C2, B3, C3, A_k, exponent, edge):
		"""Set the properties of the material
		
		This method takes 6 arguments:
		  B1, C1, B2, C2, B3, C3   the parameters of the Sellmeier model;
		  A_k, exponent, edge      the parameters of the Urbach absorption
		                           tail."""
		
		self.B1 = B1
		self.C1 = C1
		self.B2 = B2
		self.C2 = C2
		self.B3 = B3
		self.C3 = C3
		self.A_k = A_k
		self.exponent = exponent
		self.edge = edge
		
		# Set the dispersion object.
		self.dispersion.set_Sellmeier(self.B1, self.C1, self.B2, self.C2, self.B3, self.C3, self.A_k, self.exponent, self.edge)
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  B1, C1, B2, C2, B3, C3   the parameters of the Sellmeier model;
		  A_k, exponent, edge      the parameters of the Urbach absorption."""
		
		return self.B1, self.C1, self.B2, self.C2, self.B3, self.C3, self.A_k, self.exponent, self.edge
	
	
	######################################################################
	#                                                                    #
	# get_index                                                          #
	#                                                                    #
	######################################################################
	def get_index(self, wvl):
		"""Get the index of refraction of the material
		
		This method takes a single argument:
		  wvl                a wavelength
		and returns the real part of the index of refraction at this
		wavelength."""
		
		wvl_micron = wvl/1000.0
		wvl_micron_square = wvl_micron*wvl_micron
		n = math.sqrt(1+self.B1*wvl_micron_square/(wvl_micron_square-self.C1)
		               +self.B2*wvl_micron_square/(wvl_micron_square-self.C2)
		               +self.B3*wvl_micron_square/(wvl_micron_square-self.C3))
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an index structure with the dispersion curve of the
		material at those wavelengths."""
		
		N = abeles.N(wvls)
		self.dispersion.set_N_Sellmeier(N)
		
		return N



########################################################################
#                                                                      #
# material_mixture_constant                                            #
#                                                                      #
########################################################################
class material_mixture_constant(material_mixture):
	"""A class for dispersion-less material mixtures"""
	
	model = CONSTANT
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material_mixture.__init__(self)
		
		# Index is described by a list of constants.
		self.N = []
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, X, N):
		"""Set the properties of the material
		
		This method takes 2 arguments:
		  X                  a list of mixtures;
		  N                  a list of the complex index of refraction of
		                     the mixtures defined in X.
		
		Both X and the real part of N must be monotonously increasing."""
		
		self.X = X
		self.N = N
		
		nb_mixtures = len(X)
		
		self.dispersion = abeles.constant_mixture(nb_mixtures)
		for i in range(nb_mixtures):
			self.dispersion.set_constant_mixture(i, self.X[i], self.N[i])
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  X                  a list of mixtures;
		  N                  a list of the complex index of refraction of
		                     the mixtures defined in X."""
		
		return self.X, self.N
	
	
	######################################################################
	#                                                                    #
	# get_deposition_steps                                               #
	#                                                                    #
	######################################################################
	def get_deposition_steps(self, wvl):
		"""Get the deposition steps
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns a list of the index of refraction of all the mixtures
		that can be deposited at this wavelength."""
		
		deposition_steps = [self.dispersion.get_constant_mixture_index(float(x), wvl) for x in range(self.X[-1]+1)]
		
		return deposition_steps
	
	
	######################################################################
	#                                                                    #
	# check_monotonicity                                                 #
	#                                                                    #
	######################################################################
	def check_monotonicity(self, wvl):
		"""Check if the refractive index is monotonic at a wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean value.
		
		This method allows one to make sure that the refractive index is
		monotonic at a given wavelength. This monotonicity is necessary for
		the interpolation methods to work correctly."""
		
		return self.dispersion.get_constant_mixture_monotonicity(wvl)
	
	
	######################################################################
	#                                                                    #
	# get_index_range                                                    #
	#                                                                    #
	######################################################################
	def get_index_range(self, wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		return self.N[0].real, self.N[-1].real
	
	
	######################################################################
	#                                                                    #
	# change_index_wavelength                                            #
	#                                                                    #
	######################################################################
	def change_index_wavelength(self, old_n, old_wvl, new_wvl):
		"""Convert the index of refraction to another wavelength
		
		This method takes 3 argument:
		  old_n              an index of refraction;
		  old_wvl            the wavelength at which old_n is defined;
		  new_wvl            the wavelength at which the index is desired;
		and returns the index of refraction at new_wvl using the dispersion
		relations of the mixture."""
		
		# There is no dispersion...
		return old_n
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an mixture index structure with the dispersion curve of
		the material at those wavelengths."""
		
		N = abeles.N_mixture(self.dispersion, wvls)
		
		return N



########################################################################
#                                                                      #
# material_mixture_table                                               #
#                                                                      #
########################################################################
class material_mixture_table(material_mixture):
	"""A class for material mixtures defined by table of index of
	refraction"""
	
	model = TABLE
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material_mixture.__init__(self)
		
		# Index is described by a list of constants.
		self.wvls = []
		self.N = []
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, X, wvls, N):
		"""Set the properties of the material
		
		This method takes 3 arguments:
		  X                  a list of mixtures;
		  wvls               a list of wavelengths;
		  N                  a list of lists of the complex index of
		                     refraction of the mixtures defined in X at the
		                     wavelengths defined in wvls.
		
		X and wvls must be monotonously increasing. The real part of N
		must be monotonously increasing as a function of X."""
		
		self.X = X
		self.wvls = wvls
		self.N = N
		
		nb_mixture = len(X)
		nb_wvls = len(wvls)
		
		self.dispersion = abeles.table_mixture(nb_mixture, nb_wvls)
		for i_mix in range(nb_mixture):
			for i_wvl in range(nb_wvls):
				self.dispersion.set_table_mixture(i_mix, i_wvl, self.X[i_mix], self.wvls[i_wvl], self.N[i_mix][i_wvl])
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  X                  a list of mixtures;
		  wvls               a list of wavelengths;
		  N                  a list of lists of the complex index of
		                     refraction of the mixtures defined in X at the
		                     wavelengths defined in wvls."""
		
		return self.X, self.wvls, self.N
	
	
	######################################################################
	#                                                                    #
	# get_deposition_steps                                               #
	#                                                                    #
	######################################################################
	def get_deposition_steps(self, wvl):
		"""Get the deposition steps
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns a list of the index of refraction of all the mixtures
		that can be deposited at this wavelength."""
		
		return [self.dispersion.get_table_mixture_index(float(x), wvl) for x in range(self.X[-1]+1)]
	
	
	######################################################################
	#                                                                    #
	# check_monotonicity                                                 #
	#                                                                    #
	######################################################################
	def check_monotonicity(self, wvl):
		"""Check if the refractive index is monotonic at a wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean value.
		
		This method allows one to make sure that the refractive index is
		monotonic at a given wavelength. This monotonicity is necessary for
		the interpolation methods to work correctly."""
		
		return self.dispersion.get_table_mixture_monotonicity(wvl)
	
	
	######################################################################
	#                                                                    #
	# get_index_range                                                    #
	#                                                                    #
	######################################################################
	def get_index_range(self, wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		return self.dispersion.get_table_mixture_index_range(wvl)
	
	
	######################################################################
	#                                                                    #
	# change_index_wavelength                                            #
	#                                                                    #
	######################################################################
	def change_index_wavelength(self, old_n, old_wvl, new_wvl):
		"""Convert the index of refraction to another wavelength
		
		This method takes 3 argument:
		  old_n              an index of refraction;
		  old_wvl            the wavelength at which old_n is defined;
		  new_wvl            the wavelength at which the index is desired;
		and returns the index of refraction at new_wvl using the dispersion
		relations of the mixture."""
		
		return self.dispersion.change_table_mixture_index_wvl(old_n, old_wvl, new_wvl)
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an mixture index structure with the dispersion curve of
		the material at those wavelengths."""
		
		N = abeles.N_mixture(self.dispersion, wvls)
		
		return N



########################################################################
#                                                                      #
# material_mixture_Cauchy                                              #
#                                                                      #
########################################################################
class material_mixture_Cauchy(material_mixture):
	"""A class for material mixtures defined by Cauchy dispersion formula
	and Urbach absorption tail"""
	
	model = CAUCHY
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material_mixture.__init__(self)
		
		# Index is described by lists of A, B, C, A_k, exponent and edge.
		self.A = []
		self.B = []
		self.C = []
		self.A_k = []
		self.exponent = []
		self.edge = []
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, X, A, B, C, A_k, exponent, edge):
		"""Set the properties of the material
		
		This method takes 7 arguments:
		  X                    a list of mixtures;
		  A, B, C              lists of the Cauchy parameters for the
		                       mixtures defined in X;
		  A_k, exponent, edge  list of the Urbach absorption tail parameters
		                       for the mixtures defined in X.
		
		X and the real part of the index of refraction must be monotonously
		increasing."""
		
		self.X = X
		self.A = A
		self.B = B
		self.C = C
		self.A_k = A_k
		self.exponent = exponent
		self.edge = edge
		
		nb_mixtures = len(self.X)
		
		self.dispersion = abeles.Cauchy_mixture(nb_mixtures)
		for i in range(nb_mixtures):
			self.dispersion.set_Cauchy_mixture(i, self.X[i], self.A[i], self.B[i], self.C[i], self.A_k[i], self.exponent[i], self.edge[i])
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the poperties of the material:
		  X                    a list of mixtures;
		  A, B, C              lists of the Cauchy parameters for the
		                       mixtures defined in X;
		  A_k, exponent, edge  list of the Urbach absorption tail
		                       parameters for the mixtures defined in X."""
		
		return self.X, self.A, self.B, self.C, self.A_k, self.exponent, self.edge
	
	
	######################################################################
	#                                                                    #
	# get_deposition_steps                                               #
	#                                                                    #
	######################################################################
	def get_deposition_steps(self, wvl):
		"""Get the deposition steps
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns a list of the index of refraction of all the mixtures
		that can be deposited at this wavelength."""
		
		return [self.dispersion.get_Cauchy_mixture_index(float(x), wvl) for x in range(self.X[-1]+1)]
	
	
	######################################################################
	#                                                                    #
	# check_monotonicity                                                 #
	#                                                                    #
	######################################################################
	def check_monotonicity(self, wvl):
		"""Check if the refractive index is monotonic at a wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean value.
		
		This method allows one to make sure that the refractive index is
		monotonic at a given wavelength. This monotonicity is necessary for
		the interpolation methods to work correctly."""
		
		return self.dispersion.get_Cauchy_mixture_monotonicity(wvl)
	
	
	######################################################################
	#                                                                    #
	# change_index_wavelength                                            #
	#                                                                    #
	######################################################################
	def change_index_wavelength(self, old_n, old_wvl, new_wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		n = self.dispersion.change_Cauchy_mixture_index_wvl(old_n, old_wvl, new_wvl)
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_index_range                                                    #
	#                                                                    #
	######################################################################
	def get_index_range(self, wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		n_min, n_max = self.dispersion.get_Cauchy_mixture_index_range(wvl)
		
		return n_min, n_max
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an mixture index structure with the dispersion curve of
		the material at those wavelengths."""
		
		N = abeles.N_mixture(self.dispersion, wvls)
		
		return N



########################################################################
#                                                                      #
# material_mixture_Sellmeier                                           #
#                                                                      #
########################################################################
class material_mixture_Sellmeier(material_mixture):
	"""A class for material mixtures defined by Sellmeier dispersion
	 formula"""
	
	model = SELLMEIER
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the material instance"""
		
		material_mixture.__init__(self)
		
		# Index is described by lists of B1, C1, B2, C2, B3, C3, A_k, exponent and edge.
		self.B1 = []
		self.C1 = []
		self.B2 = []
		self.C2 = []
		self.B3 = []
		self.C3 = []
		self.A_k = []
		self.exponent = []
		self.edge = []
	
	
	######################################################################
	#                                                                    #
	# set_properties                                                     #
	#                                                                    #
	######################################################################
	def set_properties(self, X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge):
		"""Set the properties of the material
		
		This method takes 10 arguments:
		  X                       a list of mixtures;
		  B1, C1, B2, C2, B3, C3  lists of the Sellmeier parameters for the
		                          mixtures defined in X;
		  A_k, exponent, edge     list of the Urbach absorption tail
		                          parameters for the mixtures defined in X.
		
		X and the real part of the index of refraction must be monotonously
		increasing."""
		
		self.X = X
		self.B1 = B1
		self.C1 = C1
		self.B2 = B2
		self.C2 = C2
		self.B3 = B3
		self.C3 = C3
		self.A_k = A_k
		self.exponent = exponent
		self.edge = edge
		
		nb_mixtures = len(self.X)
		
		self.dispersion = abeles.Sellmeier_mixture(nb_mixtures)
		for i in range(nb_mixtures):
			self.dispersion.set_Sellmeier_mixture(i, self.X[i], self.B1[i], self.C1[i], self.B2[i], self.C2[i], self.B3[i], self.C3[i], self.A_k[i], self.exponent[i], self.edge[i])
	
	
	######################################################################
	#                                                                    #
	# get_properties                                                     #
	#                                                                    #
	######################################################################
	def get_properties(self):
		"""Get the properties of the material
		
		This method returns the properties of the material:
		  X                       a list of mixtures;
		  B1, C1, B2, C2, B3, C3  lists of the Sellmeier parameters for the
		                          mixtures defined in X;
		  A_k, exponent, edge     list of the Urbach absorption tail parameters
		                          for the mixtures defined in X."""
		
		return self.X, self.B1, self.C1, self.B2, self.C2, self.B3, self.C3, self.A_k, self.exponent, self.edge
	
	
	######################################################################
	#                                                                    #
	# get_deposition_steps                                               #
	#                                                                    #
	######################################################################
	def get_deposition_steps(self, wvl):
		"""Get the deposition steps
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns a list of the index of refraction of all the mixtures
		that can be deposited at this wavelength."""
		
		return [self.dispersion.get_Sellmeier_mixture_index(float(x), wvl) for x in range(self.X[-1]+1)]
	
	
	######################################################################
	#                                                                    #
	# check_monotonicity                                                 #
	#                                                                    #
	######################################################################
	def check_monotonicity(self, wvl):
		"""Check if the refractive index is monotonic at a wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean value.
		
		This method allows one to make sure that the refractive index is
		monotonic at a given wavelength. This monotonicity is necessary for
		the interpolation methods to work correctly."""
		
		return self.dispersion.get_Sellmeier_mixture_monotonicity(wvl)
	
	
	######################################################################
	#                                                                    #
	# change_index_wavelength                                            #
	#                                                                    #
	######################################################################
	def change_index_wavelength(self, old_n, old_wvl, new_wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		n = self.dispersion.change_Sellmeier_mixture_index_wvl(old_n, old_wvl, new_wvl)
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_index_range                                                    #
	#                                                                    #
	######################################################################
	def get_index_range(self, wvl):
		"""Get the range of available index of refraction
		
		This method takes a single argument:
		  wvl                a wavelength;
		and returns the range of indices of refraction."""
		
		n_min, n_max = self.dispersion.get_Sellmeier_mixture_index_range(wvl)
		
		return n_min, n_max
	
	
	######################################################################
	#                                                                    #
	# get_N                                                              #
	#                                                                    #
	######################################################################
	def get_N(self, wvls):
		"""Get the dispersion curve of the material
		
		This method takes a single argument:
		  wvls               a wavelengths structure
		and returns an mixture index structure with the dispersion curve of
		the material at those wavelengths."""
		
		N = abeles.N_mixture(self.dispersion, wvls)
		
		return N



########################################################################
#                                                                      #
# material_catalog                                                     #
#                                                                      #
########################################################################
class material_catalog(object):
	"""A class to list materials."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, directory = None):
		"""Initialize the material catalog instance"""
		
		if directory == None:
			self.directory = default_material_directory
			self.default_material_catalog = True
		else:
			self.directory = directory
			self.default_material_catalog = False
		
		self.materials = dict((str(os.path.splitext(filename)[0]), None) for filename in os.listdir(self.directory) if os.path.splitext(filename)[1].upper() == ".MAT")
	
	
	######################################################################
	#                                                                    #
	# add_material                                                       #
	#                                                                    #
	######################################################################
	def add_material(self, material, write = True):
		"""Add a new material or replace a material in the catalog
		
		This method takes 1 or 2 arguments:
		  material           the material to add to the catalog.
		  write              (optional) a boolean indicating if the
		                     material should be written to the directory
		                     of the catalog (default value is True).
		
		All the materials in the material directory are listed during the
		initialization. This method is only necessary when a new material
		is created. If the creation of the file fails, a OSError or a
		IOError will be raised."""
		
		if write:
			write_material(material, directory = self.directory)
		
		material_name = material.get_name()
		self.materials[material_name] = material
	
	
	######################################################################
	#                                                                    #
	# remove_material                                                    #
	#                                                                    #
	######################################################################
	def remove_material(self, material_name, delete = True):
		"""Remove a material from the catalog
		
		This method takes 1 or 2 arguments:
		  material_name      the name of the material to remove from the
		                     catalog.
		  delete             (optional) a boolean indicating if the
		                     material should be deleted from the disk
		                     (default value is True).
		
		This method will raise a OSError if the file cannot be deleted."""
		
		if delete:
			delete_material(material_name, self.directory)
		
		del self.materials[material_name]
	
	
	######################################################################
	#                                                                    #
	# get_material_names                                                 #
	#                                                                    #
	######################################################################
	def get_material_names(self):
		"""Get all material names
		
		This method return a list of the names of all the materials in
		alphabetical order."""
		
		# Get the material names and sort them in a case insensitive
		# manner.
		material_names = self.materials.keys()
		material_names.sort(key = str.upper)
		
		return material_names
	
	
	######################################################################
	#                                                                    #
	# get_material                                                       #
	#                                                                    #
	######################################################################
	def get_material(self, material_name):
		"""Get a material
		
		This method takes one argument:
		  material_name      the name of a material;
		and returns the material instance corresponding to that name. If
		the material does not exist or there is a problem parsing it, an
		exception is raised. """
		
		if material_name not in self.materials:
			raise material_does_not_exist_error(material_name)
		
		# Read the material only if necessary.
		if self.materials[material_name] is None:
			self.materials[material_name] = read_material(material_name, self.directory)
		
		return self.materials[material_name]
	
	
	######################################################################
	#                                                                    #
	# material_exists                                                    #
	#                                                                    #
	######################################################################
	def material_exists(self, material_name):
		"""Get if a material exist
		
		This method takes one argument:
		  material_name      the name of a material;
		and returns a boolean indicating if the material exists."""
		
		return material_name in self.materials
	
	
	######################################################################
	#                                                                    #
	# is_default_material_catalog                                        #
	#                                                                    #
	######################################################################
	def is_default_material_catalog(self):
		"""Get if the catalog is the one for default materials
		
		This method takes no argument and returns a boolean indicating if
		the catalog is the one for default materials."""
		
		return self.default_material_catalog



########################################################################
#                                                                      #
# material_catalogs                                                    #
#                                                                      #
########################################################################
class material_catalogs(object):
	"""A class to handle many material catalogs.
	
	When a material with the same name is defined in many of the
	catalogs, the one from the catalog higher in the list (at a higher
	index) is prefered."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, catalogs = []):
		"""Initialize the material catalog instance
		
		This method takes a single optional argument:
		  catalogs           a list of the catalogs."""
		
		self.catalogs = catalogs
	
	
	######################################################################
	#                                                                    #
	# get_catalogs                                                       #
	#                                                                    #
	######################################################################
	def get_catalogs(self):
		"""Get the list of catalogs
		
		This method returns the list of catalogs."""
		
		return self.catalogs
	
	
	######################################################################
	#                                                                    #
	# get_material_names                                                 #
	#                                                                    #
	######################################################################
	def get_material_names(self):
		"""Get all material names
		
		This method return a list of the names of all the materials in
		alphabetical order."""
		
		material_names = set()
		for catalog in self.catalogs:
			material_names |= set(catalog.get_material_names())
		
		material_names = list(material_names)
		
		# Sort the material names in a case insensitive manner.
		material_names.sort(key = str.upper)
		
		return material_names
	
	
	######################################################################
	#                                                                    #
	# get_material                                                       #
	#                                                                    #
	######################################################################
	def get_material(self, material_name):
		"""Get a material
		
		This method takes one argument:
		  material_name      the name of a material;
		and returns the material instance corresponding to that name. If
		the material does not exist or there is a problem parsing it, an
		exception is raised. If the material is present in more than one
		catalog, the one from the catalog higher in the list is prefered."""
		
		for catalog in reversed(self.catalogs):
			if catalog.material_exists(material_name):
				return catalog.get_material(material_name)
		else:
			raise material_does_not_exist_error(material_name)
	
	
	######################################################################
	#                                                                    #
	# material_exists                                                    #
	#                                                                    #
	######################################################################
	def material_exists(self, material_name):
		"""Get if a material exist
		
		This method takes one argument:
		  material_name      the name of a material;
		and returns a boolean indicating if the material exists."""
		
		for catalog in self.catalogs:
			if catalog.material_exists(material_name):
				return True
		else:
			return False



########################################################################
#                                                                      #
# parse_material                                                       #
#                                                                      #
########################################################################
def parse_material(name, lines):
	"""Parse a material description
	
	This function interprets the description of a material. It takes a
	two input arguments:
		name                 the name of the material and
	  lines                a list of lines describing the material;
	and returns the material.
	
	The material material_file must contain, in that order
		- A description of the material;
		- The kind of material, either homogeneous or inhomogeneous;
		- The model used to describe the material, either constant, Cauchy
		or table;
		- For materials described by a table, the wavelengths for which the
		index in defined;
		- The optical properties of the material, according to the model;
	and can contain, to be able to use the deposition_conditions function:
		- The deposition rate(s);
		- The constant deposition conditions;
		- For inhomogeneous materials, the variable deposition conditions.
	
	For homogeneous materials the properties are defined on a single
	line while for inhomogeneous materials they are defined on multiple
	lines. Each of these lines must begin by an integer step number.
	The first step number should be 0 and step number must be in
	increasing order. When deposition conditions are generated by the
	deposition_conditions function, the index profile will be
	discretized to make a step at every unity by doing a spline between
	the values given in the material material_file."""
	
	try:
		keywords, values = simple_parser.parse(lines)
	except simple_parser.parsing_error, error:
		raise material_parsing_error("Cannot parse material because %s" % error.get_value())
	
	description = None
	kind = None
	model = None
	properties = None
	rates = None
	constants = []
	constant_values = []
	variables = []
	variable_values = []
	
	for i in range(len(keywords)):
		keyword = keywords[i]
		value = values[i]
		
		# The description is an arbitrary single line text.
		if keyword == "Description":
			if description is not None:
				raise material_parsing_error(name, "Multiple description in material")
			if isinstance(value, list):
				raise material_parsing_error(name, "Description must be on a single line")
			description = value
		
		# The kind of material is regular or mixture.
		elif keyword == "Kind":
			if kind is not None:
				raise material_parsing_error(name, "Multiple definition in material")
			if isinstance(value, list):
				raise material_parsing_error(name, "Kind must be on a single line")
			kind = value.upper()
			if not (kind == "REGULAR" or kind == "MIXTURE"):
				raise material_parsing_error(name, "Kind must be regular or mixture")
		
		# The model is constant, Cauchy or table.
		elif keyword == "Model":
			if model is not None:
				raise material_parsing_error(name, "Multiple definition in material")
			if isinstance(value, list):
				raise material_parsing_error(name, "Model must be on a single line")
			model = value.upper()
			if not (model == "CONSTANT" or model == "CAUCHY" or model == "SELLMEIER" or model == "TABLE"):
				raise material_parsing_error(name, "Unknown material model!")
		
		# The properties come in multiple format and the specific
		# verifications are done later.
		elif keyword == "Properties":
			if properties is not None:
				raise material_parsing_error(name, "Multiple definition in material")
			properties = value
	
		# The rate is a single float.
		elif keyword == "Rate":
			if rates is not None:
				raise material_parsing_error(name, "Multiple definition in material")
			if isinstance(value, list):
				raise material_parsing_error(name, "Rate must be on a single line")
			try:
				rates = float(value)
			except ValueError:
				raise material_parsing_error(name, "Rate must be a float")
	
		# Rates are a list of floats.
		elif keyword == "Rates":
			if rates is not None:
				raise material_parsing_error(name, "Multiple definition in material")
			if isinstance(value, list):
				raise material_parsing_error(name, "Rates must be on a single line")
			elements = value.split()
			rates = []
			for element in elements:
				try:
					rate = float(element)
				except ValueError:
					raise material_parsing_error(name, "Rates must be floats")
				rates.append(rate)
		
		# Constants are parameters that are kept constant during the
		# deposition. Regular material only have constants.
		elif keyword == "Constants":
			if not isinstance(value, list):
				raise material_parsing_error(name, "Constants must be on multiple line")
			for line in value:
				elements = line.split(":")
				if len(elements) != 2:
					raise material_parsing_error(name, "Constants must contain one description and one value")
				constants.append(elements[0].strip())
				try:
					constant_value = float(elements[1])
				except ValueError:
					raise material_parsing_error(name, "Constants values must be floats")
				constant_values.append(constant_value)
		
		# Variables are parameters that are varied during the deposition of
		# mixtures.
		elif keyword == "Variables":
			if not isinstance(value, list):
				raise material_parsing_error(name, "Variables must be on multiple line")
			for line in value:
				elements = line.split(":")
				if len(elements) != 2:
					raise material_parsing_error(name, "Variables must contain one description and a list of values")
				variables.append(elements[0].strip())
				variable_values_ = []
				sub_elements = elements[1].split()
				for sub_element in sub_elements:
					try:
						variable_value = float(sub_element)
					except ValueError:
						raise material_parsing_error(name, "Variable values must be floats")
					variable_values_.append(variable_value)
				variable_values.append(variable_values_)
		
		else:
			raise material_parsing_error(name, "Unknown keyword %s" % keyword)
	
	if kind is None or model is None or properties is None:
		raise material_parsing_error(name, "Missing information")
	
	for value in constant_values:
		if isinstance(value, list):
			raise material_parsing_error(name, "A single value is necessary for constants")
	
	if kind == "REGULAR":
		if isinstance(rates, list):
			raise material_parsing_error(name, "A single rate is necessary for regular material")
		if variables:
			raise material_parsing_error(name, "Regular material cannot have variables")
	
	else:
		if rates is not None:
			if not isinstance(rates, list):
				raise material_parsing_error(name, "A list of rates must be provided for mixtures")
			if len(rates) != len(properties):
				raise material_parsing_error(name, "The number of rates must be equal to the number of properties")
			for values in variable_values:
				if not isinstance(values, list):
					raise material_parsing_error(name, "Variable values must be lists")
				if len(values) != len(properties):
					raise material_parsing_error(name, "The number of variable values must be equal to the number of properties")
	
	# Analyse the properties according to the kind and model of material.
	if kind == "REGULAR":
		
		if model == "CONSTANT":
			try:
				N = complex(properties)
			except ValueError:
				raise material_parsing_error(name, "Invalid property format (%s)" % properties)
		
		elif model == "TABLE":
			wvls = []
			N = []
			for line in properties:
				elements = line.split()
				if len(elements) != 2:
					raise material_parsing_error(name, "Invalid property format (%s)" % line)
				try:
					wvls.append(float(elements[0]))
					N.append(complex(elements[1]))
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % line)
		
		elif model == "CAUCHY":
			parameters = properties.split()
			if len(parameters) == 3:
				try:
					A = float(parameters[0])
					B = float(parameters[1])
					C = float(parameters[2])
					A_k = 0.0
					exponent = 1.0
					edge = 4000.0
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
			elif len(parameters) == 6:
				try:
					A = float(parameters[0])
					B = float(parameters[1])
					C = float(parameters[2])
					A_k = float(parameters[3])
					exponent = float(parameters[4])
					edge = float(parameters[5])
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
			else:
				raise material_parsing_error(name, "Invalid property format (%s)" % properties)
		
		elif model == "SELLMEIER":
			parameters = properties.split()
			if len(parameters) == 6:
				try:
					B1 = float(parameters[0])
					C1 = float(parameters[1])
					B2 = float(parameters[2])
					C2 = float(parameters[3])
					B3 = float(parameters[4])
					C3 = float(parameters[5])
					A_k = 0.0
					exponent = 1.0
					edge = 4000.0
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
			elif len(parameters) == 9:
				try:
					B1 = float(parameters[0])
					C1 = float(parameters[1])
					B2 = float(parameters[2])
					C2 = float(parameters[3])
					B3 = float(parameters[4])
					C3 = float(parameters[5])
					A_k = float(parameters[6])
					exponent = float(parameters[7])
					edge = float(parameters[8])
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
			else:
				raise material_parsing_error(name, "Invalid property format (%s)" % properties)
	
	else:
		if model == "CONSTANT":
			nb_mixtures = len(properties)
			if nb_mixtures < 2:
				raise material_parsing_error(name, "Invalid property format (there must be at least 2 mixtures)")
			X = [0]*nb_mixtures
			N = [0.0+0.0j]*nb_mixtures
			for i in range(nb_mixtures):
				parameters = properties[i].split()
				if len(parameters) != 2:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
				try:
					X[i] = int(parameters[0])
					N[i] = complex(parameters[1])
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties)
		
		elif model == "TABLE":
			# The first line represents the mixtures.
			line = properties.pop(0)
			mixtures = line.split()
			nb_mixtures = len(mixtures)
			# The other lines are one by wavelength.
			nb_wvls = len(properties)
			if nb_mixtures < 2 or nb_wvls < 2:
				raise material_parsing_error(name, "Invalid property format (there must be at least 2 mixtures and 2 wavelengths)")
			X = [0]*nb_mixtures
			wvls = [0.0]*nb_wvls
			N = [None]*nb_mixtures
			for i_mix in range(nb_mixtures):
				N[i_mix] = [0.0+0.0j]*nb_wvls
			for i_mix in range(nb_mixtures):
				try:
					X[i_mix] = int(mixtures[i_mix])
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)", mixtures)
			for i_wvl in range(nb_wvls):
				parameters = properties[i_wvl].split()
				if len(parameters) != nb_mixtures+1:
					raise material_parsing_error(name, "Invalid property format (%s)", properties[i_wvl])
				try:
					wvls[i_wvl] = float(parameters[0])
					for i_mix in range(nb_mixtures):
						N[i_mix][i_wvl] = complex(parameters[1+i_mix])
				except ValueError:
					raise material_parsing_error(name, "Invalid property format (%s)", properties[i_wvl])
		
		elif model == "CAUCHY":
			nb_mixtures = len(properties)
			if nb_mixtures < 2:
				raise material_parsing_error(name, "Invalid property format (there must be at least 2 mixtures)")
			X = [0]*nb_mixtures
			A = [0.0]*nb_mixtures
			B = [0.0]*nb_mixtures
			C = [0.0]*nb_mixtures
			A_k = [0.0]*nb_mixtures
			exponent = [1.0]*nb_mixtures
			edge = [4000.0]*nb_mixtures
			for i in range(nb_mixtures):
				parameters = properties[i].split()
				if len(parameters) == 4:
					try:
						X[i] = int(parameters[0])
						A[i] = float(parameters[1])
						B[i] = float(parameters[2])
						C[i] = float(parameters[3])
					except ValueError:
						raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
				elif len(parameters) == 7:
					try:
						X[i] = int(parameters[0])
						A[i] = float(parameters[1])
						B[i] = float(parameters[2])
						C[i] = float(parameters[3])
						A_k[i] = float(parameters[4])
						exponent[i] = float(parameters[5])
						edge[i] = float(parameters[6])
					except ValueError:
						raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
				else:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
		
		elif model == "SELLMEIER":
			nb_mixtures = len(properties)
			# It takes 3 points to define a spline
			if nb_mixtures < 2:
				raise material_parsing_error(name, "Invalid property format (there must be at least 2 mixtures)")
			X = [0]*nb_mixtures
			B1 = [0.0]*nb_mixtures
			C1 = [0.0]*nb_mixtures
			B2 = [0.0]*nb_mixtures
			C2 = [0.0]*nb_mixtures
			B3 = [0.0]*nb_mixtures
			C3 = [0.0]*nb_mixtures
			A_k = [0.0]*nb_mixtures
			exponent = [1.0]*nb_mixtures
			edge = [4000.0]*nb_mixtures
			for i in range(nb_mixtures):
				parameters = properties[i].split()
				if len(parameters) == 7:
					try:
						X[i] = int(parameters[0])
						B1[i] = float(parameters[1])
						C1[i] = float(parameters[2])
						B2[i] = float(parameters[3])
						C2[i] = float(parameters[4])
						B3[i] = float(parameters[5])
						C3[i] = float(parameters[6])
					except ValueError:
						raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
				elif len(parameters) == 10:
					try:
						X[i] = int(parameters[0])
						B1[i] = float(parameters[1])
						C1[i] = float(parameters[2])
						B2[i] = float(parameters[3])
						C2[i] = float(parameters[4])
						B3[i] = float(parameters[5])
						C3[i] = float(parameters[6])
						A_k[i] = float(parameters[7])
						exponent[i] = float(parameters[8])
						edge[i] = float(parameters[9])
					except ValueError:
						raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
				else:
					raise material_parsing_error(name, "Invalid property format (%s)" % properties[i])
		
		if X[0] != 0:
			raise material_parsing_error(name, "Invalid property format (first mixture number must be 0)")
	
	# Create the appropriate class.
	if kind == "REGULAR":
		if model == "CONSTANT":
			new_material = material_constant()
		elif model == "TABLE":
			new_material = material_table()
		elif model == "CAUCHY":
			new_material = material_Cauchy()
		elif model == "SELLMEIER":
			new_material = material_Sellmeier()
	else:
		if model == "CONSTANT":
			new_material = material_mixture_constant()
		elif model == "TABLE":
			new_material = material_mixture_table()
		elif model == "CAUCHY":
			new_material = material_mixture_Cauchy()
		elif model == "SELLMEIER":
			new_material = material_mixture_Sellmeier()
	
	new_material.set_name(name)
	if description:
		new_material.set_description(description)
	if kind == "REGULAR":
		if model == "CONSTANT":
			new_material.set_properties(N)
		elif model == "TABLE":
			new_material.set_properties(wvls, N)
		elif model == "CAUCHY":
			new_material.set_properties(A, B, C, A_k, exponent, edge)
		elif model == "SELLMEIER":
			new_material.set_properties(B1, C1, B2, C2, B3, C3, A_k, exponent, edge)
	else:
		if model == "CONSTANT":
			new_material.set_properties(X, N)
		elif model == "TABLE":
			new_material.set_properties(X, wvls, N)
		elif model == "CAUCHY":
			new_material.set_properties(X, A, B, C, A_k, exponent, edge)
		elif model == "SELLMEIER":
			new_material.set_properties(X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge)
	if rates:
		new_material.set_deposition_rate(rates)
	if constants:
		new_material.set_deposition_constants(constants, constant_values)
	if variables:
		new_material.set_deposition_variables(variables, variable_values)
	
	return new_material



########################################################################
#                                                                      #
# read_material                                                        #
#                                                                      #
########################################################################
def read_material(name, directory = None):
	"""Read a material file
	
	Read a material file and parse it using the function parse_material.
	This function takes 1 or 2 arguments:
	  name       the name of the material;
	  directory  (optional) the directory where to read the material, by
	             default it is the default material directory;
	and returns the material."""
	
	if not directory:
		directory = default_material_directory
	
	filename = os.path.join(directory, (name + ".mat"))
	
	infile = open(filename)
	lines = infile.readlines()
	infile.close()
	
	new_material = parse_material(name, lines)
	
	return new_material



######################################################################
#                                                                    #
# write_material                                                     #
#                                                                    #
######################################################################
def write_material(material, outfile = None, prefix = "", directory = None):
	"""Write a material to a file
	
	This function takes 1 to 4 arguments:
		material   the material to write;
		outfile    (optional) the file in which to write and;
		prefix     (optional) a prefix to add to every line in the output
		           file;
	  directory  (optional) the directory where to write the material, by
	             default it is the default material directory.
	It returns no argument.
	
	When no file is given to the function, the name of the material is
	used to determine the name of the file. If the creation of the file
	fails, a OSError or a IOError will be raised."""
	
	name = material.get_name()
	kind = material.get_kind()
	model = material.get_model()
	description = material.get_description()
	properties = material.get_properties()
	rate = material.get_deposition_rate()
	constants, constant_values = material.get_deposition_constants()
	if kind == MATERIAL_MIXTURE:
		variables, variable_values = material.get_deposition_variables()
	
	if not directory:
		directory = default_material_directory
	
	if not outfile:
		filename = os.path.join(directory, (name + ".mat"))
		outfile = open(filename, "w")
	
	if description:
		outfile.write(prefix + "Description: %s\n" % description)
	
	if kind == MATERIAL_REGULAR:
		outfile.write(prefix + "Kind: regular\n")
		
		if model == CONSTANT:
			outfile.write(prefix + "Model: constant\n")
			N, = properties
			if N.imag == 0.0:
				outfile.write(prefix + "Properties: %#g\n" % N.real)
			elif N.imag < 0.0:
				outfile.write(prefix + "Properties: %#g-%#gj\n" % (N.real, -N.imag))
			else:
				outfile.write(prefix + "Properties: %#g+%#gj\n" % (N.real, N.imag))
		
		elif model == TABLE:
			outfile.write(prefix + "Model: table\n")
			outfile.write(prefix + "Properties:\n")
			wvls, N = properties
			for i_wvl in range(len(wvls)):
				if N[i_wvl].imag == 0.0:
					outfile.write(prefix + "\t%f\t%#g\n" % (wvls[i_wvl], N[i_wvl].real))
				elif N[i_wvl].imag < 0.0:
					outfile.write(prefix + "\t%f\t%#g-%#gj\n" % (wvls[i_wvl], N[i_wvl].real, -N[i_wvl].imag))
				else:
					outfile.write(prefix + "\t%f\t%#g+%#gj\n" % (wvls[i_wvl], N[i_wvl].real, N[i_wvl].imag))
			outfile.write(prefix + "End\n")
		
		elif model == CAUCHY:
			A, B, C, A_k, exponent, edge = properties
			outfile.write(prefix + "Model: Cauchy\n")
			if A_k:
				outfile.write(prefix + "Properties: %#g %#g %#g %#g %#g %#g\n" % (A, B, C, A_k, exponent, edge))
			else:
				outfile.write(prefix + "Properties: %#g %#g %#g\n" % (A, B, C))
		
		elif model == SELLMEIER:
			B1, C1, B2, C2, B3, C3, A_k, exponent, edge = properties
			outfile.write(prefix + "Model: Sellmeier\n")
			if A_k:
				outfile.write(prefix + "Properties: %#g %#g %#g %#g %#g %#g %#g %#g %#g\n" % (B1, C1, B2, C2, B3, C3, A_k, exponent, edge))
			else:
				outfile.write(prefix + "Properties: %#g %#g %#g %#g %#g %#g\n" % (B1, C1, B2, C2, B3, C3))
	
	else:
		outfile.write(prefix + "Kind: mixture\n")
		if model == CONSTANT:
			outfile.write(prefix + "Model: constant\n")
			X, N = properties
			outfile.write(prefix + "Properties:\n")
			for i_mix in range(len(X)):
				if N[i_mix].imag == 0.0:
					outfile.write(prefix + "\t%i\t%#g\n" % (X[i_mix], N[i_mix].real))
				elif N[i_mix].imag < 0.0:
					outfile.write(prefix + "\t%i\t%#g-%#gj\n" % (X[i_mix], N[i_mix].real, -N[i_mix].imag))
				else:
					outfile.write(prefix + "\t%i\t%#g+%#gj\n" % (X[i_mix], N[i_mix].real, N[i_mix].imag))
			outfile.write(prefix + "End\n")
		
		elif model == TABLE:
			outfile.write(prefix + "Model: table\n")
			X, wvls, N = properties
			outfile.write(prefix + "Properties:\n")
			outfile.write(prefix)
			for i_mix in range(len(X)):
				outfile.write("\t\t\t%i" % X[i_mix])
			outfile.write("\n")
			for i_wvl in range(len(wvls)):
				outfile.write(prefix + "\t%f" % wvls[i_wvl])
				for i_mix in range(len(X)):
					if N[i_mix][i_wvl].imag == 0.0:
						outfile.write("\t%#g" % N[i_mix][i_wvl].real)
					elif N[i_mix][i_wvl].imag < 0.0:
						outfile.write("\t%#g-%#gj" % (N[i_mix][i_wvl].real, -N[i_mix][i_wvl].imag))
					else:
						outfile.write("\t%#g+%#gj" % (N[i_mix][i_wvl].real, N[i_mix][i_wvl].imag))
				outfile.write("\n")
			outfile.write(prefix + "End\n")
		
		elif model == CAUCHY:
			outfile.write(prefix + "Model: Cauchy\n")
			X, A, B, C, A_k, exponent, edge = properties
			outfile.write(prefix + "Properties:\n")
			for i_mix in range(len(X)):
				if A_k[i_mix]:
					outfile.write(prefix + "\t%i\t%#g %#g %#g %#g %#g %#g\n" % (X[i_mix], A[i_mix], B[i_mix], C[i_mix], A_k[i_mix], exponent[i_mix], edge[i_mix]))
				else:
					outfile.write(prefix + "\t%i\t%#g %#g %#g\n" % (X[i_mix], A[i_mix], B[i_mix], C[i_mix]))
			outfile.write(prefix + "End\n")
		
		elif model == SELLMEIER:
			outfile.write(prefix + "Model: Sellmeier\n")
			X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge = properties
			outfile.write(prefix + "Properties:\n")
			for i_mix in range(len(X)):
				if A_k[i_mix]:
					outfile.write(prefix + "\t%i\t%#g %#g %#g %#g %#g %#g %#g %#g %#g\n" % (X[i_mix], B1[i_mix], C1[i_mix], B2[i_mix], C2[i_mix], B3[i_mix], C3[i_mix], A_k[i_mix], exponent[i_mix], edge[i_mix]))
				else:
					outfile.write(prefix + "\t%i\t%#g %#g %#g %#g %#g %#g\n" % (X[i_mix], B1[i_mix], C1[i_mix], B2[i_mix], C2[i_mix], B3[i_mix], C3[i_mix]))
			outfile.write(prefix + "End\n")
	
	if rate:
		if kind == MATERIAL_REGULAR:
			outfile.write(prefix + "Rate: %#g\n" % rate)
		
		else:
			outfile.write(prefix + "Rates:")
			for i_mix in range(len(X)):
				outfile.write(" %#g" % rate[i_mix])
			outfile.write("\n")
		
	if constants:
		outfile.write(prefix + "Constants:\n")
		for i in range(len(constants)):
			outfile.write(prefix + "\t%s: %#g\n" % (constants[i], constant_values[i]))
		outfile.write(prefix + "End\n")
	
	if kind == MATERIAL_MIXTURE:
		if variables:
			outfile.write(prefix + "Variables:\n")
			for i_var in range(len(variables)):
				outfile.write(prefix + "\t%s:" % variables[i_var])
				for i_mix in range(len(X)):
					outfile.write(" %#g" % variable_values[i_var][i_mix])
				outfile.write("\n")
			outfile.write(prefix + "End\n")



######################################################################
#                                                                    #
# delete_material                                                    #
#                                                                    #
######################################################################
def delete_material(material_name, directory = None):
	"""Delete a material file
	
	This function takes 1 or 2 arguments:
		material_name   the name of the material to delete;
	  directory       (optional) the directory from which to delete the
	                  material, by default it is the default material
	                  directory;
	It returns no argument.
	
	A OSError is raised if the file cannot be deleted."""
	
	if not directory:
		directory = default_material_directory
	
	filename = os.path.join(directory, (material_name + ".mat"))
	
	os.remove(filename)



########################################################################
#                                                                      #
# import_material                                                      #
#                                                                      #
########################################################################
def import_material(filename, name, description, nb_header_lines, wavelength_units, permittivity):
	"""Import a table material from a text file
	
	This function takes a 6 arguments:
	  filename           the name of the text file;
	  name               the name of the material;
	  description        the description of the material;
	  nb_header_lines    the number of header lines in the text file;
	  wavelength_units   the units used for the wavelength in the file;
	  permittivity       a boolean indicating if relative permittivity
	                     is used in the file (vs refractive index);
	and returns the material.
	
	This function handles the refractive index or permittivity being
	written as a complex number or in two columns representing the real
	and imaginary parts. It also handles all sign convention by making
	sure the real part of the refractive index is positive and the
	imaginary part is negative."""
	
	try:
		file = open(filename, "r")
	except IOError:
		raise material_error(name, "Impossible to open the file")
	
	# Read the file
	lines = file.readlines()
	
	# Interpret the lines.
	wvls = []
	values = []
	for i in range(nb_header_lines, len(lines)):
		line = lines[i].strip()
		
		# Skip empty lines.
		if not line:
			continue
		
		# Replace tabs by spaces and commas by spaces to handle csv files.
		line = line.replace("\t", " ")
		line = line.replace(",", " ")
		
		# Seperate wavelength and optical property.
		elements = line.split(None, 1)
		
		if len(elements) != 2:
			raise material_parsing_error("Line %i of the file is formatted incorectly" % (i+1))
		
		try:
			wvls.append(float(elements[0]))
		except ValueError:
			raise material_parsing_error("Line %i of the file is formatted incorectly" % (i+1))
		
		s = elements[1].strip()
		
		# Remove parenthesis around the number if any.
		s = re.sub(r"\((.*)\)", r"\1", s)
		
		# Replace multiple spaces by a single space.
		s = re.sub(r" +", " ", s)
		
		# Replace i by j.
		s = re.sub(r"[iI]", "j", s)
		
		# If the real and imaginary part are seperated by a space, make
		# sure the imaginary part has a j.
		s = re.sub(r" ([+-]?[0-9]*\.*[0-9]*[eE]?[+-]?[0-9]*)$", r" \1j", s)
		
		# Move j to the end of the number.
		s = re.sub(r"[jJ]([0-9]\.*[0-9]*[eE]?[+-]?[0-9]*)", r"\1j", s)
		
		# Remove spaces around the sign seperating the real and imaginary
		# parts.
		s = re.sub(r" *([\+\-]) *", r"\1", s)
		
		# If the real and imaginary are seperated by a space (this should
		# be the only remaining space), replace it by a plus.
		s = s.replace(" ", "+")
		
		try:
			values.append(complex(s))
		except ValueError:
			raise material_parsing_error("Line %i of the file is formatted incorectly" % (i+1))
	
	for i in range(len(values)):
		# Convert wavelength to nanometers.
		wvls[i] = units.meters_to_nanometers(units.CONVERT_FROM_UNITS_TO_METERS[wavelength_units](wvls[i]))
		
		# Convert permittivity to refractive index, if necessary.
		if permittivity:
			values[i] = cmath.sqrt(values[i])
		
		# Handle all sign conventions by converting the index to what makes
		# sense for OpenFilters.
		values[i] = complex(abs(values[i].real), -abs(values[i].imag))
	
	# Make sure there are enough points for the spline.
	if len(wvls) < 3:
		raise material_parsing_error("The refractive index must be defined at least at 3 wavelengths")
	
	# Sort in order of wavelength
	wvls, values = zip(*sorted(zip(wvls, values)))
	
	# Make sure there is no repeated wavelength values.
	for i in range(len(wvls)-1):
		if wvls[i+1] == wvls[i]:
			raise material_parsing_error("The refractive index is defined multiple times at the same wavelength")
	
	new_material = material_table()
	new_material.set_name(name)
	new_material.set_description(description)
	new_material.set_properties(wvls, values)
	
	return new_material
