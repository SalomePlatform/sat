
.. include:: ../rst_prolog.rst

*********
Using SAT
*********

Getting started
===============

sat is a Command Line Interface (CLI_) based on python langage.
Its purpose is to cover the maintenance and the production of an application which run on several platforms and depend upon a lot of prerequisites.
It is most of the time used interactively from a terminal, but there is also a batch mode that can be used for example in automatic procedures (like jenkins jobs). 
sat is used in command line by invoking after its name a sat option (which is non mandatory), then a command name, followed by the arguments of the command (most of the time the name of an application and command options):

.. code-block:: bash

    ./sat [generic_options] [command] [application] [command_options]


The main sat options are:

* **-h** : to get the list of available options and commands
* **-o** : to overwrite at runtime a configuration parameter or option
* **-v** : to change the verbosity (default is 3, minimum 0 and maximum 6)
* **-b** : to enter the batch mode and avoid any question (this non interactive mode is useful for automatic procedures like jenkins jobs)
* **-t** : to display the compilation logs in the terminal (otherwise they are logged in files and displayed by the log command
   
The main sat commands are:

* **prepare** : to get the sources of the application products (from git repositories or archives) and apply patches if there are any
* **compile** : to build the application (using cmake, automake or shell script)
* **launcher** : to generate a launcher of the application (in the most general case the launcher sets up the run-time environment and start an exe)
* **package** : to build a package of the application (binary and/or source)
* **config** : to display the configuration
* **log** : to display within a web browser the logs of the commands


Getting help
============

Help option -h
--------------

More details are provided by the help of sat. The help option can ba calle at two levels : the (high) level displays information on how to use sat, the command level displays information on how to use a sat command.

.. code-block:: bash

    # display sat help
    ./sat -h

    # display the help of the compile command
    ./sat compile -h

Completion mode
---------------

When getting started with sat, the use of the competion mode is convenient. This mode will display by typing twice on the **tab key** the available options, command, applications or product available. The completion mode has to be activated by sourcing the file **complete_sat.sh** contained in SAT directory:

.. code-block:: bash

    source complete_sat.sh      # activate the completion mode

    ./sat conpile  <TAB> <TAB>  # liste all application available for compilation
    > SALOME-7.8.2   SALOME-8.5.0   SALOME-9.3.0   SALOME-master

    ./sat conpile SALOME-9.3.0 <TAB> <TAB>  # list all available options 
    > --check              --clean_build_after  --install_flags      --properties
    > --stop_first_fail    --with_fathers       --clean_all          --clean_make
    > --products           --show               --with_children



Build from scratch an application
=================================

This is the main use case : build from scratch an application.

.. code-block:: bash

    # get the list of available applications in your context
    # the result depends upon the projects that have been loaded in sat.
    ./sat config -l
    >  ...
    >  SALOME-8.5.0
    >  SALOME-9.3.0
    >  SALOME-9.4.0
    
    # get all sources of SALOME-9.4.0 application
    ./sat prepare SALOME-9.4.0

    # compile all products (prerequisites and modules of SALOME-9.4.0)
    ./sat compile SALOME-9.4.0

    # if a compilation error occured, you can access the compilation logs with:
    ./sat log SALOME-9.4.0

    # create a SALOME launcher, displays its path.
    ./sat launcher SALOME-9.4.0
    > Generating launcher for SALOME-9.4.0 :
    >   .../SALOME-9.4.0-CO7/salome

    # start salome platform
    .../SALOME-9.4.0-CO7/salome

    # create a binary package to install salome on other computers
    ./sat package SALOME-9.4.0 -b


All the build is done in the *application directory*, which is parameted by the sat configuration variable *$APPLICATION.workdir*. In the above example t corresponds to *.../SALOME-9.4.0-CO7*.
**sat** can only build application provided by the projects that have been loaded in sat with *sat init* command. These available applications are lister by *sat config -l* command. 


Partial recompilation of a packaged application 
===============================================

Getting all the sources and compile everything is a long process.
The following use case has proven to be convenient for fast usage.
It consists to get the application through a sat package containing the binaries and sat.
This allows using directly the application (the binary part). 
And later, if required, it is possible to add a module, or modify and recompile one.

.. code-block:: bash

    # untar a sat package containing binaries (for CentOS7) and sources
    tar xfz SALOME-9.4.0-CO7-SRC.tar.gz

    # start salome
    SALOME-9.4.0-CO7-SRC/salome

    # copy binaries in INSTALL directory, do required substitution to enable recompilation
    ./install_bin.sh

    # get sources of module we want to recompile
    salomeTools/sat prepare SALOME-9.4.0 -p SHAPER,SMESH
    
    # do some modifications and recompile both modules
    salomeTools/sat compile SALOME-9.4.0 -p SHAPER,SMESH  --clean_all

This use case is documented in the README file of the package

Using SAT bases
===============

Users or developers that have to build several applications, which share common products, may want to mutualise the compilation of the common products.
The notion of SAT base follow this obective. It allows sharing the installation of products between several applications.

Location
--------

By default the SAT base is located in the parent directory of sat (the directory containing sat directory) and is called BASE.
This default can be changed by the user with sat init command :

.. code-block:: bash

    # change the location of SAT base directory
    ./sat init -b <new base path>

Which products go into the base
-------------------------------

The application developper has the possibility to declare that a products will go by default in the base.
He uses for that the keyword 'base' in the install_dir key within the product configuration file (products pyconf) : *install_dir : 'base'*
It is done usually fir products that are considered as prerequisites.

At this stage, all products with install_dir set to 'base' will be installed in SAT base directory.


Application configuration
-------------------------

The default behaviour of products can be modified in the application configuration, with the base flag.
Like other application flags (debug, verbose, dev) the base flag can be used for a selection of products, or globally for all products.

.. code-block:: bash

    # declare in application configuration that SMESH and YACS are installed in base
    products :
    {
    ...
    SMESH : {base : "yes"}
    YACS : {base : "yes"}
    ...
    }

    # declare with a global application flag that all products are installed in base
    base : "yes"


Mutualisation of products
-------------------------

Products that go in base and have the same configuration will be shared by different application (it's the objective).
SAT does check the configuration to prevent of an application using a product in base with a non compatible configuration. 
To check the compatibility, SAT stores in a file *sat-config-<product name>.pyconf* the configuration.
In a next build (for example in an other application), SAT checks if the new configuration corresponds to what is described in *sat-config-<product name>.pyconf*.
If it corresponds, the previous build is used in base, otherwise a new build is done, and stored in a new directory called *config-<build number>*.

.. warning:: Please note that only the dependencies between products are considered for the checking. If the compilation options changed, it will not be tracked (for example the use of debug mode with -g option will not produce a second configuraion, it will overwrite the previous build done in production mode)


