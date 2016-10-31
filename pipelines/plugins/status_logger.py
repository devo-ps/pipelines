import json
import logging
from datetime import datetime
import os.path

from pipelines.plugin.base_plugin import BasePlugin


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
    def from_dict(cls, conf_dict, event_mgr=None):
        return StatusLogger(conf_dict.get('status_file'))

    def on_pipeline_start(self, *args):

        self._write({
            'status': 'running',
            'start_time': datetime.now().isoformat()
        })

    def on_pipeline_finish(self, pipeline_context):
        self._write({
            'status': pipeline_context['status'],
            'finish_time': datetime.now().isoformat()
        })

    def _write(self, status):
        if self.file_path:
            base = {}
            if os.path.isfile(self.file_path):
                with open(self.file_path) as f:
                    base = json.load(f)

            base.update(status)

            with open(self.file_path, 'w+') as f:
                json.dump(base, f, indent=2)
