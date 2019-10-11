
.. include:: ../rst_prolog.rst

*************************
Main usage of SAlomeTools
*************************

Purpose, Command Line Interface
===============================

sat is a Command Line Interface (CLI_) based on python langage.
Its purpose is to cover the maintenance and the production of the salome platform and its applications.

Notably:

* the definition of the applications content (the products, the resources, the options, the environment, the launcher, etc.)
* the description of the products (the environment to set, how to get the sources; how to compilation (which options), , the dependencies, etc).
* the complete preparation and build
* the management of unit or integration tests
* the production of binary or source packages

It is designed to run on several Linux OS and Windows, with
the possibility to specify platform dependent specifics (with the **__overwrite__** functionality. 
It can be used from interactively from a terminal, or in batch mode. 

.. code-block:: bash

  sat [generic_options] [command] [application] [command_options]

   
Getting help
============

Help option -h
--------------

To get help in terminal mode as simple text, use **--help** or **-h** option:

.. code-block:: bash

    sat -h          # or --help : get the list of existing commands and main options
    sat compile -h  # get the help on the specific command 'compile'

Completion mode
---------------

When getting started with sat, the use of the competion mode is usefull. This mode will display by type twice on the **tab key** the available options, command, applications or product available. The completion mode has to be activated by sourcing the file **complete_sat.sh** contained in salomeTool directory:

.. code-block:: bash

    source complete_sat.sh      # activate the completion mode

    ./sat conpile  <TAB> <TAB>  # liste all application available for compilation
    > SALOME-7.8.2   SALOME-8.5.0   SALOME-9.3.0   SALOME-master

    ./sat conpile SALOME-9.3.0 <TAB> <TAB>  # list all available options 
    > --check              --clean_build_after  --install_flags      --properties
    > --stop_first_fail    --with_fathers       --clean_all          --clean_make
    > --products           --show               --with_children


Verbose and Debug mode
======================

Verbosity
---------

**sat** has several levels of verbosity. The default value is **3** and correspond to the impression of the main information on what has been done.
A verbosity of **0** correspond to no impression at all, while on the opposite a verbosity of **6** prints a lot of information.

Change verbosity level (default is 3).

.. code-block:: bash

    sat -v0 prepare SALOME-9.3.0 -p GEOM  # prepare GEOM product in silent mode
    sat -v6 compile SALOME-9.3.0 -p GEOM  # compile GEOM with full verbosity

Debug mode -g
-------------

This mode is used by developers to see more traces and *stack* if an exception is raised.


Building a SALOME application
=============================

Get the list of available applications
--------------------------------------

To get the list of the current available applications in your context:

.. code-block:: bash

    sat config -l

The result depends upon the projects that have been loaded in sat.


Prepare sources of an application
---------------------------------

To prepare (get) *all* the sources of an application (*SALOME_xx* for example):

.. code-block:: bash

    # get all sources
    sat prepare SALOME_xx

    # get (git) sources of SALOME modules
    sat prepare SALOME_xx  --properties is_SALOME_module:yes

| The sources are usually copied in directory *$APPLICATION.workdir + $VARS.sep + 'SOURCES'*


Compile an application
----------------------

To compile an application

.. code-block:: bash

    # compile all prerequisites/products
    sat compile SALOME_xx
    
    # compile only three products (KERNEL, GUI and SHAPER), if not done yet
    sat compile SALOME_xx -p KERNEL,GUI,SHAPER

    # compile only two products, unconditionaly 
    sat compile SALOME_xx -p KERNEL,GUI --clean_all

    # (re)compile only salome modules
    sat compile SALOME_xx --properties is_SALOME_module:yes  --clean_all

| The products are usually build in the directory
| *$APPLICATION.workdir + $VARS.sep + 'BUILD'*
|
| The products are usually installed in the directory
| *$APPLICATION.workdir + $VARS.sep + 'INSTALL'*


