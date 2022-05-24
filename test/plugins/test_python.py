import os
import unittest
from unittest.case import TestCase

from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL
from pipelines.plugins.python_executor import PythonExecutor
from pipelines.utils import conf_logging

conf_logging()


class TestPythonExecutor(TestCase):

    def test_basic_script(self):
        print('Running test_basic_script')
        executor = PythonExecutor()
        args = {'script': 'print("test")'}
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.message.strip(), 'Execution finished')
        self.assertEqual(res.data['output'], u'test\n')

    def test_basic_file(self):
        print('Running test_basic_script')
        executor = PythonExecutor()
        args = {'file': 'test/files/test_python_file.py'}
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.message.strip(), 'Execution finished')
        self.assertEqual(res.data['output'], u'test: {"a": 1}\n')

    def test_workdir(self):
        print('Running test_workdir')
        executor = PythonExecutor()
        args = {'workdir': 'test/files', 'file': 'test_python_file.py'}
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.message.strip(), 'Execution finished')
        self.assertEqual(res.data['output'], u'test: {"a": 1}\n')

    def test_workdir_abspath(self):
        print('Running test_workdir')
        executor = PythonExecutor()
        args = {
            'workdir': os.path.abspath('test/files'),
            'file': 'test_python_file.py'
        }
        res = executor.execute(args)
        self.assertIsInstance(res, TaskResult)
        self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
        self.assertEqual(res.message.strip(), 'Execution finished')
        self.assertEqual(res.data['output'], u'test: {"a": 1}\n')


#     def test_workdir_virtualenv(self):
#         print('Running test_workdir')
#         executor = PythonExecutor()
#         args = {
#             'virtualenv': 'test/files/test_venv',
#             'script': '''
# import dopy
# print(dopy.__license__)
#             '''
#
#         }
#         res = executor.execute(args)
#         self.assertIsInstance(res, TaskResult)
#         self.assertEqual(res.data, 'MIT')
#         self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
#
#     def test_workdir_virtualenv_abs(self):
#         print('Running test_workdir')
#         executor = PythonExecutor()
#         args = {
#             'virtualenv': os.path.abspath('test/files/test_venv'),
#             'script': '''
# import dopy
# print(dopy.__license__)
#             '''
#
#         }
#         res = executor.execute(args)
#         self.assertIsInstance(res, TaskResult)
#         self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
#         self.assertEqual(res.message.strip(), 'MIT')

# def test_workdir_virtualenv_file(self):
#     print('Running test_workdir')
#     executor = PythonExecutor()
#     args = {
#         'virtualenv': os.path.abspath('test/files/test_venv'),
#         'file': 'test/files/test_dopy_import.py'
#
#     }
#     res = executor.execute(args)
#     self.assertIsInstance(res, TaskResult)
#     self.assertEqual(res.status, EXECUTION_SUCCESSFUL)
#     self.assertEqual(res.message.strip(), 'MIT')

if __name__ == '__main__':
    unittest.main()
