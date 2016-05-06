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


if __name__ == '__main__':
    print 'TEST: Get pipelines'
    test_get_pipelines()
    print 'TEST: Run 404'
    test_run_pipeline_404()
    print 'TEST: Run ok'
    test_run_pipeline()