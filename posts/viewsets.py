from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from bases.utils import check_str_digit
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer
from posts.models import EcoCarping, Post
from bases.response import APIResponse
from rest_framework.exceptions import MethodNotAllowed


# 4. 실시간 에코리뷰 api - 최근 3개 (사진, 제목, 내용, 시간, 리뷰날짜, pk, 오늘에코리뷰 인증 수 )
class EcoCarpingViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(EcoCarpingViewSet, self).retrieve(request)
            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])
        except Exception as e:
            response.success = False
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(EcoCarpingViewSet, self).create(request)
        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=[ret.data])

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(EcoCarpingViewSet, self).partial_update(request)
        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=[ret.data])


class AutoCampPostForWeekendViewSet(viewsets.ModelViewSet):
    """
    이번주말 이런차박지 어때요 상세페이지 가져오기 API
    """
    serializer_class = AutoCampPostSerializer
    queryset = Post.objects.all().order_by('-created_at')

    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).retrieve(request)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))
