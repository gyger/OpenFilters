# targets.py
# 
# Classes to define targets.
# 
# Copyright (c) 2000-2009,2012,2013,2015 Stephane Larouche.
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



import math

from definitions import *
import simple_parser
from moremath import interpolation
from moremath.Levenberg_Marquardt import SMALLER, EQUAL, LARGER
import color
import version



# The various kinds of targets.
R_TARGET = 1
T_TARGET = 2
A_TARGET = 3
R_SPECTRUM_TARGET = 4
T_SPECTRUM_TARGET = 5
A_SPECTRUM_TARGET = 6
R_PHASE_TARGET = 7
T_PHASE_TARGET = 8
R_GD_TARGET = 9
T_GD_TARGET = 10
R_GDD_TARGET = 11
T_GDD_TARGET = 12
R_PHASE_SPECTRUM_TARGET = 13
T_PHASE_SPECTRUM_TARGET = 14
R_GD_SPECTRUM_TARGET = 15
T_GD_SPECTRUM_TARGET = 16
R_GDD_SPECTRUM_TARGET = 17
T_GDD_SPECTRUM_TARGET = 18
R_COLOR_TARGET = 19
T_COLOR_TARGET = 20

PHOTOMETRIC_TARGETS = [R_TARGET, T_TARGET, A_TARGET, R_SPECTRUM_TARGET, T_SPECTRUM_TARGET, A_SPECTRUM_TARGET]
DISPERSIVE_TARGETS = [R_PHASE_TARGET, T_PHASE_TARGET, R_GD_TARGET, T_GD_TARGET, R_GDD_TARGET, T_GDD_TARGET, R_PHASE_SPECTRUM_TARGET, T_PHASE_SPECTRUM_TARGET, R_GD_SPECTRUM_TARGET, T_GD_SPECTRUM_TARGET, R_GDD_SPECTRUM_TARGET, T_GDD_SPECTRUM_TARGET]
PHASE_TARGETS = [R_PHASE_TARGET, T_PHASE_TARGET, R_PHASE_SPECTRUM_TARGET, T_PHASE_SPECTRUM_TARGET]
GD_TARGETS = [R_GD_TARGET, T_GD_TARGET, R_GD_SPECTRUM_TARGET, T_GD_SPECTRUM_TARGET]
GDD_TARGETS = [R_GDD_TARGET, T_GDD_TARGET, R_GDD_SPECTRUM_TARGET, T_GDD_SPECTRUM_TARGET]
COLOR_TARGETS = [R_COLOR_TARGET, T_COLOR_TARGET]

REFLECTION_TARGETS = [R_TARGET, R_SPECTRUM_TARGET, R_PHASE_TARGET, R_GD_TARGET, R_GDD_TARGET, R_PHASE_SPECTRUM_TARGET, R_GD_SPECTRUM_TARGET, R_GDD_SPECTRUM_TARGET, R_COLOR_TARGET]
TRANSMISSION_TARGETS = [T_TARGET, T_SPECTRUM_TARGET, T_PHASE_TARGET, T_GD_TARGET, T_GDD_TARGET, T_PHASE_SPECTRUM_TARGET, T_GD_SPECTRUM_TARGET, T_GDD_SPECTRUM_TARGET, T_COLOR_TARGET]
ABSORPTION_TARGETS = [A_TARGET, A_SPECTRUM_TARGET]

DISCRETE_TARGETS = [R_TARGET, T_TARGET, A_TARGET, R_PHASE_TARGET, T_PHASE_TARGET, R_GD_TARGET, T_GD_TARGET, R_GDD_TARGET, T_GDD_TARGET]
SPECTRUM_TARGETS = [R_SPECTRUM_TARGET, T_SPECTRUM_TARGET, A_SPECTRUM_TARGET, R_PHASE_SPECTRUM_TARGET, T_PHASE_SPECTRUM_TARGET, R_GD_SPECTRUM_TARGET, T_GD_SPECTRUM_TARGET, R_GDD_SPECTRUM_TARGET, T_GDD_SPECTRUM_TARGET]

REVERSIBLE_TARGETS = [R_TARGET, T_TARGET, A_TARGET, R_SPECTRUM_TARGET, T_SPECTRUM_TARGET, A_SPECTRUM_TARGET, R_COLOR_TARGET, T_COLOR_TARGET]
S_OR_P_POLARIZATION_TARGETS = DISPERSIVE_TARGETS

# Reusable lists.
DISCRETE_TARGET_KINDS = ["Reflection", "Transmission", "Absorption", "ReflectionPhase", "TransmissionPhase", "ReflectionGD", "TransmissionGD", "ReflectionGDD", "TransmissionGDD"]
SPECTRUM_TARGET_KINDS = ["ReflectionSpectrum", "TransmissionSpectrum", "AbsorptionSpectrum", "ReflectionPhaseSpectrum", "TransmissionPhaseSpectrum", "ReflectionGDSpectrum", "TransmissionGDSpectrum", "ReflectionGDDSpectrum", "TransmissionGDDSpectrum"]
COLOR_TARGET_KINDS = ["ReflectionColor", "TransmissionColor"]
REVERSIBLE_TARGET_KINDS = ["Reflection", "Transmission", "Absorption", "ReflectionSpectrum", "TransmissionSpectrum", "AbsorptionSpectrum", "ReflectionColor", "TransmissionColor"]
DISPERSIVE_TARGET_KINDS = ["ReflectionPhase", "TransmissionPhase", "ReflectionGD", "TransmissionGD", "ReflectionGDD", "TransmissionGDD", "ReflectionPhaseSpectrum", "TransmissionPhaseSpectrum", "ReflectionGDSpectrum", "TransmissionGDSpectrum", "ReflectionGDDSpectrum", "TransmissionGDDSpectrum"]
S_OR_P_POLARIZATION = [S, P]



########################################################################
#                                                                      #
# target_error                                                         #
#                                                                      #
########################################################################
class target_error(Exception):
	"""Exception class for target errors"""
	
	def __init__(self, value = ""):
		self.value = value
	
	def __str__(self):
		if self.value:
			return "Target error: %s." % self.value
		else:
			return "Target error."



########################################################################
#                                                                      #
# target                                                               #
#                                                                      #
########################################################################
class target(object):
	"""A generic class to define targets
	
	All target class derive from this class."""
	
	kind = -1
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the target class"""
		
		self.angle = 0.0
		self.polarization = UNPOLARIZED
		self.direction = FORWARD
		self.inequality = EQUAL
		
		self.modified = False
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the target
		
		This method returns a clone of the target."""
		
		clone = self.__class__()
		
		clone.set_angle(self.angle)
		clone.set_polarization(self.polarization)
		clone.set_direction(self.direction)
		clone.set_inequality(self.inequality)
		
		clone.set_modified(False)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# get_kind                                                           #
	#                                                                    #
	######################################################################
	def get_kind(self):
		"""Get the kind of target"""
		
		return self.kind
	
	
	######################################################################
	#                                                                    #
	# set_angle                                                          #
	#                                                                    #
	######################################################################
	def set_angle(self, angle):
		"""Set the angle of incidence, in degrees, of the target"""
		
		if angle != self.angle:
			self.angle = angle
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_angle                                                          #
	#                                                                    #
	######################################################################
	def get_angle(self):
		"""Get the angle of incidence, in degrees, of the target."""
		
		return self.angle
	
	
	######################################################################
	#                                                                    #
	# set_polarization                                                   #
	#                                                                    #
	######################################################################
	def set_polarization(self, polarization):
		"""Set the polarization of the target"""
		
		if polarization != self.polarization:
			self.polarization = polarization
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_polarization                                                   #
	#                                                                    #
	######################################################################
	def get_polarization(self):
		"""Get the polarization of the target"""
		
		return self.polarization
	
	
	######################################################################
	#                                                                    #
	# set_direction                                                      #
	#                                                                    #
	######################################################################
	def set_direction(self, direction):
		"""Set the direction of the target"""
		
		if direction != self.direction:
			self.direction = direction
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_direction                                                      #
	#                                                                    #
	######################################################################
	def get_direction(self):
		"""Get the direction of the target"""
		
		return self.direction
	
	
	######################################################################
	#                                                                    #
	# set_inequality                                                     #
	#                                                                    #
	######################################################################
	def set_inequality(self, inequality):
		"""Set the inequality of the target"""
		
		if inequality != self.inequality:
			self.inequality = inequality
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_inequality                                                     #
	#                                                                    #
	######################################################################
	def get_inequality(self):
		"""Get the inequality of the target"""
		
		return self.inequality
		
	
	######################################################################
	#                                                                    #
	# get_values                                                         #
	#                                                                    #
	######################################################################
	def get_values(self):
		"""Get the values of the target
		
		This method must be implemented by subclasses."""
		
		raise NotImplementedError("Subclass must implement this method")
	
	
	######################################################################
	#                                                                    #
	# set_modified                                                       #
	#                                                                    #
	######################################################################
	def set_modified(self, modified):
		"""Set the modification status of the target
		
		Use this method when the target is saved in order to track
		modifications between saves. This method takes a single input
		argument:
		  modified     indication of the modification status."""
		
		self.modified = modified
	
	
	######################################################################
	#                                                                    #
	# get_modified                                                       #
	#                                                                    #
	######################################################################
	def get_modified(self):
		"""Get if the target was modified since it was saved
		
		This method returns True or False depending if the target have been
		modified."""
		
		return self.modified



########################################################################
#                                                                      #
# discrete_target                                                      #
#                                                                      #
########################################################################
class discrete_target(target):
	"""A base class for targets consisting of a value at a single
	wavelength"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the discrete target class"""
		
		target.__init__(self)
		
		# The target value.
		self.wavelength = 0.0
		self.value = 0.0
		self.delta = 0.0
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the target
		
		This method returns a clone of the target."""
		
		clone = target.clone(self)
		
		clone.set_target(self.wavelength, self.value, self.delta)
		
		clone.set_modified(False)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# set_target                                                         #
	#                                                                    #
	######################################################################
	def set_target(self, wavelength, value, delta):
		"""Set the target
		
		This method takes 3 arguments:
		  wavelength         the wavelength of the target;
		  value              the value of the target;
		  delta              the tolerance on the target."""
		
		if wavelength != self.wavelength or value != self.value or delta != self.delta:
			self.wavelength = wavelength
			self.value = value
			self.delta = delta
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_values                                                         #
	#                                                                    #
	######################################################################
	def get_values(self):
		"""Get the target
		
		This method returns:
		  wavelength         the wavelength of the target;
		  value              the value of the target;
		  delta              the tolerance on the target.
		
		All these values are returned in single element lists to
		simplify the coding of optimization methods."""
		
		return [self.wavelength], [self.value], [self.delta]
	
	
	
########################################################################
#                                                                      #
# spectrum_target                                                      #
#                                                                      #
########################################################################
class spectrum_target(target):
	"""A base class for spectrum targets"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the spectrum target class"""
		
		target.__init__(self)
		
		# The target values.
		self.wavelengths = []
		self.values = []
		self.deltas = []
		
		# Continuous targets are usually defined by a serie of points
		# in a range of wavelengths.
		self.from_wavelength = 0.0
		self.to_wavelength = 0.0
		self.by_wavelength = 0.0
		self.point_wavelengths = []
		self.point_values = []
		self.point_deltas = []
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the target
		
		This method returns a clone of the target."""
		
		clone = target.clone(self)
		
		clone.set_target(self.from_wavelength, self.to_wavelength, self.by_wavelength, self.point_wavelengths, self.points_values, self.points_deltas)
		
		clone.set_modified(False)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# set_target                                                         #
	#                                                                    #
	######################################################################
	def set_target(self, from_wavelength, to_wavelength, by_wavelength, point_wavelengths, points_values, points_deltas):
		"""Set the target
		
		This method takes 3 arguments:
		  from_wavelength    the lower wavelength of the spectrum;
		  to_wavelength      the higher wavelength of the spectrum;
		  by_wavelength      the wavelength increment of the spectrum;
		  point_wavelengths  the wavelengths of the definition points;
		  point_values       the value of the target at the definition
		                     points;
		  point_deltas       the tolerance on the target at the definition
		                     points.
		
		The target is linearly interpolated between definition points.
		When by_wavelength is set to 0, the definition points are directly
		used as the target."""
		
		# If all parameters are identical, return immediatly.
		if self.from_wavelength == from_wavelength and self.to_wavelength == to_wavelength and self.by_wavelength == by_wavelength and self.point_wavelengths == point_wavelengths and self.points_values == points_values and self.points_deltas == points_deltas:
			return
		
		self.from_wavelength = from_wavelength
		self.to_wavelength = to_wavelength
		self.by_wavelength = by_wavelength
		self.point_wavelengths = point_wavelengths
		self.points_values = points_values
		self.points_deltas = points_deltas
		
		# If by_wavelength is null, it means that only the given points
		# should be considered.
		if self.by_wavelength == 0.0:
			self.wavelengths = self.point_wavelengths
			self.values = self.points_values
			self.deltas = self.points_deltas
			
			# The wavelength range is determined since from_wavelength and
			# to_wavelength are expected to be 0.
			self.from_wavelength = min(self.wavelengths)
			self.to_wavelength = max(self.wavelengths)
		
		else:
			# Add two points at the extremities with the values of the closest
			# point to avoid extrapolation if the are not already the end
			# points.
			if point_wavelengths[0] > self.from_wavelength:
				point_wavelengths.insert(0, from_wavelength)
				points_values.insert(0, points_values[0])
				points_deltas.insert(0, points_deltas[0])
			if point_wavelengths[-1] < self.to_wavelength:
				point_wavelengths.append(to_wavelength)
				points_values.append(points_values[-1])
				points_deltas.append(points_deltas[-1])
			
			nb_wavelengths = int(math.ceil((self.to_wavelength-self.from_wavelength)/self.by_wavelength)+1)
			self.wavelengths = [self.from_wavelength + i*self.by_wavelength for i in range(nb_wavelengths)]
			self.wavelengths[-1] = self.to_wavelength
			
			self.values = interpolation.linear_interpolation(self.point_wavelengths, self.points_values, self.wavelengths)
			self.deltas = interpolation.linear_interpolation(self.point_wavelengths, self.points_deltas, self.wavelengths)
		
		self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_points                                                         #
	#                                                                    #
	######################################################################
	def get_points(self):
		"""Get the definition of the target
		
		This method returns:
		  from_wavelength    the lower wavelength of the spectrum;
		  to_wavelength      the higher wavelength of the spectrum;
		  by_wavelength      the wavelength increment of the spectrum;
		  point_wavelengths  the wavelengths of the definition points;
		  point_values       the value of the target at the definition
		                     points;
		  point_deltas       the tolerance on the target at the definition
		                     points."""
		
		return self.from_wavelength, self.to_wavelength, self.by_wavelength, self.point_wavelengths, self.points_values, self.points_deltas
	
	
	######################################################################
	#                                                                    #
	# get_values                                                         #
	#                                                                    #
	######################################################################
	def get_values(self):
		"""Get the target
		
		This method returns:
		  wavelengths        the wavelengths of the target;
		  values             the values of the target;
		  deltas             the tolerances on the target."""
		
		return self.wavelengths, self.values, self.deltas



########################################################################
#                                                                      #
# color_target                                                         #
#                                                                      #
########################################################################
class color_target(target):
	"""A base class for color targets"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self):
		"""Initialize an instance of the color target class"""
		
		target.__init__(self)
		
		# The illuminant and observer.
		self.illuminant = None
		self.observer = None
		
		# The color space used.
		self.color_space = -1
		
		# The target values.
		self.target_values = []
		self.tolerances = []
	
	
	######################################################################
	#                                                                    #
	# clone                                                              #
	#                                                                    #
	######################################################################
	def clone(self):
		"""Get a copy of the target
		
		This method returns a clone of the target."""
		
		clone = target.clone(self)
		
		clone.set_illuminant_and_observer(self.illuminant, self.observer)
		clone.set_target(self.color_space, self.target_values, self.tolerances)
		
		clone.set_modified(False)
		
		return clone
	
	
	######################################################################
	#                                                                    #
	# set_illuminant_and_observer                                        #
	#                                                                    #
	######################################################################
	def set_illuminant_and_observer(self, illuminant, observer):
		"""Set the illuminant and the observer
		
		This method takes 2 arguments:
		  illuminant         the illuminant of the target;
		  observer           the observer of the target."""
		
		if illuminant != self.illuminant or observer != self.observer:
			self.illuminant = illuminant
			self.observer = observer
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# set_target                                                         #
	#                                                                    #
	######################################################################
	def set_target(self, color_space, target_values, tolerances):
		"""Set the target
		
		Thie method takes 3 arguments:
		  color_space        the color space used to describe the target
		                     (XYZ, xyY, Luv, or Lab);
		  target_values      the triplet of values describing the color;
		  tolerances         the tolerances on these values."""
		
		if color_space != self.color_space or target_values != self.target_values or tolerances != self.tolerances:
			self.color_space = color_space
			self.target_values = target_values
			self.tolerances = tolerances
			
			self.modified = True
	
	
	######################################################################
	#                                                                    #
	# get_illuminant_and_observer                                        #
	#                                                                    #
	######################################################################
	def get_illuminant_and_observer(self):
		"""Get the illuminant and the observer"""
		
		return self.illuminant, self.observer
	
	
	######################################################################
	#                                                                    #
	# get_color_space                                                    #
	#                                                                    #
	######################################################################
	def get_color_space(self):
		"""Get the color space"""
		
		return self.color_space
	
	
	######################################################################
	#                                                                    #
	# get_values                                                         #
	#                                                                    #
	######################################################################
	def get_values(self):
		"""Get the target
		
		This method returns:
		  target_values      the triplet of values describing the color;
		  tolerances         the tolerances on these values."""
		
		return self.target_values, self.tolerances



########################################################################
#                                                                      #
# reflection_target                                                    #
#                                                                      #
########################################################################
class reflection_target(discrete_target):
	"""A class for reflection targets"""
	
	kind = R_TARGET



########################################################################
#                                                                      #
# transmission_target                                                  #
#                                                                      #
########################################################################
class transmission_target(discrete_target):
	"""A class for transmission targets"""
	
	kind = T_TARGET



########################################################################
#                                                                      #
# absorption_target                                                    #
#                                                                      #
########################################################################
class absorption_target(discrete_target):
	"""A class for absorption targets"""
	
	kind = A_TARGET



########################################################################
#                                                                      #
# reflection_spectrum_target                                           #
#                                                                      #
########################################################################
class reflection_spectrum_target(spectrum_target):
	"""A class for reflection spectrum targets"""
	
	kind = R_SPECTRUM_TARGET



########################################################################
#                                                                      #
# transmission_spectrum_target                                         #
#                                                                      #
########################################################################
class transmission_spectrum_target(spectrum_target):
	"""A class for transmission spectrum targets"""
	
	kind = T_SPECTRUM_TARGET



########################################################################
#                                                                      #
# absorption_spectrum_target                                           #
#                                                                      #
########################################################################
class absorption_spectrum_target(spectrum_target):
	"""A class for absorption spectrum targets"""
	
	kind = A_SPECTRUM_TARGET



########################################################################
#                                                                      #
# reflection_phase_target                                              #
#                                                                      #
########################################################################
class reflection_phase_target(discrete_target):
	"""A class for reflection phase targets"""
	
	kind = R_PHASE_TARGET



########################################################################
#                                                                      #
# transmission_phase_target                                            #
#                                                                      #
########################################################################
class transmission_phase_target(discrete_target):
	"""A class for transmission phase targets"""
	
	kind = T_PHASE_TARGET



########################################################################
#                                                                      #
# reflection_GD_target                                                 #
#                                                                      #
########################################################################
class reflection_GD_target(discrete_target):
	"""A class for reflection GD targets"""
	
	kind = R_GD_TARGET



########################################################################
#                                                                      #
# transmission_GD_target                                               #
#                                                                      #
########################################################################
class transmission_GD_target(discrete_target):
	"""A class for transmission GD targets"""
	
	kind = T_GD_TARGET



########################################################################
#                                                                      #
# reflection_GDD_target                                                #
#                                                                      #
########################################################################
class reflection_GDD_target(discrete_target):
	"""A class for reflection GDD targets"""
	
	kind = R_GDD_TARGET



########################################################################
#                                                                      #
# transmission_GDD_target                                              #
#                                                                      #
########################################################################
class transmission_GDD_target(discrete_target):
	"""A class for transmission GDD targets"""
	
	kind = T_GDD_TARGET



########################################################################
#                                                                      #
# reflection_phase_spectrum_target                                     #
#                                                                      #
########################################################################
class reflection_phase_spectrum_target(spectrum_target):
	"""A class for reflection phase spectrum targets"""
	
	kind = R_PHASE_SPECTRUM_TARGET



########################################################################
#                                                                      #
# transmission_phase_spectrum_target                                   #
#                                                                      #
########################################################################
class transmission_phase_spectrum_target(spectrum_target):
	"""A class for transmission phase spectrum targets"""
	
	kind = T_PHASE_SPECTRUM_TARGET



########################################################################
#                                                                      #
# reflection_GD_spectrum_target                                        #
#                                                                      #
########################################################################
class reflection_GD_spectrum_target(spectrum_target):
	"""A class for reflection GD spectrum targets"""
	
	kind = R_GD_SPECTRUM_TARGET



########################################################################
#                                                                      #
# transmission_GD_spectrum_target                                      #
#                                                                      #
########################################################################
class transmission_GD_spectrum_target(spectrum_target):
	"""A class for transmission GD spectrum targets"""
	
	kind = T_GD_SPECTRUM_TARGET



########################################################################
#                                                                      #
# reflection_GDD_spectrum_target                                       #
#                                                                      #
########################################################################
class reflection_GDD_spectrum_target(spectrum_target):
	"""A class for reflection GDD spectrum targets"""
	
	kind = R_GDD_SPECTRUM_TARGET



########################################################################
#                                                                      #
# transmission_GDD_spectrum_target                                     #
#                                                                      #
########################################################################
class transmission_GDD_spectrum_target(spectrum_target):
	"""A class for transmission GDD spectrum targets"""
	
	kind = T_GDD_SPECTRUM_TARGET



########################################################################
#                                                                      #
# reflection_color_target                                              #
#                                                                      #
########################################################################
class reflection_color_target(color_target):
	"""A class for reflection color targets"""
	
	kind = R_COLOR_TARGET



########################################################################
#                                                                      #
# transmission_color_target                                            #
#                                                                      #
########################################################################
class transmission_color_target(color_target):
	"""A class for transmission color targets"""
	
	kind = T_COLOR_TARGET



TARGETS_BY_NAME = {"Reflection": reflection_target,
                   "Transmission": transmission_target,
                   "Absorption": absorption_target,
                   "ReflectionSpectrum": reflection_spectrum_target,
                   "TransmissionSpectrum": transmission_spectrum_target,
                   "AbsorptionSpectrum": absorption_spectrum_target,
                   "ReflectionPhase": reflection_phase_target,
                   "TransmissionPhase": transmission_phase_target,
                   "ReflectionGD": reflection_GD_target,
                   "TransmissionGD": transmission_GD_target,
                   "ReflectionGDD": reflection_GDD_target,
                   "TransmissionGDD": transmission_GDD_target,
                   "ReflectionPhaseSpectrum": reflection_phase_spectrum_target,
                   "TransmissionPhaseSpectrum": transmission_phase_spectrum_target,
                   "ReflectionGDSpectrum": reflection_GD_spectrum_target,
                   "TransmissionGDSpectrum": transmission_GD_spectrum_target,
                   "ReflectionGDDSpectrum": reflection_GDD_spectrum_target,
                   "TransmissionGDDSpectrum": transmission_GDD_spectrum_target,
                   "ReflectionColor": reflection_color_target,
                   "TransmissionColor": transmission_color_target}

KIND_NAMES = {R_TARGET: "Reflection",
              T_TARGET: "Transmission",
              A_TARGET: "Absorption",
              R_PHASE_TARGET: "ReflectionPhase",
              T_PHASE_TARGET: "TransmissionPhase",
              R_GD_TARGET: "ReflectionGD",
              T_GD_TARGET: "TransmissionGD",
              R_GDD_TARGET: "ReflectionGDD",
              T_GDD_TARGET: "TransmissionGDD",
              R_SPECTRUM_TARGET: "ReflectionSpectrum",
              T_SPECTRUM_TARGET: "TransmissionSpectrum",
              A_SPECTRUM_TARGET: "AbsorptionSpectrum",
              R_PHASE_SPECTRUM_TARGET: "ReflectionPhaseSpectrum",
              T_PHASE_SPECTRUM_TARGET: "TransmissionPhaseSpectrum",
              R_GD_SPECTRUM_TARGET: "ReflectionGDSpectrum",
              T_GD_SPECTRUM_TARGET: "TransmissionGDSpectrum",
              R_GDD_SPECTRUM_TARGET: "ReflectionGDDSpectrum",
              T_GDD_SPECTRUM_TARGET: "TransmissionGDDSpectrum",
              R_COLOR_TARGET: "ReflectionColor",
              T_COLOR_TARGET: "TransmissionColor"}

COLOR_SPACE_NAMES = {color.XYZ: "XYZ",
                     color.xyY: "xyY",
                     color.Luv: "Luv",
                     color.Lab: "Lab",
                     color.LChuv: "LChuv",
                     color.LChab: "LChab"}

COLOR_SPACES_BY_NAME = dict((value, key) for key, value in COLOR_SPACE_NAMES.iteritems())



########################################################################
#                                                                      #
# parse_target                                                         #
#                                                                      #
########################################################################
def parse_target(lines, file_version):
	"""Parse a target
	
	This method takes two arguments:
	  lines                a list of lines of text describing a target;
	  file_version         the version of the file;
	and returns the target."""
	
	try:
		keywords, values = simple_parser.parse(lines)
	except simple_parser.parsing_error, error:
		raise target_error("Cannot parse target because %s" % error.get_value())
	
	kind = None
	angle = None
	polarization = None
	direction = None
	from_wvl = None
	to_wvl = None
	by_wvl = None
	illuminant = None
	observer = None
	wavelengths = None
	color_space = None
	targets = None
	tolerances = None
	inequality = None
		
	for i in range(len(keywords)):
		keyword = keywords[i]
		value = values[i]
		
		if keyword == "Kind":
			if kind is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Kind must be on a single line")
			kind = value
		
		elif keyword == "Angle":
			if angle is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Angle must be on a single line")
			try:
				angle = float(value)
			except ValueError:
				raise target_error("In target, angle must be a float")
			if angle < 0.0 or angle >= 90.0:
				raise target_error("In target, angle must be between 0 and 90")
		
		elif keyword == "Polarization":
			if polarization is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Polarization must be on a single line")
			try:
				polarization = float(value)
			except ValueError:
				raise target_error("In target, polarization must be a float")
			if angle < 0.0 or angle > 90.0:
				raise target_error("In target, polarization must be between 0 and 90")
		
		elif keyword == "Direction":
			if direction is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Direction must be on a single line")
			if value.upper() == "NORMAL":
				direction = FORWARD
			elif value.upper() == "REVERSE":
				direction = BACKWARD
			else:
				raise target_error("In target, direction must be normal or reverse")
		
		elif keyword == "From":
			if from_wvl is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("From must be on a single line")
			try:
				from_wvl = float(value)
			except ValueError:
				raise target_error("In target, from must be a float")
			if from_wvl <= 0.0:
				raise target_error("In target, from must be positive")
		
		elif keyword == "To":
			if to_wvl is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("To must be on a single line")
			try:
				to_wvl = float(value)
			except ValueError:
				raise target_error("In target, to must be a float")
			if to_wvl <= 0.0:
				raise target_error("In target, to must be positive")
		
		elif keyword == "By":
			if by_wvl is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("By must be on a single line")
			try:
				by_wvl = float(value)
			except ValueError:
				raise target_error("In target, by must be a float")
			if by_wvl < 0.0:
				raise target_error("In target, by must be positive")
		
		elif keyword == "Illuminant":
			if illuminant is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Illuminant must be on a single line")
			illuminant = value
			if not color.illuminant_exists(illuminant):
				raise target_error("Unknown illuminant")
		
		elif keyword == "Observer":
			if observer is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Observer must be on a single line")
			observer = value
			if not color.observer_exists(observer):
				raise target_error("Unknown observer")
		
		elif keyword == "Wavelength":
			if wavelengths is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Wavelength must be on a single line")
			try:
				wavelengths = float(value)
			except ValueError:
				raise target_error("In target, wavelength must be a float")
			if wavelengths <= 0.0:
				raise target_error("In target, wavelength must be positive")
		
		elif keyword == "Value":
			if targets is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Value must be on a single line")
			try:
				targets = float(value)
			except ValueError:
				raise target_error("In target, value must be a float")
		
		elif keyword == "Points":
			if wavelengths is not None or targets is not None or tolerances is not None:
				raise target_error("Multiple definition in target")
			if not isinstance(value, list):
				value = [value]
			wavelengths = []
			targets = []
			tolerances = []
			for line in value:
				elements = line.split()
				if len(elements) != 3:
					raise target_error("In target, the points must be represented by three values")
				try:
					wavelengths.append(float(elements[0]))
					targets.append(float(elements[1]))
					tolerances.append(float(elements[2]))
				except ValueError:
					raise target_error("In target the point values must be floats")
		
		elif keyword in COLOR_SPACES_BY_NAME:
			if targets is not None:
				raise target_error("Multiple definition in target")
			if isinstance(value, list):
				raise target_error("Color target must be on a single line")
			color_space = COLOR_SPACES_BY_NAME[keyword]
			# Separate the 3 elements of the color.
			elements = value.split()
			if len(elements) != 3:
				raise target_error("Color targets must contain three values")
			try:
				value_1 = float(elements[0])
				value_2 = float(elements[1])
				value_3 = float(elements[2])
				targets = [value_1, value_2, value_3]
			except ValueError:
				raise target_error("Color target values must be floats")
		
		elif keyword == "Tolerance":
			if tolerances is not None:
				raise target_error("Multiple value definition in target")
			if isinstance(value, list):
				raise target_error("Tolerance must be on a single line")
			try:
				tolerances = float(value)
			except ValueError:
				raise target_error("In target, tolerance must be a float")
		
		elif keyword == "Tolerances":
			if tolerances is not None:
				raise target_error("Multiple tolerances definition in target")
			if isinstance(value, list):
				raise target_error("Tolerances must be on a single line")
			elements = value.split()
			tolerances = []
			for element in elements:
				try:
					tolerances.append(float(element))
				except ValueError:
					raise target_error("In target, tolerances must be a floats")
		
		elif keyword == "Inequality":
			if inequality is not None:
				raise target_error("Multiple inequality in target")
			if isinstance(value, list):
				raise target_error("Inequality must be on a single line")
			if value.upper() == "SMALLER":
				inequality = SMALLER
			elif value.upper() == "LARGER":
				inequality = LARGER
			else:
				raise target_error("In reflection or transmission target, inequality must be a smaller or larger")
		
		else:
			raise target_error("Unknown keyword %s" % keyword)
	
	if kind is None:
		raise target_error("Must provide kind of target")
	
	# Correct polarization for targets created with branch 1.0.
	if file_version < version.version(1, 1):
		if polarization == S: polarization = P;
		elif polarization == P: polarization = S
	
	# We simply do some sanity checks to be sure the software will not
	# crash. We don't actually check for the validity of the target. If a
	# user modifies the target directly in the saved file, we assume he
	# knows what he is doing!
	
	# Some kinds of targets accept a single target value.
	if kind in DISCRETE_TARGET_KINDS:
		if isinstance(targets, list):
			raise target_error("Incorrect number of values for target")
	
	# If targets is a list, tolerances must also be a list and the same
	# length.
	if isinstance(targets, list) and isinstance(tolerances, list):
		if len(tolerances) != len(targets):
			raise target_error("Incorrect number of tolerances for target")
	elif isinstance(targets, list) or isinstance(tolerances, list):
		raise target_error("Incorrect number of tolerances for target")
	
	# Direction can only be specified for some kinds of filters
	if direction is not None and kind not in REVERSIBLE_TARGET_KINDS:
		raise target_error("Direction cannot be specified for %s target" % kind)
	
	# For phase, GD, and GDD targets, the polarization must be S or P
	# only.
	if polarization is not None and kind in S_OR_P_POLARIZATION_TARGETS and polarization not in S_OR_P_POLARIZATION:
		raise target_error("The polarization for phase, GD, or GDD target can only be S or P")
	
	if kind in DISCRETE_TARGET_KINDS:
		# Verify that all and only the necessary information is given.
		if wavelengths is None or targets is None or tolerances is None:
			raise target_error("%s target must provide wavelength, value and tolerance" % kind)
		if from_wvl is not None or to_wvl is not None or by_wvl is not None or illuminant is not None or observer is not None or color_space is not None:
			raise target_error("Superfluous information in %s target" % kind)
		
		target = TARGETS_BY_NAME[kind]()
		
		target.set_target(wavelengths, targets, tolerances)
	
	elif kind in SPECTRUM_TARGET_KINDS:
		# Verify that all and only the necessary information is given.
		if wavelengths is None or targets is None or tolerances is None or from_wvl is None or to_wvl is None or by_wvl is None:
			raise target_error("%s target must provide from, to, by, wavelength, value and tolerance" % kind)
		if illuminant is not None or observer is not None or color_space is not None:
			raise target_error("Superfluous information in %s target" % kind)
		
		target = TARGETS_BY_NAME[kind]()
		
		target.set_target(from_wvl, to_wvl, by_wvl, wavelengths, targets, tolerances)
	
	elif kind in COLOR_TARGET_KINDS:
		# Verify that all and only the necessary information is given.
		if illuminant is None or observer is None or color_space is None or targets is None or tolerances is None:
			raise target_error("%s target must provide illuminant, observer, color description and tolerances" % kind)
		if from_wvl is not None or to_wvl is not None or by_wvl is not None or wavelengths is not None:
			raise target_error("Superfluous information in %s target" % kind)
		
		target = TARGETS_BY_NAME[kind]()
		
		target.set_illuminant_and_observer(illuminant, observer)
		target.set_target(color_space, targets, tolerances)
	
	else:
		raise target_error("Unknown kind of target")
	
	if angle is not None:
		target.set_angle(angle)
	if polarization is not None:
		target.set_polarization(polarization)
	if direction is not None:
		target.set_direction(direction)
	if inequality is not None:
		target.set_inequality(inequality)
	
	target.set_modified(False)
	
	return target



########################################################################
#                                                                      #
# write_target                                                         #
#                                                                      #
########################################################################
def write_target(target, outfile, prefix = ""):
	"""Write a target
	
	This method takes 2 or 3 arguments:
	  target               the target to write;
	  outfile              the file in which to write;
	  prefix               (optional) of prefix to add to every line in
	                       the file."""
	
	kind = target.get_kind()
	angle = target.get_angle()
	polarization = target.get_polarization()
	direction = target.get_direction()
	inequality = target.get_inequality()
	
	outfile.write(prefix + "Kind: %s\n" % KIND_NAMES[kind])
	outfile.write(prefix + "Angle: %f\n" % angle)
	outfile.write(prefix + "Polarization: %f\n" % polarization)
	if kind in REVERSIBLE_TARGETS:
		if direction == FORWARD:
			outfile.write(prefix + "Direction: Normal\n")
		else:
			outfile.write(prefix + "Direction: Reverse\n")
	
	if kind in DISCRETE_TARGETS:
		wvl, value, delta = target.get_values()
		
		outfile.write(prefix + "Wavelength: %f\n" % wvl[0])
		if value[0] and abs(value[0]) < 1.0e-2:
			outfile.write(prefix + "Value: %e\n" % value[0])
		else:
			outfile.write(prefix + "Value: %f\n" % value[0])
		if abs(delta[0]) < 1.0e-2:
			outfile.write(prefix + "Tolerance: %e\n" % delta[0])
		else:
			outfile.write(prefix + "Tolerance: %f\n" % delta[0])
	
	elif kind in SPECTRUM_TARGETS:
		from_wvl, to_wvl, by_wvl, wvls, values, deltas = target.get_points()
		
		outfile.write(prefix + "From: %f\n" % from_wvl)
		outfile.write(prefix + "To: %f\n" % to_wvl)
		outfile.write(prefix + "By: %f\n" % by_wvl)
		outfile.write(prefix + "Points:\n")
		for i_point in range(len(values)):
			outfile.write(prefix + "\t%15.6f" % wvls[i_point])
			if values[i_point] and abs(values[i_point]) < 1.0e-2:
				outfile.write(" %15.6e" % values[i_point])
			else:
				outfile.write(" %15.6f" % values[i_point])
			if abs(deltas[i_point]) < 1.0e-2:
				outfile.write(" %15.6e\n" % deltas[i_point])
			else:
				outfile.write(" %15.6f\n" % deltas[i_point])
		outfile.write(prefix + "End\n")
	
	elif kind in COLOR_TARGETS:
		illuminant, observer = target.get_illuminant_and_observer()
		color_space = target.get_color_space()
		target_values, tolerances = target.get_values()
		
		outfile.write(prefix + "Illuminant: %s\n" % illuminant)
		outfile.write(prefix + "Observer: %s\n" % observer)
		outfile.write(prefix + "%s: %f %f %f\n" % (COLOR_SPACE_NAMES[color_space], target_values[0], target_values[1], target_values[2]))
		outfile.write(prefix + "Tolerances: %f %f %f\n" % (tolerances[0], tolerances[1], tolerances[2]))
	
	if inequality == SMALLER:
		outfile.write(prefix + "Inequality: smaller\n")
	elif inequality == LARGER:
		outfile.write(prefix + "Inequality: larger\n")
	
	target.set_modified(False)
