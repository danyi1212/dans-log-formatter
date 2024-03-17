# Dan's Log Formatter
Every project needs logging, but why rewrite it each time?
Here's my simple, extensible formatter, designed so I never have to.

## Features

- **Extensible** - Add attributes to logs with ease, including simple error handling
- **Reusable** - Share your attribute providers across projects
- **Contextual** - Automatically adds useful context to logs
- **Out-of-the-box** - Include common providers for HTTP data, runtime, and more

My formatter and provider's default attributes are mostly compatible
with [DataDog's Standard Attributes](https://docs.datadoghq.com/logs/log_configuration/attributes_naming_convention/#standard-attributes).

#### Integrations

- **Django** - Automatically adds request context
- **FastAPI** - Automatically adds request context (including Starlette)
- **Flask** - Automatically adds request context
- **Celery** - Automatically adds task context
- **orjson** - Automatically adds JSON serialization context
- **ujson** - Automatically adds JSON serialization context

## Usage

Install my package using pip:

```shell
pip install dans-log-formatter
```

Then set up your logging configuration:

```python
import logging.config

from dans_log_formatter.providers.context import ContextProvider

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "providers": [
        ContextProvider(),
      ],  # optional
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "formatter": "json",
    }
  },
  "root": {
    "handlers": ["console"],
    "level": "INFO",
  },
})
```

Then, use it in your project:

```python
import logging

logger = logging.getLogger(__name__)


def main():
  logger.info("Hello, world!")


if __name__ == "__main__":
  main()

# STDOUT: {'timestamp': 1704060000.0, 'status': 'INFO', 'message': 'hello world!', 'location': 'my_module-main#4', 'file': '/Users/danyi1212/projects/my-project/my_module.py'}
```

## Providers

Providers add attributes to logs. You can use the built-in providers or create your own.

### Context Provider

Inject context into logs using decorator or context manager.

```python
from dans_log_formatter import JsonLogFormatter
from dans_log_formatter.providers.context import ContextProvider

formatter = JsonLogFormatter(providers=[ContextProvider()])
```

Then use the `inject_log_context()` as a context manager

```python
import logging
from dans_log_formatter.providers.context import inject_log_context

logger = logging.getLogger(__name__)

with inject_log_context({"user_id": 123}):
  logger.info("Hello, world!")

# STDOUT: {'timestamp': 1704060000.0, 'status': 'INFO', 'message': 'hello world!', 'user_id': 123, ...}
```

Alternatively, use it as `@inject_log_context()` decorator

```python
import logging
from dans_log_formatter.providers.context import inject_log_context

logger = logging.getLogger(__name__)


@inject_log_context({"custom_context": "value"})
def my_function():
  logger.info("Hello, world!")

# STDOUT: {'timestamp': 1704060000.0, 'status': 'INFO', 'message': 'hello world!', 'custom_context': 'value', ...}
```

### Extra Provider

Add `ExtraProvider()` from `dans_log_formatter.providers.extra`, then use the `extra={}` argument in your log calls

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Hello, world!", extra={"user_id": 123})
# STDOUT: {'timestamp': 1704060000.0, 'status': 'INFO', 'message': 'hello world!', 'user_id': 123, ...}
```

### Runtime Provider

Add `RuntimeProvider()` from `dans_log_formatter.providers.runtime` to add runtime information to logs.

#### Attributes

* `process` - Current process name and ID (e.g. `main (12345)`)
* `thread` - Current thread name and ID (e.g. `MainThread (12345)`)
* `task` - Current asyncio task name (e.g. `my_corrutine`)

### Create your own provider

```python
from logging import LogRecord
from typing import Any

from dans_log_formatter.providers.abstract import AbstractProvider


class MyProvider(AbstractProvider):
  """Add 'my_attribute' to all logs"""

  def get_attributes(self, record: LogRecord) -> dict[str, Any]:
    return {"my_attribute": "some value"}
```

You can also use the abstract context provider to add data from contextvars

```python
from contextvars import ContextVar
import logging
from typing import Any
from dataclasses import dataclass

from dans_log_formatter.providers.abstract_context import AbstractContextProvider


@dataclass
class User:
  id: int
  name: str


current_user_context: ContextVar[User | None] = ContextVar("current_user_context", default=None)


class MyContextProvider(AbstractContextProvider):
  """Add user.id and user.name context to logs"""

  def __init__(self):
    super().__init__(current_user_context)  # Pass the context

  def get_context_attributes(self, record: logging.LogRecord, current_user: User) -> dict[str, Any]:
    return {"user.id": current_user.id, "user.name": current_user.name}


logger = logging.getLogger(__name__)

token = current_user_context.set(User(id=123, name="John Doe"))
logger.info("Hello, world!")
current_user_context.reset(token)
# STDOUT: {'timestamp': 1704060000.0, 'status': 'INFO', 'message': 'Hello, world!', 'user.id': 123, 'user.name': 'John Doe', ...}
```

## Integrations

### Django Request Provider

Install using 'pip install dans-log-formatter[django]'

Add the 'LogContextMiddleware' to your Django middlewares at the very beginning.

```python
# settings.py
MIDDLEWARE = [
  "dans_log_formatter.contrib.django.middleware.LogContextMiddleware",
  ...
]
```

Then, add `DjangoRequestProvider()` to your formatter.

```python
# settings.py
from dans_log_formatter.contrib.django.provider import DjangoRequestProvider

LOGGING = {
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "providers": [
        DjangoRequestProvider(),
      ],
    }
  },
  # ...
}
```

#### Attributes

* `resource` - View route (e.g. `POST /api/users/<int:user_id>/delete`)
* `http.url` - Full URL (e.g. `https://example.com/api/users/123/delete`)
* `http.method` - HTTP method (e.g. `POST`)
* `http.referrer` - `Referrer` header (e.g. `https://example.com/previous-page`)
* `http.user_agent` - `useragent` header
* `http.remote_addr` - `X-Forwarded-For` or `REMOTE_ADDR` header
* `user.id` - User ID
* `user.name` - User's username
* `user.email` - User email

> Note: The `user` attributes available only inside the `django.contrib.auth.middleware.AuthenticationMiddleware`
> middleware.

### FastAPI Request Provider

Install using 'pip install dans-log-formatter[fastapi]'

Add the 'LogContextMiddleware' to your FastAPI app.

```python
from fastapi import FastAPI
from dans_log_formatter.contrib.fastapi.middleware import LogContextMiddleware

app = FastAPI()
app.add_middleware(LogContextMiddleware)
```

Then, add `FastAPIRequestProvider()` to your formatter.

```python
import logging.config
from dans_log_formatter.contrib.fastapi.provider import FastAPIRequestProvider

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "providers": [
        FastAPIRequestProvider(),
      ],
    }
  },
  # ...
})
```

#### Attributes

* `resource` - Route path (e.g. `POST /api/users/{user_id}/delete`)
* `http.url` - Full URL (e.g. `https://example.com/api/users/123/delete`)
* `http.method` - HTTP method (e.g. `POST`)
* `http.referrer` - `Referrer` header (e.g. `https://example.com/previous-page`)
* `http.user_agent` - `useragent` header
* `http.remote_addr` - `X-Forwarded-For` header or the `request.client.host` attribute

### Flask Request Provider

Install using 'pip install dans-log-formatter[flask]'

Add the 'FlastRequestProvider' to your formatter, and its magic!

```python
import logging.config
from dans_log_formatter.contrib.flask.provider import FlaskRequestProvider

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "providers": [
        FlaskRequestProvider(),
      ],
    }
  },
  # ...
})
```

#### Attributes

* `resource` - URL path (e.g. `POST /api/users/123/delete`)
* `http.url` - Full URL (e.g. `https://example.com/api/users/123/delete`)
* `http.method` - HTTP method (e.g. `POST`)
* `http.referrer` - `Referrer` header (e.g. `https://example.com/previous-page`)
* `http.user_agent` - `useragent` header
* `http.remote_addr` - `request.remote_addr` attribute

### Celery Task Provider

Install using 'pip install dans-log-formatter[celery]'

Add the 'CeleryTaskProvider' to your formatter, and its magic!

```python
import logging.config
from dans_log_formatter.contrib.celery.provider import CeleryTaskProvider

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "providers": [
        CeleryTaskProvider(),  # optional include_args=True
      ],
    }
  },
  # ...
})
```

#### Attributes

* `resource` - Task name (e.g. `my_project.tasks.my_task`)
* `task.id` - Task ID
* `task.retries` - Number of retries
* `task.root_id` - Root task ID
* `task.parent_id` - Parent task ID
* `task.origin` - Producer host name
* `task.delivery_info` - Delivery info (
  e.g. `{"exchange": "my_exchange", "routing_key": "my_routing_key", "queue": "my_queue"}`)
* `task.worker` - Worker hostname
* `task.args` - Task arguments (if `include_args=True`)
* `task.kwargs` - Task keyword arguments (if `include_args=True`)

> Warning: Including task arguments can expose sensitive information, and may result in very large logs.

### ujson Formatter

Install using 'pip install dans-log-formatter[ujson]'

Uses `ujson` for JSON serialization of the log records.

```python
import logging.config

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.contrib.ujson.UJsonLogFormatter",
      "providers": [],  # optional
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "formatter": "json",
    }
  },
  "root": {
    "handlers": ["console"],
    "level": "INFO",
  },
})
```

### orjson Serializer Formatter

Install using 'pip install dans-log-formatter[orjson]'

Uses `orjson` for JSON serialization of the log records.

```python
import logging.config

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.contrib.orjson.OrJsonLogFormatter",
      "providers": [],  # optional
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "formatter": "json",
    }
  },
  "root": {
    "handlers": ["console"],
    "level": "INFO",
  },
})
```

## Available Formatters

By default, all formatter includes the following attributes:

* `timestamp` - Unix timestamp (same as the `record.created` attribute, or the value returned
  by `time.time()`. [See the docs](https://docs.python.org/3/library/logging.html#logrecord-attributes))
* `status` - Log level name (e.g. `INFO`, `ERROR`, `CRITICAL`)
* `message` - Log message
* `location` - Location of the log call (e.g. `my_module-my_func#4`)
* `file` - File path of the log call (e.g. `/Users/danyi1212/projects/my-project/my_module.py`)
* `error` - Exception message and traceback (when `exec_info=True`)
* `stack_info` - Stack trace (when `stack_info=True`)
* `formatter_errors` - Errors from the formatter or providers (when an error occurs)

By default, the `message` value is truncated to 64k characters, and the `error`, 'stack_info', and `formatter_errors`
values are truncated to 128k characters.

You can override the default truncation using:
```python
import logging.config

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "json": {
      "()": "dans_log_formatter.JsonLogFormatter",
      "message_size_limit": 1024,  # Set None to unlimited
      "stack_size_limit": 1024,  # Set None to unlimited
    }
  },
  # ...
})
```

### JsonLogFormatter

Format log records as JSON using `json.dumps()`.

### TextLogFormatter

Format log records as human-readable text using `logging.Formatter` ([See the docs](https://docs.python.org/3/library/logging.html#formatter-objects)).

All attributes are available to use in the format string.

The `timestamp` attribute is formatted using the `datefmt` like in the `logging.Formatter`.

```python
import logging.config

from dans_log_formatter.providers.context import ContextProvider, inject_log_context

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "text": {
      "()": "dans_log_formatter.TextLogFormatter",
      "providers": [ContextProvider()],
      "fmt": "{timestamp} {status} | {user_id} - {message}",
      "datefmt": "%H:%M:%S",
      "style": "{"
    }
  },
  # ...
})

logger = logging.getLogger(__name__)

with inject_log_context({"user_id": 123}):
  logger.info("Hello, world!")

# STDOUT: 12:00:42 INFO | 123 - Hello, world!
```

## Extending your own formatter

You can extend the `JsonLogFormatter` to modify the default attributes, add new ones, use other log record serializer or anything else.

```python
import socket
from logging import LogRecord
import xml.etree.ElementTree as ET

from dans_log_formatter import JsonLogFormatter


class MyCustomFormatter(JsonLogFormatter):
  root_tag = "log"

  def format(self, record: LogRecord) -> str:
    # Serialize to XML instead of JSON
    return self.attributes_to_xml(self.get_attributes(record))

  def attributes_to_xml(self, attributes: dict[str, str]) -> str:
    root = ET.Element(self.root_tag)
    for key, value in attributes.items():
      element = ET.SubElement(root, key)
      element.text = value
    return ET.tostring(root, encoding="unicode")

  def format_status(self, record: LogRecord) -> int:
    return record.levelno  # Use the level number instead of the level name

  def format_location(self, record: LogRecord) -> str:
    return f"{record.module}-{record.funcName}"  # Use only the module and function name, without the line number

  def format_exception(self, record: LogRecord) -> str:
    return f"{record.exc_info[0].__name__}: {record.exc_info[1]}"  # Use only the exception name and message

  def get_attributes(self, record: LogRecord) -> dict:
    attributes = super().get_attributes(record)
    attributes["hostname"] = socket.gethostname()  # Add an extra hostname default attribute
    return attributes
```

> Note: Creating a custom `HostnameProvider` is a better way to add the hostname attribute.

### Error handling

When an error occurs in the formatter or providers, the `formatter_errors` attribute is added to the log record.

Silent errors can be added to the `formatter_errors` attribute using the `record_error()` method.

```python
from dans_log_formatter.providers.abstract import AbstractProvider


class MyProvider(AbstractProvider):
  def get_attributes(self, record: LogRecord) -> dict[str, Any]:
    self.record_error("Something went wrong")  # Add an error to the formatter_errors attribute
    return {'my_attribute': 'some value'}
```

Exception traceback context is automatically added to the recorded error or caught exceptions described in the `formatter_errors` attribute.


## Contributing

Before contributing, please read the [contributing guidelines](CONTRIBUTING.md) for guidance on how to get started.


### License

This project is licensed under the [MIT License](LICENSE).


# Happy logging!
