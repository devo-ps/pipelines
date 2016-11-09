import logging

from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError
from sh import ErrorReturnCode
from sh import bash

log = logging.getLogger('pipelines')

class BashExecuteError(PluginError):
    def __init__(self, stderr, code):
        self.stderr = stderr
        self.code = code


class BashExecutor(BaseExecutorPlugin):
    hook_prefix = 'bash'
    hooks = ('execute',)

    def __init__(self, log_file=None, event_mgr=None):
        self.log_file = log_file
        self.event_mgr = event_mgr

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
            # stdout = self._run_bash(cmd)
            self._run_bash(cmd)
            status = EXECUTION_SUCCESSFUL
        except BashExecuteError:
            status = EXECUTION_FAILED
            # stdout = e.stderr

        return TaskResult(status, 'Bash task finished')


    def _run_bash(self, bash_input):
        log.debug('Running bash command: "{}"'.format(bash_input))
        f = None
        if self.log_file:
            f = open(self.log_file, 'a+')

        output = {'stdout': ''}
        try:
            def process_line(line):
                log.debug('Got line: %s' % line)
                output['stdout'] += line
                log.debug('BashExec stdout: {}'.format(line))
                if f:
                    f.write(line)

                if self.event_mgr:
                    if len(line)>0 and line[-1] == '\n':
                        line = line[:-1]
                    self.event_mgr.trigger('on_task_event', {'output': line})

            proc = bash(_in=bash_input, _out=process_line, _err=process_line)
            proc.wait()
            log.debug('Finished: %s, %s, %s' % (proc.exit_code, proc.stdout, proc.stderr))

        except ErrorReturnCode as e:
            log.debug('BashExec failed')
            raise BashExecuteError(e.stderr, e.exit_code)
        return output['stdout']

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        return cls(conf_dict.get('bash_log_file'), event_mgr)

