import os
import tempfile
import unittest
from unittest.case import TestCase

from datetime import datetime

from pipelines.pipeline.pipeline import Pipeline, PIPELINE_STATUS_OK, PIPELINE_STATUS_FAIL
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugins.bash_executor import BashExecutor, BashExecuteError
from pipelines.plugins.python_executor import PythonExecutor
from pipelines.utils import conf_logging

conf_logging()

class TestPythonExecutor(TestCase):

    # def test_basic_loading(self):
    #
    #     print 'Running test_basic_loading'
    #     executor = BashExecutor.from_dict({})
    #     self.assertIsInstance(executor, BashExecutor)
    #
    # # def test_basic_loading(self):
    # #     with tempfile.NamedTemporaryFile() as f:
    # #         print 'Running test_basic_loading'
    # #         executor = BashExecutor.from_dict({'log_file': f.name})
    # #         self.assertIsInstance(executor, BashExecutor)
    # #         executor.execute()
    # #         self.assertLess(100, len())
    #
    #
    #
    #
    #
    # def test_timeout_script_pass(self):
    #     print 'Running test_timeout_script_pass'
    #     executor = BashExecutor(timeout=3)
    #     args = {
    #         'cmd': 'echo "test" && sleep "2"'
    #     }
    #     res = executor.execute(args)
    #     self.assertFalse(res.status, EXECUTION_SUCCESSFUL)
    #     self.assertEqual(res.data['output'], 'test\n')
    #
    # def test_timeout_script_fail(self):
    #     print 'Running test_timeout_script_pass'
    #     executor = BashExecutor(timeout=2)
    #     args = {
    #         'cmd': 'echo "test" && sleep "3"'
    #     }
    #     res = executor.execute(args)
    #     self.assertIsInstance(res, TaskResult)
    #     self.assertEqual(res.status, EXECUTION_FAILED)
    #     self.assertEqual(res.data['output'], 'test\n')
    #
    # def test_timeout_in_pipeline_def(self):
    #     pipeline_def = {
    #         'actions': [
    #         {
    #             'type': 'bash',
    #             'cmd': 'echo test',
    #             'timeout': 1
    #         }
    #         ],
    #
    #     }
    #     pipeline = Pipeline.form_dict(pipeline_def)
    #     res = pipeline.run()
    #     self.assertEqual(res['status'], PIPELINE_STATUS_OK)
    def test_basic_script(self):
        print 'Running test_basic_script'
        executor = BashExecutor()
        args = {
            'cmd': 'echo "test"'
        }
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.data['output'].strip(), 'test')
        self.assertEqual(res.message.strip(), 'Bash task finished')

    def test_return_obj(self):
        print 'Testing return object parsing'
        executor = BashExecutor()
        args = {
            'cmd': 'echo \'{"test": 1}\''
        }
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.data['output'].strip(), '{"test": 1}')
        self.assertEqual(res.return_obj, {"test": 1})

    def test_return_obj_empty_rows(self):
        print 'Testing return object parsing'
        executor = BashExecutor()
        args = {
            'cmd': 'echo \'{"otest": 1}\n\''
        }
        res = executor.execute(args)
        self.assertEqual(res.return_obj, {"otest": 1})

    def test_return_obj_nojson(self):
        print 'Testing return object parsing'
        executor = BashExecutor()
        args = {
            'cmd': 'echo \'abba\n"test": 1}\n\''
        }
        res = executor.execute(args)
        self.assertIsNone(res.return_obj)

    # def test_utf_script(self):
    #     print 'Running test_basic_script'
    #     executor = BashExecutor()
    #     args = {
    #         'cmd': u'echo "test\u4e2dtest"'
    #     }
    #     res = executor.execute(args)
    #     self.assertIsInstance(res, TaskResult)
    #     self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
    #     self.assertEqual(res.data['output'].strip(), u'test\u4e2dtest')
    #     self.assertEqual(res.message.strip(), 'Bash task finished')


    def test_timeout_in_pipeline_def_timeouts(self):
        pipeline_def = {
            'actions': [
            {
                'type': 'bash',
                'cmd': 'sleep 2',
                'timeout': 1
            }
            ],

        }
        start = datetime.now()
        pipeline = Pipeline.form_dict(pipeline_def)
        res = pipeline.run()
        seconds = (datetime.now() - start).total_seconds()
        print res
        print seconds
        self.assertEqual(res['status'], PIPELINE_STATUS_FAIL)
        self.assertLess(seconds, 2)
        # self.assertEqual(res['results'][0]['mesasge'], 'Timed Out')


if __name__ == '__main__':
    unittest.main()
