from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import TourSite, AutoCamp
from search.serializers import TourSiteSerializer, AutoCampSearchSerializer


class ToursiteSearchView(ListModelMixin, GenericAPIView):
    serializer_class = TourSiteSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        keyword = data.get('keyword')
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

        qs = TourSite.objects.filter(name__contains=f"{keyword}")
        serializer = self.get_serializer(qs, many=True)
        data = sorted(serializer.data, key=lambda x: x['distance'])

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)


class AutoCampMapView(GenericAPIView, ListModelMixin):
    serializer_class = AutoCampSearchSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

        qs = AutoCamp.objects.all()
        serializer = self.get_serializer(qs, many=True)
        data = sorted(serializer.data, key=lambda x: x['distance'])

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)
