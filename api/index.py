import os
import sys

from serverless_wsgi import handle_request

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app  # noqa: E402


def handler(event, context):
    return handle_request(app, event, context)