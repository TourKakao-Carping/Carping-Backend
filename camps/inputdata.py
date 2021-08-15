import requests

from urllib.parse import urlencode, quote_plus

from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings

# 전체 num : 2649

# 21개
column = ['name', 'lat', 'lon' 'animal', 'website', 'phone', 'address', 'brazier', 'oper_day', 'off_day_start',
          'off_day_end', 'faculty', 'permission_date', 'reservation', 'toilet', 'shower', 'type', 'sub_facility', 'season', 'image', 'area']

# 22개
json_column = ['facltNm', 'mapX', 'mapY', 'animalCmgCl', 'homepage', 'tel', 'addr1',
               'brazierCl', 'operDeCl', 'hvofBgnde', 'hvofEnddle', 'facltDivNm', 'prmisnDe', 'resveCl', 'toiletCo', 'swrmCo', 'induty', 'sbrsCl', 'sbrsEtc', 'operPdCl', 'firstImageUrl', 'doNm']


class InputDataAPIView(APIView):
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
                input_data[17], input_data[18])
            CampSite.objects.create(
                name=input_data[0], lat=input_data[1], lon=input_data[2], animal=input_data[3],
                website=input_data[4], phone=input_data[5], address=input_data[6],
                brazier=input_data[7], oper_day=input_data[8], off_start=input_data[9],
                off_end=input_data[10], faculty=input_data[11], permission_date=input_data[12],
                reservation=input_data[13], toilet=input_data[14], shower=input_data[15],
                type=input_data[16], sub_facility=sub_facility, season=input_data[19],
                image=input_data[20], area=input_data[21])
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
