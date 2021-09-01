from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp
from camps.serializers import AutoCampSerializer


class AutoCampViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = AutoCampSerializer
    queryset = AutoCamp.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampViewSet, self).retrieve(request)
            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            print("error occurred!!!!")
            print(str(e))
            # response.code = "UNEXPECTED_ERROR"
            return response.response(data=str(e), status=200)

    def create(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(AutoCampViewSet, self).create(request)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=[str(e)], status=200)

        response.success = True
        return response.response(data=[ret.data], status=200)

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        if check_str_digit(lat) and check_str_digit(lon):
            float(lat)
            float(lon)
        try:
            ret = super(AutoCampViewSet, self).partial_update(request)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=[str(e)], status=200)

        response.success = True
        return response.response(data=[ret.data], status=200)
