# MAKEFILE
# 
# Makefile for the moremath dynamic library. Many options are
# available:
#            used alone, it compiles the DLL;
#   install  copy the DLL to the appropriate directory;
#   clean    remove temporary files;
#   all      all of the above;
#   static   build a statically linked library (Windows only).
# 
# Copyright (c) 2006-2009,2012-2016 Stephane Larouche.
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
                -o _moremath.$(SO)\
                $(objects) $(objects_wrapper) _moremath.def\
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
    LINK_SYNTAX = -o _moremath.$(SO) $(objects) $(objects_wrapper) -lstdc++
    
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
    LINK_SYNTAX = -o _moremath.$(SO) $(objects) $(objects_wrapper)
    
    RM_FLAGS = -f
  
  # We don't know what to do for other operating systems.
  else
    $(error Unknown operating system)
  endif
endif


sources = interpolation.cpp\
          Levenberg_Marquardt.cpp\
          Newton_polynomials.cpp\
          QR.cpp\
          roots.cpp

sources_wrapper = QR_wrapper.cpp\
                  Levenberg_Marquardt_wrapper.cpp\
                  roots_wrapper.cpp\
                  _moremath.cpp


objects = $(sources:.cpp=.o)
objects_wrapper = $(sources_wrapper:.cpp=.o)


_moremath.$(SO) : $(objects)\
                  $(objects_wrapper)\
                  _moremath.def
	$(LINK) $(LINK_FLAGS) $(LINK_SYNTAX) 


ifeq ($(OS),Windows_NT)

static: SPECIAL_LINK_FLAGS = -static
static: _moremath.$(SO)

endif


interpolation.$(O) : interpolation.cpp\
                     _moremath.h
	$(CC) $(CFLAGS) interpolation.cpp

Levenberg_Marquardt.$(O) : Levenberg_Marquardt.cpp\
                           _moremath.h
	$(CC) $(CFLAGS) Levenberg_Marquardt.cpp

Levenberg_Marquardt_wrapper.$(O) : Levenberg_Marquardt_wrapper.cpp\
                                   _moremath.h\
                                   _moremath_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) Levenberg_Marquardt_wrapper.cpp

Newton_polynomials.$(O) : Newton_polynomials.cpp\
                          _moremath.h
	$(CC) $(CFLAGS) Newton_polynomials.cpp

QR.$(O) : QR.cpp\
          _moremath.h
	$(CC) $(CFLAGS) QR.cpp

QR_wrapper.$(O) : QR_wrapper.cpp\
                  _moremath.h\
                  _moremath_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) QR_wrapper.cpp

roots.$(O) : roots.cpp\
             _moremath.h
	$(CC) $(CFLAGS) roots.cpp

roots_wrapper.$(O) : roots_wrapper.cpp\
                     _moremath.h\
                     _moremath_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) roots_wrapper.cpp

_moremath.$(O) : _moremath.cpp\
                 _moremath.h\
                 _moremath_wrapper.h
	$(CC) $(CFLAGS) $(CFLAGS_FOR_PYTHON_WRAPPERS) _moremath.cpp


install : ../_moremath.$(SO)

../_moremath.$(SO): _moremath.$(SO)
	$(CP) _moremath.$(SO) ..


clean : 
	$(RM) $(RM_FLAGS) $(objects) $(objects_wrapper) _abeles.$(SO)


all : _moremath.$(SO)\
      install\
      clean
