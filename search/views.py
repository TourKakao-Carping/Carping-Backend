from django.db.models import Count, Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from accounts.models import Search
from bases.response import APIResponse
from bases.utils import check_str_digit, check_distance
from camps.models import TourSite, AutoCamp, CampSite
from posts.models import UserPostInfo
from posts.serializers import UserPostListSerializer
from search.serializers import TourSiteSerializer, AutoCampSearchSerializer, RegionCampSiteSerializer, \
    MainSearchSerializer, UserKeywordSerializer


class MainSearchView(GenericAPIView, ListModelMixin):
    serializer_class = MainSearchSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user

        keyword = data.get('keyword')
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

        # 검색 데이터 쌓음
        if Search.objects.filter(user=user, keyword=keyword, type=0).exists():
            pass
        else:
            Search.objects.create(user=user, keyword=keyword, type=0)

        # 실제 검색
        qs = CampSite.objects.filter(Q(name__icontains=f"{keyword}")
                                     | Q(event__icontains=f"{keyword}")
                                     | Q(program__icontains=f"{keyword}")
                                     | Q(address__icontains=f"{keyword}")
                                     | Q(type__icontains=f"{keyword}")
                                     | Q(sub_facility__icontains=f"{keyword}")
                                     | Q(season__icontains=f"{keyword}")
                                     | Q(area__icontains=f"{keyword}")
                                     | Q(themenv__icontains=f"{keyword}")
                                     | Q(rental_item__icontains=f"{keyword}")
                                     | Q(tags__name__icontains=f"{keyword}"))
        serializer = self.get_serializer(qs, many=True)

        data = sorted(serializer.data, key=lambda x: x['distance'])

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)


class UserKeywordView(GenericAPIView, ListModelMixin):
    serializer_class = UserKeywordSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user
        type = data.get('type')

        recent = []
        popular = []

        # 검색어 몇개까지 보여줄지 상의
        if type == 'main':
            # recent_qs = Search.objects.filter(user=user, type=0).order_by('-created_at')
            # popular_qs = sorted(Search.objects.filter(type=0),
            #                     key=lambda a: Search.same_keyword_count(Search, a), reverse=True)
            # recent_serializer = self.get_serializer(recent_qs, many=True)
            # popular_serializer = self.get_serializer(popular_qs, many=True)
            for i in Search.objects.filter(user=user, type=0).order_by('-created_at'):
                recent.append(i.keyword)

            for i in sorted(Search.objects.filter(type=0),
                            key=lambda a: Search.same_keyword_count(Search, a), reverse=True):
                if i.keyword in popular:
                    pass
                else:
                    popular.append(i.keyword)

        elif type == 'post':
            for i in Search.objects.filter(user=user, type=1).order_by('-created_at'):
                recent.append(i.keyword)

            for i in sorted(Search.objects.filter(type=1),
                            key=lambda a: Search.same_keyword_count(Search, a), reverse=True):
                if i.keyword in popular:
                    pass
                else:
                    popular.append(i.keyword)

        else:
            return response.response(error_message="INVALID_TYPE - choices are <main, post>")

        response.code = 200
        response.success = True
        return response.response(data=[{"recent": recent},
                                       {"popular": popular}])

    def post(self, request):
        return self.list(request)


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

        if keyword == "" or keyword == " " or keyword is None:
            return response.response(error_message="키워드를 입력해주세요")

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

        qs = CampSite.objects.annotate(
            bookmark_count=Count("bookmark")).filter(
            area__contains=f"{region}").order_by('-bookmark_count')[:5]
        serializer = self.get_serializer(qs, many=True)

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

        user = request.user
        keyword = request.data.get('keyword')

        # 검색 데이터 쌓음
        if Search.objects.filter(user=user, keyword=keyword, type=1).exists():
            pass
        else:
            Search.objects.create(user=user, keyword=keyword, type=1)

        # 실제 검색
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
