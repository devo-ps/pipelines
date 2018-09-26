
import unittest

from schema import SchemaError

import pipelines.api.server as server

from tornado.testing import AsyncHTTPTestCase

from pipelines.api.server import _file_iterator, PIPELINES_EXT
from pipelines.pipeline.exceptions import PipelineError
from pipelines.pipeline.pipeline import Pipeline
import os.path

WORKSPACE = os.path.realpath('test/fixtures/workspace')
SECRET = '12345'

class TestAPIs(AsyncHTTPTestCase):
    def get_app(self):
        return server.make_app(SECRET, WORKSPACE)

    def _get_pipelines(self):
        for path in _file_iterator(WORKSPACE, extensions=PIPELINES_EXT):
            print 'yielding: {}'.format(os.path.join(WORKSPACE, path))
            yield os.path.join(WORKSPACE, path)

    def test_load_sample_pipelines(self):
        for pipeline_path in self._get_pipelines():
            try:
                res = Pipeline.from_yaml(pipeline_path, {})
            except (SchemaError, PipelineError) as e:
                print e
                self.assertTrue(False, 'Pipeline failed to validate: {}'.format(pipeline_path))

        # TODO: Add more validation

if __name__ == '__main__':
    unittest.main()