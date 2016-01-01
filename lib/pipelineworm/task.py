from copy import copy


class Task(object):
    def __init__(self, name, executor, args):
        self.name = name
        self.executor = executor
        self.args = args

    @staticmethod
    def from_dict(task_dict):
        task_args = copy(task_dict)
        executor = task_args.pop('executor')
        if 'name' in task_dict:
            name = task_dict.pop('name')
        else:
            name = ''
        return Task(name, executor, task_args)

