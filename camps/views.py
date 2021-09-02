from bases.utils import check_data_key, check_str_digit, custom_theme_dict, check_distance

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.status import HTTP_200_OK

from bases.response import APIResponse
from bases.serializers import MessageSerializer
from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from camps.serializers import AutoCampMainSerializer, \
    MainPageThemeSerializer, AutoCampBookMarkSerializer


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
        response = APIResponse(success=False, code=400)
        count = self.request.data.get('count', None)
        if not count:
            return response.response(error_message="must have 'count' field in request body")

        int(count)
        if count == 0:
            qs = AutoCamp.objects.all().order_by('-created_at')
        elif count > 0:
            qs = AutoCamp.objects.all().order_by('-created_at')[:count]
        else:
            return response.response(error_message="INVALID_COUNT")

        response.success = True
        response.code = 200
        return response.response(data=AutoCampMainSerializer(qs, many=True).data)


class AutoCampBookMark(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Scrap AutoCamp"),
        operation_description=_("차박지를 스크랩합니다."),
        request_body=AutoCampBookMarkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("camps"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = AutoCampBookMarkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            autocamp_to_bookmark = AutoCamp.objects.get(
                id=serializer.validated_data["autocamp_to_bookmark"])

            if not autocamp_to_bookmark:
                return response.response(error_message="존재하지 않는 차박지 id 입니다.")

            user.autocamp_bookmark.add(autocamp_to_bookmark)
            data = MessageSerializer({"message": _("차박지를 스크랩했습니다.")}).data
            response.success = True
            response.code = 200
            return response.response(data=[data])

    @swagger_auto_schema(
        operation_id=_("Delete Scrap AutoCamp"),
        operation_description=_("차박지 스크랩을 취소합니다."),
        request_body=AutoCampBookMarkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("camps"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = AutoCampBookMarkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.autocamp_bookmark.through.objects.filter(
                user=user, autocamp=serializer.validated_data["autocamp_to_bookmark"]).delete()
            data = MessageSerializer({"message": _("차박지 스크랩을 취소했습니다.")}).data
            response.success = True
            response.code = 200
            return response.response(data=[data])


class GetMainPageThemeTravel(ListModelMixin, GenericAPIView):
    """
    Data :
    theme : 테마
    sort : 인기순, 거리순, 최신순
    select : 여행시기, 레포츠, 자연, 체험프로그램
    """

    serializer_class = MainPageThemeSerializer

    # ordering_fields = ['distance']

    def get_queryset(self):
        data = self.request.data
        theme = data.get('theme')
        sort = data.get('sort')
        select = data.get('select')

        if sort == None:
            sort = "recent"
        if theme == "brazier":
            qs = CampSite.objects.theme_brazier(sort)
        elif theme == "animal":
            qs = CampSite.objects.theme_animal(sort)
        elif theme == "season":
            qs = CampSite.objects.theme_season(select, sort)
        elif theme == "program":
            qs = CampSite.objects.theme_program(sort)
        elif theme == "event":
            qs = CampSite.objects.theme_event(sort)
        elif theme == "leports":
            qs = CampSite.objects.theme_leports(select, sort)
        elif theme == "nature":
            qs = CampSite.objects.theme_nature(select, sort)
        elif theme == "others":
            qs = CampSite.objects.theme_other_type(select, sort)
        else:
            qs = CampSite.objects.all()

        return qs

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        data = request.data

        sort = data.get('sort')

        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response()

        qs = self.filter_queryset(self.get_queryset())

        list = []

        for i in qs:
            if i.lat == None or i.lon == None:
                continue

            distance = check_distance(
                float(user_lat), float(user_lon), float(i.lat), float(i.lon))
            i = custom_theme_dict(i)

            i['distance'] = distance
            list.append(i)

        if sort == "distance":
            list.sort(key=(lambda x: x['distance']))

        serializer = MainPageThemeSerializer(data=list, many=True)
        if serializer.is_valid():
            response.code = 200
            response.success = True
            return response.response(data=serializer.data)
        else:
            return response.response(data=serializer.errors)

    def post(self, request):
        return self.list(request)
