from time import sleep

import unittest
import requests

class TestAPIs(unittest.TestCase):

    def test_get_pipelines(self):
        ret = requests.get('http://localhost:8888/api/pipelines/')
        if not ret.ok:
            print ('Request failed: %s' % ret.status_code)
        #print (ret.text)
        self.assertTrue(ret.ok)
        self.assertTrue(ret.json()[0]['slug'])
        self.assertTrue(ret.json()[0]['run_ids'])


    def test_run_pipeline_404(self):
        ret = requests.post('http://localhost:8888/api/pipelines/asdf/run')
        self.assertFalse(ret.ok)
        self.assertEqual(ret.status_code, 404)

    def test_run_pipeline(self):
        ret = requests.post('http://localhost:8888/api/pipelines/sample_pipe2/run')
        if not ret.ok:
            print ('ERROR: Request failed: %s' % (ret.status_code))
        self.assertTrue(ret.ok)
        self.assertTrue(ret.json()['task_id'])

    def test_get_status(self):
        url = ("http://localhost:8888/api/pipelines/sample_pipe2/"
        "50ec8b7b-ea4f-4df3-9362-1912b971c406/status")
        ret = requests.get(url)
        if not ret.ok:
            print ('ERROR: Request failed: %s' % (ret.status_code))
        self.assertTrue(ret.ok)
        self.assertTrue(ret.json()['status'])

    def test_get_log(self):
        url = ("http://localhost:8888/api/pipelines/sample_pipe2/"
                "50ec8b7b-ea4f-4df3-9362-1912b971c406/log")
        ret = requests.get(url)
        if not ret.ok:
            print ('ERROR: Request failed: %s' % (ret.status_code))
        self.assertTrue(ret.ok)

    def test_whole_seq(self):
        ret = requests.get('http://localhost:8888/api/pipelines/')
        pipeline_list =  ret.json()
        self.assertTrue(ret.ok)
        #print ('Response: %s' % ret.text)

        slug_id = pipeline_list[0]['slug']
        run_res = requests.post('http://localhost:8888/api/pipelines/%s/run' % slug_id)
        self.assertTrue(run_res.ok)

        task_id = run_res.json()['task_id']

        ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/status' % (slug_id, task_id))
        self.assertTrue(ret.ok)

        sleep(4)

        ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/log' % (slug_id, task_id))
        self.assertTrue(ret.ok)

        ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/status' % (slug_id, task_id))
        self.assertEqual(ret.json()['status'], 'success')


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIs)
    unittest.TextTestRunner(verbosity=2).run(suite)
