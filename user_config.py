# user_config.py
# 
# Manage, read, and write user configurations.
#
# Copyright (c) 2012,2015 Stephane Larouche.
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



import sys
import os
import ConfigParser



# Locate the position of the application data directory depending on
# the operating system.

APPLICATION_NAME = "OpenFilters"

if sys.platform == "win32":
	user_config_directory = os.path.join(os.environ["APPDATA"], APPLICATION_NAME)
elif sys.platform == "darwin":
	user_config_directory = os.path.expanduser(os.path.join("~", "Library", "Application Support", APPLICATION_NAME))
else:
	try:
		user_config_directory = os.path.join(os.environ["XDG_CONFIG_HOME"], "." + APPLICATION_NAME.lower())
	except KeyError:
		user_config_directory = os.path.expanduser(os.path.join("~", "." + APPLICATION_NAME.lower()))


# If the configuration directory does not exists, try to create one.

if os.path.exists(user_config_directory):
	if not os.path.isdir(user_config_directory):
		user_config_directory = ""
else:
	try:
		os.mkdir(user_config_directory)
	except OSError:
		user_config_directory = ""

if user_config_directory:
	user_config_filename = os.path.join(user_config_directory, "OpenFilters.cfg")
else:
	user_config_filename = ""


# Create a config object and try read the user config file.

user_config = ConfigParser.RawConfigParser()

if user_config_filename:
	try:
		user_config.read(user_config_filename)
	except ConfigParser.ParsingError:
		pass


########################################################################
#                                                                      #
# get_user_config                                                      #
#                                                                      #
########################################################################
def get_user_config():
	"""Get the user configuration parser object
	
	This function simply returns the user configuration object"""
	
	return user_config


########################################################################
#                                                                      #
# save_user_config                                                     #
#                                                                      #
########################################################################
def save_user_config():
	"""Save the user configuration parser object in the configuration file
	
	This function saves the current configuration in the configuration
	file."""
	
	if user_config_filename:
		try:
			with open(user_config_filename, "w") as user_config_file:
				user_config.write(user_config_file)
		except IOError:
			pass
