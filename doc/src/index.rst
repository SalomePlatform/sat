
.. include:: ../rst_prolog.rst

.. empty first toctree is used for pdf contents maxdepth, see sphinx/builders/latex/__init__.py, toctrees[0].get('maxdepth')

.. toctree::
   :maxdepth: 2

************
Salome Tools
************

.. image:: images/sat_about.png
   :scale: 100 %
   :align: center

.. warning:: This documentation is under construction.

The **Sa**\ lome\ **T**\ ools (sat) is a suite of commands 
that can be used to perform operations on SALOME_.

For example, sat allows you to compile SALOME's codes 
(prerequisites, products)
create application, run tests, create package, etc.

This utility code is a set of Python_ scripts files.

Find a `pdf version of this documentation <SatPdf_>`_ 


Quick start
===========

.. toctree::
   :maxdepth: 1

   Installation of salomeTools <installation_of_sat>
   Configuration <configuration>
   Usage of salomeTools <usage_of_sat>

List of Commands
================

.. toctree::
   :maxdepth: 1
   
   config <commands/config>
   prepare <commands/prepare>
   compile <commands/compile>
   launcher <commands/launcher>
   application <commands/application>
   log <commands/log>
   environ <commands/environ>
   clean <commands/clean>
   package <commands/package>
   generate <commands/generate>

Developer documentation
=======================
 
.. toctree::
   :maxdepth: 1

   Add a command <write_command>


Code documentation
==================
 
.. toctree::
   :maxdepth: 1

   SAT modules <commands/apidoc/modules.rst>


Release Notes
=============

.. toctree::
   :maxdepth: 1

   Release Notes 5.0.0 <release_notes/release_notes_5.0.0>

