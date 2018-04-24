
.. include:: ../../rst_prolog.rst

Command prepare
****************

Description
===========
The **prepare** command brings the sources of an application in the *sources 
application directory*, in order to compile them with the compile command.

The sources can be prepared from VCS software (*cvs, svn, git*), an archive or a directory.

.. warning:: When sat prepares a product, it first removes the 
             existing directory, except if the development mode is activated.
             When you are working on a product, you need to declare in 
             the application configuration this product in **dev** mode.

Remarks
=======

VCS bases (git, svn, cvs)
-------------------------

The *prepare* command does not manage authentication on the cvs server.
For example, to prepare modules from a cvs server, you first need to login once.

To avoid typing a password for each product, 
you may use a ssh key with passphrase, or store your password 
(in .cvspass or .gitconfig files).
If you have security concerns, it is also possible to use 
a bash agent and type your password only once.



Dev mode
--------

By default *prepare* uses *export* mode: it creates an image 
of the sources, corresponding to the tag or branch specified, 
without any link to the VCS base. 
To perform a *checkout* (svn, cvs) or a *git clone* (git), 
you need to declare the product in dev mode in your application configuration:
edit the application configuration file (pyconf) and modify the product declaration:

.. code-block:: bash

    sat config <application> -e
    # and edit the product section:
    #   <product> : {tag : "my_tag", dev : "yes", debug : "yes"}

The first time you will execute the *sat prepare* command, 
your module will be downloaded in *checkout* mode 
(inside the SOURCES directory of the application.
Then, you can develop in this repository, and finally push 
them in the base when they are ready.
If you type during the development process by mistake 
a *sat prepare* command, the sources in dev mode will 
not be altered/removed (Unless you use -f option)


Usage
=====
* Prepare the sources of a complete application in SOURCES directory (all products): ::

    sat prepare <application>

* Prepare only some modules: ::

    sat prepare <application>  --products <product1>,<product2> ...

* Use --force to force to prepare the products in development mode 
  (this will remove the sources and do a new clone/checkout): ::

    sat prepare <application> --force

* Use --force_patch to force to apply patch to the products 
  in development mode (otherwise they are not applied): ::

    sat prepare <application> --force_patch


Some useful configuration pathes
=================================

Command *sat prepare* uses the *pyconf file configuration* of each product to know how to get the sources.

.. note:: to verify configuration of a product, and get name of this *pyconf files configuration*

  .. code-block :: bash

     sat config <application> --info <product>


* **get_method**: the method to use to prepare the module, possible values are cvs, git, archive, dir.
* **git_info** : (used if get_method = git) information to prepare sources from git.
* **svn_info** : (used if get_method = svn) information to prepare sources from cvs.
* **cvs_info** : (used if get_method = cvs) information to prepare sources from cvs.
* **archive_info** : (used if get_method = archive) the path to the archive.
* **dir_info** : (used if get_method = dir) the directory with the sources.
