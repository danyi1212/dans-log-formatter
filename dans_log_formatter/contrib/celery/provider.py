from logging import LogRecord
from typing import Any

from celery import current_task

from providers.abstract import AbstractProvider


class CeleryTaskProvider(AbstractProvider):
    def __init__(self, *, include_args: bool = False):
        self.include_args = include_args

    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:  # noqa ARG002
        if current_task is None:
            return None

        result = {
            "resource": current_task.name,
            "task.id": current_task.request.id,
            "task.retries": current_task.request.retries,
            "task.root_id": current_task.request.root_id,
            "task.parent_id": current_task.request.parent_id,
            "task.origin": current_task.request.origin,
            "task.delivery_info": current_task.request.delivery_info,
            "task.worker": current_task.request.hostname,
        }
        if self.include_args:
            result["task.args"] = current_task.request.args
            result["task.kwargs"] = current_task.request.kwargs

        return result
