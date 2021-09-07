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

    def is_changed_image(self):
        """
        image1, 3이 있을 경우
        기존에 있으면 삭제

        """
        data = self.request.data

        is_deleted_1 = data.get('is_deleted_1', False)
        is_deleted_2 = data.get('is_deleted_2', False)
        is_deleted_3 = data.get('is_deleted_3', False)
        is_deleted_4 = data.get('is_deleted_4', False)

        return [is_deleted_1, is_deleted_2, is_deleted_3, is_deleted_4]

    def get_image_field(self, obj, i, key):
        s3 = S3Client()

        if i == 1:
            if not obj.image1 == "" and not obj.image1 == None:
                s3.delete_file(str(obj.image1))
            # obj.image1 = key
        elif i == 2:
            if not obj.image2 == "" and not obj.image2 == None:
                s3.delete_file(str(obj.image2))
        elif i == 3:
            if not obj.image3 == "" and not obj.image3 == None:
                s3.delete_file(str(obj.image3))
        else:
            if not obj.image4 == "" and not obj.image4 == None:
                s3.delete_file(str(obj.image4))

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(False, 400)

        files = request.FILES
        print(files)

        obj = self.get_object()

        for i in range(1, 5):
            try:
                key = files[f"image{i}"]

                self.get_image_field(obj, i, key)

            except MultiValueDictKeyError:
                pass

        obj.save()

        return super().partial_update(request, *args, **kwargs)
        # except Exception as e:
        #     return response.response(error_message=str(e))
