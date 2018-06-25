#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  Copyright (C) 2010-2018  CEA/DEN
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


"""
to set id_rsa from/to reflexive on local machine:

    @is231761/home/wambeke/.ssh>ssh wambeke@is231761
    Password: 
    Last login: Thu Jun  7 13:34:07 2018 from is231761.intra.cea.fr
    @is231761/home/wambeke>exit
    déconnexion

    @is231761/home/wambeke/.ssh> ssh-keygen
    Generating public/private rsa key pair.
    Enter file in which to save the key (/home/wambeke/.ssh/id_rsa): 
    Enter passphrase (empty for no passphrase): 
    Enter same passphrase again: 
    Your identification has been saved in /home/wambeke/.ssh/id_rsa.
    Your public key has been saved in /home/wambeke/.ssh/id_rsa.pub.
    The key fingerprint is:
    SHA256:V0IU/wkuCRw42rA5bHFgdJlzDx9EIJyWIBrkzkL3GNA wambeke@is231761
    The key's randomart image is:
    +---[RSA 2048]----+
    |ooo.=+o*o=*.     |

    |                 |
    +----[SHA256]-----+

    @is231761/home/wambeke/.ssh> ls
    id_rsa  id_rsa.pub  known_hosts
    @is231761/home/wambeke/.ssh> rm known_hosts
    @is231761/home/wambeke/.ssh> ls
    id_rsa  id_rsa.pub

    @is231761/home/wambeke/.ssh> ssh wambeke@is231761
    The authenticity of host 'is231761 (127.0.0.1)' can't be established.
    ECDSA key fingerprint is SHA256:QvrU7Abrbily0bzMjYbRPeKCxDkXT9rQ6pSpcm+yFN4.
    ECDSA key fingerprint is MD5:6c:95:b7:c7:cd:de:c5:07:8b:3a:9b:14:d1:69:6b:c6.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added 'is231761' (ECDSA) to the list of known hosts.
    Password: 
    Last login: Thu Jun  7 13:35:07 2018 from is231761.intra.cea.fr
    @is231761/home/wambeke>exit
    déconnexion
    Connection to is231761 closed.


    @is231761/home/wambeke/.ssh> lst
    total 124K
    -rw-r--r--   1 wambeke lgls  170  7 juin  13:36 known_hosts
    drwx------   2 wambeke lgls 4,0K  7 juin  13:36 .
    -rw-r--r--   1 wambeke lgls  398  7 juin  13:35 id_rsa.pub
    -rw-------   1 wambeke lgls 1,7K  7 juin  13:35 id_rsa
    drwxr-xr-x 182 wambeke lmpe 104K  6 juin  13:39 ..



    @is231761/home/wambeke/.ssh> ssh-copy-id -i ~/.ssh/id_rsa.pub is231761
    /usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/wambeke/.ssh/id_rsa.pub"
    /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
    /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
    Password: 

    Number of key(s) added: 1

    Now try logging into the machine, with:   "ssh 'is231761'"
    and check to make sure that only the key(s) you wanted were added.

    @is231761/home/wambeke/.ssh> ssh wambeke@is231761
    Last login: Thu Jun  7 13:36:42 2018 from is231761.intra.cea.fr
    @is231761/home/wambeke>exit
    déconnexion
    Connection to is231761 closed.

"""

import os
import sys
import unittest
import getpass

verbose = False

class TestCase(unittest.TestCase):
  "Test a paramiko connection"""

  def setLoggerParamiko(self):
    """to get logs of paramiko, useful if problems"""
    import logging as LOGI
    loggerPrmk = LOGI.getLogger("paramiko")
    if len(loggerPrmk.handlers) != 0:
       print("logging.__file__ %s" % LOGI.__file__)
       print("logger paramiko have handler set yet, is a surprise")
       return
    if not verbose:
       # stay as it, null
       return

    #set a paramiko logger verbose
    handler = LOGI.StreamHandler()
    msg = "create paramiko logger, with handler on stdout"
    
    # handler = LOGI.MemoryHandler()
    # etc... https://docs.python.org/2/library/logging.handlers.html
    # msg = "create paramiko logger, with handler in memory"

    # original frm from paramiko
    # frm = '%(levelname)-.3s [%(asctime)s.%(msecs)03d] thr=%(thread)-3d %(name)s: %(message)s' # noqa
    frm = '%(levelname)-5s :: %(asctime)s :: %(name)s :: %(message)s'
    handler.setFormatter(LOGI.Formatter(frm, '%y%m%d_%H%M%S'))
    loggerPrmk.addHandler(handler)
      
    # logger is not notset but low, handlers needs setlevel greater
    loggerPrmk.setLevel(LOGI.DEBUG)
    handler.setLevel(LOGI.INFO) # LOGI.DEBUG) # may be other one

    loggerPrmk.info(msg)


  '''example from internet
  def fetch_netmask(self, hostname, port=22):
    private_key = os.path.expanduser('~/.ssh/id_rsa')
    connection = open_ssh_connection('wambeke', hostname, port=port, key=private_key)

    get_netmask = ("ip -oneline -family inet address show | grep {}").format(hostname)
    stdin, stdout, stderr = connection.exec_command(get_netmask)
    address = parse_address(hostname, stdout)
    connection.close()
    return address

  def open_ssh_connection(self, username, hostname, port=22, key=None):
    client = PK.SSHClient()
    client.set_missing_host_key_policy(PK.AutoAddPolicy())
    client.connect(hostname, port=port, timeout=5, username=username, key_filename=key)
    return client
  '''

  def test_000(self):
    self.setLoggerParamiko()
    

  def test_010(self):
    # http://docs.paramiko.org/en/2.4/api/agent.html

    try:
      import paramiko as PK
    except:
      print("\nproblem 'import paramiko', no tests")
      return

    # port=22 # useless
    username = getpass.getuser()
    hostname = os.uname()[1]
    aFile = "/tmp/%s_test_paramiko.tmp" % username
    cmd = ("pwd; ls -alt {0}; cat {0}").format(aFile)
    
    # connect
    client = PK.SSHClient()
    client.set_missing_host_key_policy(PK.AutoAddPolicy())  
    # client.connect(hostname, username=username, password="xxxxx")
    # client.connect(hostname, username=username, passphrase="yyyy", key_filename="/home/wambeke/.ssh/id_rsa_satjobs_passphrase")
    # client.connect(hostname, username=username)

    # timeout in seconds
    client.connect(hostname, username=username, timeout=1.)
    
    # obtain session
    session = client.get_transport().open_session()
    # Forward local agent
    PK.agent.AgentRequestHandler(session)
    # commands executed after this point will see the forwarded agent on the remote end.
    
    # one api
    session.exec_command("date > %s" % aFile)
    cmd = ("pwd; ls -alt {0}; cat {0} && echo OK").format(aFile)
    # another api
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read()
    if verbose:
      print('stdout:\n%s' % output)
    self.assertTrue(aFile in output)
    self.assertTrue("OK" in output)
    client.close()
                
if __name__ == '__main__':
    # verbose = True # human eyes
    unittest.main(exit=False)
    pass
