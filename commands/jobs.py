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
import sys
import datetime
import time
import paramiko

import src


parser = src.options.Options()

parser.add_option('j', 'jobs_config', 'string', 'jobs_cfg', 
                  _('The name of the config file that contains'
                  ' the jobs configuration'))
parser.add_option('o', 'only_jobs', 'list2', 'only_jobs',
                  _('The list of jobs to launch, by their name. '))
parser.add_option('l', 'list', 'boolean', 'list', 
                  _('list all available config files.'))
parser.add_option('n', 'no_label', 'boolean', 'no_label',
                  _("do not print labels, Works only with --list."), False)
parser.add_option('t', 'test_connection', 'boolean', 'test_connection',
                  _("Try to connect to the machines. Not executing the jobs."),
                  False)
parser.add_option('p', 'publish', 'boolean', 'publish',
                  _("Generate an xml file that can be read in a browser to "
                    "display the jobs status."),
                  False)

class machine(object):
    '''Class to manage a ssh connection on a machine
    '''
    def __init__(self, host, user, port=22, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.ssh = paramiko.SSHClient()
        self._connection_successful = None
    
    def connect(self, logger):
        '''Initiate the ssh connection to the remote machine
        
        :param logger src.logger.Logger: The logger instance 
        :return: Nothing
        :rtype: N\A
        '''

        self._connection_successful = False
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.host,
                             port=self.port,
                             username=self.user,
                             password = self.password)
        except paramiko.AuthenticationException:
            message = src.KO_STATUS + _(": authentication failed\n")
            logger.write( src.printcolors.printcError(message))
        except paramiko.BadHostKeyException:
            message = (src.KO_STATUS + 
                       _(": the server's host key could not be verified\n"))
            logger.write( src.printcolors.printcError(message))
        except paramiko.SSHException:
            message = (src.KO_STATUS + 
                    _(": error connecting or establishing an SSH session\n"))
            logger.write( src.printcolors.printcError(message))
        except:
            logger.write( src.printcolors.printcError(src.KO_STATUS + '\n'))
        else:
            self._connection_successful = True
            logger.write( src.printcolors.printcSuccess(src.OK_STATUS) + '\n')
    
    def successfully_connected(self, logger):
        '''Verify if the connection to the remote machine has succeed
        
        :param logger src.logger.Logger: The logger instance 
        :return: True if the connection has succeed, False if not
        :rtype: bool
        '''
        if self._connection_successful == None:
            message = "Warning : trying to ask if the connection to "
            "(host: %s, port: %s, user: %s) is OK whereas there were"
            " no connection request" % \
            (machine.host, machine.port, machine.user)
            logger.write( src.printcolors.printcWarning(message))
        return self._connection_successful
  
    
    def close(self):
        '''Close the ssh connection
        
        :rtype: N\A
        '''
        self.ssh.close()
    
    def exec_command(self, command, logger):
        '''Execute the command on the remote machine
        
        :param command str: The command to be run
        :param logger src.logger.Logger: The logger instance 
        :return: the stdin, stdout, and stderr of the executing command,
                 as a 3-tuple
        :rtype: (paramiko.channel.ChannelFile, paramiko.channel.ChannelFile, 
                paramiko.channel.ChannelFile)
        '''
        try:        
            # Does not wait the end of the command
            (stdin, stdout, stderr) = self.ssh.exec_command(command)
        except paramiko.SSHException:
            message = src.KO_STATUS + _(
                            ": the server failed to execute the command\n")
            logger.write( src.printcolors.printcError(message))
            return (None, None, None)
        except:
            logger.write( src.printcolors.printcError(src.KO_STATUS + '\n'))
            return (None, None, None)
        else:
            return (stdin, stdout, stderr)
       
    def write_info(self, logger):
        '''Prints the informations relative to the machine in the logger 
           (terminal traces and log file)
        
        :param logger src.logger.Logger: The logger instance
        :return: Nothing
        :rtype: N\A
        '''
        logger.write("host : " + self.host + "\n")
        logger.write("port : " + str(self.port) + "\n")
        logger.write("user : " + str(self.user) + "\n")
        logger.write("password : " + str(self.password) + "\n")
        if self.successfully_connected(logger):
            status = src.OK_STATUS
        else:
            status = src.KO_STATUS
        logger.write("Connection : " + status + "\n\n") 


class job(object):
    '''Class to manage one job
    '''
    def __init__(self, name, machine, commands, timeout, logger, after=None):

        self.name = name
        self.machine = machine
        self.after = after
        self.timeout = timeout
        self.logger = logger
        
        self._T0 = -1
        self._Tf = -1
        self._has_begun = False
        self._has_finished = False
        self._stdin = None # Store the command inputs field
        self._stdout = None # Store the command outputs field
        self._stderr = None # Store the command errors field

        self.out = None # Contains something only if the job is finished
        self.err = None # Contains something only if the job is finished    
               
        self.commands = " ; ".join(commands)
    
    def get_pids(self):
        pids = []
        for cmd in self.commands.split(" ; "):
            cmd_pid = 'ps aux | grep "' + cmd + '" | awk \'{print $2}\''
            (_, out_pid, _) = self.machine.exec_command(cmd_pid, self.logger)
            pids_cmd = out_pid.readlines()
            pids_cmd = [str(src.only_numbers(pid)) for pid in pids_cmd]
            pids+=pids_cmd
        return pids
    
    def kill_remote_process(self):
        '''Kills the process on the remote machine.
        
        :return: (the output of the kill, the error of the kill)
        :rtype: (str, str)
        '''
        
        pids = self.get_pids()
        cmd_kill = " ; ".join([("kill -9 " + pid) for pid in pids])
        (_, out_kill, err_kill) = self.machine.exec_command(cmd_kill, 
                                                            self.logger)
        return (out_kill, err_kill)
            
    def has_begun(self):
        '''Returns True if the job has already begun
        
        :return: True if the job has already begun
        :rtype: bool
        '''
        return self._has_begun
    
    def has_finished(self):
        '''Returns True if the job has already finished 
           (i.e. all the commands have been executed)
           If it is finished, the outputs are stored in the fields out and err.  
        
        :return: True if the job has already finished
        :rtype: bool
        '''
        
        # If the method has already been called and returned True
        if self._has_finished:
            return True
        
        # If the job has not begun yet
        if not self.has_begun():
            return False
        
        if self._stdout.channel.closed:
            self._has_finished = True
            # And store the result outputs
            self.out = self._stdout.read()
            self.err = self._stderr.read()
            # And put end time
            self._Tf = time.time()
        
        return self._has_finished
    
    def is_running(self):
        '''Returns True if the job commands are running 
        
        :return: True if the job is running
        :rtype: bool
        '''
        return self.has_begun() and not self.has_finished()
    
    def time_elapsed(self):
        if not self.has_begun():
            return -1
        T_now = time.time()
        return T_now - self._T0
    
    def check_time(self):
        if not self.has_begun():
            return
        if self.time_elapsed() > self.timeout:
            self._has_finished = True
            self._Tf = time.time()
            self.get_pids()
            (out_kill, _) = self.kill_remote_process()
            self.out = "TIMEOUT \n" + out_kill.read()
            self.err = "TIMEOUT : %s seconds elapsed\n" % str(self.timeout)
    
    def total_duration(self):
        return self._Tf - self._T0
        
    def run(self, logger):
        if self.has_begun():
            print("Warn the user that a job can only be launched one time")
            return
        
        if not self.machine.successfully_connected(logger):
            self._has_finished = True
            self.out = "N\A"
            self.err = ("Connection to machine (host: %s, port: %s, user: %s) has failed" 
                        % (self.machine.host, self.machine.port, self.machine.user))
        else:
            self._T0 = time.time()
            self._stdin, self._stdout, self._stderr = self.machine.exec_command(
                                                        self.commands, logger)
            if (self._stdin, self._stdout, self._stderr) == (None, None, None):
                self._has_finished = True
                self._Tf = time.time()
                self.out = "N\A"
                self.err = "The server failed to execute the command"
        
        self._has_begun = True
    
    def write_results(self, logger):
        logger.write("name : " + self.name + "\n")
        if self.after:
            logger.write("after : %s\n" % self.after)
        logger.write("Time elapsed : %4imin %2is \n" % 
                     (self.total_duration()/60 , self.total_duration()%60))
        if self._T0 != -1:
            logger.write("Begin time : %s\n" % 
                         time.strftime('%Y-%m-%d %H:%M:%S', 
                                       time.localtime(self._T0)) )
        if self._Tf != -1:
            logger.write("End time   : %s\n\n" % 
                         time.strftime('%Y-%m-%d %H:%M:%S', 
                                       time.localtime(self._Tf)) )
        
        machine_head = "Informations about connection :\n"
        underline = (len(machine_head) - 2) * "-"
        logger.write(src.printcolors.printcInfo(machine_head + underline + "\n"))
        self.machine.write_info(logger)
        
        logger.write(src.printcolors.printcInfo("out : \n"))
        if self.out is None:
            logger.write("Unable to get output\n")
        else:
            logger.write(self.out + "\n")
        logger.write(src.printcolors.printcInfo("err : \n"))
        if self.err is None:
            logger.write("Unable to get error\n")
        else:
            logger.write(self.err + "\n")
        
        
    
class Jobs(object):
    '''Class to manage the jobs to be run
    '''
    def __init__(self, runner, logger, config_jobs, lenght_columns = 20):
        # The jobs configuration
        self.cfg_jobs = config_jobs
        # The machine that will be used today
        self.lmachines = []
        # The list of machine (hosts, port) that will be used today 
        # (a same host can have several machine instances since there 
        # can be several ssh parameters) 
        self.lhosts = []
        # The jobs to be launched today 
        self.ljobs = []     
        self.runner = runner
        self.logger = logger
        # The correlation dictionary between jobs and machines
        self.dic_job_machine = {} 
        self.len_columns = lenght_columns
        
        # the list of jobs that have not been run yet
        self._l_jobs_not_started = []
        # the list of jobs that have already ran 
        self._l_jobs_finished = []
        # the list of jobs that are running 
        self._l_jobs_running = [] 
                
        self.determine_products_and_machines()
    
    def define_job(self, job_def, machine):
        '''Takes a pyconf job definition and a machine (from class machine) 
           and returns the job instance corresponding to the definition.
        
        :param job_def src.config.Mapping: a job definition 
        :param machine machine: the machine on which the job will run
        :return: The corresponding job in a job class instance
        :rtype: job
        '''
        name = job_def.name
        cmmnds = job_def.commands
        timeout = job_def.timeout
        after = None
        if 'after' in job_def:
            after = job_def.after
            
        return job(name, machine, cmmnds, timeout, self.logger, after = after)
    
    def determine_products_and_machines(self):
        '''Function that reads the pyconf jobs definition and instantiates all
           the machines and jobs to be done today.

        :return: Nothing
        :rtype: N\A
        '''
        today = datetime.date.weekday(datetime.date.today())
        host_list = []
        
        for job_def in self.cfg_jobs.jobs :
            if today in job_def.when: 
                if 'host' not in job_def:
                    host = self.runner.cfg.VARS.hostname
                else:
                    host = job_def.host
                
                if 'port' not in job_def:
                    port = 22
                else:
                    port = job_def.port
                
                if (host, port) not in host_list:
                    host_list.append((host, port))
                
                if 'user' not in job_def:
                    user = self.runner.cfg.VARS.user
                else:
                    user = job_def.user
                
                if 'password' not in job_def:
                    passwd = None
                else:
                    passwd = job_def.password
                                              
                a_machine = machine(host, user, port=port, passwd=passwd)
                
                self.lmachines.append(a_machine)
                
                a_job = self.define_job(job_def, a_machine)
                
                self.ljobs.append(a_job)
                
                self.dic_job_machine[a_job] = a_machine
        
        self.lhosts = host_list
        
    def ssh_connection_all_machines(self, pad=50):
        '''Function that do the ssh connection to every machine 
           to be used today.

        :return: Nothing
        :rtype: N\A
        '''
        self.logger.write(src.printcolors.printcInfo((
                        "Establishing connection with all the machines :\n")))
        for machine in self.lmachines:
            # little algorithm in order to display traces
            begin_line = ("(host: %s, port: %s, user: %s)" % 
                          (machine.host, machine.port, machine.user))
            if pad - len(begin_line) < 0:
                endline = " "
            else:
                endline = (pad - len(begin_line)) * "." + " "
            self.logger.write( begin_line + endline )
            self.logger.flush()
            # the call to the method that initiate the ssh connection
            machine.connect(self.logger)
        self.logger.write("\n")
        

    def is_occupied(self, hostname):
        '''Function that returns True if a job is running on 
           the machine defined by its host and its port.
        
        :param hostname (str, int): the pair (host, port)
        :return: the job that is running on the host, 
                or false if there is no job running on the host. 
        :rtype: job / bool
        '''
        host = hostname[0]
        port = hostname[1]
        for jb in self.dic_job_machine:
            if jb.machine.host == host and jb.machine.port == port:
                if jb.is_running():
                    return jb
        return False
    
    def update_jobs_states_list(self):
        '''Function that updates the lists that store the currently
           running jobs and the jobs that have already finished.
        
        :return: Nothing. 
        :rtype: N\A
        '''
        jobs_finished_list = []
        jobs_running_list = []
        for jb in self.dic_job_machine:
            if jb.is_running():
                jobs_running_list.append(jb)
                jb.check_time()
            if jb.has_finished():
                jobs_finished_list.append(jb)
        self._l_jobs_finished = jobs_finished_list
        self._l_jobs_running = jobs_running_list
    
    def findJobThatHasName(self, name):
        '''Returns the job by its name.
        
        :param name str: a job name
        :return: the job that has the name. 
        :rtype: job
        '''
        for jb in self.ljobs:
            if jb.name == name:
                return jb

        # the following is executed only if the job was not found
        msg = _('The job "%s" seems to be nonexistent') % name
        raise src.SatException(msg)
    
    def str_of_length(self, text, length):
        '''Takes a string text of any length and returns 
           the most close string of length "length".
        
        :param text str: any string
        :param length int: a length for the returned string
        :return: the most close string of length "length"
        :rtype: str
        '''
        if len(text) > length:
            text_out = text[:length-3] + '...'
        else:
            diff = length - len(text)
            before = " " * (diff/2)
            after = " " * (diff/2 + diff%2)
            text_out = before + text + after
            
        return text_out
    
    def display_status(self, len_col):
        '''Takes a lenght and construct the display of the current status 
           of the jobs in an array that has a column for each host.
           It displays the job that is currently running on the host 
           of the column.
        
        :param len_col int: the size of the column 
        :return: Nothing
        :rtype: N\A
        '''
        
        display_line = ""
        for host_port in self.lhosts:
            jb = self.is_occupied(host_port)
            if not jb: # nothing running on the host
                empty = self.str_of_length("empty", len_col)
                display_line += "|" + empty 
            else:
                display_line += "|" + src.printcolors.printcInfo(
                                        self.str_of_length(jb.name, len_col))
        
        self.logger.write("\r" + display_line + "|")
        self.logger.flush()
    

    def run_jobs(self):
        '''The main method. Runs all the jobs on every host. 
           For each host, at a given time, only one job can be running.
           The jobs that have the field after (that contain the job that has
           to be run before it) are run after the previous job.
           This method stops when all the jobs are finished.
        
        :return: Nothing
        :rtype: N\A
        '''

        # Print header
        self.logger.write(src.printcolors.printcInfo(
                                                _('Executing the jobs :\n')))
        text_line = ""
        for host_port in self.lhosts:
            host = host_port[0]
            port = host_port[1]
            if port == 22: # default value
                text_line += "|" + self.str_of_length(host, self.len_columns)
            else:
                text_line += "|" + self.str_of_length(
                                "("+host+", "+str(port)+")", self.len_columns)
        
        tiret_line = " " + "-"*(len(text_line)-1) + "\n"
        self.logger.write(tiret_line)
        self.logger.write(text_line + "|\n")
        self.logger.write(tiret_line)
        self.logger.flush()
        
        # The infinite loop that runs the jobs
        l_jobs_not_started = self.dic_job_machine.keys()
        while len(self._l_jobs_finished) != len(self.dic_job_machine.keys()):
            for host_port in self.lhosts:
                
                if self.is_occupied(host_port):
                    continue
             
                for jb in l_jobs_not_started:
                    if (jb.machine.host, jb.machine.port) != host_port:
                        continue 
                    if jb.after == None:
                        jb.run(self.logger)
                        l_jobs_not_started.remove(jb)
                        break
                    else:
                        jb_before = self.findJobThatHasName(jb.after) 
                        if jb_before.has_finished():
                            jb.run(self.logger)
                            l_jobs_not_started.remove(jb)
                            break
            
            self.update_jobs_states_list()
            
            # Display the current status     
            self.display_status(self.len_columns)
            
            # Make sure that the proc is not entirely busy
            time.sleep(0.001)
        
        self.logger.write("\n")    
        self.logger.write(tiret_line)                   
        self.logger.write("\n\n")

    def write_all_results(self):
        '''Display all the jobs outputs.
        
        :return: Nothing
        :rtype: N\A
        '''
        
        for jb in self.dic_job_machine.keys():
            self.logger.write(src.printcolors.printcLabel(
                        "#------- Results for job %s -------#\n" % jb.name))
            jb.write_results(self.logger)
            self.logger.write("\n\n")

class Gui(object):
    '''Class to manage the the xml data that can be displayed in a browser to
       see the jobs states
    '''
    def __init__(self, xml_file_path, l_jobs):
        # The path of the xml file
        self.xml_file_path = xml_file_path
        # Open the file in a writing stream
        self.xml_file = src.xmlManager.XmlLogFile(xml_file_path, "JobsReport")
        # Create the lines and columns
        self.initialize_array(l_jobs)
        # Write the wml file
        self.update_xml_file()
    
    def initialize_array(self, l_jobs):
        l_hosts = []
        l_job_names_status = []
        for job in l_jobs:
            host = (job.machine.host, job.machine.port)
            if host not in l_hosts:
                l_hosts.append(host)
            l_job_names_status.append((job.name, host, "Not launched"))
        self.l_hosts = l_hosts
        self.l_job_names_status = l_job_names_status
        
    def update_xml_file(self):
        # Update the hosts node
        self.xml_file.add_simple_node("hosts")
        for host_name, host_port in self.l_hosts:
            self.xml_file.append_node_attrib("hosts", {host_name : host_port})
        
        # Update the job names and status node
        for jname, jhost, jstatus in self.l_job_names_status:
            self.xml_file.add_simple_node("job", jstatus, {"name" : jname, "host" : jhost[0] + ":" + str(jhost[1])})
        # Write the file
        self.xml_file.write_tree("job_report.xsl")
        
        
def print_info(logger, arch, JobsFilePath):
    '''Prints information header..
    
    :param logger src.logger.Logger: The logger instance
    :param arch str: a string that gives the architecture of the machine on 
                     which the command is launched
    :param JobsFilePath str: The path of the file 
                             that contains the jobs configuration
    :return: Nothing
    :rtype: N\A
    '''
    info = [
        (_("Platform"), arch),
        (_("File containing the jobs configuration"), JobsFilePath)
    ]
    
    smax = max(map(lambda l: len(l[0]), info))
    for i in info:
        sp = " " * (smax - len(i[0]))
        src.printcolors.print_value(logger, sp + i[0], i[1], 2)
    logger.write("\n", 2)

##
# Describes the command
def description():
    return _("The jobs command launches maintenances that are described"
             " in the dedicated jobs configuration file.")

##
# Runs the command.
def run(args, runner, logger):
    (options, args) = parser.parse_args(args)
       
    jobs_cfg_files_dir = runner.cfg.SITE.jobs.config_path
    
    # Make sure the path to the jobs config files directory exists 
    if not os.path.exists(jobs_cfg_files_dir):      
        logger.write(_("Creating directory %s\n") % 
                     src.printcolors.printcLabel(jobs_cfg_files_dir), 1)
        os.mkdir(jobs_cfg_files_dir)

    # list option : display all the available config files
    if options.list:
        lcfiles = []
        if not options.no_label:
            sys.stdout.write("------ %s\n" % 
                             src.printcolors.printcHeader(jobs_cfg_files_dir))

        for f in sorted(os.listdir(jobs_cfg_files_dir)):
            if not f.endswith('.pyconf'):
                continue
            cfilename = f[:-7]
            lcfiles.append(cfilename)
            sys.stdout.write("%s\n" % cfilename)
        return 0

    # Make sure the jobs_config option has been called
    if not options.jobs_cfg:
        message = _("The option --jobs_config is required\n")      
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
            sys.stdout.write("%s\n" % jobscfgname)
        raise src.SatException( _("No corresponding file") )
    
    print_info(logger, runner.cfg.VARS.dist, file_jobs_cfg)
    
    # Read the config that is in the file
    config_jobs = src.read_config_from_a_file(file_jobs_cfg)
    if options.only_jobs:
        l_jb = src.pyconf.Sequence()
        for jb in config_jobs.jobs:
            if jb.name in options.only_jobs:
                l_jb.append(jb,
                "Adding a job that was given in only_jobs option parameters")
        config_jobs.jobs = l_jb
              
    # Initialization
    today_jobs = Jobs(runner, logger, config_jobs)
    # SSH connection to all machines
    today_jobs.ssh_connection_all_machines()
    if options.test_connection:
        return 0
    
    if options.publish:
        Gui("/export/home/serioja/LOGS/test.xml", today_jobs.ljobs)
    
    try:
        # Run all the jobs contained in config_jobs
        today_jobs.run_jobs()
    except KeyboardInterrupt:
        logger.write("\n\n%s\n\n" % 
                (src.printcolors.printcWarning(_("Forced interruption"))), 1)
    finally:
        # find the potential not finished jobs and kill them
        for jb in today_jobs.ljobs:
            if not jb.has_finished():
                jb.kill_remote_process()
                
        # Output the results
        today_jobs.write_all_results()
