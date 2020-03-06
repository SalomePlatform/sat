
.. include:: ../../rst_prolog.rst

Command application
*********************

Description
===========
The **application** command creates a virtual SALOME application.
Virtual SALOME applications are used to start SALOME when distribution is needed.

Usage
=====
* Create an application: ::

    sat application <application>
    
  Create the virtual application directory in the salomeTool application directory ``$APPLICATION.workdir``.

* Give a name to the application: ::

    sat application <application> --name <my_application_name>

  *Remark*: this option overrides the name given in the virtual_app section of the configuration file ``$APPLICATION.virtual_app.name``.

* Change the directory where the application is created: ::

    sat application <application> --target <my_application_directory>

* Set a specific SALOME resources catalog (it will be used for the distribution of components on distant machines): ::

    sat application <application> --catalog <path_to_catalog>
    
  Note that the catalog specified will be copied to the application directory.

* Generate the catalog for a list of machines: ::

    sat application <application> --gencat machine1,machine2,machine3

  This will create a catalog by querying each machine through ssh protocol (memory, number of processor) with ssh.

* Generate a mesa application (if mesa and llvm are parts of the application). Use this option only if you have to use salome through ssh and have problems with ssh X forwarding of OpengGL modules (like Paravis): ::

    sat launcher <application> --use_mesa

Some useful configuration paths
=================================

The virtual application can be configured with the virtual_app section of the configuration file.

* **APPLICATION.virtual_app**

  * **name** : name of the launcher (to replace the default runAppli).
  * **application_name** : (optional) the name of the virtual application directory, if missing the default value is ``$name + _appli``.
    
