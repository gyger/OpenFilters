# definitions.py
# 
# Definitions that are used in OpenFilters.
# 
# Copyright (c) 2002-2003,2005-2008 Stephane Larouche.
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



# Polarizations.
S = 90.0
P = 0.0
UNPOLARIZED = 45.0

# The direction of the light.
FORWARD = 1
BACKWARD = -1

# Kind of material.
MATERIAL_REGULAR = 1
MATERIAL_MIXTURE = 2

# Side of the coating.
FRONT = 1
BACK = 2
BOTH = 3

# Position of the layer in the coating. Negative values are used
# since positive values or 0 represent positions in the stack.
# Positions are also defined for the substrate and mediums.
BOTTOM = -1
TOP = -2
SUBSTRATE = -3
MEDIUM = -4

# Ellipsometer kind.
RAE = 1
RPE = 2
RCE = 3

# The step spacing in graded index layers can be defined by the
# deposition possibilities. A negative value is used since positive
# values represent "real" step spacing
DEPOSITION_STEP_SPACING = -1.0
