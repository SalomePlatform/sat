from os import getenv
if getenv("SALOMEPATH"):
    import salome
    import :sat:{Cpp_Template_}_ORB
    my_:sat:{Cpp_Template_} = salome.lcc.FindOrLoadComponent("FactoryServer", ":sat:{Cpp_Template_}")
    IN_SALOME_GUI = 1
else:
    import :sat:{Cpp_Template_}SWIG
    my_:sat:{Cpp_Template_}=:sat:{Cpp_Template_}SWIG.:sat:{Cpp_Template_}()
pass
#
#
print "Test Program of :sat:{Cpp_Template_} component"

# ...

