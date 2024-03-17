import django
from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import path

from dans_log_formatter.contrib.django.provider import DjangoRequestProvider
from dans_log_formatter.formatter import JsonLogFormatter
from tests.utils import logger_factory, read_stream_log_line

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,  # Point ROOT_URLCONF to this module
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    SECRET_KEY="NOTSOSECRET",
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.auth",
    ],
    MIDDLEWARE=[
        "dans_log_formatter.contrib.django.middleware.LogContextMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    ALLOWED_HOSTS=["testserver"],
)

django.setup()

logger, stream = logger_factory(JsonLogFormatter([DjangoRequestProvider()]))


def example_view(request, param):  # noqa ARG001
    logger.info("Test log message from view")
    return HttpResponse("Test Response")


urlpatterns = [
    path("api/resource/<int:param>/action", example_view, name="test_logging"),
]


def test_django_integration():
    client = Client()

    response = client.get(
        "/api/resource/1/action",
        headers={
            "referer": "http://example.com",
            "user-agent": "some user agent",
            "x-forwarded-for": "127.0.0.2",
        },
    )
    assert response.status_code == 200

    record = read_stream_log_line(stream)
    assert record["status"] == "INFO"
    assert record["message"] == "Test log message from view"
    assert record["resource"] == "GET api/resource/<int:param>/action"
    assert record["http.method"] == "GET"
    assert record["http.url"] == "http://testserver/api/resource/1/action"
    assert record["http.remote_addr"] == "127.0.0.2"
    assert record["http.referrer"] == "http://example.com"
    assert record["http.useragent"] == "some user agent"
    assert record["user.id"] == 0
    assert record["user.name"] == "AnonymousUser"
    assert record["user.email"] is None
