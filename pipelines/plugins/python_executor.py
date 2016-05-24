import logging

from pipelines.plugins.bash_executor import BashExecutor, BashExecuteError
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError
from os import path

log = logging.getLogger()

class PythonExecutor(BashExecutor):
    hook_prefix = 'python'
    hooks = ('execute',)

    def _parse_args_dict(self, args_dict):
        for k in ['workdir', 'virtualenv', 'script']:
            if k not in args_dict:
                raise PluginError('PythonExecutor is missing argument: {}'.format(k))

        return args_dict['workdir'], args_dict['virtualenv'], args_dict['script']

    def execute(self, args_dict):

        workdir, virtualenv, script = self._parse_args_dict(args_dict)

        activate_path = path.join(virtualenv, 'bin', 'activate')
        if not path.exists(activate_path) or not path.isfile(activate_path):
            raise PluginError('Python virtualenv doesn\'t exist: {}'.format(activate_path))

        bash_input = (
            'cd {}\n'
            'source {}\n'
            'python {}'
        ).format(workdir, activate_path, script)

        log.debug('Running python script: {}'.format(bash_input))

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)


        try:
            stdout = self._run_bash(bash_input)
            status = EXECUTION_SUCCESSFUL
        except BashExecuteError as e:
            status = EXECUTION_FAILED
            stdout = e.stderr

        return TaskResult(status, stdout)


if __name__ == '__main__':
    from pluginworm.utils import setup_logging
    setup_logging(logging.WARNING)
    b = BashExecutor()
    r = b.execute({'cmd': 'echo "test" && echo "test2"'})

    print r.status
    print r.message
