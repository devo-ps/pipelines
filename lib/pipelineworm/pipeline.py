import importlib
import logging
import re

import os

import yaml

from pipelineworm.exceptions import PipelineError
from pipelineworm.task import Task
from pipelineworm.var_processing import substitute_variables
from pluginworm.exceptions import PluginError
from pluginworm.manager import PluginManager

REQUIRED_DEF_KEYS = ['tasks']
log = logging.getLogger()

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
        return Pipeline(tasks, plugins)


    @staticmethod
    def from_yaml(file_path):
        if not isinstance(file_path, basestring):
            raise PipelineError('Unexpected argument type %s expecting string' % type(file_path))

        if not os.path.exists(file_path):
            raise PipelineError('PipelineDefinition: Pipeline definition file does not exist: %s' % file_path)

        with open(file_path) as f:
            try:
                pipeline_def = yaml.load(f)
            except yaml.YAMLError as e:
                log.exception(e)
                raise PipelineError('PipelineDefinition: Pipeline definition file is not valid YAML: %s' % e.message)

        vars = pipeline_def.get('vars', {})
        pipeline_def = substitute_variables(vars, pipeline_def)

        return Pipeline.form_dict(pipeline_def)

    def __init__(self, tasks, plugins):
        self.tasks = []
        self.plugin_mgr = PluginManager()

        self.load_plugins(plugins)
        self.load_tasks(tasks)


    def load_plugins(self, plugins):
        for plugin in plugins:
            self._load_plugin(plugin)

    def load_tasks(self, tasks):
        for i, task in enumerate(tasks):
            task_obj = Task.from_dict(task)
            if not task_obj.name:
                task_obj.name = 'Task-{}'.format(i+1)
            self.tasks.append(task_obj)

    def run(self):
        self.plugin_mgr.trigger('on_pipeline_start')

        for task in self.tasks:
            self._run_task(task)

        self.plugin_mgr.trigger('on_pipeline_finish')

    def _run_task(self, task):
        log.debug('Starting to execute task {}'.format(task.name))

        self.plugin_mgr.trigger('on_task_start', task)

        hook = '{}.execute'.format(task.executor)

        if self.plugin_mgr.get_plugin_count(hook) > 1:
            raise PipelineError('More than one executor plugins with same name {}'.format(hook))

        if self.plugin_mgr.get_plugin_count(hook) == 0:
            raise PipelineError('Can not find executor plugin for {}'.format(hook))

        results = self.plugin_mgr.trigger(hook, task.args)
        result = results[0]

        self.plugin_mgr.trigger('on_task_finish', task, result)
        log.debug('Task finished. Result: %s' % result)

    def _load_plugin(self, plugin):
        if isinstance(plugin, basestring):
            plugin = {'class': plugin}

        plugin_dict = plugin

        plugin_class = plugin_dict.pop('class')
        try:
            module, class_name = plugin_class.rsplit('.', 1)
            m = importlib.import_module(module)
        except ImportError:
            raise PluginError('Could not import plugin {}'.format(plugin_class))

        if not hasattr(m, class_name):
            raise PluginError('Could not find class for plugin {}'.format(plugin_class))

        self.plugin_mgr.register_plugin(getattr(m, class_name), plugin_dict)
