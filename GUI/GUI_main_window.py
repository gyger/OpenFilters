# -*- coding: UTF-8 -*-

# GUI_main_window.py
# 
# The main window of the GUI of OpenFilters.
# 
# Copyright (c) 2001-2015 Stephane Larouche.
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



import sys
import os
import platform
import time
try:
	import threading
except ImportError:
	pass
import ConfigParser

import wx

from definitions import *
import config
import user_config
import main_directory
import about
import project
import targets
import optical_filter
import materials
import modules
import data_holder
import export
import abeles
import moremath

from GUI_filter_grid import filter_grid
from GUI_layer_grid import layer_grid
from GUI_target_grid import target_grid
from GUI_targets import reflection_target_dialog,\
                        transmission_target_dialog,\
                        absorption_target_dialog,\
                        reflection_spectrum_target_dialog,\
                        transmission_spectrum_target_dialog,\
                        absorption_spectrum_target_dialog,\
                        reflection_phase_target_dialog,\
                        transmission_phase_target_dialog,\
                        reflection_phase_spectrum_target_dialog,\
                        transmission_phase_spectrum_target_dialog,\
                        reflection_GD_target_dialog,\
                        transmission_GD_target_dialog,\
                        reflection_GD_spectrum_target_dialog,\
                        transmission_GD_spectrum_target_dialog,\
                        reflection_GDD_target_dialog,\
                        transmission_GDD_target_dialog,\
                        reflection_GDD_spectrum_target_dialog,\
                        transmission_GDD_spectrum_target_dialog,\
                        reflection_color_target_dialog,\
                        transmission_color_target_dialog,\
                        read_target_from_file_dialog
from GUI_filter_properties import filter_property_dialog
from GUI_layer_dialogs import simple_layer_dialog,\
                              import_layer_dialog,\
                              remove_layer_dialog,\
                              import_layer_error
from GUI_stack import stack_dialog
from GUI_calculate import calculate_reflection_dialog,\
                          calculate_transmission_dialog,\
                          calculate_absorption_dialog,\
                          calculate_ellipsometry_dialog,\
                          calculate_reflection_phase_dialog,\
                          calculate_transmission_phase_dialog,\
                          calculate_reflection_GD_dialog,\
                          calculate_transmission_GD_dialog,\
                          calculate_reflection_GDD_dialog,\
                          calculate_transmission_GDD_dialog,\
                          calculate_color_dialog,\
                          calculate_color_trajectory_dialog,\
                          calculate_admittance_dialog,\
                          calculate_circle_dialog,\
                          calculate_electric_field_dialog,\
                          calculate_reflection_monitoring_dialog,\
                          calculate_transmission_monitoring_dialog,\
                          calculate_ellipsometry_monitoring_dialog
from GUI_preproduction import random_errors_dialog
from GUI_optimization import optimization_Fourier_dialog,\
                             optimization_refinement_dialog,\
                             optimization_needles_dialog,\
                             optimization_steps_dialog
from GUI_materials import user_material_directory_dialog,\
                          manage_materials_dialog
from GUI_color import color_window
import GUI_plot



project_wildcard = "OpenFilters projects (*.ofp)|*.ofp|"\
                   "All files (*.*)|*.*"

# Constants that represent what to update when a update event is
# called.
UPDATE_ALL = sys.maxint
UPDATE_MENU = 1
UPDATE_STATUS_BAR = 2
UPDATE_CURSOR = 4
UPDATE_TARGET_CURVE = 8
UPDATE_FILTER = 16
UPDATE_GRIDS = 32



########################################################################
#                                                                      #
# update_event                                                         #
#                                                                      #
########################################################################

update_event_type = wx.NewEventType()

EVT_update = wx.PyEventBinder(update_event_type, 1)

class update_event(wx.PyCommandEvent):
	
	eventType = update_event_type
	
	def __init__(self, windowID, what = UPDATE_ALL):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		
		self.what = what
	
	def get_what(self):
		return self.what



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
# message_event                                                        #
#                                                                      #
########################################################################

message_event_type = wx.NewEventType()

EVT_message = wx.PyEventBinder(message_event_type, 1)

class message_event(wx.PyCommandEvent):
	
	eventType = message_event_type
	
	def __init__(self, windowID, message = "", title = "", icon = 0):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		
		self.message = message
		self.title = title
		self.icon = icon
	
	def get_message(self):
		return self.message
	
	def get_title(self):
		return self.title
	
	def get_icon(self):
		return self.icon



########################################################################
#                                                                      #
# data_event                                                           #
#                                                                      #
########################################################################

data_event_type = wx.NewEventType()

EVT_data = wx.PyEventBinder(data_event_type, 1)

class data_event(wx.PyCommandEvent):
	
	eventType = data_event_type
	
	def __init__(self, windowID, filter_nb, data):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		
		self.filter_nb = filter_nb
		self.data = data
	
	def get_filter_nb(self):
		return self.filter_nb
	
	def get_data(self):
		return self.data



########################################################################
#                                                                      #
# main_window                                                          #
#                                                                      #
########################################################################
class main_window(wx.Frame):
	"""Main window for the GUI of OpenFilters"""
	
	target_dialogs = {targets.R_TARGET: reflection_target_dialog,
	                  targets.T_TARGET: transmission_target_dialog,
	                  targets.A_TARGET: absorption_target_dialog,
	                  targets.R_SPECTRUM_TARGET: reflection_spectrum_target_dialog,
	                  targets.T_SPECTRUM_TARGET: transmission_spectrum_target_dialog,
	                  targets.A_SPECTRUM_TARGET: absorption_spectrum_target_dialog,
	                  targets.R_PHASE_TARGET: reflection_phase_target_dialog,
	                  targets.T_PHASE_TARGET: transmission_phase_target_dialog,
	                  targets.R_GD_TARGET: reflection_GD_target_dialog,
	                  targets.T_GD_TARGET: transmission_GD_target_dialog,
	                  targets.R_GDD_TARGET: reflection_GDD_target_dialog,
	                  targets.T_GDD_TARGET: transmission_GDD_target_dialog,
	                  targets.R_PHASE_SPECTRUM_TARGET: reflection_phase_spectrum_target_dialog,
	                  targets.T_PHASE_SPECTRUM_TARGET: transmission_phase_spectrum_target_dialog,
	                  targets.R_GD_SPECTRUM_TARGET: reflection_GD_spectrum_target_dialog,
	                  targets.T_GD_SPECTRUM_TARGET: transmission_GD_spectrum_target_dialog,
	                  targets.R_GDD_SPECTRUM_TARGET: reflection_GDD_spectrum_target_dialog,
	                  targets.T_GDD_SPECTRUM_TARGET: transmission_GDD_spectrum_target_dialog,
	                  targets.R_COLOR_TARGET: reflection_color_target_dialog,
	                  targets.T_COLOR_TARGET: transmission_color_target_dialog}
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent):
		"""Create the window
		
		This method takes a single argument:
		  parent             the windows parent."""
		
		self.load_configuration()
		
		# Initialization of the main window.
		wx.Frame.__init__(self, parent, -1, size = (640, 480), style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE)
		
		self.project = None
		self.project_filename = ""
		
		self.modifying = False
		self.calculating = False
		
		# Create the window layout.
		self.make_menus()
		self.make_window()
		self.make_status_bar()
		
		self.data = []
		
		self.selected_filter_nb = -1
		self.selected_target_nb = -1
		self.target_curve_nbs = [-1]*self.nb_pages
		
		# When running from the compiled version, the working directory at
		# startup is sometimes screwed up.
		directory = main_directory.get_main_directory()
		
		# Set the icon. If the program is interpreted or ran on a Mac,
		# read the icon from the ico file, if if was compiled with
		# py2exe, load the ressource.
		system = platform.system()
		if system == "Windows" and main_directory.main_is_frozen():
			executable_name = os.path.join(directory, "OpenFilters.exe")
			icon = wx.Icon(executable_name, wx.BITMAP_TYPE_ICO)
		else:
			icon_filename = os.path.join(directory, "OpenFilters.ico")
			icon = wx.Icon(icon_filename, wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)
		
		self.Bind(wx.EVT_CLOSE, self.on_quit)
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.Bind(EVT_update, self.on_update)
		self.Bind(EVT_progress, self.on_progress)
		self.Bind(EVT_data, self.on_data)
		self.Bind(EVT_message, self.on_message)
		
		self.Bind(GUI_plot.EVT_remove_curve, self.on_remove_curve)
		
		# The wx.MAXIMIZE style does not work when the software is
		# compiled.
		self.Maximize()
		
		self.update_title()
		self.update_recently_opened_projects()
		self.update_menu()
		self.update_status_bar()
		
		self.Show()
		
		# With wxPython 3.0 on Mac OS, there is a problem showing dialog
		# windows during the initialization of the application. Therefore,
		# we delay the call to those two methods by 500 ms.
		wx.CallLater(500, self.startup_checkup)
		wx.CallLater(500, self.import_modules)
	
	
	######################################################################
	#                                                                    #
	# load_configuration                                                 #
	#                                                                    #
	######################################################################
	def load_configuration(self):
		"""Load the configuration file and set some default values if they are absent"""
		
		self.user_config = user_config.get_user_config()
		
		if not self.user_config.has_section("GUI"):
			self.user_config.add_section("GUI")
		
		try:
			last_used_directory = self.user_config.get("GUI", "lastuseddirectory").decode('utf-8')
			os.chdir(last_used_directory)
		except (ConfigParser.NoOptionError, OSError):
			os.chdir(os.path.expanduser("~"))
		
		self.recently_opened_projects = []
		for i in range(config.NB_RECENTLY_OPENED_PROJECTS):
			try:
				self.recently_opened_projects.append(self.user_config.get("GUI", "recentlyopenedproject%i" % i).decode('utf-8'))
			except ConfigParser.NoOptionError:
				break
		
		if not self.user_config.has_section("Directories"):
			self.user_config.add_section("Directories")
		
		try:
			self.user_material_directory = self.user_config.get("Directories", "usermaterialdirectory").decode('utf-8')
		except (ConfigParser.NoOptionError):
			self.user_material_directory = None
	
	
	######################################################################
	#                                                                    #
	# save_configuration                                                 #
	#                                                                    #
	######################################################################
	def save_configuration(self):
		"""Save the user configuration"""
		
		self.user_config.set("GUI", "lastuseddirectory", os.getcwd().encode('utf-8'))
		
		for i in range(min(config.NB_RECENTLY_OPENED_PROJECTS, len(self.recently_opened_projects))):
			self.user_config.set("GUI", "recentlyopenedproject%i" % i, self.recently_opened_projects[i].encode('utf-8'))
		
		user_config.save_user_config()
	
	
	######################################################################
	#                                                                    #
	# make_menus                                                         #
	#                                                                    #
	######################################################################
	def make_menus(self):
		"""Create the menu bar and add it to the window"""
		
		menu_nb = 0
		
		# Create the menu bar
		self.main_menu = wx.MenuBar()
		
		# Make the File menu
		self.file_menu = wx.Menu()                                 
		self.file_menu_nb = menu_nb
		menu_nb += 1
		
		# Add the items of the menu
		self.new_project_ID = wx.NewId()
		self.file_menu.Append(self.new_project_ID, "&New Project\tCtrl+N", "Create a new project")
		self.Bind(wx.EVT_MENU, self.on_new_project, id = self.new_project_ID)
		
		self.open_project_ID = wx.NewId()
		self.file_menu.Append(self.open_project_ID, "&Open Project\tCtrl+O", "Open an existing project")
		self.Bind(wx.EVT_MENU, self.on_open_project, id = self.open_project_ID)
		
		self.close_project_ID = wx.NewId()
		self.file_menu.Append(self.close_project_ID, "&Close Project\tCtrl+W", "Close the project")
		self.Bind(wx.EVT_MENU, self.on_close_project, id = self.close_project_ID)
		
		self.file_menu.AppendSeparator()
		
		self.save_project_ID = wx.NewId()
		self.file_menu.Append(self.save_project_ID, "&Save Project\tCtrl+S", "Save the project")
		self.Bind(wx.EVT_MENU, self.on_save_project, id = self.save_project_ID)
		
		self.save_project_as_ID = wx.NewId()
		self.file_menu.Append(self.save_project_as_ID, "Save Project &As\tShift+Ctrl+S", "Save the project under a new name")
		self.Bind(wx.EVT_MENU, self.on_save_project_as, id = self.save_project_as_ID)
		
		self.revert_ID = wx.NewId()
		self.file_menu.Append(self.revert_ID, "Revert", "Revert the project to the last saved version")
		self.Bind(wx.EVT_MENU, self.on_revert, id = self.revert_ID)
		
		self.file_menu.AppendSeparator()
		
		self.recently_opened_project_IDs = [wx.NewId() for i in range(config.NB_RECENTLY_OPENED_PROJECTS)]
		for i in range(config.NB_RECENTLY_OPENED_PROJECTS):
			self.Bind(wx.EVT_MENU, self.on_open_project, id = self.recently_opened_project_IDs[i])
		
		self.recently_opened_project_starting_position = self.file_menu.GetMenuItemCount()
		
		self.file_menu.AppendSeparator()
		
		self.file_menu.Append(wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit the application")
		self.Bind(wx.EVT_MENU, self.on_quit, id = wx.ID_EXIT)
		
		# Add the File menu to the menu bar.
		self.main_menu.Append(self.file_menu, "&File")
		
		# Make the Project menu
		self.project_menu = wx.Menu()                                 
		self.project_menu_nb = menu_nb
		menu_nb += 1
		
		# Add the items of the menu
		self.add_filter_ID = wx.NewId()
		self.project_menu.Append(self.add_filter_ID, "&Add Filter\tCtrl+F", "Add a filter to the project")
		self.Bind(wx.EVT_MENU, self.on_add_filter, id = self.add_filter_ID)
		
		self.remove_filter_ID = wx.NewId()
		self.project_menu.Append(self.remove_filter_ID, "&Remove Filter", "Remove the selected filter from the project")
		self.Bind(wx.EVT_MENU, self.on_remove_filter, id = self.remove_filter_ID)
		
		self.modify_filter_ID = wx.NewId()
		self.project_menu.Append(self.modify_filter_ID, "&Modify Filter", "Modify the selected filter")
		self.Bind(wx.EVT_MENU, self.on_modify_filter, id = self.modify_filter_ID)
		
		self.copy_filter_ID = wx.NewId()
		self.project_menu.Append(self.copy_filter_ID, "&Copy Filter", "Make a copy of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_copy_filter, id = self.copy_filter_ID)
		
		self.project_menu.AppendSeparator()
		
		# Create a submenu for the addition of targets.
		self.add_target_menu = wx.Menu()
		self.add_target_menu_ID = wx.NewId()
		self.project_menu.AppendMenu(self.add_target_menu_ID, "Add &Target", self.add_target_menu)
		
		self.add_reflection_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_target_ID, "Add &Reflection Target\tCtrl+R", "Add a reflection target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_target_ID)
		
		self.add_transmission_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_target_ID, "Add &Transmission Target\tCtrl+T", "Add a transmission target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_target_ID)
		
		self.add_absorption_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_absorption_target_ID, "Add &Absorption Target", "Add a absorption target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_absorption_target_ID)
		
		self.add_target_menu.AppendSeparator()
		
		self.add_reflection_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_spectrum_target_ID, "Add Reflection &Spectrum Target\tShift+Ctrl+R", "Add a reflection spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_spectrum_target_ID)
		
		self.add_transmission_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_spectrum_target_ID, "Add Transmission &Spectrum Target\tShift+Ctrl+T", "Add a transmission spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_spectrum_target_ID)
		
		self.add_absorption_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_absorption_spectrum_target_ID, "Add Absorption &Spectrum Target", "Add a absorption spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_absorption_spectrum_target_ID)
		
		self.add_target_menu.AppendSeparator()
		
		self.add_reflection_phase_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_phase_target_ID, "Add Reflection &Phase Target", "Add a reflection phase target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_phase_target_ID)
		
		self.add_transmission_phase_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_phase_target_ID, "Add Transmission &Phase Target", "Add a transmission phase target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_phase_target_ID)
		
		self.add_reflection_GD_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_GD_target_ID, "Add Reflection &GD Target", "Add a reflection GD target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_GD_target_ID)
		
		self.add_transmission_GD_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_GD_target_ID, "Add Transmission &GD Target", "Add a transmission GD target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_GD_target_ID)
		
		self.add_reflection_GDD_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_GDD_target_ID, "Add Reflection &GDD Target", "Add a reflection GDD target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_GDD_target_ID)
		
		self.add_transmission_GDD_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_GDD_target_ID, "Add Transmission &GDD Target", "Add a transmission GDD target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_GDD_target_ID)
		
		self.add_target_menu.AppendSeparator()
		
		self.add_reflection_phase_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_phase_spectrum_target_ID, "Add Reflection &Phase Spectrum Target", "Add a reflection phase spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_phase_spectrum_target_ID)
		
		self.add_transmission_phase_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_phase_spectrum_target_ID, "Add Transmission &Phase Spectrum Target", "Add a transmission phase spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_phase_spectrum_target_ID)
		
		self.add_reflection_GD_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_GD_spectrum_target_ID, "Add Reflection &GD Spectrum Target", "Add a reflection GD spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_GD_spectrum_target_ID)
		
		self.add_transmission_GD_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_GD_spectrum_target_ID, "Add Transmission &GD Spectrum Target", "Add a transmission GD spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_GD_spectrum_target_ID)
		
		self.add_reflection_GDD_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_GDD_spectrum_target_ID, "Add Reflection &GDD Spectrum Target", "Add a reflection GDD spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_GDD_spectrum_target_ID)
		
		self.add_transmission_GDD_spectrum_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_GDD_spectrum_target_ID, "Add Transmission &GDD Spectrum Target", "Add a transmission GDD spectrum target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_GDD_spectrum_target_ID)
		
		self.add_target_menu.AppendSeparator()
		
		self.add_reflection_color_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_reflection_color_target_ID, "Add Reflection &Color Target", "Add a reflection color target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_reflection_color_target_ID)
		
		self.add_transmission_color_target_ID = wx.NewId()
		self.add_target_menu.Append(self.add_transmission_color_target_ID, "Add Transmission &Color Target", "Add a transmission color target to the project")
		self.Bind(wx.EVT_MENU, self.on_add_target, id = self.add_transmission_color_target_ID)
		
		self.add_target_menu.AppendSeparator()
		
		self.read_target_from_file_ID = wx.NewId()
		self.add_target_menu.Append(self.read_target_from_file_ID, "Read Target from &File", "Read a spectrum in a file and add it as a target to the project")
		self.Bind(wx.EVT_MENU, self.on_read_target_from_file, id = self.read_target_from_file_ID)
		
		self.remove_target_ID = wx.NewId()
		self.project_menu.Append(self.remove_target_ID, "&Remove Target", "Remove the selected target from the project")
		self.Bind(wx.EVT_MENU, self.on_remove_target, id = self.remove_target_ID)
		
		self.modify_target_ID = wx.NewId()
		self.project_menu.Append(self.modify_target_ID, "&Modify Target", "Modify the selected target")
		self.Bind(wx.EVT_MENU, self.on_modify_target, id = self.modify_target_ID)
		
		self.copy_target_ID = wx.NewId()
		self.project_menu.Append(self.copy_target_ID, "&Copy Target", "Make a copy of the selected target")
		self.Bind(wx.EVT_MENU, self.on_copy_target, id = self.copy_target_ID)
		
		# Add the Project menu to the menu bar.
		self.main_menu.Append(self.project_menu, "&Project")
		
		# Make the Filter menu
		self.filter_menu = wx.Menu()                                 
		self.filter_menu_nb = menu_nb
		menu_nb += 1
		
		# Add the items of the menu
		self.filter_properties_ID = wx.NewId()
		self.filter_menu.Append(self.filter_properties_ID, "&Properties\tAlt+Enter", "Show and modify the filter properties")
		self.Bind(wx.EVT_MENU, self.on_filter_properties, id = self.filter_properties_ID)
		
		self.filter_menu.AppendSeparator()
		
		self.add_layer_ID = wx.NewId()
		self.filter_menu.Append(self.add_layer_ID, "&Add layer\tAlt+Ins", "Add a layer to the selected filter")
		self.Bind(wx.EVT_MENU, self.on_add_layer, id = self.add_layer_ID)
		
		self.remove_layer_ID = wx.NewId()
		self.filter_menu.Append(self.remove_layer_ID, "&Remove layer\tAlt+Del", "Remove a layer from the selected filter")
		self.Bind(wx.EVT_MENU, self.on_remove_layer, id = self.remove_layer_ID)
		
		self.filter_menu.AppendSeparator()
		
		self.stack_formula_ID = wx.NewId()
		self.filter_menu.Append(self.stack_formula_ID, "&Stack Formula\tAlt+S", "Design the selected filter using a stack formula")
		self.Bind(wx.EVT_MENU, self.on_stack_formula, id = self.stack_formula_ID)
		
		self.filter_menu.AppendSeparator()
		
		self.import_layer_ID = wx.NewId()
		self.filter_menu.Append(self.import_layer_ID, "&Import layer", "Import the index profile of a layer from a text file")
		self.Bind(wx.EVT_MENU, self.on_import_layer, id = self.import_layer_ID)
		
		self.filter_menu.AppendSeparator()
		
		self.merge_layers_ID = wx.NewId()
		self.filter_menu.Append(self.merge_layers_ID, "&Merge layers", "Merge identical layers of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_merge_layers, id = self.merge_layers_ID)
		
		self.convert_layers_ID = wx.NewId()
		self.filter_menu.Append(self.convert_layers_ID, "&Convert mixture to steps", "Convert mixture layers into steps in the selected filter")
		self.Bind(wx.EVT_MENU, self.on_convert_layers, id = self.convert_layers_ID)
		
		self.swap_sides_ID = wx.NewId()
		self.filter_menu.Append(self.swap_sides_ID, "&Swap sides", "Swap sides of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_swap_sides, id = self.swap_sides_ID)
		
		self.filter_menu.AppendSeparator()
		
		# Create a submenu for modules.
		self.modules_menu = wx.Menu()
		self.modules_menu_ID = wx.NewId()
		self.filter_menu.AppendMenu(self.modules_menu_ID, "M&odules", self.modules_menu)
		
		self.filter_menu.AppendSeparator()
		
		self.export_front_index_profile_ID = wx.NewId()
		self.filter_menu.Append(self.export_front_index_profile_ID, "E&xport front index profile", "Export the front index profile of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_export_index_profile, id = self.export_front_index_profile_ID)
		
		self.export_back_index_profile_ID = wx.NewId()
		self.filter_menu.Append(self.export_back_index_profile_ID, "E&xport back index profile", "Export the back index profile of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_export_index_profile, id = self.export_back_index_profile_ID)
		
		# Add the Layers menu to the menu bar.
		self.main_menu.Append(self.filter_menu, "F&ilter")
		
		# Make the Analyse menu
		self.analyse_menu = wx.Menu()                                 
		self.analyse_menu_nb = menu_nb
		menu_nb += 1
		
		# Add the items of the menu
		self.calculate_reflection_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_reflection_ID, "Calculate &Reflection\tAlt+R", "Calculate the reflection spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_ID)
		
		self.calculate_transmission_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_transmission_ID, "Calculate &Transmission\tAlt+T", "Calculate the transmission spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_ID)
		
		self.calculate_absorption_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_absorption_ID, "Calculate &Absorption", "Calculate the absorption spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_absorption_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.calculate_reflection_phase_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_reflection_phase_ID, "Calculate Reflection &Phase", "Calculate the reflection phase spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_phase_ID)
		
		self.calculate_transmission_phase_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_transmission_phase_ID, "Calculate Transmission &Phase", "Calculate the transmission phase spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_phase_ID)
		
		self.calculate_reflection_GD_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_reflection_GD_ID, "Calculate Reflection &GD", "Calculate the reflection GD spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_GD_ID)
		
		self.calculate_transmission_GD_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_transmission_GD_ID, "Calculate Transmission &GD", "Calculate the transmission GD spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_GD_ID)
		
		self.calculate_reflection_GDD_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_reflection_GDD_ID, "Calculate Reflection GD&D", "Calculate the reflection GDD spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_GDD_ID)
		
		self.calculate_transmission_GDD_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_transmission_GDD_ID, "Calculate Transmission GD&D", "Calculate the transmission GDD spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_GDD_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.calculate_ellipsometry_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_ellipsometry_ID, "Calculate &Ellipsometry\tAlt+E", "Calculate the ellipsometric spectrum of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_ellipsometry_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.calculate_color_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_color_ID, "Calculate &Color\tAlt+C", "Calculate the color of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_color_ID)
		
		self.calculate_color_trajectory_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_color_trajectory_ID, "Calculate &Color Trajectory\tShift+Alt+C", "Calculate the color trajectory of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_color_trajectory_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.calculate_admittance_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_admittance_ID, "Calculate A&dmittance Diagram", "Calculate the admittance diagram of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_admittance_ID)
		
		self.calculate_circle_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_circle_ID, "Calculate C&ircle Diagram", "Calculate the circle diagram of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_circle_ID)
		
		self.calculate_electric_field_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_electric_field_ID, "Calculate Electric &Field", "Calculate the electric field distribution in the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_electric_field_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.calculate_reflection_monitoring_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_reflection_monitoring_ID, "Calculate Reflection &Monitoring\tShift+Alt+R", "Calculate the reflection monitoring curve of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_monitoring_ID)
		
		self.calculate_transmission_monitoring_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_transmission_monitoring_ID, "Calculate Transmission &Monitoring\tShift+Alt+T", "Calculate the transmission monitoring curve of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_monitoring_ID)
		
		self.calculate_ellipsometry_monitoring_ID = wx.NewId()
		self.analyse_menu.Append(self.calculate_ellipsometry_monitoring_ID, "Calculate Ellipsometric &Monitoring\tShift+Alt+E", "Calculate the ellipsometric monitoring curve of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_ellipsometry_monitoring_ID)
		
		self.analyse_menu.AppendSeparator()
		
		# Create a submenu for calculations in reverse direction.
		self.reverse_direction_menu = wx.Menu()
		self.reverse_direction_menu_ID = wx.NewId()
		self.analyse_menu.AppendMenu(self.reverse_direction_menu_ID, "Re&verse direction", self.reverse_direction_menu)
		
		self.calculate_reflection_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_reflection_reverse_ID, "Calculate &Reflection\tCtrl+Alt+R", "Calculate the reflection spectrum in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_reverse_ID)
		
		self.calculate_transmission_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_transmission_reverse_ID, "Calculate &Transmission\tCtrl+Alt+T", "Calculate the transmission spectrum in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_reverse_ID)
		
		self.calculate_absorption_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_absorption_reverse_ID, "Calculate &Absorption", "Calculate the absorption in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_absorption_reverse_ID)
		
		self.reverse_direction_menu.AppendSeparator()
		
		self.calculate_ellipsometry_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_ellipsometry_reverse_ID, "Calculate &Ellipsometry\tCtrl+Alt+E", "Calculate the ellipsometric spectrum in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_ellipsometry_reverse_ID)
		
		self.reverse_direction_menu.AppendSeparator()
		
		self.calculate_color_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_color_reverse_ID, "Calculate &Color\tCtrl+Alt+C", "Calculate the color in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_color_reverse_ID)
		
		self.calculate_color_trajectory_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_color_trajectory_reverse_ID, "Calculate &Color Trajectory\tCtrl+Shift+Alt+C", "Calculate the color trajectory in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_color_trajectory_reverse_ID)
		
		self.reverse_direction_menu.AppendSeparator()
		
		self.calculate_reflection_monitoring_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_reflection_monitoring_reverse_ID, "Calculate Reflection &Monitoring\tCtrl+Shift+Alt+R", "Calculate the reflection monitoring curve in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_reflection_monitoring_reverse_ID)
		
		self.calculate_transmission_monitoring_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_transmission_monitoring_reverse_ID, "Calculate Transmission &Monitoring\tCtrl+Shift+Alt+T", "Calculate the transmission monitoring curve in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_transmission_monitoring_reverse_ID)
		
		self.calculate_ellipsometry_monitoring_reverse_ID = wx.NewId()
		self.reverse_direction_menu.Append(self.calculate_ellipsometry_monitoring_reverse_ID, "Calculate Ellipsometric &Monitoring\tCtrl+Shift+Alt+E", "Calculate the ellipsometric monitoring curve in reverse direction of the selected filter")
		self.Bind(wx.EVT_MENU, self.on_calculate, id = self.calculate_ellipsometry_monitoring_reverse_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.show_targets_ID = wx.NewId()
		self.analyse_menu.Append(self.show_targets_ID, "Show targets", "Show the targets in the plots", wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.on_show_targets, id = self.show_targets_ID)
		
		self.show_all_results_ID = wx.NewId()
		self.analyse_menu.Append(self.show_all_results_ID, "Show all results", "Show the results for all filters", wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.on_show_all_results, id = self.show_all_results_ID)
		
		self.analyse_menu.AppendSeparator()
		
		self.export_results_as_text_ID = wx.NewId()
		self.analyse_menu.Append(self.export_results_as_text_ID, "Export results as text", "Export the results to a text file")
		self.Bind(wx.EVT_MENU, self.on_export_results_as_text, id = self.export_results_as_text_ID)
		
		self.export_results_as_figure_ID = wx.NewId()
		self.analyse_menu.Append(self.export_results_as_figure_ID, "Export results as figure", "Export the results to a figure file")
		self.Bind(wx.EVT_MENU, self.on_export_results_as_figure, id = self.export_results_as_figure_ID)
		
		# Add the Analyse menu to the menu bar.
		self.main_menu.Append(self.analyse_menu, "&Analyse")
		
		# Make the Optimize menu
		self.optimize_menu = wx.Menu()                                 
		self.optimize_menu_nb = menu_nb
		menu_nb += 1
		
		self.optimize_refinement_ID = wx.NewId()
		self.optimize_menu.Append(self.optimize_refinement_ID, "&Refine\tF1", "Refine the selected filter")
		self.Bind(wx.EVT_MENU, self.on_optimize, id = self.optimize_refinement_ID)
		
		self.optimize_needles_ID = wx.NewId()
		self.optimize_menu.Append(self.optimize_needles_ID, "&Needles / Refine\tF2", "Synthesize the selected filter with the needle method")
		self.Bind(wx.EVT_MENU, self.on_optimize, id = self.optimize_needles_ID)
		
		self.optimize_steps_ID = wx.NewId()
		self.optimize_menu.Append(self.optimize_steps_ID, "&Steps / Refine\tF3", "Synthesize the selected filter with the step method")
		self.Bind(wx.EVT_MENU, self.on_optimize, id = self.optimize_steps_ID)
		
		self.optimize_menu.AppendSeparator()
		
		self.design_Fourier_ID = wx.NewId()
		self.optimize_menu.Append(self.design_Fourier_ID, "&Fourier transform method\tF4", "Design the selected filter by the Fourier transform method")
		self.Bind(wx.EVT_MENU, self.on_optimize, id = self.design_Fourier_ID)
		
		# Add the Optimize menu to the menu bar.
		self.main_menu.Append(self.optimize_menu, "&Design/Optimize")
		
		# Make a Pre-production menu.
		self.preproduction_menu = wx.Menu()
		self.preproduction_menu_nb = menu_nb
		menu_nb += 1
		
		self.random_errors_ID = wx.NewId()
		self.preproduction_menu.Append(self.random_errors_ID, "Simulate &random errors\tAlt+F1", "Simulate the effect of random deposition errors")
		self.Bind(wx.EVT_MENU, self.on_random_errors, id = self.random_errors_ID)
		
		# Add the Pre-production menu to the menu bar.
		self.main_menu.Append(self.preproduction_menu, "Preprod&uction")
		
		# Make the Materials menu
		self.materials_menu = wx.Menu()                                 
		self.materials_menu_nb = menu_nb
		menu_nb += 1
		
		# Add the items of the menu
		self.manage_materials_ID = wx.NewId()
		self.materials_menu.Append(self.manage_materials_ID, "&Manage", "Manage the materials")
		self.Bind(wx.EVT_MENU, self.on_manage_materials, id = self.manage_materials_ID)
		
		self.change_user_material_directory_ID = wx.NewId()
		self.materials_menu.Append(self.change_user_material_directory_ID, "&Change user material directory", "Change the directory where user specific materials are saved.")
		self.Bind(wx.EVT_MENU, self.on_change_user_material_directory, id = self.change_user_material_directory_ID)
		
		# Add the Materials menu to the menu bar.
		self.main_menu.Append(self.materials_menu, "&Materials")
		
		# Make the About menu
		self.help_menu = wx.Menu()                                 
		self.help_menu_nb = menu_nb
		menu_nb += 1
		
		# Create a submenu for example projects.
		self.example_menu = wx.Menu()
		self.example_menu_ID = wx.NewId()
		self.help_menu.AppendMenu(self.example_menu_ID, "&Open Example Project", self.example_menu)
		
		# Add all examples to the submenu.
		example_directory = os.path.join(main_directory.get_main_directory(), "examples")
		examples = [file for file in os.listdir(example_directory) if os.path.isfile(os.path.join(example_directory, file)) and os.path.splitext(file)[1] == ".ofp"]
		
		self.open_example_IDs = {}
		for example in examples:
			filename = os.path.join(example_directory, example)
			try:
				comment = project.read_project(filename, self.get_material_catalog()).get_comment().splitlines()[0]
			except:
				pass
			else:
				ID = wx.NewId()
				self.open_example_IDs[ID] = filename
				self.example_menu.Append(ID, os.path.splitext(example)[0], comment)
				self.Bind(wx.EVT_MENU, self.on_open_project, id = ID)
		
		self.help_menu.AppendSeparator()
		
		# Add the items of the menu
		self.help_menu.Append(wx.ID_ABOUT, "About OpenFilters", "Display program version, copyright and license information")
		self.Bind(wx.EVT_MENU, self.on_about, id = wx.ID_ABOUT)
		
		# Add the About menu to the menu bar.
		self.main_menu.Append(self.help_menu, "&Help")
		
		if config.DEBUG:
			# Make the Debug menu.
			self.debug_menu = wx.Menu()                                 
			self.debug_menu_nb = menu_nb
			menu_nb += 1
			
			# Add the items of the menu.
			self.raise_exception_ID = wx.NewId()
			self.debug_menu.Append(self.raise_exception_ID, "Raise Exception", "Raise an exception")
			self.Bind(wx.EVT_MENU, self.on_raise_exception, id = self.raise_exception_ID)
			
			# Add the Debug menu to the menu bar.
			self.main_menu.Append(self.debug_menu, "Debug")
		
		# Attach the menu bar to the window.
		self.SetMenuBar(self.main_menu)
		
		# A dictionary of dialogs corresponding to target menu items.
		self.target_dialogs_by_id = {self.add_reflection_target_ID: reflection_target_dialog,
		                             self.add_transmission_target_ID: transmission_target_dialog,
		                             self.add_absorption_target_ID: absorption_target_dialog,
		                             self.add_reflection_spectrum_target_ID: reflection_spectrum_target_dialog,
		                             self.add_transmission_spectrum_target_ID: transmission_spectrum_target_dialog,
		                             self.add_absorption_spectrum_target_ID: absorption_spectrum_target_dialog,
		                             self.add_reflection_phase_target_ID: reflection_phase_target_dialog,
		                             self.add_transmission_phase_target_ID: transmission_phase_target_dialog,
		                             self.add_reflection_GD_target_ID: reflection_GD_target_dialog,
		                             self.add_transmission_GD_target_ID: transmission_GD_target_dialog,
		                             self.add_reflection_GDD_target_ID: reflection_GDD_target_dialog,
		                             self.add_transmission_GDD_target_ID: transmission_GDD_target_dialog,
		                             self.add_reflection_phase_spectrum_target_ID: reflection_phase_spectrum_target_dialog,
		                             self.add_transmission_phase_spectrum_target_ID: transmission_phase_spectrum_target_dialog,
		                             self.add_reflection_GD_spectrum_target_ID: reflection_GD_spectrum_target_dialog,
		                             self.add_transmission_GD_spectrum_target_ID: transmission_GD_spectrum_target_dialog,
		                             self.add_reflection_GDD_spectrum_target_ID: reflection_GDD_spectrum_target_dialog,
		                             self.add_transmission_GDD_spectrum_target_ID: transmission_GDD_spectrum_target_dialog,
		                             self.add_reflection_color_target_ID: reflection_color_target_dialog,
		                             self.add_transmission_color_target_ID: transmission_color_target_dialog}
		
		# Dictionaries of dialogs, methods and data holders corresponding
		# to calculate menu items.
		self.calculate_dialogs_by_id = {self.calculate_reflection_ID: calculate_reflection_dialog,
		                                self.calculate_transmission_ID: calculate_transmission_dialog,
		                                self.calculate_absorption_ID: calculate_absorption_dialog,
		                                self.calculate_reflection_phase_ID: calculate_reflection_phase_dialog,
		                                self.calculate_transmission_phase_ID: calculate_transmission_phase_dialog,
		                                self.calculate_reflection_GD_ID: calculate_reflection_GD_dialog,
		                                self.calculate_transmission_GD_ID: calculate_transmission_GD_dialog,
		                                self.calculate_reflection_GDD_ID: calculate_reflection_GDD_dialog,
		                                self.calculate_transmission_GDD_ID: calculate_transmission_GDD_dialog,
		                                self.calculate_ellipsometry_ID: calculate_ellipsometry_dialog,
		                                self.calculate_color_ID: calculate_color_dialog,
		                                self.calculate_color_trajectory_ID: calculate_color_trajectory_dialog,
		                                self.calculate_admittance_ID: calculate_admittance_dialog,
		                                self.calculate_circle_ID: calculate_circle_dialog,
		                                self.calculate_electric_field_ID: calculate_electric_field_dialog,
		                                self.calculate_reflection_monitoring_ID: calculate_reflection_monitoring_dialog,
		                                self.calculate_transmission_monitoring_ID: calculate_transmission_monitoring_dialog,
		                                self.calculate_ellipsometry_monitoring_ID: calculate_ellipsometry_monitoring_dialog,
		                                self.calculate_reflection_reverse_ID: calculate_reflection_dialog,
		                                self.calculate_transmission_reverse_ID: calculate_transmission_dialog,
		                                self.calculate_absorption_reverse_ID: calculate_absorption_dialog,
		                                self.calculate_ellipsometry_reverse_ID: calculate_ellipsometry_dialog,
		                                self.calculate_color_reverse_ID: calculate_color_dialog,
		                                self.calculate_color_trajectory_reverse_ID: calculate_color_trajectory_dialog,
		                                self.calculate_reflection_monitoring_reverse_ID: calculate_reflection_monitoring_dialog,
		                                self.calculate_transmission_monitoring_reverse_ID: calculate_transmission_monitoring_dialog,
		                                self.calculate_ellipsometry_monitoring_reverse_ID: calculate_ellipsometry_monitoring_dialog}
		self.calculate_methods_by_id = {self.calculate_reflection_ID: optical_filter.optical_filter.reflection,
		                                self.calculate_transmission_ID: optical_filter.optical_filter.transmission,
		                                self.calculate_absorption_ID: optical_filter.optical_filter.absorption,
		                                self.calculate_reflection_phase_ID: optical_filter.optical_filter.reflection_phase,
		                                self.calculate_transmission_phase_ID: optical_filter.optical_filter.transmission_phase,
		                                self.calculate_reflection_GD_ID: optical_filter.optical_filter.reflection_GD,
		                                self.calculate_transmission_GD_ID: optical_filter.optical_filter.transmission_GD,
		                                self.calculate_reflection_GDD_ID: optical_filter.optical_filter.reflection_GDD,
		                                self.calculate_transmission_GDD_ID: optical_filter.optical_filter.transmission_GDD,
		                                self.calculate_ellipsometry_ID: optical_filter.optical_filter.ellipsometry,
		                                self.calculate_color_ID: optical_filter.optical_filter.color,
		                                self.calculate_color_trajectory_ID: optical_filter.optical_filter.color_trajectory,
		                                self.calculate_admittance_ID: optical_filter.optical_filter.admittance,
		                                self.calculate_circle_ID: optical_filter.optical_filter.circle,
		                                self.calculate_electric_field_ID: optical_filter.optical_filter.electric_field,
		                                self.calculate_reflection_monitoring_ID: optical_filter.optical_filter.reflection_monitoring,
		                                self.calculate_transmission_monitoring_ID: optical_filter.optical_filter.transmission_monitoring,
		                                self.calculate_ellipsometry_monitoring_ID: optical_filter.optical_filter.ellipsometry_monitoring,
		                                self.calculate_reflection_reverse_ID: optical_filter.optical_filter.reflection_reverse,
		                                self.calculate_transmission_reverse_ID: optical_filter.optical_filter.transmission_reverse,
		                                self.calculate_absorption_reverse_ID: optical_filter.optical_filter.absorption_reverse,
		                                self.calculate_ellipsometry_reverse_ID: optical_filter.optical_filter.ellipsometry_reverse,
		                                self.calculate_color_reverse_ID: optical_filter.optical_filter.color_reverse,
		                                self.calculate_color_trajectory_reverse_ID: optical_filter.optical_filter.color_trajectory_reverse,
		                                self.calculate_reflection_monitoring_reverse_ID: optical_filter.optical_filter.reflection_monitoring_reverse,
		                                self.calculate_transmission_monitoring_reverse_ID: optical_filter.optical_filter.transmission_monitoring_reverse,
		                                self.calculate_ellipsometry_monitoring_reverse_ID: optical_filter.optical_filter.ellipsometry_monitoring_reverse}
		self.data_holders_by_id = {self.calculate_reflection_ID: data_holder.reflection_data,
		                           self.calculate_transmission_ID: data_holder.transmission_data,
		                           self.calculate_absorption_ID: data_holder.absorption_data,
		                           self.calculate_reflection_phase_ID: data_holder.reflection_phase_data,
		                           self.calculate_transmission_phase_ID: data_holder.transmission_phase_data,
		                           self.calculate_reflection_GD_ID: data_holder.reflection_GD_data,
		                           self.calculate_transmission_GD_ID: data_holder.transmission_GD_data,
		                           self.calculate_reflection_GDD_ID: data_holder.reflection_GDD_data,
		                           self.calculate_transmission_GDD_ID: data_holder.transmission_GDD_data,
		                           self.calculate_ellipsometry_ID: data_holder.ellipsometry_data,
		                           self.calculate_color_ID: data_holder.color_data,
		                           self.calculate_color_trajectory_ID: data_holder.color_trajectory_data,
		                           self.calculate_admittance_ID: data_holder.admittance_data,
		                           self.calculate_circle_ID: data_holder.circle_data,
		                           self.calculate_electric_field_ID: data_holder.electric_field_data,
		                           self.calculate_reflection_monitoring_ID: data_holder.reflection_monitoring_data,
		                           self.calculate_transmission_monitoring_ID: data_holder.transmission_monitoring_data,
		                           self.calculate_ellipsometry_monitoring_ID: data_holder.ellipsometry_monitoring_data,
		                           self.calculate_reflection_reverse_ID: data_holder.reflection_reverse_data,
		                           self.calculate_transmission_reverse_ID: data_holder.transmission_reverse_data,
		                           self.calculate_absorption_reverse_ID: data_holder.absorption_reverse_data,
		                           self.calculate_ellipsometry_reverse_ID: data_holder.ellipsometry_reverse_data,
		                           self.calculate_color_reverse_ID: data_holder.color_reverse_data,
		                           self.calculate_color_trajectory_reverse_ID: data_holder.color_trajectory_reverse_data,
		                           self.calculate_reflection_monitoring_reverse_ID: data_holder.reflection_monitoring_reverse_data,
		                           self.calculate_transmission_monitoring_reverse_ID: data_holder.transmission_monitoring_reverse_data,
		                           self.calculate_ellipsometry_monitoring_reverse_ID: data_holder.ellipsometry_monitoring_reverse_data}
	
	
	######################################################################
	#                                                                    #
	# make_window                                                        #
	#                                                                    #
	######################################################################
	def make_window(self):
		"""Create the window layout"""
		
		# Separate the window vertically in 2 and create two notebooks. The
		# top one is for the filters and the targets while the buttom one
		# is for the representation of results.
		main_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(main_sizer)
		self.left_panel = wx.SplitterWindow(self, -1)
		main_sizer.Add(self.left_panel, 1, wx.EXPAND|wx.ALL)
		
		self.upper_notebook =  wx.Notebook(self.left_panel, -1)
		self.lower_notebook =  wx.Notebook(self.left_panel, -1)
		
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_change, self.lower_notebook)
		
		self.left_panel.SplitHorizontally(self.upper_notebook, self.lower_notebook, 200)
		self.left_panel.SetMinimumPaneSize(100)
		
		# The first tab of the upper notebook shows a grid with all the
		# filters in the project. When a filter is double clicked, the grid
		# is replaced by panel representing that single filter.
		
		self.filter_tab = wx.Panel(self.upper_notebook, -1)
		self.filter_tab_sizer = wx.BoxSizer(wx.VERTICAL)
		self.filter_tab.SetSizer(self.filter_tab_sizer)
		
		self.filter_grid = filter_grid(self.filter_tab, self)
		self.filter_tab_sizer.Add(self.filter_grid, 1, wx.EXPAND|wx.ALL, 0)
		
		self.make_filter_panel()
		self.filter_tab_sizer.Add(self.filter_panel, 1, wx.EXPAND|wx.ALL, 0)
		
		self.filter_tab_sizer.Hide(self.filter_panel)
		self.filter_tab_sizer.Layout()
		
		self.upper_notebook.AddPage(self.filter_tab, "Filters")
		
		# Create a grid for the targets and add it to the upper notebook.
		self.target_grid = target_grid(self.upper_notebook, self)
		self.upper_notebook.AddPage(self.target_grid, "Targets")
		
		# Create a page for the comment.
		self.comment_box = wx.TextCtrl(self.upper_notebook, -1, "", style = wx.TE_MULTILINE)
		self.comment_box.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.Bind(wx.EVT_TEXT, self.on_comment, self.comment_box)
		self.comment_box.SetEditable(False)
		
		self.upper_notebook.AddPage(self.comment_box, "Comment")
		
		page_nb = 0
		
		# Create a plot for the photometric properties.
		self.photometry_plot = GUI_plot.plot(self.lower_notebook)
		self.photometry_plot.set_clickable()
		self.photometry_plot.set_xlabel("Wavelength (nm)")
		self.photometry_plot.set_ylabel("R, T, or A")
		self.photometry_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.photometry_plot, "Photometric")
		self.photometry_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the photometric properties.
		self.phase_plot = GUI_plot.plot(self.lower_notebook)
		self.phase_plot.set_clickable()
		self.phase_plot.set_xlabel("Wavelength (nm)")
		self.phase_plot.set_ylabel("phase (deg.), GD (fs), or GDD (fs^2)")
		self.phase_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.phase_plot, "Phase")
		self.phase_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the ellipsometric properties.
		self.ellipso_plot = GUI_plot.plot(self.lower_notebook)
		self.ellipso_plot.set_clickable()
		self.ellipso_plot.set_xlabel("Wavelength (nm)")
		self.ellipso_plot.set_ylabel("Psi or Delta (deg.)")
		self.ellipso_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.ellipso_plot, "Ellipso.")
		self.ellipso_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a panel for the colors.
		self.color_window = color_window(self.lower_notebook)
		self.lower_notebook.AddPage(self.color_window, "Color")
		self.color_window_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the admittance diagram.
		self.admittance_plot = GUI_plot.plot(self.lower_notebook)
		self.admittance_plot.set_clickable()
		self.admittance_plot.set_xlabel("Real part")
		self.admittance_plot.set_ylabel("Imag. part")
		self.admittance_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.admittance_plot, "Admittance diagram")
		self.admittance_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the circle diagram.
		self.circle_plot = GUI_plot.plot(self.lower_notebook)
		self.circle_plot.set_clickable()
		self.circle_plot.set_xlabel("Real part")
		self.circle_plot.set_ylabel("Imag. part")
		self.circle_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.circle_plot, "Circle diagram")
		self.circle_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the electric field.
		self.electric_field_plot = GUI_plot.plot(self.lower_notebook)
		self.electric_field_plot.set_clickable()
		self.electric_field_plot.set_xlabel("Distance from substrate (nm)")
		self.electric_field_plot.set_ylabel("Field")
		self.electric_field_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.electric_field_plot, "Electric field")
		self.electric_field_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the photometric monitoring.
		self.photometric_monitoring_plot = GUI_plot.plot(self.lower_notebook)
		self.photometric_monitoring_plot.set_clickable()
		self.photometric_monitoring_plot.set_xlabel("Thickness (nm)")
		self.photometric_monitoring_plot.set_ylabel("R or T")
		self.photometric_monitoring_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.photometric_monitoring_plot, "Photometric monitoring")
		self.photometric_monitoring_plot_page_nb = page_nb
		
		page_nb += 1
		
		# Create a plot for the circle diagram.
		self.ellipso_monitoring_plot = GUI_plot.plot(self.lower_notebook)
		self.ellipso_monitoring_plot.set_clickable()
		self.ellipso_monitoring_plot.set_xlabel("Thickness (nm)")
		self.ellipso_monitoring_plot.set_ylabel("Psi or Delta (deg.)")
		self.ellipso_monitoring_plot.set_legend_position(GUI_plot.TOP)
		self.lower_notebook.AddPage(self.ellipso_monitoring_plot, "Ellipso. monitoring")
		self.ellipso_monitoring_plot_page_nb = page_nb
		
		self.nb_pages = page_nb + 1
		
		# Store all the pages in a list to be able to easily access them
		# by their number.
		self.pages = [self.photometry_plot,\
		                  self.phase_plot,\
		                  self.ellipso_plot,\
		                  self.color_window,\
		                  self.admittance_plot,\
		                  self.circle_plot,\
		                  self.electric_field_plot,\
		                  self.photometric_monitoring_plot,\
		                  self.ellipso_monitoring_plot]
	
	
	######################################################################
	#                                                                    #
	# make_status_bar                                                    #
	#                                                                    #
	######################################################################
	def make_status_bar(self):
		"""Create the status bar and add it to the window"""
		
		self.status_bar = wx.StatusBar(self)
		
		# Creage a button to cancel operations.
		self.cancel_button = wx.Button(self.status_bar, wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.on_cancel_button, self.cancel_button)
		
		# The gauge is put in the status bar.
		self.gauge = wx.Gauge(self.status_bar, -1, 100, style = wx.GA_HORIZONTAL|wx.GA_SMOOTH)
		
		self.SetStatusBar(self.status_bar)
	
	
	######################################################################
	#                                                                    #
	# make_filter_panel                                                  #
	#                                                                    #
	######################################################################
	def make_filter_panel(self):
		"""Create the filter panel"""
		
		self.filter_panel = wx.Panel(self.filter_tab, -1)
		self.filter_panel_sizer = wx.BoxSizer(wx.VERTICAL)
		self.filter_panel.SetSizer(self.filter_panel_sizer)
		
		self.filter_description_box = wx.TextCtrl(self.filter_panel, -1)
		
		close_botton = wx.Button(self.filter_panel, wx.ID_CLOSE, "Back to filter list")
		
		self.filter_notebook = wx.Notebook(self.filter_panel, -1)
		
		# Create a grid for the FRONT layers.
		self.front_layer_grid = layer_grid(self.filter_notebook, self, FRONT)
		self.filter_notebook.AddPage(self.front_layer_grid, "Front Layers")
		
		# Create a plot for the FRONT index profile.
		self.front_index_profile_plot = GUI_plot.plot(self.filter_notebook)
		self.front_index_profile_plot.set_xlabel("Depth (nm)")
		self.front_index_profile_plot.set_ylabel("n")
		self.filter_notebook.AddPage(self.front_index_profile_plot, "Front Index Profile")
		
		# Create a grid for the back layers.
		self.back_layer_grid = layer_grid(self.filter_notebook, self, BACK)
		self.filter_notebook.AddPage(self.back_layer_grid, "Back Layers")
		
		# Create a plot for the back index profile.
		self.back_index_profile_plot = GUI_plot.plot(self.filter_notebook)
		self.back_index_profile_plot.set_xlabel("Depth (nm)")
		self.back_index_profile_plot.set_ylabel("n")
		self.filter_notebook.AddPage(self.back_index_profile_plot, "Back Index Profile")
		
		self.filter_panel_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.filter_panel_sizer_1.Add(wx.StaticText(self.filter_panel, -1, "Description:"),
		                              0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.filter_panel_sizer_1.Add(self.filter_description_box, 1, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
		self.filter_panel_sizer_1.Add(close_botton, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
		
		self.filter_panel_sizer.Add(self.filter_panel_sizer_1, 0, wx.EXPAND|wx.TOP, 5)
		self.filter_panel_sizer.Add(self.filter_notebook, 1, wx.EXPAND|wx.ALL, 5)
		
		self.Bind(wx.EVT_TEXT, self.on_filter_description, self.filter_description_box)
		self.Bind(wx.EVT_BUTTON, self.on_close_filter, close_botton)
	
	
	######################################################################
	#                                                                    #
	# import_modules                                                     #
	#                                                                    #
	######################################################################
	def import_modules(self):
		"""Import the modules and add items to the modules menu"""
		
		self.modules, error, error_message = modules.load_modules()
		
		# if an error occured, show the error message.
		if error:
			wx.MessageBox("Some module(s) failed to load.\n\n%s" % error_message, "Module(s) failed to load", wx.ICON_ERROR|wx.OK)
		
		# Make menus for the modules and to reload modules.
		reload_modules_menu_IDs = []
		for module in self.modules:
			module_menu_ID = wx.NewId()
			module_menu = wx.Menu()
			self.modules_menu.AppendMenu(module_menu_ID, module.get_name(), module_menu)
			module.set_menu_ID(module_menu_ID)
			
			submodule_IDs = []
			for submodule in module.get_submodule():
				submodule_ID = wx.NewId()
				module_menu.Append(submodule_ID, submodule.get_name(), submodule.get_name())
				submodule_IDs.append(submodule_ID)
				wx.EVT_MENU(self, submodule_ID, self.on_execute_module)
			module.set_submodule_IDs(submodule_IDs)
	
	
	######################################################################
	#                                                                    #
	# startup_checkup                                                    #
	#                                                                    #
	######################################################################
	def startup_checkup(self):
		"""Do a few checkup when starting the software
		
		Verify if the abeles and moremath dll were correctly loaded and
		inform the user if they were not."""
		
		try:
			import threading
		except ImportError:
			wx.MessageBox("OpenFilters requires multithreading\n\n Multithreading is not available on your system and OpenFilters cannot run.", "OpenFilters requires multithreading", wx.ICON_ERROR|wx.OK)
			
			self.Hide()
			self.Destroy()
			
			return
		
		message = ""
		if not abeles.get_abeles_dll_import_success():
			message += "Abeles dynamic library import failed, calculations will be approximatly 10 times slower and more memory will be used."
		if not moremath.get_moremath_dll_import_success():
			if message: message += "\n\n"
			message += "Moremath dynamic library import failed, refinement will be approximatly 4 times slower."
		if message:
			message = "OpenFilters will be slow!\n\n" + message
			wx.MessageBox(message, "Dynamic library import failed", wx.ICON_INFORMATION|wx.OK)
		
		try:
			from ast import literal_eval as _eval
		except ImportError:
			wx.MessageBox("Do not open files from untrusted sources!\n\nYou are running OpenFilters with a version of Python older than 2.6 and project files can be used to execute arbitrary code on your computer: DO NO OPEN PROJECT FILES FROM UNTRUSTED SOURCES. (See release notes for details.)", "Security alert", wx.ICON_WARNING|wx.OK)
		
		message = ""
		
		if self.user_material_directory and not os.path.isdir(self.user_material_directory):
			self.user_material_directory = None
			message = "The previously selected user material directory has been removed or renamed. "
		
		if not self.user_material_directory:
			message += "OpenFilters requires the selection of a user material directory. All the materials you create are saved in this directory. If you don't choose one, you will not be able to create new materials."
			dialog = user_material_directory_dialog(self, message = message)
			answer = dialog.ShowModal()
			if answer == wx.ID_OK:
				self.user_material_directory = dialog.get_directory()
				self.user_config.set("Directories", "usermaterialdirectory", self.user_material_directory.encode('utf-8'))
			dialog.Destroy()
	
	
	######################################################################
	#                                                                    #
	# get_material_catalog                                               #
	#                                                                    #
	######################################################################
	def get_material_catalog(self):
		"""Get the material catalog including the user material directory, if defined
		
		This method takes no input argument and returns the material
		catalog including the user material directory if it is defined."""
		
		default_material_catalog = materials.material_catalog()
		
		if self.user_material_directory:
			user_material_catalog = materials.material_catalog(self.user_material_directory)
			return materials.material_catalogs([default_material_catalog, user_material_catalog])
		else:
			return default_material_catalog
	
	
	######################################################################
	#                                                                    #
	# on_new_project                                                     #
	#                                                                    #
	######################################################################
	def on_new_project(self, event):
		"""Create a new project when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		material_catalog = self.get_material_catalog()
		
		self.project = project.project(material_catalog)
		
		self.filter_grid.set_project(self.project)
		self.target_grid.set_project(self.project)
		
		self.comment_box.SetEditable(True)
		
		self.update_title()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_open_project                                                    #
	#                                                                    #
	######################################################################
	def on_open_project(self, event):
		"""Open an existing project when the menu item is selected
		
		This method takes a single argument:
		  event              the event.
		
		If the event is the one to open an example project, the open dialog
		default dir is set to the example directory."""
		
		id = event.GetId()
		
		if id in self.recently_opened_project_IDs:
			filename = self.recently_opened_projects[self.recently_opened_project_IDs.index(id)]
			try:
				directory, _ = os.path.split(filename)
				os.chdir(directory)
			except OSError:
				pass
		
		elif id in self.open_example_IDs:
			filename = self.open_example_IDs[id]
		
		else:
			window = wx.FileDialog(self, "Open Project", os.getcwd(), "", project_wildcard, style = wx.OPEN|wx.CHANGE_DIR)
			
			answer = window.ShowModal()
			if answer == wx.ID_OK:
				filename = window.GetPath()
			else:
				filename = ""
			
			window.Destroy()
		
		if filename:
			material_catalog = self.get_material_catalog()
			try:
				self.project = project.read_project(filename, material_catalog)
			except (project.project_error, optical_filter.filter_error, targets.target_error, materials.material_error), error:
				if filename in self.recently_opened_projects:
					self.recently_opened_projects.remove(filename)
				wx.MessageBox("An error occured while opening the project.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		if self.project:
			if id not in self.open_example_IDs:
				self.project_filename = filename
				
				if self.project_filename in self.recently_opened_projects:
					self.recently_opened_projects.remove(self.project_filename)
				self.recently_opened_projects.insert(0, self.project_filename)
			
			nb_filters = self.project.get_nb_filters()
			self.data = [[[] for i_page in range(self.nb_pages)] for i_filter in range(nb_filters)]
			
			self.filter_grid.set_project(self.project)
			self.target_grid.set_project(self.project)
			self.comment_box.SetValue(self.project.get_comment())
			
			self.comment_box.SetEditable(True)
			
			self.update_title()
			self.update_target_curve()
		
		self.update_recently_opened_projects()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_close_project                                                   #
	#                                                                    #
	######################################################################
	def on_close_project(self, event):
		"""Close the project when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# Offer the user the possibility to save a modified project.
		if self.project.get_modified():
			dialog = wx.MessageDialog(self, "The project has been modified, do you want to save it before closing it?", "Save project?", wx.ICON_EXCLAMATION|wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT)
			answer = dialog.ShowModal()
			if answer == wx.ID_CANCEL:
				return
			elif answer == wx.ID_YES:
				self.on_save_project(event)
			dialog.Destroy()
		
		self.project_filename = ""
		self.project = None
		
		self.data = []
		
		self.target_curve_nbs = [-1]*self.nb_pages
		self.selected_filter_nb = -1
		self.selected_target_nb = -1
		
		self.filter_grid.clear_project()
		self.target_grid.clear_project()
		self.comment_box.Clear()
		
		self.comment_box.SetEditable(False)
		
		self.update_title()
		self.hide_filter()
		self.reset_all_pages()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_save_project                                                    #
	#                                                                    #
	######################################################################
	def on_save_project(self, event):
		"""Save the project when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# Save the project if it has a filename, otherwise call save as.
		if self.project_filename:
			project.write_project(self.project, self.project_filename)
			
			self.update_menu()
		
		else:
			self.on_save_project_as(event)
	
	
	######################################################################
	#                                                                    #
	# on_save_project_as                                                 #
	#                                                                    #
	######################################################################
	def on_save_project_as(self, event):
		"""Save the project under a different name when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		window = wx.FileDialog(self, "Save Project as", os.getcwd(), os.path.basename(self.project_filename), project_wildcard, style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			filename = window.GetPath()
			
			project.write_project(self.project, filename)
			self.project_filename = filename
			
			if self.project_filename in self.recently_opened_projects:
				self.recently_opened_projects.remove(self.project_filename)
			self.recently_opened_projects.insert(0, self.project_filename)
			
			self.update_title()
			self.update_recently_opened_projects()
			self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_revert                                                          #
	#                                                                    #
	######################################################################
	def on_revert(self, event):
		"""Revert to the last saved version when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# Verify that the file still exist.
		try:
			saved_version = project.read_project(self.project_filename)
		except (project.project_error, optical_filter.filter_error, materials.material_error), error:
			wx.MessageBox("It is impossible to reopen the project.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			return
		
		self.project = saved_version
		
		nb_filters = self.project.get_nb_filters()
		nb_targets = self.project.get_nb_targets()
		
		self.data = [[[] for i_page in range(self.nb_pages)] for i_filter in range(nb_filters)]
		
		self.target_curve_nbs = [-1]*self.nb_pages
		
		# If the number of the previously selected filter is larger than
		# the number of filters in the saved version, no filter is
		# selected. The filter grid will take care of selecting a filter.
		if self.selected_filter_nb >= nb_filters:
			self.selected_filter_nb = -1
		self.filter_grid.set_project(self.project)
		
		# If the number of the previously selected target is larger than
		# the number of targets in the saved version, no target is
		# selected. The target grid will take care of selecting a target.
		if self.selected_target_nb >= nb_filters:
			self.selected_target_nb = -1
		self.target_grid.set_project(self.project)
		
		self.comment_box.SetValue(self.project.get_comment())
		
		self.comment_box.SetEditable(True)
		
		self.update_title()
		self.hide_filter()
		self.reset_all_pages()
		self.update_target_curve()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_quit                                                            #
	#                                                                    #
	######################################################################
	def on_quit(self, event):
		"""Exit the application when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# Do not quit during a modification or a calculation if the user
		# presses alt-F4.
		if self.modifying or self.calculating:
			return
		
		# Offer the user the possibility to save a modified project.
		if self.project and self.project.get_modified():
			dialog = wx.MessageDialog(self, "The project has been modified, do you want to save it before quitting?", "Save project?", wx.ICON_EXCLAMATION|wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT)
			answer = dialog.ShowModal()
			if answer == wx.ID_CANCEL:
				return
			elif answer == wx.ID_YES:
				self.on_save_project(event)
			dialog.Destroy()
		
		self.save_configuration()
		
		self.Hide()
		self.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_add_filter                                                      #
	#                                                                    #
	######################################################################
	def on_add_filter(self, event):
		"""Add a filter to the project when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		try:
			nb = self.project.add_filter()
		except materials.material_error, error:
			wx.MessageBox("It is impossible to create a new filter because there is a problem with one of the default materials.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			return
		except optical_filter.filter_error, error:
			wx.MessageBox("It is impossible to create a new filter.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			return
		
		self.data.append([[] for i_page in range(self.nb_pages)])
		
		self.hide_filter()
		self.filter_grid.add_filter()
		
		self.on_filter_properties()
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_remove_filter                                                   #
	#                                                                    #
	######################################################################
	def on_remove_filter(self, event):
		"""Remove the selected filter from the project when the menu item
		is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.remove_filter(self.selected_filter_nb)
	
	
	######################################################################
	#                                                                    #
	# on_modify_filter                                                   #
	#                                                                    #
	######################################################################
	def on_modify_filter(self, event):
		"""Modify the selected filter when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.show_filter(self.selected_filter_nb)
	
	
	######################################################################
	#                                                                    #
	# on_copy_filter                                                     #
	#                                                                    #
	######################################################################
	def on_copy_filter(self, event):
		"""Copy the selected filter when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.copy_filter(self.selected_filter_nb)
	
	
	######################################################################
	#                                                                    #
	# on_add_target                                                      #
	#                                                                    #
	######################################################################
	def on_add_target(self, event):
		"""Add a target to the project when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		window = self.target_dialogs_by_id[id](self)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			target = window.get_target()
			
			self.project.add_target(target)
			
			self.target_grid.add_target()
			self.update_target_curve()
			self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_read_target_from_file                                           #
	#                                                                    #
	######################################################################
	def on_read_target_from_file(self, event):
		"""Read a target from a file and add it to the project when the
		menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		target = None
		
		window = read_target_from_file_dialog(self)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			try:
				target = window.get_target()
			except targets.target_error, error:
				wx.MessageBox("Error while reading the target.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		window.Destroy()
		
		if target:
			self.project.add_target(target)
			
			self.target_grid.add_target()
			self.update_target_curve()
			self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_remove_target                                                   #
	#                                                                    #
	######################################################################
	def on_remove_target(self, event):
		"""Remove the selected target from the project when the menu item
		is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.remove_target(self.selected_target_nb)
	
	
	######################################################################
	#                                                                    #
	# on_modify_target                                                   #
	#                                                                    #
	######################################################################
	def on_modify_target(self, event):
		"""Modify the selected target when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.modify_target(self.selected_target_nb)
	
	
	######################################################################
	#                                                                    #
	# on_copy_target                                                     #
	#                                                                    #
	######################################################################
	def on_copy_target(self, event):
		"""Copy the selected target when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.copy_target(self.selected_target_nb)
	
	
	######################################################################
	#                                                                    #
	# on_filter_properties                                               #
	#                                                                    #
	######################################################################
	def on_filter_properties(self, event = None):
		"""View the properties of the filter when the menu item is selected
		or when a new filter is created
		
		This method takes an optional argument:
		  event              (optional) the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = filter_property_dialog(self, filter)
		answer = window.ShowModal()
		
		if answer == wx.ID_OK:
			modified = window.apply_to_filter()
			
			if modified:
				if self.filter_panel.IsShown():
					self.front_layer_grid.reset()
					self.back_layer_grid.reset()
					self.update_index_profile_plots()
				self.delete_results(self.selected_filter_nb)
				self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_add_layer                                                       #
	#                                                                    #
	######################################################################
	def on_add_layer(self, event):
		"""Add a layer to the selected filter when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = simple_layer_dialog(self, filter)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			window.apply()
			
			self.filter_grid.reset_filter(self.selected_filter_nb)
			side = window.get_side()
			if self.filter_panel.IsShown():
				if side == FRONT:
					self.front_layer_grid.reset()
				else:
					self.back_layer_grid.reset()
				self.update_index_profile_plots(side)
			
			self.delete_results(self.selected_filter_nb)
			self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_remove_layer                                                    #
	#                                                                    #
	######################################################################
	def on_remove_layer(self, event):
		"""Remove a layer from the selected filter when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = remove_layer_dialog(self, filter)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			window.apply()
			
			self.filter_grid.reset_filter(self.selected_filter_nb)
			side = window.get_side()
			if self.filter_panel.IsShown():
				if side == FRONT:
					self.front_layer_grid.reset()
				else:
					self.back_layer_grid.reset()
				self.update_index_profile_plots(side)
			
			self.delete_results(self.selected_filter_nb)
			self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_stack_formula                                                   #
	#                                                                    #
	######################################################################
	def on_stack_formula(self, event):
		"""Modify the stack formula of the selected filter when the menu
		item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = stack_dialog(self, filter)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			modified = window.apply()
			
			if modified:
				self.filter_grid.reset_filter(self.selected_filter_nb)
				side = window.get_side()
				if self.filter_panel.IsShown():
					if side == FRONT:
						self.front_layer_grid.reset()
					else:
						self.back_layer_grid.reset()
					self.update_index_profile_plots(side)
				
				self.delete_results(self.selected_filter_nb)
				self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_import_layer                                                    #
	#                                                                    #
	######################################################################
	def on_import_layer(self, event):
		"""Import a graded index layer from a file when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = import_layer_dialog(self, filter)
		
		answer = window.ShowModal()
		window.Hide()
		if answer == wx.ID_OK:
			try:
				window.apply()
			except import_layer_error, error:
				wx.MessageBox("Error while importing layer.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			else:
				self.filter_grid.reset_filter(self.selected_filter_nb)
				side = window.get_side()
				if self.filter_panel.IsShown():
					if side == FRONT:
						self.front_layer_grid.reset()
					else:
						self.back_layer_grid.reset()
					self.update_index_profile_plots(side)
				
				self.delete_results(self.selected_filter_nb)
				self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_merge_layers                                                    #
	#                                                                    #
	######################################################################
	def on_merge_layers(self, event):
		"""Merge identical layers in the selected filter when the menu item
		is selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		filter.merge_layers()
		
		self.filter_grid.reset_filter(self.selected_filter_nb)
		if self.filter_panel.IsShown():
			self.front_layer_grid.reset()
			self.back_layer_grid.reset()
			self.update_index_profile_plots()
		
		self.delete_results(self.selected_filter_nb)
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_convert_layers                                                  #
	#                                                                    #
	######################################################################
	def on_convert_layers(self, event):
		"""Convert intermediate index layers of the selected filter to
		steps when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		filter.convert_mixtures_to_steps()
		
		self.filter_grid.reset_filter(self.selected_filter_nb)
		if self.filter_panel.IsShown():
			self.front_layer_grid.reset()
			self.back_layer_grid.reset()
			self.update_index_profile_plots()
		
		self.delete_results(self.selected_filter_nb)
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_swap_sides                                                      #
	#                                                                    #
	######################################################################
	def on_swap_sides(self, event):
		"""Swap the sides of the selected filter when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		filter.swap_sides()
		
		self.filter_grid.reset_filter(self.selected_filter_nb)
		if self.filter_panel.IsShown():
			self.front_layer_grid.reset()
			self.back_layer_grid.reset()
			self.update_index_profile_plots()
		
		self.delete_results(self.selected_filter_nb)
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_execute_module                                                  #
	#                                                                    #
	######################################################################
	def on_execute_module(self, event):
		"""Execute a module when the menu item is selected
		
		This method takes a single argument:
		  event              the event.
		
		Show the dialog and then execute the module according to the
		parameters obtained from the dialog."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		# Find wich submodule to execute.
		for module in self.modules:
			submodule = module.get_submodule_by_ID(event.GetId())
			if submodule:
				break
		
		# Show the submodule user interface.
		try:
			window = submodule.execute_dialog(self, filter)
			answer = window.ShowModal()
			if answer == wx.ID_OK:
				side = window.get_side()
				position = window.get_position()
				parameters = window.get_parameters()
			
			window.Destroy()
		
		except Exception:
			type_of_exception, value = sys.exc_info()[:2]
			wx.MessageBox("An error occured while executing the dialog of submodule %s of module %s.\n\n%s." % (submodule.name, module.name, value), "Module error", wx.ICON_ERROR|wx.OK)
			
			return
		
		# Execute the submodule.
		if answer == wx.ID_OK:
			self.modifying = True
			self.update_menu()
			self.update_status_bar()
			self.update_cursor()
			self.update_grids()
			
			monitoring_thread = threading.Thread(target = self.monitor_modification_progress, args = (self.selected_filter_nb, ))
			monitoring_thread.start()
			
			work_thread = threading.Thread(target = self.execute_module, args = (module, submodule, position, side, False, parameters))
			work_thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_export_index_profile                                            #
	#                                                                    #
	######################################################################
	def on_export_index_profile(self, event):
		"""Export the selected filter index profile when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		if id == self.export_front_index_profile_ID:
			side = FRONT
		elif id == self.export_back_index_profile_ID:
			side = BACK
		
		window = wx.FileDialog(self, "Export index profile", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			export.export_index_profile(filename, filter, side)
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_calculate                                                       #
	#                                                                    #
	######################################################################
	def on_calculate(self, event):
		"""Calculate properties of the selected filter when the menu item
		is selected
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		window = self.calculate_dialogs_by_id[id](self, filter)
		answer = window.ShowModal()
		
		if answer == wx.ID_OK:
			parameters = window.get_parameters()
		
		window.Destroy()
		
		if answer == wx.ID_OK:
			self.calculating = True
			self.update_menu()
			self.update_status_bar()
			self.update_cursor()
			self.update_grids()
			
			monitoring_thread = threading.Thread(target = self.monitor_calculation_progress, args = (self.selected_filter_nb, ))
			monitoring_thread.start()
			
			work_thread = threading.Thread(target = self.calculate, args = (self.selected_filter_nb, self.calculate_methods_by_id[id], parameters, self.data_holders_by_id[id]))
			work_thread.start()
	
	
	######################################################################
	#                                                                    #
	# on_random_errors                                                   #
	#                                                                    #
	######################################################################
	def on_random_errors(self, event):
		"""Show a dialog to simulate the effect of random deposition errors
		when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		targets = self.project.get_targets()
		
		window = random_errors_dialog(self, filter, targets)
		window.ShowModal()
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_show_targets                                                    #
	#                                                                    #
	######################################################################
	def on_show_targets(self, event):
		"""Show the targets when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		self.update_target_curve()
	
	
	######################################################################
	#                                                                    #
	# on_show_all_results                                                #
	#                                                                    #
	######################################################################
	def on_show_all_results(self, event):
		"""Show the results for all filters in the project when the menu
		item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		if self.project is None:
			return
		
		if self.analyse_menu.IsChecked(self.show_all_results_ID):
			for filter_nb in range(self.project.get_nb_filters()):
				if filter_nb != self.selected_filter_nb:
					self.show_results(filter_nb)
		else:
			for filter_nb in range(self.project.get_nb_filters()):
				if filter_nb != self.selected_filter_nb:
					self.hide_results(filter_nb)
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_export_results_as_text                                          #
	#                                                                    #
	######################################################################
	def on_export_results_as_text(self, event):
		"""Export results in the currently shown tab as text when the menu
		item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		window = wx.FileDialog(self, "Export results as text", os.getcwd(), "", style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			selected_page_nb = self.lower_notebook.GetSelection()
			
			if self.analyse_menu.IsChecked(self.show_all_results_ID):
				data = []
				for i_filter in range(len(self.data)):
					data += [data_and_curve_nb[0] for data_and_curve_nb in self.data[i_filter][selected_page_nb]]
			else:
				data = [data_and_curve_nb[0] for data_and_curve_nb in self.data[self.selected_filter_nb][selected_page_nb]]
			
			try:
				export.export_results_to_text(filename, data)
			except IOError, error:
				wx.MessageBox("Exportation failed.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
	
	
	######################################################################
	#                                                                    #
	# on_export_results_as_figure                                        #
	#                                                                    #
	######################################################################
	def on_export_results_as_figure(self, event):
		"""Export results in the currently shown tab as a figure when the
		menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		window = wx.FileDialog(self, "Export results as figure", os.getcwd(), "", GUI_plot.FIGURE_WILDCARD, style = wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
			
			filename = window.GetPath()
			
			selected_page_nb = self.lower_notebook.GetSelection()
			
			try:
				self.pages[selected_page_nb].save_to_file(filename)
			except KeyError:
				wx.MessageBox("Invalid file extension.", "Error", wx.ICON_ERROR|wx.OK)
			except IOError, error:
				wx.MessageBox("Exportation failed.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
			
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
	
	
	######################################################################
	#                                                                    #
	# on_optimize                                                        #
	#                                                                    #
	######################################################################
	def on_optimize(self, event):
		"""Optimize or design the selected filter when the menu item is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		id = event.GetId()
		
		filter = self.project.get_filter(self.selected_filter_nb)
		targets = self.project.get_targets()
		
		if id == self.optimize_refinement_ID:
			dialog = optimization_refinement_dialog
		elif id == self.optimize_needles_ID:
			dialog = optimization_needles_dialog
		elif id == self.optimize_steps_ID:
			dialog = optimization_steps_dialog
		elif id == self.design_Fourier_ID:
			dialog = optimization_Fourier_dialog
		
		window = dialog(self, filter, targets)
		answer = window.ShowModal()
		window.Destroy()
		
		if answer == wx.ID_OK:
			self.filter_grid.reset_filter(self.selected_filter_nb)
			if self.filter_panel.IsShown():
				self.front_layer_grid.reset()
				self.back_layer_grid.reset()
				self.update_index_profile_plots()
			
			self.delete_results(self.selected_filter_nb)
			self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_manage_materials                                                #
	#                                                                    #
	######################################################################
	def on_manage_materials(self, event):
		"""Manage materials when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		if self.project:
			material_catalog = self.project.get_material_catalog()
		else:
			material_catalog = self.get_material_catalog()
		
		window = manage_materials_dialog(self, material_catalog, not self.project)
		window.ShowModal()
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_change_user_material_directory                                  #
	#                                                                    #
	######################################################################
	def on_change_user_material_directory(self, event):
		"""Change the user material directory when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		dialog = user_material_directory_dialog(self, self.user_material_directory)
		answer = dialog.ShowModal()
		if answer == wx.ID_OK:
			self.user_material_directory = dialog.get_directory()
			self.user_config.set("Directories", "usermaterialdirectory", self.user_material_directory.encode('utf-8'))
		dialog.Destroy()
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_about                                                           #
	#                                                                    #
	######################################################################
	def on_about(self, event):
		"""Show the about box when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		wx.MessageBox(about.message, about.title, wx.OK)
	
	
	######################################################################
	#                                                                    #
	# on_raise_exception                                                 #
	#                                                                    #
	######################################################################
	def on_raise_exception(self, event):
		"""Raise an exception when the menu item is selected
		
		This method takes a single argument:
		  event              the event."""
		
		raise Exception
	
	
	######################################################################
	#                                                                    #
	# on_size                                                            #
	#                                                                    #
	######################################################################
	def on_size(self, event):
		"""Adjust the content when the size of the window is changed
		
		This method takes a single argument:
		  event              the event."""
		
		self.update_status_bar()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_update                                                          #
	#                                                                    #
	######################################################################
	def on_update(self, event):
		"""Handle update events
		
		This method takes a single argument:
		  event              the event."""
		
		what = event.get_what()
		
		if what & UPDATE_MENU:
			self.update_menu()
		
		if what & UPDATE_STATUS_BAR:
			self.update_status_bar()
		
		if what & UPDATE_CURSOR:
			self.update_cursor()
		
		if what & UPDATE_TARGET_CURVE:
			self.update_target_curve()
		
		if what & UPDATE_FILTER:
			self.filter_grid.reset_filter(self.selected_filter_nb)
			if self.filter_panel.IsShown():
				self.front_layer_grid.reset()
				self.back_layer_grid.reset()
				self.update_index_profile_plots()
			self.delete_results(self.selected_filter_nb)
		
		if what & UPDATE_GRIDS:
			self.update_grids()
	
	
	######################################################################
	#                                                                    #
	# on_progress                                                        #
	#                                                                    #
	######################################################################
	def on_progress(self, event):
		"""Handle progress events
		
		Change the progress bar.
		
		This method takes a single argument:
		  event              the event."""
		
		progress = event.get_progress()
		
		if progress is None:
			self.gauge.Pulse()
		else:
			self.gauge.SetValue(int(100.0*progress))
	
	
	######################################################################
	#                                                                    #
	# on_message                                                         #
	#                                                                    #
	######################################################################
	def on_message(self, event):
		"""Handle message events
		
		Show the message.
		
		This method takes a single argument:
		  event              the event."""
		
		message = event.get_message()
		title = event.get_title()
		icon = event.get_icon()
		
		wx.MessageBox(message, title, icon|wx.OK)
	
	
	######################################################################
	#                                                                    #
	# on_data                                                            #
	#                                                                    #
	######################################################################
	def on_data(self, event):
		"""Handle data events
		
		This method takes a single argument:
		  event              the event."""
		
		data = event.get_data()
		
		page_nb, curve_nb = self.show_data(data, self.selected_filter_nb)
		
		self.data[self.selected_filter_nb][page_nb].append([data, curve_nb])
		
		self.lower_notebook.SetSelection(page_nb)
	
	
	######################################################################
	#                                                                    #
	# on_remove_curve                                                    #
	#                                                                    #
	######################################################################
	def on_remove_curve(self, event):
		"""Handle remove curve events from the plots
		
		This method takes a single argument:
		  event              the event.
		
		Remove the data associated with the removed curve."""
		
		curve_nb = event.get_nb()
		plot_ID = event.GetId()
		
		# Locate the data and remove it.
		for page_nb in range(self.nb_pages):
			if plot_ID == self.pages[page_nb].GetId():
				
				# If it is the target curve, redraw it.
				if curve_nb == self.target_curve_nbs[page_nb]:
					self.target_curve_nbs[page_nb] = -1
					self.update_target_curve()
					break
				
				for filter_nb in range(self.project.get_nb_filters()):
					for data_nb in range(len(self.data[filter_nb][page_nb])):
						data_and_curve_nb = self.data[filter_nb][page_nb][data_nb]
						if data_and_curve_nb[1] == curve_nb:
							self.data[filter_nb][page_nb].pop(data_nb)
							break
				break
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_comment                                                         #
	#                                                                    #
	######################################################################
	def on_comment(self, event):
		"""Update the comment
		
		Update the comment in the project when the user writes in the GUI.
		
		This method takes a single argument:
		  event              the event."""
		
		# It it necessary to verify that there is a project opened before
		# setting the comment because when the comment text is cleared
		# after the closing of a filter, it generates an event.
		if self.project:
			comment = self.comment_box.GetValue()
			self.project.set_comment(comment)
			
			self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_filter_description                                              #
	#                                                                    #
	######################################################################
	def on_filter_description(self, event):
		"""Modify the filter description when text is entered in the box
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		filter.set_description(self.filter_description_box.GetValue())
		
		self.filter_grid.reset_filter(self.selected_filter_nb)
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_close_filter                                                    #
	#                                                                    #
	######################################################################
	def on_close_filter(self, event):
		"""Hide the shown filter when the close button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		self.hide_filter()
		self.filter_grid.reset_filter(self.selected_filter_nb)
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_cancel_button                                                   #
	#                                                                    #
	######################################################################
	def on_cancel_button(self, event):
		"""Cancel the current operation when the cancel button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		filter.stop()
	
	
	######################################################################
	#                                                                    #
	# on_page_change                                                     #
	#                                                                    #
	######################################################################
	def on_page_change(self, event):
		"""Update the user interface following a page change
		
		This method takes a single argument:
		  event              the event."""
		
		self.update_menu()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# select_filter                                                      #
	#                                                                    #
	######################################################################
	def select_filter(self, filter_nb):
		"""Select a filter and update the user interface accordingly
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		if filter_nb != self.selected_filter_nb:
			previously_selected_filter = self.selected_filter_nb
			self.selected_filter_nb = filter_nb
			
			if not self.analyse_menu.IsChecked(self.show_all_results_ID):
				for page_nb in range(self.nb_pages):
					if page_nb != self.color_window_page_nb:
						self.pages[page_nb].begin_batch()
				
				if previously_selected_filter != -1:
					self.hide_results(previously_selected_filter)
				self.show_results(self.selected_filter_nb)
				
				for page_nb in range(self.nb_pages):
					if page_nb != self.color_window_page_nb:
						self.pages[page_nb].end_batch()
			
			self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# remove_filter                                                      #
	#                                                                    #
	######################################################################
	def remove_filter(self, filter_nb):
		"""Remove a filter and update the user interface accordingly
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		if filter_nb == self.selected_filter_nb:
			self.hide_filter()
			self.selected_filter_nb = -1
		
		self.hide_results(filter_nb)
		self.project.remove_filter(filter_nb)
		
		self.data.pop(filter_nb)
		
		self.filter_grid.remove_filter(filter_nb)
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# show_filter                                                        #
	#                                                                    #
	######################################################################
	def show_filter(self, filter_nb):
		"""Show a filter
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		filter = self.project.get_filter(filter_nb)
		
		self.filter_grid.select_filter(filter_nb)
		
		self.filter_description_box.SetValue(filter.get_description())
		self.front_layer_grid.set_filter(filter)
		self.back_layer_grid.set_filter(filter)
		self.update_index_profile_plots()
		
		self.filter_tab_sizer.Hide(self.filter_grid)
		self.filter_tab_sizer.Show(self.filter_panel)
		self.filter_tab_sizer.Layout()
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# copy_filter                                                        #
	#                                                                    #
	######################################################################
	def copy_filter(self, filter_nb):
		"""Copy a filter and update the user interface accordingly
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		filter = self.project.get_filter(filter_nb)
		
		clone = filter.clone()
		
		self.project.add_filter(clone)
		
		self.data.append([[] for i_page in range(self.nb_pages)])
		
		self.hide_filter()
		self.filter_grid.add_filter()
		
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# hide_filter                                                        #
	#                                                                    #
	######################################################################
	def hide_filter(self):
		"""Hide the shown filter"""
		
		self.filter_tab_sizer.Hide(self.filter_panel)
		self.filter_tab_sizer.Show(self.filter_grid)
		self.filter_tab_sizer.Layout()
		
		self.front_layer_grid.clear_filter()
		self.back_layer_grid.clear_filter()
	
	
	######################################################################
	#                                                                    #
	# select_target                                                      #
	#                                                                    #
	######################################################################
	def select_target(self, target_nb):
		"""Select a target and update the user interface accordingly
		
		This method takes a single argument:
		  target_nb          the target number."""
		
		if target_nb != self.selected_target_nb:
			self.selected_target_nb = target_nb
			
			self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# remove_target                                                      #
	#                                                                    #
	######################################################################
	def remove_target(self, target_nb):
		"""Remove a target and update the user interface accordingly
		
		This method takes a single argument:
		  target_nb          the target number."""
		
		self.project.remove_target(target_nb)
		
		self.target_grid.remove_target(target_nb)
		self.update_target_curve()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# modify_target                                                      #
	#                                                                    #
	######################################################################
	def modify_target(self, target_nb):
		"""Show a target (in a dialog)
		
		This method takes a single argument:
		  target_nb          the target number."""
		
		target = self.project.get_target(target_nb)
		
		kind = target.get_kind()
		
		window = self.target_dialogs[kind](self, target)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			# We don't need to actualize the target, the dialog takes care of
			# it when get_target is called.
			target = window.get_target()
			
			self.target_grid.reset_target(target_nb)
			self.update_target_curve()
			self.update_menu()
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# copy_target                                                        #
	#                                                                    #
	######################################################################
	def copy_target(self, target_nb):
		"""Copy a target and update the user interface accordingly
		
		This method takes a single argument:
		  target_nb          the target number."""
		
		target = self.project.get_target(target_nb)
		
		clone = target.clone()
		
		self.project.add_target(clone)
		
		self.target_grid.add_target()
		
		self.update_target_curve()
		self.update_menu()
	
	
	######################################################################
	#                                                                    #
	# execute_module                                                     #
	#                                                                    #
	######################################################################
	def execute_module(self, module, submodule, position, side, replace, parameters):
		"""Execute a module
		
		This method takes 6 arguments:
		  module             the module to execute
		  submodule          the submodule to execute
		  position           the position of the layer on which to execute
		                     the module;
		  side               the side where this layer is located;
		  replace            a boolean indicating if the layer should be
		                     replaced;
		  parameters         the parameters describing the layer."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		try:
			submodule.execute_function(filter, position, side, replace, *parameters)
		
		except Exception:
			type_of_exception, value = sys.exc_info()[:2]
			
			event = message_event(self.GetId(), "An error occured while executing submodule %s of module %s.\n\n%s." % (submodule.name, module.name, value), "Module error", wx.ICON_ERROR)
			self.GetEventHandler().AddPendingEvent(event)
		
		self.modifying = False
	
	
	######################################################################
	#                                                                    #
	# modify_layer                                                       #
	#                                                                    #
	######################################################################
	def modify_layer(self, layer_nb, side):
		"""Modify a layer
		
		This method takes 2 arguments:
		  layer_nb           the layer number;
		  side               the side where the layer is located.
		
		It shows the dialog appropriate to modify the layer (from a module
		if necessary) and modifies the layer according the the answers from
		the dialog."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		description = filter.get_layer_description(layer_nb, side)
		
		if description == []:
			# If the layer is graded and there is no description, it is
			# impossible to modify it.
			if filter.is_graded(layer_nb, side):
				return
			
			old_material_name = filter.get_layer_material_name(layer_nb, side)
			old_thickness = filter.get_layer_thickness(layer_nb, side)
			old_material = filter.get_layer_material(layer_nb, side)
			if old_material.is_mixture():
				old_index = filter.get_layer_index(layer_nb, side)
			else:
				old_index = None
			old_parameters = (old_material_name, old_thickness, old_index, 0)
			
			window = simple_layer_dialog(self, filter, old_parameters)
			answer = window.ShowModal()
			
			if answer == wx.ID_OK:
				new_parameters = window.get_parameters()
				if new_parameters != old_parameters:
					material_name = new_parameters[0]
					thickness = new_parameters[1]
					index = new_parameters[2]
					OT = new_parameters[3]
					if material_name != old_material_name:
						filter.remove_layer(layer_nb, side)
						filter.add_layer(material_name, thickness, layer_nb, side, index, OT)
					else:
						# It is important to change the index before the thickness
						# when the thickness is optical thickness.
						if index != old_index:
							filter.change_layer_index(index, layer_nb, side)
						if thickness != old_thickness:
							filter.change_layer_thickness(thickness, layer_nb, side, OT = OT)
				
				self.filter_grid.reset_filter(self.selected_filter_nb)
				if self.filter_panel.IsShown():
					if side == FRONT:
						self.front_layer_grid.reset()
					else:
						self.back_layer_grid.reset()
					self.update_index_profile_plots(side)
				
				self.delete_results(self.selected_filter_nb)
				self.update_menu()
		
		else:
			name = description[0]
			parameters = description[1]
			
			# Find wich submodule to execute.
			for module in self.modules:
				submodule = module.get_submodule_by_name(name)
				if submodule:
					break
			else:
				wx.MessageBox("The module used to design that layer is not present on this system.", "Unknown module", wx.ICON_ERROR|wx.OK)
				return
			
			try:
				window = submodule.execute_dialog(self, filter, parameters)
				answer = window.ShowModal()
				if answer == wx.ID_OK:
					new_parameters = window.get_parameters()
				
				window.Destroy()
			
			except Exception:
				type_of_exception, value = sys.exc_info()[:2]
				wx.MessageBox("An error occured while executing the submodule %s of module %s.\n\n%s." % (submodule.name, module.name, value), "Module error", wx.ICON_ERROR|wx.OK)
				return
			
			if answer == wx.ID_OK and new_parameters != parameters:
				self.modifying = True
				self.update_menu()
				self.update_status_bar()
				self.update_cursor()
				self.update_grids()
				
				monitoring_thread = threading.Thread(target = self.monitor_modification_progress, args = (self.selected_filter_nb, ))
				monitoring_thread.start()
				
				work_thread = threading.Thread(target = self.execute_module, args = (module, submodule, layer_nb, side, True, new_parameters))
				work_thread.start()
	
	
	######################################################################
	#                                                                    #
	# calculate                                                          #
	#                                                                    #
	######################################################################
	def calculate(self, filter_nb, method, parameters, holder):
		"""Calculate a property of a filter
		
		This function takes 4 input arguments:
		  filter_nb          the filter nb;
		  method             the method of the filter class that must be
		                     used to obtain the property;
		  parameters         the parameters to pass to the method;
		  holder             an appropriate data holder to hold the data.
		
		When the calculation is finished, a data event is generated instead
		of directly adding the data to the window, which makes this method
		thread safe."""
		
		filter = self.project.get_filter(filter_nb)
		
		answer = method(filter, *parameters)
		
		if answer:
			data = holder(filter, answer, *parameters)
			
			event = data_event(self.GetId(), filter_nb, data)
			self.GetEventHandler().AddPendingEvent(event)
		
		self.calculating = False
	
	
	######################################################################
	#                                                                    #
	# monitor_modification_progress                                      #
	#                                                                    #
	######################################################################
	def monitor_modification_progress(self, filter_nb):
		"""Monitor the progress of a modification
		
		This method takes a single argument:
		  filter_nb      the number of the filter that is being modified.
		
		This method sends progress event regularly to update the progress
		bar instead of updating it itself, which makes this method thread
		safe."""
		
		id = self.GetId()
		event_handler = self.GetEventHandler()
		
		while self.modifying:
			event = progress_event(id)
			event_handler.AddPendingEvent(event)
			
			time.sleep(config.CALCULATION_MIN_UPDATE_DELAY)
		
		event = update_event(id, UPDATE_MENU|UPDATE_STATUS_BAR|UPDATE_CURSOR|UPDATE_FILTER|UPDATE_GRIDS)
		event_handler.AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# monitor_calculation_progress                                       #
	#                                                                    #
	######################################################################
	def monitor_calculation_progress(self, filter_nb):
		"""Monitor the progress of a calculation
		
		This method takes a single argument:
		  filter_nb      the number of the filter that is doing the
		                 calculations.
		
		This method sends progress event regularly to update the progress
		bar instead of updating it itself, which makes this method thread
		safe."""
		
		filter = self.project.get_filter(filter_nb)
		
		id = self.GetId()
		event_handler = self.GetEventHandler()
		
		while self.calculating:
			progress = filter.get_progress()
			
			event = progress_event(id, progress)
			event_handler.AddPendingEvent(event)
			
			time.sleep(config.CALCULATION_MIN_UPDATE_DELAY)
		
		event = update_event(id, UPDATE_MENU|UPDATE_STATUS_BAR|UPDATE_CURSOR|UPDATE_GRIDS)
		event_handler.AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# show_data                                                          #
	#                                                                    #
	######################################################################
	def show_data(self, data, filter_nb):
		"""Show data
		
		Add the data to the appropriate tab in the lower notebook. This
		method takes 2 argument:
		  data               the data;
		  filter_nb          the number of the filter the data belongs to;
		and returns:
		  page_nb            the page on which the data is shown;
		  curve_nb           the number of the curve on the page."""
		
		filter = self.project.get_filter(filter_nb)
		
		type = data.get_data_type()
		
		if type == data_holder.REFLECTION:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			R = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "R%s %s deg. %s" % ("_reverse" if direction == BACKWARD else "", angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, R, name = title)
			curve_nb = self.photometry_plot.add_curve(curve)
			page_nb = self.photometry_plot_page_nb
		
		elif type == data_holder.TRANSMISSION:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			T = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "T%s %s deg. %s" % ("_reverse" if direction == BACKWARD else "", angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, T, name = title)
			curve_nb = self.photometry_plot.add_curve(curve)
			page_nb = self.photometry_plot_page_nb
		
		elif type == data_holder.ABSORPTION:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			A = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "A%s %s deg. %s" % ("_reverse" if direction == BACKWARD else "", angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, A, name = title)
			curve_nb = self.photometry_plot.add_curve(curve)
			page_nb = self.photometry_plot_page_nb
		
		elif type == data_holder.REFLECTION_PHASE:
			wavelengths = data.get_wavelengths()
			phase = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "phi_r %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, phase, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.TRANSMISSION_PHASE:
			wavelengths = data.get_wavelengths()
			phase = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "phi_t %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, phase, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.REFLECTION_GD:
			wavelengths = data.get_wavelengths()
			GD = [GD_i*1.0e15 for GD_i in data.get_data()]
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "GD_r %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, GD, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.TRANSMISSION_GD:
			wavelengths = data.get_wavelengths()
			GD = [GD_i*1.0e15 for GD_i in data.get_data()]
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "GD_t %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, GD, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.REFLECTION_GDD:
			wavelengths = data.get_wavelengths()
			GDD = [GDD_i*1.0e30 for GDD_i in data.get_data()]
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "GDD_r %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, GDD, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.TRANSMISSION_GDD:
			wavelengths = data.get_wavelengths()
			GDD = [GDD_i*1.0e30 for GDD_i in data.get_data()]
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "GDD_t %s deg. %s" % (angle, polarization_text(polarization))
			curve = GUI_plot.plot_curve(wavelengths, GDD, name = title)
			curve_nb = self.phase_plot.add_curve(curve)
			page_nb = self.phase_plot_page_nb
		
		elif type == data_holder.ELLIPSOMETRY:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			Psi, Delta = data.get_data()
			angle = data.get_angle()
			title = "Psi and Delta %s%s deg." % ("reverse " if direction == BACKWARD else "", angle)
			curve_Psi = GUI_plot.plot_curve(wavelengths, Psi, name = "Psi")
			curve_Delta = GUI_plot.plot_curve(wavelengths, Delta, name = "Delta")
			curve = GUI_plot.plot_curve_multiple([curve_Psi, curve_Delta], title)
			curve.select_curve(0)
			curve.select_curve(1)
			curve_nb = self.ellipso_plot.add_curve(curve)
			page_nb = self.ellipso_plot_page_nb
		
		elif type == data_holder.COLOR:
			direction = data.get_direction()
			R_color, T_color = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			illuminant = data.get_illuminant()
			observer = data.get_observer()
			title = "%s%s deg. %s (%s, %s)" % ("Reverse " if direction == BACKWARD else "", angle, polarization_text(polarization), illuminant, observer)
			curve_nb = self.color_window.add_color_panel(title, R_color, T_color)
			page_nb = self.color_window_page_nb
		
		elif type == data_holder.COLOR_TRAJECTORY:
			direction = data.get_direction()
			R_colors, T_colors = data.get_data()
			angles = data.get_angles()
			polarization = data.get_polarization()
			illuminant = data.get_illuminant()
			observer = data.get_observer()
			title = "%s%s to %s deg. %s (%s, %s)" % ("Reverse " if direction == BACKWARD else "", min(angles), max(angles), polarization_text(polarization), illuminant, observer)
			curve_nb = self.color_window.add_color_trajectory_panel(title, angles, R_colors, T_colors)
			page_nb = self.color_window_page_nb
		
		elif type == data_holder.ADMITTANCE:
			wavelength = data.get_wavelength()
			thickness, real_part, imag_part = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "%s deg. %s nm %s" % (angle, wavelength, polarization_text(polarization))
			curve = GUI_plot.plot_curve_segmented(real_part, imag_part, name = title)
			curve_nb = self.admittance_plot.add_curve(curve)
			page_nb = self.admittance_plot_page_nb
		
		elif type == data_holder.CIRCLE:
			wavelength = data.get_wavelength()
			thickness, real_part, imag_part = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "%s deg. %s nm %s" % (angle, wavelength, polarization_text(polarization))
			curve = GUI_plot.plot_curve_segmented(real_part, imag_part, name = title)
			curve_nb = self.circle_plot.add_curve(curve)
			page_nb = self.circle_plot_page_nb
		
		elif type == data_holder.ELECTRIC_FIELD:
			wavelength = data.get_wavelength()
			thickness, field = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			title = "%s deg. %s nm %s" % (angle, wavelength, polarization_text(polarization))
			curve = GUI_plot.plot_curve_segmented(thickness, field, name = title)
			curve_nb = self.electric_field_plot.add_curve(curve)
			page_nb = self.electric_field_plot_page_nb
		
		elif type == data_holder.REFLECTION_MONITORING:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			thicknesses, R = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			if len(wavelengths) == 1:
				title = "R%s %s deg. %s nm %s" % ("_reverse" if direction == BACKWARD else "", angle, wavelengths[0], polarization_text(polarization))
				curve = GUI_plot.plot_curve_segmented(thicknesses, R[0], name = title)
			else:	
				# Select the curve that will be shown. If the center wavelength
				# is a member of the spectrum, select that wavelength.
				# Otherwise, select the middle of the spectrum.
				center_wavelength = filter.get_center_wavelength()
				if center_wavelength in wavelengths:
					selected_wavelength = wavelengths.index(center_wavelength)
				else:
					selected_wavelength = len(wavelengths)//2
				
				title = "R%s %s deg. %s" % ("_reverse" if direction == BACKWARD else "", angle, polarization_text(polarization))
				curves = []
				for i_wvl in range(len(wavelengths)):
					single_curve_title = "%s nm" % (wavelengths[i_wvl])
					single_curve = GUI_plot.plot_curve_segmented(thicknesses, R[i_wvl], name = single_curve_title)
					curves.append(single_curve)
				curve = GUI_plot.plot_curve_multiple(curves, title)
				curve.select_curve(selected_wavelength)
			
			curve_nb = self.photometric_monitoring_plot.add_curve(curve)
			page_nb = self.photometric_monitoring_plot_page_nb
		
		elif type == data_holder.TRANSMISSION_MONITORING:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			thicknesses, T = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			if len(wavelengths) == 1:
				title = "T%s %s deg. %s nm %s" % ("_reverse" if direction == BACKWARD else "", angle, wavelengths[0], polarization_text(polarization))
				curve = GUI_plot.plot_curve_segmented(thicknesses, T[0], name = title)
			else:	
				# Select the curve that will be shown. If the center wavelength
				# is a member of the spectrum, select that wavelength.
				# Otherwise, select the middle of the spectrum.
				center_wavelength = filter.get_center_wavelength()
				if center_wavelength in wavelengths:
					selected_wavelength = wavelengths.index(center_wavelength)
				else:
					selected_wavelength = len(wavelengths)//2
				
				title = "T%s %s deg. %s" % ("_reverse" if direction == BACKWARD else "", angle, polarization_text(polarization))
				curves = []
				for i_wvl in range(len(wavelengths)):
					single_curve_title = "%s nm" % (wavelengths[i_wvl])
					single_curve = GUI_plot.plot_curve_segmented(thicknesses, T[i_wvl], name = single_curve_title)
					curves.append(single_curve)
				curve = GUI_plot.plot_curve_multiple(curves, title)
				curve.select_curve(selected_wavelength)
			
			curve_nb = self.photometric_monitoring_plot.add_curve(curve)
			page_nb = self.photometric_monitoring_plot_page_nb
		
		elif type == data_holder.ELLIPSOMETRY_MONITORING:
			direction = data.get_direction()
			wavelengths = data.get_wavelengths()
			thicknesses, Psi, Delta = data.get_data()
			angle = data.get_angle()
			polarization = data.get_polarization()
			if len(wavelengths) == 1:
				title = "Psi and Delta %s%s deg. %s nm" % ("reverse " if direction == BACKWARD else "", angle, wavelengths[0])
				curve_Psi = GUI_plot.plot_curve_segmented(thicknesses, Psi[0], name = "Psi")
				curve_Delta = GUI_plot.plot_curve_segmented(thicknesses, Delta[0], name = "Delta")
				curve = GUI_plot.plot_curve_multiple([curve_Psi, curve_Delta], title)
				curve.select_curve(0)
				curve.select_curve(1)
			else:	
				# Select the curve that will be shown. If the center wavelength
				# is a member of the spectrum, select that wavelength.
				# Otherwise, select the middle of the spectrum.
				center_wavelength = filter.get_center_wavelength()
				if center_wavelength in wavelengths:
					selected_wavelength = wavelengths.index(center_wavelength)
				else:
					selected_wavelength = len(wavelengths)//2
				
				title = "Psi and Delta %s%s deg." % ("reverse " if direction == BACKWARD else "", angle)
				curves = []
				for i_wvl in range(len(wavelengths)):
					single_curve_Psi_title = "Psi %s%s nm" % ("reverse " if direction == BACKWARD else "", wavelengths[i_wvl])
					single_curve_Delta_title = "Delta %s%s nm" % ("reverse " if direction == BACKWARD else "", wavelengths[i_wvl])
					single_curve_Psi = GUI_plot.plot_curve_segmented(thicknesses, Psi[i_wvl], name = single_curve_Psi_title)
					single_curve_Delta = GUI_plot.plot_curve_segmented(thicknesses, Delta[i_wvl], name = single_curve_Delta_title)
					curves.append(single_curve_Psi)
					curves.append(single_curve_Delta)
				curve = GUI_plot.plot_curve_multiple(curves, title)
				curve.select_curve(2*selected_wavelength)
				curve.select_curve(2*selected_wavelength+1)
			
			curve_nb = self.ellipso_monitoring_plot.add_curve(curve)
			page_nb = self.ellipso_monitoring_plot_page_nb
		
		return page_nb, curve_nb
	
	
	######################################################################
	#                                                                    #
	# show_results                                                       #
	#                                                                    #
	######################################################################
	def show_results(self, filter_nb):
		"""Show the results associated with a filter
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		for page_nb in range(self.nb_pages):
			if page_nb != self.color_window_page_nb:
				self.pages[page_nb].begin_batch()
			
			for data_nb in range(len(self.data[filter_nb][page_nb])):
				data_and_curve_nb = self.data[filter_nb][page_nb][data_nb]
				dummy, curve_nb = self.show_data(data_and_curve_nb[0], filter_nb)
				data_and_curve_nb[1] = curve_nb
			
			if page_nb != self.color_window_page_nb:
				self.pages[page_nb].end_batch()
	
	
	######################################################################
	#                                                                    #
	# hide_results                                                       #
	#                                                                    #
	######################################################################
	def hide_results(self, filter_nb):
		"""Hide the results associated with a filter
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		for page_nb in range(self.nb_pages):
			page = self.pages[page_nb]
			
			if page_nb == self.color_window_page_nb:
				for data_nb in range(len(self.data[filter_nb][page_nb])):
					data_and_curve_nb = self.data[filter_nb][page_nb][data_nb]
					if data_and_curve_nb[1] != -1:
						page.remove_panel(data_and_curve_nb[1])
						data_and_curve_nb[1] = -1
			
			else:
				page.begin_batch()
				
				for data_nb in range(len(self.data[filter_nb][page_nb])):
					data_and_curve_nb = self.data[filter_nb][page_nb][data_nb]
					if data_and_curve_nb[1] != -1:
						page.remove_curve(data_and_curve_nb[1])
						data_and_curve_nb[1] = -1
				
				page.end_batch()
	
	
	######################################################################
	#                                                                    #
	# delete_results                                                     #
	#                                                                    #
	######################################################################
	def delete_results(self, filter_nb = None):
		"""Delete the results associated with a filter
		
		This method takes a single argument:
		  filter_nb          the filter number."""
		
		if filter_nb is None:
			filter_nb = self.selected_filter_nb
		
		self.hide_results(filter_nb)
		
		self.data[filter_nb] = [[] for i_page in range(self.nb_pages)]
	
	
	######################################################################
	#                                                                    #
	# reset_all_pages                                                    #
	#                                                                    #
	######################################################################
	def reset_all_pages(self):
		"""Reset all the result pages"""
		
		for page in self.pages:
			page.reset()
	
	
	######################################################################
	#                                                                    #
	# update                                                             #
	#                                                                    #
	######################################################################
	def update(self, what = UPDATE_ALL):
		"""Update the window
		
		This method is thread safe. It only sends an event that will really
		takes care of the update.
		
		It takes an optional argument:
		  what          (optional) what to update, default is UPDATE_ALL."""
		
		event = update_event(self.GetId(), what)
		self.GetEventHandler().AddPendingEvent(event)
	
	
	######################################################################
	#                                                                    #
	# update_title                                                       #
	#                                                                    #
	######################################################################
	def update_title(self):
		"""Update the title bar
		
		Set the title bar according to the project filename."""
		
		if self.project_filename :
			self.SetTitle("OpenFilters - %s" % self.project_filename)
		else:
			self.SetTitle("OpenFilters")
	
	
	######################################################################
	#                                                                    #
	# update_index_profile_plots                                         #
	#                                                                    #
	######################################################################
	def update_index_profile_plots(self, side = BOTH):
		"""Update the index profile plots
		
		This method takes a single optional argument:
		  side       the side(s) of the index profile to update (FRONT,
		             BACK or BOTH), the default value is BOTH."""
		
		filter = self.project.get_filter(self.selected_filter_nb)
		
		if side == FRONT or side == BOTH:
			if filter.get_nb_layers(FRONT):
				thickness, profile = filter.get_index_profile(FRONT)
				curve = GUI_plot.plot_curve(thickness, profile)
				self.front_index_profile_plot.reset(curve)
			else:
				self.front_index_profile_plot.reset()
		
		if side == BACK or side == BOTH:
			if filter.get_nb_layers(BACK):
				thickness, profile = filter.get_index_profile(BACK)
				curve = GUI_plot.plot_curve(thickness, profile)
				self.back_index_profile_plot.reset(curve)
			else:
				self.back_index_profile_plot.reset()
	
	
	######################################################################
	#                                                                    #
	# update_target_curve                                                #
	#                                                                    #
	######################################################################
	def update_target_curve(self):
		"""Update the target curve"""
		
		for i_page in range(self.nb_pages):
			if self.target_curve_nbs[i_page] >= 0:
				self.pages[i_page].remove_curve(self.target_curve_nbs[i_page])
				self.target_curve_nbs[i_page] = -1
		
		if self.project:
			if self.analyse_menu.IsChecked(self.show_targets_ID):
				curves = [[] for i_page in range(self.nb_pages)]
				for i_target in range(len(self.project.get_targets())):
					target = self.project.get_target(i_target)
					kind = target.get_kind()
					
					if kind in targets.PHOTOMETRIC_TARGETS or kind in targets.DISPERSIVE_TARGETS:
						wavelength, values, deltas = target.get_values()
						inequality = target.get_inequality()
						if inequality == targets.LARGER:
							style = GUI_plot.plot_curve_style("Black", 1, "^", 3)
						elif inequality == targets.SMALLER:
							style = GUI_plot.plot_curve_style("Black", 1, "v", 3)
						else:
							style = GUI_plot.plot_curve_style("Black", 1, "x", 3)
						if kind in targets.PHOTOMETRIC_TARGETS:
							single_curve = GUI_plot.plot_curve(wavelength, values, style = style)
							curves[self.photometry_plot_page_nb].append(single_curve)
						elif kind in targets.DISPERSIVE_TARGETS:
							if kind in [targets.R_GD_TARGET, targets.R_GD_SPECTRUM_TARGET, targets.T_GD_TARGET, targets.T_GD_SPECTRUM_TARGET]:
								values = [value * 1.0e15 for value in values]
							elif kind in [targets.R_GDD_TARGET, targets.R_GDD_SPECTRUM_TARGET, targets.T_GDD_TARGET, targets.T_GDD_SPECTRUM_TARGET]:
								values = [value * 1.0e30 for value in values]
							single_curve = GUI_plot.plot_curve(wavelength, values, style = style)
							curves[self.phase_plot_page_nb].append(single_curve)
				
				for i_page in range(self.nb_pages):
					if curves[i_page]:
						curve = GUI_plot.plot_curve_multiple(curves[i_page])
						for i_curve in range(len(curves[i_page])):
							curve.select_curve(i_curve)
						self.target_curve_nbs[i_page] = self.pages[i_page].add_curve(curve)
	
	
	######################################################################
	#                                                                    #
	# update_recently_opened_projects                                    #
	#                                                                    #
	######################################################################
	def update_recently_opened_projects(self):
		"""Update the menu according to the list of recently opened projects."""
		
		for id in self.recently_opened_project_IDs:
			if self.file_menu.FindItemById(id):
				self.file_menu.Delete(id)
		
		for i, filename in enumerate(self.recently_opened_projects):
			if i >= config.NB_RECENTLY_OPENED_PROJECTS:
				break
			
			# Try to make the item length reasonable.
			reasonable_length = 50
			if len(filename) > reasonable_length:
				drive, tail = os.path.splitdrive(filename)
				head, item = os.path.split(tail)
				while head:
					head, tail = os.path.split(head)
					if 2 + len(tail) + 1 + len(item) < reasonable_length:
						item = os.path.join(tail, item)
					else:
						break
				item = os.path.join(drive, "...", item)
			else:
				item = filename
			
			# Add digit shortcuts to the first 10 recently opened projects.
			if i < 10:
				item = "&%i %s" % (i+1, item)
			
			self.file_menu.Insert(self.recently_opened_project_starting_position+i, self.recently_opened_project_IDs[i], item)
	
	
	######################################################################
	#                                                                    #
	# update_menu                                                        #
	#                                                                    #
	######################################################################
	def update_menu(self):
		"""Update the menu
		
		Adjust the menu according to the current state of the software."""
		
		selected_page_nb = self.lower_notebook.GetSelection()
		if self.project:
			nb_filters = self.project.get_nb_filters()
			nb_targets = self.project.get_nb_targets()
		else:
			nb_filters = 0
			nb_targets = 0
		
		if nb_filters:
			selected_filter = self.project.get_filter(self.selected_filter_nb)
			nb_layers = selected_filter.get_nb_layers(FRONT)
			if self.analyse_menu.IsChecked(self.show_all_results_ID):
				nb_curves = 0
				for i_filter in range(nb_filters):
					nb_curves += len(self.data[i_filter][selected_page_nb])
			else:
				nb_curves = len(self.data[self.selected_filter_nb][selected_page_nb])
		else:
			selected_filter = None
			nb_layers = 0
			nb_curves = 0
		
		if self.modifying:
			self.main_menu.EnableTop(self.file_menu_nb, False)
		else:
			self.main_menu.EnableTop(self.file_menu_nb, True)
			if self.project:
				self.main_menu.Enable(self.new_project_ID, False)
				self.main_menu.Enable(self.open_project_ID, False)
				if self.calculating:
					self.main_menu.Enable(self.close_project_ID, False)
					self.main_menu.Enable(wx.ID_EXIT, False)
				else:
					self.main_menu.Enable(self.close_project_ID, True)
					self.main_menu.Enable(wx.ID_EXIT, True)
				self.main_menu.Enable(self.save_project_as_ID, True)
				if self.project.get_modified():
					self.main_menu.Enable(self.save_project_ID, True)
					if self.calculating or not self.project_filename:
						self.main_menu.Enable(self.revert_ID, False)
					else:
						self.main_menu.Enable(self.revert_ID, True)
				else:
					self.main_menu.Enable(self.save_project_ID, False)
					self.main_menu.Enable(self.revert_ID, False)
				for id in self.recently_opened_project_IDs:
					if self.file_menu.FindItemById(id):
						self.main_menu.Enable(id, False)
			else:
				self.main_menu.Enable(self.new_project_ID, True)
				self.main_menu.Enable(self.open_project_ID, True)
				self.main_menu.Enable(self.save_project_ID, False)
				self.main_menu.Enable(self.save_project_as_ID, False)
				self.main_menu.Enable(self.revert_ID, False)
				self.main_menu.Enable(self.close_project_ID, False)
				self.main_menu.Enable(wx.ID_EXIT, True)
				for id in self.recently_opened_project_IDs:
					if self.file_menu.FindItemById(id):
						self.main_menu.Enable(id, True)
		
		if self.project and not self.modifying and not self.calculating:
			self.main_menu.EnableTop(self.project_menu_nb, True)
			self.main_menu.Enable(self.add_filter_ID, True)
			if selected_filter:
				self.main_menu.Enable(self.remove_filter_ID, True)
				if self.filter_panel.IsShown():
					self.main_menu.Enable(self.modify_filter_ID, False)
				else:
					self.main_menu.Enable(self.modify_filter_ID, True)
				self.main_menu.Enable(self.copy_filter_ID, True)
			else:
				self.main_menu.Enable(self.remove_filter_ID, False)
				self.main_menu.Enable(self.modify_filter_ID, False)
				self.main_menu.Enable(self.copy_filter_ID, False)
			self.main_menu.Enable(self.add_reflection_target_ID, True)
			self.main_menu.Enable(self.add_transmission_target_ID, True)
			self.main_menu.Enable(self.add_reflection_spectrum_target_ID, True)
			self.main_menu.Enable(self.add_transmission_spectrum_target_ID, True)
			self.main_menu.Enable(self.add_reflection_color_target_ID, True)
			self.main_menu.Enable(self.add_transmission_color_target_ID, True)
			if nb_targets:
				self.main_menu.Enable(self.remove_target_ID, True)
				self.main_menu.Enable(self.modify_target_ID, True)
				self.main_menu.Enable(self.copy_target_ID, True)
			else:
				self.main_menu.Enable(self.remove_target_ID, False)
				self.main_menu.Enable(self.modify_target_ID, False)
				self.main_menu.Enable(self.copy_target_ID, False)
		else:
			self.main_menu.EnableTop(self.project_menu_nb, False)
		
		if selected_filter and not self.modifying and not self.calculating:
			self.main_menu.EnableTop(self.filter_menu_nb, True)
			self.main_menu.Enable(self.filter_properties_ID, True)
			self.main_menu.Enable(self.add_layer_ID, True)
			if selected_filter.get_nb_layers(BOTH):
				self.main_menu.Enable(self.remove_layer_ID, True)
				self.main_menu.Enable(self.convert_layers_ID, True)
				self.main_menu.Enable(self.swap_sides_ID, True)
			else:
				self.main_menu.Enable(self.remove_layer_ID, False)
				self.main_menu.Enable(self.convert_layers_ID, False)
				self.main_menu.Enable(self.swap_sides_ID, False)
			if selected_filter.get_nb_layers(FRONT) > 1 or selected_filter.get_nb_layers(BACK) > 1:
				self.main_menu.Enable(self.merge_layers_ID, True)
			else:
				self.main_menu.Enable(self.merge_layers_ID, False)
			if selected_filter.get_nb_layers(FRONT):
				self.main_menu.Enable(self.export_front_index_profile_ID, True)
			else:
				self.main_menu.Enable(self.export_front_index_profile_ID, False)
			if selected_filter.get_nb_layers(BACK):
				self.main_menu.Enable(self.export_back_index_profile_ID, True)
			else:
				self.main_menu.Enable(self.export_back_index_profile_ID, False)
		else:
			self.main_menu.EnableTop(self.filter_menu_nb, False)
		
		if selected_filter and not self.modifying and not self.calculating:
			self.main_menu.Enable(self.calculate_reflection_ID, True)
			self.main_menu.Enable(self.calculate_transmission_ID, True)
			self.main_menu.Enable(self.calculate_absorption_ID, True)
			self.main_menu.Enable(self.calculate_reflection_phase_ID, True)
			self.main_menu.Enable(self.calculate_transmission_phase_ID, True)
			self.main_menu.Enable(self.calculate_reflection_GD_ID, True)
			self.main_menu.Enable(self.calculate_transmission_GD_ID, True)
			self.main_menu.Enable(self.calculate_reflection_GDD_ID, True)
			self.main_menu.Enable(self.calculate_transmission_GDD_ID, True)
			self.main_menu.Enable(self.calculate_ellipsometry_ID, True)
			self.main_menu.Enable(self.calculate_color_ID, True)
			self.main_menu.Enable(self.calculate_color_trajectory_ID, True)
			if nb_layers:
				self.main_menu.Enable(self.calculate_admittance_ID, True)
				self.main_menu.Enable(self.calculate_circle_ID, True)
				self.main_menu.Enable(self.calculate_electric_field_ID, True)
				self.main_menu.Enable(self.calculate_reflection_monitoring_ID, True)
				self.main_menu.Enable(self.calculate_transmission_monitoring_ID, True)
				self.main_menu.Enable(self.calculate_ellipsometry_monitoring_ID, True)
			else:
				self.main_menu.Enable(self.calculate_admittance_ID, False)
				self.main_menu.Enable(self.calculate_circle_ID, False)
				self.main_menu.Enable(self.calculate_electric_field_ID, False)
				self.main_menu.Enable(self.calculate_reflection_monitoring_ID, False)
				self.main_menu.Enable(self.calculate_transmission_monitoring_ID, False)
				self.main_menu.Enable(self.calculate_ellipsometry_monitoring_ID, False)
			self.main_menu.Enable(self.reverse_direction_menu_ID, True)
			self.main_menu.Enable(self.calculate_reflection_reverse_ID, True)
			self.main_menu.Enable(self.calculate_transmission_reverse_ID, True)
			self.main_menu.Enable(self.calculate_absorption_reverse_ID, True)
			self.main_menu.Enable(self.calculate_ellipsometry_reverse_ID, True)
			self.main_menu.Enable(self.calculate_color_reverse_ID, True)
			self.main_menu.Enable(self.calculate_color_trajectory_reverse_ID, True)
			if nb_layers:
				self.main_menu.Enable(self.calculate_reflection_monitoring_reverse_ID, True)
				self.main_menu.Enable(self.calculate_transmission_monitoring_reverse_ID, True)
				self.main_menu.Enable(self.calculate_ellipsometry_monitoring_reverse_ID, True)
			else:
				self.main_menu.Enable(self.calculate_reflection_monitoring_reverse_ID, False)
				self.main_menu.Enable(self.calculate_transmission_monitoring_reverse_ID, False)
				self.main_menu.Enable(self.calculate_ellipsometry_monitoring_reverse_ID, False)
			if nb_curves:
				self.main_menu.Enable(self.export_results_as_text_ID, True)
				if selected_page_nb == self.color_window_page_nb:
					self.main_menu.Enable(self.export_results_as_figure_ID, False)
				else:
					self.main_menu.Enable(self.export_results_as_figure_ID, True)
			else:
				self.main_menu.Enable(self.export_results_as_text_ID, False)
				self.main_menu.Enable(self.export_results_as_text_ID, False)
		else:
			self.main_menu.Enable(self.calculate_reflection_ID, False)
			self.main_menu.Enable(self.calculate_transmission_ID, False)
			self.main_menu.Enable(self.calculate_absorption_ID, False)
			self.main_menu.Enable(self.calculate_reflection_phase_ID, False)
			self.main_menu.Enable(self.calculate_transmission_phase_ID, False)
			self.main_menu.Enable(self.calculate_reflection_GD_ID, False)
			self.main_menu.Enable(self.calculate_transmission_GD_ID, False)
			self.main_menu.Enable(self.calculate_reflection_GDD_ID, False)
			self.main_menu.Enable(self.calculate_transmission_GDD_ID, False)
			self.main_menu.Enable(self.calculate_ellipsometry_ID, False)
			self.main_menu.Enable(self.calculate_color_ID, False)
			self.main_menu.Enable(self.calculate_color_trajectory_ID, False)
			self.main_menu.Enable(self.calculate_admittance_ID, False)
			self.main_menu.Enable(self.calculate_circle_ID, False)
			self.main_menu.Enable(self.calculate_electric_field_ID, False)
			self.main_menu.Enable(self.calculate_reflection_monitoring_ID, False)
			self.main_menu.Enable(self.calculate_transmission_monitoring_ID, False)
			self.main_menu.Enable(self.calculate_ellipsometry_monitoring_ID, False)
			self.main_menu.Enable(self.reverse_direction_menu_ID, False)
			self.main_menu.Enable(self.calculate_reflection_reverse_ID, False)
			self.main_menu.Enable(self.calculate_transmission_reverse_ID, False)
			self.main_menu.Enable(self.calculate_absorption_reverse_ID, False)
			self.main_menu.Enable(self.calculate_ellipsometry_reverse_ID, False)
			self.main_menu.Enable(self.calculate_color_reverse_ID, False)
			self.main_menu.Enable(self.calculate_color_trajectory_reverse_ID, False)
			self.main_menu.Enable(self.calculate_reflection_monitoring_reverse_ID, False)
			self.main_menu.Enable(self.calculate_transmission_monitoring_reverse_ID, False)
			self.main_menu.Enable(self.calculate_ellipsometry_monitoring_reverse_ID, False)
			self.main_menu.Enable(self.export_results_as_text_ID, False)
			self.main_menu.Enable(self.export_results_as_figure_ID, False)
		self.main_menu.Enable(self.show_targets_ID, True)
		self.main_menu.Enable(self.show_all_results_ID, True)
		
		if not self.modifying and not self.calculating and nb_targets:
			self.main_menu.EnableTop(self.optimize_menu_nb, True)
			if nb_layers:
				self.main_menu.Enable(self.optimize_refinement_ID, True)
				self.main_menu.Enable(self.optimize_needles_ID, True)
				self.main_menu.Enable(self.optimize_steps_ID, True)
			else:
				self.main_menu.Enable(self.optimize_refinement_ID, False)
				self.main_menu.Enable(self.optimize_needles_ID, False)
				self.main_menu.Enable(self.optimize_steps_ID, False)
			if self.project.get_nb_targets(targets.R_SPECTRUM_TARGET):
				self.main_menu.Enable(self.design_Fourier_ID, True)
			else:
				self.main_menu.Enable(self.design_Fourier_ID, False)
		else:
			self.main_menu.EnableTop(self.optimize_menu_nb, False)
		
		if selected_filter and not self.modifying and not self.calculating:
			if nb_layers:
				self.main_menu.EnableTop(self.preproduction_menu_nb, True)
				self.main_menu.Enable(self.random_errors_ID, True)
			else:
				self.main_menu.EnableTop(self.preproduction_menu_nb, False)
				self.main_menu.Enable(self.random_errors_ID, False)
		else:
			self.main_menu.EnableTop(self.preproduction_menu_nb, False)
		
		if self.modifying or self.calculating:
			self.main_menu.EnableTop(self.materials_menu_nb, False)
			self.main_menu.Enable(self.manage_materials_ID, False)
			self.main_menu.Enable(self.example_menu_ID, False)
		else:
			self.main_menu.EnableTop(self.materials_menu_nb, True)
			self.main_menu.Enable(self.manage_materials_ID, True)
			if self.project:
				self.main_menu.Enable(self.change_user_material_directory_ID, False)
			else:
				self.main_menu.Enable(self.change_user_material_directory_ID, True)
		
		if self.project:
			self.main_menu.Enable(self.example_menu_ID, False)
		else:
			self.main_menu.Enable(self.example_menu_ID, True)
		
	
	######################################################################
	#                                                                    #
	# update_status_bar                                                  #
	#                                                                    #
	######################################################################
	def update_status_bar(self):
		"""Update the status bar
		
		Reposition the cancel button and the gauge in the status bar."""
		
		if self.calculating:
			
			# If the window is not maximized, we do a field for the sizing icon
			# at the right corner.
			if self.IsMaximized():
				self.status_bar.SetFieldsCount(2)
				self.status_bar.SetStatusWidths([-1, 154])
			else:
				self.status_bar.SetFieldsCount(3)
				self.status_bar.SetStatusWidths([-1, 154, 20])
			
			# Get the size of the second field.
			rect = self.status_bar.GetFieldRect(1)
			
			# Position the cancel button
			self.cancel_button.SetPosition((rect.x+1, rect.y))
			self.cancel_button.SetSize((50, rect.height))
			
			# Position the gauge.
			self.gauge.SetPosition((rect.x+52, rect.y))
			self.gauge.SetSize((100, rect.height))
			
			self.cancel_button.Show()
			self.gauge.Show()
		
		elif self.modifying:
			
			# If the window is not maximized, we do a field for the sizing icon
			# at the right corner.
			if self.IsMaximized():
				self.status_bar.SetFieldsCount(2)
				self.status_bar.SetStatusWidths([-1, 102])
			else:
				self.status_bar.SetFieldsCount(3)
				self.status_bar.SetStatusWidths([-1, 102, 20])
			
			# Get the size of the second field.
			rect = self.status_bar.GetFieldRect(1)
			
			# Position the gauge.
			self.gauge.SetPosition((rect.x+1, rect.y))
			self.gauge.SetSize((100, rect.height))
			
			self.gauge.Show()
		
		else:
			self.status_bar.SetFieldsCount(1)
			
			self.cancel_button.Hide()
			self.gauge.Hide()
	
	
	######################################################################
	#                                                                    #
	# update_cursor                                                      #
	#                                                                    #
	######################################################################
	def update_cursor(self):
		"""Update the cursor
		
		Adjust the cursor according to the current state of the software."""
		
		if self.modifying or self.calculating:
			self.SetCursor(wx.StockCursor(wx.CURSOR_ARROWWAIT))
		else:
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
	
	
	######################################################################
	#                                                                    #
	# update_grids                                                       #
	#                                                                    #
	######################################################################
	def update_grids(self):
		"""Update the grids
		
		Adjust the grids according to the current state of the software."""
		
		if self.modifying or self.calculating:
			self.filter_grid.set_allow_modifications(False)
			self.target_grid.set_allow_modifications(False)
			self.front_layer_grid.set_allow_modifications(False)
			self.back_layer_grid.set_allow_modifications(False)
		else:
			self.filter_grid.set_allow_modifications(True)
			self.target_grid.set_allow_modifications(True)
			self.front_layer_grid.set_allow_modifications(True)
			self.back_layer_grid.set_allow_modifications(True)



########################################################################
#                                                                      #
# polarization_text                                                    #
#                                                                      #
########################################################################
def polarization_text(polarization):
	"""Get a textual representation of the polarization
	
	This function takes a single argument:
	  polarization         the polarization;
	and returns a text to describe it.
	
	A special text is returned for s, p or unpolarized light."""
	
	if polarization == S:
		return "s-pol."
	
	elif polarization == P:
		return "p-pol."
	
	elif polarization == UNPOLARIZED:
		return "unpol."
	
	else:
		return "pol.: %.2f deg." % polarization
