# sin2.py
# 
# A class to handle the squared sinus of an angle. This is useful
# when calculating the effective index of refraction at oblique
# incidence
# 
# Copyright (c) 2000-2008,2015 Stephane Larouche.
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



########################################################################
#                                                                      #
# sin2                                                                 #
#                                                                      #
########################################################################
class sin2(object):
	"""A class to handle the squared sinus of an angle"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls):
		"""Initialize an instance of the sin2 class to store the normalized
	 	sinus squared of the propagation angle
		
		This method takes 1 argument:
		  wvls              the wavelengths at which to calculate the
		                    sinus squared.
		
		This class is used to store (N*sin(theta))^2 which, according
		to Snell-Descartes' law is constant in the whole filter and which
		is necessary in the calculation of the effective indices."""
	
		self.wvls = wvls
		self.sin2 = [0.0]*self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# set_sin2_theta_0                                                   #
	#                                                                    #
	######################################################################
	def set_sin2_theta_0(self, N, theta):
		"""Set the value of the normalized sinus squared of the propagation
		angle
		
		This method takes 2 arguments:
		  N                 the index of refraction of the medium where the
		                    angle of incidence is defined;
		  theta_0           the angle of propagation in that medium."""
		
		sin_theta = math.sin(math.radians(theta))
		
		for i in range(self.wvls.length):
			n_sin_theta = N.N[i]*sin_theta
			self.sin2[i] = n_sin_theta*n_sin_theta
	
	
	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of wavelengths at which the sinus squared is
		calculated
		
		This method is called when len(instance) is used. It returns the
		number of wavelengths at which the sinus squared is calculated."""
		
		return self.wvls.length
	
	
	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the sinus squared
		
		This method is called when instance[key] is used. It returns the
		items requested by the key."""
		
		return self.sin2[key]
	
	
	######################################################################
	#                                                                    #
	# __eq__                                                             #
	#                                                                    #
	######################################################################
	def __eq__(self, other):
		"""Check of this object is equal to another."""
		
		if not isinstance(other, self.__class__): return NotImplemented
		
		# If the length of the two objects is different, they are not equal.
		if self.wvls.length != other.wvls.length: return False
		
		# Otherwise, check item by item. If one item is not equal, the
		# objects are not equal.
		for i in range(self.wvls.length):
			if self.wvls.wvls[i] != other.wvls.wvls[i] or self.sin2[i] != other.sin2[i]:
				return False
		
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
		if self.wvls.length != other.wvls.length: return True
		
		# Otherwise, check item by item. If one item is not equal, the
		# objects are not equal.
		for i in range(self.wvls.length):
			if self.wvls.wvls[i] != other.wvls.wvls[i] or self.sin2[i] != other.sin2[i]:
				return True
		
		return False
