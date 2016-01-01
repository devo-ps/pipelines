from pipelineplugins.base_executor import ExecutionResult, EXECUTION_SUCCESSFUL, BaseExecutorPlugin
from pluginworm.exceptions import PluginError


class DummyExecutor(BaseExecutorPlugin):
    hook_prefix = 'executors.dummy'
    hooks = ('execute',)

    def _parse_args_dict(self, args_dict):
        if 'cmd' not in args_dict:
            raise PluginError('DummyExecutor got incorrect arguments, got: {}'.format(
                args_dict.keys()
            ))

        return args_dict['cmd']

    def execute(self, args_dict):

        cmd = self._parse_args_dict(args_dict)

        if self.dry_run:
            return ExecutionResult(EXECUTION_SUCCESSFUL, 'Dry run')

        print 'Running executor with command: %s' % cmd
        return ExecutionResult(EXECUTION_SUCCESSFUL, 'Dummy execute completed')
