# GUI_stack.py
# 
# A dialog box to design a filter from a stack formula.
# 
# Copyright (c) 2001-2008,2011,2013,2015 Stephane Larouche.
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



import string
import sys

import wx

from definitions import *
from stack import stack, analyse_stack_formula, stack_error, MIN, MAX

from GUI_layer_dialogs import layer_dialog
from GUI_validators import float_validator, material_validator



########################################################################
#                                                                      #
# stack_validator                                                      #
#                                                                      #
########################################################################
class stack_validator(wx.PyValidator):
	"""Validator for stack formula (formula, symbols and materials)"""
	
	
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
		"""Validate the formula
		
		This method takes a single argument:
		  parent             the dialog that is validated
		and it returns True if the content of the dialog is an appropriate
		stack formula or False otherwise."""
		
		formula = parent.formula_box.GetValue()
		
		# Build a list of used symbols (those in the formula).
		used_symbols = []
		for char in formula:
			if char in string.ascii_letters:
				if not char in used_symbols:
					used_symbols += char
		
		# Get a list of all defined symbols.
		defined_symbols = parent.get_symbols()
		
		# Verify that all symbols are defined.
		for symbol in used_symbols:
			if not symbol in defined_symbols:
				position = formula.index(symbol)
				if not wx.Validator_IsSilent():
					wx.Bell()
				parent.formula_box.SetFocus()
				parent.formula_box.SetSelection(position, position+1)
				return False
		
		return True



########################################################################
#                                                                      #
# stack_dialog                                                         #
#                                                                      #
########################################################################
class stack_dialog(layer_dialog):
	"""A dialog to set the stack formula"""
	
	title = "Stack Formula"
	validator = stack_validator
	nb_material_boxes = 6
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter):
		"""Initialize the dialog
		
		This method takes 2 arguments:
		  parent             the parent window of the dialog;
		  filter             the filter whose stack formula is set."""
		
		layer_dialog.__init__(self, parent, filter)
		
		self.change_side()
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_stack_definition()
		if self.description is None:
			self.add_position_choice(side_only = True)
	
	
	######################################################################
	#                                                                    #
	# add_stack_definition                                               #
	#                                                                    #
	######################################################################
	def add_stack_definition(self):
		"""Add the stack definition to the dialog."""
		
		material_catalog = self.filter.get_material_catalog()
		
		stack_static_box = wx.StaticBox(self, -1, "Stack" )
		
		# Adding the text box for specifying the stack formula.
		self.formula_box = wx.TextCtrl(self, -1, "", size=(-1, 75), style=wx.TE_MULTILINE, validator = formula_validator())
		
		stack_sizer_1 = wx.FlexGridSizer(3, self.nb_material_boxes+1, 5, 5)
		
		# Adding the text boxes for specifying the symbols.
		stack_sizer_1.Add(wx.StaticText(self , -1, "Symbols:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		
		self.symbol_box_IDs = []
		self.symbol_boxes = []
		
		for i in range(self.nb_material_boxes):
			self.symbol_box_IDs.append(wx.NewId())
			self.symbol_boxes.append(wx.TextCtrl(self, self.symbol_box_IDs[i], "", size = (75, -1), style = wx.TE_PROCESS_ENTER, validator = symbol_validator()))
			self.symbol_boxes[i].Bind(wx.EVT_KILL_FOCUS, self.on_symbol)
			self.symbol_boxes[i].Bind(wx.EVT_TEXT_ENTER, self.on_enter)
			
			stack_sizer_1.Add(self.symbol_boxes[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# Adding the text boxes for specifying the materials.
		stack_sizer_1.Add(wx.StaticText(self , -1, "Materials:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		
		self.material_box_IDs = []
		self.material_boxes = []
		
		for i in range(self.nb_material_boxes):
			self.material_box_IDs.append(wx.NewId())
			self.material_boxes.append(wx.TextCtrl(self, self.material_box_IDs[i], "", size = (75, -1), style = wx.TE_PROCESS_ENTER))
			self.material_boxes[i].SetValidator(material_validator(material_catalog, condition = self.material_boxes[i].IsEnabled))
			self.material_boxes[i].Bind(wx.EVT_KILL_FOCUS, self.on_material)
			self.material_boxes[i].Bind(wx.EVT_TEXT_ENTER, self.on_enter)
			
			stack_sizer_1.Add(self.material_boxes[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# Adding the radio buttons and text boxes for specifying the
		# indices.
		stack_sizer_1.Add(wx.StaticText(self , -1, "Index:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_TOP)
		
		self.index_min_buttons = []
		self.index_max_buttons = []
		self.index_buttons = []
		self.index_box_IDs = []
		self.index_boxes = []
		
		for i in range(self.nb_material_boxes):
			self.index_box_IDs.append(wx.NewId())
			self.index_min_buttons.append(wx.RadioButton(self, -1, "min", style = wx.RB_GROUP))
			self.index_max_buttons.append(wx.RadioButton(self, -1, "max"))
			self.index_buttons.append(wx.RadioButton(self, -1, ""))
			self.index_boxes.append(wx.TextCtrl(self, self.index_box_IDs[i], "", size = (50, -1), style = wx.TE_PROCESS_ENTER))
			
			self.index_boxes[i].SetValidator(float_validator(0.0, None, (lambda i: lambda: self.index_boxes[i].IsEnabled() and self.index_buttons[i].GetValue())(i)))
			self.index_boxes[i].Bind(wx.EVT_KILL_FOCUS, self.on_index)
			self.index_boxes[i].Bind(wx.EVT_TEXT_ENTER, self.on_enter)
			
			index_sizer = wx.BoxSizer(wx.VERTICAL)
			index_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
			index_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
			
			index_sizer_1.Add(self.index_min_buttons[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
			index_sizer_1.Add(self.index_max_buttons[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			
			index_sizer_2.Add(self.index_buttons[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
			index_sizer_2.Add(self.index_boxes[i], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			
			index_sizer.Add(index_sizer_1)
			index_sizer.Add(index_sizer_2, 0, wx.TOP, 5)
			
			stack_sizer_1.Add(index_sizer, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP)
		
		# Arrange in the static box.
		stack_box_sizer = wx.StaticBoxSizer(stack_static_box, wx.VERTICAL)
		stack_box_sizer.Add(self.formula_box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		stack_box_sizer.Add(stack_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		self.main_sizer.Add(stack_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# Default values.
		for i in range(self.nb_material_boxes):
			self.index_min_buttons[i].SetValue(True)
	
	
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
		
		# If enter was pressed in a symbol box, execute on_symbol to change
		# the enable the appropriate material box such that it is validated
		# before enter is processed.
		if event.GetEventObject() in self.symbol_boxes:
			self.on_symbol(event)
		
		# If enter was pressed in a material box, execute on_material to
		# enable the index boxes if necessary such that they are validated
		# before enter is processed.
		if event.GetEventObject() in self.material_boxes:
			self.on_material(event)
		
		layer_dialog.on_enter(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_symbol                                                          #
	#                                                                    #
	######################################################################
	def on_symbol(self, event):
		"""Update to dialog when a symbol is entered
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		nb = self.symbol_box_IDs.index(id)
		
		if not self.symbol_boxes[nb].GetValidator().Validate(self):
			return
		
		if self.symbol_boxes[nb].GetValue() == "":
			self.material_boxes[nb].SetValue("")
			self.material_boxes[nb].Disable()
			self.index_boxes[nb].SetValue("")
			self.index_min_buttons[nb].Disable()
			self.index_max_buttons[nb].Disable()
			self.index_buttons[nb].Disable()
			self.index_boxes[nb].Disable()
		else:
			self.material_boxes[nb].Enable()
			self.choose_material(nb)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_material                                                        #
	#                                                                    #
	######################################################################
	def on_material(self, event):
		"""Update to dialog when a material is entered
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		nb = self.material_box_IDs.index(id)
		
		if not self.material_boxes[nb].GetValidator().Validate(self):
			return
		
		self.choose_material(nb)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# choose_material                                                    #
	#                                                                    #
	######################################################################
	def choose_material(self, nb):
		"""Update the dialog according to the content of a material box
		
		This method takes a single argument:
		  nb                 the number of the material box."""
		
		if self.material_boxes[nb].GetValue() == "":
			self.index_boxes[nb].SetValue("")
			self.index_min_buttons[nb].Disable()
			self.index_max_buttons[nb].Disable()
			self.index_buttons[nb].Disable()
			self.index_boxes[nb].Disable()
			
			return
		
		# The material is right since it has been taken care of by the
		# validator.
		material_nb = self.filter.get_material_nb(self.material_boxes[nb].GetValue())
		material = self.filter.get_material(material_nb)
		
		# If the material is a mixture, allow modification of the index
		# radio buttons and box and set the range according to the
		# material.
		if material.is_mixture():
			n_min, n_max = material.get_index_range(self.filter.get_center_wavelength())
			self.index_min_buttons[nb].Enable()
			self.index_max_buttons[nb].Enable()
			self.index_buttons[nb].Enable()
			self.index_boxes[nb].Enable()
			self.index_boxes[nb].GetValidator().set_limits(n_min, n_max)
		else:
			self.index_boxes[nb].SetValue("")
			self.index_min_buttons[nb].Disable()
			self.index_max_buttons[nb].Disable()
			self.index_buttons[nb].Disable()
			self.index_boxes[nb].Disable()
	
	
	######################################################################
	#                                                                    #
	# on_index                                                           #
	#                                                                    #
	######################################################################
	def on_index(self, event):
		"""Automatically select the arbitrary index button when an index
		is entered in a index box
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		nb = self.index_box_IDs.index(id)
		
		if self.index_boxes[nb].GetValue() != "":
			self.index_buttons[nb].SetValue(True)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_side_radio_button                                               #
	#                                                                    #
	######################################################################
	def on_side_radio_button(self, event):
		"""Update the dialog when the user selects a side
		
		This method takes a single argument:
		  event              the event."""
		
		self.change_side()
	
	
	######################################################################
	#                                                                    #
	# get_position                                                       #
	#                                                                    #
	######################################################################
	def get_position(self):
		"""Get the position where to add the layer
		
		This method returns None since position does not apply to stacks."""
		
		return None
	
	
	######################################################################
	#                                                                    #
	# get_symbols                                                        #
	#                                                                    #
	######################################################################
	def get_symbols(self):
		"""Get the list of symbols of the stack formula
		
		This method returns:
		  symbols            the list of symbols."""
		
		symbols = []
		for i in range(self.nb_material_boxes):
			symbol = self.symbol_boxes[i].GetValue()
			if symbol != "":
				symbols.append(symbol)
		
		return symbols
	
	
	######################################################################
	#                                                                    #
	# change_side                                                        #
	#                                                                    #
	######################################################################
	def change_side(self):
		"""Update the dialog when the side is changed"""
		
		# Set the values.
		stack, materials = self.filter.get_stack_formula(self.get_side())
		
		self.formula_box.SetValue(stack)
		
		for i in range(len(materials)):
			symbol = materials.keys()[i]
			self.symbol_boxes[i].SetValue(symbol)
			self.material_boxes[i].SetValue(materials[symbol][0])
			self.choose_material(i)
			if materials[symbol][1] is None:
				pass
			elif materials[symbol][1] == MIN:
				self.index_min_buttons[i].SetValue(True)
			elif materials[symbol][1] == MAX:
				self.index_max_buttons[i].SetValue(True)
			else:
				self.index_buttons[i].SetValue(True)
				self.index_boxes[i].SetValue(str(materials[symbol][1]))
			self.material_boxes[i].Enable()
		
		for i in range(len(materials), self.nb_material_boxes):
			self.symbol_boxes[i].SetValue("")
			self.material_boxes[i].SetValue("")
			self.material_boxes[i].Disable()
			self.index_min_buttons[i].Disable()
			self.index_max_buttons[i].Disable()
			self.index_buttons[i].Disable()
			self.index_boxes[i].Disable()
	
	
	######################################################################
	#                                                                    #
	# apply                                                              #
	#                                                                    #
	######################################################################
	def apply(self):
		"""Apply the stack formula to the filter"""
		
		side = self.get_side()
		
		formula = self.formula_box.GetValue()
		
		materials = {}
		for i in range(self.nb_material_boxes):
			symbol = self.symbol_boxes[i].GetValue()
			if symbol:
				material_name = self.material_boxes[i].GetValue()
				material_nb = self.filter.get_material_nb(material_name)
				material = self.filter.get_material(material_nb)
				if material.is_mixture():
					if self.index_min_buttons[i].GetValue():
						index = MIN
					elif self.index_max_buttons[i].GetValue():
						index = MAX
					else:
						index = float(self.index_boxes[i].GetValue())
				else:
					index = None
				materials[symbol] = (material_name, index)
		
		if (formula, materials) != self.filter.get_stack_formula(side):
			self.filter.set_stack_formula(formula, materials, side)
			self.filter.apply_stack_formula(side)
			
			return True
		
		else:
			return False



########################################################################
#                                                                      #
# formula_validator                                                    #
#                                                                      #
########################################################################
class formula_validator(wx.PyValidator):
	"""Validator for stack formula (just the formula)"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, condition = None):
		"""Initialize the validator
		
		This method takes one optional argument:
		  condition   a function that is tested to verify if the validation
		              of the formula should be done or None for no
		              condition (default value is None)."""
		
		wx.PyValidator.__init__(self)
		
		# This validator will be tested only if the function given as
		# condition returns TRUE. Set to None to avoid a condition being
		# tested.
		self.condition = condition
		
		self.Bind(wx.EVT_CHAR, self.OnChar)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.condition)
	
	
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
	# OnChar                                                             #
	#                                                                    #
	######################################################################
	def OnChar(self, event):
		"""Verify that a caracter entered in the formula is appropriate
		
		This method takes a single argument:
		  event              the event."""
		
		key = event.GetKeyCode()
		
		# Accept delete and special caracters.
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		char = chr(key)
		
		# Accept various kind of spaces.
		if char.isspace():
			event.Skip()
			return
		
		# Accept digits.
		if char in string.digits:
			event.Skip()
			return
		
		# Accept lowercase and uppercase.
		if char in string.ascii_letters:
			event.Skip()
			return
		
		# Accept ".", "*", "/", "^", "(" and ")".
		if char in ".*/^()":
			event.Skip()
			return
		
		if not wx.Validator_IsSilent():
			wx.Bell()
		
		# By don't calling event.Skip(), the event is not passed to the
		# next control.
		return
	
	
	######################################################################
	#                                                                    #
	# OnKillFocus                                                        #
	#                                                                    #
	######################################################################
	def OnKillFocus(self, event):
		"""Validate the formula when the control looses focus
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the value.
		window = self.GetWindow()
		answer = window.GetValue()
		
		# Replace line changes by 1 or 2 spaces depending on the platform
		# in order for the selection position to work correctly.
		if sys.platform == "win32":
			answer = answer.replace("\n", "  ")
		else:
			answer = answer.replace("\n", " ")
		
		# If there is no value, this is an error. By not calling
		# event.Skip(), the event is not passed to the next control.
		if len(answer) == 0:
			return
		
		# Try to interpret the stack formula.
		try:
			analyse_stack_formula(answer)
		except stack_error, error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.SetSelection(error.get_position(), error.get_position()+1)
			return
		
		event.Skip()
		return
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the formula
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is an appropriate
		stack formula or False otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		window = self.GetWindow()
		answer = window.GetValue()
		
		# Try to interpret the stack formula.
		try:
			analyse_stack_formula(answer)
		except stack_error, error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.SetSelection(error.get_position(), error.get_position()+1)
			return False
		
		return True



########################################################################
#                                                                      #
# symbol_validator                                                     #
#                                                                      #
########################################################################
class symbol_validator(wx.PyValidator):
	"""Validator for stack formula symbols"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, condition = None):
		"""Initialize the validator
		
		This method takes one optional argument:
		  condition   a function that is tested to verify if the validation
		              of the symbol should be done or None for no
		              condition (default value is None)."""
		
		wx.PyValidator.__init__(self)
		
		# This validator will be tested only if the function given as
		# condition returns TRUE. Set to None to avoid a condition being
		# tested.
		self.condition = condition
		
		self.Bind(wx.EVT_CHAR, self.OnChar)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.condition)
	
	
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
	# OnChar                                                             #
	#                                                                    #
	######################################################################
	def OnChar(self, event):
		"""Verify that a caracter is appropriate for a symbol
		
		This method takes a single argument:
		  event              the event."""
		
		key = event.GetKeyCode()
		
		# Accept delete and special caracters.
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		char = chr(key)
		
		# Accept only lowercase and uppercase.
		if char not in string.ascii_letters:
			if not wx.Validator_IsSilent():
				wx.Bell()
			return
		
		# Get the value.
		window = self.GetWindow()
		answer = window.GetValue()
		selection = window.GetSelection()
		
		# The symbol must be only one caracter long, therefore there must
		# be nothing in the box to enter a new caracter or what is already
		# there must be selected.
		if len(answer) - (selection[1]-selection[0]) + 1 > 1:
			if not wx.Validator_IsSilent():
				wx.Bell()
			return
		
		# The symbol must not be used in other boxes. (Calling get_symbols
		# at this point won't return the content of the presently edited
		# window since the value has not been passed yet).
		if char in window.GetParent().get_symbols():
			if not wx.Validator_IsSilent():
				wx.Bell()
			return
		
		event.Skip()
		return
	
	
	######################################################################
	#                                                                    #
	# OnKillFocus                                                        #
	#                                                                    #
	######################################################################
	def OnKillFocus(self, event):
		"""Validate the symbol when the control looses focus
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the value.
		window = self.GetWindow()
		answer = window.GetValue()
		
		# The symbol must be only one caracter long.
		if len(answer) > 1:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.SetSelection(0, len(answer))
			return
		
		event.Skip()
		return
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the symbol
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is an appropriate
		stack formula symbol or False otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		# Get the value.
		window = self.GetWindow()
		answer = window.GetValue()
		
		# The symbol must be only one caracter long.
		if len(answer) > 1:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.SetSelection(0, len(answer))
			return False
		
		return True
