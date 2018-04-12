

Add a user custom command
***************************

Introduction
============

.. note:: This documentation is for python developers.


The salomeTools product provides a simple way to develop commands. 
The first thing to do is to add a file with ".py" extension in the **commands** directory of salomeTools.

Here are the basic requirements that must be followed in this file in order to add a command.

Basic requirements
==================

By adding a file **mycommand.py** in the **commands** directory, salomeTools will define a new command named **mycommand**.

In **mycommand.py**, there must be the following method: ::

    def run(args, runner, logger):
        # algorithm
        pass

In fact, at this point, the command will already be functional.
But there are some useful services provided by salomeTools :

* You can give some options to your command:
  
.. code-block:: python
   :emphasize-lines: 1,3,4,5,8,9

    import src
    
    # Define all possible option for mycommand command :  sat mycommand <options>
    parser = src.options.Options()
    parser.add_option('m', 'myoption', 'boolean', 'myoption', "My option changes the behavior of my command.")

    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm


* You can add a **description** method that will display a message when the user will call the help:


.. code-block:: python
   :emphasize-lines: 7,8

    import src
    
    # Define all possible option for mycommand command :  sat mycommand <options>
    parser = src.options.Options()
    parser.add_option('m', 'myoption', 'boolean', 'myoption', "My option changes the behavior of my command.")

    def description():
        return _("The help of mycommand.")   

    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm

How to access to salomeTools config and other commands ?
========================================================

The runner variable is an instance of the Sat class. It gives access to cfg : the data model that is read from all configuration files of salomeTools (*.pyconf) For example, runner.cfg.APPLICATION.out_dir will contain the root directory of the application on which you are working.

It gives also access to all other commands of salomeTools :

.. code-block:: python

    runner.prepare(runner.cfg.VARS.application)

How to log ?
============

The logger variable is an instance of the Logger class. It gives access to the write method.

When this method is called, the message passed as parameter will be displayed in the termnial and written in an xml log file.

.. code-block:: python

    logger.write("My message", 3)

The second argument defines the level of verbosity that is wanted for this message. It has to be between 1 and 5 (the most verbose level).

HELLO WORLD !
=============

Here is a hello world command :

.. code-block:: python

    import src

    # Define all possible option for mycommand command :  sat mycommand <options>
    parser = src.options.Options()
    parser.add_option('m', 'myoption', 'boolean', 'myoption', "My option changes the behavior of my command.")

    def description():
        return _("The help of mycommand.")
    
    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm
        if options.myoption:
            logger.write('HELLO, WORLD !\n')
        else:
            logger.write('WORLD, HELLO !\n')
            
A first call of mycommand:

.. code-block:: bash

    >./sat mycommand --myoption
    HELLO, WORLD !

    Tap the following command to get the log :
    /path/to/salomeTools/sat log
    
Another call of mycommand:

.. code-block:: bash

    >./sat mycommand
    WORLD, HELLO !

    Tap the following command to get the log :
    /path/to/salomeTools/sat log
    
Get the help of mycommand:

.. code-block:: bash

    >./sat --help mycommand
    Version: 5.0.0dev

    Description:
    The help of mycommand.

    Available options are:
     -m, --myoption (boolean)
             My option changes the behavior of my command.
