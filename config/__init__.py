# __init__.py
# 
# Load all configuration files for the Filters software.
# 
# Copyright (c) 2004-2008 Stephane Larouche.
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


__all__ = ["config_color",
           "config_dispersive",
           "config_Fourier",
           "config_general",
           "config_GUI",
           "config_interface",
           "config_materials",
           "config_needles",
           "config_preproduction"
           "config_refinement",
           "config_special"]


from config_color import *
from config_dispersive import *
from config_Fourier import *
from config_general import *
from config_GUI import *
from config_interface import *
from config_materials import *
from config_needles import *
from config_preproduction import *
from config_refinement import *
from config_special import *
