import json
import logging
from datetime import datetime
import os.path

from pipelines.plugin.base_plugin import BasePlugin


log = logging.getLogger('pipelines')

'''
    No-op plugin that is used just to store configuration. Configuration is used by the web API.
'''

class SlackbotPlugin(BasePlugin):
    hook_prefix = ''
    hooks = ()
