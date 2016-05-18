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
            opts2=$(echo --clean --full --last --terminal $opts2)
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts2}" -- ${cur}) )
}

_show_products()
{
    if [[ $appli != $prev ]]
    then
        opts=$(for x in `$SAT_PATH/sat -s config $appli -nv APPLICATION.products`
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
        opts="config log testcommand source patch prepare environ clean configure --help"
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
    if [[ ${prev} == "--product" || ${prev} == "-p" ]]
    then
        appli="${COMP_WORDS[2]}"
        if [[ ${command} != "source" ]]
        then
            opts=$(for x in `$SAT_PATH/sat config $appli -nv APPLICATION.products`
                do echo ${x}; done)

               COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
        fi
    fi

    # show argument for each command
    case "${command}" in
        config)
            opts="--value --list --copy --edit --no_label"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0        
            ;;
        log)
            opts="--clean --last --terminal --last"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        clean)
            opts="--products --sources --build --install --all --sources_without_dev"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        source)
            opts="--products"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        patch)
            opts="--products"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        prepare)
            opts="--products --force --force_patch"
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
        *) return 0 ;;
    esac
    
}

# activation of auto-completion for the sat command
complete -F _salomeTools_complete sat
complete -F _salomeTools_complete ./sat

