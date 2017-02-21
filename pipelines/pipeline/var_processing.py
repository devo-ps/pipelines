import logging
from dotmap import DotMap
from jinja2 import Template

log = logging.getLogger('pipelines')


def substitute_variables(pipeline_context, obj):
    if isinstance(pipeline_context, DotMap):
        pipeline_context = pipeline_context.toDict()

    pipeline_context.update(pipeline_context.get('vars'))  # Pull everything from "vars" to root

    def replace_vars_func(token):
        template = Template(token)
        substituted = template.render(**pipeline_context)

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
        'vars': {
            'var1': 11,
            'var_2': 'var2works',
            'var_3': 'var 3 also works',
            'nested': {
                'n1': 'nestedWorks'
            }
        }
    }
    obj = {
        'testnorm': '11 22',
        'testvar1': '{{var1}}',
        'testvar2': '--{{ var_2 }}',
        'testvar3': '{{ var_3}}jj',
        'test:{{var1}}': '{{var1}}',
        'testlist': ['norm', '{{var1}}', '{{var_2}}', 'norm2'],
        'testdict': {
            '{{var1}}': 'vvv',
            'd2': '{{var1}}',
            'nested': ['nest1', 'nestvar{{var_2}}']
        },
        'test1': 'nestedTest: {{ nested.n1 }}',
        'if test': 'should say ok: {% if var1 %} ok {% else %} TEST FAIL!! {% endif %}'
    }

    vars = DotMap(vars)
    res = substitute_variables(vars, obj)
    import json
    print json.dumps(res, indent=2)

