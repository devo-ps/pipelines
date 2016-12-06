#!/usr/bin/env bash

set -e

install_pipelines(){

    echo "Checking dependencies..."
    if [ ! -n "$(which python)" ]; then
        echo "Need python installed !";
        exit 1;
    fi
    if [ ! -n "$(which pip)" ]; then
        echo "Need pip installed !";
        exit 1;
    fi
    if [ ! -n "$(which git)" ]; then
        echo "Need git installed !"
        exit 1;
    fi

    echo "Installing pipelines..."
    sudo pip install git+git://github.com/Wiredcraft/pipelines@dev > /dev/null

    echo "Creating user..."
    id pipelines > /dev/null 2>&1
    if [ ! $? -eq 0 ]; then
        sudo useradd -m -d /var/lib/pipelines -s /bin/false pipelines
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