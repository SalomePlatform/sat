*****************
SAT version 5.5.0
*****************

Release Notes, November 2019
============================

.. warning:: This documentation is under construction!

New features and improvments
----------------------------

**pip mode for python modules**


**single directory mode**


**Generalisation of sat launcher command**


**optimisation of sat compile**


**new management of sections in product configution files**


Change log
----------

This chapter does not provide the complete set of changes included, only the
most significant changes are listed.


+-------------+-----------------------------------------------------------------------------------+
| Artifact    | Description                                                                       |
+=============+===================================================================================+
| spns #16894 | clean the temp directory at the end of sat package                                |
+-------------+-----------------------------------------------------------------------------------+
| sat #12965  | optimisation of sat compile : better, simplier and faster algo for dependencies!  |
+-------------+-----------------------------------------------------------------------------------+
| sat # 17206 | Use pip to manage python modules                                                  |
+-------------+-----------------------------------------------------------------------------------+
| sat #17137  | check_install functionality improvement : uses linux expending shell rules and    |
|             | interprets environment variables                                                  |
+-------------+-----------------------------------------------------------------------------------+
| sat #8544   | Update and improvement of documentation                                           |
+-------------+-----------------------------------------------------------------------------------+
| sat # 8547  | Generalisation of sat launcher command (new option --exe to specify which exe     |
|             | should be launched after setting the environment                                  |
+-------------+-----------------------------------------------------------------------------------+
| sat #17357  | New field in application pyconf "rm_rpoducts" to blacklist some products          |
+-------------+-----------------------------------------------------------------------------------+
| sat #17194  | Parametrication of the value of INSTALL and BINARIES directories                  |
|             | (in src/internal_config/salomeTools.pyconf)                                       |
+-------------+-----------------------------------------------------------------------------------+
| sat #17639  | Warning when sat is launcher with python3                                         |
+-------------+-----------------------------------------------------------------------------------+
| sat #17359  | New incremental mode for the definition of products                               |
+-------------+-----------------------------------------------------------------------------------+
|             |                                                                                   |
+-------------+-----------------------------------------------------------------------------------+
