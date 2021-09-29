from django.db.models import Count, Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, DestroyModelMixin

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
        keyword = data.get('keyword')
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        if not check_str_digit(user_lat) or not check_str_digit(user_lon):
            response.code = 400
            return response.response(error_message="check lat, lon")

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
        near_data = []

        for i in serializer.data:
            if i['distance'] <= 30:  # 30km 반경 설정
                near_data.append(i)

        data = sorted(near_data, key=lambda x: x['distance'])

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
        popular = []

        if type == 'main':
            # recent_qs = Search.objects.filter(user=user, type=0).order_by('-created_at')
            # popular_qs = sorted(Search.objects.filter(type=0),
            #                     key=lambda a: Search.same_keyword_count(Search, a), reverse=True)
            # recent_serializer = self.get_serializer(recent_qs, many=True)
            # popular_serializer = self.get_serializer(popular_qs, many=True)
            for i in Search.objects.filter(user=user, type=0).order_by('-created_at'):
                if i.keyword in recent:
                    pass
                else:
                    recent.append(i.keyword)
                if len(recent) > 9:
                    break

            for i in sorted(Search.objects.filter(type=0),
                            key=lambda a: Search.same_keyword_count(Search, a), reverse=True):
                if i.name in popular:
                    pass
                else:
                    popular.append(i.name)
                if len(popular) > 5:
                    break

        elif type == 'post':
            for i in Search.objects.filter(user=user, type=1).order_by('-created_at'):
                if i.keyword in recent:
                    pass
                else:
                    recent.append(i.keyword)
                if len(recent) > 9:
                    break

            for i in sorted(Search.objects.filter(type=1),
                            key=lambda a: Search.same_keyword_count(Search, a), reverse=True):
                if i.name in popular:
                    pass
                else:
                    popular.append(i.name)
                if len(popular) > 5:
                    break

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

        qs = AutoCamp.objects.all()
        serializer = self.get_serializer(qs, many=True)
        near_data = []

        for i in serializer.data:
            if i['distance'] <= 30:  # 30km 반경 설정
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
