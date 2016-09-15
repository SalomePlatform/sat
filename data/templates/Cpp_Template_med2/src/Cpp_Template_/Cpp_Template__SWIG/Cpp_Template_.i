%module :sat:{Cpp_Template_}SWIG

%{
#include <stdlib.h>
#include ":sat:{Cpp_Template_}.hxx"
%}

/*
   Initialisation block due to the LocalTraceCollector mechanism

 */

%include "libMEDMEM_Swig.i"

%init %{
    if (getenv("SALOME_trace") == NULL )
	setenv("SALOME_trace","local",0);
%}

%include "std_vector.i"
%include "std_string.i"

namespace std {
   %template(vectori) vector<int>;
   %template(vectord) vector<double>;
};

/*
  SWIG needs the use of the typedefs done in libMEDMEM_Swig.i to get the correct wrapping
  ( ie <C++ FIELD<double> instance at _d0709808_p_FIELDDOUBLE>, in state of
  <SWIG Object at _d0709808_p_FIELDDOUBLE> which has no attributes
   -> replace in the declaration of methods containing fields :
         FIELD<double, FullInterlace> by  FIELDDOUBLE
	 FIELD<int, FullInterlace>  by FIELDINT
	 FIELD<double, NoInterlace>  by FIELDDOUBLENOINTERLACE
	 FIELD<int, NoInterlace>  by FIELDINTNOINTERLACE
*/

%include ":sat:{Cpp_Template_}.hxx"



