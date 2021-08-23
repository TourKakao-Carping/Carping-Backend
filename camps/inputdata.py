import requests

from urllib.parse import urlencode, quote_plus

from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
# 전체 num : 2649

# 26개
column = ['name', 'lat', 'lon' 'animal', 'event', 'program', 'website', 'phone', 'address', 'brazier', 'oper_day', 'off_day_start',
          'off_day_end', 'faculty', 'permission_date', 'reservation', 'toilet', 'shower', 'type', 'sub_facility', 'season', 'image', 'area', 'themeenv', 'created_at', 'updated_at']

# 27개
json_column = ['facltNm', 'mapY', 'mapX', 'animalCmgCl', 'clturEvent', 'exprnProgrm', 'homepage', 'tel', 'addr1',
               'brazierCl', 'operDeCl', 'hvofBgnde', 'hvofEnddle', 'facltDivNm', 'prmisnDe', 'resveCl', 'toiletCo', 'swrmCo', 'induty', 'sbrsCl', 'sbrsEtc', 'operPdCl', 'firstImageUrl', 'doNm', 'themaEnvrnCl', 'createdtime', 'modifiedtime']


class InputDataAPIView(APIView):
    permission_classes = [AllowAny, ]

    @transaction.atomic
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

    def post(self, request):
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

            created_at = self.change_time_format(input_data[25])
            updated_at = self.change_time_format(input_data[26])

            CampSite.objects.create(
                name=input_data[0], lat=input_data[1], lon=input_data[2], animal=input_data[3],
                event=input_data[4], program=input_data[5],
                website=input_data[6], phone=input_data[7], address=input_data[8],
                brazier=input_data[9], oper_day=input_data[10], off_start=input_data[11],
                off_end=input_data[12], faculty=input_data[13], permission_date=input_data[14],
                reservation=input_data[15], toilet=input_data[16], shower=input_data[17],
                type=input_data[18], sub_facility=sub_facility, season=input_data[21],
                image=input_data[22], area=input_data[23], themenv=input_data[24], created_at=created_at, updated_at=updated_at)
            i += 1
        return JsonResponse({"input_items": i})


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
