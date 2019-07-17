# limits.py
# 
# Get properties of the machine specific number representation.
# 
# Copyright (c) 2005,2007,2009 Stephane Larouche.
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



# When possible (Python 2.6 and higher) use info from sys.float_info.
try:
	from sys import float_info
	
	epsilon = float_info.epsilon
	min = float_info.min

# Otherwise, calculate it.
except ImportError:
	
	# Machine precision.
	epsilon = 1.0
	while 1.0 + 0.5*epsilon > 1.0:
		epsilon *= 0.5
	
	# Smallest float number.
	min = 1.0
	while 0.5*min != 0.0:
		min *= 0.5
