# data_holder.py
# 
# Classes to keep calculated data and the conditions in which it was
# calculated.
# 
# Copyright (c) 2006,2007,2009,2015 Stephane Larouche.
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



from definitions import *



# Constants to describe the various data types.
REFLECTION = 0
TRANSMISSION = 1
ABSORPTION = 2
REFLECTION_PHASE = 3
TRANSMISSION_PHASE = 4
REFLECTION_GD = 5
TRANSMISSION_GD = 6
REFLECTION_GDD = 7
TRANSMISSION_GDD = 8
ELLIPSOMETRY = 9
COLOR = 10
COLOR_TRAJECTORY = 11
ADMITTANCE = 12
CIRCLE = 13
ELECTRIC_FIELD = 14
REFLECTION_MONITORING = 15
TRANSMISSION_MONITORING = 16
ELLIPSOMETRY_MONITORING = 17

DISPERSIVE_DATA_TYPES = [REFLECTION_PHASE, TRANSMISSION_PHASE, REFLECTION_GD, TRANSMISSION_GD, REFLECTION_GDD, TRANSMISSION_GDD]

DATA_TYPE_NAMES = {REFLECTION: "Reflection",
                   TRANSMISSION: "Transmission",
                   ABSORPTION: "Absorption",
                   REFLECTION_PHASE: "Reflection phase",
                   TRANSMISSION_PHASE: "Transmission phase",
                   REFLECTION_GD: "Reflection GD",
                   TRANSMISSION_GD: "Transmission GD",
                   REFLECTION_GDD: "Reflection GDD",
                   TRANSMISSION_GDD: "Transmission GDD",
                   ELLIPSOMETRY: "Ellipsometric variables",
                   COLOR: "Color",
                   COLOR_TRAJECTORY: "Color trajectory",
                   ADMITTANCE: "Admittance diagram",
                   CIRCLE: "Circle diagram",
                   ELECTRIC_FIELD: "Electric field distribution",
                   REFLECTION_MONITORING: "Reflection monitoring",
                   TRANSMISSION_MONITORING: "Transmission monitoring",
                   ELLIPSOMETRY_MONITORING: "Ellipsometric variable monitoring"}



########################################################################
#                                                                      #
# data_holder                                                          #
#                                                                      #
########################################################################
class data_holder(object):
	"""A generic data holder
	
	This is a base class for all data holders, it should not be used by
	itself."""
	
	data_type = None
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data):
		"""Initialize the data holder
		
		This method takes 2 arguments:
		  filter             the filter giving the data;
		  data               the data."""
		
		self.data = data
		
		self.angle = None
		self.angles = None
		self.polarization = None
		self.consider_backside = None
		self.ellipsometer_type = None
		self.illuminant = None
		self.observer = None
		self.wavelength = None
		self.wavelengths = None
	
	
	######################################################################
	#                                                                    #
	# get_data_type                                                      #
	# get_data                                                           #
	# get_direction                                                      #
	# get_angle                                                          #
	# get_angles                                                         #
	# get_polarization                                                   #
	# get_consider_backside                                              #
	# get_ellipsometer_type                                              #
	# get_illuminant                                                     #
	# get_observer                                                       #
	# get_wavelength                                                     #
	# get_wavelengths                                                    #
	#                                                                    #
	######################################################################
	
	def get_data_type(self):
		return self.data_type
	
	def get_data(self):
		return self.data
	
	def get_direction(self):
		return self.direction
	
	def get_angle(self):
		return self.angle
	
	def get_angles(self):
		return self.angles
	
	def get_polarization(self):
		return self.polarization
	
	def get_consider_backside(self):
		return self.consider_backside
	
	def get_ellipsometer_type(self):
		return self.ellipsometer_type
	
	def get_illuminant(self):
		return self.illuminant
	
	def get_observer(self):
		return self.observer
	
	def get_wavelength(self):
		return self.wavelength
	
	def get_wavelengths(self):
		return self.wavelengths



########################################################################
#                                                                      #
# spectrum_data                                                        #
#                                                                      #
########################################################################
class spectrum_data(data_holder):
	"""A data holder for spectrophotometric data"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, angle, polarization):
		"""Initialize the data holder
		
		This method takes 4 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  angle              the incidence angle;
		  polarization       the polarization."""
		
		data_holder.__init__(self, filter, data)
		
		self.angle = angle
		self.polarization = polarization
		self.consider_backside = filter.get_consider_backside()
		self.wavelengths = filter.get_wavelengths()



########################################################################
#                                                                      #
# reflection_data                                                      #
#                                                                      #
########################################################################
class reflection_data(spectrum_data):
	"""A data holder for reflection data"""
	
	data_type = REFLECTION
	direction = FORWARD



########################################################################
#                                                                      #
# reflection_reverse_data                                              #
#                                                                      #
########################################################################
class reflection_reverse_data(spectrum_data):
	"""A data holder for reflection in reverse direction data"""
	
	data_type = REFLECTION
	direction = BACKWARD



########################################################################
#                                                                      #
# transmission_data                                                    #
#                                                                      #
########################################################################
class transmission_data(spectrum_data):
	"""A data holder for transmission data"""
	
	data_type = TRANSMISSION
	direction = FORWARD



########################################################################
#                                                                      #
# transmission_reverse_data                                            #
#                                                                      #
########################################################################
class transmission_reverse_data(spectrum_data):
	"""A data holder for transmission in reverse direction data"""
	
	data_type = TRANSMISSION
	direction = BACKWARD



########################################################################
#                                                                      #
# absorption_data                                                      #
#                                                                      #
########################################################################
class absorption_data(spectrum_data):
	"""A data holder for absorption data"""
	
	data_type = ABSORPTION
	direction = FORWARD



########################################################################
#                                                                      #
# absorption_reverse_data                                              #
#                                                                      #
########################################################################
class absorption_reverse_data(spectrum_data):
	"""A data holder for absorption in reverse direction data"""
	
	data_type = ABSORPTION
	direction = BACKWARD



########################################################################
#                                                                      #
# reflection_phase_data                                                #
#                                                                      #
########################################################################
class reflection_phase_data(spectrum_data):
	"""A data holder for reflection phase data"""
	
	data_type = REFLECTION_PHASE
	direction = FORWARD



########################################################################
#                                                                      #
# transmission_phase_data                                              #
#                                                                      #
########################################################################
class transmission_phase_data(spectrum_data):
	"""A data holder for transmission phase data"""
	
	data_type = TRANSMISSION_PHASE



########################################################################
#                                                                      #
# reflection_GD_data                                                   #
#                                                                      #
########################################################################
class reflection_GD_data(spectrum_data):
	"""A data holder for reflection GD data"""
	
	data_type = REFLECTION_GD
	direction = FORWARD



########################################################################
#                                                                      #
# transmission_GD_data                                                 #
#                                                                      #
########################################################################
class transmission_GD_data(spectrum_data):
	"""A data holder for transmission GD data"""
	
	data_type = TRANSMISSION_GD



########################################################################
#                                                                      #
# reflection_GDD_data                                                  #
#                                                                      #
########################################################################
class reflection_GDD_data(spectrum_data):
	"""A data holder for reflection GDD data"""
	
	data_type = REFLECTION_GDD
	direction = FORWARD



########################################################################
#                                                                      #
# transmission_GDD_data                                                #
#                                                                      #
########################################################################
class transmission_GDD_data(spectrum_data):
	"""A data holder for transmission GDD data"""
	
	data_type = TRANSMISSION_GDD



########################################################################
#                                                                      #
# ellipsometry_data                                                    #
#                                                                      #
########################################################################
class ellipsometry_data(data_holder):
	"""A data holder for ellipsometry data"""
	
	data_type = ELLIPSOMETRY
	direction = FORWARD
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, angle):
		"""Initialize the data holder
		
		This method takes 4 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  angle              the incidence angle."""
		
		data_holder.__init__(self, filter, data)
		
		self.angle = angle
		self.consider_backside = filter.get_consider_backside()
		self.ellipsometer_type = filter.get_ellipsometer_type()
		self.wavelengths = filter.get_wavelengths()



########################################################################
#                                                                      #
# ellipsometry_reverse_data                                            #
#                                                                      #
########################################################################
class ellipsometry_reverse_data(ellipsometry_data):
	"""A data holder for ellipsometry in reverse direction data"""
	
	data_type = ELLIPSOMETRY
	direction = BACKWARD



########################################################################
#                                                                      #
# color_data                                                           #
#                                                                      #
########################################################################
class color_data(data_holder):
	"""A data holder for color data"""
	
	data_type = COLOR
	direction = FORWARD
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, angle, polarization, illuminant, observer):
		"""Initialize the data holder
		
		This method takes 6 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  angle              the incidence angle;
		  polarization       the polarization;
		  illuminant         the name of the illuminant;
		  observer           the name of the observer."""
		
		data_holder.__init__(self, filter, data)
		
		self.angle = angle
		self.polarization = polarization
		self.illuminant = illuminant
		self.observer = observer
		self.consider_backside = filter.get_consider_backside()



########################################################################
#                                                                      #
# color_reverse_data                                                   #
#                                                                      #
########################################################################
class color_reverse_data(color_data):
	"""A data holder for color data"""
	
	data_type = COLOR
	direction = BACKWARD



########################################################################
#                                                                      #
# color_trajectory_data                                                #
#                                                                      #
########################################################################
class color_trajectory_data(data_holder):
	"""A data holder for color trajectory data"""
	
	data_type = COLOR_TRAJECTORY
	direction = FORWARD
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, angles, polarization, illuminant, observer):
		"""Initialize the data holder
		
		This method takes 6 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  angles             the incidence angles;
		  polarization       the polarization;
		  illuminant         the name of the illuminant;
		  observer           the name of the observer."""
		
		data_holder.__init__(self, filter, data)
		
		self.angles = angles
		self.polarization = polarization
		self.illuminant = illuminant
		self.observer = observer
		self.consider_backside = filter.get_consider_backside()



########################################################################
#                                                                      #
# color_trajectory_reverse_data                                        #
#                                                                      #
########################################################################
class color_trajectory_reverse_data(color_trajectory_data):
	"""A data holder for color trajectory data"""
	
	data_type = COLOR_TRAJECTORY
	direction = BACKWARD



########################################################################
#                                                                      #
# diagram_data                                                         #
#                                                                      #
########################################################################
class diagram_data(data_holder):
	"""A data holder for diagram data"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, wavelength, angle, polarization):
		"""Initialize the data holder
		
		This method takes 5 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  wavelength         the wavelength;
		  angle              the incidence angle;
		  polarization       the polarization."""
		
		data_holder.__init__(self, filter, data)
		
		self.wavelength = wavelength
		self.angle = angle
		self.polarization = polarization



########################################################################
#                                                                      #
# admittance_data                                                      #
#                                                                      #
########################################################################
class admittance_data(diagram_data):
	"""A data holder for admittance diagram data"""
	
	data_type = ADMITTANCE



########################################################################
#                                                                      #
# circle_data                                                          #
#                                                                      #
########################################################################
class circle_data(diagram_data):
	"""A data holder for circle diagram data"""
	
	data_type = CIRCLE



########################################################################
#                                                                      #
# electric_field_data                                                  #
#                                                                      #
########################################################################
class electric_field_data(diagram_data):
	"""A data holder for electric field data"""
	
	data_type = ELECTRIC_FIELD



########################################################################
#                                                                      #
# photometry_monitoring_data                                           #
#                                                                      #
########################################################################
class photometry_monitoring_data(data_holder):
	"""A data holder for photometric monitoring data"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, wavelengths, angle, polarization):
		"""Initialize the data holder
		
		This method takes 5 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  wavelengths        the wavelengths;
		  angle              the incidence angle;
		  polarization       the polarization."""
		
		data_holder.__init__(self, filter, data)
		
		self.wavelengths = wavelengths
		self.angle = angle
		self.polarization = polarization



########################################################################
#                                                                      #
# reflection_monitoring_data                                           #
#                                                                      #
########################################################################
class reflection_monitoring_data(photometry_monitoring_data):
	"""A data holder for reflection monitoring data"""
	
	data_type = REFLECTION_MONITORING
	direction = FORWARD



########################################################################
#                                                                      #
# reflection_monitoring_reverse_data                                   #
#                                                                      #
########################################################################
class reflection_monitoring_reverse_data(photometry_monitoring_data):
	"""A data holder for reflection monitoring in reverse direction data"""
	
	data_type = REFLECTION_MONITORING
	direction = BACKWARD



########################################################################
#                                                                      #
# transmission_monitoring_data                                         #
#                                                                      #
########################################################################
class transmission_monitoring_data(photometry_monitoring_data):
	"""A data holder for transmission monitoring data"""
	
	data_type = TRANSMISSION_MONITORING
	direction = FORWARD



########################################################################
#                                                                      #
# transmission_monitoring_reverse_data                                 #
#                                                                      #
########################################################################
class transmission_monitoring_reverse_data(photometry_monitoring_data):
	"""A data holder for transmission monitoring in reverse direction data"""
	
	data_type = TRANSMISSION_MONITORING
	direction = BACKWARD



########################################################################
#                                                                      #
# ellipsometry_monitoring_data                                         #
#                                                                      #
########################################################################
class ellipsometry_monitoring_data(data_holder):
	"""A data holder for ellipsometry monitoring data"""
	
	data_type = ELLIPSOMETRY_MONITORING
	direction = FORWARD
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, data, wavelengths, angle):
		"""Initialize the data holder
		
		This method takes 5 arguments:
		  filter             the filter giving the data;
		  data               the data;
		  wavelengths        the wavelengths;
		  angle              the incidence angle."""
		
		data_holder.__init__(self, filter, data)
		
		self.wavelengths = wavelengths
		self.angle = angle



########################################################################
#                                                                      #
# ellipsometry_monitoring_reverse_data                                 #
#                                                                      #
########################################################################
class ellipsometry_monitoring_reverse_data(ellipsometry_monitoring_data):
	"""A data holder for ellipsometry monitoring in reverse direction data"""
	
	data_type = ELLIPSOMETRY_MONITORING
	direction = BACKWARD
