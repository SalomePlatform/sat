#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, traceback
import os.path
import time as THEBIGTIME

# set path
toolsWay = r'${toolsWay}'
resourcesWay = r'${resourcesWay}'
outWay = r'${sessionDir}'
tmpDir = r'${tmpDir}'

listTest = ${listTest}
ignore = ${ignore}

sys.path.append(toolsWay)
from TOOLS import TOOLS_class
my_tools = TOOLS_class(resourcesWay, tmpDir, toolsWay)

from TOOLS import SatNotApplicableError

# on set les variables d'environement
os.environ['TT_BASE_RESSOURCES'] = resourcesWay
sys.path.append(resourcesWay)

exec_result = open(r'${resultFile}', 'w')
exec_result.write('Open\n')

__stdout__ = sys.stdout
__stderr__ = sys.stderr

for test in listTest:
    pylog = open(os.path.join(outWay, test[:-3] + ".result.py"), "w")
    testout = open(os.path.join(outWay, test[:-3] + ".out.py"), "w")
    my_tools.init()
    sys.stdout = testout
    sys.stderr = testout

    pylog.write('#-*- coding:utf-8 -*-\n')
    exec_result.write("Run %s " % test)
    exec_result.flush()

    try:
        timeStart = THEBIGTIME.time()
        execfile(os.path.join(outWay, test), globals(), locals())
        timeTest = THEBIGTIME.time() - timeStart
    except SatNotApplicableError, ex:
        status = "NA"
        reason = str(ex)
        exec_result.write("NA\n")
        timeTest = THEBIGTIME.time() - timeStart
        pylog.write('status = "NA"\n')
        pylog.write('time = "' + timeTest.__str__() + '"\n')
        pylog.write('callback = "%s"\n' % reason)
    except Exception, ex:
        status = "KO"
        reason = ""
        if ignore.has_key(test):
            status = "KF"
            reason = "Known Failure = %s\n\n" % ignore[test]
        exec_result.write("%s\n" % status)
        timeTest = THEBIGTIME.time() - timeStart
        pylog.write('status = "%s" \n' % status)
        pylog.write('time = "' + timeTest.__str__() + '"\n')
        pylog.write('callback="""' + reason)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type,
                                  exc_value,
                                  exc_traceback,
                                  None,
                                  file=pylog)
        pylog.write('"""\n')
    else:
        exec_result.write("OK\n")
        pylog.write('status = "OK"\n')
        pylog.write('time = "' + timeTest.__str__() + '"\n')

    testout.close()
    sys.stdout = __stdout__
    sys.stderr = __stderr__
    my_tools.writeInFiles(pylog)
    pylog.close()

exec_result.write('Close\n')
exec_result.close()

if 'PY' not in '${sessionName}':
    import salome_utils
    killScript = os.path.join(os.environ['KERNEL_ROOT_DIR'],
                              'bin',
                              'salome',
                              'killSalome.py')
    cmd = '{python} {killScript} {port}'.format(python=os.environ['PYTHONBIN'],
                                      	     killScript=killScript,
                                      	     port=salome_utils.getPortNumber())
    os.system(cmd)
