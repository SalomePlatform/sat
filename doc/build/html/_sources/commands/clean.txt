
.. include:: ../../rst_prolog.rst

Command clean
****************

Description
============

The **clean** command removes products in the *source, build, or install* directories of an application. Theses directories are usually named ``SOURCES, BUILD, INSTALL``.

Use the options to define what directories you want to suppress and to set the list of products


Usage
=======

* Clean all previously created *build* and *install* directories (example application as *SALOME_xx*):

  .. code-block:: bash

    # take care, is long time to restore, sometimes
    sat clean SALOME-xx --build --install
    
* Clean previously created *build* and *install* directories, only for products with property *is_salome_module*:

  .. code-block:: bash

    sat clean SALOME-xxx --build --install \
                         --properties is_salome_module:yes


Availables options
======================

  * **--products** : Products to clean.

  * **--properties** : 

    | Filter the products by their properties.
    | Syntax: *--properties <property>:<value>*

  * **--sources** : Clean the product source directories.

  * **--build** : Clean the product build directories.

  * **--install** : Clean the product install directories.

  * **--all** : Clean the product source, build and install directories.

  * **--sources_without_dev** : 

    | Do not clean the products in development mode, 
    | (they could have VCS_ commits pending).



Some useful configuration pathes
=================================

No specific configuration.
