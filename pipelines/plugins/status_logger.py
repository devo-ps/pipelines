import json
import logging

from pipelines.plugin.base_plugin import BasePlugin
from pipelines.plugin.exceptions import PluginError


log = logging.getLogger('pipelines')

class StatusLogger(BasePlugin):
    hook_prefix = ''
    hooks = (
        'on_pipeline_start',
        'on_pipeline_finish',
    )
    file_path = None

    def __init__(self, file_path=None):
        super(StatusLogger, self).__init__()

        if file_path:
            self.file_path = file_path

    @classmethod
    def from_dict(cls, conf_dict):
        return StatusLogger(conf_dict.get('status_file'))

    def on_pipeline_start(self, *args):
        self._write({'status': 'processing'})

    def on_pipeline_finish(self, *args):
        self._write({'status': 'success'})

    def _write(self, status):
        if self.file_path:
            with open(self.file_path, 'w+') as f:
                json.dump(status, f, indent=2)
        # else:
        #     # Write to stdout
        #     print(json.dumps(status, indent=2))
