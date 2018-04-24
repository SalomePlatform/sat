*************
Configuration
*************

*salomeTools* uses files to store its configuration parameters.

There are several configuration files which are loaded by salomeTools in a specific order. 
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

PRODUCTS section
------------------
| This section is defined in the product file.
| It contains instructions on how to build a version of SALOME (list of prerequisites-products and versions)

:: 

    # to get the current setting
    sat config SALOME-xx --value PRODUCTS

APPLICATION section
---------------------
| This section is optional, it is also defined in the product file.
| It gives additional parameters to create an application based on SALOME, as versions of products to use.

:: 

    # to get the current setting
    sat config SALOME-xx --value APPLICATION


.. _USER-Section:

USER section
--------------
This section is defined by the user configuration file, 
``~/.salomeTools/salomeTools.pyconf``.

The ``USER`` section defines some parameters (not exhaustive):

* **workDir** : 

    | The working directory. 
    | Each product will be usually installed here (in sub-directories).

* **browser** : The web browser to use (*firefox*). 

* **editor** : The editor to use (*vi, pluma*). 

* and other user preferences. 

:: 

    # to get the current setting
    sat config SALOME-xx --value USER




