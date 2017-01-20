import logging
import os, sys
import json
import requests
import base64

from pipelines.plugin.base_plugin import BasePlugin
from pipelines.plugins.base_executor import BaseExecutorPlugin
from pipelines.pipeline.task import TaskResult, EXECUTION_SUCCESSFUL, EXECUTION_FAILED
from pipelines.plugin.exceptions import PluginError

log = logging.getLogger('pipelines')

class ZatoExecutor(BasePlugin):
    hook_prefix = 'zato'
    hooks = ('execute',)

    def __init__(self, base_params, event_mgr):
        super(ZatoExecutor, self).__init__()
        self.event_mgr = event_mgr
        self.base_params = base_params

    def execute(self, args_dict):
        self.from_prev_frame() # couldn't figure out how to get at the arguments otherwise..
        enc_payload = base64.b64encode(json.dumps(self.base_params, indent=2))
        payload = dict(name=args_dict['service'], payload=enc_payload, channel='http', data_format='json')
        zato_url = os.environ.get('ZATO_INVOKE_URI')
        zato_auth = (os.environ.get('ZATO_USERNAME'), os.environ.get('ZATO_PASSWORD'))

        log.info('Sending JSON payload to %s:\n%s', args_dict['service'], json.dumps(self.base_params, indent=2))
        
        res_pl = None
        resp = requests.post(zato_url, json=payload, timeout=None, auth=zato_auth)
        
        if resp.ok:
            log.debug('successfully made request to endpoint')
            res_pl = json.loads(base64.b64decode(resp.json()['zato_service_invoke_response']['response']))
        else:
            log.debug('could not make zato request. status: {}'.format(resp.status_code))

        self.event_mgr.trigger('on_task_event', {'output': 'service responded with:\n\n' + json.dumps(res_pl, indent=2) + '\n'})

        if isinstance(res_pl, (list, str)):
            return TaskResult(EXECUTION_SUCCESSFUL, 'Returned a string or list, assuming okay.')
        elif isinstance(res_pl, dict):
            if res_pl.get('error', None) is True:
                 return TaskResult(EXECUTION_FAILED, 'Fail (error=True)')
            if res_pl.get('result', None) is True:
                 return TaskResult(EXECUTION_SUCCESSFUL, 'Okay (result=True)')
            if res_pl.get('error', None) is False:
                 return TaskResult(EXECUTION_SUCCESSFUL, 'Okay (error=False)')
           
        return TaskResult(EXECUTION_FAILED, 'do not know how to parse resposne')

    def from_prev_frame(self):
        f = sys._getframe(0)
        while True:
            f = f.f_back
            if f is None: return
            if 'params' in f.f_locals and 'task' in f.f_locals:
                self.base_params.update(**f.f_locals['params'].copy())

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        base_params = conf_dict.copy()
        del base_params['log_file']
        del base_params['status_file']
        return ZatoExecutor(base_params, event_mgr)

