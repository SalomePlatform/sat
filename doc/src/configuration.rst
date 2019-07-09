*************
Configuration
*************

*salomeTools* uses files with **.pyconf** extension to store its configuration parameters.
These pyconf configuration files are provided by the salomeTool projects that are set by sat init command.

When executing a command, sat will load several configuration files in a specific order.
When all the files are loaded a *config* object is created.
Then, this object is passed to all command scripts.


Syntax
======
The configuration files use a python-like structure format 
(see `config module <http://www.red-dove.com/config-doc/>`_ for a complete description).

* **{}** define a dictionary,
* **[]** define a list,
* **@** can be used to include a file,
* **$prefix** reference to another parameter (ex: ``$PRODUCT.name``),
* **#** comments.

.. note:: in this documentation a reference to a configuration parameter will be noted ``XXX.YYY``.

Description
===========

.. _VARS-Section:

VARS section
-------------
| This section is dynamically created by salomeTools at run time.
| It contains information about the environment: date, time, OS, architecture etc. 

::

    # to get the current setting
    sat config --value VARS

APPLICATION section
------------------
| This section is defined in the application pyconf file.
| It contains instructions on how to build a version of SALOME (list of products and versions, compilation options, etc.)

:: 

    # to get the current setting
    sat config SALOME-xx --value APPLICATION

PRODUCTS section
---------------------
| This section contains all the information required to build the products contained in the application.
| It is build from the products configuration files.

:: 

    # to get the current setting
    sat config SALOME-xx --value PRODUCT


.. _USER-Section:

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

* **PROJECTs** : This section contains the configuration of the projects loaded in salomeTool by sat init --add_project command. 
* **PATHS** : This section contains paths used by saloeTools.
* **LOCAL** : contains information relative to the local installation of salomeTool.
* **INTERNAL** : contains internal salomeTool information

All these sections can be printed with sat config command:

::

    # It is possible to use sat completion mode to print available sections.
    sat config SALOME-xx --value <TAB> <TAB>
    > APPLICATION.       INTERNAL.          LOCAL.             PATHS. 
    > PRODUCTS.          PROJECTS.          USER.              VARS.

    # get paths used by sat
    sat config SALOME-xx --value PATHS

It is possible to use sat completion mode to print available sections.
