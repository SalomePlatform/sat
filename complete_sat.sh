#!/bin/bash
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

# Completion Function for salomeTools (sat)

export SAT_PATH=$(cd `dirname "${BASH_SOURCE}"` && pwd)

_show_applications()
{
    local opts2=$(for x in `$SAT_PATH/sat config -nl`
        do
            echo ${x}
        done)

    # additional options for command working without applications
    case "${command}" in
        config)
            opts2=$(echo --list --value --edit --info $opts2)
            ;;
        log)
            opts2=$(echo --clean --full --last --terminal --last_compile --no_browser $opts2)
            ;;
        jobs)
            opts2=$(echo --name --only_jobs --list --completion --test_connection --input_boards --publish $opts2)
            ;;
        shell)
            opts2=$(echo --command --sat $opts2)
            ;;
        job)
            opts2=$(echo --jobs_config --name $opts2)
            ;;
        test)
            opts2=$(echo --base --display --grid --launcher --session $opts2)
            ;;
        package)
            opts2=$(echo --name --project --salometools $opts2)
            ;;
        find_duplicates)
            opts2=$(echo --path --exclude-file --exclude-extension --exclude-path $opts2)
            ;;
        template)
            opts2=$(echo --name --template --target --param --info $opts2)
            ;;
        base)
            opts2=$(echo --set $opts2)
            ;;
        init)
            opts2=$(echo --base --workdir --VCS --tag --log_dir --add_project --reset_projects $opts2)
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts2}" -- ${cur}) )
}

_show_products()
{
    if [[ $appli != $prev ]]
    then
        opts=$(for x in `$SAT_PATH/sat config $appli --completion`
            do echo ${x}; done)

        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
   fi
}

_salomeTools_complete()
{
    if [[ "${SAT_PATH}x" == "x" ]]
    then
        return 0
    fi

    local cur opts args command
    COMPREPLY=()
    argc="${COMP_CWORD}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # second argument => show available APPLICATION
    if [[ ${argc} > 1 ]]
    then
        command="${COMP_WORDS[1]}"
    fi

    if [[ ${argc} > 1 ]]
    then
        if [[ ${command%%-*} == "" ]]
        then
            command="${COMP_WORDS[2]}"
            argc="$((( argc - 1)))"
        fi
    fi

    # first argument => show available commands
    if [[ ${argc} == 1 ]]
    then
        opts="config log source patch prepare environ clean configure make makeinstall compile launcher run jobs job shell test package generate find_duplicates application template base check profile script init --help --overwrite --debug --verbose --batch --all_in_terminal --logs_paths_in_file"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    if [[ ${argc} == 2 ]]
    then
        # get list of APPLICATIONS
        _show_applications
        return 0
    fi
    
    # option depending on command
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    if [[ ${prev} == "--value" || ${prev} == "-v" ]]
    then
        if [[ ${argc} == 4 ]]
        then
            # with application
            opts=$(for x in `$SAT_PATH/sat config ${COMP_WORDS[COMP_CWORD-2]} -s ${COMP_WORDS[COMP_CWORD]}`
                do echo ${x} ; done)
            COMPREPLY=( $(compgen -W "${opts}" -S "." -- ${cur}) )
        else
            # without application
            opts=$(for x in `$SAT_PATH/sat config -s ${COMP_WORDS[COMP_CWORD]}`
                do echo ${x} ; done)
            COMPREPLY=( $(compgen -W "${opts}" -S "." -- ${cur}) )
        fi
        
        return 0
    fi
      
    # show list of products
    if [[ ${prev} == "--products" || ${prev} == "-p" || ${prev} == "--info" || ${prev} == "-i" ]]
    then
        appli="${COMP_WORDS[2]}"
        if [[ ${command} != "source" ]]
        then
            opts=$(for x in `$SAT_PATH/sat config $appli --completion`
                do echo ${x}; done)

               COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
        fi
    fi

    # show argument for each command
    case "${command}" in
        config)
            opts="--value --list --copy --edit --no_label --info --check_system --show_patchs --show_dependencies --show_install --show_properties"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0        
            ;;
        log)
            opts="--clean --last --terminal --last --last_compile --no_browser"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        clean)
            opts="--products --sources --build --install --generated --package --all --sources_without_dev --properties"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        source)
            opts="--products --properties"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        patch)
            opts="--products --properties"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        prepare)
            opts="--products --properties --force --force_patch --complete"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        environ)
            opts="--products --shell --prefix --target"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        configure)
            opts="--products --option"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        make)
            opts="--products --option"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        makeinstall)
            opts="--products"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        compile)
            opts="--products --force --properties --with_fathers --with_children --clean_all --clean_make --install_flags --show --stop_first_fail --check --clean_build_after"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        launcher)
            opts="--products --name --exe --catalog --gencat --no_path_init --use_mesa"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        jobs)
            opts="--name --only_jobs --list --completion --test_connection --input_boards --publish"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        shell)
            opts="--command"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        job)
            opts="--jobs_config --name"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        test)
            opts="--base --launcher --grid --session --display"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        package)
            opts="--name --binaries --sources --exe --project --salometools --force_creation --add_files --with_vcs --ftp --without_property"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        generate)
            opts="--products --yacsgen"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        find_duplicates)
            opts="--path --sources --exclude-file --exclude-extension --exclude-path"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        application)
            opts="--name --catalog --target --gencat --module"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        template)
            opts="--name --template --target --param --info"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        base)
            opts="--set"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        profile)
            opts="--prefix --name --force --no_update --version --slogan"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        script)
            opts="--products --nb_proc"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        check)
            opts="--products"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        init)
            opts="--base --workdir --VCS --tag --log_dir --add_project --reset_projects"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        *) return 0 ;;
    esac
    
}

# activation of auto-completion for the sat command
complete -F _salomeTools_complete sat
complete -F _salomeTools_complete ./sat

