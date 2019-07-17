# quintic.py
# 
# A module to create quintic layers.
# 
# Copyright (c) 2000-2010,2013 Stephane Larouche.
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



name = "Quintic"
description = [["Quintic", "quintic", "quintic_dialog"]]



import math

import wx

from definitions import *
from moremath import integration

from GUI import GUI_layer_dialogs
from GUI.GUI_validators import float_validator



THICKNESS = 0
OPTICAL_THICKNESS = 1

LINEAR = 0
EXPONENTIAL = 1



########################################################################
#                                                                      #
# quintic                                                              #
#                                                                      #
########################################################################
def quintic(filter, position, side, replace, material_name, thickness, index = "auto", thickness_scaling = THICKNESS, index_scaling = LINEAR):
	"""Make a quintic layer
	
	This function add a quintic antireflection layer at the specified
	position. This function takes 5 to 8 arguments:
		position		        the position (TOP, BOTTOM or position of the
		                    layer) where the quintic layer must be placed;
		side    		        the side (FRONT or BACK), where the quintic
		                    must be placed;
		replace             a boolean value indicating if the layer
		                    currently at that position should be replaced
		material_name       the name of the material to be used in the
		                    quintic;
		thickness           the thickness of the quintic;
		index               (optional) a list containing the starting and
		                    the ending index of the quintic or "auto",
		                    in which case the quintic will match the
		                    surrounding layers as well as possible, the
		                    default value is "auto";
		thickness_scaling   (optional) the scaling of the thickness can be
		                    THICKNESS or OPTICAL_THICKNESS, the default
		                    value is THICKNESS;
		index_scaling       (optional) the scaling of the index can be
		                    LINEAR or EXPONENTIAL, the default value is
		                    LINEAR.
	
	For mode details about quintic coatings, see:
	  W. H. Southwell, "Gradient-index antireflection coatings", Opt.
	  Lett. V. 6, No. 11, 1983, pp. 584-586."""
	
	# Get the material from the filter.
	material_nb = filter.get_material_nb(material_name)
	material = filter.get_material(material_nb)
	
	# Get the useful properties of the material and the filter.
	n_min, n_max = material.get_index_range(filter.get_center_wavelength())
	step_spacing = filter.get_step_spacing()
	
	# If the step spacing is defined by the deposition, find the smallest
	# step spacing.
	if step_spacing == DEPOSITION_STEP_SPACING:
		steps = filter.get_material_index(material_nb)
		step_spacing = min(steps[i_step]-steps[i_step-1] for i_step in range(1, len(steps)))
	
	# Interpreting the value of index. If the index is auto, find the
	# index of the precedent and subsequent layer to choose the starting
	# and ending index.
	if index == "auto":
		if position == TOP:
			previous_layer = filter.get_nb_layers(side)-1
			next_layer = MEDIUM
		elif position == BOTTOM:
			previous_layer = SUBSTRATE
			next_layer = 0
		else:
			previous_layer = position - 1
			next_layer = position
		
		if replace:
			next_layer += 1
		
		if previous_layer == -1:
			previous_layer = SUBSTRATE
		if next_layer > filter.get_nb_layers(side)-1:
			next_layer = MEDIUM
		
		dummy, n_before = filter.get_layer_index_profile(previous_layer, side)
		dummy, n_after = filter.get_layer_index_profile(next_layer, side)
		n_before = n_before[-1]
		n_after = n_after[0]
		
		# Keep the index in the available range
		n_beginning = min(max(n_before, n_min), n_max)
		n_after = min(max(n_after, n_min), n_max)
		delta_n = n_after - n_beginning
	
	else:
		n_beginning = index[0]
		delta_n = index[1] - index[0]
	
	# Handle the case of null thickness.
	if thickness == 0.0:
		OT = False
		d = [0.0, 0.0]
		n = [n_beginning, n_beginning+delta_n]
	
	# Handle the case of delta n equal to 0.
	elif delta_n == 0.0:
		if thickness_scaling == THICKNESS:
			OT = False
			thickness_ = thickness
		else:
			OT = True
			thickness_ = thickness * n_beginning
		d = [0.0, thickness_]
		n = [n_beginning, n_beginning]
	
	else:
		# Calculate the optical thickness from the thickness in the case of
		# optical thickness scaling. The expressions are not analytically
		# integrable.
		if thickness_scaling == THICKNESS:
			OT = False
			thickness_ = thickness
		else:
			OT = True
			if index_scaling == LINEAR:
				integral = integration.cubic(lambda t: 1.0/(n_beginning+delta_n*t*t*t*(10.0+t*(-15.0+6.0*t))), 0.0, 1.0, 1000)
			else:
				A = math.log(1.0+delta_n/n_beginning)
				integral = (1.0/n_beginning)*integration.cubic(lambda t: 1.0/math.exp(A*t*t*t*(10.0+t*(-15.0+6.0*t))), 0.0, 1.0, 1000)
			thickness_ = thickness / integral
		
		# In the whole quintic, the profile passes by all the steps in its
		# delta_n. We generate 10 times more sublayers to be sure to don't
		# commit too much approximation errors.
		nb_steps_in_full_amplitude = abs(delta_n)/step_spacing
		sublayer_thickness = 0.1*thickness_/nb_steps_in_full_amplitude
		
		# The sublayer thickness is adjusted to have an integer number of
		# sublayers.
		nb_sublayers = 1+int(math.ceil(thickness_/sublayer_thickness))
		sublayer_thickness = thickness_/(nb_sublayers-1)
		
		# The thicknesses (or optical thicknesses).
		d = [i*sublayer_thickness for i in range(nb_sublayers)]
		
		# Calculation of the index profile.
		n = [0.0]*nb_sublayers
		if index_scaling == LINEAR:
			for i in range(nb_sublayers):
				t = d[i] / thickness_
				# The quintic expression is 10t**3 - 15t**4 + 6t**5.
				n[i] = n_beginning+delta_n*t*t*t*(10.0+t*(-15.0+6.0*t))
		else:
			A = math.log(1.0+delta_n/n_beginning)
			for i in range(nb_sublayers):
				t = d[i] / thickness_
				# The quintic expression is 10t**3 - 15t**4 + 6t**5.
				n[i] = n_beginning*math.exp(A*t*t*t*(10.0+t*(-15.0+6.0*t)))
	
	# Addition or replacement of the layer.
	if replace:
		filter.remove_layer(position, side)
	filter.add_graded_layer(material_name, n, d, position, side, OT, description = ["Quintic", (material_name, thickness, index, thickness_scaling, index_scaling)])



########################################################################
#                                                                      #
# quintic_dialog                                                       #
#                                                                      #
########################################################################
class quintic_dialog(GUI_layer_dialogs.layer_dialog):
	"""A dialog to add a quintic layer"""
	
	title = "Quintic"
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add appropriate content to the dialog"""
		
		self.add_layer_definition()
		if self.description is None:
			self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the description of the quintic layer to the dialog"""
		
		layer_static_box = wx.StaticBox(self, -1, "Layer")
		
		layer_box_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the material.
		self.create_material_box(MATERIAL_MIXTURE)
		layer_box_sizer_1.Add(wx.StaticText(self , -1, "Material:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_1.Add(self.material_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the thickness.
		self.create_thickness_box()
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "Thickness:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_2.Add(self.thickness_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding radio buttons for specifying the starting and ending index
		# of the quintic.
		self.auto_button_ID = wx.NewId()
		self.manual_button_ID = wx.NewId()
		self.from_box_ID = wx.NewId()
		self.to_box_ID = wx.NewId()
		self.auto_button = wx.RadioButton(self, self.auto_button_ID, "auto", style = wx.RB_GROUP)
		self.manual_button = wx.RadioButton(self, self.manual_button_ID, "from")
		self.from_box = wx.TextCtrl(self, self.from_box_ID, "", validator = float_validator(None, None, self.manual_button.GetValue))
		self.to_box = wx.TextCtrl(self, self.to_box_ID, "", validator = float_validator(None, None, self.manual_button.GetValue))
		self.Bind(wx.EVT_RADIOBUTTON, self.on_index_radio_button, self.auto_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_index_radio_button, self.manual_button)
		self.from_box.Bind(wx.EVT_TEXT, self.on_manual_box)
		self.to_box.Bind(wx.EVT_TEXT, self.on_manual_box)
		
		layer_box_sizer_3.Add(wx.StaticText(self, -1, "Index:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_3.Add(self.auto_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_3.Add(self.manual_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_3.Add(self.from_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_3.Add(wx.StaticText(self, -1, "to"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_3.Add(self.to_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding radio buttons for specifying the thickness scaling.
		self.thickness_button_ID = wx.NewId()
		self.optical_thickness_button_ID = wx.NewId()
		self.thickness_button = wx.RadioButton(self, self.thickness_button_ID, "thickness", style = wx.RB_GROUP)
		self.optical_thickness_button = wx.RadioButton(self, self.optical_thickness_button_ID, "optical thickness")
		
		layer_box_sizer_4.Add(wx.StaticText(self, -1, "Thickness scaling:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_4.Add(self.thickness_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_4.Add(self.optical_thickness_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding radio buttons for specifying the thickness scaling.
		self.linear_button_ID = wx.NewId()
		self.exponential_button_ID = wx.NewId()
		self.linear_button = wx.RadioButton(self, self.linear_button_ID, "linear", style = wx.RB_GROUP)
		self.exponential_button = wx.RadioButton(self, self.exponential_button_ID, "exponential")
		
		layer_box_sizer_5.Add(wx.StaticText(self, -1, "Index scaling:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_5.Add(self.linear_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_5.Add(self.exponential_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Arrange in the static box.
		layer_box_sizer = wx.StaticBoxSizer(layer_static_box, wx.VERTICAL)
		layer_box_sizer.Add(layer_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_3, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		layer_box_sizer.Add(layer_box_sizer_4, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		layer_box_sizer.Add(layer_box_sizer_5, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		self.main_sizer.Add(layer_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# If a description is provided, it is used to set the the
		# values in the boxes. Otherwise, default values are used.
		if self.description:
			material_name, thickness, index, thickness_scaling, index_scaling = self.description
			self.material_box.SetValue(material_name)
			self.thickness_box.SetValue("%s" % thickness)
			if index == "auto":
				self.auto_button.SetValue(True)
			else:
				self.manual_button.SetValue(True)
				self.from_box.SetValue("%s" % index[0])
				self.to_box.SetValue("%s" % index[1])
			if thickness_scaling == THICKNESS:
				self.thickness_button.SetValue(True)
			else:
				self.optical_thickness_button.SetValue(True)
			if index_scaling == LINEAR:
				self.linear_button.SetValue(True)
			else:
				self.exponential_button.SetValue(True)
		else:
			self.thickness_box.SetValue("0.0")
			self.auto_button.SetValue(True)
			self.thickness_button.SetValue(True)
			self.linear_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# on_material                                                        #
	#                                                                    #
	######################################################################
	def on_material(self, event):
		"""Adjust the dialog when a material is entered"""
		
		if not self.material_box.GetValidator().Validate(self):
			return
		
		# The material is right since it has been taken care of by the
		# validator.
		material_nb = self.filter.get_material_nb(self.material_box.GetValue())
		material = self.filter.get_material(material_nb)
		
		# Set the index limits according to the material.
		n_min, n_max = material.get_index_range(self.filter.get_center_wavelength())
		self.from_box.GetValidator().set_limits(n_min, n_max)
		self.to_box.GetValidator().set_limits(n_min, n_max)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_index_radio_button                                              #
	#                                                                    #
	######################################################################
	def on_index_radio_button(self, event):
		"""Adjust the dialog when an index radio button is selected"""
		
		# When an a position is selected (except if it is the other
		# position), empty the other position box.
		if not self.manual_button.GetValue():
			self.from_box.Clear()
			self.to_box.Clear()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_manual_box                                                      #
	#                                                                    #
	######################################################################
	def on_manual_box(self, event):
		"""Adjust the dialog when an index is entered in the manual index
		boxes"""
		
		# When a value is entered in the starting of the ending index boxes,
		# automaticaly select the manual radio button
		if self.from_box.GetValue() or self.to_box.GetValue():
			self.manual_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters of the quintic layer
		
		This method returns the properties of the quintic layer defined in
		the dialog:
		  material_name      the name of the material;
		  thickness          the thickness of the quintic;
		  index              a list of the index at the two ends of the
		                     quintic or "auto";
		  thickness_scaling  the thickness scaling of the quintic,
		                     THICKNESS or OPTICAL_THICKNESS;
		  index_scaling      the index scaling of the quintic, LINEAR or
		                     EXPONENTIAL."""
		
		material_name = self.get_material_name()
		thickness = self.get_thickness()
		if self.auto_button.GetValue():
			index = "auto"
		else:
			index = [float(self.from_box.GetValue()), float(self.to_box.GetValue())]
		if self.thickness_button.GetValue():
			thickness_scaling = THICKNESS
		else:
			thickness_scaling = OPTICAL_THICKNESS
		if self.linear_button.GetValue():
			index_scaling = LINEAR
		else:
			index_scaling = EXPONENTIAL
		
		return material_name, thickness, index, thickness_scaling, index_scaling
