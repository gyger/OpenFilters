# optimization_Fourier.py
# 
# Design of optical filters with the Fourier transform method.
#
# Copyright (c) 2000-2010 Stephane Larouche.
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
import cmath

from definitions import *
import config
from optimization import optimization, optimization_error
import abeles
from targets import R_SPECTRUM_TARGET, R_PHASE_SPECTRUM_TARGET
import graded
from moremath import Levenberg_Marquardt

Q_function_choices = ["Delano", "Sossi", "Bovard", "Chang"]
Q_function_descriptions = ["sqrt(R/T)", "sqrt(0.5*(1/T-T))", "0.5*ln((1+sqrt(R))/(1-sqrt(R)))", "Microw. Opt. Techn. Let., vol. 22, pp. 140-144"]



one_hundred_eighty_over_pi = 180.0/math.pi



########################################################################
#                                                                      #
# optimization_Fourier                                                 #
#                                                                      #
########################################################################
class optimization_Fourier(optimization):
	"""A class to design an optical filter using the Fourier transform
	method"""
	
	
	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, filter, targets, parent = None):
		"""Initialize an instance of the optimization class
		
		This method takes 2 or 3 arguments:
		  filter             the filter being optimized;
		  targets            the targets used in the optimization;
		  parent             (optional) the user interface used to do the
		                     optimization.
		
		If given, the parent must implement an update method taking two
		arguments (working, status)."""
		
		optimization.__init__(self, filter, targets, parent)
		
		# Stop criteria.
		self.max_iterations = config.FOURIER_MAX_ITERATIONS
		self.acceptable_chi_2 = config.FOURIER_ACCEPTABLE_CHI_2
		self.min_chi_2_change = config.FOURIER_MIN_CHI_2_CHANGE
		
		# Find the first reflection spectrum at normal incidence in the
		# targets.
		for i in range(len(self.targets)):
			target = self.targets[i]
			if target.get_kind() == R_SPECTRUM_TARGET and target.get_angle() == 0.0:
				break
		else:
			raise optimization_error("The Fourier transform method needs a reflection spectrum target at normal incidence")
		
		# Get the spectrum of the target.
		self.wvls, self.R_target, self.R_tolerances = target.get_values()
		self.nb_wvls = len(self.wvls)
		
		# The Fourier transform method doesn't tolerate reflection to be
		# exactly 1.
		for i in range(self.nb_wvls):
			if self.R_target[i] == 1.0:
				self.R_target[i] = 0.99
		
		# For the time being we don't accept phase targets.
		self.phi_target = None
		self.phi_tolerances = None
		
		# Prepare k.
		self.k = [2.0*math.pi/self.wvls[i] for i in range(self.nb_wvls)]
		
		# Prepare wavelengths object.
		self.wvls_ = abeles.wvls(self.nb_wvls)
		for i_wvl in range(self.nb_wvls):
			self.wvls_.set_wvl(i_wvl, self.wvls[i_wvl])
		
		# Prepare objects from the abeles module that will be reused to
		# reduce creation time.
		self.sin2_theta_0 = abeles.sin2(self.wvls_)
		self.global_matrices = abeles.matrices(self.wvls_)
		self.temp_matrices = abeles.matrices(self.wvls_)
		self.r_and_t = abeles.r_and_t(self.wvls_)
		
		# This variable will be used for the index object.
		self.N = None
		
		# The center wavelength is obtained from the filter.
		self.center_wavelength = self.filter.get_center_wavelength()
		
		# The parameters are obtained from the filter. If the filter
		# doesn't define the parameters, default values are used.
		parameters = self.filter.get_Fourier_parameters()
		if parameters:
			self.material_name = parameters[0]
			self.Q_function = parameters[1]
			self.OT = parameters[2]
		else:
			self.material_name = config.FOURIER_MATERIAL
			self.Q_function = config.FOURIER_Q_FUNCTION
			self.OT = config.FOURIER_OT
		
		# Prepare variables for optimization.
		self.prepare_material()
		
		# Set the iteration number to 0 and create variables to keep the
		# result of iterations.
		self.reset()
	
	
	######################################################################
	#                                                                    #
	# set_Q_function                                                     #
	#                                                                    #
	######################################################################
	def set_Q_function(self, Q_function):
		"""Set the Q function
		
		This method takes a single argument:
		  Q_function         the Q function."""
		
		if Q_function != self.Q_function:
			self.Q_function = Q_function
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# get_Q_function                                                     #
	#                                                                    #
	######################################################################
	def get_Q_function(self):
		"""Get the Q function
		
		This method returns the Q function."""
		
		return self.Q_function
	
	
	######################################################################
	#                                                                    #
	# set_material                                                       #
	#                                                                    #
	######################################################################
	def set_material(self, material_name):
		"""Set the material
		
		This method takes a single argument:
		  material_name      the name of the material."""
		
		if material_name != self.material_name:
			self.material_name = material_name
			self.prepare_material()
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# get_material                                                       #
	#                                                                    #
	######################################################################
	def get_material(self):
		"""Get the material
		
		This method returns the name of the material."""
		
		return self.material_name
	
	
	######################################################################
	#                                                                    #
	# set_OT                                                             #
	#                                                                    #
	######################################################################
	def set_OT(self, OT):
		"""Set the optical thickness
		
		This method takes a single argument:
		  OT                 the optical thickness."""
		
		if OT != self.OT:
			self.OT = OT
			self.prepare_OT()
			self.reset()
	
	
	######################################################################
	#                                                                    #
	# get_OT                                                             #
	#                                                                    #
	######################################################################
	def get_OT(self):
		"""Get the optical thickness
		
		This method returns the optical thickness."""
		
		return self.OT
	
	
	######################################################################
	#                                                                    #
	# prepare_material                                                   #
	#                                                                    #
	######################################################################
	def prepare_material(self):
		"""Prepare the material
		
		Prepare the instance attribures related to the material."""
		
		if self.material_name:
			self.material_nb = self.filter.get_material_nb(self.material_name)
			self.material = self.filter.get_material(self.material_nb)
			self.steps = self.filter.get_material_index(self.material_nb)
			self.N_min, self.N_max = self.material.get_index_range(self.center_wavelength)
			self.n_0 = math.sqrt(self.N_min*self.N_max)
			
			# We need the step spacing to choose the sublayer OT. If the step
			# spacing is defined by the deposition, find the smallest step
			# spacing.
			step_spacing = self.filter.get_step_spacing()
			if step_spacing == DEPOSITION_STEP_SPACING:
				step_spacing = steps[1]-steps[0]
				for i_step in range(2, len(steps)):
					step_spacing = min(step_spacing, steps[i_step] - steps[i_step-1])
			
			# To calculate the sublayer OT, we choose the worst case, that is
			# a filter covering all the index range and having the smallest
			# period. In one quarter wave, the profile passes by all the
			# steps in its amplitude.
			amplitude = self.N_max - self.N_min
			quarter_wave = 0.25*self.center_wavelength
			nb_steps_in_full_amplitude = amplitude/step_spacing
			self.sublayer_OT = quarter_wave/nb_steps_in_full_amplitude
			
			self.N = self.material.get_N(self.wvls_)
			self.N.prepare_N_mixture_graded(len(self.steps))
			for i_mixture in range(len(self.steps)):
				self.N.set_N_mixture_graded(i_mixture, self.steps[i_mixture], self.center_wavelength)
			
			# Prepare the multiplicative correction factor to account for the
			# variation of the amplitude of the index of refraction.
			self.K = [0.0]*self.nb_wvls
			n_min_0, n_max_0 = self.material.get_index_range(self.center_wavelength)
			ln_0 = math.log(n_max_0/n_min_0)
			for i_wvl in range(self.nb_wvls):
				N_min, N_max = self.material.get_index_range(self.wvls[i_wvl])
				self.K[i_wvl] = ln_0/math.log(N_max/N_min)
		
		else:
			self.material_nb = None
			self.material = None
			self.steps = []
			self.N_min, self.N_max = 0.0, 0.0
			self.n_0 = 0.0
			
			self.sublayer_OT = 0.0
			
			self.N = None
		
		# The sublayer OT has changed, it is necessary to recalculate
		# the step thicknesses.
		self.prepare_OT()
	
	
	######################################################################
	#                                                                    #
	# prepare_OT                                                         #
	#                                                                    #
	######################################################################
	def prepare_OT(self):
		"""Prepare the optical
		
		Prepare the instance attribures related to the optical thickness."""
		
		if self.sublayer_OT == 0.0:
			self.x = []
		else:
			# We determine the range of optical thickness that interest us.
			self.x = [i_x*self.sublayer_OT for i_x in range(int(math.ceil(self.OT/self.sublayer_OT)+1))]
			self.x[-1] = self.OT
	
	
	######################################################################
	#                                                                    #
	# reset                                                              #
	#                                                                    #
	######################################################################
	def reset(self):
		"""Reset the optimization"""
		
		self.max_iterations_reached = False
		self.status = 0
		self.stop_criteria_met = False
		
		self.iteration = 0
		
		self.Q_i = []
		self.Psi_i = []
		
		self.step_thickness = [0.0]
		self.step_profile = [0]
		self.depth = []
		self.index_profile = []
		
		# Calculate Q and Psi for the target.
		if self.phi_target:
			self.Q, self.Psi = self.calculate_Q_function(self.R_target, self.phi_target)
		else:
			self.Q, self.Psi = self.calculate_Q_function(self.R_target, [0.0]*self.nb_wvls)
		
		# Calculate the reflection and phase.
		self.R, self.phi = self.calculate_performance(self.step_profile, self.step_thickness)
		
		# Calculate chi square.
		self.chi_2 = 0.0
		for i_wvl in range(self.nb_wvls):
			delta = (self.R[i_wvl] - self.R_target[i_wvl]) / self.R_tolerances[i_wvl]
			self.chi_2 += delta*delta
		if self.phi_target:
			for i_wvl in range(self.nb_wvls):
				delta = (phi[i_wvl] - self.phi_target[i_wvl]) / self.phi_tolerances[i_wvl]
				self.chi_2 += delta*delta
	
	
	######################################################################
	#                                                                    #
	# calculate_Q_function                                               #
	#                                                                    #
	######################################################################
	def calculate_Q_function(self, R, phi):
		"""Calculate the Q function
		
		This method takes 2 arguments:
		  R                  the reflection spectrum;
		  phi                the phase spectrum;
		and return 2 arguments:
		  Q                  the amplitude Q function;
		  Psi                the phase Q function."""
		
		
		if self.Q_function == "Delano":
			Q = [math.sqrt(R[i]/(1.0-R[i])) for i in range(self.nb_wvls)]
			Psi = [0.0]*self.nb_wvls
		
		elif self.Q_function == "Sossi":
			Q = [math.sqrt(0.5*(1/(1.0-R[i])-(1.0-R[i]))) for i in range(self.nb_wvls)]
			Psi = [0.0]*self.nb_wvls
		
		elif self.Q_function == "Bovard":
			Q = [0.5*math.log((1.0+math.sqrt(R[i]))/(1.0-math.sqrt(R[i]))) for i in range(self.nb_wvls)]
			Psi = [0.0]*self.nb_wvls
		
		elif self.Q_function == "Chang":
			Q = [0.0]*self.nb_wvls
			Psi = [0.0]*self.nb_wvls
			for i in range(self.nb_wvls):
				one_minus_R = 1.0-R[i]
				sin_phi = math.sin(math.radians(phi[i]))
				sqrt_R = math.sqrt(R[i])
				A = math.log((math.sqrt(one_minus_R*one_minus_R+4.0*R[i]*sin_phi*sin_phi))/(1.0-2.0*sqrt_R*math.cos(phi[i])+R[i]))
				B = math.atan2(2.0*sqrt_R*sin_phi, one_minus_R)
				Q[i] = 0.5*math.sqrt(A*A+B*B)
				Psi[i] = math.atan2(B,A)
		
		return Q, Psi
	
	
	######################################################################
	#                                                                    #
	# calculate_performance                                              #
	#                                                                    #
	######################################################################
	def calculate_performance(self, step_profile, step_thickness):
		"""Calculate the performance of the filter
		
		This method takes 2 arguments
		  step_profile       a list of the steps of the filter;
		  step_thickness     a list of the  thicknesses of the steps;
		and returns the reflection spectrum of the filter."""
		
		R = abeles.R(self.wvls_)
		phase = abeles.phase(self.wvls_)
		
		nb_sublayers = len(step_thickness)
		
		# Consider the outermost sublayers as substrate and medium.
		pseudo_n_substrate = self.N.get_N_mixture_graded(step_profile[0])
		pseudo_n_medium = self.N.get_N_mixture_graded(step_profile[-1])
		
		# Set sin2_theta_0 for a normal angle of incidence.
		self.sin2_theta_0.set_sin2_theta_0(pseudo_n_medium, 0.0)
		
		# Multiply matrices.
		self.global_matrices.set_matrices_unity()
		for i_sublayer in range(nb_sublayers):
			index = self.N.get_N_mixture_graded(step_profile[i_sublayer])
			self.temp_matrices.set_matrices(index, step_thickness[i_sublayer], self.sin2_theta_0)
			self.global_matrices.multiply_matrices(self.temp_matrices)
		
		# Calculate reflexion and phase.
		self.r_and_t.calculate_r_and_t(self.global_matrices, pseudo_n_medium, pseudo_n_substrate, self.sin2_theta_0)
		R.calculate_R(self.r_and_t, S)
		phase.calculate_r_phase(self.global_matrices, pseudo_n_medium, pseudo_n_substrate, self.sin2_theta_0, S)
		
		phi = [phase_i*one_hundred_eighty_over_pi for phase_i in phase]
		
		return R, phi
	
	
	######################################################################
	#                                                                    #
	# iterate_                                                           #
	#                                                                    #
	######################################################################
	def iterate_(self):
		"""Do one iteration
		
		One iteration of the calculation of the index as a function of
		the thickness according to the procedure in Chang et al.
		"Inhomogeneous optical filter design with the use of a Riccati
		equation", Microwave and optical technology letters, v. 22,
		no. 2, 1999, pp. 140-144."""
		
		# Calculation of Q and Psi for this iteration.
		if self.iteration == 0:
			Q_m = self.Q[:]
			Psi_m = self.Psi[:]
		else:
			if self.phi_target:
				Q_design, Psi_design = self.calculate_Q_function(self.R, self.phi) 
			else:
				Q_design, Psi_design = self.calculate_Q_function(self.R, [0.0]*self.nb_wvls) 
			
			Q_m = [self.Q[i_wvl]*self.Q_i[-1][i_wvl]/Q_design[i_wvl] for i_wvl in range(self.nb_wvls)]
			Psi_m = self.Psi[:]
		
		# Perform a correction on the wavelength axis of the Q function
		# to account for the dispersion. Since the Fourier transform method
		# operates with wavenumbers, the inverse correction is calculated.
		# At the first iteration, the mean index is used to determine the
		# correction factor.
		if self.iteration == 0:
			self.N.set_N_mixture(self.n_0, self.center_wavelength)
			n_mixture = self.N.get_N_mixture()
			k_corrected = [self.k[i_wvl]*n_mixture[i_wvl].real/self.n_0 for i_wvl in range(self.nb_wvls)]
		else:
			# Calculate the optical thickness for every wavelength.
			optical_thickness = [0.0]*self.nb_wvls
			for i_sublayer in range(len(self.step_thickness)):
				n_sublayer = self.N.get_N_mixture_graded(self.step_profile[i_sublayer])
				sublayer_thickness = self.step_thickness[i_sublayer]
				for i_wvl in range(self.nb_wvls):
					optical_thickness[i_wvl] += n_sublayer[i_wvl].real * sublayer_thickness
			
			k_corrected = [self.k[i_wvl]*optical_thickness[i_wvl]/self.OT for i_wvl in range(self.nb_wvls)]
		
		# A multiplicative correction factor is also applied on the Q
		# function to account for the variation of the amplitude of the
		# index of refraction.
		for i_wvl in range(self.nb_wvls):
			Q_m[i_wvl] *= self.K[i_wvl]
		
		# Calculate dk as half the distance between the previous point
		# and the next point. Exception occurs at the extremities. The
		# substraction are taken in reverse order since k is in reverse
		# order
		dk = [0.0]*self.nb_wvls
		dk[0] = 0.5*(k_corrected[0]-k_corrected[1])
		for i_wvl in range(1, self.nb_wvls-1):
			dk[i_wvl] = 0.5*(k_corrected[i_wvl-1]-k_corrected[i_wvl+1])
		dk[-1] = 0.5*(k_corrected[-2]-k_corrected[-1])
		
		# Then, we calculate the value of the first right term in eq. 9.
		nb_x = len(self.x)
		first_term = [0.0]*nb_x
		for i_x in range(nb_x):
			x = self.x[i_x]
			# Calculation of the integral, Q is considered nul out of
			# the specified range. Since this calculation is long, it is
			# worth verifying that Q_m is not null.
			integral = 0.0
			for i_wvl in range(self.nb_wvls):
				if Q_m[i_wvl] != 0.0:
					integral += (Q_m[i_wvl]/k_corrected[i_wvl])*math.sin(Psi_m[i_wvl]-k_corrected[i_wvl]*2.0*(x-0.5*self.OT))*dk[i_wvl]
			first_term[i_x] = integral/math.pi
		
		# We calculate the index of refraction as a function of optical
		# thickness.
		index_profile = [self.n_0*math.exp(2.0*first_term[i_x]) for i_x in range(nb_x)]
		
		# Clip the index to the available range.
		for i_x in range(nb_x):
			if index_profile[i_x] < self.N_min:
				index_profile[i_x] = self.N_min
			elif index_profile[i_x] > self.N_max:
				index_profile[i_x] = self.N_max
		
		# Transform the index profile into steps.
		step_profile, step_thickness = graded.index_profile_in_OT_to_steps(index_profile, self.x, self.steps)
		
		# Calculate the performance.
		R, phi = self.calculate_performance(step_profile, step_thickness)
		
		# Calculate chi square.
		new_chi_2 = 0.0
		for i_wvl in range(self.nb_wvls):
			delta = (R[i_wvl] - self.R_target[i_wvl]) / self.R_tolerances[i_wvl]
			new_chi_2 += delta*delta
		if self.phi_target:
			for i_wvl in range(self.nb_wvls):
				delta = (phi[i_wvl] - self.phi_target[i_wvl]) / self.phi_tolerances[i_wvl]
				new_chi_2 += delta*delta
		
		if new_chi_2 <= self.chi_2:
			# Verify if one of the stop criteria is met:
			if new_chi_2 <= self.acceptable_chi_2:
				self.status = Levenberg_Marquardt.CHI_2_IS_OK
			elif 1.0 - (new_chi_2 / self.chi_2) < self.min_chi_2_change:
				self.status = Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL
			else:
				self.status = Levenberg_Marquardt.IMPROVING
			
			# Save the changes.
			self.index_profile = index_profile
			self.step_profile = step_profile
			self.step_thickness = step_thickness
			self.depth, self.index_profile = graded.steps_to_index_profile(self.step_thickness, self.step_profile, self.steps)
			self.chi_2 = new_chi_2
			self.Q_i.append(Q_m[:])
			self.Psi_i.append(Psi_m[:])
			self.R = R
			self.phi = phi
			
			self.iteration += 1
		
		else:
			self.status = Levenberg_Marquardt.DELTA_IS_TOO_SMALL
 		
 		# Stop if the solution is not improving.
 		if self.status != Levenberg_Marquardt.IMPROVING:
			self.stop_criteria_met = True
 		
 		# Verify if the maximum number of iterations has been reached (when
 		# specified).
 		if self.max_iterations and self.iteration >= self.max_iterations:
 			self.max_iterations_reached = True
	
	
	######################################################################
	#                                                                    #
	# get_index_profile                                                  #
	#                                                                    #
	######################################################################
	def get_index_profile(self):
		"""Get the index profile
		
		This method returns the index profile (depth, index)."""
		
		return self.depth, self.index_profile
	
	
	######################################################################
	#                                                                    #
	# get_calculated_values                                              #
	#                                                                    #
	######################################################################
	def get_calculated_values(self):
		"""Get the calculated properties
		
		This method returns the reflection spectrum and phase (wvls, R,
		phi)."""
		
		return self.wvls, self.R, self.phi
	
	
	######################################################################
	#                                                                    #
	# copy_to_filter                                                     #
	#                                                                    #
	######################################################################
	def copy_to_filter(self):
		"""Copy the optimized filter to the filter instance"""
		
		self.filter.set_Fourier_parameters((self.material_name, self.Q_function, self.OT))
		
		self.filter.clear_design()
		if self.index_profile != []:
			self.filter.add_graded_layer_from_steps_with_material_nb(self.material_nb, self.step_profile, self.step_thickness)
	
	
	######################################################################
	#                                                                    #
	# save_index_profile                                                 #
	#                                                                    #
	######################################################################
	def save_index_profile(self, outfile):
		"""Save the index profile
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		outfile.write("%10s  %7s\n" %("depth", "N"))
		for i in range(len(self.depth)):
			outfile.write("%10.2f  %7.4f\n" %(self.depth[i], self.index_profile[i]))
	
	
	######################################################################
	#                                                                    #
	# save_values                                                        #
	#                                                                    #
	######################################################################
	def save_values(self, outfile):
		"""Save the current values of the optimized properties
		
		This method takes one argument:
		  outfile            the file in which to write."""
		
		outfile.write("%10s  %10s  %10s\n" %("wvl", "target", "result"))
		for i_wvl in range(len(self.wvls)):
			outfile.write("%10.3f  %10.4f  %10.4f\n" %(self.wvls[i_wvl], self.R_target[i_wvl], self.R[i_wvl]))
