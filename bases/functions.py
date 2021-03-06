from bases.s3 import S3Client
import datetime
import os

from django.db import models
from django.utils import timezone


# class UploadTo:
#     # s3 = S3Client()
#
#     def __init__(self, name):
#         self.name = name
#
#     def __call__(self, instance, filename):
#         email = instance.user.email
#         now = timezone.now()
#
#         # if self.name == "image1":
#         #     if not instance.image1 == "" and not instance.image1 == None:
#         #         self.s3.delete_file(str(instance.image1))
#
#         # elif self.name == "image2":
#         #     if not instance.image2 == "" and not instance.image2 == None:
#         #         self.s3.delete_file(str(instance.image2))
#
#         # elif self.name == "image3":
#         #     if not instance.image3 == "" and not instance.image3 == None:
#         #         self.s3.delete_file(str(instance.image3))
#
#         # else:
#         #     if not instance.image4 == "" and not instance.image4 == None:
#         #         self.s3.delete_file(str(instance.image4))
#
#         return 'img/{year}/{month}/{day}/user_{user_id}/{now}_{name}_{microsecond}_{extension}'.format(year=now.year, month=now.month, day=now.day, user_id=instance.user.id, now=now.strftime("%Y%m%d"), name=email.split('@')[0],
#                                                                                                        microsecond=now.microsecond, extension=os.path.splitext(filename)[1])
#
#     def deconstruct(self):
#         return ('camps.models.UploadTo', [self.fieldname], {})


def upload_user_directory(instance, filename):
    email = instance.user.email
    now = timezone.now()

    # year/month/day/user_pk/20210707_s94203_123128.png
    return 'img/{year}/{month}/{day}/user_{user_id}/{now}_{name}_{microsecond}_{extension}'.format(year=now.year,
                                                                                                   month=now.month,
                                                                                                   day=now.day,
                                                                                                   user_id=instance.user.id,
                                                                                                   now=now.strftime(
                                                                                                       "%Y%m%d"), name=
                                                                                                   email.split('@')[0],
                                                                                                   microsecond=now.microsecond,
                                                                                                   extension=
                                                                                                   os.path.splitext(
                                                                                                       filename)[1])


# def upload_user_directory_userpost(instance, filename):
#     post_info = instance.userpostinfo_set.get()
#     email = post_info.author.email
#
#     now = timezone.now()
#
# # year/month/day/user_pk/20210707_s94203_123128.png return 'img/{year}/{month}/{day}/user_{user_id}/{now}_{name}_{
# microsecond}_{extension}'.format(year=now.year, month=now.month, day=now.day, user_id=post_info.author.id,
# now=now.strftime("%Y%m%d"), name=email.split('@')[0], microsecond=now.microsecond, extension=os.path.splitext(
# filename)[1])


def upload_user_directory_userpost(instance, filename):
    title = instance.title
    pk = instance.id
    now = timezone.now()

    # year/month/day/post_pk/20210707_s94203_123128.png
    return 'img/{year}/{month}/{day}/posts_{pk}/{now}_{title}_{microsecond}_{extension}'.format(year=now.year,
                                                                                                month=now.month,
                                                                                                day=now.day, pk=pk,
                                                                                                now=now.strftime(
                                                                                                    "%Y%m%d"),
                                                                                                title=title[:10],
                                                                                                microsecond=now.microsecond,
                                                                                                extension=
                                                                                                os.path.splitext(
                                                                                                    filename)[1])
