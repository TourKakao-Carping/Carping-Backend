from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.status import HTTP_200_OK

from bases.response import APIResponse
from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from django.http import JsonResponse

from camps.serializers import AutoCampSerializer, AutoCampMainSerializer, MainPageThemeSerializer


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


class AutoCampPartial(GenericAPIView):
    serializer_class = AutoCampMainSerializer

    def post(self, request, *args, **kwargs):
        count = int(self.request.data.get('count', None))
        if count == 0:
            qs = AutoCamp.objects.all().order_by('-created_at')
        elif count > 0:
            qs = AutoCamp.objects.all().order_by('-created_at')[:count]

        response = APIResponse(False, "")
        response.success = True
        return response.response(status=HTTP_200_OK, data=AutoCampMainSerializer(qs, many=True).data)


class GetMainPageThemeTravel(ListModelMixin, GenericAPIView):
    """
    Data :
    theme : 테마
    sort : 인기순, 거리순, 최신순
    select : 여행시기, 레포츠, 자연, 체험프로그램
    """

    serializer_class = MainPageThemeSerializer

    def get_queryset(self):
        data = self.request.data
        theme = data.get('theme')
        sort = data.get('sort')
        select = data.get('select')

        if theme == "bazier":
            return CampSite.objects.theme_brazier(sort)
        elif theme == "animal":
            return CampSite.objects.theme_animal(sort)
        elif theme == "season":
            if select == None:
                select = "봄"
            return CampSite.objects.theme_season(select, sort)
        elif theme == "program":
            return CampSite.objects.theme_program(sort)
        elif theme == "event":
            return CampSite.objects.theme_event(sort)
        else:
            return CampSite.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()

    # 인기순, 거리순, 최신순
    # 0, 1, 2
    # def post(self, request):
        # self.list/
