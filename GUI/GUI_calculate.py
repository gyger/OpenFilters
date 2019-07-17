# GUI_calculate.py
# 
# Dialogs for the calculation of the properties in the GUI of Filters.
# 
# Copyright (c) 2001-2009,2015 Stephane Larouche.
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

from definitions import *
import config
import color

from GUI_validators import float_validator,\
                           illuminant_validator,\
                           observer_validator



########################################################################
#                                                                      #
# calculate_dialog_validator                                           #
#                                                                      #
########################################################################
class calculate_dialog_validator(wx.PyValidator):
	"""Generic validator for calculate dialogs"""
	
	
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
		"""Validate the content of the dialog
		
		This method takes a single argument:
		  parent             the dialog that is validated
		and it returns True.
		
		To do validation, this class must be derived and the Validate
		method implemented properly."""
		
		return True



########################################################################
#                                                                      #
# calculate_color_trajectory_dialog_validator                          #
#                                                                      #
########################################################################
class calculate_color_trajectory_dialog_validator(calculate_dialog_validator):
	"""Validator for the color trajectory dialog"""
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the color trajectory dialog
		
		This method takes a single argument:
		  parent             the dialog that is validated
		and it returns True if the range of angles is correctly defined or
		False otherwise."""
		
		# Verify that to_angle is larger than from_angle.
		from_angle = float(parent.from_angle_box.GetValue())
		to_angle = float(parent.to_angle_box.GetValue())
		if to_angle < from_angle:
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.to_angle_box.SetFocus()
			parent.to_angle_box.SetSelection(0, 1000)
			parent.Refresh()
			return False
		
		# Verify that by_angle is smaller than the difference between
		# from_angle and to_angle.
		by_angle = float(parent.by_angle_box.GetValue())
		if by_angle >= (to_angle - from_angle):
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.by_angle_box.SetFocus()
			parent.by_angle_box.SetSelection(0, 1000)
			parent.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# calculate_dialog                                                     #
#                                                                      #
########################################################################
class calculate_dialog(wx.Dialog):
	"""A generic class to define calculation dialogs
	
	All calculation dialogs derive from this class."""
	
	title = ""
	include_spectroscopic = False
	s_and_p_only = False
	validator = calculate_dialog_validator
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter):
		"""Initialize an instance of the calculation dialog
		
		This method takes 2 arguments:
		  parent             the dialog's parent;
		  filter             the filter whose properties are calculated."""
		
		self.parent = parent
		self.filter = filter
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.content_sizer = wx.FlexGridSizer(0, 2, 15, 5)
		
		self.add_content()
		
		self.main_sizer.Add(self.content_sizer, 0, wx.GROW|wx.ALL, 25)
		
		self.add_buttons()
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		The derived class must implement this method."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# add_wavelength_box                                                 #
	#                                                                    #
	######################################################################
	def add_wavelength_box(self):
		"""Add a wavelength box to the dialog"""
		
		self.wavelength_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER)
		if self.include_spectroscopic:
			self.single_wvl_button = wx.RadioButton(self, -1, "", style = wx.RB_GROUP)
			self.spectroscopic_button = wx.RadioButton(self, -1, "spectroscopic")
			self.wavelength_box.SetValidator(float_validator(0.0, None, self.single_wvl_button.GetValue, include_minimum = False))
		else:
			self.wavelength_box.SetValidator(float_validator(0.0, None, include_minimum = False))
		self.wavelength_box.Bind(wx.EVT_TEXT, self.on_wavelength_box)
		self.wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		self.content_sizer.Add(wx.StaticText(self, -1, "Wavelength:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		wavelength_sizer_1 = wx.BoxSizer(wx.VERTICAL)
		wavelength_sizer_1_1 = wx.BoxSizer(wx.HORIZONTAL)
		if self.include_spectroscopic:
			wavelength_sizer_1_1.Add(self.single_wvl_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
		wavelength_sizer_1_1.Add(self.wavelength_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		wavelength_sizer_1_1.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelength_sizer_1.Add(wavelength_sizer_1_1, 0, wx.ALIGN_LEFT, 5)
		if self.include_spectroscopic:
			wavelength_sizer_1.Add(self.spectroscopic_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		self.content_sizer.Add(wavelength_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# The default value.
		center_wavelength = self.filter.get_center_wavelength()
		self.wavelength_box.SetValue(("%s" % center_wavelength))
	
	
	######################################################################
	#                                                                    #
	# add_angle_box                                                      #
	#                                                                    #
	######################################################################
	def add_angle_box(self):
		"""Add an angle box to the dialog"""
		
		self.angle_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, include_maximum = False))
		self.angle_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		angle_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		angle_sizer_1.Add(self.angle_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		angle_sizer_1.Add(wx.StaticText(self, -1, "degrees"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.content_sizer.Add(wx.StaticText(self, -1, "Angle:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.content_sizer.Add(angle_sizer_1, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# The default value.
		self.angle_box.SetValue("0.0")
	
	
	######################################################################
	#                                                                    #
	# add_angle_boxes                                                    #
	#                                                                    #
	######################################################################
	def add_angle_boxes(self):
		"""Add angle boxes to the dialog"""
		
		self.from_angle_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, include_maximum = False))
		self.to_angle_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, include_maximum = False))
		self.by_angle_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.from_angle_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.to_angle_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.by_angle_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		angle_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		angle_sizer_1.Add(self.from_angle_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		angle_sizer_1.Add(wx.StaticText(self, -1, "to"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		angle_sizer_1.Add(self.to_angle_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		angle_sizer_1.Add(wx.StaticText(self, -1, "every"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		angle_sizer_1.Add(self.by_angle_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		angle_sizer_1.Add(wx.StaticText(self, -1, "degrees"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.content_sizer.Add(wx.StaticText(self, -1, "Angles:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.content_sizer.Add(angle_sizer_1, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# The default values.
		self.from_angle_box.SetValue("0.0")
		self.to_angle_box.SetValue("89.0")
		self.by_angle_box.SetValue("1.0")
	
	
	######################################################################
	#                                                                    #
	# add_polarization_choice                                            #
	#                                                                    #
	######################################################################
	def add_polarization_choice(self):
		"""Add polarization choices to the dialog"""
		
		self.s_polarized_button = wx.RadioButton(self, -1, "s", style = wx.RB_GROUP)
		self.p_polarized_button = wx.RadioButton(self, -1, "p")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.s_polarized_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.p_polarized_button)
		if not self.s_and_p_only:
			self.unpolarized_button = wx.RadioButton(self, -1, "unpolarized")
			self.other_polarizations_button = wx.RadioButton(self, -1, "")
			self.other_polarizations_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, self.other_polarizations_button.GetValue))
			self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.unpolarized_button)
			self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.other_polarizations_button)
			self.other_polarizations_box.Bind(wx.EVT_TEXT, self.on_other_polarizations_box)
			self.other_polarizations_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		self.content_sizer.Add(wx.StaticText(self, -1, "Polarization:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_TOP)
		polarization_choices_sizer_1 = wx.BoxSizer(wx.VERTICAL)
		polarization_choices_sizer_1_1 = wx.BoxSizer(wx.HORIZONTAL)
		polarization_choices_sizer_1_1.Add(self.s_polarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		polarization_choices_sizer_1_1.Add(self.p_polarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		if self.s_and_p_only:
			polarization_choices_sizer_1.Add(polarization_choices_sizer_1_1, 0, wx.ALIGN_LEFT)
		else:
			polarization_choices_sizer_1_1.Add(self.unpolarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
			polarization_choices_sizer_1.Add(polarization_choices_sizer_1_1, 0, wx.ALIGN_LEFT)
			polarization_choices_sizer_1_2 = wx.BoxSizer(wx.HORIZONTAL)
			polarization_choices_sizer_1_2.Add(self.other_polarizations_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
			polarization_choices_sizer_1_2.Add(self.other_polarizations_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			polarization_choices_sizer_1_2.Add(wx.StaticText(self, -1, "degrees"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
			polarization_choices_sizer_1.Add(polarization_choices_sizer_1_2, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		
		self.content_sizer.Add(polarization_choices_sizer_1, wx.ALIGN_LEFT|wx.ALIGN_TOP)
		
		# The default value.
		self.s_polarized_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# add_illuminant_and_observer_choices                                #
	#                                                                    #
	######################################################################
	def add_illuminant_and_observer_choices(self):
		"""Add illuminant and observe choices to the dialog"""
		
		self.illuminant_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_illuminant_names(), validator = illuminant_validator())
		self.observer_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_observer_names(), validator = observer_validator())
		
		self.content_sizer.Add(wx.StaticText(self, -1, "Illuminant:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.content_sizer.Add(self.illuminant_choice, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.content_sizer.Add(wx.StaticText(self, -1, "Observer:"), 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self.content_sizer.Add(self.observer_choice, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# The default values.
		illuminant = self.filter.get_illuminant()
		observer = self.filter.get_observer()
		self.illuminant_choice.SetSelection(self.illuminant_choice.FindString(illuminant))
		self.observer_choice.SetSelection(self.observer_choice.FindString(observer))
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add ok and cancel buttons to the dialog"""
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK, validator = self.validator()), 0, wx.ALL, 10)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.ALL, 10)
		
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER)
	
	
	######################################################################
	#                                                                    #
	# on_wavelength_box                                                  #
	#                                                                    #
	######################################################################
	def on_wavelength_box(self, event):
		"""Update the dialog when a value is entered in the wavelength box
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in the wavelength box,
		# automatically select the single wavelength button.
		if self.include_spectroscopic and self.wavelength_box.GetValue() != "":
			self.single_wvl_button.SetValue(True)
		
		event.Skip()
		
		
	######################################################################
	#                                                                    #
	# on_polarization_radio_button                                       #
	#                                                                    #
	######################################################################
	def on_polarization_radio_button(self, event):
		"""Update the dialog when a polarization button is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# When an a polarization is selected (except if it is the other
		# polarization), empty the other polarization box.
		if not self.s_and_p_only and not self.other_polarizations_button.GetValue():
			self.other_polarizations_box.Clear()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_other_polarizations_box                                         #
	#                                                                    #
	######################################################################
	def on_other_polarizations_box(self, event):
		"""Update the dialog when text is entered in the other
		polarizations box
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in the other polarizations box,
		# automatically select the other polarization button.
		if self.other_polarizations_box.GetValue() != "":
			self.other_polarizations_button.SetValue(True)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_enter                                                           #
	#                                                                    #
	######################################################################
	def on_enter(self, event):
		"""End the dialog (after validation) when the user presses enter
		
		This method takes a single argument:
		  event              the event."""
		
		if self.Validate():
			self.EndModal(wx.ID_OK)
	
	
	######################################################################
	#                                                                    #
	# get_wavelength                                                     #
	#                                                                    #
	######################################################################
	def get_wavelength(self):
		"""Get the wavelength defined in the wavelength box
		
		This method returns a single argument:
		  wavelength         the wavelength."""
		
		wavelength = float(self.wavelength_box.GetValue())
		
		return wavelength
	
	
	######################################################################
	#                                                                    #
	# get_wavelengths                                                    #
	#                                                                    #
	######################################################################
	def get_wavelengths(self):
		"""Get the wavelengths defined by the wavelength buttons and box
		
		This method returns a single argument:
		  wavelengths        the list of wavelengths."""
		
		if not self.include_spectroscopic or self.single_wvl_button.GetValue():
			wavelengths = [float(self.wavelength_box.GetValue())]
		else:
			wavelengths = self.filter.get_wavelengths()
		
		return wavelengths
	
	
	######################################################################
	#                                                                    #
	# get_angle                                                          #
	#                                                                    #
	######################################################################
	def get_angle(self):
		"""Get the angle defined in the angle box
		
		This method returns a single argument:
		  angle              the angle."""
		
		angle = float(self.angle_box.GetValue())
		
		return angle
	
	
	######################################################################
	#                                                                    #
	# get_angles                                                         #
	#                                                                    #
	######################################################################
	def get_angles(self):
		"""Get the angle defined in the angle boxes
		
		This method returns a single argument:
		  angles             the list of angles."""
		
		from_angle = float(self.from_angle_box.GetValue())
		to_angle = float(self.to_angle_box.GetValue())
		by_angle = float(self.by_angle_box.GetValue())
		
		nb_angles = int(math.ceil((to_angle-from_angle)/by_angle)+1)
		angles = [from_angle + i_angle*by_angle for i_angle in range(nb_angles)]
		angles[-1] = to_angle
		
		return angles
	
	
	######################################################################
	#                                                                    #
	# get_polarization                                                   #
	#                                                                    #
	######################################################################
	def get_polarization(self):
		"""Get the polarization defined by the polarization buttons and box
		
		This method returns a single argument:
		  polarization       the polarization."""
		
		if self.s_and_p_only:
			if self.s_polarized_button.GetValue():
				polarization = S
			elif self.p_polarized_button.GetValue():
				polarization = P
		else:
			if self.unpolarized_button.GetValue():
				polarization = UNPOLARIZED
			elif self.s_polarized_button.GetValue():
				polarization = S
			elif self.p_polarized_button.GetValue():
				polarization = P
			elif self.other_polarizations_button.GetValue():
				polarization = float(self.other_polarizations_box.GetValue())
		
		return polarization
	
	
	######################################################################
	#                                                                    #
	# get_illuminant_and_observer                                        #
	#                                                                    #
	######################################################################
	def get_illuminant_and_observer(self):
		"""Get the choosen illuminant and observer names
		
		This method returns 2 arguments:
		  illuminant         the name of the illuminant;
		  observer           the name of the observer."""
		
		illuminant = self.illuminant_choice.GetStringSelection()
		observer = self.observer_choice.GetStringSelection()
		
		return illuminant, observer
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get all the parameters necessary for calculation
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")



########################################################################
#                                                                      #
# calculate_spectrum_dialog                                            #
#                                                                      #
########################################################################
class calculate_spectrum_dialog(calculate_dialog):
	"""A generic dialog for most spectrum calculations showing the angle
	and the polarization"""
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_angle_box()
		self.add_polarization_choice()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the spectrum
		
		This method returns:
		  angle              the angle of incidence;
		  polarization       the polarization."""
		
		angle = self.get_angle()
		polarization = self.get_polarization()
		
		return angle, polarization



########################################################################
#                                                                      #
# calculate_reflection_dialog                                          #
#                                                                      #
########################################################################
class calculate_reflection_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the reflection spectrum"""
	
	title = "Calculate Reflection"



########################################################################
#                                                                      #
# calculate_transmission_dialog                                        #
#                                                                      #
########################################################################
class calculate_transmission_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the transmission spectrum"""
	
	title = "Calculate Transmission"



########################################################################
#                                                                      #
# calculate_absorption_dialog                                          #
#                                                                      #
########################################################################
class calculate_absorption_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the absorption spectrum"""
	
	title = "Calculate Absorption"



########################################################################
#                                                                      #
# calculate_ellipsometry_dialog                                        #
#                                                                      #
########################################################################
class calculate_ellipsometry_dialog(calculate_dialog):
	"""A dialog to calculate the ellipsometric spectrum"""
	
	title = "Calculate Ellipsometric Variables"
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_angle_box()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate ellipsometric spectrum
		
		This method returns:
		  angle              the angle of incidence."""
		
		angle = self.get_angle()
		
		return angle,



########################################################################
#                                                                      #
# calculate_reflection_phase_dialog                                    #
#                                                                      #
########################################################################
class calculate_reflection_phase_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the reflection phase spectrum"""
	
	title = "Calculate Reflection Phase"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_transmission_phase_dialog                                  #
#                                                                      #
########################################################################
class calculate_transmission_phase_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the transmission phase spectrum"""
	
	title = "Calculate Transmission Phase"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_reflection_GD_dialog                                       #
#                                                                      #
########################################################################
class calculate_reflection_GD_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the reflection GD spectrum"""
	
	title = "Calculate Reflection GD"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_transmission_GD_dialog                                     #
#                                                                      #
########################################################################
class calculate_transmission_GD_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the transmission GD spectrum"""
	
	title = "Calculate Transmission GD"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_reflection_GDD_dialog                                      #
#                                                                      #
########################################################################
class calculate_reflection_GDD_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the reflection GDD spectrum"""
	
	title = "Calculate Reflection GDD"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_transmission_GDD_dialog                                    #
#                                                                      #
########################################################################
class calculate_transmission_GDD_dialog(calculate_spectrum_dialog):
	"""A dialog to calculate the transmission GDD spectrum"""
	
	title = "Calculate Transmission GDD"
	s_and_p_only = True



########################################################################
#                                                                      #
# calculate_color_dialog                                               #
#                                                                      #
########################################################################
class calculate_color_dialog(calculate_dialog):
	"""A dialog to calculate the color"""
	
	title = "Calculate Color"
	include_spectroscopic = False
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_angle_box()
		self.add_polarization_choice()
		self.add_illuminant_and_observer_choices()
		
		# Select unpolarized light by default.
		self.unpolarized_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the color
		
		This method returns:
		  angle              the angle of incidence;
		  polarization       the polarization;
		  illuminant         the name of the illuminant;
		  observer           the name of the observer."""
		
		angle = self.get_angle()
		polarization = self.get_polarization()
		illuminant, observer = self.get_illuminant_and_observer()
		
		return angle, polarization, illuminant, observer



########################################################################
#                                                                      #
# calculate_color_trajectory_dialog                                    #
#                                                                      #
########################################################################
class calculate_color_trajectory_dialog(calculate_dialog):
	"""A dialog to calculate the color trajectory"""
	
	title = "Calculate Color Trajectory"
	include_spectroscopic = False
	validator = calculate_color_trajectory_dialog_validator
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_angle_boxes()
		self.add_polarization_choice()
		self.add_illuminant_and_observer_choices()
		
		# Select unpolarized light by default.
		self.unpolarized_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the color trajectory
		
		This method returns:
		  angles             the angles of incidence;
		  polarization       the polarization;
		  illuminant         the name of the illuminant;
		  observer           the name of the observer."""
		
		angles = self.get_angles()
		polarization = self.get_polarization()
		illuminant, observer = self.get_illuminant_and_observer()
		
		return angles, polarization, illuminant, observer



########################################################################
#                                                                      #
# calculate_diagram_dialog                                             #
#                                                                      #
########################################################################
class calculate_diagram_dialog(calculate_dialog):
	"""A generic dialog for diagram calculations"""
	
	include_spectroscopic = False
	s_and_p_only = True
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_wavelength_box()
		self.add_angle_box()
		self.add_polarization_choice()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the diagram
		
		This method returns:
		  wavelength         the wavelength;
		  angle              the angle of incidence;
		  polarization       the polarization.."""
		
		wavelength = self.get_wavelength()
		angle = self.get_angle()
		polarization = self.get_polarization()
		
		return wavelength, angle, polarization



########################################################################
#                                                                      #
# calculate_admittance_dialog                                          #
#                                                                      #
########################################################################
class calculate_admittance_dialog(calculate_diagram_dialog):
	"""A dialog to calculate the admittance locus"""
	
	title = "Calculate Admittance Diagram"



########################################################################
#                                                                      #
# calculate_circle_dialog                                              #
#                                                                      #
########################################################################
class calculate_circle_dialog(calculate_diagram_dialog):
	"""A dialog to calculate the circle diagram"""
	
	title = "Calculate Circle Diagram"



########################################################################
#                                                                      #
# calculate_electric_field_box                                         #
#                                                                      #
########################################################################
class calculate_electric_field_dialog(calculate_diagram_dialog):
	"""A dialog to calculate the electric field distribution"""
	
	title = "Calculate Electric Field"



########################################################################
#                                                                      #
# calculate_photometric_monitoring_dialog                              #
#                                                                      #
########################################################################
class calculate_photometric_monitoring_dialog(calculate_dialog):
	"""A generic dialog to calculate the photometric monitoring curves"""
	
	include_spectroscopic = True
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_wavelength_box()
		self.add_angle_box()
		self.add_polarization_choice()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the photometric
		monitoring curves
		
		This method returns:
		  wavelengths        the wavelengths;
		  angle              the angle of incidence;
		  polarization       the polarization."""
		
		wavelengths = self.get_wavelengths()
		angle = self.get_angle()
		polarization = self.get_polarization()
		
		return wavelengths, angle, polarization



########################################################################
#                                                                      #
# calculate_reflection_monitoring_dialog                               #
#                                                                      #
########################################################################
class calculate_reflection_monitoring_dialog(calculate_photometric_monitoring_dialog):
	"""A dialog to calculate the refection monitoring curves"""
	
	title = "Calculate Reflection Monitoring"



########################################################################
#                                                                      #
# calculate_transmission_monitoring_dialog                             #
#                                                                      #
########################################################################
class calculate_transmission_monitoring_dialog(calculate_photometric_monitoring_dialog):
	"""A dialog to calculate the transmission monitoring curves"""
	
	title = "Calculate Transmission Monitoring"



########################################################################
#                                                                      #
# calculate_ellipsometry_monitoring_dialog                             #
#                                                                      #
########################################################################
class calculate_ellipsometry_monitoring_dialog(calculate_dialog):
	"""A dialog to calculate the ellipsometric monitoring curves"""
	
	title = "Calculate Ellipsometry Monitoring"
	include_spectroscopic = True
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		self.add_wavelength_box()
		self.add_angle_box()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters necessary to calculate the reflection
		monitoring curves
		
		This method returns:
		  wavelengths        the wavelengths;
		  angle              the angle of incidence."""
		
		wavelengths = self.get_wavelengths()
		angle = self.get_angle()
		
		return wavelengths, angle
