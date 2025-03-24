compute_dependencies
==================

The ``compute_dependencies`` command analyzes and displays the dependencies of specified products in a SALOME application.

Usage
-----

.. code-block:: bash

   sat compute_dependencies <application> --products <product1[,product2,...]>

Parameters
---------

* ``application``: The name of the SALOME application to analyze
* ``--products``: Comma-separated list of products to analyze dependencies for

Examples
--------

Basic usage with a single product:

.. code-block:: bash

   sat compute_dependencies APPLI_TEST --products KERNEL

Analyzing multiple products:

.. code-block:: bash

   sat compute_dependencies APPLI_TEST --products KERNEL,GUI

Output Format
------------

The command outputs a structured list of dependencies in the following format:

.. code-block:: text

   Required products and dependencies:
   Mandatory:
   [list of mandatory dependencies]
   Optional:
   [list of optional dependencies]

Error Cases
----------

The command will fail with an error message in the following cases:

* Invalid application name
* Missing --products option
* Application configuration errors

Example Error Messages
---------------------

* When --products is missing:
  ::

    ERROR: The --products option is required

* When an invalid application is specified:
  ::

    CRITICAL: Invalid application configuration
