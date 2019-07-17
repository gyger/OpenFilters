# dispersion_mixtures.cpp
# 
# Classes to manage the optical properties of material mixtures.
# 
# Copyright (c) 2005-2008,2012,2014 Stephane Larouche.
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
import warnings

import PCHIP



########################################################################
#                                                                      #
# mixture                                                              #
#                                                                      #
########################################################################
class mixture(object):
	"""A base class to manage the optical properties of mixtures"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the dispersion mixture class
		
		This method takes 1 argument:
		  length            the number of dispersion curves defining the
		                    mixture."""
		
		self.length = length
		self.X = [0.0]*self.length
		self._wvls = None
		self._nb_wvls = 0
		self._n = None
		self._k = None
		self._n_PCHIPs = None
		self._k_PCHIPs = None
		self._center_wvl = 0.0
		self._n_center_wvl = [0.0]*self.length
		self._n_center_wvl_PCHIP = PCHIP.PCHIP(self.X, self._n_center_wvl, True, False)
		self._other_wvl = 0.0
		self._n_other_wvl = [0.0]*self.length
		self._n_other_wvl_PCHIP = PCHIP.PCHIP(self.X, self._n_other_wvl, True, False)
	
	
	######################################################################
	#                                                                    #
	# swap_center_and_other_wvls                                         #
	#                                                                    #
	######################################################################
	def swap_center_and_other_wvls(self):
		"""Swap the center and the other wavelengths
		
		This method takes no argument."""
	
		_wvl = self._center_wvl
		_n = self._n_center_wvl
		_n_PCHIP = self._n_center_wvl_PCHIP
		self._center_wvl = self._other_wvl
		self._n_center_wvl = self._n_other_wvl
		self._n_center_wvl_PCHIP = self._n_other_wvl_PCHIP
		self._other_wvl = _wvl
		self._n_other_wvl = _n
		self._n_other_wvl_PCHIP = _n_PCHIP
	
	
	######################################################################
	#                                                                    #
	# prepare_mixture_PCHIPs                                             #
	#                                                                    #
	######################################################################
	def prepare_mixture_PCHIPs(self, wvls):
		"""Prepare the PCHIPs to calculate the refractive index at all wavelengths                                                       */
		
		This method takes 1 argument:
		  wvls              the list of wavelengths at which to prepare
		                    the PCHIPs."""
		
		self._wvls = wvls
		self._nb_wvls = wvls.length
		
		# Create n, k and PCHIP lists.
		self._n = [None]*self._nb_wvls
		self._k = [None]*self._nb_wvls
		self._n_PCHIPs = [None]*self._nb_wvls
		self._k_PCHIPs = [None]*self._nb_wvls
		for i_wvl in range(self._nb_wvls):
			self._n[i_wvl] = [0.0]*self.length
			self._k[i_wvl] = [0.0]*self.length
			self._n_PCHIPs[i_wvl] = PCHIP.PCHIP(self.X, self._n[i_wvl], True, False)
			self._k_PCHIPs[i_wvl] = PCHIP.PCHIP(self.X, self._k[i_wvl], True, False)
	
	
	######################################################################
	#                                                                    #
	# get_mixture_monotonicity                                           #
	#                                                                    #
	######################################################################
	def get_mixture_monotonicity(self, wvl):
		"""Determine if the index of refraction of a mixture is monotone at a given wavelength                                                */
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns a boolean that is true if the index of refraction is
		monotonic, and false otherwise."""
		
		# If the center wavelength is not defined, it is probably the first
	 	# time this material is used and the center wavelength will be
	 	# reused. Otherwise, the wavelength is probably about to be changed
	 	# and the other wavelength will be reused.
		if self._center_wvl == 0.0:
			self.set_mixture_center_wvl(wvl)
			n_wvl = self._n_center_wvl
		else:
			if wvl != self._other_wvl: self.set_mixture_other_wvl(wvl)
			n_wvl = self._n_other_wvl
		
		# Check monotonicity.
		for i in range(1, self.length):
			if n_wvl[i] <= n_wvl[i-1]:
				return False
		
		return True
	
	
	######################################################################
	#                                                                    #
	# get_mixture_index                                                  #
	#                                                                    #
	######################################################################
	def get_mixture_index(self, x, wvl):
		"""Get the index of refraction at a single wavelength from a dispersion mixture                                                */
		
		This method takes 2 arguments:
		  x                 the number of the mixture;
		  wvl               the wavelength;
		and returns the real part of the index of refraction."""
		
		# If the wavelength is different from the last time a calculation
		# was done, recalculate the index and reset the PCHIP.
		if wvl != self._center_wvl: self.set_mixture_center_wvl(wvl)
		
		# Get the index by using the PCHIP. */
		n = self._n_center_wvl_PCHIP.evaluate([x])[0]
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_mixture_index_range                                            #
	#                                                                    #
	######################################################################
	def get_mixture_index_range(self, wvl):
		"""Get the range of index of refraction at a single wavelength from a dispersion mixture                                        */
		
		This method takes 3 arguments:
		  wvl               the wavelength;
		  n_min, n_max      1 element lists to return the values of
		                    the minimal and maximal indices."""
		
		# If the wavelength is different from the last time a calculation
	 	# was done, recalculate the index and reset the PCHIP.
		if wvl != self._center_wvl: self.set_mixture_center_wvl(wvl)
	
		n_min = self._n_center_wvl[0]
		n_max = self._n_center_wvl[self.length-1]
		
		return n_min, n_max
	
	
	######################################################################
	#                                                                    #
	# change_mixture_index_wvl                                           #
	#                                                                    #
	######################################################################
	def change_mixture_index_wvl(self, old_n, old_wvl, new_wvl):
		"""Get the index of refraction at a given wavelength from that at another wavelength from the dispersion curves of a mixture
		
		This method takes 3 arguments:
		  old_n             the real part of index of refraction at the
		                    original wavelength;
		  old_wvl           the original wavelength;
		  new_wvl           the new wavelength;
		and returns the real part of the index of refraction at the new
		wavelength."""
		
		# If the wavelength is different from the last time a calculation
		# was done, recalculate the index and reset the PCHIP.
		if old_wvl != self._center_wvl: self.set_mixture_center_wvl(old_wvl)
		
		# If the other wavelength is different from the last time a
		# calculation was done, recalculate the index and reset the PCHIP.
		if new_wvl != self._other_wvl: self.set_mixture_other_wvl(new_wvl)
		
		# Locate the interval where the mixture is located.
		i_mix = PCHIP.locate(self._n_center_wvl, old_n, False)
		
		# Get the mixture by using the inverse of the PCHIP.
		x = self._n_center_wvl_PCHIP.evaluate_inverse([old_n], indices = [i_mix])
		
		# Evaluate the PCHIP at the new wavelength.
		new_n = self._n_other_wvl_PCHIP.evaluate(x, indices = [i_mix])[0]
		
		return new_n
	
	
	######################################################################
	#                                                                    #
	# set_N_mixture                                                      #
	#                                                                    #
	######################################################################
	def set_N_mixture(self, N, n_wvl, wvl):
		"""Set an index structure according the the dispersion of a mixture
		
		This method takes 3 arguments:
		  N                 the structure in which to store the index;
		  n_wvl             the real part of index of refraction at a
		                    given wavelength;
		  wvl               the wavelength;
		and sets the index structure according to the dispersion of the
		mixture."""
		
		# If the wavelength is different from the last time a calculation
		# was done, recalculate the index and reset the PCHIP.
		if wvl != self._center_wvl: self.set_mixture_center_wvl(wvl)
		
		# Prepare and set PCHIPs at every wavelength, if necessary.
		if N.wvls != self._wvls:
			self.prepare_and_set_mixture_PCHIPs(N.wvls)
		
		# Locate the interval where the mixture is located.
		i_mix = PCHIP.locate(self._n_center_wvl, n_wvl, False)
		
		# Get the mixture by using the inverse of the PCHIP.
		x = self._n_center_wvl_PCHIP.evaluate_inverse([n_wvl], indices = [i_mix])
		
		# Evaluate n and k using the PCHIPs. Make sure k does not get bellow
		# zero because of the PCHIP.
		for i_wvl in range(N.wvls.length):
			n = self._n_PCHIPs[i_wvl].evaluate(x, indices = [i_mix])[0]
			k = self._k_PCHIPs[i_wvl].evaluate(x, indices = [i_mix])[0]
			N.N[i_wvl] = complex(n, min(k, 0.0))
	
	
	######################################################################
	#                                                                    #
	# set_N_mixture_by_x                                                 #
	#                                                                    #
	######################################################################
	def set_N_mixture_by_x(self, N, x):
		"""Set an index structure according the the dispersion of a mixture
		
		This method takes 2 arguments:
		  N                 the structure in which to store the index;
		  x                 the number of the mixture;
		and sets the index structure according to the dispersion of the
		mixture."""
		
		# Prepare and set PCHIPs at every wavelength, if necessary.
		if N.wvls != self._wvls:
			self.prepare_and_set_mixture_PCHIPs(N.wvls)
		
		# Locate the interval where the mixture is located.
		i_mix = PCHIP.locate(self.X, x, False)
		
		# Evaluate n and k using the PCHIPs. Make sure k does not get bellow
		# zero because of the PCHIP.
		for i_wvl in range(N.wvls.length):
			n = self._n_PCHIPs[i_wvl].evaluate([x], indices = [i_mix])[0]
			k = self._k_PCHIPs[i_wvl].evaluate([x], indices = [i_mix])[0]
			N.N[i_wvl] = complex(n, min(k, 0.0))
	
	
	######################################################################
	#                                                                    #
	# set_dN_mixture                                                     #
	#                                                                    #
	######################################################################
	def set_dN_mixture(self, dN, n_wvl, wvl):
		"""Set the derivative of the index of refraction in a index structure according the the dispersion of a mixture
		
		This method takes 3 arguments:
		  dN                the structure in which to store the
		                    derivative;
		  n_wvl             the real part of index of refraction at a
		                    given wavelength;
		  wvl               the wavelength;
		and stores the derivative of the index of refraction in the index
		structure according to the dispersion of the mixture."""
		
		# If the wavelength is different from the last time a calculation
		# was done, recalculate the index and reset the PCHIP.
		if wvl != self._center_wvl: self.set_mixture_center_wvl(wvl)
		
		# Prepare and set PCHIPs at every wavelength, if necessary.
		if dN.wvls != self._wvls:
			self.prepare_and_set_mixture_PCHIPs(dN.wvls)
		
		# Locate the interval where the mixture is located.
		i_mix = PCHIP.locate(self._n_center_wvl, n_wvl, False)
		
		# Get the mixture by using the inverse of the PCHIP.
		x = self._n_center_wvl_PCHIP.evaluate_inverse([n_wvl], indices = [i_mix])
		
		# The derivative of the real part at the definition wavelength.
		dn_wvl = self._n_center_wvl_PCHIP.evaluate_derivative(x, indices = [i_mix])[0]
		
		# Evaluate dn and dk using the PCHIPs and normalize.
		for i_wvl in range(dN.wvls.length):
			dn = self._n_PCHIPs[i_wvl].evaluate_derivative(x, indices = [i_mix])[0]
			dk = self._k_PCHIPs[i_wvl].evaluate_derivative(x, indices = [i_mix])[0]
			
			# Evaluate k using the PCHIP. If k is larger than 0, set the
			# derivative to 0.
			k = self._k_PCHIPs[i_wvl].evaluate(x, indices = [i_mix])[0];
			if k > 0.0:
				dk = 0.0;
			
			dN.N[i_wvl] = complex(dn/dn_wvl, dk/dn_wvl)



########################################################################
#                                                                      #
# constant_mixture                                                     #
#                                                                      #
########################################################################
class constant_mixture(object):
	"""A class to manage the optical properties of constant mixtures"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the constant dispersion mixture class
		
		This method takes 1 argument:
		  length            the number of dispersion curves defining the
		                    mixture."""
		
		self.length = length
		self.X = [0.0]*self.length
		self.n = [0.0]*self.length
		self.k = [0.0]*self.length
		
		self._n_PCHIP = PCHIP.PCHIP(self.X, self.n, True, False)
		self._k_PCHIP = PCHIP.PCHIP(self.X, self.k, True, False)
	
	
	######################################################################
	#                                                                    #
	# set_constant_mixture                                               #
	#                                                                    #
	######################################################################
	def set_constant_mixture(self, i, x, N):
		"""Set the value of the index of refraction for constant dispersion
		
		This method takes 3 arguments:
		  i                 the position of the dispersion curve in the
		                    instance;
		  x                 the number associated with the mixture (used
		                    to determine what mixtures are fabricable);
		  N                 the index of refraction."""
		
		# Make sure that n is complex.
		N = complex(N)
		
		self.X[i] = x
		self.n[i] = N.real
		self.k[i] = N.imag
	
	
	######################################################################
	#                                                                    #
	# prepare_constant_mixture                                           #
	#                                                                    #
	######################################################################
	def prepare_constant_mixture(self):
		"""This method is deprecated"""
		
		warnings.warn(DeprecationWarning("it is no longer necessary to call prepare_constant_mixture"))
	
	
	######################################################################
	#                                                                    #
	# get_constant_mixture_monotonicity                                  #
	#                                                                    #
	######################################################################
	def get_constant_mixture_monotonicity(self, wvl):
		"""Determine if the index of refraction of a mixture is monotone at
		a given wavelength
		
		This method takes 1 argument:
			wvl               the wavelength;
		and returns a boolean that is true if the index of refraction is
		monotonic, and false otherwise."""
		
		for i_mix in range(1, self.length):
			if self.n[i_mix] <= self.n[i_mix-1]:
				return False
		
		return True
	
	
	######################################################################
	#                                                                    #
	# get_constant_mixture_index                                         #
	#                                                                    #
	######################################################################
	def get_constant_mixture_index(self, x, wvl):
		"""Get the index of refraction at a single wavelength from a
		constant dispersion mixture
		
		This method takes 2 arguments:
		  x                 the number of the mixture;
		  wvl               the wavelength;
		and returns the real part of the index of refraction."""
		
		# Get the index by using the PCHIP.
		n = self._n_PCHIP.evaluate([x])[0]
		
		return n
	
	
	######################################################################
	#                                                                    #
	# get_constant_mixture_index_range                                   #
	#                                                                    #
	######################################################################
	def get_constant_mixture_index_range(self, wvl):
		"""Get the range of index of refraction at a single wavelength from
		a constant dispersion mixture
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns
		  n_min, n_max      the minimal and maximal indices."""
		
		n_min = self.n[0]
		n_max = self.n[-1]
		
		return n_min, n_max
	
	
	######################################################################
	#                                                                    #
	# change_constant_mixture_index_wvl                                  #
	#                                                                    #
	######################################################################
	def change_constant_mixture_index_wvl(self, old_n, old_wvl, new_wvl):
		"""Get the index of refraction at a given wavelength from that at
		another wavelength from the dispersion curves of a constant
		mixture
		
		This method takes 3 arguments:
		  old_n             the real part of index of refraction at the
		                    original wavelength;
		  old_wvl           the original wavelength;
		  new_wvl           the new wavelength;
		and returns the real part of the index of refraction at the new
		wavelength."""
		
		return old_n
	
	
	######################################################################
	#                                                                    #
	# set_N_constant_mixture                                             #
	#                                                                    #
	######################################################################
	def set_N_constant_mixture(self, N, n_wvl, wvl):
		"""Set an index instance instance the the dispersion of a constant
		mixture
		
		This method takes 3 arguments:
		  N                 the instance in which to store the index;
		  n_wvl             the real part of index of refraction at a
		                    given wavelength;
		  wvl               the wavelength;
		and sets the index instance according to the dispersion of the
		mixture."""
		
		# Locate the interval where the mixture is located.
		i = PCHIP.locate(self.n, n_wvl, False)
		
		# Get the mixture by using the inverse of the PCHIP.
		x = self._n_PCHIP.evaluate_inverse([n_wvl], [i])
		
		# Evaluate k using the PCHIP.
		k = self._k_PCHIP.evaluate(x, [i])[0]
		
		# Set the index.
		N_ = complex(n_wvl, min(k, 0.0))
		for i in range(N.wvls.length):
			N.N[i] = N_
	
	
	######################################################################
	#                                                                    #
	# set_N_constant_mixture_by_x                                        #
	#                                                                    #
	######################################################################
	def set_N_constant_mixture_by_x(self, N, x):
		"""Set an index instance instance the the dispersion of a constant
		mixture
		
		This method takes 2 arguments:
		  N                 the instance in which to store the index;
		  x                 the number of the mixture;
		and sets the index instance according to the dispersion of the
		mixture."""
		
		# Locate the interval where the mixture is located.
		i = PCHIP.locate(self.X, x, False)
		
		# Evaluate n and k using the PCHIPs.
		n = self._n_PCHIP.evaluate([x], [i])[0]
		k = self._k_PCHIP.evaluate([x], [i])[0]
		
		# Set the index.
		N_ = complex(n, min(k, 0.0))
		for i in range(N.wvls.length):
			N.N[i] = N_
	
	
	######################################################################
	#                                                                    #
	# set_dN_constant_mixture                                            #
	#                                                                    #
	######################################################################
	def set_dN_constant_mixture(self, dN, n_wvl, wvl):
		"""Set the derivative of the index of refraction in a index
		instance according the the dispersion of a constant mixture
		
		This method takes 3 arguments:
		  dN                the instance in which to store the
		                    derivative;
		  n_wvl             the real part of index of refraction at a
		                    given wavelength;
		  wvl               the wavelength;
		and stores the derivative of the index of refraction in the index
		instance according to the dispersion of the mixture."""
		
		# Locate the interval where the mixture is located.
		i = PCHIP.locate(self.n, n_wvl, False)
		
		# Get the mixture by using the inverse of the PCHIP.
		x = self._n_PCHIP.evaluate_inverse([n_wvl], [i])
		
		# Evaluate dN and dk using the PCHIPs.
		_dn = self._n_PCHIP.evaluate_derivative(x, [i])[0]
		_dk = self._k_PCHIP.evaluate_derivative(x, [i])[0]
		
		# Evaluate k using the PCHIP. If k is larger than 0, set the
		# derivative to 0.
		k = self._k_PCHIP.evaluate(x, [i])[0];
		if k > 0.0:
			_dk = 0.0;
		
		# The derivative is the same for all wavelengths. When normalized
		# by dN at the center wavelength, dN equals 1.
		dN_ = complex(1.0, _dk/_dn)
		for i in range(dN.wvls.length):
			dN.N[i] = dN_



########################################################################
#                                                                      #
# table_mixture                                                        #
#                                                                      #
########################################################################
class table_mixture(mixture):
	"""A class to manage the optical properties of table mixtures"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length, nb_wvls):
		"""Initialize an instance of the table dispersion mixture class
		
		This method takes 2 arguments:
		  length            the number of dispersion curves defining the
		                    mixture;
		  nb_wvls           the number of wavelengths in every
		                    dispersion curve."""
		
		mixture.__init__(self, length)
		
		self.nb_wvls = nb_wvls
		self.wvls = [0.0]*self.nb_wvls
		self.n = [None]*self.length
		self.k = [None]*self.length
		for i_mix in range(self.length):
			self.n[i_mix] = [0.0]*self.nb_wvls
			self.k[i_mix] = [0.0]*self.nb_wvls
		
		self._table_n_PCHIPs = [None]*self.length
		self._table_k_PCHIPs = [None]*self.length
		for i_mix in range(self.length):
			self._table_n_PCHIPs[i_mix] = PCHIP.PCHIP(self.wvls, self.n[i_mix], True, True)
			self._table_k_PCHIPs[i_mix] = PCHIP.PCHIP(self.wvls, self.k[i_mix], True, True)
	
	
	######################################################################
	#                                                                    #
	# set_table_mixture                                                  #
	#                                                                    #
	######################################################################
	def set_table_mixture(self, i_mix, i_wvl, x, wvl, N):
		"""Set the value of the index of refraction for table dispersion
		
		This method takes 5 arguments:
		  i_mix, i_wvl      the position of the dispersion curve in the
		                    list of mixtures;
		  x                 the number associated with the mixture (used
		                    to determine what mixtures are fabricable);
		  wvl               the wavelength;
		  N                 the index of refraction."""
		
		# Make sure that N is complex.
		N = complex(N)
		
		self.X[i_mix] = x
		self.wvls[i_wvl] = wvl
		self.n[i_mix][i_wvl] = N.real
		self.k[i_mix][i_wvl] = N.imag
	
	
	######################################################################
	#                                                                    #
	# prepare_table_mixture                                              #
	#                                                                    #
	######################################################################
	def prepare_table_mixture(self):
		"""This method is deprecated"""
		
		warnings.warn(DeprecationWarning("it is no longer necessary to call prepare_table_mixture"))
	
	
	######################################################################
	#                                                                    #
	# set_mixture_center_wvl                                             #
	#                                                                    #
	######################################################################
	def set_mixture_center_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		# If the new center wavelength is the previous other wavelength,
		# simply swap them.
		if wvl == self._other_wvl:
			self.swap_center_and_other_wvls()
			return
		
		# Otherwise, recalculate the index at the center wavelength and
		# reset the PCHIP.
		index = PCHIP.locate(self.wvls, wvl, True)
		self._center_wvl = wvl
		for i in range(self.length):
			self._n_center_wvl[i] = self._table_n_PCHIPs[i].evaluate([self._center_wvl], indices = [index])[0]
		self._n_center_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# set_mixture_other_wvl                                              #
	#                                                                    #
	######################################################################
	def set_mixture_other_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		index = PCHIP.locate(self.wvls, wvl, True)
		self._other_wvl = wvl
		for i in range(self.length):
			self._n_other_wvl[i] = self._table_n_PCHIPs[i].evaluate([self._other_wvl], indices = [index])[0]
		self._n_other_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# prepare_and_set_mixture_PCHIPs                                     #
	#                                                                    #
	######################################################################
	def prepare_and_set_mixture_PCHIPs(self, wvls):
		"""Prepare and set the PCHIPs to calculate the refractive index at all wavelengths
		
		This method takes 1 argument:
		  wvls              the list of wavelengths at which to prepare
		                    the PCHIPs."""
		
		# Prepare the PCHIPs.
		self.prepare_mixture_PCHIPs(wvls)
		
		# Set the PCHIPs.
		position = 0
		for i_wvl in range(self._nb_wvls):
			
			wvl = self._wvls.wvls[i_wvl]
			
			# The position of the wavelength in the table is determined by
			# simply going through the whole table. This method works because
			# the wavelengths are in increasing order. It is only effective
			# if the number of wavelengths is similar to that in the table
			# and are uniformly distributed. This is usually the case.
			while wvl >= self.wvls[position+1] and position < self.nb_wvls-2:
				position += 1
			
			# Calculate n and k at this wavelength for all mixtures.
			for i_mix in range(self.length):
				self._n[i_wvl][i_mix] = self._table_n_PCHIPs[i_mix].evaluate([wvl], [position])[0]
				self._k[i_wvl][i_mix] = self._table_k_PCHIPs[i_mix].evaluate([wvl], [position])[0]
		
			# Reset the PCHIPs.
			self._n_PCHIPs[i_wvl].reset()
			self._k_PCHIPs[i_wvl].reset()
	
	
	######################################################################
	#                                                                    #
	# get_table_mixture_monotonicity                                     #
	#                                                                    #
	######################################################################
	get_table_mixture_monotonicity = mixture.get_mixture_monotonicity
	
	
	######################################################################
	#                                                                    #
	# get_table_mixture_index                                            #
	#                                                                    #
	######################################################################
	get_table_mixture_index = mixture.get_mixture_index
	
	
	######################################################################
	#                                                                    #
	# get_table_mixture_index_range                                      #
	#                                                                    #
	######################################################################
	get_table_mixture_index_range = mixture.get_mixture_index_range
	
	
	######################################################################
	#                                                                    #
	# change_table_mixture_index_wvl                                     #
	#                                                                    #
	######################################################################
	change_table_mixture_index_wvl = mixture.change_mixture_index_wvl
	
	
	######################################################################
	#                                                                    #
	# set_N_table_mixture                                                #
	#                                                                    #
	######################################################################
	set_N_table_mixture = mixture.set_N_mixture
	
	
	######################################################################
	#                                                                    #
	# set_N_table_mixture_by_x                                           #
	#                                                                    #
	######################################################################
	set_N_table_mixture_by_x = mixture.set_N_mixture_by_x
	
	
	######################################################################
	#                                                                    #
	# set_dN_table_mixture                                               #
	#                                                                    #
	######################################################################
	set_dN_table_mixture = mixture.set_dN_mixture



########################################################################
#                                                                      #
# Cauchy_mixture                                                       #
#                                                                      #
########################################################################
class Cauchy_mixture(mixture):
	"""A class to manage the optical properties of Cauchy mixtures"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the Cauchy dispersion mixture class
		
		This method takes 1 argument:
		  length            the number of dispersion curves defining the
		                    mixture."""
		
		mixture.__init__(self, length)
		
		self.A = [0.0]*self.length
		self.B = [0.0]*self.length
		self.C = [0.0]*self.length
		self.Ak = [0.0]*self.length
		self.exponent = [0.0]*self.length
		self.edge = [0.0]*self.length
	
	
	######################################################################
	#                                                                    #
	# set_Cauchy_mixture                                                 #
	#                                                                    #
	######################################################################
	def set_Cauchy_mixture(self, i, x, A, B, C, Ak, exponent, edge):
		"""Set the dispersion formula for Cauchy dispersion mixture
		
		This method takes 8 arguments:
		  i                   the position of the dispersion curve in the
		                      instance;
		  x                   the number associated with the mixture
		                      (used to determine what mixtures are
		                      fabricable);
		  A, B, C             the parameters of the Cauchy dispersion
		                      model;
		  Ak, exponent, edge  the parameters of the Urbach absorption
		                      tail."""
		
		self.X[i] = x
		self.A[i] = A
		self.B[i] = B
		self.C[i] = C
		self.Ak[i] = Ak
		self.exponent[i] = exponent
		self.edge[i] = edge
	
	
	######################################################################
	#                                                                    #
	# prepare_Cauchy_mixture                                             #
	#                                                                    #
	######################################################################
	def prepare_Cauchy_mixture(self):
		"""This method is deprecated"""
		
		warnings.warn(DeprecationWarning("it is no longer necessary to call prepare_Cauchy_mixture"))
	
	
	######################################################################
	#                                                                    #
	# set_mixture_center_wvl                                             #
	#                                                                    #
	######################################################################
	def set_mixture_center_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		# If the new center wavelength is the previous other wavelength,
		# simply swap them.
		if wvl == self._other_wvl:
			self.swap_center_and_other_wvls()
			return
		
		# Otherwise, recalculate the index at the center wavelength and
		# reset the PCHIP.
		self._center_wvl = wvl
		wvl_micron = 0.001*self._center_wvl
		wvl_micron_square = wvl_micron*wvl_micron
		for i in range(self.length):
			self._n_center_wvl[i] = self.A[i] + self.B[i]/wvl_micron_square + self.C[i]/(wvl_micron_square*wvl_micron_square)
		self._n_center_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# set_mixture_other_wvl                                              #
	#                                                                    #
	######################################################################
	def set_mixture_other_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		self._other_wvl = wvl
		wvl_micron = 0.001*self._other_wvl
		wvl_micron_square = wvl_micron*wvl_micron
		for i in range(self.length):
			self._n_other_wvl[i] = self.A[i] + self.B[i]/wvl_micron_square + self.C[i]/(wvl_micron_square*wvl_micron_square)
		self._n_other_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# prepare_and_set_mixture_PCHIPs                                     #
	#                                                                    #
	######################################################################
	def prepare_and_set_mixture_PCHIPs(self, wvls):
		"""Prepare and set the PCHIPs to calculate the refractive index at all wavelengths
		
		This method takes 1 argument:
		  wvls              the list of wavelengths at which to prepare
		                    the PCHIPs."""
		
		# Prepare the PCHIPs.
		self.prepare_mixture_PCHIPs(wvls)
		
		# Set the PCHIPs.
		for i_wvl in range(self._nb_wvls):
			wvl_micron = 0.001*self._wvls.wvls[i_wvl]
			wvl_micron_square = wvl_micron*wvl_micron
			for i_mix in range(self.length):
				self._n[i_wvl][i_mix] = self.A[i_mix] + self.B[i_mix]/wvl_micron_square + self.C[i_mix]/(wvl_micron_square*wvl_micron_square)
				self._k[i_wvl][i_mix] = -self.Ak[i_mix]*math.exp(12400.0*self.exponent[i_mix]*((1.0/(10000.0*wvl_micron))-(1.0/self.edge[i_mix])))
			
			# Reset the PCHIPs.
			self._n_PCHIPs[i_wvl].reset()
			self._k_PCHIPs[i_wvl].reset()
	
	
	######################################################################
	#                                                                    #
	# get_Cauchy_mixture_monotonicity                                    #
	#                                                                    #
	######################################################################
	get_Cauchy_mixture_monotonicity = mixture.get_mixture_monotonicity
	
	
	######################################################################
	#                                                                    #
	# get_Cauchy_mixture_index                                           #
	#                                                                    #
	######################################################################
	get_Cauchy_mixture_index = mixture.get_mixture_index
	
	
	######################################################################
	#                                                                    #
	# get_Cauchy_mixture_index_range                                     #
	#                                                                    #
	######################################################################
	get_Cauchy_mixture_index_range = mixture.get_mixture_index_range
	
	
	######################################################################
	#                                                                    #
	# change_Cauchy_mixture_index_wvl                                    #
	#                                                                    #
	######################################################################
	change_Cauchy_mixture_index_wvl = mixture.change_mixture_index_wvl
	
	
	######################################################################
	#                                                                    #
	# set_N_Cauchy_mixture                                               #
	#                                                                    #
	######################################################################
	set_N_Cauchy_mixture = mixture.set_N_mixture
	
	
	######################################################################
	#                                                                    #
	# set_N_Cauchy_mixture_by_x                                          #
	#                                                                    #
	######################################################################
	set_N_Cauchy_mixture_by_x = mixture.set_N_mixture_by_x
	
	
	######################################################################
	#                                                                    #
	# set_dN_Cauchy_mixture                                              #
	#                                                                    #
	######################################################################
	set_dN_Cauchy_mixture = mixture.set_dN_mixture



########################################################################
#                                                                      #
# Sellmeier_mixture                                                    #
#                                                                      #
########################################################################
class Sellmeier_mixture(mixture):
	"""A class to manage the optical properties of Sellmeier mixtures"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the Sellmeier dispersion mixture class
		
		This method takes 1 argument:
		  length            the number of dispersion curves defining the
		                    mixture."""
		
		mixture.__init__(self, length)
		
		self.B1 = [0.0]*self.length
		self.C1 = [0.0]*self.length
		self.B2 = [0.0]*self.length
		self.C2 = [0.0]*self.length
		self.B3 = [0.0]*self.length
		self.C3 = [0.0]*self.length
		self.Ak = [0.0]*self.length
		self.exponent = [0.0]*self.length
		self.edge = [0.0]*self.length
	
	
	######################################################################
	#                                                                    #
	# set_Sellmeier_mixture                                              #
	#                                                                    #
	######################################################################
	def set_Sellmeier_mixture(self, i, x, B1, C1, B2, C2, B3, C3, Ak, exponent, edge):
		"""Set the dispersion formula for Sellmeier dispersion mixture
		
		This method takes 11 arguments:
		  i                       the position of the dispersion curve in
		                          the instance;
		  x                       the number associated with the mixture
		                          (used to determine what mixtures are
		                          fabricable);
		  B1, C1, B2, C2, B3, C3  the parameters of the Sellmeier
		                          dispersion model;
		  Ak, exponent, edge      the parameters of the Urbach absorption
		                          tail."""
		
		self.X[i] = x
		self.B1[i] = B1
		self.C1[i] = C1
		self.B2[i] = B2
		self.C2[i] = C2
		self.B3[i] = B3
		self.C3[i] = C3
		self.Ak[i] = Ak
		self.exponent[i] = exponent
		self.edge[i] = edge
	
	
	######################################################################
	#                                                                    #
	# prepare_Sellmeier_mixture                                          #
	#                                                                    #
	######################################################################
	def prepare_Sellmeier_mixture(self):
		"""This method is deprecated"""
		
		warnings.warn(DeprecationWarning("it is no longer necessary to call prepare_Sellmeier_mixture"))
	
	
	######################################################################
	#                                                                    #
	# set_mixture_center_wvl                                             #
	#                                                                    #
	######################################################################
	def set_mixture_center_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		# If the new center wavelength is the previous other wavelength,
		# simply swap them.
		if wvl == self._other_wvl:
			self.swap_center_and_other_wvls()
			return
		
		# Otherwise, recalculate the index at the center wavelength and
		# reset the PCHIP.
		self._center_wvl = wvl
		wvl_micron = 0.001*self._center_wvl
		wvl_micron_square = wvl_micron*wvl_micron
		for i in range(self.length):
			try:
				self._n_center_wvl[i] = math.sqrt(1.0+self.B1[i]*wvl_micron_square/(wvl_micron_square-self.C1[i])\
								                             +self.B2[i]*wvl_micron_square/(wvl_micron_square-self.C2[i])\
					                                   +self.B3[i]*wvl_micron_square/(wvl_micron_square-self.C3[i]))
			except (ZeroDivisionError, ValueError):
				self._n_center_wvl[i] = 0.0
		self._n_center_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# set_mixture_other_wvl                                              #
	#                                                                    #
	######################################################################
	def set_mixture_other_wvl(self, wvl):
		"""Recalculate some internal variables for a new wavelength
		
		This method takes 1 argument:
		  wvl               the wavelength."""
		
		self._other_wvl = wvl
		wvl_micron = 0.001*self._other_wvl
		wvl_micron_square = wvl_micron*wvl_micron
		for i in range(self.length):
			try:
				self._n_other_wvl[i] = math.sqrt(1.0+self.B1[i]*wvl_micron_square/(wvl_micron_square-self.C1[i])\
							                              +self.B2[i]*wvl_micron_square/(wvl_micron_square-self.C2[i])\
				                                    +self.B3[i]*wvl_micron_square/(wvl_micron_square-self.C3[i]))
			except (ZeroDivisionError, ValueError):
				self._n_other_wvl[i] = 0.0
		self._n_other_wvl_PCHIP.reset()
	
	
	######################################################################
	#                                                                    #
	# prepare_and_set_mixture_PCHIPs                                     #
	#                                                                    #
	######################################################################
	def prepare_and_set_mixture_PCHIPs(self, wvls):
		"""Prepare and set the PCHIPs to calculate the refractive index at all wavelengths
		
		This method takes 1 argument:
		  wvls              the list of wavelengths at which to prepare
		                    the PCHIPs."""
		
		# Prepare the PCHIPs.
		self.prepare_mixture_PCHIPs(wvls)
		
		# Set the PCHIPs.
		for i_wvl in range(self._nb_wvls):
			wvl_micron = 0.001*self._wvls.wvls[i_wvl]
			wvl_micron_square = wvl_micron*wvl_micron
			for i_mix in range(self.length):
				try:
					self._n[i_wvl][i_mix] = math.sqrt(1.0+self.B1[i_mix]*wvl_micron_square/(wvl_micron_square-self.C1[i_mix])\
			 	                                       +self.B2[i_mix]*wvl_micron_square/(wvl_micron_square-self.C2[i_mix])\
			 	                                       +self.B3[i_mix]*wvl_micron_square/(wvl_micron_square-self.C3[i_mix]))
				except (ZeroDivisionError, ValueError):
					self._n[i_wvl][i_mix] = 0.0
				self._k[i_wvl][i_mix] = -self.Ak[i_mix]*math.exp(12400.0*self.exponent[i_mix]*((1.0/(10000.0*wvl_micron))-(1.0/self.edge[i_mix])))
	
			# Reset the PCHIPs.
			self._n_PCHIPs[i_wvl].reset()
			self._k_PCHIPs[i_wvl].reset()
	
	
	######################################################################
	#                                                                    #
	# get_Sellmeier_mixture_monotonicity                                 #
	#                                                                    #
	######################################################################
	get_Sellmeier_mixture_monotonicity = mixture.get_mixture_monotonicity
	
	
	######################################################################
	#                                                                    #
	# get_Sellmeier_mixture_index                                        #
	#                                                                    #
	######################################################################
	get_Sellmeier_mixture_index = mixture.get_mixture_index
	
	
	######################################################################
	#                                                                    #
	# get_Sellmeier_mixture_index_range                                  #
	#                                                                    #
	######################################################################
	get_Sellmeier_mixture_index_range = mixture.get_mixture_index_range
	
	
	######################################################################
	#                                                                    #
	# change_Sellmeier_mixture_index_wvl                                 #
	#                                                                    #
	######################################################################
	change_Sellmeier_mixture_index_wvl = mixture.change_mixture_index_wvl
	
	
	######################################################################
	#                                                                    #
	# set_N_Sellmeier_mixture                                            #
	#                                                                    #
	######################################################################
	set_N_Sellmeier_mixture = mixture.set_N_mixture
	
	
	######################################################################
	#                                                                    #
	# set_N_X_Sellmeier_mixture                                          #
	#                                                                    #
	######################################################################
	set_N_Sellmeier_mixture_by_x = mixture.set_N_mixture_by_x
	
	
	######################################################################
	#                                                                    #
	# set_dN_Sellmeier_mixture                                           #
	#                                                                    #
	######################################################################
	set_dN_Sellmeier_mixture = mixture.set_dN_mixture
