# GUI_optimization.py
# 
# Dialogs to optimize for the GUI of Filters.
# 
# Copyright (c) 2003-2011,2013-2015 Stephane Larouche.
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
import math
import copy
try:
	import threading
except ImportError:
	pass
import time

import wx
import wx.grid

from definitions import *
import config
import targets
import color
import materials
import optimization_refinement
import optimization_needles
import optimization_steps
import optimization_Fourier
from moremath import Levenberg_Marquardt

from GUI_plot import plot, plot_curve, plot_curve_segmented, plot_curve_style, TOP
from GUI_validators import float_validator, int_validator



########################################################################
#                                                                      #
# update_event                                                         #
#                                                                      #
########################################################################

update_event_type = wx.NewEventType()

EVT_update = wx.PyEventBinder(update_event_type, 1)

class update_event(wx.PyCommandEvent):
	
	eventType = update_event_type
	
	def __init__(self, windowID, working, status):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.working = working
		self.status = status
	
	def Clone(self):
		self.__class__(self.GetId())
	
	def get_working(self):
		return self.working
	
	def get_status(self):
		return self.status



########################################################################
#                                                                      #
# optimization_dialog                                                  #
#                                                                      #
########################################################################
class optimization_dialog(wx.Dialog):
	"""Base class for all optimization dialogs"""
	
	title = "Optimization"
	specific_save_name = ""
	optimization_class = None
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent             the dialog's parent;
		  filter             the filter being optimized;
		  targets            the targets."""
		
		self.parent = parent
		self.filter = filter
		self.targets = targets
		
		self.optimization = self.optimization_class(self.filter, self.targets, self)
		
		wx.Dialog.__init__(self, self.parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.add_content()
		
		self.add_buttons()
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.Bind(EVT_update, self.on_update)
		
		# Remember the status when the interface was last updated to
		# determine when it is necessary to update it.
		self.last_working = None
		self.last_status = None
		
		working = self.optimization.get_working()
		status = self.optimization.get_status()
		
		self.update_(working, status)
		
		self.last_working = working
		self.last_status = status
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add buttons to the dialog
		
		This method adds the standard Go, Iterate, Stop, Correlation
		Matrix, Ok and Cancel buttons to the dialog.
		
		In power user mode, it also adds buttons to save the spectra, the
		index profile and method specific informations"""
		
		# Create buttons.
		self.go_button = wx.Button(self, -1, "&Go")
		self.iterate_button = wx.Button(self, -1, "&Iterate")
		self.stop_button = wx.Button(self, -1, "&Stop")
		self.correlation_button = wx.Button(self, -1, "Correlation &Matrix")
		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.on_go_button, self.go_button)
		self.Bind(wx.EVT_BUTTON, self.on_iterate_button, self.iterate_button)
		self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.stop_button)
		self.Bind(wx.EVT_BUTTON, self.on_correlation_button, self.correlation_button)
		self.Bind(wx.EVT_BUTTON, self.on_ok_button, self.ok_button)
		
		# Arrange them.
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.go_button, 0)
		buttons.Add(self.iterate_button, 0, wx.LEFT, 20)
		buttons.Add(self.stop_button, 0, wx.LEFT, 20)
		buttons.Add(self.correlation_button, 0, wx.LEFT, 20)
		buttons.Add(self.ok_button, 0, wx.LEFT, 20)
		buttons.Add(self.cancel_button, 0, wx.LEFT, 20)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
		
		# Give power users the possibility to save results during the
		# optimization.
		if config.POWER_USER:
			
			# Create a button to save the values
			self.save_values_button = wx.Button(self, -1, "Save values")
			self.Bind(wx.EVT_BUTTON, self.on_save_values, self.save_values_button)
			
			# Create a button to save the index profile
			self.save_index_profile_button = wx.Button(self, -1, "Save index_profile")
			self.Bind(wx.EVT_BUTTON, self.on_save_index_profile, self.save_index_profile_button)
			
			# Create a button for saving information specific to the
			# optimization method.
			if self.specific_save_name:
				self.specific_save_button = wx.Button(self, -1, "Save dMF")
				self.Bind(wx.EVT_BUTTON, self.on_specific_save, self.specific_save_button)
			
			# Add it to the window.
			buttons_2 = wx.BoxSizer(wx.HORIZONTAL)
			buttons_2.Add(self.save_values_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
			buttons_2.Add(self.save_index_profile_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
			if self.specific_save_name:
				buttons_2.Add(self.specific_save_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
			self.main_sizer.Add(buttons_2, 0, wx.ALIGN_CENTER|wx.ALL, 0)
	
	
	######################################################################
	#                                                                    #
	# on_go_button                                                       #
	#                                                                    #
	######################################################################
	def on_go_button(self, event):
		"""Handle button events for the go button
		
		This method takes a single argument:
		  event              the event.
		
		It starts a new thread where the optimization is performed until a
		stop criteria is met."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.go)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_iterate_button                                                  #
	#                                                                    #
	######################################################################
	def on_iterate_button(self, event):
		"""Handle button events for the iterate button
		
		This method takes a single argument:
		  event              the event.
		
		It starts a new thread where 1 iteration is performed."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.iterate)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_stop_button                                                     #
	#                                                                    #
	######################################################################
	def on_stop_button(self, event):
		"""Handle button events for the stop button
		
		This method takes a single argument:
		  event              the event.
		
		It asks the optimization to stop. The optimization will actually
		stop at the next moment it checks if it should stop, usually
		between 2 iterations."""
		
		self.optimization.stop()
	
	
	######################################################################
	#                                                                    #
	# on_correlation_button                                              #
	#                                                                    #
	######################################################################
	def on_correlation_button(self, event):
		"""Handle button events for the correlation matrix button
		
		This method takes a single argument:
		  event              the event.
		
		It shows a dialog with the correlation matrix."""
		
		window = correlation_dialog(self, self.optimization)
		window.CenterOnParent()
		window.ShowModal()
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_ok_button                                                       #
	#                                                                    #
	######################################################################
	def on_ok_button(self, event):
		"""Handle button events for the ok button
		
		This method takes a single argument:
		  event              the event.
		
		It modifies the filter and closes the dialog."""
		
		self.optimization.copy_to_filter()
		self.EndModal(wx.ID_OK)
	
	
	######################################################################
	#                                                                    #
	# on_save_values                                                     #
	#                                                                    #
	######################################################################
	def on_save_values(self, event):
		"""Handle button events for the save values button
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves the spectra."""
		
		window = wx.FileDialog(self, "Save Values", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			filename = window.GetPath()
			
			output_file = open(filename, "w")
			self.optimization.save_values(output_file)
			output_file.close()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_save_index_profile                                              #
	#                                                                    #
	######################################################################
	def on_save_index_profile(self, event):
		"""Handle button events for the save index profile button
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves the index profile."""
		
		window = wx.FileDialog(self, "Save Index Profile", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			filename = window.GetPath()
			
			output_file = open(filename, "w")
			self.optimization.save_index_profile(output_file)
			output_file.close()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_specific_save                                                   #
	#                                                                    #
	######################################################################
	def on_specific_save(self, event):
		"""Handle button events for the specific save button
		
		This method takes a single argument:
		  event              the event.
		
		It shows a FileDialog and saves method specific information."""
		
		window = wx.FileDialog(self, self.specific_save_name, os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			filename = window.GetPath()
			
			output_file = open(filename, "w")
			self.optimization.specific_save(output_file)
			output_file.close()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_close                                                           #
	#                                                                    #
	######################################################################
	def on_close(self, event):
		"""Handle close events
		
		This method takes a single argument:
		  event              the event.
		
		It closes the dialog only if no operation is currently being
		executed."""
		
		# Do not close the dialog when the cancel button is disabled (the
		# close button is disabled, but the user could press ALT-F4).
		if self.cancel_button.IsEnabled():
			self.EndModal(wx.ID_CLOSE)
	
	
	######################################################################
	#                                                                    #
	# disable_all_buttons                                                #
	#                                                                    #
	######################################################################
	def disable_all_buttons(self):
		"""Disable all the buttons
		
		Call this method before starting an operation in another thread
		to avoid problems in the very short time between the moment the
		button is pressed and the moment the dialog is updated. This method
		is NOT thread safe."""
		
		self.go_button.Disable()
		self.iterate_button.Disable()
		self.stop_button.Disable()
		self.correlation_button.Disable()
		self.ok_button.Disable()
		self.cancel_button.Disable()
		
		if config.POWER_USER:
			self.save_values_button.Disable()
			self.save_index_profile_button.Disable()
		
		# Force the immediate redraw of the window without waiting for the
		# return to the event loop.
		self.Update()
	
	
	######################################################################
	#                                                                    #
	# update                                                             #
	#                                                                    #
	######################################################################
	def update(self, working, status):
		"""Update the dialog
		
		This method is thread safe. It only sends an event that will really
		takes care of the update.
		
		It takes two argument:
		  working            a boolean indicating if the optimization is
		                     working;
		  status             the status of the optimization."""
		
		event = update_event(self.GetId(), working, status)
		self.GetEventHandler().AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# on_update                                                          #
	#                                                                    #
	######################################################################
	def on_update(self, event):
		"""Handle update events
		
		This method takes a single argument:
		  event              the event.
		
		It simply calls the update_ method."""
		
		working = event.get_working()
		status = event.get_status()
		
		self.update_(working, status)
		
		self.last_working = working
		self.last_status = status
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, working, status):
		"""Update the dialog
		
		This method is NOT thread safe. If you want to update the dialog
		from another thread, use update instead.
		
		It takes 2 arguments:
		  working    a boolean indicating if the optimization is currently
		             working;
		  status     the status of the optimization."""
		
		if status != self.last_status or working != self.last_working:
			# During fitting, disable all buttons except for the stop button
			# when the process is stopable.
			if working:
				self.go_button.Disable()
				self.iterate_button.Disable()
				if self.optimization.get_can_stop():
					self.stop_button.Enable()
					self.stop_button.SetFocus()
					self.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
				else:
					self.stop_button.Disable()
					self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
				self.correlation_button.Disable()
				self.ok_button.Disable()
				self.cancel_button.Disable()
				if config.POWER_USER:
					self.save_values_button.Disable()
					self.save_index_profile_button.Disable()
			
			# If a stop criteria is met, disable the go, iterate and stop
			# buttons and enable ok and cancel button. Select the ok button.
			elif self.optimization.get_stop_criteria_met():
				self.go_button.Disable()
				self.iterate_button.Disable()
				self.stop_button.Disable()
				self.correlation_button.Enable()
				self.ok_button.Enable()
				self.cancel_button.Enable()
				self.ok_button.SetFocus()
				self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
				if config.POWER_USER:
					self.save_values_button.Enable()
					self.save_index_profile_button.Enable()
			
			# If the maximum iterations were reached, give the user the
			# opportunity to continue.
			elif self.optimization.get_max_iterations_reached():
				self.go_button.SetLabel("&Continue")
				self.go_button.Enable()
				self.iterate_button.Enable()
				self.stop_button.Disable()
				self.correlation_button.Enable()
				self.ok_button.Enable()
				self.cancel_button.Enable()
				self.go_button.SetFocus()
				self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
				if config.POWER_USER:
					self.save_values_button.Enable()
					self.save_index_profile_button.Enable()
			
			# Otherwise, enable everything except for the stop button. and make
			# sure the label of the go button is go.
			else:
				self.go_button.SetLabel("&Go")
				self.go_button.Enable()
				self.iterate_button.Enable()
				self.stop_button.Disable()
				self.correlation_button.Enable()
				self.ok_button.Enable()
				self.cancel_button.Enable()
				self.go_button.SetFocus()
				self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
				if config.POWER_USER:
					self.save_values_button.Enable()
					self.save_index_profile_button.Enable()




########################################################################
#                                                                      #
# optimization_refinement_dialog                                       #
#                                                                      #
########################################################################
class optimization_refinement_dialog(optimization_dialog):
	"""Dialog for the refinement method"""
	
	title = "Refinement"
	optimization_class = optimization_refinement.optimization_refinement
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent             the dialog's parent;
		  filter             the filter being optimized;
		  targets            the targets."""
		
		# Keep the value of the iteration locally in order to determine if
		# is has changed and if it is necessary to redraw the plots. Also
		# remember when the plots were last changed to avoid redrawing them
		# too often.
		self.iteration = -1
		self.last_update_time = 0.0
		
		optimization_dialog.__init__(self, parent, filter, targets)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		This methods adds a target plot, color target boxes, an index
		profile plot, and text information about the optimization to the
		dialog."""
		
		# Count the number of spectral and color targets.
		self.nb_photometric_targets = 0
		self.nb_dispersive_targets = 0
		self.nb_color_targets = 0
		for i_target in range(len(self.targets)):
			kind = self.targets[i_target].get_kind()
			if kind in targets.PHOTOMETRIC_TARGETS:
				self.nb_photometric_targets += 1
			elif kind in targets.DISPERSIVE_TARGETS:
				self.nb_dispersive_targets += 1
			elif kind in targets.COLOR_TARGETS:
				self.nb_color_targets += 1
		
		self.target_notebook =  wx.Notebook(self, size = (700, 230))
		
		# Create a plot for the photometric targets and the results.
		if self.nb_photometric_targets:
			self.photometric_plot = plot(self.target_notebook)
			self.photometric_plot.set_clickable()
			self.photometric_plot.set_allow_remove_curve(False)
			self.photometric_plot.set_xlabel("Wavelength (nm)")
			self.photometric_plot.set_ylabel("R, T, or A")
			
			self.target_notebook.AddPage(self.photometric_plot, "Photometric")
		
		# Create a plot for the dispersive targets and the results.
		if self.nb_dispersive_targets:
			self.dispersive_plot = plot(self.target_notebook)
			self.dispersive_plot.set_clickable()
			self.dispersive_plot.set_allow_remove_curve(False)
			self.dispersive_plot.set_xlabel("Wavelength (nm)")
			self.dispersive_plot.set_ylabel("Phase (deg.), GD (fs), GDD (fs^2)")
			
			self.target_notebook.AddPage(self.dispersive_plot, "Phase, GD, GDD")
		
		# Make a list for the white points.
		self.XYZ_n = [None]*self.nb_color_targets
		
		# Create widgets for the color targets.
		if self.nb_color_targets:
			self.color_panel = wx.ScrolledWindow(self.target_notebook)
			self.color_panel.SetScrollbars(1, 1, 1, 1)
			
			color_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
			
			self.color_panel.SetSizer(color_panel_sizer)
			
			self.color_target_borders = [None]*self.nb_color_targets
			self.color_target_boxes = [None]*self.nb_color_targets
			color_target_sizers = [None]*self.nb_color_targets
			self.color_borders = [None]*self.nb_color_targets
			self.color_boxes = [None]*self.nb_color_targets
			color_sizers = [None]*self.nb_color_targets
			for i_color_box in range(self.nb_color_targets):
				self.color_target_borders[i_color_box] = wx.Panel(self.color_panel, size = (-1, -1), style = wx.NO_BORDER|wx.ST_NO_AUTORESIZE)
				color_target_sizers[i_color_box] = wx.BoxSizer(wx.VERTICAL)
				self.color_target_borders[i_color_box].SetSizer(color_target_sizers[i_color_box])
				self.color_target_boxes[i_color_box] = wx.Panel(self.color_target_borders[i_color_box], size = (40, 40), style = wx.NO_BORDER)
				color_target_sizers[i_color_box].Add(self.color_target_boxes[i_color_box], 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
				self.color_borders[i_color_box] = wx.Panel(self.color_panel, size = (-1, -1), style = wx.NO_BORDER|wx.ST_NO_AUTORESIZE)
				color_sizers[i_color_box] = wx.BoxSizer(wx.VERTICAL)
				self.color_borders[i_color_box].SetSizer(color_sizers[i_color_box])
				self.color_boxes[i_color_box] = wx.Panel(self.color_borders[i_color_box], size = (40, 40), style = wx.NO_BORDER)
				color_sizers[i_color_box].Add(self.color_boxes[i_color_box], 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
			
			# Put them in a sizer.
			color_sizer = wx.FlexGridSizer(2, self.nb_color_targets+1, 5, 5)
			color_sizer.Add(wx.StaticText(self.color_panel, -1, "Targets: "), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
			for i in range(self.nb_color_targets):
				color_sizer.Add(self.color_target_borders[i], 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
			color_sizer.Add(wx.StaticText(self.color_panel, -1, "Results: "), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
			for i in range(self.nb_color_targets):
				color_sizer.Add(self.color_borders[i], 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
			
			color_panel_sizer.Add(color_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
			
			self.target_notebook.AddPage(self.color_panel, "Color")
		
		# Populate the target plot and the color targets.
		self.wvls, self.target_values = self.optimization.get_target_values()
		wvls, calculated_values = self.optimization.get_calculated_values()
		inequalities = self.optimization.get_inequalities()
		self.calculated_values_curve_nb = []
		i_color_box = 0
		if self.nb_photometric_targets:
			self.photometric_plot.begin_batch()
		if self.nb_dispersive_targets:
			self.dispersive_plot.begin_batch()
		for i_target in range(len(self.targets)):
			kind = self.targets[i_target].get_kind()
			if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.DISPERSIVE_TARGETS:
				if inequalities[i_target] == targets.SMALLER:
					style = plot_curve_style("Black", 1, "v", 5)
				elif inequalities[i_target] == targets.LARGER:
					style = plot_curve_style("Black", 1, "^", 5)
				else:
					style = plot_curve_style("Black", 1, "x", 5)
				if kind in targets.PHOTOMETRIC_TARGETS:
					target_curve = plot_curve(self.wvls[i_target], self.target_values[i_target], style = style)
					calculated_curve = plot_curve(self.wvls[i_target], calculated_values[i_target], style = plot_curve_style("Blue", 1, "x", 5))
					self.photometric_plot.add_curve(target_curve)
					self.calculated_values_curve_nb.append(self.photometric_plot.add_curve(calculated_curve))
				elif kind in targets.DISPERSIVE_TARGETS:
					if kind in [targets.R_PHASE_TARGET, targets.T_PHASE_TARGET, targets.R_PHASE_SPECTRUM_TARGET, targets.T_PHASE_SPECTRUM_TARGET]:
						target_curve = plot_curve(self.wvls[i_target], self.target_values[i_target], style = style)
						calculated_curve = plot_curve(self.wvls[i_target], calculated_values[i_target], style = plot_curve_style("Blue", 1, "x", 5))
					elif kind in [targets.R_GD_TARGET, targets.T_GD_TARGET, targets.R_GD_SPECTRUM_TARGET, targets.T_GD_SPECTRUM_TARGET]:
						target_curve = plot_curve(self.wvls[i_target], [value*1.0e15 for value in self.target_values[i_target]], style = style)
						calculated_curve = plot_curve(self.wvls[i_target], [value*1.0e15 for value in calculated_values[i_target]], style = plot_curve_style("Blue", 1, "x", 5))
					elif kind in [targets.R_GDD_TARGET, targets.T_GDD_TARGET, targets.R_GDD_SPECTRUM_TARGET, targets.T_GDD_SPECTRUM_TARGET]:
						target_curve = plot_curve(self.wvls[i_target], [value*1.0e30 for value in self.target_values[i_target]], style = style)
						calculated_curve = plot_curve(self.wvls[i_target], [value*1.0e30 for value in calculated_values[i_target]], style = plot_curve_style("Blue", 1, "x", 5))
					self.dispersive_plot.add_curve(target_curve)
					self.calculated_values_curve_nb.append(self.dispersive_plot.add_curve(calculated_curve))
			elif kind in targets.COLOR_TARGETS:
				target = self.targets[i_target]
				illuminant_name, observer_name = target.get_illuminant_and_observer()
				color_space = target.get_color_space()
				illuminant = color.get_illuminant(illuminant_name)
				observer = color.get_observer(observer_name)
				self.XYZ_n[i_color_box] = color.white_point(observer, illuminant)
				XYZ_target = color.change_color_space(color_space, color.XYZ, self.target_values[i_target], self.XYZ_n[i_color_box])
				XYZ = color.change_color_space(color_space, color.XYZ, calculated_values[i_target], self.XYZ_n[i_color_box])
				RGB_target, RGB_target_error = color.XYZ_to_RGB(XYZ_target)
				RGB, RGB_error = color.XYZ_to_RGB(XYZ)
				target_color = wx.Colour(RGB_target[0]*255.0, RGB_target[1]*255.0, RGB_target[2]*255.0)
				result_color = wx.Colour(RGB[0]*255.0, RGB[1]*255.0, RGB[2]*255.0)
				self.color_target_boxes[i_color_box].SetBackgroundColour(target_color)
				if RGB_target_error:
					self.color_target_borders[i_color_box].SetBackgroundColour(wx.NamedColour("RED"))
				else:
					self.color_target_borders[i_color_box].SetBackgroundColour(wx.NamedColour("BLACK"))
				self.color_boxes[i_color_box].SetBackgroundColour(result_color)
				if RGB_error:
					self.color_borders[i_color_box].SetBackgroundColour(wx.NamedColour("RED"))
				else:
					self.color_borders[i_color_box].SetBackgroundColour(wx.NamedColour("BLACK"))
				self.calculated_values_curve_nb.append(i_color_box)
				i_color_box += 1
		if self.nb_photometric_targets:
			self.photometric_plot.end_batch()
		if self.nb_dispersive_targets:
			self.dispersive_plot.end_batch()
		
		# Create a plot for the index profile.
		self.index_profile_plot = plot(self, size = (700, 180), style = wx.SUNKEN_BORDER)
		self.index_profile_plot.set_xlabel("Depth (nm)")
		self.index_profile_plot.set_ylabel("n")
		
		# Show the index profile.
		thickness, index_profile = self.optimization.get_index_profile()
		design_curve = plot_curve(thickness, index_profile)
		self.design_curve_nb = self.index_profile_plot.add_curve(design_curve)
		
		# Text for the status, the number of iterations and chi square, ...
		status_sizer = wx.BoxSizer(wx.HORIZONTAL)
		status_sizer.Add(wx.StaticText(self, -1, "Status: ", style = wx.ALIGN_LEFT), 0)
		self.status_text = wx.StaticText(self, -1, "%s" % "", style = wx.ALIGN_LEFT)
		status_sizer.Add(self.status_text, 0)
		iteration_sizer = wx.BoxSizer(wx.HORIZONTAL)
		iteration_sizer.Add(wx.StaticText(self, -1, "Iteration: ", style = wx.ALIGN_LEFT), 0)
		self.iteration_text = wx.StaticText(self, -1, "%i" % 0, style = wx.ALIGN_LEFT)
		iteration_sizer.Add(self.iteration_text, 0)
		chi_2_sizer = wx.BoxSizer(wx.HORIZONTAL)
		chi_2_sizer.Add(wx.StaticText(self, -1, "Chi square: ", style = wx.ALIGN_LEFT), 0)
		self.chi_2_text = wx.StaticText(self, -1, "%.6f" % 0.0, style = wx.ALIGN_LEFT)
		chi_2_sizer.Add(self.chi_2_text, 0)
		norm_gradient_sizer = wx.BoxSizer(wx.HORIZONTAL)
		norm_gradient_sizer.Add(wx.StaticText(self, -1, "Gradient norm: ", style = wx.ALIGN_LEFT), 0)
		self.norm_gradient_text = wx.StaticText(self, -1, "%.6f" % 0.0, style = wx.ALIGN_LEFT)
		norm_gradient_sizer.Add(self.norm_gradient_text, 0)
		nb_front_layers_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_front_layers_sizer.Add(wx.StaticText(self, -1, "Nb front layers: ", style = wx.ALIGN_LEFT), 0)
		self.nb_front_layers_text = wx.StaticText(self, -1, "%i" % 0, style = wx.ALIGN_LEFT)
		nb_front_layers_sizer.Add(self.nb_front_layers_text, 0)
		nb_back_layers_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_back_layers_sizer.Add(wx.StaticText(self, -1, "Nb back layers: ", style = wx.ALIGN_LEFT), 0)
		self.nb_back_layers_text = wx.StaticText(self, -1, "%i" % 0, style = wx.ALIGN_LEFT)
		nb_back_layers_sizer.Add(self.nb_back_layers_text, 0)
		
		# Put the statistics in a sizer.
		statistic_sizer = wx.FlexGridSizer(2, 3, 5, 150)
		statistic_sizer.Add(status_sizer)
		statistic_sizer.Add(chi_2_sizer)
		statistic_sizer.Add(nb_front_layers_sizer)
		statistic_sizer.Add(iteration_sizer)
		statistic_sizer.Add(norm_gradient_sizer)
		statistic_sizer.Add(nb_back_layers_sizer)
		
		# Put everything in the sizer.
		self.main_sizer.Add(self.target_notebook, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(self.index_profile_plot, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(statistic_sizer, 0, wx.EXPAND|wx.ALL, 10)
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, working, status):
		"""Update the dialog
		
		This method is NOT thread safe. If you want to update the dialog
		from another thread, use update instead.
		
		It takes 2 arguments:
		  working    a boolean indicating if the optimization is currently
		             working;
		  status     the status of the optimization."""
		
		optimization_dialog.update_(self, working, status)
		
		# If the status does not change during work, do not update the
		# dialog too often.
		present_time = time.clock()
		if working and working == self.last_working and status == self.last_status and present_time - self.last_update_time < config.OPTIMIZATION_MIN_UPDATE_DELAY:
			return
		self.last_update_time = present_time
		
		just_removed_thin_layers = self.optimization.get_just_removed_thin_layers()
		
		# If the iteration hasn't changed, it is not necessary to redraw
		# the plots, except if thin layers were removed.
		iteration = self.optimization.get_iteration()
		if iteration == self.iteration and not just_removed_thin_layers:
			return
		
		self.iteration = iteration
		chi_2 = self.optimization.get_chi_2()
		norm_gradient = self.optimization.get_norm_gradient()
		
		# Get the values from the optimization.
		thickness, index_profile = self.optimization.get_index_profile()
		wvls, calculated_values = self.optimization.get_calculated_values()
		
		# Update the index profile.
		design_curve = plot_curve(thickness, index_profile)
		self.design_curve_nb = self.index_profile_plot.reset(design_curve)
		
		# Update the target plot by replacing all the curves by the new
		# ones.
		if self.nb_photometric_targets:
			self.photometric_plot.begin_batch()
		if self.nb_dispersive_targets:
			self.dispersive_plot.begin_batch()
		for i_target in range(len(self.targets)):
			kind = self.targets[i_target].get_kind()
			if kind in targets.PHOTOMETRIC_TARGETS:
				self.photometric_plot.replace_curve(self.calculated_values_curve_nb[i_target], wvls[i_target], calculated_values[i_target])
			elif kind in targets.DISPERSIVE_TARGETS:
				if kind in [targets.R_PHASE_TARGET, targets.T_PHASE_TARGET, targets.R_PHASE_SPECTRUM_TARGET, targets.T_PHASE_SPECTRUM_TARGET]:
					self.dispersive_plot.replace_curve(self.calculated_values_curve_nb[i_target], wvls[i_target], calculated_values[i_target])
				elif kind in [targets.R_GD_TARGET, targets.T_GD_TARGET, targets.R_GD_SPECTRUM_TARGET, targets.T_GD_SPECTRUM_TARGET]:
					self.dispersive_plot.replace_curve(self.calculated_values_curve_nb[i_target], wvls[i_target], [value*1.0e15 for value in calculated_values[i_target]])
				elif kind in [targets.R_GDD_TARGET, targets.T_GDD_TARGET, targets.R_GDD_SPECTRUM_TARGET, targets.T_GDD_SPECTRUM_TARGET]:
					self.dispersive_plot.replace_curve(self.calculated_values_curve_nb[i_target], wvls[i_target], [value*1.0e30 for value in calculated_values[i_target]])
			elif kind in targets.COLOR_TARGETS:
				color_space = self.targets[i_target].get_color_space()
				XYZ = color.change_color_space(color_space, color.XYZ, calculated_values[i_target], self.XYZ_n[self.calculated_values_curve_nb[i_target]])
				RGB, RGB_error = color.XYZ_to_RGB(XYZ)
				result_color = wx.Colour(RGB[0]*255.0, RGB[1]*255.0, RGB[2]*255.0)
				self.color_boxes[self.calculated_values_curve_nb[i_target]].SetBackgroundColour(result_color)
				if RGB_error:
					self.color_borders[self.calculated_values_curve_nb[i_target]].SetBackgroundColour(wx.NamedColour("RED"))
				else:
					self.color_borders[self.calculated_values_curve_nb[i_target]].SetBackgroundColour(wx.NamedColour("BLACK"))
				self.color_boxes[self.calculated_values_curve_nb[i_target]].Refresh()
				self.color_borders[self.calculated_values_curve_nb[i_target]].Refresh()
		if self.nb_photometric_targets:
			self.photometric_plot.end_batch()
		if self.nb_dispersive_targets:
			self.dispersive_plot.end_batch()
		
		# Update the text.
		if status == Levenberg_Marquardt.IMPROVING:
			status_text = "improving"
		elif status == Levenberg_Marquardt.MINIMUM_FOUND:
			status_text = "minimum found"
		elif status == Levenberg_Marquardt.CHI_2_IS_OK:
			status_text = "chi square is OK"
		elif status == Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL:
			status_text = "chi square change is too small"
		elif status == Levenberg_Marquardt.SINGULAR_MATRIX:
			status_text = "singular matrix"
		elif status == Levenberg_Marquardt.ALL_PARAMETERS_ARE_STUCK:
			status_text = "all parameters stuck at their limits"
		elif status == Levenberg_Marquardt.DELTA_IS_TOO_SMALL:
			status_text = "trust region smaller than machine precision"
		else:
			status_text = ""
		self.status_text.SetLabel("%s" % status_text)
		self.iteration_text.SetLabel("%i" % iteration)
		if chi_2:
			order_of_magnitude = int(math.floor(math.log10(chi_2)))
		else:
			order_of_magnitude = 0
		if order_of_magnitude > 5 or order_of_magnitude < 0:
			self.chi_2_text.SetLabel("%.6e" % chi_2)
		else:
			nb_decimals = 6 - order_of_magnitude
			format_string = "%." + "%i" % nb_decimals + "f"
			self.chi_2_text.SetLabel(format_string % chi_2)
		if norm_gradient:
			order_of_magnitude = int(math.floor(math.log10(norm_gradient)))
		else:
			order_of_magnitude = 0
		if order_of_magnitude > 5 or order_of_magnitude < 0:
			self.norm_gradient_text.SetLabel("%.6e" % norm_gradient)
		else:
			nb_decimals = 6 - order_of_magnitude
			format_string = "%." + "%i" % nb_decimals + "f"
			self.norm_gradient_text.SetLabel(format_string % norm_gradient)
		self.nb_front_layers_text.SetLabel("%i" % self.optimization.get_nb_front_layers())
		self.nb_back_layers_text.SetLabel("%i" % self.optimization.get_nb_back_layers())



########################################################################
#                                                                      #
# optimization_needles_dialog                                          #
#                                                                      #
########################################################################
class optimization_needles_dialog(optimization_refinement_dialog):
	"""Dialog for the needle method"""
	
	title = "Needles / Refinement"
	specific_save_name = "Save dMF"
	optimization_class = optimization_needles.optimization_needles
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent             the dialog's parent;
		  filter             the filter being optimized;
		  targets            the targets."""
		
		# Remember some values to know if it is necessary to update the
		# dialog.
		self.last_automatic = None
		self.last_can_add_needles = None
		self.last_min_thickness = None
		self.last_just_added_needles = None
		
		optimization_refinement_dialog.__init__(self, parent, filter, targets)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		This methods adds a target plot, color target boxes, an index
		profile plot, text information about the optimization, and needle
		method specific buttons and controls to the dialog."""
		
		optimization_refinement_dialog.add_content(self)
		
		# Create a check box for the automatic mode.
		self.automatic_checkbox = wx.CheckBox(self, -1, "Au&tomatic")
		self.Bind(wx.EVT_CHECKBOX, self.on_automatic_checkbox, self.automatic_checkbox)
		
		# Create a button for the addition of needles.
		self.add_needles_button = wx.Button(self, -1, "&Add")
		self.Bind(wx.EVT_BUTTON, self.on_add_needles, self.add_needles_button)
		
		# A box for the number of needles.
		self.nb_needles_box = wx.TextCtrl(self, -1, "", size = (50, -1), style = wx.TE_PROCESS_ENTER, validator = int_validator(1, None))
		self.nb_needles_box.Bind(wx.EVT_TEXT_ENTER, self.on_nb_needles)
		self.nb_needles_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_needles)
		
		# Create a button for the elimination of thin layers.
		self.remove_layers_button = wx.Button(self, -1, "&Remove layers thinner than")
		self.Bind(wx.EVT_BUTTON, self.on_remove_layers, self.remove_layers_button)
		
		# A box for the thickness of layers to remove.
		self.min_thickness_box = wx.TextCtrl(self, -1, "", size = (50, -1), style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None))
		self.min_thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_min_thickness)
		self.min_thickness_box.Bind(wx.EVT_KILL_FOCUS, self.on_min_thickness)
		
		# Make a window to select the needle materials. On Windows, we use
		# PopupTransientWindow
		import platform
		if platform.system() == "Windows":
			# As of wxPython 3.0.2, controls in PopupTransientWindows do not
			# receive clicks. This is why we must create this derived class.
			class myPopupTransientWindow(wx.PopupTransientWindow):
				
				def __init__(s, parent):
					wx.PopupTransientWindow.__init__(s, parent, wx.SIMPLE_BORDER)
				
				def ProcessLeftDown(s, event):
					# Get item number.
					position = event.GetPosition()
					item = self.needle_material_box.HitTest(position)
					
					# If position is outside of box, return immediatly.
					if item < 0:
						return False
					
					# Toggle selection.
					if self.needle_material_box.IsChecked(item):
						self.needle_material_box.Check(item, False)
					else:
						self.needle_material_box.Check(item, True)
					
					# Generate and post event
					event = wx.CommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.needle_material_box.GetId())
					event.SetInt(item)
					wx.PostEvent(self.needle_material_box.GetEventHandler(), event)
					
					return True
		
		# On OS X and some Linux distributions, there are various issues
		# with PopupTransientWindow and we use a regular dialog instead.
		else:
			class myPopupTransientWindow(wx.Dialog):
				
				def __init__(s, parent):
					wx.Dialog.__init__(s, self, -1, "Needle materials", style = wx.CAPTION)
					self.has_been_used_already = False
				
				def Position(s, *args):
					pass
				
				def Popup(s):
					# The first time the dialog is used, add the OK button and
					# bind EVT_CHECKLISTBOX events.
					if not self.has_been_used_already:
						button_sizer = s.CreateButtonSizer(wx.OK)
						sizer = self.material_popup_window.GetSizer()
						sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 10)
						sizer.Fit(s)
						s.Bind(wx.EVT_CHECKLISTBOX, self.on_needle_material_box, self.needle_material_box)
						self.has_been_used_already = True
					
					s.CenterOnParent()
					s.ShowModal()
		
		self.material_popup_window = myPopupTransientWindow(self)
		
		material_popup_window_sizer = wx.BoxSizer(wx.VERTICAL)
		self.material_popup_window.SetSizer(material_popup_window_sizer)
		
		# Make a list of regular materials. First get a list of all
		# materials and remove those wich are mixtures. This requires the
		# reading of all material files and might slow down the software.
		material_catalog = self.filter.get_material_catalog()
		material_names = material_catalog.get_material_names()
		self.material_choices = []
		for material_name in material_names:
			try:
				if material_catalog.get_material(material_name).get_kind() == MATERIAL_REGULAR:
					self.material_choices.append(material_name)
			except materials.material_error:
				pass
		
		# Make a check list box to select the needle materials.
		self.needle_material_box = wx.CheckListBox(self.material_popup_window, -1, size = (150, 250), choices = self.material_choices)
		self.Bind(wx.EVT_CHECKLISTBOX, self.on_needle_material_box, self.needle_material_box)
		
		# Add the check list box to the popup window.
		material_popup_window_sizer.Add(self.needle_material_box, 0)
		material_popup_window_sizer.Fit(self.material_popup_window)
		
		# And make a button to call the popup window.
		self.materials_button = wx.Button(self, -1, "Select materials")
		self.Bind(wx.EVT_BUTTON, self.on_show_material_popup_window, self.materials_button)
		
		# Set default values.
		self.nb_needles_box.SetValue("%i" % self.optimization.get_nb_needles())
		self.min_thickness_box.SetValue("%.1f" % self.optimization.get_min_thickness())
		
		# And check the materials used for needles.
		used_materials = self.optimization.get_needle_materials()
		for material in used_materials:
			self.needle_material_box.Check(self.material_choices.index(material))
		
		# Add them to the window.
		needles_sizer = wx.BoxSizer(wx.HORIZONTAL)
		needles_sizer.Add(self.automatic_checkbox, 0, wx.ALIGN_CENTER_VERTICAL)
		needles_sizer.Add(self.add_needles_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		needles_sizer.Add(self.nb_needles_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		needles_sizer.Add(wx.StaticText(self, -1, "needles"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		needles_sizer.Add(self.remove_layers_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		needles_sizer.Add(self.min_thickness_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		needles_sizer.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		needles_sizer.Add(self.materials_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		self.main_sizer.Add(needles_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
	
	
	######################################################################
	#                                                                    #
	# on_automatic_checkbox          	                                   #
	#                                                                    #
	######################################################################
	def on_automatic_checkbox(self, event):
		"""Handle checkbox events for the automatic checkbox
		
		This method takes a single argument:
		  event              the event.
		
		It changes the automatic mode of the optimization method."""
		
		self.optimization.set_automatic_mode(self.automatic_checkbox.GetValue())
		
		self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_nb_needles                 	                                   #
	#                                                                    #
	######################################################################
	def on_nb_needles(self, event):
		"""Handle text events for the number of needles box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the number of needles to add and
		updates the dialog."""
		
		if self.nb_needles_box.GetValidator().Validate(self.nb_needles_box):
			self.optimization.set_nb_needles(int(self.nb_needles_box.GetValue()))
			
			self.update_(self.optimization.get_working(), self.optimization.get_status())
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_min_thickness                                                   #
	#                                                                    #
	######################################################################
	def on_min_thickness(self, event):
		"""Handle text events for the minimal thickness box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the minimal thickness and updates
		the dialog."""
		
		if self.min_thickness_box.GetValidator().Validate(self.min_thickness_box):
			self.optimization.set_min_thickness(float(self.min_thickness_box.GetValue()))
			
			self.update_(self.optimization.get_working(), self.optimization.get_status())
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_show_material_popup_window                                      #
	#                                                                    #
	######################################################################
	def on_show_material_popup_window(self, event):
		"""Handle button events for the needle material button
		
		This method takes a single argument:
		  event              the event.
		
		It shows a popup window to allow the user to choose the needle
		materials."""
		
		if self.material_popup_window.IsShown():
			self.material_popup_window.Hide()
		
		else:
			button = event.GetEventObject()
			position = button.ClientToScreen((0,0))
			button_size =  button.GetSize()
			popup_window_size = self.material_popup_window.GetSize()
			
			self.material_popup_window.Position(position, (0, button_size[1]))
			self.material_popup_window.Popup()
	
	
	######################################################################
	#                                                                    #
	# on_needle_material_box                                             #
	#                                                                    #
	######################################################################
	def on_needle_material_box(self, event):
		"""Handle check box events for the needle material boxes
		
		This method takes a single argument:
		  event              the event.
		
		It updates the list of materials for the needles and updates the
		dialog."""
		
		index = event.GetSelection()
		material_name = self.needle_material_box.GetString(index)
		if self.needle_material_box.IsChecked(index):
			self.optimization.add_needle_materials([material_name])
		else:
			self.optimization.remove_needle_materials([material_name])
		
		self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_add_needles                                                     #
	#                                                                    #
	######################################################################
	def on_add_needles(self, event):
		"""Handle button events for the add needle button
		
		This method takes a single argument:
		  event              the event.
		
		It calls the optimization class add needle method in a new thread."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.add_needles)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_remove_layers                                                   #
	#                                                                    #
	######################################################################
	def on_remove_layers(self, event):
		"""Handle button events for the add needle button
		
		This method takes a single argument:
		  event              the event.
		
		It calls the optimization class remove layers method in a new
		thread."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.remove_thin_layers)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# disable_all_buttons                                                #
	#                                                                    #
	######################################################################
	def disable_all_buttons(self):
		"""Disable all the buttons
		
		Call this method before starting an operation in another thread
		to avoid problems in the very short time between the moment the
		button is pressed and the moment the dialog is updated. This method
		is NOT thread safe."""
		
		optimization_refinement_dialog.disable_all_buttons(self)
		
		self.automatic_checkbox.Disable()
		self.add_needles_button.Disable()
		self.remove_layers_button.Disable()
		self.nb_needles_box.Disable()
		self.min_thickness_box.Disable()
		self.materials_button.Disable()
		if config.POWER_USER:
			self.specific_save_button.Disable()
		
		# Force the immediate redraw of the window without waiting for the
		# return to the event loop.
		self.Update()
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, working, status):
		"""Update the dialog
		
		This method is NOT thread safe. If you want to update the dialog
		from another thread, use update instead.
		
		It takes 2 arguments:
		  working    a boolean indicating if the optimization is currently
		             working;
		  status     the status of the optimization."""
		
		optimization_refinement_dialog.update_(self, working, status)
		
		automatic = self.optimization.get_automatic_mode()
		can_add_needles = self.optimization.get_can_add_needles()
		min_thickness = self.optimization.get_min_thickness()
		just_added_needles = self.optimization.get_just_added_needles()
		
		# If the last operation was the addition of needles, show dMF and
		# the needles.
		if just_added_needles and not self.last_just_added_needles:
			self.last_update_time = time.clock()
			
			depth, dMF_profile, needle_positions, needle_values = self.optimization.get_dMF_profile()
			selected_needles = self.optimization.get_selected_needles()
			scaled_dMF_profile = copy.deepcopy(dMF_profile)
			scaled_needle_values = needle_values[:]
			
			# Remember how many needles were added.
			self.nb_added_needles = len(selected_needles)
			
			# Scale the needles.
			dummy, left, bottom, right, top = self.index_profile_plot.get_axes()
			abs_maximum = 0.0
			for i_material in range(len(scaled_dMF_profile)):
				for i_layer in range(len(scaled_dMF_profile[i_material])):
					for i_pos in range(len(scaled_dMF_profile[i_material][i_layer])):
						abs_scaled_dMF = abs(scaled_dMF_profile[i_material][i_layer][i_pos])
						if abs_scaled_dMF > abs_maximum:
							abs_maximum = abs_scaled_dMF
			if abs_maximum == 0.0:
				scale = 1.0
			else:
				scale = 0.475 * (top-bottom) / abs_maximum
			shift = 0.5*(top+bottom)
			for i_material in range(len(scaled_dMF_profile)):
				for i_layer in range(len(scaled_dMF_profile[i_material])):
					for i_pos in range(len(scaled_dMF_profile[i_material][i_layer])):
						scaled_dMF_profile[i_material][i_layer][i_pos] *= scale
						scaled_dMF_profile[i_material][i_layer][i_pos] += shift
			for i_needle in selected_needles:
				scaled_needle_values[i_needle] *= scale
				scaled_needle_values[i_needle] += shift
			
			for i_material in range(len(dMF_profile)):
				curve = plot_curve_segmented(depth, scaled_dMF_profile[i_material])
				self.index_profile_plot.add_curve(curve)
			
			for i_needle in selected_needles:
				curve = plot_curve([needle_positions[i_needle], needle_positions[i_needle]], [shift, scaled_needle_values[i_needle]])
				self.index_profile_plot.add_curve(curve)
		
		if working is not self.last_working or status is not self.last_status or can_add_needles is not self.last_can_add_needles or automatic is not self.last_automatic or min_thickness != self.last_min_thickness:
			
			# The automatic checkbox is always available.
			self.automatic_checkbox.Enable()
			
			# During fitting, disable all buttons and boxes.
			if working:
				self.add_needles_button.Disable()
				self.remove_layers_button.Disable()
				self.nb_needles_box.Disable()
				self.min_thickness_box.Disable()
				self.materials_button.Disable()
				if config.POWER_USER:
					self.specific_save_button.Disable()
			
			# If it is possible to add needles, but we have not just added
			# some, enable them, except in automatic mode.
			elif can_add_needles and (not just_added_needles or not self.optimization.get_could_add_needles_on_last_attempt()):
				
				if automatic:
					self.add_needles_button.Disable()
					self.remove_layers_button.Disable()
					
					# The refinement dialog box has disabled the go button; enable it.
					self.go_button.Enable()
				else:
					self.add_needles_button.Enable()
					self.remove_layers_button.Enable()
				self.nb_needles_box.Enable()
				self.min_thickness_box.Enable()
				self.materials_button.Enable()
				if config.POWER_USER:
					self.specific_save_button.Disable()
				
				# Do not set the Focus when the material popup window is shown
				# because the lost of focus would cause it to close.
				if self.material_popup_window.IsShown():
					pass
				# When work stops, try to intelligently select a button. In
				# automatic mode, select the go button. In manual mode, if the
				# fit is still improving select the go button. Otherwise,
				# select the add needles button.
				elif automatic:
					if working is not self.last_working:
						self.go_button.SetFocus()
				else:
					if working is not self.last_working:
						if status == Levenberg_Marquardt.IMPROVING:
							self.go_button.SetFocus()
						else:
							self.add_needles_button.SetFocus()
			
			# Otherwise, disable the addition of needles.
			else:
				self.add_needles_button.Disable()
				self.nb_needles_box.Disable()
				if automatic:
					self.remove_layers_button.Disable()
				else:
					self.remove_layers_button.Enable()
				self.min_thickness_box.Enable()
				self.materials_button.Enable()
				if config.POWER_USER:
					if just_added_needles:
						self.specific_save_button.Enable()
					else:
						self.specific_save_button.Disable()
				
				# Do not set the Focus when the material popup window is shown
				# because the lost of focus would cause it to close.
				if self.material_popup_window.IsShown():
					pass
				# When work stops, try to intelligently select a button. If the
				# fit is still improving select the go button. Otherwise,
				# select the ok button. 
				elif status == Levenberg_Marquardt.IMPROVING:
					if working is not self.last_working:
						self.go_button.SetFocus()
				else:
					if working is not self.last_working:
						self.ok_button.SetFocus()
			
			self.last_automatic = automatic
			self.last_can_add_needles = can_add_needles
			self.last_min_thickness = min_thickness
		
		self.last_just_added_needles = just_added_needles



########################################################################
#                                                                      #
# optimization_steps_dialog                                            #
#                                                                      #
########################################################################
class optimization_steps_dialog(optimization_refinement_dialog):
	"""Dialog for the step method"""
	
	title = "Steps / Refinement"
	specific_save_name = "Save dMF"
	optimization_class = optimization_steps.optimization_steps
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent             the dialog's parent;
		  filter             the filter being optimized;
		  targets            the targets."""
		
		# Remember some values to know if it is necessary to update the
		# dialog.
		self.last_automatic = None
		self.last_can_add_steps = None
		self.last_min_thickness = None
		self.last_min_delta_n = None
		self.last_just_added_steps = None
		
		optimization_refinement_dialog.__init__(self, parent, filter, targets)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		This methods adds a target plot, color target boxes, an index
		profile plot, text information about the optimization, and step
		method specific buttons and controls to the dialog."""
		
		optimization_refinement_dialog.add_content(self)
		
		self.index_profile_plot.set_legend_position(TOP)
		
		# Create a check box for the automatic mode.
		self.automatic_checkbox = wx.CheckBox(self, -1, "Au&tomatic")
		self.Bind(wx.EVT_CHECKBOX, self.on_automatic_checkbox, self.automatic_checkbox)
		
		# Create a button for the addition of steps.
		self.add_steps_button = wx.Button(self, -1, "&Add")
		self.Bind(wx.EVT_BUTTON, self.on_add_steps, self.add_steps_button)
		
		# A box for the number of steps.
		self.nb_steps_box = wx.TextCtrl(self, -1, "", size = (50, -1), validator = int_validator(1, None))
		self.nb_steps_box.Bind(wx.EVT_TEXT_ENTER, self.on_nb_steps)
		self.nb_steps_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_steps)
		
		# Create a button for the elimination of thin layers.
		self.remove_layers_button = wx.Button(self, -1, "&Remove layers thinner than")
		self.Bind(wx.EVT_BUTTON, self.on_remove_layers, self.remove_layers_button)
		
		# A box for the thickness of layers to remove.
		self.min_thickness_box = wx.TextCtrl(self, -1, "", size = (50, -1), validator = float_validator(0.0, None))
		self.min_thickness_box.Bind(wx.EVT_TEXT_ENTER, self.on_min_thickness)
		self.min_thickness_box.Bind(wx.EVT_KILL_FOCUS, self.on_min_thickness)
		
		# A box for the thickness of layers to remove.
		self.min_delta_n_box = wx.TextCtrl(self, -1, "", size = (50, -1), validator = float_validator(0.0, None))
		self.min_delta_n_box.Bind(wx.EVT_TEXT_ENTER, self.on_min_delta_n)
		self.min_delta_n_box.Bind(wx.EVT_KILL_FOCUS, self.on_min_delta_n)
		
		# Set default values.
		self.nb_steps_box.SetValue("%i" % self.optimization.get_nb_steps())
		self.min_thickness_box.SetValue("%.1f" % self.optimization.get_min_thickness())
		self.min_delta_n_box.SetValue("%.1f" % self.optimization.get_min_delta_n())
		
		# Add them to the window.
		steps_sizer = wx.BoxSizer(wx.HORIZONTAL)
		steps_sizer.Add(self.automatic_checkbox, 0, wx.ALIGN_CENTER_VERTICAL)
		steps_sizer.Add(self.add_steps_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		steps_sizer.Add(self.nb_steps_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		steps_sizer.Add(wx.StaticText(self, -1, "steps"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		steps_sizer.Add(self.remove_layers_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		steps_sizer.Add(self.min_thickness_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		steps_sizer.Add(wx.StaticText(self, -1, "nm or an index difference smaller than"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		steps_sizer.Add(self.min_delta_n_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.main_sizer.Add(steps_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
	
	
	######################################################################
	#                                                                    #
	# on_automatic_checkbox          	                                   #
	#                                                                    #
	######################################################################
	def on_automatic_checkbox(self, event):
		"""Handle checkbox events for the automatic checkbox
		
		This method takes a single argument:
		  event              the event.
		
		It changes the automatic mode of the optimization method."""
		
		self.optimization.set_automatic_mode(self.automatic_checkbox.GetValue())
		
		self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_nb_steps                 	                                     #
	#                                                                    #
	######################################################################
	def on_nb_steps(self, event):
		"""Handle text events for the number of steps box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the number of steps to add and
		updates the dialog."""
		
		if self.nb_steps_box.GetValidator().Validate(self.nb_steps_box):
			self.optimization.set_nb_steps(int(self.nb_steps_box.GetValue()))
			
			self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_min_thickness                                                   #
	#                                                                    #
	######################################################################
	def on_min_thickness(self, event):
		"""Handle text events for the minimal thickness box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the minimal thickness and updates
		the dialog."""
		
		if self.min_thickness_box.GetValidator().Validate(self.min_thickness_box):
			self.optimization.set_min_thickness(float(self.min_thickness_box.GetValue()))
			
			self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_min_delta_n                                                     #
	#                                                                    #
	######################################################################
	def on_min_delta_n(self, event):
		"""Handle text events for the minimal index difference box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the minimal index difference and
		updates the dialog."""
		
		if self.min_delta_n_box.GetValidator().Validate(self.min_delta_n_box):
			self.optimization.set_min_delta_n(float(self.min_delta_n_box.GetValue()))
			
			self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_add_steps                                                       #
	#                                                                    #
	######################################################################
	def on_add_steps(self, event):
		"""Handle button events for the add step button
		
		This method takes a single argument:
		  event              the event.
		
		It calls the optimization class add step method in a new thread."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.add_steps)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_remove_layers                                                   #
	#                                                                    #
	######################################################################
	def on_remove_layers(self, event):
		"""Handle button events for the add needle button
		
		This method takes a single argument:
		  event              the event.
		
		It calls the optimization class remove layers method in a new
		thread."""
		
		self.disable_all_buttons()
		
		thread = threading.Thread(target = self.optimization.remove_thin_layers)
		thread.start()
	
	
	######################################################################
	#                                                                    #
	# disable_all_buttons                                                #
	#                                                                    #
	######################################################################
	def disable_all_buttons(self):
		"""Disable all the buttons
		
		Call this method before starting an operation in another thread
		to avoid problems in the very short time between the moment the
		button is pressed and the moment the dialog is updated. This method
		is NOT thread safe."""
		
		optimization_refinement_dialog.disable_all_buttons(self)
		
		self.automatic_checkbox.Disable()
		self.add_steps_button.Disable()
		self.remove_layers_button.Disable()
		self.nb_steps_box.Disable()
		self.min_thickness_box.Disable()
		self.min_delta_n_box.Disable()
		if config.POWER_USER:
			self.specific_save_button.Disable()
		
		# Force the immediate redraw of the window without waiting for the
		# return to the event loop.
		self.Update()
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, working, status):
		"""Update the dialog
		
		This method is NOT thread safe. If you want to update the dialog
		from another thread, use update instead.
		
		It takes 2 arguments:
		  working    a boolean indicating if the optimization is currently
		             working;
		  status     the status of the optimization."""
		
		optimization_refinement_dialog.update_(self, working, status)
		
		automatic = self.optimization.get_automatic_mode()
		can_add_steps = self.optimization.get_can_add_steps()
		min_thickness = self.optimization.get_min_thickness()
		min_delta_n = self.optimization.get_min_delta_n()
		just_added_steps = self.optimization.get_just_added_steps()
		
		if just_added_steps and not self.last_just_added_steps:
			self.last_update_time = time.clock()
			
			depth, dMF_profile_up, dMF_profile_down, step_up_positions, step_up_values, step_down_positions, step_down_values = self.optimization.get_dMF_profile()
			selected_steps_up, selected_steps_down = self.optimization.get_selected_steps()
			
			scaled_dMF_profile_up = copy.deepcopy(dMF_profile_up)
			scaled_dMF_profile_down = copy.deepcopy(dMF_profile_down)
			scaled_step_up_values = step_up_values[:]
			scaled_step_down_values = step_down_values[:]
			
			# Scale the steps.
			dummy, left, bottom, right, top = self.index_profile_plot.get_axes()
			abs_maximum = 0.0
			for i_layer in range(len(dMF_profile_up)):
				for i_pos in range(len(dMF_profile_up[i_layer])):
					abs_dMF_up = abs(dMF_profile_up[i_layer][i_pos])
					abs_dMF_down = abs(dMF_profile_down[i_layer][i_pos])
					if abs_dMF_up > abs_maximum:
						abs_maximum = abs_dMF_up
					if abs_dMF_down > abs_maximum:
						abs_maximum = abs_dMF_down
			if abs_maximum == 0.0:
				scale = 1.0
			else:
				scale = 0.95*(top-bottom) / (2.0*abs_maximum)
			shift = 0.5*(top+bottom)
			for i_layer in range(len(dMF_profile_up)):
				for i_pos in range(len(dMF_profile_up[i_layer])):
					scaled_dMF_profile_up[i_layer][i_pos] *= scale
					scaled_dMF_profile_up[i_layer][i_pos] += shift
					scaled_dMF_profile_down[i_layer][i_pos] *= scale
					scaled_dMF_profile_down[i_layer][i_pos] += shift
			for i_step in range(len(step_up_values)):
				scaled_step_up_values[i_step] *= scale
				scaled_step_up_values[i_step] += shift
			for i_step in range(len(step_down_values)):
				scaled_step_down_values[i_step] *= scale
				scaled_step_down_values[i_step] += shift
			
			curve = plot_curve_segmented(depth, scaled_dMF_profile_up, name = "up")
			curve_nb_1 = self.index_profile_plot.add_curve(curve)
			curve = plot_curve_segmented(depth, scaled_dMF_profile_down, name = "down")
			curve_nb_2 = self.index_profile_plot.add_curve(curve)
			
			for i_step in range(len(selected_steps_up)):
				curve = plot_curve([step_up_positions[selected_steps_up[i_step]], step_up_positions[selected_steps_up[i_step]]], [shift, scaled_step_up_values[selected_steps_up[i_step]]])
				self.index_profile_plot.add_curve(curve)
			for i_step in range(len(selected_steps_down)):
				curve = plot_curve([step_down_positions[selected_steps_down[i_step]], step_down_positions[selected_steps_down[i_step]]], [shift, scaled_step_down_values[selected_steps_down[i_step]]])
				self.index_profile_plot.add_curve(curve)
		
		if working is not self.last_working or status is not self.last_status or can_add_steps is not self.last_can_add_steps or automatic is not self.last_automatic or min_thickness != self.last_min_thickness or min_delta_n != self.last_min_delta_n:
			
			# The automatic checkbox is always available.
			self.automatic_checkbox.Enable()
			
			# During fitting, disable all buttons and boxes.
			if working:
				self.add_steps_button.Disable()
				self.remove_layers_button.Disable()
				self.nb_steps_box.Disable()
				self.min_thickness_box.Disable()
				self.min_delta_n_box.Disable()
				if config.POWER_USER:
					self.specific_save_button.Disable()
			
			# If it is possible to add steps, but we have not just added
			# some, enable them, except in automatic mode.
			elif can_add_steps and not just_added_steps:
				
				if automatic:
					self.add_steps_button.Disable()
					self.remove_layers_button.Disable()
					
					# The refinement dialog box has disabled the go button; enable it.
					self.go_button.Enable()
				else:
					self.add_steps_button.Enable()
					self.remove_layers_button.Enable()
				self.nb_steps_box.Enable()
				self.min_thickness_box.Enable()
				self.min_delta_n_box.Enable()
				if config.POWER_USER:
					self.specific_save_button.Disable()
				
				# When work stops, try to intelligently select a button. In
				# automatic mode, select the go button. In manual mode, if the
				# fit is still improving select the go button. Otherwise,
				# select the add steps button.
				if working is not self.last_working:
					if automatic:
						self.go_button.SetFocus()
					else:
						if status == Levenberg_Marquardt.IMPROVING:
							self.go_button.SetFocus()
						else:
							self.add_steps_button.SetFocus()
			
			# Otherwise, disable the addition of steps.
			else:
				self.add_steps_button.Disable()
				self.nb_steps_box.Disable()
				if automatic:
					self.remove_layers_button.Disable()
				else:
					self.remove_layers_button.Enable()
				self.min_thickness_box.Enable()
				self.min_delta_n_box.Enable()
				if config.POWER_USER:
					if just_added_steps:
						self.specific_save_button.Enable()
					else:
						self.specific_save_button.Disable()
				
				# When work stops, try to intelligently select a button. If the
				# fit is still improving select the go button. Otherwise,
				# select the ok button. 
				if working is not self.last_working:
					if status == Levenberg_Marquardt.IMPROVING:
						self.go_button.SetFocus()
					else:
						self.ok_button.SetFocus()
			
			self.last_automatic = automatic
			self.last_can_add_steps = can_add_steps
			self.last_min_thickness = min_thickness
			self.last_min_delta_n = min_delta_n
		
		self.last_just_added_steps = just_added_steps



########################################################################
#                                                                      #
# optimization_Fourier_dialog                                          #
#                                                                      #
########################################################################
class optimization_Fourier_dialog(optimization_dialog):
	"""Dialog for the Fourier transform method"""
	
	title = "Fourier Transform Method"
	specific_save_name = ""
	optimization_class = optimization_Fourier.optimization_Fourier
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, filter, targets):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent             the dialog's parent;
		  filter             the filter being optimized;
		  targets            the targets."""
		
		# Keep the value of the iteration locally in order to determine if
		# is has changed and if it is necessary to redraw the plots.
		self.iteration = -1
		
		optimization_dialog.__init__(self, parent, filter, targets)
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog
		
		This methods adds a target plot, an index profile plot, text
		information about the optimization and Fourier transform method
		specific controls to the dialog."""
		
		# If there is more than 1 target, indicate the only the first
		# reflection spectrum target is considered.
		if len(self.optimization.targets) > 1:
			warning = wx.StaticText(self, -1, "Warning: only the first normal incidence reflection spectrum target is used!")
			warning.SetForegroundColour("red")
			self.main_sizer.Add(warning, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.target_notebook =  wx.Notebook(self, size = (700, 230))
		
		# A plot for the spectrum.
		self.R_plot = plot(self.target_notebook)
		self.R_plot.set_xlabel("Wavelength (nm)")
		self.R_plot.set_ylabel("R")
		R_target_curve = plot_curve(self.optimization.wvls, self.optimization.R_target, style = plot_curve_style("Black", 1, "x", 5))
		self.R_plot.add_curve(R_target_curve)
		self.R_curve_nb = None
		
		self.target_notebook.AddPage(self.R_plot, "Reflection")
		
		if self.optimization.phi_target != None:
			self.phi_plot = plot(self.target_notebook)
			self.phi_plot.set_xlabel("Wavelength (nm)")
			self.phi_plot.set_ylabel("phi_r")
			phi_target_curve = plot_curve(self.optimization.wvls, self.optimization.phi_target, style = plot_curve_style("Black", 1, "x", 5))
			self.phi_plot.add_curve(phi_target_curve)
			self.phi_curve_nb = None
			
			self.target_notebook.AddPage(self.phi_plot, "Phase")
		
		# A plot for the index profile.
		self.index_profile_plot = plot(self, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.index_profile_plot.set_xlabel("Depth (nm)")
		self.index_profile_plot.set_ylabel("n")
		
		# Text for the status, the number of iterations and chi square, ...
		status_sizer = wx.BoxSizer(wx.HORIZONTAL)
		status_sizer.Add(wx.StaticText(self, -1, "Status: ", style = wx.ALIGN_LEFT), 0)
		self.status_text = wx.StaticText(self, -1, "%s" % "", style = wx.ALIGN_LEFT)
		status_sizer.Add(self.status_text, 0)
		iteration_sizer = wx.BoxSizer(wx.HORIZONTAL)
		iteration_sizer.Add(wx.StaticText(self, -1, "Iteration: ", style = wx.ALIGN_LEFT), 0)
		self.iteration_text = wx.StaticText(self, -1, "%i" % 0, style = wx.ALIGN_LEFT)
		iteration_sizer.Add(self.iteration_text, 0)
		chi_2_sizer = wx.BoxSizer(wx.HORIZONTAL)
		chi_2_sizer.Add(wx.StaticText(self, -1, "Chi square: ", style = wx.ALIGN_LEFT), 0)
		self.chi_2_text = wx.StaticText(self, -1, "%.6f" % 0.0, style = wx.ALIGN_LEFT)
		chi_2_sizer.Add(self.chi_2_text, 0)
		
		# Put the statistics in a sizer.
		statistic_sizer = wx.FlexGridSizer(2, 3, 5, 175)
		statistic_sizer.Add(status_sizer)
		statistic_sizer.Add(chi_2_sizer)
		statistic_sizer.Add((0,0))
		statistic_sizer.Add(iteration_sizer)
		statistic_sizer.Add((0,0))
		statistic_sizer.Add((0,0))
		
		# Make a list of Q functions.
		self.Q_function_choices = optimization_Fourier.Q_function_choices
		self.Q_function_descriptions = optimization_Fourier.Q_function_descriptions
		
		# Make a list of mixture materials. First get a list of all
		# materials and remove those wich are not mixtures. This requires the
		# reading of all material files and might slow down the software.
		material_catalog = self.filter.get_material_catalog()
		material_names = material_catalog.get_material_names()
		self.material_choices = []
		for material_name in material_names:
			try:
				if material_catalog.get_material(material_name).get_kind() == MATERIAL_MIXTURE:
					self.material_choices.append(material_name)
			except materials.material_error:
				pass
		
		# A choice for the material.
		self.material_choice = wx.Choice(self, -1, (-1, -1), choices = self.material_choices)
		self.Bind(wx.EVT_CHOICE, self.on_material_choice, self.material_choice)
		
		# A choice for the Q function.
		labels = [self.Q_function_choices[i] + " (%s)" % self.Q_function_descriptions[i] for i in range(len(self.Q_function_choices))]
		self.Q_function_choice = wx.Choice(self, -1, (-1, -1), choices = labels)
		self.Bind(wx.EVT_CHOICE, self.on_Q_function_choice, self.Q_function_choice)
		
		# A box for the optical thickness.
		self.OT_box = wx.TextCtrl(self, -1, "", style = wx.TE_PROCESS_ENTER, validator = float_validator(0.0, None, include_minimum = False))
		self.OT_box.Bind(wx.EVT_KILL_FOCUS, self.on_OT)
		
		# Add them to a sizer.
		Fourier_sizer = wx.BoxSizer(wx.HORIZONTAL)
		Fourier_sizer.Add(wx.StaticText(self, -1, "Material:"), 0, wx.ALIGN_CENTER_VERTICAL)
		Fourier_sizer.Add(self.material_choice, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		Fourier_sizer.Add(wx.StaticText(self, -1, "Q function:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		Fourier_sizer.Add(self.Q_function_choice, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		Fourier_sizer.Add(wx.StaticText(self, -1, "Optical thickness:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		Fourier_sizer.Add(self.OT_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		Fourier_sizer.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Put everything in the main sizer.
		self.main_sizer.Add(self.target_notebook, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(self.index_profile_plot, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(statistic_sizer, 0, wx.EXPAND|wx.ALL, 10)
		self.main_sizer.Add(Fourier_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
		
		# Set the values of the properties.
		material_name = self.optimization.get_material()
		Q_function = self.optimization.get_Q_function()
		OT = self.optimization.get_OT()
		self.material_choice.SetSelection(self.material_choices.index(material_name))
		self.Q_function_choice.SetSelection(self.Q_function_choices.index(Q_function))
		self.OT_box.SetValue("%s" % OT)
	
	
	######################################################################
	#                                                                    #
	# on_material_choice                                                 #
	#                                                                    #
	######################################################################
	def on_material_choice(self, event):
		"""Handle choice events for the material choice
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method what material was choosen and
		updates the dialog."""
		
		old_material = self.optimization.get_material()
		new_material = self.material_choices[self.material_choice.GetSelection()]
		
		if new_material != old_material:
			self.optimization.set_material(new_material)
			self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_Q_function_choice                                               #
	#                                                                    #
	######################################################################
	def on_Q_function_choice(self, event):
		"""Handle choice events for the Q choice
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method what Q function was choosen and
		updates the dialog."""
		
		old_Q_function = self.optimization.get_Q_function()
		new_Q_function = self.Q_function_choices[self.Q_function_choice.GetSelection()]
		
		if new_Q_function != old_Q_function:
			self.optimization.set_Q_function(new_Q_function)
			self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# on_OT                                                              #
	#                                                                    #
	######################################################################
	def on_OT(self, event):
		"""Handle text events for the OT box
		
		This method takes a single argument:
		  event              the event.
		
		It tells the optimization method the optical thickness that was
		entered and updates the dialog."""
		
		if self.OT_box.GetValidator().Validate(self.OT_box):
			old_OT = self.optimization.get_OT()
			new_OT = float(self.OT_box.GetValue())
			
			if new_OT != old_OT:
				self.optimization.set_OT(new_OT)
				
				self.update_(self.optimization.get_working(), self.optimization.get_status())
	
	
	######################################################################
	#                                                                    #
	# disable_all_buttons                                                #
	#                                                                    #
	######################################################################
	def disable_all_buttons(self):
		"""Disable all the buttons
		
		Call this method before starting an operation in another thread
		to avoid problems in the very short time between the moment the
		button is pressed and the moment the dialog is updated. This method
		is NOT thread safe."""
		
		optimization_dialog.disable_all_buttons(self)
		
		self.material_choice.Disable()
		self.Q_function_choice.Disable()
		self.OT_box.Disable()
		
		# Force the immediate redraw of the window without waiting for the
		# return to the event loop.
		self.Update()
	
	
	######################################################################
	#                                                                    #
	# update_                                                            #
	#                                                                    #
	######################################################################
	def update_(self, working, status):
		"""Update the dialog
		
		This method is NOT thread safe. If you want to update the dialog
		from another thread, use update instead.
		
		It takes 2 arguments:
		  working    a boolean indicating if the optimization is currently
		             working;
		  status     the status of the optimization."""
		
		optimization_dialog.update_(self, working, status)
		
		# If the iterations hasn't changed, it is not necessary to redraw
		# the plots.
		iteration = self.optimization.get_iteration()
		if iteration != self.iteration:
			thickness, index_profile = self.optimization.get_index_profile()
			design_curve = plot_curve(thickness, index_profile)
			self.index_profile_plot.reset(design_curve)
			
			wvls, R, phi = self.optimization.get_calculated_values()
			
			self.R_plot.begin_batch()
			if self.R_curve_nb is not None:
				self.R_plot.remove_curve(self.R_curve_nb)
			R_curve = plot_curve(wvls, R, style = plot_curve_style("Blue", 1, "x", 5))
			self.R_curve_nb = self.R_plot.add_curve(R_curve)
			self.R_plot.end_batch()
			
			if self.optimization.phi_target != None:
				self.phi_plot.begin_batch()
				if self.phi_curve_nb is not None:
					self.phi_plot.remove_curve(self.phi_curve_nb)
				phi_curve = plot_curve(wvls, phi, style = plot_curve_style("Blue", 1, "x", 5))
				self.phi_curve_nb = self.phi_plot.add_curve(phi_curve)
				self.phi_plot.end_batch()
		
		if iteration != self.iteration or working is not self.last_working or status != self.last_status:
			self.iteration = iteration
			chi_2 = self.optimization.get_chi_2()
			
			# Update the text.
			if status == Levenberg_Marquardt.IMPROVING:
				status_text = "improving"
			elif status == Levenberg_Marquardt.CHI_2_IS_OK:
				status_text = "chi square is OK"
			elif status == Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL:
				status_text = "chi square change is too small"
			elif status == Levenberg_Marquardt.DELTA_IS_TOO_SMALL:
				status_text = "impossible to improve chi square"
			else:
				status_text = ""
			self.status_text.SetLabel("%s" % status_text)
			self.iteration_text.SetLabel("%i" % iteration)
			if chi_2:
				order_of_magnitude = int(math.floor(math.log10(chi_2)))
			else:
				order_of_magnitude = 0
			if order_of_magnitude > 5 or order_of_magnitude < 0:
				self.chi_2_text.SetLabel("%.6e" % chi_2)
			else:
				nb_decimals = 6 - order_of_magnitude
				format_string = "%." + "%i" % nb_decimals + "f"
				self.chi_2_text.SetLabel(format_string % chi_2)
			
			# During fitting, disable modification of the parameters.
			if working:
				self.material_choice.Disable()
				self.Q_function_choice.Disable()
				self.OT_box.Disable()
			else:
				self.material_choice.Enable()
				self.Q_function_choice.Enable()
				self.OT_box.Enable()
			
		# The correlation button is not available in the Fourier transform
		# method.
		self.correlation_button.Disable()



########################################################################
#                                                                      #
# correlation_dialog                                                   #
#                                                                      #
########################################################################
class correlation_dialog(wx.Dialog):
	"""A dialog to show the correlation matrix"""
	
	title = "Correlation Matrix"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, optimization):
		"""Initialize the dialog
		
		This method takes 2 arguments:
		  parent             the dialog's parent;
		  optimization       an instance of the optimization class."""
		
		self.parent = parent
		self.optimization = optimization
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
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
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add content to the dialog"""
		
		# Get the parameters of the optimization and the correlation
		# matrix.
		parameters = self.optimization.get_parameters()
		correlation_matrix = self.optimization.get_correlation_matrix()
		nb_par = len(parameters)
		
		# Create the grid. It is necessary to specify the size because
		# auto layout does an horible job for grids.
		self.correlation_grid = wx.grid.Grid(self, -1, size = (500, 200), style = wx.VSCROLL|wx.HSCROLL|wx.SIMPLE_BORDER)
		self.correlation_grid.CreateGrid(nb_par, nb_par)
		
		# Set the row and column labels.
		for par in range(nb_par):
			self.correlation_grid.SetColSize(par, 65)
			layer_nb = parameters[par][1] + 1
			if parameters[par][0] == optimization_refinement.THICKNESS:
				col_label = "Thickness\n#%i" % layer_nb
				row_label = "Thickness #%i" % layer_nb
			elif parameters[par][0] == optimization_refinement.INDEX:
				col_label = "Index\n#%i" % layer_nb
				row_label = "Index #%i" % layer_nb
			self.correlation_grid.SetColLabelValue(par, col_label)
			self.correlation_grid.SetRowLabelValue(par, row_label)
		
		# Population the grid.
		for par_1 in range(nb_par):
			for par_2 in range(nb_par):
				correlation = correlation_matrix[par_1][par_2]
				self.correlation_grid.SetCellValue(par_1, par_2, "%6.4f" % correlation)
				self.correlation_grid.SetReadOnly(par_1, par_2)
				if par_1 != par_2:
					if abs(correlation) >= 0.99:
						self.correlation_grid.SetCellBackgroundColour(par_1, par_2, wx.NamedColour("RED"))
					elif abs(correlation) >= 0.90:
						self.correlation_grid.SetCellBackgroundColour(par_1, par_2, wx.NamedColour("YELLOW"))
		
		# Put the grid in the sizer.
		self.main_sizer.Add(self.correlation_grid, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add buttons to the dialog"""
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK), 0, wx.ALL, 10)
		
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
