
import json
import logging

import os
import re
from uuid import uuid4

import tornado
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import (
    RequestHandler,
    Application,
    url,
    HTTPError,
    authenticated,
    StaticFileHandler
)

from pipelines import PipelinesError
from pipelines.pipeline.pipeline import Pipeline
from concurrent.futures import ThreadPoolExecutor
from tornado import concurrent, ioloop

from pipelines.utils import conf_logging

PIPELINES_EXT = ('yml', 'yaml')

log = logging.getLogger('pipelines')

class PipelinesRequestHandler(RequestHandler):
    def get_current_user(self):
        if not self.settings.get('auth'):
            # No authentication required
            return 'guest'

        user_cookie = self.get_secure_cookie("user")
        if user_cookie:
            return json.loads(user_cookie)
        return None

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
    def run(self, pipeline_file, folder_path):
        pipe = Pipeline.from_yaml(pipeline_file, params={
            'status_file': os.path.join(folder_path, 'status.json'),
            'log_file': os.path.join(folder_path, 'output.log')
        })
        return pipe.run()

def _file_iterator(folder, extensions):
    for path in os.listdir(folder):
        for ext in extensions:
            if path.endswith('.%s' % ext):
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

def _authenticate_user(auth_settings, username, password):
    if username != auth_settings['username'] or password != auth_settings['password']:
        return False
    return True


class LoginHandler(PipelinesRequestHandler):
    def get(self):
        print self.current_user
        self.write('<html><body><form action="/login" method="post">'
                   'Username: <input type="text" name="username"><br/>'
                   'Password: <input type="text" name="password"><br/>'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        if _authenticate_user(
                self.settings['auth'],
                self.get_argument('username'),
                self.get_argument('password')
        ):
            self.set_secure_cookie("user", tornado.escape.json_encode(self.get_argument("username")))
            print 'set secure cookie'
            self.redirect("/index.html")
        else:
            self.redirect("/login")


class GetPipelinesHandler(PipelinesRequestHandler):

    @authenticated
    def get(self):
        workspace = self.settings['workspace_path']
        log.debug('Getting all pipelines')
        pipelines = []
        for path in _file_iterator(workspace, extensions=PIPELINES_EXT):
            slug = _slugify_file(path)
            full_path = os.path.join(workspace, slug)
            if os.path.isdir(full_path):
                # expect to have runs
                ids = list(_run_id_iterator(full_path))
                pipelines.append({'slug': slug, 'run_ids': ids})
            else:
                pipelines.append({'slug': slug, 'run_ids': []})
        self.write(json.dumps(pipelines, indent=2))
        self.finish()


class GetLogsHandler(PipelinesRequestHandler):

    def get(self, pipeline_slug, task_id):
        workspace = self.settings['workspace_path']
        log.debug('Getting pipeline logs')

        logfile_path = os.path.join(workspace, pipeline_slug, task_id, 'output.log')
        if not os.path.exists(logfile_path):
            self.write(json.dumps({}))
            self.finish()
        else:
            with open(logfile_path) as f:
                self.write(json.dumps({'output': f.read()}, indent=2))
                self.finish()

class GetStatusHandler(PipelinesRequestHandler):

    def get(self, pipeline_slug, task_id):
        print 'STATUS'
        workspace = self.settings['workspace_path']
        log.debug('Getting pipeline status')

        statusfile_path = os.path.join(workspace, pipeline_slug, task_id, 'status.json')
        if not os.path.exists(statusfile_path):
            log.debug('Status file does not exist %s' % statusfile_path)
            self.write(json.dumps({}))
            self.finish()
        else:
            with open(statusfile_path) as f:
                self.write(f.read())
                self.finish()

class RunPipelineHandler(PipelinesRequestHandler):
    @gen.coroutine
    def post(self, pipeline_slug):
        workspace = self.settings['workspace_path']
        log.debug('Running pipeline')

        # Guess the pipeline extension
        pipeline_filepath = None
        for ext in PIPELINES_EXT:
            yaml_filepath = os.path.join(workspace, '%s.%s' % (pipeline_slug, ext))
            if os.path.exists(yaml_filepath):
                pipeline_filepath = yaml_filepath
                break

        if not pipeline_filepath:
            raise HTTPError(404, 'Pipeline not found')

        task_id = str(uuid4())
        folder_path = os.path.join(workspace, pipeline_slug, task_id)
        os.makedirs(folder_path)

        self.write(json.dumps({'task_id': task_id}, indent=2))
        self.finish()

        runner = AsyncRunner()
        yield runner.run(pipeline_filepath, folder_path)

class AuthStaticFileHandler(StaticFileHandler, PipelinesRequestHandler):
    @authenticated
    def get(self, *args, **kwargs):
        return super(AuthStaticFileHandler, self).get(*args, **kwargs)

def make_app(workspace='fixtures/workspace', auth=None):
    if not os.path.isdir(workspace):
        raise PipelinesError('Workspace is not a valid directory: %s' % workspace)

    auth_dict=None
    if auth:
        auth_dict = {
            'type': 'static',
            'username': auth[0],
            'password': auth[1]
        }


    return Application([
        url(r"/api/pipelines/", GetPipelinesHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_\-]+)/run", RunPipelineHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_\-]+)/([0-9a-zA-Z_\-]+)/status", GetStatusHandler),
        url(r"/api/pipelines/([0-9a-zA-Z_\-]+)/([0-9a-zA-Z_\-]+)/log", GetLogsHandler),
        (r"/login", LoginHandler),
        (r'/(.*)', AuthStaticFileHandler, {'path': _get_static_path('app'), "default_filename": "index.html"}),
    ],
        workspace_path=workspace,
        auth=auth_dict,
        login_url= "/login",
        debug="True",
        cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="  # TODO: make configurable
    )

def _get_static_path(subpath):
    this_path = os.path.realpath(__file__)
    this_dir = os.path.dirname(this_path)
    ret = os.path.join(this_dir, 'app_dist')
    log.debug('Serving %s' % ret)
    return ret

def main(config):
    conf_logging()
    app = make_app(config.get('workspace', 'fixtures/workspace'), config.get('auth'))
    app.listen(
            int(config.get('port', 8888)),
            address=config.get('host', '127.0.0.1'),
    )

    log.info('Starting ioloop: {}'.format(config))
    io_loop = IOLoop.current()
    io_loop.start()

if __name__ == '__main__':
    main()
