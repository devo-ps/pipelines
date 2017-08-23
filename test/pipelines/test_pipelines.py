import os
import tempfile
import unittest
from unittest.case import TestCase

from pipelines.pipeline.pipeline import Pipeline, PIPELINE_STATUS_OK, PIPELINE_STATUS_FAIL
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
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



if __name__ == '__main__':
    unittest.main()
