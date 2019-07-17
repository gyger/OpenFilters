# MAKEFILE
# 
# Makefile for the abeles dynamic library. Many options are
# available:
#            used alone, it compiles the DLL;
#   install  copy the DLL to the appropriate directory;
#   clean    remove temporary files;
#   all      all of the above;
#   static   build a statically linked library (Windows only).
# 
# Copyright (c) 2002-2009,2012-2016 Stephane Larouche.
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


# Compilation with the MinGW GCC port on Windows.
ifeq ($(OS),Windows_NT)
  CC = g++
  LINK = g++
  CP = cp
  RM = rm
  
  O = o
  SO = pyd
  
  CFLAGS = -c -O3
  
  PYTHON_HEADER_PATH = C:/Python27/include
  
  ifdef PROCESSOR_ARCHITEW6432
    ARCHITECTURE = $(PROCESSOR_ARCHITEW6432)
  else
    ARCHITECTURE = $(PROCESSOR_ARCHITECTURE)
  endif
  
  ifeq ($(ARCHITECTURE),AMD64)
    ARCHITECTURE_CFLAGS_FOR_PYTHON_WRAPPERS = -DMS_WIN64
  else
    ARCHITECTURE_CFLAGS_FOR_PYTHON_WRAPPERS = 
  endif
  
  CFLAGS_FOR_PYTHON_WRAPPERS = -I$(PYTHON_HEADER_PATH) -D_hypot=hypot $(ARCHITECTURE_CFLAGS_FOR_PYTHON_WRAPPERS)
  
  PYTHON_LIB_PATH = C:/Python27/libs
  SPECIAL_LINK_FLAGS = 
  LINK_FLAGS = -L$(PYTHON_LIB_PATH) $(SPECIAL_LINK_FLAGS)
  LINK_SYNTAX = -mdll\
                -o _abeles.$(SO)\
                $(objects) $(objects_wrapper) _abeles.def\
                -lpython27
  
  RM_FLAGS = -f

# Systems other than Windows.
else
  # On all other systems, uname should exist.
  UNAME_S := $(shell uname -s)
  
  # Compilation with GCC on GNU Linux.
  ifeq ($(UNAME_S),Linux)
    CC = gcc
    LINK = gcc
    CP = cp
    RM = rm
    
    O = o
    SO = so
    
    CFLAGS = -c -O3 -fPIC
    
    PYTHON_HEADER_PATH = /usr/include/python2.7
    CFLAGS_FOR_PYTHON_WRAPPERS = -I $(PYTHON_HEADER_PATH)
    
    STANDARD_LIB_PATH = /usr/lib
    PYTHON_LIB_PATH = /usr/lib/python2.7
    SPECIAL_LINK_FLAGS = 
    LINK_FLAGS = -shared -export-dynamic -L$(STANDARD_LIB_PATH) -L$(PYTHON_LIB_PATH) $(SPECIAL_LINK_FLAGS)
    LINK_SYNTAX = -o _abeles.$(SO) $(objects) $(objects_wrapper) -lstdc++
    
    RM_FLAGS = -f
  
  # Compilation with GCC on OS X. Mac OS comes with a version of
  # Python. However py2app does not allow making a standalone
  # application using this version and it is necessary to install
  # another version. To allow this makefile to be used with either
  # versions, we detect where the python executable is and calculate
  # the header and library paths from it.
  else ifeq ($(UNAME_S),Darwin)
    PYTHON_DIRECTORY := $(shell which python)
    
    CC = c++
    LINK = c++
    CP = cp
    RM = rm
    
    O = o
    SO = so
    
    CFLAGS = -c -O3 -arch x86_64 -arch i386 -mmacosx-version-min=10.6
    
    PYTHON_HEADER_PATH = $(subst /bin/python,/include/python2.7,$(PYTHON_DIRECTORY))
    CFLAGS_FOR_PYTHON_WRAPPERS = -I $(PYTHON_HEADER_PATH)
    
    STANDARD_LIB_PATH = /usr/lib
    PYTHON_LIB_PATH = $(subst /bin/python,/lib/python2.7,$(PYTHON_DIRECTORY))
    PYTHON_DYLIB = $(subst /bin/python,/lib/libpython2.7.dylib,$(PYTHON_DIRECTORY))
    SPECIAL_LINK_FLAGS = 
    LINK_FLAGS = -bundle -arch x86_64 -arch i386 -mmacosx-version-min=10.6 -L$(STANDARD_LIB_PATH) -L$(PYTHON_LIB_PATH) $(PYTHON_DYLIB) $(SPECIAL_LINK_FLAGS)
    LINK_SYNTAX = -o _abeles.$(SO) $(objects) $(objects_wrapper)
    
    RM_FLAGS = -f
  
  # We don't know what to do for other operating systems.
  else
    $(error Unknown operating system)
  endif

endif


sources = PCHIP.cpp\
          wvls.cpp\
          N.cpp\
          N_mixture.cpp\
          dispersion.cpp\
          dispersion_mixtures.cpp\
          sin2.cpp\
          matrices.cpp\
          r_and_t.cpp\
          spectro.cpp\
          phase.cpp\
          ellipso.cpp\
          admittance.cpp\
          circle.cpp\
          electric_field.cpp\
          monitoring.cpp\
          derivatives.cpp\
          needles.cpp

sources_wrapper = wvls_wrapper.cpp\
                  N_wrapper.cpp\
                  N_mixture_wrapper.cpp\
                  dispersion_wrapper.cpp\
                  dispersion_mixtures_wrapper.cpp\
                  sin2_wrapper.cpp\
                  matrices_wrapper.cpp\
                  r_and_t_wrapper.cpp\
                  spectro_wrapper.cpp\
                  phase_wrapper.cpp\
                  ellipso_wrapper.cpp\
                  admittance_wrapper.cpp\
                  circle_wrapper.cpp\
                  electric_field_wrapper.cpp\
                  monitoring_wrapper.cpp\
                  derivatives_wrapper.cpp\
                  needles_wrapper.cpp\
                  _abeles.cpp

objects = $(sources:.cpp=.o)
objects_wrapper = $(sources_wrapper:.cpp=.o)


_abeles.$(SO) : $(objects)\
                $(objects_wrapper)\
                _abeles.def
	$(LINK) $(LINK_FLAGS) $(LINK_SYNTAX) 


ifeq ($(OS),Windows_NT)

static: SPECIAL_LINK_FLAGS = -static
static: _abeles.$(SO)

endif


PCHIP.$(O) : PCHIP.cpp\
             _abeles.h
	$(CC) $(CFLAGS) PCHIP.cpp

wvls.$(O) : wvls.cpp\
            _abeles.h
	$(CC) $(CFLAGS) wvls.cpp

wvls_wrapper.$(O) : wvls_wrapper.cpp\
                   _abeles.h\
                   _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) wvls_wrapper.cpp

N.$(O) : N.cpp\
         _abeles.h
	$(CC) $(CFLAGS) N.cpp

N_wrapper.$(O) : N_wrapper.cpp\
                 _abeles.h\
                 _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) N_wrapper.cpp

N_mixture.$(O) : N_mixture.cpp\
                 _abeles.h
	$(CC) $(CFLAGS) N_mixture.cpp

N_mixture_wrapper.$(O) : N_mixture_wrapper.cpp\
                         _abeles.h\
                         _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) N_mixture_wrapper.cpp

dispersion.$(O) : dispersion.cpp\
                  _abeles.h
	$(CC) $(CFLAGS) dispersion.cpp

dispersion_wrapper.$(O) : dispersion_wrapper.cpp\
                          _abeles.h\
                          _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) dispersion_wrapper.cpp

dispersion_mixtures.$(O) : dispersion_mixtures.cpp\
                           _abeles.h
	$(CC) $(CFLAGS) dispersion_mixtures.cpp

dispersion_mixtures_wrapper.$(O) : dispersion_mixtures_wrapper.cpp\
                                   _abeles.h\
                                   _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) dispersion_mixtures_wrapper.cpp

sin2.$(O) : sin2.cpp\
            _abeles.h
	$(CC) $(CFLAGS) sin2.cpp

sin2_wrapper.$(O) : sin2_wrapper.cpp\
                    _abeles.h\
                    _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) sin2_wrapper.cpp

matrices.$(O) : matrices.cpp\
                _abeles.h
	$(CC) $(CFLAGS) matrices.cpp

matrices_wrapper.$(O) : matrices_wrapper.cpp\
                        _abeles.h\
                        _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) matrices_wrapper.cpp

r_and_t.$(O) : r_and_t.cpp\
               _abeles.h
	$(CC) $(CFLAGS) r_and_t.cpp

r_and_t_wrapper.$(O) : r_and_t_wrapper.cpp\
                       _abeles.h\
                       _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) r_and_t_wrapper.cpp

spectro.$(O) : spectro.cpp\
               _abeles.h
	$(CC) $(CFLAGS) spectro.cpp

spectro_wrapper.$(O) : spectro_wrapper.cpp\
                       _abeles.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) spectro_wrapper.cpp

phase.$(O) : phase.cpp\
             _abeles.h
	$(CC) $(CFLAGS) phase.cpp

phase_wrapper.$(O) : phase_wrapper.cpp\
                     _abeles.h\
                     _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) phase_wrapper.cpp

ellipso.$(O) : ellipso.cpp\
               _abeles.h
	$(CC) $(CFLAGS) ellipso.cpp

ellipso_wrapper.$(O) : ellipso_wrapper.cpp\
                       _abeles.h\
                       _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) ellipso_wrapper.cpp

admittance.$(O) : admittance.cpp\
                  _abeles.h
	$(CC) $(CFLAGS) admittance.cpp

admittance_wrapper.$(O) : admittance_wrapper.cpp\
                          _abeles.h\
                          _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) admittance_wrapper.cpp

circle.$(O) : circle.cpp\
             _abeles.h
	$(CC) $(CFLAGS) circle.cpp

circle_wrapper.$(O) : circle_wrapper.cpp\
                     _abeles.h\
                     _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) circle_wrapper.cpp

electric_field.$(O) : electric_field.cpp\
                      _abeles.h
	$(CC) $(CFLAGS) electric_field.cpp

electric_field_wrapper.$(O) : electric_field_wrapper.cpp\
                              _abeles.h\
                              _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) electric_field_wrapper.cpp

monitoring.$(O) : monitoring.cpp\
                  _abeles.h
	$(CC) $(CFLAGS) monitoring.cpp

monitoring_wrapper.$(O) : monitoring_wrapper.cpp\
                          _abeles.h\
                          _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) monitoring_wrapper.cpp

derivatives.$(O) : derivatives.cpp\
                   _abeles.h
	$(CC) $(CFLAGS) derivatives.cpp

derivatives_wrapper.$(O) : derivatives_wrapper.cpp\
                           _abeles.h\
                           _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) derivatives_wrapper.cpp

needles.$(O) : needles.cpp\
               _abeles.h
	$(CC) $(CFLAGS) needles.cpp

needles_wrapper.$(O) : needles_wrapper.cpp\
                       _abeles.h\
                       _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) needles_wrapper.cpp

_abeles.$(O) : _abeles.cpp\
               _abeles.h\
               _abeles_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) _abeles.cpp


install : ../_abeles.$(SO)

../_abeles.$(SO): _abeles.$(SO)
	$(CP) _abeles.$(SO) ..


clean : 
	$(RM) $(RM_FLAGS) $(objects) $(objects_wrapper) _abeles.$(SO)


all : _abeles.$(SO)\
      install\
      clean
