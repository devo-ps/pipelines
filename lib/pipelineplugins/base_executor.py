import json

from pipelineworm.exceptions import PipelineError
from pluginworm.base_plugin import BasePlugin

EXECUTION_SUCCESSFUL = 0
EXECUTION_FAILED = 1

class BaseExecutorPlugin(BasePlugin):
    dry_run = False

    def call(self, *args, **kwargs):
        result =  self.execute(*args, **kwargs)
        if not isinstance(result, ExecutionResult):
            raise PipelineError('Executor did not return type ExecutionResult, got {}'.format(type(result)))

        return result

    def execute(self, command):
        print 'Running executor with command: %s' % command

class ExecutionResult(object):
    def __init__(self, status, message=''):
        self.status = status
        self.message = message

    def isSuccessful(self):
        return self.status == EXECUTION_SUCCESSFUL

    def __str__(self):
        obj = {
            'status': self.status,
            'message': self.message
        }
        return json.dumps(obj)