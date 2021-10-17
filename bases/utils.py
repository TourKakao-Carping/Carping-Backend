import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta

import requests
from django.conf import settings
from geopy import units
from haversine import haversine

URL = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json'


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


def modify_created_time(data):
    time = datetime.now() - data.created_at

    if time < timedelta(minutes=1):
        return '방금 전'
    elif time < timedelta(hours=1):
        return str(int(time.seconds / 60)) + '분 전'
    elif time < timedelta(days=1):
        return str(int(time.seconds / 3600)) + '시간 전'
    elif time < timedelta(days=30):
        time = datetime.now().date() - data.created_at.date()
        return str(time.days) + '일 전'
    else:
        return data.created_at.strftime("%Y년 %m월 %d일")


def json_request(url='', encoding='utf-8', success=None):
    headers = {"Authorization": "KakaoAK " + getattr(settings, 'KAKAO_REST_API_KEY')}
    resp = requests.get(url, headers=headers)

    return resp.text


def reverse_geocode(longitude, latitude):
    url = '%s?x=%s&y=%s' % (URL, longitude, latitude)
    # json request
    try:
        json_req = json_request(url=url)
        json_data = json.loads(json_req)
        json_doc = json_data.get('documents')[0]
        json_name = json_doc.get('address_name')
    except:
        json_name = 'NaN'

    return json_name


def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return (float(latitude) - rough_distance,
            float(latitude) + rough_distance,
            float(longitude) - rough_distance,
            float(longitude) + rough_distance)
