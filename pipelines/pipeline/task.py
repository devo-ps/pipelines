import logging
from copy import copy


EXECUTION_SUCCESSFUL = 0
EXECUTION_FAILED = 1

log = logging.getLogger('pipelines')

class Task(object):
    def __init__(self, name, executor, args, always_run, ignore_errors):
        self.name = name
        self.executor = executor
        self.args = args
        self.always_run = always_run
        self.ignore_errors = ignore_errors


    @staticmethod
    def from_dict(task_dict):
        task_args = copy(task_dict)
        executor = task_args.pop('type')

        name = ''
        if 'name' in task_dict:
            name = task_dict.pop('name')

        always_run = False
        if 'always_run' in task_dict:
            always_run = task_dict.pop('always_run')

        ignore_errors = False
        if 'ignore_errors' in task_dict:
            ignore_errors = task_dict.pop('ignore_errors')

        return Task(name, executor, task_args, always_run, ignore_errors)


class TaskResult(dict):
    def __init__(self, status, message=''):
        self['status'] = status
        self['message'] = message

    @property
    def status(self):
        return self.get('status')

    @property
    def message(self):
        return self.get('message')


    def is_successful(self):
        return self.status == EXECUTION_SUCCESSFUL
