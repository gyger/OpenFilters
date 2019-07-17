# tests.py
# 
# Test the various functions provided by moremath. Provide the list of
# tests to execute. If no argument is provided, all the tests are
# executed.
#
# Copyright (c) 2006,2007,2009,2014 Stephane Larouche.
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

import moremath


print ""


if moremath.get_moremath_dll_import_success():
	print "Working with the dll."
else:
	print "Working with Python versions."
print ""


# Get the list of tests to execute. If no test is provided, execute all tests.
tests = sys.argv[1:]
if tests == []:
	tests = ["Gauss_Jordan", "integration", "interpolation", "least_squares", "Levenberg_Marquardt", "limits", "Newton_polynomials", "QR", "roots", "StRD"]


# Test the Gauss-Jordan elimination.
if "Gauss_Jordan" in tests:
	tests.remove("Gauss_Jordan")
	
	print ""
	print "========== Gauss_Jordan tests =========="
	print ""
	
	from moremath import Gauss_Jordan
	
	import copy
	import random
	from moremath import linear_algebra
	from moremath import random_system
	
	# Make a linear system.
	print "----- Square system: -----"
	m = 100
	r = 100
	print "Creating a %i by %i system of full rank." % (m, m)
	A, b = random_system.random_system(m, m, r, 0)
	
	# Solve the system and calculate the inverse matrix using Gauss-
	# Jordan elimination.
	iA = copy.deepcopy(A)
	x = copy.deepcopy(b)
	
	start = time.clock()
	Gauss_Jordan.Gauss_Jordan(iA, [x])
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	print ""
	
	# Reduce the system.
	print "----- Reduced square system: -----"
	use = [1]*m
	for i in range(5):
		use[random.randint(0, m-1)] = 0
	iA = copy.deepcopy(A)
	x = copy.deepcopy(b)
	
	# Solve the reduced system and calculate the inverse matrix.
	start = time.clock()
	Gauss_Jordan.Gauss_Jordan(iA, [x], use)
	end = time.clock()
	
	# Set the unused values to 0 before multiplying matrices.
	for col in range(m):
		for row in range(m):
			A[col][row] *= use[col]*use[row]
			iA[col][row] *= use[col]*use[row]
	for row in range(m):
		b[row] *= use[row]
		x[row] *= use[row]
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the verifications.
	print "solved in %.4f s." % (end-start)
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	print ""


if "integration" in tests:
	tests.remove("integration")
	
	print ""
	print "========== integration tests =========="
	print ""
	
	from moremath import integration

	import math
	
	# Test using the sinus function.
	a = 0.0
	b = 1.0
	nb_points = [10, 100, 1000, 10000]
	for n in nb_points:
		numerical_trapezoidal = integration.trapezoidal(math.sin, a, b, n)
		numerical_cubic = integration.cubic(math.sin, a, b, n)
		analytical = math.cos(a)-math.cos(b)
		
		print "for n =", n, " trapezoidal error is: ", numerical_trapezoidal - analytical
		print "for n =", n, " cubic error is: ", numerical_cubic - analytical
	
	print ""


# Test the interpolation methods.
if "interpolation" in tests:
	tests.remove("interpolation")
	
	print ""
	print "========== interpolation tests =========="
	print ""
	
	from moremath import interpolation
	
	# The known points.
	length = 5
	Xa = range(length)
	Ya = [Xa[i]*Xa[i] for i in range(length)]
	
	# Set the spline.
	my_spline = interpolation.new_spline(length)
	interpolation.init_spline(my_spline, Xa, Ya)
	
	# Set the interpolation points and calculate the analytic values
	# of the function and it's derivative.
	nb_points = 21
	X = [i*0.2 for i in range(nb_points)]
	Y = [X[i]*X[i] for i in range(nb_points)]
	dY = [2.0*X[i] for i in range(nb_points)]
	
	# Locate where the values are.
	positions = [interpolation.locate(Xa, length, X[i]) for i in range(nb_points)]
	for i in range(nb_points):
		if positions[i] < 0: positions[i] = 0
		elif positions[i] > length - 2: positions[i] = length - 2
	
	# Calculate Y and dY values using the spline and also inverse the
	# spline.
	Y_spline = [0.0]*nb_points
	dY_spline = [0.0]*nb_points
	X_spline = [0.0]*nb_points
	interpolation.evaluate_spline(my_spline, X, Y_spline, positions, nb_points)
	interpolation.evaluate_spline_derivative(my_spline, X, dY_spline, positions, nb_points)
	interpolation.evaluate_spline_inverse(my_spline, X_spline, Y, positions, nb_points)
	
	# Show the results.
	print "%10s %10s %10s %10s %10s %10s" % ("X", "Y", "dY", "Y_spline", "dY_spline", "X_spline")
	for i in range(nb_points):
		print "%10.2f %10.2f %10.2f %10.2f %10.2f %10.2f" % (X[i], Y[i], dY[i], Y_spline[i], dY_spline[i], X_spline[i])
	
	# Delete the spline.
	interpolation.del_spline(my_spline)
	
	print ""


# Test the least square methods.
if "least_squares" in tests:
	tests.remove("least_squares")
	
	print ""
	print "========== least_squares tests =========="
	print ""
	
	from moremath import least_squares
	
	import random
	
	a_0 = random.uniform(-1.0, 1.0)
	a_1 = random.uniform(-1.0, 1.0)
	a_2 = random.uniform(-1.0, 1.0)
	a_3 = random.uniform(-1.0, 1.0)
	
	X = [random.uniform(-1.0, 1.0) for i in range(100)]
	
	sigma = 0.01
	
	print ""
	print "----- Linear least-squares method: -----"
	
	Y = [random.gauss(a_0+a_1*x, sigma) for x in X]
	
	a_0_fit, a_1_fit = least_squares.least_squares_linear(X, Y)
	
	print "%4s  %10s  %10s" %("", "value", "fit")
	print "%4s  %10.6f  %10.6f" %("a_0:", a_0, a_0_fit)
	print "%4s  %10.6f  %10.6f" %("a_1:", a_1, a_1_fit)
	
	print ""
	print "----- Quadradic least-squares method: -----"
	
	Y = [random.gauss(a_0+x*(a_1+x*a_2), sigma) for x in X]
	
	a_0_fit, a_1_fit, a_2_fit = least_squares.least_squares_quadratic(X, Y)
	
	print "%4s  %10s  %10s" %("", "value", "fit")
	print "%4s  %10.6f  %10.6f" %("a_0:", a_0, a_0_fit)
	print "%4s  %10.6f  %10.6f" %("a_1:", a_1, a_1_fit)
	print "%4s  %10.6f  %10.6f" %("a_2:", a_2, a_2_fit)
	
	print ""
	print "----- Cubic least-squares method: -----"
	
	Y = [random.gauss(a_0+x*(a_1+x*(a_2+x*a_3)), sigma) for x in X]
	
	a_0_fit, a_1_fit, a_2_fit, a_3_fit = least_squares.least_squares_cubic(X, Y)
	
	print "%4s  %10s  %10s" %("", "value", "fit")
	print "%4s  %10.6f  %10.6f" %("a_0:", a_0, a_0_fit)
	print "%4s  %10.6f  %10.6f" %("a_1:", a_1, a_1_fit)
	print "%4s  %10.6f  %10.6f" %("a_2:", a_2, a_2_fit)
	print "%4s  %10.6f  %10.6f" %("a_3:", a_3, a_3_fit)
	
	print ""
	print "----- Polynomial least-squares method (applied on cubic polynomial): -----"
	
	a_0_fit, a_1_fit, a_2_fit, a_3_fit = least_squares.least_squares(X, Y, 3)
	
	print "%4s  %10s  %10s" %("", "value", "fit")
	print "%4s  %10.6f  %10.6f" %("a_0:", a_0, a_0_fit)
	print "%4s  %10.6f  %10.6f" %("a_1:", a_1, a_1_fit)
	print "%4s  %10.6f  %10.6f" %("a_2:", a_2, a_2_fit)
	print "%4s  %10.6f  %10.6f" %("a_3:", a_3, a_3_fit)
	
	print ""


# Test the Levenberg-Marquardt method using the NIST standard tests.
if "Levenberg_Marquardt" in tests:
	tests.remove("Levenberg_Marquardt")
	
	print ""
	print "========== Levenberg_Marquardt tests =========="
	print ""
	
	from moremath import Levenberg_Marquardt
	
	import math
	import StRD
	
 	# Stop criteria.
	max_iterations = 2000
	min_gradient = 1.0E-9
	acceptable_chi_2 = 0.0
	min_chi_2_change = 1.0E-9
	
	# A few variables to keep stats.
	nb_tests = len(StRD.tests)
	nb_success = 0
	total_nb_iterations = 0
	total_nb_f_eval = 0
	total_nb_df_eval = 0
	total_time = 0.0
	
	for test in StRD.tests:
		
		# Get the test.
		f, df, X, Y, par, start, SSR, level = StRD.get_test(test)
		
		# Choose a set of starting values.
		b = start[1][:]
		
		# Don't consider sigma.
		sigma = [1.0]*len(Y)
		
 		# Init the Levenberg-Marquardt method.
		my_optimizer = Levenberg_Marquardt.Levenberg_Marquardt(f, df, b, Y, sigma, X)
 		my_optimizer.set_stop_criteria(min_gradient, acceptable_chi_2, min_chi_2_change)
 		my_optimizer.prepare()
		
		start_time = time.clock()
		for iteration in range(max_iterations):
			answer = my_optimizer.iterate()
 			if answer == Levenberg_Marquardt.MINIMUM_FOUND or answer == Levenberg_Marquardt.CHI_2_IS_OK or answer == Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL:
 				break
		stop_time = time.clock()
		test_time = stop_time - start_time
		
		# Calculate the correlation matrix. This is only used to check for
		# crash due to overflow and other conditions.
		C = my_optimizer.get_correlation_matrix()
 		
 		# Get the SSR.
 		chi_2 = my_optimizer.get_chi_2()
		
		# Calculate the number of correct digits on every parameter and on
		# the SSR.
		nb_par = len(par)
		digits = [0.0]*nb_par
		for i in range(nb_par):
			if b[i]-par[i] == 0.0:
				digits[i] = 100
			elif par[i] == 0.0:
				digits[i] = round(-math.log10( abs(b[i]) ) )
			else:
				digits[i] = round(-math.log10( abs(b[i]-par[i])/ abs(par[i]) ) )
		if chi_2-SSR == 0.0:
			digits_SSR = 100
		elif SSR == 0.0:
			digits_SSR = round(-math.log10( abs(chi_2) ) )
		else:
			digits_SSR = round(-math.log10( abs(chi_2-SSR)/ SSR ) )
		
		# Evaluate if the fit has passed of failed. We consider a fit has
		# passed if at least 4 digits of every parameter are ok.
		min_digits = digits[0]
		for i in range(2, nb_par):
			min_digits = min(min_digits, digits[i])
		if min_digits >= 4:
			success = 1
		else:
			success = 0
		
		# Get the number of function and jacobian evaluation.
		nb_f_eval, nb_df_eval = my_optimizer.get_stats()
		
		# If test succeded, increase the variable.
		if success:
			nb_success += 1
			total_nb_iterations += iteration+1
			total_nb_f_eval += nb_f_eval
			total_nb_df_eval += nb_df_eval
			total_time += test_time
		
		print ""
		print test
		print "  Level of difficulty:", level
		if success:
			print "  PASS after, %i function and %i jacobian evaluations in %.4f seconds." % (nb_f_eval, nb_df_eval, test_time)
		else:
			print "  FAIL after, %i function and %i jacobian evaluations in %.4f seconds." % (nb_f_eval, nb_df_eval, test_time)
		if answer == Levenberg_Marquardt.MINIMUM_FOUND:
			print "  Fit stopped because a minimum was found."
 		elif answer == Levenberg_Marquardt.CHI_2_IS_OK:
			print "  Fit stopped an acceptable chi square was found."
 		elif answer == Levenberg_Marquardt.CHI_2_CHANGE_TOO_SMALL:
			print "  Fit stopped because chi square change is too small."
 		elif answer == Levenberg_Marquardt.DELTA_IS_TOO_SMALL:
			print "  Fit stopped because the trust zone is smaller than the machine precision."
		else:
			print "  Fit stopped because maximum iterations reached."
		print "             Start            Optimized          Certified     Digits"
		for i in range(len(par)):
	 		print "  b%1i  %18.10e %18.10e %18.10e   %2i" % (i+1, start[1][i], b[i], par[i], digits[i])
 		print "  SSR                    %18.10e %18.10e   %2i" % (chi_2, SSR, digits_SSR)
	
	if nb_success != nb_tests:
		print ""
		print "%i tests out of %i were successfull." % (nb_success, nb_tests)
	else:
		print ""
		print "All %i tests were successfull." % nb_tests
	if nb_success:
		print "Successfull tests took a mean of %.1f iterations and %.3f seconds." % (float(total_nb_iterations)/nb_success, total_time/nb_success)
	
	print ""


# Test the limits.
if "limits" in tests:
	tests.remove("limits")
	
	print ""
	print "========== limits tests =========="
	print ""
	
	from moremath import limits
	
	print "epsilon:", limits.epsilon
	print "min:", limits.min
	
	print ""


# Test the Newton polynomials.
if "Newton_polynomials" in tests:
	tests.remove("Newton_polynomials")
	
	print ""
	print "========== Newton_polynomials tests =========="
	print ""
	
	from moremath import Newton_polynomials
	
	import random
	import linear_algebra
	
	print ""
	print "----- Linear -----"
	
	X = [random.uniform(-1.0, 1.0) for i in range(2)]
	Y = [random.uniform(-1.0, 1.0) for i in range(2)]
	
	b = Newton_polynomials.Newton_linear(X, Y)
	norm = linear_algebra.norm([b[0]+b[1]*X[i]-Y[i] for i in range(2)])
	
	print "norm(f(x)-y) (should be 0):", norm
	
	print ""
	print "----- Quadratic -----"
	
	X = [random.uniform(-1.0, 1.0) for i in range(3)]
	Y = [random.uniform(-1.0, 1.0) for i in range(3)]
	
	b = Newton_polynomials.Newton_quadratic(X, Y)
	norm = linear_algebra.norm([b[0]+b[1]*X[i]+b[2]*X[i]*X[i]-Y[i] for i in range(3)])
	
	print "norm(f(x)-y) (should be 0):", norm
	
	print ""
	print "----- Cubic -----"
	
	X = [random.uniform(-1.0, 1.0) for i in range(4)]
	Y = [random.uniform(-1.0, 1.0) for i in range(4)]
	
	b = Newton_polynomials.Newton_cubic(X, Y)
	norm = linear_algebra.norm([b[0]+b[1]*X[i]+b[2]*X[i]*X[i]+b[3]*X[i]*X[i]*X[i]-Y[i] for i in range(4)])
	
	print "norm(f(x)-y) (should be 0):", norm
	
	print ""



# Test the QR method.
if "QR" in tests:
	tests.remove("QR")
	
	print ""
	print "========== QR tests =========="
	print ""
	
	from moremath import QR
	
	import copy
	import random
	import linear_algebra
	import random_system
	
	# Square system.
	print ""
	print "----- Square system: -----"
	m = 100
	n = 100
	r = 100
	print "Creating a %i by %i system of full rank." % (m, n)
	A, b = random_system.random_system(m, n, r)
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Badly scaled square system.
	print ""
	print "----- Badly scaled square system: -----"
	m = 100
	n = 100
	r = 100
	print "Creating a %i by %i system of full rank." % (m, n)
	A, b = random_system.random_system(m, n, r)
	
	# Rescale the columns:
	for col in range(m):
		exponent = random.uniform(-100.0, 100.0)
		factor = 10**exponent
		for row in range(n):
			A[col][row] *= factor
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Make an overdetermined system.
	print ""
	print "----- Overdetermined system: -----"
	m = 50
	n = 200
	r = 50
	print "Creating a %i by %i system." % (m, n)
	A, b = random_system.random_system(m, n, r)
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be small):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Make a rank deficient system.
	print ""
	print "----- Rank deficient system: -----"
	m = 100
	n = 100
	r = 90
	print "Creating a %i by %i system of rank %i." % (m, n, r)
	A, b = random_system.random_system(m, n, r, True)
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Make a badly scaled rank deficient system.
	print ""
	print "----- Badly scaled rank deficient system: -----"
	m = 100
	n = 100
	r = 90
	print "Creating a %i by %i system of rank %i." % (m, n, r)
	A, b = random_system.random_system(m, n, r, True)
	
	# Rescale the columns:
	for col in range(m):
		exponent = random.uniform(-100, 100.0)
		factor = 10**exponent
		for row in range(n):
			A[col][row] *= factor
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Make a rank deficient overdetermined system.
	print ""
	print "----- Rank deficient overdetermined system: -----"
	m = 50
	n = 200
	r = 40
	print "Creating a %i by %i system of rank %i." % (m, n, r)
	A, b = random_system.random_system(m, n, r, False)
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be small):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])

	# Make a system.
	print ""
	print "----- Rectangular system: -----"
	m = 50
	n = 200
	r = 50
	print "Creating a %i by %i system of rank %i." % (m, n, r)
	A, b = random_system.random_system(m, n, r, False)
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	x = [0.0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	QR.QTb(A_QR, diag, perm, c)
	QR.R_solve(A_QR, diag, perm, c, x)
	end = time.clock()
	
	# Verify the calculations.
	Ax = linear_algebra.matrix_product(A, [x])
	
	# Show the results.
	print "solved in %.4f s." % (end-start)
	print "found rank = %i" % rank
	print "norm(Ax-b) (should be small):", linear_algebra.norm(linear_algebra.matrix_difference(Ax, [b])[0])
	
	# Augment the system using a diagonal matrix.
	print ""
	print "----- Augmented rectangular system 1: -----"
	
	# Add diagonal elements.
	D_1 = [random.uniform(-1.0, 1.0) for i in range(m)]
	
	start = time.clock()
	x_augmented_1 = QR.R_solve_with_update(A_QR, diag, perm, c, D_1)
	end = time.clock()
	
	print "updated and solved in %.4f s." % (end-start)
	
	# Augment the system using a diagonal matrix.
	print ""
	print "----- Augmented rectangular system 2: -----"
	
	# Add diagonal elements.
	D_2 = [random.uniform(-100.0, 100.0) for i in range(m)]
	
	start = time.clock()
	x_augmented_2 = QR.R_solve_with_update(A_QR, diag, perm, c, D_2)
	end = time.clock()
	
	print "updated and solved in %.4f s." % (end-start)
	
	# Create a rectangular matrix equivalent to the augmented system.
	print ""
	print "----- Equivalent rectangular system 1: -----"
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Enlarge the system.
	for i in range(m):
		A_QR[i] += [0.0]*m
		A_QR[i][n+i] = D_1[i]
	c += [0.0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x_equivalent = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	print "solved in %.4f s." % (end-start)
	print "norm(x_augmented-x_equivalent) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference([x_equivalent], [x_augmented_1])[0])
	
	# Create a rectangular matrix equivalent to the augmented system.
	print ""
	print "----- Equivalent rectangular system 2: -----"
	
	A_QR = copy.deepcopy(A)
	c = copy.deepcopy(b)
	diag = [0.0]*m
	perm = [0]*m
	
	# Enlarge the system.
	for i in range(m):
		A_QR[i] += [0.0]*m
		A_QR[i][n+i] = D_2[i]
	c += [0.0]*m
	
	# Solve the system using QR factorization.
	start = time.clock()
	rank = QR.QR(A_QR, diag, perm)
	x_equivalent = QR.QR_solve(A_QR, diag, perm, c)
	end = time.clock()
	
	print "solved in %.4f s." % (end-start)
	print "norm(x_augmented-x_equivalent) (should be 0):", linear_algebra.norm(linear_algebra.matrix_difference([x_equivalent], [x_augmented_2])[0])
	
	print ""


# Test the roots.
if "roots" in tests:
	tests.remove("roots")
	
	print ""
	print "========== roots tests =========="
	print ""
	
	from moremath import roots
	
	found_roots = [0.0]*3
	
	a_0 = 5.0
	a_1 = 1.0
	
	nb_roots = roots.roots_linear(found_roots, a_0, a_1)
	verification = [a_0 + a_1*found_roots[i] for i in range(nb_roots)]
	print ""
	print "Linear:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 20.0
	a_1 = -10.0
	a_2 = 1.0
	
	nb_roots = roots.roots_quadratic(found_roots, a_0, a_1, a_2)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*a_2) for i in range(nb_roots)]
	print ""
	print "Quadratic with 2 roots:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 25.0
	a_1 = -10.0
	a_2 = 1.0
	
	nb_roots = roots.roots_quadratic(found_roots, a_0, a_1, a_2)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*a_2) for i in range(nb_roots)]
	print ""
	print "Quadratic with double root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 30.0
	a_1 = -10.0
	a_2 = 1.0
	
	nb_roots = roots.roots_quadratic(found_roots, a_0, a_1, a_2)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*a_2) for i in range(nb_roots)]
	print ""
	print "Quadratic with no root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 24.0
	a_1 = -2.0
	a_2 = -6.0
	a_3 = 1.0
	
	nb_roots = roots.roots_cubic(found_roots, a_0, a_1, a_2, a_3)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*(a_2 + found_roots[i]*a_3)) for i in range(nb_roots)]
	print ""
	print "Cubic with 3 roots:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = -125.0
	a_1 = 75.0
	a_2 = -15.0
	a_3 = 1.0
	
	nb_roots = roots.roots_cubic(found_roots, a_0, a_1, a_2, a_3)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*(a_2 + found_roots[i]*a_3)) for i in range(nb_roots)]
	print ""
	print "Cubic with triple root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 32.0
	a_1 = 0.0
	a_2 = -6.0
	a_3 = 1.0
	
	nb_roots = roots.roots_cubic(found_roots, a_0, a_1, a_2, a_3)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*(a_2 + found_roots[i]*a_3)) for i in range(nb_roots)]
	print ""
	print "Cubic with a single and a double root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 32.0
	a_1 = 2.0
	a_2 = -6.0
	a_3 = 1.0
	
	nb_roots = roots.roots_cubic(found_roots, a_0, a_1, a_2, a_3)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*(a_2 + found_roots[i]*a_3)) for i in range(nb_roots)]
	print ""
	print "Cubic with 1 root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	a_0 = 32.0
	a_1 = -2.0
	a_2 = 6.0
	a_3 = -1.0
	
	nb_roots = roots.roots_cubic(found_roots, a_0, a_1, a_2, a_3)
	verification = [a_0 + found_roots[i]*(a_1 + found_roots[i]*(a_2 + found_roots[i]*a_3)) for i in range(nb_roots)]
	print ""
	print "Cubic with 1 root:"
	print "  Found %i root(s)" % nb_roots
	print "  Roots:", found_roots[0:nb_roots]
	print "  Verification (should be zeros):", verification
	
	print ""


if "StRD" in tests:
	tests.remove("StRD")
	
	print ""
	print "========== StRD tests =========="
	print ""
	
	from moremath import StRD
	
	import math
	
	diff = 1E-8
	
	for test in StRD.tests:
		
		print ""
		print test
		
		# Get the test.
		f, df, X, Y, par, start, SSR, level = StRD.get_test(test)
		
		# Choose a set of starting values.
		b = start[1][:]
		
		Y = f(b, X)
		dY = df(b, X)
		
		dY_diff = [0.0]*len(Y)
		
		nb_par = len(b)
		
		digits = [0]*len(Y)
		
		for par in range(nb_par):
			b_plus= b[:]
			if b_plus[par] == 0.0:
				b_plus[par] = +diff
			else:
				b_plus[par] *= 1.0+diff
			
			b_minus= b[:]
			if b_minus[par] == 0.0:
				b_minus[par] = -diff
			else:
				b_minus[par] *= 1.0-diff
			
			Y_plus = f(b_plus, X)
			Y_minus = f(b_minus, X)
			
			for i in range(len(Y)):
				dY_diff[i] = (Y_plus[i]-Y_minus[i]) / (b_plus[par] - b_minus[par])
				
				if dY_diff[i]-dY[par][i] == 0.0:
					digits[i] = 100.0
				elif dY[par][i] == 0.0:
					digits[i] = -math.log10( abs(dY_diff[i]) )
				else:
					digits[i] = -math.log10( abs(dY_diff[i]-dY[par][i])/ abs(dY[par][i]) )
			
			print "  par %i: %5.1f %5.1f %5.1f" % (par, min(digits), sum(digits)/len(digits), max(digits))
	
	print ""


# Verify that all tests were executed
if tests:
	print ""
	print "Unknown or duplicate tests were ignored."
	print ""
