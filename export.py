# export.py
# 
# Export the filters and the results in various formats.
#
# Copyright (c) 2004-2010,2013,2015 Stephane Larouche.
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
from data_holder import REFLECTION,\
                        TRANSMISSION,\
                        ABSORPTION,\
                        REFLECTION_PHASE,\
                        TRANSMISSION_PHASE,\
                        REFLECTION_GD,\
                        TRANSMISSION_GD,\
                        REFLECTION_GDD,\
                        TRANSMISSION_GDD,\
                        ELLIPSOMETRY,\
                        COLOR,\
                        COLOR_TRAJECTORY,\
                        ADMITTANCE,\
                        CIRCLE,\
                        ELECTRIC_FIELD,\
                        REFLECTION_MONITORING,\
                        TRANSMISSION_MONITORING,\
                        ELLIPSOMETRY_MONITORING,\
                        DATA_TYPE_NAMES



SPECTROPHOTOMETRIC_DATA_TYPES = [REFLECTION,\
                                 TRANSMISSION,\
                                 ABSORPTION,\
                                 REFLECTION_PHASE,\
                                 TRANSMISSION_PHASE,\
                                 REFLECTION_GD,\
                                 TRANSMISSION_GD,\
                                 REFLECTION_GDD,\
                                 TRANSMISSION_GDD]

DIAGRAM_DATA_TYPES = [ADMITTANCE, CIRCLE]

SPECTROPHOTOMETRIC_MONITORING_TYPES = [REFLECTION_MONITORING, TRANSMISSION_MONITORING]

COLUMN_TITLES = {REFLECTION: "R",
                 TRANSMISSION: "T",
                 ABSORPTION: "A",
                 REFLECTION_PHASE: "phase (deg.)",
                 TRANSMISSION_PHASE: "phase (deg.)",
                 REFLECTION_GD: "GD (s)",
                 TRANSMISSION_GD: "GD (s)",
                 REFLECTION_GDD: "GDD (s^2)",
                 TRANSMISSION_GDD: "GDD (s^2)",
                 REFLECTION_MONITORING: "R",
                 TRANSMISSION_MONITORING: "T"}



########################################################################
#                                                                      #
# export_index_profile                                                 #
#                                                                      #
########################################################################
def export_index_profile(filename, filter, side = FRONT):
	"""Export the index profile of a filter to a file
	
	This function takes 3 arguments:
	  filename        the name of the file in which to write;
	  filter          the filter;
	  side            the side."""
	
	outfile = open(filename, "w")
	
	thickness, n = filter.get_index_profile(side)			
	
	outfile.write("  Depth (nm)    n at %7.2f nm\n" % filter.get_center_wavelength())
	for i in range(len(thickness)):
		outfile.write("%10.3f  %17.6f\n" % (thickness[i], n[i]))
	outfile.close()



########################################################################
#                                                                      #
# export_results_to_text                                               #
#                                                                      #
########################################################################
def export_results_to_text(filename, results):
	"""Export results to a file
	
	This function takes 3 arguments:
	  filename        the name of the file in which to write;
	  results         a list of results to export.
	
	The results must be data_handler instances. All results are exported
	in a single file."""
	
	outfile = open(filename, "w")
	
	for result in results:
		
		data_type = result.get_data_type()
		
		if data_type in SPECTROPHOTOMETRIC_DATA_TYPES:
			
			# Get the data and the properties.
			angle = result.get_angle()
			polarization = result.get_polarization()
			wavelengths = result.get_wavelengths()
			spectrum = result.get_data()
			
			# Write the header
			outfile.write("%s at %.2f degrees for %s\n" % (DATA_TYPE_NAMES[data_type], angle, polarization_text(polarization)))
			outfile.write("%15s %15s\n" % ("wavelength (nm)", COLUMN_TITLES[data_type]))
			
			# Write the data
			for i_wvl in range(len(wavelengths)):
				if spectrum[i_wvl] < 1.0e-2:
					outfile.write("%15.6f %15.6e\n" % (wavelengths[i_wvl], spectrum[i_wvl]))
				else:
					outfile.write("%15.6f %15.6f\n" % (wavelengths[i_wvl], spectrum[i_wvl]))
			
		elif data_type == ELLIPSOMETRY:
			# Get the data and the properties.
			angle = result.get_angle()
			wavelengths = result.get_wavelengths()
			Psi, Delta = result.get_data()
			
			# Write the header
			outfile.write("%s at %.2f degrees\n" % (DATA_TYPE_NAMES[data_type], angle))
			outfile.write("%15s %15s %15s\n" % ("wavelength (nm)", "Psi (deg.)", "Delta (deg.)"))
			
			# Write the data
			for i in range(len(wavelengths)):
				outfile.write("%15.6f %15.6f %15.6f\n" % (wavelengths[i], Psi[i], Delta[i]))
			
		elif data_type == COLOR:
			# Get the data and the properties.
			angle = result.get_angle()
			illuminant = result.get_illuminant()
			observer = result.get_observer()
			R_color, T_color = result.get_data()
			
			# Write the header
			outfile.write("%s at %.2f degrees (%s, %s)\n" % (DATA_TYPE_NAMES[data_type], angle, illuminant, observer))
			outfile.write("%10s %15s %15s\n" % ("", "R", "T"))
			XYZ_R = R_color.XYZ()
			xyY_R = R_color.xyY()
			Luv_R = R_color.Luv()
			Lab_R = R_color.Lab()
			LChuv_R = R_color.LChuv()
			LChab_R = R_color.LChab()
			XYZ_T = T_color.XYZ()
			xyY_T = T_color.xyY()
			Luv_T = T_color.Luv()
			Lab_T = T_color.Lab()
			LChuv_T = T_color.LChuv()
			LChab_T = T_color.LChab()
			outfile.write("%10s %15.6f %15.6f\n" % ("X", XYZ_R[0], XYZ_T[0]))
			outfile.write("%10s %15.6f %15.6f\n" % ("Y", XYZ_R[1], XYZ_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("Z", XYZ_R[2], XYZ_T[2]))
			outfile.write("%10s %15.6f %15.6f\n" % ("x", xyY_R[0], xyY_T[0]))
			outfile.write("%10s %15.6f %15.6f\n" % ("y", xyY_R[1], xyY_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("L", Luv_R[0], Luv_T[0]))
			outfile.write("%10s %15.6f %15.6f\n" % ("u*", Luv_R[1], Luv_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("v*", Luv_R[2], Luv_T[2]))
			outfile.write("%10s %15.6f %15.6f\n" % ("a*", Lab_R[1], Lab_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("b*", Lab_R[2], Lab_T[2]))
			outfile.write("%10s %15.6f %15.6f\n" % ("C*(u*v*)", LChuv_R[1], LChuv_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("h(u*v*)", LChuv_R[2], LChuv_T[2]))
			outfile.write("%10s %15.6f %15.6f\n" % ("C*(a*b*)", LChab_R[1], LChab_T[1]))
			outfile.write("%10s %15.6f %15.6f\n" % ("h(a*b*)", LChab_R[2], LChab_T[2]))
		
		elif data_type == COLOR_TRAJECTORY:
			# Get the data and the properties.
			angles = result.get_angles()
			illuminant = result.get_illuminant()
			observer = result.get_observer()
			R_colors, T_colors = result.get_data()
			
			# Write the header
			outfile.write("%s (%s, %s)\n" % (DATA_TYPE_NAMES[data_type], illuminant, observer))
			
			# Write the header
			outfile.write("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s\n" % ("angle (deg)", "R X", "R Y", "R Z", "R x", "R y", "R L", "R u*", "R v*", "R a*", "R b*", "R C*(u*v*)", "R h(u*v*)", "R C*(a*b*)", "R h(a*b*)", "T X", "T Y", "T Z", "T x", "T y", "T L", "T u*", "T v*", "T a*", "T b*", "T C*(u*v*)", "T h(u*v*)", "T C*(a*b*)", "T h(a*b*)"))
			
			# Write the data
			for i_angle in range(len(angles)):
				XYZ_R = R_colors[i_angle].XYZ()
				xyY_R = R_colors[i_angle].xyY()
				Luv_R = R_colors[i_angle].Luv()
				Lab_R = R_colors[i_angle].Lab()
				LChuv_R = R_colors[i_angle].LChuv()
				LChab_R = R_colors[i_angle].LChab()
				XYZ_T = T_colors[i_angle].XYZ()
				xyY_T = T_colors[i_angle].xyY()
				Luv_T = T_colors[i_angle].Luv()
				Lab_T = T_colors[i_angle].Lab()
				LChuv_T = T_colors[i_angle].LChuv()
				LChab_T = T_colors[i_angle].LChab()
				outfile.write("%15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f %15.6f\n" % (angles[i_angle], XYZ_R[0], XYZ_R[1], XYZ_R[2], xyY_R[0], xyY_R[1], Luv_R[0], Luv_R[1], Luv_R[2], Lab_R[1], Lab_R[2], LChuv_R[1], LChuv_R[2], LChab_R[1], LChab_R[2], XYZ_T[0], XYZ_T[1], XYZ_T[2], xyY_T[0], xyY_T[1], Luv_T[0], Luv_T[1], Luv_T[2], Lab_T[1], Lab_T[2], LChuv_T[1], LChuv_T[2], LChab_T[1], LChab_T[2]))
		
		elif data_type in DIAGRAM_DATA_TYPES:
			
			# Get the data and the properties.
			angle = result.get_angle()
			polarization = result.get_polarization()
			thickness, real_part, imag_part = result.get_data()
			
			# Write the header
			outfile.write("%s at %.2f degrees for %s\n" % (DATA_TYPE_NAMES[data_type], angle, polarization_text(polarization)))
			outfile.write("%5s %15s %15s %15s\n" % ("layer", "thickness (nm)", "real part", "imag. part"))
			
			# Write the data
			for i_layer in range(len(thickness)):
				for i_sublayer in range(len(thickness[i_layer])):
					outfile.write("%5i %15.6f %15.6f %15.6f\n" % (i_layer, thickness[i_layer][i_sublayer], real_part[i_layer][i_sublayer], imag_part[i_layer][i_sublayer]))
		
		elif data_type == ELECTRIC_FIELD:
			
			# Get the data and the properties.
			angle = result.get_angle()
			polarization = result.get_polarization()
			thickness, field = result.get_data()
			
			# Write the header
			outfile.write("%s at %.2f degrees for %s\n" % (DATA_TYPE_NAMES[data_type], angle, polarization_text(polarization)))
			outfile.write("%5s %15s %15s\n" % ("layer", "thickness", "field"))
			
			# Write the data
			for i_layer in range(len(thickness)):
				for i_sublayer in range(len(thickness[i_layer])):
					outfile.write("%5i %15.6f %15.6f\n" % (i_layer, thickness[i_layer][i_sublayer], field[i_layer][i_sublayer]))
		
		elif data_type in SPECTROPHOTOMETRIC_MONITORING_TYPES:
			
			# Get the data and the properties.
			wavelengths = result.get_wavelengths()
			angle = result.get_angle()
			polarization = result.get_polarization()
			thickness, spectrum = result.get_data()
			
			if len(wavelengths) == 1:
				# Write the header
				outfile.write("%s at %.4f nm and %.2f degrees for %s\n" % (DATA_TYPE_NAMES[data_type], wavelengths[0], angle, polarization_text(polarization)))
				outfile.write("%5s %15s %15s\n" % ("layer", "thickness (nm)", COLUMN_TITLES[data_type]))
				
				# Write the data
				for i_layer in range(len(thickness)):
					for i_sublayer in range(len(thickness[i_layer])):
						outfile.write("%5i %15.6f %15.6f\n" % (i_layer, thickness[i_layer][i_sublayer], spectrum[0][i_layer][i_sublayer]))
			
			else:
				# Write the header
				outfile.write("%s at %.2f degrees for %s\n" % (DATA_TYPE_NAMES[data_type], angle, polarization_text(polarization)))
				outfile.write("%21s" % "Wavelength (nm)")
				for i_wvl in range(len(wavelengths)):
					outfile.write(" %15.6f" % wavelengths[i_wvl])
				outfile.write("\n")
				outfile.write("%5s %15s\n" % ("layer", "thickness (nm)"))
				
				# Write the data
				for i_layer in range(len(thickness)):
					for i_sublayer in range(len(thickness[i_layer])):
						outfile.write("%5s %15.6f" % (i_layer, thickness[i_layer][i_sublayer]))
						for i_wvl in range(len(wavelengths)):
							outfile.write(" %15.6f" % spectrum[i_wvl][i_layer][i_sublayer])
						outfile.write("\n")
		
		elif data_type == ELLIPSOMETRY_MONITORING:
			
			# Get the data and the properties.
			wavelengths = result.get_wavelengths()
			angle = result.get_angle()
			thickness, Psi, Delta = result.get_data()
			
			if len(wavelengths) == 1:
				# Write the header
				outfile.write("%s at %.4f nm and %.2f degrees\n" % (DATA_TYPE_NAMES[data_type], wavelengths[0], angle))
				outfile.write("%5s %15s %15s %15s\n" % ("layer", "thickness (nm)", "Psi (deg.)", "Delta (deg.)"))
				
				# Write the data
				for i_layer in range(len(thickness)):
					for i_sublayer in range(len(thickness[i_layer])):
						outfile.write("%5i %15.6f %15.6f %15.6f\n" % (i_layer, thickness[i_layer][i_sublayer], Psi[0][i_layer][i_sublayer], Delta[0][i_layer][i_sublayer]))
			
			else:
				# Write the header
				outfile.write("%s at %.2f degrees\n" % (DATA_TYPE_NAMES[data_type], angle))
				outfile.write("%21s" % "")
				for i_wvl in range(len(wavelengths)):
					outfile.write(" %15s %15s" % ("Psi (deg.)", "Delta (deg.)"))
				outfile.write("\n")
				outfile.write("%21s" % ("Wavelength (nm)"))
				for i_wvl in range(len(wavelengths)):
					outfile.write(" %15.6f %15.6f" % (wavelengths[i_wvl], wavelengths[i_wvl]))
				outfile.write("\n")
				outfile.write("%5s %15s\n" % ("layer", "thickness (nm)"))
				
				# Write the data
				for i_layer in range(len(thickness)):
					for i_sublayer in range(len(thickness[i_layer])):
						outfile.write("%5s %15.6f" % (i_layer, thickness[i_layer][i_sublayer]))
						for i_wvl in range(len(wavelengths)):
							outfile.write(" %15.6f %15.6f" % (Psi[i_wvl][i_layer][i_sublayer], Delta[i_wvl][i_layer][i_sublayer]))
						outfile.write("\n")
	
	outfile.close()


########################################################################
#                                                                      #
# polarization_text                                                    #
#                                                                      #
########################################################################
def polarization_text(polarization):
	"""Get a textual representation of the polarization
	
	This function takes a single argument:
	  polarization         the polarization;
	and returns a text to describe it.
	
	A special text is returned for s, p or unpolarized light."""
	
	if polarization == S:
		return "s-polarized light"
	
	elif polarization == P:
		return "p-polarized light"
	
	elif polarization == UNPOLARIZED:
		return "unpolarized light"
	
	else:
		return "a polarization of %.2f degrees" % polarization
