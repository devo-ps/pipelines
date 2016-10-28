from time import sleep

import unittest
import requests
import json

import pipelines.api.server as server

from tornado.testing import AsyncHTTPTestCase

WORKSPACE = '../../fixtures/workspace'

class TestAPIs(AsyncHTTPTestCase):
    def get_app(self):
        return server.make_app(WORKSPACE)

    def test_get_pipelines(self):
        '''
        Listing the pipelines from the fixtures
        '''
        url = ("/api/pipelines/")
        response = self.fetch(url)
        self.assertEqual(response.code, 200)

        try:
            content = json.loads(response.body)
        except:
            # TODO - better way to raise the error
            self.assertTrue(False)

        self.assertTrue(content[0]['slug'])
        self.assertTrue(content[0]['run_ids'])


    def test_run_pipeline_404(self):
        '''
        Attempt to run a missing pipeline - should return 404
        '''
        url = ("/api/pipelines/missing/run")
        response = self.fetch(url, method='POST', body='')

        self.assertEqual(response.code, 404)

    def test_run_pipeline(self):
        '''
        Run an existing pipeline
        '''
        url = '/api/pipelines/sample-deploy/run'
        response = self.fetch(url, method='POST', body='')
        self.assertEqual(response.code, 200)

        try:
            content = json.loads(response.body)
        except:
            # TODO - better way to raise the error
            self.assertTrue(False)

        # Expect task_id in the parsed response
        self.assertTrue(content['task_id'])

    def test_get_status(self):
        '''
        Fetch the status of a pipeline run
        '''
        url = ("/api/pipelines/sample-deploy/"
        "50ec8b7b-ea4f-4df3-9362-1912b971c406/status")
    
        response = self.fetch(url)
        self.assertEqual(response.code, 200)

        try:
            content = json.loads(response.body)
        except:
            # TODO - better way to raise the error
            self.assertTrue(False)

        # Expect status in the parsed response
        self.assertTrue(content['status'])

    def test_get_log(self):
        '''
        Fetching logs from saved pipeline's run
        '''
        url = ("/api/pipelines/sample-deploy/f3387895-bdcf-4261-9d3f-4214d64db520/log")
        response = self.fetch(url)
        self.assertEqual(response.code, 200)

    def test_whole_seq(self):
        '''
        End to end testing - list pipelines, execute one, check status and logs, check status on completion
        '''
        url_list = '/api/pipelines/'
        url_run = '/api/pipelines/%s/run'
        url_status = '/api/pipelines/%s/%s/status'
        url_log = '/api/pipelines/%s/%s/log'

        # Fetch the pipelines' list and extract one of the pipeline's ID
        resp_list = self.fetch(url_list)
        self.assertTrue(resp_list.code, 200)
        json_list = json.loads(resp_list.body)
        pipeline_id = json_list[0]['slug']

        # Run the pipeline, and extract the task id
        resp_run = self.fetch(url_run % pipeline_id, method='POST', body='')
        self.assertTrue(resp_list.code, 200)
        json_run = json.loads(resp_run.body)
        task_id = json_run['task_id']

        # Get the status of the task - should be incomplete 
        resp_status1 = self.fetch(url_status % (pipeline_id, task_id))
        self.assertTrue(resp_status1.code, 200)

        # Wait a few seconds to ensure the run complete
        sleep(4)

        # Fetch the logs - expect a success
        resp_log = self.fetch(url_log % (pipeline_id, task_id))
        self.assertTrue(resp_log.code, 200)        

        # Get (again) the status of the task - should be complete 
        resp_status2 = self.fetch(url_status % (pipeline_id, task_id))
        self.assertTrue(resp_status2.code, 200)
        json_status2 = json.loads(resp_status2.body)
        print 'ddd'
        print json_status2
        self.assertEqual(json_status2['status'], 'success')


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIs)
    # unittest.TextTestRunner(verbosity=2).run(suite)
