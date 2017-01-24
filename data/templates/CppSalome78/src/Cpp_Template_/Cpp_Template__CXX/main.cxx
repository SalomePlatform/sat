#include ":sat:{Cpp_Template_}.hxx"
// uncoment if the component uses MED
// #include "MEDCouplingUMesh.hxx"
// #include "MEDCouplingFieldDouble.hxx"
#include <stdlib.h>

using namespace std;
int main(int argc, char ** argv)
{
    if (getenv("SALOME_trace") == NULL )
	setenv("SALOME_trace","local",0);
    :sat:{Cpp_Template_} myCalc;
    // test myCalc component ...
}
