# optimization.py
# 
# Optimization classes for Filters
#
# Copyright (c) 2000-2008 Stephane Larouche.
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

import config
from moremath import interpolation
import targets



########################################################################
#                                                                      #
# optimization_error                                                   #
#                                                                      #
########################################################################
class optimization_error(Exception):
	"""Exception class for optimization errors"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Optimization error: %s." % self.value
		else:
			return "Optimization error."



########################################################################
#                                                                      #
# optimization                                                         #
#                                                                      #
########################################################################
class optimization(object):
	"""A generic optimization class
	
	All optimization class derive from this class."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, targets, parent = None):
		"""Initialize an instance of the optimization class
		
		This method takes 2 or 3 arguments:
		  filter             the filter being optimized;
		  targets            the targets used in the optimization;
		  parent             (optional) the user interface used to do the
		                     optimization.
		
		If given, the parent must implement an update method taking two
		arguments (working, status)."""
		
		self.filter = filter
		self.targets = targets
		self.parent = parent
		
		# Stop criteria.
		self.max_iterations = 0
		self.acceptable_chi_2 = 0.0
		self.min_chi_2_change = 0.0
		
		# Initial maximum number of iteration, used to increase the maximum
		# number of iteration when the user wants to continue the
		# refinement.
		self.initial_max_iterations = self.max_iterations
		
		# The evolution and quality of the fit.
		self.max_iterations_reached = False
		self.status = 0
		self.chi_2 = 0.0
		self.stop_criteria_met = False
		
		# The number of iterations already done.
		self.iteration = 0
		
		# Is work currently being done and can it be stopped?
		self.working = False
		self.can_stop = False
		
		# Should the optimization continue.
		self.continue_optimization = False
	
	
	######################################################################
	#                                                                    #
	# set_parent                                                         #
	#                                                                    #
	######################################################################
	def set_parent(self, parent = None):
		"""Set the parent
		
		This method takes an optional argument:
		  parent             (optional) the user interface used to do the
		                     optimization.
		
		If given, the parent must implement an update method taking two
		arguments (working, status)."""
		
		self.parent = parent
	
	
	######################################################################
	#                                                                    #
	# increase_max_iterations                                            #
	#                                                                    #
	######################################################################
	def increase_max_iterations(self, increment = None):
		"""Increase the maximum number of iterations
		
		This method takes an optional argument:
		  increment          (optional) the number of iterations to add.
		
		By default, the number of iterations is increased by the original
		number of arguments."""
		
		if increment is None:
			increment = self.initial_max_iterations
		self.max_iterations += increment
		self.max_iterations_reached = False
	
	
	######################################################################
	#                                                                    #
	# reset_iterations                                                   #
	#                                                                    #
	######################################################################
	def reset_iterations(self):
		"""Reset the number of iterations"""
		
		self.iteration = 0
		self.max_iterations = self.initial_max_iterations
		self.max_iterations_reached = False
		self.stop_criteria_met = False
	
	
	######################################################################
	#                                                                    #
	# iterate_                                                           #
	#                                                                    #
	######################################################################
	def iterate_(self):
		"""A generic method to do one iteration
		
		The derived class must define this method."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# iterate                                                            #
	#                                                                    #
	######################################################################
	def iterate(self):
		"""Perform one iteration
		
		In addition to calling the derived class iterate_, this method
		takes care of updating the user interface."""
		
		self.working = True
		self.can_stop = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		self.iterate_()
		
		self.working = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
	
	
	######################################################################
	#                                                                    #
	# go                                                                 #
	#                                                                    #
	######################################################################
	def go(self):
		"""Optimize the filter
		
		This method optimizes the filter until a stopping criteria is met
		or the maximum number of iteration is reached.
		
		In addition to calling the derived class iterate_ repeatedly, this
		method takes care of updating the user interface."""
		
		self.continue_optimization = True
		self.working = True
		self.can_stop = True
		
		# Increase the number of iteration when asked to continue.
		if self.max_iterations_reached:
			self.increase_max_iterations()
		
		if self.parent:
			self.parent.update(self.working, self.status)
		
		while self.continue_optimization:
			self.iterate_()
			
			if self.stop_criteria_met or self.max_iterations_reached:
				break
			
			if self.parent:
				self.parent.update(self.working, self.status)
		
		self.working = False
		
		if self.parent:
			self.parent.update(self.working, self.status)
	
	
	######################################################################
	#                                                                    #
	# stop                                                               #
	#                                                                    #
	######################################################################
	def stop(self):
		"""Stop the optimization
		
		This will stop the optimization after the current iteration."""
		
		self.continue_optimization = False
	
	
	######################################################################
	#                                                                    #
	# get_iteration                                                      #
	#                                                                    #
	######################################################################
	def get_iteration(self):
		"""Get the number of iterations
		
		This method returns the number of iteration."""
		
		return self.iteration
	
	
	######################################################################
	#                                                                    #
	# get_status                                                         #
	#                                                                    #
	######################################################################
	def get_status(self):
		"""Get the status of the optimization
		
		This method returns the status of the optimization."""
		
		return self.status
	
	
	######################################################################
	#                                                                    #
	# get_chi_2                                                          #
	#                                                                    #
	######################################################################
	def get_chi_2(self):
		"""Get chi square
		
		This method returns the chi square of the optimization."""
		
		return self.chi_2
	
	
	######################################################################
	#                                                                    #
	# get_stop_criteria_met                                              #
	#                                                                    #
	######################################################################
	def get_stop_criteria_met(self):
		"""Get if a stop criteria was met
		
		This method returns a boolean indicating if a stop criteria was med
		during the optimization."""
		
		return self.stop_criteria_met
	
	
	######################################################################
	#                                                                    #
	# get_max_iterations_reached                                         #
	#                                                                    #
	######################################################################
	def get_max_iterations_reached(self):
		"""Get if the maximum number of iteration was reached
		
		This method returns a boolean indicating if the maximum number of
		iteration was reached."""
		
		return self.max_iterations_reached
	
	
	######################################################################
	#                                                                    #
	# get_working                                                        #
	#                                                                    #
	######################################################################
	def get_working(self):
		"""Get if the optimization is working
		
		This method returns a boolean indicating if the optimization is
		working."""
		
		return self.working
	
	
	######################################################################
	#                                                                    #
	# get_can_stop                                                       #
	#                                                                    #
	######################################################################
	def get_can_stop(self):
		"""Get if it is possible to stop the current operation
		
		This method returns a boolean indicating if it is possible to stop
		the current operation. In most optimization method, it is possible
		to stop between iterations, but not inside an iteration."""
		
		return self.can_stop
	
	
	######################################################################
	#                                                                    #
	# copy_to_filter                                                     #
	#                                                                    #
	######################################################################
	def copy_to_filter(self):
		"""Copy the optimized filter to the filter instance
		
		Derived class must implement this method."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# save_index_profile                                                 #
	#                                                                    #
	######################################################################
	def save_index_profile(self, file):
		"""Save the index profile
		
		This method takes one argument:
		  file               the file in which to write.
		
		Derived class must implement this method."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# save_values                                                        #
	#                                                                    #
	######################################################################
	def save_values(self, file):
		"""Save the current values of the optimized properties
		
		This method takes one argument:
		  file               the file in which to write.
		
		Derived class must implement this method."""
		
		raise NotImplementedError("Subclass must implement this method")
