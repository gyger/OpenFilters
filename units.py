# units.py
# 
# A few functions to convert between different wavelength and thickness
# units for OpenFilters.
#
# Copyright (c) 2009,2012 Stephane Larouche.
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


METERS = 1
MILLIMETERS = 2
MICROMETERS = 3
NANOMETERS = 4
ANGSTROMS = 5
ELECTRONVOLTS = 6
INVERSECENTIMETERS = 7
HERTZ = 8
MEGAHERTZ = 9
GIGAHERTZ = 10
TERAHERTZ = 11

NAMES = {METERS: "meters",
         MILLIMETERS: "millimeters",
         MICROMETERS: "micrometers",
         NANOMETERS: "nanometers",
         ANGSTROMS: "Angstrom",
         ELECTRONVOLTS: "electron volts",
         INVERSECENTIMETERS: "inverse centimeters",
         HERTZ: "hertz",
         MEGAHERTZ: "megahertz",
         GIGAHERTZ: "gigahertz",
         TERAHERTZ: "terahertz"}

ABBREVIATIONS = {METERS: "m",
                 MILLIMETERS: "mm",
                 MICROMETERS: "um",
                 NANOMETERS: "nm",
                 ANGSTROMS: "A",
                 ELECTRONVOLTS: "eV",
                 INVERSECENTIMETERS: "cm-1",
                 HERTZ: "Hz",
                 MEGAHERTZ: "MHz",
                 GIGAHERTZ: "GHz",
                 TERAHERTZ: "THz"}

WAVELENGTH_UNITS = [METERS, MILLIMETERS, MICROMETERS, NANOMETERS, ANGSTROMS, ELECTRONVOLTS, INVERSECENTIMETERS, HERTZ, MEGAHERTZ, GIGAHERTZ, TERAHERTZ]
THICKNESS_UNITS = [METERS, MILLIMETERS, MICROMETERS, NANOMETERS, ANGSTROMS]


# Plank constant (in eV*s) and speed of light (in m/s).
h = 4.13566733e-15
c = 299792458.0
hc = h*c


def meters_to_meters(x): return x

def meters_to_millimeters(x): return 1.0e3*x
def meters_to_micrometers(x): return 1.0e6*x
def meters_to_nanometers(x): return 1.0e9*x
def meters_to_angstroms(x): return 1.0e10*x
def meters_to_electronvolts(x): return hc/x
def meters_to_inversecentimeters(x): return 1.0e-2/x
def meters_to_hertz(x): return c/x
def meters_to_megahertz(x): return 1.0e-6*c/x
def meters_to_gigahertz(x): return 1.0e-9*c/x
def meters_to_terahertz(x): return 1.0e-12*c/x

def millimeters_to_meters(x): return 1.0e-3*x
def micrometers_to_meters(x): return 1.0e-6*x
def nanometers_to_meters(x): return 1.0e-9*x
def angstroms_to_meters(x): return 1.0e-10*x
def electronvolts_to_meters(x): return hc/x
def inversecentimeters_to_meters(x): return 1.0e-2/x
def hertz_to_meters(x): return c/x
def megahertz_to_meters(x): return 1.0e-6*c/x
def gigahertz_to_meters(x): return 1.0e-9*c/x
def terahertz_to_meters(x): return 1.0e-12*c/x


CONVERT_FROM_METERS_TO_UNITS = {METERS: meters_to_meters,
                                MILLIMETERS: meters_to_millimeters,
                                MICROMETERS: meters_to_micrometers,
                                NANOMETERS: meters_to_nanometers,
                                ANGSTROMS: meters_to_angstroms,
                                ELECTRONVOLTS: meters_to_electronvolts,
                                INVERSECENTIMETERS: meters_to_inversecentimeters,
                                HERTZ: meters_to_hertz,
                                MEGAHERTZ: meters_to_megahertz,
                                GIGAHERTZ: meters_to_gigahertz,
                                TERAHERTZ: meters_to_terahertz}

CONVERT_FROM_UNITS_TO_METERS = {METERS: meters_to_meters,
                                MILLIMETERS: millimeters_to_meters,
                                MICROMETERS: micrometers_to_meters,
                                NANOMETERS: nanometers_to_meters,
                                ANGSTROMS: angstroms_to_meters,
                                ELECTRONVOLTS: electronvolts_to_meters,
                                INVERSECENTIMETERS: inversecentimeters_to_meters,
                                HERTZ: hertz_to_meters,
                                MEGAHERTZ: megahertz_to_meters,
                                GIGAHERTZ: gigahertz_to_meters,
                                TERAHERTZ: terahertz_to_meters}
