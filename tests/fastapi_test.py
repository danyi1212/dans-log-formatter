from fastapi import FastAPI
from fastapi.testclient import TestClient

from contrib.fastapi.middleware import LogContextMiddleware
from contrib.fastapi.provider import FastAPIRequestProvider
from formatter import JsonLogFormatter
from utils import logger_factory, read_stream_log_line


def test_fastapi_integration():
    logger, stream = logger_factory(
        JsonLogFormatter(
            [
                FastAPIRequestProvider(),
            ]
        )
    )

    app = FastAPI()
    app.add_middleware(LogContextMiddleware)

    @app.get("/resource/{id}/action")
    def read_root():
        logger.info("hello world!")
        return "hello world!"

    client = TestClient(app)

    response = client.get(
        "/resource/1/action",
        headers={
            "referer": "http://example.com",
            "user-agent": "some user agent",
            "x-forwarded-for": "127.0.0.2",
        },
    )
    assert response.status_code == 200

    record = read_stream_log_line(stream)
    assert record["status"] == "INFO"
    assert record["message"] == "hello world!"
    assert record["resource"] == "GET /resource/{id}/action"
    assert record["http.method"] == "GET"
    assert record["http.url"] == "http://testserver/resource/1/action"
    assert record["http.referrer"] == "http://example.com"
    assert record["http.useragent"] == "some user agent"
    assert record["http.remote_addr"] == "127.0.0.2"
