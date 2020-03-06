
.. include:: ../../rst_prolog.rst

Command compile
****************

Description
===========
The **compile** command allows compiling the products of a SALOME_ application.


Usage
=====
* Compile a complete application: ::

    sat compile <application>

* Compile only some products: ::

    sat compile <application> --products <product1>,<product2> ... 

* Use *sat -t* to duplicate the logs in the terminal (by default the logs are stored and displayed with *sat log* command): ::

    sat -t compile <application> --products <product1>

* Compile a module and its dependencies: ::

    sat compile <application> --products med --with_fathers

* Compile a module and the modules depending on it (for example plugins): ::
  
    sat compile <application> --products med --with_children

* Clean the build and install directories before starting compilation: ::

    sat compile <application> --products GEOM  --clean_all

  .. note:: | a warning will be shown if option *--products* is missing
            | (as it will clean everything)

* Clean only the install directories before starting compilation: ::

    sat compile <application> --clean_install

* Add options for make: ::

    sat compile <application> --products <product> --make_flags <flags>

* Use the *--check* option to execute the unit tests after compilation: ::

    sat compile <application> --check

* Remove the build directory after successful compilation (some build directory like qt are big): ::

    sat compile <application> --products qt --clean_build_after

* Stop the compilation as soon as the compilation of a module fails: ::
  
    sat compile <application> --stop_first_fail

* Do not compile, just show if products are installed or not, and where is the installation: ::

    sat compile <application> --show

* Print the recursive list of dependencies of one (or several) products: ::

    sat -v5 compile SALOME-master -p GEOM --with_fathers --show


Some useful configuration paths
=================================

The way to compile a product is defined in the *pyconf* file configuration.
The main options are: 

  * **build_source** : the method used to build the product (cmake/autotools/script)
  * **compil_script** : the compilation script if build_source is equal to "script"
  * **cmake_options** : additional options for cmake.
  * **nb_proc** : number of jobs to use with make for this product.
  * **check_install** : allow to specify a list of paths (relative to install directory), that sat will check after installation. This flag allows to check if an installation is complete.  
  * **install_dir** : allow to change the default install dir. If the value is set to *'base'*, the product will by default be installed in salomeTool base. Unless base was set to 'no' in application pyconf.
