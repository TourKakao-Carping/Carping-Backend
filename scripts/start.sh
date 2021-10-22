#!/bin/bash

export DJANGO_SETTINGS_MODULE=carping.settings.production
gunicorn carping.wsgi:application --bind 0.0.0.0:8000