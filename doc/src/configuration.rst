*************
Configuration
*************

Introduction
============

For the configuration, SAT uses a python module called *config*, which aims to offer more power and flexibility for the configuration of python programs.
This module was slightly adapted for SAT, and renamed Pyconf.
(see `config module <http://www.red-dove.com/config-doc/>`_ for a complete description of the module, the associated syntax, the documentation).

*salomeTools* uses files with **.pyconf** extension to store the configuration parameters.
These *.pyconf* are parsed by SAT, and merged into a global configuration, which is passed to the sat commands and used by them.


Configuration projects
======================

By default SAT is provided with no configuration at all, except is own internal one.
The configuration is brought by SAT projects : usually a git base containing all the configuration files of a project (*.pyconf* files).
For Salome platform, the SAT project is called SAT_SALOME and can be downloaded from salome Tuleap forge.
SAT projects are loaded in sat with the sat init command:

.. code-block:: bash

    # get salome platform SAT configuration project (SAT_SALOME), and load it into SAT
    git clone SAT_SALOME
    SAT/sat init --add_project $(pwd)/SAT_SALOME/salome.pyconf  

SAT_SALOME project provides all configuration files for salome applications, and for the products that are used in these applications.


Application configuration
=========================

The configuration files of applications contain the required information for SAT to build the application.
They are usually located in the application directory of the project:

.. code-block:: bash

    # list applications provided by SAT_SALOME project
    ls SAT_SALOME/applications
        MEDCOUPLING-9.4.0.pyconf             SALOME-7.8.0.pyconf       SALOME-8.5.0.pyconf          SALOME-9.4.0.pyconf

These files can be edited directly, and also with the SAT:

.. code-block:: bash

    # edit SALOME-9.4.0.pyconf configuration file
    SAT/sat config SALOME-9.4.0 -e


The application configuration file defines the APPLICATION sections. The content of this section (or a part of it) can be displayed with *sat config* command:

.. code-block:: bash

    # display the complete APPLICATION configuration
    sat config SALOME-9.4.0 -v APPLICATION

    # display only the application properties
    sat config SALOME-9.4.0 -v APPLICATION.properties

SAT users that need to create new application files for their own purpose usually copy an existing configuration file and adapt it to their application.
Let's discribe the content of an application pyconf file. We take in the following examples the file *SAT_SALOME/applications/SALOME-9.4.0.pyconf*.


Global variables and flags
--------------------------

At the beginning of the APPLICATION sections, global variables and flags are defined:  

  * **name** : the name of the application (mandatory)
  * **workdir** : the directory in which the application is produced (mandatory)
  * **tag** : the default tag to use for the git bases
  * **dev** : activate the dev mode. In dev mode git bases are checked out only one time, to avoid risks of removing developments.
  * **verbose** : activate verbosity in the compilation
  * **debug** : activate debug mode in the compilation, i.e -g option
  * **python3** : 'yes/no' tell sat that the application uses python3 
  * **base** : 'yes/no/name' to set up the use of a SAT base

.. code-block:: bash

    APPLICATION :
    {
        name : 'SALOME-9.4.0'
        workdir : $LOCAL.workdir + $VARS.sep + $APPLICATION.name + '-' + $VARS.dist
        tag : 'V9_4_BR'
        debug : 'no'
        dev : 'no'
        base : 'no'
        python3 : 'yes'
        ...

Please note the workdir variable is defined in the above example with references to other sections defined in other configurations files (i.e. $LOCAL and $VARS).
It's a useful Pyconf functionality.
Most of the global variables are optionnal, except name and workdir.

Environment subsection
----------------------

This subsection allows defining environment variables at the application level (most of the time the environment is set by the products configuration).

.. code-block:: bash

    APPLICATION :
    {
    ...
        environ :
        {
            build : {CONFIGURATION_ROOT_DIR : $workdir + $VARS.sep + "SOURCES" + $VARS.sep + "CONFIGURATION"}
            launch : {PYTHONIOENCODING:"UTF_8"}
            SALOME_trace : "local" # local/file:.../with_logger
            SALOME_MODULES : "SHAPER,GEOM,SMESH,PARAVIS,YACS,JOBMANAGER"  # specify the first modules to display in gui
        }
    }

In the example above CONFIGURATION_ROOT_DIR variable will be set only at compile time (usage of *build* key), while PYTHONIOENCODING will be set only at run-time (use of *launch* key).
variables SALOME_trace and SALOME_MODULES are set both at compile time and run time.


products subsection
-------------------

This subsection will specify which products are included in the application.
For each product, it is possible to specify in a dictionnary:

  * **tag** : the tag to use for the product
  * **dev** : activate the dev mode.
  * **verbose** : activate verbosity in the compilation
  * **debug** : activate debug mode

If these flags are not specified, SAT takes the default application flag.
In the following example, SAT uses the default tag V9_4_BR for products SHAPER, KERNEL and MEDCOUPLING.
For LIBBATCH it uses the tag V2_4_2.
KERNEL is compiled in debug and verbose mode.

.. code-block:: bash

    APPLICATION :
    {
    ...
        tag : 'V9_4_BR'
    ...
        products :
        {
        'SHAPER'
        'LIBBATCH' : {tag :'V2_4_2'}
        'KERNEL' : {debug:'yes', verbose:'yes'}
        'MEDCOUPLING'
        ...


properties
----------

Properties are used by SAT to define some general rules or policies.
They can be defined in the application configuration with the properties subsection:

.. code-block:: bash

    APPLICATION :
    {
    ...
        properties :
        {
            mesa_launcher_in_package : "yes"
            repo_dev : "yes"
            pip : 'yes'
            pip_install_dir : 'python'
        }

In this example the following properties are used:

 * **mesa_launcher_in_package** : ask to put a mesa launcher in the packages produced by sat package command
 * **repo_dev** : use the development git base (for salome, the tuleap forge)
 * **pip** : ask to use pip to get python products
 * **pip_install_dir** : install pip products in python installation directory (not in separate directories)


Products configuration
======================

The configuration files of products contain the required information for SAT to build each product.
They are usually located in the product directory of the project. SAT_SALOME supports a lot of products:

.. code-block:: bash

    ls SAT_SALOME/products/
    ADAO_INTERFACE.pyconf  COREFLOWS_PROFILE.pyconf  GHS3DPLUGIN.pyconf         JOBMANAGER.pyconf       omniORB.pyconf       Python.pyconf                    Sphinx.pyconf
    ADAO_MODULE.pyconf     COREFLOWS.pyconf          GHS3DPRLPLUGIN.pyconf      KERNEL.pyconf           omniORBpy.pyconf     pytz.pyconf                      sphinx_rtd_theme.pyconf
    ADAO.pyconf            cppunit.pyconf            gl2ps.pyconf               kiwisolver.pyconf       opencv.pyconf        qt.pyconf                        subprocess32.pyconf
    alabaster.pyconf       cycler.pyconf             glu.pyconf                 lapack.pyconf           openmpi.pyconf       qwt.pyconf                       swig.pyconf
    ALAMOS_PROFILE.pyconf  Cython.pyconf             GMSHPLUGIN.pyconf          lata.pyconf             ospray.pyconf        requests.pyconf                  tbb.pyconf
    ALAMOS.pyconf          dateutil.pyconf           gmsh.pyconf                LIBBATCH.pyconf         packaging.pyconf     SALOME_FORMATION_PROFILE.pyconf  tcl.pyconf
    Babel.pyconf           distribute.pyconf         graphviz.pyconf            libpng.pyconf           ParaViewData.pyconf  SALOME_PROFILE.pyconf            TECHOBJ_ROOT.pyconf
    BLSURFPLUGIN.pyconf    DOCUMENTATION.pyconf      GUI.pyconf                 libxml2.pyconf          ParaView.pyconf      SALOME.pyconf                    tk.pyconf
    boost.pyconf           docutils.pyconf           hdf5.pyconf                llvm.pyconf             PARAVIS.pyconf       SAMPLES.pyconf                   Togl.pyconf
    bsd_xdr.pyconf         doxygen.pyconf            HELLO.pyconf               markupsafe.pyconf       ParMetis.pyconf      scipy.pyconf                     TRIOCFD_IHM.pyconf
    CALCULATOR.pyconf      EFICAS.pyconf             HEXABLOCKPLUGIN.pyconf     matplotlib.pyconf       patches              scons.pyconf                     TrioCFD.pyconf
    CAS.pyconf             EFICAS_TOOLS.pyconf       HEXABLOCK.pyconf           MEDCOUPLING.pyconf      petsc.pyconf         scotch.pyconf                    TRUST.pyconf
    CDMATH.pyconf          eigen.pyconf              HexoticPLUGIN.pyconf       medfile.pyconf          planegcs.pyconf      setuptools.pyconf                typing.pyconf
    CEATESTBASE.pyconf     embree.pyconf             Hexotic.pyconf             med_pre_windows.pyconf  pockets.pyconf       SHAPER.pyconf                    uranie_win.pyconf
    certifi.pyconf         env_scripts               homard_bin.pyconf          MED.pyconf              pthreads.pyconf      sip.pyconf                       urllib3.pyconf
    cgns.pyconf            expat.pyconf              homard_pre_windows.pyconf  mesa.pyconf             PY2CPP.pyconf        six.pyconf                       VISU.pyconf
    chardet.pyconf         f2c.pyconf                HOMARD.pyconf              MeshGems.pyconf         PYCALCULATOR.pyconf  SMESH.pyconf                     vtk.pyconf
    click.pyconf           FIELDS.pyconf             HXX2SALOME.pyconf          metis.pyconf            Pygments.pyconf      snowballstemmer.pyconf           XDATA.pyconf
    cmake.pyconf           freeimage.pyconf          HYBRIDPLUGIN.pyconf        NETGENPLUGIN.pyconf     pyhamcrest.pyconf    solvespace.pyconf                YACSGEN.pyconf
    colorama.pyconf        freetype.pyconf           idna.pyconf                netgen.pyconf           PYHELLO.pyconf       sphinxcontrib_napoleon.pyconf    YACS.pyconf
    compil_scripts         ftgl.pyconf               imagesize.pyconf           nlopt.pyconf            pyparsing.pyconf     sphinxcontrib.pyconf             zlib.pyconf
    COMPONENT.pyconf       functools32.pyconf        ispc.pyconf                numpy.pyconf            PyQt.pyconf          sphinxcontrib_websupport.pyconf
    CONFIGURATION.pyconf   GEOM.pyconf               Jinja2.pyconf              omniNotify.pyconf       pyreadline.pyconf    sphinxintl.pyconf


Available product configuration flags
-------------------------------------

* **name** : the name of the product 
* **build_source** : the method to use when getting the sources, possible choices are script/cmake/autotools. If "script" is chosen, a compilation script should be provided with compil_script key
* **compil_script** : to specify a compilation script (in conjonction with build_source set to "script"). The programming language is bash under linux, and bat under windows.  
* **get_source** : the mode to get the sources, possible choices are archive/git/svn/cvs
* **depend** : to give SAT the dependencies of the product
* **patches** : provides a list of patches, if required
* **source_dir** : where SAT copies the source
* **build_dir** : where SAT builds the product
* **install_dir** : where SAT installs the product

The following example is the configuration of boost product:

.. code-block:: bash

    default :
    {
        name : "boost"
        build_source : "script"
        compil_script :  $name + $VARS.scriptExtension
        get_source : "archive"
        environ :
        {
           env_script : $name + ".py"
        }
        depend : ['Python' ]
        opt_depend : ['openmpi' ]
        patches : [ ]
        source_dir : $APPLICATION.workdir + $VARS.sep + 'SOURCES' + $VARS.sep + $name
        build_dir : $APPLICATION.workdir + $VARS.sep + 'BUILD' + $VARS.sep + $name
        install_dir : 'base'
        properties :
        {
            single_install_dir : "yes"
            incremental : "yes"
        }
    }


Product properties
------------------

Properties are also associated to products.
It is possible to list all the properties with the command *./sat config SALOME-9.4.0 --show_properties**

Here are some properties frequently used:

* **single_install_dir** : the product can be installed in a common directory 
* **compile_time** : the product is used only at compile time (ex : swig)
* **pip** : the product is managed by pip
* **not_in_package** : the product will not be put in packages
* **is_SALOME_module** : the product is a SALOME module
* **is_distene** : the product requires a DISTENE licence

The product properties allow SAT doing specific choices according to the property.
They also allow users filtering products when calling commands.
For example it is possible to compile only SALOME modules with the command:

.. code-block:: bash

    # just recompile SALOME modules, not other products
    ./sat compile SALOME-9.4.0 --properties is_SALOME_module:yes --clean_all


Product environment
-------------------

The product environment is declared in a subsection called environment.
It is used by sat at compile time to set up the environment for the compilation of all the products depending upon it.
It is also used at run tim to set up the application environment.

Two mechanisms are offered to define the environment.
The first one is similar to the one used in the application configuration : inside the environ section, we declare variables or paths.
A variable appended or prepended by an underscore is treated as a path, to which we prepend or append the valued according to the position of the underscore.
In the following example, the value *<install_dir/share/salome/ressources/salome* is prepended to the path SalomeAppConfig.

.. code-block:: bash

    environ :
    {
        _SalomeAppConfig : $install_dir + $VARS.sep + "share" + $VARS.sep + "salome" + $VARS.sep + "resources" + $VARS.sep + "salome"
    }


But the most common way is to use an environment script, which specifies the environment by using an API provided by sat: 

.. code-block:: bash

    # use script qt.py to set up qt environment
    environ :
    {
       env_script : "qt.py"
    }

As an example, the environment script for qt is:

.. code-block:: python

    #!/usr/bin/env python
    #-*- coding:utf-8 -*-

    import os.path
    import platform

    def set_env(env, prereq_dir, version):
        env.set('QTDIR', prereq_dir)

        version_maj = version.split('.')
        if version_maj[0] == '5':
            env.set('QT5_ROOT_DIR', prereq_dir)
            env.prepend('QT_PLUGIN_PATH', os.path.join(prereq_dir, 'plugins'))
            env.prepend('QT_QPA_PLATFORM_PLUGIN_PATH', os.path.join(prereq_dir, 'plugins'))
            pass
        else:
            env.set('QT4_ROOT_DIR', prereq_dir)
            pass

        env.prepend('PATH', os.path.join(prereq_dir, 'bin'))

        if platform.system() == "Windows" :
            env.prepend('LIB', os.path.join(prereq_dir, 'lib'))
            pass
        else :
            env.prepend('LD_LIBRARY_PATH', os.path.join(prereq_dir, 'lib'))
            pass

*env* is the API provided by SAT, *prereq_dir* is the installation directory, *version* the product version.
*env.set* sets a variable, *env.prepend* and *env.append* are used to prepend or append values to a path.

The **setenv** function is used to set the environment at compile time and run time.
It is also possible to use **set_env_build** and **set_env_launch** callback functions to set specific compile or run time environment.
Finally the function **set_nativ_env** is used for native products.


Product sections
----------------

The product configuration file may contain several sections.
In addition to the  "default" section, it is possible to declare other sections that will be used for specific versions of the product.
This allows SAT compiling different versions of a product.
To determine which section should be used, SAT has an algorithm that takes into account the version number.
Here are some examples of sections that will be taken into account by SAT :

.. code-block:: bash

    # this section will be used for versions between 8.5.0 and 9.2.1
    _from_8_5_0_to_9_2_1 :
    {
        ...
    }

    # this section will only ve used for 9.3.0 version
    version_9_3_0 :
    {
        ...
    }

Several version numbering are considered by SAT (not only X.Y.Z)
For example V9, v9, 9, 9.0.0, 9_0_0, are accepted. 

By default SAT only considers one section : the one determined according to the version number, or the default one.
But if the **incremental property** is defined in the default section, and is set to "yes", then SAT enters in the **incremental mode** and merges different sections into one,
by proceeding incremental steps. SAT uses the following algorithm to merge the sections:

#. We take the complete "default" section
#. If a "default_win" section is defined, we merge it.
#. If a section name corresponds to the version number, we also merge it.
#. Finally on windows platform if the same section name appended by _win exists, we merge it.


Other configuration sections
============================ 


The configuration of SAT is split into eight sections : VARS, APPLICATION, PRODUCTS, PROJECTS, PATHS, USER, LOCAL, INTERNAL.
These sections are feeded by the pyconf files which are loaded by sat: each pyconf file is parsed by SAT and merged into the global configuration.
One file can reference variables defined in other files. Files are loaded in this order :

* the internal pyconf (declared inside sat)
* the personal pyconf : *~/.salomeTools/SAT.pyconf*
* the application pyconf
* the products pyconf (for all products declared in the application)

In order to check the configuration and the merge done by sat, it is possible to display the resulting eight section with the command:

.. code-block:: bash

    # display the content of a configuration section 
    # (VARS, APPLICATION, PRODUCTS, PROJECTS, PATHS, USER, LOCAL, INTERNAL)
    SAT/sat config SALOME-9.4.0 -v <section>

Note also that if you don't remember the name of a section it is possible to display section names with the automatic completion functionality.

We have already described two of the sections : APPLICATION and PRODUCTS.
Let's describe briefly the six others.

.. _VARS-Section:

VARS section
-------------
| This section is dynamically created by SAT at run time.
| It contains information about the environment: date, time, OS, architecture etc. 

::

    # to get the current setting
    sat config --value VARS


USER section
--------------

This section is defined by the user configuration file, 
``~/.salomeTools/SAT.pyconf``.

The ``USER`` section defines some parameters (not exhaustive):

* **pdf_viewer** : the pdf viewer used to read pdf documentation 

* **browser** : The web browser to use (*firefox*). 

* **editor** : The editor to use (*vi, pluma*). 

* and other user preferences. 

:: 

    # to get the current setting
    sat config SALOME-xx --value USER

    # to edit your personal configuration file
    sat config -e


Other sections
--------------

* **PROJECTS** : This section contains the configuration of the projects loaded in SAT by *sat init --add_project* command. 
* **PATHS** : This section contains paths used by salomeTools.
* **LOCAL** : contains information relative to the local installation of SAT.
* **INTERNAL** : contains internal SAT information


Overwriting the configuration
=============================

At the end of the process, SAT ends up with a complete global configuration resulting from the parsing of all *.pyconf* files.
It may be interesting to overwrite the configuration.
SAT offers two overwriting mechanisms to answer these two use cases:

#. Be able to conditionally modify the configuration of an application to take into account specifics and support multi-platform builds
#. Be able to modify the configuration in the command line, to enable or disable some options at run time

Application overwriting
-----------------------

At the end of the application configuration, it is possible to define an overwrite section with the keyword **__overwrite__ :**.
It is followed by a list of overwrite sections, that may be conditionnal (use of the keyword **__condition__ :**).
A classical usage of the application overwriting is the change of a prerequisite version for a given platform (when the default version does not compile).

.. code-block:: bash

    __overwrite__ :
    [
      {
       # opencv 3 do not compile on old CO6
        __condition__ : "VARS.dist in ['CO6']"
        'APPLICATION.products.opencv' : '2.4.13.5'
      }
    ]


Command line overwriting
------------------------

Command line overwriting is triggered by sat **-o** option, followed in double quotes by the parameter to overwrite, the = sign and the value in simple quotes.
In the following example, we suppose that the application SALOME-9.4.0 has set both flags debug and verbose to "no", and that we want to recompile MEDCOUPLING in debug mode, with cmake verbosity activated. The command to use is:

.. code-block:: bash

    # recompile MEDCOUPLING in debug mode (-g) and with verbosity
    ./sat -t -o "APPLICATION.verbose='yes'" -o "APPLICATION.debug='yes'" compile SALOME-9.4.0 -p MEDCOUPLING --clean_all

