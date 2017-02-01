#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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

# create a parser for command line options
parser = src.options.Options()
parser.add_option("s",
                  "sources",
                  "boolean",
                  "sources",
                  _("Search the duplicate files in the SOURCES directory."))
parser.add_option("p",
                  "path",
                  "list2",
                  "path",
                  _("Optional: Search the duplicate files in the given "
                    "directory paths."))
parser.add_option("",
                  "exclude-file",
                  "list2",
                  "exclude_file",
                  _("Optional: Override the default list of filtered files."))
parser.add_option("",
                  "exclude-extension",
                  "list2",
                  "exclude_extension",
                  _("Optional: Override the default list of filtered "
                    "extensions."))
parser.add_option("",
                  "exclude-path",
                  "list2",
                  "exclude_path",
                  _("Optional: Override the default list of filtered paths."))

default_extension_ignored = ['html', 'png', 'txt', 'js', 'xml', 'cmake', 'gif', 
                     'm4', 'in', 'pyo', 'pyc', 'doctree', 'css']
default_files_ignored = ['__init__.py', 'Makefile.am', 'VERSION',
                         'build_configure', 
                         'README', 'AUTHORS', 'NEWS', 'COPYING', 'ChangeLog']
default_directories_ignored = []

def list_directory(lpath, extension_ignored, files_ignored, directories_ignored):
    '''Make the list of all files and paths that are not filtered 
    
    :param lpath List: The list of path to of the directories where to 
                       search for duplicates
    :param extension_ignored List: The list of extensions to ignore
    :param files_ignored List: The list of files to ignore
    :param directories_ignored List: The list of directory paths to ignore
    :return: files_arb_out is the list of [file, path] 
             and files_out is is the list of files
    :rtype: List, List
    '''
    files_out = []
    files_arb_out=[]
    for path in lpath:
        for root, __, files in os.walk(path):  
            for fic in files:
                extension = fic.split('.')[-1]   
                if (extension not in extension_ignored and 
                                                      fic not in files_ignored):
                    in_ignored_dir = False
                    for rep in directories_ignored:
                        if rep in root:
                            in_ignored_dir = True                
                    if not in_ignored_dir:
                        files_out.append([fic])              
                        files_arb_out.append([fic, root])
    return files_arb_out, files_out

def format_list_of_str(l_str):
    '''Make a list from a string
    
    :param l_str List or Str: The variable to format
    :return: the formatted variable
    :rtype: List
    '''
    if not isinstance(l_str, list):
        return l_str
    return ",".join(l_str)

def print_info(logger, info, level=2):
    '''Format a display
    
    :param logger Logger: The logger instance
    :param info List: the list of tuple to display
    :param valMax float: the maximum value of the variable
    :param level int: the verbose level that will be used
    '''
    smax = max(map(lambda l: len(l[0]), info))
    for i in info:
        sp = " " * (smax - len(i[0]))
        src.printcolors.print_value(logger,
                                    sp + i[0],
                                    format_list_of_str(i[1]),
                                    2)
    logger.write("\n", level)

class Progress_bar:
    "Create a progress bar in the terminal"
    
    def __init__(self, name, valMin, valMax, logger, length = 50):
        '''Initialization of the progress bar.
        
        :param name str: The name of the progress bar
        :param valMin float: the minimum value of the variable
        :param valMax float: the maximum value of the variable
        :param logger Logger: the logger instance
        :param length int: the lenght of the progress bar
        '''
        self.name = name
        self.valMin = valMin
        self.valMax = valMax
        self.length = length
        self.logger = logger
        if (self.valMax - self.valMin) <= 0 or length <= 0:
            out_err = _('ERROR: Wrong init values for the progress bar\n')
            raise src.SatException(out_err)
        
    def display_value_progression(self,val):
        '''Display the progress bar.
        
        :param val float: val must be between valMin and valMax.
        '''
        if val < self.valMin or val > self.valMax:
            self.logger.write(src.printcolors.printcWarning(_(
                           'WARNING : wrong value for the progress bar.\n')), 3)
        else:
            perc = (float(val-self.valMin) / (self.valMax - self.valMin)) * 100.
            nb_equals = int(perc * self.length / 100)
            out = '\r %s : %3d %% [%s%s]' % (self.name, perc, nb_equals*'=',
                                             (self.length - nb_equals)*' ' )
            self.logger.write(out, 3)
            self.logger.flush()

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the find_duplicates command description.
    :rtype: str
    '''
    return _("The find_duplicates command search recursively for all duplicates"
             " files in a the INSTALL directory (or the optionally given "
             "directory) and prints the found files to the terminal.\n\n"
             "example:\nsat find_duplicates --path /tmp")

def run(args, runner, logger):
    '''method that is called when salomeTools is called with find_duplicates 
       parameter.
    '''
    # parse the arguments
    (options, args) = parser.parse_args(args)
    
    # Determine the directory path where to search 
    # for duplicates files regarding the options
    if options.path:
        l_dir_path = options.path
    else:
        src.check_config_has_application(runner.cfg)
        if options.sources:
            l_dir_path = [os.path.join(runner.cfg.APPLICATION.workdir,
                                       "SOURCES")]
        else:
            # find all installation paths
            all_products = runner.cfg.APPLICATION.products.keys()
            l_product_cfg = src.product.get_products_infos(all_products,
                                                           runner.cfg)
            l_dir_path = [pi.install_dir for __, pi in l_product_cfg]
    
    # Get the files to ignore during the searching
    files_ignored = default_files_ignored
    if options.exclude_file:
        files_ignored = options.exclude_file

    # Get the extension to ignore during the searching
    extension_ignored = default_extension_ignored
    if options.exclude_extension:
        extension_ignored = options.exclude_extension

    # Get the directory paths to ignore during the searching
    directories_ignored = default_directories_ignored
    if options.exclude_path:
        directories_ignored = options.exclude_path
    
    # Check the directories
    l_path = src.deepcopy_list(l_dir_path)
    l_dir_path = []
    for dir_path in l_path:
        if not(os.path.isdir(dir_path)):
            msg = _("%s does not exists or is not a directory path: "
                    "it will be ignored" % dir_path)
            logger.write("%s\n" % src.printcolors.printcWarning(msg), 3)
            continue
        l_dir_path.append(dir_path)
            
    
    # Display some information
    info = [(_("Directories"), "\n".join(l_dir_path)),
            (_("Ignored files"), files_ignored),
            (_("Ignored extensions"), extension_ignored),
            (_("Ignored directories"), directories_ignored)
           ]
    print_info(logger, info)
    
    # Get all the files and paths
    logger.write(_("Store all file paths ... "), 3)
    logger.flush()
    dic, fic = list_directory(l_dir_path,
                              extension_ignored,
                              files_ignored,
                              directories_ignored)  
    logger.write(src.printcolors.printcSuccess('OK\n'), 3)
    
    # Eliminate all the singletons
    len_fic = len(fic)
    range_fic = range(0,len_fic)
    range_fic.reverse()
    my_bar = Progress_bar(_('Eliminate the files that are not duplicated'),
                          0,
                          len_fic,
                          logger,
                          length = 50)
    for i in range_fic:
        my_bar.display_value_progression(len_fic - i)
        if fic.count(fic[i])==1:
            fic.remove(fic[i])
            dic.remove(dic[i])

    # Format the resulting variable to get a dictionary
    logger.write(_("\n\nCompute the dict {files : [list of pathes]} ... "), 3)
    fic.sort()
    len_fic = len(fic)
    rg_fic = range(0,len_fic)
    rg_fic.reverse()
    for i in rg_fic:
        if fic[i-1] != fic[i]:
            fic.remove(fic[i])

    dic_fic_paths = {}
    for fichier in fic:
        the_file = fichier[0]
        l_path = []
        for fic_path in dic:
            if fic_path[0] == the_file:
                l_path.append(fic_path[1])
        dic_fic_paths[the_file] = l_path
    
    logger.write(src.printcolors.printcSuccess('OK\n'), 3)

    # End the execution if no duplicates were found
    if len(dic_fic_paths) == 0:
        logger.write(_("No duplicate files found.\n"), 3)
        return 0

    # Check that there are no singletons in the result (it would be a bug)
    for elem in dic_fic_paths:
        if len(dic_fic_paths[elem])<2:
            logger.write(_("Warning : element %s has not more than"
                         " two paths.\n") % elem, 3)


    # Display the results
    logger.write(src.printcolors.printcInfo(_('\nResults:\n\n')), 3)
    max_file_name_lenght = max(map(lambda l: len(l), dic_fic_paths.keys()))
    for fich in dic_fic_paths:
        logger.write(src.printcolors.printcLabel(fich), 1)
        sp = " " * (max_file_name_lenght - len(fich))
        logger.write(sp, 1)
        for rep in dic_fic_paths[fich]:
            logger.write(rep, 1)
            logger.write(" ", 1)
        logger.write("\n", 1)

    return 0
