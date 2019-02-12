#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2012  CEA/DEN
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

import os
import src

# Define all possible option for log command :  sat doc <options>
parser = src.options.Options()
parser.add_option('x', 'xml', 'boolean', 'xml', "Open sat xml/html documentation in browser (x as firefoX)", None)
parser.add_option('p', 'pdf', 'boolean', 'pdf', "Open sat pdf documentation in viewer", False)
parser.add_option('e', 'edit', 'boolean', 'edit', "edit/modify source dodumentation rst files", False)
parser.add_option('c', 'compile', 'boolean', 'compile', "how to compile html/pdf doc", False)

def description():
    """method that is called when salomeTools is called with --help option.

    :return: The text to display for the log command description.
    :rtype: str
    """
    return _("""\
The doc command gives access to the sat documentation.
    
example:
>> sat doc         # --xml as default
>> sat doc --xml
>> sat doc --pdf
""")

def run(args, runner, logger):
    '''method that is called when salomeTools is called with log parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)

    # get the log directory. 
    satDir = runner.cfg.VARS.salometoolsway
    docDir = os.path.join(satDir, "doc")
    htmlFile = os.path.join(docDir, "build", "html", "index.html")
    pdfFile = os.path.join(satDir, "doc", "build", "latex", "salomeTools.pdf")
    rstFiles = os.path.join(satDir, "doc", "src", "*.rst")
    rstFilesCommands = os.path.join(satDir, "doc", "src", "commands", "*.rst")
    readmeFile = os.path.join(satDir, "doc", "README")

    logger.write("docdir %s\n" % docDir, 6)
    logger.write("options %s\n" % options, 6)

    if options.pdf:
        if not os.path.isfile(pdfFile):
            msg = "\npdf documentation not found. Please build it inside doc directory\n"\
                  "(follow README instructions in doc directory)\n"
            logger.error(msg)
            return 1
        src.system.show_in_editor(runner.cfg.USER.pdf_viewer, pdfFile, logger)

    elif options.edit:
        src.system.show_in_editor(runner.cfg.USER.editor, rstFiles, logger)
        src.system.show_in_editor(runner.cfg.USER.editor, rstFilesCommands, logger)

    elif options.compile:
        logger.write("How to compile documentation:\n%s" % open(readmeFile,"r").read(), 3)

    else:
        if not os.path.isfile(htmlFile):
            msg = "\nhtml documentation not found. Please build it inside doc directory\n"\
                  "(follow README instructions in doc directory)\n"
            logger.error(msg)
            return 1
        src.system.show_in_editor(runner.cfg.USER.browser, htmlFile, logger)

    return 0
