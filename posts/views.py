import datetime

from posts.constants import A_TO_Z_LIST_NUM, POST_INFO_CATEGORY_LIST_NUM
from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from haversine import haversine

from django.db.models import Count, query, F
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from bases.serializers import MessageSerializer
from posts.models import EcoCarping, Post, Share, Region, Store, UserPost, UserPostInfo
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSortSerializer, PostLikeSerializer, \
    ShareCompleteSerializer, ShareSortSerializer, SigunguSearchSerializer, DongSearchSerializer, StoreSerializer, UserPostAddProfileSerializer, UserPostInfoDetailSerializer, UserPostListSerializer, UserPostDetailSerializer

from bases.utils import check_data_key, check_str_digit, paginate, custom_list, custom_dict, check_distance
from bases.response import APIResponse


class GetAutoCampPostForWeekend(GenericAPIView):
    """
    이번주말 이런차박지 어때요
    메인 페이지 및 전체보기 클릭 시 썸네일 포스트들 가져오기
    (id, tags, title, thumbnail, views)
    """
    serializer_class = AutoCampPostForWeekendSerializer

    def get_queryset(self):
        data = self.request.data
        count = data.get('count')

        count = int(count)

        if count == 0:
            qs = Post.objects.all().order_by('-created_at')
        elif count > 0:
            qs = Post.objects.all().order_by('-views')[:count]
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = APIResponse(success=False, code=400)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=serializer.data)

    def post(self, request):
        response = APIResponse(success=False, code=400)

        data = request.data
        count = data.get('count')

        if not check_data_key(count) or not check_str_digit(count):
            return response.response(error_message='Invalid Count')

        return self.list(request)


class EcoCarpingSort(GenericAPIView):
    serializer_class = EcoCarpingSortSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = self.request.data
        sort = data.get('sort')

        if sort == 'recent':
            if not 'count' in self.request.data:
                return response.response(error_message="'count' field is required")
            count = int(self.request.data.get('count', None))

            if count == 0:
                qs = EcoCarping.objects.all().order_by('-created_at')
            elif count > 0:
                qs = EcoCarping.objects.all().order_by('-created_at')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            today_count = EcoCarping.objects.filter(
                created_at__contains=datetime.date.today()).count()
            serializer.insert(0, {"today_count": today_count})

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'popular':
            qs = EcoCarping.objects.annotate(
                like_count=Count('like')).order_by('-like_count')
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer.data)

        else:
            return response.response(error_message="INVALID_SORT - choices are <recent, popular>")

    @swagger_auto_schema(
        operation_id=_("Sort EcoCarping(recent/distance/popular)"),
        operation_description=_("에코리뷰를 정렬합니다."),
        request_body=EcoCarpingSortSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)


class EcoLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Eco"),
        operation_description=_("포스트에 좋아요를 답니다."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                post_to_like = EcoCarping.objects.get(
                    id=serializer.validated_data["post_to_like"])
                user.eco_like.add(post_to_like)
                data = MessageSerializer({"message": _("포스트 좋아요 완료")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Like Eco"),
        operation_description=_("포스트에 단 좋아요를 취소합니다."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.eco_like.through.objects.filter(
                    user=user, ecocarping=serializer.validated_data["post_to_like"]).delete()
                data = MessageSerializer({"message": _("포스트 좋아요 취소")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")


# 무료나눔
class ShareSort(GenericAPIView):
    serializer_class = ShareSortSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = self.request.data
        sort = data.get('sort')

        if not 'count' in self.request.data:
            return response.response(error_message="'count' field is required")
        count = int(self.request.data.get('count', None))

        if sort == 'recent':
            if count == 0:
                qs = Share.objects.annotate(
                    like_count=Count("like")).order_by('-created_at')
            elif count > 0:
                qs = Share.objects.annotate(like_count=Count(
                    "like")).order_by('-created_at')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            total_share = Share.objects.all().count()
            serializer.insert(0, {"total_share": total_share})  # 안드와 요청 방식 상의

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'popular':
            if count == 0:
                qs = Share.objects.annotate(
                    like_count=Count("like")).order_by('-like_count')
            elif count > 0:
                qs = Share.objects.annotate(like_count=Count(
                    "like")).order_by('-like_count')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        else:
            return response.response(error_message="INVALID_SORT")

    @swagger_auto_schema(
        operation_id=_("Sort Share-Posts(recent/distance)"),
        operation_description=_("무료나눔 포스트를 정렬합니다."),
        request_body=EcoCarpingSortSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)


class ShareLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Share"),
        operation_description=_("포스트에 좋아요를 답니다."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                post_to_like = Share.objects.get(
                    id=serializer.validated_data["post_to_like"])
                user.share_like.add(post_to_like)
                data = MessageSerializer({"message": _("포스트 좋아요 완료")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Like Share"),
        operation_description=_("포스트에 단 좋아요를 취소합니다."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.share_like.through.objects.filter(
                    user=user, share=serializer.validated_data["post_to_like"]).delete()
                data = MessageSerializer({"message": _("포스트 좋아요 취소")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")


class ShareCompleteView(APIView):
    @swagger_auto_schema(
        operation_id=_("Share Complete"),
        operation_description=_("거래 완료 상태로 변환"),
        request_body=ShareCompleteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        serializer = ShareCompleteSerializer(data=request.data)

        if serializer.is_valid():
            try:
                Share.objects.filter(
                    id=serializer.validated_data["share_to_complete"]).update(is_shared=True)
                data = MessageSerializer({"message": _("거래 완료")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'share_to_complete' field is required.")

    @swagger_auto_schema(
        operation_id=_("Cancel Share Complete"),
        operation_description=_("거래 완료 취소"),
        request_body=ShareCompleteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        serializer = ShareCompleteSerializer(data=request.data)

        if serializer.is_valid():
            try:
                Share.objects.filter(
                    id=serializer.validated_data["share_to_complete"]).update(is_shared=False)

                data = MessageSerializer({"message": _("거래 완료 취소")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'share_to_complete' field is required.")


# 동네 검색 api
class RegionSearchView(APIView):
    @swagger_auto_schema(
        operation_id=_("Search region in Share"),
        operation_description=_("무료나눔 동네 검색"),
        request_body=SigunguSearchSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)

        sido = request.data.get('sido')
        sigungu = request.data.get('sigungu')

        sido_list = [_("강원도"), _("경기도"), _("경상남도"), _("경상북도"), _("광주광역시"),
                     _("대구광역시"), _("대전광역시"), _("부산광역시"), _(
                         "서울특별시"), _("세종특별자치시"),
                     _("울산광역시"), _("인천광역시"), _(
                         "전라남도"), _("전라북도"), _("제주특별자치도"),
                     _("충청남도"), _("충청북도"), ]

        if 'sigungu' in request.data:
            if sigungu == "":
                qs = Region.objects.filter(sido=sido)
            else:
                qs = Region.objects.filter(sigungu=sigungu)

            data = DongSearchSerializer(qs, many=True).data

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=data)

        else:
            if sido in sido_list:
                qs = Region.objects.filter(sido=f"{sido}")
                data = SigunguSearchSerializer(qs, many=True).data

                result = []

                for i in range(len(data)):
                    if data[i] in result:
                        pass
                    else:
                        result.append(data[i])

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=result)

            else:
                return response.response(error_message="시도명이 잘못되었습니다.")


# 스토어 리스트 반환 api
class StoreListView(APIView):
    def get(self, request):
        response = APIResponse(success=False, code=400)

        items = Store.objects.all()

        data = StoreSerializer(items, many=True).data

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=data)


class UserPostInfoListAPIView(ListModelMixin, GenericAPIView):
    # serializer_class = UserPostListSerializer

    def get_serializer_class(self):
        data = self.request.data

        type = int(data.get('type'))

        if type == 1:
            return UserPostAddProfileSerializer
        else:
            return UserPostListSerializer

    def get_queryset(self):
        """
        type
        2 : A부터 Z까지 리스트 (랜덤 10개)
        3 : 차박 포스트 페이지 리스트 (카테고리별) -> 초보 차박러를 위한 포스트, 차박에 관한 모든 것, 차에 맞는 차박여행
        4 : 각 카테고리 리스트
        """

        user = self.request.user
        data = self.request.data

        type = int(data.get('type'))

        try:
            category = int(data.get('category'))
        except TypeError:
            category = 0

        if type == 1:
            qs_type = UserPostInfo.objects.random_qs(A_TO_Z_LIST_NUM)
        elif type == 2:
            qs = UserPostInfo.objects.category_qs(
                POST_INFO_CATEGORY_LIST_NUM, user.pk)

            return qs
        else:
            qs_type = UserPostInfo.objects.filter(category=category)

        qs_type = qs_type.select_related('author').prefetch_related(
            'author__profile').annotate(user_profile=F("author__profile__image"))

        qs = qs_type.like_qs(user.pk)

        return qs

    def post(self, request):
        data = request.data

        response = APIResponse(success=False, code=400)

        type = data.get('type')

        if not check_str_digit(type):
            response.code = status.HTTP_400_BAD_REQUEST
            return response.response(error_message=_("Invalid type"))

        list = super().list(request)

        response.code = 200
        response.success = True
        return response.response(data=list.data)


class UserPostInfoDetailAPIView(RetrieveModelMixin, GenericAPIView):
    queryset = UserPostInfo.objects.user_post_info_detail()
    serializer_class = UserPostInfoDetailSerializer

    def get_queryset(self):
        user = self.request.user
        pk = user.pk

        qs_info = UserPostInfo.objects.user_post_info_detail()
        qs = qs_info.like_qs(pk)

        return qs

    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        try:
            ret = super().retrieve(request)
            response.success = True
            response.code = 200
            return response.response(data=ret.data)

        except BaseException as e:
            return response.response(error_message=str(e))


class UserPostDetailAPIView(RetrieveModelMixin, GenericAPIView):
    queryset = UserPost.objects.all()
    serializer_class = UserPostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        try:
            ret = super().retrieve(request)
            response.success = True
            response.code = 200
            return response.response(data=ret.data)

        except BaseException as e:
            return response.response(error_message=str(e))


# class UserPostPaymentAPIView()
