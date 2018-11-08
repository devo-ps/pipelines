import os
import tempfile
import unittest
from unittest.case import TestCase

from dotmap import DotMap

from pipelines.pipeline.pipeline import Pipeline, PIPELINE_STATUS_OK, PIPELINE_STATUS_FAIL
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.pipeline.var_processing import substitute_variables
from pipelines.plugins.bash_executor import BashExecutor, BashExecuteError
from pipelines.plugins.python_executor import PythonExecutor
from pipelines.utils import conf_logging

conf_logging()

class TestPipelines(TestCase):

    def test_parsine_minimal(self):
        pipeline_def = {
            'actions': []
        }
        pipeline = Pipeline.form_dict(pipeline_def)
        self.assertIsInstance(pipeline, Pipeline)

    def test_ignore_errors(self):
        pipeline_def = {
            'actions': [
            {
                'type': 'bash',
                'cmd': 'echo test && exit 1',
                'ignore_errors': True
            },
            'echo second'
            ],

        }
        pipeline = Pipeline.form_dict(pipeline_def)
        res = pipeline.run()
        self.assertEqual(res['status'], PIPELINE_STATUS_OK)
        self.assertEqual(len(res['results']), 2)
        self.assertEqual(res['results'][0].status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res['results'][1].status, EXECUTION_SUCCESSFUL)

    def test_ignore_errors_false(self):
        pipeline_def = {
            'actions': [
            {
                'type': 'bash',
                'cmd': 'echo test && exit 1',
                'ignore_errors': False
            },
            'echo second'
            ],

        }
        pipeline = Pipeline.form_dict(pipeline_def)
        res = pipeline.run()
        self.assertEqual(res['status'], PIPELINE_STATUS_FAIL)
        self.assertEqual(res['results'][0].status, EXECUTION_FAILED)
        self.assertEqual(len(res['results']), 1)

    def test_variable_passing(self):
        pipeline_def = {
            'actions': [
            'echo \'{"test22": 1}\'',
            'echo "{{ prev_result.return_obj.test22 }}"'
            ],
        }
        pipeline = Pipeline.form_dict(pipeline_def)
        res = pipeline.run()

        self.assertEqual(res['status'], PIPELINE_STATUS_OK)
        self.assertEqual(res['results'][1].data['output'].strip(), "1")

    def test_variable_passing_python(self):
        pipeline_def = {
            'actions': [
            {
                'type': 'python',
                'script': '''
import json
a = {'testpy': 'tdd', 'array': [1,2,3]}
print json.dumps(a)
'''
            },
            'echo "{{ prev_result.return_obj.testpy }}"'
            ],
        }
        pipeline = Pipeline.form_dict(pipeline_def)
        res = pipeline.run()

        self.assertEqual(res['status'], PIPELINE_STATUS_OK)
        self.assertEqual(res['results'][1].data['output'].strip(), "tdd")

    def test_templating(self):
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
            'if test': 'should say ok: {% if var1 %} ok {% else %} TEST FAIL!! {% endif %}',
            'testjson': '{{ nested | to_json }}',
            'testyaml': '{{ nested | to_yaml }}',
        }

        vars = DotMap(vars)
        res = substitute_variables(vars, obj)
        self.assertEqual(res['testnorm'], '11 22')
        self.assertEqual(res['testvar1'], '11')
        self.assertEqual(res['testvar2'], '--var2works')
        self.assertEqual(res['testvar3'], 'var 3 also worksjj')
        self.assertEqual(res['test:11'], '11')
        self.assertEqual(res['testlist'], ['norm', '11', 'var2works', 'norm2'])
        self.assertEqual(res['testdict'], {
                '11': 'vvv',
                'd2': '11',
                'nested': ['nest1', 'nestvarvar2works']
            })
        self.assertEqual(res['test1'], 'nestedTest: nestedWorks')
        self.assertEqual(res['if test'], 'should say ok:  ok ')
        self.assertEqual(res['testjson'], '{"n1": "nestedWorks"}')
        self.assertEqual(res['testyaml'], 'n1: nestedWorks\n')

if __name__ == '__main__':
    unittest.main()
