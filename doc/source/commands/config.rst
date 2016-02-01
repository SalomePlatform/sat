******
config
******

Description
===========
The **config** manages sat configuration.

Usage
=====
* List available products: ::
  
    sat config --list

* Copy a product into the user personal directory: ::
  
    sat config <product> --copy [new_name]

* Edit the user configuration file: ::

    sat config --edit

* Edit a product: ::

    sat config <product> --edit

* Get the value of a parameter: ::

    sat config --value <parameter_path>
    sat config --value TOOLS.prepare.cvs_server

    sat config <product> --value <parameter_path>
    sat config SALOME_7_7_1 --value PRODUCT.out_dir


Configuration
=============
* SITE.config

  * **configPath**: list of directories where to find products files.

* USER

  * **editor**: command to use to start an editor (by default vi),
  * **browser**: command to use to start a browser (by default firefox),
  * **pdf_viewer**: command to use to start a pdf viewer (by default evince).
