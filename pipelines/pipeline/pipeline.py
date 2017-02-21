import importlib
import logging
import os
import sys

import yaml

from jinja2 import TemplateError
from dotmap import DotMap

from pipelines.pipeline.task import TaskResult, EXECUTION_FAILED
from pipelines.plugins import builtin_plugins
from pipelines.pipeline.exceptions import PipelineError
from pipelines.pipeline.task import Task
from pipelines.pipeline.var_processing import substitute_variables
from pipelines.plugin.exceptions import PluginError
from pipelines.plugin.manager import PluginManager
from schema import Or, Schema, Optional

from pipelines.utils import conf_logging, deepmerge

log = logging.getLogger('pipelines')

PIPELINE_STATUS_OK = 'success'
PIPELINE_STATUS_FAIL = 'failure'

DEFAULT_PLUGINS = [
    'stdout_logger',
    'bash',
    'python',
    'status_logger',
    'slack'
    # 'webhook_logger'
]

DEFAULTS = {
    'task': {
        'type': 'bash',
        'param': 'cmd',
    }
}

PIPELINES_SCHEMA = Schema({
    Optional('vars'): {
        Optional(basestring): Or(
            Optional(basestring),
            Optional(dict)
        )
    },
    Optional('name'): basestring,
    'actions': [
        Or(
            basestring,
            {
                'type': basestring,
                Optional('cmd'): basestring,
                Optional('always_run'): bool,
                Optional('message'): basestring,
                Optional(basestring): basestring  # Allow custom keys for actions
            }
        )
    ],
    Optional('plugins'): [
        Optional(basestring)
    ],
    Optional('prompt'): {
        Optional(basestring): Or(
            Optional(basestring),
            {
                'type': Or('text', 'select'),
                Optional('default'): basestring,
                Optional('options'): [basestring],
            }
        )
    },
    Optional('triggers'): [{
        'type': Or('webhook', 'cron'),
        Optional('schedule'): basestring
    }]
})

class Pipeline(object):

    @staticmethod
    def form_dict(definition_dict):

        PIPELINES_SCHEMA.validate(definition_dict)

        if 'vars' not in definition_dict:
            definition_dict['vars'] = {}
        if 'params' not in definition_dict:
            definition_dict['params'] = {}
        if 'triggers' not in definition_dict:
            definition_dict['triggers'] = {}

        if not isinstance(definition_dict, dict):
            raise PipelineError('Unexpected argument type %s expecting dict' % type(definition_dict))

        tasks = definition_dict['actions']
        plugins = definition_dict.get('plugins', [])

        return Pipeline(tasks, plugins, context=definition_dict)


    @staticmethod
    def from_yaml(file_path, params={}):
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
                raise PipelineError('PipelineDefinition: Pipeline definition file is not valid YAML: %s - %s' % (file_path, err_msg))

        pipeline_def['vars'] = deepmerge(pipeline_def.get('vars', {}), params or {})

        # Substitute {{ }} variables in tasks
        # vars = pipeline_def.get('vars', {})
        # pipeline_def = substitute_variables(vars, pipeline_def)

        return Pipeline.form_dict(pipeline_def)

    def __init__(self, tasks, plugins, context):
        self.tasks = []
        self.context = context

        self.plugin_mgr = PluginManager()
        plugins.extend(DEFAULT_PLUGINS)
        self.load_plugins(plugins)

        self.load_tasks(tasks)

    def load_plugins(self, plugins):
        log.debug("Loading plugins: %s" % plugins)
        for plugin in plugins:
            self._load_plugin(plugin)

    def load_tasks(self, tasks):
        for i, task in enumerate(tasks):
            normalized_task = self._normalize_task_dict(task)
            if not self._task_executor_valid(normalized_task['type']):
                raise PipelineError('Unsupported task type: %s' % normalized_task['type'])
            task_obj = Task.from_dict(normalized_task)
            if not task_obj.name:
                task_obj.name = 'Task-{}'.format(i + 1)
            self.tasks.append(task_obj)

    def _task_executor_valid(self, task_type):
        return bool(self.plugin_mgr.get_plugin('{}.execute'.format(task_type)))


    def run(self):
        log.debug('Run pipeline. params: {}'.format(self.context))
        pipeline_context ={
            'results': [],
            'vars': self.context.get('vars', {}),
            'status': PIPELINE_STATUS_OK,
            'prev_result': None,
            'params': self.context.get('params', {})
        }

        pipeline_context = DotMap(pipeline_context)

        self.plugin_mgr.trigger('on_pipeline_start', pipeline_context)
        log.debug('Pipeline starting. context: %s' % pipeline_context)
        for task in self.tasks:
            if self._should_run(task, pipeline_context):
                result_obj = None
                try:
                    task.args = substitute_variables(pipeline_context, task.args)
                except TemplateError as e:
                    result_obj = TaskResult(EXECUTION_FAILED, e.message)

                if not result_obj:
                    result_obj = self._run_task(task)

                pipeline_context.results.append(result_obj)
                pipeline_context['prev_result'] = result_obj

                if pipeline_context['status'] == PIPELINE_STATUS_OK and result_obj.get('status') != 0:
                    pipeline_context['status'] = PIPELINE_STATUS_FAIL
            else:
                log.debug('Skipping task: {}'.format(task.name))
        log.debug('Pipeline finished. Status: {}'.format(pipeline_context['status']))
        self.plugin_mgr.trigger('on_pipeline_finish', pipeline_context)

    def _should_run(self, task, pipeline_context):

        if task.always_run:
            return True

        if pipeline_context['status'] != PIPELINE_STATUS_OK:
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

        try:
            results = self.plugin_mgr.trigger(event_name, task.args)  # Run the task
        except KeyboardInterrupt as e:
            raise
        except Exception as e:
            log.warning('Unexpected error running task: %s' % e)
            log.exception(e)
            results = [TaskResult(EXECUTION_FAILED, 'Unknown Error: %s' % e)]

        result = results[0]

        if not result:
            raise PipelineError('Result still missing %s' % result)

        self.plugin_mgr.trigger('on_task_finish', task, result)
        log.debug('Task finished. Result: %s' % result)

        return result

    def _load_plugin(self, plugin_str):
        if not isinstance(plugin_str, basestring):
            raise PluginError('Plugins must be a string, got {}'.format(plugin_str))

        plugin_class = self._resolve_plugin_class(plugin_str)
        self.plugin_mgr.register_plugin(plugin_class, self.context.get('vars'))


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

def _parse_class(plugin_path):
    if '.' not in plugin_path:
        raise PluginError('Invalid plugin: %s' % plugin_path)
    try:
        module, class_name = plugin_path.rsplit('.', 1)
        m = importlib.import_module(module)

    except ImportError:
        raise PluginError('Could not import plugin {}'.format(plugin_path))

    if not hasattr(m, class_name):
        raise PluginError('Could not find class for plugin {}'.format(plugin_path))

    return getattr(m, plugin_path)

if __name__ == '__main__':
    conf_logging()

    if len(sys.argv) != 2:
        raise PipelineError('Wrong number of arguments')

    log_file = None
    if 'LOG_FILE' in os.environ:
        log_file = os.environ['LOG_FILE']

    pipeline_yaml_path = sys.argv[-1]

    params = {}
    if log_file:
        params['log_file'] = log_file

    pipe = Pipeline.from_yaml(pipeline_yaml_path, params=None)
    pipe.run()
