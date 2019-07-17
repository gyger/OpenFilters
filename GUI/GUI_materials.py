# GUI_materials.py
# 
# Dialogs to manipulate materials.
# 
# Copyright (c) 2004-2009,2011-2016 Stephane Larouche.
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

import wx

import abeles
import materials
import units

from GUI_validators import int_validator, float_validator
from GUI_plot import plot, plot_curve, plot_curve_style



# A list of characters that are valid for filenames on most operating
# systems. The space is not accepted because it causes trouble in the
# project files.
valid_material_name_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"



########################################################################
#                                                                      #
# user_material_directory_dialog                                       #
#                                                                      #
########################################################################
class user_material_directory_dialog(wx.Dialog):
	"""A dialog to let the user select the user material directory"""
	
	title = "Select user material directory"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, directory = None, message = ""):
		"""Initialize the dialog
		
		This method takes 1 to 3 arguments:
		  parent                 the window's parent;
		  directory              the current user directory;
		  message                (optional) a message to show in the
		                         dialog."""
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		if message: message += " "
		
		message += "Make sure you select a directory where you have write privileges (such as inside your home directory)."
		
		static_text = wx.StaticText(self, -1, message)
		self.main_sizer.Add(static_text, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		static_text.Wrap(400)
		
		self.directory_picker_ctrl = wx.DirPickerCtrl(self, -1, size = (400, -1), validator = user_directory_validator())
		
		self.main_sizer.Add(self.directory_picker_ctrl, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.ok_button, 0, wx.ALL, 10)
		buttons.Add(self.cancel_button, 0, wx.ALL, 10)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		if directory:
			self.directory_picker_ctrl.SetPath(directory)
	
	
	######################################################################
	#                                                                    #
	# get_directory                                                      #
	#                                                                    #
	######################################################################
	def get_directory(self):
		"""Get the selected directory
		
		This method takes no argument and return the directory that was
		selected."""
		
		return self.directory_picker_ctrl.GetPath()



########################################################################
#                                                                      #
# manage_materials_dialog                                              #
#                                                                      #
########################################################################
class manage_materials_dialog(wx.Dialog):
	"""A dialog class to manage the materials."""
	
	title = "Manage materials"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, material_catalog, allow_modifications):
		"""Initialize the dialog
		
		This method takes 3 arguments:
		  parent               the window's parent;
		  material_catalog     the catalog of materials to show;
		  allow_modifications  a boolean indicating is materials can be
		                       modified (for example, not while a project
		                       is opened)."""
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.allow_modifications = allow_modifications
		
		# Get all the catalogs.
		if isinstance(material_catalog, materials.material_catalogs):
			self.catalogs = material_catalog.get_catalogs()
		else:
			self.catalogs = [material_catalog]
		
		self.has_user_catalog = False
		
		self.locations = [None]*len(self.catalogs)
		for i, catalog in enumerate(self.catalogs):
			if catalog.is_default_material_catalog():
				self.locations[i] = "Default"
			else:
				self.locations[i] = "User"
				self.has_user_catalog = True
				self.user_catalog_nb = i
		
		# Prevent recursive calls when operating on selection.
		self.operating_on_selection = False
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		# Create a grid to show the materials and set column labels.
		self.material_grid = wx.grid.Grid(self, -1, size = (650, 400), style = wx.SUNKEN_BORDER)
		self.material_grid.CreateGrid(0, 4)
		self.material_grid.SetColSize(0, 240)
		self.material_grid.SetColLabelValue(0, "Material")
		self.material_grid.SetColSize(1, 100)
		self.material_grid.SetColLabelValue(1, "Kind")
		self.material_grid.SetColSize(2, 100)
		self.material_grid.SetColLabelValue(2, "Dispersion")
		self.material_grid.SetColSize(3, 100)
		self.material_grid.SetColLabelValue(3, "Location")
		
		# Disable resizing and editing of the grid.
		self.material_grid.DisableDragColSize()
		self.material_grid.DisableDragGridSize()
		self.material_grid.DisableDragRowSize()
		self.material_grid.EnableEditing(False)
		
		self.main_sizer.Add(self.material_grid, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		static_text = wx.StaticText(self, -1, "Grayed out materials are default materials overwritten by user materials with the same name.")
		self.main_sizer.Add(static_text, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, 10)
		static_text.Wrap(600)
		
		self.view_modify_button = wx.Button(self, wx.NewId(), "View/Modify")
		self.new_button = wx.Button(self, wx.ID_NEW)
		self.copy_button = wx.Button(self, wx.ID_COPY)
		self.import_button = wx.Button(self, wx.NewId(), "Import from text file")
		self.remove_button = wx.Button(self, wx.ID_REMOVE)
		self.close_button = wx.Button(self, wx.ID_CLOSE)
		self.Bind(wx.EVT_BUTTON, self.on_view_modify, self.view_modify_button)
		self.Bind(wx.EVT_BUTTON, self.on_new, self.new_button)
		self.Bind(wx.EVT_BUTTON, self.on_copy, self.copy_button)
		self.Bind(wx.EVT_BUTTON, self.on_import, self.import_button)
		self.Bind(wx.EVT_BUTTON, self.on_remove, self.remove_button)
		self.Bind(wx.EVT_BUTTON, self.on_close, self.close_button)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.view_modify_button, 0, wx.ALL, 10)
		buttons.Add(self.new_button, 0, wx.ALL, 10)
		buttons.Add(self.copy_button, 0, wx.ALL, 10)
		buttons.Add(self.import_button, 0, wx.ALL, 10)
		buttons.Add(self.remove_button, 0, wx.ALL, 10)
		buttons.Add(self.close_button, 0, wx.ALL, 10)
		
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
		
		# Put the materials in the grid.
		self.reset_grid()
		
		# The context menu key or right clicking on a cell opens a popup
		# menu. Double clicking opens the material. 
		self.material_grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
		self.material_grid.GetGridWindow().Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
		self.material_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_double_click)
		
		# Manage selection events to prevent selections.
		self.material_grid.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.on_range_selection)
		self.material_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_selection)
		
		# Catch char events (to process ESC).
		self.Bind(wx.EVT_CHAR_HOOK, self.on_char)
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		# Prepare the context menu.
		self.context_menu = wx.Menu()
		self.view_modify_ID = wx.NewId()
		self.context_menu.Append(self.view_modify_ID, "&View/Modify")
		self.Bind(wx.EVT_MENU, self.on_view_modify, id = self.view_modify_ID)
		self.copy_ID = wx.NewId()
		self.context_menu.Append(self.copy_ID, "&Copy")
		self.Bind(wx.EVT_MENU, self.on_copy, id = self.copy_ID)
		self.remove_ID = wx.NewId()
		self.context_menu.Append(self.remove_ID, "&Remove")
		self.Bind(wx.EVT_MENU, self.on_remove, id = self.remove_ID)
	
	
	######################################################################
	#                                                                    #
	# reset_grid                                                         #
	#                                                                    #
	######################################################################
	def reset_grid(self):
		"""Redraw the whole grid
		
		This method does not take or return any argument."""
		
		# Get all the materials and some information about them.
		self.materials = []
		for i_catalog, catalog in enumerate(self.catalogs):
			names = catalog.get_material_names()
			materials_in_catalog = [None]*len(names)
			for i_material, name in enumerate(names):
				try:
					material = catalog.get_material(name)
				except materials.material_parsing_error:
					material = None
				materials_in_catalog[i_material] = (i_catalog, name, material)
			self.materials += materials_in_catalog
		
		# Reorganize the materials in alphabetical order.
		self.materials.sort(key = lambda material_and_properties: material_and_properties[1].upper())
		
		self.material_grid.BeginBatch()
		
		nb_rows = self.material_grid.GetNumberRows()
		nb_materials = len(self.materials)
		
		if nb_materials > nb_rows:
			self.material_grid.AppendRows(nb_materials-nb_rows)
		elif nb_materials < nb_rows:
			self.material_grid.DeleteRows(nb_materials, nb_rows-nb_materials)
		
		for i, material_and_properties in enumerate(self.materials):
			material = material_and_properties[2]
			self.material_grid.SetCellValue(i, 0, material_and_properties[1])
			self.material_grid.SetCellValue(i, 3, self.locations[material_and_properties[0]])
			if material:
				self.material_grid.SetCellValue(i, 1, materials.KINDS[material.get_kind()])
				self.material_grid.SetCellValue(i, 2, materials.MODELS[material.get_model()])
				if i+1 < nb_materials and self.materials[i+1][2] and self.materials[i+1][1].upper() == material_and_properties[1].upper():
					self.material_grid.SetCellTextColour(i, 0, wx.LIGHT_GREY)
					self.material_grid.SetCellTextColour(i, 1, wx.LIGHT_GREY)
					self.material_grid.SetCellTextColour(i, 2, wx.LIGHT_GREY)
					self.material_grid.SetCellTextColour(i, 3, wx.LIGHT_GREY)
				else:
					self.material_grid.SetCellTextColour(i, 0, wx.BLACK)
					self.material_grid.SetCellTextColour(i, 1, wx.BLACK)
					self.material_grid.SetCellTextColour(i, 2, wx.BLACK)
					self.material_grid.SetCellTextColour(i, 3, wx.BLACK)
			else:
				self.material_grid.SetCellTextColour(i, 0, wx.RED)
				self.material_grid.SetCellTextColour(i, 3, wx.RED)
		
		self.material_grid.EndBatch()
		
		self.update()
	
	
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
		
		row = self.material_grid.GetGridCursorRow()
		self.material_grid.ClearSelection()
		self.material_grid.SelectRow(row)
		
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
		
		if row != self.material_grid.GetGridCursorRow() or not self.material_grid.IsSelection():
			self.operating_on_selection = True
			
			self.material_grid.SelectRow(row)
			self.update(row)
			
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
		
		self.material_grid.SetGridCursor(event.GetRow(), event.GetCol())
		
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
		
		rect = self.material_grid.CellToRect(self.material_grid.GetGridCursorRow(), self.material_grid.GetGridCursorCol())
		
		position = rect.GetTopLeft() + wx.Point(self.material_grid.GetRowLabelSize()+rect.width//2, self.material_grid.GetColLabelSize()+rect.height//2)
		
		self.show_context_menu(position)
	
	
	######################################################################
	#                                                                    #
	# on_double_click                                                    #
	#                                                                    #
	######################################################################
	def on_double_click(self, event):
		"""View and/or modify a material when the user double clicks
		
		This method takes a single argument:
		  event              the event."""
		
		# Get the row that was clicked.
		row = event.GetRow()
		
		self.view_modify(row)
	
	
	######################################################################
	#                                                                    #
	# on_view_modify                                                     #
	#                                                                    #
	######################################################################
	def on_view_modify(self, event):
		"""View and/or modify a material when the menu item is selected or the button is clicked
		
		This method takes a single argument:
		  event              the event."""
		
		self.view_modify(self.material_grid.GetGridCursorRow())
	
	
	######################################################################
	#                                                                    #
	# on_new                                                             #
	#                                                                    #
	######################################################################
	def on_new(self, event):
		"""Create a new material when the menu item is selected or the button is clicked
		
		This method takes a single argument:
		  event              the event."""
		
		user_catalog = self.catalogs[self.user_catalog_nb]
		
		material = None
		
		window = new_material_dialog(self, user_catalog)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			material = window.get_new_material()
		
		window.Destroy()
		
		if material:
			window = open_material_dialog(self, material, True)
			
			answer = window.ShowModal()
			
			if answer == wx.ID_OK:
				window.apply_modifications()
				try:
					user_catalog.add_material(material)
				except:
					wx.MessageBox("Cannot write material. Check permissions to the user material directory.", "Error", wx.ICON_ERROR|wx.OK)
			
			window.Destroy()
			
			self.reset_grid()
	
	
	######################################################################
	#                                                                    #
	# on_copy                                                            #
	#                                                                    #
	######################################################################
	def on_copy(self, event):
		"""Copy a material when the menu item is selected or the button is clicked
		
		This method takes a single argument:
		  event              the event."""
		
		row = self.material_grid.GetGridCursorRow()
		
		original_material = self.materials[row][2]
		
		user_catalog = self.catalogs[self.user_catalog_nb]
		
		material = None
		
		window = new_material_dialog(self, user_catalog, original_material)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			material = window.get_new_material()
		
		window.Destroy()
		
		if material:
			window = open_material_dialog(self, material, True)
			
			answer = window.ShowModal()
			
			if answer == wx.ID_OK:
				window.apply_modifications()
				try:
					user_catalog.add_material(material)
				except:
					wx.MessageBox("Cannot write material. Check permissions to the user material directory.", "Error", wx.ICON_ERROR|wx.OK)
			
			window.Destroy()
			
			self.reset_grid()
	
	
	######################################################################
	#                                                                    #
	# on_import                                                          #
	#                                                                    #
	######################################################################
	def on_import(self, event):
		"""Import a new material when button is clicked
		
		This method takes a single argument:
		  event              the event."""
		
		user_catalog = self.catalogs[self.user_catalog_nb]
		
		material = None
		
		window = import_material_dialog(self, user_catalog)
		
		answer = window.ShowModal()
		if answer == wx.ID_OK:
			try:
				material = window.get_material()
			except materials.material_error, error:
				wx.MessageBox("An error occured while importing the material.\n\n%s" % error, "Error", wx.ICON_ERROR|wx.OK)
		
		window.Destroy()
		
		if material:
			window = open_material_dialog(self, material, True)
			
			answer = window.ShowModal()
			
			if answer == wx.ID_OK:
				window.apply_modifications()
				try:
					user_catalog.add_material(material)
				except:
					wx.MessageBox("Cannot write material. Check permissions to the user material directory.", "Error", wx.ICON_ERROR|wx.OK)
			
			window.Destroy()
			
			self.reset_grid()
	
	
	######################################################################
	#                                                                    #
	# on_remove                                                          #
	#                                                                    #
	######################################################################
	def on_remove(self, event):
		"""Remove a material when the menu item is selected or the button is clicked
		
		This method takes a single argument:
		  event              the event."""
		
		row = self.material_grid.GetGridCursorRow()
		
		catalog = self.catalogs[self.materials[row][0]]
		
		try:
			catalog.remove_material(self.materials[row][1])
		except (OSError, IOError):
			wx.MessageBox("Cannot delete the material. Check permissions to the user material directory.", "Error", wx.ICON_ERROR|wx.OK)
		
		self.reset_grid()
	
	
	######################################################################
	#                                                                    #
	# on_close                                                           #
	#                                                                    #
	######################################################################
	def on_close(self, event):
		"""Close the dialog
		
		This method takes a single argument:
		  event              the event."""
		
		self.EndModal(wx.ID_CLOSE)
	
	
	######################################################################
	#                                                                    #
	# show_context_menu                                                  #
	#                                                                    #
	######################################################################
	def show_context_menu(self, position = wx.DefaultPosition):
		"""Show a context menu
		
		This method takes a single argument:
		  position           the position where to put the popup munu."""
		
		row = self.material_grid.GetGridCursorRow()
		
		if self.catalogs[self.materials[row][0]].is_default_material_catalog() or not self.allow_modifications:
			self.context_menu.SetLabel(self.view_modify_ID, "&View")
		else:
			self.context_menu.SetLabel(self.view_modify_ID, "&View/Modify")
		
		if self.materials[row][2]:
			if self.catalogs[self.materials[row][0]].is_default_material_catalog():
				self.context_menu.Enable(self.view_modify_ID, True)
				if self.has_user_catalog and self.allow_modifications:
					self.context_menu.Enable(self.copy_ID, True)
				else:
					self.context_menu.Enable(self.copy_ID, False)
				self.context_menu.Enable(self.remove_ID, False)
			else:
				if self.allow_modifications:
					self.context_menu.Enable(self.view_modify_ID, True)
					self.context_menu.Enable(self.copy_ID, True)
					self.context_menu.Enable(self.remove_ID, True)
				else:
					self.context_menu.Enable(self.view_modify_ID, True)
					self.context_menu.Enable(self.copy_ID, False)
					self.context_menu.Enable(self.remove_ID, False)
		elif not self.catalogs[self.materials[row][0]].is_default_material_catalog() and self.allow_modifications:
			self.context_menu.Enable(self.view_modify_ID, False)
			self.context_menu.Enable(self.copy_ID, False)
			self.context_menu.Enable(self.remove_ID, True)
		else:
			self.context_menu.Enable(self.view_modify_ID, False)
			self.context_menu.Enable(self.copy_ID, False)
			self.context_menu.Enable(self.remove_ID, False)
		
		self.PopupMenu(self.context_menu, position)
	
	
	######################################################################
	#                                                                    #
	# view_modify                                                        #
	#                                                                    #
	######################################################################
	def view_modify(self, row):
		"""View and/or modify a material
		
		This method takes a single argument:
		  row                the position of the material in the grid."""
		
		catalog = self.catalogs[self.materials[row][0]]
		material = self.materials[row][2]
		
		if not material: return
		
		if catalog.is_default_material_catalog():
			allow_modifications = False
		else:
			allow_modifications = self.allow_modifications
		
		if allow_modifications:
			material = material.clone()
		
		window = open_material_dialog(self, material, allow_modifications)
		
		answer = window.ShowModal()
		
		if answer == wx.ID_OK and window.get_modified():
			window.apply_modifications()
			try:
				catalog.add_material(material)
			except (OSError, IOError):
				wx.MessageBox("Cannot write modified material. Check permissions to the user material directory.", "Error", wx.ICON_ERROR|wx.OK)
			else:
				self.materials[row] = (self.materials[row][0], self.materials[row][1], material)
		
		window.Destroy()
	
	
	######################################################################
	#                                                                    #
	# update                                                             #
	#                                                                    #
	######################################################################
	def update(self, row = None):
		"""Update the dialog according to the selection
		
		This method does not take arguments."""
		
		if row is None:
			row = self.material_grid.GetGridCursorRow()
		
		if self.has_user_catalog and self.allow_modifications:
			if self.catalogs[self.materials[row][0]].is_default_material_catalog():
				self.view_modify_button.SetLabel("View")
				self.remove_button.Disable()
			else:
				self.view_modify_button.SetLabel("View/Modify")
				self.remove_button.Enable()
			self.new_button.Enable()
			if self.materials[row][2]:
				self.copy_button.Enable()
			else:
				self.copy_button.Disable()
			self.import_button.Enable()
		else:
			self.view_modify_button.SetLabel("View")
			self.view_modify_button.Enable()
			self.new_button.Disable()
			self.copy_button.Disable()
			self.import_button.Disable()
			self.remove_button.Disable()
			self.close_button.Enable()
		
		if self.materials[row][2]:
			self.view_modify_button.Enable()
		else:
			self.view_modify_button.Disable()
		
		self.close_button.Enable()



########################################################################
#                                                                      #
# material_dialog                                                      #
#                                                                      #
########################################################################
class material_dialog(wx.Dialog):
	"""An abstract dialog class for creating and manipulating materials"""
	
	title = "Material"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, material, allow_modifications = False):
		"""Initialize the dialog
		
		This method takes 2 or 3 arguments:
		  parent                 the window's parent;
		  material               the material being manipulated;
		  allow_modifications    (optional) a boolean indicating if the
		                         user can modify the material."""
		
		self.material = material
		self.allow_modifications = allow_modifications
		
		if allow_modifications:
			self.modified_material = material.clone()
		else:
			self.modified_material = material
		
		title = self.title + " - " + self.material.get_name()
		
		wx.Dialog.__init__(self, parent, -1, title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.description_box = wx.TextCtrl(self, -1, "", size = (-1, -1))
		
		description_sizer = wx.BoxSizer(wx.HORIZONTAL)
		description_sizer.Add(wx.StaticText(self, -1, "Description:"), 0, wx.ALIGN_CENTER_VERTICAL)
		description_sizer.Add(self.description_box, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALIGN_RIGHT|wx.LEFT, 5)
		self.main_sizer.Add(description_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.n_plot = plot(self, size = (800, 150), style = wx.SUNKEN_BORDER)
		self.n_plot.set_xlabel("Wavelength (nm)")
		self.n_plot.set_ylabel("n")
		self.n_plot.set_allow_remove_curve(False)
		self.n_plot.set_clickable()
		self.k_plot = plot(self, size = (800, 150), style = wx.SUNKEN_BORDER)
		self.k_plot.set_xlabel("Wavelength (nm)")
		self.k_plot.set_ylabel("k")
		self.k_plot.set_allow_remove_curve(False)
		self.k_plot.set_clickable()
		self.main_sizer.Add(self.n_plot, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(self.k_plot, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		self.add_properties()
		
		self.add_buttons()
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		self.nb_wvls = 600
		
		self.select_wavelengths()
		
		self.show_description()
		self.show_properties()
		self.update_plots()
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# add_buttons                                                        #
	#                                                                    #
	######################################################################
	def add_buttons(self):
		"""Add ok and cancel buttons to the dialog"""
		
		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.ok_button, 0, wx.ALL, 10)
		buttons.Add(self.cancel_button, 0, wx.ALL, 10)
		
		# Call a specific on_cancel function that will unbind some events in
		# order to be able to cancel.
		self.Bind(wx.EVT_BUTTON, self.on_cancel, id = wx.ID_CANCEL)
		
		# Add buttons to the window.
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
	
	
	######################################################################
	#                                                                    #
	# select_wavelengths                                                 #
	#                                                                    #
	######################################################################
	def select_wavelengths(self, min_wvl = None, max_wvl = None):
		"""Select a wavelength range
		
		This method takes two optional arguments:
		  min_wvl            (optional) the minimum wavelength;
		  max_wvl            (optional) the maximum wavelength.
		
		If the arguments are not provided, default values (300nm and
		1000nm) are used."""
		
		if not min_wvl: min_wvl = 300.0
		if not max_wvl: max_wvl = 1000.0
		
		self.wvls = abeles.wvls(self.nb_wvls)
		self.wvls.set_wvls_by_range(min_wvl, (max_wvl-min_wvl)/(self.nb_wvls-1))
	
	
	######################################################################
	#                                                                    #
	# show_description                                                   #
	#                                                                    #
	######################################################################
	def show_description(self):
		"""Show the description of the material
		
		Modify the content of the description box."""
		
		self.description_box.SetValue(self.material.get_description())
		
		if not self.allow_modifications:
			self.description_box.Disable()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self, reset = True):
		"""Update the n and k plots
		
		This method takes one optional argument:
		  reset              (optional) a boolean indicating if the plots
		                     need to be reset before updating them; this
		                     allows subclasses to reset the plots and put
		                     elements in them before calling this method,
		                     when necessary (default value is True)."""
		
		N = self.modified_material.get_N(self.wvls)
		
		n = [N[i].real for i in range(self.nb_wvls)]
		k = [-N[i].imag for i in range(self.nb_wvls)]
		
		self.n_plot.begin_batch()
		self.k_plot.begin_batch()
		if reset:
			self.n_plot.reset()
			self.k_plot.reset()
		self.n_plot.add_curve(plot_curve(self.wvls, n, style = plot_curve_style(colour = "BLUE")))
		self.k_plot.add_curve(plot_curve(self.wvls, k, style = plot_curve_style(colour = "BLUE")))
		self.n_plot.end_batch()
		self.k_plot.end_batch()
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method must be implemented by derived classes."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed
		
		This method takes a single argument:
		  event              the event."""
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if self.description_box.GetValue() != self.material.get_description():
			return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		self.material.set_description(self.description_box.GetValue())



########################################################################
#                                                                      #
# material_mixture_dialog                                              #
#                                                                      #
########################################################################
class material_mixture_dialog(material_dialog):
	"""An abstract dialog class for creating and manipulating mixture
	materials"""
	
	title = "Material"
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self, reset = True):
		"""Update the n and k plots
		
		This method takes one optional argument:
		  reset              (optional) a boolean indicating if the plots
		                     need to be reset before updating them; this
		                     allows subclasses to reset the plots and put
		                     elements in them before calling this method,
		                     when necessary (default value is True)."""
		
		N = self.modified_material.get_N(self.wvls)
		N_mixture = N.get_N_mixture()
		
		X = self.modified_material.X
		
		nb_mixtures = len(X)
		
		n = [None]*nb_mixtures
		k = [None]*nb_mixtures
		
		for i_mix in range(nb_mixtures):
			N.set_N_mixture_by_x(X[i_mix])
			
			n[i_mix] = [N_mixture[i_wvl].real for i_wvl in range(self.nb_wvls)]
			k[i_mix] = [-N_mixture[i_wvl].imag for i_wvl in range(self.nb_wvls)]
		
		self.n_plot.begin_batch()
		self.k_plot.begin_batch()
		if reset:
			self.n_plot.reset()
			self.k_plot.reset()
		for i_mix in range(nb_mixtures):
			self.n_plot.add_curve(plot_curve(self.wvls, n[i_mix], style = plot_curve_style(colour = "BLUE")))
			self.k_plot.add_curve(plot_curve(self.wvls, k[i_mix], style = plot_curve_style(colour = "BLUE")))
		self.n_plot.end_batch()
		self.k_plot.end_batch()



########################################################################
#                                                                      #
# material_constant_dialog                                             #
#                                                                      #
########################################################################
class material_constant_dialog(material_dialog):
	"""A dialog class for creating and manipulating regular
	dispersionless materials"""
	
	title = "Constant Material"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to set n and k to the dialog."""
		
		self.n_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.k_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		
		self.n_box.Bind(wx.EVT_KILL_FOCUS, self.on_n_or_k_box)
		self.k_box.Bind(wx.EVT_KILL_FOCUS, self.on_n_or_k_box)
		
		properties_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		properties_sizer.Add(wx.StaticText(self, -1, "n:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer.Add(self.n_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer.Add(wx.StaticText(self, -1, "k:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer.Add(self.k_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		self.main_sizer.Add(properties_sizer, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the n
		and k text boxes."""
		
		N, = self.material.get_properties()
		
		self.n_box.SetValue("%#g" % N.real)
		self.k_box.SetValue("%#g" % (-N.imag if N.imag else 0.0))
		
		if not self.allow_modifications:
			self.n_box.Disable()
			self.k_box.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_n_or_k_box                                                      #
	#                                                                    #
	######################################################################
	def on_n_or_k_box(self, event):
		"""Handle the event when n or k is entered
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots"""
		
		try:
			n = float(self.n_box.GetValue())
			k = float(self.k_box.GetValue())
		except ValueError:
			self.n_plot.reset()
			self.k_plot.reset()
		else:
			N = complex(n, -k)
			self.modified_material.set_properties(N)
			material_dialog.update_plots(self)
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_dialog.get_modified(self):
			return True
		
		N, = self.material.get_properties()
		
		n = float(self.n_box.GetValue())
		k = float(self.k_box.GetValue())
		
		if n != N.real or k != -N.imag:
			return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_dialog.apply_modifications(self)
		
		n = float(self.n_box.GetValue())
		k = float(self.k_box.GetValue())
		
		N = complex(n, -k)
		
		self.material.set_properties(N)



########################################################################
#                                                                      #
# material_table_dialog                                                #
#                                                                      #
########################################################################
class material_table_dialog(material_dialog):
	"""A dialog class for creating and manipulating regular materials
	defined by a table of indices"""
	
	title = "Table Material"
	
	
	######################################################################
	#                                                                    #
	# select_wavelengths                                                 #
	#                                                                    #
	######################################################################
	def select_wavelengths(self, min_wvl = None, max_wvl = None):
		"""Select a wavelength range
		
		This method takes two optional arguments:
		  min_wvl            (optional) the minimum wavelength;
		  max_wvl            (optional) the maximum wavelength.
		
		If the arguments are not provided, the range where the table is
		defined is used by default."""
		
		wvls, N = self.modified_material.get_properties()
		
		if not min_wvl: min_wvl = min(wvls)
		if not max_wvl: max_wvl = max(wvls)
		
		material_dialog.select_wavelengths(self, min_wvl, max_wvl)
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to set the number of wavelengths and a
		grid to set n and k."""
		
		# A box to specify the nb of points in the definition.
		self.nb_wvls_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_wvls_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_wvls)
		
		# Add a table to specify the index.
		self.grid = wx.grid.Grid(self, -1, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.grid.CreateGrid(0, 3)
		self.grid.SetColSize(0, 140)
		self.grid.SetColLabelValue(0, "Wavelength (nm)")
		self.grid.SetColSize(1, 100)
		self.grid.SetColLabelValue(1, "n")
		self.grid.SetColSize(2, 100)
		self.grid.SetColLabelValue(2, "k")
		
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.grid.DisableDragColSize()
		self.grid.DisableDragGridSize()
		self.grid.DisableDragRowSize()
		
		self.grid.SetValidator(material_table_validator())
		
		# Put the nb points box in a sizer.
		nb_wvls_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_wvls_sizer.Add(wx.StaticText(self, -1, "Nb wavelengths:"),
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_wvls_sizer.Add(self.nb_wvls_box,
		                  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.main_sizer.Add(nb_wvls_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		wvls, N = self.material.get_properties()
		
		nb_wvls = len(wvls)
		
		self.nb_wvls_box.SetValue("%i" % nb_wvls)
		
		self.grid.AppendRows(nb_wvls)
		
		for i in range(nb_wvls):
			self.grid.SetCellValue(i, 0, "%f" % wvls[i])
			self.grid.SetCellValue(i, 1, "%#g" % N[i].real)
			self.grid.SetCellValue(i, 2, "%#g" % (-N[i].imag if N[i].imag else 0.0))
		
		if not self.allow_modifications:
			self.nb_wvls_box.Disable()
			self.grid.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS event of the nb_wvls_box.
		self.nb_wvls_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_nb_wvls                                                         #
	#                                                                    #
	######################################################################
	def on_nb_wvls(self, event):
		"""Handle text and kill focus events for the number of wavelength
		box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of wavelengths."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_wvls_box.GetValidator().Validate(self):
			return
		
		nb_wvls = int(self.nb_wvls_box.GetValue())
		
		nb_rows = self.grid.GetNumberRows()
		
		if nb_wvls > nb_rows:
			self.grid.AppendRows(nb_wvls-nb_rows)
		elif nb_wvls < nb_rows:
			self.grid.DeleteRows(nb_wvls, nb_rows-nb_wvls)
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Handle the event when a cell changes
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to read index values from the grid. It then plots
		the result."""
		
		nb_wavelengths = int(self.nb_wvls_box.GetValue())
		
		wvls = [None]*nb_wavelengths
		n = [None]*nb_wavelengths
		k = [None]*nb_wavelengths
		
		for i in range(nb_wavelengths):
			try:
				wvl = float(self.grid.GetCellValue(i, 0))
				n_i = float(self.grid.GetCellValue(i, 1))
				k_i = float(self.grid.GetCellValue(i, 2))
			except ValueError:
				pass
			else:
				wvls[i] = wvl
				n[i] = n_i
				k[i] = k_i
		
		self.n_plot.begin_batch()
		self.k_plot.begin_batch()
		
		self.n_plot.reset()
		self.k_plot.reset()
		
		wvls_, n_, = zip(*[(wvls[i], n[i]) for i in range(nb_wavelengths) if wvls[i] != None and n[i] != None]) or ([], [])
		self.n_plot.add_curve(plot_curve(wvls_, n_, style = plot_curve_style(colour = "RED", width = 0, marker = "x")))
		
		wvls_, k_, = zip(*[(wvls[i], k[i]) for i in range(nb_wavelengths) if wvls[i] != None and k[i] != None]) or ([], [])
		self.k_plot.add_curve(plot_curve(wvls_, k_, style = plot_curve_style(colour = "RED", width = 0, marker = "x")))
		
		if all(wvl is not None for wvl in wvls) and all(n_i is not None for n_i in n) and all(k_i is not None for k_i in k) and all(wvls[i] > wvls[i-1] for i in range(1, len(wvls))):
			N = [complex(n[i], -k[i]) for i in range(len(wvls))]
			self.modified_material.set_properties(wvls, N)
			self.select_wavelengths()
			material_dialog.update_plots(self, reset = False)
		
		self.n_plot.end_batch()
		self.k_plot.end_batch()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_dialog.get_modified(self):
			return True
		
		wvls, N = self.material.get_properties()
		
		nb_wvls = len(wvls)
		
		if int(self.nb_wvls_box.GetValue()) != nb_wvls:
			return True
		
		for i in range(nb_wvls):
			wvl = float(self.grid.GetCellValue(i, 0))
			n = float(self.grid.GetCellValue(i, 1))
			k = float(self.grid.GetCellValue(i, 2))
			if wvl != wvls[i] or n != N[i].real or k != -N[i].imag:
				return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_dialog.apply_modifications(self)
		
		nb_wvls = int(self.nb_wvls_box.GetValue())
		
		wvls = [float(self.grid.GetCellValue(i, 0)) for i in range(nb_wvls)]
		N = [complex(float(self.grid.GetCellValue(i, 1)), -float(self.grid.GetCellValue(i, 2))) for i in range(nb_wvls)]
		
		self.material.set_properties(wvls, N)



########################################################################
#                                                                      #
# material_Cauchy_dialog                                               #
#                                                                      #
########################################################################
class material_Cauchy_dialog(material_dialog):
	"""A dialog class for creating and manipulating regular materials
	defined by a Cauchy dispersion formula"""
	
	title = "Cauchy Material"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls for the parameters of the Cauchy
		dispersion formula."""
		
		self.A_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.B_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.C_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.A_k_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.exponent_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.edge_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None, include_minimum = False))
		
		self.A_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.B_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.C_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.A_k_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.exponent_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.edge_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		
		properties_sizer = wx.BoxSizer(wx.VERTICAL)
		properties_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		properties_sizer_1.Add(wx.StaticText(self, -1, "A:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(self.A_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_1.Add(wx.StaticText(self, -1, "B:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_1.Add(self.B_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_1.Add(wx.StaticText(self, -1, "C:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_1.Add(self.C_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_2.Add(wx.StaticText(self, -1, "A_k:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_2.Add(self.A_k_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_2.Add(wx.StaticText(self, -1, "Exponent:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_2.Add(self.exponent_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_2.Add(wx.StaticText(self, -1, "Edge:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_2.Add(self.edge_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer.Add(properties_sizer_1, 0)
		properties_sizer.Add(properties_sizer_2, 0, wx.TOP, 5)
		
		self.main_sizer.Add(properties_sizer, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		A, B, C, A_k, exponent, edge = self.material.get_properties()
		
		self.A_box.SetValue("%#g" % A)
		self.B_box.SetValue("%#g" % B)
		self.C_box.SetValue("%#g" % C)
		
		self.A_k_box.SetValue("%#g" % A_k)
		self.exponent_box.SetValue("%#g" % exponent)
		self.edge_box.SetValue("%#g" % edge)
		
		if not self.allow_modifications:
			self.A_box.Disable()
			self.B_box.Disable()
			self.C_box.Disable()
			self.A_k_box.Disable()
			self.exponent_box.Disable()
			self.edge_box.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS events.
		self.A_box.Unbind(wx.EVT_KILL_FOCUS)
		self.B_box.Unbind(wx.EVT_KILL_FOCUS)
		self.C_box.Unbind(wx.EVT_KILL_FOCUS)
		self.A_k_box.Unbind(wx.EVT_KILL_FOCUS)
		self.exponent_box.Unbind(wx.EVT_KILL_FOCUS)
		self.edge_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_property_box                                                    #
	#                                                                    #
	######################################################################
	def on_property_box(self, event):
		"""Handle the event when one of the parameter of the Cauchy model is changed
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to interpret the optical properties from the
		dialog. If they make sense, they are ploted."""
		
		try:
			A = float(self.A_box.GetValue())
			B = float(self.B_box.GetValue())
			C = float(self.C_box.GetValue())
			A_k = float(self.A_k_box.GetValue())
			exponent = float(self.exponent_box.GetValue())
			edge = float(self.edge_box.GetValue())
		except ValueError:
			self.n_plot.reset()
			self.k_plot.reset()
		else:
			self.modified_material.set_properties(A, B, C, A_k, exponent, edge)
			material_dialog.update_plots(self)
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_dialog.get_modified(self):
			return True
		
		A, B, C, A_k, exponent, edge = self.material.get_properties()
		
		new_A = float(self.A_box.GetValue())
		new_B = float(self.B_box.GetValue())
		new_C = float(self.C_box.GetValue())
		new_A_k = float(self.A_k_box.GetValue())
		new_exponent = float(self.exponent_box.GetValue())
		new_edge = float(self.edge_box.GetValue())
		
		if new_A != A or new_B != B or new_C != C:
			return True
		if new_A_k != A_k or new_exponent != exponent or new_edge != edge:
			return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_dialog.apply_modifications(self)
		
		A = float(self.A_box.GetValue())
		B = float(self.B_box.GetValue())
		C = float(self.C_box.GetValue())
		A_k = float(self.A_k_box.GetValue())
		exponent = float(self.exponent_box.GetValue())
		edge = float(self.edge_box.GetValue())
		
		self.material.set_properties(A, B, C, A_k, exponent, edge)



########################################################################
#                                                                      #
# material_Sellmeier_dialog                                            #
#                                                                      #
########################################################################
class material_Sellmeier_dialog(material_dialog):
	"""A dialog class for creating and manipulating regular materials
	defined by a Sellmeier dispersion formula"""
	
	title = "Sellmeier Material"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls for the parameters of the Sellmeier
		dispersion formula."""
		
		self.B1_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.B2_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.B3_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.C1_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.C2_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.C3_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator())
		self.A_k_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.exponent_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None))
		self.edge_box = wx.TextCtrl(self, -1, "", size = (75, -1), validator = float_validator(0.0, None, include_minimum = False))
		
		self.B1_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.B2_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.B3_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.C1_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.C2_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.C3_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.A_k_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.exponent_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		self.edge_box.Bind(wx.EVT_KILL_FOCUS, self.on_property_box)
		
		properties_sizer = wx.BoxSizer(wx.VERTICAL)
		properties_sizer_1 = wx.FlexGridSizer(2, 3, 5, 15)
		properties_sizer_1_1 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_1_2 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_1_3 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_1_4 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_1_5 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_1_6 = wx.BoxSizer(wx.HORIZONTAL)
		properties_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		properties_sizer_1_1.Add(wx.StaticText(self, -1, "B1:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_1.Add(self.B1_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1_2.Add(wx.StaticText(self, -1, "B2:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_2.Add(self.B2_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1_3.Add(wx.StaticText(self, -1, "B3:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_3.Add(self.B3_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1_4.Add(wx.StaticText(self, -1, "C1:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_4.Add(self.C1_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1_5.Add(wx.StaticText(self, -1, "C2:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_5.Add(self.C2_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1_6.Add(wx.StaticText(self, -1, "C3:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1_6.Add(self.C3_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer_1.Add(properties_sizer_1_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(properties_sizer_1_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(properties_sizer_1_3, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(properties_sizer_1_4, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(properties_sizer_1_5, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_1.Add(properties_sizer_1_6, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		
		properties_sizer_2.Add(wx.StaticText(self, -1, "A_k:"), 0, wx.ALIGN_CENTER_VERTICAL)
		properties_sizer_2.Add(self.A_k_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_2.Add(wx.StaticText(self, -1, "Exponent:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_2.Add(self.exponent_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		properties_sizer_2.Add(wx.StaticText(self, -1, "Edge:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)
		properties_sizer_2.Add(self.edge_box, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		properties_sizer.Add(properties_sizer_1, 0)
		properties_sizer.Add(properties_sizer_2, 0, wx.TOP, 5)
		
		self.main_sizer.Add(properties_sizer, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		B1, C1, B2, C2, B3, C3, A_k, exponent, edge = self.material.get_properties()
		
		self.B1_box.SetValue("%#g" % B1)
		self.B2_box.SetValue("%#g" % B2)
		self.B3_box.SetValue("%#g" % B3)
		self.C1_box.SetValue("%#g" % C1)
		self.C2_box.SetValue("%#g" % C2)
		self.C3_box.SetValue("%#g" % C3)
		
		self.A_k_box.SetValue("%#g" % A_k)
		self.exponent_box.SetValue("%#g" % exponent)
		self.edge_box.SetValue("%#g" % edge)
		
		if not self.allow_modifications:
			self.B1_box.Disable()
			self.B2_box.Disable()
			self.B3_box.Disable()
			self.C1_box.Disable()
			self.C2_box.Disable()
			self.C3_box.Disable()
			self.A_k_box.Disable()
			self.exponent_box.Disable()
			self.edge_box.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS events.
		self.B1_box.Unbind(wx.EVT_KILL_FOCUS)
		self.B2_box.Unbind(wx.EVT_KILL_FOCUS)
		self.B3_box.Unbind(wx.EVT_KILL_FOCUS)
		self.C1_box.Unbind(wx.EVT_KILL_FOCUS)
		self.C2_box.Unbind(wx.EVT_KILL_FOCUS)
		self.C3_box.Unbind(wx.EVT_KILL_FOCUS)
		self.A_k_box.Unbind(wx.EVT_KILL_FOCUS)
		self.exponent_box.Unbind(wx.EVT_KILL_FOCUS)
		self.edge_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_property_box                                                    #
	#                                                                    #
	######################################################################
	def on_property_box(self, event):
		"""Handle the event when one of the parameter of the Sellmeier model is changed
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to interpret the optical properties from the
		dialog. If they make sense, they are ploted."""
		
		try:
			B1 = float(self.B1_box.GetValue())
			B2 = float(self.B2_box.GetValue())
			B3 = float(self.B3_box.GetValue())
			C1 = float(self.C1_box.GetValue())
			C2 = float(self.C2_box.GetValue())
			C3 = float(self.C3_box.GetValue())
			A_k = float(self.A_k_box.GetValue())
			exponent = float(self.exponent_box.GetValue())
			edge = float(self.edge_box.GetValue())
		except ValueError:
			self.n_plot.reset()
			self.k_plot.reset()
		else:
			self.modified_material.set_properties(B1, C1, B2, C2, B3, C3, A_k, exponent, edge)
			material_dialog.update_plots(self)
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_dialog.get_modified(self):
			return True
		
		B1, C1, B2, C2, B3, C3, A_k, exponent, edge = self.material.get_properties()
		
		new_B1 = float(self.B1_box.GetValue())
		new_C1 = float(self.C1_box.GetValue())
		new_B2 = float(self.B2_box.GetValue())
		new_C2 = float(self.C2_box.GetValue())
		new_B3 = float(self.B3_box.GetValue())
		new_C3 = float(self.C3_box.GetValue())
		new_A_k = float(self.A_k_box.GetValue())
		new_exponent = float(self.exponent_box.GetValue())
		new_edge = float(self.edge_box.GetValue())
		
		if new_B1 != B1 or new_C1 != C1 or new_B2 != B2 or new_C2 != C2 or new_B3 != B3 or new_C3 != C3:
			return True
		if new_A_k != A_k or new_exponent != exponent or new_edge != edge:
			return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_dialog.apply_modifications(self)
		
		B1 = float(self.B1_box.GetValue())
		C1 = float(self.C1_box.GetValue())
		B2 = float(self.B2_box.GetValue())
		C2 = float(self.C2_box.GetValue())
		B3 = float(self.B3_box.GetValue())
		C3 = float(self.C3_box.GetValue())
		A_k = float(self.A_k_box.GetValue())
		exponent = float(self.exponent_box.GetValue())
		edge = float(self.edge_box.GetValue())
		
		self.material.set_properties(B1, C1, B2, C2, B3, C3, A_k, exponent, edge)



########################################################################
#                                                                      #
# material_mixture_constant_dialog                                     #
#                                                                      #
########################################################################
class material_mixture_constant_dialog(material_mixture_dialog):
	"""A dialog class for creating and manipulating mixture
	dispersionless materials"""
	
	title = "Constant Mixture"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to set the number of mixtures and a grid
		to set the n and k values."""
		
		# A box to specify the nb of mixtures in the definition.
		self.nb_mixtures_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_mixtures_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_mixtures)
		
		# Add a table to specify the index..
		self.grid = wx.grid.Grid(self, -1, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.grid.CreateGrid(0, 3)
		self.grid.SetColSize(0, 80)
		self.grid.SetColLabelValue(0, "Mixture")
		self.grid.SetColSize(1, 100)
		self.grid.SetColLabelValue(1, "n")
		self.grid.SetColSize(2, 100)
		self.grid.SetColLabelValue(2, "k")
		
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.grid.DisableDragColSize()
		self.grid.DisableDragGridSize()
		self.grid.DisableDragRowSize()
		
		self.grid.SetValidator(material_mixture_constant_validator())
		
		# Put the nb points box in a sizer.
		nb_mixtures_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_mixtures_sizer.Add(wx.StaticText(self, -1, "Nb mixtures:"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_mixtures_sizer.Add(self.nb_mixtures_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.main_sizer.Add(nb_mixtures_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		X, N = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		self.nb_mixtures_box.SetValue("%i" % nb_mixtures)
		
		self.grid.AppendRows(nb_mixtures)
		
		for i in range(nb_mixtures):
			self.grid.SetCellValue(i, 0, "%i" % X[i])
			self.grid.SetCellValue(i, 1, "%#g" % N[i].real)
			self.grid.SetCellValue(i, 2, "%#g" % (-N[i].imag if N[i].imag else 0.0))
		
		if not self.allow_modifications:
			self.nb_mixtures_box.Disable()
			self.grid.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS event of the nb_mixtures_box.
		self.nb_mixtures_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_mixture_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_nb_mixtures                                                     #
	#                                                                    #
	######################################################################
	def on_nb_mixtures(self, event):
		"""Handle text and kill focus events for the number of mixture
		box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of mixtures and
		updates the plots."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_mixtures_box.GetValidator().Validate(self):
			return
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		nb_rows = self.grid.GetNumberRows()
		
		if nb_mixtures > nb_rows:
			self.grid.AppendRows(nb_mixtures-nb_rows)
		elif nb_mixtures < nb_rows:
			self.grid.DeleteRows(nb_mixtures, nb_rows-nb_mixtures)
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Handle the event when a cell changes
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to read index values from the grid. If a row does
		not make sense, it simply ignores it. It then plots the result."""
		
		N = []
		
		for i in range(int(self.nb_mixtures_box.GetValue())):
			try:
				n = float(self.grid.GetCellValue(i, 1))
				k = float(self.grid.GetCellValue(i, 2))
			except ValueError:
				pass
			else:
				N.append(complex(n, -k))
		
		if len(N) >= 2:
			# Number the mixtures simply using range. This makes it easier to
			# avoid plot update failures that might happen if the first
			# mixture is not 0, or if the mixtures are not in order. This only
			# applies to the modified material used internally for plotting.
			X = range(len(N))
			
			self.modified_material.set_properties(X, N)
			material_mixture_dialog.update_plots(self)
		else:
			self.n_plot.reset()
			self.k_plot.reset()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_mixture_dialog.get_modified(self):
			return True
		
		X, N = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		if int(self.nb_mixtures_box.GetValue()) != nb_mixtures:
			return True
		
		for i in range(nb_mixtures):
			x = int(self.grid.GetCellValue(i, 0))
			n = float(self.grid.GetCellValue(i, 1))
			k = float(self.grid.GetCellValue(i, 2))
			if x != X[i] or n != N[i].real or k != -N[i].imag:
				return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_mixture_dialog.apply_modifications(self)
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		X = [int(self.grid.GetCellValue(i, 0)) for i in range(nb_mixtures)]
		N = [complex(float(self.grid.GetCellValue(i, 1)), -float(self.grid.GetCellValue(i, 2))) for i in range(nb_mixtures)]
		
		self.material.set_properties(X, N)



########################################################################
#                                                                      #
# material_mixture_table_dialog                                        #
#                                                                      #
########################################################################
class material_mixture_table_dialog(material_mixture_dialog):
	"""A dialog class for creating and manipulating mixture materials
	defined by a table of indices"""
	
	title = "Table Mixture"
	
	
	######################################################################
	#                                                                    #
	# select_wavelengths                                                 #
	#                                                                    #
	######################################################################
	def select_wavelengths(self, min_wvl = None, max_wvl = None):
		"""Select a wavelength range
		
		This method takes two optional arguments:
		  min_wvl            (optional) the minimum wavelength;
		  max_wvl            (optional) the maximum wavelength.
		
		If the arguments are not provided, the range where the table is
		defined is used by default."""
		
		X, wvls, N = self.modified_material.get_properties()
		
		if not min_wvl: min_wvl = min(wvls)
		if not max_wvl: max_wvl = max(wvls)
		
		material_dialog.select_wavelengths(self, min_wvl, max_wvl)
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to set the number of wavelengths, the
		number of mixtures and a grid to set n and k."""
		
		# A box to specify the nb of mixtures in the definition.
		self.nb_mixtures_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_mixtures_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_mixtures)
		
		# A box to specify the nb of wavelengths in the definition.
		self.nb_wvls_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_wvls_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_wavelengths)
		
		# Add a table to specify the index
		self.grid = wx.grid.Grid(self, -1, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.grid.CreateGrid(1, 1)
		self.grid.SetColSize(0, 120)
		self.grid.SetColLabelValue(0, "Wavelength")
		self.grid.SetRowLabelValue(0, "Mixture")
		
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.grid.DisableDragColSize()
		self.grid.DisableDragGridSize()
		self.grid.DisableDragRowSize()
		
		self.grid.SetValidator(material_mixture_table_validator())
		
		# Put the nb points box in a sizer.
		nb_mixtures_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_mixtures_sizer.Add(wx.StaticText(self, -1, "Nb mixtures:"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_mixtures_sizer.Add(self.nb_mixtures_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Put the nb points box in a sizer.
		nb_wavelengths_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_wavelengths_sizer.Add(wx.StaticText(self, -1, "Nb wavelengths:"),
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_wavelengths_sizer.Add(self.nb_wvls_box,
		                         0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.main_sizer.Add(nb_mixtures_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(nb_wavelengths_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		X, wvls, N = self.material.get_properties()
		
		nb_mixtures = len(X)
		nb_wavelengths = len(wvls)
		
		self.nb_mixtures_box.SetValue("%i" % nb_mixtures)
		self.nb_wvls_box.SetValue("%i" % nb_wavelengths)
		
		self.grid.AppendRows(nb_wavelengths)
		self.grid.AppendCols(nb_mixtures)
		
		for i_mix in range(nb_mixtures):
			self.grid.SetColSize(i_mix+1, 100)
			self.grid.SetColLabelValue(i_mix+1, "%i" % (i_mix+1))
			self.grid.SetCellValue(0, i_mix+1, "%i" % X[i_mix])
		
		for i_wvl in range(nb_wavelengths):
			self.grid.SetRowLabelValue(i_wvl+1, "%i" % (i_wvl+1))
			self.grid.SetCellValue(i_wvl+1, 0, "%f" % wvls[i_wvl])
		
		for i_mix in range(nb_mixtures):
			for i_wvl in range(nb_wavelengths):
				self.grid.SetCellValue(i_wvl+1, i_mix+1, ("%s" % N[i_mix][i_wvl])[1:-1])
			
		if not self.allow_modifications:
			self.nb_wvls_box.Disable()
			self.nb_mixtures_box.Disable()
			self.grid.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS event of the nb_mixtures_box and
		# the nb_wvls_box.
		self.nb_mixtures_box.Unbind(wx.EVT_KILL_FOCUS)
		self.nb_wvls_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_mixture_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_nb_mixtures                                                     #
	#                                                                    #
	######################################################################
	def on_nb_mixtures(self, event):
		"""Handle text and kill focus events for the number of mixture
		box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of mixtures."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_mixtures_box.GetValidator().Validate(self):
			return
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		nb_cols = self.grid.GetNumberCols()
		
		if nb_mixtures+1 != nb_cols:
			if nb_mixtures+1 > nb_cols:
				self.grid.AppendCols(nb_mixtures+1-nb_cols)
				for i_mix in range(nb_cols-1, nb_mixtures+1):
					self.grid.SetColLabelValue(i_mix+1, "%i" % (i_mix+1))
			else:
				self.grid.DeleteCols(nb_mixtures+1, nb_cols-nb_mixtures+1)
			
			self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_nb_wavelengths                                                  #
	#                                                                    #
	######################################################################
	def on_nb_wavelengths(self, event):
		"""Handle text and kill focus events for the number of wavelength
		box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of wavelengths."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_wvls_box.GetValidator().Validate(self):
			return
		
		nb_wavelengths = int(self.nb_wvls_box.GetValue())
		nb_rows = self.grid.GetNumberRows()
		
		if nb_wavelengths+1 != nb_rows:
			if nb_wavelengths+1 > nb_rows:
				self.grid.AppendRows(nb_wavelengths+1-nb_rows)
				for i_wvl in range(nb_rows-1, nb_wavelengths+1):
					self.grid.SetRowLabelValue(i_wvl+1, "%i" % (i_wvl+1))
			else:
				self.grid.DeleteRows(nb_wavelengths+1, nb_rows-nb_wavelengths+1)
			
			self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Handle the event when a cell changes
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to read index values from the grid. If a value
		does not make sense, it simply ignores it. It then plots the
		result."""
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		nb_wavelengths = int(self.nb_wvls_box.GetValue())
		
		# Try to read wavelengths as floats.
		wvls = [None]*nb_wavelengths
		for i_wvl in range(nb_wavelengths):
			try:
				wvl = float(self.grid.GetCellValue(i_wvl+1, 0))
			except ValueError:
				pass
			else:
				wvls[i_wvl] = wvl
		
		# Try to read refractive index as complex numbers.
		N = [[None]*nb_wavelengths for i_mix in range(nb_mixtures)]
		for i_mix in range(nb_mixtures):
			for i_wvl in range(nb_wavelengths):
				try:
					N_cell = complex(self.grid.GetCellValue(i_wvl+1, i_mix+1))
				except ValueError:
					pass
				else:
					N[i_mix][i_wvl] = N_cell
		
		self.n_plot.begin_batch()
		self.k_plot.begin_batch()
		
		self.n_plot.reset()
		self.k_plot.reset()
		
		# Plot n and k ignoring wavelengths or refractive indices that
		# could not be read.
		for i_mix in range(nb_mixtures):
			wvls_, n_, k_ = zip(*[(wvls[i_wvl], N[i_mix][i_wvl].real, -N[i_mix][i_wvl].imag) for i_wvl in range(nb_wavelengths) if wvls[i_wvl] != None and N[i_mix][i_wvl] != None]) or ([], [], [])
			self.n_plot.add_curve(plot_curve(wvls_, n_, style = plot_curve_style(colour = "RED", width = 0, marker = "x")))
			self.k_plot.add_curve(plot_curve(wvls_, k_, style = plot_curve_style(colour = "RED", width = 0, marker = "x")))
		
		if all(wvl is not None for wvl in wvls):
			good_mixtures = [i_mix for i_mix in range(nb_mixtures) if all(n is not None for n in N[i_mix])]
			if len(good_mixtures) >= 2:
				# Number the mixtures simply using range. This makes it easier to
				# avoid plot update failures that might happen if the first
				# mixture is not 0, or if the mixtures are not in order. This only
				# applies to the modified material used internally for plotting.
				X = range(len(good_mixtures))
				
				N_ = [N[i_mix] for i_mix in good_mixtures]
				
				self.modified_material.set_properties(X, wvls, N_)
				self.select_wavelengths()
				material_mixture_dialog.update_plots(self, reset = False)
		
		self.n_plot.end_batch()
		self.k_plot.end_batch()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_mixture_dialog.get_modified(self):
			return True
		
		X, wvls, N = self.material.get_properties()
		
		nb_mixtures = len(X)
		nb_wavelengths = len(wvls)
		
		if int(self.nb_mixtures_box.GetValue()) != nb_mixtures:
			return True
		
		if int(self.nb_wvls_box.GetValue()) != nb_wavelengths:
			return True
		
		for i_mix in range(nb_mixtures):
			x = int(self.grid.GetCellValue(0, i_mix+1))
			if x != X[i_mix]:
				return True
		
		for i_wvl in range(nb_wavelengths):
			wvl = float(self.grid.GetCellValue(i_wvl+1, 0))
			if wvl != wvls[i_wvl]:
				return True
		
		for i_mix in range(nb_mixtures):
			for i_wvl in range(nb_wavelengths):
				N_ = complex(self.grid.GetCellValue(i_wvl+1, i_mix+1))
				if N_ != N[i_mix][i_wvl]:
					return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_mixture_dialog.apply_modifications(self)
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		nb_wavelengths = int(self.nb_wvls_box.GetValue())
		
		X = [int(self.grid.GetCellValue(0, i_mix+1)) for i_mix in range(nb_mixtures)]
		wvls = [float(self.grid.GetCellValue(i_wvl+1, 0)) for i_wvl in range(nb_wavelengths)]
		N = [[complex(self.grid.GetCellValue(i_wvl+1, i_mix+1)) for i_wvl in range(nb_wavelengths)] for i_mix in range(nb_mixtures)]
		
		self.material.set_properties(X, wvls, N)



########################################################################
#                                                                      #
# material_mixture_Cauchy_dialog                                       #
#                                                                      #
########################################################################
class material_mixture_Cauchy_dialog(material_mixture_dialog):
	"""A dialog class for creating and manipulating mixture materials
	defined by a Cauchy dispersion formula"""
	
	title = "Cauchy Mixture"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to the number of mixtures and a grid to
		set the properties of the Cauchy model."""
		
		# A box to specify the nb of points in the definition.
		self.nb_mixtures_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_mixtures_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_mixtures)
		
		# Add a table to specify the index.
		self.grid = wx.grid.Grid(self, -1, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.grid.CreateGrid(0, 7)
		self.grid.SetColSize(0, 80)
		self.grid.SetColLabelValue(0, "Mixture")
		self.grid.SetColSize(1, 100)
		self.grid.SetColLabelValue(1, "A")
		self.grid.SetColSize(2, 100)
		self.grid.SetColLabelValue(2, "B")
		self.grid.SetColSize(3, 100)
		self.grid.SetColLabelValue(3, "C")
		self.grid.SetColSize(4, 100)
		self.grid.SetColLabelValue(4, "A_k")
		self.grid.SetColSize(5, 100)
		self.grid.SetColLabelValue(5, "exponent")
		self.grid.SetColSize(6, 100)
		self.grid.SetColLabelValue(6, "edge")
		
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.grid.DisableDragColSize()
		self.grid.DisableDragGridSize()
		self.grid.DisableDragRowSize()
		
		self.grid.SetValidator(material_mixture_Cauchy_validator())
		
		# Put the nb points box in a sizer.
		nb_mixtures_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_mixtures_sizer.Add(wx.StaticText(self, -1, "Nb mixtures:"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_mixtures_sizer.Add(self.nb_mixtures_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.main_sizer.Add(nb_mixtures_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		X, A, B, C, A_k, exponent, edge = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		self.nb_mixtures_box.SetValue("%i" % nb_mixtures)
		
		self.grid.AppendRows(nb_mixtures)
		
		for i in range(nb_mixtures):
			self.grid.SetCellValue(i, 0, "%i" % X[i])
			self.grid.SetCellValue(i, 1, "%#g" % A[i])
			self.grid.SetCellValue(i, 2, "%#g" % B[i])
			self.grid.SetCellValue(i, 3, "%#g" % C[i])
			self.grid.SetCellValue(i, 4, "%#g" % A_k[i])
			self.grid.SetCellValue(i, 5, "%#g" % exponent[i])
			self.grid.SetCellValue(i, 6, "%#g" % edge[i])
			
		if not self.allow_modifications:
			self.nb_mixtures_box.Disable()
			self.grid.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS event of the nb_mixtures_box.
		self.nb_mixtures_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_mixture_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_nb_mixtures                                                     #
	#                                                                    #
	######################################################################
	def on_nb_mixtures(self, event):
		"""Handle text and kill focus events for the number of mixture
		box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of mixtures and
		updates the plots."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_mixtures_box.GetValidator().Validate(self):
			return
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		nb_rows = self.grid.GetNumberRows()
		
		if nb_mixtures > nb_rows:
			self.grid.AppendRows(nb_mixtures-nb_rows)
		elif nb_mixtures < nb_rows:
			self.grid.DeleteRows(nb_mixtures, nb_rows-nb_mixtures)
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Handle the event when a cell changes
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to read index values from the grid. If a row does
		not make sense, it simply ignores it. It then plots the result."""
		
		A = []
		B = []
		C = []
		A_k = []
		exponent = []
		edge = []
		
		for i in range(int(self.nb_mixtures_box.GetValue())):
			try:
				A_i = float(self.grid.GetCellValue(i, 1))
				B_i = float(self.grid.GetCellValue(i, 2))
				C_i = float(self.grid.GetCellValue(i, 3))
				A_k_i = float(self.grid.GetCellValue(i, 4))
				exponent_i = float(self.grid.GetCellValue(i, 5))
				edge_i = float(self.grid.GetCellValue(i, 6))
			except ValueError:
				pass
			else:
				A.append(A_i)
				B.append(B_i)
				C.append(C_i)
				A_k.append(A_k_i)
				exponent.append(exponent_i)
				edge.append(edge_i)
		
		if len(A) >= 2:
			# Number the mixtures simply using range. This makes it easier to
			# avoid plot update failures that might happen if the first
			# mixture is not 0, or if the mixtures are not in order. This only
			# applies to the modified material used internally for plotting.
			X = range(len(A))
			
			self.modified_material.set_properties(X, A, B, C, A_k, exponent, edge)
			material_mixture_dialog.update_plots(self)
		else:
			self.n_plot.reset()
			self.k_plot.reset()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_mixture_dialog.get_modified(self):
			return True
		
		X, A, B, C, A_k, exponent, edge = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		if int(self.nb_mixtures_box.GetValue()) != nb_mixtures:
			return True
		
		for i in range(nb_mixtures):
			x = int(self.grid.GetCellValue(i, 0))
			A_i = float(self.grid.GetCellValue(i, 1))
			B_i = float(self.grid.GetCellValue(i, 2))
			C_i = float(self.grid.GetCellValue(i, 3))
			A_k_i = float(self.grid.GetCellValue(i, 4))
			exponent_i = float(self.grid.GetCellValue(i, 5))
			edge_i = float(self.grid.GetCellValue(i, 6))
			if x != X[i]:
				return True
			if A_i != A[i] or B_i != B[i] or C_i != C[i]:
				return True
			if A_k_i != A_k[i] or exponent_i != exponent[i] or edge_i != edge[i]:
				return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_mixture_dialog.apply_modifications(self)
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		X = [int(self.grid.GetCellValue(i, 0)) for i in range(nb_mixtures)]
		A = [float(self.grid.GetCellValue(i, 1)) for i in range(nb_mixtures)]
		B = [float(self.grid.GetCellValue(i, 2)) for i in range(nb_mixtures)]
		C = [float(self.grid.GetCellValue(i, 3)) for i in range(nb_mixtures)]
		A_k = [float(self.grid.GetCellValue(i, 4)) for i in range(nb_mixtures)]
		exponent = [float(self.grid.GetCellValue(i, 5)) for i in range(nb_mixtures)]
		edge = [float(self.grid.GetCellValue(i, 6)) for i in range(nb_mixtures)]
		
		self.material.set_properties(X, A, B, C, A_k, exponent, edge)



########################################################################
#                                                                      #
# material_mixture_Sellmeier_dialog                                    #
#                                                                      #
########################################################################
class material_mixture_Sellmeier_dialog(material_mixture_dialog):
	"""A dialog class for creating and manipulating mixture materials
	defined by a Sellmeier dispersion formula"""
	
	title = "Sellmeier Mixture"
	
	
	######################################################################
	#                                                                    #
	# add_properties                                                     #
	#                                                                    #
	######################################################################
	def add_properties(self):
		"""Add property controls to the dialog
		
		This method adds controls to the number of mixtures and a grid to
		set the properties of the Sellmeier model."""
		
		# A box to specify the nb of points in the definition.
		self.nb_mixtures_box = wx.TextCtrl(self, -1, "", validator = int_validator(2, None))
		self.nb_mixtures_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_mixtures)
		
		# Add a table to specify the index.
		self.grid = wx.grid.Grid(self, -1, size = (600, 200), style = wx.SUNKEN_BORDER)
		self.grid.CreateGrid(0, 10)
		self.grid.SetColSize(0, 80)
		self.grid.SetColLabelValue(0, "Mixture")
		self.grid.SetColSize(1, 100)
		self.grid.SetColLabelValue(1, "B1")
		self.grid.SetColSize(2, 100)
		self.grid.SetColLabelValue(2, "C1")
		self.grid.SetColSize(3, 100)
		self.grid.SetColLabelValue(3, "B2")
		self.grid.SetColSize(4, 100)
		self.grid.SetColLabelValue(4, "C2")
		self.grid.SetColSize(5, 100)
		self.grid.SetColLabelValue(5, "B3")
		self.grid.SetColSize(6, 100)
		self.grid.SetColLabelValue(6, "C3")
		self.grid.SetColSize(7, 100)
		self.grid.SetColLabelValue(7, "A_k")
		self.grid.SetColSize(8, 100)
		self.grid.SetColLabelValue(8, "exponent")
		self.grid.SetColSize(9, 100)
		self.grid.SetColLabelValue(9, "edge")
		
		self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
		
		# Disable resizing of the grid.
		self.grid.DisableDragColSize()
		self.grid.DisableDragGridSize()
		self.grid.DisableDragRowSize()
		
		self.grid.SetValidator(material_mixture_Sellmeier_validator())
		
		# Put the nb points box in a sizer.
		nb_mixtures_sizer = wx.BoxSizer(wx.HORIZONTAL)
		nb_mixtures_sizer.Add(wx.StaticText(self, -1, "Nb mixtures:"),
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		nb_mixtures_sizer.Add(self.nb_mixtures_box,
		                      0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add the nb points and the grid to the content sizer.
		self.main_sizer.Add(nb_mixtures_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		self.main_sizer.Add(self.grid, 0, wx.EXPAND|wx.ALL, 5)
	
	
	######################################################################
	#                                                                    #
	# show_properties                                                    #
	#                                                                    #
	######################################################################
	def show_properties(self):
		"""Show the properties of the material
		
		This method shows the present properties of the material in the
		controls."""
		
		X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		self.nb_mixtures_box.SetValue("%i" % nb_mixtures)
		
		self.grid.AppendRows(nb_mixtures)
		
		for i in range(nb_mixtures):
			self.grid.SetCellValue(i, 0, "%i" % X[i])
			self.grid.SetCellValue(i, 1, "%#g" % B1[i])
			self.grid.SetCellValue(i, 2, "%#g" % C1[i])
			self.grid.SetCellValue(i, 3, "%#g" % B2[i])
			self.grid.SetCellValue(i, 4, "%#g" % C2[i])
			self.grid.SetCellValue(i, 5, "%#g" % B3[i])
			self.grid.SetCellValue(i, 6, "%#g" % C3[i])
			self.grid.SetCellValue(i, 7, "%#g" % A_k[i])
			self.grid.SetCellValue(i, 8, "%#g" % exponent[i])
			self.grid.SetCellValue(i, 9, "%#g" % edge[i])
		
		if not self.allow_modifications:
			self.nb_mixtures_box.Disable()
			self.grid.Disable()
	
	
	######################################################################
	#                                                                    #
	# on_cancel                                                          #
	#                                                                    #
	######################################################################
	def on_cancel(self, event): 
		"""Handle button events when the cancel button is pressed.
		
		This method takes a single argument:
		  event              the event."""
		
		# Unbind the EVT_KILL_FOCUS event of the nb_mixtures_box.
		self.nb_mixtures_box.Unbind(wx.EVT_KILL_FOCUS)
		
		material_mixture_dialog.on_cancel(self, event)
	
	
	######################################################################
	#                                                                    #
	# on_nb_mixtures                                                     #
	#                                                                    #
	######################################################################
	def on_nb_mixtures(self, event):
		"""Handle text and kill focus events for the number of mixture box
		
		This method takes a single argument:
		  event              the event.
		
		It adjusts the grid according the the number of mixtures and
		updates the plots."""
		
		# If focus is lost in favor of another application or the cancel
		# button, skip the event and return immediatly. 
		if event.GetWindow() in [None, self.cancel_button]:
			event.Skip()
			return
		
		if not self.nb_mixtures_box.GetValidator().Validate(self):
			return
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		nb_rows = self.grid.GetNumberRows()
		
		if nb_mixtures > nb_rows:
			self.grid.AppendRows(nb_mixtures-nb_rows)
		elif nb_mixtures < nb_rows:
			self.grid.DeleteRows(nb_mixtures, nb_rows-nb_mixtures)
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_cell_change                                                     #
	#                                                                    #
	######################################################################
	def on_cell_change(self, event):
		"""Handle the event when a cell changes
		
		This method takes a single argument:
		  event              the event.
		
		This method simply calls the method that updates the plots."""
		
		self.update_plots()
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# update_plots                                                       #
	#                                                                    #
	######################################################################
	def update_plots(self):
		"""Update the n and k plots
		
		This method tries to read index values from the grid. If a row does
		not make sense, it simply ignores it. It then plots the result."""
		
		B1 = []
		C1 = []
		B2 = []
		C2 = []
		B3 = []
		C3 = []
		A_k = []
		exponent = []
		edge = []
		
		for i in range(int(self.nb_mixtures_box.GetValue())):
			try:
				B1_i = float(self.grid.GetCellValue(i, 1))
				C1_i = float(self.grid.GetCellValue(i, 2))
				B2_i = float(self.grid.GetCellValue(i, 3))
				C2_i = float(self.grid.GetCellValue(i, 4))
				B3_i = float(self.grid.GetCellValue(i, 5))
				C3_i = float(self.grid.GetCellValue(i, 6))
				A_k_i = float(self.grid.GetCellValue(i, 7))
				exponent_i = float(self.grid.GetCellValue(i, 8))
				edge_i = float(self.grid.GetCellValue(i, 9))
			except ValueError:
				pass
			else:
				B1.append(B1_i)
				C1.append(C1_i)
				B2.append(B2_i)
				C2.append(C2_i)
				B3.append(B3_i)
				C3.append(C3_i)
				A_k.append(A_k_i)
				exponent.append(exponent_i)
				edge.append(edge_i)
		
		if len(B1) >= 2:
			# Number the mixtures simply using range. This makes it easier to
			# avoid plot update failures that might happen if the first
			# mixture is not 0, or if the mixtures are not in order. This only
			# applies to the modified material used internally for plotting.
			X = range(len(B1))
			
			self.modified_material.set_properties(X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge)
			material_mixture_dialog.update_plots(self)
		else:
			self.n_plot.reset()
			self.k_plot.reset()
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the material was modified
		
		This method returns a boolean indicating if the material was
		modified."""
		
		if material_mixture_dialog.get_modified(self):
			return True
		
		X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge = self.material.get_properties()
		
		nb_mixtures = len(X)
		
		if int(self.nb_mixtures_box.GetValue()) != nb_mixtures:
			return True
		
		for i in range(nb_mixtures):
			x = int(self.grid.GetCellValue(i, 0))
			B1_i = float(self.grid.GetCellValue(i, 1))
			C1_i = float(self.grid.GetCellValue(i, 2))
			B2_i = float(self.grid.GetCellValue(i, 3))
			C2_i = float(self.grid.GetCellValue(i, 4))
			B3_i = float(self.grid.GetCellValue(i, 5))
			C3_i = float(self.grid.GetCellValue(i, 6))
			A_k_i = float(self.grid.GetCellValue(i, 7))
			exponent_i = float(self.grid.GetCellValue(i, 8))
			edge_i = float(self.grid.GetCellValue(i, 9))
			if x != X[i]:
				return True
			if B1_i != B1[i] or C1_i != C1[i] or B2_i != B2[i] or C2_i != C2[i] or B3_i != B3[i] or C3_i != C3[i]:
				return True
			if A_k_i != A_k[i] or exponent_i != exponent[i] or edge_i != edge[i]:
				return True
		
		return False
	
	
	######################################################################
	#                                                                    #
	# apply_modifications                                                #
	#                                                                    #
	######################################################################
	def apply_modifications(self):
		"""Apply the modification to the material"""
		
		material_mixture_dialog.apply_modifications(self)
		
		nb_mixtures = int(self.nb_mixtures_box.GetValue())
		
		X = [int(self.grid.GetCellValue(i, 0)) for i in range(nb_mixtures)]
		B1 = [float(self.grid.GetCellValue(i, 1)) for i in range(nb_mixtures)]
		C1 = [float(self.grid.GetCellValue(i, 2)) for i in range(nb_mixtures)]
		B2 = [float(self.grid.GetCellValue(i, 3)) for i in range(nb_mixtures)]
		C2 = [float(self.grid.GetCellValue(i, 4)) for i in range(nb_mixtures)]
		B3 = [float(self.grid.GetCellValue(i, 5)) for i in range(nb_mixtures)]
		C3 = [float(self.grid.GetCellValue(i, 6)) for i in range(nb_mixtures)]
		A_k = [float(self.grid.GetCellValue(i, 7)) for i in range(nb_mixtures)]
		exponent = [float(self.grid.GetCellValue(i, 8)) for i in range(nb_mixtures)]
		edge = [float(self.grid.GetCellValue(i, 9)) for i in range(nb_mixtures)]
		
		self.material.set_properties(X, B1, C1, B2, C2, B3, C3, A_k, exponent, edge)



########################################################################
#                                                                      #
# open_material_dialog                                                 #
#                                                                      #
########################################################################
def open_material_dialog(parent, material, allow_modifications):
	"""Open a material dialog appropriate for a material
	
	This method takes 3 arguments:
	  parent               the dialog window's parent;
	  material             the material
	  allow_modifications  a boolean indicating if modification of the
	                       material are allowed.
	and shows the dialog and return it."""
	
	model = material.get_model()
	if material.is_mixture():
		if model == materials.CONSTANT:
			window = material_mixture_constant_dialog(parent, material, allow_modifications)
		elif model == materials.CAUCHY:
			window = material_mixture_Cauchy_dialog(parent, material, allow_modifications)
		elif model == materials.SELLMEIER:
			window = material_mixture_Sellmeier_dialog(parent, material, allow_modifications)
		elif model == materials.TABLE:
			window = material_mixture_table_dialog(parent, material, allow_modifications)
	else:
		if model == materials.CONSTANT:
			window = material_constant_dialog(parent, material, allow_modifications)
		elif model == materials.CAUCHY:
			window = material_Cauchy_dialog(parent, material, allow_modifications)
		elif model == materials.SELLMEIER:
			window = material_Sellmeier_dialog(parent, material, allow_modifications)
		elif model == materials.TABLE:
			window = material_table_dialog(parent, material, allow_modifications)
	
	return window



########################################################################
#                                                                      #
# new_material_dialog                                                  #
#                                                                      #
########################################################################
class new_material_dialog(wx.Dialog):
	"""A dialog to select the dispersion model and the name of a new
	material"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, catalog, original_material = None):
		"""Initialize the dialog
		
		This method takes a single argument:
		  parent             the window's parent."""
		
		self.original_material = original_material
		
		if self.original_material:
			title = "Copy material"
		else:
			title = "New material"
		
		wx.Dialog.__init__(self, parent, -1, title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.name_box = wx.TextCtrl(self, -1, "", validator = new_material_name_validator(catalog))
		self.name_box.SetMaxLength(251)
		
		self.regular_button = wx.RadioButton(self, -1, "regular", style = wx.RB_GROUP)
		self.mixture_button = wx.RadioButton(self, -1, "mixture")
		
		self.constant_button = wx.RadioButton(self, -1, "constant", style = wx.RB_GROUP)
		self.table_button = wx.RadioButton(self, -1, "table")
		self.Cauchy_button = wx.RadioButton(self, -1, "Cauchy")
		self.Sellmeier_button = wx.RadioButton(self, -1, "Sellmeier")
		
		sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		sizer_1.Add(wx.StaticText(self, -1, "Name:"),
		            0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(self.name_box, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		
		sizer_2.Add(wx.StaticText(self, -1, "Kind:"),
		            0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_2.Add(self.regular_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_2.Add(self.mixture_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		
		sizer_3.Add(wx.StaticText(self, -1, "Model:"),
		            0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3.Add(self.constant_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3.Add(self.table_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3.Add(self.Cauchy_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3.Add(self.Sellmeier_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		
		self.main_sizer.Add(sizer_1, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(sizer_2, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		self.main_sizer.Add(sizer_3, 0, wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK), 0, wx.ALL, 10)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.ALL, 10)
		
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
		
		# Default values.
		if self.original_material:
			self.name_box.SetValue(self.original_material.get_name())
			kind = self.original_material.get_kind()
			if kind == materials.MATERIAL_REGULAR:
				self.regular_button.SetValue(True)
			else:
				self.mixture_button.SetValue(True)
			self.regular_button.Disable()
			self.mixture_button.Disable()
			model = self.original_material.get_model()
			if model == materials.CONSTANT:
				self.constant_button.SetValue(True)
			elif model == materials.TABLE:
				self.table_button.SetValue(True)
			elif model == materials.CAUCHY:
				self.Cauchy_button.SetValue(True)
			elif model == materials.SELLMEIER:
				self.Sellmeier_button.SetValue(True)
			self.constant_button.Disable()
			self.table_button.Disable()
			self.Cauchy_button.Disable()
			self.Sellmeier_button.Disable()
		else:
			self.regular_button.SetValue(True)
			self.constant_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_new_material                                                   #
	#                                                                    #
	######################################################################
	def get_new_material(self):
		"""Get the new material
		
		This method returns the newly created material."""
		
		if self.original_material:
			new_material = self.original_material.clone()
		
		else:
			# Create an instance of the appropriate class. Also set default
			# values in order for the material dialog to show up correctly.
			if self.regular_button.GetValue():
				if self.constant_button.GetValue():
					new_material = materials.material_constant()
					new_material.set_properties(1.5+0.0j)
				elif self.table_button.GetValue():
					new_material = materials.material_table()
					new_material.set_properties([400.0, 600.0, 800.0], [1.55+0.0j, 1.50+0.0j, 1.45+0.0j])
				elif self.Cauchy_button.GetValue():
					new_material = materials.material_Cauchy()
					new_material.set_properties(1.5, 0.01, 0.0, 0.0, 8.0, 4000)
				elif self.Sellmeier_button.GetValue():
					new_material = materials.material_Sellmeier()
					new_material.set_properties(1.0, 5.0e-3, 0.2, 1.0e-2, 0.1, 2.0e-2, 0.0, 8.0, 4000)
			else:
				if self.constant_button.GetValue():
					new_material = materials.material_mixture_constant()
					new_material.set_properties([0, 50, 100], [1.50+0.0j, 2.00+0.0j, 2.5+0.0j])
				elif self.table_button.GetValue():
					new_material = materials.material_mixture_table()
					new_material.set_properties([0, 50, 100], [400.0, 600.0, 800.0], [[1.55+0.0j, 1.50+0.0j, 1.45+0.0j], [2.05+0.0j, 2.00+0.0j, 1.95+0.0j], [2.55+0.0j, 2.50+0.0j, 2.45+0.0j]])
				elif self.Cauchy_button.GetValue():
					new_material = materials.material_mixture_Cauchy()
					new_material.set_properties([0, 50, 100], [1.50, 2.00, 2.5], [0.01, 0.02, 0.03], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [8.0, 8.0, 8.0], [4000.0, 4000.0, 4000.0])
				elif self.Sellmeier_button.GetValue():
					new_material = materials.material_mixture_Sellmeier()
					new_material.set_properties([0, 50, 100], [1.0, 1.1, 1.2], [5.0e-3, 5.0e-3, 5.0e-3], [0.2, 0.2, 0.2], [1.0e-2, 1.0e-2, 1.0e-2], [0.1, 0.1, 0.1], [2.0e-2, 2.0e-2, 2.0e-2], [0.0, 0.0, 0.0], [8.0, 8.0, 8.0], [4000.0, 4000.0, 4000.0])
		
		new_material.set_name(str(self.name_box.GetValue()))
		
		return new_material



########################################################################
#                                                                      #
# import_material_dialog                                               #
#                                                                      #
########################################################################
class import_material_dialog(wx.Dialog):
	"""A dialog to read a table material from a file"""
	
	title = "Import Material From Text File"
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, parent, catalog):
		"""Initialize the dialog
		
		This method takes 1 argument:
		  parent    the parent window."""
		
		wx.Dialog.__init__(self, parent, -1, self.title, style = wx.CAPTION)
		
		self.SetAutoLayout(True)
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.main_sizer)
		
		self.file_browse_button = wx.lib.filebrowsebutton.FileBrowseButton(self, -1, size=(450, -1), labelText = "Input file:")
		
		self.name_box = wx.TextCtrl(self, -1, "", validator = new_material_name_validator(catalog))
		self.name_box.SetMaxLength(251)
		
		self.description_box = wx.TextCtrl(self, -1, "", size=(300, -1))
		
		self.nb_header_lines_box = wx.TextCtrl(self, -1, "", validator = int_validator(0))
		
		self.unit_radio_buttons = {}
		for unit in units.WAVELENGTH_UNITS:
			unit_radio_button = wx.RadioButton(self, -1, units.ABBREVIATIONS[unit], style = wx.RB_SINGLE)
			self.unit_radio_buttons[unit] = unit_radio_button
			self.Bind(wx.EVT_RADIOBUTTON, self.on_unit_radio_button, unit_radio_button)
		
		self.refractive_index_button = wx.RadioButton(self, -1, "refractive index", style = wx.RB_GROUP)
		self.relative_permittivity_button = wx.RadioButton(self, -1, "relative permittivity")
		
		content_sizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		
		sizer_1.Add(wx.StaticText(self, -1, "Name:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_1.Add(self.name_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_2.Add(wx.StaticText(self, -1, "Description:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_2.Add(self.description_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_3.Add(wx.StaticText(self, -1, "Header lines:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_3.Add(self.nb_header_lines_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_4.Add(wx.StaticText(self, -1, "Wavelength units:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		for unit in units.WAVELENGTH_UNITS:
			sizer_4.Add(self.unit_radio_buttons[unit], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		sizer_5.Add(wx.StaticText(self, -1, "Refractive index format:"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		sizer_5.Add(self.refractive_index_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		sizer_5.Add(self.relative_permittivity_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		content_sizer.Add(self.file_browse_button, 0, wx.ALIGN_LEFT|wx.TOP, 5)
		content_sizer.Add(sizer_1, 0, wx.ALIGN_LEFT)
		content_sizer.Add(sizer_2, 0, wx.ALIGN_LEFT|wx.TOP, 10)
		content_sizer.Add(sizer_3, 0, wx.ALIGN_LEFT|wx.TOP, 10)
		content_sizer.Add(sizer_4, 0, wx.ALIGN_LEFT|wx.TOP, 10)
		content_sizer.Add(sizer_5, 0, wx.ALIGN_LEFT|wx.TOP, 10)
		
		self.main_sizer.Add(content_sizer, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 20)
		
		# Default values.
		self.nb_header_lines_box.SetValue("0")
		self.unit_radio_buttons[units.NANOMETERS].SetValue(True)
		self.refractive_index_button.SetValue(True)
		
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(wx.Button(self, wx.ID_OK), 0, wx.ALL, 10)
		buttons.Add(wx.Button(self, wx.ID_CANCEL), 0, wx.ALL, 10)
		
		self.main_sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 0)
		
		self.main_sizer.Fit(self)
		self.Layout()
		self.CenterOnParent()
	
	
	######################################################################
	#                                                                    #
	# on_unit_radio_button                                               #
	#                                                                    #
	######################################################################
	def on_unit_radio_button(self, event):
		"""Handle wavelength unit selection events
		
		This method takes a single argument:
		  event              the event.
		
		This method unselects all wavelength unit radio buttons excepts
		the one that was selected. In is necessary to handle that rather
		than relying on wx to do it because of the way the buttons are
		created "dynamically" from the list of units."""
		
		selected_button = event.GetEventObject()
		
		for unit in units.WAVELENGTH_UNITS:
			if self.unit_radio_buttons[unit] != selected_button:
				self.unit_radio_buttons[unit].SetValue(False)
	
	
	######################################################################
	#                                                                    #
	# get_material                                                       #
	#                                                                    #
	######################################################################
	def get_material(self):
		"""Get the material
		
		This method returns the material imported from the text file."""
		
		filename = self.file_browse_button.GetValue()
		name = str(self.name_box.GetValue())
		description = self.description_box.GetValue()
		nb_header_lines = int(self.nb_header_lines_box.GetValue())
		for unit in units.WAVELENGTH_UNITS:
			if self.unit_radio_buttons[unit].GetValue():
				break
		if self.relative_permittivity_button.GetValue():
			permittivity = True
		else:
			permittivity = False
		
		new_material = materials.import_material(filename, name, description, nb_header_lines, unit, permittivity)
		
		return new_material



########################################################################
#                                                                      #
# material_table_validator                                             #
#                                                                      #
########################################################################
class material_table_validator(wx.PyValidator):
	"""Validator for the content of the grid in table material"""
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		
		previous_wvl = 0.0
		
		for row in range(nb_rows):
			try:
				wvl = float(window.GetCellValue(row, 0))
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			# Verify that wavelengths are in increasing order and all larger
			# than 0.0.
			if wvl <= previous_wvl:
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			try:
				n = float(window.GetCellValue(row, 1))
			except ValueError:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			if n < 0.0:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			try:
				k = float(window.GetCellValue(row, 2))
			except ValueError:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			if k < 0.0:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			previous_wvl = wvl
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# material_mixture_constant_validator                                  #
#                                                                      #
########################################################################
class material_mixture_constant_validator(wx.PyValidator):
	"""Validator for the content of the grid in constant mixture material"""
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		
		previous_x = -1
		
		for row in range(nb_rows):
			try:
				x = int(window.GetCellValue(row, 0))
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			# Verify that mixtures are in increasing order and all
			# positive. Also verify that first mixture is 0.
			if x <= previous_x or (row == 0 and x != 0):
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			try:
				n = float(window.GetCellValue(row, 1))
			except ValueError:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			if n < 0.0:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			try:
				k = float(window.GetCellValue(row, 2))
			except ValueError:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			if k < 0.0:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			previous_x = x
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# material_mixture_table_validator                                     #
#                                                                      #
########################################################################
class material_mixture_table_validator(wx.PyValidator):
	"""Validator for the content of the grid in table mixture material"""
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		nb_cols = window.GetNumberCols()
		
		previous_x = -1
		previous_wvl = 0.0
		
		for col in range(1, nb_cols):
			try:
				x = int(window.GetCellValue(0, col))
			except ValueError:
				error = True
				window.SelectBlock(0, col, 0, col, True)
				window.GoToCell(0, col)
				break
			
			# Verify that mixtures are in increasing order and all
			# positive. Also verify that first mixture is 0.
			if x <= previous_x or (col == 1 and x != 0):
				error = True
				window.SelectBlock(0, col, 0, col)
				window.GoToCell(0, col)
				break
			
			previous_x = x
		
		if not error:
			for row in range(1, nb_rows):
				try:
					wvl = float(window.GetCellValue(row, 0))
				except ValueError:
					error = True
					window.SelectBlock(row, 0, row, 0)
					window.GoToCell(row, 0)
					break
				
				# Verify that wavelengths are in increasing order and all
				# positive.
				if wvl <= previous_wvl:
					error = True
					window.SelectBlock(row, 0, row, 0)
					window.GoToCell(row, 0)
					break
				
				previous_wvl = wvl
		
		if not error:
			for col in range(1, nb_cols):
				for row in range(1, nb_rows):
					try:
						N = complex(window.GetCellValue(row, col))
					except ValueError:
						error = True
						window.SelectBlock(row, col, row, col)
						window.GoToCell(row, col)
						break
					
					if N.real < 0.0 or N.imag > 0.0:
						error = True
						window.SelectBlock(row, col, row, col)
						window.GoToCell(row, col)
						break
				
				if error: break
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# material_mixture_Cauchy_validator                                    #
#                                                                      #
########################################################################
class material_mixture_Cauchy_validator(wx.PyValidator):
	"""Validator for the content of the grid in Cauchy mixture material"""
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		
		previous_x = -1
		
		for row in range(nb_rows):
			try:
				x = int(window.GetCellValue(row, 0))
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			# Verify that mixtures are in increasing order and all
			# positive. Also verify that first mixture is 0.
			if x <= previous_x or (row == 0 and x != 0):
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			try:
				A = float(window.GetCellValue(row, 1))
			except ValueError:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			if A < 0.0:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			try:
				B = float(window.GetCellValue(row, 2))
			except ValueError:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			try:
				C = float(window.GetCellValue(row, 3))
			except ValueError:
				error = True
				window.SelectBlock(row, 3, row, 3)
				window.GoToCell(row, 3)
				break
			
			try:
				A_k = float(window.GetCellValue(row, 4))
			except ValueError:
				error = True
				window.SelectBlock(row, 4, row, 4)
				window.GoToCell(row, 4)
				break
			
			if A_k < 0.0:
				error = True
				window.SelectBlock(row, 4, row, 4)
				window.GoToCell(row, 4)
				break
			
			try:
				exponent = float(window.GetCellValue(row, 5))
			except ValueError:
				error = True
				window.SelectBlock(row, 5, row, 5)
				window.GoToCell(row, 5)
				break
			
			if exponent < 0.0:
				error = True
				window.SelectBlock(row, 5, row, 5)
				window.GoToCell(row, 5)
				break
			
			try:
				edge = float(window.GetCellValue(row, 6))
			except ValueError:
				error = True
				window.SelectBlock(row, 6, row, 6)
				window.GoToCell(row, 6)
				break
			
			if edge <= 0.0:
				error = True
				window.SelectBlock(row, 6, row, 6)
				window.GoToCell(row, 6)
				break
			
			previous_x = x
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# material_mixture_Sellmeier_validator                                 #
#                                                                      #
########################################################################
class material_mixture_Sellmeier_validator(wx.PyValidator):
	"""Validator for the content of the grid in Sellmeier mixture material"""
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the grid that is validated
		and it returns True if the grid contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		
		previous_x = -1
		
		for row in range(nb_rows):
			try:
				x = int(window.GetCellValue(row, 0))
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0, True)
				window.GoToCell(row, 0)
				break
			
			# Verify that mixtures are in increasing order and all
			# positive. Also verify that first mixture is 0.
			if x <= previous_x or (row == 0 and x != 0):
				error = True
				window.SelectBlock(row, 0, row, 0)
				window.GoToCell(row, 0)
				break
			
			try:
				B1 = float(window.GetCellValue(row, 1))
			except ValueError:
				error = True
				window.SelectBlock(row, 1, row, 1)
				window.GoToCell(row, 1)
				break
			
			try:
				C1 = float(window.GetCellValue(row, 2))
			except ValueError:
				error = True
				window.SelectBlock(row, 2, row, 2)
				window.GoToCell(row, 2)
				break
			
			try:
				B2 = float(window.GetCellValue(row, 3))
			except ValueError:
				error = True
				window.SelectBlock(row, 3, row, 3)
				window.GoToCell(row, 3)
				break
			
			try:
				C2 = float(window.GetCellValue(row, 4))
			except ValueError:
				error = True
				window.SelectBlock(row, 4, row, 4)
				window.GoToCell(row, 4)
				break
			
			try:
				B3 = float(window.GetCellValue(row, 5))
			except ValueError:
				error = True
				window.SelectBlock(row, 5, row, 5)
				window.GoToCell(row, 5)
				break
			
			try:
				C3 = float(window.GetCellValue(row, 6))
			except ValueError:
				error = True
				window.SelectBlock(row, 6, row, 6)
				window.GoToCell(row, 6)
				break
			
			previous_x = x
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True



########################################################################
#                                                                      #
# new_material_name_validator                                          #
#                                                                      #
########################################################################
class new_material_name_validator(wx.PyValidator):
	"""Validator for the content of the name box in the new material
	dialog"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, catalog = None):
		"""Initialize the validator"""
		
		wx.PyValidator.__init__(self)
		
		if catalog:
			self.catalog = catalog
		else:
			self.catalog = materials.material_catalog()
		
		self.Bind(wx.EVT_CHAR, self.OnChar)
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Clone the validator
		
		The method returns a clone of the validator."""
		
		return self.__class__(self.catalog)
	
	
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
	# OnChar                                                             #
	#                                                                    #
	######################################################################
	def OnChar(self, event):
		"""Verify that a caracter is appropriate for a material name
		
		This method takes a single argument:
		  event              the event."""
		
		key = event.GetKeyCode()
		
		# Accept delete and special caracters.
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		# Accept the valid characters.
		if chr(key) in valid_material_name_characters:
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
		and it returns True if the control contains valid properties or
		False otherwise."""
		
		error = False
		
		window = self.GetWindow()
		answer = window.GetValue()
		
		material_names = [name.upper() for name in self.catalog.get_material_names()]
		
		if len(answer) == 0:
			error = True
		
		elif answer.upper() in material_names:
			error = True
		
		elif answer[0] == "-":
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
# user_directory_validator                                             #
#                                                                      #
########################################################################
class user_directory_validator(wx.PyValidator):
	"""Validator to check that the user material directory exists"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the validator"""
		
		wx.PyValidator.__init__(self)
	
	
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
		"""Validate the content of the control
		
		This method takes a single argument:
		  parent             the control that is validated
		and it returns True if the control contains valid properties or
		False otherwise."""
		
		window = self.GetWindow()
		path = window.GetPath()
		
		if not os.path.isdir(path):
			if not wx.Validator_IsSilent(): wx.Bell()
			window.GetTextCtrl().SetFocus()
			window.GetTextCtrl().SetSelection(0, len(path))
			window.Refresh()
			return False
		
		return True
