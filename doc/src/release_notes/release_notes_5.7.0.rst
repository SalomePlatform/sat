*****************
SAT version 5.7.0
*****************

Release Notes, November 2020
============================


New features and improvements
-----------------------------


**New field build_depend used in product configuration files**

In order to improve the setting of the environment at run-time and compile-time, a new field was introduced in the product configuration files : *build_depend*.
This field allows the user to specify which products are required for the build (use the field *build_depend*) , and which one are used at runtime (use the former field *depend*).
If a product is used at both build and runtime it is only declared (like before) in the *depend* field (it is the case for example of graphviz which is used at build-time by doxygen, and at run-time by YACS).

These two fields are used by sat accordingly to the context for the dependencies evaluation.
Here is the example of med prerequisites (medfile.pyconf), which depends at runtime on hdf5 and python, and requires cmake for the compilation: ::

    ...
    depend : ["hdf5", "Python"]
    build_depend : ["cmake"]


**New option --update for sat compile**

The time spent to compile salome and its 60 prerequisites is regularly increasing... and can exceed ten hours on slow computers!
It is therefore problematic and expensive in term of resources to recompile completely salome everyday.
The **--update** option was introduced to allow compiling only the products which source code has changed.
This option is **only implemented for git** (not for svn and cvs).
To use the option, one has to call *sat prepare* before. this call will get new sources, and will allow sat checking if the source code was modified since the last compilation.
The mechanism is based upon git *log -1* command, and the modification of the source directory date accordingly: ::
  
    # update SALOME sources and set the date of the source directories of git 
    # products accordingly: to the last commit
    ./sat prepare <application> --properties  is_SALOME_module:yes

    # only compile products that has to be recompiled.                                             
    sat compile <application> --update

This option can also be mixed with *--proterties* option, to avoid recompiling salome prerequisites: ::


    # only compile SALOME products which source code has changed
    sat compile <application> --update --properties is_SALOME_module:yes


**sat do not reinitialise PATH, LD_LIBRARY_PATH and PYTHONPATH variables anymore**

The last versions of sat were reinitialising the PATH, LD_LIBRARY_PATH and PYTHONPATH variables before the compilation.
The objective was to avoid bad interaction with the user environment, and ensure that sat environment was correctly set for build.
Alas this policy causes difficulties, notably on cluster where people sometimes need to use an alternate compiler and have to set it through *module load* command.
It was therefore decided to suppress this policy.

Please note that apart from this use case (set the environment of a specific compiler) it is strongly advised to use sat with a clean environment!
Note also that it is possible to manage with sat a compiler as a product, and therefore delegate the setting of this compiler to sat. When you have the choice it is a better option.

Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| sat #19888  | suppress at compile time the reinit if PATH, LD_LIBRARY_PATH and PYTHONPATH       |
+-------------+-----------------------------------------------------------------------------------+
| sat #19894  | use the product configuration file to assert if a product was compiled or not.    |
|             | (before sat was using the product directory, which was in some cases error prone) |
+-------------+-----------------------------------------------------------------------------------+
