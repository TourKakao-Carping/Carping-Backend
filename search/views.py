from django.db.models import Count
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import TourSite, AutoCamp, CampSite
from camps.serializers import MainPageThemeSerializer
from search.serializers import TourSiteSerializer, AutoCampSearchSerializer, RegionCampSiteSerializer


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


# 메인 검색 - 지역별 인기 여행지 뷰
class RegionTourView(GenericAPIView, ListModelMixin):
    serializer_class = RegionCampSiteSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        region = data.get('region')
        popular = data.get('popular')
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

        if popular != "" and popular is not None:
            qs = CampSite.objects.annotate(
                bookmark_count=Count("bookmark")).filter(
                area__contains=f"{region}").order_by('-bookmark_count')[:5]
            serializer = self.get_serializer(qs, many=True)

            response.code = 200
            response.success = True
            return response.response(data=serializer.data)

        qs = CampSite.objects.filter(area__contains=f"{region}")
        bookmark_qs = qs.bookmark_qs(request.user.pk)
        serializer = self.get_serializer(bookmark_qs, many=True)

        response.code = 200
        response.success = True
        return response.response(data=serializer.data)

    def post(self, request):
        return self.list(request)
