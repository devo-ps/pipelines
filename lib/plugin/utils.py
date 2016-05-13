import json
import logging

from datetime import datetime, timedelta

from pipelines.pipeline.task import Task, TaskResult


def class_name(obj):
    if isinstance(obj, type):
        return obj.__name__

    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
        return obj.__class__.__name__

    return str(obj)


def setup_logging(level=logging.DEBUG):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

    # Hide most logging for 3rd party libs
    for pack in ['sh', 'requests']:
        logging.getLogger(pack).setLevel(logging.WARNING)

def datetime_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, Task):
        serial = json.dumps({
            'name': obj.name,
            'executor': obj.executor,
            'args': obj.args,
        })
        return serial

    if isinstance(obj, TaskResult):
        serial = json.dumps({
            'status': obj.status,
            'message': obj.message
        })
        return serial

    if isinstance(obj, timedelta):
        return obj.total_seconds()

    return json.dumps(obj)
