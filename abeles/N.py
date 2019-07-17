# N.py
#
# A class to manage an array of index of refraction.
#
# Copyright (c) 2002-2008 Stephane Larouche.
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



########################################################################
#                                                                      #
# N                                                                    #
#                                                                      #
########################################################################
class N(object):
	"""A class to manage an array of index of refraction."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the N class to store the index of
		refraction of a material
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    index of refraction."""
		
		self.wvls = wvls
		self.N = [0.0+0.0j]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# copy                                                               #
	#                                                                    #
	######################################################################
	def copy(self, N):
		"""Copy an index instance
		
		This method takes 1 argument:
		  N                 the original index of refraction
		and copy it in the instance used to call this method."""
		
		for i in range(self.wvls.length):
			self.N[i] = N.N[i]
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the index is calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the index is calculated."""
	
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the index
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
	
		return self.N[key]
