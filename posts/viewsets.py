import sys

from rest_framework.exceptions import MethodNotAllowed
from bases.response import APIResponse
from posts.models import EcoCarping, Post, Share, Region
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer, ShareSerializer, SharePostSerializer
from bases.utils import check_str_digit
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework import viewsets, status
from django.db.models import Count, Case, When
from bases.s3 import S3Client

from django.utils.datastructures import MultiValueDictKeyError


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

    # def update(self, request, *args, **kwargs):
    #     response = APIResponse(success=False, code=400)
    #     eco = self.get_object()
    #     lat = request.data.get('latitude')
    #     lon = request.data.get('longitude')
    #     image1 = request.data.get('image1')
    #     image2 = request.data.get('image2')
    #     image3 = request.data.get('image3')
    #     image4 = request.data.get('image4')

    #     try:
    #         if image1 is None:
    #             eco.image1.delete()
    #         if image2 is None:
    #             eco.image2.delete()
    #         if image3 is None:
    #             eco.image3.delete()
    #         if image4 is None:
    #             eco.image4.delete()

    #         if check_str_digit(lat) and check_str_digit(lon):
    #             float(lat)
    #             float(lon)

    #         ret = super(EcoCarpingViewSet, self).update(request)

    #         response.success = True
    #         response.code = HTTP_200_OK
    #         return response.response(data=[ret.data])

    #     except Exception as e:
    #         response.code = HTTP_404_NOT_FOUND
    #         return response.response(error_message=str(e))

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

        # is_null??? ?????? ????????? ???????????? image ????????? ?????? ????????? ????????????
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

        # ???????????? ????????? Delete
        for i in range(1, 5):
            try:
                if i in is_null:
                    self.get_image_field(obj, i)

            except MultiValueDictKeyError:
                pass

        # ????????? Overwrite ??? ????????? ????????? ??????
        obj.save()

        ret = super().partial_update(request, *args, **kwargs)

        sort_obj = self.get_object()

        arr = []

        arr.append(sort_obj.image1)
        arr.append(sort_obj.image2)
        arr.append(sort_obj.image3)
        arr.append(sort_obj.image4)

        # j??? ???????????? j + 1??? ???????????? ?????? ??????
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
            ret = super(EcoCarpingViewSet, self).destroy(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


class AutoCampPostForWeekendViewSet(viewsets.ModelViewSet):
    """
    ???????????? ??????????????? ????????? ??????????????? ???????????? API
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
            ret = super(ShareViewSet, self).retrieve(request)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])

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
        region = request.data.get('region')

        if image1 == "":
            request.data.pop('image1')

        if image2 == "":
            request.data.pop('image2')

        if image3 == "":
            request.data.pop('image3')

        if image4 == "":
            request.data.pop('image4')

        # is_null??? ?????? ????????? ???????????? image ????????? ?????? ????????? ????????????
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

        # ???????????? ????????? Delete
        for i in range(1, 5):
            try:
                if i in is_null:
                    self.get_image_field(obj, i)

            except MultiValueDictKeyError:
                pass

        # ????????? Overwrite ??? ????????? ????????? ??????
        obj.save()

        ret = super().partial_update(request, *args, **kwargs)

        sort_obj = self.get_object()

        arr = []

        arr.append(sort_obj.image1)
        arr.append(sort_obj.image2)
        arr.append(sort_obj.image3)
        arr.append(sort_obj.image4)

        # j??? ???????????? j + 1??? ???????????? ?????? ??????
        for i in reversed(range(len(arr))):  # 3, 2, 1, 0
            for j in range(i):  # 2, 1, 0
                if arr[j] == "" and not arr[j + 1] == "":
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

        sort_obj.image1 = arr[0]
        sort_obj.image2 = arr[1]
        sort_obj.image3 = arr[2]
        sort_obj.image4 = arr[3]

        sort_obj.save()
        if region:
            if check_str_digit(region):
                int(region)
            Share.objects.filter(id=sort_obj.id).update(region=Region.objects.get(id=region))

        ret = super(ShareViewSet, self).retrieve(request)

        response.success = True
        response.code = 200
        return response.response(data=[ret.data])

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
