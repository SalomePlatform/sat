
.. include:: ../../rst_prolog.rst

Command package
****************

Description
============
The **package** command creates a SALOME archive (usually a compressed Tar_ file .tgz).
This tar file is used later to install SALOME on other remote computer.

Depending on the selected options, the archive includes sources and binaries
of SALOME products and prerequisites.

Usually utility *salomeTools* is included in the archive.

.. note::
  By default the package includes the sources of prerequisites and products.
  To select a subset, use the *--without_property* or *--with_vcs* options.
   

Usage
=====
* Create a package for a product (example as *SALOME_xx*): ::

    sat package SALOME_xx
    
  This command will create an archive named ``SALOME_xx.tgz`` 
  in the working directory (``USER.workDir``).
  If the archive already exists, do nothing.


* Create a package with a specific name: ::

    sat package SALOME_xx --name YourSpecificName

.. note::
    By default, the archive is created in the working directory of the user (``USER.workDir``).
    
    If the option *--name* is used with a path (relative or absolute) it will be used.
    
    If the option *--name* is not used and binaries (prerequisites and products) 
    are included in the package, the OS_ architecture
    will be appended to the name (example: ``SALOME_xx-CO7.tgz``).
    
    Examples: ::
    
        # Creates SALOME_xx.tgz in $USER.workDir
        sat package SALOME_xx
        
        # Creates SALOME_xx_<arch>.tgz in $USER.workDir
        sat package SALOME_xx --binaries
        
        # Creates MySpecificName.tgz in $USER.workDir
        sat package SALOME_xx --name MySpecificName
    
    
* Force the creation of the archive (if it already exists): ::

    sat package SALOME_xx --force


* Include the binaries in the archive (products and prerequisites): ::

    sat package SALOME_xx --binaries
    
  This command will create an archive named ``SALOME_xx _<arch>.tgz`` 
  where <arch> is the OS architecture of the machine.


* Do not delete Version Control System (VCS_) information from the configuration files of the embedded salomeTools: ::

    sat package SALOME_xx --with_vcs

  The version control systems known by this option are CVS_, SVN_ and Git_.


Some useful configuration paths
=================================

No specific configuration.
