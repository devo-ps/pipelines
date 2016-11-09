import logging
from tempfile import NamedTemporaryFile

from pipelines.plugins.bash_executor import BashExecutor, BashExecuteError
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError
from os import path

log = logging.getLogger('pipelines')


'''

THIS HAS NOT BEEN UPDATED/TESED PROPERLY

'''

class PythonExecutor(BashExecutor):
    hook_prefix = 'python'
    hooks = ('execute',)

    def _validate_args_dict(self, args_dict):
        if 'file' not in args_dict and 'script' not in args_dict:
            raise PluginError('PythonExecutor requires either "file" or "script" arguments. Given: {}'.format(args_dict))

        if args_dict.get('file') and args_dict.get('script'):
            raise PluginError(
                'PythonExecutor got both "file" and "script" aguments. Only one is supported.')

        if args_dict.get('workspace') and args_dict.get('script'):
            raise PluginError('PythonExecutor requires either "file" or "script" arguments. Given: {}'.format(args_dict))

    def execute(self, args_dict):
        self._validate_args_dict(args_dict)
        workdir = args_dict.get('workdir')
        script = args_dict.get('script')
        file = args_dict.get('file')
        virtualenv = args_dict.get('virtualenv')

        bash_input = ''
        if workdir:
            bash_input += 'cd {}\n'.format(workdir)

        if virtualenv:
            activate_path = path.join(virtualenv, 'bin', 'activate')
            if not path.exists(activate_path) or not path.isfile(activate_path):
                raise PluginError('Python virtualenv doesn\'t exist: {}'.format(activate_path))

            bash_input += 'source {}\n'.format(activate_path)

        filename = file

        if script:
            f = NamedTemporaryFile(delete=False)

            f.write(script)
            log.debug('Wrote script to file {}, {}'.format(f.name, script))
            filename = f.name
            f.close()

        bash_input += 'python {}'.format(filename)
        log.debug('Running python script: {}'.format(bash_input))

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)

        try:
            stdout = self._run_bash(bash_input)
            status = EXECUTION_SUCCESSFUL
        except BashExecuteError as e:
            status = EXECUTION_FAILED
            stdout = e.stderr
        print 'Finished, stdout: %s' % (stdout)

        return TaskResult(status, 'Execution finished')



if __name__ == '__main__':
    pass
    # from plugins.utils import setup_logging
    # setup_logging(logging.WARNING)
    # b = BashExecutor()
    # r = b.execute({'cmd': 'echo "test" && echo "test2"'})
    #
    # print r.status
    # print r.message
