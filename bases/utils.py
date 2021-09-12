import base64
import hashlib
import hmac

from django.conf import settings
from haversine import haversine


def check_data_key(key):
    if key == None:
        return False
    else:
        return True


def check_str_digit(numstr):
    if not check_data_key(numstr):
        return False

    if type(numstr) == str:
        if numstr.isdigit():
            return True
        try:
            float(numstr)
            return True
        except ValueError:
            return False
    elif type(numstr) == int or type(numstr) == float:
        return True
    else:
        return False


def custom_list(queryset):
    list = []
    for i in queryset:
        i = {
            'id': i.id,
            'user': i.user,
            'username': i.user.username,
            'image1': i.image1,
            'title': i.title,
            'text': i.text,
            'created_at': i.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        list.append(i)
    return list


def custom_dict(i):
    return {
        'id': i.id,
        'user': i.user,
        'username': i.user.username,
        'image1': i.image1,
        'title': i.title,
        'text': i.text,
        'created_at': i.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def paginate(self, queryset):
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


def check_distance(user_lat, user_lon, camp_lat, camp_lon):

    user_loc = (user_lat, user_lon)
    camp_loc = (float(camp_lat), float(camp_lon))

    distance = haversine(user_loc, camp_loc, unit='km')

    return round(distance, 2)


def make_signature(timestamp):
    access_key = getattr(settings, 'NAVER_ACCESS_KEY')
    secret_key = getattr(settings, 'NAVER_SECRET_KEY')
    secret_key = bytes(secret_key, 'UTF-8')

    uri = f"/sms/v2/services/{getattr(settings, 'NAVER_PROJECT_ID')}/messages"

    message = "POST" + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey
