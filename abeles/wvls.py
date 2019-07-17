# wvls.py
# 
# Manage an array of wavelengths for the Abeles module.
#
# Copyright (c) 2002-2008,2015 Stephane Larouche.
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
# wvls                                                                 #
#                                                                      #
########################################################################
class wvls(object):
	"""A class to manage an array of wavelengths for the Abeles module"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, length):
		"""Initialize an instance of the wvls class to store an array of
		wavelengths
		
		This method takes 1 argument:
		  length            the number of wavelengths in the array.
		
		This class is used in many of the classes defined in the abeles
		module to define the wavelengths used for calculations."""
		
		self.length = length
		self.wvls = [0.0]*self.length
	
	
	######################################################################
	#                                                                    #
	# set_wvl                                                            #
	#                                                                    #
	######################################################################
	def set_wvl(self, position, wvl):
		"""Set one of the wavelengths in a wvls instance
		
		This method takes 2 arguments:
		  position          the position of the wavelength to set;
		  wvl               the wavelength."""
		
		self.wvls[position] = wvl
	
	
	######################################################################
	#                                                                    #
	# set_wvls_by_range                                                  #
	#                                                                    #
	######################################################################
	def set_wvls_by_range(self, from_wvl, by_wvl):
		"""Set the wavelengths by an initial value and an increment.
		
		This method takes 2 arguments:
		  from_wvl          the wavelength for position 0;
		  by_wvl            the wavelength increment."""
		
		for i in range(self.length):
			self.wvls[i] = from_wvl + i*by_wvl
	
	
	######################################################################
	#                                                                    #
	# index                                                              #
	#                                                                    #
	######################################################################
	def index(self, wavelength):
		"""Get the index of one wavelength
		
		This method takes 1 argument:
		  wavelength        the element to find;
		and returns the position of the wavelength in the array."""
		
		return self.wvls.index(wavelength)
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths."""
		
		return self.length
	
	
	######################################################################
	#                                                                    #
	# __contains__                                                       #
	#                                                                    #
	######################################################################
	def __contains__(self, item):
		"""Determine if a wavelength is member of an instance
		
		This method is called when "item in instance" is used. It returns
		a boolean indicating if the item is a wavelength contained in the
		instance."""
		
		return item in self.wvls
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the wavelength
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
		
		return self.wvls[key]
	
	
	######################################################################
	#                                                                    #
	# __eq__                                                             #
	#                                                                    #
	######################################################################
	def __eq__(self, other):
		"""Check of this object is equal to another."""
		
		if not isinstance(other, self.__class__): return NotImplemented
		
		# If the length of the two objects is different, they are not equal.
		if self.length != other.length: return False
		
		# Otherwise, check item by item. If one item is not equal, the
		# objects are not equal.
		for i in range(self.length):
			if self.wvls[i] != other.wvls[i]: return False
		
		return True
	
	
	######################################################################
	#                                                                    #
	# __ne__                                                             #
	#                                                                    #
	######################################################################
	def __ne__(self, other):
		"""Check of this object is not equal to another."""
		
		if not isinstance(other, self.__class__): return NotImplemented
		
		# If the length of the two objects is different, they are not equal.
		if self.length != other.length: return True
		
		# Otherwise, check item by item. If one item is not equal, the
		# objects are not equal.
		for i in range(self.length):
			if self.wvls[i] != other.wvls[i]: return True
		
		return False
