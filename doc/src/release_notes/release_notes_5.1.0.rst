*****************
SAT version 5.1.0
*****************

Release Notes, June, 2018
=========================

This version of sat was used to produce SALOME 8.5.0

New features and improvements
-----------------------------

**sat compile : management of a verbose and debug option**

The verbose and debug option for cmake products is activated through two new keys introduced in application configuration files : **debug** and **verbose**.
**debug** option will trigger the tranmmission of *-DCMAKE_VERBOSE_MAKEFILE=ON* to cmake, while **verbose** option will transmit *-DCMAKE_VERBOSE_MAKEFILE=ON*.
The new options can be activated for a selected products (within the option dictionnary associated to the products): 

.. code-block:: bash

    # for KERNEL compilation : specify to cmake a debug compilation with verbosity
    KERNEL : {tag : "V7_8_0", base : "yes", debug : "yes", verbose : "yes"}

These two options can also be activated globally, for all products, through golbal keys:

.. code-block:: bash

    specify to cmake a debug compilation with verbosity for all products
    APPLICATION :
    {
        name : 'SALOME-master'
        workdir : $LOCAL.workdir + $VARS.sep + $APPLICATION.name + '-' + $VARS.dist
        tag : 'master'
        verbose :'yes'
        debug : 'yes'
        ...
    }

**Implementation of salome test functionality with sat launcher**

**sat** launcher is now able to launch salome tests (before the development, only virtual applications where able to launch salome tests).
SALOME module was adapted to hold the tests (through links to SALOME module test directories).
Notably, the results and logs of the test are stored in *INSTALL/SALOME/bin/salome/test*.

.. code-block:: bash

    # display help for salome test command
    salome test -h

    # show available tests (without running them)
    salome test -N

    # run tests
    salome test


Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #8908   | sat compile : management of a verbose and debug options                           |
+-------------+-----------------------------------------------------------------------------------+
| sat #8560   | Define handles set_env_build and set_env_launch to be able to specialise env      |
+-------------+-----------------------------------------------------------------------------------+
| sat #8638   | Improve information printed by --show option of sat compile                       |
+-------------+-----------------------------------------------------------------------------------+
| sat #8911   | Implementation of salome test with sat launcher in connection with SALOME module  |
+-------------+-----------------------------------------------------------------------------------+
| sat #11056  | Generation of new salome launcher with mesa with sat launcher command             |
+-------------+-----------------------------------------------------------------------------------+
| sat #11028  | Use of a new property "configure_dependency" to manage the dependency of all      |
|             | salome modules to CONFIGURATION module                                            |
+-------------+-----------------------------------------------------------------------------------+
| sat #10569  | Debug and improvement of products filters in sat commands                         |
+-------------+-----------------------------------------------------------------------------------+
| sat #8576   | Improve if messages displayed by sat compile command                              |
| sat #8646   | Improve management of errors                                                      |
| sat #8605   |                                                                                   |
| sat #8646   |                                                                                   |
| sat #8576   |                                                                                   |
+-------------+-----------------------------------------------------------------------------------+
