
.. include:: ../rst_prolog.rst

.. empty first toctree is used for pdf contents maxdepth, see sphinx/builders/latex/__init__.py, toctrees[0].get('maxdepth')

.. toctree::
   :maxdepth: 2

.. **********
.. SalomeTool
.. **********


Welcome
=======

**SAT** is a tool that makes it easy to build on various linux platforms and windows large software, which rely on a lot of prerequisites.
It was originally created for the maintenance and the packaging of SALOME platform (its name comes from **Sa**\ lome\ **T**\ ools), its usage is now wider.
The following features should be highlighted:

 * the **definition** of the application content: which products (prerequisites, codes, modules) are necessary and which versions are required
 * the **configuration** of the application : how to get the source of products, how to compile them, which options to use, etc. The configuration can be conditionnaly overwritten, this feature allows application developers taking into account platform specifics.
 * the **preparation** of the complete software: all the required sources with correct versions are retrieved from git/svn/cvs repositories, or from already prepared tarballs.
 * management of **patches** if some are required to compile on specific platforms (portage)
 * management of the **environment** to set up at compile time and at runtime
 * automatic **compilation** of the complete application (the application with all its products).
 * production of a **launcher** that sets up the environment and starts the application
 * management of **tests**: both unit and integration tests are managed
 * **packaging**: creation of binary and/or source packages to distribute the application on various platforms
 * **overwriting** the configuration in command line: it allows users setting easily their own preferences or options
 
SAT uses **python**, and many of its strength come from its power and straightforwardness.
SAT is a Command Line Interface (CLI_) based on python langage. It is a suite of commands, which are detailed later in this documentation.
These commands are used to perform the operations on the application.


Documentation
=============

.. toctree::
   :maxdepth: 2

   Installation of SAT <installation_of_sat>
   Using SAT <usage_of_sat>
   Configuration <configuration>


List of Commands
================

.. toctree::
   :maxdepth: 1
   
   doc <commands/doc>
   config <commands/config>
   prepare <commands/prepare>
   compile <commands/compile>
   launcher <commands/launcher>
   log <commands/log>
   environ <commands/environ>
   clean <commands/clean>
   package <commands/package>
   generate <commands/generate>
   init <commands/init>
   template <commands/template>


Release Notes
=============

.. toctree::
   :maxdepth: 1

   Release Notes 5.5.0 <release_notes/release_notes_5.5.0>
   Release Notes 5.4.0 <release_notes/release_notes_5.4.0>
   Release Notes 5.3.0 <release_notes/release_notes_5.3.0>
   Release Notes 5.2.0 <release_notes/release_notes_5.2.0>
   Release Notes 5.1.0 <release_notes/release_notes_5.1.0>
   Release Notes 5.0.0 <release_notes/release_notes_5.0.0>

