from time import sleep

import requests

def test_get_pipelines():
    ret = requests.get('http://localhost:8888/api/pipelines/')
    if not ret.ok:
        print 'Request failed: %s' % ret.status_code
    print ret.text


def test_run_pipeline_404():
    ret = requests.post('http://localhost:8888/api/pipelines/asdf/run')
    if not ret.ok:
        print 'Request failed as expected: %s' % (ret.status_code)
    print ret.text

def test_run_pipeline():
    ret = requests.post('http://localhost:8888/api/pipelines/sample_pipe2/run')
    if not ret.ok:
        print 'ERROR: Request failed: %s' % (ret.status_code)
    print ret.text

def test_get_status():
    ret = requests.get('http://localhost:8888/api/pipelines/sample_pipe2/50ec8b7b-ea4f-4df3-9362-1912b971c406/status')
    if not ret.ok:
        print 'ERROR: Request failed: %s' % (ret.status_code)
    print ret.text

def test_get_log():
    ret = requests.get('http://localhost:8888/api/pipelines/sample_pipe2/50ec8b7b-ea4f-4df3-9362-1912b971c406/log')
    if not ret.ok:
        print 'ERROR: Request failed: %s' % (ret.status_code)
    print ret.text

def test_whole_seq():
    print 'GET http://localhost:8888/api/pipelines/'
    ret = requests.get('http://localhost:8888/api/pipelines/')
    pipeline_list =  ret.json()
    print 'Response: %s' % ret.text

    print 'POST http://localhost:8888/api/pipelines/%s/run' % pipeline_list[0]['slug']
    run_res = requests.post('http://localhost:8888/api/pipelines/%s/run' % pipeline_list[0]['slug'])
    print 'Response: %s' % run_res.text

    task_id = run_res.json()['task_id']

    print 'GET http://localhost:8888/api/pipelines/%s/%s/status' % (pipeline_list[0]['slug'], task_id)
    ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/status' % (pipeline_list[0]['slug'], task_id))
    print 'Response: %s' % ret.text

    sleep(4)

    print 'GET http://localhost:8888/api/pipelines/%s/%s/log' % (pipeline_list[0]['slug'], task_id)
    ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/log' % (pipeline_list[0]['slug'], task_id))
    print 'Response: %s...' % ret.text[:320]

    print 'GET http://localhost:8888/api/pipelines/%s/%s/status' % (pipeline_list[0]['slug'], task_id)
    ret = requests.get('http://localhost:8888/api/pipelines/%s/%s/status' % (pipeline_list[0]['slug'], task_id))
    print 'Response: %s' % ret.text


if __name__ == '__main__':
    # print 'TEST: Get pipelines'
    # test_get_pipelines()
    # print 'TEST: Run 404'
    # test_run_pipeline_404()
    # print 'TEST: Run ok'
    # test_run_pipeline()
    # print 'TEST: Get status'
    # test_get_status()
    # print 'TEST: Get status'
    # test_get_log()

    test_whole_seq()