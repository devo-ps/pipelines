import logging

from pipelines.plugin.base_plugin import BasePlugin
from pipelines.plugin.exceptions import PluginError
from pipelines.plugin.utils import class_name

log = logging.getLogger()

class PluginManager():
    def __init__(self):
        self.plugins = {}

    def get_plugin(self, name):
        return self.plugins.get(name)

    def trigger(self, hook_name, *args):
        callbacks = self.plugins.get(hook_name, [])
        results = []
        for cb in callbacks:
            try:
                ret = cb(*args)
                results.append(ret)
            except Exception as e:
                log.error('Unknown error running callback {} hook {}, aborting.'.format(
                    cb.__name__, hook_name)
                )
                raise
        return results

    def get_plugin_count(self, hook_name=None):
        if hook_name is None:
            return reduce(lambda counter, p: counter + len(p), self.plugins.values(), 0)

        if hook_name in self.plugins:
            return len(self.plugins[hook_name])
        return 0

    def register_plugin(self, plugin_class, conf_dict):
        if not issubclass(plugin_class, BasePlugin):
            raise PluginError('Trying to register plugin that is not extending BasePlugin: {}'.format(
                class_name(plugin_class))
            )

        plugin = plugin_class.from_dict(conf_dict)

        for k in ['hook_prefix', 'hooks']:
            if not hasattr(plugin, k):
                raise PluginError('Plugin is missing "{}" attribute.'.format(k))

        prefix = '{}.'.format(plugin.hook_prefix) if plugin.hook_prefix else ''
        for hook in plugin.hooks:
            if not hasattr(plugin, hook):
                raise PluginError('Plugin {} is missing {}-function'.format(
                    class_name(plugin), hook
                ))

            hook_key = '{}{}'.format(prefix, hook)
            if hook_key not in self.plugins:
                self.plugins[hook_key] = []
            self.plugins[hook_key].append(getattr(plugin, hook))

if __name__ == '__main__':
    from pipelineplugins.dummy_executor import DummyExecutor
    from pipelineplugins.stdout_logger import StdoutLogger
    m = PluginManager()
    m.register_plugin(DummyExecutor)
    m.register_plugin(StdoutLogger)
    print m.get_plugin_count()
    print m.get_plugin_count('on_task_start')
