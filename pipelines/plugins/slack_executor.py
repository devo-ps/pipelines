import logging
import requests
from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError

log = logging.getLogger('pipelines')

RETRY_COUNT = 2

class SlackExecutor(BaseExecutorPlugin):
    hook_prefix = 'slack'
    hooks = ('execute',)

    # webhook_url = 'https://hooks.slack.com/services/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'

    def __init__(self, slack_webhook):
        self.slack_webhook = slack_webhook

    def execute(self, args_dict):
        # try to use task level parameter first, then fallback to the top level
        slack_webhook = args_dict.get('slack_webhook', self.slack_webhook)
        if not slack_webhook:
            raise PluginError('SlackExecutor is missing slack_webhook parameter. Can not execute')

        if not isinstance(slack_webhook, str):
            raise PluginError('SlackExecutor has invalid slack_webhook parameter')

        if 'message' not in args_dict:
            raise PluginError('SlackExecutor got incorrect arguments, got: {}'.format(
                args_dict.keys()
            ))
        message = args_dict['message']

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)

        payload = {
            'username': 'Pipelines',
            'link_names': 1,
            'text': message
        }

        for i in range(RETRY_COUNT + 1):
            resp = requests.post(slack_webhook, json=payload)
            if resp.ok:
                log.debug('Successfully sent slack message')
                break
            log.debug('Problem sending slack message. Status {}'.format(resp.status_code))
        else:
            log.warning('Could not successfully send slack message. Status: {}'.format(resp.status_code))
            return TaskResult(EXECUTION_FAILED, 'Sending slack notification failed')

        return TaskResult(EXECUTION_SUCCESSFUL, 'Sending slack notification successful')

    def _parse_args_dict(self, args_dict):
        return args_dict['message']

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        if 'slack_webhook' not in conf_dict:
            log.debug('SlackExecutor is missing slack_webhook parameter')
        else:
            if not isinstance(conf_dict['slack_webhook'], str):
                raise PluginError('SlackExecutor has invalid slack_webhook parameter')
            log.debug('SlackExecutor got slack_webhook parameter: %s' % conf_dict['slack_webhook'])

        return cls(slack_webhook=conf_dict.get('slack_webhook'))

if __name__ == '__main__':
    pass
