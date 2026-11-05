
.. include:: ../../rst_prolog.rst

Command package
****************

Description
============
The **package** command creates a SALOME archive (usually a compressed Tar_ file .tgz).
This tar file is used later to install SALOME on other remote computer.

Depending on the selected options, the archive includes sources and binaries
of SALOME products and prerequisites.

Usually utility *sat* is included in the archive.

.. note::
  By default the package includes the sources of prerequisites and products.
  To select a subset, use the *--without_property* or *--with_vcs* options.
   

Usage
=====
* Create a package for a product (example as *SALOME-master*): ::

    sat package SALOME-master
    
  This command will create an archive named ``SALOME-master.tar.gz`` 
  in the working directory (``USER.workDir``).
  If the archive already exists, do nothing.


* Create a package with a specific name: ::

    sat package SALOME-master --name YourSpecificName

.. note::
    By default, the archive is created in the working directory of the user (``USER.workDir``).
    
    If the option *--name* is used with a path (relative or absolute) it will be used.
    
    If the option *--name* is not used and binaries (prerequisites and products) 
    are included in the package, the OS_ architecture
    will be appended to the name (example: ``SALOME-master-UB24.04.tar.gz``).
    
    Examples: ::
    
        # Creates SALOME-master.tgz in $USER.workDir
        sat package SALOME-master
        
        # Creates SALOME-master_<arch>.tar.gz in $USER.workDir
        sat package SALOME-master --binaries
        
        # Creates MySpecificName.tar.gz in $USER.workDir
        sat package SALOME-master --name MySpecificName
    
    
* Force the creation of the archive (if it already exists): ::

    sat package SALOME-master --force


* Include the binaries in the archive (products and prerequisites): ::

    sat package SALOME-master --binaries
    
  This command will create an archive named ``SALOME-master _<arch>.tar.gz`` 
  where <arch> is the OS architecture of the machine.


* Create a binary archive with ``extra.env.d`` subdirectory which implements each product environment: ::

    sat package SALOME-master --binaries --with-extra.env.d

    
* Do not delete Version Control System (VCS_) information from the configuration files of the embedded sat: ::

    sat package SALOME-master --with_vcs

  The version control systems known by this option are CVS_, SVN_ and Git_.

* Create binary archives for each product: ::

    # Create binary product archives for all products
    sat package SALOME-master --bin_products

    # Create binary product archives only for VCS products
    sat package SALOME-master --bin_products --with_vcs

Archive formats
===============
The format of the archive is selected with the *--archive* option:

* ``tar`` (default): a compressed Tar_ file ``.tar.gz``;
* ``dmg``: a macOS application bundle (``SALOME.app``) and a disk image (``.dmg``), see below;
* ``msi``: a Windows installer built with WiX from the compiled install tree of the application.

The options of the command are compatible with all the formats, except:

* the msi installer only contains the binaries of the application: *--sources*,
  *--ftp*, *--exe*, *--project*, *--salometools* and *--with-extra.env.d* are not
  compatible with it, *--with_vcs* only when combined with *--bin_products*;
* the options *--bundle_version*, *--bundle_id*, *--icon*, *--slim*, *--no_test*,
  *--sign_adhoc*, *--no_dmg* and *--replace* only apply to the dmg archive.

An incompatible option stops the command with an error.

* Create a binary tar archive (the default format): ::

    sat package SALOME-master --binaries

* Create a dmg archive on macOS, an msi archive on Windows: ::

    sat package SALOME-master-macOS --archive dmg
    sat package SALOME-master-windows --archive msi

dmg archive (macOS)
-------------------
The dmg archive is only available on macOS (Xcode Command Line Tools are required).
It implies *--binaries*. The dmg options (*--icon*, *--slim*...) require *--archive dmg*.

The bundle contains the files of the archive (binaries, launcher, and the sources,
project, salomeTools or additional files when requested): they are copied into
``SALOME.app/Contents/Resources/``. ``Contents/MacOS/SALOME`` runs the relative
salome launcher with the embedded Python.

The binaries are made relocatable on any Mac:

* absolute dependencies outside the system are rewritten to ``@rpath/...``;
* libraries that do not belong to the application (e.g. the gcc runtime:
  ``libgfortran``, ``libquadmath``, ``libgcc_s``) are embedded in
  ``BINARIES-<dist>/_external/lib``;
* absolute ``LC_RPATH`` (the build directory) are removed and replaced by
  ``@loader_path`` relative rpaths;
* absolute symbolic links and absolute shebangs are fixed.

A verification step reports every dependency that does not resolve inside the bundle.

The bundle is not signed: the linker signatures of the binaries are kept and only
the invalid ones are re-signed ad hoc. Use *--sign_adhoc* to sign the whole bundle.
Notarization (Developer ID signature of every binary) is not done by this command.

* Create ``SALOME.app`` and ``SALOME-<version>-<dist>-<arch>.dmg`` in ``<workdir>/PACKAGE``: ::

    sat package SALOME-master-macOS --archive dmg

* With a name, an icon, without the development files: ::

    sat package SALOME-master-macOS --archive dmg --name SALOME --icon salome.png --slim

* From an archive already produced by ``sat package --binaries``: ::

    sat package SALOME-master-macOS --archive /tmp/SALOME-master-MACOS15.tar.gz

* Only the bundle, replacing an existing one: ::

    sat package SALOME-master-macOS --archive dmg --no_dmg --replace

.. note::
   When launched from the Finder, the output of SALOME is written in
   ``~/Library/Logs/<name>/<name>.log``.

   Binaries that cannot be modified (``not enough header space``) must be linked with
   ``-Wl,-headerpad_max_install_names``.

msi archive (Windows)
---------------------
The msi archive is only available on Windows, with WiX Toolset v4 (``wix`` in the ``PATH``,
``dotnet tool install --global wix``). It implies *--binaries*.

The installer is built directly from the compiled install tree of the application
(``APPLICATION.workdir``): the products directory (``W64``) is referenced in the staging
directory, the installer resources of the project are copied next to it, an optional
project script fixes the staging tree, a WiX source is generated (one ``Component`` per
directory, to stay under the 65536 components limit of MSI) and ``wix build`` produces
the ``.msi``.

As in a binary tar archive, the products with the property ``not_in_package`` or
``compile_time`` are not in the installer, and missing product installations stop the
command unless *--force_creation* is given.

* Create ``<APPLICATION.name>-win64.msi`` in ``<workdir>/MSI/build``: ::

    sat package SALOME-master-windows --archive msi

* With a name or a full path, additional files at the root of the installation,
  without the products that have a given property: ::

    sat package SALOME-master-windows --archive msi --name C:\out\SALOME --add_files LICENSE.txt --without_properties is_SALOME_module:yes

Some useful configuration paths
=================================

* **APPLICATION.workdir**: the default output directory is ``<workdir>/PACKAGE``.
* **APPLICATION.profile.launcher_name**: the name of the launcher run by the dmg bundle.
* **APPLICATION.installer** (or the ``installer`` section of the project): the installer
  resources of the msi archive, provided by the project (for SALOME:
  ``sat_salome/installer/windows``):

  * ``resources_dir``: launchers, scripts, branding and ``.wxs`` files copied in the staging directory;
  * ``wxs_sources``: the WiX sources (``Package.wxs``...), ``generated_wxs`` (default ``w64_files.wxs``);
  * ``wix_arch`` (default ``x64``), ``wix_extensions``, ``guid_namespace``;
  * ``output_name`` (default ``<APPLICATION.name>-win64.msi``), ``staging_dir`` (default ``<workdir>/MSI``);
  * ``pre_build_script``, ``python_in_tree``: the optional staging script and its Python;
  * ``tree``: ``root_install_files``, ``install_dirs``, ``skip_dirs``, ``skip_products``,
    ``product_root`` (default ``W64``), ``product_groups`` (product -> ``ComponentGroup``).
