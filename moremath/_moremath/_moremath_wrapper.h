/*
 *
 *  _moremath_wrapper.h
 *
 *
 *  Header files for Python wrapper functions of the moremath DLL.
 *
 *  Copyright (c) 2006-2007,2013 Stephane Larouche.
 *
 *  This file is part of OpenFilters.
 *
 *  OpenFilters is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or (at
 *  your option) any later version.
 *
 *  OpenFilters is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 *  USA
 *
 */


#ifndef __MOREMATH_WRAPPER
#define __MOREMATH_WRAPPER


/* Make sure that Python.h is loaded. */
#include <Python.h>


#ifdef __cplusplus
extern "C" {
#endif


/* Every module is seperatly initialized. It only needs to export its
 * init function. */
PyObject * init_Levenberg_Marquardt();
PyObject * init_QR();
PyObject * init_roots();


#ifdef __cplusplus
}
#endif

#endif /* #ifndef __MOREMATH_WRAPPER */
