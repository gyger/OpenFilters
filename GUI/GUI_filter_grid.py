# GUI_filter_grid.py
# 
# A grid class to display the list of filters in a project for the GUI
# of Filters.
# 
# Copyright (c) 2004-2008,2012,2013,2015 Stephane Larouche.
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



########################################################################
#                                                                      #
# filter_grid                                                          #
#                                                                      #
########################################################################
class filter_grid(wx.grid.Grid):
	"""A class implementing a grid to show the filters of a project"""
	
	
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
		
		# By default, modifying the filters is allowed. Is is forbiden
		# during optimization.
		self.allow_modifications = True
		
		# Prevent recursive calls when operating on selection.
		self.operating_on_selection = False
		
		self.CreateGrid(0, 5)
		
		# The first column is for the materials.
		self.SetColSize(0, 60)
		self.SetColLabelValue(0, "Nb front\nlayers")
		
		# The second column is for the angle.
		self.SetColSize(1, 100)
		self.SetColLabelValue(1, "Front\nthickness (nm)")
		
		# The third column is for the polarization.
		self.SetColSize(2, 60)
		self.SetColLabelValue(2, "Nb back\nlayers")
		
		# The fifth column is for the wavelength.
		self.SetColSize(3, 100)
		self.SetColLabelValue(3, "Back\nthickness (nm)")
		
		# The sixth column is for the filter value.
		self.SetColSize(4, 600)
		self.SetColLabelValue(4, "Description")
		
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
		
		# The context menu key or right clicking on a cell opens a popup
		# menu. Double clicking opens the filter. 
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
		"""Set the project whose filters will be shown in the grid and
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
			nb_filters = self.project.get_nb_filters()
		else:
			nb_filters = 0
		
		self.BeginBatch()
		
		nb_rows = self.GetNumberRows()
		
		if nb_filters > nb_rows:
			self.AppendRows(nb_filters-nb_rows)
		elif nb_filters < nb_rows:
			self.DeleteRows(nb_filters, nb_rows-nb_filters)
		
		if self.project:
			for i in range(nb_filters):
				self.reset_filter(i)
			
			# If no row is selected, select the one where the cursor is.
			if nb_filters:
				if not self.IsSelection():
					self.select_filter(self.GetGridCursorRow())
			else:
				self.main_window.select_filter(-1)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# reset_filter                                                       #
	#                                                                    #
	######################################################################
	def reset_filter(self, nb):
		"""Redraw the line of the grid corresponding to a filter
		
		This method takes a single argument:
		  nb                 the number of the filter to redraw."""
		
		filter = self.project.get_filter(nb)
		
		self.BeginBatch()
		
		self.SetRowLabelValue(nb, "%d" % (nb+1))
		self.SetCellValue(nb, 0, "%d" % filter.get_nb_layers(FRONT))
		self.SetCellValue(nb, 1, "%.2f" % filter.get_total_thickness(FRONT))
		self.SetCellValue(nb, 2, "%d" % filter.get_nb_layers(BACK))
		self.SetCellValue(nb, 3, "%.2f" % filter.get_total_thickness(BACK))
		self.SetCellValue(nb, 4, filter.get_description())
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# add_filter                                                         #
	#                                                                    #
	######################################################################
	def add_filter(self):
		"""Add one filter to the grid
		
		This method should be called after a filter has been added to
		the project."""
		
		self.BeginBatch()
		
		self.AppendRows(1)
		
		nb = self.GetNumberRows() - 1
		
		self.reset_filter(nb)
		self.select_filter(nb)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# remove_filter                                                      #
	#                                                                    #
	######################################################################
	def remove_filter(self, nb):
		"""Remove the line of the grid corresponding to a filter
		
		This method takes a single argument:
		  nb                 the number of the filter to remove."""
		
		self.DeleteRows(nb, 1)
		
		nb_rows = self.GetNumberRows()
		
		# If no row is selected, select the one where the cursor is.
		if nb_rows:
			if not self.IsSelection():
				self.select_filter(self.GetGridCursorRow())
		else:
			self.main_window.select_filter(-1)
	
	
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
		"""Prevent the selection of multiple rows when a range of cells is
		selected
		
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
		"""Select a whole row when a cell is selected
		
		This method takes a single argument:
		  event              the event."""
		
		row = event.GetRow()
		
		if row != self.GetGridCursorRow() or not self.IsSelection():
			self.operating_on_selection = True
			
			self.SelectRow(row)
			self.main_window.select_filter(row)
			
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
		"""Tell the main window when the user double clicks on a filter
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the row that was clicked.
		row = event.GetRow()
		
		self.main_window.show_filter(row)
	
	
	######################################################################
	#                                                                    #
	# on_remove                                                          #
	#                                                                    #
	######################################################################
	def on_remove(self, event):
		"""Tell the main window when the user selects the remove menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.remove_filter(self.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# on_modify                                                          #
	#                                                                    #
	######################################################################
	def on_modify(self, event):
		"""Tell the main window when the user selects the modify menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.show_filter(self.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# on_copy                                                            #
	#                                                                    #
	######################################################################
	def on_copy(self, event):
		"""Tell the main window when the user selects the copy menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.copy_filter(self.GetGridCursorRow())
	
	
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
	# select_filter                                                      #
	#                                                                    #
	######################################################################
	def select_filter(self, nb):
		"""Select a filter
		
		This method takes a single argument:
		  nb                 the number of the filter to select."""
		
		# An event is generated when the cell is selected.
		self.SetGridCursor(nb, 0)
