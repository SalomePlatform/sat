
Command environ
****************

Description
===========
The **environ** command generates the environment files used to run and compile SALOME.
Please note that these files are not required any more, 
salomeTool set the environment himself, when compiling.
And so does the salome launcher.
These files are useful when someone wants to check the environment.
They could be used in debug mode to set the environment for gdb.
The configuration part at the end of this page explains how 
to specify the environment which will be used by sat (at build or run time), 
and which is written in files by sat environ command.

Usage
=====
* Create the (sh) environment files of the application: ::

    sat environ <application>

* Create the environment files of the application for a given shell. 
  Options are bash, bat (for windows) and cfg (the configuration format used by salomé): ::

    sat environ <application> --shell [bash|cfg|all]

* Use a different prefix for the files (default is 'env'): ::

    sat environ <application> --prefix <prefix>
    This will create file <prefix>_launch.sh, <prefix>_build.sh...

* Use a different target directory for the files: ::

    sat environ <application> --target <path>
    This will create file env_launch.sh, env_build.sh... in the directory corresponding to <path>

* Generate the environment files only with the given products: ::

    sat environ <application> --product <product1> --product <product2> ....
    This will create the environment files only for the given products and their prerequisites.
    It is useful when you want to visualise which environment uses sat to compile a given product.


Configuration
=============
The specification of the environment can be done through sevaral mechanisms.

1. For salome products (the products with the property is_SALOME_module : "yes") the environment is set automatically by sat, in respect with Salomé requirements.

2. For other products, the environment is set with the use of the environ section within the pyconf file of the product. The user has two possibilities, either set directly the environment within the section, or specify a python script which wil be used to set the environment programmatically.

Within the section, the user can define environment variables. He can also modify PATH variables, by appending or prepending directories.
In the following example, we prepend <install_dir>/lib to LD_LIBRARY_PATH (note the underscore before), append <install_dir>/lib to PYTHONPATH (the underscore is after!), and set LAPACK_ROOT_DIR  to <install_dir>: ::

    environ :
    {
       _LD_LIBRARY_PATH : $install_dir + $VARS.sep + "lib"
       PYTHONPATH_ : $install_dir + $VARS.sep + "lib"
       LAPACK_ROOT_DIR : $install_dir
    }

It is possible here to distinguish the build environment from the launch environment. For that, use a subsection called build or launch. In the example below, LD_LIBRARY_PATH and PYTHONPATH are only modified at run time, not at compile time: ::

    environ :
    {
        build
        {
            LAPACK_ROOT_DIR : $install_dir
        }
        launch
        {
            LAPACK_ROOT_DIR : $install_dir
           _LD_LIBRARY_PATH : $install_dir + $VARS.sep + "lib"
           PYTHONPATH_ : $install_dir + $VARS.sep + "lib"
        }
    }

3. The last possibility is to set the environment with a python script. The script should be provided in the products/env_scripts directory of the sat project, and its name is specified in the environment section with the key **env_script**: ::

    environ :
    {
        env_script : "lapack.py"   
    }

Please note that the two modes are complementary and are both taken into account.
Most of the time, the first mode is sufficient. The second mode can be used when the environment has to be set programmatically.
Here is an example: ::

    #!/usr/bin/env python
    #-*- coding:utf-8 -*-

    import os.path
    import platform

    def set_env(env, prereq_dir, version):
        env.set("TRUST_ROOT_DIR",prereq_dir)
        env.prepend('PATH', os.path.join(prereq_dir, 'bin'))
        env.prepend('PATH', os.path.join(prereq_dir, 'include'))
        env.prepend('LD_LIBRARY_PATH', os.path.join(prereq_dir, 'lib'))
        pass

The developer implements a handle which is called by sat to set the environment.
sat defines four handles:

* *set_env(env, prereq_dir, version)* : used at build and run time. 
* *set_env_launch(env, prereq_dir, version)* : used only at run time (if defined!)
* *set_env_build(env, prereq_dir, version)* : used only at build time (if defined!)
* *set_native_env(env)* : used only for native products, at build and run time.
