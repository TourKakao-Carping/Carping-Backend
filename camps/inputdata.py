import requests

from urllib.parse import urlencode, quote_plus

from bases.utils import reverse_geocode
from camps.models import AutoCamp, CampSite, TourSite

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction

import xml.etree.ElementTree as ET
import pymysql
# 전체 num : 2649

# 26개
column = ['name', 'lat', 'lon' 'animal', 'event', 'program', 'website', 'phone', 'address', 'brazier', 'oper_day', 'off_day_start',
          'off_day_end', 'faculty', 'permission_date', 'reservation', 'toilet', 'shower', 'type', 'sub_facility', 'season', 'image', 'area', 'themeenv', 'rental_item', 'main_general', 'main_autocamp', 'main_glamcamp', 'main_caravan', 'main_personal_caravan', 'created_at', 'updated_at']

# 30개
json_column = ['facltNm', 'mapY', 'mapX', 'animalCmgCl', 'clturEvent', 'exprnProgrm', 'homepage', 'tel', 'addr1',
               'brazierCl', 'operDeCl', 'hvofBgnde', 'hvofEnddle', 'facltDivNm', 'prmisnDe', 'resveCl', 'toiletCo', 'swrmCo', 'induty', 'sbrsCl', 'sbrsEtc', 'operPdCl', 'firstImageUrl', 'doNm', 'themaEnvrnCl',  'eqpmnLendCl', 'gnrlSiteCo', 'autoSiteCo', 'glampSiteCo', 'caravSiteCo', 'indvdlCaravSiteCo', 'createdtime', 'modifiedtime']

column_tour = ['type', 'image', 'lat', 'lon', 'name']
json_column_tour = ['contenttypeid', 'firstimage', 'mapy', 'mapx', 'title']

class InputDataAPIView(APIView):
    permission_classes = [AllowAny, ]

    def get_data(self):
        API_KEY = getattr(settings, "CAMP_API_KEY")
        url = "http://api.visitkorea.or.kr/openapi/service/rest/GoCamping/basedList"
        queryParams = '?' + urlencode({quote_plus(
            'numOfRows'): '2649',
            quote_plus('MobileOS'): 'AND',
            quote_plus('MobileApp'): 'Carping',
            quote_plus('_type'): 'json',
            quote_plus('ServiceKey'): ""}) + API_KEY

        req = requests.get(url + queryParams)
        req_json = req.json()
        response = req_json['response']
        body = response['body']
        items = body['items']
        item = items['item']
        return item

    def check_sub_facility(self, sub_fac1, sub_fac2):
        if sub_fac1 == None and sub_fac2 == None:
            sub_facility = None
        elif not sub_fac1 == None and sub_fac2 == None:
            sub_facility = sub_fac1
        elif sub_fac1 == None and not sub_fac2 == None:
            sub_facility = sub_fac2
        else:
            sub_facility = sub_fac1 + ',' + sub_fac2
        return sub_facility

    def change_time_format(self, time):
        time = time.strip()
        return time

    @transaction.atomic
    def post(self, request):
        CampSite.objects.all().delete()

        items = self.get_data()
        i = 0
        for item in items:
            input_data = []
            # num : 0 ~21
            for num in range(len(json_column)):
                input_data.append(item.get(json_column[num]))
                # 17, 18 (sbrsCl, sbrsEtc)
            sub_facility = self.check_sub_facility(
                input_data[19], input_data[20])

            created_at = self.change_time_format(input_data[31])
            updated_at = self.change_time_format(input_data[32])

            CampSite.objects.create(
                name=input_data[0], lat=input_data[1], lon=input_data[2], animal=input_data[3],
                event=input_data[4], program=input_data[5],
                website=input_data[6], phone=input_data[7], address=input_data[8],
                brazier=input_data[9], oper_day=input_data[10], off_start=input_data[11],
                off_end=input_data[12], faculty=input_data[13], permission_date=input_data[14],
                reservation=input_data[15], toilet=input_data[16], shower=input_data[17],
                type=input_data[18], sub_facility=sub_facility, season=input_data[21],
                image=input_data[22], area=input_data[23], themenv=input_data[24], rental_item=input_data[25],
                main_general=input_data[26], main_autocamp=input_data[
                    27], main_glamcamp=input_data[28], main_caravan=input_data[29],
                main_personal_caravan=input_data[30], created_at=created_at, updated_at=updated_at)
            i += 1

        return JsonResponse({"input_items": i})


class InputTourAPIView(APIView):
    permission_classes = [AllowAny, ]

    def get_data(self):
        API_KEY = getattr(settings, "TOUR_API_KEY")
        url = "http://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList"
        queryParams = '?' + urlencode({quote_plus(
            'numOfRows'): '27118',
            quote_plus('MobileOS'): 'AND',
            quote_plus('MobileApp'): 'Carping',
            quote_plus('_type'): 'json',
            quote_plus('ServiceKey'): ""}) + API_KEY

        req = requests.get(url + queryParams)
        req_json = req.json()
        response = req_json['response']
        body = response['body']
        items = body['items']
        item = items['item']
        return item

    @transaction.atomic
    def post(self, request):
        TourSite.objects.all().delete()

        items = self.get_data()
        i = 0
        for item in items:
            input_data = []
            for num in range(len(json_column_tour)):
                input_data.append(item.get(json_column_tour[num]))

            if input_data[0] != 32:
                TourSite.objects.update_or_create(
                    type=input_data[0], image=input_data[1], lat=input_data[2],
                    lon=input_data[3], name=input_data[4])
                i += 1

        return JsonResponse({"input_items": i})


class InputTourAddressAPIView(APIView):
    permission_classes = [AllowAny, ]

    @transaction.atomic
    def post(self, request):
        items = TourSite.objects.all()
        i = 0

        for item in items:
            address = reverse_geocode(item.lon, item.lat)
            TourSite.objects.filter(lat=item.lat, lon=item.lon, name=item.name).update(address=address)
            i += 1

        return JsonResponse({"input_items": i})


class InputTagAPIView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        for i in CampSite.objects.all():
            if i.event:
                tags = i.event.split(',')
                for tag in tags:
                    i.tags.add(tag)
            if i.program:
                tags = i.program.split(',')
                for tag in tags:
                    i.tags.add(tag)
            if i.themenv:
                tags = i.themenv.split(',')
                for tag in tags:
                    i.tags.add(tag)
        return JsonResponse({"success": True})


class GetPopularSearchList(APIView):

    def check_popular_views(self, qs1, qs2):
        qs_sum = qs1 | qs2
        qs = qs_sum.order_by('-views')
        return qs

    def get_queryset(self):
        data = self.request.data
        count = data.get('count')

        count = int(count)

        if count == 0:
            count = None
            qs1 = CampSite.objects.autocamp_type(count)
            qs2 = AutoCamp.objects.ordering_views(count)

            qs = self.check_popular_views(qs1, qs2)
            return qs
        else:
            qs1 = CampSite.objects.autocamp_type(count)
            qs2 = AutoCamp.objects.ordering_views(count)

            qs = self.check_popular_views(qs1, qs2)
            print(qs[:3])
            return qs

    def post(self, request):
        print(self.get_queryset())
        return JsonResponse("hi", safe=False)
