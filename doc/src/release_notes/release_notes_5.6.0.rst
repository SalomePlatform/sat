*****************
SAT version 5.5.0
*****************

Release Notes, May 2020
=======================


New features and improvements
-----------------------------


**Checking of system dependencies**

SALOME depends upon some system prerequisites. Recent examples are tbb and openssl. For these products SALOME made the choice not to embedd the prerequisite, but
to rely on the system version. 
SAT has now the capacity to check for the system dependencies in two ways:

* **sat prepare** command will return an error if system prerequisites are not installed.
* **sat config** has now an option **--check_system** that list all the system prerequisites with their status.




Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #18501  | mauvaise gestion de la fonctionnalité rm_products dans les archives               |
+-------------+-----------------------------------------------------------------------------------+
| sat #18546  | pour les produits installés en base, replacement dans le nom du répertoire de /   |
|             | par _ pour éviter la création d'un sous répertoire                                |
+-------------+-----------------------------------------------------------------------------------+
|             |                                                                                   |
+-------------+-----------------------------------------------------------------------------------+
