
.. include:: ../rst_prolog.rst


Add a user custom command
***************************

Introduction
============

.. note:: This documentation is for Python_ developers.


The salomeTools product provides a simple way to develop commands. 
The first thing to do is to add a file with *.py* extension in the ``commands`` directory of salomeTools.

Here are the basic requirements that must be followed in this file in order to add a command.

Basic requirements
==================

By adding a file *mycommand.py* in the ``commands`` directory, salomeTools will define a new command named ``mycommand``.

In *mycommand.py*, there must be the following method: ::

    def run(args, runner, logger):
        # your algorithm ...
        pass

In fact, at this point, the command will already be functional.
But there are some useful services provided by salomeTools :

* You can give some options to your command:
  
.. code-block:: python

    import src
    
    # Define all possible option for mycommand command :  'sat mycommand <options>'
    parser = src.options.Options()
    parser.add_option('m', 'myoption', \
                      'boolean', 'myoption', \
                      'My option changes the behavior of my command.')

    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm


* You can add a *description* method that will display a message when the user will call the help:


.. code-block:: python
   :emphasize-lines: 9,10

    import src
    
    # Define all possible option for mycommand command : 'sat mycommand <options>'
    parser = src.options.Options()
    parser.add_option('m', 'myoption', \
                      'boolean', 'myoption', \
                      'My option changes the behavior of my command.')

    def description():
        return _("The help of mycommand.")   

    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm

HowTo access salomeTools config and other commands
========================================================

The *runner* variable is an python instance of *Sat* class. 
It gives access to *runner.cfg* which is the data model defined from all 
*configuration pyconf files* of salomeTools 
For example, *runner.cfg.APPLICATION.workdir*
contains the root directory of the current application.

The *runner* variable gives also access to other commands of salomeTools:

.. code-block:: python

    # as CLI_ 'sat prepare ...'
    runner.prepare(runner.cfg.VARS.application)

HowTo logger
==============

The logger variable is an instance of the Logger class. 
It gives access to the write method.

When this method is called, the message passed as parameter 
will be displayed in the terminal and written in an xml log file.

.. code-block:: python

    logger.write("My message", 3) # 3 as default

The second argument defines the level of verbosity 
that is wanted for this message. 
It has to be between 1 and 5 (the most verbose level).

HELLO example
==============

Here is a *hello* command, file *commands/hello.py*:

.. code-block:: python

    import src

    """
    hello.py
    Define all possible options for hello command: 
    sat hello <options>
    """

    parser = src.options.Options()
    parser.add_option('f', 'french', 'boolean', 'french', "french set hello message in french.")

    def description():
        return _("The help of hello.")
    
    def run(args, runner, logger):
        # Parse the options
        (options, args) = parser.parse_args(args)
        # algorithm
        if not options.french:
            logger.write('HELLO! WORLD!\n')
        else:
            logger.write('Bonjour tout le monde!\n')
            
A first call of hello:

.. code-block:: bash

    # Get the help of hello:
    ./sat --help hello

    # To get bonjour
    ./sat hello --french
    Bonjour tout le monde!
 
    # To get hello
    ./sat hello
    HELLO! WORLD!

    # To get the log
    ./sat log



    

