# modules.py
# 
# Manage modules.
# 
# Copyright (c) 2002,2005-2009 Stephane Larouche.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
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
import sys
import imp
import glob

import config
import main_directory



base_directory = main_directory.get_main_directory()
module_directory = os.path.join(base_directory, *config.MODULE_DIRECTORY)



########################################################################
#                                                                      #
# submodule                                                            #
#                                                                      #
########################################################################
class submodule(object):
	"""A class for submodules"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, name, function, dialog):
		"""Initialize an instance of the submodule class
		
		This method takes 3 arguments:
		  name               the name of the submodule;
		  function           the function executed by the submodule;
		  dialog             the dialog associated with the module."""
		
		self.name = name
		self.function = function
		self.dialog = dialog
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the submodule"""
		
		return self.name
	
	
	######################################################################
	#                                                                    # 
	# execute_function                                                   #
	#                                                                    #
	######################################################################
	def execute_function(self, filter, position, side, replace, *parameters):
		"""Execute the function of the submodule
		
		This method takes at least 4 arguments:
		  filter             the filter to which to apply the function;
		  position           the position in the filter where to add the
		                     layer designed by the function, when
		                     appropriate;
		  side               the side on which to apply the function, when
		                     appropriate
		  replace            a boolean indicating if the function should
		                     replace existing layer(s)
		any supplementary parameters will be passed to the function."""
		
		self.function(filter, position, side, replace, *parameters)
	
	
	######################################################################
	#                                                                    #
	# execute_dialog                                                     #
	#                                                                    #
	######################################################################
	def execute_dialog(self, parent, filter, description = None):
		"""Show the dialog associated with the submodule
		
		This method takes 2 or 3 arguments:
		  parent             the window that parents the dialog;
		  filter             the filter on which the submodule acts;
		  description        (optional) the present description of the
		                     layer on which the submodule is acting, when
		                     the dialog is used to modify a layer;
		and returns the created dialog (without showing it)."""
		
		window = self.dialog(parent, filter, description)
		
		return window



########################################################################
#                                                                      #
# module                                                               #
#                                                                      #
########################################################################
class module(object):
	"""A class to handle modules"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filename, path = None):
		"""Initialize an instance of the module class
		
		This method takes 2 arguments:
		  filename           the name of the file defining the module;
		  path               the path to the file."""
		
		self.filename = filename
		self.path = path
		
		self.name = self.filename
		self.description = []
		
		self.submodules = []
		
		self.error = False
		self.error_message = ""
		
		self.menu_ID = None
		self.submodule_IDs = []
		self.reload_module_ID = None
		
		self.module = None

		self.load_module()
	
	
	######################################################################
	#                                                                    #
	# load_module                                                        #
	#                                                                    #
	######################################################################
	def load_module(self):
		"""Load the module from the file
		
		This method can also be used to reload a module. This might be
		usefull when debugging a module."""
		
		self.submodules = []
		
		del self.module
		self.module = None
		
		try:
			file, path_name, description = imp.find_module(self.filename, [self.path])
			
			# Try to import the module. Catch all kind of exception since
			# anything can happen during the import of the module.
			try:
				self.module = imp.load_module(self.filename, file, path_name, description)
			except Exception:
				self.error = True
				type_of_exception, value = sys.exc_info()[:2]
				self.error_message += "It was impossible to load the module %s. An exception occured and returned the value: %s.\n" % (self.name, value)
		
		except ImportError:
			self.error = True
			self.error_message += "Could not find module %s. An exception occured and returned the value: %s.\n" % (self.name, value)
		else:
			file.close()
		
		# If there was an error, don't go further.
		if self.error:
			return
		
		# Extract the name or the module. It is not mandatory to
		# define the name of the module inside the module, but it can
		# be used to name the module differently than it's file name.
		# We do it this way instead of checking if the module has a
		# name attribute since hasattr() does it this way too.
		try:
			self.name = self.module.name
		except AttributeError:
			pass
		
		# Extract the definition from the module. The definition is
		# mandatory and must be an array of arrays. Each of those last
		# array describe a submodule by, in that order, it's name,
		# the name of the function that execute the module and the
		# name of the class that present a dialog box for the module.
		try:
			self.description = self.module.description
		except AttributeError:
			self.error = True
			self.error_message += "Could not extract the description from the module %s.\n"
			return
		
		# Analyse the description to create submodules.
		for submodule_description in self.description:
			submodule_name = "?????"
			try:
				submodule_name = submodule_description[0]
				exec(("submodule_function = self.module." + submodule_description[1]))
				exec(("submodule_dialog = self.module." + submodule_description[2]))
				self.submodules.append(submodule(submodule_name, submodule_function, submodule_dialog))
			except (AttributeError, IndexError):
				self.error = True
				type_of_exception, value = sys.exc_info()[:2]
				self.error_message += "An error occured while creating the submodule %s of the module %s. An exception occured and returned the value:%s. Check that the description given in the module correspond to the functions.\n" % (submodule_name, self.name, value)
	
	
	######################################################################
	#                                                                    #
	# get_error                                                          #
	#                                                                    #
	######################################################################
	def get_error(self):
		"""Get if an error occured and the error message
		
		This method returns a boolean indicating if a error occured while
		the module was loaded and the error message associated with it."""
		
		error = self.error
		error_message = self.error_message
		
		self.error = False
		self.error_message = ""
		
		return error, error_message
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the module"""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# get_submodule                                                      #
	#                                                                    #
	######################################################################
	def get_submodule(self, number = None):
		"""Get submodule(s)
		
		This method takes an optional argument:
		  number             (optional) the number of the submodule.
		
		When number is absent, a list of all submodules is returned."""
		
		if number is None:
			return self.submodules
		else:
			return self.submodules[number]
	
	
	######################################################################
	#                                                                    #
	# set_menu_ID                                                        #
	#                                                                    #
	######################################################################
	def set_menu_ID(self, menu_ID):
		"""Set the ID of the menu associated with the module
		
		This method takes a single argument:
		  menu_ID            the id of the menu of the module"""
		
		self.menu_ID = menu_ID
	
	
	######################################################################
	#                                                                    #
	# get_menu_ID                                                        #
	#                                                                    #
	######################################################################
	def get_menu_ID(self):
		"""Get the ID of the menu associated with the module"""
		
		return self.menu_ID
	
	
	######################################################################
	#                                                                    #
	# set_submodule_IDs                                                  #
	#                                                                    #
	######################################################################
	def set_submodule_IDs(self, submodule_IDs):
		"""Set the IDs of the menu items associated with the modules
		
		This method takes a single argument:
		  submodule_IDs      the ids of the menu items associated with the
		                     submodules."""
		
		self.submodule_IDs = submodule_IDs
	
	
	######################################################################
	#                                                                    #
	# get_submodule_IDs                                                  #
	#                                                                    #
	######################################################################
	def get_submodule_IDs(self):
		"""Get the IDs of the menu items associated with the modules"""
		
		return self.submodule_IDs
	
	
	######################################################################
	#                                                                    #
	# get_submodule_by_ID                                                #
	#                                                                    #
	######################################################################
	def get_submodule_by_ID(self, submodule_ID):
		"""Get the submodule associated with a menu item ID
		
		This method takes a single input argument
		  submodule_ID       the id of the menu items;
		and returns the submodule associated to this id, or None if no
		submodule is associated with this id."""
		
		try:
			return self.submodules[self.submodule_IDs.index(submodule_ID)]
		except ValueError:
			return None
	
	
	######################################################################
	#                                                                    #
	# get_submodule_by_name                                              #
	#                                                                    #
	######################################################################
	def get_submodule_by_name(self, name):
		"""Get the submodule with a given name
		
		This method takes a single input argument
		  name               the name of the submodule;
		and returns the submodule associated to this name, or None if no
		submodule is associated with this name."""
		
		for i in range(len(self.submodules)):
			if self.submodules[i].get_name() == name:
				return self.submodules[i]
		
		return None



########################################################################
#                                                                      #
# load_modules                                                         #
#                                                                      #
########################################################################
def load_modules():
	"""Load the modules
	
	This method returns:
	  modules              a list of all the modules in the module
	                       directory
	  errors               a boolean indicating if an error occurred
	                       while loading the modules
	  error_messages       the messages discribing all errors that
	                       occured."""
	
	# Find modules and compiled modules.
	module_files = [os.path.split(filename)[1][:-3] for filename in glob.glob(os.path.join(module_directory, "*.py"))]
	compiled_module_files = [os.path.split(filename)[1][:-4] for filename in glob.glob(os.path.join(module_directory, "*.pyc"))]
	optimized_module_files = [os.path.split(filename)[1][:-4] for filename in glob.glob(os.path.join(module_directory, "*.pyo"))]
	
	# Build a list of all modules without redundancy.
	module_files += [filename for filename in compiled_module_files if filename not in module_files]
	module_files += [filename for filename in optimized_module_files if filename not in module_files]
	
	# Sort the modules in alphabetical order.
	module_files.sort(key = str.lower)
	
	# Open the modules via the module class.
	errors = False
	error_messages = ""
	modules = []
	for module_name in module_files:
		new_module = module(module_name, module_directory)
		modules.append(new_module)
		error, error_message = new_module.get_error()
		errors = errors or error
		if error:
			error_messages = error_messages + error_message + "\n"
	
	return modules, errors, error_messages
