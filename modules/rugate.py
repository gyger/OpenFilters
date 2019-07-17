# rugate.py
# 
# A module to create rugate filters.
# 
# Copyright (c) 2000-2009 Stephane Larouche.
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


name = "Rugate"
description = [["Rugate (nb periods and amplitude)", "rugate", "rugate_dialog"],
               ["Rugate (R and bandwidth)", "rugate_by_R", "rugate_by_R_dialog"],
               ["Multiband Rugate (nb periods and amplitude)", "multiband_rugate", "multiband_rugate_dialog"],
               ["Multiband Rugate (R and bandwidth)", "multiband_rugate_by_R", "multiband_rugate_by_R_dialog"]]



import math
import cmath

import wx
import wx.grid

from definitions import *
from moremath import interpolation
from moremath import limits

from GUI import GUI_layer_dialogs
from GUI.GUI_validators import int_validator, float_validator



sqrt_epsilon = math.sqrt(limits.epsilon)



########################################################################
#                                                                      #
# BesselI0                                                             #
#                                                                      #
########################################################################
def BesselI0(x):
	"""Modified Bessel function I_0
	
	Calculates the modified Bessel function I_0 of a real argument. It
	is calculated using two different expansion, one for small arguments
	and one for large arguments.
	
	For details on these expansions, see
	  Milton Abramowitz and Irene A. Stegun, Handbook of mathematical
	  functions."""
	
	if abs(x) < 3.75:
		t = x/3.75
		t_square = t*t
		I0 = 1.0+t_square*(3.5156229\
		        +t_square*(3.0899424\
		        +t_square*(1.2067492\
		        +t_square*(0.2659732\
		        +t_square*(0.0360768\
		        +t_square* 0.0045813)))))
	else:
		inv_t = 3.75/x
		I0 = (math.exp(abs(x))/math.sqrt(abs(x)))\
		     *(0.39894228+inv_t*( 0.01328592\
		                 +inv_t*( 0.00225319\
		                 +inv_t*(-0.00157565\
		                 +inv_t*( 0.00916281\
                     +inv_t*(-0.02057706\
                     +inv_t*( 0.02635537\
                     +inv_t*(-0.01647633\
                     +inv_t*  0.00392377))))))))
  
	return I0



########################################################################
#                                                                      #
# rugate                                                               #
#                                                                      #
########################################################################
def rugate(filter, position, side, replace, material_name, band_wvl, nb_periods, amplitude, phase, apodisation):
	"""Create a rugate layer with given number of periods and amplitude
	
	This function takes 10 arguments:
	  filter               the filter to which to add the rugate;
	  position             the position in the filter where to add the
	                       rugate;
	  side                 the side on which to add the rugate;
	  replace              a boolean indicating if the rugate sould
	                       replace the layer at the given position;
	  material_name        the name of the material to user;
	  band_wvl             the wavelength of the rugate;
	  nb_periods           the number of periods of the rugate;
	  amplitude            the amplitude of the rugate;
	  phase                the phase of the rugate;
	  apodisation          the apodisation of the rugate.
	and modifies the filter accordingly.
	
	For more details about rugates, see
	  Bovard, "Rugate Filter Theory: An Overview", Appl. Opt. vol .32,
	  1993, pp. 5427-5442."""
	
	material, center_wvl, step_spacing = get_filter_properties(filter, material_name)
	
	n_min_center, n_max_center, n_min, n_max, n_0 = index_ranges(material, 1, [band_wvl], center_wvl)
	
	sublayer_OT = select_sublayer_OT([band_wvl], n_min_center, n_max_center, step_spacing)
	
	# Adjustement of n_min and n_max to account for the amplitude.
	if amplitude is not None:
		half_amplitude = 0.5*amplitude
		n_min[0] = n_0[0]-half_amplitude
		n_max[0] = n_0[0]+half_amplitude
	
	# The phase.
	if phase is None:
		Phi = 0.0
	else:
		Phi = phase
	
	# When Phi is not used, try to make sure the rugate finishes with
	# an high index semi-period.
	if phase is None:
		# Integer number of periods.
		if nb_periods == round(nb_periods):
			# For an even number of periods, a pi shift is added.
			if (nb_periods/2.0) == round(nb_periods/2.0):
				Phi = math.pi
			# For an odd number of periods, no shift is added.
		# Half integer number of periods.
		elif 2.0*nb_periods == round(2.0*nb_periods):
			if (nb_periods - 0.5)/2.0 == round((nb_periods - 0.5)/2.0):
				Phi = 0.5*math.pi
			else:
				Phi = -0.5*math.pi
	
	x, OT, profiles, nb_sublayers, centers = prepare_profiles(1, [band_wvl], [nb_periods], sublayer_OT)
	
	W = apodisation_enveloppes(1, x, OT, nb_sublayers, apodisation)
	
	# The Q-function, expressed as 2*Q/pi.
	Q_reduced = 0.5*math.log(n_max[0]/n_min[0])
	
	# Generate rugate for each band, defined by the index of
	# refraction profile at the rejection wavelength.
	for j in range(nb_sublayers[0]):
		profiles[0][j] = n_0[0]*math.exp(Q_reduced\
		                                 *math.sin(4.0*math.pi*OT[0][j]/band_wvl+Phi)\
		                                 *W[0][j])
	
	if amplitude is None:
		normalize_amplitude = True
	else:
		normalize_amplitude = False
	
	OT_commun, profile_multiple_normalized = multiply_profiles(material, center_wvl, 1, [band_wvl], OT, profiles, nb_sublayers, centers, n_0, n_min_center, n_max_center, normalize_amplitude)
	
	# Add the layer.
	if replace:
		filter.remove_layer(position, side)
	filter.add_graded_layer(material_name, profile_multiple_normalized, OT_commun, position, side, OT = True, description = ["Rugate (nb periods and amplitude)", (material_name, band_wvl, nb_periods, amplitude, phase, apodisation)])



########################################################################
#                                                                      #
# rugate_by_R                                                          #
#                                                                      #
########################################################################
def rugate_by_R(filter, position, side, replace, material_name, band_wvl, R, bandwidth, phase, apodisation):
	"""Create a rugate layer with given reflection and bandwidth
	
	This function takes 10 arguments:
	  filter               the filter to which to add the rugate;
	  position             the position in the filter where to add the
	                       rugate;
	  side                 the side on which to add the rugate;
	  replace              a boolean indicating if the rugate sould
	                       replace the layer at the given position;
	  material_name        the name of the material to user;
	  band_wvl             the wavelength of the rugate;
	  R                    the reflection of the rugate;
	  bandwidth            the bandwidths of the rugate;
	  phase                the phase of the rugate;
	  apodisation          the apodisation of the rugate.
	and modifies the filter accordingly.
	
	For more details about rugates, see
	  Bovard, "Rugate Filter Theory: An Overview", Appl. Opt. vol .32,
	  1993, pp. 5427-5442."""
	
	material, center_wvl, step_spacing = get_filter_properties(filter, material_name)
	
	n_min_center, n_max_center, n_min, n_max, n_0 = index_ranges(material, 1, [band_wvl], center_wvl)
	
	sublayer_OT = select_sublayer_OT([band_wvl], n_min_center, n_max_center, step_spacing)
	
	# The continuous part of the Fourier transform of the apodisation
	# function, for every band. The Fourier transform of a rectangular
	# function is sqrt(2/pi)*sin(b*omega)/b*omega where b = x/2 is the
	# half width of the rectangular function. For omega = 0, the value
	# is sqrt(2/pi), that is 0.79788456080287. A supplementary 0.5
	# factor is also common to all apodisation function since we use
	# optical thickness and not half optical thickness: giving a
	# cummulative common factor of 0.5*0.79788456080287 = 0.39894228040143
	if apodisation == 0.0:
		W_0 = 0.39894228040143
	else:
		W_0 = 0.39894228040143*math.sinh(apodisation)/(apodisation*BesselI0(apodisation))
	
	# The Qbar value.
	Qbar = 0.5*math.log10((1.0+math.sqrt(R))/(1.0-math.sqrt(R)))
	
	# If no constraint is given on the bandwidth of the bands, the
	# optimal optical thickness (the one minimizing the total thickness)
	# is calculated.
	if bandwidth is None:
		sum_Qbar = Qbar/(abs(W_0)/band_wvl)
		x_0 = 2.0*sum_Qbar/(math.pi*math.log(n_max[0]/n_min[0]))
		x = x_0
	
	# Otherwise, the thickness of the profile for every band is selected
	# so that the appropriate bandwidth will be acheived. See Bovard,
	# "Fourier transform technique applied to quarterwave optical
	# coatings", Appl. Opt. V. 27 # 15, 1998, pp. 3062-3063 for the
	# calculation of delta_n for a specific bandwidth.
	else:
		delta_n = 2.0*n_0[0]*math.sin((0.25*math.pi)*(bandwidth/band_wvl))
		x = 2.0*Qbar/(math.pi*math.log((n_0[0]+0.5*delta_n)/(n_0[0]-0.5*delta_n))\
		              *abs(W_0)/band_wvl)
	
	# Round the optical thickness of all the bands to the
	# closest number of periods.
	nb_periods = int(round(2.0*x/band_wvl))
	
	# The phases.
	if phase is None:
		Phi = 0.0
	else:
		Phi = phase
	
	# When Phi is not used, try to make sure the rugate finishes with
	# an high index semi-period.
	if phase is None:
		# Integer number of periods.
		if nb_periods == int(nb_periods):
			# For an even number of periods, a pi shift is added.
			if (nb_periods/2.0) == round(nb_periods/2.0):
				Phi = math.pi
			# For an odd number of periods, no shift is added.
	
	x, OT, profiles, nb_sublayers, centers = prepare_profiles(1, [band_wvl], [nb_periods], sublayer_OT)
	
	W = apodisation_enveloppes(1, x, OT, nb_sublayers, apodisation)
	
	# Generate rugate defined by the index of refraction profile at the
	# rejection wavelength.
	for j in range(nb_sublayers[0]):
		profiles[0][j] = n_0[0]*math.exp((Qbar/(math.pi*x[0]*abs(W_0)/band_wvl))\
		                                 *math.sin(4.0*math.pi*OT[0][j]/band_wvl+Phi)\
		                                 *W[0][j])
	
	if bandwidth is None:
		normalize_amplitude = True
	else:
		normalize_amplitude = False
	
	OT_commun, profile_multiple_normalized = multiply_profiles(material, center_wvl, 1, [band_wvl], OT, profiles, nb_sublayers, centers, n_0, n_min_center, n_max_center, normalize_amplitude)
	
	# Add the layer.
	if replace:
		filter.remove_layer(position, side)
	filter.add_graded_layer(material_name, profile_multiple_normalized, OT_commun, position, side, OT = True, description = ["Rugate (R and bandwidth)", (material_name, band_wvl, R, bandwidth, phase, apodisation)])



########################################################################
#                                                                      #
# multiband_rugate                                                     #
#                                                                      #
########################################################################
def multiband_rugate(filter, position, side, replace, material_name, band_wvls, nb_periods, amplitudes, phase, apodisation):
	"""Create a multiband rugate layer with given number of periods and
	amplitudes
	
	This function takes 10 arguments:
	  filter               the filter to which to add the rugate;
	  position             the position in the filter where to add the
	                       rugate;
	  side                 the side on which to add the rugate;
	  replace              a boolean indicating if the rugate sould
	                       replace the layer at the given position;
	  material_name        the name of the material to user;
	  band_wvls            the wavelengths of the bands;
	  nb_periods           the number of periods of the bands;
	  amplitude            the amplitude of the bands;
	  phase                the phase of the bands;
	  apodisation          the apodisation of the rugate.
	and modifies the filter accordingly.
	
	For more details about rugates, see
	  Bovard, "Rugate Filter Theory: An Overview", Appl. Opt. vol .32,
	  1993, pp. 5427-5442.
	
	This function considers the dispersion of the material in the design
	using the method presented in
	  Daniel Poitras, Stephane Larouche, amd Ludvik Martinu, "Design and
	  plasma deposition of dispersion-corrected multiband rugate
	  filters", Appl. Opt., vol. 41, 2002, p. 5249--5255"""
	
	# The number of bands.
	nb_bands = len(band_wvls)
	
	material, center_wvl, step_spacing = get_filter_properties(filter, material_name)
	
	n_min_center, n_max_center, n_min, n_max, n_0 = index_ranges(material, nb_bands, band_wvls, center_wvl)
	
	sublayer_OT = select_sublayer_OT(band_wvls, n_min_center, n_max_center, step_spacing)
	
	# Adjustement of n_min and n_max to account for the amplitude.
	if amplitudes:
		for i in range(nb_bands):
			half_amplitude = 0.5*amplitudes[i]
			n_min[i] = n_0[i]-half_amplitude
			n_max[i] = n_0[i]+half_amplitude
	
	# The phases.
	if phase is None:
		Phi = [0.0]*nb_bands
	else:
		Phi = phase
	
	# When Phi is not used, try to make sure the rugate finishes with
	# an high index semi-period.
	if phase is None:
		for i in range(nb_bands):
			# Integer number of periods.
			if nb_periods[i] == round(nb_periods[i]):
				# For an even number of periods, a pi shift is added.
				if (nb_periods[i]/2.0) == round(nb_periods[i]/2.0):
					Phi[i] = math.pi
				# For an odd number of periods, no shift is added.
			# Half integer number of periods.
			elif 2.0*nb_periods[i] == round(2.0*nb_periods[i]):
				if (nb_periods[i] - 0.5)/2.0 == round((nb_periods[i] - 0.5)/2.0):
					Phi[i] = 0.5*math.pi
				else:
					Phi[i] = -0.5*math.pi
	
	x, OT, profiles, nb_sublayers, centers = prepare_profiles(nb_bands, band_wvls, nb_periods, sublayer_OT)
	
	W = apodisation_enveloppes(nb_bands, x, OT, nb_sublayers, apodisation)
	
	# The Q-functions, expressed as 2*Q/pi.
	Q_reduced = [0.5*math.log(n_max[i]/n_min[i]) for i in range(nb_bands)]
	
	# Generate rugate for each band, defined by the index of
	# refraction profile at the rejection wavelength.
	for i in range(nb_bands):
		for j in range(nb_sublayers[i]):
			profiles[i][j] = n_0[i]*math.exp(Q_reduced[i]\
			                                 *math.sin(4.0*math.pi*OT[i][j]/band_wvls[i]+Phi[i])\
			                                 *W[i][j])
	
	if amplitudes is None:
		normalize_amplitude = True
	else:
		normalize_amplitude = False
	
	OT_commun, profile_multiple_normalized = multiply_profiles(material, center_wvl, nb_bands, band_wvls, OT, profiles, nb_sublayers, centers, n_0, n_min_center, n_max_center, normalize_amplitude)
	
	# Add the layer.
	if replace:
		filter.remove_layer(position, side)
	filter.add_graded_layer(material_name, profile_multiple_normalized, OT_commun, position, side, OT = True, description = ["Multiband Rugate (nb periods and amplitude)", (material_name, band_wvls, nb_periods, amplitudes, phase, apodisation)])



########################################################################
#                                                                      #
# multiband_rugate_by_R                                                #
#                                                                      #
########################################################################
def multiband_rugate_by_R(filter, position, side, replace, material_name, band_wvls, R, bandwidth, phase, apodisation):
	"""Create a multiband rugate layer with given reflections and
	bandwidths
	
	This function takes 10 arguments:
	  filter               the filter to which to add the rugate;
	  position             the position in the filter where to add the
	                       rugate;
	  side                 the side on which to add the rugate;
	  replace              a boolean indicating if the rugate sould
	                       replace the layer at the given position;
	  material_name        the name of the material to user;
	  band_wvls            the wavelengths of the bands;
	  R                    the reflections of the bands;
	  bandwidth            the bandwidths of the bands;
	  phase                the phase of the bands;
	  apodisation          the apodisation of the rugate.
	and modifies the filter accordingly.
	
	For more details about rugates, see
	  Bovard, "Rugate Filter Theory: An Overview", Appl. Opt. vol .32,
	  1993, pp. 5427-5442.
	
	This function considers the dispersion of the material in the design
	using the method presented in
	  Daniel Poitras, Stephane Larouche, amd Ludvik Martinu, "Design and
	  plasma deposition of dispersion-corrected multiband rugate
	  filters", Appl. Opt., vol. 41, 2002, p. 5249--5255"""
	
	# The number of bands.
	nb_bands = len(band_wvls)
	
	material, center_wvl, step_spacing = get_filter_properties(filter, material_name)
	
	n_min_center, n_max_center, n_min, n_max, n_0 = index_ranges(material, nb_bands, band_wvls, center_wvl)
	
	sublayer_OT = select_sublayer_OT(band_wvls, n_min_center, n_max_center, step_spacing)
	
	# The continuous part of the Fourier transform of the apodisation
	# function, for every band. The Fourier transform of a rectangular
	# function is sqrt(2/pi)*sin(b*omega)/b*omega where b = x/2 is the
	# half width of the rectangular function. For omega = 0, the value
	# is sqrt(2/pi), that is 0.79788456080287. A supplementary 0.5
	# factor is also common to all apodisation function since we use
	# optical thickness and not half optical thickness: giving a
	# cummulative common factor of 0.5*0.79788456080287 = 0.39894228040143
	if apodisation == 0.0:
		W_0 = [0.39894228040143]*nb_bands
	else:
		# Kayser window.
		W_0 = [0.39894228040143*math.sinh(apodisation)/(apodisation*BesselI0(apodisation))]*nb_bands
	
	# The Qbar values.
	Qbar = [0.5*math.log10((1.0+math.sqrt(R[i]))/(1.0-math.sqrt(R[i]))) for i in range(nb_bands)]
	
	# If no constraint is given on the bandwidth of the bands, the
	# optimal optical thickness (the one minimizing the total thickness)
	# is calculated.
	if bandwidth is None:
		sum_Qbar = 0.0
		for i in range(nb_bands):
			sum_Qbar += Qbar[i]/(abs(W_0[i])/band_wvls[i])
		x_0 = 2.0*sum_Qbar/(math.pi*math.log(n_max[i]/n_min[i]))
		x = [x_0]*nb_bands
	
	# Otherwise, the thickness of the profile for every band is selected
	# so that the appropriate bandwidth will be acheived. See Bovard,
	# "Fourier transform technique applied to quarterwave optical
	# coatings", Appl. Opt. V. 27 # 15, 1998, pp. 3062-3063 for the
	# calculation of delta_n for a specific bandwidth.
	else:
		x = [0.0]*nb_bands
		for i in range(nb_bands):
			delta_n = 2.0*n_0[i]*math.sin((0.25*math.pi)*(bandwidth[i]/band_wvls[i]))
			x[i] = 2.0*Qbar[i]/(math.pi*math.log((n_0[i]+0.5*delta_n)/(n_0[i]-0.5*delta_n))\
			                    *abs(W_0[i])/band_wvls[i])
	
	# Round the optical thickness of all the bands to the
	# closest number of periods.
	nb_periods = [int(round(2.0*x[i]/band_wvls[i])) for i in range(nb_bands)]
	
	# The phases.
	if phase is None:
		Phi = [0.0]*nb_bands
	else:
		Phi = phase
	
	# When Phi is not used, try to make sure the rugate finishes with
	# an high index semi-period.
	if phase is None:
		for i in range(nb_bands):
			# Integer number of periods.
			if nb_periods[i] == int(nb_periods[i]):
				# For an even number of periods, a pi shift is added.
				if (nb_periods[i]/2.0) == round(nb_periods[i]/2.0):
					Phi[i] = math.pi
				# For an odd number of periods, no shift is added.
	
	x, OT, profiles, nb_sublayers, centers = prepare_profiles(nb_bands, band_wvls, nb_periods, sublayer_OT)
	
	W = apodisation_enveloppes(nb_bands, x, OT, nb_sublayers, apodisation)
	
	# Generate rugate for each band, defined by the index of
	# refraction profile at the rejection wavelength.
	for i in range(nb_bands):
		for j in range(nb_sublayers[i]):
			profiles[i][j] = n_0[i]*math.exp((Qbar[i]/(math.pi*x[i]*abs(W_0[i])/band_wvls[i]))\
			                                 *math.sin(4.0*math.pi*OT[i][j]/band_wvls[i]+Phi[i])\
			                                 *W[i][j])
	
	if bandwidth is None:
		normalize_amplitude = True
	else:
		normalize_amplitude = False
	
	OT_commun, profile_multiple_normalized = multiply_profiles(material, center_wvl, nb_bands, band_wvls, OT, profiles, nb_sublayers, centers, n_0, n_min_center, n_max_center, normalize_amplitude)
	
	# Add the layer.
	if replace:
		filter.remove_layer(position, side)
	filter.add_graded_layer(material_name, profile_multiple_normalized, OT_commun, position, side, OT = True, description = ["Multiband Rugate (R and bandwidth)", (material_name, band_wvls, R, bandwidth, phase, apodisation)])



########################################################################
#                                                                      #
# get_filter_properties                                                #
#                                                                      #
########################################################################
def get_filter_properties(filter, material_name):
	"""Get the properties of a filter and material
	
	This function takes 2 arguments:
	  filter               the filter;
	  material_name        the name of the material;
	and returns
	  material             the material;
	  center_wvl           the center wavelength;
	  step_spacing         the step spacing."""
	
	# Get the material from the filter.
	material_nb = filter.get_material_nb(material_name)
	material = filter.get_material(material_nb)
	
	# Get the properties of the filter.
	center_wvl = filter.get_center_wavelength()
	step_spacing = filter.get_step_spacing()
	
	# If the step spacing is defined by the deposition, find the smallest
	# step spacing.
	if step_spacing == DEPOSITION_STEP_SPACING:
		steps = filter.get_material_index(material_nb)
		step_spacing = steps[1]-steps[0]
		for i_step in range(2, len(steps)):
			step_spacing = min(step_spacing, steps[i_step] - steps[i_step-1])
	
	return material, center_wvl, step_spacing



########################################################################
#                                                                      #
# select_sublayer_OT                                                   #
#                                                                      #
########################################################################
def select_sublayer_OT(band_wvls, n_min, n_max, step_spacing):
	"""Select the sublayer optical thickness
	
	Select the sublayer optical thickness to properly represent the
	rugate profile according to the properties of the rugate and the
	rugate.
	
	This function takes 3 arguments:
	  band_wvls            the band wavelengths;
	  n_min, n_max         the minimal and maximal indices at those
	                       wavelengths;
	  step_spacing         the step spacing used in the filter;
	and returns the most appropriate sublayer optical thickness."""
	
	# Choose the worst case, that is a filter covering all the index
	# range and having the smallest period.
	amplitude = n_max - n_min
	shortest_quarter_wave = 0.25*min(band_wvls)
	
	# In one quarter wave, the profile passes by all the steps in its
	# amplitude. We generate 4 times more sublayers to be sure to don't
	# commit too much approximation errors.
	nb_steps_in_full_amplitude = amplitude/step_spacing
	sublayer_OT = 0.25*shortest_quarter_wave/nb_steps_in_full_amplitude
	
	return sublayer_OT



########################################################################
#                                                                      #
# index_ranges                                                         #
#                                                                      #
########################################################################
def index_ranges(material, nb_bands, band_wvls, center_wvl):
	"""Get the available index ranges at the band wavelengths
	
	This function takes 4 arguments:
	  material             the material;
	  nb_bands             the number of bands;
	  band_wvls            the band wavelengths;
	  center_wvl           the center wavelength;
	and returns:
	  n_min_center         the minimal index at the center wavelength;
	  n_max_center         the maximal index at the center wavelength;
	  n_min                a list of the minimal indices at the band
	                       wavelengths
	  n_max                a list of the maximal indices at the band
	                       wavelengths
	  n_0                  a list of the center indices at the band
	                       wavelengths."""
	
	# The maximum, minimum and mean index for the center wavelength and every band.
	n_min_center, n_max_center = material.get_index_range(center_wvl)
	n_min = [0.0]*nb_bands
	n_max = [0.0]*nb_bands
	n_0 = [0.0]*nb_bands
	for i in range(nb_bands):
		n_min_i, n_max_i = material.get_index_range(band_wvls[i])
		n_min[i] = n_min_i
		n_max[i] = n_max_i
		
		# Since the profile in the exponential of a sinus, the use of the
		# geometrical mean reduce the need the rescale the profile.
		n_0[i] = math.sqrt(n_min_i*n_max_i)
	
	return n_min_center, n_max_center, n_min, n_max, n_0



########################################################################
#                                                                      #
# prepare_profiles                                                     #
#                                                                      #
########################################################################
def prepare_profiles(nb_bands, band_wvls, nb_periods, sublayer_OT):
	"""Prepare structures for the index profiles of the bands
	
	This function takes 4 arguments:
	  nb_bands             the number of bands;
	  band_wvls            the band wavelengths;
	  nb_periods           the number of periods of the bands;
	  sublayer_OT          the sublayer optical thickness;
	and returns:
	  x                    the optical thickness of the bands;
	  OT                   lists of all the positions (in OT) of
	                       sublayers in the index profiles;
	  profiles             lists ready to receive the index profiles;
	  nb_sublayers         the number of sublayers in the profiles;
	  centers              the positions of the centers in the profiles."""
	
	# Calculate the OT for all bands according to the number of periods.
	x = [0.5*nb_periods[i]*band_wvls[i] for i in range(nb_bands)]
	
	# Sublayers in optical thickness for each peak. The OT are 0 at the
	# center.
	centers = [int(math.ceil(0.5*x[i]/sublayer_OT)) for i in range(nb_bands)]
	nb_sublayers = [2*centers[i]+1 for i in range(nb_bands)]
	
	OT = [[]]*nb_bands
	for i in range(nb_bands):
		OT[i] = [0.0]*nb_sublayers[i]
		for j in range(1, centers[i]):
			abs_OT = j*sublayer_OT
			OT[i][centers[i]+j] = abs_OT
			OT[i][centers[i]-j] = -abs_OT
		# The first and last elements are set the +/- half ot the total OT.
		# This way, the total OT is exactly what is expected.
		OT[i][0] = -0.5*x[i]
		OT[i][-1] = 0.5*x[i]
	
	profiles = [[0.0]*nb_sublayers[i] for i in range(nb_bands)]
	
	return x, OT, profiles, nb_sublayers, centers



########################################################################
#                                                                      #
# apodisation_enveloppes                                               #
#                                                                      #
########################################################################
def apodisation_enveloppes(nb_bands, x, OT, nb_sublayers, apodisation):
	"""Calculate the apodisation enveloppes for all bands
	
	This function takes 5 arguments:
	  nb_bands             the number of bands;
	  x                    the optical thickness of the bands;
	  OT                   lists of all the positions (in OT) of
	                       sublayers in the index profiles;
	  nb_sublayers         the number of sublayers in the profiles;
	  apodisation          the value of the apodisation;
	and returns:
	  W                    the apodisation enveloppes of all the bands."""
	
	# Apodisation, as described in Bovard's article.
	W = [[]]*nb_bands
	for i in range(nb_bands):
		W[i] = [1.0]*nb_sublayers[i]
		if apodisation != 0:
			denominateur = BesselI0(apodisation)
			for j in range(nb_sublayers[i]):
				x_prime = OT[i][j]/x[i]
				W[i][j] = BesselI0(apodisation*math.sqrt(1.0-4.0*x_prime*x_prime))/denominateur
	
	return W



########################################################################
#                                                                      #
# multiply_profiles                                                    #
#                                                                      #
########################################################################
def multiply_profiles(material, center_wvl, nb_bands, band_wvls, OT, profiles, nb_sublayers, centers, n_0, n_min_center, n_max_center, normalize_amplitude):
	"""Convert all the band profiles to the center wavelength and multiply
	them
	
	This function takes 5 arguments:
	  material             the material;
	  center_wvl           the center wavelength
	  nb_bands             the number of bands;
	  OT                   lists of all the position (in OT) of sublayers
	                       in the index profiles;
	  profiles             the index profiles of the bands;
	  nb_sublayers         the number of sublayers in the profiles;
	  centers              the positions of the centers in the profiles;
	  n_0                  a list of the center indices at the band
	                       wavelengths;
	  n_min_center         the minimal index at the center wavelength;
	  n_max_center         the maximal index at the center wavelength;
	  normalize_amplitude  a boolean indicating the the amplitudes should
	                       be normalized to fill the whole available
	                       index ranges;
	and returns:
	  OT_commun                     lists of the positions (in OT) of
	                                sublayers in the index profile;
    profile_multiple_normalized   the index profile of the multiband
                                  rugate at the center wavelength."""
	
	OT_center_wvl = [None]*nb_bands
	
	for i in range(nb_bands):
		# If the band is already at the center wavelength, do nothing.
		if band_wvls[i] == center_wvl:
			OT_center_wvl[i] = OT[i]
		
		# Otherwise, change the index and adjust the OT to keep a constant
		# physical thickness.
		else:
			OT_center_wvl[i] = [0.0]*nb_sublayers[i]
			
			# Express the OT in unitless value and as the sublayer thickness
			# of every sublayers.
			for j in range(centers[i]+1, nb_sublayers[i]):
				OT_center_wvl[i][j] = (OT[i][j]-OT[i][j-1])/profiles[i][j]
			for j in range(centers[i]-1, 0-1, -1):
				OT_center_wvl[i][j] = (OT[i][j+1]-OT[i][j])/profiles[i][j]
			
			# Express the index profiles at the center wavelength
			# according to dispersion.
			material.change_index_profile_wavelength(profiles[i], band_wvls[i], center_wvl)
			
			# Express the OT at the new wavelength.
			for j in range(centers[i]+1, nb_sublayers[i]):
				OT_center_wvl[i][j] = OT_center_wvl[i][j-1] + OT_center_wvl[i][j]*profiles[i][j]
			for j in range(centers[i]-1, 0-1, -1):
				OT_center_wvl[i][j] = OT_center_wvl[i][j+1] - OT_center_wvl[i][j]*profiles[i][j]
	
	# Choose the thickest profile as the profile for the multiple band
	# filter (the thickest index profile will start at the more negative
	# optical thickness value).
	thickest_profile = 0
	for i in range(1, nb_bands):
		if OT_center_wvl[i][0] < OT_center_wvl[thickest_profile][0]:
			thickest_profile = i
	OT_commun = OT_center_wvl[thickest_profile]
	nb_sublayers_commun = nb_sublayers[thickest_profile]
	
	# Expressing all the profiles in term of the same optical thickness.
	profiles_commun_center_wvl = [None]*nb_bands
	for i in range(nb_bands):
		if i == thickest_profile:
			profiles_commun_center_wvl[i] = profiles[i]
		else:
			profiles_commun_center_wvl[i] = interpolation.spline(OT_center_wvl[i], profiles[i], OT_commun)
	
	# Transform the mean index for every wavelength to the center wavelength.
	# It should be close to the mean index at the center wavelength, but not
	# necessaraly identical.
	n_0_center_wvl = [material.change_index_wavelength(n_0[i_band], band_wvls[i_band], center_wvl) for i_band in range(nb_bands)]
	
	# Pad the shorter index profiles (and remove the crap generated by
	# extrapolation by the spline).
	for i in range(nb_bands):
		if i != thickest_profile:
			j = 0
			while OT_commun[j] < OT_center_wvl[i][0]:
				profiles_commun_center_wvl[i][j] = n_0_center_wvl[i]
				j += 1
			j = len(OT_commun)-1
			while OT_commun[j] > OT_center_wvl[i][-1]:
				profiles_commun_center_wvl[i][j] = n_0_center_wvl[i]
				j -= 1
	
	# Multiply the index profiles.
	profile_multiple = [1.0]*nb_sublayers_commun
	for j in range(nb_sublayers_commun):
		for i in range(nb_bands):
			profile_multiple[j] *= profiles_commun_center_wvl[i][j]
	
	# Normalize the index profile of the multiband to fit inside the
	# range of available indices according the the method described
	# in the Poitras and al. article. The exponent can take a value
	# different that one only if the amplitude is normalized. The
	# multiplicative factor isn't calculated as in the article so
	# that the profile always get centered around n_0 even in the
	# cases where the exponent is not 1.0.
	profile_max = max(profile_multiple)
	profile_min = min(profile_multiple)
	if normalize_amplitude:
		exponent = math.log(n_max_center/n_min_center)/math.log(profile_max/profile_min)
	else:
		exponent = 1.0
	multiplication = (n_min_center+n_max_center)/(profile_min**exponent+profile_max**exponent)
	profile_multiple_normalized = [multiplication*profile_multiple[j]**exponent for j in range(nb_sublayers_commun)]
	
	# Shift the OT to make it begin at 0.
	OT_min = OT_commun[0]
	for j in range(nb_sublayers_commun):
		OT_commun[j] -= OT_min
	
	return OT_commun, profile_multiple_normalized



########################################################################
#                                                                      #
# rugate_dialog                                                        #
#                                                                      #
########################################################################
class rugate_dialog(GUI_layer_dialogs.layer_dialog):
	"""A dialog to design a rugate layer with given number of periods and
	amplitude"""
	
	title = "Rugate"
	
	# A few constant definitions that permits the reuse of this class
	# for the rugate by R dialog box.
	thickness_title = "Nb periods"
	amplitude_title = "Amplitude"
	amplitude_units = ""
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content to the dialog"""
		
		self.add_layer_definition()
		if self.description is None:
			self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the rugate definition to the dialog"""
		
		layer_static_box = wx.StaticBox(self, -1, "Layer")
		
		layer_box_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the material.
		self.create_material_box(MATERIAL_MIXTURE)
		layer_box_sizer_1.Add(wx.StaticText(self, -1, "Material:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_1.Add(self.material_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the wavelength.
		self.wavelength_box_ID = wx.NewId()
		self.wavelength_box = wx.TextCtrl(self, self.wavelength_box_ID, "", validator = float_validator(1.0, None))
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "Wavelength:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_2.Add(self.wavelength_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "nm"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.wavelength_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		layer_box_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the nb_periods.
		self.nb_periods_box_ID = wx.NewId()
		self.nb_periods_box = wx.TextCtrl(self, self.nb_periods_box_ID, "", validator = float_validator(0.25, None))
		layer_box_sizer_3.Add(wx.StaticText(self, -1, "%s:" % self.thickness_title), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_3.Add(self.nb_periods_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.nb_periods_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		layer_box_sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the apodisation.
		self.apodisation_box_ID = wx.NewId()
		self.apodisation_box = wx.TextCtrl(self, self.apodisation_box_ID, "", validator = float_validator(0.0, None))
		layer_box_sizer_4.Add(wx.StaticText(self, -1, "Apodisation:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_4.Add(self.apodisation_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		self.apodisation_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		layer_box_sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Radio buttons and TextCtrl for the control of the amplitude of
		# the index profile of the band.
		self.max_amplitude_button_ID = wx.NewId()
		self.amplitude_button_ID = wx.NewId()
		self.amplitude_box_ID = wx.NewId()
		self.max_amplitude_button = wx.RadioButton(self, self.max_amplitude_button_ID, "maximum", style = wx.RB_GROUP)
		self.amplitude_button = wx.RadioButton(self, self.amplitude_button_ID, "")
		self.amplitude_box = wx.TextCtrl(self, self.amplitude_box_ID, "", validator = float_validator(0.0, None, self.amplitude_button.GetValue))
		self.Bind(wx.EVT_RADIOBUTTON, self.on_amplitude_button, self.max_amplitude_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_amplitude_button, self.amplitude_button)
		self.amplitude_box.Bind(wx.EVT_TEXT, self.on_amplitude_box)
		self.amplitude_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		layer_box_sizer_5.Add(wx.StaticText(self, -1, "%s:" % self.amplitude_title), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_5.Add(self.max_amplitude_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_5.Add(self.amplitude_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_5.Add(self.amplitude_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_5.Add(wx.StaticText(self, -1, "%s" % self.amplitude_units), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Radio buttons and TextCtrl for the control of the phase of
		# the index profile of the band.
		self.auto_phase_button_ID = wx.NewId()
		self.phase_button_ID = wx.NewId()
		self.phase_box_ID = wx.NewId()
		self.auto_phase_button = wx.RadioButton(self, self.auto_phase_button_ID, "automatic", style = wx.RB_GROUP)
		self.phase_button = wx.RadioButton(self, self.phase_button_ID, "")
		self.phase_box = wx.TextCtrl(self, self.phase_box_ID, "", validator = float_validator(None, None, self.phase_button.GetValue))
		self.Bind(wx.EVT_RADIOBUTTON, self.on_phase_button, self.auto_phase_button)
		self.Bind(wx.EVT_RADIOBUTTON, self.on_phase_button, self.phase_button)
		self.phase_box.Bind(wx.EVT_TEXT, self.on_phase_box)
		self.phase_box.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
		
		layer_box_sizer_6.Add(wx.StaticText(self, -1, "Phase:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_6.Add(self.auto_phase_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_6.Add(self.phase_button, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_6.Add(self.phase_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		layer_box_sizer_6.Add(wx.StaticText(self, -1, "* pi"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Arrange in the static box.
		layer_box_sizer = wx.StaticBoxSizer(layer_static_box, wx.VERTICAL)
		layer_box_sizer.Add(layer_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_3, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_4, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_5, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_6, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		
		self.main_sizer.Add(layer_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# If a self.description is provided, it is used to set the the
		# values in the boxes. Otherwise, default values are used.
		if self.description:
			material, wavelength, nb_periods, amplitude, Phi, apodisation = self.description
			self.material_box.SetValue(material)
			self.wavelength_box.SetValue("%s" % wavelength)
			self.nb_periods_box.SetValue("%s" % nb_periods)
			self.apodisation_box.SetValue("%s" % apodisation)
			if amplitude is None:
				self.max_amplitude_button.SetValue(True)
			else:
				self.amplitude_button.SetValue(True)
				self.amplitude_box.SetValue("%s" % amplitude)
			if Phi is None:
				self.auto_phase_button.SetValue(True)
			else:
				self.phase_button.SetValue(True)
				self.phase_box.SetValue("%s" % (Phi/math.pi))
		else:
			self.wavelength_box.SetValue("%s" % self.filter.get_center_wavelength())
			self.nb_periods_box.SetValue("")
			self.apodisation_box.SetValue("0.0")
			self.max_amplitude_button.SetValue(True)
			self.auto_phase_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# on_amplitude_button                                                #
	#                                                                    #
	######################################################################
	def on_amplitude_button(self, event):
		"""Adjust the dialog when an amplitude button is choosen"""
		
		# When the max amplitude button is choosen, clear the amplitude
		# box.
		if self.max_amplitude_button.GetValue():
			self.amplitude_box.Clear()
	
	
	######################################################################
	#                                                                    #
	# on_amplitude_box                                                   #
	#                                                                    #
	######################################################################
	def on_amplitude_box(self, event):
		"""Adjust the dialog when a text is entered in the amplitude box"""
		
		# When a value is entered in the amplitude box, automatically
		# select the amplitude button.
		if self.amplitude_box.GetValue():
			self.amplitude_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# on_phase_button                                                    #
	#                                                                    #
	######################################################################
	def on_phase_button(self, event):
		"""Adjust the dialog when a phase button is choosen"""
		
		# When the automatic phase button is choosen, clear the phase box.
		if self.auto_phase_button.GetValue():
			self.phase_box.Clear()
	
	
	######################################################################
	#                                                                    #
	# on_phase_box                                                       #
	#                                                                    #
	######################################################################
	def on_phase_box(self, event):
		"""Adjust the dialog text is entered in the phase box"""
		
		# When a value is entered in the phase box, automatically select
		# the phase button.
		if self.phase_box.GetValue():
			self.phase_button.SetValue(True)
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters of the rugate defined in the dialog"""
		
		material_name = self.get_material_name()
		wavelength = float(self.wavelength_box.GetValue())
		apodisation = float(self.apodisation_box.GetValue())
		nb_periods = float(self.nb_periods_box.GetValue())
		if self.amplitude_button.GetValue():
			amplitude = float(self.amplitude_box.GetValue())
		else:
			amplitude = None
		if self.phase_button.GetValue():
			Phi = math.pi*float(self.phase_box.GetValue())
		else:
			Phi = None
		
		return material_name, wavelength, nb_periods, amplitude, Phi, apodisation



########################################################################
#                                                                      #
# rugate_by_R_dialog                                                   #
#                                                                      #
########################################################################
class rugate_by_R_dialog(rugate_dialog):
	"""A dialog to design a rugate layer with given reflection and
	bandwidth"""
	
	title = "Rugate (R and bandwidth)"
	
	# A few constant definitions that permits the reuse of this class
	# for the rugate by R dialog box.
	thickness_title = "R"
	amplitude_title = "Bandwidth"
	amplitude_units = "nm"
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the rugate definition to the dialog"""
		
		rugate_dialog.add_layer_definition(self)
		
		self.nb_periods_box.SetValidator(validator = float_validator(0.0, 1.0-sqrt_epsilon))
		self.amplitude_box.SetValidator(validator = float_validator(1.0, None, self.amplitude_button.GetValue))



########################################################################
#                                                                      #
# multiband_rugate_dialog                                              #
#                                                                      #
########################################################################
class multiband_rugate_dialog(GUI_layer_dialogs.layer_dialog):
	"""A dialog to design a multiband rugate layer with given numbers of
	periods and and amplitudes"""
	
	title = "Multiband Rugate"
	
	# A few constant definitions that permits the reuse of this class
	# for the multiband rugate by R dialog box. In this case, the
	# amplitude of the bands can be defined and the nb of bands for every
	# band.
	amplitude_button_title = "Specify amplitude"
	amplitude_column_title = "Amplitude"
	thickness_column_title = "Nb periods"
	phase_column_title = "Phase (*pi)"
	
	
	######################################################################
	#                                                                    #
	# add_content                                                        #
	#                                                                    #
	######################################################################
	def add_content(self):
		"""Add the content to the dialog"""
		
		self.add_layer_definition()
		if self.description is None:
			self.add_position_choice()
	
	
	######################################################################
	#                                                                    #
	# add_layer_definition                                               #
	#                                                                    #
	######################################################################
	def add_layer_definition(self):
		"""Add the rugate definition to the dialog"""
		
		layer_static_box = wx.StaticBox(self, -1, "Layer")
		
		layer_box_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the material.
		self.create_material_box(MATERIAL_MIXTURE)
		layer_box_sizer_1.Add(wx.StaticText(self, -1, "Material:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_1.Add(self.material_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Adding the text box for specifying the number of bands.
		self.nb_bands_box_ID = wx.NewId()
		self.nb_bands_box = wx.TextCtrl(self, self.nb_bands_box_ID, "", style = wx.TE_PROCESS_ENTER, validator = int_validator(1, None))
		self.nb_bands_box.Bind(wx.EVT_TEXT_ENTER, self.on_nb_bands)
		self.nb_bands_box.Bind(wx.EVT_KILL_FOCUS, self.on_nb_bands)
		
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "Nb bands:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_2.Add(self.nb_bands_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Adding the text box for specifying the apodisation.
		self.apodisation_box_ID = wx.NewId()
		self.apodisation_box = wx.TextCtrl(self, self.apodisation_box_ID, "", validator = float_validator(0.0, None))
		
		layer_box_sizer_2.Add(wx.StaticText(self, -1, "Apodisation:"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 20)
		layer_box_sizer_2.Add(self.apodisation_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		layer_box_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
		
		# Check box for the control of the amplitude of the index profile of
		# the bands.
		self.amplitude_box_ID = wx.NewId()
		self.amplitude_box = wx.CheckBox(self, self.amplitude_box_ID, self.amplitude_button_title)
		self.Bind(wx.EVT_CHECKBOX, self.on_amplitude_box, self.amplitude_box)
		
		# Check box for the control of the phase of the index profile of
		# the bands.
		self.phase_box_ID = wx.NewId()
		self.phase_box = wx.CheckBox(self, self.phase_box_ID, "Specify phase")
		self.Bind(wx.EVT_CHECKBOX, self.on_phase_box, self.phase_box)
		
		layer_box_sizer_3.Add(self.amplitude_box, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		layer_box_sizer_3.Add(self.phase_box, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
		
		# Add a table to specify the wavelengths and reflection of the
		# bands.
		self.properties_grid = wx.grid.Grid(self, -1, size = (450, 150), style = wx.SUNKEN_BORDER)#wx.VSCROLL|wx.HSCROLL|
		self.properties_grid.CreateGrid(0, 2)
		self.properties_grid.SetColSize(0, 80)
		self.properties_grid.SetColLabelValue(0, "Wavelength")
		self.properties_grid.SetColSize(1, 80)
		self.properties_grid.SetColLabelValue(1, self.thickness_column_title)
		
		# Disable resizing of the grid.
		self.properties_grid.DisableDragColSize()
		self.properties_grid.DisableDragGridSize()
		self.properties_grid.DisableDragRowSize()
		
		self.properties_grid.SetValidator(rugate_grid_validator())
		
		# Arrange in the static box.
		layer_box_sizer = wx.StaticBoxSizer(layer_static_box, wx.VERTICAL)
		layer_box_sizer.Add(layer_box_sizer_1, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(layer_box_sizer_3, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 5)
		layer_box_sizer.Add(self.properties_grid, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		self.main_sizer.Add(layer_box_sizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT|wx.RIGHT, 10)
		
		# If a self.description is provided, it is used to set the the
		# values in the boxes. Otherwise, default values are used.
		if self.description is None:
			self.nb_bands_box.SetValue("1")
			self.apodisation_box.SetValue("0.0")
			self.amplitude_box.SetValue(False)
			self.phase_box.SetValue(False)
			self.properties_grid.AppendRows(1)
		else:
			material, wavelengths, thickness_criteria_values, amplitude_criteria_values, Phi, apodisation = self.description
			self.material_box.SetValue(material)
			nb_bands = len(wavelengths)
			self.nb_bands_box.SetValue("%s" % nb_bands)
			self.apodisation_box.SetValue("%s" % apodisation)
			self.properties_grid.AppendRows(nb_bands)
			for i in range(nb_bands):
				self.properties_grid.SetCellValue(i, 0, ("%s" % wavelengths[i]))
				self.properties_grid.SetCellValue(i, 1, ("%s" % thickness_criteria_values[i]))
			if amplitude_criteria_values is None:
				self.amplitude_box.SetValue(False)
			else:
				self.amplitude_box.SetValue(True)
				nb_cols = self.properties_grid.GetNumberCols()
				self.properties_grid.AppendCols(1)
				self.properties_grid.SetColLabelValue(nb_cols, self.amplitude_column_title)
				self.properties_grid.SetColSize(nb_cols, 80)
				for i in range(nb_bands):
					self.properties_grid.SetCellValue(i, nb_cols, ("%s" % amplitude_criteria_values[i]))
			if Phi is None:
				self.phase_box.SetValue(False)
			else:
				self.phase_box.SetValue(True)
				nb_cols = self.properties_grid.GetNumberCols()
				self.properties_grid.AppendCols(1)
				self.properties_grid.SetColLabelValue(nb_cols, self.phase_column_title)
				self.properties_grid.SetColSize(nb_cols, 80)
				for i in range(nb_bands):
					self.properties_grid.SetCellValue(i, nb_cols, ("%s" % (Phi[i]/math.pi)))
	
	
	######################################################################
	#                                                                    #
	# on_nb_bands                                                        #
	#                                                                    #
	######################################################################
	def on_nb_bands(self, event):
		"""Adjust the dialog when the number of bands is changed"""
		
		nb_bands = int(self.nb_bands_box.GetValue())
		nb_rows = self.properties_grid.GetNumberRows()
		
		if nb_bands > nb_rows:
			self.properties_grid.AppendRows(nb_bands-nb_rows)
		elif nb_bands < nb_rows:
			self.properties_grid.DeleteRows(nb_bands, nb_rows-nb_bands)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_amplitude_box                                                   #
	#                                                                    #
	######################################################################
	def on_amplitude_box(self, event):
		"""Adjust the dialog when the amplitude box is selected"""
		
		# If the checkbox is selected, a column for specifying the amplitude
		# needs to be added to the properties grid. If the checkbox is not
		# selected, the column is removed. The first step is to find the
		# amplitude column, the second step is to remove, or add it, or do
		# nothing if the grid is already in the right state.
		nb_cols = self.properties_grid.GetNumberCols()
		for col in range(2, nb_cols):
			if self.properties_grid.GetColLabelValue(col) == self.amplitude_column_title:
				break
		else:
			col = None
		
		if self.amplitude_box.GetValue() and col is None:
			self.properties_grid.AppendCols(1)
			self.properties_grid.SetColLabelValue(nb_cols, self.amplitude_column_title)
			self.properties_grid.SetColSize(nb_cols, 80)
		elif not self.amplitude_box.GetValue() and col is not None:
			self.properties_grid.DeleteCols(col, 1)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# on_phase_box                                                       #
	#                                                                    #
	######################################################################
	def on_phase_box(self, event):
		"""Adjust the dialog when the phase box is selected"""
		
		# If the checkbox is selected, a column for specifying the phase
		# needs to be added to the properties grid. If the checkbox is not
		# selected, the column is removed. The first step is to find the
		# phase column, the second step is to remove, or add it, or do
		# nothing if the grid is already in the right state.
		nb_cols = self.properties_grid.GetNumberCols()
		for col in range(2, nb_cols):
			if self.properties_grid.GetColLabelValue(col) == self.phase_column_title:
				break
		else:
			col = None
		
		if self.phase_box.GetValue() and col is None:
			self.properties_grid.AppendCols(1)
			self.properties_grid.SetColLabelValue(nb_cols, self.phase_column_title)
			self.properties_grid.SetColSize(nb_cols, 80)
		elif not self.phase_box.GetValue() and col is not None:
			self.properties_grid.DeleteCols(col, 1)
		
		event.Skip()
	
	
	######################################################################
	#                                                                    #
	# get_parameters                                                     #
	#                                                                    #
	######################################################################
	def get_parameters(self):
		"""Get the parameters of the rugate defined in the dialog"""
		
		material_name = self.get_material_name()
		
		nb_rows = self.properties_grid.GetNumberRows()
		nb_cols = self.properties_grid.GetNumberCols()
		
		wavelengths = [float(self.properties_grid.GetCellValue(i, 0)) for i in range(nb_rows)]
		thickness_criteria_values = [float(self.properties_grid.GetCellValue(i, 1)) for i in range(nb_rows)]
		apodisation = float(self.apodisation_box.GetValue())
		if self.amplitude_box.GetValue():
			for col in range(2, nb_cols):
				if self.properties_grid.GetColLabelValue(col) == self.amplitude_column_title:
					break
			amplitude_criteria_values = [float(self.properties_grid.GetCellValue(i, col)) for i in range(nb_rows)]
		else:
			amplitude_criteria_values = None
		if self.phase_box.GetValue():
			for col in range(2, nb_cols):
				if self.properties_grid.GetColLabelValue(col) == self.phase_column_title:
					break
			Phi = [math.pi*float(self.properties_grid.GetCellValue(i, col)) for i in range(nb_rows)]
		else:
			Phi = None
		
		return material_name, wavelengths, thickness_criteria_values, amplitude_criteria_values, Phi, apodisation



########################################################################
#                                                                      #
# multiband_rugate_by_R_dialog                                         #
#                                                                      #
########################################################################
class multiband_rugate_by_R_dialog(multiband_rugate_dialog):
	"""A dialog to design a multiband rugate layer with given reflections
	and bandwidths"""
	
	title = "Multiband Rugate by R"
	
	# A few constant definitions to reuse the multiband_rugate_dialog
	# class.
	amplitude_button_title = "Specify bandwidth"
	amplitude_column_title = "Bandwidth"
	thickness_column_title = "R"



########################################################################
#                                                                      #
# rugate_grid_validator                                                #
#                                                                      #
########################################################################
class rugate_grid_validator(wx.PyValidator):
	"""Validate the content of the grid in the multiband rugate dialog
	box."""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize the validator"""
		
		wx.PyValidator.__init__(self)
	
	
	######################################################################
	#                                                                    #
	# Clone                                                              #
	#                                                                    #
	######################################################################
	def Clone(self):
		"""Return a clone of the validator"""
		
		return rugate_grid_validator()
	
	
	######################################################################
	#                                                                    #
	# TransferToWindow                                                   #
	#                                                                    #
	######################################################################
	def TransferToWindow(self):
		"""Indicate that the transfer of data to the window went well"""
		
		return True
	
	
	######################################################################
	#                                                                    #
	# TransferFromWindow                                                 #
	#                                                                    #
	######################################################################
	def TransferFromWindow(self):
		"""Indicate that the transfer of data from the window went well"""
		
		return True
	
	
	######################################################################
	#                                                                    #
	# Validate                                                           #
	#                                                                    #
	######################################################################
	def Validate(self, parent):
		"""Validate the content of the grid."""
		
		error = False
		
		window = self.GetWindow()
		
		nb_rows = window.GetNumberRows()
		nb_cols = window.GetNumberCols()
		
		for row in range(nb_rows):
			try:
				wavelength = float(window.GetCellValue(row, 0))
				if wavelength <= 0.0:
					raise ValueError
			except ValueError:
				error = True
				window.SelectBlock(row, 0, row, 0, True)
		
		if isinstance(parent, multiband_rugate_by_R_dialog):
			for row in range(nb_rows):
				try:
					R = float(window.GetCellValue(row, 1))
					if R <= 0.0 or R > 1.0-sqrt_epsilon:
						raise ValueError
				except ValueError:
					error = True
					window.SelectBlock(row, 1, row, 1, True)
		
		else:
			for row in range(nb_rows):
				try:
					nb_periods = float(window.GetCellValue(row, 1))
					if nb_periods <= 0.25:
						raise ValueError
				except ValueError:
					error = True
					window.SelectBlock(row, 1, row, 1, True)
		
		for col in range(2, nb_cols):
			
			# The column that specifies the amplitude of the index profile.
			if window.GetColLabelValue(col) == parent.amplitude_column_title:
				
				if isinstance(parent, multiband_rugate_by_R_dialog):
					for row in range(nb_rows):
						try:
							bandwith = float(window.GetCellValue(row, col))
							if bandwith < 1.0:
								raise ValueError
						except ValueError:
							error = True
							window.SelectBlock(row, col, row, col, True)
				
				else:
					for row in range(nb_rows):
						try:
							amplitude = float(window.GetCellValue(row, col))
							if amplitude < 0.0:
								raise ValueError
						except ValueError:
							error = True
							window.SelectBlock(row, col, row, col, True)
			
			# The column that specifies the phase of the index profile.
			if window.GetColLabelValue(col) == parent.phase_column_title:
				
				for row in range(nb_rows):
					try:
						phi = float(window.GetCellValue(row, col))
					except ValueError:
						error = True
						window.SelectBlock(row, col, row, col, True)
		
		if error:
			if not wx.Validator_IsSilent():
				wx.Bell()
			window.SetFocus()
			window.Refresh()
			return False
		
		return True
