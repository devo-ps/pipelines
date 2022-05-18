from datetime import datetime

import yaml
from concurrent.futures.thread import ThreadPoolExecutor
from tornado import ioloop, concurrent
from yaml.error import YAMLError
import re
from pipelines.api import PIPELINES_EXT
import os.path
import json
import logging
from uuid import uuid4
import base64

from tornado.web import HTTPError
import os.path

from pipelines import PipelinesError
from pipelines.pipeline.pipeline import Pipeline
from pipelines.plugin.exceptions import PluginError

log = logging.getLogger('pipelines')

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
        self.pipe = None

    def load(self, pipeline_filepath, folder_path, params={}):
        base_params = {
            'status_file': os.path.join(folder_path, 'status.json'),
            'log_file': os.path.join(folder_path, 'output.log')
        }
        base_params.update(params)
        self.log_file = base_params['log_file']
        self.pipe = Pipeline.from_yaml(pipeline_filepath, base_params)

    def _write_user_context(self, context):
        user = context.get('username', 'anonymous')
        ip = context.get('ip', '(unknown ip)')
        timestamp = datetime.utcnow().strftime('%Y:%m:%d %H:%M:%S')
        msg = 'Pipeline triggered by: "{}" [ip: {}]'.format(user, ip)
        to_write = '{timestamp}: {message}'.format(timestamp=timestamp,
                                                   message=msg)
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(to_write)
                f.write('\n')

    @concurrent.run_on_executor
    def run(self, context):
        log.debug('Running with context: {}'.format(context))
        self._write_user_context(context)
        if self.pipe:
            return self.pipe.run()
        else:
            raise PipelinesError('AsyncRunner error. No pipeline.')


def _file_iterator(folder, extensions):
    for path in os.listdir(folder):
        for ext in extensions:
            if path.endswith('.%s' % ext):
                yield path


def _slugify_file(filename):
    basename = filename.rsplit('/', 1)[-1]
    return basename.rsplit('.', 1)[0]


def _run_id_iterator(slug, log_limits):
    dir_list = os.listdir(slug)
    #sorted by modify time
    dir_list = sorted(dir_list,key=lambda x: os.path.getmtime(os.path.join(slug, x)), reverse = True)
    for sub_folder in dir_list[:log_limits]:
        if _is_valid_uuid(sub_folder):
            yield sub_folder


def _is_valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


def _get_pipeline_filepath(workspace, slug):
    for ext in PIPELINES_EXT:
        yaml_filepath = os.path.join(workspace, '%s.%s' % (slug, ext))
        if os.path.exists(yaml_filepath):
            return yaml_filepath
            break
    return None

# TODO server.js line 211 to use this func
def walk_pipelines(workspace):
    for path in _file_iterator(workspace, extensions=PIPELINES_EXT):
        try:
            with open(os.path.join(workspace, path)) as f:
                yaml_string = f.read()
        except IOError as e:
            log.error('Can not read pipelines, file missing: {}'.format(path))
            continue

        try:
            pipeline_def = yaml.safe_load(yaml_string)
        except YAMLError:
            log.error('Skipping pipeline. Could not load yaml for: {}'.format(path))
            continue
        slug = _slugify_file(path)
        yield slug, pipeline_def


def _run_pipeline(handler, workspace, pipeline_slug, params={}, response_fn=None):
    log.debug('Running pipeline %s with params %s' % (pipeline_slug, params))
    # Guess the pipeline extension
    pipeline_filepath = _get_pipeline_filepath(workspace, pipeline_slug)
    if not pipeline_filepath:
        raise HTTPError(404, 'Pipeline not found')

    task_id = str(uuid4())
    folder_path = os.path.join(workspace, pipeline_slug, task_id)

    try:
        runner = AsyncRunner()
        runner.load(pipeline_filepath, folder_path, params)
    except (PipelinesError, PluginError) as e:
        handler.clear()
        handler.set_status(400)
        err_msg = 'Error loading pipeline: {}'.format(e.message)
        handler.finish(json.dumps({'message': err_msg}))
        logging.warn(err_msg)
        return

    os.makedirs(folder_path)

    if response_fn:
        response_fn(handler, task_id)
    else:
        handler.write(json.dumps({'task_id': task_id}, indent=2))
        handler.finish()

    username = handler.get_current_user()
    if isinstance(username, dict):
        username = username.get('username', 'unknown')

    user_context = {
        'username': username,
        'ip': handler.request.remote_ip
    }
    log.debug('user context: %s' % user_context)
    if 'authorization' in handler.request.headers:
        user_context['username'] = _parse_basicauth_user(handler.request.headers['authorization'])
    
    yield runner.run(user_context)

def _parse_basicauth_user(basicauth_http_header):
    try:
        return base64.decodestring (basicauth_http_header.split(' ')[1]).split(':')[0]
    except Exception as e:
        log.warn('Could not parse nginx auth header: {}'.format(basicauth_http_header))
        return '(problem parsing user)'
