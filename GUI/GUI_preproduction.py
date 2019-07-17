# GUI_preproduction.py
# 
# Dialogs to do preproduction analysis.
# 
# Copyright (c) 2007-2011,2013-2015 Stephane Larouche.
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



import os
try:
	import threading
except ImportError:
	pass
import time

import wx

from definitions import *
import config
import preproduction
import data_holder
import targets
import color

import GUI_plot
import GUI_color
from GUI_validators import int_validator, float_validator,\
                           illuminant_validator, observer_validator



S_or_P = [S, P]



########################################################################
#                                                                      #
# progress_event                                                       #
#                                                                      #
########################################################################

progress_event_type = wx.NewEventType()

EVT_progress = wx.PyEventBinder(progress_event_type, 1)

class progress_event(wx.PyCommandEvent):
	
	eventType = progress_event_type
	
	def __init__(self, windowID, progress = None):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.progress = progress
	
	def Clone(self):
		self.__class__(self.GetId())
	
	def get_progress(self):
		return self.progress



########################################################################
#                                                                      #
# finished_event                                                       #
#                                                                      #
########################################################################

finished_event_type = wx.NewEventType()

EVT_finished = wx.PyEventBinder(finished_event_type, 1)

class finished_event(wx.PyCommandEvent):
	
	eventType = finished_event_type
	
	def __init__(self, windowID):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)



########################################################################
#                                                                      #
# random_errors_dialog                                                 #
#                                                                      #
########################################################################
class random_errors_dialog(wx.Dialog):
	"""A dialog to simulate random deposition errors."""
	
	title = "Random error analysis"
	
	multiplication_factors = {data_holder.REFLECTION: 1.0,
	                          data_holder.TRANSMISSION: 1.0,
	                          data_holder.ABSORPTION: 1.0,
	                          data_holder.REFLECTION_PHASE: 1.0,
	                          data_holder.TRANSMISSION_PHASE: 1.0,
	                          data_holder.REFLECTION_GD: 1.0e15,
	                          data_holder.TRANSMISSION_GD: 1.0e15,
	                          data_holder.REFLECTION_GDD: 1.0e30,
	                          data_holder.TRANSMISSION_GDD: 1.0e30,
	                          data_holder.COLOR: 1.0}
	
	data_type_targets = {data_holder.REFLECTION: [targets.R_TARGET, targets.R_SPECTRUM_TARGET],
	                     data_holder.TRANSMISSION: [targets.T_TARGET, targets.T_SPECTRUM_TARGET],
	                     data_holder.ABSORPTION: [targets.A_TARGET, targets.A_SPECTRUM_TARGET],
	                     data_holder.REFLECTION_PHASE: [targets.R_PHASE_TARGET, targets.R_PHASE_SPECTRUM_TARGET],
	                     data_holder.TRANSMISSION_PHASE: [targets.T_PHASE_TARGET, targets.T_PHASE_SPECTRUM_TARGET],
	                     data_holder.REFLECTION_GD: [targets.R_GD_TARGET, targets.R_GD_SPECTRUM_TARGET],
	                     data_holder.TRANSMISSION_GD: [targets.T_GD_TARGET, targets.T_GD_SPECTRUM_TARGET],
	                     data_holder.REFLECTION_GDD: [targets.R_GDD_TARGET, targets.R_GDD_SPECTRUM_TARGET],
	                     data_holder.TRANSMISSION_GDD: [targets.T_GDD_TARGET, targets.T_GDD_SPECTRUM_TARGET],
	                     data_holder.COLOR: [targets.R_COLOR_TARGET, targets.T_COLOR_TARGET]}
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent                 the parent window;
		  filter                 the filter on which to simulate deposition
		                         errors; and
		  targets                a list of targets."""
		
		self.parent = parent
		self.filter = filter
		self.targets = targets
		
		self.analyser = preproduction.random_errors(self.filter)
		
		self.nb_std_devs = 3.0
		
		self.simulating = False
		
		self.wavelengths = self.analyser.get_wavelengths()
		self.nb_wavelengths = len(self.wavelengths)
		
		wx.Dialog.__init__(self, self.parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.add_content()
		self.add_buttons()
		
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.Bind(wx.EVT_CHAR_HOOK, self.on_char)
		self.Bind(EVT_progress, self.on_progress)
		self.Bind(EVT_finished, self.on_finished)
		
		self.result_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_page_changed)
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		self.update_data_types()
		self.enable_controls()
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		# A static box for the kind of data and the conditions of the
		# simulation.
		data_static_box = wx.StaticBox(self, -1, "Data type")
		
		self.reflection_box = wx.CheckBox(self, -1, "reflection")
		self.transmission_box = wx.CheckBox(self, -1, "transmission")
		self.absorption_box = wx.CheckBox(self, -1, "absorption")
		self.reflection_phase_box = wx.CheckBox(self, -1, "reflection phase")
		self.transmission_phase_box = wx.CheckBox(self, -1, "transmission phase")
		self.reflection_GD_box = wx.CheckBox(self, -1, "reflection GD")
		self.transmission_GD_box = wx.CheckBox(self, -1, "transmission GD")
		self.reflection_GDD_box = wx.CheckBox(self, -1, "reflection GDD")
		self.transmission_GDD_box = wx.CheckBox(self, -1, "transmission GDD")
		self.color_box = wx.CheckBox(self, -1, "color")
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.reflection_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.transmission_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.absorption_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.reflection_phase_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.transmission_phase_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.reflection_GD_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.transmission_GD_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.reflection_GDD_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.transmission_GDD_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_data_type, self.color_box)
		
		self.data_type_boxes = {data_holder.REFLECTION: self.reflection_box,
		                        data_holder.TRANSMISSION: self.transmission_box,
		                        data_holder.ABSORPTION: self.absorption_box,
		                        data_holder.REFLECTION_PHASE: self.reflection_phase_box,
		                        data_holder.TRANSMISSION_PHASE: self.transmission_phase_box,
		                        data_holder.REFLECTION_GD: self.reflection_GD_box,
		                        data_holder.TRANSMISSION_GD: self.transmission_GD_box,
		                        data_holder.REFLECTION_GDD: self.reflection_GDD_box,
		                        data_holder.TRANSMISSION_GDD: self.transmission_GDD_box,
		                        data_holder.COLOR: self.color_box}
		
		self.angle_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, include_maximum = False))
		self.angle_box.Bind(wx.EVT_KILL_FOCUS, self.on_angle)
		
		self.s_polarized_button = wx.RadioButton(self, -1, "s", style = wx.RB_GROUP)
		self.p_polarized_button = wx.RadioButton(self, -1, "p")
		self.unpolarized_button = wx.RadioButton(self, -1, "unpolarized")
		self.other_polarizations_button = wx.RadioButton(self, -1, "")
		self.other_polarizations_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, 90.0, ))
		self.other_polarizations_box.SetValidator(float_validator(0.0, 90.0, lambda: self.other_polarizations_button.GetValue() or self.other_polarizations_box.GetValue()))
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.s_polarized_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.p_polarized_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.unpolarized_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_polarization_radio_button, self.other_polarizations_button)
		self.other_polarizations_box.Bind(wx.EVT_KILL_FOCUS, self.on_other_polarizations_box)
		
		self.illuminant_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_illuminant_names())
		self.observer_choice = wx.Choice(self, -1, (-1, -1), choices = color.get_observer_names())
		self.illuminant_choice.SetValidator(illuminant_validator(condition = self.illuminant_choice.IsEnabled))
		self.observer_choice.SetValidator(observer_validator(condition = self.observer_choice.IsEnabled))
		self.Bind(wx.EVT_CHOICE, self.on_illuminant_choice, self.illuminant_choice)
		self.Bind(wx.EVT_CHOICE, self.on_observer_choice, self.observer_choice)
		
		# A static box for the errors being simulated.
		error_static_box = wx.StaticBox(self, -1, "Errors")
		
		self.percentage_thickness_button = wx.RadioButton(self, -1, "", style = wx.RB_GROUP)
		self.percentage_thickness_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, 100.0))
		self.physical_thickness_button = wx.RadioButton(self, -1, "")
		self.physical_thickness_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None))
		self.Bind(wx.EVT_RADIOBUTTON, self.on_thickness_error_type, self.percentage_thickness_button)
		self.percentage_thickness_box.Bind(wx.EVT_KILL_FOCUS, self.on_percentage_thickness)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_thickness_error_type, self.physical_thickness_button)
		self.physical_thickness_box.Bind(wx.EVT_KILL_FOCUS, self.on_physical_thickness)
		
		self.uniform_button = wx.RadioButton(self, -1, "uniform", style = wx.RB_GROUP)
		self.normal_button = wx.RadioButton(self, -1, "normal")
		self.Bind(wx.EVT_RADIOBUTTON, self.on_distribution, self.uniform_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_distribution, self.normal_button)
		
		self.nb_tests_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_tests_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_tests)
		
		self.all_results_box = wx.CheckBox(self, -1, "all results")
		self.mean_box = wx.CheckBox(self, -1, "mean")
		self.plus_minus_n_std_devs_box = wx.CheckBox(self, -1, "+/-")
		self.nb_std_devs_box = wx.TextCtrl(self, -1, "", validator = float_validator(0.0, None))
		self.min_max_box = wx.CheckBox(self, -1, "worst case")
		self.expected_result_box = wx.CheckBox(self, -1, "design")
		self.targets_box = wx.CheckBox(self, -1, "targets")
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.all_results_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.mean_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.plus_minus_n_std_devs_box)
		self.nb_std_devs_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_std_devs)
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.min_max_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.expected_result_box)
		self.Bind(wx.EVT_CHECKBOX, self.on_show, self.targets_box)
		
		self.result_notebook =  wx.Notebook(self, size = (700, 350))
		
		self.reflection_plot = GUI_plot.plot(self.result_notebook)
		self.reflection_plot.set_clickable()
		self.reflection_plot.set_allow_remove_curve(False)
		self.reflection_plot.set_xlabel("Wavelength (nm)")
		self.reflection_plot.set_ylabel("R")
		self.reflection_plot.set_legend_position(GUI_plot.TOP)
		
		self.transmission_plot = GUI_plot.plot(self.result_notebook)
		self.transmission_plot.set_clickable()
		self.transmission_plot.set_allow_remove_curve(False)
		self.transmission_plot.set_xlabel("Wavelength (nm)")
		self.transmission_plot.set_ylabel("T")
		self.transmission_plot.set_legend_position(GUI_plot.TOP)
		
		self.absorption_plot = GUI_plot.plot(self.result_notebook)
		self.absorption_plot.set_clickable()
		self.absorption_plot.set_allow_remove_curve(False)
		self.absorption_plot.set_xlabel("Wavelength (nm)")
		self.absorption_plot.set_ylabel("A")
		self.absorption_plot.set_legend_position(GUI_plot.TOP)
		
		self.reflection_phase_plot = GUI_plot.plot(self.result_notebook)
		self.reflection_phase_plot.set_clickable()
		self.reflection_phase_plot.set_allow_remove_curve(False)
		self.reflection_phase_plot.set_xlabel("Wavelength (nm)")
		self.reflection_phase_plot.set_ylabel("Phase (deg.)")
		self.reflection_phase_plot.set_legend_position(GUI_plot.TOP)
		
		self.transmission_phase_plot = GUI_plot.plot(self.result_notebook)
		self.transmission_phase_plot.set_clickable()
		self.transmission_phase_plot.set_allow_remove_curve(False)
		self.transmission_phase_plot.set_xlabel("Wavelength (nm)")
		self.transmission_phase_plot.set_ylabel("Phase (deg.)")
		self.transmission_phase_plot.set_legend_position(GUI_plot.TOP)
		
		self.reflection_GD_plot = GUI_plot.plot(self.result_notebook)
		self.reflection_GD_plot.set_clickable()
		self.reflection_GD_plot.set_allow_remove_curve(False)
		self.reflection_GD_plot.set_xlabel("Wavelength (nm)")
		self.reflection_GD_plot.set_ylabel("GD (fs)")
		self.reflection_GD_plot.set_legend_position(GUI_plot.TOP)
		
		self.transmission_GD_plot = GUI_plot.plot(self.result_notebook)
		self.transmission_GD_plot.set_clickable()
		self.transmission_GD_plot.set_allow_remove_curve(False)
		self.transmission_GD_plot.set_xlabel("Wavelength (nm)")
		self.transmission_GD_plot.set_ylabel("GD (fs)")
		self.transmission_GD_plot.set_legend_position(GUI_plot.TOP)
		
		self.reflection_GDD_plot = GUI_plot.plot(self.result_notebook)
		self.reflection_GDD_plot.set_clickable()
		self.reflection_GDD_plot.set_allow_remove_curve(False)
		self.reflection_GDD_plot.set_xlabel("Wavelength (nm)")
		self.reflection_GDD_plot.set_ylabel("GDD (fs^2)")
		self.reflection_GDD_plot.set_legend_position(GUI_plot.TOP)
		
		self.transmission_GDD_plot = GUI_plot.plot(self.result_notebook)
		self.transmission_GDD_plot.set_clickable()
		self.transmission_GDD_plot.set_allow_remove_curve(False)
		self.transmission_GDD_plot.set_xlabel("Wavelength (nm)")
		self.transmission_GDD_plot.set_ylabel("GDD (fs^2)")
		self.transmission_GDD_plot.set_legend_position(GUI_plot.TOP)
		
		self.color_panel = color_error_panel(self.result_notebook)
		
		self.plots = {data_holder.REFLECTION: self.reflection_plot,
		              data_holder.TRANSMISSION: self.transmission_plot,
		              data_holder.ABSORPTION: self.absorption_plot,
		              data_holder.REFLECTION_PHASE: self.reflection_phase_plot,
		              data_holder.TRANSMISSION_PHASE: self.transmission_phase_plot,
		              data_holder.REFLECTION_GD: self.reflection_GD_plot,
		              data_holder.TRANSMISSION_GD: self.transmission_GD_plot,
		              data_holder.REFLECTION_GDD: self.reflection_GDD_plot,
		              data_holder.TRANSMISSION_GDD: self.transmission_GDD_plot,
		              data_holder.COLOR: self.color_panel}
		
		# Add all plots to the notebook so we don't have to hide them.
		# Hiding them and then showing them could create issues on some
		# operating systems.
		for data_type, plot in self.plots.items():
			self.result_notebook.AddPage(plot, data_holder.DATA_TYPE_NAMES[data_type])
		self.shown_plots = self.plots.values()
		
		data_box_sizer = wx.StaticBoxSizer(data_static_box, wx.VERTICAL)
		
		data_type_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		data_type_sizer_1.Add(self.reflection_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer_1.Add(self.transmission_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_type_sizer_1.Add(self.absorption_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		data_type_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		data_type_sizer_2.Add(self.reflection_phase_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer_2.Add(self.transmission_phase_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_type_sizer_2.Add(self.reflection_GD_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer_2.Add(self.transmission_GD_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_type_sizer_2.Add(self.reflection_GDD_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_type_sizer_2.Add(self.transmission_GDD_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		data_type_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		data_type_sizer_3.Add(self.color_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		data_type_sizer = wx.FlexGridSizer(3, 2, 8, 10)
		data_type_sizer.Add(wx.StaticText(self, -1, "Data types:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer.Add(data_type_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer.Add((0, 0))
		data_type_sizer.Add(data_type_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_type_sizer.Add((0, 0))
		data_type_sizer.Add(data_type_sizer_3, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		data_properties_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		data_properties_sizer_1.Add(wx.StaticText(self, -1, "Angle:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_properties_sizer_1.Add(self.angle_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_1.Add(wx.StaticText(self, -1, "degres"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		data_properties_sizer_1.Add(wx.StaticText(self, -1, "Polarization:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 25)
		data_properties_sizer_1.Add(self.s_polarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_1.Add(self.p_polarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_1.Add(self.unpolarized_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_1.Add(self.other_polarizations_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_1.Add(self.other_polarizations_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		data_properties_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		data_properties_sizer_2.Add(wx.StaticText(self, -1, "Illuminant:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		data_properties_sizer_2.Add(self.illuminant_choice, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		data_properties_sizer_2.Add(wx.StaticText(self, -1, "Observer:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 25)
		data_properties_sizer_2.Add(self.observer_choice, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		data_box_sizer.Add(data_type_sizer, 0,  wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		data_box_sizer.Add(data_properties_sizer_1, 0,  wx.ALIGN_LEFT|wx.ALL, 5)
		data_box_sizer.Add(data_properties_sizer_2, 0,  wx.ALIGN_LEFT|wx.ALL, 5)
		
		error_box_sizer = wx.StaticBoxSizer(error_static_box, wx.VERTICAL)
		
		variation_sizer = wx.BoxSizer(wx.HORIZONTAL)
		variation_sizer.Add(wx.StaticText(self, -1, "Vary thickness by:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		variation_sizer.Add(self.percentage_thickness_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		variation_sizer.Add(self.percentage_thickness_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		variation_sizer.Add(wx.StaticText(self, -1, "%"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		variation_sizer.Add(self.physical_thickness_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		variation_sizer.Add(self.physical_thickness_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		variation_sizer.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		distribution_sizer = wx.BoxSizer(wx.HORIZONTAL)
		distribution_sizer.Add(wx.StaticText(self, -1, "Distribution:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		distribution_sizer.Add(self.uniform_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		distribution_sizer.Add(self.normal_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		distribution_sizer.Add(wx.StaticText(self, -1, "Nb. tests:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 25)
		distribution_sizer.Add(self.nb_tests_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		error_box_sizer.Add(variation_sizer, 0,  wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		error_box_sizer.Add(distribution_sizer, 0,  wx.ALIGN_LEFT|wx.ALL, 5)
		
		show_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		show_sizer_1.Add(self.all_results_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		show_sizer_1.Add(self.mean_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		show_sizer_1.Add(self.plus_minus_n_std_devs_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		show_sizer_1.Add(self.nb_std_devs_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		show_sizer_1.Add(wx.StaticText(self, -1, "standard deviations"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		show_sizer_1.Add(self.min_max_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		show_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		show_sizer_2.Add(self.expected_result_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		show_sizer_2.Add(self.targets_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
		
		show_sizer = wx.FlexGridSizer(2, 2, 5, 10)
		show_sizer.Add(wx.StaticText(self, -1, "Show:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		show_sizer.Add(show_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		show_sizer.Add((0, 0))
		show_sizer.Add(show_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		self.main_sizer.Add(data_box_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(error_box_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(show_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(self.result_notebook, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# Set default values.
		data_types = self.analyser.get_data_types()
		angle = self.analyser.get_angle()
		polarization = self.analyser.get_polarization()
		illuminant_name = self.analyser.get_illuminant()
		observer_name = self.analyser.get_observer()
		thickness_error_type = self.analyser.get_thickness_error_type()
		relative_thickness_error = self.analyser.get_relative_thickness_error()
		physical_thickness_error = self.analyser.get_physical_thickness_error()
		distribution = self.analyser.get_distribution()
		nb_tests = self.analyser.get_nb_tests()
		for data_type in data_types:
			self.data_type_boxes[data_type].SetValue(True)
		self.angle_box.SetValue("%.2f" % angle)
		if polarization == S:
			self.s_polarized_button.SetValue(True)
		elif polarization == P:
			self.p_polarized_button.SetValue(True)
		elif polarization == UNPOLARIZED:
			self.unpolarized_button.SetValue(True)
		else:
			self.other_polarizations_button.SetValue(True)
			self.other_polarizations_box.SetValue("%.2f" % polarization)
		self.illuminant_choice.SetSelection(self.illuminant_choice.FindString(illuminant_name))
		self.observer_choice.SetSelection(self.observer_choice.FindString(observer_name))
		self.percentage_thickness_box.SetValue("%.2f" % (100.0 * relative_thickness_error))
		self.physical_thickness_box.SetValue("%.2f" % physical_thickness_error)
		if thickness_error_type == preproduction.RELATIVE_THICKNESS:
			self.percentage_thickness_button.SetValue(True)
		elif thickness_error_type == preproduction.PHYSICAL_THICKNESS:
			self.physical_thickness_button.SetValue(True)
		if distribution == preproduction.UNIFORM:
			self.uniform_button.SetValue(True)
		elif distribution == preproduction.NORMAL:
			self.normal_button.SetValue(True)
		self.nb_tests_box.SetValue("%i" % nb_tests)
		self.min_max_box.SetValue(True)
		self.expected_result_box.SetValue(True)
		self.nb_std_devs_box.SetValue("%.2f" % self.nb_std_devs)
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add buttons to the dialog"""
		
		# Create buttons.
		self.simulate_button = wx.Button(self, -1, "S&imulate")
		self.stop_button = wx.Button(self, wx.ID_STOP)
		self.save_button = wx.Button(self, -1, "&Save statistics")
		self.save_all_button = wx.Button(self, -1, "Save &all results")
		self.save_figure_button = wx.Button(self, -1, "Save &figure")
		self.close_button = wx.Button(self, wx.ID_CLOSE)
		self.Bind(wx.EVT_BUTTON, self.on_simulate, self.simulate_button)
		self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
		self.Bind(wx.EVT_BUTTON, self.on_save, self.save_button)
		self.Bind(wx.EVT_BUTTON, self.on_save_all, self.save_all_button)
		self.Bind(wx.EVT_BUTTON, self.on_save_figure, self.save_figure_button)
		self.Bind(wx.EVT_BUTTON, self.on_close, self.close_button)
		
		# Arrange them.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.simulate_button, 0)
		buttons.Add(self.stop_button, 0, wx.LEFT, 20)
		buttons.Add(self.save_button, 0, wx.LEFT, 20)
		buttons.Add(self.save_all_button, 0, wx.LEFT, 20)
		buttons.Add(self.save_figure_button, 0, wx.LEFT, 20)
		buttons.Add(self.close_button, 0, wx.LEFT, 20)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 10)
	
	
	######################################################################
	#                                                                    #
	# on_data_type                                                       #
	#                                                                    #
	######################################################################
	def on_data_type(self, event):
		"""Handle the event when a data type is selected
		
		This method takes a single argument:
		  event              the event.
		
		This method tells the preproduction class instance the data types
		that are selected and reset the plots."""
		
		self.update_data_types()
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_angle                                                           #
	#                                                                    #
	######################################################################
	def on_angle(self, event):
		"""Handle the event when an indicence angle is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the angle, tells the preproduction class
		instance the angle that was entered, and reset the plot (if the
		angle was changed)."""
		
		if not self.angle_box.GetValidator().Validate(self):
			return
		
		angle = float(self.angle_box.GetValue())
		if angle != self.analyser.get_angle():
			self.analyser.set_angle(angle)
			self.reset()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_polarization_radio_button                                       #
	#                                                                    #
	######################################################################
	def on_polarization_radio_button(self, event):
		"""Handle the event when a polarization button is selected
		
		This method takes a single argument:
		  event              the event.
		
		This method tells the preproduction class instance the polarization
		that was selected and resets the plot (if the polarization was
		changed)."""
		
		if self.other_polarizations_button.GetValue():
			if self.other_polarizations_box.GetValue():
				polarization = float(self.other_polarizations_box.GetValue())
			else:
				self.other_polarizations_box.SetFocus()
				return
		
		else:
			self.other_polarizations_box.SetValue("")
			if self.s_polarized_button.GetValue():
				polarization = S
			elif self.p_polarized_button.GetValue():
				polarization = P
			elif self.unpolarized_button.GetValue():
				polarization = UNPOLARIZED
		
		if polarization != self.analyser.get_polarization():
			self.analyser.set_polarization(polarization)
			self.adjust_available_data_types()
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_other_polarizations_box                                         #
	#                                                                    #
	######################################################################
	def on_other_polarizations_box(self, event):
		"""Handle the event when a polarization is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the polarization, tells the preproduction
		class instance the polarization that was entered, and resets the
		plot (if the polarization was changed)."""
		
		# If focus is lost in favor of another application, the close
		# button, or any of the polarization buttons, skip the event and
		# return immediatly. 
		if event.GetWindow() in [None, self.close_button, self.s_polarized_button, self.p_polarized_button, self.unpolarized_button]:
			event.Skip()
			return
		
		if not self.other_polarizations_box.GetValidator().Validate(self):
			return
		
		value = self.other_polarizations_box.GetValue()
		
		if value:
			polarization = float(value)
			
			self.other_polarizations_button.SetValue(True)
			
			if polarization != self.analyser.get_polarization():
				self.analyser.set_polarization(polarization)
				self.adjust_available_data_types()
				self.reset()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_illuminant_choice                                               #
	#                                                                    #
	######################################################################
	def on_illuminant_choice(self, event):
		"""Handle the event when an illuminant is chosen
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the illuminant, tells the preproduction class
		instance the illuminant that was chosen, and resets the plot (if
		the illuminant was changed)."""
		
		if not self.illuminant_choice.GetValidator().Validate(self):
			return
		
		illuminant_name = self.illuminant_choice.GetStringSelection()
		
		if illuminant_name != self.analyser.get_illuminant():
			self.analyser.set_illuminant(illuminant_name)
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_observer_choice                                                 #
	#                                                                    #
	######################################################################
	def on_observer_choice(self, event):
		"""Handle the event when an observer is chosen
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the observer, tells the preproduction class
		instance the observer that was chosen, and resets the plot (if the
		observer was changed)."""
		
		if not self.observer_choice.GetValidator().Validate(self):
			return
		
		observer_name = self.observer_choice.GetStringSelection()
		
		if observer_name != self.analyser.get_observer():
			self.analyser.set_observer(observer_name)
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_thickness_error_type                                            #
	#                                                                    #
	######################################################################
	def on_thickness_error_type(self, event):
		"""Handle the event when a thickness error type is selected
		
		This method takes a single argument:
		  event              the event.
		
		This method tells the preproduction class instance the thickness
		error type that was selected and resets the plot."""
		
		if self.percentage_thickness_button.GetValue():
			self.analyser.set_thickness_error_type(preproduction.RELATIVE_THICKNESS)
		elif self.physical_thickness_button.GetValue():
			self.analyser.set_thickness_error_type(preproduction.PHYSICAL_THICKNESS)
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_percentage_thickness                                            #
	#                                                                    #
	######################################################################
	def on_percentage_thickness(self, event):
		"""Handle the event when a percentage of thickness error is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the percentage, tells the preproduction class
		instance the value that was entered, and resets the plot (if the
		percentage was changed)."""
		
		# If focus is lost in favor of another application or the close
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.close_button]:
			event.Skip()
			return
		
		if not self.percentage_thickness_box.GetValidator().Validate(self):
			return
		
		relative_thickness_error = 0.01*float(self.percentage_thickness_box.GetValue())
		if relative_thickness_error != self.analyser.get_relative_thickness_error():
			self.analyser.set_relative_thickness_error(relative_thickness_error)
			self.percentage_thickness_button.SetValue(True)
			self.analyser.set_thickness_error_type(preproduction.RELATIVE_THICKNESS)
			self.reset()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_physical_thickness                                              #
	#                                                                    #
	######################################################################
	def on_physical_thickness(self, event):
		"""Handle the event when a physical thickness error value is
		entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the value of the physical thickness error,
		tells the preproduction class instance the value that was entered,
		and resets the plot (if the error value was changed)."""
		
		# If focus is lost in favor of another application or the close
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.close_button]:
			event.Skip()
			return
		
		if not self.physical_thickness_box.GetValidator().Validate(self):
			return
		
		physical_thickness_error = float(self.physical_thickness_box.GetValue())
		if physical_thickness_error != self.analyser.get_physical_thickness_error():
			self.analyser.set_physical_thickness_error(physical_thickness_error)
			self.physical_thickness_button.SetValue(True)
			self.analyser.set_thickness_error_type(preproduction.PHYSICAL_THICKNESS)
			self.reset()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_distribution                                                    #
	#                                                                    #
	######################################################################
	def on_distribution(self, event):
		"""Handle the event when a distribution is selected
		
		This method takes a single argument:
		  event              the event.
		
		This method tells the preproduction class instance the distribution
		that was selected and resets the plot."""
		
		if self.uniform_button.GetValue():
			self.analyser.set_distribution(preproduction.UNIFORM)
		elif self.normal_button.GetValue():
			self.analyser.set_distribution(preproduction.NORMAL)
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# on_nb_tests                                                        #
	#                                                                    #
	######################################################################
	def on_nb_tests(self, event):
		"""Handle the event when a number of tests is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the value of the number of tests, tells the
		preproduction class instance the value that was entered, and resets
		the plot (if the number of tests was changed)."""
		
		# If focus is lost in favor of another application or the close
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.close_button]:
			event.Skip()
			return
		
		if not self.nb_tests_box.GetValidator().Validate(self):
			return
		
		nb_tests = int(self.nb_tests_box.GetValue())
		if nb_tests != self.analyser.get_nb_tests():
			self.analyser.set_nb_tests(nb_tests)
			self.reset()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_show                                                            #
	#                                                                    #
	######################################################################
	def on_show(self, event):
		"""Handle the event when an item to show is (un)selected
		
		This method takes a single argument:
		  event              the event.
		
		This method updates the plot according to the items selected."""
		
		self.show_results()
	
	
	######################################################################
	#                                                                    #
	# on_nb_std_devs                                                     #
	#                                                                    #
	######################################################################
	def on_nb_std_devs(self, event):
		"""Handle the event when a number of stardard deviation is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method validates the number of stardard deviation and updates
		the plot (if necessary)."""
		
		# If focus is lost in favor of another application or the close
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.close_button]:
			event.Skip()
			return
		
		if not self.nb_std_devs_box.GetValidator().Validate(self):
			return
		
		nb_std_devs = float(self.nb_std_devs_box.GetValue())
		
		if nb_std_devs != self.nb_std_devs:
			self.nb_std_devs = nb_std_devs
			
			if self.plus_minus_n_std_devs_box.GetValue():
				self.show_results()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_simulate                                                        #
	#                                                                    #
	######################################################################
	def on_simulate(self, event):
		"""Start the simulation when the simulate button is pressed
		
		This method takes a single argument:
		  event              the event.
		
		This method calls the method that disables the controls (except the
		stop button) and starts a seperate thread to simulate the
		deposition errors."""
		
		if not self.Validate():
			return
		
		self.simulating = True
		
		self.disable_controls()
		
		work_thread = threading.Thread(target = self.simulate)
		work_thread.start()
		
		monitoring_thread = threading.Thread(target = self.monitor_progress)
		monitoring_thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_stop                                                            #
	#                                                                    #
	######################################################################
	def on_stop(self, event):
		"""Stop the simulation when the stop button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		self.analyser.stop()
	
	
	######################################################################
	#                                                                    #
	# on_save                                                            #
	#                                                                    #
	######################################################################
	def on_save(self, event):
		"""Save the results when the save button is pressed
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves the results of the preproduction
		analysis."""
		
		window = wx.FileDialog(self, "Save preproduction analysis", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			output_file = open(filename, "w")
			self.analyser.save(output_file)
			output_file.close()
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_save_all                                                        #
	#                                                                    #
	######################################################################
	def on_save_all(self, event):
		"""Save all results when save all button is pressed
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves all the results of the
		preproduction analysis."""
		
		window = wx.FileDialog(self, "Save preproduction analysis", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			output_file = open(filename, "w")
			self.analyser.save_all_results(output_file)
			output_file.close()
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_save_figure                                                     #
	#                                                                    #
	######################################################################
	def on_save_figure(self, event):
		"""Save the shown figure when save figure button is pressed
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves the currently shown figure of the
		preproduction analysis."""
		
		window = wx.FileDialog(self, "Save preproduction analysis figure", os.getcwd(), "", GUI_plot.FIGURE_WILDCARD, style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			try:
				self.result_notebook.GetCurrentPage().save_to_file(filename)
			except KeyError:
				wx.MessageBox("Invalid file extension.", "Error", wx.ICON_ERROR|wx.OK)
			except IOError, error:
				wx.MessageBox("Exportation failed.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
	
	
	######################################################################
	#                                                                    #
	# on_close                                                           #
	#                                                                    #
	######################################################################
	def on_close(self, event):
		"""Close the dialog
		
		This method takes a single argument:
		  event              the event."""
		
		# Do not close the dialog during a simulation (the close button is
		# disabled, but the user can press ALT-F4).
		if not self.simulating:
			self.EndModal(wx.ID_CLOSE)
	
	
	######################################################################
	#                                                                    #
	# on_char                                                            #
	#                                                                    #
	######################################################################
	def on_char(self, event):
		"""When the escape key is pressed, emit a close event.
		
		This method takes a single argument:
		  event              the event."""
		
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_notebook_page_changed                                           #
	#                                                                    #
	######################################################################
	def on_notebook_page_changed(self, event):
		"""Adjust dialog when the notebook page is changed
		
		This method takes a single argument:
		  event              the event."""
		
		if not self.simulating and self.analyser.get_results():
			if self.result_notebook.GetPage(event.GetSelection()) != self.color_panel:
				self.save_figure_button.Enable()
			else:
				self.save_figure_button.Disable()
		else:
			self.save_figure_button.Disable()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_progress                                                        #
	#                                                                    #
	######################################################################
	def on_progress(self, event):
		"""Handle progress events
		
		This method takes a single argument:
		  event              the event.
		
		This method changes the title of the window."""
		
		progress = event.get_progress()
		
		if progress < 1.0:
			self.SetTitle("%s (%i%%)" % (self.title, int(round(100.0*progress))))
		else:
			self.SetTitle(self.title)
	
	
	######################################################################
	#                                                                    #
	# on_finished                                                        #
	#                                                                    #
	######################################################################
	def on_finished(self, event):
		"""Handle the event indication that the simulation is finished
		
		This method takes a single argument:
		  event              the event.
		
		This method calls the method to show the results of the simulation
		and the one that enables the controls."""
		
		self.show_results()
		
		self.enable_controls()
		
		self.simulating = False
	
	
	######################################################################
	#                                                                    #
	# simulate                                                           #
	#                                                                    #
	######################################################################
	def simulate(self):
		"""Simulate the deposition errors
		
		When the simulation is finished (either normally or when the stop
		button is pressed), a finished_event is sent."""
		
		self.analyser.simulate()
		
		event = finished_event(self.GetId())
		self.GetEventHandler().AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# monitor_progress                                                   #
	#                                                                    #
	######################################################################
	def monitor_progress(self):
		"""Monitor the progress of the simulation
		
		This method sends events to update the user interface."""
		
		progress = 0.0
		
		while self.simulating:
			progress = self.analyser.get_progress()
			
			event = progress_event(self.GetId(), progress)
			self.GetEventHandler().AddPendingEvent(event)
			
			time.sleep(config.CALCULATION_MIN_UPDATE_DELAY)
		
		event = progress_event(self.GetId(), 1.0)
		self.GetEventHandler().AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Reset the simulation"""
		
		for plot in self.plots.values():
			plot.reset()
		self.save_button.Disable()
		self.save_all_button.Disable()
		self.save_figure_button.Disable()
	
	
	######################################################################
	#                                                                    #
	# adjust_available_data_types                                        #
	#                                                                    #
	######################################################################
	def adjust_available_data_types(self):
		"""Prevent the use of dispersive data types when a polarisation
		other than s or p is chosen"""
		
		polarization = self.analyser.get_polarization()
		
		if polarization in S_or_P:
			for box in self.data_type_boxes.values():
				box.Enable()
		else:
			modified = False
			for data_type, box in self.data_type_boxes.items():
				if data_type in data_holder.DISPERSIVE_DATA_TYPES:
					if box.GetValue():
						box.SetValue(False)
						modified = True
					box.Disable()
				else:
					box.Enable()
			
			if modified:
				self.update_data_types()
	
	
	######################################################################
	#                                                                    #
	# update_data_types                                                  #
	#                                                                    #
	######################################################################
	def update_data_types(self):
		"""Show the tabs corresponding to the choosen data types"""
		
		data_types = [data_type for data_type, box in self.data_type_boxes.items() if box.GetValue()]
		self.analyser.set_data_types(data_types)
		
		data_types = self.analyser.get_data_types()
		
		position = 0
		for data_type, plot in self.plots.items():
			if data_type in data_types:
				if plot not in self.shown_plots:
					self.result_notebook.InsertPage(position, plot, data_holder.DATA_TYPE_NAMES[data_type])
					self.shown_plots.insert(position, plot)
				position += 1
			else:
				if plot in self.shown_plots:
					self.result_notebook.RemovePage(position)
					self.shown_plots.pop(position)
		
		if data_holder.COLOR in data_types:
			self.illuminant_choice.Enable()
			self.observer_choice.Enable()
		else:
			self.illuminant_choice.Disable()
			self.observer_choice.Disable()
		
		if data_types:
			self.simulate_button.Enable()
		else:
			self.simulate_button.Disable()
	
	
	######################################################################
	#                                                                    #
	# show_results                                                       #
	#                                                                    #
	######################################################################
	def show_results(self):
		"""Show the results
		
		This method redraws the plot according to the results and what the
		user selected to show."""
		
		data_types = self.analyser.get_data_types()
		nb_tests = self.analyser.get_nb_tests()
		expected_result = self.analyser.get_expected_result()
		results = self.analyser.get_results()
		mean = self.analyser.get_mean()
		std_dev = self.analyser.get_std_dev()
		min_, max_ = self.analyser.get_min_max()
		
		if not results:
			return
		
		for i_data_type, data_type in enumerate(data_types):
			
			if data_type is data_holder.COLOR:
				self.plots[data_type].set_content(expected_result[i_data_type], results[i_data_type], mean[i_data_type], std_dev[i_data_type], max_[i_data_type])
			
			else:
				plot = self.plots[data_type]
				
				plot.begin_batch()
				
				plot.reset()
				
				if self.all_results_box.GetValue():
					style = GUI_plot.plot_curve_style("GREY", 1)
					curves = [GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(results[i_data_type][i_test], self.multiplication_factors[data_type]), name = "%i" % (i_test+1), style = style) for i_test in range(nb_tests)]
					all_results_curve = GUI_plot.plot_curve_multiple(curves, "All results")
					for i_test in range(nb_tests):
						all_results_curve.select_curve(i_test)
					plot.add_curve(all_results_curve)
				
				if self.mean_box.GetValue():
					style = GUI_plot.plot_curve_style("BLUE", 1)
					mean_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(mean[i_data_type], self.multiplication_factors[data_type]), name = "mean", style = style)
					plot.add_curve(mean_curve)
				
				if self.plus_minus_n_std_devs_box.GetValue():
					style = GUI_plot.plot_curve_style("GREEN", 1)
					minus_n_std_devs = [mean[i_data_type][i_wvl] - self.nb_std_devs*std_dev[i_data_type][i_wvl] for i_wvl in range(self.nb_wavelengths)]
					plus_n_std_devs = [mean[i_data_type][i_wvl] + self.nb_std_devs*std_dev[i_data_type][i_wvl] for i_wvl in range(self.nb_wavelengths)]
					
					minus_n_std_devs_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(minus_n_std_devs, self.multiplication_factors[data_type]), name = "-%.1f std. dev." % self.nb_std_devs, style = style)
					plus_n_std_devs_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(plus_n_std_devs, self.multiplication_factors[data_type]), name = "+%.1f std. dev." % self.nb_std_devs, style = style)
					plus_or_minus_n_std_devs_curve = GUI_plot.plot_curve_multiple([minus_n_std_devs_curve, plus_n_std_devs_curve], "+/-%.1f std. dev." % self.nb_std_devs)
					plus_or_minus_n_std_devs_curve.select_curve(0)
					plus_or_minus_n_std_devs_curve.select_curve(1)
					plot.add_curve(plus_or_minus_n_std_devs_curve)
				
				if self.min_max_box.GetValue():
					style = GUI_plot.plot_curve_style("RED", 1)
					min_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(min_[i_data_type], self.multiplication_factors[data_type]), name = "min", style = style)
					max_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(max_[i_data_type], self.multiplication_factors[data_type]), name = "max", style = style)
					min_max_curve = GUI_plot.plot_curve_multiple([min_curve, max_curve], "worst case")
					min_max_curve.select_curve(0)
					min_max_curve.select_curve(1)
					plot.add_curve(min_max_curve)
				
				if self.expected_result_box.GetValue():
					style = GUI_plot.plot_curve_style("BLACK", 1)
					expected_result_curve = GUI_plot.plot_curve(self.wavelengths, apply_multiplication_factor(expected_result[i_data_type], self.multiplication_factors[data_type]), name = "design", style = style)
					plot.add_curve(expected_result_curve)
				
				if self.targets_box.GetValue():
					curves = []
					for target in self.targets:
						if target.get_kind() in self.data_type_targets[data_type]:
							wavelength, values, deltas = target.get_values()
							inequality = target.get_inequality()
							if inequality == targets.LARGER:
								style = GUI_plot.plot_curve_style("Black", 1, "^", 3)
							elif inequality == targets.SMALLER:
								style = GUI_plot.plot_curve_style("Black", 1, "v", 3)
							else:
								style = GUI_plot.plot_curve_style("Black", 1, "x", 3)
							single_curve = GUI_plot.plot_curve(wavelength, values, style = style)
							curves.append(single_curve)
					
					if curves:
						curve = GUI_plot.plot_curve_multiple(curves)
						for i in range(len(curves)):
							curve.select_curve(i)
						plot.add_curve(curve)
				
				plot.end_batch()
	
	
	######################################################################
	#                                                                    #
	# disable_controls                                                   #
	#                                                                    #
	######################################################################
	def disable_controls(self):
		"""Disable the controls
		
		Disable all controls (except the stop button) during a simulation."""
		
		for box in self.data_type_boxes.values():
			box.Disable()
		self.angle_box.Disable()
		self.s_polarized_button.Disable()
		self.p_polarized_button.Disable()
		self.unpolarized_button.Disable()
		self.other_polarizations_button.Disable()
		self.other_polarizations_box.Disable()
		self.illuminant_choice.Disable()
		self.observer_choice.Disable()
		self.percentage_thickness_button.Disable()
		self.percentage_thickness_box.Disable()
		self.physical_thickness_button.Disable()
		self.physical_thickness_box.Disable()
		self.uniform_button.Disable()
		self.normal_button.Disable()
		self.nb_tests_box.Disable()
		self.all_results_box.Disable()
		self.mean_box.Disable()
		self.plus_minus_n_std_devs_box.Disable()
		self.nb_std_devs_box.Disable()
		self.min_max_box.Disable()
		self.expected_result_box.Disable()
		self.targets_box.Disable()
		self.simulate_button.Disable()
		self.stop_button.Enable()
		self.save_button.Disable()
		self.save_all_button.Disable()
		self.save_figure_button.Disable()
		self.close_button.Disable()
		
		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
	
	
	######################################################################
	#                                                                    #
	# enable_controls                                                    #
	#                                                                    #
	######################################################################
	def enable_controls(self):
		"""Enable the controls
		
		This method enables all controls except the stop button, and the
		save and save all buttons when no results are available. It also
		takes care of disabling the illuminant and observer choice when the
		color errors are not simulated."""
		
		data_types = self.analyser.get_data_types()
		
		self.adjust_available_data_types()
		self.angle_box.Enable()
		self.s_polarized_button.Enable()
		self.p_polarized_button.Enable()
		self.unpolarized_button.Enable()
		self.other_polarizations_button.Enable()
		self.other_polarizations_box.Enable()
		if data_holder.COLOR in data_types:
			self.illuminant_choice.Enable()
			self.observer_choice.Enable()
		else:
			self.illuminant_choice.Disable()
			self.observer_choice.Disable()
		self.percentage_thickness_button.Enable()
		self.percentage_thickness_box.Enable()
		self.physical_thickness_button.Enable()
		self.physical_thickness_box.Enable()
		self.uniform_button.Enable()
		self.normal_button.Enable()
		self.nb_tests_box.Enable()
		self.all_results_box.Enable()
		self.mean_box.Enable()
		self.plus_minus_n_std_devs_box.Enable()
		self.nb_std_devs_box.Enable()
		self.min_max_box.Enable()
		self.expected_result_box.Enable()
		self.targets_box.Enable()
		if self.analyser.get_data_types():
			self.simulate_button.Enable()
		else:
			self.simulate_button.Disable()
		self.stop_button.Disable()
		if self.analyser.get_results():
			self.save_button.Enable()
			self.save_all_button.Enable()
			if self.result_notebook.GetCurrentPage() and self.result_notebook.GetCurrentPage() != self.color_panel:
				self.save_figure_button.Enable()
			else:
				self.save_figure_button.Disable()
		else:
			self.save_button.Disable()
			self.save_all_button.Disable()
			self.save_figure_button.Disable()
		self.close_button.Enable()
		
		self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))


########################################################################
#                                                                      #
# color_error_panel                                                    #
#                                                                      #
########################################################################
class color_error_panel(wx.Panel):
	"""A class for the panel to show the color errors"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent):
		"""Initialize an instance of the panel
		
		This method takes 1 argument:
		  parent             the panel's parent."""
		
		wx.Panel.__init__(self, parent, style = wx.NO_BORDER)
		
		self.R_colors = []
		self.T_colors = []
		
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.subpanel = None
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Reset the content of the panel"""
		
		if self.subpanel:
			self.R_colors = []
			self.T_colors = []
			
			self.main_sizer.Remove(self.subpanel)
			self.subpanel.Destroy()
			self.subpanel = None
	
	
	######################################################################
	#                                                                    #
	# set_content                                                        #
	#                                                                    #
	######################################################################
	def set_content(self, expected_result, results, mean, std_dev, max_):
		"""Set the content of the panel
		
		This method takes 5 arguments:
		  expected_result    the expected result (a list of two color
		                     instances containing reflection and
		                     tranmission colors of the design);
		  mean               the mean result (a list of two color
		                     instances containing mean reflection and
		                     tranmission colors);
		  results            a list of the results of all tests, each
		                     element of the list is itself a list of two
		                     elements for reflextion and transmission;
		  std_dev            the standard deviation of the results with
		                     regard to the expected results (a list of 2
		                     elements);
		  max_               the maximum deviation from the expected
		                     results (a list of two elements)."""
		
		if self.subpanel:
			self.main_sizer.Remove(self.subpanel)
			self.subpanel.Destroy()
		
		self.subpanel = wx.Panel(self, style = wx.NO_BORDER)
		
		subpanel_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.subpanel.SetAutoLayout(True)
		self.subpanel.SetSizer(subpanel_sizer)
		
		expected_Lab_R = expected_result[0].Lab()
		expected_Lab_T = expected_result[1].Lab()
		
		self.R_colors = [result[0] for result in results]
		self.T_colors = [result[1] for result in results]
		self.R_colors.sort(key = lambda R_color: color.Delta_E_1976(R_color, expected_Lab_R))
		self.T_colors.sort(key = lambda T_color: color.Delta_E_1976(T_color, expected_Lab_T))
		
		# Create a static box to put the color.
		static_box = wx.StaticBox(self.subpanel, -1)
		
		subpanel_sizer_1 = wx.FlexGridSizer(0, 6, 5, 15)
		
		subpanel_sizer_1.Add((-1,-1))
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "design"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "mean"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "std. dev."), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "max. Delta E"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "worst results"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "Reflection:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(GUI_color.color_bar([expected_result[0]], self.subpanel, size = (20, 20)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(GUI_color.color_bar([mean[0]], self.subpanel, size = (20, 20)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "%.3f" % std_dev[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "%.3f" % color.Delta_E_1976(max_[0], expected_Lab_R)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1_1 = wx.BoxSizer(wx.HORIZONTAL)
		for i in range(max(-5, -len(self.R_colors)), -1):
			subpanel_sizer_1_1.Add(GUI_color.color_bar([self.R_colors[i]], self.subpanel, size = (20, 20)), 0, wx.RIGHT, 5)
		subpanel_sizer_1_1.Add(GUI_color.color_bar([self.R_colors[-1]], self.subpanel, size = (20, 20)), 0)
		subpanel_sizer_1.Add(subpanel_sizer_1_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "Transmission:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(GUI_color.color_bar([expected_result[1]], self.subpanel, size = (20, 20)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(GUI_color.color_bar([mean[1]], self.subpanel, size = (20, 20)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "%.3f" % std_dev[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1.Add(wx.StaticText(self.subpanel, -1, "%.3f" % color.Delta_E_1976(max_[1], expected_Lab_T)), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		subpanel_sizer_1_2 = wx.BoxSizer(wx.HORIZONTAL)
		for i in range(max(-5, -len(self.T_colors)), -1):
			subpanel_sizer_1_2.Add(GUI_color.color_bar([self.T_colors[i]], self.subpanel, size = (20, 20)), 0, wx.RIGHT, 5)
		subpanel_sizer_1_2.Add(GUI_color.color_bar([self.T_colors[-1]], self.subpanel, size = (20, 20)), 0)
		subpanel_sizer_1.Add(subpanel_sizer_1_2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		
		# Put in the static box.
		box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
		box_sizer.Add(subpanel_sizer_1, 0,  wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		subpanel_sizer.Add(box_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
		
		self.subpanel.Fit()
		
		self.main_sizer.Add(self.subpanel)


########################################################################
#                                                                      #
# apply_multiplication_factor                                          #
#                                                                      #
########################################################################
def apply_multiplication_factor(data, multiplication_factor):
	"""Apply a multiplication factor to data
	
	This function takes 2 arguments:
	  data                   a list of data;
	  multiplication_factor  the muliplication factor."""
	
	if multiplication_factor == 1.0:
		return data
	else:
		return [multiplication_factor*datum for datum in data]
