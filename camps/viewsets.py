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

    # def update(self, request, *args, **kwargs):
    #     print("1")
    #     response = APIResponse(success=False, code=400)
    #     auto = self.get_object()
    #     # print(auto)
    #     lat = request.data.get('latitude')
    #     lon = request.data.get('longitude')
    #     image1 = request.data.get('image1')
    #     image2 = request.data.get('image2')
    #     image3 = request.data.get('image3')
    #     image4 = request.data.get('image4')

    #     try:
    #         if image1 is None:
    #             auto.image1.delete()
    #         if image2 is None:
    #             auto.image2.delete()
    #         if image3 is None:
    #             auto.image3.delete()
    #         if image4 is None:
    #             auto.image4.delete()

    #         if check_str_digit(lat) and check_str_digit(lon):
    #             float(lat)
    #             float(lon)

    #         ret = super(AutoCampViewSet, self).update(request)

    #         response.success = True
    #         response.code = 200
    #         return response.response(data=[ret.data])

    #     except Exception as e:
    #         response.code = status.HTTP_404_NOT_FOUND
    #         return response.response(error_message=str(e))

    def check_error(self):
        """
        is_null에 들어가 있지만
        해당 이미지 필드에 blank가 아닌 이미지 값이 들어올 때 에러 발생
        """
        return True

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
        is_null = request.data.pop('is_null')

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

        response.success = True
        response.code = 200
        return response.response(data=ret.data)
