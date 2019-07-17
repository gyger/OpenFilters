# tests.py
# 
# Test some functionnalities provided by OpenFilters. You must provide
# the list of tests to execute. If no argument is provided, all the
# tests are executed.
#
# Copyright (c) 2007,2009,2013,2015 Stephane Larouche.
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


print ""


# Get the list of tests to execute. If no test is provided, execute all tests.
tests = sys.argv[1:]
if tests == []:
	tests = ["color", "units"]


# Test the color conversion.
if "color" in tests:
	tests.remove("color")
	
	print ""
	print "========== color tests =========="
	print ""

	import color
	import random
	import math
	
	# Test all possible color conversions.
	
	observer = color.get_observer("CIE-1931-1NM")
	illuminant = color.get_illuminant("CIE-D65-1NM")
	
	XYZ_n = color.white_point(observer, illuminant)
	XYZ = [100.0*random.random(), 100.0*random.random(), 100.0*random.random()]
	
	color_spaces = [color.XYZ, color.xyY, color.Luv, color.Lab, color.LChuv, color.LChab]
	color_space_names = {color.XYZ: "XYZ",
	                     color.xyY: "xyY",
	                     color.Luv: "Luv",
	                     color.Lab: "Lab",
	                     color.LChuv: "LChuv",
	                     color.LChab: "LChab"}
	colors = {color.XYZ: XYZ,
	          color.xyY: color.XYZ_to_xyY(XYZ),
	          color.Luv: color.XYZ_to_Luv(XYZ, XYZ_n),
	          color.Lab: color.XYZ_to_Lab(XYZ, XYZ_n),
	          color.LChuv: color.Luv_to_LChuv(color.XYZ_to_Luv(XYZ, XYZ_n)),
	          color.LChab: color.Lab_to_LChab(color.XYZ_to_Lab(XYZ, XYZ_n))}
	
	for color_space_1 in color_spaces:
		for color_space_2 in color_spaces:
			new_color = color.change_color_space(color_space_1, color_space_2, colors[color_space_1], XYZ_n)
			old_color_inv = color.change_color_space(color_space_2, color_space_1, new_color, XYZ_n)
			color_diff = math.sqrt( (new_color[0]-colors[color_space_2][0])**2
			                       +(new_color[1]-colors[color_space_2][1])**2
			                       +(new_color[2]-colors[color_space_2][2])**2)
			if color_diff > 10e-8:
				result = "An error occured"
			else:
				result = "OK"
			print "%s -> %s -> %s: %s" % (color_space_names[color_space_1], color_space_names[color_space_2], color_space_names[color_space_1], result)
	
	print ""
	
	# XYZ -> RGB and RGB -> XYZ
	RGB, error = color.XYZ_to_RGB(XYZ)
	XYZ_inv = color.RGB_to_XYZ(RGB)
	if error: print "This color cannot be represented in RGB, expect an error."
	print "XYZ -> RGB: [%.3f, %.3f, %.3f] -> [%.3f, %.3f, %.3f]" % (XYZ[0], XYZ[1], XYZ[2], RGB[0], RGB[1], RGB[2])
	print "RGB -> XYZ: [%.3f, %.3f, %.3f] -> [%.3f, %.3f, %.3f]" % (RGB[0], RGB[1], RGB[2], XYZ_inv[0], XYZ_inv[1], XYZ_inv[2])
	
	print ""
	
	
	# Test color difference calculations according to the examples found in
	#   M. R. Luo, G. Cui, and B. Rigg, "The Development of the CIE 2000
	#   Colour-Difference Formula: CIEDE2000", Color Research and
	#   Application, Volume 26, Number 5, October 2001, pp. 340-350.
	
	print "Testing CIELABDE2000 implementation"
	
	pairs = [[[19.4100,   28.4100,   11.5766], [19.5525,   28.6400,   10.5791  ], 1.2644],
	         [[22.4800,   31.6000,   38.4800], [22.5833,   31.3700,   36.7901  ], 1.2630],
	         [[28.9950,   29.5800,   35.7500], [28.7704,   29.7400,   35.6045  ], 1.8731],
	         [[ 4.1400,    8.5400,    8.0300], [ 4.4129,    8.5100,    8.6453  ], 1.8645],
	         [[ 4.9600,    3.7200,   19.5900], [ 4.6651,    3.8100,   17.7848  ], 2.0373],
	         [[15.6000,    9.2500,    5.0200], [15.9148,    9.1500,    4.3872  ], 1.4146],
	         [[73.0000,   78.0500,   81.8000], [73.9351,   78.8200,   84.5156  ], 1.4440],
	         [[73.9950,   78.3200,   85.3060], [69.1762,   73.4000,   79.7130  ], 1.5381],
	         [[ 0.7040,    0.7500,    0.9720], [ 0.613873,  0.6500,    0.851025], 0.6378],
	         [[ 0.2200,    0.2300,    0.3250], [ 0.093262,  0.1000,    0.145292], 0.9082]]
	XYZ_n = [94.811, 100.000, 107.304]
	for i, pair in enumerate(pairs):
		Lab_1 = color.XYZ_to_Lab(pair[0], XYZ_n)
		Lab_2 = color.XYZ_to_Lab(pair[1], XYZ_n)
		Delta_E_tabulated = pair[2]
		Delta_E_calculated = color.Delta_E_2000(Lab_1, Lab_2)
		diff = abs(Delta_E_calculated-Delta_E_tabulated)
		if diff < 1e-3: result = "OK"
		else: result = "Error (got %.4f instead of %.4f)" % (Delta_E_calculated, Delta_E_tabulated)
		print "Pair %i: %s" % (i+1, result)
	

# Test the unit conversion.
if "units" in tests:
	tests.remove("units")
	
	print ""
	print "========== units tests =========="
	print ""
	
	import units
	
	for unit in units.WAVELENGTH_UNITS:
		converted = units.CONVERT_FROM_METERS_TO_UNITS[unit](500e-9)
		converted_back = units.CONVERT_FROM_UNITS_TO_METERS[unit](converted)
		print "500 nm =", converted, units.ABBREVIATIONS[unit], "=", converted_back, "m"


# Verify that all tests were executed
if tests:
	print ""
	print "Unknown or duplicate tests were ignored."
	print ""
