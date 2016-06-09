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
import jobs

# Define all possible option for the make command :  sat make <options>
parser = src.options.Options()
parser.add_option('j', 'jobs_config', 'string', 'jobs_cfg', 
                  _('The name of the config file that contains'
                  ' the jobs configuration'))
parser.add_option('', 'job', 'string', 'job',
    _('The job name from which to execute commands.'), "")

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the job command description.
    :rtype: str
    '''
    return _("Executes the commands of the job defined"
             " in the jobs configuration file")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with job parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)
      
    jobs_cfg_files_dir = runner.cfg.SITE.jobs.config_path
    
    # Make sure the path to the jobs config files directory exists 
    if not os.path.exists(jobs_cfg_files_dir):      
        logger.write(_("Creating directory %s\n") % 
                     src.printcolors.printcLabel(jobs_cfg_files_dir), 1)
        os.mkdir(jobs_cfg_files_dir)

    # Make sure the jobs_config option has been called
    if not options.jobs_cfg:
        message = _("The option --jobs_config is required\n")      
        raise src.SatException( message )
    
    # Make sure the job option has been called
    if not options.job:
        message = _("The option --job is required\n")      
        raise src.SatException( message )
    
    # Make sure the invoked file exists
    file_jobs_cfg = os.path.join(jobs_cfg_files_dir, options.jobs_cfg)
    if not file_jobs_cfg.endswith('.pyconf'):
        file_jobs_cfg += '.pyconf'
        
    if not os.path.exists(file_jobs_cfg):
        message = _("The file %s does not exist.\n") % file_jobs_cfg
        logger.write(src.printcolors.printcError(message), 1)
        message = _("The possible files are :\n")
        logger.write( src.printcolors.printcInfo(message), 1)
        for f in sorted(os.listdir(jobs_cfg_files_dir)):
            if not f.endswith('.pyconf'):
                continue
            jobscfgname = f[:-7]
            logger.write("%s\n" % jobscfgname)
        raise src.SatException( _("No corresponding file") )
    
    jobs.print_info(logger, runner.cfg.VARS.dist, file_jobs_cfg)
    
    # Read the config that is in the file
    config_jobs = src.read_config_from_a_file(file_jobs_cfg)
    
    # Find the job and its commands
    found = False
    for job in config_jobs.jobs:
        if job.name == options.job:
            commands = job.commands
            found = True
            break
    if not found:
        msg = _("Impossible to find the job \"%(job_name)s\" in "
                "%(jobs_config_file)s" % {"job_name" : options.job,
                                          "jobs_config_file" : file_jobs_cfg})
        logger.write(src.printcolors.printcError(msg) + "\n")
        return 1
    
    # Find the maximum length of the commands in order to format the display
    len_max_command = max([len(cmd) for cmd in commands])
    
    # Loop over the commands and execute it
    res = 0
    nb_pass = 0
    for command in commands:
        # Determine if it is a sat command or a shell command
        cmd_exe = command.split(" ")[0] # first part
        if cmd_exe == "sat":
            sat_command_name = command.split(" ")[1]
            end_cmd = command.replace(cmd_exe + " " + sat_command_name, "")
        else:
            sat_command_name = "shell"
            end_cmd = "--command " + command
        
        # Get dynamically the command function to call 
        sat_command = runner.__getattr__(sat_command_name)
        logger.write("Executing " + 
                     src.printcolors.printcLabel(command) + " ", 3)
        logger.write("." * (len_max_command - len(command)) + " ", 3)
        logger.flush()
        # Execute the command
        code = sat_command(end_cmd,
                                     batch = True,
                                     verbose = 0,
                                     logger_add_link = logger)
        # Print the status of the command
        if code == 0:
            nb_pass += 1
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 3)
        else:
            res = 1
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 3)
    
    # Print the final state
    if res == 0:
        final_status = "OK"
    else:
        final_status = "KO"
   
    logger.write(_("\nCommands: %(status)s (%(valid_result)d/%(nb_products)d)\n\n") % \
        { 'status': src.printcolors.printc(final_status), 
          'valid_result': nb_pass,
          'nb_products': len(commands) }, 3)
    
    # Print the status and the list of log files
    logger.write(_("The status and the list of log files "
                   "used in the command is the following :\n"))
    logger.write("%i\n" % res, 1)
    for file_path in logger.l_logFiles:
        logger.write("%s\n" % file_path, 1)
    
    return res