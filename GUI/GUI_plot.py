# GUI_plot.py
# 
# This file implement classes to draw plots in a wxPython application.
# To draw a plot, you must first create an instance of the plot class,
# which is derived for the wxWindow class. Then, you need to create one
# or many instances of the various curve classes, and add them to the
# plot.
#
# Copyright (c) 2001-2010,2012,2013,2015 Stephane Larouche.
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



# REMOVE when Python 3.0 will be out.
from __future__ import division

import sys
import os.path
import math
import array

import wx
from wx.lib.dialogs import ScrolledMessageDialog

from moremath import limits

import GUI_validators


# Default behaviour is to use buffered drawing.
use_buffered_drawing = True

TOP = 0
BOTTOM = 1
LEFT = 2
RIGHT = 3

APPEND = 1
REPLACE = 2

LINEAR = 0
LOG = 1

AUTOMATIC = None

NO_FAST_DRAWING = 0
HALF_SCREEN = 1
FULL_SCREEN = 2
NO_REDRAW = 3

FIGURE_WILDCARD = "Windows bitmap file (*.bmp)|*.bmp|"\
                  "JPEG file (*.jpg)|*.jpg|"\
                  "PNG file (*.png)|*.png|"\
                  "TIFF file (*.tif)|*.tif"
BITMAP_TYPES = {".bmp": wx.BITMAP_TYPE_BMP,
                ".jpg": wx.BITMAP_TYPE_JPEG,
                ".png": wx.BITMAP_TYPE_PNG,
                ".tif": wx.BITMAP_TYPE_TIF}


# The colours used in the plots.		
colour_database = ["BLUE",
                   "RED",
                   "GREEN",
                   "ORANGE",
                   "YELLOW",
                   "PURPLE",
                   "SEA GREEN",
                   "GOLDENROD",
                   "NAVY",
                   "MAGENTA",
                   "DARK GREEN",
                   "GOLD",
                   "SLATE BLUE",
                   "PINK",
                   "CYAN",
                   "CORAL"
                   "VIOLET",
                   "CORNFLOWER BLUE",
                   "BLACK",
                   "GREY"]

# Constants related to the separation of the ticks.
absolute_max_nb_of_ticks = 15
multiples = (1.0, 2.0, 2.5, 5.0, 10.0)
divisors = (1.0, 2.0, 4.0, 5.0, 10.0)
nb_multiples = len(multiples)
nb_divisors = len(divisors)

# The maximum marker size.
max_marker_size = 100

# The canvas size if limited to C longs. To allow markers, it is
# reduced by the maximum marker size.
maxint = sys.maxint - max_marker_size
minint = -maxint - 1 + max_marker_size

# Zero and negative value cannot be handled correctly in log scale. The
# minimal value is the smallest possible positive value. To draw a line
# falling outside of the figure, the log value is replaced by the log
# of the smallest representable number.
log_min_float = math.log10(limits.min)



########################################################################
#                                                                      #
# remove_curve_event                                                   #
#                                                                      #
########################################################################

remove_curve_event_type = wx.NewEventType()

EVT_remove_curve = wx.PyEventBinder(remove_curve_event_type, 1)

class remove_curve_event(wx.PyCommandEvent):
	
	eventType = remove_curve_event_type
	
	def __init__(self, windowID, nb):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		
		self.nb = nb
	
	def get_nb(self):
		return self.nb



########################################################################
#                                                                      #
# limited_int                                                          #
#                                                                      #
########################################################################
def limited_int(x):
	"""Limit the value of integers.
	
	Return the value of the input argument converted to an integer and
	limited to C longs."""
	
	return min(max(int(round(x)), minint), maxint)



########################################################################
#                                                                      #
# limited_log10                                                        #
#                                                                      #
########################################################################
def limited_log10(x):
	"""Calculate the logarithm in base 10 of a number
	
	This method takes a single input argument:
	  x                    a number;
	and returns its logarithm in base 10. If the argument is null or
	negative, it returns the logarithm of the smallest representable
	float number. This is intended to be used for logarithmic scaling of
	plots."""
	
	if x <= 0.0:
		return log_min_float
	else:
		return math.log10(x)



########################################################################
#                                                                      #
# set_use_buffered_drawing                                             #
#                                                                      #
########################################################################
def set_use_buffered_drawing(new_setting):
	"""Set buffered drawing mode
	
	This function sets a general setting determining if plots will use
	buffered drawing. It affects all plots created AFTER the function
	has been called. This function takes a single input argument:
	  new_setting          a boolean indicating to use buffered drawing
	                       or not
	and it returns a boolean indicating if the setting was changed
	(True), or if it already had the value of the new setting (False)."""
	
	global use_buffered_drawing
	
	# If the new setting is identical to the old one, don't change it
	# and return False.
	if new_setting == use_buffered_drawing:
		return False
	
	# If the new setting is different change it and return True.
	else:
		use_buffered_drawing = new_setting
		return True



########################################################################
#                                                                      #
# get_use_buffered_drawing                                             #
#                                                                      #
########################################################################
def get_use_buffered_drawing():
	"""Get buffered drawing mode
	
	This function returns a boolean indicating if buffered drawing is
	used or not."""
	
	return use_buffered_drawing



########################################################################
#                                                                      #
# plot_curve_style                                                     #
#                                                                      #
########################################################################
class plot_curve_style(object):
	"""A class to describe the style of a curve"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, colour = "", width = 1, marker = "", marker_size = 6):
		"""Initialize the style
		
		This method takes 4 optional arguments:
		  colour             (optional) a string defining the colour of the
		                     curve, this string must be a colour recognized
		                     by wxPython, if omitted, the colour selection
		                     will be handled by the plot in order to avoid
		                     redundancy;
		  width              (optional) the width of pen used to draw the
		                     curve, the default value is 1;
		  marker             (optional) a character describing the marker
		                     used in the drawing of the curve, "" for no
		                     symbol, "+" or "x" for crosses, "^" or "v"
		                     for half crosses, or "o" for circles, by
		                     default no marker is used;
		  marker_size        (optional) the size of the marker, by default
		                     the size is 6."""
		
		if marker_size > max_marker_size:
			raise ValueError("Marker size larger than maximum value")
		
		self.colour = colour
		self.width = width
		self.marker = marker
		self.marker_size = marker_size
	
	
	######################################################################
	#                                                                    #
	# get_colours                                                        #
	#                                                                    #
	######################################################################
	def get_colours(self):
		"""Get the colour of the style
		
		This method returns the colour used in the style inside a list. It
		is used by the plot class when making a list of all used colours
		to automatically choose the color of a curve. If no colour is
		assigned to the curve, it returns an empty list."""
		
		if self.colour == "":
			return []
		
		return [self.colour]



########################################################################
#                                                                      #
# plot_curve_segmented_style                                           #
#                                                                      #
########################################################################
class plot_curve_segmented_style(object):
	"""A class to describe the style of a segmented curve"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, colour_1 = "", colour_2 = "", width = 1, marker = "", marker_size = 6):
		"""Initialize the style
		
		This method takes 5 optional arguments:
		  colour_1, colour_2 (optional) strings defining the colours of the
		                     curve, these strings must be colours
		                     recognized by wxPython, if omitted, the
		                     colour selection will be handled by the plot
		                     in order to avoid redundancy;
		  width              (optional) the width of pen used to draw the
		                     curve, the default value is 1;
		  marker             (optional) a character describing the marker
		                     used in the drawing of the curve, "" for no
		                     symbol, "+" or "x" for crosses, "^" or "v"
		                     for half crosses, or "o" for circles, by
		                     default no marker is used;
		  marker_size        (optional) the size of the marker, by default
		                     the value is 6."""
		
		if marker_size > max_marker_size:
			raise ValueError("Marker size larger than maximum value")
		
		self.colour_1 = colour_1
		self.colour_2 = colour_2
		self.width = width
		self.marker = marker
		self.marker_size = marker_size
	
	
	######################################################################
	#                                                                    #
	# get_colours                                                        #
	#                                                                    #
	######################################################################
	def get_colours(self):
		"""Get the colours of the style
		
		This method returns the colours used in the style inside a list. It
		is used by the plot class when making a list of all used colours
		to automatically choose the color of a curve. If no colour is
		assigned to the curve, it returns an empty list."""
		
		colours = []
		
		if self.colour_1 != "":
			colours.append(self.colour_1)
		if self.colour_2 != "":
			colours.append(self.colour_2)
		
		return colours



########################################################################
#                                                                      #
# plot_curve                                                           #
#                                                                      #
########################################################################
class plot_curve(object):
	"""A class to handle the data of a single curve and plot it"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, x = [], y = [], size = -1, name = "", policy = APPEND, style = None):
		"""Initialize the curve
		
		This method takes 6 optional arguments:
		  x, y               (optional) x and y vectors of the same length
		                     describing the curve, default values are empty
		                     lists;
		  size               (optional) number of points in the curve, by
		                     default the value is -1 and the number of
		                     points is adjusted to fit the x and y vectors;
		  name               (optional) a string giving the name of the
		                     curve that is used for the legend and similar
		                     stuff, by default the curves does not have a
		                     name;
		  policy             (optional) APPEND or REPLACE (see below), by
		                     default the policy is to append;
		  style              (optional) an instance of the
		                     plot_curve_style class describing the style
		                     of the curve, by default the default style
		                     is choosen.
		
		This class can be used to create static curve. In that case
		simply initialize it with the appropriate x and y vectors. It can
		also be used to create dynamic curve on which data can be appended.
		It that case, it may be useful to reserve memory for the points
		that will be added to avoid constant modifications to the x and y
		vector representation in the memory. When points are added to the
		curve such that it becomes longer than the reserved size, the
		policy is used to determine what to do. If the policy is to APPEND,
		the x and y vectors are expanded to be 10% longer than the required
		size (hoping it will not be necessary to do the same thing the next
		time points are added). If the policy is to REPLACE, the points at
		the begining of the x and y vectors are replaced by the new points.
		This can be used to limit the memory used by a curve on a system
		plotting some values in real time."""
		
		self.name = name
		
		if style:
			self.style = style
		else:
			self.style = plot_curve_style()
		
		# When appending points, so that the graph would become bigger
		# than size, two policies are possible, APPEND, in which memory
		# is added to fit the new points, or REPLACE, where old points are
		# replaced beginning at the beginning of the array. The REPLACE
		# policy requires a size and/or values of x and y.
		self.append_points_policy = policy
		
		# The starting point or the curve in the array. Only useful in
		# the REPLACE policy.
		self.starting_point = 0
		
		# Create array self.x and self.y according to the requested size.
		# If values of x and y are given, initialize self.x and self.y.
		if size == -1 and x == []:
			self.x = array.array("d")
			self.y = array.array("d")
			self.nb_points = 0
			self.size = 0
		elif size != -1 and x == []:
			self.x = array.array("d", [0.0]*size)
			self.y = array.array("d", [0.0]*size)
			self.nb_points = 0
			self.size = size
		elif size == -1 and x != []:
			self.x = x
			self.y = y
			self.nb_points = len(self.x)
			self.size = self.nb_points
		else:
			if size >= len(x):
				self.x = array.array("d", [0.0]*size)
				self.y = array.array("d", [0.0]*size)
				for i in range(len(x)):
					self.x[i] = x[i]
					self.y[i] = y[i]
				self.nb_points = len(x)
				self.size = size
			else:
				if self.append_points_policy == APPEND:
					self.x = x
					self.y = y
					self.nb_points = len(self.x)
					self.size = self.nb_points
				else:
					self.x = array.array("d", x[-1-size:-1])
					self.y = array.array("d", y[-1-size:-1])
					self.nb_points = size
					self.size = size
	
	
	######################################################################
	#                                                                    #
	# set_name                                                           #
	#                                                                    #
	######################################################################
	def set_name(self, name):
		"""Set or replace the name of the curve
		
		This method takes a single argument:
		  name               the name of the curve."""
		
		self.name = name
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the curve
		
		This method returns the name of the curve."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# set_style                                                          #
	#                                                                    #
	######################################################################
	def set_style(self, style):
		"""Set or replace the style of the curve
		
		This method takes a single argument:
		  style              the style of the curve."""
		
		self.style = style
	
	
	######################################################################
	#                                                                    #
	# get_style                                                          #
	#                                                                    #
	######################################################################
	def get_style(self):
		"""Get the style of the curve
		
		This method returns the style of the curve."""
		
		return self.style
	
	
	######################################################################
	#                                                                    #
	# set_colour_from_usage                                              #
	#                                                                    #
	######################################################################
	def set_colour_from_usage(self, colour_database, colour_usage):
		"""Set the colour of the curve automatically while reducing
		redundancy
		
		This method takes 2 arguments:
		  colour_database    a list of colour names;
		  colour_usage       a list of the number of times the colour in
		                     the database are used in the plot containing
		                     the curve.
		
		This method is automatically called by the plot method when
		appropriate. You don't need to call it yourself."""
		
		least_used_colour = colour_database[colour_usage.index(min(colour_usage))]
		
		self.style.colour = least_used_colour
	
	
	######################################################################
	#                                                                    #
	# bounding_box                                                       #
	#                                                                    #
	######################################################################
	def bounding_box(self):
		"""Get the bounding box of the curve
		
		This method returns 4 arguments:
		  x_min, x_max       the range of values in the x vector;
		  y_min, y_max       the range of values in the y vector.
		
		If the vector is empty, it returns Nones."""
		
		if self.nb_points:
			x_min = min(self.x)
			x_max = max(self.x)
			y_min = min(self.y)
			y_max = max(self.y)
		else:
			x_min = None
			x_max = None
			y_min = None
			y_max = None
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# draw_legend                                                        #
	#                                                                    #
	######################################################################
	def draw_legend(self, DC, x_left, y_bottom, x_right, y_top):
		"""Draw the legend for the curve
		
		This method takes 5 arguments:
		  DC                 the device context on which to draw the
		                     legend;
		  x_left, y_button   the starting point of the legend line;
		  x_right, y_top     the ending point of the legend line.
		
		It draws a line and eventually a marker according to the curve
		style."""
		
		DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour), self.style.width))
		DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour), wx.TRANSPARENT))
		
		if self.style.width > 0:
			DC.DrawLine(x_left, y_bottom, x_right, y_top)
		
		x = limited_int(0.5*(x_left+x_right))
		y = limited_int(0.5*(y_bottom+y_top))
		half_size = limited_int(0.5*self.style.marker_size)
		
		if self.style.marker == "+":
			DC.DrawLine(x-half_size, y,           x+half_size+1, y            )
			DC.DrawLine(x,           y-half_size, x,             y+half_size+1)
		elif self.style.marker == "x":
			DC.DrawLine(x-half_size, y-half_size, x+half_size+1, y+half_size+1)
			DC.DrawLine(x-half_size, y+half_size, x+half_size+1, y-half_size-1)
		elif self.style.marker == "^":
			DC.DrawLine(x-half_size, y+half_size, x,             y            )
			DC.DrawLine(x,           y,           x+half_size+1, y+half_size+1)
		elif self.style.marker == "v":
			DC.DrawLine(x-half_size, y-half_size, x,           y              )
			DC.DrawLine(x,           y,           x+half_size+1, y-half_size-1)
		elif self.style.marker == "o":
			DC.DrawCircle(x, y, half_size)
	
	
	######################################################################
	#                                                                    #
	# draw_line                                                          #
	#                                                                    #
	######################################################################
	def draw_line(self, DC, shift_x, scale_x, shift_y, scale_y, nb_points = 0, min_x_value = None, axis_x = LINEAR, axis_y = LINEAR):
		"""Draw the curve
		
		This method takes 5 to 9 arguments:
		  DC                 the device context on which to draw the curve;
		  shift_x            position of the x origin on the device
		                     context;
		  scale_x            scaling factor of the x axis;
		  shift_y            position of the y origin on the device
		                     context;
		  scale_y            scaling factor of the x axis;
		  nb_points          (optional) the number of points to draw, if
		                     the value is 0 (default), all points are
		                     drawn (see below for details);
		  min_x_value        (optional) the value of x on the left of the
		                     figure (see below for details);
		  axis_x             (optional) LINEAR (default) or LOG;
		  axis_y             (optional) LINEAR (default) or LOG.
		
		Both nb_points and min_x_value can be used to limit redrawing
		of the figure. If a few points were added to the curve, it is
		possible to draw only the last nb_points of the curve. It is also
		possible to eliminate for the drawing all the points for which x
		is smaller than min_x_value. This last case works only when the x
		value are in increasing order and is targeted at applications where
		a value is acquired in real time, plotted as the function of the
		time, and you only want to show a recently acquired part of the
		curve."""
		
		DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour), self.style.width))
		DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour), wx.TRANSPARENT))
		
		# Calculate half the marker size.
		half_size = limited_int(0.5*self.style.marker_size)
		
		# Find where to start and where to stop.
		if self.nb_points > 0:
			if nb_points == 0:
				# Select all points that are defined.
				first_point = self.starting_point
				last_point = first_point + self.nb_points
				
				# If a minimal x value is defined, search for the last point
				# where x is smaller than or equal to the minimum value. We
				# might keep one exterior point in order to draw the line from
				# that point to the interior point.
				if min_x_value is not None:
					for first_point in range(first_point, last_point-1):
						if self.x[(first_point+1) % self.size] > min_x_value:
							break
			# If nb_points is non-zero, only the last nb_points should be
			# drawn.
			else:
				first_point = self.starting_point+self.nb_points-nb_points
				last_point = self.starting_point+self.nb_points
			
			# If the first point is not the starting point, the previous
			# point is considered to do the line. Otherwise, there is no
			# previous point and the previous point is initialized to the
			# first point to avoid crashes.
			if first_point == self.starting_point:
				x = self.x[first_point % self.size]
				y = self.y[first_point % self.size]
				if axis_x == LOG:
					x = limited_log10(x)
				if axis_y == LOG:
					y = limited_log10(y)
				x_minus_1 = limited_int(scale_x*(x-shift_x))
				y_minus_1 = limited_int(scale_y*(y-shift_y))
			else:
				x = self.x[(first_point-1) % self.size]
				y = self.y[(first_point-1) % self.size]
				if axis_x == LOG:
					x = limited_log10(x)
				if axis_y == LOG:
					y = limited_log10(y)
				x_minus_1 = limited_int(scale_x*(x-shift_x))
				y_minus_1 = limited_int(scale_y*(y-shift_y))
			
			# The loop is executed from the first point in order to get the
			# mark for the first point.
			for i in range(first_point, last_point):
				x = self.x[i % self.size]
				y = self.y[i % self.size]
				if axis_x == LOG:
					x = limited_log10(x)
				if axis_y == LOG:
					y = limited_log10(y)
				x = limited_int(scale_x*(x-shift_x))
				y = limited_int(scale_y*(y-shift_y))
				if self.style.width > 0:
					DC.DrawLine(x_minus_1, y_minus_1, x, y)
				if self.style.marker == "+":
					DC.DrawLine(x-half_size, y,           x+half_size+1, y            )
					DC.DrawLine(x,           y-half_size, x,             y+half_size+1)
				elif self.style.marker == "x":
					DC.DrawLine(x-half_size, y-half_size, x+half_size+1, y+half_size+1)
					DC.DrawLine(x-half_size, y+half_size, x+half_size+1, y-half_size-1)
				elif self.style.marker == "^":
					DC.DrawLine(x-half_size, y+half_size, x,             y            )
					DC.DrawLine(x,           y,           x+half_size+1, y+half_size+1)
				elif self.style.marker == "v":
					DC.DrawLine(x-half_size, y-half_size, x,             y            )
					DC.DrawLine(x,           y,           x+half_size+1, y-half_size-1)
				elif self.style.marker == "o":
					DC.DrawCircle(x, y, half_size)
				x_minus_1 = x
				y_minus_1 = y
	
	
	######################################################################
	#                                                                    #
	# append_data                                                        #
	#                                                                    #
	######################################################################
	def append_data(self, x, y):
		"""Append data to the curve
		
		This method takes 2 arguments:
		  x, y               vectors of x and y values to add to the curve.
		
		Depending on the size of the curve and the policy. It is possible
		that the added points will replace existing points. If the number
		of added points is larger that the prescribed size and the policy
		is to REPLACE, only the last points will be kept."""
		
		nb_added_points = len(x)
		
		# If the size of the self.x and self.y arrays is not big enough
		# to fit all the new data and the policy is to APPEND new points,
		# self.x and self.y are expanded to fit all this new data. This
		# is a long process since the array has to be moved in the memory
		# space. Therefore, arrays are expanded to get a 10% free space
		# at the end after the addition of the data to minimize the number
		# of time this process has to be done.
		if self.append_points_policy == APPEND:
			needed_points = self.nb_points + nb_added_points
			
			if needed_points > self.size:
				new_size = int(math.ceil(1.10*needed_points))
				added_size = new_size-self.size
				self.x += array.array("d", range(added_size))
				self.y += array.array("d", range(added_size))
				
				self.size = new_size
		
		# Inserting the new points in the array.
		first_added_point = self.starting_point-self.size+self.nb_points
		for i in range(nb_added_points):
			self.x[(first_added_point+i) % self.size] = x[i]
			self.y[(first_added_point+i) % self.size] = y[i]
		
		self.nb_points = (self.nb_points + nb_added_points)
		
		if self.append_points_policy == REPLACE:
			if self.nb_points >= self.size:
				self.nb_points = self.size
				self.starting_point = (first_added_point + nb_added_points) % self.size
		
		# Calculate and return the bounding box of the new points.
		x_min = min(x)
		x_max = max(x)
		y_min = min(y)
		y_max = max(y)
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# replace_data                                                       #
	#                                                                    #
	######################################################################
	def replace_data(self, x, y):
		"""Replace the data of the curve
		
		This method takes 2 arguments:
		  x, y               vectors of x and y values to replace the
		                     present curve.
		
		If the policy is REPLACE and the number of points in x and y is
		larger than the size of the curve, only the last points will be
		kept."""
		
		nb_new_points = len(x)
		
		# If the size of the self.x and self.y arrays is not big enough
		# to fit all the new data and the policy is to APPEND new points,
		# self.x and self.y are expanded to fit all this new data. This
		# is a long process since the array has to be moved in the memory
		# space. Therefore, arrays are expanded to get a 10% free space
		# at the end after the addition of the data to minimize the number
		# of time this process has to be done.
		if self.append_points_policy == APPEND:
			
			if nb_new_points > self.size:
				new_size = int(math.ceil(1.10*nb_new_points))
				added_size = new_size-self.size
				self.x += array.array("d", range(added_size))
				self.y += array.array("d", range(added_size))
				
				self.size = new_size
		
		# Inserting the new points in the array.
		for i in range(nb_new_points):
			self.x[i % self.size] = x[i]
			self.y[i % self.size] = y[i]
		
		self.nb_points = nb_new_points
		
		if self.append_points_policy == REPLACE:
			if self.nb_points >= self.size:
				self.nb_points = self.size
				self.starting_point = (nb_new_points) % self.size
		
		# Calculate and return the bounding box of the new points.
		x_min = min(x)
		x_max = max(x)
		y_min = min(y)
		y_max = max(y)
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# get_x                                                              #
	#                                                                    #
	######################################################################
	def get_x(self):
		"""Get the x vector
		
		This method returns a copy of the x vector.
		
		The returned result is not directly the x vector kept internally.
		It is first reordered and allocated memory that is not used is
		removed."""
		
		first_point = self.starting_point-self.size
		last_point = first_point+self.nb_points
		if last_point == 0:
			return self.x[first_point:]
		elif last_point < 0:
			return self.x[first_point:last_point]
		else:
			return self.x[first_point:] + self.x[:last_point]
	
	
	######################################################################
	#                                                                    #
	# get_y                                                              #
	#                                                                    #
	######################################################################
	def get_y(self):
		"""Get the y vector
		
		This method returns a copy of the y vector.
		
		The returned result is not directly the y vector kept internally.
		It is first reordered and allocated memory that is not used is
		removed."""
		
		first_point = self.starting_point-self.size
		last_point = first_point+self.nb_points
		if last_point == 0:
			return self.y[first_point:]
		elif last_point < 0:
			return self.y[first_point:last_point]
		else:
			return self.y[first_point:] + self.y[:last_point]
	
	
	######################################################################
	#                                                                    #
	# get_data_as_text                                                   #
	#                                                                    #
	######################################################################
	def get_data_as_text(self):
		"""Get the curve as text
		
		This method returns a string with all the data in text format.
		Every line contains a point."""
		
		return "".join("%15s   %15s\n" % (self.x[i%self.size], self.y[i%self.size]) for i in range(self.starting_point, self.starting_point+self.nb_points))
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Reset the plot
		
		This method cancel all data in the curve, but doest not actually
		free the memory, which can be reused when appending points."""
		
		self.nb_points = 0
		self.starting_point = 0
	
	
	######################################################################
	#                                                                    #
	# get_context_menu                                                   #
	#                                                                    #
	######################################################################
	def get_context_menu(self, parent):
		"""Get the curve specific context menu
		
		This method takes one argument:
		  parent             the window that handles the menu events.
		It returns ("", None).
		
		Actually, this kind of curve does have a context menu."""
		
		return "", None
	
	
	######################################################################
	#                                                                    #
	# execute_menu_item                                                  #
	#                                                                    #
	######################################################################
	def execute_menu_item(self, item_ID):
		"""Execute one of the menu item of the context menu
		
		This method takes a single argument:
		  item_ID            the id of the item that was selected;
		and returns a boolean indicating if it is necessary to redraw the
		plot.
		
		Actually, since this kind of curve does not add items to the
		context menu, this method does not do anything and simply returns
		False."""
		
		return False



########################################################################
#                                                                      #
# plot_curve_segmented                                                 #
#                                                                      #
########################################################################
class plot_curve_segmented(object):
	"""A class to handle the data of a segmented curve and plot it
	
	A segmented curve consists of multiple segments which are plotted in
	two different colours alternatively."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, Xs , Ys , name = "", style = None):
		"""Initialize the curve
		
		This method takes 2 to 4 arguments:
		  Xs, Ys             lists of x and y vectors of the same lengths
		                     describing the segments of the curve;
		  name               (optional) a string giving the name of the
		                     curve that is used for the legend and similar
		                     stuff, by default the curves does not have a
		                     name;
		  style              (optional) an instance of the
		                     plot_curve_segmented_style class describing
		                     the style of the curve, by default the default
		                     style is choosen."""
		
		self.name = name
		
		if style:
			self.style = style
		else:
			self.style = plot_curve_segmented_style()
		
		self.Xs = Xs
		self.Ys = Ys
	
	
	######################################################################
	#                                                                    #
	# set_name                                                           #
	#                                                                    #
	######################################################################
	def set_name(self, name):
		"""Set or replace the name of the curve
		
		This method takes a single argument:
		  name               the name of the curve."""
		
		self.name = name
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the curve
		
		This method returns the name of the curve."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# set_style                                                          #
	#                                                                    #
	######################################################################
	def set_style(self, style):
		"""Set or replace the style of the curve
		
		This method takes a single argument:
		  style              the style of the curve."""
		
		self.style = style
	
	
	######################################################################
	#                                                                    #
	# get_style                                                          #
	#                                                                    #
	######################################################################
	def get_style(self):
		"""Get the style of the curve
		
		This method returns the style of the curve."""
		
		return self.style
	
	
	######################################################################
	#                                                                    #
	# set_colour_from_usage                                              #
	#                                                                    #
	######################################################################
	def set_colour_from_usage(self, colour_database, colour_usage):
		"""Set the colours of the curve automatically while reducing
		redundancy
		
		This method takes 2 arguments:
		  colour_database    a list of colour names;
		  colour_usage       a list of the number of times the colour in
		                     the database are used in the plot containing
		                     the curve.
		
		This method is automatically called by the plot method when
		appropriate. You don't need to call it yourself."""
		
		if colour_usage[0] > colour_usage[1]:
			least_used_colour_ID = 1
			second_least_used_colour_ID = 0
		else:
			least_used_colour_ID = 0
			second_least_used_colour_ID = 1
		
		for i in range(2, len(colour_usage)):
			if colour_usage[i] < colour_usage[least_used_colour_ID]:
				second_least_used_colour_ID = least_used_colour_ID
				least_used_colour_ID = i
			elif colour_usage[i] < colour_usage[second_least_used_colour_ID]:
				second_least_used_colour_ID = i
		
		least_used_colour = colour_database[least_used_colour_ID]
		second_least_used_colour = colour_database[second_least_used_colour_ID]
		
		self.style.colour_1 = least_used_colour
		self.style.colour_2 = second_least_used_colour
	
	
	######################################################################
	#                                                                    #
	# bounding_box                                                       #
	#                                                                    #
	######################################################################
	def bounding_box(self):
		"""Get the bounding box of the curve
		
		This method returns 4 arguments:
		  x_min, x_max       the range of values in the x vectors;
		  y_min, y_max       the range of values in the y vectors.
		
		If all the vectors are empty, it returns Nones."""
		
		x_min = None
		x_max = None
		y_min = None
		y_max = None
		
		for i in range(len(self.Xs)):
			if self.Xs[i]:
				x_min_i = min(self.Xs[i])
				x_max_i = max(self.Xs[i])
				y_min_i = min(self.Ys[i])
				y_max_i = max(self.Ys[i])
				
				if x_min is None:
					x_min = x_min_i
					x_max = x_max_i
					y_min = y_min_i
					y_max = y_max_i
				else:
					x_min = min(x_min, x_min_i)
					x_max = max(x_max, x_max_i)
					y_min = min(y_min, y_min_i)
					y_max = max(y_max, y_max_i)
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# draw_legend                                                        #
	#                                                                    #
	######################################################################
	def draw_legend(self, DC, x_left, y_bottom, x_right, y_top):
		"""Draw the legend for the curve
		
		This method takes 5 arguments:
		  DC                 the device context on which to draw the
		                     legend;
		  x_left, y_button   the starting point of the legend line;
		  x_right, y_top     the ending point of the legend line.
		
		It draws a line and eventually a marker according to the curve
		style."""
		
		x = limited_int(0.5*(x_left+x_right))
		y = limited_int(0.5*(y_bottom+y_top))
		half_size = limited_int(0.5*self.style.marker_size)
		
		DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour_1), self.style.width))
		DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour_1), wx.TRANSPARENT))
		
		DC.DrawLine(x_left, y_bottom, x, y)
		
		if self.style.marker == "+":
			DC.DrawLine(x-half_size, y,           x+half_size+1, y            )
			DC.DrawLine(x,           y-half_size, x,             y+half_size+1)
		elif self.style.marker == "x":
			DC.DrawLine(x-half_size, y-half_size, x+half_size+1, y+half_size+1)
			DC.DrawLine(x-half_size, y+half_size, x+half_size+1, y-half_size-1)
		elif self.style.marker == "^":
			DC.DrawLine(x-half_size, y+half_size, x,             y            )
			DC.DrawLine(x,           y,           x+half_size+1, y+half_size+1)
		elif self.style.marker == "v":
			DC.DrawLine(x-half_size, y-half_size, x,           y              )
			DC.DrawLine(x,           y,           x+half_size+1, y-half_size-1)
		elif self.style.marker == "o":
			DC.DrawCircle(x, y, half_size)
		
		DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour_2), self.style.width))
		DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour_2), wx.TRANSPARENT))
		
		DC.DrawLine(x, y, x_right, y_top)
	
	
	######################################################################
	#                                                                    #
	# draw_line                                                          #
	#                                                                    #
	######################################################################
	def draw_line(self, DC, shift_x, scale_x, shift_y, scale_y, nb_points = 0, min_x_value = None, axis_x = LINEAR, axis_y = LINEAR):
		"""Draw the curve
		
		This method takes 5 to 9 arguments:
		  DC                 the device context on which to draw the curve;
		  shift_x            position of the x origin on the device
		                     context;
		  scale_x            scaling factor of the x axis;
		  shift_y            position of the y origin on the device
		                     context;
		  scale_y            scaling factor of the x axis;
		  nb_points          (optional) the number of points to draw, if
		                     the value is 0 (default), all points are
		                     drawn (not used);
		  min_x_value        (optional) the value of x on the left of the
		                     figure (not used);
		  axis_x             (optional) LINEAR (default) or LOG;
		  axis_y             (optional) LINEAR (default) or LOG.
		
		The values of nb_points and min_x_value are ignored."""
		
		# Calculate half the marker size.
		half_size = limited_int(0.5*self.style.marker_size)
		
		for i in range(len(self.Xs)):
			if self.Xs[i]:
				if round(0.5*i) == 0.5*i:
					DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour_1), self.style.width))
					DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour_1), wx.TRANSPARENT))
				else:
					DC.SetPen(wx.Pen(wx.NamedColour(self.style.colour_2), self.style.width))
					DC.SetBrush(wx.Brush(wx.NamedColour(self.style.colour_2), wx.TRANSPARENT))
				
				if len(self.Xs[i]) > 0:
					
					# The first point.
					x = self.Xs[i][0]
					y = self.Ys[i][0]
					if axis_x == LOG:
						x = limited_log10(x)
					if axis_y == LOG:
						y = limited_log10(y)
					x_minus_1 = limited_int(scale_x*(x-shift_x))
					y_minus_1 = limited_int(scale_y*(y-shift_y))
					
					# The curve.
					for j in range(len(self.Xs[i])):
						x = self.Xs[i][j]
						y = self.Ys[i][j]
						if axis_x == LOG:
							x = limited_log10(x)
						if axis_y == LOG:
							y = limited_log10(y)
						x = limited_int(scale_x*(x-shift_x))
						y = limited_int(scale_y*(y-shift_y))
						DC.DrawLine(x_minus_1, y_minus_1, x, y)
						if self.style.marker == "+":
							DC.DrawLine(x-half_size, y,           x+half_size+1, y            )
							DC.DrawLine(x,           y-half_size, x,             y+half_size+1)
						elif self.style.marker == "x":
							DC.DrawLine(x-half_size, y-half_size, x+half_size+1, y+half_size+1)
							DC.DrawLine(x-half_size, y+half_size, x+half_size+1, y-half_size-1)
						elif self.style.marker == "^":
							DC.DrawLine(x-half_size, y+half_size, x,             y            )
							DC.DrawLine(x,           y,           x+half_size+1, y+half_size+1)
						elif self.style.marker == "v":
							DC.DrawLine(x-half_size, y-half_size, x,             y            )
							DC.DrawLine(x,           y,           x+half_size+1, y-half_size-1)
						elif self.style.marker == "o":
							DC.DrawCircle(x, y, half_size)
						x_minus_1 = x
						y_minus_1 = y
	
	
	######################################################################
	#                                                                    #
	# get_x                                                              #
	#                                                                    #
	######################################################################
	def get_x(self):
		"""Get the x vectors
		
		This method returns the list of x vectors."""
		
		return self.Xs
	
	
	######################################################################
	#                                                                    #
	# get_y                                                              #
	#                                                                    #
	######################################################################
	def get_y(self):
		"""Get the x vectors
		
		This method returns the list of y vectors."""
		
		return self.Ys
	
	
	######################################################################
	#                                                                    #
	# get_data_as_text                                                   #
	#                                                                    #
	######################################################################
	def get_data_as_text(self):
		"""Get the curve as text
		
		This method returns a string with all the data in text format.
		Every line contains a point and the number of the curve segment."""
		
		return "".join("%15s   %15s   %3s\n" % (self.Xs[i_curve][i_point], self.Ys[i_curve][i_point], i_curve) for i_curve in range(len(self.Xs)) for i_point in range(len(self.Xs[i_curve])))
	
	
	######################################################################
	#                                                                    #
	# get_context_menu                                                   #
	#                                                                    #
	######################################################################
	def get_context_menu(self, parent):
		"""Get the curve specific context menu
		
		This method takes one argument:
		  parent             the window that handles the menu events.
		It returns ("", None).
		
		Actually, this kind of curve does have a context menu."""
		
		return "", None
	
	
	######################################################################
	#                                                                    #
	# execute_menu_item                                                  #
	#                                                                    #
	######################################################################
	def execute_menu_item(self, item_ID):
		"""Execute one of the menu item of the context menu
		
		This method takes a single argument:
		  item_ID            the id of the item that was selected;
		and returns a boolean indicating if it is necessary to redraw the
		plot.
		
		Actually, since this kind of curve does not add items to the
		context menu, this method does not do anything and simply returns
		False."""
		
		return False



########################################################################
#                                                                      #
# plot_curve_multiple                                                  #
#                                                                      #
########################################################################
class plot_curve_multiple(object):
	"""A class to handle the multiple curve as a single curve
	
	A multiple curve consists of multiple multiple curves, each having
	their style, but regrouped under a single legend. It is possible to
	select a limited number of curves to plot. By default no curve is
	selected."""
	
	context_menu_label = "Select curve"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, curves , name = ""):
		"""Initialize the curve
		
		This method takes 2 to 4 arguments:
		  curves             a list of curves;
		  name               (optional) a string giving the name of the
		                     curve that is used for the legend and similar
		                     stuff, by default the curves does not have a
		                     name."""
		
		self.name = name
		
		self.curves = curves
		
		self.nb_curves = len(self.curves)
		
		# The curves that are selected (by default, none).
		self.selected_curves = [False]*self.nb_curves
		
		# Prepare IDs for the context menu.
		self.curves_IDs = [wx.NewId() for i in range(len(self.curves))]
	
	
	######################################################################
	#                                                                    #
	# set_name                                                           #
	#                                                                    #
	######################################################################
	def set_name(self, name):
		"""Set or replace the name of the curve
		
		This method takes a single argument:
		  name               the name of the curve."""
		
		self.name = name
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the curve
		
		This method returns the name of the curve."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# set_style                                                          #
	#                                                                    #
	######################################################################
	def set_style(self, style):
		"""Set or replace the style of the curve
		
		This method takes a single argument:
		  style              the style of the curve.
		
		It replaces the style of all the curves included in the multiple
		curve."""
		
		for i in range(self.nb_curves):
			self.curves[i].set_style(self.style)
	
	
	######################################################################
	#                                                                    #
	# get_style                                                          #
	#                                                                    #
	######################################################################
	def get_style(self):
		"""Get the style of the curve
		
		This method returns the style of the first curve of the multiple
		curve."""
		
		return self.curves[0].get_style()
	
	
	######################################################################
	#                                                                    #
	# set_colour_from_usage                                              #
	#                                                                    #
	######################################################################
	def set_colour_from_usage(self, colour_database, colour_usage):
		"""Set the colour of the curve automatically while reducing
		redundancy
		
		This method takes 2 arguments:
		  colour_database    a list of colour names;
		  colour_usage       a list of the number of times the colour in
		                     the database are used in the plot containing
		                     the curve.
		
		It replaces the style of all the curves of the multiple curve
		with that of the first curve and the automatically selected
		colour.
		
		This method is automatically called by the plot method when
		appropriate. You don't need to call it yourself."""
		
		self.curves[0].set_colour_from_usage(colour_database, colour_usage)
		
		style = self.curves[0].get_style()
		
		for i in range(1, self.nb_curves):
			self.curves[i].set_style(style)
	
	
	######################################################################
	#                                                                    #
	# bounding_box                                                       #
	#                                                                    #
	######################################################################
	def bounding_box(self):
		"""Get the bounding box of the curve
		
		This method returns 4 arguments:
		  x_min, x_max       the range of values in the x vectors;
		  y_min, y_max       the range of values in the y vectors.
		
		If all the curves are empty, it returns Nones."""
		
		x_min = None
		x_max = None
		y_min = None
		y_max = None
		
		for i in range(self.nb_curves):
			x_min_i, x_max_i, y_min_i, y_max_i = self.curves[i].bounding_box()
			
			if x_min_i is not None:
				if x_min is None:
					x_min = x_min_i
					x_max = x_max_i
					y_min = y_min_i
					y_max = y_max_i
				else:
					x_min = min(x_min, x_min_i)
					x_max = max(x_max, x_max_i)
					y_min = min(y_min, y_min_i)
					y_max = max(y_max, y_max_i)
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# draw_legend                                                        #
	#                                                                    #
	######################################################################
	def draw_legend(self, DC, x_left, y_bottom, x_right, y_top):
		"""Draw the legend for the curve
		
		This method takes 5 arguments:
		  DC                 the device context on which to draw the
		                     legend;
		  x_left, y_button   the starting point of the legend line;
		  x_right, y_top     the ending point of the legend line.
		
		It draws a line and eventually a marker according to the style of
		the first of the multiple curves."""
		
		self.curves[0].draw_legend(DC, x_left, y_bottom, x_right, y_top)
	
	
	######################################################################
	#                                                                    #
	# draw_line                                                          #
	#                                                                    #
	######################################################################
	def draw_line(self, DC, shift_x, scale_x, shift_y, scale_y, nb_points = 0, min_x_value = None, axis_x = LINEAR, axis_y = LINEAR):
		"""Draw the curves
		
		This method takes 5 to 9 arguments:
		  DC                 the device context on which to draw the curve;
		  shift_x            position of the x origin on the device
		                     context;
		  scale_x            scaling factor of the x axis;
		  shift_y            position of the y origin on the device
		                     context;
		  scale_y            scaling factor of the x axis;
		  nb_points          (optional) the number of points to draw, if
		                     the value is 0 (default), all points are
		                     drawn;
		  min_x_value        (optional) the value of x on the left of the
		                     figure;
		  axis_x             (optional) LINEAR (default) or LOG;
		  axis_y             (optional) LINEAR (default) or LOG.
		
		This method simply calls the draw_line methods of all selected
		curves."""
		
		for i in range(self.nb_curves):
			if self.selected_curves[i]:
				self.curves[i].draw_line(DC, shift_x, scale_x, shift_y, scale_y, nb_points, min_x_value, axis_x, axis_y)
	
	
	######################################################################
	#                                                                    #
	# get_data_as_text                                                   #
	#                                                                    #
	######################################################################
	def get_data_as_text(self):
		"""Get the curves as text
		
		This method returns a string with all the data in text format.
		The text is obtained for each curve get_data_as_text method and
		aggregated, seperated by the name of the curves."""
		
		return "".join(self.curves[i].name + "\n" + self.curves[i].get_data_as_text() for i in range(self.nb_curves) if self.selected_curves[i])	
	
	
	######################################################################
	#                                                                    #
	# select_curve                                                       #
	#                                                                    #
	######################################################################
	def select_curve(self, curve_nb, select = True):
		"""Select/unselect a curve
		
		This method takes 1 or 2 arguments:
		  curve_nb           the number of the curve to select;
		  select             (optional) a boolean indicating if the curve
		                     is selected of unselected (by default True).
		and returns a boolean indicating if the plot needs to be redrawn."""
		
		if self.selected_curves[curve_nb] == select:
			return False
		
		else:
			self.selected_curves[curve_nb] = select
			return True
	
	
	######################################################################
	#                                                                    #
	# get_context_menu                                                   #
	#                                                                    #
	######################################################################
	def get_context_menu(self, DC):
		"""Get the curve specific context menu
		
		This method takes one argument:
		  parent             the window that handles the menu events.
		It returns the label of the context menu, and the context menu.
		
		A menu item is created for every curve of the multiple curve with
		the curve name. It allows the user to select which curve to show.
		If a curve is selected, the item is checked."""
		
		# We need to recreate the submenu every time since when it is added
		# to the context menu, the latter takes ownership.
		context_menu = wx.Menu()
		for i in range(self.nb_curves):
			context_menu.AppendCheckItem(self.curves_IDs[i], self.curves[i].name)
			DC.Bind(wx.EVT_MENU, DC.on_menu_item, id = self.curves_IDs[i])
			context_menu.Check(self.curves_IDs[i], self.selected_curves[i])
		
		return self.context_menu_label, context_menu
	
	
	######################################################################
	#                                                                    #
	# execute_menu_item                                                  #
	#                                                                    #
	######################################################################
	def execute_menu_item(self, item_ID):
		"""Execute one of the menu item of the context menu
		
		This method takes a single argument:
		  item_ID            the id of the item that was selected;
		and returns a boolean indicating if it is necessary to redraw the
		plot."""
		
		try:
			curve_nb = self.curves_IDs.index(item_ID)
		except ValueError:
			return False
		
		self.selected_curves[curve_nb] = not self.selected_curves[curve_nb]
		return True



########################################################################
#                                                                      #
# plot                                                                 #
#                                                                      #
########################################################################
class plot(wx.Window):
	"""A class, derived from wxWindow, to plot data
	
	To use this class, you first need to create the plot. Then, you can
	add curves, add points to them or remove curves. The class manages
	the scaling and creation of the axis, the legend, and the curves. The
	plot can be clickable. In that case, when the user right clicks a
	context menu is shown in which the user can select the scaling of the
	plot and to remove curves. When the user right clicks on the legend of
	a curve, he can remove that curve and certain curve types allow other
	operations."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, id = -1, size = wx.DefaultSize, style = 0):
		"""Initialize the plot
		
		This method takes 1 to 4 arguments:
			parent             the window's parent;
			id                 (optional) the window's id;
			size               (optional) the window's size;
			style              (optional) the window's style."""
		
		# Create the window
		wx.Window.__init__(self, parent, id, size = size, style = style|wx.NO_FULL_REPAINT_ON_RESIZE)
		
		# The plot uses the global settings for buffered drawing. But
		# saves the setting locally so it can be changed betwen plots.
		self.use_buffered_drawing = use_buffered_drawing
		
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.Bind(wx.EVT_PAINT, self.on_paint)
		
		# Some properties of the plot.
		self.font_size = 9
		self.legend_line_length = 24
		
		# Batch mode allows the addition of many curves or points
		# without redrawing to accelerate drawing. The instance remembers
		# how many times begin_batch has been called and update the plot
		# only when end_batch is called as many times. We remember if a
		# change was done in batch mode to know if we must redraw
		# everything.
		self.batch = 0
		self.batch_needs_redraw = False
		
		# Are the axis scaled linearly of logarithmically. By default, they
		# are linear.
		self.x_axis = LINEAR
		self.y_axis = LINEAR
		
		# Should the axes be determined automaticaly? Otherwise, they
		# must be provided using 
		self.automatic_axes = True
		self.x_left = 0.0
		self.y_bottom = 0.0
		self.x_right = 1.0
		self.y_top = 1.0
		
		# In fast drawing modes, the curves and axes are not always redrawn
		# to speed up the execution.
		self.fast_drawing = NO_FAST_DRAWING
		
		# The position and size of the legend.
		self.legend_position = None
		self.legend_height = 0
		self.legend_width = 0
		
		# Show a grid?
		self.grid = False
		
		# The positions of the legends of the various curves.
		# Those positions are kept to allow specific handling of the right
		# click on those legends.
		self.legend_positions = []
		
		self.curves = []
		
		self.xlabel = None
		self.ylabel = None
		self.ylabel_rotated = True
		
		# By default, the plot is not clickable. But if it is made
		# clickable, by default the user will have the right to remove
		# curves.
		self.clickable = False
		self.allow_remove_curve = True
		
		# Prepare the context menu.
		self.context_menu = wx.Menu()
		self.set_properties_ID = wx.NewId()
		self.context_menu.Append(self.set_properties_ID, "&Set properties")
		self.Bind(wx.EVT_MENU, self.on_set_properties, id = self.set_properties_ID)
		self.context_menu.AppendSeparator()
		self.view_data_ID = wx.NewId()
		self.context_menu.Append(self.view_data_ID, "&View data")
		self.Bind(wx.EVT_MENU, self.on_view_data, id = self.view_data_ID)
		self.rename_ID = wx.NewId()
		self.context_menu.Append(self.rename_ID, "&Rename")
		self.Bind(wx.EVT_MENU, self.on_rename, id = self.rename_ID)
		self.submenu_ID = wx.NewId()
		self.remove_curve_ID = wx.NewId()
		self.context_menu.Append(self.remove_curve_ID, "&Remove curve")
		self.Bind(wx.EVT_MENU, self.on_remove_curve, id = self.remove_curve_ID)
		self.context_menu.AppendSeparator()
		self.remove_all_curves_ID = wx.NewId()
		self.context_menu.Append(self.remove_all_curves_ID, "Remove &all curves")
		self.Bind(wx.EVT_MENU, self.on_remove_all_curves, id = self.remove_all_curves_ID)
		
		# When a right click is done, a menu can be poped up. Variables
		# keep information about where the click was done to be used by
		# the items of the menu.
		self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		self.clicked_curve = 0
		
		# Create and initialize a buffer to avoir flicker.
		self.width, self.height = self.GetClientSizeTuple()
		self.buffer = wx.EmptyBitmap(self.width, self.height)
	
	
	######################################################################
	#                                                                    #
	# set_clickable                                                      #
	#                                                                    #
	######################################################################
	def set_clickable(self, clickable = True):
		"""Allow/disallow clicking on the plot
		
		This method takes a single optional argument:
		  clickable          (optional) a boolean indicating if the plot is
		                     clickable, default value is True."""
		
		self.clickable = clickable
	
	
	######################################################################
	#                                                                    #
	# set_allow_remove_curve                                             #
	#                                                                    #
	######################################################################
	def set_allow_remove_curve(self, allow_remove_curve = True):
		"""Allow/disallow removing of curves
		
		This method takes a single optional argument:
		  allow_remove_curve (optional) a boolean indicating if the user is
		                     is allowed to remove curves using the context
		                     menu shown when he right clicks, default value
		                     is True."""
		
		self.allow_remove_curve	= allow_remove_curve
	
	
	######################################################################
	#                                                                    #
	# begin_batch                                                        #
	#                                                                    #
	######################################################################
	def begin_batch(self):
		"""Begin batch mode
		
		In batch mode the operations such as curve adding or removal are
		postponed until end_batch is called. 
		
		You can call this method multiple times. It increases the batch
		mode count by one and the plot is updated only when the batch gets
		back to 0."""
		
		self.batch += 1
	
	
	######################################################################
	#                                                                    #
	# end_batch                                                          #
	#                                                                    #
	######################################################################
	def end_batch(self):
		"""End batch mode
		
		This method decreases the batch mode count by one. If the count is
		0, and it is necessary, the plot is redrawn."""
		
		self.batch -= 1
		
		if self.batch == 0:
			if self.batch_needs_redraw:
				self.update()
			
			self.batch_needs_redraw = False
	
	
	######################################################################
	#                                                                    #
	# on_paint                                                           #
	#                                                                    #
	######################################################################
	def on_paint(self, event):
		"""Handle paint events
		
		This method takes a single argument:
		  event              the event.
		
		This method redraws the window (from a buffer) when a region was
		damaged."""
		
		# If we use buffered drawing, we simply put on the screen what
		# is already in the buffer.
		if self.use_buffered_drawing:
			DC = wx.BufferedPaintDC(self, self.buffer)
		
		# If we don't use buffered drawing, we have to redraw everything.
		else:
			DC = wx.PaintDC(self)
			DC.DrawBitmap(self.buffer, 0, 0)
	
	
	######################################################################
	#                                                                    #
	# on_size                                                            #
	#                                                                    #
	######################################################################
	def on_size(self, event):
		"""Handle size events
		
		This method takes a single argument:
		  event              the event.
		
		This method redraws the window when its size changes."""
		
		self.width, self.height = self.GetClientSizeTuple()
		self.buffer = wx.EmptyBitmap(self.width, self.height)
		
		self.update()
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, function, *args):
		"""Update the plot
		
		This method takes care of updating the plot for other methods. It
		takes at least one argument:
		  function           the function that must be called to update the
		                     plot, by default it is draw all;
		  *args              all other arguments will be passed to the
		                     function.
		
		Do not call this method directly, use update instead."""
		
		if function is None:
			function = self.draw_all
		
		if self.use_buffered_drawing:
			DC = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		else:
			DC = wx.MemoryDC()
			DC.SelectObject(self.buffer)
		
		DC.BeginDrawing()
		
		function(DC, *args)
		
		DC.EndDrawing()
		
		if not self.use_buffered_drawing:
			wx.ClientDC(self).Blit(0, 0, self.width, self.height, DC, 0, 0)
	
	
	######################################################################
	#                                                                    #
	# update                                                             #
	#                                                                    #
	######################################################################
	def update(self, function = None, *args):
		"""Update the plot
		
		This method takes care of updating the plot for other methods. It
		takes any number of arguments:
		  function           (optional) the method that must be called to
		                     update the plot, by default it is draw_all;
		  *args              all other arguments will be passed to the
		                     function."""
		
		# On GTK, there are some issues if we update the windows before it
		# is shown. So we use CallAfter.
		if "__WXGTK__" in wx.PlatformInfo:
			wx.CallAfter(self.update_, function, *args)
		else:
			self.update_(function, *args)
	
	
	######################################################################
	#                                                                    #
	# bounding_box                                                       #
	#                                                                    #
	######################################################################
	def bounding_box(self):
		"""Get the bounding box of all the curves of the plot
		
		This method returns 4 arguments:
		  x_min, x_max       the range of values in the x vectors;
		  y_min, y_max       the range of values in the y vectors.
		
		This method verifies that the range of both axis is not null, and
		in the case of log scale that the bounds are not null or negative."""
		
		x_min = None
		x_max = None
		y_min = None
		y_max = None
		
		for i in range(len(self.curves)):
			if self.curves[i]:
				x_min_i, x_max_i, y_min_i, y_max_i = self.curves[i].bounding_box()
				
				if x_min_i is not None:
					if x_min is None:
						x_min = x_min_i
						x_max = x_max_i
						y_min = y_min_i
						y_max = y_max_i
					else:
						x_min = min(x_min, x_min_i)
						x_max = max(x_max, x_max_i)
						y_min = min(y_min, y_min_i)
						y_max = max(y_max, y_max_i)
		
		if x_min is None:
			x_min = 0.0
			x_max = 1.0
			y_min = 0.0
			y_max = 1.0
		
		# If the x or y value are constant, provide some space to avoid
		# division by 0.
		if x_min == x_max:
			if x_min == 0.0:
				x_min = -1.0
				x_max = 1.0
			elif x_min > 0:
				x_min = 0.999*x_min
				x_max = 1.001*x_max
			else:
				x_min = 1.001*x_min
				x_max = 0.999*x_max
		if y_min == y_max:
			if y_min == 0.0:
				y_min = -1.0
				y_max = 1.0
			elif y_min > 0:
				y_min = 0.999*y_min
				y_max = 1.001*y_max
			else:
				y_min = 1.001*y_min
				y_max = 0.999*y_max
		
		# If an axis is logarithmically scalled, avoid null or negative
		# values.
		if self.x_axis == LOG:
			if x_max <= 0.0:
				x_max = 1.0
			if x_min <= 0.0:
				x_min = 1.0E-6*x_max
		if self.y_axis == LOG:
			if y_max <= 0.0:
				y_max = 1.0
			if y_min <= 0.0:
				y_min = 1.0E-6*y_max
		
		return x_min, x_max, y_min, y_max
	
	
	######################################################################
	#                                                                    #
	# is_in_bounds                                                       #
	#                                                                    #
	######################################################################
	def is_in_bounds(self, curve):
		"""Determine if a curve is in actual bounds
		
		This method takes a single argument:
		  curve              a curve;
		and returns a boolean indicating if the curve is inside the actual
		bounds of the plot."""
		
		x_min, x_max, y_min, y_max = curve.bounding_box()
		
		return x_min >= self.x_left and x_max <= self.x_right and y_min >= self.y_bottom and y_max <= self.y_top
	
	
	######################################################################
	#                                                                    #
	# add_curve                                                          #
	#                                                                    #
	######################################################################
	def add_curve(self, curve):
		"""Add a curve to the plot
		
		This method takes a single argument:
		  curve              the curve to add to the plot;
		and it returns
		  curve_nb           the number of the curve."""
		
		# If no colour is assigned to the curve, give one.
		if curve.get_style().get_colours() == []:
			# Find the colours that are the less used. The first one of
			# those colour appearing in coulour_database_list will be used.
			used_colours = []
			for curve_ in self.curves:
				if curve_:
					used_colours += curve_.get_style().get_colours()
			
			colour_usage = []
			for colour in colour_database:
				colour_usage.append(used_colours.count(colour))
			
			curve.set_colour_from_usage(colour_database, colour_usage)
		
		self.curves.append(curve)
		curve_nb = len(self.curves)-1
		
		if self.batch:
			self.batch_needs_redraw = True
			return curve_nb
		
		if curve_nb == 0:
			self.update()
		elif self.is_in_bounds(curve):
			if self.legend_position is not None:
				self.update()
			else:
				self.update(self.draw_curve, curve)
		else:
			self.update()
		
		return curve_nb
	
	
	######################################################################
	#                                                                    #
	# add_points_to_curve                                                #
	#                                                                    #
	######################################################################
	def add_points_to_curve(self, curve_nb, x, y):
		"""Add points to an existing curve
		
		This method takes 3 arguments:
		  curve_nb           the number of the curve on which to add
		                     points;
		  x, y               vectors of the x and y values of the points to
		                     add."""
		
		x_min, x_max, y_min, y_max = self.curves[curve_nb].append_data(x, y)
		
		if self.batch:
			self.batch_needs_redraw = True
			return
		
		if self.fast_drawing == NO_REDRAW or (x_min >= self.x_left and x_max <= self.x_right and y_min >= self.y_bottom and y_max <= self.y_top):
			nb_points = len(x)
			
			self.update(self.draw_curve, self.curves[curve_nb], nb_points)
		
		else:
			self.update()
	
	
	######################################################################
	#                                                                    #
	# replace_curve                                                      #
	#                                                                    #
	######################################################################
	def replace_curve(self, curve_nb, x, y):
		"""Replace an existing curve
		
		This method takes 3 arguments:
		  curve_nb           the number of the curve to replace;
		  x, y               vectors of the x and y replacement values."""
		
		x_min, x_max, y_min, y_max = self.curves[curve_nb].replace_data(x, y)
		
		if self.batch:
			self.batch_needs_redraw = True
			return
		
		# In the fastest mode, only draw the new curve without removing
		# anything.
		if self.fast_drawing == NO_REDRAW:
			self.update(self.draw_curve, self.curves[curve_nb])
		
		# Otherwise, redraw everything.
		else:
			self.update()
	
	
	######################################################################
	#                                                                    #
	# get_curve                                                          #
	#                                                                    #
	######################################################################
	def get_curve(self, curve_nb):
		"""Get a curve
		
		This method takes a single argument:
		  curve_nb           the number of the requested curve
		and return a curve instance."""
		
		return self.curves[curve_nb]
	
	
	######################################################################
	#                                                                    #
	# remove_curve                                                       #
	#                                                                    #
	######################################################################
	def remove_curve(self, curve_nb):
		"""Remove a curve
		
		This method takes a single argument:
		  curve_nb           the number of the curve to remove."""
		
		self.curves[curve_nb] = None
		
		# Remove trailing None.
		for i in range(len(self.curves)-1, -1, -1):
			if self.curves[i] is None:
				self.curves.pop(i)
			else:
				break
		
		if self.batch:
			self.batch_needs_redraw = True
			return
		
		self.update()
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self, curve = None):
		"""Reset the plot
		
		This method removes all the curve of a plot and, if requested, add
		a single new curve. It takes an optional argument:
		  curve              (optional) a new curve to add to the plot."""
		
		self.curves = []
		
		# If a new curve is added, we use add_curve in order to use the
		# color selection mecanism. Otherwise, we call update to draw
		# empty axes.
		if curve:
			return self.add_curve(curve)
		else:
			if self.batch:
				self.batch_needs_redraw = True
				return
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# draw_curve                                                         #
	#                                                                    #
	######################################################################
	def draw_curve(self, DC, curve, nb_points = 0):
		"""Draw a curve
		
		This method takes 2 or 3 arguments:
		  DC                 the device context on which to draw the curve;
		  curve              the curve to draw
		  nb_points          (optional) the number of points of the curve
		                     to draw, if it is 0 (default) all the points
		                     of the curve are drawn."""
		
		DC.SetClippingRegion(self.left_axe, self.top_axe, self.right_axe-self.left_axe+1, self.bottom_axe-self.top_axe+1)
		
		curve.draw_line(DC, self.shift_x, self.scale_x, self.shift_y, self.scale_y, nb_points, axis_x = self.x_axis, axis_y = self.y_axis)
		
		DC.DestroyClippingRegion()
	
	
	######################################################################
	#                                                                    #
	# draw_all                                                           #
	#                                                                    #
	######################################################################
	def draw_all(self, DC):
		"""Draw the plot
		
		This method draws the axes, the legend and all the curves. It takes
		a single argument:
		  DC                 the device context on which to draw the plot."""
		
		DC.SetBackground(wx.Brush("white"))
		
		DC.Clear()
		
		self.draw_legend(DC)
		self.axes(DC)
		
		DC.SetClippingRegion(self.left_axe, self.top_axe, self.right_axe-self.left_axe+1, self.bottom_axe-self.top_axe+1)
		
		# Except in the fastest drawing mode trace all curves.
		if self.fast_drawing != NO_REDRAW:
			if self.automatic_axes:
				for curve in self.curves:
					if curve:
						curve.draw_line(DC, self.shift_x, self.scale_x, self.shift_y, self.scale_y, axis_x = self.x_axis, axis_y = self.y_axis)
			else:
				for curve in self.curves:
					if curve:
						curve.draw_line(DC, self.shift_x, self.scale_x, self.shift_y, self.scale_y, min_x_value = self.x_left, axis_x = self.x_axis, axis_y = self.y_axis)
		
		DC.DestroyClippingRegion()
	
	
	######################################################################
	#                                                                    #
	# set_legend_position                                                #
	#                                                                    #
	######################################################################
	def set_legend_position(self, legend_position):
		"""Set the legend position
		
		This method takes a single argument:
		  legend_position    None, TOP, or BUTTOM.
		
		If the position is None, no legend is drawn."""
		
		if legend_position != self.legend_position:
			self.legend_position = legend_position
			
			if self.batch:
				self.batch_needs_redraw = True
				return
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# set_axis                                                           #
	#                                                                    #
	######################################################################
	def set_axis(self, x_axis = None, y_axis = None):
		"""Set axis scaling
		
		This method takes 2 optional arguments:
		  x_axis, y_axis     (optional) LINEAR or LOG.
		
		When an argument is not used, the axis scaling is not changed."""
		
		if x_axis is not None or y_axis is not None:
			if x_axis is not None:
				self.x_axis = x_axis
			if y_axis is not None:
				self.y_axis = y_axis
			
			if self.batch:
				self.batch_needs_redraw = True
				return
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# get_axis                                                           #
	#                                                                    #
	######################################################################
	def get_axis(self):
		"""Get axis scaling
		
		This method returns 2 arguments:
		  x_axis, y_axis       the scaling of both axis (LINEAR or LOG)."""
		
		return self.x_axis, self.y_axis
	
	
	######################################################################
	#                                                                    #
	# set_grid                                                           #
	#                                                                    #
	######################################################################
	def set_grid(self, grid):
		"""Add/remove grid from the plot
		
		This method takes a single argument:
		  grid               a boolean indicating if the grid must be shown
		                     or not."""
		
		if grid != self.grid:
			self.grid = grid
			
			if self.batch:
				self.batch_needs_redraw = True
				return
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# get_grid                                                           #
	#                                                                    #
	######################################################################
	def get_grid(self):
		"""Get grid
		
		This method returns a boolean indicating if the grid is shown or
		not."""
		
		return self.grid
	
	
	######################################################################
	#                                                                    #
	# set_axes                                                           #
	#                                                                    #
	######################################################################
	def set_axes(self, setting = AUTOMATIC):
		"""Set the axes
		
		This method takes an optional argument:
		  setting            (optional) AUTOMATIC or a 4 element vector
		                     containing, in that order, the value of the
		                     left, buttom, right, and top axes."""
		
		if setting == AUTOMATIC:
			self.automatic_axes = True
		else:
			self.automatic_axes = False
			self.x_left = setting[0]
			self.y_bottom = setting[1]
			self.x_right = setting[2]
			self.y_top = setting[3]
		
		if self.batch:
			self.batch_needs_redraw = True
			return
		
		self.update()
	
	
	######################################################################
	#                                                                    #
	# get_axes                                                           #
	#                                                                    #
	######################################################################
	def get_axes(self):
		"""Get the axes
		
		This method returns:
		  automatic_axes                       a boolean indicating if the
		                                       axes are automaticaly set;
		  x_left, y_bottom, x_right, y_top     the value of the axes."""
		
		return self.automatic_axes, self.x_left, self.y_bottom, self.x_right, self.y_top
	
	
	######################################################################
	#                                                                    #
	# set_xlabel                                                         #
	#                                                                    #
	######################################################################
	def set_xlabel(self, xlabel):
		"""Set the x axis label
		
		This method takes a single argument:
		  xlabel             a string with the label of the x axis."""
		
		if self.xlabel != xlabel:
			self.xlabel = xlabel
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# set_ylabel                                                         #
	#                                                                    #
	######################################################################
	def set_ylabel(self, ylabel):
		"""Set the y axis label
		
		This method takes a single argument:
		  ylabel             a string with the label of the y axis."""
		
		if self.ylabel != ylabel:
			self.ylabel = ylabel
			# If the ylabel is shorter than 3 caracters, it can be drawed
			# horizontally, otherwise it will be rotated.
			if len(self.ylabel) < 3:
				self.ylabel_rotated = False
			else:
				self.ylabel_rotated = True
			
			self.update()
	
	
	######################################################################
	#                                                                    #
	# set_fast_drawing                                                   #
	#                                                                    #
	######################################################################
	def set_fast_drawing(self, fast_drawing):
		"""Set a mode in which the plots will be drawn faster
		
		This method takes a single argument:
		  fast_drawing        the drawing mode.
		
		4 drawing modes are possible:
		  NO_FAST_DRAWING   no fast drawing;
		  HALF_SCREEN       half screen mode - in this mode, when data
		                    overflows the graph, the x axis is moved up by
		                    half of it's range and the half part of the
		                    curves still fitting in the new range is drawn;
		  FULL_SCREEN       full screen mode - in this mode, when data
		                    overflows the graph, the x axis is moved up by
		                    it's full range and no curve needs to be
		                    redrawn;
		  NO_REDRAW         no redraw mode - in this mode, the axis are
		                    never changed and the data is never redrawn.
		
		For all the fast drawing modes, the axis must have been manually
		set."""
		
		self.fast_drawing = fast_drawing
	
	
	######################################################################
	#                                                                    #
	# draw_legend                                                        #
	#                                                                    #
	######################################################################
	def draw_legend(self, DC):
		"""Draw the legend
		
		This method takes a single argument:
		  DC                 the device context on which to design the
		                     legend."""
		
		if self.legend_position is None:
			return
		
		# Get the size of the window.
		(width, height) = self.GetClientSizeTuple()
		
		# Set the font.
		font = DC.GetFont()
		font.SetFamily(wx.SWISS)
		font.SetPointSize(self.font_size)
		DC.SetFont(font)
		
		# Create legend positions for all curves. Position are initialized
		# with None value that indicate that the is no legend for this
		# curve.
		self.legend_positions = [None]*len(self.curves)
		
		# Get the space needed for all legend elements. If a curve has no
		# name, it is not calculated in the legend.
		extent = []
		for curve in self.curves:
			if not curve or not curve.name:
				extent.append(0)
			else:
				text_extent = DC.GetTextExtent(curve.name)
				total_extent = limited_int(self.legend_line_length+0.5*self.font_size+text_extent[0])
				extent.append(total_extent)
		
		# If the legend is in top of bottom, calculate the number of lines
		# needed and the length of each line.
		if self.legend_position == TOP or self.legend_position == BOTTOM:
			
			nb_lines = 0
			lines = []
			line_lengths = []
			for i in range(len(self.curves)):
				if extent[i]:
					
					# If this is the first legend element, or if it does not fit
					# in the current line, add a new line.
					if nb_lines == 0 or line_lengths[-1]+2*self.font_size+extent[i] > width:
						nb_lines += 1
						lines.append([i])
						line_lengths.append(extent[i])
					
					# If this legend element fits in this line, add it.
					else:
						lines[-1].append(i)
						line_lengths[-1] += 2*self.font_size+extent[i]
			
			self.legend_height = limited_int((1.5*nb_lines-0.5+1)*self.font_size)
			self.legend_width = width
		
		# Draw the legend.
		text_height = DC.GetTextExtent("bp")[1]
		if self.legend_position == TOP or self.legend_position == BOTTOM:
			if self.legend_position == TOP:
				legend_top = limited_int(0 + 0.5*self.font_size)
			else:
				legend_top = limited_int(height - self.legend_height + 0.5*self.font_size)
			
			for i in range(nb_lines):
				x_left = limited_int(0.5*(width-line_lengths[i]))
				y_top = legend_top + limited_int(1.5 * i * self.font_size)
				y_bottom = y_top + text_height
				y_center = limited_int(y_top + 0.5*self.font_size)
				
				for curve_nb in lines[i]:
					x_end_line = x_left + self.legend_line_length
					self.curves[curve_nb].draw_legend(DC, x_left, y_center, x_end_line, y_center)
					x_begin_text = limited_int(x_end_line + 0.5*self.font_size)
					DC.DrawText(self.curves[curve_nb].name, x_begin_text, y_top)
					x_right = x_left + extent[curve_nb]
					
					self.legend_positions[curve_nb] = [x_left, y_top, x_right, y_bottom]
					
					x_left = x_right + 2*self.font_size
	
	
	######################################################################
	#                                                                    #
	# axes                                                               #
	#                                                                    #
	######################################################################
	def axes(self, DC):
		"""Draw the axes
		
		This method takes a single argument:
		  DC                 the device context on which to design the
		                     axes."""
		
		DC.SetPen(wx.Pen(wx.NamedColour("BLACK"), 1))
		
		# Set the font.
		font = DC.GetFont()
		font.SetFamily(wx.SWISS)
		font.SetPointSize(self.font_size)
		DC.SetFont(font)
		
		# Get the size of the window.
		(width, height) = self.GetClientSizeTuple()
		
		# Get the bounding box of the curves.
		x_min, x_max, y_min, y_max = self.bounding_box()
		
		half_font_size = limited_int(0.5*self.font_size)
		
		if self.automatic_axes:
			x_left = x_min
			x_right = x_max
			y_bottom = y_min
			y_top = y_max
		else:
			x_left = self.x_left
			x_right = self.x_right
			y_bottom = self.y_bottom
			y_top = self.y_top
		
		# If one of the fast drawing mode is selected, select the axes
		# accordingly.
		if self.fast_drawing:
			if self.fast_drawing == NO_REDRAW:
				pass
			elif x_max > x_right:
				if self.fast_drawing == FULL_SCREEN:
					full_range = x_right - x_left
					x_left = math.floor(x_max/full_range)*full_range
					x_right = x_left + full_range
				elif self.fast_drawing == HALF_SCREEN:
					full_range = x_right - x_left
					x_left = (math.floor(2.0*x_max/full_range) - 1.0)*0.5*full_range
					x_right = x_left + full_range
		
		# Determine the position of the the top and bottom axes
		# according to the font size in order to keep some space
		# for the ticks label and the legend.
		self.top_axe = 0+self.font_size
		self.bottom_axe = height-(2*self.font_size)
		if self.xlabel:
			self.bottom_axe = self.bottom_axe - 2*self.font_size
		if self.legend_position == TOP:
			self.top_axe = self.top_axe + self.legend_height
		elif self.legend_position == BOTTOM:
			self.bottom_axe = self.bottom_axe - self.legend_height
		
		# From the length of the y axis and the font size, calculate
		# the maximum number of ticks that can fit.
		delta_y_axes = self.bottom_axe-self.top_axe
		max_number_of_y_ticks = math.floor(delta_y_axes/(2*self.font_size))+1
		
		# If there is only place for less than 2 ticks, show 2 anyway. They
		# will overlab, but we can't do better.
		if max_number_of_y_ticks < 2:
			max_number_of_y_ticks = 2
		
		# Linear scaling.
		if self.y_axis == LINEAR:
			# Calculate the order of magnitude of delta_y and the distance
			# between ticks according to this order of magnitude.
			delta_y = y_top-y_bottom
			ticks_order_of_magnitude = math.floor(math.log10(abs(delta_y)))
			ticks_distance = 10.0**ticks_order_of_magnitude
			
			# Determine the top and bottom axes according the the ticks.
			y_top_tick = ticks_distance*math.ceil(y_top/ticks_distance)
			y_bottom_tick = ticks_distance*math.floor(y_bottom/ticks_distance)
			
			# If there is only place for 2 ticks keep the top and bottom axes
			# that we have found.
			if max_number_of_y_ticks == 2:
				nb_ticks = 2
				ticks_distance = y_top_tick-y_bottom_tick
			
			# Otherwise, limit it to the maximum number of ticks, but try
			# to put as many as possible.
			else:
				nb_ticks = limited_int((y_top_tick-y_bottom_tick)/ticks_distance)+1
				# In other cases where the number of ticks is too high, the
				# number of ticks can be reduced by increasing the distance
				# between ticks by a factor of 1, 2, 2.5, 5 or 10.
				if nb_ticks > max_number_of_y_ticks:
					for i in range(1, nb_multiples):
						if nb_ticks <= max_number_of_y_ticks:
							break
						ticks_distance = (multiples[i]/multiples[i-1])*ticks_distance
						y_top_tick = ticks_distance*math.ceil(y_top/ticks_distance)
						y_bottom_tick = ticks_distance*math.floor(y_bottom/ticks_distance)
						nb_ticks = limited_int((y_top_tick-y_bottom_tick)/ticks_distance)+1
				# If the number of ticks is not to small, try to increase it
				# to get a better resolution.
				else:
					for i in range(1, nb_divisors):
						ticks_distance = (divisors[i-1]/divisors[i])*ticks_distance
						y_top_tick = ticks_distance*math.ceil(y_top/ticks_distance)
						y_bottom_tick = ticks_distance*math.floor(y_bottom/ticks_distance)
						nb_ticks = limited_int((y_top_tick-y_bottom_tick)/ticks_distance)+1
						# When number of ticks gets larger than the maximum number of
						# ticks, do one step back.
						if nb_ticks > max_number_of_y_ticks or nb_ticks > absolute_max_nb_of_ticks:
							ticks_distance = (divisors[i]/divisors[i-1])*ticks_distance
							y_top_tick = ticks_distance*math.ceil(y_top/ticks_distance)
							y_bottom_tick = ticks_distance*math.floor(y_bottom/ticks_distance)
							nb_ticks = limited_int((y_top_tick-y_bottom_tick)/ticks_distance)+1
							break
			
			# The definitive position of the y axes.
			if self.automatic_axes:
				y_bottom = y_bottom_tick
				y_top = y_top_tick
			else:
				# In manual mode, remove the ticks that fall outside of the range.
				while y_bottom_tick < y_bottom:
					y_bottom_tick += ticks_distance
					nb_ticks -= 1
				while y_top_tick > y_top:
					y_top_tick -= ticks_distance
					nb_ticks -= 1
			
			# Generate all the ticks.
			y_ticks = [y_bottom_tick+i*ticks_distance for i in range(nb_ticks)]
			
			# Determine the space needed for y ticks label and the format
			# that should be used to show them.
			order_of_magnitude = math.floor(math.log10(max(abs(y_top), abs(y_bottom))))
			
			# Find the smallest decimal (it can be one order of magnitude smaller
			# than the the ticks order of magnitude).
			smallest_order_of_magnitude = math.floor(math.log10(abs(ticks_distance)))
			division = ticks_distance/(10**smallest_order_of_magnitude)
			if int(division) != division:
				smallest_order_of_magnitude = smallest_order_of_magnitude - 1
			
			# If the order of magnitude is too high or too low, use exponential
			# notation. In the case of values with an hign order of
			# magnitude, we verigy that thicks distance order of magnitude is
			# greater than zero because otherwise it isn't worth using the
			# exponential notation (it doesn't save any space)
			if (order_of_magnitude > 5 and smallest_order_of_magnitude > 3) or order_of_magnitude < -3:
				y_ticks_format_string = "%1." + ("%i" % int(order_of_magnitude-smallest_order_of_magnitude)) + "e"
			else:
				if smallest_order_of_magnitude >= 0:
					y_ticks_format_string = "%i"
				else:
					y_ticks_format_string = "%1." + ("%i" % int(abs(smallest_order_of_magnitude))) + "f"
			if min(y_top, y_bottom) < 0:
				test_value = -8*10**order_of_magnitude
			else:
				test_value = 8*10**order_of_magnitude
			width_of_y_ticks_label = DC.GetTextExtent(y_ticks_format_string % test_value)[0]
		
		# Log scaling.
		else:
			# Determine on how many orders of magnitude the data appears.
			smallest_order_of_magnitude = int(math.floor(math.log10(y_bottom)))
			largest_order_of_magnitude = int(math.ceil(math.log10(y_top)))
			nb_orders_of_magnitude = largest_order_of_magnitude - smallest_order_of_magnitude
			
			# If there is only place for 2 ticks keep the top and bottom axes
			# that we have found.
			if max_number_of_y_ticks == 2:
				nb_ticks = 2
				tick_seperation = nb_orders_of_magnitude
			
			# Determine the number of orders of magnitude between ticks.
			# Contrarly to the linear case, we try to fit as many ticks as
			# possible and there is no absolute maximum number of ticks. To
			# follow scientific notation, if there is too many ticks, we
			# divide the number by multiples of 3.
			else:
				
				nb_ticks = nb_orders_of_magnitude + 1
				tick_seperation = 1
				if nb_ticks > max_number_of_y_ticks:
					while nb_ticks > max_number_of_y_ticks:
						tick_seperation *= 3
						nb_ticks = int(math.ceil((nb_orders_of_magnitude + 1)/tick_seperation))
				
				# Adjust the largets and smallest order of magnitude according to
				# the tick seperation.
				smallest_order_of_magnitude = tick_seperation*int(math.floor(smallest_order_of_magnitude/tick_seperation))
				largest_order_of_magnitude = tick_seperation*int(math.ceil(largest_order_of_magnitude/tick_seperation))
				
				# To avoid underflow because the smallest order of magnitude is
				# too small it might be necessary to remove some ticks.
				while smallest_order_of_magnitude <= log_min_float:
					smallest_order_of_magnitude += tick_seperation
			
			# Determine the top and bottom axes according the the ticks.
			y_bottom_tick = 10**smallest_order_of_magnitude
			y_top_tick = 10**largest_order_of_magnitude
			
			# The definitive position of the y axes.
			if self.automatic_axes:
				y_bottom = y_bottom_tick
				y_top = y_top_tick
			else:
				# In manual mode, remove the ticks that fall outside of the range.
				if y_bottom_tick < y_bottom:
					smallest_order_of_magnitude += tick_seperation
					y_bottom_tick = 10**smallest_order_of_magnitude
					nb_ticks -= 1
				if y_top_tick > y_top:
					largest_order_of_magnitude -= tick_seperation
					y_top_tick = 10**largest_order_of_magnitude
					nb_ticks -= 1
			
			# Generate all the ticks.
			y_ticks = [10**(smallest_order_of_magnitude+i*tick_seperation) for i in range(nb_ticks)]
			
			# If the axes are between 0.001 and 1000, they are written in
			# full. Otherwise, the scientific notation is used.
			use_scientific_notation = False
			if min(y_bottom_tick, y_top_tick) < 0.001:
				use_scientific_notation = True
			if max(y_bottom_tick, y_top_tick) > 1000:
				use_scientific_notation = True
			if use_scientific_notation:
				y_ticks_format_string = "%.0e"
			else:
				y_ticks_format_string = "%s"
			
			# Determine the largest width of y tick labels. In logarithmic
			# scaling, it is possible that there is not a single tick, we
			# must therefore test for that case.
			if nb_ticks:
				width_of_y_ticks_label = max(DC.GetTextExtent(y_ticks_format_string % y_ticks[0])[0], DC.GetTextExtent(y_ticks_format_string % y_ticks[-1])[0])
			else:
				width_of_y_ticks_label = 0
		
		# The space needed for y ticks label and the axis label
		min_left_axe = width_of_y_ticks_label+self.font_size
		if self.ylabel:
			if self.ylabel_rotated:
				min_left_axe = min_left_axe + limited_int(1.5*self.font_size)
			else:
				text_extent = DC.GetTextExtent(self.ylabel)[0]
				min_left_axe = min_left_axe + text_extent + half_font_size
		
		# Determine the range of x values and do a first approximation of
		# the space needed for x ticks.
		if self.x_axis == LINEAR:
			# Determine the order of magnitude of the values and the order of
			# magnitude of the range of values.
			delta_x = x_right - x_left
			order_of_magnitude = math.floor(math.log10(max(abs(x_left), abs(x_right))))
			ticks_order_of_magnitude = math.floor(math.log10(abs(delta_x)))
			
			# Approximate the space needed for x ticks.
			if (order_of_magnitude > 5 and ticks_order_of_magnitude > 3) or order_of_magnitude < -3:
				x_ticks_format_string = "%1." + ("%i" % int(order_of_magnitude-smallest_order_of_magnitude+4)) + "e"
			else:
				if ticks_order_of_magnitude >= 0:
					x_ticks_format_string = "%" + ("%i" % int(order_of_magnitude+1+3)) + "i"
				else:
					x_ticks_format_string = "%" + ("%i" % int(order_of_magnitude+1+3)) + "." + ("%i" % int(abs(smallest_order_of_magnitude))) + "f"
			if min(x_right, x_left) < 0:
				test_value = -8*10**order_of_magnitude
			else:
				test_value = 8*10**order_of_magnitude
			width_of_x_ticks_label = DC.GetTextExtent(x_ticks_format_string % test_value)[0]
		
		else:
			# Determine on how many orders of magnitude the data appears.
			smallest_order_of_magnitude = int(math.floor(math.log10(x_left)))
			largest_order_of_magnitude = int(math.ceil(math.log10(x_right)))
			nb_orders_of_magnitude = largest_order_of_magnitude - smallest_order_of_magnitude
			
			# Approximate the space needed for x ticks.
			if min(x_right, x_left) < 1:
				test_value = 0.1
			else:
				test_value = 10.0
			width_of_x_ticks_label = DC.GetTextExtent("%.0e" % test_value)[0]
		
		# Approximate the position of the the left and right axes
		# according to the font size in order to keep some space
		# for the ticks label.
		self.left_axe = 0 + max(min_left_axe, width_of_x_ticks_label/2.0+self.font_size)
		self.right_axe = width-(width_of_x_ticks_label/2.0+self.font_size)
		
		# From the length of the y axis and the font size, calculate
		# the maximum number of ticks that can fit.
		delta_x_axes = self.right_axe-self.left_axe
		max_number_of_x_ticks = math.floor(delta_x_axes/width_of_x_ticks_label + 1)
		
		# If there is only place for less than 2 ticks, show 2 anyway. They
		# will overlab, but we can't do better.
		if max_number_of_x_ticks < 2:
			max_number_of_x_ticks = 2
		
		# Linear scaling.
		if self.x_axis == LINEAR:
			# Calculate the order of magnitude of delta_x and the distance
			# between ticks according to this order of magnitude.
			delta_x = x_right-x_left
			ticks_order_of_magnitude = math.floor(math.log10(abs(delta_x)))
			ticks_distance = 10.0**ticks_order_of_magnitude
			
			# Determine the left and right axes according the the ticks.
			x_right_tick = ticks_distance*math.ceil(x_right/ticks_distance)
			x_left_tick = ticks_distance*math.floor(x_left/ticks_distance)
			
			# If there is only place for 2 ticks keep the left and right axes
			# that we have found.
			if max_number_of_x_ticks == 2:
				nb_ticks = 2
				ticks_distance = x_right_tick-x_left_tick
			
			# Otherwise, limit it to the maximum number of ticks, but try
			# to put as many as possible.
			else:
				nb_ticks = limited_int((x_left_tick-x_right_tick)/ticks_distance)+1
				
				# In other cases where the number of ticks is too high, the
				# number of ticks can be reduced by increasing the distance
				# between ticks by a factor of 2, 2.5, 5 or 10.
				if nb_ticks > max_number_of_x_ticks:
					i = 1
					while nb_ticks > max_number_of_x_ticks:
						ticks_distance = (multiples[i]/multiples[i-1])*ticks_distance
						x_right_tick = ticks_distance*math.ceil(x_right/ticks_distance)
						x_left_tick = ticks_distance*math.floor(x_left/ticks_distance)
						nb_ticks = limited_int((x_right_tick-x_left_tick)/ticks_distance)+1
						i = i+1
				# If the number of ticks is not to small, try to increase it
				# to get a better resolution.
				else:
					i = 1
					while  i < 5:
						ticks_distance = (divisors[i-1]/divisors[i])*ticks_distance
						x_right_tick = ticks_distance*math.ceil(x_right/ticks_distance)
						x_left_tick = ticks_distance*math.floor(x_left/ticks_distance)
						nb_ticks = limited_int((x_right_tick-x_left_tick)/ticks_distance)+1
						# When number of ticks gets larger than the maximum number of
						# ticks, do one step back.
						if nb_ticks > max_number_of_x_ticks or nb_ticks > absolute_max_nb_of_ticks:
							ticks_distance = (divisors[i]/divisors[i-1])*ticks_distance
							x_right_tick = ticks_distance*math.ceil(x_right/ticks_distance)
							x_left_tick = ticks_distance*math.floor(x_left/ticks_distance)
							nb_ticks = limited_int((x_right_tick-x_left_tick)/ticks_distance)+1
							break
						i = i+1
			
			# The definitive position of the x axes.
			if self.automatic_axes:
				x_right = x_right_tick
				x_left = x_left_tick
			else:
				# In manual mode, remove the ticks that fall outside of the range.
				while x_left_tick < x_left:
					x_left_tick += ticks_distance
					nb_ticks -= 1
				while x_right_tick > x_right:
					x_right_tick -= ticks_distance
					nb_ticks -= 1
			
			# Generate all the ticks.
			x_ticks = [x_left_tick+i*ticks_distance for i in range(nb_ticks)]
			
			# Determine the space needed for x ticks label and the format
			# that should be used to show them.
			order_of_magnitude = math.floor(math.log10(max(abs(x_right), abs(x_left))))
			
			# Find the smallest decimal (it can be one order of magnitude smaller
			# than the the ticks order of magnitude).
			smallest_order_of_magnitude = math.floor(math.log10(abs(ticks_distance)))
			division = ticks_distance/(10**smallest_order_of_magnitude)
			if int(division) != division:
				smallest_order_of_magnitude = smallest_order_of_magnitude - 1
			
			# If the order of magnitude is too high or too low, use exponential
			# notation. In the case of values values with an hign order of
			# magnitude, we verify that ticks distance order of magnitude is
			# greater than zero because otherwise it isn't worth using the
			# exponential notation (it doesn't save any space).
			if (order_of_magnitude > 5 and smallest_order_of_magnitude > 3) or order_of_magnitude < -3:
				x_ticks_format_string = "%1." + ("%i" % int(order_of_magnitude-smallest_order_of_magnitude)) + "e"
			else:
				if smallest_order_of_magnitude >= 0:
					x_ticks_format_string = "%i"
				else:
					x_ticks_format_string = "%1." + ("%i" % int(abs(smallest_order_of_magnitude))) + "f"
		
		# Logarithmic scaling.
		else:
			# If there is only place for 2 ticks keep the left and right axes
			# that we have found.
			if max_number_of_x_ticks == 2:
				nb_ticks = 2
				tick_seperation = nb_orders_of_magnitude
			
			# Determine the number of orders of magnitude between ticks.
			# Contrarly to the linear case, we try to fit as many ticks as
			# possible and there is no absolute maximum number of ticks. To
			# follow scientific notation, if there is too many ticks, we
			# divide the number by multiples of 3.
			else:
				nb_ticks = nb_orders_of_magnitude + 1
				tick_seperation = 1
				if nb_ticks > max_number_of_x_ticks:
					while nb_ticks > max_number_of_x_ticks:
						tick_seperation *= 3
						nb_ticks = int(math.ceil((nb_orders_of_magnitude + 1)/tick_seperation))
				
				# Adjust the largets and smallest order of magnitude according to
				# the tick seperation.
				smallest_order_of_magnitude = tick_seperation*int(math.floor(smallest_order_of_magnitude/tick_seperation))
				largest_order_of_magnitude = tick_seperation*int(math.ceil(largest_order_of_magnitude/tick_seperation))
			
			# Determine the left and right axes according the the ticks.
			x_left_tick = 10**smallest_order_of_magnitude
			x_right_tick = 10**largest_order_of_magnitude
			
			# The definitive position of the x axes.
			if self.automatic_axes:
				x_left = x_left_tick
				x_right = x_right_tick
			else:
				# In manual mode, remove the ticks that fall outside of the range.
				if x_left_tick < x_left:
					smallest_order_of_magnitude += tick_seperation
					x_left_tick = 10**smallest_order_of_magnitude
					nb_ticks -= 1
				if x_right_tick > x_right:
					largest_order_of_magnitude -= tick_seperation
					x_right_tick = 10**largest_order_of_magnitude
					nb_ticks -= 1
			
			# Generate all the ticks.
			x_ticks = [10**(smallest_order_of_magnitude+i*tick_seperation) for i in range(nb_ticks)]
			
			# If the axes are between 0.001 and 1000, they are written in
			# full. Otherwise, the scientific notation is used.
			use_scientific_notation = False
			if min(x_left_tick, x_right_tick) < 0.001:
				use_scientific_notation = True
			if max(x_left_tick, x_right_tick) > 1000:
				use_scientific_notation = True
			if use_scientific_notation:
				x_ticks_format_string = "%.0e"
			else:
				x_ticks_format_string = "%s"
		
		# Save the axis range values.
		if self.automatic_axes or self.fast_drawing:
			self.x_left = x_left
			self.x_right = x_right
			self.y_bottom = y_bottom
			self.y_top = y_top
		
		# Determine the space really needed for ticks labels. In
		# logarithmic scaling, it is possible that there is not a single
		# tick, we must therefore test for that case.
		if nb_ticks:
			first_tick_extent = DC.GetTextExtent(x_ticks_format_string % x_ticks[0])[0]
			self.left_axe = max(min_left_axe, limited_int(0.5*(first_tick_extent+self.font_size)))
			last_tick_extent = DC.GetTextExtent(x_ticks_format_string % x_ticks[-1])[0]
			self.right_axe = limited_int(width-(0.5*(last_tick_extent+self.font_size)))
		else:
			self.left_axe = min_left_axe
			self.right_axe = limited_int(width-(0.5*self.font_size))
		
		if self.curves:
			# Calculate scale and shift for both axis.
			if self.x_axis == LINEAR:
				self.scale_x = (self.right_axe-self.left_axe)/(self.x_right-self.x_left)
				self.shift_x = self.x_right-self.right_axe/self.scale_x
			else:
				self.scale_x = (self.right_axe-self.left_axe)/(math.log10(self.x_right)-math.log10(self.x_left))
				self.shift_x = math.log10(self.x_right)-self.right_axe/self.scale_x
			if self.y_axis == LINEAR:
				self.scale_y = (self.top_axe-self.bottom_axe)/(self.y_top-self.y_bottom)
				self.shift_y = self.y_top-self.top_axe/self.scale_y
			else:
				self.scale_y = (self.top_axe-self.bottom_axe)/(math.log10(self.y_top)-math.log10(self.y_bottom))
				self.shift_y = math.log10(self.y_top)-self.top_axe/self.scale_y
			
			# Draw the ticks, the ticks label and the grid.
			x_tick_left = self.left_axe-2
			x_tick_right = self.left_axe
			for tick in y_ticks:
				if self.y_axis == LINEAR:
					y_tick = tick
				else:
					y_tick = math.log10(tick)
				y_tick = limited_int(self.scale_y*(y_tick-self.shift_y))
				# Draw the tick.
				DC.SetPen(wx.Pen(wx.NamedColour("BLACK"), 1))
				DC.DrawLine(x_tick_left, y_tick, x_tick_right, y_tick)
				# Draw the grid.
				if self.grid:
					DC.SetPen(wx.Pen(wx.NamedColour("LIGHT GREY"), 1))
					DC.DrawLine(self.left_axe, y_tick, self.right_axe, y_tick)
				text_extent = DC.GetTextExtent(y_ticks_format_string % tick)
				x_text_left = self.left_axe-half_font_size-text_extent[0]
				y_text_bottom = y_tick - limited_int(0.5*text_extent[1])
				DC.DrawText(y_ticks_format_string % tick, x_text_left, y_text_bottom)
			y_tick_bottom = self.bottom_axe+2
			y_tick_top = self.bottom_axe
			for tick in x_ticks:
				if self.x_axis == LINEAR:
					x_tick = tick
				else:
					x_tick = math.log10(tick)
				x_tick = limited_int(self.scale_x*(x_tick-self.shift_x))
				DC.SetPen(wx.Pen(wx.NamedColour("BLACK"), 1))
				DC.DrawLine(x_tick, y_tick_bottom, x_tick, y_tick_top)
				if self.grid:
					DC.SetPen(wx.Pen(wx.NamedColour("LIGHT GREY"), 1))
					DC.DrawLine(x_tick, self.bottom_axe, x_tick, self.top_axe)
				text_extent = DC.GetTextExtent(x_ticks_format_string % tick)
				x_text_left = x_tick - limited_int(0.5*text_extent[0])
				y_text_bottom = self.bottom_axe+half_font_size
				DC.DrawText(x_ticks_format_string % tick, x_text_left, y_text_bottom)
		
		# Drawing the axes. We draw the axis after the ticks and the grid
		# because the grid makes grey lines on the axes.
		DC.SetPen(wx.Pen(wx.NamedColour("BLACK"), 1))
		DC.DrawLine(self.left_axe, self.bottom_axe, self.right_axe+1, self.bottom_axe)
		DC.DrawLine(self.left_axe, self.top_axe, self.right_axe+1, self.top_axe)
		DC.DrawLine(self.left_axe, self.bottom_axe, self.left_axe, self.top_axe-1)
		DC.DrawLine(self.right_axe, self.bottom_axe, self.right_axe, self.top_axe-1)
		
		# Add the axis labels.
		if self.xlabel:
			text_extent = DC.GetTextExtent(self.xlabel)[0]
			x_legend_left = limited_int(0.5*(self.left_axe+self.right_axe-text_extent))
			y_legend_bottom = self.bottom_axe + limited_int(2*self.font_size)
			DC.DrawText(self.xlabel, x_legend_left, y_legend_bottom)
		if self.ylabel:
			x_legend_left = half_font_size
			# The y axis label is usually rotated
			if self.ylabel_rotated:
				text_extent = DC.GetTextExtent(self.ylabel)[0]
				y_legend_bottom = limited_int(0.5*(self.bottom_axe+self.top_axe+text_extent))
				DC.DrawRotatedText(self.ylabel, x_legend_left, y_legend_bottom, 90)
			else:
				text_extent = DC.GetTextExtent(self.ylabel)[1]
				y_legend_bottom = limited_int(0.5*(self.bottom_axe+self.top_axe-text_extent))
				DC.DrawText(self.ylabel, x_legend_left, y_legend_bottom)
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Handle right click events
		
		This method takes a single argument:
		  event              the event.
		
		It shows a menu if the plot is clickable."""
		
		if not self.clickable:
			return
		
		# Check were the click was done.
		(x, y) = event.GetPositionTuple()
		
		# Determine if the click was on a legend and on which legend.
		self.clicked_curve = -1
		if self.legend_position is not None:
			for curve_nb in range(len(self.curves)):
				if self.legend_positions[curve_nb]:
					[x_left, y_top, x_right, y_bottom] = self.legend_positions[curve_nb]
					if x >= x_left and x <= x_right and y >= y_top and y <= y_bottom:
						self.clicked_curve = curve_nb
						break
		
		# Calculate the number of curves (not considering removed curves).
		nb_curves = 0
		for curve_nb in range(len(self.curves)):
			if self.curves[curve_nb]:
				nb_curves += 1
		
		# Create the menu.
		if self.clicked_curve != -1:
			self.context_menu.Enable(self.view_data_ID, True)
			self.context_menu.Enable(self.rename_ID, True)
			if self.allow_remove_curve:
				self.context_menu.Enable(self.remove_curve_ID, True)
			else:
				self.context_menu.Enable(self.remove_curve_ID, False)
		else:
			self.context_menu.Enable(self.view_data_ID, False)
			self.context_menu.Enable(self.rename_ID, False)
			self.context_menu.Enable(self.remove_curve_ID, False)
		if nb_curves:
			if self.allow_remove_curve:
				self.context_menu.Enable(self.remove_all_curves_ID, True)
			else:
				self.context_menu.Enable(self.remove_all_curves_ID, False)
		self.context_menu.Enable(self.set_properties_ID, True)
		
		# Add the curve submenu, if it exists.
		if self.context_menu.FindItemById(self.submenu_ID):
			self.context_menu.Remove(self.submenu_ID)
		if self.clicked_curve != -1:
			label, submenu = self.curves[self.clicked_curve].get_context_menu(self)
			if submenu:
				self.context_menu.InsertMenu(4, self.submenu_ID, label, submenu)
		
		# Show the menu.
		self.PopupMenu(self.context_menu)
	
	
	######################################################################
	#                                                                    #
	# on_view_data                                                       #
	#                                                                    #
	######################################################################
	def on_view_data(self, event):
		"""Handle menu event when the view data item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It shows a window with the curve data."""
		
		self.view_data(self.clicked_curve)
	
	
	######################################################################
	#                                                                    #
	# on_remove_curve                                                    #
	#                                                                    #
	######################################################################
	def on_remove_curve(self, event):
		"""Handle menu event when the remove curve item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It removes the curve and sends a remove_curve_event to the parent
		window."""
		
		self.remove_curve(self.clicked_curve)
		
		event = remove_curve_event(self.GetId(), self.clicked_curve)
		self.GetEventHandler().ProcessEvent(event)
	
	
	######################################################################
	#                                                                    #
	# on_rename                                                          #
	#                                                                    #
	######################################################################
	def on_rename(self, event):
		"""Handle menu event when the rename item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It changes the name of the curve."""
		
		self.rename(self.clicked_curve)
	
	
	######################################################################
	#                                                                    #
	# rename                                                             #
	#                                                                    #
	######################################################################
	def rename(self, curve_nb):
		"""Rename a curve
		
		This method takes a single argument:
		  curve_nb           the number of the curve.
		
		It shows a renaming dialog."""
		
		old_name = self.curves[curve_nb].get_name()
		
		window = rename_dialog(self, old_name)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			new_name = window.get_name()
			self.curves[curve_nb].set_name(new_name)
			
			self.update()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_remove_all_curves                                               #
	#                                                                    #
	######################################################################
	def on_remove_all_curves(self, event):
		"""Handle menu event when the remove all curves item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It removes all the curves. It also sends remove_curve_event's to
		the parent window."""
		
		self.begin_batch()
		
		for curve_nb in range(len(self.curves)):
			if self.curves[curve_nb]:
				self.remove_curve(curve_nb)
				
				event = remove_curve_event(self.GetId(), curve_nb)
				self.GetEventHandler().ProcessEvent(event)
		
		self.end_batch()
	
	
	######################################################################
	#                                                                    #
	# on_set_properties                                                  #
	#                                                                    #
	######################################################################
	def on_set_properties(self, event):
		"""Handle menu event when the set properties item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It shows a property dialog and updates the plot accordingly."""
		
		window = properties_dialog(self)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			automatic, x_from, y_from, x_to, y_to, x_axis, y_axis, grid = window.get_answers()
			
			self.begin_batch()
			
			if automatic:
				self.set_axes(AUTOMATIC)
			else:
				self.set_axes([x_from, y_from, x_to, y_to])
			self.set_axis(x_axis, y_axis)
			self.set_grid(grid)
			
			self.end_batch()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_menu_item                                                       #
	#                                                                    #
	######################################################################
	def on_menu_item(self, event):
		"""Handle menu event for curve specific menu items
		
		This method takes a single argument:
		  event              the event.
		
		It asks the appropriate curve to take the appropriate action."""
		
		need_to_redraw = False
		
		for curve in self.curves:
			if curve:
				need_to_redraw = need_to_redraw or curve.execute_menu_item(event.GetId())
		
		if need_to_redraw:
			self.update()
	
	
	######################################################################
	#                                                                    #
	# view_data                                                          #
	#                                                                    #
	######################################################################
	def view_data(self, curve_nb):
		"""Show the data of a curve
		
		This method takes a single argument:
		  curve_nb           the number of the curve.
		
		It shows a window with the data in text form."""
		
		title = self.curves[curve_nb].name
		
		if self.xlabel:
			x_label = self.xlabel
		else:
			x_label = ""
		if self.ylabel:
			y_label = self.ylabel
		else:
			y_label = ""
		
		# Create the text of the window
		text = ""
		if x_label or y_label:
			text += "%15s   %15s\n" % (x_label, y_label)
		text += self.curves[curve_nb].get_data_as_text()
		
		window = ScrolledMessageDialog(self, text, title)
		window.ShowModal()
	
	
	######################################################################
	#                                                                    #
	# save_to_file                                                       #
	#                                                                    #
	######################################################################
	def save_to_file(self, filename):
		"""Save the figure to a file
	
		This method takes a single argument:
		  filename           the name of the file.
		
		It saves the figure in a format according to the extention of the
		filename (bmp, jpg, png, and tif are allowed). If an invalid file
		extension is used, a KeyError will be raised."""
		
		_, extension = os.path.splitext(filename)
		self.buffer.SaveFile(filename, BITMAP_TYPES[extension.lower()])



########################################################################
#                                                                      #
# rename_dialog                                                        #
#                                                                      #
########################################################################
class rename_dialog(wx.Dialog):
	"""A dialog for renaming a curve"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, old_name = ""):
		"""Initialize the dialog
		
		This method takes 1 or 2 arguments:
			parent             the plot window;
			old_name           (optional) the present name of the curve."""
		
		wx.Dialog.__init__(self, parent, -1, "Rename curve")
		
		self.SetAutoLayout(True)
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.name_box = wx.TextCtrl(self, -1, old_name)
		
		name_sizer = wx.BoxSizer(wx.HORIZONTAL)
		name_sizer.Add(wx.StaticText(self, -1, "Name: "), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		name_sizer.Add(self.name_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK, "Ok"), 0)
		buttons.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 0, wx.LEFT, 20)
		
		main_sizer.Add(name_sizer, 0, wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT, 20)
		main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 20)
		
		self.SetSizer(main_sizer)
		main_sizer.Fit(self)
		
		self.Layout()
		
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the new name of the curve
		
		This method returns the new name of the curve."""
		
		return self.name_box.GetValue()



########################################################################
#                                                                      #
# properties_dialog_validator                                          #
#                                                                      #
########################################################################
class properties_dialog_validator(wx.PyValidator):
	"""Validator for the properties dialog
	
	It verifies that the range of the x and y axis set by the user are
	positives."""
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__()
	
	
	######################################################################
	#                                                                    #
	# TransferToWindow                                                   #
	#                                                                    #
	######################################################################
	def TransferToWindow(self):
		"""Indicate that the transfer of data to the window went well
		
		This method returns True."""
		
		return True
	
	
	######################################################################
	#                                                                    #
	# TransferFromWindow                                                 #
	#                                                                    #
	######################################################################
	def TransferFromWindow(self):
		"""Indicate that the transfer of data from the window went well
		
		This method returns True."""
		
		return True
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the dialog that is validated
		and it returns True if the dialog contains valid properties or
		False otherwise."""
		
		# Verify that the ranges are positive.
		
		x_from = float(parent.x_from_box.GetValue())
		x_to = float(parent.x_to_box.GetValue())
		y_from = float(parent.y_from_box.GetValue())
		y_to = float(parent.y_to_box.GetValue())
		
		if not x_from < x_to:
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.x_to_box.SetFocus()
			parent.x_to_box.SetSelection(0, len(parent.x_to_box.GetValue()))
			parent.Refresh()
			return False
		
		if not y_from < y_to:
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.y_to_box.SetFocus()
			parent.y_to_box.SetSelection(0, len(parent.y_to_box.GetValue()))
			parent.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# properties_dialog                                                    #
#                                                                      #
########################################################################
class properties_dialog(wx.Dialog):
	"""A dialog to set the properties of a plot
	
	This dialog allows the user to select automatic or manual axis,
	linear or logarithmic scales, and whether to show a grid or not."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent):
		"""Initialize the dialog
		
		This method takes a single argument:
		  parent             the parent of the dialog."""
		
		wx.Dialog.__init__(self, parent, -1, "Set Properties")
		
		self.SetAutoLayout(True)
		
		axis_box = wx.StaticBox(self, -1, "Axis" )
		
		axis_sizer = wx.BoxSizer(wx.VERTICAL)
		axis_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		axis_sizer_2 = wx.FlexGridSizer(0, 4, 5, 5)
		axis_sizer_3 = wx.FlexGridSizer(0, 3, 5, 5)
		
		self.auto_button = wx.RadioButton(self, -1, "automatic", style = wx.RB_GROUP)
		self.manual_button = wx.RadioButton(self, -1, "manual")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_mode_selection, self.auto_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_mode_selection, self.manual_button)
		
		self.x_from_box = wx.TextCtrl(self, -1, "", validator = GUI_validators.float_validator(condition = self.manual_button.GetValue))
		self.x_to_box = wx.TextCtrl(self, -1, "", validator = GUI_validators.float_validator(condition = self.manual_button.GetValue))
		self.y_from_box = wx.TextCtrl(self, -1, "", validator = GUI_validators.float_validator(condition = self.manual_button.GetValue))
		self.y_to_box = wx.TextCtrl(self, -1, "", validator = GUI_validators.float_validator(condition = self.manual_button.GetValue))
		self.Bind(wx.EVT_TEXT, self.on_value, self.x_from_box)
		self.Bind(wx.EVT_TEXT, self.on_value, self.x_to_box)
		self.Bind(wx.EVT_TEXT, self.on_value, self.y_from_box)
		self.Bind(wx.EVT_TEXT, self.on_value, self.y_to_box)
		
		self.x_linear_button = wx.RadioButton(self, -1, "linear", style = wx.RB_GROUP)
		self.x_log_button = wx.RadioButton(self, -1, "logarithmic")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_x_scaling_selection, self.x_linear_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_x_scaling_selection, self.x_log_button)
		
		self.y_linear_button = wx.RadioButton(self, -1, "linear", style = wx.RB_GROUP)
		self.y_log_button = wx.RadioButton(self, -1, "logarithmic")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_y_scaling_selection, self.y_linear_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_y_scaling_selection, self.y_log_button)
		
		self.grid_box = wx.CheckBox(self, -1, "Show grid")
		
		axis_sizer_1.Add(self.auto_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_1.Add(self.manual_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		axis_sizer_2.Add(wx.StaticText(self, -1, "x range: from"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(self.x_from_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(wx.StaticText(self, -1, "to"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(self.x_to_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		axis_sizer_2.Add(wx.StaticText(self, -1, "y range: from"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(self.y_from_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(wx.StaticText(self, -1, "to"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_2.Add(self.y_to_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		axis_sizer_3.Add(wx.StaticText(self, -1, "x scaling: "), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_3.Add(self.x_linear_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_3.Add(self.x_log_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		axis_sizer_3.Add(wx.StaticText(self, -1, "y scaling: "), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_3.Add(self.y_linear_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		axis_sizer_3.Add(self.y_log_button, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		axis_sizer.Add(axis_sizer_1, 0)
		axis_sizer.Add(axis_sizer_2, 0, wx.TOP, 5)
		axis_sizer.Add(axis_sizer_3, 0, wx.TOP, 5)
		axis_sizer.Add(self.grid_box, 0, wx.TOP, 5)
		
		# Arrange buttons in a static box.
		axis_box_sizer = wx.StaticBoxSizer(axis_box, wx.VERTICAL)
		axis_box_sizer.Add(axis_sizer, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		# Set values.
		automatic, x_from, y_from, x_to, y_to = parent.get_axes()
		x_scaling, y_scaling = parent.get_axis()
		grid = parent.get_grid()
		self.x_from_box.SetValue(str(x_from))
		self.x_to_box.SetValue(str(x_to))
		self.y_from_box.SetValue(str(y_from))
		self.y_to_box.SetValue(str(y_to))
		if automatic:
			self.auto_button.SetValue(True)
		else:
			self.manual_button.SetValue(True)
		if x_scaling == LINEAR:
			self.x_linear_button.SetValue(True)
		else:
			self.x_log_button.SetValue(True)
		if y_scaling == LINEAR:
			self.y_linear_button.SetValue(True)
		else:
			self.y_log_button.SetValue(True)
		if grid:
			self.grid_box.SetValue(True)
		else:
			self.grid_box.SetValue(False)
		
		# In log scale, null or negative values are not acceptable.
		if x_scaling == LOG:
			self.x_from_box.GetValidator().set_limits(0.0, None)
			self.x_from_box.GetValidator().set_include_limits(include_minimum = False)
			self.x_to_box.GetValidator().set_limits(0.0, None)
			self.x_to_box.GetValidator().set_include_limits(include_minimum = False)
		if y_scaling == LOG:
			self.y_from_box.GetValidator().set_limits(0.0, None)
			self.y_from_box.GetValidator().set_include_limits(include_minimum = False)
			self.y_to_box.GetValidator().set_limits(0.0, None)
			self.y_to_box.GetValidator().set_include_limits(include_minimum = False)
		
		# Adding the buttons.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK, "Ok", validator = properties_dialog_validator()), 0, wx.ALL, 10)
		buttons.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 0, wx.ALL, 10)
		
		border = wx.BoxSizer(wx.VERTICAL)
		border.Add(axis_box_sizer, 0, wx.GROW|wx.ALL, 10)
		border.Add(buttons, 0, wx.ALIGN_CENTER)
		self.SetSizer(border)
		border.Fit(self)
		
		self.Layout()
		
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# on_mode_selection                                                  #
	#                                                                    #
	######################################################################
	def on_mode_selection(self, event):
		"""Handle mode selection events
		
		This method takes a single argument:
		  event              the event."""
		
		pass
	
	
	######################################################################
	#                                                                    #
	# on_x_scaling_selection                                             #
	#                                                                    #
	######################################################################
	def on_x_scaling_selection(self, event):
		"""Handle x scaling selection events
		
		This method takes a single argument:
		  event              the event.
		
		When the scaling is logarithmic the axis is limited to positive
		values."""
		
		# On log scaling, limit to positive values.
		if self.x_linear_button.GetValue():
			self.x_from_box.GetValidator().set_limits(None, None)
			self.x_to_box.GetValidator().set_limits(None, None)
		else:
			self.x_from_box.GetValidator().set_limits(0.0, None)
			self.x_from_box.GetValidator().set_include_limits(include_minimum = False)
			self.x_to_box.GetValidator().set_limits(0.0, None)
			self.x_to_box.GetValidator().set_include_limits(include_minimum = False)
	
	
	######################################################################
	#                                                                    #
	# on_y_scaling_selection                                             #
	#                                                                    #
	######################################################################
	def on_y_scaling_selection(self, event):
		"""Handle y scaling selection events
		
		This method takes a single argument:
		  event              the event.
		
		When the scaling is logarithmic the axis is limited to positive
		values."""
		
		# On log scaling, limit to positive values.
		if self.y_linear_button.GetValue():
			self.y_from_box.GetValidator().set_limits(None, None)
			self.y_to_box.GetValidator().set_limits(None, None)
		else:
			self.y_from_box.GetValidator().set_limits(0.0, None)
			self.y_from_box.GetValidator().set_include_limits(include_minimum = False)
			self.y_to_box.GetValidator().set_limits(0.0, None)
			self.y_to_box.GetValidator().set_include_limits(include_minimum = False)
	
	
	######################################################################
	#                                                                    #
	# on_value                                                           #
	#                                                                    #
	######################################################################
	def on_value(self, event):
		"""Handle text events in the axes value boxes
		
		This method takes a single argument:
		  event              the event.
		
		When a value is entered in a box, the manual mode is automatically
		selected."""
		
		# When a value is entered in the from or to boxes,the manual mode
		# is automatically selected.
		if self.x_from_box.GetValue() != "" or self.x_to_box.GetValue() != "" or self.y_from_box.GetValue() != "" or self.y_to_box.GetValue() != "":
			self.manual_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_answers                                                        #
	#                                                                    #
	######################################################################
	def get_answers(self):
		"""Get all the properties set by the dialog
		
		This method returns:
		  automatic                     a boolean indicating if the axes
		                                must be set automatically or
		                                manually;
		  x_from, y_from, x_to, y_to    the limits of the x and y axes (for
		                                manual axes);
		  x_scaling, y_scaling          the scaling of x and y axes;
		  grid                          a boolean indicating whether to
		                                show a grid or not."""
		
		if self.auto_button.GetValue():
			automatic = True
			x_from = None
			x_to = None
			y_from = None
			y_to = None
		else:
			automatic = False
			x_from = float(self.x_from_box.GetValue())
			x_to = float(self.x_to_box.GetValue())
			y_from = float(self.y_from_box.GetValue())
			y_to = float(self.y_to_box.GetValue())
		if self.x_linear_button.GetValue():
			x_scaling = LINEAR
		else:
			x_scaling = LOG
		if self.y_linear_button.GetValue():
			y_scaling = LINEAR
		else:
			y_scaling = LOG
		grid = self.grid_box.GetValue()
		
		return automatic, x_from, y_from, x_to, y_to, x_scaling, y_scaling, grid
