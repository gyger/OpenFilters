# color.py
# 
# This module provides functions to quantify the color of a sample
# from its transmission or reflection spectrum. It also provides
# functions to change the representation of color between different
# color spaces. The methods included in this file are fully compliant
# with the recommandations found in
#   CIE Colorimetry Technical Report 3rd Edition, 2004 (CIE 15:2004).
# 
# Copyright (c) 2001-2003,2005-2007,2009,2010,2013,2015 Stephane Larouche.
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



# REMOVE when Python 3.0 will be out.
from __future__ import division

import os
import os.path

import math
import copy

import config
import simple_parser
from moremath import interpolation
from moremath import Gauss_Jordan
import main_directory



one_hundred_eighty_over_pi = 180.0/math.pi


# Constants to describe the different color spaces.
XYZ = 1
xyY = 2
Luv = 3
Lab = 4
LChuv = 5
LChab = 6
	
color_spaces = {XYZ: "XYZ",
			          xyY: "xyY",
			          Luv: "L*u*v*",
			          Lab: "L*a*b*",
			          LChuv: "L*C*h(u*v*)",
			          LChab: "L*C*h(a*b*)"}


# The observer and illuminant filenames are given relative to the
# directory where this file is located, we therefore need the path of
# the directory. This is mainly usefull when Filters is used as a
# package.
base_directory = main_directory.get_main_directory()
observers_directory = os.path.join(base_directory, *config.OBSERVERS_DIRECTORY)
illuminants_directory = os.path.join(base_directory, *config.ILLUMINANTS_DIRECTORY)


# This matrix, used in the conversion from XYZ color to RGB color
# depends on your computer. Heres the value for the ITU-R BT.709
# standard and the sRGB standard.
XYZ_to_RGB_matrix_709 = [[ 3.240479, -0.969256,  0.055648],
                         [-1.537150,  1.875992, -0.204043],
                         [-0.498535,  0.041556,  1.057311]]
XYZ_to_RGB_matrix_sRGB = [[ 3.2410, -0.9692,  0.0556],
                          [-1.5374,  1.8760, -0.2040],
                          [-0.4986,  0.0416,  1.0570]]

# Some constants that will be used in calculations related to Lab and
# Luv color spaces. The constant are named according to
#   H. Pauli, "Proposed extension of the CIE recommendation on "Uniform
#   color spaces, color difference equations, and metric color terms"",
#   J. Opt. Soc. Am., Vol. 66 No. 8, 1976, pp. 666-667.
one_third = 1.0/3.0
minus_two_third = -2.0/3.0
sixteen_over_one_hundred_sixteen = 16.0/116.0
cubic_root_gamma = 24.0/116.0
gamma = 216.0/24389.0
alpha = 841.0/108.0



########################################################################
#                                                                      #
# color_error                                                          #
#                                                                      #
########################################################################
class color_error(Exception):
	
	def __init__(self, name, value = ""):
		self.name = name
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Color error (%s): %s." % (self.name, self.value)
		else:
			return "Color error (%s)." % self.name



########################################################################
#                                                                      #
# illuminant                                                           #
#                                                                      #
########################################################################
class illuminant(object):
	"""A simple class to store the data of a colorimetric illuminant."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, name, description, wvls, spectrum):
		"""Creator of the illuminant.
		
		This method takes four arguments:
		  name           the name of the illuminant;
		  description    a text describing the illuminant;
		  wvls           the wavelengths;
		  spectrum       the spectrum of the illuminant."""
		
		self.name = name
		self.description = description
		self.wvls = wvls
		self.spectrum = spectrum
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the illuminant
		
		This function takes no argument and returns a single argument:
		  name             the name of the illuminant."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# get_description                                                    #
	#                                                                    #
	######################################################################
	def get_description(self):
		"""Get the description text for the illuminant		
		
		This function takes no argument and returns a single argument:
		  description      the description of the illuminant."""
		
		return self.description
	
	
	######################################################################
	#                                                                    #
	# get_spectrum                                                       #
	#                                                                    #
	######################################################################
	def get_spectrum(self):
		"""Get the spectrum of the illuminant
		
		This method return two arguments:
		  wvls             the wavelengths;
		  spectrum         the spectrum of the illuminant."""
		
		return self.wvls, self.spectrum



########################################################################
#                                                                      #
# observer                                                             #
#                                                                      #
########################################################################
class observer(object):
	"""A simple class to store the data of a colorimetric observer."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, name, description, wvls, x_function, y_function, z_function):
		"""Create an observer object
		
		This method takes five arguments:
			name             the name of the observer;
		  description      a text describing the observer;
		  wvls             the wavelengths;
		  x_function;
		  y_function;
		  z_function       the colorimetric functions.
		It returns no argument."""
		
		self.name = name
		self.description = description
		self.wvls = wvls
		self.x_function = x_function
		self.y_function = y_function
		self.z_function = z_function
	
	
	######################################################################
	#                                                                    #
	# get_name                                                           #
	#                                                                    #
	######################################################################
	def get_name(self):
		"""Get the name of the observer."""
		
		return self.name
	
	
	######################################################################
	#                                                                    #
	# get_description                                                    #
	#                                                                    #
	######################################################################
	def get_description(self):
		"""Get the description text for the observer."""
		
		return self.description
	
	
	######################################################################
	#                                                                    #
	# get_functions                                                      #
	#                                                                    #
	######################################################################
	def get_functions(self):
		"""Get the functions of the illuminant.
		
		This method return four arguments:
		  wvls           the wavelengths;
		  x_function;
		  y_function;
		  z_function     the colorimetric functions."""
		
		return self.wvls, self.x_function ,self.y_function, self.z_function



########################################################################
#                                                                      #
# illuminants                                                          #
#                                                                      #
########################################################################
class illuminants(object):
	"""A class to list the colorimetric illuminants."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, directory):
		"""Initialize the list of illuminants.
		
		This method initialize the list of colorimetric illuminants by
		listing all files in a directory. It takes one argument
		  directory        the directory where are the illuminant files.
		
		The illuminants are not actually read on initialization. They are
		read only if demanded with the get_illuminant method but where they
		are, they are kept in memory to avoid reading them twice."""
		
		self.illuminants = dict((os.path.splitext(filename)[0], None) for filename in os.listdir(directory) if os.path.splitext(filename)[1].upper() == ".TXT")
	
	
	######################################################################
	#                                                                    #
	# get_illuminant_names                                               #
	#                                                                    #
	######################################################################
	def get_illuminant_names(self):
		"""Return a list of all the illuminants.
		
		The method takes no arguments and return a list of all the
		illuminants in alphabetic order."""
		
		illuminant_names = self.illuminants.keys()
		illuminant_names.sort()
		
		return illuminant_names
	
	
	######################################################################
	#                                                                    #
	# get_illuminant                                                     #
	#                                                                    #
	######################################################################
	def get_illuminant(self, illuminant_name):
		"""Get an illuminant.
		
		This method takes a single argument:
		  illuminant_name  the name of the illuminant.
		and returns the illuminant object corresponding to this name."""
		
		if illuminant_name not in self.illuminants:
			raise color_error(illuminant_name, "Unknown illuminant")
		
		# Read the illuminant only if necessary.
		if self.illuminants[illuminant_name] is None:
			self.illuminants[illuminant_name] = read_illuminant(illuminant_name)
		
		return self.illuminants[illuminant_name]
	
	
	######################################################################
	#                                                                    #
	# illuminant_exists                                                  #
	#                                                                    #
	######################################################################
	def illuminant_exists(self, illuminant_name):
		"""Verify in an illuminant exist.
		
		This method takes a single argument:
		  illuminant_name  the name of the illuminant.
		and returns a boolean value indicating if this illuminant is member
		of the list of illuminants."""
		
		return illuminant_name in self.illuminants



########################################################################
#                                                                      #
# observers                                                            #
#                                                                      #
########################################################################
class observers(object):
	"""A class to list the colorimetric observers."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, directory):
		"""Initialize the list of observers.
		
		This method initialize the list of colorimetric observers by
		listing all files in a directory. It takes one argument
		  directory        the directory where are the observer files.
		
		The observers are not actually read on initialization. They are
		read only if demanded with the get_observer method but where they
		are, they are kept in memory to avoid reading them twice."""
		
		self.observers = dict((os.path.splitext(filename)[0], None) for filename in os.listdir(directory) if os.path.splitext(filename)[1].upper() == ".TXT")
	
	
	######################################################################
	#                                                                    #
	# get_observer_names                                                 #
	#                                                                    #
	######################################################################
	def get_observer_names(self):
		"""Return a list of all the observers.
		
		The method takes no arguments and return a list of all the obervers
		in alphabetic order."""
		
		observer_names = self.observers.keys()
		observer_names.sort()
		
		return observer_names
	
	
	######################################################################
	#                                                                    #
	# get_observer                                                       #
	#                                                                    #
	######################################################################
	def get_observer(self, observer_name):
		"""Get an observer.
		
		This method takes a single argument:
		  observer_name    the name of the observer.
		and returns the observer object corresponding to this name."""
		
		if observer_name not in self.observers:
			raise color_error(observer_name, "Unknown observer")
		
		# Read the observer only if necessary.
		if self.observers[observer_name] is None:
			self.observers[observer_name] = read_observer(observer_name)
		
		return self.observers[observer_name]
	
	
	######################################################################
	#                                                                    #
	# observer_exists                                                    #
	#                                                                    #
	######################################################################
	def observer_exists(self, observer_name):
		"""Verify in an observer exist.
		
		This method takes a single argument:
		  observer_name    the name of the observer.
		and returns a boolean value indicating if this observer is member
		of the list of observers."""
		
		return observer_name in self.observers



# Make a list of observers and illuminants. This way they only need
# to be read once. And provide functions to access these lists.
__illuminants = illuminants(illuminants_directory)
__observers = observers(observers_directory)



########################################################################
#                                                                      #
# get_illuminant_names                                                 #
# get_illuminant                                                       #
# illuminant_exists                                                    #
# get_observer_names                                                   #
# get_observer                                                         #
# observer_exists                                                      #
#                                                                      #
########################################################################

def get_illuminant_names():
	return __illuminants.get_illuminant_names()

def get_illuminant(illuminant_name):
	return __illuminants.get_illuminant(illuminant_name)

def illuminant_exists(illuminant_name):
	return __illuminants.illuminant_exists(illuminant_name)

def get_observer_names():
	return __observers.get_observer_names()

def get_observer(observer_name):
	return __observers.get_observer(observer_name)

def observer_exists(observer_name):
	return __observers.observer_exists(observer_name)



########################################################################
#                                                                      #
# spectrum_to_XYZ                                                      #
#                                                                      #
########################################################################
def spectrum_to_XYZ(spectrum_wvls, spectrum, observer, illuminant):
	"""Calculate the XYZ color of the object from its spectrum.
	
	This functions takes four arguments:
	  spectrum_wvls  the wavelengths;
	  spectrum       the spectrum;
	  observer       the colorimetric observer
	  illuminant     the colorimetric illuminant
	and returns one argument:
	  XYZ            the XYZ color."""
	
	# Get the spectrums of the observer and the illuminant.
	observer_wvls, x_function, y_function, z_function = observer.get_functions()
	illuminant_wvls, illuminant_spectrum = illuminant.get_spectrum()
	
	# Express the spectrum and the illuminant at the same wavelengths than
	# the observer.
	if spectrum_wvls != observer_wvls:
		spectrum_prime = interpolation.spline(spectrum_wvls, spectrum, observer_wvls)
	else:
		spectrum_prime = spectrum
	if illuminant_wvls != observer_wvls:
		illuminant_spectrum_prime = interpolation.spline(illuminant_wvls, illuminant_spectrum, observer_wvls)
	else:
		illuminant_spectrum_prime = illuminant_spectrum
	
	# Calculate X, Y and Z of the object.
	X = 0.0
	Y = 0.0
	Z = 0.0
	normalization = 0.0
	for i in range(len(observer_wvls)):
		X += illuminant_spectrum_prime[i]*spectrum_prime[i]*x_function[i]
		Y += illuminant_spectrum_prime[i]*spectrum_prime[i]*y_function[i]
		Z += illuminant_spectrum_prime[i]*spectrum_prime[i]*z_function[i]
		normalization += illuminant_spectrum_prime[i]*y_function[i]
	
	# Normalize X, Y and Z (Y = 100 for the white point).
	normalization = 100.0/normalization
	X *= normalization
	Y *= normalization
	Z *= normalization
	
	return [X, Y, Z]



########################################################################
#                                                                      #
# white_point                                                          #
#                                                                      #
########################################################################
def white_point(observer, illuminant):
	"""Calculate the XYZ color of the white point.
	
	This functions takes two arguments:
	  observer       the colorimetric observer
	  illuminant     the colorimetric illuminant
	and returns one argument:
	  XYZ_n          the XYZ color of the white point."""
	
	# Get the spectrums of the observer and the illuminant.
	observer_wvls, x_function, y_function, z_function = observer.get_functions()
	illuminant_wvls, illuminant_spectrum = illuminant.get_spectrum()
	
	# Express the  the illuminant at the same wavelengths than the
	# observer.
	if illuminant_wvls != observer_wvls:
		illuminant_spectrum_prime = interpolation.spline(illuminant_wvls, illuminant_spectrum, observer_wvls)
	else:
		illuminant_spectrum_prime = illuminant_spectrum
	
	# Calculate X, Y and Z of the white point.
	X_n = 0.0
	Y_n = 0.0
	Z_n = 0.0
	normalization = 0.0
	for i in range(len(observer_wvls)):
		X_n += illuminant_spectrum_prime[i]*x_function[i]
		Y_n += illuminant_spectrum_prime[i]*y_function[i]
		Z_n += illuminant_spectrum_prime[i]*z_function[i]
	
	# Normalize X, Y and Z (Y = 100 for the white point).
	normalization = 100.0/Y_n
	X_n *= normalization
	Y_n = 100.0
	Z_n *= normalization
	
	return [X_n, Y_n, Z_n]



########################################################################
#                                                                      #
# XYZ_to_xyY                                                           #
#                                                                      #
########################################################################
def XYZ_to_xyY(XYZ):
	"""Convert a XYZ color to xyY.
	
	This function takes one argument:
		XYZ            the color in XYZ;
	and returns one argument:
		xyY            the color in xyY."""
	
	X = XYZ[0]
	Y = XYZ[1]
	Z = XYZ[2]
	
	sum = X + Y + Z
	
	if sum == 0.0:
		x = y = 0.0
	else:
		x = X/sum
		y = Y/sum
	
	return [x, y, Y]



########################################################################
#                                                                      #
# XYZ_to_Luv                                                           #
#                                                                      #
########################################################################
def XYZ_to_Luv(XYZ, XYZ_n):
	"""Convert a XYZ color to CIE L*u*v*.
	
	This function takes two arguments:
		XYZ            the color in XYZ;
	  XYZ_n          the white point in XYZ;
	and returns one argument:
		Luv            the color in L*u*v*."""
	
	X = XYZ[0]
	Y = XYZ[1]
	Z = XYZ[2]
	X_n = XYZ_n[0]
	Y_n = XYZ_n[1]
	Z_n = XYZ_n[2]
	
	denominator = X + 15.0*Y + 3.0*Z
	denominator_n = X_n + 15.0*Y_n + 3.0*Z_n
	
	if denominator == 0.0: return [0.0, 0.0, 0.0]
	
	u_ = 4.0*X / denominator
	v_ = 9.0*Y / denominator
	u_n = 4.0*X_n / denominator_n
	v_n = 9.0*Y_n / denominator_n
	
	Y_r = Y/Y_n
	
	if Y_r > gamma:
		f_Y = Y_r**one_third
	else:
		f_Y = alpha*Y_r + sixteen_over_one_hundred_sixteen
	
	L = 116.0*f_Y - 16.0
	u = 13.0*L*(u_ - u_n)
	v = 13.0*L*(v_ - v_n)
	
	return [L, u, v]



########################################################################
#                                                                      #
# XYZ_to_Lab                                                           #
#                                                                      #
########################################################################
def XYZ_to_Lab(XYZ, XYZ_n):
	"""Convert a XYZ color to L*a*b*.
	
	This function takes two arguments:
		XYZ            the color in XYZ;
	  XYZ_n          the white point in XYZ;
	and returns one argument:
		Lab            the color in L*a*b*."""
	
	X = XYZ[0]
	Y = XYZ[1]
	Z = XYZ[2]
	X_n = XYZ_n[0]
	Y_n = XYZ_n[1]
	Z_n = XYZ_n[2]
	
	X_r = X/X_n
	Y_r = Y/Y_n
	Z_r = Z/Z_n
	
	if Y_r > gamma:
		f_Y = Y_r**one_third
	else:
		f_Y = alpha*Y_r+sixteen_over_one_hundred_sixteen
	
	if X_r > gamma:
		f_X = X_r**one_third
	else:
		f_X = alpha*X_r+sixteen_over_one_hundred_sixteen
	
	if Z_r > gamma:
		f_Z = Z_r**one_third
	else:
		f_Z = alpha*Z_r+sixteen_over_one_hundred_sixteen
	
	L = 116.0*f_Y - 16.0
	a = 500.0*(f_X - f_Y)
	b = 200.0*(f_Y - f_Z)
	
	return [L, a, b]



########################################################################
#                                                                      #
# xyY_to_XYZ                                                           #
#                                                                      #
########################################################################
def xyY_to_XYZ(xyY):
	"""Convert a xyY color to XYZ.
	
	This function takes one argument:
		xyY            the color in xyY;
	and returns one argument:
		XYZ            the color in XYZ."""
	
	x = xyY[0]
	y = xyY[1]
	Y = xyY[2]
	
	sum = Y/y
	
	X = x*sum
	Z = (1.0 - x - y)*sum
	
	return [X, Y, Z]



########################################################################
#                                                                      #
# Luv_to_XYZ                                                           #
#                                                                      #
########################################################################
def Luv_to_XYZ(Luv, XYZ_n):
	"""Convert a CIE L*u*v* color to XYZ.
	
	This function takes two arguments:
		Luv            the color in L*u*v*;
	  XYZ_n          the white point in XYZ;
	and returns one argument:
		XYZ            the color in XYZ."""
	
	L = Luv[0]
	u = Luv[1]
	v = Luv[2]
	X_n = XYZ_n[0]
	Y_n = XYZ_n[1]
	Z_n = XYZ_n[2]
	
	denominator_n = X_n + 15.0*Y_n + 3.0*Z_n
	
	u_n = 4.0*X_n / denominator_n
	v_n = 9.0*Y_n / denominator_n
	
	u_ = u/(13.0*L) + u_n
	v_ = v/(13.0*L) + v_n
	
	f_Y = (L+16.0)/116.0
	
	if f_Y > cubic_root_gamma:
		Y_r = f_Y*f_Y*f_Y
	else:
		Y_r = (f_Y - sixteen_over_one_hundred_sixteen)/alpha
	
	Y = Y_r*Y_n
	X = 2.25*u_/v_ * Y
	Z = ((3.0-0.75*u_)/v_ - 5.0) * Y
	
	return [X, Y, Z]



########################################################################
#                                                                      #
# Luv_to_LChuv                                                         #
#                                                                      #
########################################################################
def Luv_to_LChuv(Luv):
	"""Convert a L*u*v* color to L*C*h(u*v*).
	
	This function takes one argument:
		Luv            the color in L*u*v*;
	and returns one argument:
		LChuv          the color in L*C*h(u*v*)."""
	
	L, u, v = Luv
	
	C = math.sqrt(u*u + v*v)
	h = one_hundred_eighty_over_pi*math.atan2(v, u)
	
	if h < 0.0: h += 360.0
	
	return [L, C, h]



########################################################################
#                                                                      #
# Lab_to_XYZ                                                           #
#                                                                      #
########################################################################
def Lab_to_XYZ(Lab, XYZ_n):
	"""Convert a L*a*b* color to XYZ.
	
	This function takes two arguments
		Lab            the color in L*a*b*;
	  XYZ_n          the white point in XYZ;
	and returns one argument:
	  XYZ            the color in XYZ."""
	
	L = Lab[0]
	a = Lab[1]
	b = Lab[2]
	X_n = XYZ_n[0]
	Y_n = XYZ_n[1]
	Z_n = XYZ_n[2]
	
	f_Y = (L+16.0)/116.0
	f_X = a/500.0 + f_Y
	f_Z = f_Y - b/200.0
	
	if f_X > cubic_root_gamma:
		X_r = f_X*f_X*f_X
	else:
		X_r = (f_X - sixteen_over_one_hundred_sixteen)/alpha
	
	if f_Y > cubic_root_gamma:
		Y_r = f_Y*f_Y*f_Y
	else:
		Y_r = (f_Y - sixteen_over_one_hundred_sixteen)/alpha
	
	if f_Z > cubic_root_gamma:
		Z_r = f_Z*f_Z*f_Z
	else:
		Z_r = (f_Z - sixteen_over_one_hundred_sixteen)/alpha
	
	X = X_r*X_n
	Y = Y_r*Y_n
	Z = Z_r*Z_n
	
	return [X, Y, Z]



########################################################################
#                                                                      #
# Lab_to_LChab                                                         #
#                                                                      #
########################################################################
def Lab_to_LChab(Lab):
	"""Convert a La*b* color to L*C*h(a*b*).
	
	This function takes one argument:
		Lab            the color in L*a*b*;
	and returns one argument:
		LChab          the color in L*C*h(a*b*)."""
	
	L, a, b = Lab
	
	C = math.sqrt(a*a + b*b)
	h = one_hundred_eighty_over_pi*math.atan2(b, a)
	
	if h < 0.0: h += 360.0
	
	return [L, C, h]



########################################################################
#                                                                      #
# LChuv_to_Luv                                                         #
#                                                                      #
########################################################################
def LChuv_to_Luv(LChuv):
	"""Convert a L*C*h(u*v*) color to L*u*v*.
	
	This function takes one argument:
		LChuv          the color in L*C*h(u*v*);
	and returns one argument:
		Luv            the color in L*u*v*."""
	
	L, C, h = LChuv
	
	h /= one_hundred_eighty_over_pi
	
	u = C*math.cos(h)
	v = C*math.sin(h)
	
	return [L, u, v]



########################################################################
#                                                                      #
# LChab_to_Lab                                                         #
#                                                                      #
########################################################################
def LChab_to_Lab(LChab):
	"""Convert a L*C*h(a*b*) color to L*a*b*.
	
	This function takes one argument:
		LChab          the color in L*C*h(a*b*);
	and returns one argument:
		Lab            the color in L*a*b*."""
	
	L, C, h = LChab
	
	h /= one_hundred_eighty_over_pi
	
	a = C*math.cos(h)
	b = C*math.sin(h)
	
	return [L, a, b]



########################################################################
#                                                                      #
# change_color_space                                                   #
#                                                                      #
########################################################################
def change_color_space(old_color_space, new_color_space, old_color, XYZ_n):
	"""Convert a color from a color space to another.
	
	This function takes four arguments:
		old_color_space    the old color space;
	  new_color_space    the new color space;
	  old_color          the color in the old color space
	  XYZ_n              the white point in XYZ;
	and returns one argument:
		new_color          the color in the new color space.
	
	The conversion is made by calling this function recursively when
	necessary."""
	
	# The trivial case of same old and new color space.
	
	if new_color_space == old_color_space:
		return old_color
	
	
	# Now lets handle the case of color spaces that are 2 steps away
	# from XYZ
	
	if old_color_space == LChuv:
		return change_color_space(Luv, new_color_space, LChuv_to_Luv(old_color), XYZ_n)
	
	if old_color_space == LChab:
		return change_color_space(Lab, new_color_space, LChab_to_Lab(old_color), XYZ_n)
	
	if new_color_space == LChuv:
		return Luv_to_LChuv(change_color_space(old_color_space, Luv, old_color, XYZ_n))
	
	if new_color_space == LChab:
		return Lab_to_LChab(change_color_space(old_color_space, Lab, old_color, XYZ_n))
	
	
	# And now the case of color spaces that are a single step away from
	# XYZ.
	
	if old_color_space == xyY:
		return change_color_space(XYZ, new_color_space, xyY_to_XYZ(old_color), XYZ_n)
	
	if old_color_space == Lab:
		return change_color_space(XYZ, new_color_space, Lab_to_XYZ(old_color, XYZ_n), XYZ_n)
	
	if old_color_space == Luv:
		return change_color_space(XYZ, new_color_space, Luv_to_XYZ(old_color, XYZ_n), XYZ_n)

	if new_color_space == xyY:
		return XYZ_to_xyY(change_color_space(old_color_space, XYZ, old_color, XYZ_n))
	
	if new_color_space == Lab:
		return XYZ_to_Lab(change_color_space(old_color_space, XYZ, old_color, XYZ_n), XYZ_n)
	
	if new_color_space == Luv:
		return XYZ_to_Luv(change_color_space(old_color_space, XYZ, old_color, XYZ_n), XYZ_n)



########################################################################
#                                                                      #
# XYZ_to_RGB                                                           #
#                                                                      #
########################################################################
def XYZ_to_RGB(XYZ):
	"""Convert a XYZ color to RGB.
	
	This function takes two arguments:
		XYZ            the color in XYZ;
	and returns one argument:
		RGB            the color in RGB
		error          indication that the color is not representable in
		               RGB.
	
	When a color is not representable in RGB, R, G and B components
	are limited to [0, 1]. To verify if such an error occured, you can
	call the get_RGB_error method."""
	
	# Get X, Y and Z in a [0, 1] interval.
	X = 0.01*XYZ[0]
	Y = 0.01*XYZ[1]
	Z = 0.01*XYZ[2]
	
	M = XYZ_to_RGB_matrix_709
	
	R_ = M[0][0]*X + M[1][0]*Y + M[2][0]*Z
	G_ = M[0][1]*X + M[1][1]*Y + M[2][1]*Z
	B_ = M[0][2]*X + M[1][2]*Y + M[2][2]*Z
	
	# Correct RGB values that are smaller than 0 or larger that 1. This
	# implies that not all color can be reprensented in RGB.
	R = min(max(R_, 0.0), 1.0)
	G = min(max(G_, 0.0), 1.0)
	B = min(max(B_, 0.0), 1.0)
	
	if R != R_ or G != G_ or B != B_:
		return [R, G, B], True
	else:
		return [R, G, B], False



########################################################################
#                                                                      #
# RGB_to_XYZ                                                           #
#                                                                      #
########################################################################
def RGB_to_XYZ(RGB):
	"""Convert a RGB color to XYZ.
	
	This function takes one argument:
		RGB            the color in RGB;
	and returns one argument:
		XYZ            the color in XYZ."""
	
	XYZ = RGB[:]
	
	M = copy.deepcopy(XYZ_to_RGB_matrix_709)
	
	Gauss_Jordan.Gauss_Jordan(M, [XYZ])
	
	# Put X, Y and Z in a [0, 100] interval.
	XYZ[0] *= 100.0
	XYZ[1] *= 100.0
	XYZ[2] *= 100.0
	
	return XYZ



########################################################################
#                                                                      #
# color                                                                #
#                                                                      #
########################################################################
class color(object):
	"""A class to calculate the color of an object in various color
	spaces."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, observer, illuminant):
		"""Creator of the color.
		
		This method takes two arguments:
		  observer       a colorimetric observer class object;
		  illuminant     a colorimetric illuminant class object"""
		
		self.observer = observer
		self.illuminant = illuminant
		
		# Calculate the color of the white point immediatly.
		self.XYZ_n = white_point(self.observer, self.illuminant)
		
		# The color of the object is kept in XYZ.
		self.XYZ_ = []
		
		# Keep information about the RGB color conversion.
		self.RGB_error = False
	
	
	######################################################################
	#                                                                    #
	# get_observer                                                       #
	#                                                                    #
	######################################################################
	def get_observer(self):
		"""Return the observer."""
		
		return self.observer
	
	
	######################################################################
	#                                                                    #
	# get_illuminant                                                     #
	#                                                                    #
	######################################################################
	def get_illuminant(self):
		"""Return the illuminant."""
		
		return self.illuminant
	
	
	######################################################################
	#                                                                    #
	# set_color                                                          #
	#                                                                    #
	######################################################################
	def set_color(self, color_, color_space = XYZ):
		"""Calculate the color of the object from its spectrum.
		
		This method takes two arguments:
		  spectrum_wvls  the wavelengths;
		  spectrum       the spectrum."""
		
		if color_space == XYZ:
			self.XYZ_ = color_
		elif color_space == xyY:
			self.XYZ_ = xyY_to_XYZ(color_)
		elif color_space == Luv:
			self.XYZ_ = Luv_to_XYZ(color_, self.XYZ_n)
		elif color_space == Lab:
			self.XYZ_ = Lab_to_XYZ(color_, self.XYZ_n)
		elif color_space == LChuv:
			self.XYZ_ = Luv_to_XYZ(LChuv_to_Luv(color_), self.XYZ_n)
		elif color_space == LChab:
			self.XYZ_ = Lab_to_XYZ(LChab_to_Lab(color_), self.XYZ_n)
	
	
	######################################################################
	#                                                                    #
	# calculate_color                                                    #
	#                                                                    #
	######################################################################
	def calculate_color(self, spectrum_wvls, spectrum):
		"""Calculate the color of the object from its spectrum.
		
		This method takes two arguments:
		  spectrum_wvls  the wavelengths;
		  spectrum       the spectrum."""
		
		self.XYZ_ = spectrum_to_XYZ(spectrum_wvls, spectrum, self.observer, self.illuminant)
	
	
	######################################################################
	#                                                                    #
	# XYZ                                                                #
	#                                                                    #
	######################################################################
	def XYZ(self):
		"""Return the color in XYZ color space."""
		
		return self.XYZ_
	
	
	######################################################################
	#                                                                    #
	# xyY                                                                #
	#                                                                    #
	######################################################################
	def xyY(self):
		"""Return the xyY color."""
		
		return XYZ_to_xyY(self.XYZ_)
	
	
	######################################################################
	#                                                                    #
	# Luv                                                                #
	#                                                                    #
	######################################################################
	def Luv(self):
		"""Return the L*u*v* color."""
		
		return XYZ_to_Luv(self.XYZ_, self.XYZ_n)
	
	
	######################################################################
	#                                                                    #
	# Lab                                                                #
	#                                                                    #
	######################################################################
	def Lab(self):
		"""Return the L*a*b* color."""
		
		return XYZ_to_Lab(self.XYZ_, self.XYZ_n)
	
	
	######################################################################
	#                                                                    #
	# LChuv                                                              #
	#                                                                    #
	######################################################################
	def LChuv(self):
		"""Return the L*C*h(u*v*) color."""
		
		return Luv_to_LChuv(XYZ_to_Luv(self.XYZ_, self.XYZ_n))
	
	
	######################################################################
	#                                                                    #
	# LChab                                                              #
	#                                                                    #
	######################################################################
	def LChab(self):
		"""Return the L*C*h(a*b*) color."""
		
		return Lab_to_LChab(XYZ_to_Lab(self.XYZ_, self.XYZ_n))
	
	
	######################################################################
	#                                                                    #
	# color                                                              #
	#                                                                    #
	######################################################################
	def color(self, color_space):
		"""Return the color in a specified color space.
		
		This method takes one argument:
		  color_space    the color space;
		and returns the color in that color space."""
		
		if color_space == XYZ:
			return self.XYZ_
		elif color_space == xyY:
			return XYZ_to_xyY(self.XYZ_)
		elif color_space == Luv:
			return XYZ_to_Luv(self.XYZ_, self.XYZ_n)
		elif color_space == Lab:
			return XYZ_to_Lab(self.XYZ_, self.XYZ_n)
		elif color_space == LChuv:
			return Luv_to_LChuv(XYZ_to_Luv(self.XYZ_, self.XYZ_n))
		elif color_space == LChab:
			return Lab_to_LChab(XYZ_to_Lab(self.XYZ_, self.XYZ_n))
	
	
	######################################################################
	#                                                                    #
	# RGB                                                                #
	#                                                                    #
	######################################################################
	def RGB(self):
		"""Return the RGB color.
		
		When a color is not representable in RGB, R, G and B components
		are limited to [0, 1]. To verify if such an error occured, you can
		call the get_RGB_error method."""
		
		RGB, self.RGB_error = XYZ_to_RGB(self.XYZ_)
		
		return RGB
	
	
	######################################################################
	#                                                                    #
	# get_RGB_error                                                      #
	#                                                                    #
	######################################################################
	def get_RGB_error(self):
		"""Indicate if an error occured the last time a color was converted
		to RGB."""
		
		return self.RGB_error
	
	
	######################################################################
	#                                                                    #
	# white_point                                                        #
	#                                                                    #
	######################################################################
	def white_point(self):
		"""Return the white point in XYZ color space."""
		
		return self.XYZ_n



########################################################################
#                                                                      #
# color_derivative                                                     #
#                                                                      #
########################################################################
class color_derivative(object):
	"""A class to calculate the derivative of the color of an object in
	various color spaces."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, color):
		"""Creator of the color derivative.
		
		This method takes one arguments:
		  color          the color of which the derivative is wanted.
		
		When calculating the derivative the color must be up to date."""
		
		self.color = color
		
		# The derivative of the color of the object.
		self.dX = 0.0
		self.dY = 0.0
		self.dZ = 0.0
	
	
	######################################################################
	#                                                                    #
	# calculate_color_derivative                                         #
	#                                                                    #
	######################################################################
	def calculate_color_derivative(self, spectrum_wvls, spectrum, dspectrum):
		"""Calcule the derivative of the color of an object using the
		derivative of the spectrum.
		
		This method takes three arguments:
		  spectrum_wvls  the wavelengths;
		  spectrum       the spectrum;
		  dspectrum      the derivative of the spectrum."""
		
		# Get the observer and the illuminant.
		observer = self.color.get_observer()
		illuminant = self.color.get_illuminant()
		
		# Get the spectrums of the observer and the illuminant.
		observer_wvls, x_function, y_function, z_function = observer.get_functions()
		illuminant_wvls, illuminant_spectrum = illuminant.get_spectrum()
		
		# Express the spectrum and the illuminant at the same wavelengths than
		# the observer.
		if spectrum_wvls != observer_wvls:
			dspectrum_prime = interpolation.spline(spectrum_wvls, dspectrum, observer_wvls)
			spectrum_prime = interpolation.spline(spectrum_wvls, spectrum, observer_wvls)
		else:
			dspectrum_prime = dspectrum
			spectrum_prime = spectrum
		if illuminant_wvls != observer_wvls:
			illuminant_spectrum_prime = interpolation.spline(illuminant_wvls, illuminant_spectrum, observer_wvls)
		else:
			illuminant_spectrum_prime = illuminant_spectrum
		
		# Calculate X, Y and Z of the object and those of the white point.
		self.dX = 0.0
		self.dY = 0.0
		self.dZ = 0.0
		normalization = 0.0
		for i in range(len(observer_wvls)):
			self.dX += illuminant_spectrum_prime[i]*dspectrum_prime[i]*x_function[i]
			self.dY += illuminant_spectrum_prime[i]*dspectrum_prime[i]*y_function[i]
			self.dZ += illuminant_spectrum_prime[i]*dspectrum_prime[i]*z_function[i]
			normalization += illuminant_spectrum_prime[i]*y_function[i]
		
		# Normalize dX, dY and dZ (Y = 100 for the white point).
		normalization = 100.0/normalization
		self.dX *= normalization
		self.dY *= normalization
		self.dZ *= normalization
	
	
	######################################################################
	#                                                                    #
	# dXYZ                                                               #
	#                                                                    #
	######################################################################
	def dXYZ(self):
		"""Return the derivative of the color in XYZ color space."""
		
		return [self.dX, self.dY, self.dZ]
	
	
	######################################################################
	#                                                                    #
	# dxyY                                                               #
	#                                                                    #
	######################################################################
	def dxyY(self):
		"""Return the derivative of the xyY color."""
		
		XYZ = self.color.XYZ()
		X = XYZ[0]
		Y = XYZ[1]
		Z = XYZ[2]
		
		sum = X + Y + Z
		
		dx = (self.dX - X*(self.dX+self.dY+self.dZ)/sum) / sum
		dy = (self.dY - Y*(self.dX+self.dY+self.dZ)/sum) / sum
		
		return [dx, dy, self.dY]
	
	
	######################################################################
	#                                                                    #
	# dLuv                                                               #
	#                                                                    #
	######################################################################
	def dLuv(self):
		"""Return derivative of the L*u*v* color."""
		
		XYZ = self.color.XYZ()
		XYZ_n = self.color.white_point()
		X = XYZ[0]
		Y = XYZ[1]
		Z = XYZ[2]
		X_n = XYZ_n[0]
		Y_n = XYZ_n[1]
		Z_n = XYZ_n[2]
		
		denominator = X + 15.0*Y + 3.0*Z
		denominator_n = X_n + 15.0*Y_n + 3.0*Z_n
		
		if denominator == 0.0: return [0.0, 0.0, 0.0]
		
		ddenominator = self.dX + 15.0*self.dY + 3.0*self.dZ
		
		u_ = 4.0*X / denominator
		v_ = 9.0*Y / denominator
		u_n = 4.0*X_n / denominator_n
		v_n = 9.0*Y_n / denominator_n
		
		du_ = (4.0*self.dX - u_*ddenominator) / denominator
		dv_ = (9.0*self.dY - v_*ddenominator) / denominator
		
		Y_r = Y/Y_n
		dY_r = self.dY/Y_n
		
		if Y_r > gamma:
			f_Y = Y_r**one_third
			df_Y= one_third*Y_r**minus_two_third * dY_r
		else:
			f_Y = alpha*Y_r + sixteen_over_one_hundred_sixteen
			df_Y = alpha*dY_r
		
		L = 116.0*f_Y - 16.0
		dL = 116.0*df_Y
		
		dL = 116.0*df_Y
		du = 13.0*(dL*(u_ - u_n) + L*du_)
		dv = 13.0*(dL*(v_ - v_n) + L*dv_)
		
		return [dL, du, dv]
	
	
	######################################################################
	#                                                                    #
	# dLab                                                               #
	#                                                                    #
	######################################################################
	def dLab(self):
		"""Return derivative of the L*a*b* color."""
		
		XYZ = self.color.XYZ()
		XYZ_n = self.color.white_point()
		X = XYZ[0]
		Y = XYZ[1]
		Z = XYZ[2]
		X_n = XYZ_n[0]
		Y_n = XYZ_n[1]
		Z_n = XYZ_n[2]
		
		X_r = X/X_n
		Y_r = Y/Y_n
		Z_r = Z/Z_n
		
		dX_r = self.dX/X_n
		dY_r = self.dY/Y_n
		dZ_r = self.dZ/Z_n
		
		if Y_r > gamma:
			df_Y = one_third*Y_r**minus_two_third * dY_r
		else:
			df_Y = alpha*dY_r
		
		if X_r > gamma:
			df_X = one_third*X_r**minus_two_third * dX_r
		else:
			df_X = alpha*dX_r
		
		if Z_r > gamma:
			df_Z = one_third*Z_r**minus_two_third * dZ_r
		else:
			df_Z = alpha*dZ_r
		
		dL = 116.0*df_Y
		da = 500.0*(df_X - df_Y)
		db = 200.0*(df_Y - df_Z)
		
		return [dL, da, db]
	
	
	######################################################################
	#                                                                    #
	# dLChuv                                                             #
	#                                                                    #
	######################################################################
	def dLChuv(self):
		"""Return derivative of the L*C*h(u*v*) color."""
		
		L, u, v = self.color.Luv()
		dL, du, dv = self.dLuv()
		
		u_square = u*u
		v_square = v*v
		
		dC = (u*du+v*dv)/math.sqrt(u_square+v_square)
		if u == 0.0:
			dh = -1.0/v
		else:
			dh = (dv/u-v*du/u_square)/(1.0+v_square/u_square)
		
		dh *= one_hundred_eighty_over_pi
		
		return [dL, dC, dh]
	
	
	######################################################################
	#                                                                    #
	# dLChab                                                             #
	#                                                                    #
	######################################################################
	def dLChab(self):
		"""Return derivative of the L*C*h(a*b*) color."""
		
		L, a, b = self.color.Lab()
		dL, da, db = self.dLab()
		
		a_square = a*a
		b_square = b*b
		
		dC = (a*da+b*db)/math.sqrt(a_square+b_square)
		if a == 0.0:
			dh = -1.0/b
		else:
			dh = (db/a-b*da/a_square)/(1.0+b_square/a_square)
		
		dh *= one_hundred_eighty_over_pi
		
		return [dL, dC, dh]
	
	
	######################################################################
	#                                                                    #
	# dcolor                                                             #
	#                                                                    #
	######################################################################
	def dcolor(self, color_space):
		"""Return the derivative of the color in a specified color space.
		
		This method takes one argument:
		  color_space    the color space;
		and returns the derivative of the color in that color space."""
		
		if color_space == XYZ:
			return self.dXYZ()
		elif color_space == xyY:
			return self.dxyY()
		elif color_space == Luv:
			return self.dLuv()
		elif color_space == Lab:
			return self.dLab()
		elif color_space == LChuv:
			return self.dLChuv()
		elif color_space == LChab:
			return self.dLChab()



########################################################################
#                                                                      #
# Delta_E_1976                                                         #
#                                                                      #
########################################################################
def Delta_E_1976(color_1, color_2):
	"""Calculate color difference according to CIE1976 standard.
	
	This method takes two arguments:
	  color_1        the color of the first object,
	  color_2        the color of the second object;
	and returns the color difference. The color can either be an instance
	of the color class, or a 3-element sequence containing the color in
	Lab coordinates."""
	
	if isinstance(color_1, color):
		Lab_1 = color_1.Lab()
	else:
		Lab_1 = color_1
	if isinstance(color_2, color):
		Lab_2 = color_2.Lab()
	else:
		Lab_2 = color_2
	
	Delta_L = Lab_2[0] - Lab_1[0]
	Delta_a = Lab_2[1] - Lab_1[1]
	Delta_b = Lab_2[2] - Lab_1[2]
	
	Delta_E = math.sqrt(Delta_L*Delta_L + Delta_a*Delta_a + Delta_b*Delta_b)
	
	return Delta_E



########################################################################
#                                                                      #
# Delta_E_2000                                                         #
#                                                                      #
########################################################################
def Delta_E_2000(color_1, color_2):
	"""Calculate color difference according to CIEDE2000 standard.
	
	This method takes two arguments:
	  color_1        the color of the first object,
	  color_2        the color of the second object;
	and returns the color difference. The color can either be an instance
	of the color class, or a 3-element sequence containing the color in
	Lab coordinates.
	
	For more information about the CIEDE2000 standard, see
	  M. R. Luo, G. Cui, and B. Rigg, "The Development of the CIE 2000
	  Colour-Difference Formula: CIEDE2000", Color Research and
	  Application, Volume 26, Number 5, October 2001, pp. 340-350."""
	
	if isinstance(color_1, color):
		Lab_1 = color_1.Lab()
	else:
		Lab_1 = color_1
	if isinstance(color_2, color):
		Lab_2 = color_2.Lab()
	else:
		Lab_2 = color_2
	
	L_1 = Lab_1[0]
	a_1 = Lab_1[1]
	b_1 = Lab_1[2]
	
	L_2 = Lab_2[0]
	a_2 = Lab_2[1]
	b_2 = Lab_2[2]
	
	C_1 = math.sqrt(a_1*a_1 + b_1*b_1)
	
	C_2 = math.sqrt(a_2*a_2 + b_2*b_2)
	
	C_bar = 0.5*(C_1+C_2)
	C_bar_seven = C_bar**7
	G = 0.5*(1.0-math.sqrt(C_bar_seven/(C_bar_seven+6103515625.0)))
	
	L_prime_1 = L_1
	a_prime_1 = (1.0+G)*a_1
	b_prime_1 = b_1
	C_prime_1 = math.sqrt(a_prime_1*a_prime_1+b_prime_1*b_prime_1)
	h_prime_1 = math.atan2(b_prime_1, a_prime_1) * one_hundred_eighty_over_pi
	if h_prime_1 < 0.0: h_prime_1 += 360.0
	
	L_prime_2 = L_2
	a_prime_2 = (1.0+G)*a_2
	b_prime_2 = b_2
	C_prime_2 = math.sqrt(a_prime_2*a_prime_2+b_prime_2*b_prime_2)
	h_prime_2 = math.atan2(b_prime_2, a_prime_2) * one_hundred_eighty_over_pi
	if h_prime_2 < 0.0: h_prime_2 += 360.0
	
	Delta_h_prime = h_prime_2-h_prime_1
	Delta_L_prime = L_prime_2-L_prime_1
	Delta_C_prime = C_prime_2-C_prime_1
	Delta_H_prime = 2.0*math.sqrt(C_prime_1*C_prime_2)*math.sin(0.5*Delta_h_prime/one_hundred_eighty_over_pi)
	
	L_prime_bar = 0.5*(L_prime_1+L_prime_2)
	C_prime_bar = 0.5*(C_prime_1+C_prime_2)
	h_prime_bar = 0.5*(h_prime_1+h_prime_2)
	if abs(Delta_h_prime) > 180.0: h_prime_bar -= 180.0
	
	T = 1.0 - 0.17*math.cos((h_prime_bar-30.0)/one_hundred_eighty_over_pi)\
	        + 0.24*math.cos(2.0*h_prime_bar/one_hundred_eighty_over_pi)\
	        + 0.32*math.cos((3.0*h_prime_bar+6.0)/one_hundred_eighty_over_pi)\
	        - 0.20*math.cos((4.0*h_prime_bar-63.0)/one_hundred_eighty_over_pi)
	temp = (h_prime_bar-275.0)/25.0
	Delta_theta = 30.0*math.exp(-temp*temp)
	C_prime_bar_seven = C_prime_bar**7
	R_C = 2.0*math.sqrt(C_prime_bar_seven/(C_prime_bar_seven+6103515625.0))
	R_T = -math.sin(2.0*Delta_theta/one_hundred_eighty_over_pi)*R_C
	
	L_prime_bar_minus_50 = L_prime_bar-50.0
	L_prime_bar_minus_50_square = L_prime_bar_minus_50*L_prime_bar_minus_50
	S_L = 1.0+0.015*L_prime_bar_minus_50_square/math.sqrt(20.0+L_prime_bar_minus_50_square)
	S_C = 1.0+0.045*C_prime_bar
	S_H = 1.0+0.015*C_prime_bar*T
	
	k_L = k_C = k_H = 1.0
	
	Delta_L_prime_over_k_L_S_L = Delta_L_prime/k_L/S_L
	Delta_C_prime_over_k_C_S_C = Delta_C_prime/k_C/S_C
	Delta_H_prime_over_k_H_S_H = Delta_H_prime/k_H/S_H
	
	Delta_E = math.sqrt(  Delta_L_prime_over_k_L_S_L*Delta_L_prime_over_k_L_S_L
	                    + Delta_C_prime_over_k_C_S_C*Delta_C_prime_over_k_C_S_C
	                    + Delta_H_prime_over_k_H_S_H*Delta_H_prime_over_k_H_S_H
	                    + R_T*Delta_C_prime_over_k_C_S_C*Delta_H_prime_over_k_H_S_H)
	
	return Delta_E



########################################################################
#                                                                      #
# calculate_xy_boundary                                                #
#                                                                      #
########################################################################
def calculate_xy_boundary(observer, min_wvl = None, max_wvl = None):
	"""Calculate (x,y) chromaticity values for monocromatic stimulations
	for the whole spectrum."""
	
	# Get the observer functions.
	observer_wvls, x_function, y_function, z_function = observer.get_functions()
	
	if min_wvl is None:
		min_wvl = min(observer_wvls)
	if max_wvl is None:
		max_wvl = max(observer_wvls)
	
	nb_wvls = len(observer_wvls)
	
	boundary_x = [0.0]*nb_wvls
	boundary_y = [0.0]*nb_wvls
	boundary_wvls = observer_wvls[::]
	
	# Scan the wavelengths in reverse order so we can remove elements at
	# which the xy value is impossible to calculate without screwing
	# the increment variable.
	for i in range(nb_wvls)[::-1]:
		# The chromaticity of a monochromatic stimulation can be obtained
		# simply from the tristimulus functions. Multiplying by an
		# illuminant is useless because all functions would be multiplied
		# by the same value and we later do a normalization.
		X = x_function[i]
		Y = y_function[i]
		Z = z_function[i]
		
		sum = X + Y + Z
		
		# If the sum is 0, all 3 functions are null and it is impossible to
		# determine the color. Remove that point.
		if sum == 0.0:
			boundary_x.pop(i)
			boundary_y.pop(i)
			boundary_wvls.pop(i)
		
		# If the wavelength is outside of established limits, remove that
		# point.
		elif boundary_wvls[i] < min_wvl or boundary_wvls[i] > max_wvl:
			boundary_x.pop(i)
			boundary_y.pop(i)
			boundary_wvls.pop(i)
		
		else:
			boundary_x[i] = X/sum
			boundary_y[i] = Y/sum
	
	return boundary_x, boundary_y, boundary_wvls



########################################################################
#                                                                      #
# read_observer                                                        #
#                                                                      #
########################################################################
def read_observer(observer_name):
	"""Read an observer file and returns its functions."""
	
	file_name = observer_name + ".txt"
	file_name = os.path.join(observers_directory, file_name)
	
	try:
		observer_file = open(file_name, "r")
	except IOError:
		raise color_error(observer_name, "Impossible to open observer file")
	
	try:
		keywords, values = simple_parser.parse_file(observer_file)
	except simple_parser.parsing_error, error:
		raise color_error(observer_name, "Cannot parse observer because %s" % error.get_value())
	
	observer_file.close()
	
	description = ""
	wvls = []
	x_function = []
	y_function = []
	z_function = []
	
	# Analyse the elements
	while keywords != []:
		keyword = keywords.pop(0)
		value = values.pop(0)
		
		# In the case of the description, the values are simply considered
		# as lines of the description. The description can be empty.
		if keyword == "Description":
			if value == []:
				description = ""
			else:
				description = value.pop(0)
				while value != []:
					line = value.pop(0)
					description = description + "\n" + line
		
		# For the spectrum, each line is a wavelength and a power.
		elif keyword == "Functions":
			for i in range(len(value)):
				elements = value[i].split()
				
				if len(elements) != 4:
					raise color_error(observer_name, "Each line in the observer functions must contain a wavelength and the three colorimetric functions")
				
				try:
					wvl = float(elements[0])
					x = float(elements[1])
					y = float(elements[2])
					z = float(elements[3])
				except ValueError:
					raise color_error(observer_name, "Colorimetric functions must be floats")
				
				wvls.append(wvl)
				x_function.append(x)
				y_function.append(y)
				z_function.append(z)
		
		else:
			raise color_error(observer_name, "Unknown keyword %s" % keyword)
	
	# Verify that wavelengths are in stricly increasing order.
	for i_wvl in range(1, len(wvls)):
		if wvls[i_wvl] <= wvls[i_wvl-1]:
			raise color_error(observer_name, "Wavelengths in observer functions must be in increasing order")
	
	return observer(observer_name, description, wvls, x_function, y_function, z_function)



########################################################################
#                                                                      #
# read_illuminant                                                      #
#                                                                      #
########################################################################
def read_illuminant(illuminant_name):
	"""Read an illuminant file and return its spectrum."""
	
	file_name = illuminant_name + ".txt"
	file_name = os.path.join(illuminants_directory, file_name)
	
	try:
		illuminant_file = open(file_name, "r")
	except IOError:
		raise color_error(illuminant_name, "Impossible to open illuminant file")
	
	try:
		keywords, values = simple_parser.parse_file(illuminant_file)
	except simple_parser.parsing_error, error:
		raise color_error(illuminant_name, "Cannot parse illuminant because %s" % error.get_value())
	
	illuminant_file.close()
	
	description = ""
	wvls = []
	spectrum = []
	
	# Analyse the elements
	while keywords != []:
		keyword = keywords.pop(0)
		value = values.pop(0)
		
		# In the case of the description, the values are simply considered
		# as lines of the description. The description can be empty.
		if keyword == "Description":
			if value == []:
				description = ""
			else:
				description = value.pop(0)
				while value != []:
					line = value.pop(0)
					description = description + "\n" + line
		
		# For the spectrum, each line is a wavelength and a power.
		elif keyword == "Spectrum":
			for i in range(len(value)):
				elements = value[i].split()
				
				if len(elements) != 2:
					raise color_error(illuminant_name, "Each line in the illuminant spectrum must contain a wavelength and a value")
				
				try:
					wvl = float(elements[0])
					power = float(elements[1])
				except ValueError:
					raise color_error(illuminant_name, "Illuminant spectrum must be floats")
				
				wvls.append(wvl)
				spectrum.append(power)
		
		else:
			raise color_error(illuminant_name, "Unknown keyword %s" % keyword)
	
	# Verify that wavelengths are in stricly increasing order.
	for i_wvl in range(1, len(wvls)):
		if wvls[i_wvl] <= wvls[i_wvl-1]:
			raise color_error(illuminant_name, "Wavelengths in illuminant spectrum must be in increasing order")
	
	return illuminant(illuminant_name, description, wvls, spectrum)
