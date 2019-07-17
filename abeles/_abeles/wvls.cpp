/*
 *
 *  wvls.cpp
 *
 *
 *  Manage an array of wavelengths for the Abeles module.
 *
 *  Copyright (c) 2002-2007,2012,2013 Stephane Larouche.
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


#include <cstdlib>

#include "_abeles.h"


#ifdef __cplusplus
extern "C" {
#endif


/*********************************************************************/
/*                                                                   */
/* new_wvls                                                          */
/*                                                                   */
/* Create a new wvls structure to store an array of wavelengths      */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   length            the number of wavelengths in the array;       */
/* and returns a wvls structure.                                     */
/*                                                                   */
/* This structure is used in many of the structures defined in the   */
/* abeles module to define the wavelengths used for calculations.    */
/*                                                                   */
/* If the creation of the structure fails because of a lack of heap  */
/* memory, a NULL pointer is returned.                               */
/*                                                                   */
/*********************************************************************/
wvls_type * new_wvls(const long length)
{
	wvls_type												*wvls;

	wvls = (wvls_type *)malloc(sizeof(wvls_type));

	if (!wvls) return NULL;

	wvls->length = length;
	wvls->wvls = (double *)malloc(length*sizeof(double));

	if (!wvls->wvls)
	{
		del_wvls(wvls);
		return NULL;
	}

	return wvls;
}


/*********************************************************************/
/*                                                                   */
/* del_wvls                                                          */
/*                                                                   */
/* Delete a wvls structure                                           */
/*                                                                   */
/* This function takes 1 argument:                                   */
/*   wvls              the structure to delete.                      */
/*                                                                   */
/* If the argument is a NULL pointer, the function does nothing.     */
/*                                                                   */
/*********************************************************************/
void del_wvls(wvls_type *wvls)
{
	if (!wvls) return;

	free(wvls->wvls);

	free(wvls);
}


/*********************************************************************/
/*                                                                   */
/* set_wvl                                                           */
/*                                                                   */
/* Set one of the wavelengths in a wvls structure                    */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   wvls              the structure being set;                      */
/*   position          the position of the wavelength to set;        */
/*   wvl               the wavelength.                               */
/*                                                                   */
/*********************************************************************/
void set_wvl(const wvls_type *wvls, const long position, const double wvl)
{
	wvls->wvls[position] = wvl;
}


/*********************************************************************/
/*                                                                   */
/* set_wvls_by_range                                                 */
/*                                                                   */
/* Set the wavelengths by an initial value and an increment.         */
/*                                                                   */
/* This function takes 3 arguments:                                  */
/*   wvls              the structure being set;                      */
/*   from              the wavelength for position 0;                */
/*   by                the wavelength increment.                     */
/*                                                                   */
/*********************************************************************/
void set_wvls_by_range(const wvls_type *wvls, const double from, const double by)
{
	long														i;

	for (i = 0; i < wvls->length; i++)
	{
		wvls->wvls[i] = from + i*by;
	}
}


#ifdef __cplusplus
}
#endif
