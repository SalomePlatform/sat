
.. include:: ../rst_prolog.rst

********************
Usage of SAlomeTools
********************

Usage
=====
sat usage is a Command Line Interface (CLI_).

.. code-block:: bash

  sat [generic_options] [command] [product] [command_options]
   
Options of sat
--------------

Useful *not exhaustive* generic options of *sat* CLI.

*--help or -h*
...............

Get help as simple text.

.. code-block:: bash

    sat --help          # get the list of existing commands
    sat --help compile  # get the help on a specific command 'compile'


*--debug or -g*
................

Execution in debug mode allows to see more trace and *stack* if an exception is raised.

*--verbose or -v*
..................

Change verbosity level (default is 3).

.. code-block:: bash

    # for product 'SALOME_xx' for example
    # execute compile command in debug mode with trace level 4
    sat -g -v 4 compile SALOME_xx


Build a SALOME product
======================

Get the list of available products
----------------------------------

To get the list of the current available products in your context:

.. code-block:: bash

    sat config --list

Prepare sources of a product
----------------------------

To prepare (get) *all* the sources of a product (*SALOME_xx* for example):

.. code-block:: bash

    sat prepare SALOME_xx

| The sources are usually copied in directories
| *$USER.workDir + SALOME_xx... + SOURCES + $PRODUCT.name*


Compile SALOME
----------------

To compile products:

.. code-block:: bash

    # compile all prerequisites/products
    sat compile SALOME_xx
    
    # compile only 2 products (KERNEL and SAMPLES), if not done yet
    sat compile SALOME_xx --products KERNEL,SAMPLES

    # compile only 2 products, unconditionaly
    sat compile SALOME_xx ---products SAMPLES --clean_all


| The products are usually build in the directories
| *$USER.workDir + SALOME_xx... + BUILD + $PRODUCT.name*
|
| The products are usually installed in the directories
| *$USER.workDir + SALOME_xx... + INSTALL + $PRODUCT.name*


