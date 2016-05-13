import logging
import requests
from pipelines.plugins.stdout_logger import StdoutLogger
from pipelines.plugin.exceptions import PluginError

RETRY_COUNT = 2

log = logging.getLogger()

class WebhookLogger(StdoutLogger):

    webhook_url = 'https://hooks.slack.com/services/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'

    def __init__(self, webhook_url):
        super(WebhookLogger, self).__init__()

        self.write_on = ['on_pipeline_finish']

    @classmethod
    def from_dict(cls, conf_dict):
        if 'webhook_url' not in conf_dict:
            raise PluginError('WebhookLogger is missing webhook_url'
                              'configuration parameter')

        if not isinstance(conf_dict['webhook_url'], basestring):
            raise PluginError('WebhookLogger has invalid webhook_url parameter')

        return WebhookLogger(conf_dict['webhook_url'])

    def write(self, msg):
        payload = {
            'username': 'Pipelines',
            'text': msg
        }

        for i in range(RETRY_COUNT + 1):
            resp = requests.post(self.webhook_url, json=payload)
            if resp.ok:
                log.debug('Successfully sent webhook')
                break
            log.debug('Problem sending webhook. Status {}'.format(resp.status_code))
        else:
            log.warning('Could not successfully send webhook. Status: {}'.format(resp.status_code))
