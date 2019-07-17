# project.py
# 
# A class to handle a full optical coating design project. A project
# mainly consists of filters and targets. This file also defines
# functions to read and write a project to a file.
#
# Copyright (c) 2007,2009,2010,2012,2013,2015 Stephane Larouche.
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



import os
import tempfile

import simple_parser
import optical_filter
import targets
import materials
import version
import release



########################################################################
#                                                                      #
# project_error                                                        #
#                                                                      #
########################################################################
class project_error(Exception):
	"""Exception class for project errors"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Project error: %s." % self.value
		else:
			return "Project error."



########################################################################
#                                                                      #
# project                                                              #
#                                                                      #
########################################################################
class project(object):
	"""A class to represent an optical coating design project
	
	This class holds together a list of filters and a list of targets. In
	addition, it provides the possibility to set a multiline comment."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, material_catalog = None):
		"""Initialize the project
		
		This method takes one optional input argument:
		  material_catalog      (optional) the material catalog to use, if
		                        omitted, the default materials are used."""
		
		# If no material catalog is provided, use the default one.
		if material_catalog:
			self.material_catalog = material_catalog
		else:
			self.material_catalog = materials.material_catalog()
		
		self.comment = ""
		
		self.filters = []
		self.targets = []
		
		self.nb_filters = 0
		self.nb_targets = 0
		
		self.modified = False
	
	
	######################################################################
	#                                                                    #
	# set_comment                                                        #
	#                                                                    #
	######################################################################
	def set_comment(self, comment):
		"""Set the comment
		
		This method takes a single input argument:
		  comment      the comment."""
		
		if comment != self.comment:
			self.comment = comment
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_comment                                                        #
	#                                                                    #
	######################################################################
	def get_comment(self):
		"""Get the comment
		
		This method returns a single output argument:
		  comment      the comment."""
		
		return self.comment
	
	
	######################################################################
	#                                                                    #
	# get_material_catalog                                               #
	#                                                                    #
	######################################################################
	def get_material_catalog(self):
		"""Get the material catalog used by the project
		
		This method returns a single output argument:
		  catalog      the catalog."""
		
		return self.material_catalog
	
	
	######################################################################
	#                                                                    #
	# add_filter                                                         #
	#                                                                    #
	######################################################################
	def add_filter(self, filter = None):
		"""Add a filter to the project
		
		This method takes an optional input argument:
		  filter       (optional) the filter to add ,
		and returns the index of the filter that was added,
		
		If no filter is provided, a new one is created."""
		
		if not filter:
			filter = optical_filter.optical_filter(self.material_catalog)
		
		self.filters.append(filter)
		
		self.nb_filters += 1
		
		self.modified = True
		
		return self.filters.index(filter)
	
	
	######################################################################
	#                                                                    #
	# add_target                                                         #
	#                                                                    #
	######################################################################
	def add_target(self, target):
		"""Add a target to the project
		
		This method takes a single input argument:
		  target       the target to add."""
		
		self.targets.append(target)
		self.nb_targets += 1
		
		self.modified = True
		
		return self.targets.index(target)
	
	
	######################################################################
	#                                                                    #
	# remove_filter                                                      #
	#                                                                    #
	######################################################################
	def remove_filter(self, nb):
		"""Remove a filter from the project
		
		This method takes a single input argument:
		  filter       the number of the filter to remove."""
		
		self.filters.pop(nb)
		self.nb_filters -= 1
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# remove_target                                                      #
	#                                                                    #
	######################################################################
	def remove_target(self, nb):
		"""Remove a target from the project
		
		This method takes a single input argument:
		  target       the number of the target to remove."""
		
		self.targets.pop(nb)
		self.nb_targets -= 1
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_nb_filters                                                     #
	#                                                                    #
	######################################################################
	def get_nb_filters(self):
		"""Get the number of filters in the project
		
		This method returns of filters in the project."""
		
		return self.nb_filters
	
	
	######################################################################
	#                                                                    #
	# get_filters                                                        #
	#                                                                    #
	######################################################################
	def get_filters(self):
		"""Get the list of filters in the project
		
		This method returns the list of filters in the project."""
		
		return self.filters
	
	
	######################################################################
	#                                                                    #
	# get_filter                                                         #
	#                                                                    #
	######################################################################
	def get_filter(self, nb):
		"""Get a filter in the project
		
		This method takes a single input argument:
		  nb       the number of the filter
		and returns the filter."""
		
		return self.filters[nb]
	
	
	######################################################################
	#                                                                    #
	# get_nb_targets                                                     #
	#                                                                    #
	######################################################################
	def get_nb_targets(self, kind = None):
		"""Get the number of targets in the project
		
		When used without argument, this method simply returns of targets
		in the project. When used with the argument
		  kind          a specific king of target,
		it returns the number of targets of this kind."""
		
		if kind is None:
			return self.nb_targets
		
		nb_targets = 0
		for target in self.targets:
			if target.get_kind() == kind:
				nb_targets += 1
		
		return nb_targets
	
	
	######################################################################
	#                                                                    #
	# get_targets                                                        #
	#                                                                    #
	######################################################################
	def get_targets(self):
		"""Get the list of targets in the project
		
		This method returns the list of targets in the project."""
		
		return self.targets
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self, nb):
		"""Get a target in the project
		
		This method takes a single input argument:
		  nb       the number of the target
		and returns the target."""
		
		return self.targets[nb]
	
	
	######################################################################
	#                                                                    #
	# set_modified                                                       #
	#                                                                    #
	######################################################################
	def set_modified(self, modified):
		"""Set the modification status of the project
		
		Use this method when the project is saved in order to track
		modifications between saves. This method takes a single input
		argument:
		  modified     indication of the modification status."""
		
		self.modified = modified
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the project was modified
		
		This method returns True or False depending if the project, or any
		filter or target included in the project have been modified."""
		
		if self.modified:
			return True
		
		for i in range(self.nb_filters):
			if self.filters[i].get_modified():
				return True
		for i in range(self.nb_targets):
			if self.targets[i].get_modified():
				return True
		
		return False



########################################################################
#                                                                      #
# parse_project                                                        #
#                                                                      #
########################################################################
def parse_project(lines, material_catalog = None):
	"""Parse a project file
	
	This function takes 1 or 2 input arguments:
	  lines             the lines of a project file (a list of strings);
	  material_catalog  (optional) the material catalog to use with this
		                  project;
	and returns a single output argument:
	  project           the project.
	
	If an error occurs during the parsing of the file, a project_error
  is raised."""
  
	try:
		keywords, values = simple_parser.parse(lines)
	except simple_parser.parsing_error, error:
		raise project_error("Cannot parse project because %s" % error.get_value())
	
	new_project = project(material_catalog)
	
	if keywords[0] == "Version":
		keywords.pop(0)
		try:
			file_version = version.version(values.pop(0))
		except ValueError:
			raise project_error("Version number could not be parsed")
	else:
		file_version = version.version("1.0")
	
	for i in range(len(keywords)):
		keyword = keywords[i]
		value = values[i]
		
		if keyword == "Comment":
			if new_project.get_comment():
				raise project_error("Only one comment allowed by project")
			if not isinstance(value, list):
				value = [value]
			comment = ""
			for line in value:
				if line.startswith("*") and line.endswith("*"):
					line = line[1:-1]
				if comment:
					comment += "\n" + line
				else:
					comment = line
			new_project.set_comment(comment)
		
		elif keyword == "Filter":
			try:
				filter = optical_filter.parse_filter(value, file_version, material_catalog)
			except (optical_filter.filter_error, materials.material_error), error:
				if file_version > version.version(release.VERSION):
					raise project_error("%s\n\nThe project file was created with a newer version of OpenFilters, which may explain this error" % error)
				else:
					raise
			new_project.add_filter(filter)
		
		elif keyword == "Target":
			try:
				target = targets.parse_target(value, file_version)
			except targets.target_error, error:
				if file_version > version.version(release.VERSION):
					raise project_error("%s\n\nThis error may be due to the fact that the project file was created with a newer version of OpenFilters" % error)
				else:
					raise
			new_project.add_target(target)
		
		elif keyword == "Version":
			raise project_error("Only one version is allowed on the first line of the project file")
		
		else:
			raise project_error("Unknown keyword %s while reading project" % keyword)
	
	new_project.set_modified(False)
	
	return new_project



########################################################################
#                                                                      #
# read_project                                                         #
#                                                                      #
########################################################################
def read_project(filename, material_catalog = None):
	"""Read a project file
	
	This function takes 1 or 2 input arguments:
	  filename          the name of the project file, including the
	                    directory;
	  material_catalog  (optional) the material catalog to use with this
		                  project;
	and returns a single output argument:
	  project           the project.
	
	If an error occurs during the reading of the file, a parsing error,
  is raised."""
	
	try:
		file = open(filename)
	except IOError:
		raise project_error("This file does not exist")
	
	lines = file.readlines()
	
	file.close()
	
	new_project = parse_project(lines, material_catalog)
	
	return new_project



########################################################################
#                                                                      #
# write_project                                                        #
#                                                                      #
########################################################################
def write_project(project, filename):
	"""Write a project file
	
	This function takes a two input argument:
	  filename      the name of the file in which to save, including the
	                directory;
	  project       the project to save."""
	
	temporary_file = tempfile.NamedTemporaryFile(mode="w", suffix=".ofp", prefix="", dir=os.path.dirname(filename), delete=False)
	temporary_file_name = temporary_file.name
	
	temporary_file.write("Version: %s\n" % release.VERSION)
	
	temporary_file.write("Comment:\n")
	for line in project.get_comment().splitlines():
		temporary_file.write("\t*%s*\n" % line)
	temporary_file.write("End\n")
	
	for filter in project.get_filters():
		temporary_file.write("Filter:\n")
		optical_filter.write_filter(filter, temporary_file, "\t")
		temporary_file.write("End\n")
	
	for target in project.get_targets():
		temporary_file.write("Target:\n")
		targets.write_target(target, temporary_file, "\t")
		temporary_file.write("End\n")
	
	temporary_file.close()
	
	try:
		os.remove(filename)
	except OSError, WindowsError:
		pass
	
	os.rename(temporary_file_name, filename)
	
	project.set_modified(False)
