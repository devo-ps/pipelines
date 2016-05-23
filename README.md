# Pipelines

**Pipelines** is a tool that executes - pipelines!

Consider pipelines as sequence of tasks, Pipelines lets you trigger them simply.

**Pipelines** comes all bundled with:
- an API
- a web frontend
- a CLI

**Pipelines** is primarily developed to run on Linux / MacOS. Windows support is not available at the moment.

## Installation

```
pip install pipelines
```

Or get the latest dev version from [Github](https://github.com/Wiredcraft/pipelines) and run `pip install .` from within the cloned repo. 

## Configuration

The configuration files can be found in `/etc/pipelines/`.

**Currently not supported! too bad, come back at 0.0.3!**

### pipelines.conf

```
# Listening address / port
host: 127.0.0.1
port: 8888

# Admin user
user: admin
pass: admin

# Enable web interface
ui: True

# Workspace
workspace: /var/lib/pipelines/workspace
pipelines: /var/lib/pipelines/pipelines

# Log
log_file: /var/log/pipelines/pipelines.log
log_level: error
```

## Run standalone

Start the API with the following:

```
pipelines api
```

## Run as a daemon

Create a dedicated user to run pipelines

```
useradd -m -d /var/lib/pipelines -s /sbin/nologin pipelines
```

You may want to rely on supervisord to run the API.

```
# Ubuntu / Debian
apt-get install supervisor

# CentOS / RedHat
yum install supervisord
```

Copy and adapt de config file from `etc/supervisor/pipelines.conf` to `/etc/supervisor`

```
# Update and reload supervisord
supervisorctl reread
supervisorctl update
supervisorctl start pipelines
```

Access the web interface at http://localhost:8888/web

## pipelines descriptions

Pipeline definition file uses YAML syntax. Example:

```yaml
tasks:
  - executor: executors.dummy
    cmd: "anything"
  - executor: executors.bash
    cmd: "sleep 1 && echo {{workspace}} > ~/hhh"
  - executor: executors.python
    virtualenv: /Users/juha/work/getpipeline/.venv
    workdir: /Users/juha/work/getpipeline/test
    script: test_script.py
```

