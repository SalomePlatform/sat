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

import src

def get_module_config(config, module_name, version):
    vv = version
    for c in ".-": vv = vv.replace(c, "_") # substitute some character with _
    full_module_name = module_name + '_' + vv

    mod_info = None
    if full_module_name in config.MODULES:
        # returns specific information for the given version
        mod_info = config.MODULES[full_module_name]    

    elif module_name in config.MODULES:
        # returns the generic information (given version not found)
        mod_info = config.MODULES[module_name]
    
    # merge opt_depend in depend
    if mod_info is not None and 'opt_depend' in mod_info:
        for depend in mod_info.opt_depend:
            if depend in config.MODULES:
                mod_info.depend.append(depend,'')
    return mod_info

def get_modules_infos(lmodules, config):
    modules_infos = []
    for mod in lmodules:
        version_mod = config.APPLICATION.modules[mod][0]
        mod_info = get_module_config(config, mod, version_mod)
        if mod_info is not None:
            modules_infos.append((mod, mod_info))
        else:
            msg = _("The %s module has no definition in the configuration.") % mod
            raise src.SatException(msg)
    return modules_infos


def module_is_sample(module_info): 
    mtype = module_info.module_type
    return mtype.lower() == 'sample'