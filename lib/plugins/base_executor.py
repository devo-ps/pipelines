from pipelines.pipeline.exceptions import PipelineError
from pipelines.pipeline.task import TaskResult
from pipelines.plugin.base_plugin import BasePlugin

class BaseExecutorPlugin(BasePlugin):
    dry_run = False

    def call(self, *args, **kwargs):
        result = self.execute(*args, **kwargs)
        if not isinstance(result, TaskResult):
            raise PipelineError('Executor did not return type ExecutionResult, got {}'.format(type(result)))

        return result

    def execute(self, command):
        print 'Running executor with command: %s' % command
