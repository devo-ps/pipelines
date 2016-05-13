from pipelines.plugins.bash_executor import BashExecutor
from pipelines.plugins.dummy_executor import DummyExecutor
from pipelines.plugins.python_executor import PythonExecutor
from pipelines.plugins.status_logger import StatusLogger
from pipelines.plugins.stdout_logger import StdoutLogger
from pipelines.plugins.webhook_logger import WebhookLogger

builtin_plugins = {
    'stdout_logger': StdoutLogger,
    'status_logger': StatusLogger,
    # 'file_logger': FileLogger,
    'webhook_logger': WebhookLogger,
    'bash': BashExecutor,
    'python': PythonExecutor,
    'dummy': DummyExecutor
}
