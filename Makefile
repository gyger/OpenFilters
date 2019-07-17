# MAKEFILE
# 
# Makefile for the OpenFilters project. Many options are available:
#   (no argument)   make the most possible on any operating system
#                   (meaning the distribution on Window or Mac, and
#                   just compiling the libraries on Linux);
#   distribution    create the distribution (including the installer
#                   and source code on Windows, and only the installer
#                   on Mac);
#   installer       create the installer (an executable created using
#                   NSIS on Windows or a DMG on Mac);
#   executable      create the executable (exe on Windows or app on
#                   Mac);
#   libraries       compile the abeles and moremath libraries;
#   abeles          compile the abeles library;
#   moremath        compile the moremath library;
#   clean           remove all created files except the distribution
#                   files, the compiled libraries, and the compiled
#                   Python files;
#   cleanall        remove all created files.
# 
# In order for make to work, you need Python and wxPython. On Windows,
# you also need py2exe and NSIS. On Mac you also need py2app.
# 
# Copyright (c) 2006-2008,2012-2014,2016 Stephane Larouche.
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


VERSION = 1.1.1


ifeq ($(OS),Windows_NT)
  MKDIR = mkdir
  CP = cp
  RM = rm
  SO = pyd
  CD = cd
  MV = mv
  FIND = /bin/find
  TAR = tar
  GZIP = gzip
  
  EXE = exe
  
  DISTUTIL = py2exe
  
  ifdef PROCESSOR_ARCHITEW6432
  	ARCHITECTURE = $(PROCESSOR_ARCHITEW6432)
  else
  	ARCHITECTURE = $(PROCESSOR_ARCHITECTURE)
  endif
  
  ifeq ($(ARCHITECTURE),AMD64)
  	BITS = 64bit
  else
  	BITS = 32bit
  endif
  
  INSTALLER_NAME = Install_OpenFilters_$(VERSION)_$(BITS).exe
  TAR_NAME = OpenFilters_$(VERSION).tar
  DISTRIBUTION_DIRECTORY = OpenFilters_$(VERSION)

else
  UNAME_S := $(shell uname -s)
  
  # On Linux, it is possible to compile the libraries, but
  # nothing more.
  ifeq ($(UNAME_S),Linux)
    MKDIR = mkdir
    CP = cp
    RM = rm
    SO = so
    CD = cd
    MV = mv
    FIND = find
    TAR = tar
    GZIP = gzip
    
    $(warning It is impossible to create an executable or a distribution of OpenFilters on Linux. You will have to run OpenFilters using the python interpreter (python Filters.py).)
  
  else ifeq ($(UNAME_S),Darwin)
    MKDIR = mkdir
    CP = cp
    RM = rm
    SO = so
    CD = cd
    MV = mv
    FIND = find
    TAR = tar
    GZIP = gzip
    
    EXE = app
    
    DISTUTIL = py2app
    
    INSTALLER_NAME = OpenFilters_$(VERSION).dmg
    DISTRIBUTION_DIRECTORY = OpenFilters_$(VERSION)
  
  # We don't know what to do for other operating systems.
  else
    $(error Unknown operating system)
  endif
endif



ifdef DISTRIBUTION_DIRECTORY

distribution: $(DISTRIBUTION_DIRECTORY)/$(INSTALLER_NAME)

$(DISTRIBUTION_DIRECTORY)/$(INSTALLER_NAME): $(INSTALLER_NAME)
	$(RM) -r -f $(DISTRIBUTION_DIRECTORY)
	$(MKDIR) $(DISTRIBUTION_DIRECTORY)
	$(CP) $(INSTALLER_NAME) $(DISTRIBUTION_DIRECTORY)
ifeq ($(OS),Windows_NT)
	$(CP) -r dist/sources $(DISTRIBUTION_DIRECTORY)/sources
	$(CD) $(DISTRIBUTION_DIRECTORY); $(TAR) -cvvf $(TAR_NAME) sources/
	$(CD) $(DISTRIBUTION_DIRECTORY); $(GZIP) $(TAR_NAME)
	$(RM) -r -f $(DISTRIBUTION_DIRECTORY)/sources
endif

endif


ifdef INSTALLER_NAME

installer: $(INSTALLER_NAME)

ifeq ($(OS),Windows_NT)

$(INSTALLER_NAME): dist/OpenFilters.$(EXE)\
                   OpenFilters.nsi
	makensis OpenFilters.nsi

OpenFilters.nsi: dist/OpenFilters.exe\
                 installer.py
	python installer.py

else ifeq ($(UNAME_S),Darwin)

$(INSTALLER_NAME): dist/OpenFilters.$(EXE)\
                   make_dmg.applescript\
                   dmg_background.png
	hdiutil create -srcfolder dist -volname OpenFilters -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size 100M OpenFilters.temp.dmg
	mkdir dmg
	hdiutil attach -readwrite -noverify -noautoopen -mountpoint dmg OpenFilters.temp.dmg
	sleep 20
	mkdir dmg/.background
	cp dmg_background.png dmg/.background/
	chmod -fr go-w dmg
	osascript make_dmg.applescript
	sync
	sync
	hdiutil detach -force dmg
	sleep 10
	hdiutil convert OpenFilters.temp.dmg -format UDZO -imagekey zlib-level=9 -o $(INSTALLER_NAME)
	rmdir dmg
	rm -f OpenFilters.temp.dmg

endif

endif


ifdef EXE

executable: dist/OpenFilters.$(EXE)

dist/OpenFilters.$(EXE): *.py\
                         OpenFilters.ico\
                         OpenFilters.icns\
                         abeles/*.py\
                         abeles/_abeles.$(SO)\
                         color/illuminants/*.txt\
                         color/observers/*.txt\
                         config/*.py\
                         examples/*.ofp\
                         GUI/*.py\
                         materials/*.mat\
                         modules/*.py\
                         moremath/*.py\
                         moremath/_moremath.$(SO)
	python setup.py $(DISTUTIL)

endif


libraries: abeles\
           moremath


abeles: abeles/_abeles.$(SO)

abeles/_abeles.$(SO): abeles/_abeles/*.cpp\
                      abeles/_abeles/*.h\
                      abeles/_abeles/Makefile
	$(CD) abeles/_abeles; make install


moremath: moremath/_moremath.$(SO)

moremath/_moremath.$(SO): moremath/_moremath/*.cpp\
                          moremath/_moremath/*.h\
                          moremath/_moremath/Makefile
	$(CD) moremath/_moremath; make install


clean:
ifeq ($(OS),Windows_NT)
	$(RM) -f OpenFilters.nsi
endif
ifdef EXE
	$(RM) -r -f build
	$(RM) -r -f dist
endif
ifdef INSTALLER_NAME
	$(RM) -f $(INSTALLER_NAME)
endif


cleanall: clean
	$(CD) abeles/_abeles; make clean
	$(CD) moremath/_moremath; make clean
	$(RM) -f abeles/_abeles.$(SO)
	$(RM) -f moremath/_moremath.$(SO)
	$(FIND) ./ -type f -name "*.pyc" -exec rm {} \;
ifdef DISTRIBUTION_DIRECTORY
	$(RM) -r -f $(DISTRIBUTION_DIRECTORY)
endif
