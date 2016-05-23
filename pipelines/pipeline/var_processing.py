import re

from pipelines.pipeline.exceptions import PipelineError


def substitute_variables(vars, obj):

    pattern = re.compile(r'\{\{' + r'[\s]{0,2}' + r'(?P<var>[\w-]+)' + r'[\s]{0,2}' + r'\}\}')

    def replace_vars_func(token):
        substituted = ''
        content_cursor = 0
        for match in re.finditer(pattern, token):
            substituted += token[content_cursor:match.start()]

            variable_name = match.groupdict()['var']

            if variable_name not in vars:
                raise PipelineError('Missing variable: {}'.format(variable_name))

            value = vars[variable_name]

            substituted += str(value)

            content_cursor = match.end()

        substituted += token[content_cursor:]

        return substituted

    return _loop_strings(replace_vars_func, obj)

def _loop_strings(func, obj):
    new_obj = obj
    if isinstance(obj, basestring):
        new_obj = func(obj)
    elif isinstance(obj, dict):
        new_obj = dict([(_loop_strings(func, k), _loop_strings(func, v)) for k,v in obj.items()])
    elif isinstance(obj, list) or isinstance(obj, tuple):
        new_obj = [_loop_strings(func, item) for item in obj]
    return new_obj

if __name__ == '__main__':
    vars = {
        'var1': 11,
        'var-2': 'var2works',
        'var_3': 'var 3 also works',
    }
    obj = {
        'testnorm': '11 22',
        'testvar1': '{{var1}}',
        'testvar2': '--{{ var-2 }}',
        'testvar3': '{{ var_3}}jj',
        'test:{{var1}}': '{{var1}}',
        'testlist': ['norm', '{{var1}}', '{{var-2}}', 'norm2'],
        'testdict': {
            '{{var1}}': 'vvv',
            'd2': '{{var1}}',
            'nested': ['nest1', 'nestvar{{var-2}}']
        }

    }
    res = substitute_variables(vars, obj)
    import json
    print json.dumps(res, indent=2)
