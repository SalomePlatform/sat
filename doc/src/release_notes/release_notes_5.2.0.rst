*****************
SAT version 5.2.0
*****************

Release Notes, December, 2018
=============================

This version of salomeTool was used to produce SALOME 9.2.0

New features and improvments
----------------------------

**Generalisation of --properties option**

Wherever the --product option was available (to select products), an option **--properties** has been implemented, 
to offer a alternative way to select products, based on theur property. For example

.. code-block:: bash

    # get only the sources of SALOME modules, not the prerequisites
    sat prepare SALOME-9.2.0 --properties is_SALOME_module:yes

**Compatibility with python 3**

salomeTool is still meant to run under python2. But it magages now the build of applications runninfg under python3.
It includes:
* the generation of python3 launcher,
* the testing of applications under python 3 (*sat test* command).

**New syntax for the naming of sections in  product pyconf**

The old syntax is still supported for compatibility, but the new one, more explicit, is recommended.

.. code-block:: bash

    # all tags from 8.5.0 to 9.2.1, with variants (8, 8_5_0, 8.5, V8, v8.6, etc)
    _from_8_5_0_to_9_2_1
    {
        ....

**mesa launcher**

When salome is used on a remote machine, the use of openGL 3 is not compatible with X11 forwarding (ssh -X).
This cause segmentation faults when the 3D viewers are used.
For people who have no other choice and need to use ssh (it may be useful for testing SALOME on a client remote machine), 
we provide in the packages a mesa launcher mesa_salome.
It will avoid the segmentation faults, at the price of poor performance : it should only be used in this case!
If performance is required, a solution based on the use of VirtualGL and TurboVNC/x2go would be recommended.
But this requires some configuration of the tools to be done as root.
To activate the production of the mesa launcher, use the application property **mesa_launcher_in_package**:


.. code-block:: bash

    # activate the production of a launcher using mesa library
    properties :
    {
        mesa_launcher_in_package : "yes"
    }


Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #8577   | Add a --properties option everywhere useful (whenever there is a --product option)|
+-------------+-----------------------------------------------------------------------------------+
| sat #8471   | Windows portage necessary to produce SALOME 8.2.0 on Windows                      |
+-------------+-----------------------------------------------------------------------------------+
| sat #13031  | Python 3 compatibility                                                            |
+-------------+-----------------------------------------------------------------------------------+
| sat #8561   | New syntax for sections names in products pyconf files                            |
+-------------+-----------------------------------------------------------------------------------+
| sat #11056  | New application property mesa_launcher_in_package to activate the production      |
|             | of a mesa launcher in the package                                                 |
+-------------+-----------------------------------------------------------------------------------+
