from pipelineplugins.bash_executor import BashExecutor
from pipelineplugins.dummy_executor import DummyExecutor
from pipelineplugins.python_executor import PythonExecutor
from pipelineplugins.stdout_logger import StdoutLogger
from pipelineplugins.webhook_logger import WebhookLogger

builtin_plugins = {
    'stdout_logger': StdoutLogger,
    'webhook_logger': WebhookLogger,
    'bash': BashExecutor,
    'python': PythonExecutor,
    'dummy': DummyExecutor
}