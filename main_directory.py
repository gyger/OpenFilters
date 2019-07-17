# main_directory.py
# 
# Get the main directory of optical filters with a hack in the case
# the software is compiled with py2exe or py2app. This file is similar
# to the script proposed by Thomas Heller (http://www.py2exe.org/
# index.cgi/HowToDetermineIfRunningFromExe)
# 
# Copyright (c) 2005,2007,2014 Stephane Larouche
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



import os, sys
import platform



########################################################################
#                                                                      #
# main_is_frozen                                                       #
#                                                                      #
########################################################################
def main_is_frozen():
	"""Determine if the software runs from a py2exe compiled executable"""
	
	return hasattr(sys, "frozen")



########################################################################
#                                                                      #
# get_main_directory                                                   #
#                                                                      #
########################################################################
def get_main_directory():
	"""Get the directory from where the software is runned
	
	This function returns the directory where the software is located,
	whether the software is interperted using Python or running from an
	executable compiled with py2exe. In the case of an executable, it
	returns the directory where this executable is located. In the case
	of interpretation, it returns the directory where this file is
	located; this way, it is possible to call OpenFilters from another
	directory and still have its path."""
	
	
	if main_is_frozen():
		system = platform.system()
		if system == "Windows":
			pathname = os.path.dirname(sys.executable)
		elif system == "Darwin":
			pathname = os.environ["RESOURCEPATH"]
		else:
			raise ValueError("Unknown operating system.")
	
	else:
		pathname = os.path.dirname(__file__)
	
	return os.path.abspath(pathname)
