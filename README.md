# Pipelines

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
 - Ensure you have python and pip (you probably do)
 - Run: `pip install git+git://github.com/Wiredcraft/pipelines@dev`
 - Create a workspace anywhere in the filesystem (you'll have your task definitions, logs and temporary data here)
 - Run the backend. This is up to you but you can run it manually (for quick testing), inside a screen (bit better) or
   set up supervisord to run it (our recommendation). You can run it with: `pipelines api --workspace=(your-workspace) --username=(your-username) --password=(your-password)`
 - Add some pipeline definition files to the workspace (see the section below)

## Writing task definitions


The Pipeline definition file uses YAML syntax. Lets start with a simple example:

```yaml
---
## Variables are exposed to all the tasks
vars:
 code_branch: dev
 log_folder: "/var/log"

## Triggers define the automated ways to run the task
triggers: []

## Actions are the steps tbat are run for this pipeline
actions:
 - 'echo "Pre sleep task for {{ code_branch }}"'
 - "echo 'from time import sleep\nfor a in range(20):\n  print \"test\"\n  sleep(2)' | python"
 - 'echo "Post sleep task"'
 ```

__More complex actions__

The default mode for an action is a bash command. We also support more verbose style of defining actions where you can
set more options. Here is an example of an action that send a message to slack channel:
 ```
- type: slack
  message: 'Deployment finished with status {{ status }} for jekyllplus (api+client).'
  always_run: true
```

Explanation of fields:
 - `type` defines the execution method for this action, currently we only support `bash` (default) or `slack`.
 - `always_run` overrides the default behavior where if action fails the following tasks are not ran.
 - `message` is a slack specific field that defines the message that is posted to the slack channel.

__Webhooks__

If you want to run your pipeline by triggering it through a webhook you can enable it in the triggers section. For
example:
```
triggers:
  - type: webhook
```

If you open the web-UI you can see the webhook URL that was generated for this pipeline. You can for example configure
GitHub repository to trigger this task on every commit.

__Field prompts__

You can prompt users to manually input fields when they run the pipeine through the web-UI. To do this add a `prompt`
section to your pipeline definition, for example:
```
prompt:
 code_branch: dev
```

This example would ask the user to fill in a code_branch field when they try to run the pipeline with `dev` as default
value. The prompted value will override any values defines in the `vars` section.

__Simple step by step install__

**TODO**: replace by ansible playbook...

- `apt-get update`
- `apt-get upgrade`
- `apt-get install python-pip git`
- `pip install virtualenv`
- `mkdir /opt/virtualenvs && cd /opt/virtualenvs`
- `virtualenv pipelines`
- `source pipelines/bin/activate`
- `pip install git+git://github.com/Wiredcraft/pipelines@dev`

