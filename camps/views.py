from django.db.models.expressions import Case, Exists, Value, When
from rest_framework import serializers, status
from rest_framework.viewsets import GenericViewSet

from bases.utils import check_str_digit

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.status import HTTP_200_OK

from bases.response import APIResponse
from bases.serializers import MessageSerializer
from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from camps.serializers import AutoCampMainSerializer, \
    MainPageThemeSerializer, AutoCampBookMarkSerializer, CampSiteBookMarkSerializer, CampSiteSerializer

from django.db.models import F, Count, Q


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
            return qs

    def post(self, request):
        return JsonResponse("hi", safe=False)


class AutoCampPartial(GenericAPIView):
    serializer_class = AutoCampMainSerializer

    def post(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        if not 'count' in self.request.data:
            return response.response(error_message="'count' field is required")
        count = int(self.request.data.get('count', None))

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

        if serializer.is_valid():
            try:
                autocamp_to_bookmark = AutoCamp.objects.get(
                    id=serializer.validated_data["autocamp_to_bookmark"])

                user.autocamp_bookmark.add(autocamp_to_bookmark)
                data = MessageSerializer({"message": _("차박지를 스크랩했습니다.")}).data

                response.success = True
                response.code = 200
                return response.response(data=[data])
            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'autocamp_to_bookmark' field is required.")

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

        if serializer.is_valid():
            try:
                user.autocamp_bookmark.through.objects.filter(
                    user=user, autocamp=serializer.validated_data["autocamp_to_bookmark"]).delete()
                data = MessageSerializer(
                    {"message": _("차박지 스크랩을 취소했습니다.")}).data

                response.success = True
                response.code = 200
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'autocamp_to_bookmark' field is required.")


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
        user = request.user

        sort = data.get('sort')

        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

        qs = self.filter_queryset(
            self.get_queryset())

        if qs is not None:
            bookmark_qs = qs.bookmark_qs(user.pk)
        else:
            bookmark_qs = qs

        serializer = self.get_serializer(bookmark_qs, many=True)

        if sort == "distance":
            data = sorted(serializer.data, key=lambda x: x['distance'])
        else:
            data = serializer.data

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)


class CampSiteDetailAPIView(RetrieveModelMixin, GenericAPIView):
    serializer_class = CampSiteSerializer

    def get_queryset(self):
        user = self.request.user
        return CampSite.objects.all().bookmark_qs(user.pk)

    def retrieve(self, request, pk):
        data = request.data

        response = APIResponse(success=False, code=400)

        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = status.HTTP_400_BAD_REQUEST
            return response.response(error_message=_("Invalid Lat or Lon"))

        try:
            ret = super(CampSiteDetailAPIView, self).retrieve(request)

            obj = self.get_object()
            obj.views += 1
            obj.save()

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def post(self, request, pk):
        return self.retrieve(request, pk)


class CampSiteBookMark(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Scrap CampSite"),
        operation_description=_("캠핑장을 스크랩합니다."),
        request_body=CampSiteBookMarkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("camps"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = CampSiteBookMarkSerializer(data=request.data)

        if serializer.is_valid():
            try:
                campsite_to_bookmark = CampSite.objects.get(
                    id=serializer.validated_data["campsite_to_bookmark"])
                user.campsite_bookmark.add(campsite_to_bookmark)
                data = MessageSerializer({"message": _("캠핑장을 스크랩했습니다.")}).data

                response.success = True
                response.code = 200
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'campsite_to_bookmark' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Scrap CampSite"),
        operation_description=_("캠핑장 스크랩을 취소합니다."),
        request_body=CampSiteBookMarkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("camps"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = CampSiteBookMarkSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.campsite_bookmark.through.objects.filter(
                    user=user, campsite=serializer.validated_data[
                        "campsite_to_bookmark"]).delete()
                data = MessageSerializer(
                    {"message": _("캠핑장 스크랩을 취소했습니다.")}).data

                response.success = True
                response.code = 200
                return response.response(data=[data])
            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'campsite_to_bookmark' field is required.")
