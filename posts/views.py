import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from haversine import haversine

from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from bases.serializers import MessageSerializer
from posts.models import EcoCarping, Post, Share
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSortSerializer, PostLikeSerializer, \
    ShareCompleteSerializer, ShareSortSerializer

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
            serializer = EcoCarpingSortSerializer(
                custom_list(queryset), many=True).data

            today_count = EcoCarping.objects.filter(
                created_at__contains=datetime.date.today()).count()
            serializer.insert(0, {"today_count": today_count})

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'distance':
            if not 'latitude' in self.request.data or not 'longitude' in self.request.data:
                return response.response(error_message="'latitude', 'longitude' fields are required")

            queryset = EcoCarping.objects.all()
            paginate(self, queryset)

            list = []
            for i in queryset:
                distance = check_distance(float(data.get('latitude', None)),
                                          float(data.get('longitude', None)),
                                          float(i.latitude), float(i.longitude))
                i = custom_dict(i)
                i['distance'] = distance
                list.append(i)
            list.sort(key=(lambda x: x['distance']))

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=EcoCarpingSortSerializer(list, many=True).data)

        if sort == 'popular':
            qs = EcoCarping.objects.annotate(
                like_count=Count('like')).order_by('-like_count')
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = EcoCarpingSortSerializer(
                custom_list(queryset), many=True)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer.data)

        else:
            return response.response(error_message="INVALID_SORT - choices are <recent, distance, popular>")

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

        if sort == 'recent':
            if not 'count' in self.request.data:
                return response.response(error_message="'count' field is required")
            count = int(self.request.data.get('count', None))

            if count == 0:
                qs = Share.objects.annotate(like_count=Count("like")).order_by('-created_at')
            elif count > 0:
                qs = Share.objects.annotate(like_count=Count("like")).order_by('-created_at')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = [self.get_serializer(
                queryset, many=True).data]

            total_share = Share.objects.all().count()
            serializer.insert(0, {"total_share": total_share})  # 안드와 요청 방식 상의

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'popular':
            qs = Share.objects.annotate(like_count=Count("like")).order_by('like_count')

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = [self.get_serializer(
                queryset, many=True).data]

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
# class RegionSearchView(APIView):
#
#     def post(self, request):
#         response = APIResponse(success=False, code=400)
