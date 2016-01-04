# Pipelines Command Line Tool

Pipelines is a simple tool to manage running tasks.

Pipeline definition file uses YAML syntax. Example:

```yaml
dry_run: False  # TODO
vars:
  workspace: 'test'
tasks:
 - executor: executors.dummy
   cmd: "anything"
 - executor: executors.bash
   cmd: "sleep 1 && echo {{workspace}} > ~/hhh"
 - executor: executors.python
   virtualenv: /Users/juha/work/getpipeline/.venv
   workdir: /Users/juha/work/getpipeline/test
   script: test_script.py
plugins:
  - pipelineplugins.dummy_executor.DummyExecutor
  - pipelineplugins.stdout_logger.StdoutLogger
  - class: pipelineplugins.webhook_logger.WebhookLogger
    webhook_url: 'https://hooks.slack.com/services/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'
  - pipelineplugins.bash_executor.BashExecutor
  - pipelineplugins.python_executor.PythonExecutor
 ```

## Installation

 To install simply run:
 - `pip install git+git://github.com/Wiredcraft/getpipelines`

## Usage

  - Normal usage: `pline sample_pipe.yaml`
  - With more verbosity: `pline sample_pipe.yaml --verbose`

## Plugins

Currently package includes following pugins:
 - Bash executor: Allow to run bash commands
 - Python executor: Run python scripts, supports virtualenv
 - STDOUT logger: Write log to stdout
 - Webhook logger: Send a report at the end of pipeline to webhook (can be used for slack integration).
 - Dummy executor: Just used for testing

There are event plugins that can hook to pipeline lifecycle with following events:
 - `on_pipeline_start`
 - `on_task_start`
 - `on_task_finish`
 - `on_pipeline_finish`

 The executor plugins are specialized plugins that implement `execute` function.

