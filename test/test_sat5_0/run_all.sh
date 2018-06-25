#!/usr/bin/env bash
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

echo "TODO: SAT5.1 OBSOLETE: to set as python script, may be"
echo "Begin date:"
date
echo
echo "Remove old results ... "
rm -rf .coverage htmlcov
echo "Done"
echo
echo "****************************"
coverage run --source=../commands/config.py    config/option_value.py > test_res.html
coverage run --source=../commands/config.py -a config/option_value_2.py >> test_res.html
coverage run --source=../commands/config.py -a config/create_user_pyconf.py >> test_res.html
coverage run --source=../commands/config.py -a config/option_copy.py >> test_res.html
coverage run --source=../commands/config.py -a config/option_edit.py >> test_res.html
coverage run --source=../commands/config.py,../commands/log.py,../src/xmlManager.py,../src/logger.py -a log/launch_browser.py >> test_res.html
coverage run --source=../commands/config.py,../commands/log.py,../src/xmlManager.py,../src/logger.py -a log/launch_browser2.py >> test_res.html
coverage run --source=../commands/config.py,../commands/source.py,../commands/patch.py,../commands/prepare.py -a prepare/test_source.py >> test_res.html
coverage run --source=../commands/config.py,../commands/source.py,../commands/patch.py,../commands/prepare.py -a prepare/test_patch.py >> test_res.html
coverage run --source=../commands/config.py,../commands/source.py,../commands/patch.py,../commands/prepare.py -a prepare/test_prepare.py >> test_res.html
coverage run --source=../commands/config.py,../commands/source.py,../commands/patch.py,../commands/prepare.py,../commands/clean.py -a prepare/test_clean.py >> test_res.html
coverage run --source=../commands/config.py,../commands/environ.py -a environ/test_environ.py >> test_res.html
coverage run --source=../commands/config.py,../commands/configure.py,../commands/environ.py -a compilation/test_configure.py >> test_res.html
coverage run --source=../commands/config.py,../commands/make.py,../commands/environ.py -a compilation/test_make.py >> test_res.html
coverage run --source=../commands/config.py,../commands/makeinstall.py,../commands/environ.py -a compilation/test_makeinstall.py >> test_res.html
coverage run --source=../commands/config.py,../commands/compile.py,../commands/configure.py,../commands/make.py,../commands/makeinstall.py,../commands/environ.py -a compilation/test_compilation.py >> test_res.html
coverage run --source=../commands/shell.py -a shell/test_shell.py >> test_res.html
coverage run --source=../commands/job.py -a job/test_job.py >> test_res.html
coverage run --source=../commands/jobs.py -a jobs/test_jobs.py >> test_res.html
coverage run --source=../commands/test.py,../src/test_module.py,../src/fork.py -a test/test_command.py >> test_res.html
echo "****************************"
echo
echo "building html coverage"
coverage html
echo "Done"
echo
echo "End date:"
date
echo

#firefox test_res.html htmlcov/index.html
