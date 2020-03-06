.. include:: ../../rst_prolog.rst

Command init
************

Description
===========
The **init** command manages the sat local configuration (which is stored in the data/local.pyconf file).
It allows to initialise the content of this file.

Usage
=====
* A sat project provides all the pyconf files relative to a project (salome for example). Use the *--add_project* command to add a sat project locally, in data/local.pyconf (by default sat comes without any project). It is possible to add  as many projects as required. ::

    sat init --add_project <path/to/a/sat/project/project.pyconf>


* If you need to remove a sat project from the local configuration, use the *--reset_projects* command to remove all projects and then add the next ones with *--add_project*: ::
  
    sat init --reset_projects
    sat init --add_project <path/to/a/new/sat/project/project.pyconf>

* By default the product archives are stored locally within the directory containing salomeTool, in a subdirectory called ARCHIVES. If you want to change the default, use the *--archive_dir* option: ::

    sat init --archive_dir  <local/path/where/to/store/product/archives>

* sat enables a **base** mode, which allows to mutualize product builds between several applications. By default, the mutualized builds are stored locally within the directory containing salomeTool, in a subdirectory called BASE. To change the default, use the *--base* option: ::
  
    sat init --base <local/path/where/to/store/product/mutualised/product/builds>

* In the same way, you can use the *--workdir* and *--log_dir* commands to change the default directories used to store the application builds, and sat logs: ::
  
    sat init --workdir <local/path/where/to/store/applications>
    sat init --log_dir <local/path/where/to/store/sat/logs>



Some useful configuration paths
=================================

All the sat init commands update the local pyconf salomeTool file data/local.pyconf. The same result can be achieved by editing the file directly. 
The content of data/local.pyconf is dumped into two sat configuration variables:

* **LOCAL**: Contains notably all the default paths in the fields archive_dir, base, log_dir and workdir.

* **PROJECTS**: The field project_file_paths contains all the project files that have been included with --add_project option.

sat commands: ::

  sat config -v LOCAL
  sat config -v PROJECTS



