# monitoring.py
# 
# A class to calculate characteristic matrices adapted for
# monitoring purposes.
# 
# Copyright (c) 2004,2005,2007,2008 Stephane Larouche.
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



from matrices import *



########################################################################
#                                                                      #
# monitoring_matrices                                                  #
#                                                                      #
########################################################################
class monitoring_matrices(object):
	"""A class to calculate characteristic matrices adapted for
	monitoring purposes"""


	######################################################################
	#                                                                    #
	# __init__                                                           #
	#                                                                    #
	######################################################################
	def __init__(self, wvls, length):
		"""Initialize an instance of the monitoring_matrices class to store
		the characteristic matrix necessary to calculate monitoring curves
		
		This method takes 2 arguments:
		  wvls              the wavelengths at which to calculate the
		                    monitoring matrices;
		  length            the number of sublayers.
		
		When calculating a monitoring curve, a layer must be seperated in
		multiple slices and the property being monitored calculated
		after the addition of each of these slices. The monitoring
		matrices instance keeps the characteristic matrices
		corresponding to all the slices to allow the calculation of the
		curves."""
	
		self.length = length
		
		self.wvls = wvls
		self.thicknesses = [0.0]*self.length
		self.matrices = [matrices(wvls) for i in range(self.length)]
	
	
	######################################################################
	#                                                                    #
	# set_monitoring_matrices                                            #
	#                                                                    #
	######################################################################
	def set_monitoring_matrices(self, position, N, slice_thickness, sin2_theta_0):
		"""Set the caracteristic matrices of one slice
		
		This method takes 5 arguments:
		  slice             the number of the sublayer;
		  N                 the index of refraction of the sublayer;
		  slice_thickness   the thickness of the slice;
		  sin2_theta_0      the normalized sinus squared of the propagation
		                    angle."""
		
		self.matrices[position].set_matrices(N, slice_thickness, sin2_theta_0);
	
	
	######################################################################
	#                                                                    #
	# multiply_monitoring_matrices                                       #
	#                                                                    #
	######################################################################
	def multiply_monitoring_matrices(self, M1):
		"""Multiply the monitoring matrices
		
		This method takes 1 argument:
		  M1                the matrices corresponding to the layers
		                    below the one currently being monitored.
		
		This function calculates the product of M1 with the matrix of
		every slice in the instance used to call this method and stores
		the result in the instance. This method is meant to be used for
		homogeneous layers."""
		
		# multiply_matrices is not used because the answer must be kept in M2
		# (multiply_matrices keeps it in M1) and the supplementary
		# copy_matrices operation would increase the calculation time by about
		# 10% (I tried it).
		
		for i_slice in range(self.length):
			
			M = self.matrices[i_slice]
			
			for i_wvl in range(M1.wvls.length):
				temp0 = M.s[i_wvl][0]*M1.s[i_wvl][0] + M.s[i_wvl][1]*M1.s[i_wvl][2]
				temp1 = M.s[i_wvl][0]*M1.s[i_wvl][1] + M.s[i_wvl][1]*M1.s[i_wvl][3]
				temp2 = M.s[i_wvl][2]*M1.s[i_wvl][0] + M.s[i_wvl][3]*M1.s[i_wvl][2]
				M.s[i_wvl][3] = M.s[i_wvl][2]*M1.s[i_wvl][1] + M.s[i_wvl][3]*M1.s[i_wvl][3]
				M.s[i_wvl][0] = temp0
				M.s[i_wvl][1] = temp1
				M.s[i_wvl][2] = temp2
				
				temp0 = M.p[i_wvl][0]*M1.p[i_wvl][0] + M.p[i_wvl][1]*M1.p[i_wvl][2]
				temp1 = M.p[i_wvl][0]*M1.p[i_wvl][1] + M.p[i_wvl][1]*M1.p[i_wvl][3]
				temp2 = M.p[i_wvl][2]*M1.p[i_wvl][0] + M.p[i_wvl][3]*M1.p[i_wvl][2]
				M.p[i_wvl][3] = M.p[i_wvl][2]*M1.p[i_wvl][1] + M.p[i_wvl][3]*M1.p[i_wvl][3]
				M.p[i_wvl][0] = temp0
				M.p[i_wvl][1] = temp1
				M.p[i_wvl][2] = temp2
	
	
	######################################################################
	#                                                                    #
	# multiply_monitoring_matrices_cumulative                            #
	#                                                                    #
	######################################################################
	def multiply_monitoring_matrices_cumulative(self, M1):
		"""Multiply the monitoring matrices cumulatively
		
		This method takes 1 argument:
		  M1                the matrices corresponding to the layers
		                    below the one currently being monitored.
		
		This function calculates the product of M1 with the matrix of
		every slice in the instance used to call this method cumulatively
		and stores the result in the instance. This method is meant to be
		used for graded-index layers."""
		
		total_thickness = 0.0
		M_pre = M1
		
		for i_slice in range(self.length):
			M = self.matrices[i_slice]
			
			for i_wvl in range(M1.wvls.length):
				temp0 = M.s[i_wvl][0]*M_pre.s[i_wvl][0] + M.s[i_wvl][1]*M_pre.s[i_wvl][2];
				temp1 = M.s[i_wvl][0]*M_pre.s[i_wvl][1] + M.s[i_wvl][1]*M_pre.s[i_wvl][3];
				temp2 = M.s[i_wvl][2]*M_pre.s[i_wvl][0] + M.s[i_wvl][3]*M_pre.s[i_wvl][2];
				M.s[i_wvl][3] = M.s[i_wvl][2]*M_pre.s[i_wvl][1] + M.s[i_wvl][3]*M_pre.s[i_wvl][3];
				M.s[i_wvl][0] = temp0;
				M.s[i_wvl][1] = temp1;
				M.s[i_wvl][2] = temp2;
				
				temp0 = M.p[i_wvl][0]*M_pre.p[i_wvl][0] + M.p[i_wvl][1]*M_pre.p[i_wvl][2];
				temp1 = M.p[i_wvl][0]*M_pre.p[i_wvl][1] + M.p[i_wvl][1]*M_pre.p[i_wvl][3];
				temp2 = M.p[i_wvl][2]*M_pre.p[i_wvl][0] + M.p[i_wvl][3]*M_pre.p[i_wvl][2];
				M.p[i_wvl][3] = M.p[i_wvl][2]*M_pre.p[i_wvl][1] + M.p[i_wvl][3]*M_pre.p[i_wvl][3];
				M.p[i_wvl][0] = temp0;
				M.p[i_wvl][1] = temp1;
				M.p[i_wvl][2] = temp2;
			
			M_pre = M;


	######################################################################
	#                                                                    #
	# __len__                                                            #
	#                                                                    #
	######################################################################
	def __len__(self):
		"""Get the number of slices
		
		This method is called when len(instance) is used. It returns the
		number of slices for which the monitoring is done."""
	
		return self.length


	######################################################################
	#                                                                    #
	# __getitem__                                                        #
	#                                                                    #
	######################################################################
	def __getitem__(self, key):
		"""Get items of the monitoring matrices
		
		This method is called when instance[key] is used. It returns the
		the characteristic matrices of the slices requested by the key."""
	
		return self.matrices[key]
