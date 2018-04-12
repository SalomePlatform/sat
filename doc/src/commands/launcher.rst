
Command launcher
******************

Description
===========
The **launcher** command creates a SALOME launcher (a python command to start SALOME).


Usage
=====
* Create a launcher: ::

    sat launcher <application>
    
  Generate a launcher in the application directory, i.e ``$APPLICATION.workdir``.

* Create a launcher with a given name ::

    sat launcher <application>

  The launcher will called ZeLauncher.

* Set a specific resources catalog: ::

    sat launcher <application>
    
  Note that the catalog specified will be copied to the profile directory.

* Generate the catalog for a list of machines: ::

    sat launcher <application>

  This will create a catalog by querying each machine (memory, number of processor) with ssh.


Some useful configuration pathes
=================================

* APPLICATION.profile

  * **product**: the name of the profile product (the product in charge of holding the application stuff, like logos, splashscreen)
  * **launcher_name**: the name of the launcher.

