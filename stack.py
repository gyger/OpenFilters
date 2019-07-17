# stack.py
# 
# Design a filter from a stack formula.
# 
# Copyright (c) 2001-2007,2013 Stephane Larouche.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA



from definitions import *


MIN = -1.0
MAX = -2.0



########################################################################
#                                                                      #
# stack_error                                                          #
#                                                                      #
########################################################################
class stack_error(Exception):
	"""Exception class for stack errors"""
	
	def __init__(self, position, value):
		self.position = position
		self.value = value
	
	def __str__(self):
		return "Stack error: %s at position %i." % (self.value, self.position)
	
	def get_position(self):
		return self.position



########################################################################
#                                                                      #
# stack                                                                #
#                                                                      #
########################################################################
def stack(filter, formula, materials, side = FRONT):
	"""Create a stack from a stack formula
	
	This function takes 3 or 4 arguments:
	  filter               the filter on which to put the filter;
	  formula              the formula
	  materials            a dictionary that associates materials with
	                       symbols;
	  side                 (optional) the side where to put the stack,
	                       the default value is FRONT.
	
	In the stack, single letters describe quarter waves of
	materials defined in the variable materials. Multiplicative
	factors can be added in front of the letters to change the
	thickness. Exponent can be added after the letters to indicate
	a repetition of the letters. Finaly parenthesis can be used to
	apply a multiplication factor or an exponent to many letters
	at the same time. Spaces are needed only to avoid ambiguity.
	Exponents must be integers and multiplication factors can be
	integers or floats.
	
	The materials variable must be a dictionary of materials name and
	indices corresponding to the letters used in stack."""
	
	center_wavelength = filter.get_center_wavelength()
	QW = 0.25*center_wavelength
	
	elements, multiplication_factors = analyse_stack_formula(formula)
	
	nb_layers = len(elements)
	
	thicknesses = [multiplication_factors[i_layer]*QW for i_layer in range(nb_layers)]
	
	filter.clear_design(side)
	
	for i_layer in range(len(elements)):
		material_name = materials[elements[i_layer]][0]
		material_nb = filter.get_material_nb(material_name)
		material = filter.get_material(material_nb)
		if material.is_mixture():
			index = materials[elements[i_layer]][1]
			n_min, n_max = material.get_index_range(filter.get_center_wavelength())
			if index == MIN:
				index = n_min
			elif index == MAX:
				index = n_max
		else:
			index = None
		filter.add_layer(material_name, thicknesses[i_layer], side = side, index = index, OT = True)


########################################################################
#                                                                      #
# analyse_stack_formula                                                #
#                                                                      #
########################################################################
def analyse_stack_formula(formula):
	"""Analyse the stack formula
	
	This funtion takes a single argument:
	  formula                  the stack formula
	and returns
	  elements                 the symbols of all the layers
	  multiplication_factors   the number of quarter waves of every
	                           layer."""
	
	elements = []
	multiplication_factors = []
	this_element = None
	this_multiplication_factor = 1.0
	this_exponent = 1
	
	i = 0
	
	while i < len(formula):
		
		# If the caracter is a space, do nothing
		if formula[i].isspace():
			i += 1
		
		# If the character is a digit or a ".", this must be the beginning
		# of a multiplication factor.
		elif formula[i].isdigit() or formula[i] == ".":
			begin = i
			while True:
				i += 1
				if i >= len(formula):
					raise stack_error(i, "Stack formula finished by a multiplication factor")
				elif formula[i].isdigit() or formula[i] == ".":
					pass
				else:
					break
			
			try:
				this_multiplication_factor *= float(formula[begin:i])
			except ValueError:
				raise stack_error(i, "Multiplicative factor cannot be converted to a float")
			
			# Ignore spaces and up to one multiplication sign after a
			# multiplication factor.
			nb_multiplication_signs = 0
			while True:
				if i >= len(formula):
					raise stack_error(i, "Stack formula finished by a multiplication factor that does not apply to any element")
				elif formula[i].isspace():
					pass
				elif formula[i] == "*":
					nb_multiplication_signs += 1
					if nb_multiplication_signs > 1:
						raise stack_error(i, "Many consecutive multiplication signs are present")
				else:
					break
				i += 1
		
		# A simple letter.
		elif formula[i].isalpha():
			this_element = formula[i]
			i += 1
		
		# If an opening parenthesis is found, find the closing
		# parenthesis.
		elif formula[i] == "(":
			opening_parenthesis = i
			nb_opened_parenthesis = 1
			while nb_opened_parenthesis:
				i += 1
				if i >= len(formula):
					raise stack_error(opening_parenthesis, "Unmatched opening parenthesis in stack formula")
				elif formula[i] == ")":
					nb_opened_parenthesis -= 1
				elif formula[i] == "(":
					nb_opened_parenthesis += 1
			begin_element = opening_parenthesis+1
			this_element = formula[begin_element:i]
			i += 1
		
		# If an closing parenthesis is found here, it is not matched.
		elif formula[i] == ")":
			raise stack_error(i, "Unmatched closing parenthesis in stack formula")
		
		# Any other caracter is unacceptable at this point.
		else:
			raise stack_error(i, "Unacceptable caracter in stack formula")
		
		# If an element was selected, try to find multiplication and
		# division factors and/or exponents on the right and then interpret
		# the element.
		if this_element is not None:
			while True:
				if i >= len(formula):
					break
				
				elif formula[i].isspace():
					i += 1
				
				elif formula[i] == "*" or formula[i] == "/":
					if formula[i] == "*":
						sign = 1
					else:
						sign = -1
					i += 1
					begin = i
					while True:
						if i >= len(formula):
							break
						elif formula[begin:i+1].isspace() or formula[i].isdigit() or formula[i] == ".":
							i += 1
						else:
							break
					if i == begin:
						raise stack_error(i-1, "Multiplication factor not specified in stack formula")
					try:
						this_multiplication_factor *= float(formula[begin:i])**sign
					except ValueError:
						raise stack_error(i, "Multiplication factor cannot be converted to a float")
				
				elif formula[i] == "^":
					i += 1
					begin = i
					while True:
						if i >= len(formula):
							break
						elif formula[begin:i+1].isspace() or formula[i].isdigit():
							i += 1
						elif formula[i] == ".":
							raise stack_error(i, "Exponent in stack formula must be an integer")
						else:
							break
					if i == begin:
						raise stack_error(i-1, "Exponent not specified in stack formula")
					try:
						this_exponent *= int(formula[begin:i])
					except ValueError:
						raise stack_error(i, "Exponent cannot be converted to an integer")
				
				else:
					break
			
			if len(this_element) == 1:
				these_elements = [this_element]
				these_multiplication_factors = [this_multiplication_factor]
			else:
				try:
					these_elements, these_multiplication_factors = analyse_stack_formula(this_element)
				except stack_error as error:
					raise stack_error(begin_element+error.get_position(), str(error))
				for j in range(len(these_multiplication_factors)):
					these_multiplication_factors[j] *= this_multiplication_factor
			
			elements.extend(these_elements*this_exponent)
			multiplication_factors.extend(these_multiplication_factors*this_exponent)
			
			this_element = None
			this_exponent = 1
			this_multiplication_factor = 1.0
	
	# Merge identical adjacent layers.
	for i in range(len(elements)-1, 1-1, -1):
		if elements[i] == elements[i-1]:
			elements.pop(i)
			multiplication_factors[i-1] += multiplication_factors[i]
			multiplication_factors.pop(i)
	
	return elements, multiplication_factors
