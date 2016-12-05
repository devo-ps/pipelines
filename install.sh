#!/usr/bin/env bash

set -e

install_pipelines(){

    echo "Checking dependencies..."
    if [ ! -n "$(which python)" ]; then
        echo "Need python !";
        exit 1;
    fi
    if [ ! -n "$(which pip)" ]; then
        echo "Need pip !";
        exit 1;
    fi
    if [ ! -n "$(which git)" ]; then
        echo "Need git !"
        exit 1;
    fi

    echo "Installing pipelines..."
    pip_install="pip install git+git://github.com/Wiredcraft/pipelines@dev"
    eval $pip_install

    echo "Creating user..."
    user=`getent passwd pipelines > /dev/null`
    if [ $user -eq 0 ]; then

        `useradd -m -d /var/lib/pipelines -s /bin/false pipelines`
    fi

    echo "Creating workspace..."
    `mkdir -p /var/lib/pipelines/workspace > /dev/null`
    `chown -R pipelines. /var/lib/pipelines > /dev/null`

    echo `pipelines --version`
    echo "Successfully installed"
}

install_pipelines "$@"