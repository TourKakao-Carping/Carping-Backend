import datetime
import os

from django.db import models
from django.utils import timezone


def upload_user_directory(instance, filename):
    email = instance.user.email
    now = timezone.now()

    # year/month/day/user_pk/20210707_s94203_123128.png
    return 'img/{year}/{month}/{day}/user_{user_id}/{now}_{name}_{microsecond}_{extension}'.format(year=now.year, month=now.month, day=now.day, user_id=instance.user.id, now=now.strftime("%Y%m%d"), name=email.split('@')[0],
                                                                                                   microsecond=now.microsecond, extension=os.path.splitext(filename)[1])
