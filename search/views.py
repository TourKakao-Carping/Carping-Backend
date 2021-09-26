from django.db.models import Count, Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from bases.response import APIResponse
from bases.utils import check_str_digit, check_distance
from camps.models import TourSite, AutoCamp, CampSite
from posts.models import UserPostInfo
from posts.serializers import UserPostListSerializer
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
        near_data = []

        for i in qs:  # 10km 반경 설정
            if check_distance(float(user_lat), float(user_lon), i.lat, i.lon) <= 10:
                near_data.append(i)

        serializer = self.get_serializer(near_data, many=True)
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
        near_data = []

        for i in serializer.data:
            if i['distance'] <= 10:  # 10km 반경 설정
                near_data.append(i)

        data = sorted(near_data, key=lambda x: x['distance'])

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

        # 캠핑장 이름만 가져오도록 변경할 지 논의
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


# 포스트 - 유저 작성 포스트 검색 -- UserPostListSerializer
class UserPostSearchView(GenericAPIView, ListModelMixin):
    serializer_class = UserPostListSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        keyword = request.data.get('keyword')

        qs = UserPostInfo.objects.filter(Q(user_post__title__icontains=f"{keyword}")
                                         | Q(user_post__sub_title1__icontains=f"{keyword}")
                                         | Q(user_post__text1__icontains=f"{keyword}")
                                         | Q(user_post__sub_title2__icontains=f"{keyword}")
                                         | Q(user_post__text2__icontains=f"{keyword}")
                                         | Q(user_post__sub_title3__icontains=f"{keyword}")
                                         | Q(user_post__text3__icontains=f"{keyword}")
                                         | Q(user_post__sub_title4__icontains=f"{keyword}")
                                         | Q(user_post__text4__icontains=f"{keyword}")
                                         | Q(user_post__sub_title5__icontains=f"{keyword}")
                                         | Q(user_post__text5__icontains=f"{keyword}")
                                         | Q(category__icontains=f"{keyword}")
                                         | Q(info__icontains=f"{keyword}")
                                         | Q(recommend_to__icontains=f"{keyword}"))

        serializer = self.get_serializer(qs, many=True)

        response.code = 200
        response.success = True
        return response.response(data=serializer.data)

    def post(self, request):
        return self.list(request)
