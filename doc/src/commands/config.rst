
.. include:: ../../rst_prolog.rst

Command config
******************

Description
===========
The **config** command manages sat configuration. 
It allows display, manipulation and operation on configuration files

Usage
=====
* Edit the user personal configuration file ``$HOME/.salomeTools/SAT.pyconf``. It is used to store the user personal choices, like the favorite editor, browser, pdf viewer: ::

    sat config --edit

* List the available applications (they come from the sat projects defined in ``data/local.pyconf``: ::
  
    sat config --list

* Edit the configuration of an application: ::

    sat config <application> --edit

* Copy an application configuration file into the user personal directory: ::
  
    sat config <application> --copy [new_name]

* | Print the value of a configuration parameter. 
  | Use the automatic completion to get recursively the parameter names.
  | Use *--no_label* option to get *only* the value, *without* label (useful in automatic scripts).
  | Examples (with *SALOME-xx* as *SALOME-8.4.0* ): 

  .. code-block:: bash

    # sat config --value <parameter_path>
    sat config --value .         # all the configuration
    sat config --value LOCAL
    sat config --value LOCAL.workdir

    # sat config <application> --value <parameter_path>
    sat config SALOME-xx --value APPLICATION.workdir
    sat config SALOME-xx --no_label --value APPLICATION.workdir

* | Print in one-line-by-value mode the value of a configuration parameter, 
  | with its source *expression*, if any. 
  | This is a debug mode, useful for developers.
  | Prints the parameter path, the source expression if any, and the final value:

  ::

    sat config SALOME-xx -g USER

  .. note:: And so, *not only for fun*, to get **all expressions** of configuration
   
    .. code-block:: bash

      sat config SALOME-xx -g . | grep -e "-->"


* Print the patches that are applied: ::

    sat config SALOME-xx --show_patchs

* Get information on a product configuration: 

.. code-block:: bash

    # sat config <application> --info <product>
    sat config SALOME-xx --info KERNEL
    sat config SALOME-xx --info qt

Some useful configuration pathes
=================================

Exploring a current configuration.

* **PATHS**: To get list of directories where to find files.

* **USER**: To get user preferences (editor, pdf viewer, web browser, default working dir).

sat commands: ::

  sat config SALOME-xx -v PATHS
  sat config SALOME-xx -v USERS



