# -*- coding: UTF-8 -*-

# release.py
# 
# The version of the software and release notes.
# 
# Copyright (c) 2000-2010,2012,2014-2016 Stephane Larouche.
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



import time



MAJOR = 1
MINOR = 1
REVISION = 1
BUILD = ""

DATE = time.strftime("%Y/%m/%d")

VERSION = "%i.%i" % (MAJOR, MINOR)
if REVISION: VERSION += ".%i" % REVISION

if BUILD == "current":
	BUILD += time.strftime(" (%Y/%m/%d %H:%M:%S)")

RELEASE_NOTES = """VERSION 1.1.1

This is a bugfix release.

Bug fixes:
- Fixed the calculation of the phase for p polarization and for transmission (Thanks to Paul D. Hillman for identifying this bug and its cause, and helping fix it).
- A few smaller bugs have been fixed.


VERSION 1.1

Major changes:
- A new menu item Import layer allows to import the index profile of a layer from a text file.
- A new tool to simulate the effect of random deposition errors.
- Targets for absorption, phase, GD, and GDD.
- Each user on a computer now has their own catalog of materials, in addition to the default materials.

Minor changes:
- The phase in now shown in degrees.
- Color target and calculation dialogs now accept polarization choice.
- The resolution of the needle or step methods is now relative to the shortest wavelength in the targets, making those methods scalable to different wavelength ranges.
- When thin layers are removed during optimization, their optical thickness is now distributed on surrounding layres.
- It is now possible to save the result plots in figure files. (This feature is not intended to produce high quality figures. If you want to produce high quality figures for publication, export the results as text, and plot them with a plotting software.)
- The conversion of the index profile of graded-index layers into steps is improved to preserve both the physical and the optical thicknesses of the layer. The minimum thickness of sublayers is now in physical thickness. The value defined in old files, in optical thickness, is interpreted as a physical thickness.
- The Sellmeier dispersion model was added.
- OpenFilters now remembers the last used directory and recently opened projects.

Security fix:
- The way layer descriptions from project files are read in older version of OpenFilters may allow a malicious user to execute arbitrary code when a project file is opened. Python 2.6 includes a function to safely evaluate such strings which is used when that version of Python is used. The Windows executable available on the FCSEL website is compiled with Python 2.6 and is therefore safe. If OpenFilter is ran with an older version of Python, making it unsafe, a warning message is shown on startup. In that case you should not open project files from untrusted sources.

Bug fixes:
- Previously, optimization by the Fourier transform method would regress after a certain number of steps. Now the optimization is stopped when this occurs.
- It is now really possible to add more than one step at a time.
- The validation of the user input was improved in many dialogs to avoid null wavelength and 90 degrees incidence angle, for example.
- The thickness of quintic layers is now correct when optical thickness scaling is chosen.
- Total internal reflection now gives correct results.
- Reverse direction calculations now give correct results (the bug only affected non-normal incidence when the front and back media were different).
- Many smaller bugs have been fixed.

Other improvements:
- A large number of improvements have been made under the hood to make the code cleaner and faster.


VERSION 1.0.2:

This is a bugfix release.

Bug fixes:
- A bug that affected the Levenberg-Marquardt algorithm when a parameter is bounded was corrected. This problem particularly hindered the step method.
- A bug that occured when extrapolating the index of refraction from a table was corrected.
- The quintic module now handles null thickness gracefully.


VERSION 1.0.1:

This is a bugfix release.

Bug fixes:
- The p-polarization phase, GD and GDD are calculated correctly. The scale of GD and GDD was corrected.
- The files gdiplus.dll and MSVCP71.dll are included in the installer since they are not present on all systems.
- The bug with the don't consider substrate and medium option when the uppermost front layer is a mixture has been corrected.
- The bug with comment lines finishing with a colon was corrected.
- A filter is correctly selected when reverting to saved version of the project. Efforts are made to keep the same selected filter.
- The bug with the step method when the optical thickness of a layer is kept constant was corrected.
- The controls in the step method dialog are correctly enabled/disabled.
- Pressing Alt-F4 to close the dialog is disabled during design/optimization/synthesis.
- The software does not crash when there is an error in a material file.
- Controls of the Fourier transform method dialog are correctly enabled.
- The bug that prevented showing the table mixture dialog when a filter was opened was solved.
- The bug that prevented modifying a quintic layer was solved.
- The bug that occured using the needle or step methods with targets in reverse direction was solved.
- The columns in color trajectory export files are now correctly identified.


VERSION 1.0:

First public release of OpenFilters.


KNOWN BUGS:

- Many functions are susceptible to underflow errors when the layers are thick and the absorbtion important. In the abeles dll, all NaNs and other are transformed to 0s in the Python wrappers but this doesn't really solve the problem which is that k is overestimated. There are still problems in the Python implementation because I can't find a reproducible way to detect NaNs.
- Numerical types (ints and floats) are immortal in Python, this will lead to important memory leaks that can prevent the software to work properly when the DLL are not used, particularly for graded-index filters."""
