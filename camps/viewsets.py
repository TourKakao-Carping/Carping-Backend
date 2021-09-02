from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp
from camps.serializers import AutoCampSerializer


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
            print("error occurred!!!!")
            response.code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response.response(data=str(e))

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(AutoCampViewSet, self).create(request)
        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(data=[str(e)])

        response.success = True
        response.code = 200
        return response.response(data=[ret.data])

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(AutoCampViewSet, self).partial_update(request)
        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(data=[str(e)])

        response.success = True
        response.code = 200
        return response.response(data=[ret.data])
