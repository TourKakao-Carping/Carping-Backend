from django.shortcuts import render

# Create your views here.
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import ugettext_lazy as _
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from bases.response import APIResponse
from bases.serializers import MessageSerializer
from comments.models import Review, Comment
from comments.serializers import ReviewLikeSerializer, CommentLikeSerializer


class ReviewLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Review"),
        operation_description=_("리뷰에 좋아요를 답니다."),
        request_body=ReviewLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("comments"), ]
    )
    def post(self, request):
        user = request.user
        serializer = ReviewLikeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            review_to_like = Review.objects.get(id=serializer.validated_data["review_to_like"])
            user.review_like.add(review_to_like)
            data = MessageSerializer({"message": _("리뷰 좋아요 완료")}).data
            response = APIResponse(False, "")
            response.success = True
            return response.response(status=HTTP_200_OK, data=[data])

    @swagger_auto_schema(
        operation_id=_("Delete Like Review"),
        operation_description=_("리뷰에 단 좋아요를 취소합니다."),
        request_body=ReviewLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("comments"), ]
    )
    def delete(self, request):
        user = request.user
        serializer = ReviewLikeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.review_like.through.objects.filter(user=user, review=serializer.validated_data["review_to_like"]).delete()
            data = MessageSerializer({"message": _("리뷰 좋아요 취소")}).data
            response = APIResponse(False, "")
            response.success = True
            return response.response(status=HTTP_200_OK, data=[data])


class CommentLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Comment"),
        operation_description=_("댓글에 좋아요를 답니다."),
        request_body=CommentLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("comments"), ]
    )
    def post(self, request):
        user = request.user
        serializer = CommentLikeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            comment_to_like = Comment.objects.get(id=serializer.validated_data["comment_to_like"])
            user.comment_like.add(comment_to_like)
            data = MessageSerializer({"message": _("댓글 좋아요 완료")}).data
            response = APIResponse(False, "")
            response.success = True
            return response.response(status=HTTP_200_OK, data=[data])

    @swagger_auto_schema(
        operation_id=_("Delete Like Comment"),
        operation_description=_("댓글에 단 좋아요를 취소합니다."),
        request_body=CommentLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("comments"), ]
    )
    def delete(self, request):
        user = request.user
        serializer = CommentLikeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.comment_like.through.objects.filter(user=user, comment=serializer.validated_data["comment_to_like"]).delete()
            data = MessageSerializer({"message": _("댓글 좋아요 취소")}).data
            response = APIResponse(False, "")
            response.success = True
            return response.response(status=HTTP_200_OK, data=[data])
