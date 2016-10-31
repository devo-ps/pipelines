import logging
import requests
from pipelines.plugins.stdout_logger import StdoutLogger
from pipelines.plugin.exceptions import PluginError

RETRY_COUNT = 2

log = logging.getLogger('pipelines')

class WebhookLogger(StdoutLogger):

    def __init__(self, webhook_url):
        super(WebhookLogger, self).__init__()
        self.webhook_url = webhook_url
        self.write_on = ['on_pipeline_finish']

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        if 'webhook_url' not in conf_dict:
            # raise PluginError('WebhookLogger is missing webhook_url'
            #                   'configuration parameter')
            log.debug('WebhookLogger missing webhook_url parameter. Disabling.')
        else:
            if not isinstance(conf_dict['webhook_url'], basestring):
                raise PluginError('WebhookLogger has invalid webhook_url parameter')

        return WebhookLogger(conf_dict.get('webhook_url'))

    def write(self, msg):
        if not self.webhook_url:
            return

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
