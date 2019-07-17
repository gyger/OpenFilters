# GUI_target_grid.py
# 
# A grid class for displaying targets in the GUI of Filters.
# 
# Copyright (c) 2004-2009,2012,2013,2015 Stephane Larouche.
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
import wx.grid

from definitions import *
import targets
import color



########################################################################
#                                                                      #
# target_grid                                                          #
#                                                                      #
########################################################################
class target_grid(wx.grid.Grid):
	"""A class implementing a grid to show the targets of a project"""
	
	kinds = {targets.R_TARGET: "R",
	         targets.T_TARGET: "T",
	         targets.A_TARGET: "A",
	         targets.R_PHASE_TARGET: "R phase",
	         targets.T_PHASE_TARGET: "T phase",
	         targets.R_GD_TARGET: "R GD",
	         targets.T_GD_TARGET: "T GD",
	         targets.R_GDD_TARGET: "R GDD",
	         targets.T_GDD_TARGET: "T GDD",
	         targets.R_SPECTRUM_TARGET: "R",
	         targets.T_SPECTRUM_TARGET: "T",
	         targets.A_SPECTRUM_TARGET: "A",
	         targets.R_PHASE_SPECTRUM_TARGET: "R phase",
	         targets.T_PHASE_SPECTRUM_TARGET: "T phase",
	         targets.R_GD_SPECTRUM_TARGET: "R GD",
	         targets.T_GD_SPECTRUM_TARGET: "T GD",
	         targets.R_GDD_SPECTRUM_TARGET: "R GDD",
	         targets.T_GDD_SPECTRUM_TARGET: "T GDD",
	         targets.R_COLOR_TARGET: "R color",
	         targets.T_COLOR_TARGET: "T color"}
	
	units = {targets.R_TARGET: "",
	         targets.T_TARGET: "",
	         targets.A_TARGET: "",
	         targets.R_PHASE_TARGET: " deg.",
	         targets.T_PHASE_TARGET: " deg.",
	         targets.R_GD_TARGET: " fs",
	         targets.T_GD_TARGET: " fs",
	         targets.R_GDD_TARGET: " fs^2",
	         targets.T_GDD_TARGET: " fs^2",
	         targets.R_SPECTRUM_TARGET: "",
	         targets.T_SPECTRUM_TARGET: "",
	         targets.A_SPECTRUM_TARGET: "",
	         targets.R_PHASE_SPECTRUM_TARGET: " deg.",
	         targets.T_PHASE_SPECTRUM_TARGET: " deg.",
	         targets.R_GD_SPECTRUM_TARGET: " fs",
	         targets.T_GD_SPECTRUM_TARGET: " fs",
	         targets.R_GDD_SPECTRUM_TARGET: " fs^2",
	         targets.T_GDD_SPECTRUM_TARGET: " fs^2",
	         targets.R_COLOR_TARGET: "",
	         targets.T_COLOR_TARGET: ""}
	
	multiplicative_factors = {targets.R_TARGET: 1.0,
	                          targets.T_TARGET: 1.0,
	                          targets.A_TARGET: 1.0,
	                          targets.R_PHASE_TARGET: 1.0,
	                          targets.T_PHASE_TARGET: 1.0,
	                          targets.R_GD_TARGET: 1.0e15,
	                          targets.T_GD_TARGET: 1.0e15,
	                          targets.R_GDD_TARGET: 1.0e30,
	                          targets.T_GDD_TARGET: 1.0e30,
	                          targets.R_SPECTRUM_TARGET: 1.0,
	                          targets.T_SPECTRUM_TARGET: 1.0,
	                          targets.A_SPECTRUM_TARGET: 1.0,
	                          targets.R_PHASE_SPECTRUM_TARGET: 1.0,
	                          targets.T_PHASE_SPECTRUM_TARGET: 1.0,
	                          targets.R_GD_SPECTRUM_TARGET: 1.0e15,
	                          targets.T_GD_SPECTRUM_TARGET: 1.0e15,
	                          targets.R_GDD_SPECTRUM_TARGET: 1.0e30,
	                          targets.T_GDD_SPECTRUM_TARGET: 1.0e30,
	                          targets.R_COLOR_TARGET: 1.0,
	                          targets.T_COLOR_TARGET: 1.0}
	
	inequalities = {targets.EQUAL: "",
	                targets.SMALLER: "< ",
	                targets.LARGER: "> "}
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, main_window):
		"""Initialize the grid
		
		This method takes 2 arguments:
		  parent             the window's parent;
		  main_window        the main window."""
		
		self.main_window = main_window
		
		wx.grid.Grid.__init__(self, parent, -1, style = wx.VSCROLL|wx.HSCROLL)
		
		self.project = None
		
		# By default, modifying the targets is allowed. Is is forbiden
		# during optimization.
		self.allow_modifications = True
		
		# Prevent recursive calls when operating on selection.
		self.operating_on_selection = False
		
		self.CreateGrid(0, 6)
		
		# The first column is for the materials.
		self.SetColSize(0, 120)
		self.SetColLabelValue(0, "Kind")
		
		# The second column is for the angle.
		self.SetColSize(1, 60)
		self.SetColLabelValue(1, "Angle\n(degrees)")
		
		# The third column is for the polarization.
		self.SetColSize(2, 100)
		self.SetColLabelValue(2, "Polarization\n(degrees)")
		
		# The fifth column is for the wavelength.
		self.SetColSize(3, 100)
		self.SetColLabelValue(3, "Wavelength(s)\n(nm)")
		
		# The sixth column is for the target value.
		self.SetColSize(4, 120)
		self.SetColLabelValue(4, "Value(s)")
		
		# The seventh column is for the target tolerance.
		self.SetColSize(5, 120)
		self.SetColLabelValue(5, "Tolerance(s)")
		
		# Prepare the context menu.
		self.context_menu = wx.Menu()
		self.modify_ID = wx.NewId()
		self.context_menu.Append(self.modify_ID, "&Modify")
		self.Bind(wx.EVT_MENU, self.on_modify, id = self.modify_ID)
		self.copy_ID = wx.NewId()
		self.context_menu.Append(self.copy_ID, "&Copy")
		self.Bind(wx.EVT_MENU, self.on_copy, id = self.copy_ID)
		self.remove_ID = wx.NewId()
		self.context_menu.Append(self.remove_ID, "&Remove")
		self.Bind(wx.EVT_MENU, self.on_remove, id = self.remove_ID)
		
		# Manage selection events to prevent selections.
		self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_selection)
		self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_selection)
		
		# The context menu key or right clicking on a cell or a label opens
		# a popup menu. Double clicking opens a target dialog. 
		self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
		self.GetGridWindow().Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_double_click)
		
		# Disable resizing and editing of the grid.
		self.DisableDragColSize()
		self.DisableDragGridSize()
		self.DisableDragRowSize()
		self.EnableEditing(False)
	
	
	######################################################################
	#                                                                    #
	# set_project                                                        #
	#                                                                    #
	######################################################################
	def set_project(self, project):
		"""Set the project whose targets will be shown in the grid and
		redraw the grid
		
		This method takes a single argument:
		  project            the project."""
		
		self.project = project
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# clear_project                                                      #
	#                                                                    #
	######################################################################
	def clear_project(self):
		"""Remove the project and draw an empty grid"""
		
		self.project = None
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Redraw the whole grid"""
		
		if self.project:
			nb_targets = self.project.get_nb_targets()
		else:
			nb_targets = 0
		
		self.BeginBatch()
		
		nb_rows = self.GetNumberRows()
		
		if nb_targets > nb_rows:
			self.AppendRows(nb_targets-nb_rows)
		elif nb_targets < nb_rows:
			self.DeleteRows(nb_targets, nb_rows-nb_targets)
		
		if self.project:
			for i in range(nb_targets):
				self.reset_target(i)
			
			# If no row is selected, select the first one.
			if nb_targets:
				if self.IsSelection():
					self.main_window.select_target(self.GetGridCursorRow())
				else:
					self.SelectRow(0)
					self.main_window.select_target(0)
			else:
				self.main_window.select_target(-1)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# reset_target                                                       #
	#                                                                    #
	######################################################################
	def reset_target(self, nb):
		"""Redraw the line of the grid corresponding to a target
		
		This method takes a single argument:
		  nb                 the number of the target to redraw."""
		
		target = self.project.get_target(nb)
		
		kind = target.get_kind()
		direction = target.get_direction()
		
		kind_text = self.kinds[kind]
		if kind in targets.REVERSIBLE_TARGETS and direction == targets.BACKWARD:
			kind_text += " reverse"
		
		if kind in targets.DISCRETE_TARGETS:
			
			angle = target.get_angle()
			polarization = target.get_polarization()
			wvl, value, delta = target.get_values()
			inequality = target.get_inequality()
			
			angle_text = "%s" % angle
			if polarization == S:
				polarization_text = "s"
			elif polarization == P:
				polarization_text = "p"
			elif polarization == UNPOLARIZED:
				polarization_text = "unpolarised"
			else:
				polarization_text = "%s" % polarization
			wvl_text = "%s" % wvl[0]
			value_text = self.inequalities[inequality] + "%s" % (value[0]*self.multiplicative_factors[kind]) + self.units[kind]
			tolerance_text = "%s" % (delta[0]*self.multiplicative_factors[kind]) + self.units[kind]
		
		elif kind in targets.SPECTRUM_TARGETS:
			
			angle = target.get_angle()
			polarization = target.get_polarization()
			from_wvl, to_wvl, by_wvl, wvls, values, deltas = target.get_points()
			inequality = target.get_inequality()
			
			angle_text = "%s" % angle
			if polarization == S:
				polarization_text = "s"
			elif polarization == P:
				polarization_text = "p"
			elif polarization == UNPOLARIZED:
				polarization_text = "unpolarised"
			else:
				polarization_text = "%s" % polarization
			wvl_text = "%s-%s" % (from_wvl, to_wvl)
			for i_wvl in range(1, len(values)):
				if values[i_wvl] != values[0]:
					value_text = self.inequalities[inequality] + "spectrum"
					break
			else:
				value_text = self.inequalities[inequality] + "%s" % (values[0]*self.multiplicative_factors[kind]) + self.units[kind]
			for i_wvl in range(1, len(deltas)):
				if deltas[i_wvl] != deltas[0]:
					tolerance_text = "spectrum"
					break
			else:
				tolerance_text = "%s%s" % (deltas[0]*self.multiplicative_factors[kind], self.units[kind])
		
		elif kind in targets.COLOR_TARGETS:
			
			angle = target.get_angle()
			polarization = target.get_polarization()
			color_space = target.get_color_space()
			target_values, tolerances = target.get_values()
			
			angle_text = "%s" % angle
			if polarization == S:
				polarization_text = "s"
			elif polarization == P:
				polarization_text = "p"
			elif polarization == UNPOLARIZED:
				polarization_text = "unpolarised"
			else:
				polarization_text = "%s" % polarization
			kind_text += " (%s)" % color.color_spaces[color_space]
			wvl_text = ""
			value_text = "%s, %s, %s" % (target_values[0], target_values[1], target_values[2])
			tolerance_text = "%s, %s, %s" % (tolerances[0], tolerances[1], tolerances[2])
		
		self.BeginBatch()
		
		self.SetRowLabelValue(nb, "%d" % (nb+1))
		self.SetCellValue(nb, 0, kind_text)
		self.SetCellValue(nb, 1, angle_text)
		self.SetCellValue(nb, 2, polarization_text)
		self.SetCellValue(nb, 3, wvl_text)
		self.SetCellValue(nb, 4, value_text)
		self.SetCellValue(nb, 5, tolerance_text)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# add_target                                                         #
	#                                                                    #
	######################################################################
	def add_target(self):
		"""Add one target to the grid
		
		This method should be called after a target has been added to
		the project."""
		
		self.BeginBatch()
		
		self.AppendRows(1)
		
		nb = self.GetNumberRows() - 1
		
		self.reset_target(nb)
		self.select_target(nb)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# remove_target                                                      #
	#                                                                    #
	######################################################################
	def remove_target(self, nb):
		"""Remove the line of the grid corresponding to a target
		
		This method takes a single argument:
		  nb                 the number of the target to remove."""
		
		self.DeleteRows(nb, 1)
		
		nb_rows = self.GetNumberRows()
		
		# If no row is selected, select the one where the cursor is.
		if nb_rows:
			if not self.IsSelection():
				self.select_target(self.GetGridCursorRow())
		else:
			self.main_window.select_target(-1)
	
	
	######################################################################
	#                                                                    #
	# set_allow_modifications                                            #
	#                                                                    #
	######################################################################
	def set_allow_modifications(self, allow_modifications):
		"""Enable or disable modifications of the grid
		
		This method takes a single argument:
		  allow_modifications    a boolean indicating if the grid must be
		                         enabled or disabled."""
		
		self.allow_modifications = allow_modifications
		
		if self.allow_modifications:
			self.Enable()
		else:
			self.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_range_selection                                                 #
	#                                                                    #
	######################################################################
	def on_range_selection(self, event):
		"""Select whole rows when a range of cells is selected
		
		This method takes a single argument:
		  event              the event."""
		
		# Prevent recursive calls.
		if self.operating_on_selection:
			return
		
		self.operating_on_selection = True
		
		row = self.GetGridCursorRow()
		self.ClearSelection()
		self.SelectRow(row)
		
		self.operating_on_selection = False
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_selection                                                  #
	#                                                                    #
	######################################################################
	def on_cell_selection(self, event):
		"""Select a whose row when a cell is selected
		
		This method takes a single argument:
		  event              the event."""
		
		row = event.GetRow()
		
		if row != self.GetGridCursorRow() or not self.IsSelection():
			self.operating_on_selection = True
			
			self.SelectRow(row)
			self.main_window.select_target(row)
			
			self.operating_on_selection = False
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Show a menu when the user presses the mouse right button
		
		This method takes a single argument:
		  event              the event."""
		
		# If the left or middle button are down, don't show the context
		# menu. LeftIsDown and MiddleIsDown are only available for wx
		# versions 2.9 and later.
		mouse_state = wx.GetMouseState()
		try:
			if mouse_state.LeftIsDown() or mouse_state.MiddleIsDown():
				return
		except AttributeError:
			if mouse_state.LeftDown() or mouse_state.MiddleDown():
				return
		
		self.SetGridCursor(event.GetRow(), event.GetCol())
		
		self.show_context_menu()
	
	
	######################################################################
	#                                                                    #
	# on_context_menu                                                    #
	#                                                                    #
	######################################################################
	def on_context_menu(self, event):
		"""Show a menu when the user presses the context menu key
		
		This method takes a single argument:
		  event              the event."""
		
		# If any button is down, don't show the context menu. LeftIsDown,
		# MiddleIsDown, and RightIsDown are only available for wx versions
		# 2.9 and later.
		mouse_state = wx.GetMouseState()
		try:
			if mouse_state.LeftIsDown() or mouse_state.MiddleIsDown() or mouse_state.RightIsDown():
				return
		except AttributeError:
			if mouse_state.LeftDown() or mouse_state.MiddleDown() or mouse_state.RightDown():
				return
		
		rect = self.CellToRect(self.GetGridCursorRow(), self.GetGridCursorCol())
		
		position = rect.GetTopLeft() + wx.Point(self.GetRowLabelSize()+rect.width//2, self.GetColLabelSize()+rect.height//2)
		
		self.show_context_menu(position)
	
	
	######################################################################
	#                                                                    #
	# on_double_click                                                    #
	#                                                                    #
	######################################################################
	def on_double_click(self, event):
		"""Modify a target when the user double clicks on a target
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the row that was clicked.
		row = event.GetRow()
		
		# If the columns labels were clicked, don't do anything.
		if row < 0:
			return
		
		self.main_window.modify_target(row)
	
	
	######################################################################
	#                                                                    #
	# on_remove                                                          #
	#                                                                    #
	######################################################################
	def on_remove(self, event):
		"""Tell the main window when the user selects the remove menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.remove_target(self.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# on_modify                                                          #
	#                                                                    #
	######################################################################
	def on_modify(self, event):
		"""Modify a target when the user selects the modify menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.modify_target(self.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# on_copy                                                            #
	#                                                                    #
	######################################################################
	def on_copy(self, event):
		"""Tell the main window when the user selects the copy menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.copy_target(self.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# show_context_menu                                                  #
	#                                                                    #
	######################################################################
	def show_context_menu(self, position = wx.DefaultPosition):
		"""Show a context menu
		
		This method takes a single argument:
		  position           the position where to put the popup munu."""
		
		self.PopupMenu(self.context_menu, position)
	
	
	######################################################################
	#                                                                    #
	# select_target                                                      #
	#                                                                    #
	######################################################################
	def select_target(self, nb):
		"""Select a target
		
		This method takes a single argument:
		  nb                 the number of the target to select."""
		
		# An event is generated when the cell is selected.
		self.SetGridCursor(nb, 0)
