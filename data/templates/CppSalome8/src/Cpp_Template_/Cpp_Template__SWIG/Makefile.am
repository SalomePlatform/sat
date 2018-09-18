#
# Common begin part
#

include $(top_srcdir)/adm/unix/make_begin.am

#
# Developper part
#

lib_LTLIBRARIES = lib:sat:{Cpp_Template_}SWIG.la
nodist_lib:sat:{Cpp_Template_}SWIG_la_SOURCES = :sat:{Cpp_Template_}_wrap.cxx 

BUILT_SOURCES = :sat:{Cpp_Template_}_wrap.cxx

SWIG_PYTHON_INCLUDES = $(MEDCOUPLING_CXXFLAGS) -I$(top_srcdir)/src/:sat:{Cpp_Template_}/:sat:{Cpp_Template_}_CXX

INCLUDES = -I$(top_srcdir)/src/:sat:{Cpp_Template_}/:sat:{Cpp_Template_}_CXX $(PYTHON_INCLUDES) $(MEDCOUPLING_CXXFLAGS) $(MED3_INCLUDES) $(KERNEL_CXXFLAGS)

lib:sat:{Cpp_Template_}SWIG_la_LIBADD = -L../:sat:{Cpp_Template_}_CXX -l:sat:{Cpp_Template_}CXX $(MEDCOUPLING_LDFLAGS)


bin_SCRIPTS = :sat:{Cpp_Template_}SWIG.py

clean-local:
	$(RM) :sat:{Cpp_Template_}SWIG.py :sat:{Cpp_Template_}_wrap.cxx

#
# Common end part
#

include $(top_srcdir)/adm/unix/make_end.am
