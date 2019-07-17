# config_refinement.py
# 
# Configurations related to refinement for the Filters software.
# 
# Copyright (c) 2004-2007 Stephane Larouche.
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


# Stopping criteria of the refinement method with the Levenberg-
# Marquardt method.
REFINEMENT_MAX_ITERATIONS = None
REFINEMENT_MAX_ITERATIONS_NO_THREADING = 100
REFINEMENT_MIN_GRADIENT = 1E-9
REFINEMENT_ACCEPTABLE_CHI_2 = 1E-9
REFINEMENT_MIN_CHI_2_CHANGE = 1E-6
