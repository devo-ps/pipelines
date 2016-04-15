from pipelineworm.exceptions import PipelineError
from pipelineworm.task import TaskResult
from pluginworm.base_plugin import BasePlugin

class BaseExecutorPlugin(BasePlugin):
    dry_run = False

    def call(self, *args, **kwargs):
        result =  self.execute(*args, **kwargs)
        if not isinstance(result, TaskResult):
            raise PipelineError('Executor did not return type ExecutionResult, got {}'.format(type(result)))

        return result

    def execute(self, command):
        print 'Running executor with command: %s' % command
