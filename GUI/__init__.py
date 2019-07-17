# __init__.py
# 
# GUI for OpenFilters.
# 
# Copyright (c) 2001,2002,2004-2007 Stephane Larouche.
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

import GUI_calculate
import GUI_color
import GUI_filter_grid
import GUI_filter_properties
import GUI_layer_dialogs
import GUI_layer_grid
import GUI_main_window
import GUI_materials
import GUI_optimization
import GUI_plot
import GUI_preproduction
import GUI_stack
import GUI_target_grid
import GUI_targets
import GUI_validators



########################################################################
#                                                                      #
# Filters_GUI                                                          #
#                                                                      #
########################################################################
class Filters_GUI(wx.App):
	"""Graphical user interface for OpenFilters"""
	
	
	######################################################################
	#                                                                    #
	# OnInit                                                             #
	#                                                                    #
	######################################################################
	def OnInit(self):
		"""Initialize the graphical user interface
		
		This method is automatically called when the instance is
		initialized. It takes no arguments and returns a boolean value
		indicating if it the application was successfully initialized."""
		
		main_window = GUI_main_window.main_window(None)
		self.SetTopWindow(main_window)
		
		return True
		