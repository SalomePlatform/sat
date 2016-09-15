#
# Common begin part
#

include $(top_srcdir)/adm/unix/make_begin.am

#
# Developper part
#

lib_LTLIBRARIES            = lib:sat:{Cpp_Template_}CXX.la
lib:sat:{Cpp_Template_}CXX_la_SOURCES  = :sat:{Cpp_Template_}.cxx
lib:sat:{Cpp_Template_}CXX_la_LIBADD   =

# exported headers
library_includedir=$(includedir)
library_include_HEADERS = :sat:{Cpp_Template_}.hxx

INCLUDES  =

bin_PROGRAMS = :sat:{Cpp_Template_}_test
:sat:{Cpp_Template_}_test_SOURCES = main.cxx
:sat:{Cpp_Template_}_test_LDADD   = lib:sat:{Cpp_Template_}CXX.la


#
# Common end part
#

include $(top_srcdir)/adm/unix/make_end.am


