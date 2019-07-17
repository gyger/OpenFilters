Abeles


This dynamically loaded library implements functions to perform the analysis of a optical interference coating using the Abeles matrix method and several other functions to manage dispersion relations and mixtures of materials, to refine filters and to use the needle or step methods. It is written as a part of the Filters software written in Python, but could be used alone in other software written in Python or C.


KNOWN BUGS:

- Important absorption on thick films can create underflows. At this moment, all NaNs and range errors are replaced by 0s, this is not very elegant.


Copyright (c) 2002-2007 Stephane Larouche.
