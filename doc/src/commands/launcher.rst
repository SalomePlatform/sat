
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

* Set a specific resources catalog: ::

    sat launcher <application>  --catalog  <path of a salome resources catalog>
    
  Note that the catalog specified will be copied to the profile directory.

* Generate the catalog for a list of machines: ::

    sat launcher <application> --gencat <list of machines>

  This will create a catalog by querying each machine (memory, number of processor) with ssh.

* Generate a mesa launcher (if mesa and llvm are parts of the application). Use this option only if you have to use salome through ssh and have problems with ssh X forwarding of OpengGL modules (like Paravis): ::

    sat launcher <application> --use_mesa


Configuration
=============

Some useful configuration pathes: 

* **APPLICATION.profile**

  * **product** : the name of the profile product (the product in charge of holding the application stuff, like logos, splashscreen)
  * **launcher_name** : the name of the launcher.

