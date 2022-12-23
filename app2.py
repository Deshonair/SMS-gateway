from fastapi import FastAPI, Form, Depends
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.middleware.wsgi import WSGIMiddleware
from django.core.wsgi import get_wsgi_application
import os
from importlib.util import find_spec
from fastapi.staticfiles import StaticFiles
from django.conf import settings


# Export Django settings env variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coreapp.settings')

# Get Django WSGI app
django_app = get_wsgi_application()

# Import a model
# And always import your models after you export settings
# and you get Django WSGI app
from connectors.models import Connector
from notifications.models import Message
from notifications.models import MessageDispatch

# Create FasatAPI instance
app = FastAPI()


# Serve Django static files
app.mount('/static',
          StaticFiles(
              directory=os.path.normpath(
                  os.path.join(find_spec('django.contrib.admin').origin, '..', 'static')
              )
          ),
          name='static',
          )


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


@form_body
class Notification(BaseModel):
    subject: str
    recipient: str
    channel: str
    request_id: str
    domain: str
    text: str


# Define a FastAPI route
@app.get('/v1/connectors/{connector_id}', tags=['connectors'])
def get_connectors(connector_id: int):
    return {
        'total_accounts': Connector.objects.count(),
        'is_debug': settings.DEBUG
    }


@app.get('/v1/connectors', tags=['connectors'])
def get_connectors():
    return {
        'total_accounts': Connector.objects.count(),
        'is_debug': settings.DEBUG
    }


@app.post('/v1/connectors', tags=['connectors'])
def get_connectors():
    return {
        'total_accounts': Connector.objects.count(),
        'is_debug': "create"
    }


# Define a FastAPI route
@app.get('/notifications/', tags=['notification'])
def get_notification():
    message_dispatch = MessageDispatch.objects.filter()
    return {
        'total_accounts': MessageDispatch.objects.count(),
        'is_debug': settings.DEBUG
    }


@app.get('/notifications/{notification_id}', tags=['notification'])
def get_notification_by_id(notification_id: int):
    message_dispatch = MessageDispatch.objects.filter(message_id=notification_id)
    return {
        'total_accounts': message_dispatch,
        'is_debug': settings.DEBUG
    }


@app.post('/notifications', tags=['notification'], description="Create a new notification")
def create_notification(notification: Notification = Depends(Notification)):

    return {
        'total_accounts': "",
        'is_debug': settings.DEBUG
    }


# Mount Django app
app.mount('/', WSGIMiddleware(django_app))
