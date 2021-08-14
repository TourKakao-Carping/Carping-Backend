import json
import requests
from rest_framework import status
from allauth.account.models import EmailAddress
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from accounts.serializers import CustomTokenRefreshSerializer

from rest_framework_simplejwt.views import TokenRefreshView


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
