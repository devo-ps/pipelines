from pipelineplugins.bash_executor import BashExecutor
from pipelineplugins.dummy_executor import DummyExecutor
from pipelineplugins.python_executor import PythonExecutor
from pipelineplugins.status_logger import StatusLogger
from pipelineplugins.stdout_logger import StdoutLogger
from pipelineplugins.webhook_logger import WebhookLogger

builtin_plugins = {
    'stdout_logger': StdoutLogger,
    'status_logger': StatusLogger,
    # 'file_logger': FileLogger,
    'webhook_logger': WebhookLogger,
    'bash': BashExecutor,
    'python': PythonExecutor,
    'dummy': DummyExecutor
}