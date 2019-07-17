# circle.py
# 
# A class to calculate the circle diagram of the coating from
# amplitude reflection.
# 
# Copyright (c) 2006-2008 Stephane Larouche.
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



from definitions import *



########################################################################
#                                                                      #
# circle                                                               #
#                                                                      #
########################################################################
class circle(object):
	"""A class to calculate the circle diagram of the coating from
	amplitude reflection."""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the circle class
		
		This function takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    circle."""
		
		self.wvls = wvls
		
		self.data = [0.0]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# calculate_circle                                                   #
	#                                                                    #
	######################################################################
	def calculate_circle(self, r_and_t, polarization):
		"""Determine the value of amplitude reflection for the circle
		diagram
		
		This method takes 2 arguments:
		  r_and_t           the amplitude reflection and transmission;
		  polarization      the polarization of light."""
		
		if polarization == S:
			for i in range(self.wvls.length):
				self.data[i] = r_and_t.r_s[i]
		
		elif polarization == P:
			for i in range(self.wvls.length):
				self.data[i] = r_and_t.r_p[i]
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the circle is calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the circle is calculated."""
		
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the circle
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
		
		return self.data[key]
