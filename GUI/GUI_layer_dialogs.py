# GUI_layer_dialogs.py
# 
# Dialogs to add and remove layers for the GUI of Filters.
# 
# Copyright (c) 2001-2009,2011,2013-2015 Stephane Larouche.
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



import wx

from definitions import *
import materials
import graded

from GUI_validators import int_validator, float_validator, material_validator


ADD = 0
REMOVE = 1
REPLACE = 2



########################################################################
#                                                                      #
# layer_dialog                                                         #
#                                                                      #
########################################################################
class layer_dialog(wx.Dialog):
	"""Abstract layer dialog class
	
	This abstract class, derived from wxDialog, provides an architecture
	for all the layer dialogs, such as those to add, modify or remove
	layers."""
	
	operation = ADD
	validator = wx.PyValidator
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, description = None):
		"""Initialize the dialog
		
		This method takes 2 or 3 arguments:
		  parent             the window's parent;
		  filter             the filter containing the layer;
		  description        (optional) a tuple describing the layer when
		                     this dialog is used to modify an existing
		                     layer."""
		
		self.filter = filter
		self.description = description
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.SetValidator(self.validator())
		
		self.material_box = None
		self.thickness_box = None
		self.index_box = None
		
		self.side_only = False
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.add_content()
		
		self.add_buttons()
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS events .
		if self.material_box:
			self.material_box.Unbind(wx.EVT_KILL_FOCUS)
		if self.thickness_box:
			self.thickness_box.Unbind(wx.EVT_KILL_FOCUS)
		if self.index_box:
			self.index_box.Unbind(wx.EVT_KILL_FOCUS)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_enter                                                           #
	#                                                                    #
	######################################################################
	def on_enter(self, event):
		"""Terminate the dialog when enter is pressed into a wxTextCtrl
		
		This method takes a single argument:
		  event              the event.
		
		It validates the dialog before ending it."""
		
		if self.Validate():
			self.EndModal(wx.ID_OK)
	
	
	######################################################################
	#                                                                    #
	# create_material_box                                                #
	#                                                                    #
	######################################################################
	def create_material_box(self, kind = None):
		"""Create a box to specify the material of the layer
		
		This method takes an optional argument:
		  kind               (optional) the kind of material
		                     (MATERIAL_REGULAR or MATERIAL_MIXTURE).
		
		When a kind of material is specified, the box only accepts that
		kind of material."""
		
		material_catalog = self.filter.get_material_catalog()
		
		# Adding the text box for specifying the material.
		self.material_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = material_validator(material_catalog, kind))
		
		self.material_box.Bind(wx.EVT_KILL_FOCUS, self.on_material)
		self.material_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
	
	
	######################################################################
	#                                                                    #
	# create_thickness_box                                               #
	#                                                                    #
	######################################################################
	def create_thickness_box(self):
		"""Create a box to specify the thickness of the layer"""
		
		# Adding the text box for specifying the thickness.
		self.thickness_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None))
		
		self.thickness_box.Bind(wx.EVT_KILL_FOCUS, self.on_thickness)
		self.thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
	
	
	######################################################################
	#                                                                    #
	# create_index_box                                                   #
	#                                                                    #
	######################################################################
	def create_index_box(self):
		"""Create a box to specify the index of refraction of the layer"""
		
		# Adding the text box for specifying the index.
		self.index_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER)
		self.index_box.SetValidator(float_validator(0.0, None, self.index_box.IsEnabled))
		
		self.index_box.Bind(wx.EVT_KILL_FOCUS, self.on_index)
		self.index_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		Derived classes must implement this method so that it takes care of
		adding all appropriate elements to the dialog."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# add_position_choice                                                #
	#                                                                    #
	######################################################################
	def add_position_choice(self, side_only = False):
		"""Add controls to set the position of the layer to the dialog
		
		This method takes an optional argument:
		  side_only          (optional) a boolean indicating that only the
		                     side must be selected.
		
		This method adds control the the dialog to select the side and the
		position (except if side_only is True) where the layer goes."""
		
		self.side_only = side_only
		
		position_static_box = wx.StaticBox(self, -1, "Side/Position" )
		
		position_box_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Adding radio buttons for the side.
		self.front_button = wx.RadioButton(self, -1, "front", style = wx.RB_GROUP)
		self.back_button = wx.RadioButton(self, -1, "back")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_side_radio_button, self.front_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_side_radio_button, self.back_button)
		
		position_box_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		position_box_sizer_1.Add(wx.StaticText(self, -1, "Side:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		position_box_sizer_1.Add(self.front_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		position_box_sizer_1.Add(self.back_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		position_box_sizer.Add(position_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# Adding radio buttons and a text box for specifying the
		# position.
		if not self.side_only:
			self.top_button = wx.RadioButton(self, -1, "top", style = wx.RB_GROUP)
			self.bottom_button = wx.RadioButton(self, -1, "bottom")
			self.other_position_button = wx.RadioButton(self, -1, "at position ")
			self.other_position_box = wx.TextCtrl(self, -1, "", validator = int_validator(condition = self.other_position_button.GetValue))
			self.Bind(wx.EVT_RADIOBUTTON, self.on_position_radio_button, self.top_button)
			self.Bind(wx.EVT_RADIOBUTTON, self.on_position_radio_button, self.bottom_button)
			self.Bind(wx.EVT_RADIOBUTTON, self.on_position_radio_button, self.other_position_button)
			self.Bind(wx.EVT_TEXT, self.on_other_position_box, self.other_position_box)
			self.Bind(wx.EVT_TEXT_ENTER, self.on_enter, self.other_position_box)
			
			position_box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
			
			position_box_sizer_2.Add(wx.StaticText(self, -1, "Position:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
			position_box_sizer_2.Add(self.top_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			position_box_sizer_2.Add(self.bottom_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			position_box_sizer_2.Add(self.other_position_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			position_box_sizer_2.Add(self.other_position_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
			
			position_box_sizer.Add(position_box_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
		
		# Arrange buttons in the static box.
		position_static_box_sizer = wx.StaticBoxSizer(position_static_box, wx.VERTICAL)
		position_static_box_sizer.Add(position_box_sizer, 0, wx.ALL, 5)
		
		self.main_sizer.Add(position_static_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		nb_front_layers = self.filter.get_nb_layers(FRONT)
		nb_back_layers = self.filter.get_nb_layers(BACK)
		
		if self.side_only:
			if self.operation == ADD:
				self.front_button.Enable(True)
				self.back_button.Enable(True)
				self.front_button.SetValue(True)
			elif (self.operation == REMOVE or self.operation == REPLACE):
				if nb_front_layers:
					self.front_button.SetValue(True)
				else:
					self.back_button.SetValue(True)
		
		else:
			# When adding layers, the front side is always selected by default.
			# When removing of replacing layers, the front side is prefered,
			# but if there is no layer on the front, the back side is selected.
			if self.operation == ADD:
				nb_layers = nb_front_layers
			elif (self.operation == REMOVE or self.operation == REPLACE) and nb_front_layers == 0:
				nb_layers = nb_back_layers
			
			# When adding layers, both side are available.
			if self.operation == ADD:
				self.front_button.Enable(True)
				self.back_button.Enable(True)
				self.front_button.SetValue(True)
				if nb_front_layers:
					self.other_position_box.GetValidator().set_limits(1, nb_front_layers+1)
				else:
					self.bottom_button.Enable(False)
					self.other_position_button.Enable(False)
					self.other_position_box.Enable(False)
			
			# When removing or replacing layers, only the sides with layers are
			# available.
			elif (self.operation == REMOVE or self.operation == REPLACE):
				if nb_front_layers:
					self.front_button.SetValue(True)
					nb_layers = nb_front_layers
				else:
					self.front_button.Enable(False)
					self.back_button.SetValue(True)
					nb_layers = nb_back_layers
				
				if nb_back_layers == 0:
					self.back_button.Enable(False)
				
				if nb_layers < 2:
					self.bottom_button.Enable(False)
					self.other_position_button.Enable(False)
					self.other_position_box.Enable(False)
				else:
					self.other_position_box.GetValidator().set_limits(1, nb_layers)
			
			# The default values.
			self.top_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add ok and cancel buttons to the dialog"""
		
		# Create buttons.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK, validator = self.validator()), 0)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.LEFT, 20)
		
		# Call a specific on_cancel function that will unbind some events in
		# order to be able to cancel.
		self.Bind(wx.EVT_BUTTON, self.on_cancel, id = wx.ID_CANCEL)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 20)
	
	
	######################################################################
	#                                                                    #
	# on_material                                                        #
	#                                                                    #
	######################################################################
	def on_material(self, event):
		"""Handle kill focus events for the material box
		
		This method takes a single argument:
		  event              the event.
		
		It validates the content of the material box before letting it
		loose focus."""
		
		# If the focus is lost to the Cancel button, don't actually
		# validate the material.
		if event.GetEventType() == wx.wxEVT_KILL_FOCUS and event.GetWindow() and event.GetWindow().GetId() == wx.ID_CANCEL:
			event.Skip()
			return
		
		if self.material_box.GetValidator().Validate(self):
			event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_thickness                                                       #
	#                                                                    #
	######################################################################
	def on_thickness(self, event):
		"""Handle kill focus events for the thickness box
		
		This method takes a single argument:
		  event              the event.
		
		It validates the content of the thickness box before letting it
		loose focus."""
		
		# If the focus is lost to the Cancel button, don't actually
		# validate the thickness.
		if event.GetEventType() == wx.wxEVT_KILL_FOCUS and event.GetWindow() and event.GetWindow().GetId() == wx.ID_CANCEL:
			event.Skip()
			return
		
		if self.thickness_box.GetValidator().Validate(self):
			event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_index                                                           #
	#                                                                    #
	######################################################################
	def on_index(self, event):
		"""Handle kill focus events for the index box
		
		This method takes a single argument:
		  event              the event.
		
		It validates the content of the index box before letting it loose
		focus."""
		
		# If the focus is lost to the Cancel button, don't actually
		# validate the index.
		if event.GetEventType() == wx.wxEVT_KILL_FOCUS and event.GetWindow() and event.GetWindow().GetId() == wx.ID_CANCEL:
			event.Skip()
			return
		
		if self.index_box.GetValidator().Validate(self):
			event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_side_radio_button                                               #
	#                                                                    #
	######################################################################
	def on_side_radio_button(self, event):
		"""Handle radio button events for the side buttons
		
		This method takes a single argument:
		  event              the event.
		
		It modifies the range of acceptable positions according to the
		number of layers on the selected side."""
		
		if self.side_only:
			return
		
		if self.front_button.GetValue():
			side = FRONT
		elif self.back_button.GetValue():
			side = BACK
		
		nb_layers = self.filter.get_nb_layers(side)
		
		# If there is an other position box, change its validator.
		if self.other_position_box:
			if self.operation == ADD:
				self.other_position_box.GetValidator().set_limits(1, nb_layers+1)
			else:
				self.other_position_box.GetValidator().set_limits(1, nb_layers)
		
		# When adding layers, make the other position radio button and
		# radio box only selectable when there is already one layer.
		if self.operation == ADD:
			if nb_layers == 0:
				self.bottom_button.Enable(False)
				self.other_position_button.Enable(False)
				self.other_position_box.Enable(False)
			else:
				self.bottom_button.Enable(True)
				self.other_position_button.Enable(True)
				self.other_position_box.Enable(True)
		
		# When removing or replacing layers, make the other position radio
		# button and radio box only selectable when there is more than one
		# layer.
		if (self.operation == REMOVE or self.operation == REPLACE):
			if nb_layers < 2:
				self.bottom_button.Enable(False)
				self.other_position_button.Enable(False)
				self.other_position_box.Enable(False)
			else:
				self.bottom_button.Enable(True)
				self.other_position_button.Enable(True)
				self.other_position_box.Enable(True)
	
	
	######################################################################
	#                                                                    #
	# on_position_radio_button                                           #
	#                                                                    #
	######################################################################
	def on_position_radio_button(self, event):
		"""Handle radio button events for the position buttons
		
		This method takes a single argument:
		  event              the event.
		
		When an a position is selected (except if it is the other
		position), it empties the position text box."""
		
		if not self.other_position_button.GetValue():
			self.other_position_box.Clear()
	
	
	######################################################################
	#                                                                    #
	# on_other_position_box                                              #
	#                                                                    #
	######################################################################
	def on_other_position_box(self, event):
		"""Handle text events for the position text box
		
		This method takes a single argument:
		  event              the event.
		
		When an a position is entered in the position text box, it
		automatically selects the other position radio button."""
		
		if self.other_position_box.GetValue():
			self.other_position_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_side                                                           #
	#                                                                    #
	######################################################################
	def get_side(self):
		"""Get the side of the layer
		
		This method returns the side where to add the layer."""
		
		if self.front_button.GetValue():
			return FRONT
		elif self.back_button.GetValue():
			return BACK
	
	
	######################################################################
	#                                                                    #
	# get_position                                                       #
	#                                                                    #
	######################################################################
	def get_position(self):
		"""Get the position of the layer
		
		This method returns the position where to add the layer."""
		
		# Verify the existance of the buttons before calling them.
		if self.top_button and self.top_button.GetValue():
			return TOP
		elif self.bottom_button and self.bottom_button.GetValue():
			return BOTTOM
		elif self.other_position_button and self.other_position_button.GetValue():
			# Convert the position from 1 based list (as in the user
			# interface) to 0 based list (as in the software).
			return int(self.other_position_box.GetValue())-1
		else:
			return None
	
	
	######################################################################
	#                                                                    #
	# get_material_name                                                  #
	#                                                                    #
	######################################################################
	def get_material_name(self):
		"""Get the name of the material
		
		This method returns the name of the material of the layer."""
		
		return self.material_box.GetValue()
	
	
	######################################################################
	#                                                                    #
	# get_thickness                                                      #
	#                                                                    #
	######################################################################
	def get_thickness(self):
		"""Get the thickness of the layer
		
		This method returns the thickness of the layer."""
		
		return float(self.thickness_box.GetValue())
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get all the parameters of the layer
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# apply                                                              #
	#                                                                    #
	######################################################################
	def apply(self):
		"""Apply the result of the dialog to the filter
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")



########################################################################
#                                                                      #
# simple_layer_dialog                                                  #
#                                                                      #
########################################################################
class simple_layer_dialog(layer_dialog):
	"""A dialog to add or modify an homogeneous layer"""
	
	title = "Simple layer"
	
	operation = ADD
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the appropriate content to the dialog"""
		
		self.add_layer_definition()
		if self.description is None:
			self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the layer description to the dialog
		
		This method adds controls to specify the layer material, thickness
		and index of refraction. It also offers a choice to specify the
		thickness in physical or optical thickness."""
		
		self.index = None
		
		layer_static_box = wx.StaticBox(self, -1, "Layer" )
		
		layer_box_sizer_1 = wx.FlexGridSizer(2, 5, 5, 0)
		
		# Adding the text box for specifying the material.
		self.create_material_box()
		layer_box_sizer_1.Add(wx.StaticText(self, -1, "Material:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_1.Add(self.material_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		thickness_list = ["nm", "nm OT", "QWOT"]
		
		# Adding the text box for specifying the thickness.
		self.create_thickness_box()
		self.thickness_choice = wx.Choice(self, -1, (-1, -1), choices = thickness_list)
		layer_box_sizer_1.Add(wx.StaticText(self, -1, "Thickness:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		layer_box_sizer_1.Add(self.thickness_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_1.Add(self.thickness_choice, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.Bind(wx.EVT_CHOICE, self.on_choice, self.thickness_choice)
		
		# Adding the text box for specifying the index. The value is
		# validated only when the index box is editable.
		self.create_index_box()
		layer_box_sizer_1.Add(wx.StaticText(self, -1, "Index:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_1.Add(self.index_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Arrange in the static box.
		layer_box_sizer = wx.StaticBoxSizer(layer_static_box, wx.VERTICAL)
		layer_box_sizer.Add(layer_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		self.main_sizer.Add(layer_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# The default values.
		if self.description:
			self.material_box.SetValue(self.description[0])
			self.thickness_box.SetValue("%.6f" % self.description[1])
			self.selection = self.description[3]
			self.thickness_choice.SetSelection(self.selection)
			self.index = self.description[2]
			if self.index is None:
				self.index_box.SetValue("")
				self.index_box.Enable(False)
			else:
				self.index_box.SetValue("%.6f" % self.index)
				self.index_box.Enable(True)
		else:
			self.thickness_box.SetValue("0.0")
			self.selection = 0
			self.thickness_choice.SetSelection(self.selection)
			self.index_box.Enable(False)
	
	
	######################################################################
	#                                                                    #
	# on_enter                                                           #
	#                                                                    #
	######################################################################
	def on_enter(self, event):
		"""Terminate the dialog when enter is pressed into a wxTextCtrl
		
		This method takes a single argument:
		  event              the event.
		
		It validates the dialog before ending it."""
		
		# If enter was pressed in the material box, execute on_material
		# to change the validator of the index box if the kind of material
		# was changed.
		if event.GetEventObject() is self.material_box:
			self.on_material(event)
		
		layer_dialog.on_enter(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_material                                                        #
	#                                                                    #
	######################################################################
	def on_material(self, event):
		"""Handle kill focus events for the material box
		
		This method takes a single argument:
		  event              the event.
		
		In addition to validating the content of the material box before
		letting it loose focus, it enables/disables the index box according
		to the kind of material."""
		
		# If the focus is lost to the Cancel button, don't actually
		# validate the material.
		if event.GetEventType() == wx.wxEVT_KILL_FOCUS and event.GetWindow() and event.GetWindow().GetId() == wx.ID_CANCEL:
			event.Skip()
			return
		
		if not self.material_box.GetValidator().Validate(self):
			return
		
		# The material is right since it has been taken care of by the
		# validator. However, it is possible that this material cannot be
		# used in this filter, because it is not monotonic at the center
		# wavelength, for example.
		material_name = self.material_box.GetValue()
		try:
			material_nb = self.filter.get_material_nb(material_name)
			material = self.filter.get_material(material_nb)
		except materials.material_error, error:
			wx.MessageBox("This material cannot be used.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			
			self.material_box.SetFocus()
			self.material_box.SetSelection(0, len(material_name))
			self.material_box.Refresh()
			
			return
		
		# If the material is a mixture, allow modification of the index box
		# and set the range according to the material.
		if material.is_mixture():
			n_min, n_max = material.get_index_range(self.filter.get_center_wavelength())
			self.index_box.Enable(True)
			self.index_box.GetValidator().set_limits(n_min, n_max)
			try:
				self.index = float(self.index_box.GetValue())
			except ValueError:
				self.index = None
		else:
			self.index_box.SetValue("")
			self.index_box.Enable(False)
			self.index = material.get_index(self.filter.get_center_wavelength())
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_choice                                                          #
	#                                                                    #
	######################################################################
	def on_choice(self, event):
		"""Handle choice events for thickness choice
		
		This method takes a single argument:
		  event              the event.
		
		This method recalculate the thickness according to a change of the
		way it is expressed."""
		
		if self.thickness_box.GetValidator().Validate(self):
			thickness = float(self.thickness_box.GetValue())
		else:
			thickness = 0.0
		
		old_selection = self.selection
		self.selection = event.GetSelection()
		
		# Change the thickness only if the index and thickness are defined.
		# If the thickness is 0, it doesn't need to be changed.
		if self.index and thickness and self.selection != old_selection:
			if old_selection == 0:
				pass
			elif old_selection == 1:
				thickness /= self.index
			elif old_selection == 2:
				thickness *= self.filter.get_center_wavelength()/4.0/self.index
			
			if self.selection == 0:
				self.thickness_box.SetValue("%.6f" % thickness)
			elif self.selection == 1:
				self.thickness_box.SetValue("%.6f" % (thickness*self.index))
			elif self.selection == 2:
				self.thickness_box.SetValue("%.6f" % (4.0*thickness*self.index/self.filter.get_center_wavelength()))
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_index                                                           #
	#                                                                    #
	######################################################################
	def on_index(self, event):
		"""Handle kill focus events for the index box
		
		This method takes a single argument:
		  event              the event.
		
		It validates the content of the index box before letting it loose
		focus."""
		
		# If the focus is lost to the Cancel button, don't actually
		# validate the index.
		if event.GetEventType() == wx.wxEVT_KILL_FOCUS and event.GetWindow() and event.GetWindow().GetId() == wx.ID_CANCEL:
			event.Skip()
			return
		
		if not self.index_box.GetValidator().Validate(self):
			return
		
		self.index = float(self.index_box.GetValue())
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get all the parameters of the layer
		
		This method returns:
		  material_name      the name of the material;
		  thickness          the physical or optical thickness of the layer;
		  index              the index of the layer
		  OT                 a boolean indicating if the thickness is
		                     expressed in optical thickness (True) or
		                     physical thickness (False)."""
		
		material_name = self.get_material_name()
		thickness = self.get_thickness()
		if self.index_box.GetValue() == "":
			index = None
		else:
			index = float(self.index_box.GetValue())
		if self.thickness_choice.GetSelection() == 0:
			OT = False
		elif self.thickness_choice.GetSelection() == 1:
			OT = True
		elif self.thickness_choice.GetSelection() == 2:
			OT = True
			thickness *= self.filter.get_center_wavelength()/4.0
		
		return material_name, thickness, index, OT
	
	
	######################################################################
	#                                                                    #
	# apply                                                              #
	#                                                                    #
	######################################################################
	def apply(self):
		"""Apply the result of the dialog to the filter
		
		This method adds the layer to the filter."""
		
		material_name = self.get_material_name()
		thickness = self.get_thickness()
		position = self.get_position()
		side = self.get_side()
		if self.index_box.GetValue() == "":
			index = None
		else:
			index = float(self.index_box.GetValue())
		if self.thickness_choice.GetSelection() == 0:
			OT = False
		elif self.thickness_choice.GetSelection() == 1:
			OT = True
		elif self.thickness_choice.GetSelection() == 2:
			OT = True
			thickness *= self.filter.get_center_wavelength()/4.0
		
		self.filter.add_layer(material_name, thickness, position, side, index, OT)



########################################################################
#                                                                      #
# import_layer_error                                                   #
#                                                                      #
########################################################################
class import_layer_error(Exception):
	"""Exception class for layer importation error"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Layer import error: %s." % self.value
		else:
			return "Layer import error."



########################################################################
#                                                                      #
# import_layer_dialog                                                  #
#                                                                      #
########################################################################
class import_layer_dialog(layer_dialog):
	"""A dialog to add add a graded-index layer while reading its index
	profile in a text file"""
	
	title = "Import layer"
	
	operation = ADD
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the appropriate content to the dialog"""
		
		self.add_layer_definition()
		self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the layer description to the dialog
		
		This method adds controls to specify the layer material, and the
		file where to read the index profile."""
		
		layer_static_box = wx.StaticBox(self, -1, "Layer" )
		
		layer_box_sizer_1 = wx.BoxSizer(wx.VERTICAL)
		layer_box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		layer_box_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.file_browse_button = wx.lib.filebrowsebutton.FileBrowseButton(self, -1, size=(450, -1), labelText = "Input file:")
		layer_box_sizer_1.Add(self.file_browse_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		# A text box for the number of header lines.
		self.header_lines_box = wx.TextCtrl(self, -1, "", validator = int_validator(0))
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "Nb header lines:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_2.Add(self.header_lines_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_1.Add(layer_box_sizer_2, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		# Adding the text box for specifying the material.
		self.create_material_box(MATERIAL_MIXTURE)
		layer_box_sizer_3.Add(wx.StaticText(self, -1, "Material:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_3.Add(self.material_box, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_1.Add(layer_box_sizer_3, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		# Arrange in the static box.
		layer_box_sizer = wx.StaticBoxSizer(layer_static_box, wx.VERTICAL)
		layer_box_sizer.Add(layer_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		self.main_sizer.Add(layer_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# The default values.
		self.header_lines_box.SetValue("0")
	
	
	######################################################################
	#                                                                    #
	# apply                                                              #
	#                                                                    #
	######################################################################
	def apply(self):
		"""Apply the result of the dialog to the filter
		
		This method adds the layer to the filter."""
		
		filename = self.file_browse_button.GetValue()
		nb_header_lines = int(self.header_lines_box.GetValue())
		material_name = self.get_material_name()
		position = self.get_position()
		side = self.get_side()
		
		try:
			file = open(filename, "r")
		except IOError:
			raise import_layer_error("Impossible to open the file")
		
		# Read the file
		lines = file.readlines()
		
		# Interpret the lines.
		thickness = []
		profile = []
		for i in range(nb_header_lines, len(lines)):
			lines[i] = lines[i].strip()
			elements = lines[i].split()
			if len(elements) >= 2:
				try:
					thickness.append(float(elements[0]))
					profile.append(float(elements[1]))
				except ValueError:
					raise import_layer_error("The file is incorectly formatted")
			# Don't bug if a line is empty.
			elif len(elements) == 0:
				pass
			else:
				raise import_layer_error("The file is incorectly formatted")
		
		try:
			self.filter.add_graded_layer(material_name, profile, thickness, position, side)
		except graded.grading_error, error:
			raise import_layer_error("Improper grading (%s)" % error.value)



########################################################################
#                                                                      #
# remove_layer_dialog                                                  #
#                                                                      #
########################################################################
class remove_layer_dialog(layer_dialog):
	"""A dialog to remove a layer from a filter"""
	
	title = "Remove layer"
	
	operation = REMOVE
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the appropriate content to the dialog"""
		
		self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# apply                                                              #
	#                                                                    #
	######################################################################
	def apply(self):
		"""Apply the result of the dialog to the filter
		
		This method removes the layer to the filter."""
		
		position = self.get_position()
		side = self.get_side()
		
		self.filter.remove_layer(position, side)
