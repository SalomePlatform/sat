
.. include:: ../../rst_prolog.rst

Command launcher
******************

Description
===========
The **launcher** command creates a SALOME launcher, a python script file to start SALOME_.


Usage
=====
* Create a launcher: ::

    sat launcher <application>
    
  Generate a launcher in the application directory, i.e ``$APPLICATION.workdir``.

* Create a launcher with a given name (default name is ``APPLICATION.profile.launcher_name``) ::

    sat launcher <application> --name ZeLauncher

  The launcher will be called *ZeLauncher*.

* Set a launcher which does not initialise the PATH variables: ::

    sat launcher <application>  --no_path_init
    
  In this case the launcher does not initialise the path variables (the default is to do it only for PATH, not for LD_LIBRARY_PATH, PYTHONPATH, etc).

* Create a generic launcher, which sets the environment (bash or bat) and call the exe given as argument: ::

    sat launcher <application> -e INSTALL/SALOME/bin/salome/salome.py -n salome.sh 

  The launcher will be called salome.sh. It will source the environment and call ``$APPLICATION.workdir``/INSTALL/SALOME/bin/salome/salome.py.
  The arguments given to salome.sh are transfered to salome.py.  

* Set a specific resources catalog: ::

    sat launcher <application>  --catalog  <path of a salome resources catalog>
    
  Note that the catalog specified will be copied to the profile directory.

* Generate the catalog for a list of machines: ::

    sat launcher <application> --gencat <list of machines>

  This will create a catalog by querying each machine (memory, number of processors) with ssh.

* Generate a mesa launcher (if mesa and llvm are parts of the application). Use this option only if you have to use salome through ssh and have problems with ssh X forwarding of OpengGL modules (like Paravis): ::

    sat launcher <application> --use_mesa


Configuration
=============

Some useful configuration paths: 

* **APPLICATION.profile**

  * **product** : the name of the profile product (the product in charge of holding the application stuff, like logos, splashscreen)
  * **launcher_name** : the name of the launcher.

