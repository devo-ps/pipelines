import logging

from pipelineplugins.base_executor import BaseExecutorPlugin
from pipelineworm.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pluginworm.exceptions import PluginError
from sh import ErrorReturnCode

log = logging.getLogger()

class BashExecuteError(PluginError):
    def __init__(self, stderr, code):
        self.stderr = stderr
        self.code = code


class BashExecutor(BaseExecutorPlugin):
    hook_prefix = 'bash'
    hooks = ('execute',)

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
        try:
            for line in bash(_in=bash_input):
                log.debug('BashExec stdout: {}'.format(line))
                stdout += line
        except ErrorReturnCode as e:
            log.debug('BashExec failed')
            raise BashExecuteError(e.stderr, e.exit_code)

        return stdout



if __name__ == '__main__':
    from pluginworm.utils import setup_logging
    setup_logging(logging.WARNING)
    b = BashExecutor()
    r = b.execute({'cmd': 'echo "test" && echo "test2"'})

    print r.status
    print r.message
