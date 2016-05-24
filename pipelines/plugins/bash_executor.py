import json
import logging

from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError
from sh import ErrorReturnCode

log = logging.getLogger()

class BashExecuteError(PluginError):
    def __init__(self, stderr, code):
        self.stderr = stderr
        self.code = code


class BashExecutor(BaseExecutorPlugin):
    hook_prefix = 'bash'
    hooks = ('execute',)

    def __init__(self, log_file=None):
        self.log_file = log_file

    def _parse_args_dict(self, args_dict):
        if 'cmd' not in args_dict:
            raise PluginError('BashExecutor got incorrect arguments, got: {}'.format(
                args_dict.keys()
            ))

        return args_dict['cmd']

    def execute(self, args_dict):

        cmd = self._parse_args_dict(args_dict)

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)

        try:
            stdout = self._run_bash(cmd)
            status = EXECUTION_SUCCESSFUL
        except BashExecuteError as e:
            status = EXECUTION_FAILED
            stdout = e.stderr

        return TaskResult(status, stdout)


    def _run_bash(self, bash_input):
        log.debug('Running bash command: "{}"'.format(bash_input))

        from sh import bash
        stdout = ''
        f = None
        if self.log_file:
            f = open(self.log_file, 'w+')

        try:
            for line in bash(_in=bash_input, _iter=True):
                log.debug('BashExec stdout: {}'.format(line))
                stdout += line
                if f:
                    f.write(line)
        except ErrorReturnCode as e:
            log.debug('BashExec failed')
            raise BashExecuteError(e.stderr, e.exit_code)

        return stdout

    @classmethod
    def from_dict(cls, conf_dict):
        return cls(conf_dict.get('log_file'))

if __name__ == '__main__':
    from pluginworm.utils import setup_logging
    setup_logging(logging.WARNING)
    b = BashExecutor()
    r = b.execute({'cmd': 'echo "test" && echo "test2"'})

    print r.status
    print r.message
