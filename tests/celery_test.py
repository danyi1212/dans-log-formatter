import socket

from celery import Celery
from celery.result import EagerResult

from contrib.celery.provider import CeleryTaskProvider
from formatter import JsonLogFormatter
from utils import logger_factory, read_stream_log_line

app = Celery("test_app", broker="memory://", backend="cache+memory://")
app.conf.task_always_eager = True

logger, stream = logger_factory(JsonLogFormatter([CeleryTaskProvider(include_args=True)]))


@app.task(name="my_task")
def sample_task(param: int):  # noqa ARG001
    logger.info("Log example from a Celery task!")


def test_celery_integration():
    result: EagerResult = sample_task.delay(param=1)

    record = read_stream_log_line(stream)
    assert record
    assert record["status"] == "INFO"
    assert record["message"] == "Log example from a Celery task!"
    assert record["resource"] == "my_task"
    assert record["task.id"] == result.id
    assert record["task.retries"] == 0
    assert record["task.root_id"] is None
    assert record["task.parent_id"] is None
    assert record["task.origin"] is None
    assert record["task.delivery_info"] == {"exchange": None, "is_eager": True, "priority": None, "routing_key": None}
    assert record["task.worker"] == socket.gethostname()
    assert record["task.args"] == []
    assert record["task.kwargs"] == {"param": 1}
