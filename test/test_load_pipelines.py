from time import sleep

import unittest
import requests
import json

import pipelines.api.server as server

from tornado.testing import AsyncHTTPTestCase

from pipelines.api.server import _file_iterator, PIPELINES_EXT
from pipelines.pipeline.pipeline import Pipeline
import os.path

WORKSPACE = '../fixtures/workspace'

class TestAPIs(AsyncHTTPTestCase):
    def get_app(self):
        return server.make_app(WORKSPACE)

    def _get_pipelines(self):
        for path in _file_iterator(WORKSPACE, extensions=PIPELINES_EXT):
            yield os.path.join(WORKSPACE, path)

    def test_get_pipelines(self):
        for pipeline_path in self._get_pipelines():
            res = Pipeline.from_yaml(pipeline_path, {})
            self.assertTrue(res)



if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIs)
    # unittest.TextTestRunner(verbosity=2).run(suite)
