import copy

from django.utils.datastructures import MultiValueDictKeyError

from botocore.exceptions import ClientError
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, exceptions

from bases.s3 import S3Client
from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp, CampSite
from camps.serializers import AutoCampSerializer, CampSiteSerializer

from django.utils.translation import ugettext_lazy as _


class AutoCampViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = AutoCampSerializer
    queryset = AutoCamp.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(AutoCampViewSet, self).retrieve(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        try:
            if check_str_digit(lat) and check_str_digit(lon):
                float(lat)
                float(lon)
            ret = super(AutoCampViewSet, self).create(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])

        except Exception as e:
            if not self.get_serializer(data=request.data).is_valid():
                response.code = status.HTTP_400_BAD_REQUEST
                return response.response(error_message=str(e))
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def get_image_field(self, obj, i):
        s3 = S3Client()

        if i == 1:
            if not obj.image1 == "" and not obj.image1 == None:
                s3.delete_file(str(obj.image1))
                obj.image1 = None
        elif i == 2:
            if not obj.image2 == "" and not obj.image2 == None:
                s3.delete_file(str(obj.image2))
                obj.image2 = None

        elif i == 3:
            if not obj.image3 == "" and not obj.image3 == None:
                s3.delete_file(str(obj.image3))
                obj.image3 = None

        else:
            if not obj.image4 == "" and not obj.image4 == None:
                s3.delete_file(str(obj.image4))
                obj.image4 = None

    def swap_image(arr, i, j):
        arr[i], arr[j] = arr[j], arr[i]

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(False, 400)
        request.data._mutable = True

        image1 = request.data.get('image1')
        image2 = request.data.get('image2')
        image3 = request.data.get('image3')
        image4 = request.data.get('image4')

        if image1 == "":
            request.data.pop('image1')

        if image2 == "":
            request.data.pop('image2')

        if image3 == "":
            request.data.pop('image3')

        if image4 == "":
            request.data.pop('image4')

        # is_null에 있는 숫자에 해당되는 image 필드에 기존 이미지 삭제처리
        try:
            is_null = request.data.pop('is_null')
        except KeyError:
            is_null = []

        if len(is_null) == 0:
            pass
        else:
            for i in range(0, len(is_null)):
                if check_str_digit(is_null[i]):
                    is_null[i] = int(is_null[i])
                else:
                    pass

        obj = self.get_object()

        # 사용자가 원하는 Delete
        for i in range(1, 5):
            try:
                if i in is_null:
                    self.get_image_field(obj, i)

            except MultiValueDictKeyError:
                pass

        # 이미지 Overwrite 시 삭제할 이미지 설정
        obj.save()

        ret = super().partial_update(request, *args, **kwargs)
        sort_obj = self.get_object()

        arr = []

        arr.append(sort_obj.image1)
        arr.append(sort_obj.image2)
        arr.append(sort_obj.image3)
        arr.append(sort_obj.image4)

        # j가 공백이고 j + 1에 이미지가 있을 경우
        for i in reversed(range(len(arr))):  # 3, 2, 1, 0
            for j in range(i):  # 2, 1, 0
                if arr[j] == "" and not arr[j + 1] == "":
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

        sort_obj.image1 = arr[0]
        sort_obj.image2 = arr[1]
        sort_obj.image3 = arr[2]
        sort_obj.image4 = arr[3]

        sort_obj.save()

        change_obj = self.get_serializer(sort_obj)

        response.success = True
        response.code = 200
        return response.response(data=[change_obj.data])

    def destroy(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(AutoCampViewSet, self).destroy(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))
