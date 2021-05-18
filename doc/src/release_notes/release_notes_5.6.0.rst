*****************
SAT version 5.6.0
*****************

Release Notes, July 2020
========================


New features and improvements
-----------------------------


**Checking of system dependencies**

SALOME depends upon some system prerequisites. Recent examples are tbb and openssl. For these products SALOME made the choice not to embed the prerequisite, but
to rely on the system version. 
SAT has now the capacity to check for the system dependencies in two ways:

* **sat prepare** command will return an error if system prerequisites are not installed.
* **sat config** has now an option **--check_system** that list all the system prerequisites with their status.

**Removing build dependencies from binary archives**

SALOME archive are getting fat. In order to reduce the size of binary archives, the management by sat of the build prerequisites was modified.
build prerequisites declared with the property **compile_time : "yes"** are not included anymore in binary archives.

**New option -f --force for sat compile**

This option can be used to **force** the recompilation of products.
It is an alternative to --clean_all, which do not work properly with the single_dir mode
(it will erase the complete PRODUCTS directory, which is usually not expected!

Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #18501  | bad management of rm_products functionality in archives                           |
+-------------+-----------------------------------------------------------------------------------+
| sat #18546  | for products installed in BASE, replace in directory name / by _ to avoid the     |
|             | creation if a directory                                                           |
+-------------+-----------------------------------------------------------------------------------+
| sat #19109  | more robust choice of the package manager to check system dependencies            |
+-------------+-----------------------------------------------------------------------------------+
| sat #18720  | add option --use-mesa in automatic completion                                     |
+-------------+-----------------------------------------------------------------------------------+
| sat #19192  | don't remove PRODUCTS dir when compilation fails                                  |
+-------------+-----------------------------------------------------------------------------------+
| sat #19234  | remove build products from bin archives, better management of their environment   |
+-------------+-----------------------------------------------------------------------------------+
| sat #19218  | correct out_dir_Path substitution for appended variables                          |
+-------------+-----------------------------------------------------------------------------------+
| sat #18350  | -f option for sat compile : force the recompilation                               |
+-------------+-----------------------------------------------------------------------------------+
| sat #18831  | sat compile --clean_all : do all the cleaning, then compile                       |
|             | (bug correction with single_dir mode)                                             |
+-------------+-----------------------------------------------------------------------------------+
| sat #18653  | replace platform.linux_distribution by distro.linux_distribution for python 3.8+  |
+-------------+-----------------------------------------------------------------------------------+
