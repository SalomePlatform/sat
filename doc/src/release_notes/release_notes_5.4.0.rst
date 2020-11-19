*****************
SAT version 9.4.0
*****************

Release Notes, April, 2019
==========================

This version of sat was used to produce SALOME 9.3.0

New features and improvments
----------------------------

**sat package**

The sat package command has been completed and finalised, in order to manage standalone packages of sat, with or without an embedded project.
Options **--ftp** and **--with_vcs** have been added, in order to reduce the size of salome project packages (without these options, the archive of the sat salome project is huge, as it includes all the prerequisites archives.  The **--ftp** option allows pointing directly to salome ftp site, which provides the prerequisites archives. These are therefore not included. With the same approach, **--with_vcs** option specify an archive that points directly to the git bases of SALOME. Sources of SALOME modules are therefore not embedded in the archive, reducing the size.

.. code-block:: bash

    # produce a standalone archive of sat
    sat package -t   

    # produce a HUGE standalone archive of sat with the salome project embedded.
    sat package -t -p salome    

    # produce a small archive with sat and embedded salome project, 
    # with direct links to ftp server and git repos
    sat package -t -p salome --ftp --with_vcs 


**repo_dev property**

This new application property **repo_dev** was introduced to trigger the use of the development git repositories for all the git bases of an application. 
Before, the only way to use the development git repositories was to declare all products in dev mode. This was problematic, for example one had to use 
*--force_patch* option to apply patches, or to use *--force* option to reinstall sources.

The use of the development git repository is now triggered by declaring this new **repo_dev** property in the application. And products are declared in dev mode only if we develop them.

.. code-block:: bash

    # add this section in an application to force the use of the development git bases
    # (from Tuleap)
    properties :
    {
        repo_dev : "yes"
    }

**windows compatibility**

The compatibility to windows platform has been improved. The calls to lsb_release linux command have been replaced by the use of python platform module.
Also the module med has been renamed medfile, and module Homard has been renamed homard_bin, in order to avoid lower/upper case conflicts.


Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+------------+-----------------------------------------------------------------------------------+
| Artifact   | Description                                                                       |
+============+===================================================================================+
| sat #12099 | Add a new field called check_install to verify the correct installation           |
+------------+-----------------------------------------------------------------------------------+
| sat #8607  | Suppression of sat profile command, replaced by sat template command (AppModule)  |
+------------+-----------------------------------------------------------------------------------+
| 69d6a69f43 | Introduction of a new property called repo_dev to trigger the use of the dev git  |
|            | repository.                                                                       |
+------------+-----------------------------------------------------------------------------------+
| scs #13187 | Update of PythonComponent template                                                |
+------------+-----------------------------------------------------------------------------------+
| sat #16728 | Replace call to lsb_release by platform module                                    |
+------------+-----------------------------------------------------------------------------------+
| sat #13318 | command sat package -t -p salome --ftp --with_vcs                                 |
| sat #16713 | debug of sat packages containing sat and embedded projects                        |
+------------+-----------------------------------------------------------------------------------+
| sat #16787 | Rename product med by medfile and Homard by homard_bin                            |
+------------+-----------------------------------------------------------------------------------+
