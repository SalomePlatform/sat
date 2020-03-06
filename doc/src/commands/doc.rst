
.. include:: ../../rst_prolog.rst

Command doc
****************

Description
===========
The **doc** command displays sat documentation.

Usage
=====
* Show (in a web browser) the sat documentation in format xml/html: ::

    sat doc --xml

* Show (in evince, for example) the (same) sat documentation in format pdf: ::

    sat doc --pdf

* Edit and modify in your preference user editor the sources files (rst) of sat documentation: ::

    sat doc --edit

* get information how to compile locally sat documentation (from the sources files): ::

    sat doc --compile



Some useful configuration paths
=================================

* **USER**

  * **browser** : The browser used to show the html files (*firefox* for example).
  * **pdf_viewer** : The viewer used to show the pdf files (*evince* for example).
  * **editor** : The editor used to edit ascii text files (*pluma or gedit* for example).

