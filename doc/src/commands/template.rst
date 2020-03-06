
.. include:: ../../rst_prolog.rst

Command template
****************

Description
===========
The **template** command generates the sources of a SALOME module out of a template.
SAT provides two templates for SALOME 9 :

* PythonComponent : a complete template for a SALOME module implemented in python (with data model and GUI).
* CppComponent : a template for a SALOME component implemented in C++, with a code coupling API.

Usage
=====
* Create a python SALOME module: ::

    sat template --name <product_name> --template PythonComponent --target <my_directory>
    
  Create in *my_directory* a ready to use SALOME module implemented in python. The generated module can then be adapted to the needs, and pushed in a git repository.

