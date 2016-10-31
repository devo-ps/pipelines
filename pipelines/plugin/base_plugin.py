class BasePlugin(object):
    name = 'undefined'
    hooks = []
    dry_run = False

    @classmethod
    def from_dict(cls, conf_dict, event_mgr=None):
        return cls()
