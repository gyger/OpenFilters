# __init__.py
# 
# Initialize the abeles package.
# 
# The abeles package provides classes to calculate optical properties
# of a filter using the Abeles matrices. This file first tries to
# import the functions from a dynamicaly loaded library (_abeles.dll
# on Windows). If this fails, a Python implementation is loaded. The
# dynamicaly loaded library, written in C, is much faster than the
# Python implementation. The later is maintained to allow the use of
# this software on any system running Python, even if it is impossible
# to compile the dynamicaly loaded library. It is also usefull when
# develloping new features in Python before translating them in C.
# 
# Copyright (c) 2000-2007 Stephane Larouche.
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



# Try to import the dll.
abeles_dll_import_failed = False
try:
	from _abeles import *
except ImportError:
	abeles_dll_import_failed = True

# If the importation of the dll failed, load the Python versions.
if abeles_dll_import_failed:
	from definitions import *
	from wvls import *
	from N import *
	from N_mixture import *
	from dispersion import *
	from dispersion_mixtures import *
	from sin2 import *
	from matrices import *
	from r_and_t import *
	from spectro import *
	from phase import *
	from ellipso import *
	from admittance import *
	from circle import *
	from electric_field import *
	from monitoring import *
	from derivatives import *
	from needles import *



########################################################################
#                                                                      #
# get_abeles_dll_import_success                                        #
#                                                                      #
########################################################################
def get_abeles_dll_import_success():
	"""Indicate if the abeles dll was successfully imported."""
	
	return not abeles_dll_import_failed
