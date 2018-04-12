
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
    
  Create the virtual application directory in the salomeTool application directory, i.e. ``$APPLICATION.workdir``

* Give a name to the application: ::

    sat application <application> --name MYAPP

  *Remark*: this option overrides the name given in the virtual_app section of the configuration file (``$APPLICATION.virtual_app.name``).

* Change the directory where the application is created: ::

    sat application <application> --target </my/applications/directory>

* Set a specific SALOME resources catalog (it will be used for the distribution of components on distant machines): ::

    sat application <application> --catalog <path to catalog>
    
  Note that the catalog specified will be copied to the application directory.

* Generate the catalog for a list of machines: ::

    sat application <application> --gencat machine,machine2,machine3

  This will create a catalog by querying each machine through ssh protocol (memory, number of processor) with ssh.


Some useful configuration pathes
=================================

The virtual application can be configured with the virtual_app section of the configutation file.
* APPLICATION.virtual_app

  * **name**: name of the launcher (to replace the default runAppli).
  * **application_name**: (optional) the name of the virtual application directory.

    * if missing the default value is '$name + _appli'.
    
