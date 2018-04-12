
.. include:: ../../rst_prolog.rst

Command package
****************

Description
============
The **package** command creates a SALOME_ archive (usually a compressed Tar_ file .tgz).
This tar file is used later to intall SALOME on other remote computer.

Depending on the selected options, the created archive includes sources and binaries
of SALOME products and prerequisites.

Utility *salomeTools* is also included in the archive.

.. note::
  By default the package only includes the sources of the prerequisites and the products.
  To select a subset use the *--content* option.
   

Usage
=====
* Create a package for a product (example as *SALOME_xx*): ::

    sat package SALOME_xx
    
  This command will create an archive named ``SALOME_xx.tgz`` in the working directory (``$USER.workDir``).
  If the archive already exists, do nothing.

* Create a package with a specific name: ::

    sat package SALOME_xx --name YourSpecificName

.. note::
    By default, the archive is created in the working directory of the user (``$USER.workDir``).
    If the option *name* is used with a path (relative or absolute) it will be used.
    If the option *name* is not used and binaries (modules or prerequisites) are
    included in the package, the OS_ architecture (ex: *MD10_64*) 
    will be appended to the name.
    
    Examples: ::
    
        # Creates SALOME_xx.tgz in $USER.workDir
        sat package SALOME_xx
        
        # Creates SALOME_xx_<arch>.tgz in $USER.workDir
        sat package SALOME_xx --binaries
        
        # Creates MySpecificName.tgz in $USER.workDir
        sat package SALOME_xx --name MySpecificName
        

* Force the creation of the archive (if it already exists): ::

    sat package SALOME_xx  --force

* Include the binaries in the archive (products and prerequisites): ::

    sat package SALOME_xx --binaries
    
  This command will create an archive named ``SALOME_xx _<arch>.tgz`` 
  where <arch> is the OS_ architecture of the machine.

* Set content of the archive: ::

    # only the prerequisites
    sat package <product> --content ps,pb
    # only the modules sources
    sat package <product> --content ms
    # only the binaries
    sat package <product> --content mb,pb


  Possible values for content option are:
    * ms: modules sources
    * mb: modules binaries
    * ps: prerequisites sources
    * pb: prerequisites binaries

  .. note:: this option is not compatible with the *--binaries* option.


* Simulate the creation of the package (only check for required components): ::

    sat package <product> --simulate

* Do not include *sample* modules (like HELLO): ::

    sat package <product> --no_sample

  Sample modules are identified by the ``$TOOLS.common.module_info.<module_name>.module_type`` parameter.

  By default salomeTools creates a copy of the installer with the same name than
  the package. Use this option to not generate the installer.

* Do not delete version control system informations from the configurations files of the embedded salomeTools: ::

    sat package <product> --with_vcs

  The version control systems (vcs) taken into account by this option are CVS, SVN and Git.

Configuration
=============
No specific configuration.
