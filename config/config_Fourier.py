# config_Fourier.py
# 
# Configurations related to the Fourier transform method for the Filters
# software.
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


# Default values of the parameters.
FOURIER_Q_FUNCTION = "Bovard"
FOURIER_MATERIAL = "SiO2TiO2"
FOURIER_OT = 20000.0
FOURIER_SUBLAYER_OT = 2.0

# Stopping criteria of the Fourier transform method with the
# Levenberg-Marquardt method.
FOURIER_MAX_ITERATIONS = None
FOURIER_MAX_ITERATIONS_NO_THREADING = 10
FOURIER_ACCEPTABLE_CHI_2 = 1E-6
FOURIER_MIN_CHI_2_CHANGE = 1E-3
