
.. include:: ../../rst_prolog.rst

Command generate
****************

Description
===========
The **generate** command generates and compile SALOME modules from cpp modules using YACSGEN.

.. note:: This command uses YACSGEN to generate the module. It needs to be specified with *--yacsgen* option, or defined in the product or by the environment variable ``$YACSGEN_ROOT_DIR``.


Remarks
=======
* This command will only apply on the CPP modules of the application, those who have both properties: ::

        cpp : "yes"
        generate : "yes"

* The cpp module are usually computational components, and the generated module brings the CORBA layer which allows distributing the compononent on remore machines. cpp modules should conform to YACSGEN/hxx2salome requirements (please refer to YACSGEN documentation)


Usage
=====
* Generate all the modules of a product: ::

    sat generate <application>

* Generate only specific modules: ::

    sat generate <application> --products <list_of_products>

  Remark: modules which don't have the *generate* property are ignored.

* Use a specific version of YACSGEN: ::

    sat generate <application> --yacsgen <path_to_yacsgen>

