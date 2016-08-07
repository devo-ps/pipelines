import logging
import requests
from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError

log = logging.getLogger()
RETRY_COUNT = 2

class SlackExecutor(BaseExecutorPlugin):
    hook_prefix = 'slack'
    hooks = ('execute',)

    webhook_url = 'https://hooks.slack.com/services/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'

    def __init__(self):
        pass

    def execute(self, args_dict):
        print 'Slacking %s' % args_dict
        if 'message' not in args_dict:
            raise PluginError('BashExecutor got incorrect arguments, got: {}'.format(
                args_dict.keys()
            ))
        message = args_dict['message']

        if self.dry_run:
            return TaskResult(EXECUTION_SUCCESSFUL)

        payload = {
            'username': 'Pipelines',
            'text': message
        }

        for i in range(RETRY_COUNT + 1):
            resp = requests.post(self.webhook_url, json=payload)
            if resp.ok:
                log.debug('Successfully sent webhook')
                break
            log.debug('Problem sending webhook. Status {}'.format(resp.status_code))
        else:
            log.warning('Could not successfully send webhook. Status: {}'.format(resp.status_code))
            return TaskResult(EXECUTION_FAILED, 'Sending slack notification failed')

        return TaskResult(EXECUTION_SUCCESSFUL, 'Sending slack notification failed')

    def _parse_args_dict(self, args_dict):
        return args_dict['message']

    @classmethod
    def from_dict(cls, conf_dict):
        return cls()

if __name__ == '__main__':
    pass
