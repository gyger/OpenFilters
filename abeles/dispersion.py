# dispersion.py
# 
# Classes to manage various dispersion models.
# 
# Copyright (c) 2002-2008,2012,2014 Stephane Larouche.
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
# constant                                                             #
#                                                                      #
########################################################################
class constant(object):
	"""A class to manage constant dispersion"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the constant dispersion class
		
		This method takes and returns no argument."""
		
		self.N = 0.0+0.0j
	
	
	######################################################################
	#                                                                    #
	# set_constant                                                       #
	#                                                                    #
	######################################################################
	def set_constant(self, N):
		"""Set the value of the index of refraction for constant dispersion
		
		This method takes 1 argument:
		  N                 the index of refraction."""
		
		# Make sure that n is complex.
		N = complex(N)
		
		self.N = N
	
	
	######################################################################
	#                                                                    #
	# set_N_constant                                                     #
	#                                                                    #
	######################################################################
	def set_N_constant(self, N):
		"""Set the index of refraction from a constant dispersion
		
		This method takes 1 argument:
		  N                 the index of refraction instance that must
		                    be set."""
	
		for i in range(N.wvls.length):
			N.N[i] = self.N


########################################################################
#                                                                      #
# table                                                                #
#                                                                      #
########################################################################
class table(object):
	"""A class to manage table dispersion"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the table dispersion class
		
		This method takes 1 argument:
		  length            the number of points in the table."""
		
		self.length = length
		self.wvls = [0.0]*self.length
		self.n = [0.0]*self.length
		self.k = [0.0]*self.length
		self._n_PCHIP = PCHIP.PCHIP(self.wvls, self.n, preserve_monotonicity = True, allow_extrapolation = True)
		self._k_PCHIP = PCHIP.PCHIP(self.wvls, self.k, preserve_monotonicity = True, allow_extrapolation = True)
	
	
	######################################################################
	#                                                                    #
	# set_table                                                          #
	#                                                                    #
	######################################################################
	def set_table(self, pos, wvl, N):
		"""Set one value of the index of refraction for table dispersion
		
		This method takes 3 arguments:
		  pos               the position in the table;
		  wlv               the wavelength;
		  N                 the index of refraction."""
		
		# Make sure that n is complex.
		N = complex(N)
		
		self.wvls[pos] = wvl
		self.n[pos] = N.real
		self.k[pos] = N.imag
	
	
	######################################################################
	#                                                                    #
	# prepare_table                                                      #
	#                                                                    #
	######################################################################
	def prepare_table(self):
		"""This method is deprecated"""
		
		warnings.warn(DeprecationWarning("it is no longer necessary to call prepare_table"))
	
	
	######################################################################
	#                                                                    #
	# get_table_index                                                    #
	#                                                                    #
	######################################################################
	def get_table_index(self, wvl):
		"""Get the index of refraction at a single wavelength from a table
		dispersion
		
		This method takes 1 argument:
		  wvl               the wavelength;
		and returns the real part of the index of refraction."""
		
		# Calculate real part of the index using PCHIPs.
		n = self._n_PCHIP.evaluate([wvl])[0]
		
		return n
	
	
	######################################################################
	#                                                                    #
	# set_N_table                                                        #
	#                                                                    #
	######################################################################
	def set_N_table(self, N):
		"""Set the index of refraction from a table dispersion
		
		This method takes 1 argument:
		  N                 the index of refraction instance that must
		                    be set."""
		
		positions = [0]*N.wvls.length
		
		# Find the positions of the wavelengths of n in the intervals
		# of basis. The search method supposes that wavelengths are in
		# increasing order. It simply goes through all of the table which
		# is only effective if the number of interpolated wavelengths
		# is similar or higher than the number of wavelengths in the
		# table and if they are uniformly distributed. This is
		# usually the case, so I don't bother creating a more complex
		# algorithm.
		i_wvl = 0
		for i_wvl_material in range(self.length-1):
			while i_wvl < N.wvls.length and N.wvls.wvls[i_wvl] < self.wvls[i_wvl_material+1]:
				positions[i_wvl] = i_wvl_material
				i_wvl += 1
		# A special case must be done for the data extrapolated at the
		# end of the basis.
		for i_wvl in range(i_wvl, N.wvls.length):
			positions[i_wvl] = self.length-2
		
		# Evaluate the PCHIPs.
		n = self._n_PCHIP.evaluate(N.wvls.wvls, indices = positions)
		k = self._k_PCHIP.evaluate(N.wvls.wvls, indices = positions)
		
		# Convert it back to complex numbers and put it in N. Eliminate
		# positive values of k.
		for i_wvl in range(N.wvls.length):
			N.N[i_wvl] = complex(n[i_wvl], min(k[i_wvl], 0.0))



########################################################################
#                                                                      #
# Cauchy                                                               #
#                                                                      #
########################################################################
class Cauchy(object):
	"""A class to manage Cauchy dispersion"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the Cauchy dispersion class
		
		This method takes and returns no argument."""
		
		self.A = 0.0
		self.B = 0.0
		self.C = 0.0
		self.Ak = 0.0
		self.exponent = 0.0
		self.edge = 0.0
	
	
	######################################################################
	#                                                                    #
	# set_Cauchy                                                         #
	#                                                                    #
	######################################################################
	def set_Cauchy(self, A, B, C, Ak, exponent, edge):
		"""Set the dispersion formula for Cauchy dispersion
		
		This method takes 6 arguments:
		  A, B, C             the parameters of the Cauchy dispersion
		                      model;
		  Ak, exponent, edge  the parameters of the Urbach absorption
		                      tail."""
		
		self.A = A
		self.B = B
		self.C = C
		self.Ak = Ak
		self.exponent = exponent
		self.edge = edge
	
	
	######################################################################
	#                                                                    #
	# set_N_Cauchy                                                       #
	#                                                                    #
	######################################################################
	def set_N_Cauchy(self, N):
		"""Set the index of refraction from a Cauchy dispersion
		
		This method takes 1 argument:
		  N                 the index of refraction instance that must
		                    be set."""
		
		for i in range(N.wvls.length):
			wvl_micron = 0.001*N.wvls.wvls[i]
			wvl_micron_square = wvl_micron*wvl_micron
			N.N[i] = complex(self.A + self.B/wvl_micron_square + self.C/(wvl_micron_square*wvl_micron_square),
			                 -self.Ak*math.exp(12400.0*self.exponent*((1.0/(10000.0*wvl_micron))-(1.0/self.edge))))



########################################################################
#                                                                      #
# Sellmeier                                                            #
#                                                                      #
########################################################################
class Sellmeier(object):
	"""A class to manage Sellmeier dispersion"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the Sellmeier dispersion class
		
		This method takes and returns no argument."""
		
		self.B1 = 0.0
		self.C1 = 0.0
		self.B2 = 0.0
		self.C2 = 0.0
		self.B3 = 0.0
		self.C3 = 0.0
		self.Ak = 0.0
		self.exponent = 0.0
		self.edge = 0.0
	
	
	######################################################################
	#                                                                    #
	# set_Sellmeier                                                      #
	#                                                                    #
	######################################################################
	def set_Sellmeier(self, B1, C1, B2, C2, B3, C3, Ak, exponent, edge):
		"""Set the dispersion formula for Sellmeier dispersion
		
		This method takes 9 arguments:
		  B1, C1, B2, C2, B3, C3  the parameters of the Sellmeier dispersion
		                          model;
		  Ak, exponent, edge      the parameters of the Urbach absorption
		                          tail."""
		
		self.B1 = B1
		self.C1 = C1
		self.B2 = B2
		self.C2 = C2
		self.B3 = B3
		self.C3 = C3
		self.Ak = Ak
		self.exponent = exponent
		self.edge = edge
	
	
	######################################################################
	#                                                                    #
	# set_N_Sellmeier                                                    #
	#                                                                    #
	######################################################################
	def set_N_Sellmeier(self, N):
		"""Set the index of refraction from a Sellmeier dispersion
		
		This method takes 1 argument:
		  N                 the index of refraction instance that must
		                    be set."""
		
		for i in range(N.wvls.length):
			wvl_micron = 0.001*N.wvls.wvls[i]
			wvl_micron_square = wvl_micron*wvl_micron
			try:
				n = math.sqrt(1.0+self.B1*wvl_micron_square/(wvl_micron_square-self.C1)\
				                 +self.B2*wvl_micron_square/(wvl_micron_square-self.C2)\
				                 +self.B3*wvl_micron_square/(wvl_micron_square-self.C3))
			except (ZeroDivisionError, ValueError):
				n = 0.0
			N.N[i] = complex(n, -self.Ak*math.exp(12400.0*self.exponent*((1.0/(10000.0*wvl_micron))-(1.0/self.edge))))
