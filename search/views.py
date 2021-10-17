from django.db.models import Count, Q, Case, When
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, DestroyModelMixin

from accounts.models import Search
from bases.response import APIResponse
from bases.utils import check_str_digit, check_distance, get_bounding_box
from camps.models import TourSite, AutoCamp, CampSite
from posts.models import UserPostInfo
from posts.serializers import UserPostListSerializer
from search.serializers import TourSiteSerializer, AutoCampSearchSerializer, RegionCampSiteSerializer, \
    MainSearchSerializer, UserKeywordSerializer, PopularCampSiteSearchSerializer


class MainSearchView(GenericAPIView, ListModelMixin):
    serializer_class = MainSearchSerializer

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
        # near_data = []
        #
        # for i in serializer.data:
        #     if i['distance'] <= 30:  # 30km 반경 설정
        #         near_data.append(i)
        #
        # data = sorted(near_data, key=lambda x: x['distance'])

        serializer = self.get_serializer(qs, many=True)
        data = sorted(serializer.data, key=lambda x: x['distance'])

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)


class UserKeywordView(GenericAPIView, ListModelMixin, DestroyModelMixin):
    serializer_class = UserKeywordSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user
        type = data.get('type')

        recent = []

        if type == 'main':
            recent_qs = list(Search.objects.values('keyword').filter(
                user=user, type=0).order_by('-created_at')[:10].values_list("keyword", flat=True))

            for i in recent_qs:
                if i not in recent:
                    recent.append(i)

            popular = list(Search.objects.values('name').annotate(
                search_count=Count('name')).filter(
                type=0).order_by('-search_count')[:6].values_list("name", flat=True))

        elif type == 'post':
            recent_qs = list(Search.objects.values('keyword').filter(
                user=user, type=1).order_by('-created_at')[:10].values_list("keyword", flat=True))

            for i in recent_qs:
                if i not in recent:
                    recent.append(i)

            popular = list(Search.objects.values('name').annotate(
                search_count=Count('name')).filter(
                type=1).order_by('-search_count')[:6].values_list("name", flat=True))

        else:
            return response.response(error_message="INVALID_TYPE - choices are <main, post>")

        response.code = 200
        response.success = True
        return response.response(data=[{"recent": recent},
                                       {"popular": popular}])

    def post(self, request):
        return self.list(request)

    def destroy(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user

        keyword = data.get('keyword')
        type = data.get('type')
        all = data.get('all')

        # 최근 검색어 데이터 삭제
        if type == 'main':
            if Search.objects.filter(user=user, keyword=keyword, type=0).exists():
                Search.objects.filter(user=user, keyword=keyword, type=0).delete()
            else:
                return response.response(error_message="유저와 검색어를 다시 확인해주세요.")

        if type == 'post':
            if Search.objects.filter(user=user, keyword=keyword, type=1).exists():
                Search.objects.filter(user=user, keyword=keyword, type=1).delete()
            else:
                return response.response(error_message="유저와 검색어를 다시 확인해주세요.")

        response.code = 200
        response.success = True
        return response.response(data=[])

    @swagger_auto_schema(
        operation_id=_("Delete Recent User-Keyword"),
        operation_description=_("사용자의 최근 검색어를 삭제합니다."),
        request_body=MainSearchSerializer,
        responses={200: openapi.Response(_("OK"), )},
        tags=[_("search"), ]
    )
    def delete(self, request):
        return self.destroy(request)


class KeywordSaveView(ListModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = MainSearchSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user

        keyword = data.get('keyword')
        name = data.get('name')
        type = data.get('type')

        # 검색 데이터 쌓음
        if type == 'main':
            if Search.objects.filter(user=user, keyword=keyword, name=name, type=0).exists():
                pass
            else:
                Search.objects.create(user=user, keyword=keyword, name=name, type=0)

        if type == 'post':
            if Search.objects.filter(user=user, keyword=keyword, name=name, type=1).exists():
                pass
            else:
                Search.objects.create(user=user, keyword=keyword, name=name, type=1)

        response.code = 200
        response.success = True
        return response.response(data=[])

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

        # 30km 반경 설정, 계산 식 오차를 고려해 약 25로 잡음
        min_latitude, max_latitude, min_longitude, max_longitude = \
            get_bounding_box(user_lat, user_lon, 25)

        qs = AutoCamp.objects.filter(
            latitude__range=(
                min_latitude,
                max_latitude
            ),
            longitude__range=(
                min_longitude,
                max_longitude
            )
        )

        serializer = self.get_serializer(qs, many=True)

        # near_data = []

        # for i in serializer.data:
        #     if i['distance'] <= 30:  # 30km 반경 설정
        #         near_data.append(i)

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

        popular = CampSite.objects.none()

        popular_searched_site_name = list(Search.objects.filter(
            type=0).values_list("name", flat=True))

        for site_name in popular_searched_site_name:
            if f"{region}" in CampSite.objects.get(name=site_name).area:
                popular |= CampSite.objects.filter(name=site_name)

        if len(popular) < 5:
            qs = CampSite.objects.filter(area__icontains=f"{region}").exclude(id__in=popular)[:5 - len(popular)]
            result = list(popular) + list(qs)
        else:
            result = popular

        serializer = self.get_serializer(result, many=True)
        data = sorted(serializer.data, key=lambda x: x['search_count'], reverse=True)

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)


# 포스트 - 유저 작성 포스트 검색 -- UserPostListSerializer
class UserPostSearchView(GenericAPIView, ListModelMixin):
    serializer_class = UserPostListSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        keyword = request.data.get('keyword')

        if keyword == "" or keyword == " " or keyword is None:
            return response.response(error_message="키워드를 입력해주세요")

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
                                         | Q(recommend_to__icontains=f"{keyword}")).exclude(is_approved=False)

        like_qs = qs.like_qs(request.user.pk)
        serializer = self.get_serializer(like_qs, many=True)

        response.code = 200
        response.success = True
        return response.response(data=serializer.data)

    def post(self, request):
        return self.list(request)


class PopularCampSiteSearchView(GenericAPIView, ListModelMixin, DestroyModelMixin):
    serializer_class = PopularCampSiteSearchSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        region = data.get('region')

        popular = CampSite.objects.none()

        popular_searched_site_name = list(Search.objects.filter(
            type=0).values_list("name", flat=True))

        for site_name in popular_searched_site_name:
            if f"{region}" in CampSite.objects.get(name=site_name).area:
                popular |= CampSite.objects.filter(name=site_name)

        bookmark_qs = popular.bookmark_qs(request.user.pk)

        if len(bookmark_qs) < 3:
            qs = CampSite.objects.filter(area__icontains=f"{region}").exclude(id__in=bookmark_qs).bookmark_qs(
                request.user.pk)[:3 - len(bookmark_qs)]
            result = list(bookmark_qs) + list(qs)
        else:
            result = bookmark_qs[:3]

        serializer = self.get_serializer(result, many=True)

        data = sorted(serializer.data, key=lambda x: x['search_count'], reverse=True)

        response.code = 200
        response.success = True
        return response.response(data=data)

    def post(self, request):
        return self.list(request)
