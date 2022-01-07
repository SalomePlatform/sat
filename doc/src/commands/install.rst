
.. include:: ../../rst_prolog.rst

Command install
***************

Description
===========
The **install** command gets the binaries of the application products from local (ARCHIVEPATH) or ftp server.


Usage
=====
* Create a binary installation of SALOME which only contains SALOME,GEOM and SMESH modules, plus their dependencies: ::

    sat install SALOME-master --products SALOME,GEOM,SMESH
