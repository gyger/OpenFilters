# GUI_layer_grid.py
# 
# A grid class for displaying layers in the GUI of Filters.
# 
# Copyright (c) 2001,2002,2004,2005,2007,2008,2012,2013,2015 Stephane Larouche.
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



import operator

import wx
import wx.grid

from definitions import *



########################################################################
#                                                                      #
# layer_grid                                                           #
#                                                                      #
########################################################################
class layer_grid(wx.grid.Grid):
	"""A class to show the layers of a filter in a grid"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, main_window, side = FRONT):
		"""Initialize the grid
		
		This method takes 2 or 3 arguments:
		  parent             the parent window;
		  main_window        the main window of OpenFilters;
		  side               (optional) the side that the grid must show,
		                     by default FRONT."""
		
		self.main_window = main_window
		self.side = side
		
		self.filter = None
		
		# By default, modifying the filter is allowed. Is is forbiden
		# during calculations.
		self.allow_modifications = True
		
		wx.grid.Grid.__init__(self, parent, -1)
		
		self.CreateGrid(0, 10)
		
		# Set the size of layer numbers.
		self.SetRowLabelSize(35)
		
		# The first column is for the materials.
		self.SetColSize(0, 75)
		self.SetColLabelValue(0, "Material")
		
		# The second column is for the thickness.
		self.SetColSize(1, 65)
		self.SetColLabelValue(1, "Thickness\n(nm)")
		
		# The third column is for the thickness.
		self.SetColSize(2, 65)
		self.SetColLabelValue(2, "Index")
		
		# The fourth column is for the optical thickness.
		self.SetColSize(3, 65)
		self.SetColLabelValue(3, "OT")
		
		# The fifth column determines if the layer should be refined
		# during optimization.
		self.SetColSize(4, 60)
		self.SetColLabelValue(4, "Refine\nthickness")
		self.SetColFormatBool(4)
		
		# The sixth column determines if the layer should be refined
		# during optimization.
		self.SetColSize(5, 60)
		self.SetColLabelValue(5, "Refine\nindex")
		self.SetColFormatBool(5)
		
		# The seventh column determines if the OT should be preserved
		# during optimization.
		self.SetColSize(6, 60)
		self.SetColLabelValue(6, "Preserve\nOT")
		self.SetColFormatBool(6)
		
		# The eightht column determines if needles should be added in
		# the layer during optimization.
		self.SetColSize(7, 60)
		self.SetColLabelValue(7, "Add\nneedles")
		self.SetColFormatBool(7)
		
		# The ninth column determines if steps should be added in
		# the layer during optimization.
		self.SetColSize(8, 60)
		self.SetColLabelValue(8, "Add\nsteps")
		self.SetColFormatBool(8)
		
		# The tenth column is for the description of the layer.
		self.SetColSize(9, 150)
		self.SetColLabelValue(9, "Description")
		
		# Prepare the context menu.
		self.context_menu = wx.Menu()
		self.modify_ID = wx.NewId()
		self.context_menu.Append(self.modify_ID, "&Modify")
		self.Bind(wx.EVT_MENU, self.on_modify, id = self.modify_ID)
		self.remove_ID = wx.NewId()
		self.context_menu.Append(self.remove_ID, "&Remove layer")
		self.Bind(wx.EVT_MENU, self.on_remove, id = self.remove_ID)
		self.context_menu.AppendSeparator()
		self.select_all_ID = wx.NewId()
		self.context_menu.Append(self.select_all_ID, "&Select all")
		self.Bind(wx.EVT_MENU, self.on_select_or_unselect_all, id = self.select_all_ID)
		self.unselect_all_ID = wx.NewId()
		self.context_menu.Append(self.unselect_all_ID, "&Unselect all")
		self.Bind(wx.EVT_MENU, self.on_select_or_unselect_all, id = self.unselect_all_ID)
		
		# Manage the selected cells.
		self.selection = []
		self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_selection)
		self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_selection)
		
		# A double click opens the layer modification dialog (if any). In
		# case of a right click on a cell or the use of the context menu
		# button, a menu is poped up. The self.menu_row keeps the number of
		# the row where the right click was done to make it available to
		# the self.on_remove and self.on_modify methods.
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_double_click)
		self.GetGridWindow().Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
		self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
		self.menu_row = 0
		self.menu_col = 0
		
		# Call a method when a cell is changed.
		self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.DisableDragColSize()
		self.DisableDragGridSize()
		self.DisableDragRowSize()
		
		# Show the layers
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_filter                                                         #
	#                                                                    #
	######################################################################
	def set_filter(self, filter):
		"""Set the filter to show and update the grid accordingly
		
		This method takes a single argument:
		  filter             the filter to show."""
		
		self.filter = filter
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# clear_filter                                                       #
	#                                                                    #
	######################################################################
	def clear_filter(self):
		"""Remove the filter shown in the grid and update the grid
		accordingly"""
		
		self.filter = None
		
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Redraw the grid"""
		
		self.BeginBatch()
		
		nb_rows = self.GetNumberRows()
		
		if self.filter:
			nb_layers = self.filter.get_nb_layers(self.side)
		else:
			nb_layers = 0
		
		if nb_layers > nb_rows:
			self.AppendRows(nb_layers-nb_rows)
		elif nb_layers < nb_rows:
			self.DeleteRows(nb_layers, nb_rows-nb_layers)
		
		for i in range(nb_rows, nb_layers):
			self.SetRowLabelValue(i, "%d" % (i+1))
			
			self.SetCellEditor(i, 4, wx.grid.GridCellBoolEditor())
			self.SetCellEditor(i, 5, wx.grid.GridCellBoolEditor())
			self.SetCellEditor(i, 6, wx.grid.GridCellBoolEditor())
			self.SetCellEditor(i, 7, wx.grid.GridCellBoolEditor())
			self.SetCellEditor(i, 8, wx.grid.GridCellBoolEditor())
			
			self.SetReadOnly(i, 0)
			self.SetReadOnly(i, 1)
			self.SetReadOnly(i, 2)
			self.SetReadOnly(i, 3)
			self.SetReadOnly(i, 9)
		
		if self.filter:
			for i in range(nb_layers):
				self.reset_layer(i)
		
		self.EndBatch()
	
	
	######################################################################
	#                                                                    #
	# reset_layer                                                        #
	#                                                                    #
	######################################################################
	def reset_layer(self, layer_nb):
		"""Reset a line of the grid corresponding to a layer
		
		This method takes a single argument:
		  layer_nb           the number of the layer to update."""
		
		material_name = self.filter.get_layer_material_name(layer_nb, self.side)
		thickness = self.filter.get_layer_thickness(layer_nb, self.side)
		index = self.filter.get_layer_index(layer_nb, self.side)
		OT = self.filter.get_layer_OT(layer_nb, None, self.side)
		refine_thickness = self.filter.get_refine_layer_thickness(layer_nb, self.side)
		refinable_thickness = self.filter.get_refinable_layer_thickness(layer_nb, self.side)
		refine_index = self.filter.get_refine_layer_index(layer_nb, self.side)
		refinable_index = self.filter.get_refinable_layer_index(layer_nb, self.side)
		preserve_OT = self.filter.get_preserve_OT(layer_nb, self.side)
		add_needles = self.filter.get_add_needles(layer_nb, self.side)
		add_steps = self.filter.get_add_steps(layer_nb, self.side)
		description = self.filter.get_layer_description(layer_nb, self.side)
		
		self.SetCellValue(layer_nb, 0, material_name)
		self.SetCellValue(layer_nb, 1, "%1.3f" % thickness)
		if isinstance(index, list):
			self.SetCellValue(layer_nb, 2, "")
		else:
			self.SetCellValue(layer_nb, 2, "%1.4f" % index)
		self.SetCellValue(layer_nb, 3, "%1.6f" % OT)
		if refine_thickness:
			self.SetCellValue(layer_nb, 4, "1")
		else:
			self.SetCellValue(layer_nb, 4, "")
		if refine_index:
			self.SetCellValue(layer_nb, 5, "1")
		else:
			self.SetCellValue(layer_nb, 5, "")
		if preserve_OT:
			self.SetCellValue(layer_nb, 6, "1")
		else:
			self.SetCellValue(layer_nb, 6, "")
		if add_needles:
			self.SetCellValue(layer_nb, 7, "1")
		else:
			self.SetCellValue(layer_nb, 7, "")
		if add_steps:
			self.SetCellValue(layer_nb, 8, "1")
		else:
			self.SetCellValue(layer_nb, 8, "")
		if description == []:
			pass
		else:
			self.SetCellValue(layer_nb, 9, description[0])
		
		if refinable_thickness:
			self.SetReadOnly(layer_nb, 4, False)
			self.SetCellTextColour(layer_nb, 4, wx.NamedColour("BLACK"))
		else:
			self.SetReadOnly(layer_nb, 4)
			self.SetCellTextColour(layer_nb, 4, wx.NamedColour("GRAY"))
		if refinable_index:
			self.SetReadOnly(layer_nb, 5, False)
			self.SetCellTextColour(layer_nb, 5, wx.NamedColour("BLACK"))
		else:
			self.SetReadOnly(layer_nb, 5)
			self.SetCellTextColour(layer_nb, 5, wx.NamedColour("GRAY"))
		if refine_thickness or not refine_index:
			self.SetReadOnly(layer_nb, 6)
			self.SetCellTextColour(layer_nb, 6, wx.NamedColour("GRAY"))
		else:
			self.SetReadOnly(layer_nb, 6, False)
			self.SetCellTextColour(layer_nb, 6, wx.NamedColour("BLACK"))
		if refine_thickness:
			self.SetReadOnly(layer_nb, 7, False)
			self.SetCellTextColour(layer_nb, 7, wx.NamedColour("BLACK"))
		else:
			self.SetReadOnly(layer_nb, 7)
			self.SetCellTextColour(layer_nb, 7, wx.NamedColour("GRAY"))
		if refine_index:
			self.SetReadOnly(layer_nb, 8, False)
			self.SetCellTextColour(layer_nb, 8, wx.NamedColour("BLACK"))
		else:
			self.SetReadOnly(layer_nb, 8)
			self.SetCellTextColour(layer_nb, 8, wx.NamedColour("GRAY"))
	
	
	######################################################################
	#                                                                    #
	# set_allow_modifications                                            #
	#                                                                    #
	######################################################################
	def set_allow_modifications(self, allow_modifications):
		"""Allow or disallow modifications to the filter through the grid
		
		This method takes a single argument:
		  allow_modifications  a boolean indicating if modifications to the
		                       filter are allowed."""
		
		self.allow_modifications = allow_modifications
	
	
	######################################################################
	#                                                                    #
	# on_range_selection                                                 #
	#                                                                    #
	######################################################################
	def on_range_selection(self, event):
		"""Update the list of selected cells when a range of cells is
		selected
		
		This method takes a single argument:
		  event              the event."""
		
		if event.Selecting():
			for row in range(event.GetTopRow(), event.GetBottomRow()+1):
				for col in range(event.GetLeftCol(), event.GetRightCol()+1):
					if not [row, col] in self.selection:
						self.selection.append([row, col])
		else:
			for row in range(event.GetTopRow(), event.GetBottomRow()+1):
				for col in range(event.GetLeftCol(), event.GetRightCol()+1):
					if [row, col] in self.selection:
						self.selection.remove([row, col])
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_selection                                                  #
	#                                                                    #
	######################################################################
	def on_cell_selection(self, event):
		"""Update the list of selected cells when a cell is selected
		
		This method takes a single argument:
		  event              the event."""
		
		row = event.GetRow()
		col = event.GetCol()
		
		if event.Selecting():
			self.selection = [[row, col]]
		else:
			if [row, col] in self.selection:
				self.selection.remove([row, col])
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Apply the change to the filter when a cell of the grid is changed
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the row and the column that have been modified.
		row = event.GetRow()
		col = event.GetCol()
		
		# If one of the refine columns or the add needles or steps columns
		# have been modified, tell the optical filter.
		if col == 4:
			if self.GetCellValue(row, 4):
				value = True
			else:
				value = False
			self.filter.set_refine_layer_thickness(row, value, self.side)
		if col == 5:
			if self.GetCellValue(row, 5):
				value = True
			else:
				value = False
			self.filter.set_refine_layer_index(row, value, self.side)
		if col == 6:
			if self.GetCellValue(row, 6):
				value = True
			else:
				value = False
			self.filter.set_preserve_OT(row, value, self.side)
		if col == 7:
			if self.GetCellValue(row, 7):
				value = True
			else:
				value = False
			self.filter.set_add_needles(row, value, self.side)
		if col == 8:
			if self.GetCellValue(row, 8):
				value = True
			else:
				value = False
			self.filter.set_add_steps(row, value, self.side)
		
		self.reset_layer(row)
	
	
	######################################################################
	#                                                                    #
	# on_double_click                                                    #
	#                                                                    #
	######################################################################
	def on_double_click(self, event):
		"""Tell the main window that the user wants to modify a layer when
		it double clicks
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the row and column of the cell that was clicked and keep it
		# for use in self.on_remove and in self.on_modify
		self.menu_row = event.GetRow()
		self.menu_col = event.GetCol()
		
		if self.allow_modifications:
			self.main_window.modify_layer(self.menu_row, self.side)
	
	
	######################################################################
	#                                                                    #
	# on_right_click                                                     #
	#                                                                    #
	######################################################################
	def on_right_click(self, event):
		"""Show a menu when the user right clicks
		
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
		
		# Get the row and column of the cell that was clicked and keep it
		# for use in self.on_remove and in self.on_modify
		self.menu_row = event.GetRow()
		self.menu_col = event.GetCol()
		
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
		
		# Get the row and column of the cell where the cursor is located
		# for use in self.on_remove and in self.on_modify
		self.menu_row = self.GetGridCursorRow()
		self.menu_col = self.GetGridCursorCol()
		
		rect = self.CellToRect(self.menu_row, self.menu_col)
		
		position = rect.GetTopLeft() + wx.Point(self.GetRowLabelSize()+rect.width//2, self.GetColLabelSize()+rect.height//2)
		
		self.show_context_menu(position)
	
	
	######################################################################
	#                                                                    #
	# on_remove                                                          #
	#                                                                    #
	######################################################################
	def on_remove(self, event):
		"""Remove a layer or a selection of layers when the user selects the menu item
		
		This method takes a single argument:
		  event              the event."""
		
		rows = set([cell[0] for cell in self.selection])
		
		if len(rows) > 1:
			rows = list(rows)
			rows.sort(reverse = True)
			for layer in rows:
				self.filter.remove_layer(layer, self.side)
		else:
			self.filter.remove_layer(self.menu_row, self.side)
		
		self.ClearSelection()
		
		self.reset()
		
		self.main_window.update_index_profile_plots(self.side)
		self.main_window.delete_results()
		self.main_window.update_menu()
	
	
	######################################################################
	#                                                                    #
	# on_modify                                                          #
	#                                                                    #
	######################################################################
	def on_modify(self, event):
		"""Tell the main window that the user wants to modify a layer when
		he selects the menu item
		
		This method takes a single argument:
		  event              the event."""
		
		self.main_window.modify_layer(self.menu_row, self.side)
	
	
	######################################################################
	#                                                                    #
	# on_select_or_unselect_all                                          #
	#                                                                    #
	######################################################################
	def on_select_or_unselect_all(self, event):
		"""Set all the cells in the selection to True or False when the user
		selects the menu item and update the filter accordingly
		
		This method takes a single argument:
		  event              the event."""
		
		if event.GetId() == self.select_all_ID:
			select = True
		else:
			select = False
		
		# Make a unique list of cells.
		cells = list(set([tuple(cell) for cell in self.selection]))
		
		# Sort so that cells are classified row by row and, for a row in
		# increasing number of column.
		cells.sort(key = operator.itemgetter(1))
		cells.sort(key = operator.itemgetter(0))
		
		# Change the properties of the filter.
		for i in range(len(cells)):
			row = cells[i][0]
			col = cells[i][1]
			
			if col == 4 and self.filter.get_refinable_layer_thickness(row, self.side):
				self.filter.set_refine_layer_thickness(row, select, self.side)
			elif col == 5 and self.filter.get_refinable_layer_index(row, self.side):
				self.filter.set_refine_layer_index(row, select, self.side)
			elif col == 6 and self.filter.get_refine_layer_index(row, self.side) and not self.filter.get_refine_layer_thickness(row, self.side):
				self.filter.set_preserve_OT(row, select, self.side)
			elif col == 7 and self.filter.get_refine_layer_thickness(row, self.side):
				self.filter.set_add_needles(row, select, self.side)
			elif col == 8 and self.filter.get_refine_layer_index(row, self.side):
				self.filter.set_add_steps(row, select, self.side)
			
			self.reset_layer(row)
	
	
	######################################################################
	#                                                                    #
	# show_context_menu                                                  #
	#                                                                    #
	######################################################################
	def show_context_menu(self, position = wx.DefaultPosition):
		"""Show a context menu
		
		This method takes a single argument:
		  position           the position where to put the popup munu."""
		
		# If the user clicked outside of the selection, modify the
		# selection.
		if not self.IsInSelection(self.menu_row, self.menu_col):
			self.ClearSelection()
			self.SetGridCursor(self.menu_row, self.menu_col)
		
		# Make sets of all selected rows and cols.
		rows = set([cell[0] for cell in self.selection])
		cols = set([cell[1] for cell in self.selection])
		
		if not self.allow_modifications:
			return
		
		# If a single row is selected, offer the user the possibility to
		# remove or modify the layer. Otherwise, offer the user the
		# possibility to remove all selected layers.
		if len(rows) == 1:
			self.context_menu.Enable(self.modify_ID, True)
			self.context_menu.SetLabel(self.remove_ID, "&Remove layer")
			self.context_menu.Enable(self.remove_ID, True)
		else:
			self.context_menu.Enable(self.modify_ID, False)
			self.context_menu.SetLabel(self.remove_ID, "&Remove selected layers")
			self.context_menu.Enable(self.remove_ID, True)
		
		# If the whole selection is in columns 4 to 8 and there is more
		# than one selected cell, offer the possibility to select or
		# unselect all.
		if len(self.selection) > 1 and cols.issubset(set([4, 5, 6, 7, 8])):
			self.context_menu.Enable(self.select_all_ID, True)
			self.context_menu.Enable(self.unselect_all_ID, True)
		else:
			self.context_menu.Enable(self.select_all_ID, False)
			self.context_menu.Enable(self.unselect_all_ID, False)
		
		self.PopupMenu(self.context_menu, position)
