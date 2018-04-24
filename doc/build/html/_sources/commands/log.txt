
.. include:: ../../rst_prolog.rst

Command log
****************

Description
===========
The **log** command displays sat log in a web browser or in a terminal.

Usage
=====
* Show (in a web browser) the log of the commands corresponding to an application: ::

    sat log <application>

* Show the log for commands that do not use any application: ::

    sat log
    
* The --terminal (or -t) display the log directly in the terminal, through a CLI_ interactive menu: ::

	sat log <application> --terminal

* The --last option displays only the last command: ::

    sat log <application> --last

* To access the last compilation log in terminal mode, use --last_terminal option: ::

    sat log <application> --last_terminal

* The --clean (int) option erases the n older log files and print the number of remaining log files: ::

    sat log <application> --clean 50



Some useful configuration pathes
=================================

* **USER**

  * **browser** : The browser used to show the log (by default *firefox*).
  * **log_dir** : The directory used to store the log files.

