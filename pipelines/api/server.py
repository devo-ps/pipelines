
import json
import logging

import os
import re
from uuid import uuid4

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, HTTPError
from pipelines.pipeline.pipeline import Pipeline
from concurrent.futures import ThreadPoolExecutor
from tornado import concurrent, ioloop

def conf_logging():
    logger = logging.getLogger('applog')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger.propagate = False

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

conf_logging()
log = logging.getLogger('applog')

class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class AsyncRunner(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(
                AsyncRunner, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.io_loop = ioloop.IOLoop.current()

    @concurrent.run_on_executor
    def run(self, yaml_filepath, folder_path):
        pipe = Pipeline.from_yaml(yaml_filepath, params={
            'status_file': os.path.join(folder_path, 'status.json'),
            'log_file': os.path.join(folder_path, 'output.log')
        })
        return pipe.run()

def _file_iterator(folder, extension):
    for path in os.listdir(folder):
        if path.endswith('.%s' % extension):
            yield path

def _slugify_file(filename):
    basename = filename.rsplit('/', 1)[-1]
    return basename.rsplit('.', 1)[0]

def _run_id_iterator(slug):
    for sub_folder in os.listdir(slug):
        if _is_valid_uuid(sub_folder):
            yield sub_folder

def _is_valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)

class GetPipelinesHandler(BaseHandler):

    def get(self):
        workspace = self.settings['workspace_path']
        log.debug('Getting all pipelines')
        pipelines = []
        for path in _file_iterator(workspace, extension='yaml'):
            slug = _slugify_file(path)
            full_path = os.path.join(workspace, slug)
            if os.path.isdir(full_path):
                ids = list(_run_id_iterator(full_path))
                pipelines.append({ 'slug': slug, 'run_ids': ids })
        self.write(json.dumps(pipelines, indent=2))
        self.finish()

class GetLogsHandler(BaseHandler):

    def get(self, pipeline_slug, task_id):
        workspace = self.settings['workspace_path']
        log.debug('Getting all pipelines')

        with open(os.path.join(workspace, pipeline_slug, task_id, 'output.log')) as f:
            self.write(json.dumps({'output': f.read()}, indent=2))
            self.finish()

class GetStatusHandler(BaseHandler):

    def get(self, pipeline_slug, task_id):
        workspace = self.settings['workspace_path']
        log.debug('Getting all pipelines')

        with open(os.path.join(workspace, pipeline_slug, task_id, 'status.json')) as f:
            self.write(f.read())
            self.finish()

class RunPipelineHandler(BaseHandler):
    @gen.coroutine
    def post(self, pipeline_slug):
        workspace = self.settings['workspace_path']
        log.debug('Running pipeline')

        # payload = json.loads(self.request.body.decode())
        yaml_filepath = os.path.join(workspace, '%s.yaml' % pipeline_slug)

        if not os.path.exists(yaml_filepath):
            print 'not found %s' % yaml_filepath
            raise HTTPError(404, 'Pipeline not found')

        task_id = str(uuid4())
        folder_path = os.path.join(workspace, pipeline_slug, task_id)
        os.makedirs(folder_path)

        self.write(json.dumps({'task_id': task_id}, indent=2))
        self.finish()

        runner = AsyncRunner()
        yield runner.run(yaml_filepath, folder_path)


def make_app(workspace='fixtures/workspace'):
    return Application([
        url(r"/api/pipelines/", GetPipelinesHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_]+)/run", RunPipelineHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_]+)/([0-9a-zA-Z_\-]+)/status", GetStatusHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_]+)/([0-9a-zA-Z_\-]+)/log", GetLogsHandler),
    ],
        workspace_path=workspace
    )

def main(config):
    app = make_app(config.get('workspace'))
    app.listen(int(config.get('port', 8888)), address=config.get('host', '127.0.0.1'))
    print('Starting ioloop')
    io_loop = IOLoop.current()
    io_loop.start()

if __name__ == '__main__':
    main()
