#!/usr/bin/env bash

set -e

install_pipelines(){

    echo "Checking dependencies..."
    if [ ! -n "$(which python)" ]; then
        echo "Need python installed !"
        exit 1
    fi
    if [ ! -n "$(which pip)" ]; then
        echo "Need pip installed !"
        exit 1
    fi
    if [ ! -n "$(which git)" ]; then
        echo "Need git installed !"
        exit 1
    fi

    echo "Installing pipelines..."
    echo -n "Which version of pipelines to install? (dev/stable)"
    read version
    if [ -z "$version" ]; then
        version=stable
    fi

    if [ "$version" == "dev" ]; then
        sudo pip install git+git://github.com/Wiredcraft/pipelines@dev > /dev/null
    elif [ "$version" == "stable" ]; then
        sudo pip install pipelines
    else
        echo "Invalid version !"
        exit 1
    fi

    echo "Creating user..."
    id pipelines > /dev/null 2>&1
    if [ $? -nq 0 ]; then
        sudo useradd -m -d /var/lib/pipelines -s /bin/false pipelines
        sudo -u pipelines ssh-keygen -P '' -f /var/lib/pipelines/.ssh/id_rsa -b 2048 -q
        echo "Pipelines' SSH public KEY:"
        echo ""
        sudo cat /var/lib/pipelines/.ssh/id_rsa.pub
        echo ""
    fi

    echo "Creating workspace..."
    sudo mkdir -p /var/lib/pipelines/workspace
    sudo chown -R pipelines:pipelines /var/lib/pipelines

    echo ""
    pipelines --version
    echo ""

    echo "Successfully installed"
}

install_pipelines "$@"