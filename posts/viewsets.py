import sys

from django.db.models import Count, Case, When
from rest_framework import viewsets, status
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from bases.utils import check_str_digit
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer, ShareSerializer, SharePostSerializer
from posts.models import EcoCarping, Post, Share
from bases.response import APIResponse
from rest_framework.exceptions import MethodNotAllowed

mod = sys.modules[__name__]


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
        try:
            if check_str_digit(lat) and check_str_digit(lon):
                float(lat)
                float(lon)

            ret = super(EcoCarpingViewSet, self).create(request)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            if not self.get_serializer(data=request.data).is_valid():
                response.code = status.HTTP_400_BAD_REQUEST
                return response.response(error_message=str(e))
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        eco = self.get_object()
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        image1 = request.data.get('image1')
        image2 = request.data.get('image2')
        image3 = request.data.get('image3')
        image4 = request.data.get('image4')

        try:
            if image1 is None:
                eco.image1.delete()
            if image2 is None:
                eco.image2.delete()
            if image3 is None:
                eco.image3.delete()
            if image4 is None:
                eco.image4.delete()

            if check_str_digit(lat) and check_str_digit(lon):
                float(lat)
                float(lon)

            ret = super(EcoCarpingViewSet, self).update(request)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


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


class ShareViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            qs = Share.objects

            is_liked = qs.filter(like=request.user.pk)
            liked_list = []

            if is_liked.exists():
                liked_list = is_liked.values_list("id", flat=True)

            qs = qs.annotate(like_count=Count("like"),
                             is_liked=Case(
                                 When(
                                     id__in=liked_list,
                                     then=True
                                 ), default=False
            )
            )

            ret = self.get_serializer(
                qs.filter(id=self.get_object().id), many=True)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=ret.data)

        except Exception as e:
            response.success = False
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        try:
            serializer = SharePostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            latest = Share.objects.latest('id').id
            result = Share.objects.get(id=latest)
            result.is_liked = False
            serializer2 = self.get_serializer(result)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[serializer2.data])

        except Exception as e:
            if not self.get_serializer(data=request.data).is_valid():
                response.code = status.HTTP_400_BAD_REQUEST
                return response.response(error_message=str(e))
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def destroy(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(ShareViewSet, self).destroy(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))
