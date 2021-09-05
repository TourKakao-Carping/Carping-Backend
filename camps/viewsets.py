from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, exceptions

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp, CampSite
from camps.serializers import AutoCampSerializer, CampSiteSerializer


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

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        try:
            if check_str_digit(lat) and check_str_digit(lon):
                float(lat)
                float(lon)
            ret = super(AutoCampViewSet, self).partial_update(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))
