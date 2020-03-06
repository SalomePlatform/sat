
.. include:: ../../rst_prolog.rst

Command environ
****************

Description
===========
The **environ** command generates the environment files used 
to run and compile your application (as SALOME_ is an example).

.. note :: 
   these files are **not** required, 
   salomeTool sets the environment itself, when compiling.
   And so does the salome launcher.

   These files are useful when someone wants to check the environment.
   They could be used in debug mode to set the environment for *gdb*.

The configuration part at the end of this page explains how 
to specify the environment used by sat (at build or run time), 
and saved in some files by *sat environ* command.

Usage
=====
* Create the shell environment files of the application: ::

    sat environ <application>

* Create the environment files of the application for a given shell. 
  Options are bash, bat (for windows), tcl, cfg (the configuration format used by SALOME): ::

    sat environ <application> --shell [bash|bat|cfg|tcl|all]

* Use a different prefix for the files (default is 'env'):

  .. code-block:: bash

    # This will create file <prefix>_launch.sh, <prefix>_build.sh
    sat environ <application> --prefix <prefix>

* Use a different target directory for the files:

  .. code-block:: bash

    # This will create file env_launch.sh, env_build.sh
    # in the directory corresponding to <path>
    sat environ <application> --target <path>

* Generate the environment files only with the given products:

  .. code-block:: bash

    # This will create the environment files only for the given products
    # and their prerequisites.
    # It is useful when you want to visualise which environment uses 
    # sat to compile a given product.
    sat environ <application> --product <product1>,<product2>, ...

* Generate tcl modules for use with *environment-modules* package. 

  .. code-block:: bash

    sat environ <application> --shell tcl

Use this command to generate tcl modules associated to a module base.
The production of a module base is triggered when the flag *base* in the application pyconf is set to a value not equal to *yes*.

  .. code-block:: bash

    APPLICATION :
    {
        ...
        # trigger the production of a environment module base which name is salome9
        base : 'salome9'
    }

In this example, the module base will be produced in *BASE/apps/salome9*, and the tcl modules associated in the directory tcl *BASE/apps/modulefiles/salome9*.
Later, it will be possible to enable these modules with the shell command *module use --append .../SAT/BASE/modulefiles*.

Configuration
=============

The specification of the environment can be done through several mechanisms.

1. For salome products (the products with the property ``is_SALOME_module`` as ``yes``) the environment is set automatically by sat, in respect with SALOME requirements.

2. For other products, the environment is set with the use of the environ section within the pyconf file of the product. The user has two possibilities, either set directly the environment within the section, or specify a python script which will be used to set the environment programmatically.

Within the section, the user can define environment variables. He can also modify PATH variables, by appending or prepending directories.
In the following example, we prepend *<install_dir>/lib* to ``LD_LIBRARY_PATH`` (note the *left first* underscore), append *<install_dir>/lib* to ``PYTHONPATH`` (note the *right last* underscore), and set ``LAPACK_ROOT_DIR`` to *<install_dir>*:

.. code-block:: bash

    environ :
    {
      _LD_LIBRARY_PATH : $install_dir + $VARS.sep + "lib"
      PYTHONPATH_ : $install_dir + $VARS.sep + "lib"
      LAPACK_ROOT_DIR : $install_dir
    }

It is possible to distinguish the build environment from the launch environment: use a subsection called *build* or *launch*. In the example below, ``LD_LIBRARY_PATH`` and ``PYTHONPATH`` are only modified at run time, not at compile time:

.. code-block:: bash

    environ :
    {
      build :
      {
        LAPACK_ROOT_DIR : $install_dir
      }
      launch :
      {
        LAPACK_ROOT_DIR : $install_dir
        _LD_LIBRARY_PATH : $install_dir + $VARS.sep + "lib"
        PYTHONPATH_ : $install_dir + $VARS.sep + "lib"
      }
    }

3. The last possibility is to set the environment with a python script. The script should be provided in the *products/env_scripts* directory of the sat project, and its name is specified in the environment section with the key ``environ.env_script``:

.. code-block:: python

    environ :
    {
      env_script : 'lapack.py'  
    }

Please note that the two modes are complementary and are both taken into account.
Most of the time, the first mode is sufficient.

The second mode can be used when the environment has to be set programmatically.
The developer implements a handle (as a python method) 
which is called by sat to set the environment.
Here is an example:

.. code-block:: python


    #!/usr/bin/env python
    #-*- coding:utf-8 -*-

    import os.path
    import platform

    def set_env(env, prereq_dir, version):
        env.set("TRUST_ROOT_DIR",prereq_dir)
        env.prepend('PATH', os.path.join(prereq_dir, 'bin'))
        env.prepend('PATH', os.path.join(prereq_dir, 'include'))
        env.prepend('LD_LIBRARY_PATH', os.path.join(prereq_dir, 'lib'))
        return

SalomeTools defines four handles:

* **set_env(env, prereq_dir, version)** : used at build and run time. 
* **set_env_launch(env, prereq_dir, version)** : used only at run time (if defined!)
* **set_env_build(env, prereq_dir, version)** : used only at build time (if defined!)
* **set_native_env(env)** : used only for native products, at build and run time.

