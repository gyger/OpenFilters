# setup.py
# 
# Pack the OpenFilters python code into an executable using py2exe or
# py2app.
# 
# To compile, use
# 	python setup.py py2exe
# or
# 	python setup.py py2app
# 
# Copyright 2000-2002,2004-2007,2009,2010,2012-2015 Stephane Larouche..
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


import os
import sys
from distutils.core import setup
import glob
import imp
import compileall

import wx

import release


# Create a Release notes file
release_notes = open("Release notes.txt", "w")
release_notes.write("OpenFilters %s (%s)\n" % (release.VERSION, release.DATE))
release_notes.write("\n")
release_notes.write("\n")
release_notes.write(release.RELEASE_NOTES)
release_notes.write("\n")
release_notes.close()

# Compile all files in modules.
compileall.compile_dir("modules")

name = "OpenFilters"

data_files = [(".", ["Release notes.txt", "gpl.txt", "OpenFilters.ico"]),
              (os.path.join("color", "illuminants"), glob.glob(os.path.join("color", "illuminants", "*.txt"))),
              (os.path.join("color", "observers"), glob.glob(os.path.join("color", "observers", "*.txt"))),
              ("examples", glob.glob(os.path.join("examples", "*.ofp"))),
              ("materials", glob.glob(os.path.join("materials", "*.mat"))),
              ("modules", glob.glob(os.path.join("modules", "*.pyc")))]

source_files = [("sources", ["gpl.txt"]),
                ("sources", glob.glob("*.py")),
                ("sources", glob.glob("OpenFilters.ico")),
                ("sources", glob.glob("OpenFilters.icns")),
                ("sources", glob.glob("dmg_background.png")),
                ("sources", ["Makefile"]),
                ("sources", ["make_dmg.applescript"]),
                (os.path.join("sources", "abeles"), glob.glob(os.path.join("abeles", "*.py"))),
                (os.path.join("sources", "abeles"), [os.path.join("abeles", "README.txt")]),
                (os.path.join("sources", "abeles", "_abeles"), glob.glob(os.path.join("abeles", "_abeles", "*.cpp"))),
                (os.path.join("sources", "abeles", "_abeles"), glob.glob(os.path.join("abeles", "_abeles", "*.h"))),
                (os.path.join("sources", "abeles", "_abeles"), glob.glob(os.path.join("abeles", "_abeles", "*.def"))),
                (os.path.join("sources", "abeles", "_abeles"), [os.path.join("abeles", "_abeles", "Makefile")]),
                (os.path.join("sources", "color", "illuminants"), glob.glob(os.path.join("color", "illuminants", "*.txt"))),
                (os.path.join("sources", "color", "observers"), glob.glob(os.path.join("color", "observers", "*.txt"))),
                (os.path.join("sources", "config"), glob.glob(os.path.join("config", "*.py"))),
                (os.path.join("sources", "examples"), glob.glob(os.path.join("examples", "*.ofp"))),
                (os.path.join("sources", "GUI"), glob.glob(os.path.join("GUI", "*.py"))),
                (os.path.join("sources", "materials"), glob.glob(os.path.join("materials", "*.*"))),
                (os.path.join("sources", "modules"), glob.glob(os.path.join("modules", "*.py"))),
                (os.path.join("sources", "moremath"), glob.glob(os.path.join("moremath", "*.py"))),
                (os.path.join("sources", "moremath"), [os.path.join("moremath", "README.txt")]),
                (os.path.join("sources", "moremath", "_moremath"), glob.glob(os.path.join("moremath", "_moremath", "*.cpp"))),
                (os.path.join("sources", "moremath", "_moremath"), glob.glob(os.path.join("moremath", "_moremath", "*.h"))),
                (os.path.join("sources", "moremath", "_moremath"), glob.glob(os.path.join("moremath", "_moremath", "*.def"))),
                (os.path.join("sources", "moremath", "_moremath"), [os.path.join("moremath", "_moremath", "Makefile")])]

if sys.argv[1] == "py2exe":
	from py2exe import py2exe_util
	import platform
	
	bits, _ = platform.architecture()	
	
	# Locate msvcp90.dll.
	wx_directory = imp.find_module("wx")[1]
	dependencies = set()
	for filename in glob.glob(os.path.join(wx_directory, "*.pyd")) + glob.glob(os.path.join(wx_directory, "*.dll")):
		dependencies |= set(py2exe_util.depends(filename).keys())
	for filename in dependencies:
		if os.path.basename(filename).lower() == "msvcp90.dll":
			msvcp90 = filename
			break
	else:
		raise IOError("Could not locate msvcp90.dll")
	
	class Target:
		def __init__(self, **kw):
			self.__dict__.update(kw)
			# for the versioninfo resources
			self.version = release.VERSION
			self.company_name = ""
			self.copyright = "Stephane Larouche"
			self.name = name
	
	manifest = """
	<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
	<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
		<assemblyIdentity
			version="%(version)s"
			processorArchitecture="%(architecture)s"
			name="%(name)s"
			type="win32"
		/>
		<description>%(description)s</description>
		<dependency>
			<dependentAssembly>
				<assemblyIdentity
					type="win32"
					name="Microsoft.Windows.Common-Controls"
					version="6.0.0.0"
					processorArchitecture="%(architecture)s"
					publicKeyToken="6595b64144ccf1df"
					language="*"
				/>
			</dependentAssembly>
		</dependency>
		<dependency>
			<dependentAssembly>
				<assemblyIdentity 
					type="win32" 
					name="Microsoft.VC90.CRT" 
					version="9.0.21022.8" 
					processorArchitecture="%(architecture)s" 
					publicKeyToken="1fc8b3b9a1e18e3b"
				/>
			</dependentAssembly>
		</dependency>
	</assembly>
	""" % {"name" : name,
	       "version" : ("%s.%s.%s.%s" % (release.MAJOR, release.MINOR, release.REVISION, 0)),
	       "description" : "A software to design optical filters",
	       "architecture" : ("x86" if (bits == "32bit") else "amd64")}
	
	RT_MANIFEST = 24
	
	OpenFilters = Target(description = name,
	                     script = "Filters.py",
	                     other_resources = [(RT_MANIFEST, 1, manifest)],
	                     icon_resources = [(1, "OpenFilters.ico")],
	                     dest_base = name)
	
	data_files += [(".", [msvcp90])] + source_files
	
	setup(name = name,
	      windows = [OpenFilters],
	      options = {"py2exe": {"compressed": 1,
	                            "optimize": 0,
	                            "ascii": 0,
	                            "bundle_files": 3,
	                            "dll_excludes": ["MSVCP90.dll",
	                                             "CRYPT32.dll",
	                                             "KERNELBASE.dll",
	                                             "MSASN1.dll",
	                                             "API-MS-Win-Core-ErrorHandling-L1-1-0.dll",
	                                             "API-MS-Win-Core-LibraryLoader-L1-1-0.dll",
	                                             "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
	                                             "API-MS-Win-Core-Misc-L1-1-0.dll",
	                                             "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
	                                             "API-MS-Win-Core-Profile-L1-1-0.dll",
	                                             "API-MS-Win-Core-String-L1-1-0.dll",
	                                             "API-MS-Win-Core-SysInfo-L1-1-0.dll",
	                                             "API-MS-Win-Security-Base-L1-1-0.dll"]}},
	      zipfile = None,
	      data_files = data_files)

elif sys.argv[1] == "py2app":
	import py2app
	
	data_files += [(".", glob.glob("*.ico"))]
	
	setup(name = name,
	      app = ["Filters.py"],
	      options = {"py2app": {"extension": ".app",
	                            "argv_emulation": True,
	                            "site_packages": True,
	                            "arch": "intel",
	                            "iconfile": "OpenFilters.icns",
	                            "plist": {"CFBundleName": "OpenFilters",
	                                      "CFBundleShortVersionString": release.VERSION,
	                                      "CFBundleVersion": release.BUILD,
	                                      "NSHumanReadableCopyright": "Stephane Larouche",
	                                      "CFBundleIconFile": "OpenFilters.icns"}}},
	      data_files = data_files)

# Delete the Release notes file
os.remove("Release notes.txt")





