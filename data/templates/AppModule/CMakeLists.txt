# Copyright (C) 2012-2016  CEA/DEN, EDF R&D, OPEN CASCADE
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
CMAKE_MINIMUM_REQUIRED(VERSION 2.8.8 FATAL_ERROR)
PROJECT(Salome_:sat:{AppModule} C CXX)

# Ensure a proper linker behavior:
CMAKE_POLICY(SET CMP0003 NEW)

# Versioning
# ===========
# Project name, upper case
STRING(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UC)

SET(${PROJECT_NAME_UC}_MAJOR_VERSION 0)
SET(${PROJECT_NAME_UC}_MINOR_VERSION 0)
SET(${PROJECT_NAME_UC}_PATCH_VERSION 0)
SET(${PROJECT_NAME_UC}_VERSION
  ${${PROJECT_NAME_UC}_MAJOR_VERSION}.${${PROJECT_NAME_UC}_MINOR_VERSION}.${${PROJECT_NAME_UC}_PATCH_VERSION})


# Common CMake macros
SET(CONFIGURATION_ROOT_DIR $ENV{CONFIGURATION_ROOT_DIR} CACHE PATH "Path to the Salome CMake configuration files")
IF(EXISTS ${CONFIGURATION_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${CONFIGURATION_ROOT_DIR}/cmake")
  INCLUDE(SalomeMacros)
ELSE()
  MESSAGE(FATAL_ERROR "We absolutely need the Salome CMake configuration files, please define CONFIGURATION_ROOT_DIR !")
ENDIF()

# Find KERNEL
# ===========
SET(KERNEL_ROOT_DIR $ENV{KERNEL_ROOT_DIR} CACHE PATH "Path to the Salome KERNEL")
IF(EXISTS ${KERNEL_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${KERNEL_ROOT_DIR}/salome_adm/cmake_files")
  FIND_PACKAGE(SalomeKERNEL REQUIRED)
  KERNEL_WITH_CORBA() # check whether KERNEL builded with CORBA
ELSE(EXISTS ${KERNEL_ROOT_DIR})
  MESSAGE(FATAL_ERROR "We absolutely need a Salome KERNEL, please define KERNEL_ROOT_DIR")
ENDIF(EXISTS ${KERNEL_ROOT_DIR})

# User options
# ============
OPTION(SALOME_BUILD_TESTS "Build SALOME tests" ON)
OPTION(SALOME_BUILD_DOC "Generate SALOME :sat:{AppModule} documentation" ON)

IF(SALOME_BUILD_TESTS)
  ENABLE_TESTING()
ENDIF()

# KERNEL optionals:
IF(SALOME_BUILD_DOC)
  FIND_PACKAGE(SalomePythonInterp REQUIRED)
  FIND_PACKAGE(SalomePythonLibs REQUIRED)
  FIND_PACKAGE(SalomeSphinx)
  SALOME_LOG_OPTIONAL_PACKAGE(Sphinx SALOME_BUILD_DOC)
ENDIF()

  
# Find GUI
# ===========

SET(GUI_ROOT_DIR $ENV{GUI_ROOT_DIR} CACHE PATH "Path to the Salome GUI")
IF(EXISTS ${GUI_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${GUI_ROOT_DIR}/adm_local/cmake_files")
  FIND_PACKAGE(SalomeGUI REQUIRED)
  SALOME_GUI_WITH_CORBA() #remove this line if you don't need GUI module builded with CORBA
  #remove unnecessary options from this list (see SALOME_GUI_MODE() macro description)
  SALOME_GUI_MODE(SALOME_USE_SALOMEOBJECT SALOME_USE_OCCVIEWER SALOME_USE_VTKVIEWER SALOME_USE_PYCONSOLE
                  OPTIONAL SALOME_USE_PLOT2DVIEWER SALOME_USE_GLVIEWER SALOME_USE_GRAPHICSVIEW 
                  SALOME_USE_QXGRAPHVIEWER SALOME_USE_PVVIEWER SALOME_USE_PYVIEWER
                  )
  ADD_DEFINITIONS(${GUI_DEFINITIONS})
  INCLUDE_DIRECTORIES(${GUI_INCLUDE_DIRS})
ELSE(EXISTS ${GUI_ROOT_DIR})
  MESSAGE(FATAL_ERROR "We absolutely need a Salome GUI, please define GUI_ROOT_DIR")
ENDIF(EXISTS ${GUI_ROOT_DIR})

# Qt
IF(NOT SALOME_GUI_BUILD_WITH_QT5)
  FIND_PACKAGE(SalomeQt4 REQUIRED COMPONENTS QtCore QtGui)
ELSE()
  FIND_PACKAGE(SalomeQt5 REQUIRED)
ENDIF()

# Directories
# (default values taken from KERNEL)
# ===========
SET(SALOME_INSTALL_SCRIPT_PYTHON "${SALOME_INSTALL_SCRIPT_PYTHON}" CACHE PATH "Install path: SALOME Python scripts")

# Specific to :sat:{AppModule}:
SET(SALOME_INSTALL_RES_DATA "${SALOME_INSTALL_RES}/salome" CACHE PATH "Install path: SALOME SALOME specific data")
SET(SALOME_INSTALL_DOC_GUI "${SALOME_INSTALL_DOC}/gui/${PROJECT_NAME_UC}" CACHE PATH "Install path: SALOME SALOME gui documentation")
SET(SALOME_HTML_STATIC_PATH "${SALOME_INSTALL_DOC_GUI}/_static" CACHE PATH "Install path: SALOME SALOME html static data")

MARK_AS_ADVANCED(SALOME_INSTALL_SCRIPT_PYTHON)

INSTALL(CODE "FILE(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/USERS)")

# Sources 
# ========
#ADD_SUBDIRECTORY( src ) # JCC 29/08/2017 #spns 8090
ADD_SUBDIRECTORY( resources )
#ADD_SUBDIRECTORY( doc )

# Additional files
# ================
SET(_salome_context_API_SCRIPTS
   ${KERNEL_ROOT_DIR}/bin/salome/salomeContext.py
   ${KERNEL_ROOT_DIR}/bin/salome/salomeContextUtils.py
   ${KERNEL_ROOT_DIR}/bin/salome/parseConfigFile.py
)
SALOME_INSTALL_SCRIPTS("${_salome_context_API_SCRIPTS}" ${SALOME_INSTALL_SCRIPT_PYTHON})
SET(_salome_context_TEST_DRIVER
   ${KERNEL_ROOT_DIR}/bin/salome/appliskel/salome_test_driver.py
   ${KERNEL_ROOT_DIR}/bin/salome/appliskel/salome_test_driver_gui.py
)
SALOME_INSTALL_SCRIPTS("${_salome_context_TEST_DRIVER}" ${SALOME_INSTALL_SCRIPT_PYTHON}/appliskel)
SET(_salome_context_BASHRC
   ${KERNEL_ROOT_DIR}/bin/salome/appliskel/.bashrc
)
FILE(TO_CMAKE_PATH ${CMAKE_INSTALL_PREFIX} _:sat:{AppModule}_ROOT_DIR)
SALOME_INSTALL_SCRIPTS("${_salome_context_BASHRC}" ${_:sat:{AppModule}_ROOT_DIR})
