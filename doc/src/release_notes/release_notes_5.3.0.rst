*****************
SAT version 5.3.0
*****************

Release Notes, February, 2019
=============================

New features and improvments
----------------------------

**sat init**

The command *sat init* has been finalized, with the addition of options **--add_project** and **--reset_projects**. 
It is now able to manage projects after an initial git clone of sat. The capacity is used by users
installing sat from the git repositories:

.. code-block:: bash

    # get sources of sat
    git clone https://codev-tuleap.cea.fr/plugins/git/spns/SAT.git sat

    # get SAT_SALOME project (the sat project that contains the configuration of SALOME) 
    git clone https://codev-tuleap.cea.fr/plugins/git/spns/SAT_SALOME.git

    # initialise sat with this project
    sat init --add_project $(pwd)/SAT_SALOME/salome.pyconf 

It is possible to initialise sat with several projects by calling several times *sat init --add_project*

**sat prepare : git retry functionality**

With large git repositories (>1GB) *git clone* command may fail. To decrease the risk, sat prepare will now retry 
three times the *git clone* function in case of failure.

**Reset of LD_LIBRARY_PATH and PYTHONPATH  before setting the environment**

Every year, a lot of problems occur, due to users (bad) environment. This is most of the time caused
by the presence (out-of-date) .bashrc files.
To prevent these (time-consuming) problems, sat now reset LD_LIBRARY_PATH and PYTHONPATH variables
before setting the environment thus avoiding side effects.
Users who wish anayway to start SALOME with a non empty LD_LIBRARY_PATH or PYTHONPATH may comment 
the reset in salome launcher or in env_launch.sh file.

**New option --complete for sat prepare**

This option is used when an installation is interrupted or incomplete. It allows downloading only
the sources of missing products

.. code-block:: bash

    # only get sources of missing products (i.e products not present in INSTALL dir)
    git prepare SALOME-master -c

** New option --packages for sat clean**

SALOME packages are big... It is usefull to be able to clean them whith this new option.

.. code-block:: bash

    # remove packages present in PACKAGES directory of SALOME-master
    git clean SALOME-master --packages

**Global configuration keys "debug", "verbose" and "dev" in applications**


These new keys can be defined in applications in order to trigger the debug, verbose and dev mode for all products.
In the following example, the SALOME-master application will be compiled in debug mode (use of **-g** flag), but with no verbosity.
Its products are not in development mode.

.. code-block:: bash

    APPLICATION :
    {
        name : 'SALOME-master'
        workdir : $LOCAL.workdir + $VARS.sep + $APPLICATION.name + '-' + $VARS.dist
        tag : 'master'
        dev : 'no'
        verbose :'no'
        debug : 'yes'
        ...
    }

Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+------------+-----------------------------------------------------------------------------------+
| Artifact   | Description                                                                       |
+============+===================================================================================+
| sat #16548 | Finalisation of sat init command (options -add_project and --reset_projects)      |
| sat #8566  |                                                                                   |
+------------+-----------------------------------------------------------------------------------+
| sat #12994 | new git retry functionality for sat prepare : give three trials in case of        |
|            | failures                                                                          |
+------------+-----------------------------------------------------------------------------------+
| sat #8581  | traceability : save tag of sat and its projects                                   |
+------------+-----------------------------------------------------------------------------------+
| sat #8588  | reset LD_LIBRARY_PATH and PYTHONPATH before launching SALOME                      |
+------------+-----------------------------------------------------------------------------------+
| sat #9575  | Improvement of the DISTENE licences management (notably for packages)             |
+------------+-----------------------------------------------------------------------------------+
| sat #8597  | Implementation of option sat prepare -c (--complete) for preparing only the       |
|            | sources that are not yet installed                                                |
+------------+-----------------------------------------------------------------------------------+
| sat #8655  | implementation of option sat clean --packages                                     |
+------------+-----------------------------------------------------------------------------------+
| sat #8532  | sat log : rename option --last_terminal in --last_compile                         |
| sat #8594  | Extension of sat log --last_compile to the logs of make check                     |
+------------+-----------------------------------------------------------------------------------+
| sat #13271 | hpc mode triggered by product "hpc" key in state of MPI_ROOT variable             |
|            |                                                                                   |
+------------+-----------------------------------------------------------------------------------+
| sat #8606  | sat generate clean old directories before a new generation                        |
+------------+-----------------------------------------------------------------------------------+
| sat #12952 | Add global keys "debug", "verbose" and "dev" to manage globally these modes       |
|            | for all the products of an application                                            |
+------------+-----------------------------------------------------------------------------------+
| sat #8523  | protection of call to ssh on windows platform                                     |
+------------+-----------------------------------------------------------------------------------+
