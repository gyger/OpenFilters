# -*- coding: UTF-8 -*-

# GUI_targets.py
# 
# Dialogs to set targets for the GUI of Filters.
# 
# Copyright (c) 2003-2010,2012,2013,2015 Stephane Larouche.
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

import wx
import wx.lib.filebrowsebutton

from definitions import *
import config
import targets
import color

from GUI_validators import float_validator, int_validator



one_hundred_eighty_over_pi = 180.0/math.pi



########################################################################
#                                                                      #
# target_dialog                                                        #
#                                                                      #
########################################################################
class target_dialog(wx.Dialog):
	"""A abstract class for all target dialogs
	
	This class provides a common architecture for all target dialogs. It
	must be subclassed to actually be used."""
	
	target_class = None
	
	title = ""
	value_title = ""
	data_column_title = ""
	delta_column_title = ""
	units = ""
	multiplicative_factor = 1.0
	min_value = None
	max_value = None
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, target = None):
		"""Initialize the dialog
		
		This method takes 1 or 2 arguments:
		  parent    the parent window
		  target    (optional) the target to be modified by the dialog when
		            the dialog is used to modify an existing target."""
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.target = target
		
		# Determine if reverse directiona and arbitrary polarization are
		# allowed based on the target class.
		if self.target_class:
			self.allow_direction = self.target_class.kind in targets.REVERSIBLE_TARGETS
			self.allow_arbitrary_polarization = self.target_class.kind not in targets.S_OR_P_POLARIZATION_TARGETS
		else:
			self.allow_direction = True
			self.allow_arbitrary_polarization = True
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.content_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.add_content()
		self.main_sizer.Add(self.content_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 20)
		
		self.add_buttons()
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# add_angle_box                                                      #
	#                                                                    #
	######################################################################
	def add_angle_box(self):
		"""Add an angle box to the dialog"""
		
		# Create the box.
		self.angle_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, 90.0))
		
		# Arrange it in a sizer.
		angle_sizer = wx.BoxSizer(wx.HORIZONTAL)
		angle_sizer.Add(wx.StaticText(self, -1, "Angle:"),
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		angle_sizer.Add(self.angle_box,
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		angle_sizer.Add(wx.StaticText(self, -1, "degres"),
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(angle_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_polarization_choice                                            #
	#                                                                    #
	######################################################################
	def add_polarization_choice(self):
		"""Add polarization choice to the dialog"""
		
		# Create the buttons.
		self.s_polarized_button = wx.RadioButton(self, -1, "s", style = wx.RB_GROUP)
		self.p_polarized_button = wx.RadioButton(self, -1, "p")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.s_polarized_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.p_polarized_button)
		if self.allow_arbitrary_polarization:
			self.unpolarized_button = wx.RadioButton(self, -1, "unpolarized")
			self.other_polarizations_button = wx.RadioButton(self, -1, "")
			self.other_polarizations_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, self.other_polarizations_button.GetValue))
			self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.unpolarized_button)
			self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.other_polarizations_button)
			self.other_polarizations_box.Bind(wx.EVT_TEXT, self.on_other_polarizations_box)
		
		# Arrange them in a sizer.
		polarization_sizer = wx.BoxSizer(wx.HORIZONTAL)
		polarization_sizer.Add(wx.StaticText(self, -1, "Polarization:"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		polarization_sizer.Add(self.s_polarized_button,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		polarization_sizer.Add(self.p_polarized_button,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		if self.allow_arbitrary_polarization:
			polarization_sizer.Add(self.unpolarized_button,
														 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			polarization_sizer.Add(self.other_polarizations_button,
														 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			polarization_sizer.Add(self.other_polarizations_box,
														 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			polarization_sizer.Add(wx.StaticText(self, -1, "degres"),
														 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(polarization_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_direction_choice                                               #
	#                                                                    #
	######################################################################
	def add_direction_choice(self):
		"""Add direction radio buttons to the dialog"""
		
		self.normal_direction_button = wx.RadioButton(self, -1, "normal", style = wx.RB_GROUP)
		self.reverse_direction_button = wx.RadioButton(self, -1, "reverse")
		
		# Arrange it in a sizer.
		direction_sizer = wx.BoxSizer(wx.HORIZONTAL)
		direction_sizer.Add(wx.StaticText(self, -1, "Direction:"),
		                    0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		direction_sizer.Add(self.normal_direction_button,
		                    0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		direction_sizer.Add(self.reverse_direction_button,
		                    0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(direction_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_wavelength_box                                                 #
	#                                                                    #
	######################################################################
	def add_wavelength_box(self):
		"""Add a wavelength box to the dialog"""
		
		# Create the box.
		self.wavelength_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None, include_minimum = False))
		
		# Arrange it in a sizer.
		wavelength_sizer = wx.BoxSizer(wx.HORIZONTAL)
		wavelength_sizer.Add(wx.StaticText(self, -1, "Wavelength:"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		wavelength_sizer.Add(self.wavelength_box,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelength_sizer.Add(wx.StaticText(self, -1, "nm"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(wavelength_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_value_and_tolerance_boxes                                      #
	#                                                                    #
	######################################################################
	def add_value_and_tolerance_boxes(self):
		"""Add a value and a tolorance boxes to the dialog"""
		
		# 2 boxes to specify the value and the tolerance.
		self.value_box = wx.TextCtrl(self, -1, "", validator = float_validator(self.min_value, self.max_value))
		self.tolerance_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None, include_minimum = False))
		
		# Arrange them in a sizer.
		value_sizer = wx.BoxSizer(wx.HORIZONTAL)
		value_sizer.Add(wx.StaticText(self, -1, "%s:" % self.value_title),
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		value_sizer.Add(self.value_box,
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		try:
			value_sizer.Add(wx.StaticText(self, -1, "±"),
			                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		except UnicodeDecodeError:
			value_sizer.Add(wx.StaticText(self, -1, "+-"),
			                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		value_sizer.Add(self.tolerance_box,
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		value_sizer.Add(wx.StaticText(self, -1, self.units),
		                0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(value_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_wavelength_range_boxes                                         #
	#                                                                    #
	######################################################################
	def add_wavelength_range_boxes(self):
		"""Add wavelenght range boxes to the dialog"""
		
		# Radio boxes to specify if only the data points are used, or if
		# the spectrum should be interpolated over a range of wavelength.
		self.wavelength_range_button = wx.RadioButton(self, -1, "", style = wx.RB_GROUP)
		self.wavelength_point_button = wx.RadioButton(self, -1, "only at definition points")
		
		self.Bind(wx.EVT_RADIOBUTTON, self.on_wavelength_range_radio_button, self.wavelength_range_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_wavelength_range_radio_button, self.wavelength_point_button)
		
		# 3 boxes to specify the range of wavelengths.
		self.from_wavelength_box = wx.TextCtrl(self, -1, "", validator = float_validator(minimum = 0.0, include_minimum = False, condition = self.wavelength_range_button.GetValue))
		self.to_wavelength_box = wx.TextCtrl(self, -1, "", validator = float_validator(minimum = lambda: float(self.from_wavelength_box.GetValue()), include_minimum = False, condition = lambda: self.wavelength_range_button.GetValue() and self.from_wavelength_box.GetValidator().Validate(self.from_wavelength_box)))
		self.by_wavelength_box = wx.TextCtrl(self, -1, "", validator = float_validator(minimum = 0.0, include_minimum = False, condition = self.wavelength_range_button.GetValue))
		
		self.from_wavelength_box.Bind(wx.EVT_TEXT, self.on_wavelength_range_box)
		self.to_wavelength_box.Bind(wx.EVT_TEXT, self.on_wavelength_range_box)
		self.by_wavelength_box.Bind(wx.EVT_TEXT, self.on_wavelength_range_box)
		
		# Arrange them in a sizer.
		wavelengths_sizer = wx.BoxSizer(wx.HORIZONTAL)
		wavelengths_sizer.Add(wx.StaticText(self, -1, "Wavelengths:"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		wavelengths_sizer.Add(self.wavelength_range_button,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(self.from_wavelength_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(wx.StaticText(self, -1, "to"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(self.to_wavelength_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(wx.StaticText(self, -1, "by"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(self.by_wavelength_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(wx.StaticText(self, -1, "nm"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer.Add(self.wavelength_point_button,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		# Add it to the content sizer.
		self.content_sizer.Add(wavelengths_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_definition_grid                                                #
	#                                                                    #
	######################################################################
	def add_definition_grid(self):
		"""Add a definition grid to the dialog"""
		
		# A box to specify the nb of points in the definition.
		self.nb_points_box = wx.TextCtrl(self, -1, "", validator = int_validator(1, None))
		self.nb_points_box.Bind(wx.EVT_TEXT_ENTER, self.on_nb_points)
		self.nb_points_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_points)
		
		# Add a table to specify the wavelengths, the values and the
		# tolerances at the points.
		self.points_grid = wx.grid.Grid(self, -1, size = (400, 100), style = wx.SUNKEN_BORDER)
		self.points_grid.CreateGrid(0, 3)
		self.points_grid.SetColSize(0, 80)
		self.points_grid.SetColLabelValue(0, "Wavelength")
		self.points_grid.SetColSize(1, 80)
		self.points_grid.SetColLabelValue(1, self.data_column_title)
		self.points_grid.SetColSize(2, 80)
		self.points_grid.SetColLabelValue(2, self.delta_column_title)
		
		self.points_grid.SetValidator(target_point_grid_validator(self.min_value, self.max_value))
		
		# Put the nb points box in a sizer.
		nb_points_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_points_sizer.Add(wx.StaticText(self, -1, "Nb definition points:"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_points_sizer.Add(self.nb_points_box,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.content_sizer.Add(nb_points_sizer, 0, wx.EXPAND|wx.TOP, 5)
		self.content_sizer.Add(self.points_grid, 0, wx.EXPAND|wx.TOP, 10)
	
	
	######################################################################
	#                                                                    #
	# add_illuminant_and_observer_choices                                #
	#                                                                    #
	######################################################################
	def add_illuminant_and_observer_choices(self):
		"""Add illuminant and observer choices to the dialog"""
		
		# Choices for the illuminant and the observer.
		self.illuminant_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_illuminant_names())
		self.observer_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_observer_names())
		
		# Arrange them in a sizer.
		illuminant_and_observer_sizer = wx.BoxSizer(wx.HORIZONTAL)
		illuminant_and_observer_sizer.Add(wx.StaticText(self, -1, "Illuminant:"),
		                                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		illuminant_and_observer_sizer.Add(self.illuminant_choice,
		                                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		illuminant_and_observer_sizer.Add(wx.StaticText(self, -1, "Observer:"),
		                                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		illuminant_and_observer_sizer.Add(self.observer_choice,
		                                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Put in in the content sizer.
		self.content_sizer.Add(illuminant_and_observer_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_color_buttons_and_boxes                                        #
	#                                                                    #
	######################################################################
	def add_color_buttons_and_boxes(self):
		"""Add color buttons and boxes to the dialog"""
		
		# Radio buttons to specify the color space.
		self.XYZ_button = wx.RadioButton(self, -1, "XYZ", style = wx.RB_GROUP)
		self.xyY_button = wx.RadioButton(self, -1, "xyY")
		self.Luv_button = wx.RadioButton(self, -1, "L*u*v*")
		self.Lab_button = wx.RadioButton(self, -1, "L*a*b*")
		self.LChuv_button = wx.RadioButton(self, -1, "L*C*h(u*v*)")
		self.LChab_button = wx.RadioButton(self, -1, "L*C*h(a*b*)")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.XYZ_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.xyY_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.Luv_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.Lab_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.LChuv_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_color_space, self.LChab_button)
		
		# 3 boxes to specify the color and 3 more for the tolerances. The
		# content of the boxes will depend on the color space.
		self.first_text = wx.StaticText(self, -1, "", size = (25, -1), style = wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
		self.second_text = wx.StaticText(self, -1, "", size = (25, -1), style = wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
		self.third_text = wx.StaticText(self, -1, "", size = (25, -1), style = wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
		self.first_box = wx.TextCtrl(self, -1, "")
		self.second_box = wx.TextCtrl(self, -1, "")
		self.third_box = wx.TextCtrl(self, -1, "")
		try:
			self.first_pm = wx.StaticText(self, -1, "±")
			self.second_pm = wx.StaticText(self, -1, "±")
			self.third_pm = wx.StaticText(self, -1, "±")
		except UnicodeDecodeError:
			self.first_pm = wx.StaticText(self, -1, "+-")
			self.second_pm = wx.StaticText(self, -1, "+-")
			self.third_pm = wx.StaticText(self, -1, "+-")
		self.delta_first_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None, include_minimum = False))
		self.delta_second_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None, include_minimum = False))
		self.delta_third_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None, include_minimum = False))
		
		# Arrange everything in sizers.
		color_space_sizer = wx.BoxSizer(wx.VERTICAL)
		color_space_sizer.Add(self.XYZ_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		color_space_sizer.Add(self.xyY_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		color_space_sizer.Add(self.Luv_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		color_space_sizer.Add(self.Lab_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		color_space_sizer.Add(self.LChuv_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		color_space_sizer.Add(self.LChab_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		first_sizer = wx.BoxSizer(wx.HORIZONTAL)
		second_sizer = wx.BoxSizer(wx.HORIZONTAL)
		third_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		first_sizer.Add(self.first_text, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		first_sizer.Add(self.first_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		first_sizer.Add(self.first_pm, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		first_sizer.Add(self.delta_first_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		second_sizer.Add(self.second_text, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		second_sizer.Add(self.second_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		second_sizer.Add(self.second_pm, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		second_sizer.Add(self.delta_second_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		third_sizer.Add(self.third_text, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		third_sizer.Add(self.third_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		third_sizer.Add(self.third_pm, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		third_sizer.Add(self.delta_third_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		value_sizer = wx.BoxSizer(wx.VERTICAL)
		value_sizer.Add(first_sizer, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		value_sizer.Add(second_sizer, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		value_sizer.Add(third_sizer, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		color_sizer = wx.BoxSizer(wx.HORIZONTAL)
		color_sizer.Add(color_space_sizer, 0, wx.ALIGN_LEFT)
		color_sizer.Add(value_sizer, 0, wx.ALIGN_LEFT|wx.LEFT, 40)
		
		# Add it to the content sizer.
		self.content_sizer.Add(color_sizer, 0, wx.EXPAND|wx.TOP, 10)
	
	
	######################################################################
	#                                                                    #
	# add_inequality_choice                                              #
	#                                                                    #
	######################################################################
	def add_inequality_choice(self):
		"""Add inequality radio buttons to the dialog"""
		
		self.smaller_button = wx.RadioButton(self, -1, "smaller than", style = wx.RB_GROUP)
		self.equal_button = wx.RadioButton(self, -1, "equal to")
		self.larger_button = wx.RadioButton(self, -1, "larger than")
		
		# Arrange it in a sizer.
		inequality_sizer = wx.BoxSizer(wx.HORIZONTAL)
		inequality_sizer.Add(wx.StaticText(self, -1, "Condition:"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		inequality_sizer.Add(self.smaller_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		inequality_sizer.Add(self.equal_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		inequality_sizer.Add(self.larger_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add it to the content sizer.
		self.content_sizer.Add(inequality_sizer, 0, wx.EXPAND|wx.TOP, 5)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content to the dialog
		
		This method takes care of the arangement of controls specific to
		kind of target. It must be implemented by the derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add the ok and cancel buttons to the dialog"""
		
		# Create buttons.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK), 0)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.LEFT, 20)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 20)
		
		
	######################################################################
	#                                                                    #
	# on_polarization_radio_button                                       #
	#                                                                    #
	######################################################################
	def on_polarization_radio_button(self, event):
		"""Handle the selection of a polarization radio button
		
		This method takes a single argument:
		  event              the event."""
		
		# When an a polarization is selected (except if it is the other
		# polarization), empty the other polarization box.
		if self.allow_arbitrary_polarization and not self.other_polarizations_button.GetValue():
			self.other_polarizations_box.Clear()
	
	
	######################################################################
	#                                                                    #
	# on_other_polarizations_box                                         #
	#                                                                    #
	######################################################################
	def on_other_polarizations_box(self, event):
		"""Handle text events related to the other polarization box
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in the other polarizations box,
		# automatically select the other polarization button.
		if self.other_polarizations_box.GetValue() != "":
			self.other_polarizations_button.SetValue(True)
		
		
	######################################################################
	#                                                                    #
	# on_wavelength_range_radio_button                                   #
	#                                                                    #
	######################################################################
	def on_wavelength_range_radio_button(self, event):
		"""Handle the selection of the wavelength range or the wavelength points radio button
		
		This method takes a single argument:
		  event              the event."""
		
		# When the wavelength point button is selected, clear the wavelength
		# range boxes.
		if self.wavelength_point_button.GetValue():
			self.from_wavelength_box.Clear()
			self.to_wavelength_box.Clear()
			self.by_wavelength_box.Clear()
	
	
	######################################################################
	#                                                                    #
	# on_wavelength_range_box                                            #
	#                                                                    #
	######################################################################
	def on_wavelength_range_box(self, event):
		"""Handle text events related to the wavelength range boxes
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in any of the wavelength range boxes,
		# automatically select the wavelength range button.
		if event.GetEventObject().GetValue():
			self.wavelength_range_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# on_nb_points                                                       #
	#                                                                    #
	######################################################################
	def on_nb_points(self, event):
		"""Handle text events for the number of points box
		
		This method takes a single argument:
		  event              the event."""
		
		nb_points = int(self.nb_points_box.GetValue())
		
		nb_rows = self.points_grid.GetNumberRows()
		
		if nb_points > nb_rows:
			self.points_grid.AppendRows(nb_points-nb_rows)
		elif nb_points < nb_rows:
			self.points_grid.DeleteRows(nb_points, nb_rows-nb_points)
	
	
	######################################################################
	#                                                                    #
	# change_color_space                                                 #
	#                                                                    #
	######################################################################
	def change_color_space(self, color_space):
		"""Convert the color description when the color space is changed
		
		This method takes a single argument:
		  color_space        the newly selected color space."""
		
		# If the color space is identical to the previous choice, don't do
		# anything.
		if color_space == self.color_space:
			return
		
		# Calculate the white point according to the illuminant and
		# observer.
		illuminant_name, observer_name = self.get_illuminant_and_observer()
		observer = color.get_observer(observer_name)
		illuminant = color.get_illuminant(illuminant_name)
		XYZ_n = color.white_point(observer, illuminant)
		
		# Remember the previous color space to allow conversion.
		old_color_space = self.color_space
		self.color_space = color_space
		
		# Try to interpret the color.
		try:
			first_term = float(self.first_box.GetValue())
			second_term = float(self.second_box.GetValue())
			third_term = float(self.third_box.GetValue())
			old_color = [first_term, second_term, third_term]
		except ValueError:
			old_color = None
		
		# Convert to the new color space, when possible.
		if old_color_space and old_color:
			new_color = color.change_color_space(old_color_space, self.color_space, old_color, XYZ_n)
		else:
			new_color = None
		
		if color_space == color.XYZ:
			self.first_text.SetLabel("X:")
			self.second_text.SetLabel("Y:")
			self.third_text.SetLabel("Z:")
			self.first_box.SetValidator(float_validator(0.0, None))
			self.second_box.SetValidator(float_validator(0.0, 100.0))
			self.third_box.SetValidator(float_validator(0.0, None))
		elif color_space == color.xyY:
			self.first_text.SetLabel("x:")
			self.second_text.SetLabel("y:")
			self.third_text.SetLabel("Y:")
			self.first_box.SetValidator(float_validator(0.0, 1.0))
			self.second_box.SetValidator(float_validator(0.0, 1.0))
			self.third_box.SetValidator(float_validator(0.0, 100.0))
		elif color_space == color.Luv:
			self.first_text.SetLabel("L*:")
			self.second_text.SetLabel("u*:")
			self.third_text.SetLabel("v*:")
			self.first_box.SetValidator(float_validator(0.0, 100.0))
			self.second_box.SetValidator(float_validator(None, None))
			self.third_box.SetValidator(float_validator(None, None))
		elif color_space == color.Lab:
			self.first_text.SetLabel("L*:")
			self.second_text.SetLabel("a*:")
			self.third_text.SetLabel("b*:")
			self.first_box.SetValidator(float_validator(0.0, 100.0))
			self.second_box.SetValidator(float_validator(None, None))
			self.third_box.SetValidator(float_validator(None, None))
		elif color_space == color.LChuv:
			self.first_text.SetLabel("L*:")
			self.second_text.SetLabel("C*:")
			self.third_text.SetLabel("h:")
			self.first_box.SetValidator(float_validator(0.0, 100.0))
			self.second_box.SetValidator(float_validator(None, None))
			self.third_box.SetValidator(float_validator(None, None))
		elif color_space == color.LChab:
			self.first_text.SetLabel("L*:")
			self.second_text.SetLabel("C*:")
			self.third_text.SetLabel("h:")
			self.first_box.SetValidator(float_validator(0.0, 100.0))
			self.second_box.SetValidator(float_validator(None, None))
			self.third_box.SetValidator(float_validator(None, None))
		
		if new_color:
			self.first_box.SetValue("%s" % new_color[0])
			self.second_box.SetValue("%s" % new_color[1])
			self.third_box.SetValue("%s" % new_color[2])
	
	
	######################################################################
	#                                                                    #
	# on_color_space                                                     #
	#                                                                    #
	######################################################################
	def on_color_space(self, event):
		"""Handle the selection of a color space button
		
		This method takes a single argument:
		  event              the event."""
		
		if self.XYZ_button.GetValue():
			self.change_color_space(color.XYZ)
		elif self.xyY_button.GetValue():
			self.change_color_space(color.xyY)
		elif self.Luv_button.GetValue():
			self.change_color_space(color.Luv)
		elif self.Lab_button.GetValue():
			self.change_color_space(color.Lab)
		elif self.LChuv_button.GetValue():
			self.change_color_space(color.LChuv)
		elif self.LChab_button.GetValue():
			self.change_color_space(color.LChab)
	
	
	######################################################################
	#                                                                    #
	# set_angle                                                          #
	#                                                                    #
	######################################################################
	def set_angle(self, angle):
		"""Set the angle box
		
		This method takes a single argument:
		  angle              the angle."""
		
		self.angle_box.SetValue("%s" % angle)
	
	
	######################################################################
	#                                                                    #
	# get_angle                                                          #
	#                                                                    #
	######################################################################
	def get_angle(self):
		"""Get the content of the angle box
		
		This method returns the content of the angle box as a float."""
		
		return float(self.angle_box.GetValue())
	
	
	######################################################################
	#                                                                    #
	# set_polarization                                                   #
	#                                                                    #
	######################################################################
	def set_polarization(self, polarization):
		"""Set the polarization
		
		This method takes a single argument:
		  polarization       the polarization."""
		
		if polarization == S:
			self.s_polarized_button.SetValue(True)
			if self.allow_arbitrary_polarization:
				self.other_polarizations_box.Clear()
		elif polarization == P:
			self.p_polarized_button.SetValue(True)
			if self.allow_arbitrary_polarization:
				self.other_polarizations_box.Clear()
		elif polarization == UNPOLARIZED:
			self.unpolarized_button.SetValue(True)
			self.other_polarizations_box.Clear()
		else:
			self.other_polarizations_button.SetValue(True)
			self.other_polarizations_box.SetValue("%s" %polarization)
	
	
	######################################################################
	#                                                                    #
	# get_polarization                                                   #
	#                                                                    #
	######################################################################
	def get_polarization(self):
		"""Get the polarization
		
		The method returns the polarization defined by the polarization
		bottons and box as a float."""
		
		if self.s_polarized_button.GetValue():
			return S
		if self.p_polarized_button.GetValue():
			return P
		if self.unpolarized_button.GetValue():
			return UNPOLARIZED
		if self.other_polarizations_button.GetValue():
			return float(self.other_polarizations_box.GetValue())
	
	
	######################################################################
	#                                                                    #
	# set_direction                                                      #
	#                                                                    #
	######################################################################
	def set_direction(self, direction):
		"""Set the direction
		
		This method takes a single argument:
		  direction          the direction."""
		
		if direction == FORWARD:
			self.normal_direction_button.SetValue(True)
		else:
			self.reverse_direction_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_direction                                                      #
	#                                                                    #
	######################################################################
	def get_direction(self):
		"""Get the direction
		
		This method returns the direction as a integer."""
		
		if self.normal_direction_button.GetValue():
			return FORWARD
		else:
			return BACKWARD
	
	
	######################################################################
	#                                                                    #
	# set_wavelength                                                     #
	#                                                                    #
	######################################################################
	def set_wavelength(self, wavelength):
		"""Set the wavelength
		
		This method takes a single argument:
		  wavelength         the wavelength."""
		
		self.wavelength_box.SetValue("%s" % wavelength)
	
	
	######################################################################
	#                                                                    #
	# get_wavelength                                                     #
	#                                                                    #
	######################################################################
	def get_wavelength(self):
		"""Get the wavelength
		
		This method returns the content of the wavelength box as a float."""
		
		return float(self.wavelength_box.GetValue())
	
	
	######################################################################
	#                                                                    #
	# set_value                                                          #
	#                                                                    #
	######################################################################
	def set_value(self, value):
		"""Set the value of a single value target
		
		This method takes a single argument:
		  value              the value."""
		
		self.value_box.SetValue("%s" % (value*self.multiplicative_factor))
	
	
	######################################################################
	#                                                                    #
	# get_value                                                          #
	#                                                                    #
	######################################################################
	def get_value(self):
		"""Get the value of a single value target
		
		This method returns the value of a single value target as a float."""
		
		return float(self.value_box.GetValue())/self.multiplicative_factor
	
	
	######################################################################
	#                                                                    #
	# set_tolerance                                                      #
	#                                                                    #
	######################################################################
	def set_tolerance(self, tolerance):
		"""Set the tolerance
		
		This method takes a single argument:
		  tolerance          the tolerance."""
		
		self.tolerance_box.SetValue("%s" % (tolerance*self.multiplicative_factor))
	
	
	######################################################################
	#                                                                    #
	# get_tolerance                                                      #
	#                                                                    #
	######################################################################
	def get_tolerance(self):
		"""Get the tolerance
		
		This method returns the value of the tolerance as a float."""
		
		return float(self.tolerance_box.GetValue())/self.multiplicative_factor
	
	
	######################################################################
	#                                                                    #
	# set_wavelength_range                                               #
	#                                                                    #
	######################################################################
	def set_wavelength_range(self, from_wavelength, to_wavelength, by_wavelength):
		"""Set the wavelength range
		
		This method takes 3 arguments:
		  from_wavelength    the inferior limit of the wavelength range;
		  to_wavelength      the superior limit of the wavelength range;
		  by_wavelength      the spacing inside the wavelength range."""
		
		if by_wavelength:
			self.wavelength_range_button.SetValue(True)
			self.from_wavelength_box.SetValue("%s" % from_wavelength)
			self.to_wavelength_box.SetValue("%s" % to_wavelength)
			self.by_wavelength_box.SetValue("%s" % by_wavelength)
		else:
			self.wavelength_point_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_wavelength_range                                               #
	#                                                                    #
	######################################################################
	def get_wavelength_range(self):
		"""Get the wavelength range
		
		This method returns 3 float arguments:
		  from_wavelength    the inferior limit of the wavelength range;
		  to_wavelength      the superior limit of the wavelength range;
		  by_wavelength      the spacing inside the wavelength range."""
		
		if self.wavelength_range_button.GetValue():
			from_wavelength = float(self.from_wavelength_box.GetValue())
			to_wavelength = float(self.to_wavelength_box.GetValue())
			by_wavelength = float(self.by_wavelength_box.GetValue())
		else:
			from_wavelength = 0.0
			to_wavelength = 0.0
			by_wavelength = 0.0
		
		return from_wavelength, to_wavelength, by_wavelength
	
	
	######################################################################
	#                                                                    #
	# set_definition_grid                                                #
	#                                                                    #
	######################################################################
	def set_definition_grid(self, wavelengths, values, tolerances):
		"""Set the target definition grid
		
		This method takes 3 arguments:
		  wavelengths        a list of the wavelengths;
		  values             a list of the values;
		  tolerances         a list of the tolerances."""
		
		nb_wvls = len(wavelengths)
		
		self.nb_points_box.SetValue("%s" % nb_wvls)
		self.points_grid.AppendRows(nb_wvls)
		
		for i in range(nb_wvls):
			self.points_grid.SetCellValue(i, 0, "%s" % wavelengths[i])
			self.points_grid.SetCellValue(i, 1, "%s" % (values[i]*self.multiplicative_factor))
			self.points_grid.SetCellValue(i, 2, "%s" % (tolerances[i]*self.multiplicative_factor))
	
	
	######################################################################
	#                                                                    #
	# get_definition_grid                                                #
	#                                                                    #
	######################################################################
	def get_definition_grid(self):
		"""Get the target definition grid
		
		This method returns 3 arguments:
		  wavelengths        a list of the wavelengths;
		  values             a list of the values;
		  tolerances         a list of the tolerances."""
		
		nb_rows = self.points_grid.GetNumberRows()
		
		wavelengths = [float(self.points_grid.GetCellValue(i, 0)) for i in range(nb_rows)]
		values = [float(self.points_grid.GetCellValue(i, 1))/self.multiplicative_factor for i in range(nb_rows)]
		tolerances = [float(self.points_grid.GetCellValue(i, 2))/self.multiplicative_factor for i in range(nb_rows)]
		
		return wavelengths, values, tolerances
	
	
	######################################################################
	#                                                                    #
	# set_illuminant_and_observer                                        #
	#                                                                    #
	######################################################################
	def set_illuminant_and_observer(self, illuminant_name, observer_name):
		"""Set the illuminant and observer
		
		This method takes 2 arguments:
		  illuminant_name    the name of the illuminant;
		  observer_name      the name of the observer."""
		
		self.illuminant_choice.SetSelection(self.illuminant_choice.FindString(illuminant_name))
		self.observer_choice.SetSelection(self.observer_choice.FindString(observer_name))
	
	
	######################################################################
	#                                                                    #
	# get_illuminant_and_observer                                        #
	#                                                                    #
	######################################################################
	def get_illuminant_and_observer(self):
		"""Get the illuminant and observer
		
		This method returns 2 arguments:
		  illuminant_name    the name of the illuminant;
		  observer_name      the name of the observer."""
		
		illuminant_name = self.illuminant_choice.GetStringSelection()
		observer_name = self.observer_choice.GetStringSelection()
		
		return illuminant_name, observer_name
	
	
	######################################################################
	#                                                                    #
	# set_color_space                                                    #
	#                                                                    #
	######################################################################
	def set_color_space(self, color_space):
		"""Set the color space
		
		This method takes 1 argument:
		  color_space        the color space."""
		
		if color_space == color.XYZ:
			self.XYZ_button.SetValue(True)
		elif color_space == color.xyY:
			self.xyY_button.SetValue(True)
		elif color_space == color.Luv:
			self.Luv_button.SetValue(True)
		elif color_space == color.Lab:
			self.Lab_button.SetValue(True)
		elif color_space == color.LChuv:
			self.LChuv_button.SetValue(True)
		elif color_space == color.LChab:
			self.LChab_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_color_space                                                    #
	#                                                                    #
	######################################################################
	def get_color_space(self):
		"""Set the color space
		
		This method returns 1 argument:
		  color_space        the color space."""
		
		return self.color_space
	
	
	######################################################################
	#                                                                    #
	# set_color_and_tolerance                                            #
	#                                                                    #
	######################################################################
	def set_color_and_tolerance(self, values, tolerances):
		"""Set the color and its tolerance
		
		This method takes 1 argument:
		  color_space        the color space."""
		
		self.first_box.SetValue("%s" % values[0])
		self.delta_first_box.SetValue("%s" % tolerances[0])
		self.second_box.SetValue("%s" % values[1])
		self.delta_second_box.SetValue("%s" % tolerances[1])
		self.third_box.SetValue("%s" % values[2])
		self.delta_third_box.SetValue("%s" % tolerances[2])
	
	
	######################################################################
	#                                                                    #
	# get_color_and_tolerance                                            #
	#                                                                    #
	######################################################################
	def get_color_and_tolerance(self):
		"""Set the color and its tolerance
		
		This method returns 1 argument:
		  color_space        the color space."""
		
		value_1 = float(self.first_box.GetValue())
		value_2 = float(self.second_box.GetValue())
		value_3 = float(self.third_box.GetValue())
		delta_1 = float(self.delta_first_box.GetValue())
		delta_2 = float(self.delta_second_box.GetValue())
		delta_3 = float(self.delta_third_box.GetValue())
		values = [value_1, value_2, value_3]
		tolerances = [delta_1, delta_2, delta_3]
		
		return values, tolerances
	
	
	######################################################################
	#                                                                    #
	# set_inequality                                                     #
	#                                                                    #
	######################################################################
	def set_inequality(self, inequality):
		"""Set the inequality
		
		This method takes 1 argument:
		  inequality         the inequality."""
		
		if inequality == targets.SMALLER:
			self.smaller_button.SetValue(True)
		elif inequality == targets.EQUAL:
			self.equal_button.SetValue(True)
		elif inequality == targets.LARGER:
			self.larger_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_inequality                                                     #
	#                                                                    #
	######################################################################
	def get_inequality(self):
		"""Get the inequality
		
		This method returns 1 argument:
		  inequality        the inequality."""
		
		if self.smaller_button.GetValue():
			return targets.SMALLER
		if self.equal_button.GetValue():
			return targets.EQUAL
		if self.larger_button.GetValue():
			return targets.LARGER
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self):
		"""Get the target
		
		This method returns the target defined by the dialog. It must be
		defined by the target specific subclasses."""
		
		raise NotImplementedError("Subclass must implement this method")



########################################################################
#                                                                      #
# discrete_target_dialog                                               #
#                                                                      #
########################################################################
class discrete_target_dialog(target_dialog):
	"""A base class for all discrete target dialogs
	
	This class provides a common architecture for all discrete target
	dialogs. It must be subclassed to actually be used."""
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content specific to discrete targets to the dialog"""
		
		# Put the angle, polarization, direction, wavelength, value and
		# inequality controls.
		self.add_angle_box()
		self.add_polarization_choice()
		if self.allow_direction:
			self.add_direction_choice()
		self.add_wavelength_box()
		self.add_value_and_tolerance_boxes()
		self.add_inequality_choice()
		
		if self.target:
			angle = self.target.get_angle()
			polarization = self.target.get_polarization()
			if self.allow_direction:
				direction = self.target.get_direction()
			wavelength, value, tolerance = self.target.get_values()
			inequality = self.target.get_inequality()
			
			self.set_angle(angle)
			self.set_polarization(polarization)
			if self.allow_direction:
				self.set_direction(direction)
			self.set_wavelength(wavelength[0])
			self.set_value(value[0])
			self.set_tolerance(tolerance[0])
			self.set_inequality(inequality)
		else:
			# Set default values
			self.set_angle(0.0)
			self.set_polarization(S)
			if self.allow_direction:
				self.set_direction(FORWARD)
			self.set_inequality(targets.EQUAL)
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self):
		"""Get the target
		
		This method returns the target defined by the dialog."""
		
		if self.target is None:
			self.target = self.target_class()
		
		angle = self.get_angle()
		polarization = self.get_polarization()
		if self.allow_direction:
			direction = self.get_direction()
		wavelength = self.get_wavelength()
		value = self.get_value()
		tolerance = self.get_tolerance()
		inequality = self.get_inequality()
		
		self.target.set_angle(angle)
		self.target.set_polarization(polarization)
		if self.allow_direction:
			self.target.set_direction(direction)
		self.target.set_target(wavelength, value, tolerance)
		self.target.set_inequality(inequality)
		
		return self.target



########################################################################
#                                                                      #
# spectrum_target_dialog                                               #
#                                                                      #
########################################################################
class spectrum_target_dialog(target_dialog):
	"""A base class for all spectrum target dialogs
	
	This class provides a common architecture for all spectrum target
	dialogs. It must be subclassed to actually be used."""
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content specific to reflection spectrum targets to the
		dialog"""
		
		# Put the angle, polarization, direction, wavelength range, grid
		# and inequality controls.
		self.add_angle_box()
		self.add_polarization_choice()
		if self.allow_direction:
			self.add_direction_choice()
		self.add_wavelength_range_boxes()
		self.add_definition_grid()
		self.add_inequality_choice()
		
		if self.target:
			angle = self.target.get_angle()
			polarization = self.target.get_polarization()
			if self.allow_direction:
				direction = self.target.get_direction()
			from_wavelength, to_wavelength, by_wavelength, wavelengths, values, deltas = self.target.get_points()
			inequality = self.target.get_inequality()
			
			self.set_angle(angle)
			self.set_polarization(polarization)
			if self.allow_direction:
				self.set_direction(direction)
			self.set_wavelength_range(from_wavelength, to_wavelength, by_wavelength)
			self.set_definition_grid(wavelengths, values, deltas)
			self.set_inequality(inequality)
		else:
			# Set default values
			nb_points = 1
			self.set_angle(0.0)
			self.set_polarization(S)
			if self.allow_direction:
				self.set_direction(FORWARD)
			self.wavelength_range_button.SetValue(True)
			self.nb_points_box.SetValue("%s" % nb_points)
			self.points_grid.AppendRows(nb_points)
			self.set_inequality(targets.EQUAL)
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self):
		"""Get the target
		
		This method returns the target defined by the dialog."""
		
		if self.target is None:
			self.target = self.target_class()
		
		angle = self.get_angle()
		polarization = self.get_polarization()
		if self.allow_direction:
			direction = self.get_direction()
		from_wavelength, to_wavelength, by_wavelength = self.get_wavelength_range()
		wavelengths, values, deltas = self.get_definition_grid()
		inequality = self.get_inequality()
		
		self.target.set_angle(angle)
		self.target.set_polarization(polarization)
		if self.allow_direction:
			self.target.set_direction(direction)
		self.target.set_target(from_wavelength, to_wavelength, by_wavelength, wavelengths, values, deltas)
		self.target.set_inequality(inequality)
		
		return self.target



########################################################################
#                                                                      #
# color_target_dialog                                                  #
#                                                                      #
########################################################################
class color_target_dialog(target_dialog):
	"""A base class for all color target dialogs
	
	This class provides a common architecture for all color target
	dialogs. It must be subclassed to actually be used."""
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content specific to reflection color targets to the
		dialog"""
		
		# Put the angle, direction, illuminant, observer and color
		# controls.
		self.add_angle_box()
		self.add_polarization_choice()
		if self.allow_direction:
			self.add_direction_choice()
		self.add_illuminant_and_observer_choices()
		self.add_color_buttons_and_boxes()
		
		self.color_space = None
		
		if self.target:
			angle = self.target.get_angle()
			polarization = self.target.get_polarization()
			if self.allow_direction:
				direction = self.target.get_direction()
			illuminant_name, observer_name = self.target.get_illuminant_and_observer()
			color_space = self.target.get_color_space()
			values, tolerances = self.target.get_values()
			
			self.set_angle(angle)
			self.set_polarization(polarization)
			if self.allow_direction:
				self.set_direction(direction)
			self.set_illuminant_and_observer(illuminant_name, observer_name)
			self.change_color_space(color_space)
			self.set_color_space(color_space)
			self.set_color_and_tolerance(values, tolerances)
		else:
			# Set default values
			self.set_angle(0.0)
			self.set_polarization(UNPOLARIZED)
			if self.allow_direction:
				self.set_direction(FORWARD)
			self.set_illuminant_and_observer(config.ILLUMINANT, config.OBSERVER)
			self.change_color_space(color.XYZ)
			self.set_color_space(color.XYZ)
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self):
		"""Get the target
		
		This method returns the target defined by the dialog."""
		
		if self.target is None:
			self.target = self.target_class()
		
		angle = self.get_angle()
		polarization = self.get_polarization()
		if self.allow_direction:
			direction = self.get_direction()
		illuminant_name, observer_name = self.get_illuminant_and_observer()
		color_space = self.get_color_space()
		values, tolerances = self.get_color_and_tolerance()
		
		self.target.set_angle(angle)
		self.target.set_polarization(polarization)
		if self.allow_direction:
			self.target.set_direction(direction)
		self.target.set_illuminant_and_observer(illuminant_name, observer_name)
		self.target.set_target(color_space, values, tolerances)
		
		return self.target



########################################################################
#                                                                      #
# reflection_target_dialog                                             #
#                                                                      #
########################################################################
class reflection_target_dialog(discrete_target_dialog):
	"""A dialog to define a reflection target"""
	
	target_class = targets.reflection_target
	
	title = "Set Reflection Target"
	value_title = "R"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# transmission_target_dialog                                           #
#                                                                      #
########################################################################
class transmission_target_dialog(discrete_target_dialog):
	"""A dialog to define a transmission target"""
	
	target_class = targets.transmission_target
	
	title = "Set Transmission Target"
	value_title = "T"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# absorption_target_dialog                                             #
#                                                                      #
########################################################################
class absorption_target_dialog(discrete_target_dialog):
	"""A dialog to define a absorption target"""
	
	target_class = targets.absorption_target
	
	title = "Set Absorption Target"
	value_title = "A"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# reflection_spectrum_target_dialog                                    #
#                                                                      #
########################################################################
class reflection_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a reflection spectrum target"""
	
	target_class = targets.reflection_spectrum_target
	
	title = "Set Reflection Spectrum Target"
	data_column_title = "R"
	delta_column_title = "Delta R"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# transmission_spectrum_target_dialog                                  #
#                                                                      #
########################################################################
class transmission_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a transmission spectrum target"""
	
	target_class = targets.transmission_spectrum_target
	
	title = "Set Transmission Spectrum Target"
	data_column_title = "T"
	delta_column_title = "Delta T"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# absorption_spectrum_target_dialog                                    #
#                                                                      #
########################################################################
class absorption_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a absorption spectrum target"""
	
	target_class = targets.absorption_spectrum_target
	
	title = "Set Absorption Spectrum Target"
	data_column_title = "A"
	delta_column_title = "Delta A"
	min_value = 0.0
	max_value = 1.0



########################################################################
#                                                                      #
# reflection_phase_target_dialog                                       #
#                                                                      #
########################################################################
class reflection_phase_target_dialog(discrete_target_dialog):
	"""A dialog to define a reflection phase target"""
	
	target_class = targets.reflection_phase_target
	
	title = "Set Reflection Phase Target"
	value_title = "phi_r"
	units = "degrees"
	min_value = 0.0
	max_value = 360.0



########################################################################
#                                                                      #
# transmission_phase_target_dialog                                     #
#                                                                      #
########################################################################
class transmission_phase_target_dialog(discrete_target_dialog):
	"""A dialog to define a transmission phase target"""
	
	target_class = targets.transmission_phase_target
	
	title = "Set Transmission Phase Target"
	value_title = "phi_t"
	units = "degrees"
	min_value = 0.0
	max_value = 360.0



########################################################################
#                                                                      #
# reflection_GD_target_dialog                                          #
#                                                                      #
########################################################################
class reflection_GD_target_dialog(discrete_target_dialog):
	"""A dialog to define a reflection GD target"""
	
	target_class = targets.reflection_GD_target
	
	title = "Set Reflection GD Target"
	value_title = "GD_r"
	units = "fs"
	multiplicative_factor = 1.0e15



########################################################################
#                                                                      #
# transmission_GD_target_dialog                                        #
#                                                                      #
########################################################################
class transmission_GD_target_dialog(discrete_target_dialog):
	"""A dialog to define a transmission GD target"""
	
	target_class = targets.transmission_GD_target
	
	title = "Set Transmission GD Target"
	value_title = "GD_t"
	units = "fs"
	multiplicative_factor = 1.0e15
	min_value = 0.0



########################################################################
#                                                                      #
# reflection_GDD_target_dialog                                         #
#                                                                      #
########################################################################
class reflection_GDD_target_dialog(discrete_target_dialog):
	"""A dialog to define a reflection GDD target"""
	
	target_class = targets.reflection_GDD_target
	
	title = "Set Reflection GDD Target"
	value_title = "GDD_r"
	units = "fs^2"
	multiplicative_factor = 1.0e30



########################################################################
#                                                                      #
# transmission_GDD_target_dialog                                       #
#                                                                      #
########################################################################
class transmission_GDD_target_dialog(discrete_target_dialog):
	"""A dialog to define a transmission GDD target"""
	
	target_class = targets.transmission_GDD_target
	
	title = "Set Transmission GDD Target"
	value_title = "GDD_t"
	units = "fs^2"
	multiplicative_factor = 1.0e30



########################################################################
#                                                                      #
# reflection_phase_spectrum_target_dialog                              #
#                                                                      #
########################################################################
class reflection_phase_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a reflection phase spectrum target"""
	
	target_class = targets.reflection_phase_spectrum_target
	
	title = "Set Reflection Phase Spectrum Target"
	data_column_title = "phi_r\n(degrees)"
	delta_column_title = "Delta phi_r\n(degrees)"
	min_value = 0.0
	max_value = 360.0



########################################################################
#                                                                      #
# transmission_phase_spectrum_target_dialog                            #
#                                                                      #
########################################################################
class transmission_phase_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a transmission phase spectrum target"""
	
	target_class = targets.transmission_phase_spectrum_target
	
	title = "Set Transmission Phase Spectrum Target"
	data_column_title = "phi_t\n(degrees)"
	delta_column_title = "Delta phi_t\n(degrees)"
	min_value = 0.0
	max_value = 360.0



########################################################################
#                                                                      #
# reflection_GD_spectrum_target_dialog                                 #
#                                                                      #
########################################################################
class reflection_GD_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a reflection GD spectrum target"""
	
	target_class = targets.reflection_GD_spectrum_target
	
	title = "Set Reflection GD Spectrum Target"
	data_column_title = "GD_r\n(fs)"
	delta_column_title = "Delta GD_r\n(fs)"
	multiplicative_factor = 1.0e15



########################################################################
#                                                                      #
# transmission_GD_spectrum_target_dialog                               #
#                                                                      #
########################################################################
class transmission_GD_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a transmission GD spectrum target"""
	
	target_class = targets.transmission_GD_spectrum_target
	
	title = "Set Transmission GD Spectrum Target"
	data_column_title = "GD_t\n(fs)"
	delta_column_title = "Delta GD_t\n(fs)"
	multiplicative_factor = 1.0e15
	min_value = 0.0



########################################################################
#                                                                      #
# reflection_GDD_spectrum_target_dialog                                #
#                                                                      #
########################################################################
class reflection_GDD_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a reflection GDD spectrum target"""
	
	target_class = targets.reflection_GDD_spectrum_target
	
	title = "Set Reflection GDD Spectrum Target"
	data_column_title = "GDD_r\n(fs^2)"
	delta_column_title = "Delta GDD_r\n(fs^2)"
	multiplicative_factor = 1.0e30



########################################################################
#                                                                      #
# transmission_GDD_spectrum_target_dialog                              #
#                                                                      #
########################################################################
class transmission_GDD_spectrum_target_dialog(spectrum_target_dialog):
	"""A dialog to define a transmission GDD spectrum target"""
	
	target_class = targets.transmission_GDD_spectrum_target
	
	title = "Set Transmission GDD Spectrum Target"
	data_column_title = "GDD_t\n(fs^2)"
	delta_column_title = "Delta GDD_t\n(fs^2)"
	multiplicative_factor = 1.0e30



########################################################################
#                                                                      #
# reflection_color_target_dialog                                       #
#                                                                      #
########################################################################
class reflection_color_target_dialog(color_target_dialog):
	"""A dialog to define a reflection color target"""
	
	target_class = targets.reflection_color_target
	
	title = "Set Reflection Color Target"
	allow_direction = True



########################################################################
#                                                                      #
# transmission_color_target_dialog                                     #
#                                                                      #
########################################################################
class transmission_color_target_dialog(color_target_dialog):
	"""A dialog to define a transmission color target"""
	
	target_class = targets.transmission_color_target
	
	title = "Set Transmission Color Target"



########################################################################
#                                                                      #
# read_target_from_file_dialog                                         #
#                                                                      #
########################################################################
class read_target_from_file_dialog(target_dialog):
	"""A dialog to read a target from a file"""
	
	title = "Read Target From File"
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content necessary to read a target from a file to the
		dialog"""
		
		self.file_browse_button = wx.lib.filebrowsebutton.FileBrowseButton(self, -1, size=(450, -1), labelText = "Input file:")
		
		# Radio buttons to describe the file.
		self.two_columns_button = wx.RadioButton(self, -1, "two columns", style = wx.RB_GROUP)
		self.three_columns_button = wx.RadioButton(self, -1, "three columns")
		
		# A text box for the number of header lines.
		self.header_lines_box = wx.TextCtrl(self, -1, "", validator = int_validator(0))
		
		# Radio buttons and a box for the multiplicative factor.
		self.unit_multiplicative_factor_button = wx.RadioButton(self, -1, "1", style = wx.RB_GROUP)
		self.percent_multiplicative_factor_button = wx.RadioButton(self, -1, "%")
		self.radian_multiplicative_factor_button = wx.RadioButton(self, -1, "180/pi")
		self.other_multiplicative_factor_button = wx.RadioButton(self, -1, "")
		self.other_multiplicative_factor_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(condition = self.other_multiplicative_factor_button.GetValue))
		self.other_multiplicative_factor_box.Bind(wx.EVT_TEXT, self.on_other_multiplicative_factor_box)
		
		# Radio buttons for the kind of target.
		self.reflection_spectrum_button = wx.RadioButton(self, -1, "reflection spectrum", style = wx.RB_GROUP)
		self.transmission_spectrum_button = wx.RadioButton(self, -1, "transmission spectrum")
		self.absorption_spectrum_button = wx.RadioButton(self, -1, "absorption spectrum")
		self.reflection_phase_spectrum_button = wx.RadioButton(self, -1, "reflection phase spectrum")
		self.transmission_phase_spectrum_button = wx.RadioButton(self, -1, "transmission phase spectrum")
		self.reflection_GD_spectrum_button = wx.RadioButton(self, -1, "reflection GD spectrum")
		self.transmission_GD_spectrum_button = wx.RadioButton(self, -1, "transmission GD spectrum")
		self.reflection_GDD_spectrum_button = wx.RadioButton(self, -1, "reflection GDD spectrum")
		self.transmission_GDD_spectrum_button = wx.RadioButton(self, -1, "transmission GDD spectrum")
		self.reflection_color_button = wx.RadioButton(self, -1, "reflection color")
		self.transmission_color_button = wx.RadioButton(self, -1, "transmission color")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.reflection_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.transmission_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.absorption_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.reflection_phase_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.transmission_phase_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.reflection_GD_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.transmission_GD_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.reflection_GDD_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.transmission_GDD_spectrum_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.reflection_color_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_kind, self.transmission_color_button)
		
		sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_3_1_1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3_1_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3_1_3 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3_1_4 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3_1_5 = wx.BoxSizer(wx.HORIZONTAL)
		
		sizer_1.Add(wx.StaticText(self, -1, "File format:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(self.two_columns_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_1.Add(self.three_columns_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_1.Add(wx.StaticText(self, -1, "Header lines:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		sizer_1.Add(self.header_lines_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_2.Add(wx.StaticText(self, -1, "Multiplicative factor:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_2.Add(self.unit_multiplicative_factor_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_2.Add(self.percent_multiplicative_factor_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_2.Add(self.radian_multiplicative_factor_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_2.Add(self.other_multiplicative_factor_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_2.Add(self.other_multiplicative_factor_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1_1.Add(self.reflection_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3_1_1.Add(self.transmission_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_3_1_1.Add(self.absorption_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1_2.Add(self.reflection_phase_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3_1_2.Add(self.transmission_phase_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1_3.Add(self.reflection_GD_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3_1_3.Add(self.transmission_GD_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1_4.Add(self.reflection_GDD_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3_1_4.Add(self.transmission_GDD_spectrum_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1_5.Add(self.reflection_color_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3_1_5.Add(self.transmission_color_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3_1.Add(sizer_3_1_1, 0, wx.ALIGN_LEFT)
		sizer_3_1.Add(sizer_3_1_2, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		sizer_3_1.Add(sizer_3_1_3, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		sizer_3_1.Add(sizer_3_1_4, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		sizer_3_1.Add(sizer_3_1_5, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		sizer_3.Add(wx.StaticText(self, -1, "Target:"), 0, wx.ALIGN_LEFT|wx.ALIGN_TOP)
		sizer_3.Add(sizer_3_1, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP)
		
		self.content_sizer.Add(self.file_browse_button, 0, wx.ALIGN_LEFT)
		self.content_sizer.Add(sizer_1, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		self.content_sizer.Add(sizer_2, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		self.content_sizer.Add(sizer_3, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		self.add_angle_box()
		self.add_polarization_choice()
		self.add_illuminant_and_observer_choices()
		self.add_direction_choice()
		
		# The default values.
		self.two_columns_button.SetValue(True)
		self.header_lines_box.SetValue("%s" % 0)
		self.unit_multiplicative_factor_button.SetValue(True)
		self.reflection_spectrum_button.SetValue(True)
		self.set_angle(0.0)
		self.set_polarization(S)
		self.set_illuminant_and_observer(config.ILLUMINANT, config.OBSERVER)
		self.illuminant_choice.Disable()
		self.observer_choice.Disable()
		self.set_direction(FORWARD)
	
	
	######################################################################
	#                                                                    #
	# on_kind                                                            #
	#                                                                    #
	######################################################################
	def on_kind(self, event):
		"""Handle the selection of a kind of target
		
		This method takes a single argument:
		  event              the event."""
		
		if self.reflection_spectrum_button.GetValue() or self.absorption_spectrum_button.GetValue() or self.reflection_color_button.GetValue():
			self.normal_direction_button.Enable()
			self.reverse_direction_button.Enable()
		else:
			self.set_direction(FORWARD)
			self.normal_direction_button.Disable()
			self.reverse_direction_button.Disable()
		
		if self.reflection_spectrum_button.GetValue() or self.transmission_spectrum_button.GetValue() or self.absorption_spectrum_button.GetValue() or self.reflection_color_button.GetValue() or self.transmission_color_button.GetValue():
			self.s_polarized_button.Enable()
			self.p_polarized_button.Enable()
			self.unpolarized_button.Enable()
			self.other_polarizations_button.Enable()
			self.other_polarizations_box.Enable()
		else:
			self.s_polarized_button.Enable()
			self.p_polarized_button.Enable()
			self.unpolarized_button.Disable()
			self.other_polarizations_button.Disable()
			self.other_polarizations_box.Disable()
			if not (self.s_polarized_button.GetValue() or self.p_polarized_button.GetValue()):
				self.set_polarization(S)
		
		if self.reflection_color_button.GetValue() or self.transmission_color_button.GetValue():
			self.illuminant_choice.Enable()
			self.observer_choice.Enable()
		else:
			self.illuminant_choice.Disable()
			self.observer_choice.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_other_multiplicative_factor_box                                 #
	#                                                                    #
	######################################################################
	def on_other_multiplicative_factor_box(self, event):
		"""Handle text events related to the multiplicative factor box
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in the other multiplicative factor box,
		# automatically select the other multiplicative factor button.
		if self.other_multiplicative_factor_box.GetValue() != "":
			self.other_multiplicative_factor_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_target                                                         #
	#                                                                    #
	######################################################################
	def get_target(self):
		"""Get the target
		
		This method returns the target defined by the dialog."""
		
		filename = self.file_browse_button.GetValue()
		
		try:
			file = open(filename, "r")
		except IOError:
			raise targets.target_error("Impossible to open the file")
		
		# The angle, polarization and direction.
		nb_header_lines = int(self.header_lines_box.GetValue())
		angle = float(self.angle_box.GetValue())
		polarization = self.get_polarization()
		direction = self.get_direction()
		
		# Read the file
		lines = file.readlines()
		
		# Interpret the lines.
		wvls = []
		values = []
		deltas = []
		if self.two_columns_button.GetValue():
			for i in range(nb_header_lines, len(lines)):
				line = lines[i].strip()
				line = line.replace(",", " ")
				elements = line.split()
				if len(elements) >= 2:
					try:
						wvls.append(float(elements[0]))
						values.append(float(elements[1]))
						deltas.append(1.0)
					except ValueError:
						raise targets.target_error("The file is incorectly formatted")
				# Don't bug if a line is empty.
				elif len(elements) == 0:
					pass
				else:
					raise targets.target_error("The file is incorectly formatted")
		else:
			for i in range(nb_header_lines, len(lines)):
				line = lines[i].strip()
				line = line.replace(",", " ")
				elements = line.split()
				if len(elements) >= 3:
					try:
						wvls.append(float(elements[0]))
						values.append(float(elements[1]))
						deltas.append(float(elements[2]))
					except ValueError:
						return None
				# Don't bug if a line is empty.
				elif len(elements) == 0:
					pass
				else:
					raise targets.target_error("The file is incorectly formatted")
		
		if not self.unit_multiplicative_factor_button.GetValue():
			if self.percent_multiplicative_factor_button.GetValue():
				multiplicative_factor = 0.01
			elif self.radian_multiplicative_factor_button.GetValue():
				multiplicative_factor = one_hundred_eighty_over_pi
			else:
				multiplicative_factor = float(self.other_multiplicative_factor_box.GetValue())
			values = [multiplicative_factor*value for value in values]
			deltas = [multiplicative_factor*delta for delta in deltas]
		
		# Make sure that the values are reasonable.
		if self.reflection_spectrum_button.GetValue() or self.transmission_spectrum_button.GetValue() or self.absorption_spectrum_button.GetValue():
			if not all(0.0 <= value <= 1.0 for value in values):
				raise targets.target_error("Spectrophotometric targets must be between 0 and 1")
		elif self.reflection_phase_spectrum_button.GetValue() or self.transmission_phase_spectrum_button.GetValue():
			if not all(0.0 <= value <= 360.0 for value in values):
				raise targets.target_error("Phase targets must be between 0 and 360")
		elif self.transmission_GD_spectrum_button.GetValue():
			if not all(0.0 <= value for value in values):
				raise targets.target_error("Transmission GD targets must be positive")
		elif self.reflection_color_button.GetValue() or self.transmission_color_button.GetValue():
			if not all(0.0 <= value <= 1.0 for value in values):
				raise targets.target_error("Spectrum entering in the calculation of color targets must be between 0 and 1")
		
		# Make sure the deltas are positive.
		if not all(delta > 0.0 for delta in deltas):
			raise targets.target_error("Tolerances must be positive")
		
		if self.reflection_spectrum_button.GetValue():
			target = targets.reflection_spectrum_target()
		elif self.transmission_spectrum_button.GetValue():
			target = targets.transmission_spectrum_target()
		elif self.absorption_spectrum_button.GetValue():
			target = targets.absorption_spectrum_target()
		elif self.reflection_phase_spectrum_button.GetValue():
			target = targets.reflection_phase_spectrum_target()
		elif self.transmission_phase_spectrum_button.GetValue():
			target = targets.transmission_phase_spectrum_target()
		elif self.reflection_GD_spectrum_button.GetValue():
			target = targets.reflection_GD_spectrum_target()
		elif self.transmission_GD_spectrum_button.GetValue():
			target = targets.transmission_GD_spectrum_target()
		elif self.reflection_GDD_spectrum_button.GetValue():
			target = targets.reflection_GDD_spectrum_target()
		elif self.transmission_GDD_spectrum_button.GetValue():
			target = targets.transmission_GDD_spectrum_target()
		elif self.reflection_color_button.GetValue():
			target = targets.reflection_color_target()
		elif self.transmission_color_button.GetValue():
			target = targets.transmission_color_target()
		
		target.set_angle(angle)
		target.set_polarization(polarization)
		if self.reflection_spectrum_button.GetValue() or self.absorption_spectrum_button.GetValue() or self.reflection_color_button.GetValue():
			target.set_direction(direction)
		if self.reflection_color_button.GetValue() or self.transmission_color_button.GetValue():
			illuminant_name, observer_name = self.get_illuminant_and_observer()
			illuminant = color.get_illuminant(illuminant_name)
			observer = color.get_observer(observer_name)
			XYZ = color.spectrum_to_XYZ(wvls, values, observer, illuminant)
			target.set_illuminant_and_observer(illuminant_name, observer_name)
			target.set_target(color.XYZ, XYZ, [1.0, 1.0, 1.0])
		else:
			target.set_target(0.0, 0.0, 0.0, wvls, values, deltas)
		
		return target



########################################################################
#                                                                      #
# target_point_grid_validator                                          #
#                                                                      #
########################################################################
class target_point_grid_validator(wx.PyValidator):
	"""Validator for the content of the grid in the spectral targets dialog
	box"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, minimum = None, maximum = None, condition = None):
		"""Initialize the validator
		
		This method takes 3 optional arguments:
		  minimum     the minimal acceptable value or None for no limit
		              (default value is None);
		  maximum     the maximal acceptable value or None for no limit
		              (default value is None);
		  condition   a function that is tested to verify if the validation
		              of the integer should be done or None for no
		              condition (default value is None).
		The truth testing of the condition function follows Python truth
		testing."""
		
		wx.PyValidator.__init__(self)
		
		self.minimum = minimum
		self.maximum = maximum
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.minimum, self.maximum, self.condition)
	
	
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
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or False
		otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			event.Skip()
			return
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		
		previous_wavelength = 0.0
		for row in range(nb_rows):
			try:
				wavelength = float(window.GetCellValue(row, 0))
				if wavelength <= previous_wavelength:
					raise ValueError
				previous_wavelength = wavelength
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0, True)
			
			try:
				value = float(window.GetCellValue(row, 1))
				if self.minimum is not None and value < self.minimum:
					raise ValueError
				if self.maximum is not None and value > self.maximum:
					raise ValueError
			except ValueError:
				error = True
				window.SelectBlock(row, 1, row, 1, True)
			
			try:
				delta = float(window.GetCellValue(row, 2))
				if delta <= 0:
					raise ValueError
			except ValueError:
				error = True
				window.SelectBlock(row, 2, row, 2, True)
			
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True
