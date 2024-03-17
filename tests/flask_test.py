from flask import Flask

from dans_log_formatter.contrib.flask.provider import FlaskRequestProvider
from dans_log_formatter.formatter import JsonLogFormatter
from tests.utils import logger_factory, read_stream_log_line


def test_flask_integration():
    logger, stream = logger_factory(
        JsonLogFormatter(
            [
                FlaskRequestProvider(),
            ]
        )
    )

    app = Flask(__name__)

    @app.route("/resource/<int:id>/action", methods=["GET"])
    def read_root(id):  # noqa ARG001
        logger.info("hello world!")
        return "hello world!"

    client = app.test_client()

    response = client.get(
        "/resource/1/action",
        headers={
            "Referer": "http://example.com",
            "User-Agent": "some user agent",
        },
    )
    assert response.status_code == 200

    record = read_stream_log_line(stream)
    assert record["status"] == "INFO"
    assert record["message"] == "hello world!"
    assert record["resource"] == "GET /resource/1/action"
    assert record["http.method"] == "GET"
    assert record["http.url"] == "http://localhost/resource/1/action"
    assert record["http.referrer"] == "http://example.com"
    assert record["http.useragent"] == "some user agent"
    assert record["http.remote_addr"] == "127.0.0.1"
