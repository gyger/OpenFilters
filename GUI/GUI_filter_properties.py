# GUI_filter_properties.py
# 
# Dialog to set the properties of an optical filter.
# 
# Copyright (c) 2001-2005,2007-2010,2015 Stephane Larouche.
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
import color
import graded

from GUI_validators import int_validator, float_validator, material_validator,\
                           illuminant_validator, observer_validator



########################################################################
#                                                                      #
# filter_property_dialog_validator                                     #
#                                                                      #
########################################################################
class filter_property_dialog_validator(wx.PyValidator):
	"""Validator for the properties dialog"""
	
	
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
		"""Validate the content of the filter property dialog
		
		This method takes a single argument:
		  parent             the dialog that is validated
		and it returns True if the range of wavelengths is correctly
		defined or False otherwise."""
		
		# Verify that to_wavelength is larger that from_wavelength.
		from_wavelength = float(parent.from_wavelength_box.GetValue())
		to_wavelength = float(parent.to_wavelength_box.GetValue())
		if to_wavelength < from_wavelength:
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.to_wavelength_box.SetFocus()
			parent.to_wavelength_box.SetSelection(0, 1000)
			parent.Refresh()
			return False
		
		# Verify that by_wavelength is smaller than the difference between
		# from_wavelength and to_wavelength.
		by_wavelength = float(parent.by_wavelength_box.GetValue())
		if by_wavelength >= (to_wavelength - from_wavelength):
			if not wx.Validator_IsSilent():
				wx.Bell()
			parent.by_wavelength_box.SetFocus()
			parent.by_wavelength_box.SetSelection(0, 1000)
			parent.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# filter_property_dialog                                               #
#                                                                      #
########################################################################
class filter_property_dialog(wx.Dialog):
	"""Dialog to set the properties of of filter"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter):
		"""Initialize the dialog
		
		This method takes 2 arguments:
		  parent             the parent window;
		  filter             the filter whose property are set."""
		
		wx.Dialog.__init__(self, parent, -1, "Properties", style = wx.CAPTION)
		
		self.parent = parent
		self.filter = filter
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.add_content()
		
		# Create the buttons.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK, validator = filter_property_dialog_validator()), 0, wx.ALL, 10)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.ALL, 10)
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		
		# Fit the panel around the sizer to get the smaller possible panel.
		self.main_sizer.Fit(self)
		
		self.CenterOnParent()
		
		self.set_values()
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog."""
		
		# First, we will create all the necessary boxes. Then we will
		# create the layout with sizers, subsizers, text and the boxes.
		# Finally, we will set the actual values of the boxes.
		
		# So, let's create boxes.
		
		material_catalog = self.filter.get_material_catalog()
		
		# A static box for the substrate and mediums.
		substrate_and_medium_static_box = wx.StaticBox(self, -1, "Substrate and mediums" )
		
		# Boxes to specify the substrate and its thickness.
		self.substrate_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = material_validator(material_catalog, MATERIAL_REGULAR))
		self.substrate_thickness_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None))
		self.substrate_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.substrate_thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# Boxes to specify the front and back media.
		self.front_medium_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = material_validator(material_catalog, MATERIAL_REGULAR))
		self.back_medium_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = material_validator(material_catalog, MATERIAL_REGULAR))
		self.front_medium_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.back_medium_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# Check box for substrate and mediums consideration.
		self.dont_consider_substrate_box = wx.CheckBox(self, -1, "Don't consider substrate and mediums")
		self.Bind(wx.EVT_CHECKBOX, self.on_dont_consider_substrate, self.dont_consider_substrate_box)
		
		# A static box for the wavelengths.
		wavelengths_static_box = wx.StaticBox(self, -1, "Wavelengths")
		
		# A box to specify the center wavelength.
		self.center_wavelength_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.center_wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# 3 boxes to specify the range of wavelengths.
		self.from_wavelength_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.to_wavelength_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.by_wavelength_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.from_wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.to_wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		self.by_wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# A static box for specification of graded-index layers.
		graded_index_static_box = wx.StaticBox(self, -1, "Graded-index layers" )
		
		# Buttons and a box to specify the step spacing.
		self.step_spacing_deposition_button = wx.RadioButton(self, -1, "deposition", style = wx.RB_GROUP)
		self.step_spacing_other_button = wx.RadioButton(self, -1, "")
		self.step_spacing_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, self.step_spacing_other_button.GetValue))
		self.step_spacing_box.Bind(wx.EVT_TEXT, self.on_step_spacing_box)
		self.step_spacing_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# Box to specify the sublayer minimum thickness.
		self.minimum_thickness_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None))
		self.minimum_thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# A static box for the the illuminant and observer.
		color_static_box = wx.StaticBox(self, -1, "Color" )
		
		# Choices to specify the illuminant and the observer.
		self.illuminant_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_illuminant_names(), validator = illuminant_validator())
		self.observer_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_observer_names(), validator = observer_validator())
		
		# A static box for the analysis.
		analysis_static_box = wx.StaticBox(self, -1, "Analysis" )
		
		# Check box for backside consideration.
		self.consider_backside_box = wx.CheckBox(self, -1, "Consider backside")
		
		# Buttons for the ellipsometer type.
		self.RAE_button = wx.RadioButton(self, -1, "RAE", style = wx.RB_GROUP)
		self.RPE_button = wx.RadioButton(self, -1, "RPE")
		self.RCE_button = wx.RadioButton(self, -1, "RCE")
		
		# Box for the Delta min.
		self.Delta_min_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(-360.0, 0.0))
		self.Delta_min_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# A static box for the monitoring.
		monitoring_static_box = wx.StaticBox(self, -1, "Monitoring" )
		
		# Check box for backside consideration on monitoring.
		self.consider_backside_on_monitoring_box = wx.CheckBox(self, -1, "Consider backside")
		
		# Buttons for the monitoring ellipsometer type.
		self.monitoring_RAE_button = wx.RadioButton(self, -1, "RAE", style = wx.RB_GROUP)
		self.monitoring_RPE_button = wx.RadioButton(self, -1, "RPE")
		self.monitoring_RCE_button = wx.RadioButton(self, -1, "RCE")
		
		# Box for the monitoring Delta min.
		self.monitoring_Delta_min_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(-360.0, 0.0))
		self.monitoring_Delta_min_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		# A box to specify the monitoring sublayer thickness.
		self.monitoring_sublayer_thickness_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.monitoring_sublayer_thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		
		# Now lets create a layout.
		
		# First we arrange the elements refering to the substrate and mediums.
		substrate_and_medium_sizer = wx.StaticBoxSizer(substrate_and_medium_static_box, wx.VERTICAL)
		substrate_and_medium_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		substrate_and_medium_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		substrate_and_medium_sizer_1.Add(wx.StaticText(self, -1, "Substrate:"),
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		substrate_and_medium_sizer_1.Add(self.substrate_box,
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		substrate_and_medium_sizer_1.Add(wx.StaticText(self, -1, "Thickness:"),
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		substrate_and_medium_sizer_1.Add(self.substrate_thickness_box,
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		substrate_and_medium_sizer_1.Add(wx.StaticText(self, -1, "mm"),
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		substrate_and_medium_sizer_2.Add(wx.StaticText(self, -1, "Front medium:"),
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		substrate_and_medium_sizer_2.Add(self.front_medium_box,
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		substrate_and_medium_sizer_2.Add(wx.StaticText(self, -1, "Back medium:"),
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		substrate_and_medium_sizer_2.Add(self.back_medium_box,
		                                 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		substrate_and_medium_sizer.Add(substrate_and_medium_sizer_1, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
		substrate_and_medium_sizer.Add(substrate_and_medium_sizer_2, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
		substrate_and_medium_sizer.Add(self.dont_consider_substrate_box, 0, wx.ALL, 5)
		
		# Then we arrange the elements refering to the wavelengths.
		wavelengths_sizer = wx.StaticBoxSizer(wavelengths_static_box, wx.VERTICAL)
		wavelengths_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		wavelengths_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		wavelengths_sizer_1.Add(wx.StaticText(self, -1, "Reference wavelength:"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		wavelengths_sizer_1.Add(self.center_wavelength_box,
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_1.Add(wx.StaticText(self, -1, "nm"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		wavelengths_sizer_2.Add(wx.StaticText(self, -1, "Wavelengths:"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		wavelengths_sizer_2.Add(self.from_wavelength_box,
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_2.Add(wx.StaticText(self, -1, "to"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_2.Add(self.to_wavelength_box,
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_2.Add(wx.StaticText(self, -1, "every"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_2.Add(self.by_wavelength_box,
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		wavelengths_sizer_2.Add(wx.StaticText(self, -1, "nm"),
		                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		wavelengths_sizer.Add(wavelengths_sizer_1, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
		wavelengths_sizer.Add(wavelengths_sizer_2, 0, wx.ALL, 5)
		
		# Then we arrange the elements refering to graded-index layers.
		graded_index_sizer = wx.StaticBoxSizer(graded_index_static_box, wx.VERTICAL)
		graded_index_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		graded_index_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		graded_index_sizer_1.Add(wx.StaticText(self, -1, "Step spacing:"),
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		graded_index_sizer_1.Add(self.step_spacing_deposition_button,
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		graded_index_sizer_1.Add(self.step_spacing_other_button,
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		graded_index_sizer_1.Add(self.step_spacing_box,
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		graded_index_sizer_2.Add(wx.StaticText(self, -1, "Sublayer minimum thickness:"),
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		graded_index_sizer_2.Add(self.minimum_thickness_box,
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		graded_index_sizer_2.Add(wx.StaticText(self, -1, "nm"),
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		graded_index_sizer.Add(graded_index_sizer_1, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
		graded_index_sizer.Add(graded_index_sizer_2, 0, wx.ALL, 5)
		
		# Then we arrange the elements refering to color.
		color_sizer = wx.StaticBoxSizer(color_static_box, wx.VERTICAL)
		color_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		color_sizer_1.Add(wx.StaticText(self, -1, "Illuminant:"),
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		color_sizer_1.Add(self.illuminant_choice,
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		color_sizer_1.Add(wx.StaticText(self, -1, "Observer:"),
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		color_sizer_1.Add(self.observer_choice,
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		color_sizer.Add(color_sizer_1, 0, wx.ALL, 5)
		
		# Then we arrange the elements refering to the analysis.
		analysis_sizer = wx.StaticBoxSizer(analysis_static_box, wx.VERTICAL)
		analysis_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		analysis_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		analysis_sizer_1.Add(wx.StaticText(self, -1, "Ellipsometer type:"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		analysis_sizer_1.Add(self.RAE_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		analysis_sizer_1.Add(self.RPE_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		analysis_sizer_1.Add(self.RCE_button,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		analysis_sizer_2.Add(wx.StaticText(self, -1, "Delta min:"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		analysis_sizer_2.Add(self.Delta_min_box,
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		analysis_sizer_2.Add(wx.StaticText(self, -1, "degrees"),
		                     0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		analysis_sizer.Add(self.consider_backside_box,
		                   0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		analysis_sizer.Add(analysis_sizer_1,
		                   0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		analysis_sizer.Add(analysis_sizer_2,
		                   0, wx.ALIGN_LEFT|wx.ALL, 5)
		
		# Finally, we arrange the elements refering to the monitoring.
		monitoring_sizer = wx.StaticBoxSizer(monitoring_static_box, wx.VERTICAL)
		monitoring_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		monitoring_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		monitoring_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		monitoring_sizer_1.Add(wx.StaticText(self, -1, "Ellipsometer type:"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		monitoring_sizer_1.Add(self.monitoring_RAE_button,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		monitoring_sizer_1.Add(self.monitoring_RPE_button,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		monitoring_sizer_1.Add(self.monitoring_RCE_button,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		monitoring_sizer_2.Add(wx.StaticText(self, -1, "Delta min:"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		monitoring_sizer_2.Add(self.monitoring_Delta_min_box,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		monitoring_sizer_2.Add(wx.StaticText(self, -1, "degrees"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		monitoring_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		monitoring_sizer_3.Add(wx.StaticText(self, -1, "Sublayer thickness:"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		monitoring_sizer_3.Add(self.monitoring_sublayer_thickness_box,
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		monitoring_sizer_3.Add(wx.StaticText(self, -1, "nm"),
		                       0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		monitoring_sizer.Add(self.consider_backside_on_monitoring_box,
		                     0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		monitoring_sizer.Add(monitoring_sizer_1,
		                     0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		monitoring_sizer.Add(monitoring_sizer_2,
		                     0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		monitoring_sizer.Add(monitoring_sizer_3,
		                     0, wx.ALIGN_LEFT|wx.ALL, 5)
		
		main_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		main_sizer_1.Add(analysis_sizer, 1, wx.EXPAND)
		main_sizer_1.Add(monitoring_sizer, 1, wx.EXPAND|wx.LEFT, 10)
		
		self.main_sizer.Add(substrate_and_medium_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(wavelengths_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(graded_index_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(color_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(main_sizer_1, 0, wx.EXPAND|wx.ALL, 10)
	
	
	######################################################################
	#                                                                    #
	# on_enter                                                           #
	#                                                                    #
	######################################################################
	def on_enter(self, event):
		"""Close the dialog if the enter button is pressed (after
		validation)
		
		This method takes a single argument:
		  event              the event."""
		
		if self.Validate():
			self.EndModal(wx.ID_OK)
	
	
	######################################################################
	#                                                                    #
	# on_step_spacing_box                                                #
	#                                                                    #
	######################################################################
	def on_step_spacing_box(self, event):
		"""Automatically select the other step spacing radio button when
		text is entered in the other step spacing box.
		
		This method takes a single argument:
		  event              the event."""
		
		# When a value is entered in the other step spacing box,
		# automatically select the other step spacing button.
		if self.step_spacing_box.GetValue() != "":
			self.step_spacing_other_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# on_dont_consider_substrate                                         #
	#                                                                    #
	######################################################################
	def on_dont_consider_substrate(self, event):
		"""Adjust the dialog when the don't consider backside box is
		checked
		
		This method takes a single argument:
		  event              the event."""
		
		# If the substrate and mediums are not considered, it is impossible
		# to considerer the backside.
		if self.dont_consider_substrate_box.GetValue():
			self.consider_backside_box.SetValue(False)
			self.consider_backside_box.Disable()
			self.consider_backside_on_monitoring_box.SetValue(False)
			self.consider_backside_on_monitoring_box.Disable()
		else:
			self.consider_backside_box.Enable()
			self.consider_backside_on_monitoring_box.Enable()
	
	
	######################################################################
	#                                                                    #
	# set_values                                                         #
	#                                                                    #
	######################################################################
	def set_values(self):
		"""Set the values in the dialog according to the filter"""
		
		# Get the values.
		substrate = self.filter.get_substrate()
		substrate_thickness = self.filter.get_substrate_thickness()
		front_medium, back_medium = self.filter.get_medium()
		dont_consider_substrate = self.filter.get_dont_consider_substrate()
		center_wavelength = self.filter.get_center_wavelength()
		from_wavelength, to_wavelength, by_wavelength = self.filter.get_wavelengths_by_range()
		step_spacing = self.filter.get_step_spacing()
		minimum_thickness = self.filter.get_minimum_thickness()
		illuminant = self.filter.get_illuminant()
		observer = self.filter.get_observer()
		consider_backside = self.filter.get_consider_backside()
		ellipsometer_type = self.filter.get_ellipsometer_type()
		Delta_min = self.filter.get_Delta_min()
		consider_backside_on_monitoring = self.filter.get_consider_backside_on_monitoring()
		monitoring_ellipsometer_type = self.filter.get_monitoring_ellipsometer_type()
		monitoring_Delta_min = self.filter.get_monitoring_Delta_min()
		monitoring_sublayer_thickness = self.filter.get_monitoring_sublayer_thickness()
		
		# Set the values.
		self.substrate_box.SetValue("%s" % substrate)
		self.substrate_thickness_box.SetValue("%s" % (substrate_thickness/1000000.0))
		self.front_medium_box.SetValue("%s" % front_medium)
		self.back_medium_box.SetValue("%s" % back_medium)
		if dont_consider_substrate:
			self.dont_consider_substrate_box.SetValue(True)
			self.consider_backside_box.Disable()
			self.consider_backside_on_monitoring_box.Disable()
		else:
			self.dont_consider_substrate_box.SetValue(False)
		self.center_wavelength_box.SetValue("%s" % center_wavelength)
		if from_wavelength is not None:
			self.from_wavelength_box.SetValue("%s" % from_wavelength)
		if to_wavelength is not None:
			self.to_wavelength_box.SetValue("%s" % to_wavelength)
		if by_wavelength is not None:
			self.by_wavelength_box.SetValue("%s" % by_wavelength)
		if step_spacing == DEPOSITION_STEP_SPACING:
			# Set a default value to the step_spacing_box to avoid validation
			# problems.
			self.step_spacing_box.SetValue("%s" % 0.0025)
			self.step_spacing_deposition_button.SetValue(True)
		else:
			self.step_spacing_box.SetValue("%s" % step_spacing)
			self.step_spacing_other_button.SetValue(True)
		self.minimum_thickness_box.SetValue("%s" % minimum_thickness)
		self.illuminant_choice.SetSelection(self.illuminant_choice.FindString(illuminant))
		self.observer_choice.SetSelection(self.observer_choice.FindString(observer))
		if consider_backside:
			self.consider_backside_box.SetValue(True)
		else:
			self.consider_backside_box.SetValue(False)
		if ellipsometer_type == RAE:
			self.RAE_button.SetValue(True)
		elif ellipsometer_type == RPE:
			self.RPE_button.SetValue(True)
		elif ellipsometer_type == RCE:
			self.RCE_button.SetValue(True)
		self.Delta_min_box.SetValue("%s" % Delta_min)
		if consider_backside_on_monitoring:
			self.consider_backside_on_monitoring_box.SetValue(True)
		else:
			self.consider_backside_on_monitoring_box.SetValue(False)
		if monitoring_ellipsometer_type == RAE:
			self.monitoring_RAE_button.SetValue(True)
		elif monitoring_ellipsometer_type == RPE:
			self.monitoring_RPE_button.SetValue(True)
		elif monitoring_ellipsometer_type == RCE:
			self.monitoring_RCE_button.SetValue(True)
		self.monitoring_Delta_min_box.SetValue("%s" % monitoring_Delta_min)
		self.monitoring_sublayer_thickness_box.SetValue("%s" % monitoring_sublayer_thickness)
	
	
	######################################################################
	#                                                                    #
	# apply_to_filter                                                    #
	#                                                                    #
	######################################################################
	def apply_to_filter(self):
		"""Apply the values set in the dialog to the filter"""
		
		substrate = self.substrate_box.GetValue()
		substrate_thickness = float(self.substrate_thickness_box.GetValue())*1000000.0
		front_medium = self.front_medium_box.GetValue()
		back_medium = self.back_medium_box.GetValue()
		dont_consider_substrate = self.dont_consider_substrate_box.GetValue()
		center_wavelength = float(self.center_wavelength_box.GetValue())
		from_wavelength = float(self.from_wavelength_box.GetValue())
		to_wavelength = float(self.to_wavelength_box.GetValue())
		by_wavelength = float(self.by_wavelength_box.GetValue())
		if self.step_spacing_deposition_button.GetValue():
			step_spacing = DEPOSITION_STEP_SPACING
		else:
			step_spacing = float(self.step_spacing_box.GetValue())
		minimum_thickness = float(self.minimum_thickness_box.GetValue())
		illuminant = self.illuminant_choice.GetStringSelection()
		observer = self.observer_choice.GetStringSelection()
		consider_backside = self.consider_backside_box.GetValue()
		if self.RAE_button.GetValue():
			ellipsometer_type = RAE
		elif self.RPE_button.GetValue():
			ellipsometer_type = RPE
		elif self.RCE_button.GetValue():
			ellipsometer_type = RCE
		Delta_min = float(self.Delta_min_box.GetValue())
		consider_backside_on_monitoring = self.consider_backside_on_monitoring_box.GetValue()
		if self.monitoring_RAE_button.GetValue():
			monitoring_ellipsometer_type = RAE
		elif self.monitoring_RPE_button.GetValue():
			monitoring_ellipsometer_type = RPE
		elif self.monitoring_RCE_button.GetValue():
			monitoring_ellipsometer_type = RCE
		monitoring_Delta_min = float(self.monitoring_Delta_min_box.GetValue())
		monitoring_sublayer_thickness = float(self.monitoring_sublayer_thickness_box.GetValue())
		
		# Change the properties of the filters and keep track if a change
		# was made that requires an update of the interface.
		modified = False
		
		if substrate != self.filter.get_substrate():
			self.filter.set_substrate(substrate)
			modified = True
		
		if substrate_thickness != self.filter.get_substrate_thickness():
			self.filter.set_substrate_thickness(substrate_thickness)
			modified = True
		
		if front_medium != self.filter.get_medium(FRONT):
			self.filter.set_medium(front_medium, FRONT)
			modified = True
		
		if back_medium != self.filter.get_medium(BACK):
			self.filter.set_medium(back_medium, BACK)
			modified = True
		
		if dont_consider_substrate != self.filter.get_dont_consider_substrate():
			self.filter.set_dont_consider_substrate(dont_consider_substrate)
			modified = True
		
		if center_wavelength != self.filter.get_center_wavelength():
			try:
				self.filter.set_center_wavelength(center_wavelength)
				modified = True
			except (graded.grading_error, materials.material_error) as error:
				wx.MessageBox("Could not change the reference wavelength.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		if (from_wavelength, to_wavelength, by_wavelength) != self.filter.get_wavelengths_by_range():
			self.filter.set_wavelengths_by_range(from_wavelength, to_wavelength, by_wavelength)
			modified = True
		
		if step_spacing != self.filter.get_step_spacing():
			try:
				self.filter.set_step_spacing(step_spacing)
				modified = True
			except graded.grading_error, error:
				wx.MessageBox("Could not change the step spacing.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		if minimum_thickness != self.filter.get_minimum_thickness():
			try:
				self.filter.set_minimum_thickness(minimum_thickness)
				modified = True
			except graded.grading_error, error:
				wx.MessageBox("Could not change the sublayer minimum thickness.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		if illuminant != self.filter.get_illuminant():
			self.filter.set_illuminant(illuminant)
			modified = True
		
		if observer != self.filter.get_observer():
			self.filter.set_observer(observer)
			modified = True
		
		if consider_backside != self.filter.get_consider_backside():
			self.filter.set_consider_backside(consider_backside)
			modified = True
		
		if ellipsometer_type != self.filter.get_ellipsometer_type():
			self.filter.set_ellipsometer_type(ellipsometer_type)
			modified = True
		
		if Delta_min != self.filter.get_Delta_min():
			self.filter.set_Delta_min(Delta_min)
			modified = True
		
		if  consider_backside_on_monitoring!= self.filter.get_consider_backside_on_monitoring():
			self.filter.set_consider_backside_on_monitoring(consider_backside_on_monitoring)
			modified = True
		
		if monitoring_ellipsometer_type != self.filter.get_monitoring_ellipsometer_type():
			self.filter.set_monitoring_ellipsometer_type(monitoring_ellipsometer_type)
			modified = True
		
		if monitoring_Delta_min != self.filter.get_monitoring_Delta_min():
			self.filter.set_monitoring_Delta_min(monitoring_Delta_min)
			modified = True
		
		if monitoring_sublayer_thickness != self.filter.get_monitoring_sublayer_thickness():
			self.filter.set_monitoring_sublayer_thickness(monitoring_sublayer_thickness)
			modified = True
		
		return modified
