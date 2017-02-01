%module :sat:{Cpp_Template_}SWIG

%{
#include <stdlib.h>
#include ":sat:{Cpp_Template_}.hxx"
%}

/*
   Initialisation block due to the LocalTraceCollector mechanism

 */

/* %include "MEDCouplingCommon.i" */

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


%include ":sat:{Cpp_Template_}.hxx"



