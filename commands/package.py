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
import stat
import shutil
import tarfile

import src

BINARY = "binary"
SOURCE = "Source"
PROJECT = "Project"
SAT = "Sat"

ARCHIVE_DIR = "ARCHIVES"
PROJECT_DIR = "PROJECT"

PROJECT_TEMPLATE = """#!/usr/bin/env python
#-*- coding:utf-8 -*-

# The path to the archive root directory
root_path : ""
# path to the PROJECT
project_path : $root_path + "PROJECT/"

# Where to search the archives of the products
ARCHIVEPATH : $root_path + "ARCHIVES"
# Where to search the pyconf of the applications
APPLICATIONPATH : $project_path + "applications/"
# Where to search the pyconf of the products
PRODUCTPATH : $project_path + "products/"
# Where to search the pyconf of the jobs of the project
JOBPATH : $project_path + "jobs/"
# Where to search the pyconf of the machines of the project
MACHINEPATH : $project_path + "machines/"
"""

SITE_TEMPLATE = ("""#!/usr/bin/env python
#-*- coding:utf-8 -*-

SITE :
{   
    log :
    {
        log_dir : $USER.workdir + "/LOGS"
    }
    test :{
           tmp_dir_with_application : '/tmp' + $VARS.sep + $VARS.user + """
"""$VARS.sep + $APPLICATION.name + $VARS.sep + 'test'
           tmp_dir : '/tmp' + $VARS.sep + $VARS.user + $VARS.sep + 'test'
           timeout : 150
           }
}

PROJECTS :
{
project_file_paths : [$VARS.salometoolsway + $VARS.sep + \"..\" + $VARS.sep"""
""" + \"""" + PROJECT_DIR + """\" + $VARS.sep + "project.pyconf"]
}
""")

# Define all possible option for the package command :  sat package <options>
parser = src.options.Options()
parser.add_option('b', 'binaries', 'boolean', 'binaries',
    _('Produce a binary package.'), False)
parser.add_option('s', 'sources', 'boolean', 'sources',
    _('Produce a compilable archive of the sources of the application.'), False)
parser.add_option('p', 'project', 'string', 'project',
    _('Produce an archive that contains a project.'), "")
parser.add_option('', 'salometools', 'boolean', 'sat',
    _('Produce an archive that contains salomeTools.'), False)
parser.add_option('n', 'name', 'string', 'name',
    _('The name or full path of the archive.'), None)
parser.add_option('', 'with_vcs', 'boolean', 'with_vcs',
    _('Only source package: do not make archive of vcs products.'), False)

def add_files(tar, name_archive, d_content, logger):
    '''Create an archive containing all directories and files that are given in
       the d_content argument.
    
    :param tar tarfile: The tarfile instance used to make the archive.
    :param name_archive str: The name of the archive to make.
    :param d_content dict: The dictionary that contain all directories and files
                           to add in the archive.
                           d_content[label] = 
                                        (path_on_local_machine, path_in_archive)
    :param logger Logger: the logging instance
    :return: 0 if success, 1 if not.
    :rtype: int
    '''
    # get the max length of the messages in order to make the display
    max_len = len(max(d_content.keys(), key=len))
    
    success = 0
    # loop over each directory or file stored in the d_content dictionary
    for name in d_content.keys():
        # display information
        len_points = max_len - len(name)
        logger.write(name + " " + len_points * "." + " ", 3)
        # Get the local path and the path in archive 
        # of the directory or file to add
        local_path, archive_path = d_content[name]
        in_archive = os.path.join(name_archive, archive_path)
        # Add it in the archive
        try:
            tar.add(local_path, arcname=in_archive)
            logger.write(src.printcolors.printcSuccess(_("OK")), 3)
        except Exception as e:
            logger.write(src.printcolors.printcError(_("KO ")), 3)
            logger.write(e, 3)
            success = 1
        logger.write("\n", 3)
    return success

def produce_relative_launcher(config,
                              logger,
                              file_dir,
                              file_name,
                              binaries_dir_name):
    '''Create a specific SALOME launcher for the binary package. This launcher 
       uses relative paths.
    
    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :param file_dir str: the directory where to put the launcher
    :param file_name str: The launcher name
    :param binaries_dir_name str: the name of the repository where the binaries
                                  are, in the archive.
    :return: the path of the produced launcher
    :rtype: str
    '''
    
    # Get the launcher template
    profile_install_dir = os.path.join(binaries_dir_name,
                                       config.APPLICATION.profile.product)
    withProfile = src.fileEnviron.withProfile.replace( "PROFILE_INSTALL_DIR",
                                                       profile_install_dir )

    before, after = withProfile.split(
                                "# here your local standalone environment\n")

    # create an environment file writer
    writer = src.environment.FileEnvWriter(config,
                                           logger,
                                           file_dir,
                                           src_root=None)
    
    filepath = os.path.join(file_dir, file_name)
    # open the file and write into it
    launch_file = open(filepath, "w")
    launch_file.write(before)
    # Write
    writer.write_cfgForPy_file(launch_file, for_package = binaries_dir_name)
    launch_file.write(after)
    launch_file.close()
    
    # change the rights in order to make the file executable for everybody
    os.chmod(filepath,
             stat.S_IRUSR |
             stat.S_IRGRP |
             stat.S_IROTH |
             stat.S_IWUSR |
             stat.S_IXUSR |
             stat.S_IXGRP |
             stat.S_IXOTH)
    
    return filepath

def binary_package(config, logger, options, tmp_working_dir):
    '''Prepare a dictionary that stores all the needed directories and files to
       add in a binary package.
    
    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :param options OptResult: the options of the launched command
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                binary package
    :return: the dictionary that stores all the needed directories and files to
             add in a binary package.
             {label : (path_on_local_machine, path_in_archive)}
    :rtype: dict
    '''

    # Get the list of product installation to add to the archive
    l_products_name = config.APPLICATION.products.keys()
    l_product_info = src.product.get_products_infos(l_products_name,
                                                    config)
    l_install_dir = []
    l_not_installed = []
    for prod_name, prod_info in l_product_info:
        # ignore the native and fixed products
        if (src.product.product_is_native(prod_info) 
                or src.product.product_is_fixed(prod_info)):
            continue
        if src.product.check_installation(prod_info):
            l_install_dir.append((prod_name, prod_info.install_dir))
        else:
            l_not_installed.append(prod_name)
    
    # Print warning or error if there are some missing products
    if len(l_not_installed) > 0:
        text_missing_prods = ""
        for p_name in l_not_installed:
            text_missing_prods += "-" + p_name + "\n"
        if not options.force_creation:
            msg = _("ERROR: there are missing products installations:")
            logger.write("%s\n%s" % (src.printcolors.printcError(msg),
                                     text_missing_prods),
                         1)
            return None
        else:
            msg = _("WARNING: there are missing products installations:")
            logger.write("%s\n%s" % (src.printcolors.printcWarning(msg),
                                     text_missing_prods),
                         1)
    
    # construct the name of the directory that will contain the binaries
    binaries_dir_name = "BINARIES-" + config.VARS.dist
    
    # construct the correlation table between the product names, there 
    # actual install directories and there install directory in archive
    d_products = {}
    for prod_name, install_dir in l_install_dir:
        path_in_archive = os.path.join(binaries_dir_name, prod_name)
        d_products[prod_name] = (install_dir, path_in_archive)
    
    # create the relative launcher and add it to the files to add
    launcher_name = config.APPLICATION.profile.launcher_name
    launcher_package = produce_relative_launcher(config,
                                                 logger,
                                                 tmp_working_dir,
                                                 launcher_name,
                                                 binaries_dir_name)
    
    d_products["launcher"] = (launcher_package, launcher_name)
    
    return d_products

def source_package(sat, config, logger, options, tmp_working_dir):
    '''Prepare a dictionary that stores all the needed directories and files to
       add in a source package.
    
    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :param options OptResult: the options of the launched command
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                binary package
    :return: the dictionary that stores all the needed directories and files to
             add in a source package.
             {label : (path_on_local_machine, path_in_archive)}
    :rtype: dict
    '''
    
    # Get all the products that are prepared using an archive
    logger.write("Find archive products ... ")
    d_archives, l_pinfo_vcs = get_archives(config, logger)
    logger.write("Done\n")
    d_archives_vcs = {}
    if not options.with_vcs:
        # Make archives with the products that are not prepared using an archive
        # (git, cvs, svn, etc)
        logger.write("Construct archives for vcs products ... ")
        d_archives_vcs = get_archives_vcs(l_pinfo_vcs,
                                          sat,
                                          config,
                                          logger,
                                          tmp_working_dir)
        logger.write("Done\n")

    # Create a project
    logger.write("Create the project ... ")
    d_project = create_project_for_src_package(config,
                                                tmp_working_dir,
                                                options.with_vcs)
    logger.write("Done\n")
    
    # Add salomeTools
    tmp_sat = add_salomeTools(config, tmp_working_dir)
    d_sat = {"salomeTools" : (tmp_sat, "salomeTools")}
    
    # Add a sat symbolic link
    tmp_satlink_path = os.path.join(tmp_working_dir, 'sat')
    t = os.getcwd()
    os.chdir(tmp_working_dir)
    if os.path.lexists(tmp_satlink_path):
        os.remove(tmp_satlink_path)
    os.symlink(os.path.join('salomeTools', 'sat'), 'sat')
    os.chdir(t)
    
    d_sat["sat link"] = (tmp_satlink_path, "sat")
    
    return src.merge_dicts(d_archives, d_archives_vcs, d_project, d_sat)

def get_archives(config, logger):
    '''Find all the products that are get using an archive and all the products
       that are get using a vcs (git, cvs, svn) repository.
    
    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :return: the dictionary {name_product : 
             (local path of its archive, path in the package of its archive )}
             and the list of specific configuration corresponding to the vcs 
             products
    :rtype: (Dict, List)
    '''
    # Get the list of product informations
    l_products_name = config.APPLICATION.products.keys()
    l_product_info = src.product.get_products_infos(l_products_name,
                                                    config)
    d_archives = {}
    l_pinfo_vcs = []
    for p_name, p_info in l_product_info:
        # ignore the native and fixed products
        if (src.product.product_is_native(p_info) 
                or src.product.product_is_fixed(p_info)):
            continue
        if p_info.get_source == "archive":
            archive_path = p_info.archive_info.archive_name
            archive_name = os.path.basename(archive_path)
        else:
            l_pinfo_vcs.append((p_name, p_info))
            
        d_archives[p_name] = (archive_path,
                              os.path.join(ARCHIVE_DIR, archive_name))
    return d_archives, l_pinfo_vcs

def add_salomeTools(config, tmp_working_dir):
    '''Prepare a version of salomeTools that has a specific site.pyconf file 
       configured for a source package.

    :param config Config: The global configuration.
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                source package
    :return: The path to the local salomeTools directory to add in the package
    :rtype: str
    '''
    # Copy sat in the temporary working directory
    sat_tmp_path = src.Path(os.path.join(tmp_working_dir, "salomeTools"))
    sat_running_path = src.Path(config.VARS.salometoolsway)
    sat_running_path.copy(sat_tmp_path)
    
    # Update the site.pyconf file that contains the path to the project
    site_pyconf_name = "site.pyconf"
    site_pyconf_dir = os.path.join(tmp_working_dir, "salomeTools", "data")
    site_pyconf_file = os.path.join(site_pyconf_dir, site_pyconf_name)
    ff = open(site_pyconf_file, "w")
    ff.write(SITE_TEMPLATE)
    ff.close()
    
    return sat_tmp_path.path

def get_archives_vcs(l_pinfo_vcs, sat, config, logger, tmp_working_dir):
    '''For sources package that require that all products are get using an 
       archive, one has to create some archive for the vcs products.
       So this method calls the clean and source command of sat and then create
       the archives.

    :param l_pinfo_vcs List: The list of specific configuration corresponding to
                             each vcs product
    :param sat Sat: The Sat instance that can be called to clean and source the
                    products
    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                source package
    :return: the dictionary that stores all the archives to add in the source 
             package. {label : (path_on_local_machine, path_in_archive)}
    :rtype: dict
    '''
    # clean the source directory of all the vcs products, then use the source 
    # command and thus construct an archive that will not contain the patches
    l_prod_names = [pn for pn, __ in l_pinfo_vcs]
    # clean
    logger.write(_("clean sources\n"))
    args_clean = config.VARS.application
    args_clean += " --sources --products "
    args_clean += ",".join(l_prod_names)
    sat.clean(args_clean, batch=True, verbose=0, logger_add_link = logger)
    # source
    logger.write(_("get sources"))
    args_source = config.VARS.application
    args_source += " --products "
    args_source += ",".join(l_prod_names)
    sat.source(args_source, batch=True, verbose=0, logger_add_link = logger)

    # make the new archives
    d_archives_vcs = {}
    for pn, pinfo in l_pinfo_vcs:
        path_archive = make_archive(pn, pinfo, tmp_working_dir)
        d_archives_vcs[pn] = (path_archive,
                              os.path.join(ARCHIVE_DIR, pn + ".tgz"))
    return d_archives_vcs

def make_archive(prod_name, prod_info, where):
    '''Create an archive of a product by searching its source directory.

    :param prod_name str: The name of the product.
    :param prod_info Config: The specific configuration corresponding to the 
                             product
    :param where str: The path of the repository where to put the resulting 
                      archive
    :return: The path of the resulting archive
    :rtype: str
    '''
    path_targz_prod = os.path.join(where, prod_name + ".tgz")
    tar_prod = tarfile.open(path_targz_prod, mode='w:gz')
    local_path = prod_info.source_dir
    tar_prod.add(local_path, arcname=prod_name)
    tar_prod.close()
    return path_targz_prod       

def create_project_for_src_package(config, tmp_working_dir, with_vcs):
    '''Create a specific project for a source package.

    :param config Config: The global configuration.
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                source package
    :param with_vcs boolean: True if the package is with vcs products (not 
                             transformed into archive products)
    :return: The dictionary 
             {"project" : (produced project, project path in the archive)}
    :rtype: Dict
    '''

    # Create in the working temporary directory the full project tree
    project_tmp_dir = os.path.join(tmp_working_dir, PROJECT_DIR)
    products_pyconf_tmp_dir = os.path.join(project_tmp_dir,
                                         "products")
    compil_scripts_tmp_dir = os.path.join(project_tmp_dir,
                                         "products",
                                         "compil_scripts")
    env_scripts_tmp_dir = os.path.join(project_tmp_dir,
                                         "products",
                                         "env_scripts")
    patches_tmp_dir = os.path.join(project_tmp_dir,
                                         "products",
                                         "patches")
    application_tmp_dir = os.path.join(project_tmp_dir,
                                         "applications")
    for directory in [project_tmp_dir,
                      compil_scripts_tmp_dir,
                      env_scripts_tmp_dir,
                      patches_tmp_dir,
                      application_tmp_dir]:
        src.ensure_path_exists(directory)

    # Create the pyconf that contains the information of the project
    project_pyconf_name = "project.pyconf"        
    project_pyconf_file = os.path.join(project_tmp_dir, project_pyconf_name)
    ff = open(project_pyconf_file, "w")
    ff.write(PROJECT_TEMPLATE)
    ff.close()
    
    # Loop over the products to get there pyconf and all the scripts 
    # (compilation, environment, patches)
    # and create the pyconf file to add to the project
    lproducts_name = config.APPLICATION.products.keys()
    l_products = src.product.get_products_infos(lproducts_name, config)
    for p_name, p_info in l_products:
        # ignore native and fixed products
        if (src.product.product_is_native(p_info) or 
                src.product.product_is_fixed(p_info)):
            continue
        find_product_scripts_and_pyconf(p_name,
                                        p_info,
                                        config,
                                        with_vcs,
                                        compil_scripts_tmp_dir,
                                        env_scripts_tmp_dir,
                                        patches_tmp_dir,
                                        products_pyconf_tmp_dir)
    
    find_application_pyconf(config, application_tmp_dir)
    
    d_project = {"project" : (project_tmp_dir, PROJECT_DIR )}
    return d_project

def find_product_scripts_and_pyconf(p_name,
                                    p_info,
                                    config,
                                    with_vcs,
                                    compil_scripts_tmp_dir,
                                    env_scripts_tmp_dir,
                                    patches_tmp_dir,
                                    products_pyconf_tmp_dir):
    '''Create a specific pyconf file for a given product. Get its environment 
       script, its compilation script and patches and put it in the temporary
       working directory. This method is used in the source package in order to
       construct the specific project.

    :param p_name str: The name of the product.
    :param p_info Config: The specific configuration corresponding to the 
                             product
    :param config Config: The global configuration.
    :param with_vcs boolean: True if the package is with vcs products (not 
                             transformed into archive products)
    :param compil_scripts_tmp_dir str: The path to the temporary compilation 
                                       scripts directory of the project.
    :param env_scripts_tmp_dir str: The path to the temporary environment script 
                                    directory of the project.
    :param patches_tmp_dir str: The path to the temporary patch scripts 
                                directory of the project.
    :param products_pyconf_tmp_dir str: The path to the temporary product 
                                        scripts directory of the project.
    '''
    
    # read the pyconf of the product
    product_pyconf_path = src.find_file_in_lpath(p_name + ".pyconf",
                                           config.PATHS.PRODUCTPATH)
    product_pyconf_cfg = src.pyconf.Config(product_pyconf_path)

    # find the compilation script if any
    if src.product.product_has_script(p_info):
        compil_script_path = src.Path(p_info.compil_script)
        compil_script_path.copy(compil_scripts_tmp_dir)
        product_pyconf_cfg[p_info.section].compil_script = os.path.basename(
                                                    p_info.compil_script)
    # find the environment script if any
    if src.product.product_has_env_script(p_info):
        env_script_path = src.Path(p_info.environ.env_script)
        env_script_path.copy(env_scripts_tmp_dir)
        product_pyconf_cfg[p_info.section].environ.env_script = os.path.basename(
                                                p_info.environ.env_script)
    # find the patches if any
    if src.product.product_has_patches(p_info):
        patches = src.pyconf.Sequence()
        for patch_path in p_info.patches:
            p_path = src.Path(patch_path)
            p_path.copy(patches_tmp_dir)
            patches.append(os.path.basename(patch_path), "")

        product_pyconf_cfg[p_info.section].patches = patches
    
    if with_vcs:
        # put in the pyconf file the resolved values
        for info in ["git_info", "cvs_info", "svn_info"]:
            if info in p_info:
                for key in p_info[info]:
                    product_pyconf_cfg[p_info.section][info][key] = p_info[
                                                                      info][key]
    else:
        # if the product is not archive, then make it become archive.
        if src.product.product_is_vcs(p_info):
            product_pyconf_cfg[p_info.section].get_source = "archive"
            if not "archive_info" in product_pyconf_cfg[p_info.section]:
                product_pyconf_cfg[p_info.section].addMapping("archive_info",
                                        src.pyconf.Mapping(product_pyconf_cfg),
                                        "")
            product_pyconf_cfg[p_info.section
                              ].archive_info.archive_name = p_info.name + ".tgz"
    
    # write the pyconf file to the temporary project location
    product_tmp_pyconf_path = os.path.join(products_pyconf_tmp_dir,
                                           p_name + ".pyconf")
    ff = open(product_tmp_pyconf_path, 'w')
    ff.write("#!/usr/bin/env python\n#-*- coding:utf-8 -*-\n\n")
    product_pyconf_cfg.__save__(ff, 1)
    ff.close()

def find_application_pyconf(config, application_tmp_dir):
    '''Find the application pyconf file and put it in the specific temporary 
       directory containing the specific project of a source package.

    :param config Config: The global configuration.
    :param application_tmp_dir str: The path to the temporary application 
                                       scripts directory of the project.
    '''
    # read the pyconf of the application
    application_name = config.VARS.application
    application_pyconf_path = src.find_file_in_lpath(
                                            application_name + ".pyconf",
                                            config.PATHS.APPLICATIONPATH)
    application_pyconf_cfg = src.pyconf.Config(application_pyconf_path)
    
    # Change the workdir
    application_pyconf_cfg.APPLICATION.workdir = src.pyconf.Reference(
                                    application_pyconf_cfg,
                                    src.pyconf.DOLLAR,
                                    'VARS.salometoolsway + $VARS.sep + ".."')

    # Prevent from compilation in base
    application_pyconf_cfg.APPLICATION.no_base = "yes"
    
    # write the pyconf file to the temporary application location
    application_tmp_pyconf_path = os.path.join(application_tmp_dir,
                                               application_name + ".pyconf")
    ff = open(application_tmp_pyconf_path, 'w')
    ff.write("#!/usr/bin/env python\n#-*- coding:utf-8 -*-\n\n")
    application_pyconf_cfg.__save__(ff, 1)
    ff.close()

def project_package(project_file_path, tmp_working_dir):
    '''Prepare a dictionary that stores all the needed directories and files to
       add in a project package.
    
    :param project_file_path str: The path to the local project.
    :param tmp_working_dir str: The temporary local directory containing some 
                                specific directories or files needed in the 
                                project package
    :return: the dictionary that stores all the needed directories and files to
             add in a project package.
             {label : (path_on_local_machine, path_in_archive)}
    :rtype: dict
    '''
    d_project = {}
    # Read the project file and get the directories to add to the package
    project_pyconf_cfg = src.pyconf.Config(project_file_path)
    paths = {"ARCHIVEPATH" : "archives",
             "APPLICATIONPATH" : "applications",
             "PRODUCTPATH" : "products",
             "JOBPATH" : "jobs",
             "MACHINEPATH" : "machines"}
    # Loop over the project paths and add it
    for path in paths:
        if path not in project_pyconf_cfg:
            continue
        # Add the directory to the files to add in the package
        d_project[path] = (project_pyconf_cfg[path], paths[path])
        # Modify the value of the path in the package
        project_pyconf_cfg[path] = src.pyconf.Reference(
                                    project_pyconf_cfg,
                                    src.pyconf.DOLLAR,
                                    'project_path + "/' + paths[path] + '"')
    
    # Modify some values
    if "project_path" not in project_pyconf_cfg:
        project_pyconf_cfg.addMapping("project_path",
                                      src.pyconf.Mapping(project_pyconf_cfg),
                                      "")
    project_pyconf_cfg.project_path = ""
    
    # Write the project pyconf file
    project_file_name = os.path.basename(project_file_path)
    project_pyconf_tmp_path = os.path.join(tmp_working_dir, project_file_name)
    ff = open(project_pyconf_tmp_path, 'w')
    ff.write("#!/usr/bin/env python\n#-*- coding:utf-8 -*-\n\n")
    project_pyconf_cfg.__save__(ff, 1)
    ff.close()
    d_project["Project hat file"] = (project_pyconf_tmp_path, project_file_name)
    
    return d_project

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the package command description.
    :rtype: str
    '''
    return _("The package command creates an archive of the application.")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with package parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)
       
    # Check that a type of package is called, and only one
    all_option_types = (options.binaries,
                        options.sources,
                        options.project != "",
                        options.sat)

    # Check if no option for package type
    if all_option_types.count(True) == 0:
        msg = _("Error: Precise a type for the package\nUse one of the "
                "following options: --binaries, --sources, --project or --sat")
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1
    
    # Check for only one option for package type
    if all_option_types.count(True) > 1:
        msg = _("Error: You can use only one type for the package\nUse only one"
                " of the following options: --binaries, --sources, --project or"
                " --sat")
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1
    
    # Get the package type
    if options.binaries:
        package_type = BINARY
    if options.sources:
        package_type = SOURCE
    if options.project:
        package_type = PROJECT
    if options.sat:
        package_type = SAT

    # The repository where to put the package if not Binary or Source
    package_default_path = runner.cfg.USER.workdir
    
    if package_type in [BINARY, SOURCE]:
        # Check that the command has been called with an application
        src.check_config_has_application(runner.cfg)

        # Display information
        logger.write(_("Packaging application %s\n") % src.printcolors.printcLabel(
                                                    runner.cfg.VARS.application), 1)
        
        # Get the default directory where to put the packages
        package_default_path = os.path.join(runner.cfg.APPLICATION.workdir,
                                            "PACKAGE")
        src.ensure_path_exists(package_default_path)
        
    elif package_type == PROJECT:
        # check that the project is visible by SAT
        if options.project not in runner.cfg.PROJECTS.project_file_paths:
            site_path = os.path.join(runner.cfg.VARS.salometoolsway,
                                     "data",
                                     "site.pyconf")
            msg = _("ERROR: the project %(proj)s is not visible by salomeTools."
                    "\nPlease add it in the %(site)s file." % {
                                  "proj" : options.project, "site" : site_path})
            logger.write(src.printcolors.printcError(msg), 1)
            logger.write("\n", 1)
            return 1
    
    # Print
    src.printcolors.print_value(logger, "Package type", package_type, 2)

    # get the name of the archive or construct it
    if options.name:
        if os.path.basename(options.name) == options.name:
            # only a name (not a path)
            archive_name = options.name           
            dir_name = package_default_path
        else:
            archive_name = os.path.basename(options.name)
            dir_name = os.path.dirname(options.name)
        
        # suppress extension
        if archive_name[-len(".tgz"):] == ".tgz":
            archive_name = archive_name[:-len(".tgz")]
        if archive_name[-len(".tar.gz"):] == ".tar.gz":
            archive_name = archive_name[:-len(".tar.gz")]
        
    else:
        dir_name = package_default_path
        if package_type == BINARY:
            archive_name = (runner.cfg.APPLICATION.name +
                            "-" +
                            runner.cfg.VARS.dist)
            
        if package_type == SOURCE:
            archive_name = (runner.cfg.APPLICATION.name +
                            "-" +
                            "SRC")

        if package_type == PROJECT:
            project_name, __ = os.path.splitext(
                                            os.path.basename(options.project))
            archive_name = ("PROJECT" +
                            "-" +
                            project_name)
 
        if package_type == SAT:
            archive_name = ("salomeTools" +
                            "-" +
                            runner.cfg.INTERNAL.sat_version)
 
    path_targz = os.path.join(dir_name, archive_name + ".tgz")
    
    # Print the path of the package
    src.printcolors.print_value(logger, "Package path", path_targz, 2)

    # Create a working directory for all files that are produced during the
    # package creation and that will be removed at the end of the command
    tmp_working_dir = os.path.join(runner.cfg.VARS.tmp_root,
                                   runner.cfg.VARS.datehour)
    src.ensure_path_exists(tmp_working_dir)
    
    logger.write("\n", 3)

    msg = _("Preparation of files to add to the archive")
    logger.write(src.printcolors.printcLabel(msg), 2)
    logger.write("\n", 2)

    if package_type == BINARY:
        d_files_to_add = binary_package(runner.cfg,
                                        logger,
                                        options,
                                        tmp_working_dir)
        if not(d_files_to_add):
            return 1

    if package_type == SOURCE:
        d_files_to_add = source_package(runner,
                                        runner.cfg,
                                        logger, 
                                        options,
                                        tmp_working_dir)          
    
    if package_type == PROJECT:
        d_files_to_add = project_package(options.project, tmp_working_dir)

    if package_type == SAT:
        d_files_to_add = {"salomeTools" : (runner.cfg.VARS.salometoolsway, "")}
    
    logger.write("\n", 2)

    logger.write(src.printcolors.printcLabel(_("Actually do the package")), 2)
    logger.write("\n", 2)
    
    # Creating the object tarfile
    tar = tarfile.open(path_targz, mode='w:gz')
    
    # Add the files to the tarfile object
    res = add_files(tar, archive_name, d_files_to_add, logger)
    tar.close()
    
    # remove the working directory
    shutil.rmtree(tmp_working_dir)
    
    # Print again the path of the package
    logger.write("\n", 2)
    src.printcolors.print_value(logger, "Package path", path_targz, 2)
    
    return res