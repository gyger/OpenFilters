# test_derivatives.py
# 
# Test the various derivatives calculated by the abeles package by
# comparing them to the results obtained by finite differences.
#
# Copyright (c) 2005-2007,2009,2012 Stephane Larouche.
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
import cmath

import abeles
import moremath


if abeles.get_abeles_dll_import_success():
	print "Working with the dll."
else:
	print "Working with Python versions."
print ""


center_wvl = 550.0
angle = 60.0
pol = 45.0
nb_wvls = 351
thickness_SiO2 = 50.0
thickness_TiO2 = 100.0
thickness_SiO2TiO2 = 200.0
index_SiO2TiO2 = 1.9
diff = math.sqrt(moremath.limits.epsilon)
nb_needles = 101
needle_thickness = diff
nb_steps = 101
step_delta_n = diff*index_SiO2TiO2
mixture_type = "Sellmeier"
substrate_thickness = 1000000
angle_of_constant_OT = 45.0


start = time.clock()
wvls = abeles.wvls(nb_wvls)
wvls.set_wvls_by_range(300.0, (1000.0-300.0)/(nb_wvls-1))
stop = time.clock()
print "wvls created in %.8f seconds" % (stop-start)

start = time.clock()
TiO2 = abeles.Cauchy()
SiO2 = abeles.Cauchy()
if mixture_type == "constant":
	SiO2TiO2 = abeles.constant_mixture(5)
elif mixture_type == "table":
	SiO2TiO2 = abeles.table_mixture(5, 13)
elif mixture_type == "Cauchy":
	SiO2TiO2 = abeles.Cauchy_mixture(5)
elif mixture_type == "Sellmeier":
	SiO2TiO2 = abeles.Sellmeier_mixture(5)
medium = abeles.constant()
substrate = abeles.constant()
TiO2.set_Cauchy(2.1959, 0.025614, 0.0059846, 0.002574500, 8.508000, 4000)
SiO2.set_Cauchy(1.4598, 0.0075239, 0, 0, 4, 4000)
medium.set_constant(1.0)
substrate.set_constant(1.5)
if mixture_type == "constant":
	SiO2TiO2.set_constant_mixture(0, 0  , 1.464-0.0j)
	SiO2TiO2.set_constant_mixture(1, 25 , 1.5722-0.0j)
	SiO2TiO2.set_constant_mixture(2, 50 , 1.7678-0.0001j)
	SiO2TiO2.set_constant_mixture(3, 75 , 1.9475-0.0002j)
	SiO2TiO2.set_constant_mixture(4, 100, 2.0681-0.0004j)
	SiO2TiO2.prepare_constant_mixture()
elif mixture_type == "table":
	for i_wvl in range(13):
		wvl = 400.0 + i_wvl*50.0
		wvl_micron = wvl/1000.0
		SiO2TiO2.set_table_mixture(0, i_wvl,   0, wvl, 1.464+0.001/wvl_micron**2-0.0j)
		SiO2TiO2.set_table_mixture(1, i_wvl,  25, wvl, 1.572+0.003/wvl_micron**2-0.0j)
		SiO2TiO2.set_table_mixture(2, i_wvl,  50, wvl, 1.767+0.006/wvl_micron**2-0.0001j)
		SiO2TiO2.set_table_mixture(3, i_wvl,  75, wvl, 1.947+0.010/wvl_micron**2-0.0002j)
		SiO2TiO2.set_table_mixture(4, i_wvl, 100, wvl, 2.068+0.014/wvl_micron**2-0.0004j)
	SiO2TiO2.prepare_table_mixture()
elif mixture_type == "Cauchy":
	SiO2TiO2.set_Cauchy_mixture(0, 0  , 1.464 , 0.0010228 , 0.0      , 0.0      , 7.2334, 3500)
	SiO2TiO2.set_Cauchy_mixture(1, 25 , 1.5722, -0.0033129, 0.0020644, 0.0      , 7.2334, 3500)
	SiO2TiO2.set_Cauchy_mixture(2, 50 , 1.7678, 0.0067224 , 0.0029301, 0.013889 , 7.2334, 3500)
	SiO2TiO2.set_Cauchy_mixture(3, 75 , 1.9475, 0.010044  , 0.0046517, 0.0061015, 8.2956, 3750)
	SiO2TiO2.set_Cauchy_mixture(4, 100, 2.0681, 0.014277  , 0.0064263, 0.012958 , 7.6302, 3800)
	SiO2TiO2.prepare_Cauchy_mixture()
elif mixture_type == "Sellmeier":
	SiO2TiO2.set_Sellmeier_mixture(0, 0  , 1.00, 6.00e-3, 0.25, 2.00e-2, 1.00, 1.00e2, 0.00001, 4.0, 3000)
	SiO2TiO2.set_Sellmeier_mixture(1, 25 , 1.40, 6.10e-3, 0.30, 2.01e-2, 1.01, 1.01e2, 0.00002, 4.0, 3200)
	SiO2TiO2.set_Sellmeier_mixture(2, 50 , 1.80, 6.20e-3, 0.35, 2.02e-2, 1.02, 1.02e2, 0.00005, 4.0, 3400)
	SiO2TiO2.set_Sellmeier_mixture(3, 75 , 2.20, 6.30e-3, 0.40, 2.03e-2, 1.03, 1.03e2, 0.0001,  4.5, 3600)
	SiO2TiO2.set_Sellmeier_mixture(4, 100, 2.60, 6.40e-3, 0.55, 2.04e-2, 1.04, 1.04e2, 0.0003,  5.0, 3700)
	SiO2TiO2.prepare_Sellmeier_mixture()
n_TiO2 = abeles.N(wvls)
n_SiO2 = abeles.N(wvls)
n_medium = abeles.N(wvls)
n_substrate = abeles.N(wvls)
n_SiO2TiO2_ = abeles.N_mixture(SiO2TiO2, wvls)
n_SiO2TiO2 = n_SiO2TiO2_.get_N_mixture()
dn_SiO2TiO2 = n_SiO2TiO2_.get_dN_mixture()
TiO2.set_N_Cauchy(n_TiO2)
SiO2.set_N_Cauchy(n_SiO2)
medium.set_N_constant(n_medium)
substrate.set_N_constant(n_substrate)
stop = time.clock()
print "TiO2, SiO2, medium, substrate and indices created in %.8f seconds" % (stop-start)

start = time.clock()
sin2_theta_0 = abeles.sin2(wvls)
sin2_theta_0.set_sin2_theta_0(n_medium, angle)
stop = time.clock()
print "sin2_theta_0 created in %.8f seconds" % (stop-start)

start = time.clock()
pre_and_post_matrices = abeles.pre_and_post_matrices(wvls, 3)
# We only get the global matrices once since we get a pointer
# that will always point to the right matrices.
matrices_front = pre_and_post_matrices.get_global_matrices()
stop = time.clock()
print "pre_and_post_matrices created in %.8f seconds" % (stop-start)

start = time.clock()
matrices_back = abeles.matrices(wvls)
stop = time.clock()
print "matrices_back created in %.8f seconds" % (stop-start)

start = time.clock()
pre_and_post_matrices.set_pre_and_post_matrices(0, n_TiO2, thickness_TiO2, sin2_theta_0)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2, sin2_theta_0)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
stop = time.clock()
print "setting of pre_and_post_matrices made in %.8f seconds" % (stop-start)

start = time.clock()
pre_and_post_matrices.multiply_pre_and_post_matrices()
stop = time.clock()
print "multiplication of pre_and_post_matrices made in %.8f seconds" % (stop-start)

start = time.clock()
matrices_back.set_matrices(n_TiO2, thickness_TiO2, sin2_theta_0)
stop = time.clock()
print "matrices_back set in %.8f seconds" % (stop-start)

start = time.clock()
r_and_t_front = abeles.r_and_t(wvls)
r_and_t_front_reverse = abeles.r_and_t(wvls)
r_and_t_back = abeles.r_and_t(wvls)
r_and_t_back_reverse = abeles.r_and_t(wvls)
stop = time.clock()
print "r_and_t variables created in %.8f seconds" % (stop-start)

start = time.clock()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_front_reverse.calculate_r_and_t_reverse(matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_back.calculate_r_and_t_reverse(matrices_back, n_medium, n_substrate, sin2_theta_0)
r_and_t_back_reverse.calculate_r_and_t_reverse(matrices_back, n_medium, n_substrate, sin2_theta_0)
stop = time.clock()
print "calculation of r_and_t_front made in %.8f seconds" % (stop-start)

start = time.clock()
R_front = abeles.R(wvls)
T_front = abeles.T(wvls)
R_front_reverse = abeles.R(wvls)
T_front_reverse = abeles.T(wvls)
R_back = abeles.R(wvls)
T_back = abeles.T(wvls)
R_back_reverse = abeles.R(wvls)
T_back_reverse = abeles.T(wvls)
R = abeles.R(wvls)
T = abeles.T(wvls)
A = abeles.A(wvls)
R_reverse = abeles.R(wvls)
stop = time.clock()
print "R, T, and A variables created in %.8f seconds" % (stop-start)

start = time.clock()
R_front.calculate_R(r_and_t_front, pol)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
R_front_reverse.calculate_R(r_and_t_front_reverse, pol)
T_front_reverse.calculate_T(r_and_t_front_reverse, n_substrate, n_medium, sin2_theta_0, pol)
R_back.calculate_R(r_and_t_back, pol)
T_back.calculate_T(r_and_t_back, n_substrate, n_medium, sin2_theta_0, pol)
R_back_reverse.calculate_R(r_and_t_back_reverse, pol)
T_back_reverse.calculate_T(r_and_t_back_reverse, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "calculation of R and T made in %.8f seconds" % (stop-start)

start = time.clock()
dMi = abeles.dM(wvls)
dM = abeles.dM(wvls)
psi = abeles.psi_matrices(wvls)
psi_reverse = abeles.psi_matrices(wvls)
dr_and_dt_front = abeles.dr_and_dt(wvls)
dr_and_dt_front_reverse = abeles.dr_and_dt(wvls)
stop = time.clock()
print "dMi, dM, psi_r, psi_t, dr_and_dt_front matrices created in %.8f seconds" % (stop-start)

start = time.clock()
dR_front = abeles.dR(wvls)
dT_front = abeles.dT(wvls)
dR_front_reverse = abeles.dR(wvls)
dT_front_reverse = abeles.dT(wvls)
dR = abeles.dR(wvls)
dT = abeles.dT(wvls)
dA = abeles.dA(wvls)
dR_reverse = abeles.dR(wvls)
stop = time.clock()
print "dR, dT, and dA variables created in %.8f seconds" % (stop-start)

start = time.clock()
dr_phase_s = abeles.dphase(wvls)
dr_phase_p = abeles.dphase(wvls)
dt_phase_s = abeles.dphase(wvls)
dt_phase_p = abeles.dphase(wvls)
stop = time.clock()
print "dphase variables created in %.8f seconds" % (stop-start)

start = time.clock()
dr_GD_s = abeles.dGD(wvls)
dr_GD_p = abeles.dGD(wvls)
dt_GD_s = abeles.dGD(wvls)
dt_GD_p = abeles.dGD(wvls)
dr_GDD_s = abeles.dGDD(wvls)
dr_GDD_p = abeles.dGDD(wvls)
dt_GDD_s = abeles.dGDD(wvls)
dt_GDD_p = abeles.dGDD(wvls)
stop = time.clock()
print "dGD and dGDD variables created in %.8f seconds" % (stop-start)


# Thickness derivatives.

start = time.clock()
dMi.set_dMi_thickness(n_SiO2, thickness_SiO2, sin2_theta_0)
dM.calculate_dM(dMi, pre_and_post_matrices, 1)
stop = time.clock()
print "calculation of dMi and dM made in %.8f seconds" % (stop-start)

start = time.clock()
psi.calculate_psi_matrices(r_and_t_front, n_medium, n_substrate, sin2_theta_0)
psi_reverse.calculate_psi_matrices_reverse(r_and_t_front_reverse, n_medium, n_substrate, sin2_theta_0)
dr_and_dt_front.calculate_dr_and_dt(dM, psi)
dr_and_dt_front_reverse.calculate_dr_and_dt_reverse(dM, psi_reverse)
stop = time.clock()
print "calculation of psi matrices and dr_and_dt_front made in %.8f seconds" % (stop-start)

start = time.clock()
dR_front.calculate_dR(dr_and_dt_front, r_and_t_front, pol)
dT_front.calculate_dT(dr_and_dt_front, r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
dR_front_reverse.calculate_dR(dr_and_dt_front_reverse, r_and_t_front_reverse, pol)
dT_front_reverse.calculate_dT(dr_and_dt_front_reverse, r_and_t_front_reverse, n_substrate, n_medium, sin2_theta_0, pol)
dR.calculate_dR_with_backside(T_front, dT_front, dR_front, T_front_reverse, dT_front_reverse, R_front_reverse, dR_front_reverse, R_back, n_substrate, substrate_thickness, sin2_theta_0)
dT.calculate_dT_with_backside(T_front, dT_front, R_front_reverse, dR_front_reverse, T_back, R_back, n_substrate, substrate_thickness, sin2_theta_0)
dA.calculate_dA(dR, dT)
dR_reverse.calculate_dR_with_backside_2(T_back_reverse, T_back, R_back, R_front_reverse, dR_front_reverse, n_substrate, substrate_thickness, sin2_theta_0)
stop = time.clock()
print "calculation of dR, dT, and dA made in %.8f seconds" % (stop-start)

start = time.clock()
dr_phase_s.calculate_dr_phase(matrices_front, dM, n_medium, n_substrate, sin2_theta_0, abeles.S)
dr_phase_p.calculate_dr_phase(matrices_front, dM, n_medium, n_substrate, sin2_theta_0, abeles.P)
dt_phase_s.calculate_dt_phase(matrices_front, dM, n_medium, n_substrate, sin2_theta_0, abeles.S)
dt_phase_p.calculate_dt_phase(matrices_front, dM, n_medium, n_substrate, sin2_theta_0, abeles.P)
stop = time.clock()
print "calculation of phase derivatives made in %.8f seconds" % (stop-start)

start = time.clock()
dr_GD_s.calculate_dGD(dr_phase_s)
dr_GD_p.calculate_dGD(dr_phase_p)
dt_GD_s.calculate_dGD(dt_phase_s)
dt_GD_p.calculate_dGD(dt_phase_p)
dr_GDD_s.calculate_dGDD(dr_phase_s)
dr_GDD_p.calculate_dGDD(dr_phase_p)
dt_GDD_s.calculate_dGDD(dt_phase_s)
dt_GDD_p.calculate_dGDD(dt_phase_p)
stop = time.clock()
print "calculation of GD and GDD derivatives made in %.8f seconds" % (stop-start)

start = time.clock()
R_front_plus = abeles.R(wvls)
R_front_minus = abeles.R(wvls)
T_front_plus = abeles.T(wvls)
T_front_minus = abeles.T(wvls)
R_front_reverse_plus = abeles.R(wvls)
R_front_reverse_minus = abeles.R(wvls)
T_front_reverse_plus = abeles.T(wvls)
T_front_reverse_minus = abeles.T(wvls)
R_plus = abeles.R(wvls)
R_minus = abeles.R(wvls)
T_plus = abeles.T(wvls)
T_minus = abeles.T(wvls)
A_plus = abeles.A(wvls)
A_minus = abeles.A(wvls)
R_reverse_plus = abeles.R(wvls)
R_reverse_minus = abeles.R(wvls)
r_phase_s_plus = abeles.phase(wvls)
r_phase_s_minus = abeles.phase(wvls)
r_phase_p_plus = abeles.phase(wvls)
r_phase_p_minus = abeles.phase(wvls)
t_phase_s_plus = abeles.phase(wvls)
t_phase_s_minus = abeles.phase(wvls)
t_phase_p_plus = abeles.phase(wvls)
t_phase_p_minus = abeles.phase(wvls)
r_GD_s_plus = abeles.GD(wvls)
r_GD_s_minus = abeles.GD(wvls)
r_GD_p_plus = abeles.GD(wvls)
r_GD_p_minus = abeles.GD(wvls)
t_GD_s_plus = abeles.GD(wvls)
t_GD_s_minus = abeles.GD(wvls)
t_GD_p_plus = abeles.GD(wvls)
t_GD_p_minus = abeles.GD(wvls)
r_GDD_s_plus = abeles.GDD(wvls)
r_GDD_s_minus = abeles.GDD(wvls)
r_GDD_p_plus = abeles.GDD(wvls)
r_GDD_p_minus = abeles.GDD(wvls)
t_GDD_s_plus = abeles.GDD(wvls)
t_GDD_s_minus = abeles.GDD(wvls)
t_GDD_p_plus = abeles.GDD(wvls)
t_GDD_p_minus = abeles.GDD(wvls)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2*(1.0+diff), sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_front_reverse.calculate_r_and_t_reverse(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_plus.calculate_R(r_and_t_front, pol)
T_front_plus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
R_front_reverse_plus.calculate_R(r_and_t_front_reverse, pol)
T_front_reverse_plus.calculate_T(r_and_t_front_reverse, n_substrate, n_medium, sin2_theta_0, pol)
R_plus.calculate_R_with_backside(T_front_plus, R_front_plus, T_front_reverse_plus, R_front_reverse_plus, R_back, n_substrate, substrate_thickness, sin2_theta_0)
T_plus.calculate_T_with_backside(T_front_plus, R_front_reverse_plus, T_back, R_back, n_substrate, substrate_thickness, sin2_theta_0)
A_plus.calculate_A(R_plus, T_plus)
R_reverse_plus.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse_plus, n_substrate, substrate_thickness, sin2_theta_0)
r_phase_s_plus.calculate_r_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
r_phase_p_plus.calculate_r_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.P)
t_phase_s_plus.calculate_t_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
t_phase_p_plus.calculate_t_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.P)
r_GD_s_plus.calculate_GD(r_phase_s_plus)
r_GD_p_plus.calculate_GD(r_phase_p_plus)
t_GD_s_plus.calculate_GD(t_phase_s_plus)
t_GD_p_plus.calculate_GD(t_phase_p_plus)
r_GDD_s_plus.calculate_GDD(r_phase_s_plus)
r_GDD_p_plus.calculate_GDD(r_phase_p_plus)
t_GDD_s_plus.calculate_GDD(t_phase_s_plus)
t_GDD_p_plus.calculate_GDD(t_phase_p_plus)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2*(1.0-diff), sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
r_and_t_front_reverse.calculate_r_and_t_reverse(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_minus.calculate_R(r_and_t_front, pol)
T_front_minus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
R_front_reverse_minus.calculate_R(r_and_t_front_reverse, pol)
T_front_reverse_minus.calculate_T(r_and_t_front_reverse, n_substrate, n_medium, sin2_theta_0, pol)
R_minus.calculate_R_with_backside(T_front_minus, R_front_minus, T_front_reverse_minus, R_front_reverse_minus, R_back, n_substrate, substrate_thickness, sin2_theta_0)
T_minus.calculate_T_with_backside(T_front_minus, R_front_reverse_minus, T_back, R_back, n_substrate, substrate_thickness, sin2_theta_0)
A_minus.calculate_A(R_minus, T_minus)
R_reverse_minus.calculate_R_with_backside(T_back_reverse, R_back_reverse, T_back, R_back, R_front_reverse_minus, n_substrate, substrate_thickness, sin2_theta_0)
r_phase_s_minus.calculate_r_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
r_phase_p_minus.calculate_r_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.P)
t_phase_s_minus.calculate_t_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.S)
t_phase_p_minus.calculate_t_phase(matrices_front, n_medium, n_substrate, sin2_theta_0, abeles.P)
r_GD_s_minus.calculate_GD(r_phase_s_minus)
r_GD_p_minus.calculate_GD(r_phase_p_minus)
t_GD_s_minus.calculate_GD(t_phase_s_minus)
t_GD_p_minus.calculate_GD(t_phase_p_minus)
r_GDD_s_minus.calculate_GDD(r_phase_s_minus)
r_GDD_p_minus.calculate_GDD(r_phase_p_minus)
t_GDD_s_minus.calculate_GDD(t_phase_s_minus)
t_GDD_p_minus.calculate_GDD(t_phase_p_minus)
dR_front_diff = [(R_front_plus[i] - R_front_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dT_front_diff = [(T_front_plus[i] - T_front_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dR_front_reverse_diff = [(R_front_reverse_plus[i] - R_front_reverse_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dT_front_reverse_diff = [(T_front_reverse_plus[i] - T_front_reverse_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dR_diff = [(R_plus[i] - R_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dT_diff = [(T_plus[i] - T_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dA_diff = [(A_plus[i] - A_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dR_reverse_diff = [(R_reverse_plus[i] - R_reverse_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_phase_s_diff = [(r_phase_s_plus[i] - r_phase_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_phase_p_diff = [(r_phase_p_plus[i] - r_phase_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_phase_s_diff = [(t_phase_s_plus[i] - t_phase_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_phase_p_diff = [(t_phase_p_plus[i] - t_phase_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_GD_s_diff = [(r_GD_s_plus[i] - r_GD_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_GD_p_diff = [(r_GD_p_plus[i] - r_GD_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_GD_s_diff = [(t_GD_s_plus[i] - t_GD_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_GD_p_diff = [(t_GD_p_plus[i] - t_GD_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_GDD_s_diff = [(r_GDD_s_plus[i] - r_GDD_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dr_GDD_p_diff = [(r_GDD_p_plus[i] - r_GDD_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_GDD_s_diff = [(t_GDD_s_plus[i] - t_GDD_s_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
dt_GDD_p_diff = [(t_GDD_p_plus[i] - t_GDD_p_minus[i]) / (2.0*thickness_SiO2*diff) for i in range(nb_wvls)]
stop = time.clock()
print "numerical calculation of all derivatives made in %.8f seconds" % (stop-start)

digits_dR_front = [0.0]*nb_wvls
digits_dT_front = [0.0]*nb_wvls
digits_dR_front_reverse = [0.0]*nb_wvls
digits_dT_front_reverse = [0.0]*nb_wvls
digits_dR = [0.0]*nb_wvls
digits_dT = [0.0]*nb_wvls
digits_dA = [0.0]*nb_wvls
digits_dR_reverse = [0.0]*nb_wvls
digits_r_phase_s = [0.0]*nb_wvls
digits_r_phase_p = [0.0]*nb_wvls
digits_t_phase_s = [0.0]*nb_wvls
digits_t_phase_p = [0.0]*nb_wvls
digits_r_GD_s = [0.0]*nb_wvls
digits_r_GD_p = [0.0]*nb_wvls
digits_t_GD_s = [0.0]*nb_wvls
digits_t_GD_p = [0.0]*nb_wvls
digits_r_GDD_s = [0.0]*nb_wvls
digits_r_GDD_p = [0.0]*nb_wvls
digits_t_GDD_s = [0.0]*nb_wvls
digits_t_GDD_p = [0.0]*nb_wvls
for i in range(nb_wvls):
	if dR_front_diff[i]-dR_front[i] == 0.0:
		digits_dR_front[i] = 100.0
	elif dR_front[i] == 0.0:
		digits_dR_front[i] = -math.log10( abs(dR_front_diff[i]) )
	else:
		digits_dR_front[i] = -math.log10( abs(dR_front_diff[i]-dR_front[i])/ abs(dR_front[i]) )
	
	if dT_front_diff[i]-dT_front[i] == 0.0:
		digits_dT_front[i] = 100.0
	elif dT_front[i] == 0.0:
		digits_dT_front[i] = -math.log10( abs(dT_front_diff[i]) )
	else:
		digits_dT_front[i] = -math.log10( abs(dT_front_diff[i]-dT_front[i])/ abs(dT_front[i]) )
	
	if dR_front_reverse_diff[i]-dR_front_reverse[i] == 0.0:
		digits_dR_front_reverse[i] = 100.0
	elif dR_front_reverse[i] == 0.0:
		digits_dR_front_reverse[i] = -math.log10( abs(dR_front_reverse_diff[i]) )
	else:
		digits_dR_front_reverse[i] = -math.log10( abs(dR_front_reverse_diff[i]-dR_front_reverse[i])/ abs(dR_front_reverse[i]) )
	
	if dT_front_reverse_diff[i]-dT_front_reverse[i] == 0.0:
		digits_dT_front_reverse[i] = 100.0
	elif dT_front_reverse[i] == 0.0:
		digits_dT_front_reverse[i] = -math.log10( abs(dT_front_reverse_diff[i]) )
	else:
		digits_dT_front_reverse[i] = -math.log10( abs(dT_front_reverse_diff[i]-dT_front_reverse[i])/ abs(dT_front_reverse[i]) )
	
	if dR_diff[i]-dR[i] == 0.0:
		digits_dR[i] = 100.0
	elif dR[i] == 0.0:
		digits_dR[i] = -math.log10( abs(dR_diff[i]) )
	else:
		digits_dR[i] = -math.log10( abs(dR_diff[i]-dR[i])/ abs(dR[i]) )
	
	if dT_diff[i]-dT[i] == 0.0:
		digits_dT[i] = 100.0
	elif dT[i] == 0.0:
		digits_dT[i] = -math.log10( abs(dT_diff[i]) )
	else:
		digits_dT[i] = -math.log10( abs(dT_diff[i]-dT[i])/ abs(dT[i]) )
	
	if dA_diff[i]-dA[i] == 0.0:
		digits_dA[i] = 100.0
	elif dA[i] == 0.0:
		digits_dA[i] = -math.log10( abs(dA_diff[i]) )
	else:
		digits_dA[i] = -math.log10( abs(dA_diff[i]-dA[i])/ abs(dA[i]) )
	
	if dR_reverse_diff[i]-dR_reverse[i] == 0.0:
		digits_dR_reverse[i] = 100.0
	elif dR_reverse[i] == 0.0:
		digits_dR_reverse[i] = -math.log10( abs(dR_reverse_diff[i]) )
	else:
		digits_dR_reverse[i] = -math.log10( abs(dR_reverse_diff[i]-dR_reverse[i])/ abs(dR_reverse[i]) )
	
	if dr_phase_s_diff[i]-dr_phase_s[i] == 0.0:
		digits_r_phase_s[i] = 100.0
	elif dr_phase_s[i] == 0.0:
		digits_r_phase_s[i] = -math.log10( abs(dr_phase_s_diff[i]) )
	else:
		digits_r_phase_s[i] = -math.log10( abs(dr_phase_s_diff[i]-dr_phase_s[i])/ abs(dr_phase_s[i]) )
	
	if dr_phase_p_diff[i]-dr_phase_p[i] == 0.0:
		digits_r_phase_p[i] = 100.0
	elif dr_phase_p[i] == 0.0:
		digits_r_phase_p[i] = -math.log10( abs(dr_phase_p_diff[i]) )
	else:
		digits_r_phase_p[i] = -math.log10( abs(dr_phase_p_diff[i]-dr_phase_p[i])/ abs(dr_phase_p[i]) )
	
	if dt_phase_s_diff[i]-dt_phase_s[i] == 0.0:
		digits_t_phase_s[i] = 100.0
	elif dt_phase_s[i] == 0.0:
		digits_t_phase_s[i] = -math.log10( abs(dt_phase_s_diff[i]) )
	else:
		digits_t_phase_s[i] = -math.log10( abs(dt_phase_s_diff[i]-dt_phase_s[i])/ abs(dt_phase_s[i]) )
	
	if dt_phase_p_diff[i]-dt_phase_p[i] == 0.0:
		digits_t_phase_p[i] = 100.0
	elif dt_phase_p[i] == 0.0:
		digits_t_phase_p[i] = -math.log10( abs(dt_phase_p_diff[i]) )
	else:
		digits_t_phase_p[i] = -math.log10( abs(dt_phase_p_diff[i]-dt_phase_p[i])/ abs(dt_phase_p[i]) )
	
	if dr_GD_s_diff[i]-dr_GD_s[i] == 0.0:
		digits_r_GD_s[i] = 100.0
	elif dr_GD_s[i] == 0.0:
		digits_r_GD_s[i] = -math.log10( abs(dr_GD_s_diff[i]) )
	else:
		digits_r_GD_s[i] = -math.log10( abs(dr_GD_s_diff[i]-dr_GD_s[i])/ abs(dr_GD_s[i]) )
	
	if dr_GD_p_diff[i]-dr_GD_p[i] == 0.0:
		digits_r_GD_p[i] = 100.0
	elif dr_GD_p[i] == 0.0:
		digits_r_GD_p[i] = -math.log10( abs(dr_GD_p_diff[i]) )
	else:
		digits_r_GD_p[i] = -math.log10( abs(dr_GD_p_diff[i]-dr_GD_p[i])/ abs(dr_GD_p[i]) )
	
	if dt_GD_s_diff[i]-dt_GD_s[i] == 0.0:
		digits_t_GD_s[i] = 100.0
	elif dt_GD_s[i] == 0.0:
		digits_t_GD_s[i] = -math.log10( abs(dt_GD_s_diff[i]) )
	else:
		digits_t_GD_s[i] = -math.log10( abs(dt_GD_s_diff[i]-dt_GD_s[i])/ abs(dt_GD_s[i]) )
	
	if dt_GD_p_diff[i]-dt_GD_p[i] == 0.0:
		digits_t_GD_p[i] = 100.0
	elif dt_GD_p[i] == 0.0:
		digits_t_GD_p[i] = -math.log10( abs(dt_GD_p_diff[i]) )
	else:
		digits_t_GD_p[i] = -math.log10( abs(dt_GD_p_diff[i]-dt_GD_p[i])/ abs(dt_GD_p[i]) )
	
	if dr_GDD_s_diff[i]-dr_GDD_s[i] == 0.0:
		digits_r_GDD_s[i] = 100.0
	elif dr_GDD_s[i] == 0.0:
		digits_r_GDD_s[i] = -math.log10( abs(dr_GDD_s_diff[i]) )
	else:
		digits_r_GDD_s[i] = -math.log10( abs(dr_GDD_s_diff[i]-dr_GDD_s[i])/ abs(dr_GDD_s[i]) )
	
	if dr_GDD_p_diff[i]-dr_GDD_p[i] == 0.0:
		digits_r_GDD_p[i] = 100.0
	elif dr_GDD_p[i] == 0.0:
		digits_r_GDD_p[i] = -math.log10( abs(dr_GDD_p_diff[i]) )
	else:
		digits_r_GDD_p[i] = -math.log10( abs(dr_GDD_p_diff[i]-dr_GDD_p[i])/ abs(dr_GDD_p[i]) )
	
	if dt_GDD_s_diff[i]-dt_GDD_s[i] == 0.0:
		digits_t_GDD_s[i] = 100.0
	elif dt_GDD_s[i] == 0.0:
		digits_t_GDD_s[i] = -math.log10( abs(dt_GDD_s_diff[i]) )
	else:
		digits_t_GDD_s[i] = -math.log10( abs(dt_GDD_s_diff[i]-dt_GDD_s[i])/ abs(dt_GDD_s[i]) )
	
	if dt_GDD_p_diff[i]-dt_GDD_p[i] == 0.0:
		digits_t_GDD_p[i] = 100.0
	elif dt_GDD_p[i] == 0.0:
		digits_t_GDD_p[i] = -math.log10( abs(dt_GDD_p_diff[i]) )
	else:
		digits_t_GDD_p[i] = -math.log10( abs(dt_GDD_p_diff[i]-dt_GDD_p[i])/ abs(dt_GDD_p[i]) )

print ""
print "Minimum, mean and maximum number of equal digits for thickness derivatives:"
print "         dR_front: %7.2f %7.2f %7.2f" % (min(digits_dR_front), sum(digits_dR_front)/len(digits_dR_front), max(digits_dR_front))
print "         dT_front: %7.2f %7.2f %7.2f" % (min(digits_dT_front), sum(digits_dT_front)/len(digits_dT_front), max(digits_dT_front))
print "  dR_front (rev.): %7.2f %7.2f %7.2f" % (min(digits_dR_front_reverse), sum(digits_dR_front_reverse)/len(digits_dR_front_reverse), max(digits_dR_front_reverse))
print "  dT_front (rev.): %7.2f %7.2f %7.2f" % (min(digits_dT_front_reverse), sum(digits_dT_front_reverse)/len(digits_dT_front_reverse), max(digits_dT_front_reverse))
print "               dR: %7.2f %7.2f %7.2f" % (min(digits_dR), sum(digits_dR)/len(digits_dR), max(digits_dR))
print "               dT: %7.2f %7.2f %7.2f" % (min(digits_dT), sum(digits_dT)/len(digits_dT), max(digits_dT))
print "               dA: %7.2f %7.2f %7.2f" % (min(digits_dA), sum(digits_dA)/len(digits_dA), max(digits_dA))
print "     dR (reverse): %7.2f %7.2f %7.2f" % (min(digits_dR_reverse), sum(digits_dR_reverse)/len(digits_dR_reverse), max(digits_dR_reverse))
print "       dr_phase_s: %7.2f %7.2f %7.2f" % (min(digits_r_phase_s), sum(digits_r_phase_s)/len(digits_r_phase_s), max(digits_r_phase_s))
print "       dr_phase_p: %7.2f %7.2f %7.2f" % (min(digits_r_phase_p), sum(digits_r_phase_p)/len(digits_r_phase_p), max(digits_r_phase_p))
print "       dt_phase_s: %7.2f %7.2f %7.2f" % (min(digits_t_phase_s), sum(digits_t_phase_s)/len(digits_t_phase_s), max(digits_t_phase_s))
print "       dt_phase_p: %7.2f %7.2f %7.2f" % (min(digits_t_phase_p), sum(digits_t_phase_p)/len(digits_t_phase_p), max(digits_t_phase_p))
print "          dr_GD_s: %7.2f %7.2f %7.2f" % (min(digits_r_GD_s), sum(digits_r_GD_s)/len(digits_r_GD_s), max(digits_r_GD_s))
print "          dr_GD_p: %7.2f %7.2f %7.2f" % (min(digits_r_GD_p), sum(digits_r_GD_p)/len(digits_r_GD_p), max(digits_r_GD_p))
print "          dt_GD_s: %7.2f %7.2f %7.2f" % (min(digits_t_GD_s), sum(digits_t_GD_s)/len(digits_t_GD_s), max(digits_t_GD_s))
print "          dt_GD_p: %7.2f %7.2f %7.2f" % (min(digits_t_GD_p), sum(digits_t_GD_p)/len(digits_t_GD_p), max(digits_t_GD_p))
print "         dr_GDD_s: %7.2f %7.2f %7.2f" % (min(digits_r_GDD_s), sum(digits_r_GDD_s)/len(digits_r_GDD_s), max(digits_r_GDD_s))
print "         dr_GDD_p: %7.2f %7.2f %7.2f" % (min(digits_r_GDD_p), sum(digits_r_GDD_p)/len(digits_r_GDD_p), max(digits_r_GDD_p))
print "         dt_GDD_s: %7.2f %7.2f %7.2f" % (min(digits_t_GDD_s), sum(digits_t_GDD_s)/len(digits_t_GDD_s), max(digits_t_GDD_s))
print "         dt_GDD_p: %7.2f %7.2f %7.2f" % (min(digits_t_GDD_p), sum(digits_t_GDD_p)/len(digits_t_GDD_p), max(digits_t_GDD_p))
print ""

start = time.clock()
pre_and_post_matrices.set_pre_and_post_matrices(0, n_TiO2, thickness_TiO2, sin2_theta_0)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2, sin2_theta_0)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, pol)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "Reset made in %.8f seconds" % (stop-start)


# Index derivatives.

start = time.clock()
n_SiO2TiO2_.set_dN_mixture(index_SiO2TiO2, center_wvl)
dMi.set_dMi_index(n_SiO2TiO2, dn_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
dM.calculate_dM(dMi, pre_and_post_matrices, 2)
stop = time.clock()
print "calculation of dMi and dM made in %.8f seconds" % (stop-start)

start = time.clock()
psi.calculate_psi_matrices(r_and_t_front, n_medium, n_substrate, sin2_theta_0)
dr_and_dt_front.calculate_dr_and_dt(dM, psi)
stop = time.clock()
print "calculation of psi matrices and dr_and_dt_front made in %.8f seconds" % (stop-start)

start = time.clock()
dR_front.calculate_dR(dr_and_dt_front, r_and_t_front, pol)
dT_front.calculate_dT(dr_and_dt_front, r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "calculation of dR_front and dT_front made in %.8f seconds" % (stop-start)

start = time.clock()
R_front_plus = abeles.R(wvls)
T_front_plus = abeles.T(wvls)
R_front_minus = abeles.R(wvls)
T_front_minus = abeles.T(wvls)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2*(1.0+diff), center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_plus.calculate_R(r_and_t_front, pol)
T_front_plus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2*(1.0-diff), center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_minus.calculate_R(r_and_t_front, pol)
T_front_minus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
dR_front_diff = [(R_front_plus[i] - R_front_minus[i]) / (2.0*index_SiO2TiO2*diff) for i in range(nb_wvls)]
dT_front_diff = [(T_front_plus[i] - T_front_minus[i]) / (2.0*index_SiO2TiO2*diff) for i in range(nb_wvls)]
stop = time.clock()
print "numerical calculation of dR_front and dT_front made in %.8f seconds" % (stop-start)

digits_dR_front = [0.0]*nb_wvls
digits_dT_front = [0.0]*nb_wvls
for i in range(nb_wvls):
	if dR_front_diff[i]-dR_front[i] == 0.0:
		digits_dR_front[i] = 100.0
	elif dR_front[i] == 0.0:
		digits_dR_front[i] = -math.log10( abs(dR_front_diff[i]) )
	else:
		digits_dR_front[i] = -math.log10( abs(dR_front_diff[i]-dR_front[i]) / abs(dR_front[i]) )
	
	if dT_front_diff[i]-dT_front[i] == 0.0:
		digits_dT_front[i] = 100.0
	elif dT_front[i] == 0.0:
		digits_dT_front[i] = -math.log10( abs(dT_front_diff[i]) )
	else:
		digits_dT_front[i] = -math.log10( abs(dT_front_diff[i]-dT_front[i]) / abs(dT_front[i]) )

print ""
print "Minimum, mean and maximum number of equal digits for index derivatives:"
print "         dR_front: %7.2f %7.2f %7.2f" % (min(digits_dR_front), sum(digits_dR_front)/len(digits_dR_front), max(digits_dR_front))
print "         dT_front: %7.2f %7.2f %7.2f" % (min(digits_dT_front), sum(digits_dT_front)/len(digits_dT_front), max(digits_dT_front))
print ""

start = time.clock()
pre_and_post_matrices.set_pre_and_post_matrices(0, n_TiO2, thickness_TiO2, sin2_theta_0)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2, sin2_theta_0)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, pol)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "Reset made in %.8f seconds" % (stop-start)


# Index derivatives with constant OT.

start = time.clock()
center_wvl_ = abeles.wvls(1)
center_wvl_.set_wvl(0, center_wvl)
n_SiO2TiO2_center_wvl__ = abeles.N_mixture(SiO2TiO2, center_wvl_)
n_SiO2TiO2_center_wvl__.set_N_mixture(index_SiO2TiO2, center_wvl)
n_SiO2TiO2_center_wvl_ = n_SiO2TiO2_center_wvl__.get_N_mixture()
n_SiO2TiO2_center_wvl = n_SiO2TiO2_center_wvl_[0]
sin2_theta_0_center_wvl = math.sin(math.radians(angle_of_constant_OT))**2
n_s_center_wvl = cmath.sqrt(n_SiO2TiO2_center_wvl*n_SiO2TiO2_center_wvl - sin2_theta_0_center_wvl)
stop = time.clock()
print "calculation of the index at center wavelength done in %.8f seconds" % (stop-start)

start = time.clock()
n_SiO2TiO2_.set_dN_mixture(index_SiO2TiO2, center_wvl)
dMi.set_dMi_index_with_constant_OT(n_SiO2TiO2, dn_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0, n_SiO2TiO2_center_wvl_, sin2_theta_0_center_wvl)
dM.calculate_dM(dMi, pre_and_post_matrices, 2)
stop = time.clock()
print "calculation of dMi and dM made in %.8f seconds" % (stop-start)

start = time.clock()
psi.calculate_psi_matrices(r_and_t_front, n_medium, n_substrate, sin2_theta_0)
dr_and_dt_front.calculate_dr_and_dt(dM, psi)
stop = time.clock()
print "calculation of psi matrices and dr_and_dt_front made in %.8f seconds" % (stop-start)

start = time.clock()
dR_front.calculate_dR(dr_and_dt_front, r_and_t_front, pol)
dT_front.calculate_dT(dr_and_dt_front, r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "calculation of dR_front and dT_front made in %.8f seconds" % (stop-start)

start = time.clock()
R_front_plus = abeles.R(wvls)
T_front_plus = abeles.T(wvls)
R_front_minus = abeles.R(wvls)
T_front_minus = abeles.T(wvls)
n_SiO2TiO2_center_wvl__.set_N_mixture(index_SiO2TiO2*(1.0+diff), center_wvl)
n_s_center_wvl_plus = cmath.sqrt(n_SiO2TiO2_center_wvl_[0]*n_SiO2TiO2_center_wvl_[0] - sin2_theta_0_center_wvl)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2*(1.0+diff), center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2*n_s_center_wvl.real/n_s_center_wvl_plus.real, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_plus.calculate_R(r_and_t_front, pol)
T_front_plus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
n_SiO2TiO2_center_wvl__.set_N_mixture(index_SiO2TiO2*(1.0-diff), center_wvl)
n_s_center_wvl_minus = cmath.sqrt(n_SiO2TiO2_center_wvl_[0]*n_SiO2TiO2_center_wvl_[0] - sin2_theta_0_center_wvl)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2*(1.0-diff), center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2*n_s_center_wvl.real/n_s_center_wvl_minus.real, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front_minus.calculate_R(r_and_t_front, pol)
T_front_minus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
dR_front_diff = [(R_front_plus[i] - R_front_minus[i]) / (2.0*index_SiO2TiO2*diff) for i in range(nb_wvls)]
dT_front_diff = [(T_front_plus[i] - T_front_minus[i]) / (2.0*index_SiO2TiO2*diff) for i in range(nb_wvls)]
stop = time.clock()
print "numerical calculation of dR_front and dT_front made in %.8f seconds" % (stop-start)

digits_dR_front = [0.0]*nb_wvls
digits_dT_front = [0.0]*nb_wvls
for i in range(nb_wvls):
	if dR_front_diff[i]-dR_front[i] == 0.0:
		digits_dR_front[i] = 100.0
	elif dR_front[i] == 0.0:
		digits_dR_front[i] = -math.log10(abs(dR_front_diff[i]))
	else:
		digits_dR_front[i] = -math.log10(abs(dR_front_diff[i]-dR_front[i]) / abs(dR_front[i]))
	
	if dT_front_diff[i]-dT_front[i] == 0.0:
		digits_dT_front[i] = 100.0
	elif dT_front[i] == 0.0:
		digits_dT_front[i] = -math.log10(abs(dT_front_diff[i]))
	else:
		digits_dT_front[i] = -math.log10(abs(dT_front_diff[i]-dT_front[i]) / abs(dT_front[i]))
	
print ""
print "Minimum, mean and maximum number of equal digits for index derivatives with constant OT:"
print "         dR_front: %7.2f %7.2f %7.2f" % (min(digits_dR_front), sum(digits_dR_front)/len(digits_dR_front), max(digits_dR_front))
print "         dT_front: %7.2f %7.2f %7.2f" % (min(digits_dT_front), sum(digits_dT_front)/len(digits_dT_front), max(digits_dT_front))
print ""

start = time.clock()
pre_and_post_matrices.set_pre_and_post_matrices(0, n_TiO2, thickness_TiO2, sin2_theta_0)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2, sin2_theta_0)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, pol)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "Reset made in %.8f seconds" % (stop-start)


# needles are put in the second layer.

start = time.clock()
spacing = thickness_SiO2/(nb_needles-1)
dMi_needles = abeles.needle_matrices(wvls, nb_needles)
dMi_needles.set_needle_positions(spacing)
stop = time.clock()
print "dMi_needles object created in %.8f seconds" % (stop-start)

start = time.clock()
dMi_needles.calculate_dMi_needles(n_SiO2, n_TiO2, thickness_SiO2, sin2_theta_0);
stop = time.clock()
print "dMi_needles calculated in %.8f seconds" % (stop-start)

dR_needles_anal = [None]*nb_needles
dT_needles_anal = [None]*nb_needles

start = time.clock()
psi.calculate_psi_matrices(r_and_t_front, n_medium, n_substrate, sin2_theta_0)
for i in range(nb_needles):
	dMi_needle = dMi_needles[i]
	dM.calculate_dM(dMi_needle, pre_and_post_matrices, 1)
	dr_and_dt_front.calculate_dr_and_dt(dM, psi);
	dR_front.calculate_dR(dr_and_dt_front, r_and_t_front, pol);
	dT_front.calculate_dT(dr_and_dt_front, r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
	dR_needles_anal[i] = dR_front[:]
	dT_needles_anal[i] = dT_front[:]
stop = time.clock()
print "Other derivatives related to needles calculated in %.8f seconds" % (stop-start)

dR_needles_diff = [None]*nb_needles
dT_needles_diff = [None]*nb_needles

start = time.clock()
matrices_layer = abeles.matrices(wvls)
matrices_global = abeles.matrices(wvls)
R_front_diff = abeles.R(wvls)
T_front_diff = abeles.T(wvls)
for i in range(nb_needles):
	position = spacing * i
	matrices_global.set_matrices_unity()
	matrices_layer.set_matrices(n_TiO2, thickness_TiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_SiO2, position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_TiO2, needle_thickness, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_SiO2, thickness_SiO2-position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	r_and_t_front.calculate_r_and_t(matrices_global, n_medium, n_substrate, sin2_theta_0)
	R_front_diff.calculate_R(r_and_t_front, pol)
	T_front_diff.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
	dR_needles_diff[i] = [(R_front_diff[i_wvl] - R_front[i_wvl]) / needle_thickness for i_wvl in range(nb_wvls)]
	dT_needles_diff[i] = [(T_front_diff[i_wvl] - T_front[i_wvl]) / needle_thickness for i_wvl in range(nb_wvls)]
stop = time.clock()
print "Numerical calculations related to needles calculated in %.8f seconds" % (stop-start)

digits_dR_needles = [[0.0]*nb_wvls for i in range(nb_needles)]
digits_dT_needles = [[0.0]*nb_wvls for i in range(nb_needles)]

for i in range(nb_needles):
	for i_wvl in range(nb_wvls):
		if dR_needles_diff[i][i_wvl]-dR_needles_anal[i][i_wvl] == 0.0:
			digits_dR_needles[i][i_wvl] = 100.0
		elif dR_needles_anal[i][i_wvl] == 0.0:
			digits_dR_needles[i][i_wvl] = -math.log10(abs(dR_needles_diff[i][i_wvl]))
		else:
			digits_dR_needles[i][i_wvl] = -math.log10(abs(dR_needles_diff[i][i_wvl]-dR_needles_anal[i][i_wvl]) / abs(dR_needles_anal[i][i_wvl]))
		
		if dT_needles_diff[i][i_wvl]-dT_needles_anal[i][i_wvl] == 0.0:
			digits_dT_needles[i][i_wvl] = 100.0
		elif dT_needles_anal[i][i_wvl] == 0.0:
			digits_dT_needles[i][i_wvl] = -math.log10(abs(dT_needles_diff[i][i_wvl]))
		else:
			digits_dT_needles[i][i_wvl] = -math.log10(abs(dT_needles_diff[i][i_wvl]-dT_needles_anal[i][i_wvl]) / abs(dT_needles_anal[i][i_wvl]))

mean_digits_dR_needles = 0.0
mean_digits_dT_needles = 0.0
for i in range(nb_needles):
	mean_digits_dR_needles += sum(digits_dR_needles[i])
	mean_digits_dT_needles += sum(digits_dT_needles[i])
mean_digits_dR_needles /= nb_needles*nb_wvls
mean_digits_dT_needles /= nb_needles*nb_wvls

print ""
print "Minimum, mean and maximum number of equal digits for needles:"
print "         dR_front: %7.2f %7.2f %7.2f" % (min(min(digits_dR_needles)), mean_digits_dR_needles, max(max(digits_dR_needles)))
print "         dT_front: %7.2f %7.2f %7.2f" % (min(min(digits_dT_needles)), mean_digits_dT_needles, max(max(digits_dT_needles)))
print ""

start = time.clock()
pre_and_post_matrices.set_pre_and_post_matrices(0, n_TiO2, thickness_TiO2, sin2_theta_0)
pre_and_post_matrices.set_pre_and_post_matrices(1, n_SiO2, thickness_SiO2, sin2_theta_0)
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
pre_and_post_matrices.set_pre_and_post_matrices(2, n_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0)
pre_and_post_matrices.multiply_pre_and_post_matrices()
r_and_t_front.calculate_r_and_t(matrices_front, n_medium, n_substrate, sin2_theta_0)
R_front.calculate_R(r_and_t_front, pol)
T_front.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
stop = time.clock()
print "Reset made in %.8f seconds" % (stop-start)


# Steps are put in the third layer.

start = time.clock()
spacing = thickness_SiO2TiO2/(nb_steps-1)
dMi_steps = abeles.needle_matrices(wvls, nb_steps)
dMi_steps.set_needle_positions(spacing)
stop = time.clock()
print "dMi_steps object created in %.8f seconds" % (stop-start)

start = time.clock()
n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2, center_wvl)
n_SiO2TiO2_.set_dN_mixture(index_SiO2TiO2, center_wvl)
dMi_steps.calculate_dMi_steps(n_SiO2TiO2, dn_SiO2TiO2, thickness_SiO2TiO2, sin2_theta_0);
stop = time.clock()
print "dMi_steps calculated in %.8f seconds" % (stop-start)

dR_steps_anal = [None]*nb_steps
dT_steps_anal = [None]*nb_steps

start = time.clock()
psi.calculate_psi_matrices(r_and_t_front, n_medium, n_substrate, sin2_theta_0)
for i in range(nb_steps):
	dMi_step = dMi_steps[i]
	dM.calculate_dM(dMi_step, pre_and_post_matrices, 2)
	dr_and_dt_front.calculate_dr_and_dt(dM, psi);
	dR_front.calculate_dR(dr_and_dt_front, r_and_t_front, pol);
	dT_front.calculate_dT(dr_and_dt_front, r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
	dR_steps_anal[i] = dR_front[:]
	dT_steps_anal[i] = dT_front[:]
stop = time.clock()
print "Other derivatives related to steps calculated in %.8f seconds" % (stop-start)

dR_steps_diff = [None]*nb_steps
dT_steps_diff = [None]*nb_steps

start = time.clock()
matrices_layer = abeles.matrices(wvls)
matrices_global = abeles.matrices(wvls)
R_front_plus = abeles.R(wvls)
T_front_plus = abeles.T(wvls)
R_front_minus = abeles.R(wvls)
T_front_minus = abeles.T(wvls)
for i in range(nb_steps):
	position = spacing * i
	# Difference in the positive direction.
	matrices_global.set_matrices_unity()
	matrices_layer.set_matrices(n_TiO2, thickness_TiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_SiO2, thickness_SiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2-step_delta_n/2.0, center_wvl)
	matrices_layer.set_matrices(n_SiO2TiO2, position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2+step_delta_n/2.0, center_wvl)
	matrices_layer.set_matrices(n_SiO2TiO2, thickness_SiO2TiO2-position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	r_and_t_front.calculate_r_and_t(matrices_global, n_medium, n_substrate, sin2_theta_0)
	R_front_plus.calculate_R(r_and_t_front, pol)
	T_front_plus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
	# Difference in the negative direction.	
	matrices_global.set_matrices_unity()
	matrices_layer.set_matrices(n_TiO2, thickness_TiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	matrices_layer.set_matrices(n_SiO2, thickness_SiO2, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2+step_delta_n/2.0, center_wvl)
	matrices_layer.set_matrices(n_SiO2TiO2, position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	n_SiO2TiO2_.set_N_mixture(index_SiO2TiO2-step_delta_n/2.0, center_wvl)
	matrices_layer.set_matrices(n_SiO2TiO2, thickness_SiO2TiO2-position, sin2_theta_0)
	matrices_global.multiply_matrices(matrices_layer)
	r_and_t_front.calculate_r_and_t(matrices_global, n_medium, n_substrate, sin2_theta_0)
	R_front_minus.calculate_R(r_and_t_front, pol)
	T_front_minus.calculate_T(r_and_t_front, n_medium, n_substrate, sin2_theta_0, pol)
	dR_steps_diff[i] = [0.5 * (R_front_plus[i_wvl] - R_front_minus[i_wvl]) / step_delta_n for i_wvl in range(nb_wvls)]
	dT_steps_diff[i] = [0.5 * (T_front_plus[i_wvl] - T_front_minus[i_wvl]) / step_delta_n for i_wvl in range(nb_wvls)]
stop = time.clock()
print "Numerical calculations related to steps calculated in %.8f seconds" % (stop-start)

digits_dR_steps = [[0.0]*nb_wvls for i in range(nb_steps)]
digits_dT_steps = [[0.0]*nb_wvls for i in range(nb_steps)]

for i in range(nb_steps):
	for i_wvl in range(nb_wvls):
		if dR_steps_diff[i][i_wvl]-dR_steps_anal[i][i_wvl] == 0.0:
			digits_dR_steps[i][i_wvl] = 100.0
		elif dR_steps_anal[i][i_wvl] == 0.0:
			digits_dR_steps[i][i_wvl] = -math.log10( abs(dR_steps_diff[i][i_wvl]) )
		else:
			digits_dR_steps[i][i_wvl] = -math.log10( abs(dR_steps_diff[i][i_wvl]-dR_steps_anal[i][i_wvl])/ abs(dR_steps_anal[i][i_wvl]) )
		
		if dT_steps_diff[i][i_wvl]-dT_steps_anal[i][i_wvl] == 0.0:
			digits_dT_steps[i][i_wvl] = 100.0
		elif dT_steps_anal[i][i_wvl] == 0.0:
			digits_dT_steps[i][i_wvl] = -math.log10( abs(dT_steps_diff[i][i_wvl]) )
		else:
			digits_dT_steps[i][i_wvl] = -math.log10( abs(dT_steps_diff[i][i_wvl]-dT_steps_anal[i][i_wvl])/ abs(dT_steps_anal[i][i_wvl]) )

mean_digits_dR_steps = 0.0
mean_digits_dT_steps = 0.0
for i in range(nb_steps):
	mean_digits_dR_steps += sum(digits_dR_steps[i])
	mean_digits_dT_steps += sum(digits_dT_steps[i])
mean_digits_dR_steps /= nb_steps*nb_wvls
mean_digits_dT_steps /= nb_steps*nb_wvls

print ""
print "Minimum, mean and maximum number of equal digits for steps:"
print "         dR_front: %7.2f %7.2f %7.2f" % (min(min(digits_dR_steps)), mean_digits_dR_steps, max(max(digits_dR_steps)))
print "         dT_front: %7.2f %7.2f %7.2f" % (min(min(digits_dT_steps)), mean_digits_dT_steps, max(max(digits_dT_steps)))
print ""
