# graded.py
# 
# Functions to help with the manipulation of graded-index layers.
# 
# Copyright (c) 2000-2003,2005-2010,2012 Stephane Larouche.
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

import math

from definitions import *
from moremath import interpolation
from moremath import limits

# If log1p is implemented (Python 2.6 and later), use it, otherwise
# implement it using log.
try:
	from math import log1p
except ImportError:
	def log1p(x): return math.log(1.0 + x)



epsilon = limits.epsilon
sqrt_epsilon = math.sqrt(epsilon)



########################################################################
#                                                                      #
# grading_error                                                        #
#                                                                      #
########################################################################
class grading_error(Exception):
	"""Exception class for errors in the manipulation of graded-index
	layers"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Grading error: %s." % self.value
		else:
			return "Grading error."



########################################################################
#                                                                      #
# calculate_steps                                                      #
#                                                                      #
########################################################################
def calculate_steps(material, step_spacing, wvl):
	"""Make a list of available steps
	
	Make a list of available steps for a given material and step spacing.
	This function takes three arguments:
	  material         the material;
	  step_spacing     the step spacing, use DEPOSITION_STEP_SPACING to
	                   get the steps that can be deposited;
	  wvl              the wavelength at which to calculate the steps.
	and returns:
	  steps            the list of steps."""
	
	if step_spacing == DEPOSITION_STEP_SPACING:
		return material.get_deposition_steps(wvl)
	
	# Steps are choosen so that they are exactly divisible by the
	# steps spacing. The first and last steps may be undivisible by the
	# steps spacing since they are defined by the maximum and minimum
	# available index for that material.
	n_min, n_max = material.get_index_range(wvl)
	
	# We first find the indices exactly divisible by the step spacing
	# and that are just outside the range of available index. These
	# will be replaced by n_min and n_max. If the "dummy"
	dummy_first_step = math.floor(n_min/step_spacing)*step_spacing
	dummy_last_step = math.ceil(n_max/step_spacing)*step_spacing
	
	# To avoid numerical errors, if the second or the next to last
	# steps are too close to n_min and n_max, they are eliminated.
	if abs(dummy_first_step+step_spacing-n_min) < sqrt_epsilon:
		dummy_first_step += step_spacing
	if abs(dummy_last_step-step_spacing-n_max) < sqrt_epsilon:
		dummy_last_step -= step_spacing
	
	# Calculate the number of steps.
	nb_steps = 1 + int(round((dummy_last_step - dummy_first_step) / step_spacing))
	
	# Calculate the steps and replace the first and last ones by n_min
	# and n_max, respectively.
	steps = [dummy_first_step + i_step*step_spacing for i_step in range(nb_steps)]
	steps[0] = n_min
	steps[-1] = n_max
	
	return steps



########################################################################
#                                                                      #
# index_profile_to_steps_                                              #
#                                                                      #
########################################################################
def index_profile_to_steps_(n, d, x, steps, minimum_thickness, defined_in_OT):
	"""Convert an index profile to steps
	
	Convert an index profile into steps. This function takes 6 arguments:
	  n                  a list containing the index of the index
	                     profile;
	  d                  a list containing the depth in physical
	                     thickness;
	  x                  a list containing the depth in optical
	                     thickness;
	  steps              a list containing the steps into which the index
	                     must be converted that must be monotonuously
	                     increasing;
	  minimum_thickness  the minimum thickness of the steps;
	  defined_in_OT      a boolean indicating that the index profile is
	                     defined in optical thickness;
	and returns:
	  step_profile       a list with the steps, described by their position
	                     in the step list;
	  thickness          a list with the thickness of the steps.
	
	The conversion is done preserving both the physical and the optical
	thickness, or raises a grading_error to indicate that it is
	impossible to do so. This function is only meant to be called
	internally by the functions index_profile_to_steps and
	index_profile_in_OT_to_steps."""
	
	# Merge sublayers with identical refractive index at the beginning.
	while len(n) > 1 and n[1] == n[0]:
		n.pop(0)
		d.pop(0)
		x.pop(0)
	
	nb_steps = len(steps)
	nb_sublayers = len(d)
	
	# Verification that the whole index profile is within available
	# values (a small difference is tolerated to avoid numerical
	# problems). Correct the index if it falls outside of available
	# values.
	min_index = steps[0]
	max_index = steps[-1]
	if min(n) < (1.0-sqrt_epsilon)*min_index or max(n) > (1.0+sqrt_epsilon)*max_index:
		raise grading_error("Index out of range")
	for i_sublayer in range(nb_sublayers):
		if n[i_sublayer] < min_index:
			n[i_sublayer] = min_index
		elif n[i_sublayer] > max_index:
			n[i_sublayer] = max_index
	
	# Localize the interval where the first sublayer is located.
	step = interpolation.locate(steps, nb_steps, n[0])
	
	# A special treatment for the improbable case of null total
	# thickness.
	if d[-1] == 0.0:
		return [step], [0.0]
	
	# A special treatment for the case of a single sublayer.
	if nb_sublayers == 1:
		if n[0] == steps[0]:
			step_profile = [0]
			thickness = [d[0]]
		
		elif n[0] == steps[step+1]:
			step_profile = [step+1]
			thickness = [d[0]]
		
		else:
			step_profile = [step, step+1]
			d_0 = (steps[step+1]*d[0]-x[0])/(steps[step+1]-steps[step])
			thickness = [d_0, d[0]-d_0]
		
		if min(thickness) < minimum_thickness:
			raise grading_error("Impossible to discretize with the given minimum sublayer thickness")
		
		return step_profile, thickness
	
	# Determine if the index is going up or down at the beginning. If
	# going down, begin with the superior step.
	if n[1] > n[0]:
		slope = +1
		# The superior limit of an interval is part of that interval.
		# If the index of the first sublayer has precisely that value and
		# the index profile is going up, we should begin with that step
		# and not the previous one.
		if n[0] == steps[step+1]: step += 1
	else:
		slope = -1
		step += 1
	
	# Begin with a zero thickness step.
	step_profile = [step]
	thickness = [0.0]
	
	last_step = step
	d_old = 0.0
	x_old = 0.0
	for i_sublayer in range(1, nb_sublayers):
		
		# If the index is not in the same interval, one or many steps must
		# be added.
		while slope*n[i_sublayer] > slope*steps[step+slope]:
			
			# Calculate where the index profile crosses the step and the
			# integral of n(x)*dx at this point.
			delta_n = n[i_sublayer]-n[i_sublayer-1]
			p = (steps[step+slope]-n[i_sublayer-1]) / delta_n
			if defined_in_OT:
				delta_x = x[i_sublayer]-x[i_sublayer-1]
				x_new = x[i_sublayer-1] + p*delta_x
				d_new = d[i_sublayer-1] + delta_x/delta_n*log1p(p*delta_n/n[i_sublayer-1])
			else:
				delta_d = d[i_sublayer]-d[i_sublayer-1]
				d_new = d[i_sublayer-1] + p*delta_d
				x_new = x[i_sublayer-1] + p*delta_d*(n[i_sublayer-1]+0.5*p*delta_n)
			
			# Calculate the thickness of the two steps that will permit to
			# keep d and x constant.
			delta_d = d_new - d_old
			delta_x = x_new - x_old
			delta_n = steps[step+slope] - steps[step]
			d_i = (steps[step+slope]*delta_d - delta_x) / delta_n
			d_i_plus_1 = delta_d - d_i
			
			# Increase the thickness of the previous step and create a new
			# one.
			thickness[-1] += d_i
			step += slope
			step_profile.append(step)
			thickness.append(d_i_plus_1)
			
			# Determine the total physical and optical thickness after the
			# addition of the two sublayers. Don't directly use d_new and
			# x_new to avoid accumulation of errors.
			d_old += d_i + d_i_plus_1
			x_old += d_i*steps[step-slope] + d_i_plus_1*steps[step]
		
		# If there is a change in direction, a step must be added.
		if i_sublayer+1 < nb_sublayers and (n[i_sublayer+1]-n[i_sublayer])*slope < 0:
			
			d_new = d[i_sublayer]
			x_new = x[i_sublayer]
			
			# Calculate the thickness of the two steps that will permit to
			# keep d and x constant.
			delta_d = d_new - d_old
			delta_x = x_new - x_old
			delta_n = steps[step+slope] - steps[step]
			d_i = (steps[step+slope]*delta_d - delta_x) / delta_n
			d_i_plus_1 = delta_d - d_i
			
			# Increase the thickness of the previous step and create a new
			# one.
			thickness[-1] += d_i
			step += slope
			step_profile.append(step)
			thickness.append(d_i_plus_1)
			
			# Determine the total physical and optical thickness after the
			# addition of the two sublayers. Don't directly use d_new and
			# x_new to avoid accumulation of errors.
			d_old += d_i + d_i_plus_1
			x_old += d_i*steps[step-slope] + d_i_plus_1*steps[step]
			
			# Reverse slope.
			slope *= -1
	
	# At the end, a step must be added.
	d_new = d[-1]
	x_new = x[-1]
	
	# Calculate the thickness of the two steps that will permit to
	# keep d and the integral of n(d)*dd constant.
	delta_d = d_new - d_old
	delta_x = x_new - x_old
	delta_n = steps[step+slope] - steps[step]
	d_i = (steps[step+slope]*delta_d - delta_x) / delta_n
	d_i_plus_1 = delta_d - d_i
	
	# Increase the thickness of the previous step and create a new
	# one.
	thickness[-1] += d_i
	step += slope
	step_profile.append(step)
	thickness.append(d_i_plus_1)
	
	# Remove layers thinner than 0 which might occur due to numerical
	# errors. Merge identical layers that might be created by that
	# process.
	i_step = 0
	while i_step < len(step_profile) - 1:
		if thickness[i_step] <= 0.0:
			thickness.pop(i_step)
			step_profile.pop(i_step)
		elif i_step > 0 and step_profile[i_step] == step_profile[i_step-1]:
			thickness[i_step-1] += thickness[i_step]
			thickness.pop(i_step)
			step_profile.pop(i_step)
		else:
			i_step += 1
	
	# Make sure that the first sublayer is thick enough. This is done by
	# distributing the thickness of the second sublayer on the first and
	# the third (repeatedly, if necessary) in a way that preserves both
	# the physical and the optical thickness. 
	while thickness[0] < minimum_thickness:
		# If the second sublayer is an extremum or the last sublayer, it is
		# impossible to distribute its thickness while preserving the total
		# optical thickness.
		if len(step_profile) < 3 or (step_profile[1]-step_profile[0])*(step_profile[2]-step_profile[1]) < 0:
			raise grading_error("Impossible to discretize with the given minimum sublayer thickness")
		
		# Calculate how much thickness is missing on the first sublayer.
		missing_d = minimum_thickness-thickness[0]
		
		# Determine the maximum thickness that can be obtained from the
		# second sublayer.
		max_delta_d = thickness[1]*(steps[step_profile[2]]-steps[step_profile[1]])/(steps[step_profile[2]]-steps[step_profile[0]])
		
		# If that maximum thickness is smaller or equal to the thickness
		# missing on the first layer, completely distribute the second
		# sublayer.
		if max_delta_d <= missing_d:
			thickness[0] += max_delta_d
			thickness[2] += thickness[1] - max_delta_d
			
			thickness.pop(1)
			step_profile.pop(1)
		
		# Otherwise, take only what is necessary.
		else:
			delta_d_2 = missing_d*(steps[step_profile[1]]-steps[step_profile[0]])/(steps[step_profile[2]]-steps[step_profile[1]])
			thickness[0] += missing_d
			thickness[1] -= missing_d+delta_d_2
			thickness[2] += delta_d_2
	
	# Make sure that the last sublayer is thick enough. This is done the
	# same way than for the first sublayer
	while thickness[-1] < minimum_thickness:
		# If the second to last sublayer is an extremum or the first
		# sublayer, it is impossible to distribute its thickness while
		# preserving the total optical thickness.
		if len(step_profile) < 3 or (step_profile[-2]-step_profile[-1])*(step_profile[-3]-step_profile[-2]) < 0:
			raise grading_error("Impossible to discretize with the given minimum sublayer thickness")
		
		# Calculate how much thickness is missing on the last sublayer.
		missing_d = minimum_thickness-thickness[-1]
		
		# Determine the maximum thickness that can be obtained from the
		# second to last sublayer.
		max_delta_d = thickness[-2]*(steps[step_profile[-3]]-steps[step_profile[-2]])/(steps[step_profile[-3]]-steps[step_profile[-1]])
		
		# If that maximum thickness is smaller or equal to the thickness
		# missing on the last layer, completely distribute the second to
		# last sublayer.
		if max_delta_d <= missing_d:
			thickness[-1] += max_delta_d
			thickness[-3] += thickness[-2] - max_delta_d
			
			thickness.pop(-2)
			step_profile.pop(-2)
		
		# Otherwise, take only what is necessary.
		else:
			delta_d_2 = missing_d*(steps[step_profile[-2]]-steps[step_profile[-1]])/(steps[step_profile[-3]]-steps[step_profile[-2]])
			thickness[-1] += missing_d
			thickness[-2] -= missing_d+delta_d_2
			thickness[-3] += delta_d_2
	
	# Make sure that all extrema are thick enough. To try to keep
	# extrema in their position, this is done by taking thickness from
	# the previous and the next sublayers, when possible. When thickness
	# is taken from the previous or next sublayers, it is distributed to
	# the optimum and the other sublayer adjacent to them in order to
	# preserve both the physical and the optical thickness.
	i_step = 1
	while i_step < len(step_profile) - 1:
		# If the sublayer is thick enough, or not an extremum, immediately
		# skip to the next sublayer.
		if thickness[i_step] >= minimum_thickness or not (step_profile[i_step]-step_profile[i_step-1])*(step_profile[i_step+1]-step_profile[i_step]) < 0:
			i_step += 1
			continue
		
		# Evaluate if the previous and next sublayer can participate in
		# increasing the thickness of the optimum sublayer. The first and
		# last sublayers of the layer, as well as sublayers which are
		# themselves optima cannot participate.
		if i_step == 1 or (step_profile[i_step-1]-step_profile[i_step-2])*(step_profile[i_step]-step_profile[i_step-1]) < 0:
			previous_sublayer_can_participate = False
		else:
			previous_sublayer_can_participate = True
		if i_step == len(step_profile) - 2 or (step_profile[i_step+1]-step_profile[i_step])*(step_profile[i_step+2]-step_profile[i_step+1]) < 0:
			next_sublayer_can_participate = False
		else:
			next_sublayer_can_participate = True
		
		# If neither can participate, it is impossible to increase the
		# thickness of the extremum.
		if not (previous_sublayer_can_participate or next_sublayer_can_participate):
			raise grading_error("Impossible to discretize with the given minimum sublayer thickness")
		
		# Calculate how much thickness is missing on the last sublayer.
		missing_d = minimum_thickness-thickness[i_step]
		
		# Calculate how much thickness can be obtained from the previous
		# and the next sublayers.
		if previous_sublayer_can_participate:
			max_delta_d_from_previous_sublayer = thickness[i_step-1]*(steps[step_profile[i_step-1]]-steps[step_profile[i_step-2]])/(steps[step_profile[i_step]]-steps[step_profile[i_step-2]])
		else:
			max_delta_d_from_previous_sublayer = 0.0
		if next_sublayer_can_participate:
			max_delta_d_from_next_sublayer = thickness[i_step+1]*(steps[step_profile[i_step+1]]-steps[step_profile[i_step+2]])/(steps[step_profile[i_step]]-steps[step_profile[i_step+2]])
		else:
			max_delta_d_from_next_sublayer = 0.0
		
		# Determine how much is taken from the adjactent sublayers.
		if previous_sublayer_can_participate and next_sublayer_can_participate:
			half_max_delta_d = min(max_delta_d_from_previous_sublayer, max_delta_d_from_next_sublayer)
			delta_d_from_previous_sublayer = min(half_max_delta_d, 0.5*missing_d)
			delta_d_from_next_sublayer = delta_d_from_previous_sublayer
		elif previous_sublayer_can_participate:
			delta_d_from_previous_sublayer = min(max_delta_d_from_previous_sublayer, missing_d)
			delta_d_from_next_sublayer = 0.0
		else:
			delta_d_from_previous_sublayer = 0.0
			delta_d_from_next_sublayer = min(max_delta_d_from_next_sublayer, missing_d)
		
		# Adjust adjacent sublayers (beginning with the next one to avoid
		# numbering issues).
		if next_sublayer_can_participate:
			if delta_d_from_next_sublayer == max_delta_d_from_next_sublayer:
				thickness[i_step] += delta_d_from_next_sublayer
				thickness[i_step+2] += thickness[i_step+1]-delta_d_from_next_sublayer
				
				thickness.pop(i_step+1)
				step_profile.pop(i_step+1)
			else:
				delta_d_i_step_plus_2 = delta_d_from_next_sublayer*(steps[step_profile[i_step+1]]-steps[step_profile[i_step]])/(steps[step_profile[i_step+2]]-steps[step_profile[i_step+1]])
				thickness[i_step] += delta_d_from_next_sublayer
				thickness[i_step+1] -= delta_d_from_next_sublayer+delta_d_i_step_plus_2
				thickness[i_step+2] += delta_d_i_step_plus_2
		if previous_sublayer_can_participate:
			if delta_d_from_previous_sublayer == max_delta_d_from_previous_sublayer:
				thickness[i_step] += delta_d_from_previous_sublayer
				thickness[i_step-2] += thickness[i_step-1]-delta_d_from_previous_sublayer
				
				thickness.pop(i_step-1)
				step_profile.pop(i_step-1)
				
				i_step -= 1
			else:
				delta_d_i_step_minus_2 = delta_d_from_previous_sublayer*(steps[step_profile[i_step-1]]-steps[step_profile[i_step]])/(steps[step_profile[i_step-2]]-steps[step_profile[i_step-1]])
				thickness[i_step] += delta_d_from_previous_sublayer
				thickness[i_step-1] -= delta_d_from_previous_sublayer+delta_d_i_step_minus_2
				thickness[i_step-2] += delta_d_i_step_minus_2
	
	# Do the rest of the job. We repeatadly work on the thinnest sublayer
	# instead of sequentially going through all the sublayers because it
	# gives a more symmetric effect.
	while min(thickness) < minimum_thickness:
		step_nb = thickness.index(min(thickness))
		
		# Verify if it is possible to increase the thickness of the
		# sublayer by taking thickness for the adjacent sublayers without
		# making them too thin.
		missing_d = minimum_thickness-thickness[step_nb]
		d_step_nb_minus_1 = missing_d*(steps[step_profile[step_nb+1]]-steps[step_profile[step_nb]])/(steps[step_profile[step_nb+1]]-steps[step_profile[step_nb-1]])
		d_step_nb_plus_1 = missing_d-d_step_nb_minus_1
		if thickness[step_nb-1]-d_step_nb_minus_1 >= minimum_thickness and thickness[step_nb+1]-d_step_nb_plus_1 >= minimum_thickness:
			thickness[step_nb-1] -= d_step_nb_minus_1
			thickness[step_nb] = minimum_thickness
			thickness[step_nb+1] -= d_step_nb_plus_1
		
		# If it is not, distribute the thickness of the sublayer on the
		# previous and the next sublayers.
		else:
			d_step_nb_minus_1 = thickness[step_nb]*(steps[step_profile[step_nb+1]]-steps[step_profile[step_nb]])/(steps[step_profile[step_nb+1]]-steps[step_profile[step_nb-1]])
			d_step_nb_plus_1 = thickness[step_nb]-d_step_nb_minus_1
			
			thickness[step_nb-1] += d_step_nb_minus_1
			thickness[step_nb+1] += d_step_nb_plus_1
			
			thickness.pop(step_nb)
			step_profile.pop(step_nb)
	
	return step_profile, thickness



########################################################################
#                                                                      #
# index_profile_to_steps                                               #
#                                                                      #
########################################################################
def index_profile_to_steps(n, d, steps, minimum_thickness = 0.0):
	"""Convert an index profile given in physical thickness to steps
	
	Convert an index profile, defined by the index as a function of depth
	in physical thickness into steps. This conversion is done preserving
	the total optical thickness. This function takes 3 or 4 arguments:
	  n                  a list containing the index of the index
	                     profile;
	  d                  a list containing the depth in physical
	                     thickness;
	  steps              a list containing the steps into which the index
	                     must be converted that must be monotonuously
	                     increasing;
	  minimum_thickness  (optional) the minimum thickness of the steps,
	                     default value is 0.0;
	and returns:
	  step_profile       a list with the steps, described by their
	                     position in the step list;
	  thickness          a list with the thickness of the steps.
	
	It raises a grading_error if it is impossible to discretize the index
	profile according to the steps and minimum_thickness given."""
	
	nb_sublayers = len(n)
	
	# Verify that d increases monotonously.
	for i_sublayer in range(1, nb_sublayers):
		if d[i_sublayer] < d[i_sublayer-1]:
			raise grading_error("The thickness is not monotonously increasing")
	
	# Calculate the optical thickess.
	x = [0.0]*nb_sublayers
	x_ = d[0]*n[0]
	x[0] = x_
	for i_sublayer in range(1, nb_sublayers):
		x_ += 0.5*(n[i_sublayer-1]+n[i_sublayer])*(d[i_sublayer]-d[i_sublayer-1])
		x[i_sublayer] = x_
	
	return index_profile_to_steps_(n, d, x, steps, minimum_thickness, False)



########################################################################
#                                                                      #
# index_profile_in_OT_to_steps                                         #
#                                                                      #
########################################################################
def index_profile_in_OT_to_steps(n, x, steps, minimum_thickness = 0.0):
	"""Convert an index profile given in optical thickness to steps
	
	Convert an index profile, defined by the index a function of depth in
	optical thickness into steps. This conversion is done preserving the
	total optical thickness. This function takes 3 or 4 arguments:
	  n                  a list containing the index of the index
	                     profile;
	  x                  a list containing the depth in optical
	                     thickness;
	  steps              a list containing the steps into which the index
	                     must be converted that must be monotonuously
	                     increasing;
	  minimum_thickness  (optional) the minimum thickness of the steps,
	                     default value is 0.0;
	and returns:
	  step_profile       a list with the steps, described by their position
	                     in the step list;
	  thickness          a list with the thickness of the steps.
	
	It raises a grading_error if it is impossible to discretize the index
	profile according to the steps and minimum_thickness given."""
	
	nb_sublayers = len(x)
	
	# Verify that x increases monotonously.
	for i_sublayer in range(1, nb_sublayers):
		if x[i_sublayer] < x[i_sublayer-1]:
			raise grading_error("The optical thickness is not monotonously increasing")
	
	d = [0.0]*nb_sublayers
	
	# Convert the optical thickness to physical thickness.
	d[0] = x[0]/n[0]
	for i_sublayer in range(1, nb_sublayers):
		delta_n = n[i_sublayer]-n[i_sublayer-1]
		delta_x = x[i_sublayer]-x[i_sublayer-1]
		if delta_n == 0:
			d[i_sublayer] = d[i_sublayer-1] + delta_x/n[i_sublayer]
		else:
			d[i_sublayer] = d[i_sublayer-1] + delta_x/delta_n*math.log(n[i_sublayer]/n[i_sublayer-1])
	
	return index_profile_to_steps_(n, d, x, steps, minimum_thickness, True)



########################################################################
#                                                                      #
# steps_to_index_profile                                               #
#                                                                      #
########################################################################
def steps_to_index_profile(thickness, step_profile, steps):
	"""Get the index profile corresponding to a step profile.
	
	This function takes 3 arguments:
		thickness        a list containing the thickness of the steps;
	  step_profile     a list containing the list of steps in the step
	                   profile;
	  steps            a list containing the indices corresponding to the
	                   steps used in the step profile;
	and returns:
	  d                the depth of the index profile;
	  n                the index profile."""
	
	nb_steps = len(step_profile)
	
	d = [0.0]*(2*nb_steps)
	d_ = 0.0
	for i_step in range(nb_steps):
		d[2*i_step] = d_
		d_ += thickness[i_step]
		d[2*i_step+1] = d_
	
	n = [steps[step_profile[i_step//2]] for i_step in range(2*nb_steps)]
	
	return d, n



########################################################################
#                                                                      #
# steps_to_index                                                       #
#                                                                      #
########################################################################
def steps_to_index(step_profile, steps):
	"""Get a list of indices corresponding to a list of steps.
	
	This function takes 2 arguments:
	  step_profile     a list containing the steps of the index profile;
	  steps            a list containing the indices corresponding to the
	                   steps used in the step profile;
	and returns a list containing the index profile of the layer."""
	
	return [steps[step_profile[i_step]] for i_step in range(len(step_profile))]



########################################################################
#                                                                      #
# change_step_profile                                                  #
#                                                                      #
########################################################################
def change_step_profile(material, old_step_profile, old_thickness, old_steps, old_wvl, new_steps, new_wvl, minimum_thickness = 0.0):
	"""Convert a step profile at one wavelength to another wavelength or
	another step discretization
	
	This function takes 7 or 8 arguments:
	  material           the material;
	  old_step_profile   a list containing the steps of the input index
	                     profile;
	  old_thickness      a list with the thickness of the steps of the
	                     input index profile;
	  old_steps          a list containing the indices corresponding to
	                     the steps used in the input step profile;
	  old_wvl            the wavelength of the input step profile;
	  new_steps          a list containing the indices corresponding to
	                     the steps used in the output step profile;
	  new_wvl            the wavelength of the output step profile;
	  minimum_thickness  (optional) the minimum thickness of the steps,
	                     default value is 0.0);
	and returns:
	  new_step_profile   the steps at the new wavelength;
	  new_thickness      the thickness of the steps in the output step
	                     profile."""
	
	if old_wvl == new_wvl:
		# Calculate the index profile at the wavelength.
		d, n = steps_to_index_profile(old_thickness, old_step_profile, old_steps)
	
	else:
		# Calculate the old steps at the new wavelength.
		old_steps_at_new_wvl = [material.change_index_wavelength(old_steps[i_mixture], old_wvl, new_wvl) for i_mixture in range(len(old_steps))]
		
		# Calculate the index profile at the new wavelength.
		d, n = steps_to_index_profile(old_thickness, old_step_profile, old_steps_at_new_wvl)
	
	# Change the index profile to the new steps.
	new_step_profile, new_thickness = index_profile_to_steps(n, d, new_steps, minimum_thickness)
	
	return new_step_profile, new_thickness
