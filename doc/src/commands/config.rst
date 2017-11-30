******
config
******

Description
===========
The **config** command manages sat configuration. It allows display, manipulation and operation on configuration files

Usage
=====
* Edit the user personal configuration file (~/.salomeTools/SAT.pyconf). It is used to store the user personal choices, like the favorite editor, browser, pdf viewer: ::

    sat config --edit

* List the available applications (they come from the sat projects defined in data/local.pyconf): ::
  
    sat config --list

* Edit the configuration of an application: ::

    sat config <application> --edit

* Copy an application configuration file into the user personal directory: ::
  
    sat config <application> --copy [new_name]

* Print the value of a configuration parameter. Use the automatic completion to get recursively the parameter names. Use -n option to get only the value, not the lable (useful in automatic scripts). Examples: ::

    sat config --value <parameter_path>
    sat config --value LOCAL
    sat config --value LOCAL.workdir

    sat config <application> --value <parameter_path>
    sat config SALOME-8.4.0  --value  APPLICATION.workdir
    sat config SALOME-8.4.0 -n  --value  APPLICATION.workdir

* Print the patches that are applied: ::

    sat config SALOME-8.4.0  --show_patchs

* Get information on a product configuration: ::

    sat config <application> --info <product>
    sat config SALOME-8.4.0 --info KERNEL
    sat config SALOME-8.4.0 --info qt

Configuration
=============
* PATH.

  * **ARCHIVEPATH** list of directories where to find application files.
  * **PRODUCTPATH** list of directories where to find products configuration files.

* USER

  * **editor**: command to use to start an editor (by default vi),
  * **browser**: command to use to start a browser (by default firefox),
  * **pdf_viewer**: command to use to start a pdf viewer (by default evince).
