# version.py
# 
# A class to manage and compare versions.
# 
# Copyright (c) 2012 Stephane Larouche.
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



import string



########################################################################
#                                                                      #
# version                                                              #
#                                                                      #
########################################################################
class version(object):
	"""A class to manage and compare versions
	
	This class implements all the comparison operators to compare version
	numbers."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, *args):
		"""Initialize an instance of the target class
		
		A version is composed of 2 or 3 digits, seperated by periods. For
		example, 1.0.5 and 2.1 are valid version numbers.
		
		This method either takes a single string argument defining the
		version number, or 2 or 3 integer arguments."""
		
		if len(args) < 1 or len(args) > 3:
			raise TypeError
		
		try:
			if len(args) == 1 and isinstance(args[0], str):
				number, _, self.build = args[0].partition("-")
				numbers = string.split(number, ".")
				self.major = int(numbers[0])
				self.minor = int(numbers[1])
				if len(numbers) == 2: self.revision = 0
				elif len(numbers) == 3: self.revision = int(numbers[2])
				else:	raise ValueError
			
			else:
				self.major = int(args[0])
				self.minor = int(args[1])
				if len(args) > 2: self.revision = int(args[2])
				else: self.revision = 0
		except:
			raise ValueError
	
	
	######################################################################
	#                                                                    #
	# __repr__                                                           #
	#                                                                    #
	######################################################################
	def __repr__(self):
		return "version(%i, %i, %i)" % (self.major, self.minor, self.revision)
	
	
	######################################################################
	#                                                                    #
	# __str__                                                            #
	#                                                                    #
	######################################################################
	def __str__(self):
		if self.revision:
			return "%i.%i.%i" % (self.major, self.minor, self.revision)
		else:
			return "%i.%i" % (self.major, self.minor)
	
	
	######################################################################
	#                                                                    #
	# __lt__                                                             #
	# __le__                                                             #
	# __eq__                                                             #
	# __ne__                                                             #
	# __gt__                                                             #
	# __ge__                                                             #
	#                                                                    #
	######################################################################
	def __lt__(self, other):
		if self.major < other.major: return True
		elif self.minor < other.minor: return True
		elif self.revision < other.revision: return True
		else: return False
	
	def __le__(self, other):
		if self.major > other.major: return False
		elif self.minor > other.minor: return False
		elif self.revision > other.revision: return False
		else: return True
	
	def __eq__(self, other):
		if self.major == other.major and self.minor == other.minor and self.revision == other.revision: return True
		else: return False
	
	def __ne__(self, other): 
		if self.major != other.major or self.minor != other.minor or self.revision != other.revision: return True
		else: return False
	
	def __gt__(self, other):
		if self.major > other.major: return True
		elif self.minor > other.minor: return True
		elif self.revision > other.revision: return True
		else: return False
	
	def __ge__(self, other):
		if self.major < other.major: return False
		elif self.minor < other.minor: return False
		elif self.revision < other.revision: return False
		else: return True
