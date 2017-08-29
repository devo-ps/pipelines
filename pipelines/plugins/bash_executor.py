import logging

from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError
from sh import ErrorReturnCode, TimeoutException
from sh import bash

log = logging.getLogger('pipelines')
DEFAULT_TIMEOUT = 60*60  # Timeout to 1h

class BashExecuteError(PluginError):
    def __init__(self, msg, code, data={}):
        self.msg = msg
        self.code = code
        self.data = data


class BashExecutor(BaseExecutorPlugin):
    hook_prefix = 'bash'
    hooks = ('execute',)

    def __init__(self, log_file=None, event_mgr=None):
        self.log_file = log_file
        self.event_mgr = event_mgr

        log.debug('Bash executor initiated with log_file: %s' % self.log_file)

    def _parse_args_dict(self, args_dict):
        if 'cmd' not in args_dict:
            raise PluginError('BashExecutor got incorrect arguments, got: {}'.format(
                args_dict.keys()
            ))
        timeout = args_dict.get('timeout') or DEFAULT_TIMEOUT
        if not isinstance(timeout, int):
            raise PluginError('BashExecutor got incorrect timeout argument type, got: {} expecting int'.format(
                type(timeout)
            ))

        return args_dict['cmd'], timeout

    def execute(self, args_dict):
        cmd, timeout = self._parse_args_dict(args_dict)

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)

        try:
            # stdout = self._run_bash(cmd)
            output = self._run_bash(cmd, timeout)
            status = EXECUTION_SUCCESSFUL
            msg = 'Bash task finished'
        except BashExecuteError as e:
            status = EXECUTION_FAILED
            # stdout = e.stderr
            msg = 'Bash task failed: %s' % e.msg
            output = e.data['stdout']

        return TaskResult(status, msg, data={'output': output})


    def _run_bash(self, bash_input, timeout):
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

            proc = bash(_in=bash_input, _out=process_line, _err=process_line, _timeout=timeout)
            proc.wait()
            log.debug('Finished: %s, %s, %s' % (proc.exit_code, proc.stdout, proc.stderr))

        except ErrorReturnCode as e:
            log.debug('BashExec failed')
            raise BashExecuteError("Execution failed with code: %s" % e.exit_code, e.exit_code)
        except TimeoutException as e:
            log.debug('BashExec timed out after %s seconds' % timeout)
            raise BashExecuteError("Task Timed Out", 1, data=output)
        return output['stdout']

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        return cls(conf_dict.get('bash_log_file'), event_mgr)

