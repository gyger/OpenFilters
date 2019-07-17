# Filters.py
# 
# Main routine for OpenFilters.
# 
# Copyright (c) 2000,2001,2003-2007,2015 Stephane Larouche.
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

import config
import localize
import user_config

import GUI



########################################################################
#                                                                      #
# run                                                                  #
#                                                                      #
########################################################################
def run(interface):
	"""Start OpenFilters with the appropriate interface.
	
	This function takes a single argument:
	  interface       the interface to run, the only choice at the moment
	                  is "GUI".
	
	If the GUI interface is selected, a GUI is started."""
	
	# Localize the software.
	localize.localize()
	
	if interface == "GUI":
		app = GUI.Filters_GUI(0)
		app.MainLoop()



if __name__ == "__main__":
	
	# Allow setting of the user material directory through a command-line
	# argument. This way allows a workaroud for people on OSs where the
	# directory chooser crashes.
	
	try:
		import argparse
	except ImportError:
		pass
	else:
		def directory_type(directory):
			directory = os.path.abspath(directory)
			if not os.path.isdir(directory):
				raise argparse.ArgumentTypeError("%s is not a directory" % directory)
			if not os.access(directory, os.R_OK):
				raise argparse.ArgumentTypeError("%s is not readable" % directory)
			return directory
		parser = argparse.ArgumentParser()
		parser.add_argument("-u", "--user_material_directory", metavar='DIRECTORY', help = "change the user material directory", type = directory_type)
		args = parser.parse_args()
		
		if args.user_material_directory:
			my_user_config = user_config.get_user_config()
			if not my_user_config.has_section("Directories"):
				my_user_config.add_section("Directories")
			my_user_config.set("Directories", "usermaterialdirectory", args.user_material_directory)
	
	
	# Run the interface selected in the configuration file.
	run(config.INTERFACE)
