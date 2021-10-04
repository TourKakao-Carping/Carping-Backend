from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from django.utils.translation import ugettext_lazy as _
from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp
from comments.models import Review, Comment
from comments.serializers import ReviewSerializer, CommentSerializer
from posts.models import EcoCarping, Share, UserPostInfo


class ReviewViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(ReviewViewSet, self).retrieve(request)

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(data=str(e), status=404)

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        autocamp = request.data.get('autocamp')
        post = request.data.get('post')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if autocamp and post:
                response.code = status.HTTP_400_BAD_REQUEST
                return response.response(error_message=_(
                    "Invalid Request: cannot send autocamp & post together."))
            self.perform_create(serializer)
            latest = Review.objects.latest('id').id

            if autocamp:
                AutoCamp.objects.get(id=autocamp).review.add(
                    Review.objects.get(id=latest))
            if post:
                UserPostInfo.objects.get(id=post).review.add(
                    Review.objects.get(id=latest))

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[serializer.data])
        else:
            return response.response(error_message="necessary field(s) missing. check request once more.")

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        star1 = request.data.get('star1')
        star2 = request.data.get('star2')
        star3 = request.data.get('star3')
        star4 = request.data.get('star4')
        try:
            if check_str_digit(star1) and check_str_digit(star2) and check_str_digit(star3) and check_str_digit(star4):
                float(star1)
                float(star2)
                float(star3)
                float(star4)
            ret = super(ReviewViewSet, self).partial_update(request)

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_400_BAD_REQUEST
            return response.response(error_message=[str(e)])

    def destroy(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(ReviewViewSet, self).destroy(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


class CommentViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(CommentViewSet, self).retrieve(request)

            response.success = True
            response.status = status.HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def create(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        eco = request.data.get('eco')
        share = request.data.get('share')
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if eco and share:
                response.code = status.HTTP_400_BAD_REQUEST
                return response.response(error_message=_(
                    "Invalid Request: cannot send eco & share together."))
            self.perform_create(serializer)
            latest = Comment.objects.latest('id').id

            if eco:
                EcoCarping.objects.get(id=eco).comment.add(
                    Comment.objects.get(id=latest))
            if share:
                Share.objects.get(id=share).comment.add(
                    Comment.objects.get(id=latest))

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[serializer.data])
        else:
            return response.response(error_message="necessary field(s) missing")

    def update(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(CommentViewSet, self).update(request)

            response.success = True
            response.code = status.HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def destroy(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(CommentViewSet, self).destroy(request)

            response.success = True
            response.code = 200
            return response.response(data=[ret.data])
        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))
