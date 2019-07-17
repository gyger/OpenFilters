# GUI_validators.py
# 
# Some simple validators for the dialogs of OpenFilters.
# 
# Copyright (c) 2003-2009,2013,2015 Stephane Larouche.
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
import string

import materials
import color



########################################################################
#                                                                      #
# int_validator                                                        #
#                                                                      #
########################################################################
class int_validator(wx.PyValidator):
	"""Validator for integer number
	
	This class provides a validator for an integer number. It is possible
	to specify a minimum and a maximum values as well as a condition when
	the validation is performed."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, minimum = None, maximum = None, condition = None):
		"""Initialize the validator
		
		This method takes 3 optional arguments:
		  minimum     (optional) the minimal acceptable value or None for
		              no limit (default value is None);
		  maximum     (optional) the maximal acceptable value or None for
		              no limit (default value is None);
		  condition   (optional) a function that is tested to verify if the
		              validation of the integer should be done or None for
		              no condition (default value is None).
		For minimum and maximum, either a callable or a numerical value can
		be provided. The truth testing of the condition function follows
		Python truth testing. For example, if you want the content of a
		TextCtrl to be evaluated only if a value is given, you could use
		  my_TextCtrl.SetValidator(condition = my_TextCtrl.GetValue)."""
		
		wx.PyValidator.__init__(self)
		
		self.minimum = minimum
		self.maximum = maximum
		self.condition = condition
		
		self.Bind(wx.EVT_CHAR, self.OnChar)
	
	
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
	# set_limits                                                         #
	#                                                                    #
	######################################################################
	def set_limits(self, minimum = None, maximum = None):
		"""Set the acceptable limits
		
		This method takes 2 optional arguments:
		  minimum     (optional) the minimal acceptable value or None for
		              no limit (default value is None);
		  maximum     (optional) the maximal acceptable value or None for
		              no limit (default value is None)."""
		
		self.minimum = minimum
		self.maximum = maximum
	
	
	######################################################################
	#                                                                    #
	# set_condition                                                      #
	#                                                                    #
	######################################################################
	def set_condition(self, condition = None):
		"""Set the condition in which the validation is done
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the integer should be done or None for
		              no condition (default value is None)."""
		
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# OnChar                                                             #
	#                                                                    #
	######################################################################
	def OnChar(self, event):
		"""Verify that the caracters entered in the control are digits"""
		
		key = event.GetKeyCode()
		
		# Accept delete and special caracters.
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		window = self.GetWindow()
		answer = window.GetValue()
		selection_span = window.GetSelection()
		
		# Accept the digits, except before a dash.
		if chr(key) in string.digits:
			if selection_span[1] == len(answer) or answer[selection_span[1]] != "-":
				event.Skip()
				return
		
		# Accept a dash, if the minimum is negative, it is the first
		# character and there is no other dash.
		elif chr(key) == "-":
			if self.minimum is not None and self.minimum < 0.0:
				if selection_span[0] == 0 and "-" not in answer[selection_span[1]:]:
					event.Skip()
					return
		
		if not wx.Validator_IsSilent(): wx.Bell()
		
		# Since event.Skip() is not called, the event is not passed to the
		# control.
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is an integer
		within the imposed limits or False otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		error = False
		
		window = self.GetWindow()
		answer = window.GetValue()
		
		# First try to convert the value to a int.
		try:
			value = int(answer)
		except ValueError:
			error = True
		
		# Then verify that the value fits in acceptable values.
		if not error:
			if self.minimum is not None:
				if callable(self.minimum):
					minimum = self.minimum()
				else:
					minimum = self.minimum
				if value < minimum:
					error = True
			if self.maximum is not None:
				if callable(self.maximum):
					maximum = self.maximum()
				else:
					maximum = self.maximum
				if value > maximum:
					error = True
		
		if error:
			if not wx.Validator_IsSilent(): wx.Bell()
			window.SetFocus()
			window.SetSelection(0, len(answer))
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# float_validator                                                      #
#                                                                      #
########################################################################
class float_validator(wx.PyValidator):
	"""Validator for float number
	
	This class provides a validator for a float number. It is possible to
	specify a minimum and a maximum values as well as a condition when
	the validation is performed."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, minimum = None, maximum = None, condition = None, include_minimum = True, include_maximum = True):
		"""Initialize the validator
		
		This method takes 5 optional arguments:
		  minimum          (optional) the minimal acceptable value or None
		                   for no limit (default value is None);
		  maximum          (optional) the maximal acceptable value or None
		                   for no limit (default value is None);
		  condition        (optional) a function that is tested to verify
		                   if the validation of the integer should be done
		                   or None for no condition (default value is
		                   None);
		  include_minimum  (optional) a boolean indicating if the range of
		                   acceptable values includes the minimum (default
		                   is True);
		  include_maximum  (optional) a boolean indicating if the range
		                   of acceptable values include the maximum
		                   (default is True).
		For minimum and maximum, either a callable or a numerical value can
		be provided. The truth testing of the condition function follows
		Python truth testing. For example, if you want the content of a
		TextCtrl to be evaluated only if a value is given, you could use
		  my_TextCtrl.SetValidator(condition = my_TextCtrl.GetValue)."""
		
		wx.PyValidator.__init__(self)
		
		self.minimum = minimum
		self.maximum = maximum
		self.condition = condition
		self.include_minimum = include_minimum
		self.include_maximum = include_maximum
		
		self.Bind(wx.EVT_CHAR, self.OnChar)
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.minimum, self.maximum, self.condition, self.include_minimum, self.include_maximum)
	
	
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
	# set_limits                                                         #
	#                                                                    #
	######################################################################
	def set_limits(self, minimum = None, maximum = None):
		"""Set the acceptable limits
		
		This method takes 2 optional arguments:
		  minimum          (optional) the minimal acceptable value or None
		                   for no limit (default value is None);
		  maximum          (optional) the maximal acceptable value or None
		                   for no limit (default value is None)."""
		
		self.minimum = minimum
		self.maximum = maximum
	
	
	######################################################################
	#                                                                    #
	# set_condition                                                      #
	#                                                                    #
	######################################################################
	def set_condition(self, condition = None):
		"""Set the condition in which the validation is done
		
		This method takes a single optional argument:
		  condition        a function that is tested to verify if the
		                   validation of the integer should be done or None
		                   for no condition (default value is None)."""
		
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# set_include_limits                                                 #
	#                                                                    #
	######################################################################
	def set_include_limits(self, include_minimum = True, include_maximum = True):
		"""Set if the range acceptable values includes its limits
		
		This method takes 2 optional arguments:
		  include_minimum  (optional) a boolean indicating if the range of
		                   acceptable values includes the minimum (default
		                   is True);
		  include_maximum  (optional) a boolean indicating if the range of
		                   acceptable values include the maximum (default
		                   is True)."""
		
		self.include_minimum = include_minimum
		self.include_maximum = include_maximum
	
	
	######################################################################
	#                                                                    #
	# OnChar                                                             #
	#                                                                    #
	######################################################################
	def OnChar(self, event):
		"""Verify that the caracters entered in the control are compatible
		with a float number"""
		
		key = event.GetKeyCode()
		
		# Accept delete and special caracters.
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		window = self.GetWindow()
		answer = window.GetValue()
		selection_span = window.GetSelection()
		
		# Accept the digits, except before a dash.
		if chr(key) in string.digits:
			if selection_span[1] == len(answer) or answer[selection_span[1]] != "-":
				event.Skip()
				return
		
		# Dash can be used in negative numbers and in the exponential
		# notation.
		elif chr(key) == "-":
			
			# If the dash is at the beginning of the control, the minimum
			# must be negative.
			if selection_span[0] == 0:
				if self.minimum is None or self.minimum < 0.0:
					if selection_span[1] == len(answer) or answer[selection_span[1]] != "-":
						event.Skip()
						return
			
			# If the dash is not at the beginning of the control, it must
			# immediatly follow an e.
			else:
				if answer[selection_span[0]-1] in ["e", "E"] and "-" not in answer[selection_span[1]:]:
					event.Skip()
					return
		
		# If the character is a point, verify that the control doesn't
		# already contain a point or that point is in the selection.
		# (window.GetValue() gets the value before the addition of the new
		# decimal point.)
		elif chr(key) == ".":
			
			before = answer[:selection_span[0]]
			
			if "e" not in before and "E" not in before:
				if not "." in answer or "." in answer[selection_span[0]:selection_span[1]]:
					event.Skip()
					return
		
		# If the character is a e, verify that the control doesn't
		# already contain a e that is not in the selection.
		elif chr(key) in ["e", "E"]:
			
			selection = answer[selection_span[0]:selection_span[1]]
			
			if "e" not in answer and "E" not in answer or "e" in selection or "E" in selection:
				if "." not in answer[selection_span[1]:]:
					event.Skip()
					return
		
		if not wx.Validator_IsSilent(): wx.Bell()
		
		# Since event.Skip() is not called, the event is not passed to the
		# control.
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent           the control that is validated
		and it returns True if the content of the control is a float within
		the imposed limits or False otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		error = False
		
		window = self.GetWindow()
		answer = window.GetValue()
		
		# First try to convert the value to a float.
		try:
			value = float(answer)
		except ValueError:
			error = True
		
		# Check if the value is NaN or another similar condition.
		if not error:
			if value - value != 0.0:
				error = True
		
		# Then verify that the value fits in acceptable values.
		if not error:
			if self.minimum is not None:
				if callable(self.minimum):
					minimum = self.minimum()
				else:
					minimum = self.minimum
				if self.include_minimum:
					if value < minimum:
						error = True
				else:
					if value <= minimum:
						error = True
			if self.maximum is not None:
				if callable(self.maximum):
					maximum = self.maximum()
				else:
					maximum = self.maximum
				if self.include_maximum:
					if value > maximum:
						error = True
				else:
					if value >= maximum:
						error = True
		
		if error:
			if not wx.Validator_IsSilent(): wx.Bell()
			window.SetFocus()
			window.SetSelection(0, len(answer))
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# material_validator                                                   #
#                                                                      #
########################################################################
class material_validator(wx.PyValidator):
	"""Validator for material
	
	This class provides a validator for materials. It is possible to
	specify the kind of material as well as a condition when the
	validation is performed."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, material_catalog = None, kind = None, condition = None):
		"""Initialize the validator
		
		This method takes 2 optional arguments:
		  material_catalog  (optional) the material catalog to use to
		                    determine if the material exists, if not
		                    provided, the default materials will be used;
		  kind              (optional) the specific kind of material that
		                    is desired (MATERIAL_REGULAR or
		                    MATERIAL_MIXTURE) or None for any kind of
		                    material (default value is None);
		  condition         (optional) a function that is tested to verify
		                    if the validation of the integer should be done
		                    or None for no condition (default value is
		                    None).
		The truth testing of the condition function follows Python truth
		testing. For example, if you want the content of a TextCtrl to be
		evaluated only if a value is given, you could use
		  my_TextCtrl.SetValidator(condition = my_TextCtrl.GetValue)."""
		
		wx.PyValidator.__init__(self)
		
		if material_catalog:
			self.material_catalog = material_catalog
		else:
			self.material_catalog = materials.material_catalog()
		
		self.kind = kind
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.material_catalog, self.kind, self.condition)
	
	
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
	# set_kind                                                           #
	#                                                                    #
	######################################################################
	def set_kind(self, kind = None):
		"""Set the kind of material desired
		
		This method takes a single optional argument:
		  kind        (optional) the specific kind of material that is
		              desired (MATERIAL_REGULAR or MATERIAL_MIXTURE) or
		              None for any kind of material (default value is
		              None)."""
		
		self.kind = kind
	
	
	######################################################################
	#                                                                    #
	# set_condition                                                      #
	#                                                                    #
	######################################################################
	def set_condition(self, condition = None):
		"""Set the condition in which the validation is done
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the integer should be done or None for
		              no condition (default value is None)."""
		
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is valid
		materials of the imposed kind or False otherwise."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		window = self.GetWindow()
		answer = window.GetValue()
		
		error = False
		
		# If there is no value, the material doesn't open correctly or is
		# the wrong kind, validation fails.
		if len(answer) == 0:
			error = True
		try:
			material = self.material_catalog.get_material(answer)
		except materials.material_error:
			error = True
		else:
			if self.kind is not None and material.get_kind() != self.kind:
				error = True
		
		# If an error occured, set the focus to the control and return
		# False.
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.SetSelection(0, len(answer))
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# illuminant_validator                                                 #
#                                                                      #
########################################################################
class illuminant_validator(wx.PyValidator):
	"""Validator for illuminant
	
	This class provides a validator for illuminant choice. It tries to
	load the illuminant file to check of it is correct."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, condition = None):
		"""Initialize the validator
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the illuminant should be done or None
		              for no condition (default value is None).
		The truth testing of the condition function follows Python truth
		testing."""
		
		wx.PyValidator.__init__(self)
		
		self.condition = condition
	
	
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
	# set_condition                                                      #
	#                                                                    #
	######################################################################
	def set_condition(self, condition = None):
		"""Set the condition in which the validation is done
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the illuminant should be done or None
		              for no condition (default value is None)."""
		
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is a valid
		illuminant or False otherwise.
		
		It also shows an error message if the illuminant is invalid."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		window = self.GetWindow()
		
		# Try to get the illuminant to make sure that the file is correct.
		try:
			color.get_illuminant(window.GetStringSelection())
		except color.color_error, error:
			wx.MessageBox("An error occured while reading illuminant file.\n\n%s" % error, "Illuminant error", wx.ICON_ERROR|wx.OK)
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# observer_validator                                                   #
#                                                                      #
########################################################################
class observer_validator(wx.PyValidator):
	"""Validator for observer
	
	This class provides a validator for observer choice. It tries to load
	the observer file to check of it is correct."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, condition = None):
		"""Initialize the validator
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the observer should be done or None for
		              no condition (default value is None).
		The truth testing of the condition function follows Python truth
		testing."""
		
		wx.PyValidator.__init__(self)
		
		self.condition = condition
	
	
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
	# set_condition                                                      #
	#                                                                    #
	######################################################################
	def set_condition(self, condition = None):
		"""Set the condition in which the validation is done
		
		This method takes a single optional argument:
		  condition   (optional) a function that is tested to verify if the
		              validation of the observer should be done or None for
		              no condition (default value is None)."""
		
		self.condition = condition
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the content of the control is a valid
		observer or False otherwise.
		
		It also shows an error message if the observer is invalid."""
		
		# If the condition for testing is not filled, the test is not
		# performed.
		if self.condition and not self.condition():
			return True
		
		window = self.GetWindow()
		
		# Try to get the observer to make sure that the file is correct.
		try:
			color.get_observer(window.GetStringSelection())
		except color.color_error, error:
			wx.MessageBox("An error occured while reading observer file.\n\n%s" % error, "Observer error", wx.ICON_ERROR|wx.OK)
			window.SetFocus()
			window.Refresh()
			return False
		
		return True
