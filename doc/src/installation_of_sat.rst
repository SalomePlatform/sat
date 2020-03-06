************
Installation
************

**sat** is provided either embedded into a salome package, or as a standalone package. It can also be retrieved from the git repositories.


From git bases
--------------

**sat** git bases are hosted by the `salome platform Tuleap forge <https://codev-tuleap.cea.fr/projects/salome>`_ . Therefore you first have to get an account to this forge.
To get started, one has to download sat, and at last one sat project (usually SAT_SALOME project, which contains all the configuration required to build SALOME and its prerequisites). The following script get sat and SAT_SALOME project from git repos: ::

    # get sat
    BASE_SAT=https://codev-tuleap.cea.fr/plugins/git/spns/SAT.git
    BASE_PROJET=https://codev-tuleap.cea.fr/plugins/git/spns/SAT_SALOME.git
    TAG_SAT=master
    TAG_PROJET=master
    git clone ${BASE_SAT}
    cd SAT
    git checkout ${TAG_SAT}
    cd ..
    
    # get sat project SAT_SALOME 
    git clone ${BASE_PROJET}
    cd  SAT_SALOME
    git checkout ${TAG_PROJET}
    cd ..

    # initialisation de sat 

    # add SAT_SALOME project to sat, other configurations projects can be added
    SAT/sat init --add_project  $(pwd)/SAT_SALOME/salome.pyconf

    # record tag and url (not mandatory)
    SAT/sat init --VCS $BASE_SAT
    SAT/sat init --tag $(git describe --tags)


Embedded sat version
--------------------

**sat** is provided in salome packages with sources, in order to be able to recompile the sources (**sat** is not provided in salome packages with only binaries).

Embedded **sat** is always associated to an embedded **sat**  project, which contains all the products and application configuration necessary to the package.

.. code-block:: bash

    tar -xf SALOME-9.3.0-CO7-SRC.tgz
    cd SALOME-9.3.0-CO7-SRC
    ls PROJECT/   # list the embedded sat project
    salomeTools/sat config SALOME-9.3.0 -e   # edit the SALOME-9.3.0 configuration pyconf file


The user has usually two main use cases with an embedded sat, which are explained in the README file of the archive:

1. recompile the complete application

.. code-block:: bash

    ./sat prepare SALOME-9.3.0
    ./sat compile SALOME-9.3.0
    ./sat launcher SALOME-9.3.0

Please note that the sources are installed in *SOURCES* directory, and the compilation is installed in *INSTALL*  directory (therefore they do not overwrite the initial binaries, which are stored in *BINARIES-XXX* directory). The launcher *salome* is overwritten (it will use the new compiled binaries) but the old binaries can still be used in connection with *binsalome* launcher).

2. recompile only a part of the application

It is possible to recompile only a part of the products (those we need to modify and recompile). To enter this (partial recompilation mode), one has initialy to copy the binaries from *BINARIES-XXX* to *INSTALL*, and do the path substitutions by using the **install_bin.sh** script: 

.. code-block:: bash

    ./install_bin.sh  # pre-installation of all binaries in INSTALL dir, with substitutions
    ./sat prepare SALOME-9.3.0 -p GEOM  # get GEOM sources, modify them
    ./sat compile SALOME-9.3.0 -p GEOM --clean_all  # only recompile GEOM



Standalone sat packages
---------------------------

**sat** is also delivered as a standalone package, usually associated to a sat project. The following example is an archive containing salomeTools 5.3.0 and the salome sat project. It can be used to build from scratch any salome application.

.. code-block:: bash

    # untar a standalone sat package, with a salome project
    tar xf salomeTools_5.3.0_satproject_salome.tgz
    cd salomeTools_5.3.0_satproject_salome
    ls projects  # list embedded sat projects
    > salome
    ./sat config -l  # list all salome applications available for build


Finally, the project also provides bash scripts that get a tagged version of sat from the git repository, and a tagged version of salome projects. This mode is dedicated to the developpers, and requires an access to the Tuleap git repositories. 
