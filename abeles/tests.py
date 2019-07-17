# tests.py
# 
# Test the functions of the abeles package to verify that they work
# well and are corectly accessible from Python.
#
# Copyright (c) 2002-2003,2005,2006,2012 Stephane Larouche.
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



import sys
sys.path.append("..")

import time
import math

import abeles


if abeles.get_abeles_dll_import_success():
	print "Working with the dll."
else:
	print "Working with Python versions."
print ""


thickness_layer = 1000.0
thickness_substrate = 1000000.0
theta_0 = 75.0
polarization = 45.0


start = time.clock()
wvls = abeles.wvls(701)
wvls.set_wvls_by_range(300.0, 1.0)
stop = time.clock()
print "wvls created in %.4f seconds" % (stop-start)

print "wvls[50]:", wvls[50]
print "wvls[250]:", wvls[250]
print ""

start = time.clock()
constant = abeles.constant()
constant.set_constant(1.0)
table = abeles.table(8)
table.set_table(0,  300, 2.40-0.0003j)
table.set_table(1,  400, 2.35-0.0002j)
table.set_table(2,  500, 2.30-0.0001j)
table.set_table(3,  600, 2.26)
table.set_table(4,  700, 2.23)
table.set_table(5,  800, 2.21)
table.set_table(6,  900, 2.20)
table.set_table(7, 1000, 2.19)
table.prepare_table()
Cauchy = abeles.Cauchy()
Cauchy.set_Cauchy(1.5, 0.002, 0.0001, 0.00002, 6.0, 3000)
Sellmeier = abeles.Sellmeier()
Sellmeier.set_Sellmeier(1.03961212, 6.00069867e-3, 0.231792344, 2.00179144e-2, 1.01046945, 1.03560653e2, 0.00002, 6.0, 3000)
stop = time.clock()
print "constant, table and Cauchy created and set in %.4f seconds" % (stop-start)
print ""

start = time.clock()
constant_mixture = abeles.constant_mixture(6)
constant_mixture.set_constant_mixture(0,  0, 1.5)
constant_mixture.set_constant_mixture(1, 10, 1.7)
constant_mixture.set_constant_mixture(2, 20, 1.9)
constant_mixture.set_constant_mixture(3, 30, 2.1)
constant_mixture.set_constant_mixture(4, 40, 2.3-0.000001j)
constant_mixture.set_constant_mixture(5, 50, 2.5-0.000002j)
constant_mixture.prepare_constant_mixture()
Cauchy_mixture = abeles.Cauchy_mixture(6)
Cauchy_mixture.set_Cauchy_mixture(0,  0, 1.5, 0.002, 0.0000, 0.00001, 4.0, 3000)
Cauchy_mixture.set_Cauchy_mixture(1, 10, 1.7, 0.003, 0.0001, 0.00002, 4.0, 3200)
Cauchy_mixture.set_Cauchy_mixture(2, 20, 1.9, 0.005, 0.0002, 0.00005, 4.0, 3400)
Cauchy_mixture.set_Cauchy_mixture(3, 30, 2.1, 0.009, 0.0004, 0.0001,  4.5, 3600)
Cauchy_mixture.set_Cauchy_mixture(4, 40, 2.3, 0.015, 0.0007, 0.0003,  5.0, 3700)
Cauchy_mixture.set_Cauchy_mixture(5, 50, 2.5, 0.050, 0.0015, 0.0005,  6.0, 3800)
Cauchy_mixture.prepare_Cauchy_mixture()
Sellmeier_mixture = abeles.Sellmeier_mixture(5)
Sellmeier_mixture.set_Sellmeier_mixture(0, 0  , 1.00, 6.00e-3, 0.25, 2.00e-2, 1.00, 1.00e2, 0.00001, 4.0, 3000)
Sellmeier_mixture.set_Sellmeier_mixture(1, 25 , 1.40, 6.10e-3, 0.30, 2.01e-2, 1.01, 1.01e2, 0.00002, 4.0, 3200)
Sellmeier_mixture.set_Sellmeier_mixture(2, 50 , 1.80, 6.20e-3, 0.35, 2.02e-2, 1.02, 1.02e2, 0.00005, 4.0, 3400)
Sellmeier_mixture.set_Sellmeier_mixture(3, 75 , 2.20, 6.30e-3, 0.40, 2.03e-2, 1.03, 1.03e2, 0.0001,  4.5, 3600)
Sellmeier_mixture.set_Sellmeier_mixture(4, 100, 2.60, 6.40e-3, 0.55, 2.04e-2, 1.04, 1.04e2, 0.0003,  5.0, 3700)
Sellmeier_mixture.prepare_Sellmeier_mixture()
table_mixture = abeles.table_mixture(5, 13)
for i_wvl in range(13):
	wvl = 400.0 + i_wvl*50.0
	wvl_micron = wvl/1000.0
	table_mixture.set_table_mixture(0, i_wvl,   0, wvl, 1.464+0.001/wvl_micron**2-0.0j)
	table_mixture.set_table_mixture(1, i_wvl,  25, wvl, 1.572+0.003/wvl_micron**2-0.0j)
	table_mixture.set_table_mixture(2, i_wvl,  50, wvl, 1.767+0.006/wvl_micron**2-0.0001j)
	table_mixture.set_table_mixture(3, i_wvl,  75, wvl, 1.947+0.010/wvl_micron**2-0.0002j)
	table_mixture.set_table_mixture(4, i_wvl, 100, wvl, 2.068+0.014/wvl_micron**2-0.0004j)
table_mixture.prepare_table_mixture()
stop = time.clock()
print "mixtures created and set in %.4f seconds" % (stop-start)

print "constant_mixture index range @ 350nm:", constant_mixture.get_constant_mixture_index_range(350.0)
print "constant_mixture index range @ 550nm:", constant_mixture.get_constant_mixture_index_range(550.0)
print "Cauchy_mixture index range @ 350nm:", Cauchy_mixture.get_Cauchy_mixture_index_range(350.0)
print "Cauchy_mixture index range @ 550nm:", Cauchy_mixture.get_Cauchy_mixture_index_range(550.0)
print "Sellmeier_mixture index range @ 350nm:", Sellmeier_mixture.get_Sellmeier_mixture_index_range(350.0)
print "Sellmeier_mixture index range @ 550nm:", Sellmeier_mixture.get_Sellmeier_mixture_index_range(550.0)
print "table_mixture index range @ 350nm:", table_mixture.get_table_mixture_index_range(350.0)
print "table_mixture index range @ 550nm:", table_mixture.get_table_mixture_index_range(550.0)
print ""

start = time.clock()
n_medium = abeles.N(wvls)
n_layer = abeles.N(wvls)
n_substrate = abeles.N(wvls)
n_Sellmeier = abeles.N(wvls)
constant.set_N_constant(n_medium)
table.set_N_table(n_layer)
Cauchy.set_N_Cauchy(n_substrate)
Sellmeier.set_N_Sellmeier(n_Sellmeier)
stop = time.clock()
print "n_constant, n_table and n_Cauchy created and set in %.4f seconds" % (stop-start)

print "n_medium @ %fnm:" % wvls[50], n_medium[50]
print "n_medium @ %fnm:" % wvls[250], n_medium[250]
print "n_layer @ %fnm:" % wvls[50], n_layer[50]
print "n_layer @ %fnm:" % wvls[250], n_layer[250]
print "n_substrate @ %fnm:" % wvls[50], n_substrate[50]
print "n_substrate @ %fnm:" % wvls[250], n_substrate[250]
print "n_Sellmeier @ %fnm:" % wvls[50], n_Sellmeier[50]
print "n_Sellmeier @ %fnm:" % wvls[250], n_Sellmeier[250]
print ""

start = time.clock()
N_mixture_constant = abeles.N_mixture(constant_mixture, wvls)
N_mixture_table = abeles.N_mixture(table_mixture, wvls)
N_mixture_Cauchy = abeles.N_mixture(Cauchy_mixture, wvls)
N_mixture_Sellmeier = abeles.N_mixture(Sellmeier_mixture, wvls)
N_mixture_constant.set_N_mixture(1.9, 550.0)
N_mixture_table.set_N_mixture(1.7, 550.0)
N_mixture_Cauchy.set_N_mixture(2.1, 550.0)
N_mixture_Sellmeier.set_N_mixture(1.75, 550.0)
N_mixture_constant.set_dN_mixture(1.9, 550.0)
N_mixture_table.set_dN_mixture(1.7, 550.0)
N_mixture_Cauchy.set_dN_mixture(2.1, 550.0)
N_mixture_Sellmeier.set_dN_mixture(1.75, 550.0)
n_layer_2 = N_mixture_constant.get_N_mixture()
n_layer_3 = N_mixture_table.get_N_mixture()
n_layer_4 = N_mixture_Cauchy.get_N_mixture()
n_layer_5 = N_mixture_Sellmeier.get_N_mixture()
dn_layer_2 = N_mixture_constant.get_dN_mixture()
dn_layer_3 = N_mixture_table.get_dN_mixture()
dn_layer_4 = N_mixture_Cauchy.get_dN_mixture()
dn_layer_5 = N_mixture_Sellmeier.get_dN_mixture()
stop = time.clock()
print "n for mixtures created and set in %.4f seconds" % (stop-start)

print "n_layer_2 @ %fnm:" % wvls[50], n_layer_2[50]
print "n_layer_2 @ %fnm:" % wvls[250], n_layer_2[250]
print "n_layer_3 @ %fnm:" % wvls[50], n_layer_3[50]
print "n_layer_3 @ %fnm:" % wvls[250], n_layer_3[250]
print "n_layer_4 @ %fnm:" % wvls[50], n_layer_4[50]
print "n_layer_4 @ %fnm:" % wvls[250], n_layer_4[250]
print "n_layer_5 @ %fnm:" % wvls[50], n_layer_5[50]
print "n_layer_5 @ %fnm:" % wvls[250], n_layer_5[250]
print "dn_layer_2 @ %fnm:" % wvls[50], dn_layer_2[50]
print "dn_layer_2 @ %fnm:" % wvls[250], dn_layer_2[250]
print "dn_layer_3 @ %fnm:" % wvls[50], dn_layer_3[50]
print "dn_layer_3 @ %fnm:" % wvls[250], dn_layer_3[250]
print "dn_layer_4 @ %fnm:" % wvls[50], dn_layer_4[50]
print "dn_layer_4 @ %fnm:" % wvls[250], dn_layer_4[250]
print "dn_layer_5 @ %fnm:" % wvls[50], dn_layer_5[50]
print "dn_layer_5 @ %fnm:" % wvls[250], dn_layer_5[250]
print ""

start = time.clock()
N_mixture_constant.prepare_N_mixture_graded(101)
N_mixture_table.prepare_N_mixture_graded(101)
N_mixture_Cauchy.prepare_N_mixture_graded(101)
N_mixture_Sellmeier.prepare_N_mixture_graded(101)
n_min_constant, n_max_constant = constant_mixture.get_constant_mixture_index_range(550.0)
n_min_table, n_max_table = table_mixture.get_table_mixture_index_range(550.0)
n_min_Cauchy, n_max_Cauchy = Cauchy_mixture.get_Cauchy_mixture_index_range(550.0)
n_min_Sellmeier, n_max_Sellmeier = Sellmeier_mixture.get_Sellmeier_mixture_index_range(550.0)
for i in range(101):
	N_mixture_constant.set_N_mixture_graded(i, n_min_constant+i*(n_max_constant-n_min_constant)/(101-1), 550.0)
	N_mixture_table.set_N_mixture_graded(i, n_min_table+i*(n_max_table-n_min_table)/(101-1), 550.0)
	N_mixture_Cauchy.set_N_mixture_graded(i, n_min_Cauchy+i*(n_max_Cauchy-n_min_Cauchy)/(101-1), 550.0)
	N_mixture_Sellmeier.set_N_mixture_graded(i, n_min_Sellmeier+i*(n_max_Sellmeier-n_min_Sellmeier)/(101-1), 550.0)
stop = time.clock()
print "graded n created and set in %.4f seconds" % (stop-start)

print "n of constant mixture at middle step @ %fnm:" % wvls[50], N_mixture_constant.get_N_mixture_graded(50)[50]
print "n of constant mixture at middle step @ %fnm:" % wvls[250], N_mixture_constant.get_N_mixture_graded(50)[250]
print "n of table mixture at middle step @ %fnm:" % wvls[50], N_mixture_table.get_N_mixture_graded(50)[50]
print "n of table mixture at middle step @ %fnm:" % wvls[250], N_mixture_table.get_N_mixture_graded(50)[250]
print "n of Cauchy mixture at middle step @ %fnm:" % wvls[50], N_mixture_Cauchy.get_N_mixture_graded(50)[50]
print "n of Cauchy mixture at middle step @ %fnm:" % wvls[250], N_mixture_Cauchy.get_N_mixture_graded(50)[250]
print "n of Sellmeier mixture at middle step @ %fnm:" % wvls[50], N_mixture_Sellmeier.get_N_mixture_graded(50)[50]
print "n of Sellmeier mixture at middle step @ %fnm:" % wvls[250], N_mixture_Sellmeier.get_N_mixture_graded(50)[250]
print ""

start = time.clock()
sin2_theta_0 = abeles.sin2(wvls)
sin2_theta_0.set_sin2_theta_0(n_medium, theta_0)
stop = time.clock()
print "sin2_theta_0 created and set in %.4f seconds" % (stop-start)

print ""

start = time.clock()
matrices = abeles.matrices(wvls)
global_matrices_front = abeles.matrices(wvls)
global_matrices_back = abeles.matrices(wvls)
stop = time.clock()
print "matrices and global_matrices created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
global_matrices_front.set_matrices_unity()
global_matrices_back.copy_matrices(global_matrices_front)
matrices.set_matrices(n_layer, thickness_layer, sin2_theta_0)
global_matrices_front.multiply_matrices(matrices)
stop = time.clock()
print "matrices set and multiplied in %.4f seconds" % (stop-start)

print ""

start = time.clock()
r_and_t_front = abeles.r_and_t(wvls)
r_and_t_front_reverse = abeles.r_and_t(wvls)
r_and_t_back = abeles.r_and_t(wvls)
R_front = abeles.R(wvls)
R_front_reverse = abeles.R(wvls)
T_front = abeles.T(wvls)
T_front_reverse = abeles.T(wvls)
R_back = abeles.R(wvls)
T_back = abeles.T(wvls)
R = abeles.R(wvls)
T = abeles.T(wvls)
A = abeles.A(wvls)
stop = time.clock()
print "Multiple r_and_t and spectrum created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
r_and_t_front.calculate_r_and_t(global_matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_front_reverse.calculate_r_and_t_reverse(global_matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_back.calculate_r_and_t_reverse(global_matrices_back, n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, polarization)
R_front_reverse.calculate_R(r_and_t_front_reverse, polarization)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, polarization)
T_front_reverse.calculate_T(r_and_t_front_reverse, n_substrate, n_medium, sin2_theta_0, polarization)
R_back.calculate_R(r_and_t_back, polarization)
T_back.calculate_T(r_and_t_back, n_substrate, n_medium, sin2_theta_0, polarization)
R.calculate_R_with_backside(T_front, R_front, T_front_reverse, R_front_reverse, R_back, n_substrate, thickness_substrate, sin2_theta_0)
T.calculate_T_with_backside(T_front, R_front_reverse, T_back, R_back, n_substrate, thickness_substrate, sin2_theta_0)
A.calculate_A(R, T)
stop = time.clock()
print "r_and_t and spectrum calculated in %.4f seconds" % (stop-start)

print "R @ %fnm:" % wvls[50], R[50]
print "R @ %fnm:" % wvls[250], R[250]
print "T @ %fnm:" % wvls[50], T[50]
print "T @ %fnm:" % wvls[250], T[250]
print "A @ %fnm:" % wvls[50], A[50]
print "A @ %fnm:" % wvls[250], A[250]
print ""

#for i in range(len(wvls)):
#	print "R, T and A at %fnm" % wvls[i], R[i], T[i], A[i]

start = time.clock()
phase_r = abeles.phase(wvls)
phase_t = abeles.phase(wvls)
GD_r = abeles.GD(wvls)
GD_t = abeles.GD(wvls)
GDD_r = abeles.GDD(wvls)
GDD_t = abeles.GDD(wvls)
stop = time.clock()
print "phase, GD and GDD objects created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
phase_r.calculate_r_phase(global_matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
phase_t.calculate_t_phase(global_matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
GD_r.calculate_GD(phase_r)
GD_t.calculate_GD(phase_t)
GDD_r.calculate_GDD(phase_r)
GDD_t.calculate_GDD(phase_t)
stop = time.clock()
print "phase, GD and GDD calculated in %.4f seconds" % (stop-start)

print "phase_r @ %fnm:" % wvls[50], phase_r[50]
print "phase_t @ %fnm:" % wvls[250], phase_t[250]
print "GD_r @ %fnm:" % wvls[50], GD_r[50]
print "GD_t @ %fnm:" % wvls[250], GD_t[250]
print "GDD_r @ %fnm:" % wvls[50], GDD_r[50]
print "GDD_t @ %fnm:" % wvls[250], GDD_t[250]
print ""

#for i in range(len(wvls)):
#	print "phase_r, GD_r and GDD_r at %fnm" % wvls[i], phase_r[i], GD_r[i], GDD_r[i]

start = time.clock()
Psi_and_Delta = abeles.Psi_and_Delta(wvls)
Psi_and_Delta_with_backside = abeles.Psi_and_Delta(wvls)
stop = time.clock()
print "Psi_and_Delta objects created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
Psi_and_Delta.calculate_Psi_and_Delta(r_and_t_front)
Psi_and_Delta_with_backside.calculate_Psi_and_Delta_with_backside(r_and_t_front, r_and_t_front_reverse, r_and_t_back, n_substrate, thickness_substrate, sin2_theta_0)
stop = time.clock()
print "Psi_and_Delta calculated in %.4f seconds" % (stop-start)

Psi = Psi_and_Delta.get_Psi()
Delta = Psi_and_Delta.get_Delta()
print "Psi and Delta @ %fnm:" % wvls[50], Psi[50], Delta[50]
print "Psi and Delta @ %fnm:" % wvls[250], Psi[250], Delta[250]
print "Psi and Delta with backside @ %fnm:" % wvls[50], Psi_and_Delta_with_backside[50]
print "Psi and Delta with backside @ %fnm:" % wvls[250], Psi_and_Delta_with_backside[250]
print ""

#for i in range(len(wvls)):
#	print "Psi and Delta @ %fnm:" % wvls[i], Psi_and_Delta[i]

start = time.clock()
admittance = abeles.admittance(wvls)
stop = time.clock()
print "admittance object created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
admittance.calculate_admittance(global_matrices_front, n_substrate, sin2_theta_0, abeles.S)
stop = time.clock()
print "admittance calculated in %.4f seconds" % (stop-start)

print "admittance @ %fnm:" % wvls[50], admittance[50]
print "admittance @ %fnm:" % wvls[250], admittance[250]
print ""

start = time.clock()
circle = abeles.circle(wvls)
stop = time.clock()
print "circle object created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
circle.calculate_circle(r_and_t_front, abeles.S)
stop = time.clock()
print "circle calculated in %.4f seconds" % (stop-start)

print "circle @ %fnm:" % wvls[50], circle[50]
print "circle @ %fnm:" % wvls[250], circle[250]
print ""

start = time.clock()
electric_field = abeles.electric_field(wvls)
stop = time.clock()
print "electric_field object created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
electric_field.calculate_electric_field(global_matrices_front, n_substrate, sin2_theta_0, abeles.S)
stop = time.clock()
print "electric_field calculated in %.4f seconds" % (stop-start)

print "electric_field @ %fnm:" % wvls[50], electric_field[50]
print "electric_field @ %fnm:" % wvls[250], electric_field[250]
print ""

start = time.clock()
monitoring_matrices = abeles.monitoring_matrices(wvls, 101)
stop = time.clock()
print "monitoring_matrices object created in %.4f seconds" % (stop-start)

print ""

start = time.clock()
global_matrices_front.set_matrices_unity()
for i in range(101):
	monitoring_matrices.set_monitoring_matrices(i, n_layer, i*thickness_layer/100, sin2_theta_0)
monitoring_matrices.multiply_monitoring_matrices(global_matrices_front)
stop = time.clock()
print "monitoring_matrices calculated in %.4f seconds" % (stop-start)

print ""

start = time.clock()
r_and_t_front.calculate_r_and_t(monitoring_matrices[75], n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, polarization)
stop = time.clock()
print "R spectrum calculated in %.4f seconds" % (stop-start)

print "R @ %fnm:" % wvls[50], R_front[50]
print "R @ %fnm:" % wvls[250], R_front[250]
print ""

start = time.clock()
global_matrices_front.set_matrices_unity()
monitoring_matrices.set_monitoring_matrices(0, n_layer, 0, sin2_theta_0)
for i in range(1, 101):
	monitoring_matrices.set_monitoring_matrices(i, n_layer, thickness_layer/100, sin2_theta_0)
monitoring_matrices.multiply_monitoring_matrices_cumulative(global_matrices_front)
stop = time.clock()
print "monitoring_matrices calculated cumulatively in %.4f seconds" % (stop-start)

print ""

start = time.clock()
r_and_t_front.calculate_r_and_t(monitoring_matrices[75], n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, polarization)
stop = time.clock()
print "R spectrum calculated in %.4f seconds" % (stop-start)

print "R @ %fnm:" % wvls[50], R_front[50]
print "R @ %fnm:" % wvls[250], R_front[250]
