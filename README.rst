Pipelines
=========

``Pipelines`` is a tool that executes - pipelines!

Consider pipelines as sequence of tasks, Pipelines lets you trigger them simply.

``Pipelines`` comes all bundled with:

- an API
- a web frontend
- a CLI

``Pipelines`` is primarily developed to run on Linux / MacOS. Windows support is not available at the moment.

Installation
============

.. code-block:: bash

    pip install pipelines


Or get the latest dev version from `Github <https://github.com/Wiredcraft/pipelines>`_ and run `pip install .` from within the cloned repo. 

Configuration
=============

The configuration files can be found in `/etc/pipelines/`.

``Currently not supported! too bad, come back at 0.1.0!``

pipelines.conf
--------------

.. code-block:: bash

    # Listening address / port
    host: 127.0.0.1
    port: 8888
    
    # Admin user
    user: admin
    pass: admin
    
    # Enable web interface
    ui: True
    
    # 
    # Workspace Directory
    # 
    # Where all the pipelines and runs will be stored
    workspace: /var/lib/pipelines/workspace
    
    # Log
    log_file: /var/log/pipelines/pipelines.log
    log_level: error

Run standalone
--------------

Start the API with the following:

.. code-block:: bash

    pipelines api

Run as a daemon
---------------

Create a dedicated user to run pipelines

.. code-block:: bash

    # Create a pipelines user
    useradd -m -d /var/lib/pipelines -s /sbin/nologin pipelines
    
    # Create the workspace folder (optional)
    mkdir /var/lib/pipelines/workspace
    chown -R pipelines. /var/lib/pipelines
    
    # Create a SSH key pair (optional)
    sudo -u pipelines ssh-keygen


You may want to rely on supervisord to run the API.

.. code-block:: bash

    # Ubuntu / Debian
    apt-get install supervisor

    # CentOS / RedHat (to confirm)
    yum install supervisord


Copy and adapt de config file from `etc/supervisor/pipelines.conf` to `/etc/supervisor`

.. code-block:: bash

    # Update and reload supervisord
    supervisorctl reread
    supervisorctl update
    supervisorctl start pipelines


Access the web interface at http://localhost:8888/web

Pipelines descriptions
======================

Pipeline definition file uses YAML syntax. Example:

.. code-block:: yaml

    tasks:
      - executor: executors.dummy
        cmd: "anything"
      - executor: executors.bash
        cmd: "sleep 1 && echo {{workspace}} > ~/hhh"
      - executor: executors.python
        virtualenv: /Users/juha/work/getpipeline/.venv
        workdir: /Users/juha/work/getpipeline/test
        script: test_script.py

Roadmap
=======

No definitive roadmap for the moment, mainly focusing on having a lean code base (heavy refactoring to come).

Among the possible features:

- better web UI
- better webhook management
- better management of the tasks (celery?)
- better CLI 
- toolbar 
- auth
- etc.
