# GUI_color.py
# 
# Panel for the colors properties in the GUI of Filters.
# 
# Copyright (c) 2005-2009,2013,2015 Stephane Larouche.
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



# REMOVE when Python 3.0 will be out.
from __future__ import division

import wx

import color
from moremath import interpolation

import GUI_plot



# Default behaviour is to use buffered drawing.
use_buffered_drawing = True



########################################################################
#                                                                      #
# color_window                                                         #
#                                                                      #
########################################################################
class color_window(wx.Panel):
	"""A class for the color tab in the main window"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent):
		"""Initialize an instance of the color window
		
		This method takes a single argument:
		  parent             the window's parent."""
		
		wx.Panel.__init__(self, parent, -1, (-1, -1))
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(main_sizer)
		
		self.panel_window = wx.ScrolledWindow(self, -1, (-1, -1), style = wx.VSCROLL)
		
		self.panel_window.SetScrollbars(20, 20, 50, 50)
		self.panel_window_sizer = wx.BoxSizer(wx.VERTICAL)
		self.panel_window.SetSizer(self.panel_window_sizer)
		
		main_sizer.Add(self.panel_window, 1, wx.EXPAND)
		
		self.panels = []
		
		self.panel_window.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		# Prepare context menu.
		self.context_menu = wx.Menu()
		self.rename_panel_ID = wx.NewId()
		self.context_menu.Append(self.rename_panel_ID, "&Rename")
		self.Bind(wx.EVT_MENU, self.on_rename_panel, id = self.rename_panel_ID)
		self.remove_panel_ID = wx.NewId()
		self.context_menu.Append(self.remove_panel_ID, "&Remove panel")
		self.Bind(wx.EVT_MENU, self.on_remove_panel, id = self.remove_panel_ID)
		self.context_menu.AppendSeparator()
		self.remove_all_panels_ID = wx.NewId()
		self.context_menu.Append(self.remove_all_panels_ID, "Remove &all panels")
		self.Bind(wx.EVT_MENU, self.on_remove_all_panels, id = self.remove_all_panels_ID)
	
	
	######################################################################
	#                                                                    #
	# add_color_panel                                                    #
	#                                                                    #
	######################################################################
	def add_color_panel(self, title, R_color, T_color):
		"""Add a color panel to the window
		
		This method takes 3 arguments:
		  title              the title of the panel;
		  R_color            a color object for the reflection color;
		  T_color            a color object for the transmission color.
		
		It returns the number of the panel"""
		
		panel = color_panel(self.panel_window, title, R_color, T_color)
		
		self.panels.append(panel)
		
		self.panel_window_sizer.Add(panel, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.Layout()
		
		return self.panels.index(panel)
	
	
	######################################################################
	#                                                                    #
	# add_color_trajectory_panel                                         #
	#                                                                    #
	######################################################################
	def add_color_trajectory_panel(self, title, angles, R_colors, T_colors):
		"""Add a color trajectory panel to the window
		
		This method takes 3 arguments:
		  title              the title of the panel;
		  R_colors           color objects for the reflection colors;
		  T_colors           color objects for the transmission colors.
		
		It returns the number of the panel"""
		
		panel = color_trajectory_panel(self.panel_window, title, angles, R_colors, T_colors)
		
		self.panels.append(panel)
		
		self.panel_window_sizer.Add(panel, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.Layout()
		
		return self.panels.index(panel)
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Remove all the panels from the window"""
		
		for i in range(len(self.panels)):
			if self.panels[i]:
				self.panel_window_sizer.Remove(self.panels[i])
				self.panels[i].Destroy()
				self.panels[i] = None
		
		self.Layout()
	
	
	######################################################################
	#                                                                    #
	# remove_panel                                                       #
	#                                                                    #
	######################################################################
	def remove_panel(self, nb):
		"""Remove a single panel from the window
		
		This method takes a single argument:
		  nb                 the number of the panel."""
		
		self.panel_window_sizer.Remove(self.panels[nb])
		self.panels[nb].Destroy()
		self.panels[nb] = None
		
		self.Layout()
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Handle right click events
		
		This method takes a single argument:
		  event              the event.
		
		It shows a menu proposing to rename a panel, to remove one or all
		panels."""
		
		clicked_panel = event.GetEventObject()
		
		try:
			self.clicked_panel_nb = self.panels.index(clicked_panel)
		except ValueError:
			self.clicked_panel_nb = -1
		
		if self.clicked_panel_nb != -1:
			self.context_menu.Enable(self.rename_panel_ID, True)
			self.context_menu.Enable(self.remove_panel_ID, True)
		else:
			self.context_menu.Enable(self.rename_panel_ID, False)
			self.context_menu.Enable(self.remove_panel_ID, False)
		if any(self.panels):
			self.context_menu.Enable(self.remove_all_panels_ID, True)
		else:
			self.context_menu.Enable(self.remove_all_panels_ID, False)
		
		# Show the menu.
		self.PopupMenu(self.context_menu)
	
	
	######################################################################
	#                                                                    #
	# on_remove_panel                                                    #
	#                                                                    #
	######################################################################
	def on_remove_panel(self, event):
		"""Handle menu event when the remove panel item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It removes the panel and sends a remove_curve_event to the parent
		window."""
		
		self.remove_panel(self.clicked_panel_nb)
		
		event = GUI_plot.remove_curve_event(self.GetId(), self.clicked_panel_nb)
		self.GetEventHandler().ProcessEvent(event)
	
	
	######################################################################
	#                                                                    #
	# on_rename_panel                                                    #
	#                                                                    #
	######################################################################
	def on_rename_panel(self, event):
		"""Handle menu event when the rename panel item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It changes the name of the panel."""
		
		self.rename(self.clicked_panel_nb)
	
	
	######################################################################
	#                                                                    #
	# rename                                                             #
	#                                                                    #
	######################################################################
	def rename(self, panel_nb):
		"""Rename a panel
		
		This method takes a single argument:
		  panel_nb           the number of the panel.
		
		It shows a renaming dialog."""
		
		old_title = self.panels[panel_nb].get_title()
		
		window = GUI_plot.rename_dialog(self, old_title)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			new_title = window.get_name()
			self.panels[panel_nb].set_title(new_title)
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# on_remove_all_panels                                               #
	#                                                                    #
	######################################################################
	def on_remove_all_panels(self, event):
		"""Handle menu event when the remove all panels item is selected
		
		This method takes a single argument:
		  event              the event.
		
		It removes all the panels. It also sends remove_panel_event's to
		the parent window."""
		
		for panel_nb, panel in enumerate(self.panels):
			if panel:
				self.remove_panel(panel_nb)
				
				event = GUI_plot.remove_curve_event(self.GetId(), panel_nb)
				self.GetEventHandler().ProcessEvent(event)



########################################################################
#                                                                      #
# color_panel                                                          #
#                                                                      #
########################################################################
class color_panel(wx.Panel):
	"""A class for panels to show the color"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, title, R_color, T_color):
		"""Initialize an instance of the panel
		
		This method takes 4 arguments:
		  parent             the panel's parent;
		  title              the title of the panel;
		  R_color            a color object for the reflection color;
		  T_color            a color object for the transmission color."""
		
		self.title = title
		self.R_color = R_color
		self.T_color = T_color
		
		wx.Panel.__init__(self, parent, style = wx.NO_BORDER)
		
		# Get the color in interresting color coordinates.
		XYZ_R = R_color.XYZ()
		xyY_R = R_color.xyY()
		Luv_R = R_color.Luv()
		Lab_R = R_color.Lab()
		LChuv_R = R_color.LChuv()
		LChab_R = R_color.LChab()
		RGB_R = R_color.RGB()
		error_RGB_R = R_color.get_RGB_error()
		XYZ_T = T_color.XYZ()
		xyY_T = T_color.xyY()
		Luv_T = T_color.Luv()
		Lab_T = T_color.Lab()
		LChuv_T = T_color.LChuv()
		LChab_T = T_color.LChab()
		RGB_T = T_color.RGB()
		error_RGB_T = T_color.get_RGB_error()
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.SetAutoLayout(True)
		self.SetSizer(main_sizer)
		
		# Create a static box to put the color.
		self.static_box = wx.StaticBox(self, -1, title)
		
		# Create the color panels. They are bars with a single color.
		reflection_panel = color_bar([self.R_color], self, size = (20, 20))
		transmission_panel = color_bar([self.T_color], self, size = (20, 20))
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer_1 = wx.FlexGridSizer(0, 16, 5, 15)
		
		sizer_1.Add((-1,-1))
		sizer_1.Add(wx.StaticText(self, -1, "X"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "Y"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "Z"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "x"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "y"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "L*"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "u*"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "v*"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "a*"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "b*"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "C*(u*v*)"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "h(u*v*)"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "C*(a*b*)"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "h(a*b*)"), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add((-1,-1))
		
		sizer_1.Add(wx.StaticText(self, -1, "Reflection:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_R[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_R[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % xyY_R[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % xyY_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_R[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_R[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Lab_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Lab_R[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChuv_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChuv_R[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChab_R[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChab_R[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(reflection_panel, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		
		sizer_1.Add(wx.StaticText(self, -1, "Transmission:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_T[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % XYZ_T[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % xyY_T[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % xyY_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_T[0]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Luv_T[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Lab_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % Lab_T[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChuv_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChuv_T[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChab_T[1]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(wx.StaticText(self, -1, "%.3f" % LChab_T[2]), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(transmission_panel, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
		
		# Create a button to show the locus.
		self.locus_button = wx.Button(self, -1, "View locus")
		self.locus_button.Bind(wx.EVT_BUTTON, self.on_locus_button)
		
		# Put in the static box.
		box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
		box_sizer.Add(sizer_1, 0,  wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		box_sizer.Add(self.locus_button, 0,  wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
		
		main_sizer.Add(box_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
		
		# It is necessary to bind both the panel and the static box since
		# the window that gets the event depends on the OS.
		self.static_box.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		reflection_panel.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		transmission_panel.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		for child in self.GetChildren():
			if isinstance(child, wx.StaticText):
				child.SetEventHandler(child)
				child.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
	
	
	######################################################################
	#                                                                    #
	# on_locus_button                                                    #
	#                                                                    #
	######################################################################
	def on_locus_button(self, event):
		"""Show the color locus when the locus button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		observer = self.R_color.get_observer()
		illuminant = self.R_color.get_illuminant()
		
		window = locus_dialog(self, observer, illuminant, [self.R_color], [self.T_color])
		
		answer = window.ShowModal()
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Handle right click events
		
		This method takes a single argument:
		  event              the event.
		
		This method creates a new event with an adjusted click position and
		then asks the parent to process it."""
		
		new_event = wx.MouseEvent(wx.wxEVT_RIGHT_DOWN)
		new_event.SetEventObject(self)
		
		window = event.GetEventObject()
		
		if window is self:
			new_event.X, new_event.Y = event.X, event.Y
		else:
			position = window.GetPosition()
			new_event.X, new_event.Y = event.X+position[0], event.Y+position[1]
		
		self.GetParent().ProcessEvent(new_event)
	
	
	######################################################################
	#                                                                    #
	# set_title                                                          #
	#                                                                    #
	######################################################################
	def set_title(self, title):
		"""Set or replace the title of the panel
		
		This method takes a single argument:
		  title               the title of the panel."""
		
		self.title = title
		self.static_box.SetLabel(title)
	
	
	######################################################################
	#                                                                    #
	# get_title                                                          #
	#                                                                    #
	######################################################################
	def get_title(self):
		"""Get the title of the panel
		
		This method returns the title of the panel."""
		
		return self.title



########################################################################
#                                                                      #
# color_trajectory_panel                                               #
#                                                                      #
########################################################################
class color_trajectory_panel(wx.Panel):
	"""A class for panels to show the color trajectory"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, title, angles, R_colors, T_colors):
		"""Initialize an instance of the panel
		
		This method takes 4 arguments:
		  parent             the panel's parent;
		  title              the title of the panel;
		  R_colors           color objects for the reflection colors;
		  T_colors           color objects for the transmission colors."""
		
		self.title = title
		self.angles = angles
		self.R_colors = R_colors
		self.T_colors = T_colors
		
		wx.Panel.__init__(self, parent, style = wx.NO_BORDER)
		
		# Hide the panel while we create it (to avoid flicker).
		self.Hide()
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.SetAutoLayout(True)
		self.SetSizer(main_sizer)
		
		# Create a static box to put the color.
		self.static_box = wx.StaticBox(self, -1, title)
		
		# Create the bars.
		reflection_bar = color_bar(self.R_colors, self, size = (500, 20))
		transmission_bar = color_bar(self.T_colors, self, size = (500, 20))
		
		sizer_1 = wx.FlexGridSizer(3, 2, 5, 15)
		
		sizer_1.Add(wx.StaticText(self, -1, "Reflection:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(reflection_bar, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		sizer_1.Add(wx.StaticText(self, -1, "Transmission:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(transmission_bar, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		# Create a button to show the locus.
		self.locus_button = wx.Button(self, -1, "View locus")
		self.locus_button.Bind(wx.EVT_BUTTON, self.on_locus_button)
		
		# Put in the static box.
		box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
		box_sizer.Add(sizer_1, 0, wx.ALL, 5)
		box_sizer.Add(self.locus_button, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
		
		main_sizer.Add(box_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
		
		# Bind some events.
		reflection_bar.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)
		reflection_bar.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
		reflection_bar.Bind(wx.EVT_MOTION, self.on_motion)
		reflection_bar.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		transmission_bar.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)
		transmission_bar.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
		transmission_bar.Bind(wx.EVT_MOTION, self.on_motion)
		transmission_bar.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		# It is necessary to bind both the panel and the static box since
		# the window that gets the event depends on the OS.
		self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		self.static_box.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		for child in self.GetChildren():
			if isinstance(child, wx.StaticText):
				child.SetEventHandler(child)
				child.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
		# Create a window that will be used for showing the angle.
		self.angle_window = wx.StaticText(self, -1, "")
		self.angle_window.Hide()
		
		# Finally show the panel
		self.Show()
	
	
	######################################################################
	#                                                                    #
	# on_locus_button                                                    #
	#                                                                    #
	######################################################################
	def on_locus_button(self, event):
		"""Show the color locus when the locus button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		observer = self.R_colors[0].get_observer()
		illuminant = self.R_colors[0].get_illuminant()
		
		window = locus_dialog(self, observer, illuminant, self.R_colors, self.T_colors)
		
		answer = window.ShowModal()
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Handle right click events
		
		This method takes a single argument:
		  event              the event.
		
		This method creates a new event with an adjusted click position and
		then asks the parent to process it."""
		
		new_event = wx.MouseEvent(wx.wxEVT_RIGHT_DOWN)
		new_event.SetEventObject(self)
		
		window = event.GetEventObject()
		
		if window is self:
			new_event.X, new_event.Y = event.X, event.Y
		else:
			position = window.GetPosition()
			new_event.X, new_event.Y = event.X+position[0], event.Y+position[1]
		
		self.GetParent().ProcessEvent(new_event)
	
	
	######################################################################
	#                                                                    #
	# on_enter_window                                                    #
	#                                                                    #
	######################################################################
	def on_enter_window(self, event):
		"""Show the angle of incidence when the mouse moves over the
		trajectory
		
		This method takes a single argument:
		  event              the event."""
		
		self.angle_window.Show()
	
	
	######################################################################
	#                                                                    #
	# on_leave_window                                                    #
	#                                                                    #
	######################################################################
	def on_leave_window(self, event):
		"""Hide the angle of incidence when the mouse leaves the trajectory
		
		This method takes a single argument:
		  event              the event."""
		
		self.angle_window.Hide()
	
	
	######################################################################
	#                                                                    #
	# on_motion                                                          #
	#                                                                    #
	######################################################################
	def on_motion(self, event):
		"""Update the angle of incidence when the mouse moves over the
		trajectory
		
		This method takes a single argument:
		  event              the event."""
		
		bar = event.GetEventObject()
		
		# Get the current position in pixels.
		bar_position = bar.GetPositionTuple()
		mouse_position = event.GetPositionTuple()
		text_position = (bar_position[0]+mouse_position[0]+5, bar_position[1]+mouse_position[1]-5)
		
		# Convert it to a position in the list of angles.
		position = bar.get_position(mouse_position[0])
		if position < 0:
			position = 0
		
		self.angle_window.SetLabel("%s" % self.angles[position])
		self.angle_window.SetPosition(text_position)
	
	
	######################################################################
	#                                                                    #
	# set_title                                                          #
	#                                                                    #
	######################################################################
	def set_title(self, title):
		"""Set or replace the title of the panel
		
		This method takes a single argument:
		  title               the title of the panel."""
		
		self.title = title
		self.static_box.SetLabel(title)
	
	
	######################################################################
	#                                                                    #
	# get_title                                                          #
	#                                                                    #
	######################################################################
	def get_title(self):
		"""Get the title of the panel
		
		This method returns the title of the panel."""
		
		return self.title



########################################################################
#                                                                      #
# color_bar                                                            #
#                                                                      #
########################################################################
class color_bar(wx.Window):
	"""A window to show a color bar representing a color trajectory"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, colors, parent, id = -1, size = wx.DefaultSize, style = 0):
		"""Initialize an instance of the window
		
		This method takes 2 to 5 arguments:
		  colors             the colors of the trajectory;
		  parent             the parent of the window;
		  id                 (optional) the id of the window;
		  size               (optional) the size of the window;
		  style              (optional) the style of the window."""
		
		# Create the window
		wx.Window.__init__(self, parent, id, size = size, style = style|wx.NO_FULL_REPAINT_ON_RESIZE)
		
		self.colors = colors
		
		# We keep a list of the position of every color.
		self.nb_colors = len(self.colors)
		self.positions = [0]*self.nb_colors
		
		# The plot uses the global settings for buffered drawing. But
		# saves the setting locally so it can be changed betwen plots.
		self.use_buffered_drawing = use_buffered_drawing
		
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.Bind(wx.EVT_PAINT, self.on_paint)
		
		# Make this user selectible.
		self.border_width = 1
		
		# Should the axes be determined automaticaly? Otherwise, they
		# must be provided using 
		self.automatic_axes = True
		self.x_left = 0.0
		self.y_bottom = 0.0
		self.x_right = 1.0
		self.y_top = 1.0
		
		# Create and initialize a buffer to avoir flicker.
		self.width, self.height = self.GetClientSizeTuple()
		self.buffer = wx.EmptyBitmap(self.width, self.height)
		
		self.update()
	
	
	######################################################################
	#                                                                    #
	# on_paint                                                           #
	#                                                                    #
	######################################################################
	def on_paint(self, event):
		"""Handle paint events
		
		This method takes a single argument:
		  event              the event."""
		
		# If we use buffered drawing, we simply put on the screen what
		# is already in the buffer.
		if self.use_buffered_drawing:
			DC = wx.BufferedPaintDC(self, self.buffer)
		
		# If we don't use buffered drawing, we have to redraw everything.
		else:
			DC = wx.PaintDC(self)
			DC.DrawBitmap(self.buffer, 0, 0)
	
	
	######################################################################
	#                                                                    #
	# on_size                                                            #
	#                                                                    #
	######################################################################
	def on_size(self, event):
		"""Handle size events
		
		This method takes a single argument:
		  event              the event."""
		
		self.width, self.height = self.GetClientSizeTuple()
		self.buffer = wx.EmptyBitmap(self.width, self.height)
		
		self.update()
	
	
	######################################################################
	#                                                                    #
	# update                                                             #
	#                                                                    #
	######################################################################
	def update(self):
		"""Update the color bar"""
		
		if self.use_buffered_drawing:
			DC = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		else:
			DC = wx.MemoryDC()
			DC.SelectObject(self.buffer)
		
		DC.BeginDrawing()
		
		self.draw(DC)
		
		DC.EndDrawing()
		
		if not self.use_buffered_drawing:
			wx.ClientDC(self).Blit(0, 0, self.width, self.height, DC, 0, 0)
	
	
	######################################################################
	#                                                                    #
	# draw                                                               #
	#                                                                    #
	######################################################################
	def draw(self, DC):
		"""Draw the color bar
		
		This method takes a single argument:
		  DC                 the drawing canvas on which to draw."""
		
		DC.Clear()
		
		# Calculate the width and height of the rectangle for a single
		# color.
		single_color_width = (self.width - 2*self.border_width) / self.nb_colors
		single_color_height = self.height - 2*self.border_width
		
		DC.SetPen(wx.TRANSPARENT_PEN)
		
		# Draw all colors.
		for i in range(self.nb_colors):
			
			RGB = self.colors[i].RGB()
			RGB_error = self.colors[i].get_RGB_error()
			
			# Determine the position of this color in the bar.
			left = self.border_width + int(round(i*single_color_width))
			right = self.border_width + int(round((i+1)*single_color_width))
			width = int(round(right-left))
			
			self.positions[i] = left
			
			# Draw the border.
			if RGB_error:
				DC.SetBrush(wx.RED_BRUSH)
			else:
				DC.SetBrush(wx.BLACK_BRUSH)
			DC.DrawRectangle(left, 0, width, self.height)
			
			# Draw the color.
			DC.SetBrush(wx.Brush(wx.Colour(RGB[0]*255.0, RGB[1]*255.0, RGB[2]*255.0)))
			DC.DrawRectangle(left, self.border_width, width, single_color_height)
		
		# Draw the left and right borders. We do it after drawing the bar
		# because RGB errors are only generated when the color is converted
		# to RGB.
		if self.colors[0].get_RGB_error():
			DC.SetBrush(wx.RED_BRUSH)
		else:
			DC.SetBrush(wx.BLACK_BRUSH)
		DC.DrawRectangle(0, 0, self.border_width, self.height)
		if self.colors[-1].get_RGB_error():
			DC.SetBrush(wx.RED_BRUSH)
		else:
			DC.SetBrush(wx.BLACK_BRUSH)
		DC.DrawRectangle(self.width - self.border_width, 0, self.border_width, self.height)
	
	
	######################################################################
	#                                                                    #
	# get_position                                                       #
	#                                                                    #
	######################################################################
	def get_position(self, x):
		"""Get the angle corresponding to a position of the mouse on the
		color bar
		
		This method takes a single argument:
		  x                  the position of the mouse."""
		
		return interpolation.locate(self.positions, self.nb_colors, x)



########################################################################
#                                                                      #
# locus_dialog                                                         #
#                                                                      #
########################################################################
class locus_dialog(wx.Dialog):
	"""A dialog to show the color locus"""
	
	title = "xy locus"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, observer, illuminant, R_colors, T_colors):
		"""Initialize the dialog
		
		This method takes 5 arguments:
		  parent             the panel's parent;
		  observer           the observer;
		  illuminant         the illuminant;
		  R_colors           color objects for the reflection colors;
		  T_colors           color objects for the transmission colors."""
		
		self.parent = parent
		self.observer = observer
		self.illuminant = illuminant
		self.R_colors = R_colors
		self.T_colors = T_colors
		
		wx.Dialog.__init__(self, self.parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		# Create a plot for the color locus.
		self.locus_plot = GUI_plot.plot(self, size = (400, 400), style = wx.SIMPLE_BORDER)
		self.locus_plot.set_xlabel("x")
		self.locus_plot.set_ylabel("y")
		self.locus_plot.set_legend_position(GUI_plot.TOP)
		self.locus_plot.set_grid(True)
		
		# Add it to the window.
		self.main_sizer.Add(self.locus_plot, 0, wx.ALIGN_CENTER|wx.ALL, 10)
		
		# Add it to the window.
		self.main_sizer.Add(wx.Button(self, wx.ID_OK), 0, wx.ALIGN_CENTER|wx.ALL, 10)
		
		self.add_trajectories()
		
		self.main_sizer.Fit(self)
		self.Layout()
	
	
	######################################################################
	#                                                                    #
	# add_trajectories                                                   #
	#                                                                    #
	######################################################################
	def add_trajectories(self):
		"""Add the trajectories to the locus"""
		
		# Calculate the boundary of the locus.
		x, y, wvls = color.calculate_xy_boundary(self.observer)
		
		# Close the locus.
		x.append(x[0])
		y.append(y[0])
		
		# Show it in the plot.
		boundary_curve = GUI_plot.plot_curve(x, y, style = GUI_plot.plot_curve_style("Black", 1))
		self.locus_plot.add_curve(boundary_curve)
		
		# Calculate the white point.
		XYZ_n = color.white_point(self.observer, self.illuminant)
		xyY_n = color.XYZ_to_xyY(XYZ_n)
		
		# Show it in the plot.
		white_point_curve = GUI_plot.plot_curve([xyY_n[0]], [xyY_n[1]], style = GUI_plot.plot_curve_style("Black", 1, "o", 6))
		self.locus_plot.add_curve(white_point_curve)
		
		# Get the reflection trajectory.
		nb_points = len(self.R_colors)
		x = [0.0]*nb_points
		y = [0.0]*nb_points
		for i_point in range(nb_points):
			xyY = self.R_colors[i_point].xyY()
			x[i_point] = xyY[0]
			y[i_point] = xyY[1]
		
		# Show it in the plot.
		starting_point = GUI_plot.plot_curve([x[0]], [y[0]], style = GUI_plot.plot_curve_style("Blue", 1, "o", 6))
		curve = GUI_plot.plot_curve(x, y, name = "Reflection", style = GUI_plot.plot_curve_style("Blue", 1))
		self.locus_plot.add_curve(starting_point)
		self.locus_plot.add_curve(curve)
		
		# Get the transmission trajectory.
		nb_points = len(self.T_colors)
		x = [0.0]*nb_points
		y = [0.0]*nb_points
		for i_point in range(nb_points):
			xyY = self.T_colors[i_point].xyY()
			x[i_point] = xyY[0]
			y[i_point] = xyY[1]
		
		# Show it in the plot.
		starting_point = GUI_plot.plot_curve([x[0]], [y[0]], style = GUI_plot.plot_curve_style("Red", 1, "o", 6))
		curve = GUI_plot.plot_curve(x, y, name = "Transmission", style = GUI_plot.plot_curve_style("Red", 1))
		self.locus_plot.add_curve(starting_point)
		self.locus_plot.add_curve(curve)
