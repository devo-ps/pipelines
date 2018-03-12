import json
import logging

import filelock
import yaml
from tornado import gen
from tornado.escape import json_decode
from tornado.httputil import parse_body_arguments
from tornado.web import RequestHandler, HTTPError
from yaml.error import YAMLError

from pipelines.api import WEB_HOOK_CONFIG, PIPELINES_EXT
import os.path

from pipelines.api.utils import _run_pipeline, _file_iterator, walk_pipelines

log = logging.getLogger('pipelines')

slackbot_commands = None

def load_slackbot_commands(workspace_path):
    slackbot_configs = {}
    for slug, pipeline_def in walk_pipelines(workspace_path):
        slackbot_confs = filter(lambda d: d.get('type') == 'slackbot', pipeline_def.get('triggers', []))
        for slackbot_conf in slackbot_confs:
            if slackbot_conf.get('command'):
                conf = {
                    'command': slackbot_conf.get('command'),
                    'arguments': slackbot_conf.get('arguments', []),
                    'slug': slug
                }
                slackbot_configs[conf['command']] = conf
                log.debug('Added slackbot config for %s, conf: %s', slug, conf)
            else:
                log.debug('Slackbot config is missing "command" parameter, skipping, slug=', slug, slackbot_conf)

    return slackbot_configs

def _read_slackbot_state(workspace):
    conf_path = os.path.join(workspace, WEB_HOOK_CONFIG)
    if not os.path.exists(conf_path):
        raise HTTPError(404, 'Pipelines config not found')

    with open(conf_path) as f:
        try:
            pipeline_state = json.load(f)
            slackbot_slug = pipeline_state.get('slackbot', {}).get('public_slug')
            if not slackbot_slug:
                raise HTTPError(404, 'Not found')
            return slackbot_slug
        except KeyError:
            raise HTTPError(500, 'Invalid webhook config')
    return None


def update_pipelines_config(workspace_path, fn):
    with filelock.FileLock(os.path.join(workspace_path, '.pipelinelock')):
        pipeline_config = {'webhooks': {}, 'slackbot': {}}
        config_path = os.path.join(workspace_path, WEB_HOOK_CONFIG)
        if os.path.isfile(config_path):
            with open(config_path) as wh_file:
                pipeline_config = json.load(wh_file)

        fn(pipeline_config)

        with open(config_path, 'w') as wh_file:
            json.dump(pipeline_config, wh_file, indent=2)

class SlackbotHandler(RequestHandler):

    def _parse_body_args(self, body):
        args = {}
        parse_body_arguments('application/x-www-form-urlencoded', self.request.body, args, {})
        # command, environment, component, branch = args['text'].split(' ')
        command_args = args['text'][0].split(' ')

        return {
            'response_url': args.get('response_url')[0],
            'user': args.get('user_name', [''])[0],
            'channel': args['channel_name'][0] if len(args.get('channel_name',[])) else None,
            'command':  command_args[0] if len(command_args) else '',
            'args': args['text'][0].split(' '),
            'slash_command': args['command'][0]
        }


    # def _get_slackbot_context(self, command_name, workspace):
    #     conf_path = os.path.join(workspace, WEB_HOOK_CONFIG)
    #     if not os.path.exists(conf_path):
    #         raise HTTPError(404, 'Webhook config not found')
    #
    #     with open(conf_path) as f:
    #         try:
    #             pipeline_state = json.load(f)
    #
    #         except KeyError:
    #             raise HTTPError(500, 'Invalid slackbot config')
    #
    #     slackbot_conf = pipeline_state.get('slackbot-commands', {})
    #     slackbot_context = slackbot_conf.get(command_name)
    #     if not slackbot_context:
    #         raise HTTPError(404, 'Not found')
    #
    #     log.debug('Slackbot context %s for command %s', slackbot_context, command_name)
    #     return slackbot_context

    def usage(self, commands, slash_command):
        commands = {c['command']: '%s %s %s' % (slash_command, c['command'], ' '.join(['(%s)' % arg for arg in c['arguments'][1:] ]))
          for c in commands.values()}
        log.debug('Showing slackbot usage, commands: %s', commands)
        self.write({
            'response_type': 'in_channel',
            'text': 'Usage',
            'attachments': [{"text": yaml.dump(commands, default_flow_style=False)}]
        })
        self.finish()

    @gen.coroutine
    def post(self, slug):
        log.info('SlackbotHandler %s' % slug)

        workspace = self.settings['workspace_path']

        # validate request
        pipelines_slug = _read_slackbot_state(workspace)
        if slug != pipelines_slug:
            raise HTTPError(404, 'Slug doesn\'t match %s %s' % (slug, pipelines_slug))

        # Compile the slackbot command configs the first time
        slackbot_commands = load_slackbot_commands(workspace)

            # def update_config(pipeline_config):
            #     pipeline_config['slackbot'] = slackbot_configs
            # update_pipelines_config(workspace, update_config)
        log.debug('Generate slackbot commands. Found %s slackbot commands' % len(slackbot_commands.keys()))

        body_args = {}
        parse_body_arguments('application/x-www-form-urlencoded', self.request.body, body_args, {})
        log.info('Body: %s' % json.dumps(body_args))

        command_args = self._parse_body_args(body_args)

        if command_args['command'] in ['', 'usage', 'help', 'commands']:
            return self.usage(slackbot_commands, command_args['slash_command'])

        if command_args['command'] not in slackbot_commands:
            log.warn('Unknown slack command %s' % command_args['command'])
            self.write({
                'response_type': 'in_channel',
                'text': 'Unknown command %s' % command_args['command'],
                'attachments': []
            })
            return self.finish()

        command_config = slackbot_commands[command_args['command']]

        # slackbot_context = self._get_slackbot_context(command_args['command'], workspace)
        # if not slackbot_context:
        #     raise HTTPError(404, 'Not found')

        pipeline_args = {
            'trigger': 'slackbot',
            'slakbot_args': command_args
        }

        # Map args
        named_slackbot_args = {}
        if command_config.get('arguments'):
            if len(command_config.get('arguments')) != len(command_args['args']):
                log.warn('Incorrect amount of arguments %s, expecting %s' % (len(command_args['args']), len(command_config.get('arguments'))))
                return'Incorrect amount of arguments %s, expecting %s' % (len(command_args['args']), len(command_config.get('arguments')))

            for i, arg_name in  enumerate(command_config.get('arguments', [])):
                named_slackbot_args[arg_name] = command_args['args'][i]

        pipeline_args.update(named_slackbot_args)
        pipeline_args['webhook_content'] = named_slackbot_args  # For legacy reasons

        def response_fn(handler, task_id):
            handler.write({
                'response_type': 'in_channel',
                'text': '%s triggered by %s' % (command_args['command'], command_args.get('user')),
                'attachments': [{"text": yaml.dump(named_slackbot_args, default_flow_style=False)}]
            })
            handler.finish()
        return _run_pipeline(self, workspace, command_config['slug'], params=pipeline_args, response_fn=response_fn)
