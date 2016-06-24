import importlib
import json
import logging
import re

import os

import sys

import yaml

import pipelines.plugins
from dotmap import DotMap
from pipelines.plugins import builtin_plugins
from pipelines.pipeline.exceptions import PipelineError
from pipelines.pipeline.task import Task
from pipelines.pipeline.var_processing import substitute_variables
from pipelines.plugin.exceptions import PluginError
from pipelines.plugin.manager import PluginManager
from schema import Or, Schema, Optional

REQUIRED_DEF_KEYS = ['tasks']
log = logging.getLogger()

DEFAULT_PLUGINS = [
    'stdout_logger',
    'bash',
    'python',
    'status_logger'
]

DEFAULTS = {
    'task': {
        'type': 'bash',
        'param': 'cmd',
    }
}

PIPELINES_SCHEMA = Schema({
    'vars': {
        basestring: basestring
    },
    'tasks': [
        Or(basestring, {
            'type': basestring,
            'cmd': basestring
        })
    ],
    'plugins': [
        basestring
    ],
    Optional('triggers'): {
        'webhook': 'basestring'
    }
})

class Pipeline(object):

    @staticmethod
    def form_dict(definition_dict):
        if not isinstance(definition_dict, dict):
            raise PipelineError('Unexpected argument type %s expecting dict' % type(definition_dict))

        for key in REQUIRED_DEF_KEYS:
            if key not in definition_dict:
                raise PipelineError('Pipeline definition is missing {}' % type(definition_dict))

        tasks = definition_dict['tasks']
        plugins = definition_dict.get('plugins', [])
        return Pipeline(tasks, plugins, state=definition_dict)


    @staticmethod
    def from_yaml(file_path, params):
        if not isinstance(file_path, basestring):
            raise PipelineError('Unexpected argument type %s expecting string' % type(file_path))

        if not os.path.exists(file_path):
            raise PipelineError('PipelineDefinition: Pipeline definition file does not exist: %s' % file_path)

        with open(file_path) as f:
            try:
                pipeline_def = yaml.load(f)
            except yaml.YAMLError as e:
                log.exception(e)
                err_msg = e.problem
                err_msg += ' (line: {})'.format(e.problem_mark.line)
                raise PipelineError('PipelineDefinition: Pipeline definition file is not valid YAML: %s' % err_msg)


        PIPELINES_SCHEMA.validate(pipeline_def)

        if 'vars' not in pipeline_def:
            pipeline_def['vars'] = {}

        # Merge parameters to variables dict
        pipeline_def['vars'].update(params)

        # Substitute {{ }} variables in tasks
        vars = pipeline_def.get('vars', {})
        pipeline_def = substitute_variables(vars, pipeline_def)

        return Pipeline.form_dict(pipeline_def)

    def __init__(self, tasks, plugins, state):
        self.tasks = []
        self.state = state

        self.plugin_mgr = PluginManager()
        plugins.extend(DEFAULT_PLUGINS)
        self.load_plugins(plugins)

        self.load_tasks(tasks)

    def load_plugins(self, plugins):
        for plugin in plugins:
            self._load_plugin(plugin)

    def load_tasks(self, tasks):
        for i, task in enumerate(tasks):
            normalized_task = self._normalize_task_dict(task)
            task_obj = Task.from_dict(normalized_task)
            if not task_obj.name:
                task_obj.name = 'Task-{}'.format(i + 1)
            self.tasks.append(task_obj)

    def run(self, trigger_data={}):
        self.plugin_mgr.trigger('on_pipeline_start')

        pipeline_context = DotMap({
            'results': [],
            'trigger_data': trigger_data,
            'status': 0,
            'prev_result': None
        })
        for task in self.tasks:
            if self._should_run(task, pipeline_context):
                result_obj = self._run_task(task)
                pipeline_context.results.append(result_obj)
                pipeline_context['prev_result'] = result_obj
                if result_obj.get('status') != 0:
                    pipeline_context['status'] = result_obj.get('status')
            else:
                log.debug('Skipping task: {}'.format(task.name))

        self.plugin_mgr.trigger('on_pipeline_finish')

    def _should_run(self, task, pipeline_context):

        if task.always_run:
            return True

        if pipeline_context['status'] != 0:
            return False

        return True

    def _validate_executor_plugin(self, event_name):
        if self.plugin_mgr.get_plugin_count(event_name) > 1:
            raise PipelineError('More than one executor plugins with same name {}'.format(event_name))

        if self.plugin_mgr.get_plugin_count(event_name) == 0:
            raise PipelineError('Can not find executor plugin for {}'.format(event_name))

    def _run_task(self, task):
        log.debug('Starting to execute task {}'.format(task.name))

        self.plugin_mgr.trigger('on_task_start', task)

        event_name = '{}.execute'.format(task.executor)

        self._validate_executor_plugin(event_name)

        # Run the executor
        status = 0
        try:
            results = self.plugin_mgr.trigger(event_name, task.args)
        except Exception as e:
            log.warning('Unexpected error running task: %s' % e)
            log.exception(e)
            status = 1

        result = results[0]

        self.plugin_mgr.trigger('on_task_finish', task, result)
        log.debug('Task finished. Result: %s' % result)

        return {'output': result, 'status': status}

    def _load_plugin(self, plugin_str):
        if not isinstance(plugin_str, basestring):
            raise PluginError('Plugins must be a string, got {}'.format(plugin_str))

        plugin_class = self._resolve_plugin_class(plugin_str)
        self.plugin_mgr.register_plugin(plugin_class, self.state.get('vars'))


    def _resolve_plugin_class(self, plugin_name):
        if plugin_name in builtin_plugins:
            return builtin_plugins[plugin_name]

        return _parse_class(plugin_name)

    def _normalize_task_dict(self, task):
        # Ensure dict
        if not isinstance(task, dict):
            task = {
                'type': DEFAULTS['task']['type'],
                DEFAULTS['task']['param']: task
            }

        # Ensure type
        if 'type' not in task:
            task['type'] = DEFAULTS['task']['type']

        return task

def _parse_class(class_path):
    plugin_dict = class_path

    plugin_class = plugin_dict.pop('class')
    try:
        module, class_name = plugin_class.rsplit('.', 1)
        m = importlib.import_module(module)

    except ImportError:
        raise PluginError('Could not import plugin {}'.format(plugin_class))

    if not hasattr(m, class_name):
        raise PluginError('Could not find class for plugin {}'.format(plugin_class))

    return getattr(m, plugin_class)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Wrong number of arguments'
        exit(1)

    pipeline_yaml_path = sys.argv[1]

    if not pipeline_yaml_path or not pipeline_yaml_path.endswith('yaml') or not os.path.exists(pipeline_yaml_path):
        print 'Missing pipeline file'
        exit(1)

    pipe = Pipeline.from_yaml(pipeline_yaml_path, params={})
    pipe.run(trigger_data={})
