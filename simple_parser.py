# simple_parser.py
# 
# A simple parser for the various files of OpenFilters.
#
# Copyright (c) 2004-2007 Stephane Larouche.
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
# parsing_error                                                        #
#                                                                      #
########################################################################
class parsing_error(Exception):
	"""Exception class for parsing errors"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Parsing error: %s." % self.value
		else:
			return "Parsing error."
	
	def get_value(self):
		return self.value



########################################################################
#                                                                      #
# parse                                                                #
#                                                                      #
########################################################################
def parse(lines):
	"""Parse lines written in a simple format
	
	This function takes a single argument:
	  lines                a list of lines to parse.
	and it returns two lists containing the names of the properties and
	their values.
	
	This funtion parses lines written in a format where each line contains
	the name of a property, a colon, and the value of the property. More
	complex properties can be splitted on multiple line; in that case a
	line contains the name of the property and ends with a colon, the
	value of the property is written on multiple lines, and the end of
	the property in indicated by a line containing only "end".
	
	No attempt is made to convert the value of the properties; it is left
	to the calling function to interpret the properties and they are
	returned as strings."""
	
	# Remove leading and trailing spaces, tabs, returns and line feeds.
	for i in range(len(lines)):
		lines[i] = lines[i].strip()
	
	# Do a first separation of the elements of the file. If a line ends
	# with ":", look for the end statement.
	keywords = []
	values = []
	while lines:
		line = lines.pop(0)
		if line:
			if line.count(":") == 1 and line.endswith(":"):
				keyword = line[0:-1].strip()
				value = []
				level = 1
				while lines:
					line = lines.pop(0)
					if line and line.count(":") == 1 and line.endswith(":"):
						level += 1
					elif line.upper() == "END":
						level -= 1
						if level == 0:
							break
					value.append(line)
				else:
					raise parsing_error("End of file reached inside a multiline property (%s)" % keyword)
				keywords.append(keyword)
				values.append(value)
			else:
				# Seperate around the first colon.
				elements = line.split(":", 1)
				if len(elements) != 2:
					raise parsing_error("Line does not contain property (%s)" % line)
				keywords.append(elements[0].strip())
				values.append(elements[1].strip())
	
	return keywords, values



########################################################################
#                                                                      #
# parse_file                                                           #
#                                                                      #
########################################################################
def parse_file(infile):
	"""Parse simple files
	
	Read a file and parse it using the parse function.
	
	This function takes a single input argument:
	  infile               the file to parse."""
	
	lines = infile.readlines()
	keywords, values = parse(lines)
	
	return keywords, values
