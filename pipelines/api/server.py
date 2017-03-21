import os
import re
import json
from copy import copy

from operator import itemgetter

import yaml
import logging
import tornado
import filelock
from uuid import uuid4
from yaml import YAMLError
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.ioloop import IOLoop
from tornado import concurrent, ioloop
from tornado.web import (
    RequestHandler,
    Application,
    url,
    HTTPError,
    authenticated,
    StaticFileHandler
)
from pipelines import PipelinesError
from pipelines.api.ghauth import GithubOAuth2LoginHandler
from pipelines.plugin.exceptions import PluginError
from pipelines.utils import conf_logging
from pipelines.pipeline.pipeline import Pipeline

WEB_HOOK_CONFIG = '.pipeline-store.json'
PIPELINES_EXT = ('yml', 'yaml')

log = logging.getLogger('pipelines')


class PipelinesRequestHandler(RequestHandler):
    def get_current_user(self):
        log.debug('Get current user')
        log.debug(self.settings)
        if not self.settings.get('auth'):
            log.debug('noauth')
            # No authentication required
            return 'guest'
        user_cookie = self.get_secure_cookie("user")
        if user_cookie:
            log.debug('user cookie %s' % user_cookie)
            return json.loads(user_cookie)
        log.debug('none')
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
        self.pipe = None

    def load(self, pipeline_filepath, folder_path, params={}):
        base_params = {
            'status_file': os.path.join(folder_path, 'status.json'),
            'log_file': os.path.join(folder_path, 'output.log')
        }
        base_params.update(params)
        self.pipe = Pipeline.from_yaml(pipeline_filepath, base_params)

    @concurrent.run_on_executor
    def run(self):
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


def _run_id_iterator(slug):
    for sub_folder in os.listdir(slug):
        if _is_valid_uuid(sub_folder):
            yield sub_folder


def _is_valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


def _get_webhook_id(trigger_identifier, wh_config):
    for k, v in wh_config.items():
        if trigger_identifier == v:
            return k
    return str(uuid4())


def _get_pipeline_filepath(workspace, slug):
    for ext in PIPELINES_EXT:
        yaml_filepath = os.path.join(workspace, '%s.%s' % (slug, ext))
        if os.path.exists(yaml_filepath):
            return yaml_filepath
            break
    return None


def _run_pipeline(handler, workspace, pipeline_slug, params={}):
    log.debug('Running pipeline %s with params %s' % (pipeline_slug, json.dumps(params)))
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
        handler.finish(json.dumps({'message': 'Error loading pipeline: %s' % e.message}))
        return

    os.makedirs(folder_path)

    handler.write(json.dumps({'task_id': task_id}, indent=2))
    handler.finish()

    yield runner.run()


def _authenticate_user(auth_settings, username, password):
    if username != auth_settings['username'] or password != auth_settings['password']:
        return False
    return True


class WebhookHandler(RequestHandler):
    def _get_wh_context(self, webhook_id, workspace):
        conf_path = os.path.join(workspace, WEB_HOOK_CONFIG)
        if not os.path.exists(conf_path):
            raise HTTPError(404, 'Webhook config not found')

        with open(conf_path) as f:
            try:
                pipeline_state = json.load(f)
                wh_conf = pipeline_state.get('webhooks', {})
                if webhook_id not in wh_conf:
                    raise HTTPError(404, 'Not found')
                webhook_context = wh_conf[webhook_id]

                log.debug('wh context %s', webhook_context)
                return webhook_context
            except KeyError:
                raise HTTPError(500, 'Invalid webhook config')
        return None

    @gen.coroutine
    def post(self, webhook_id):
        log.debug('WebhookHandler: %s' % webhook_id)
        workspace = self.settings['workspace_path']
        wh_context = self._get_wh_context(webhook_id, workspace)
        if not wh_context:
            raise HTTPError(404, 'Not found')

        params = {'webhook_content': {'raw': self.request.body}}
        if self.request.body:
            try:
                json_body = tornado.escape.json_decode(self.request.body)
                params['webhook_content'].update(json_body)
            except ValueError:
                pass

        return _run_pipeline(self, workspace, wh_context['slug'], params=params)


class GetTriggersHandler(PipelinesRequestHandler):
    @authenticated
    def get(self, pipeline_slug):
        workspace = self.settings['workspace_path']
        log.debug('Get triggers %s' % pipeline_slug)
        yaml_filepath = _get_pipeline_filepath(workspace, pipeline_slug)

        if not os.path.exists(yaml_filepath):
            print('Not found %s' % yaml_filepath)
            raise HTTPError(404, 'Pipeline not found')

        with open(yaml_filepath) as f:
            try:
                pipeline_def = yaml.load(f)
                log.debug(pipeline_def)
            except yaml.YAMLError as e:
                log.exception(e)
                raise HTTPError(500, 'Invalid yaml config')

            with filelock.FileLock(os.path.join(workspace, '.pipelinelock')):
                pipeline_config = {'webhooks': {}}
                config_path = os.path.join(workspace, WEB_HOOK_CONFIG)
                if os.path.isfile(config_path):
                    with open(config_path) as wh_file:
                        pipeline_config = json.load(wh_file)
                        if 'webhooks' not in pipeline_config:
                            pipeline_config['webhooks'] = {}

                for index, trigger in enumerate(pipeline_def.get('triggers', [])):
                    if trigger.get('type') == 'webhook':
                        wh_identifier = {
                            'slug': pipeline_slug,
                            'index': index,
                            'type': trigger.get('type')
                        }
                        wh_id = _get_webhook_id(wh_identifier, pipeline_config['webhooks'])
                        trigger['webhook_id'] = wh_id
                        pipeline_config['webhooks'][wh_id] = wh_identifier

                with open(config_path, 'w') as wh_file:
                    json.dump(pipeline_config, wh_file, indent=2)

            self.write(json.dumps({'triggers': pipeline_def.get('triggers', [])}, indent=2))
            self.finish()


class LoginHandler(PipelinesRequestHandler):
    def get(self):
        log.debug('Login page %s.' % self.settings['auth'])
        login_type = self.settings['auth'].get('type') if self.settings['auth'] else None
        self.render(
            'templates/login.html',
            error_msg=None,
            login_type=login_type
        )

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
            self.render(
                'templates/login.html',
                error_msg='Wrong username or password',
                login_type=self.settings['auth'].get('type') if self.settings['auth'] else None
            )


class GetPipelinesHandler(PipelinesRequestHandler):
    @authenticated
    def get(self):
        log.debug('Get pipelines')
        workspace = self.settings['workspace_path']
        log.debug('Getting all pipelines')
        pipelines = []
        for path in _file_iterator(workspace, extensions=PIPELINES_EXT):
            try:
                with open(os.path.join(workspace, path)) as f:
                    yaml_string = f.read()
            except IOError as e:
                log.error('Can not read pipelines, file missing: {}'.format(path))
                continue

            try:
                pipeline_def = yaml.load(yaml_string)
            except YAMLError:
                log.error('Skipping pipeline. Could not load yaml for: {}'.format(path))
                continue

            slug = _slugify_file(path)
            full_path = os.path.join(workspace, slug)
            run_dict = {
                'slug': slug,
                'run_ids': [],
                'definition': pipeline_def,
                'raw': yaml_string
            }
            if os.path.isdir(full_path):
                # expect to have runs
                ids = list(_run_id_iterator(full_path))
                runs = _fetch_runs(full_path, ids)
                run_dict['run_ids'] = ids
                run_dict['runs'] = runs
            pipelines.append(run_dict)

        # Sort the pipelines alphabetically
        sorted_pipelines = sorted(pipelines, key=itemgetter('slug'))
        
        self.write(json.dumps(sorted_pipelines, indent=2))
        self.finish()


class GetPipelineHandler(PipelinesRequestHandler):
    @authenticated
    def get(self, pipeline_slug):
        log.debug('Get pipeline %s' % pipeline_slug)
        workspace = self.settings['workspace_path']

        folder_path = os.path.join(workspace, pipeline_slug)
        file_path = ''
        if os.path.exists(folder_path + '.yml'):
            file_path = folder_path + '.yml'
        elif os.path.exists(folder_path + '.yaml'):
            file_path = folder_path + '.yaml'
        else:
            raise HTTPError(404, 'Pipeline not found')

        with open(file_path) as f:
            yaml_string = f.read()
        pipeline_def = yaml.load(yaml_string)

        # expect to have runs
        ids = list(_run_id_iterator(folder_path))
        runs = _fetch_runs(folder_path, ids)

        ret = {
            'slug': pipeline_slug,
            'run_ids': ids,
            'definition': pipeline_def,
            'raw': yaml_string
        }
        if runs:
            ret['runs'] = runs
        self.write(json.dumps(ret, indent=2))
        self.finish()


def _fetch_runs(path, run_ids):
    ret = []

    for run_id in run_ids:
        item = {'id': run_id}
        run_status_path = os.path.join(path, run_id, 'status.json')
        if os.path.isfile(run_status_path):
            with open(run_status_path) as f:
                try:
                    run_status = json.load(f)
                    item.update(run_status)
                except ValueError:
                    log.warning('Failed to parse json file. Skipping. File: %s' % run_status_path)
        else:
            log.debug('Run status file doesn\'t exist: %s' % run_status_path)

        ret.append(item)
    ret.sort(key=lambda run: run.get('start_time'), reverse=True)
    return ret


class GetLogsHandler(PipelinesRequestHandler):
    def get(self, pipeline_slug, task_id):
        log.debug('Get logs: {}, {}'.format(pipeline_slug, task_id))
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
        log.debug('Get status of: {}, {}'.format(pipeline_slug, task_id))
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
        log.debug('Run pipeline: {}'.format(pipeline_slug))
        workspace = self.settings['workspace_path']
        log.debug('Running pipeline')

        prompted_params = {}
        if self.request.body:
            try:
                json_body = tornado.escape.json_decode(self.request.body)
                prompted_params = json_body.get('prompt', {})
            except ValueError:
                raise HTTPError(400, 'Bad Request')

        return _run_pipeline(self, workspace, pipeline_slug, params=prompted_params)

    def options(self, pipeline_slug):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.finish()


class AuthStaticFileHandler(StaticFileHandler, PipelinesRequestHandler):
    @authenticated
    def get(self, *args, **kwargs):
        return super(AuthStaticFileHandler, self).get(*args, **kwargs)


def _get_auth_dict(auth_settings):
    if not auth_settings or len(auth_settings) == 0:
        return None

    if auth_settings[0] == 'static':
        return {
            'type': 'static',
            'username': auth_settings[1],
            'password': auth_settings[2]
        }

    if auth_settings[0] == 'gh':
        return {
            'type': 'gh',
            'teams': auth_settings[1]
        }


def make_app(workspace='fixtures/workspace', auth=None):
    if not os.path.isdir(workspace):
        raise PipelinesError('Workspace is not a valid directory: %s' % workspace)

    auth_dict = _get_auth_dict(auth)

    slug_regexp = '[0-9a-zA-Z_\-]+'
    endpoints = [
        url(r"/api/pipelines/", GetPipelinesHandler),
        url(r"/api/pipelines/({slug})/".format(slug=slug_regexp), GetPipelineHandler),
        url(r"/api/pipelines/({slug})/run".format(slug=slug_regexp), RunPipelineHandler),
        url(r"/api/pipelines/({slug})/({slug})/status".format(slug=slug_regexp), GetStatusHandler),
        url(r"/api/pipelines/({slug})/({slug})/log".format(slug=slug_regexp), GetLogsHandler),
        url(r"/api/pipelines/({slug})/triggers".format(slug=slug_regexp), GetTriggersHandler),
        url(r"/api/webhook/({slug})".format(slug=slug_regexp), WebhookHandler),
        (r"/login", LoginHandler),
        (r'/(.*)', AuthStaticFileHandler, {'path': _get_static_path('app'), "default_filename": "index.html"}),
    ]

    if auth_dict and auth_dict.get('type') == 'gh':
        endpoints.insert(len(endpoints) - 1, (r"/ghauth", GithubOAuth2LoginHandler)),

    return Application(endpoints,
                       workspace_path=workspace,
                       auth=auth_dict,
                       login_url="/login",
                       debug="True",
                       cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="  # TODO: make configurable
                       )


def _get_static_path(subpath):
    this_path = os.path.realpath(__file__)
    this_dir = os.path.dirname(this_path)
    ret = os.path.join(this_dir, 'app_dist')
    log.debug('Serving %s' % ret)
    return ret


def _hide_pw(conf_dict):
    out = copy(conf_dict)
    if 'auth' in out and len(out['auth']) > 0 and out['auth'][0] == 'static':
        out['auth'] = (out['auth'][0], out['auth'][1], '*******')
    return out


def main(config):
    conf_logging()
    app = make_app(config.get('workspace', 'fixtures/workspace'), config.get('auth'))
    app.listen(
        int(config.get('port', 8888)),
        address=config.get('host', '127.0.0.1'),
    )

    log.info('Starting server: {}'.format(_hide_pw(config)))
    io_loop = IOLoop.current()
    io_loop.start()


if __name__ == '__main__':
    main()
