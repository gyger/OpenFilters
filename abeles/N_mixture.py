# n_mixture.py
# 
# A class to manage the index of a mixture of material.
#
# The index of refraction of mixtures of material is adjustable.
# It cannot be set once and for all, but rather must be associated
# with a dispersion formula. Furthermore, when the index of
# refraction of a layer is refined, it is necessary to calculate the
# wavelength dependant derivative of the index of refraction with
# regard to a variation of the index of refraction at the reference
# wavelength. Finally, material mixtures can be used in graded-index
# layers, in which the index profile is discretized according to
# predefined levels.
#
# The instance representing the index of refraction of material
# mixtures therefore consists of a mixture dispersion instance,
# one index instance for the index of refraction, one for its
# derivative, and, when necessary, an array of index of refraction
# instances for the predefined levels of the graded-index layer.
# 
# Copyright (c) 2005,2007,2008,2012,2014 Stephane Larouche.
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



from dispersion_mixtures import *
from N import *



########################################################################
#                                                                      #
# N_mixture                                                            #
#                                                                      #
########################################################################
class N_mixture(object):
	"""A class to manage the index of a mixture of material"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, dispersion, wvls):
		"""Initialize an instance of N_mixture class to store the index of
		refraction of a mixture with constant dispersion
		
		This method takes 2 arguments:
		  material          an instance of a mixture dispersion class;
		  wvls              the wavelengths at which to calculate the
		                    index of refraction."""
		
		self.wvls = wvls
		self.dispersion = dispersion
		if isinstance(self.dispersion, constant_mixture):
			self.f_N = self.dispersion.set_N_constant_mixture
			self.f_N_x = self.dispersion.set_N_constant_mixture_by_x
			self.f_dN = self.dispersion.set_dN_constant_mixture
		elif isinstance(self.dispersion, table_mixture):
			self.f_N = self.dispersion.set_N_table_mixture
			self.f_N_x = self.dispersion.set_N_table_mixture_by_x
			self.f_dN = self.dispersion.set_dN_table_mixture
		elif isinstance(self.dispersion, Cauchy_mixture):
			self.f_N = self.dispersion.set_N_Cauchy_mixture
			self.f_N_x = self.dispersion.set_N_Cauchy_mixture_by_x
			self.f_dN = self.dispersion.set_dN_Cauchy_mixture
		elif isinstance(self.dispersion, Sellmeier_mixture):
			self.f_N = self.dispersion.set_N_Sellmeier_mixture
			self.f_N_x = self.dispersion.set_N_Sellmeier_mixture_by_x
			self.f_dN = self.dispersion.set_dN_Sellmeier_mixture
		self.N = N(self.wvls)
		self.dN = N(self.wvls)
		self.length = 0
		self.N_graded = None
	
	
	######################################################################
	#                                                                    #
	# prepare_N_mixture_graded                                           #
	#                                                                    #
	######################################################################
	def prepare_N_mixture_graded(self, length):
		"""Prepare a mixture index instance to represent graded-index
		layers
		
		This method takes 1 argument:
		  length            the number of index levels to prepare."""
		
		self.length = length
		self.N_graded = [N(self.wvls) for i in range(self.length)]
	
	
	######################################################################
	#                                                                    #
	# N_mixture_graded_is_prepared                                       #
	#                                                                    #
	######################################################################
	def N_mixture_graded_is_prepared(self):
		"""Determine if a mixture index instance was prepared to use in
		graded-index layers
		
		This method returns a boolean indicating if the instance is ready
		to be used to represent graded-index layers."""
		
		if self.length > 0: return True
		else: return False
	
	
	######################################################################
	#                                                                    #
	# set_N_mixture                                                      #
	#                                                                    #
	######################################################################
	def set_N_mixture(self, n_wvl, wvl):
		"""Set the index of refraction of a mixture
		
		This method takes 2 arguments:
		  n_wvl             the index of refraction at a given
		                    wavelength;
		  wavelength        the wavelength;
		and sets the index of refraction using the dispersion formula
		associated with the instance."""
		
		self.f_N(self.N, n_wvl, wvl)
	
	
	######################################################################
	#                                                                    #
	# set_N_mixture_by_x                                                 #
	#                                                                    #
	######################################################################
	def set_N_mixture_by_x(self, x):
		"""Set the index of refraction of a mixture
		
		This method takes 1 arguments:
		  x                 the number of the mixture;
		and sets the index of refraction using the dispersion formula
		associated with the instance."""
		
		self.f_N_x(self.N, x)
	
	
	######################################################################
	#                                                                    #
	# set_dN_mixture                                                     #
	#                                                                    #
	######################################################################
	def set_dN_mixture(self, n_wvl, wvl):
		"""Set the derivative of the index of refraction of a mixture
		
		This method takes 2 arguments:
		  n_wvl             the index of refraction at a given
		                    wavelength;
		  wavelength        the wavelength;
		and sets the derivative of the index of refraction using the
		dispersion formula associated with the instance."""
		
		self.f_dN(self.dN, n_wvl, wvl)
	
	
	######################################################################
	#                                                                    #
	# set_N_mixture_graded                                               #
	#                                                                    #
	######################################################################
	def set_N_mixture_graded(self, position, n_wvl, wvl):
		"""Set the index of refraction of one mixture when the material is
		used in graded-index layers
		
		This method takes 3 arguments:
		  position          the position of the index in the graded-index
		                    instance;
		  n_wvl             the index of refraction at a given
		                    wavelength;
		  wavelength        the wavelength;
		and sets the derivative of the index of refraction using the
		dispersion formula associated with the instance."""
		
		self.f_N(self.N_graded[position], n_wvl, wvl)
	
	
	######################################################################
	#                                                                    #
	# get_N_mixture                                                      #
	#                                                                    #
	######################################################################
	def get_N_mixture(self):
		"""Get the index of refraction of a mixture
		
		This method returns the index instance representing the index of
		refraction of the mixture."""
		
		return self.N
	
	
	######################################################################
	#                                                                    #
	# get_dN_mixture                                                     #
	#                                                                    #
	######################################################################
	def get_dN_mixture(self):
		"""Get the index of refraction of a mixture
		
		This method returns the index instance representing the derivative
		of the index of refraction of the mixture."""
		
		return self.dN
	
	
	######################################################################
	#                                                                    #
	# get_N_mixture_graded                                               #
	#                                                                    #
	######################################################################
	def get_N_mixture_graded(self, position):
		"""Get the index of refraction of one level when a mixture is used
		in graded-index layers
		
		This method takes 1 argument:
		  position          the position of the index in the graded-index
		                    instance;
		and returns the index instance representing the index of
		refraction of one level of the mixture."""
	
		return self.N_graded[position]
