
.. include:: ../rst_prolog.rst

*********
Using SAT
*********

Getting started
===============

SAT is a Command Line Interface (CLI_) based on python language.
Its purpose is to cover the maintenance and the production of an application which has to run on several platforms and depends upon a lot of prerequisites.
It is most of the time used interactively from a terminal, but there is also a batch mode that can be used for example in automatic procedures (like jenkins jobs). 
SAT is used in command line by invoking after its name a sat option (which is non mandatory), then a command name, followed by the arguments of the command (most of the time the name of an application and command options):

.. code-block:: bash

    ./sat [generic_options] [command] [application] [command_options]


The main sat options are:

* **-h** : to invoke the **help** and get the list of available options and commands
* **-o** : to **overwrite** at runtime a configuration parameter or option
* **-v** : to change the **verbosity** (default is 3, minimum 0 and maximum 6)
* **-b** : to enter the **batch** mode and avoid any question (this non interactive mode is useful for automatic procedures like jenkins jobs)
* **-t** : to display the compilation logs in the **terminal** (otherwise they are logged in files and displayed by the log command
   
The main sat commands are:

* **prepare** : to get the sources of the application products (from git repositories or archives) and apply patches if there are any
* **compile** : to build the application (using cmake, automake or shell script)
* **launcher** : to generate a launcher of the application (in the most general case the launcher sets up the run-time environment and starts an exe)
* **package** : to build a package of the application (binary and/or source)
* **config** : to display the configuration
* **log** : to display within a web browser the logs of SAT


Getting help
============

Help option -h
--------------

More details are provided by the help of sat. The help option can be called at two levels : the high level displays information on how to use sat, the command level displays information on how to use a sat command.

.. code-block:: bash

    # display sat help
    ./sat -h

    # display the help of the compile command
    ./sat compile -h

Completion mode
---------------

When getting started with sat, the use of the completion mode is convenient. This mode will display by typing twice on the **tab key** the available options, commands, applications or products available. The completion mode has to be activated by sourcing the file **complete_sat.sh** contained in SAT directory:

.. code-block:: bash

    # activate the completion mode
    source complete_sat.sh      

    # list all application available for compilation
    ./sat compile  <TAB> <TAB>
    > SALOME-7.8.2   SALOME-8.5.0   SALOME-9.3.0   SALOME-master

    # list all available options of sat compile 
    ./sat compile SALOME-9.3.0 <TAB> <TAB>
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


All the build is done in the *application directory*, which is parameterized by the sat configuration variable *$APPLICATION.workdir*. In the above example this directory corresponds to *.../SALOME-9.4.0-CO7*.
SAT can only build applications provided by the projects that have been loaded with *sat init* command. The available applications are listed by *sat config -l* command. 


Partial recompilation of a packaged application 
===============================================

Getting all the sources and compile everything is often a long process.
The following use case has proven to be convenient for fast usage!
It consists to get the application through a sat package containing the binaries, the sources and SAT.
This allows using directly the application after the untar (the binary part).
And later, if required, it is possible to add a module, or modify some source code and recompile only what was added or modified.

.. code-block:: bash

    # untar a sat package containing binaries (for CentOS7) and sources
    tar xfz SALOME-9.4.0-CO7-SRC.tar.gz

    # start salome
    SALOME-9.4.0-CO7-SRC/salome

    # copy binaries in INSTALL directory, do required substitutions to enable recompilation
    ./install_bin.sh

    # get sources of modules we want to recompile
    salomeTools/sat prepare SALOME-9.4.0 -p SHAPER,SMESH
    
    # do some modifications and recompile both modules
    salomeTools/sat compile SALOME-9.4.0 -p SHAPER,SMESH  --clean_all

This use case is documented in the README file of the package

Using SAT bases
===============

Users or developers that have to build several applications, which share common products, may want to mutualise the compilation of the common products.
The notion of SAT base follows this objective. It allows sharing the installation of products between several applications, and therefore compile these products only once.

Location
--------

By default the SAT base is located in the parent directory of sat (the directory containing sat directory) and is called BASE.
This default can be changed by the user with sat init command :

.. code-block:: bash

    # change the location of SAT base directory
    ./sat init -b <new base path>

Which products go into the base
-------------------------------

The application developer has the possibility to declare that a product will go by default in the base.
He uses for that the keyword 'base' in the install_dir key within the product configuration file (products pyconf) : *install_dir : 'base'*
It is done usually for products that are considered as prerequisites.

At this stage, all products with install_dir set to 'base' will be installed in SAT base directory.


Application configuration
-------------------------

The default behavior of products can be modified in the application configuration, with the **base** flag.
Like other application flags (debug, verbose, dev) the **base** flag can be used for a selection of products, or globally for all products.

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

Products that go in base and have the same configuration will be shared by different applications (it's the objective).
SAT does check the configuration to prevent of an application using a product in base with a non compatible configuration. 
To check the compatibility, SAT stores the configuration in a file called *sat-config-<product name>.pyconf*.
In a next build (for example in another application), SAT checks if the new configuration corresponds to what is described in *sat-config-<product name>.pyconf*.
If it corresponds, the previous build is used in base, otherwise a new build is done, and stored in a new directory called *config-<build number>*.

.. warning:: Please note that only the dependencies between products are considered for the checking. If the compilation options changed, it will not be tracked (for example the use of debug mode with -g option will not produce a second configuration, it will overwrite the previous build done in production mode)


Developing a module with SAT
============================

SAT has some features that make developers' life easier. Let's highlight some of the developers use cases.
(if you are not familiar with SAT configuration, you may first read Configuration Chapter before, and come back to this paragraph after)

Activating the development mode
-------------------------------

By default *sat prepare* command is not suited for development, because it erases the source directory (if it already exists) before getting the sources.
If you did developments in this directory **they will be lost!**.

Therefore before you start some developments inside a product, you should **declare the product in development mode** in the application configuration.  
For example if you plan to modify KERNEL module, modify SALOME configuration like this:

.. code-block:: bash

    APPLICATION :
    {
    ...
        products :
        {
        # declare KERNEL in development mode (and also compile it
        # with debug and verbose options)
        'KERNEL' : {dev:'yes', debug:'yes', verbose:'yes', tag:'my_dev_branch', section:'version_7_8_0_to_8_4_0'}
        ...
        }
    }

When the dev mode is activated, SAT will load the sources from the git repository only the first time, when the local directory does not exist.
For the next calls to *sat prepare*, it will keep the source intact and do nothing!

In the example we have also set the debug and the verbose flags to "yes" - it is often useful when developing.

Finally, we have changed the tag and replaced it with a development branch (to be able to push developments directly in git repo - without producing patches).

.. warning:: But doing this we have (probably) broken the automatic association done by SAT between the tag of the product and the product section used by SAT to compile it!  (see the chapter "Product sections" in the Configuration documentation for more details about this association) Therefore you need to tell SAT which section to use (otherwise it will take the "default" section, and it may not be the one you need).  This is done with : **section:'version_7_8_0_to_8_4_0'**. If you don't know which section should be used, print it with SAT config before changing the tag : *./sat config SALOME-9.4.0 -i KERNEL* will tell you which section is being used.

Pushing developments in base, or creating patches
-------------------------------------------------

If you have set the tag to a development branch (like in the previous example), you can directly push your developments in the git repository with *git push* command.
If not (if you are detached to a tag, you can produce with git a patch of you developments:

    git diff > my_dev.patch

And use this patch either with SAT to apply it automatically with *sat prepare* command, or send the patch for an integration request.


Changing the source directory
-----------------------------

By default the source directory of a product is located inside SAT installation, in the SOURCES directory.
This default may not be convenient. Developers may prefer to develop inside the HOME directory (for example when this directory is automatically saved).

To change the default source directory, you first have to identify which product section is used by SAT: ::

    ./sat config SALOME-9.4.0 -i KERNEL
    >  ....
    >  section = default

Then you can change the source directory in the section being used (default in the example above).
For that you can modify the **source_dir** field in the file *SAT_SALOME/products/KERNEL.pyconf*.
Or change it in command line: **./sat -o "PRODUCTS.KERNEL.default.source_dir='/home/KERNEL'"  <your sat command>**.
For example the following command recompiles KERNEL using */home/KERNEL* as source directory: ::

    # take KERNEL sources in /home/KERNEL
    ./sat -o "PRODUCTS.KERNEL.default.source_dir='/home/KERNEL'" compile SALOME-master -p KERNEL --clean_all

Displaying compilation logs in the terminal
-------------------------------------------
When developing a module you often have to compile it, and correct errors that occurs.
In this case, using *sat log*  command to consult the compilation logs is not convenient!
It is advised to use in this case the **-t** option of sat, it will display the logs directly inside the terminal: ::

    # sat -t option put the compilation logs in the terminal
    ./sat -t -o "PRODUCTS.KERNEL.default.source_dir='/home/KERNEL'" compile SALOME-master -p KERNEL --clean_all


