# localize.py
# 
# Set OS specific settings.
# 
# Copyright (c) 2006,2015 Stephane Larouche.
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

import config



########################################################################
#                                                                      #
# localize                                                             #
#                                                                      #
########################################################################
def localize():
	"""Set OS specific settings.
	
	More specificaly:
	  - set the iteration limits when true multithreading is not
	    available;
	  - change the position of the log file created when the application
	    frozen with py2exe crashes."""
	
	try:
		import threading
	except ImportError:
		config.REFINEMENT_MAX_ITERATIONS = config.REFINEMENT_MAX_ITERATIONS_NO_THREADING
		config.FOURIER_MAX_ITERATIONS = config.FOURIER_MAX_ITERATIONS_NO_THREADING
	
	# If OpenFilters was frozen with py2exe, modify the location of the
	# log file created in boot_common.py to a place where the user should
	# have the right to write when OpenFilters is run (the user profile).
	if hasattr(sys, "frozen") and sys.frozen == "windows_exe":
		import functools
		import os
		sys.stderr.write = functools.partial(sys.stderr.write, fname = os.path.join(os.environ["USERPROFILE"], "OpenFilters.log"))
