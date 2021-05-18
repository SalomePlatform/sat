*****************
SAT version 5.8.0
*****************

Release Notes, May 2021
============================


New features and improvements
-----------------------------


**New key git_options**

This new key was introduced in order to be able to use specific *git clone* options when getting sources with sat. 
This was motivated by paraview, which sometimes requires the option --recursive.
This git_options key should be added in the git_info section of the product: ::

    git_info:
    {
        repo : "https://gitlab.kitware.com/paraview/paraview-superbuild"
        repo_dev : $repo
        git_options: ' --recursive '
    }



**Completion of system_info section with system specifics**

This development allows defining more precisely the system prerequisites that are required (the name of some packages change from one linux distribution to the other,
with this development it is now possible to specialise system prerequisites for each distribution).
In addition a new product called *salome_system* was added, which includes all *implicit* system prerequisites (prerequisites that are not specifically managed by
sat, and that should be installed on the user machine).
The command *sat config --check_system* is now quite exhaustive. 
The syntax of this new section is: ::

    system_info : 
    {
        rpm : ["dbus-libs", "gmp", ...  "zlib"]
        rpm_dev : ["openssl-devel", "tbb-devel", ... "libXft-devel"]
        apt : ["libbsd0", ...   "zlib1g"]
        apt_dev : ["libssl-dev", "gcc", ...]

        # specific to some plateform(s)
        "CO7" :
        {
            rpm_dev : ["perl"]
        }
        "CO8-FD30-FD32" :
        {
            rpm_dev : ["perl-interpreter"]
        }
    }



Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #24027  | Print a warning for users executing .sh environment scripts outside bash (zsh,...)|
+-------------+-----------------------------------------------------------------------------------+
| spns #20662 | For sat compile --update : do not change the date of source directory for tags    |
|             | (only for branches)                                                               |
+-------------+-----------------------------------------------------------------------------------+
| sat #18868  | Implement the recompilation of archives produced with BASE mode                   |
+-------------+-----------------------------------------------------------------------------------+
| sat #18867  | Implement the recompilation of an archive produced with git links                 |
|             | --with_vcs)                                                                       |
+-------------+-----------------------------------------------------------------------------------+
| sat #20601  | bug fix the case where the the name of a product differ from the pyconf name      |
+-------------+-----------------------------------------------------------------------------------+
| sat #20061  | Use a new optimized algorithm for the calculation of dependencies (much faster)   |
+-------------+-----------------------------------------------------------------------------------+
| sat #20089  | bug fix for python 2.6                                                            |
+-------------+-----------------------------------------------------------------------------------+
| sat #20490  | suppress false positive return of sat prepare if tag doesn't exist                |
+-------------+-----------------------------------------------------------------------------------+
| sat #20391  | Update Exception API message method to conform with python3                       |
+-------------+-----------------------------------------------------------------------------------+
| sat #20460  | debug sat config --check_system on debian system                                  |
+-------------+-----------------------------------------------------------------------------------+
