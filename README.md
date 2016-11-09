# Pipelines

![image](https://cloud.githubusercontent.com/assets/919180/20129399/425a0c2a-a68a-11e6-82ef-b252424a4b48.png)

## What is Pipelines

Pipelines is a simple tool with a web UI to manage running tasks. It supports triggering tasks manually throught a Web
UI or using webhooks.

Pipelines is composed of three components:
 - __Web UI__: User interface that allows users to run tasks, inspect logs and show the task details. It also support
   username/password authentication.
 - __Pipelines API__: This is the backend for the Web UI and webh
 - __Pipelines library__: This component includescore logic for running pipelies such as reading task definitions,
   handling logging and running the pipelines.


## Getting started

In order to run the pipelines on your own server you need to do the following:
 - Ensure you have python (2.7) and pip (you probably do)
 - Run: `pip install git+git://github.com/Wiredcraft/pipelines@dev`
 - Create a workspace anywhere in the filesystem (you'll have your task definitions, logs and temporary data here)
 - Run the backend. This is up to you but you can run it manually (for quick testing), inside a screen (bit better) or
   set up supervisord to run it (our recommendation). You can run it with: `pipelines api --workspace=(your-workspace) --username=(your-username) --password=(your-password)`
 - Add some pipeline definition files to the workspace (see the section below)

## Writing task definitions


The Pipeline definition file uses YAML syntax. Lets start with a simple example:

`example-pipeline.yaml`:
```yaml
---
# Pipeline definitions are standard yaml and you can include comments inside

# Variables are exposed to all actions through {{ varname }} syntax.
vars:
 code_branch: dev
 log_folder: "/var/log"

# Triggers define the automated ways to run the task. Only webhook is supported for now.
triggers:
 - webhook

# Actions are the steps that are run for this pipeline. The default action plugin is bash, but you can use others by
# defining the "type" field.
actions:
 - 'echo "Starting task for {{ code_branch }}"'
 - type: bash
   cmd: "echo 'less compact way to define actions'"
 - 'ls -la /tmp'
 ```

__More complex actions__

The default mode for an action is a bash command. We also support more verbose style of defining actions where you can
set more options.

Currently supported action types:
 - bash: run bash command
 - slack: send message to slack through webhook
 - python: write inline script or run python script inside a virtualenv

Here is an example of an action that send a message to slack channel:
 ```
- type: slack
  message: 'Deployment finished with status {{ status }} for jekyllplus (api+client).'
  always_run: true
```

Explanation of fields:
 - `type` defines the execution method for this action, currently we only support `bash` (default) or `slack`.
 - `always_run` overrides the default behavior where if action fails the following tasks are not ran.
 - `message` is a slack specific field that defines the message that is posted to the slack channel.


Example python action:
```
 - type: python
   script: |
     import json
     a = {'test': 'value', 'array': [1,2,3]}
     print json.dumps(a, indent=2)
 - type: python
   virtualenv:  test/files/test_venv
   file: 'test/files/test_dopy_import.py'
```

Explanation of the fields:
 - `script`: raw python code to be run directly
 - `virtualenv`: run the python code inside a virtualenv
 - `file`: run a python file (can not be used together with "script" field).


__Webhooks__

If you want to run your pipeline by triggering it through a webhook you can enable it in the triggers section. For
example:
```
triggers:
  - type: webhook
```

If you open the web-UI you can see the webhook URL that was generated for this pipeline in the "Webhook" tab. You can
for example configure GitHub repository to call this url after every commit.

__Field prompts__

You can prompt users to manually input fields when they run the pipeine through the web-UI. To do this add a `prompt`
section to your pipeline definition. The prompt fields will override the variables from the "vars" section.

For example:
```
prompt:
 code_branch: dev
```

This example would ask the user to fill in a code_branch field when they try to run the pipeline with `dev` as default
value. The prompted value will override any values defines in the `vars` section.

__Simple step by step install for Ubuntu server__

**TODO**: replace by ansible playbook...

- `apt-get update`
- `apt-get upgrade`
- `apt-get install python-pip git`
- `pip install virtualenv`
- `mkdir /opt/virtualenvs && cd /opt/virtualenvs`
- `virtualenv pipelines`
- `source pipelines/bin/activate`
- `pip install git+git://github.com/Wiredcraft/pipelines@dev`

