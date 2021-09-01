from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from bases.response import APIResponse
from bases.utils import check_str_digit
from camps.models import AutoCamp
from comments.models import Review, Comment
from comments.serializers import ReviewSerializer, CommentSerializer
from posts.models import EcoCarping, Share


class ReviewViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(ReviewViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=str(e), status=404)

    def create(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        autocamp = request.data.get('autocamp')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        latest = Review.objects.latest('id').id
        AutoCamp.objects.get(id=autocamp).review.add(Review.objects.get(id=latest))
        response.success = True
        return response.response(data=[serializer.data], status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        star1 = request.data.get('star1')
        star2 = request.data.get('star2')
        star3 = request.data.get('star3')
        star4 = request.data.get('star4')
        if check_str_digit(star1) and check_str_digit(star2) and check_str_digit(star3) and check_str_digit(star4):
            float(star1)
            float(star2)
            float(star3)
            float(star4)
        try:
            ret = super(ReviewViewSet, self).partial_update(request)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=[str(e)], status=200)

        response.success = True
        return response.response(data=[ret.data], status=200)


class CommentViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(CommentViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=str(e), status=404)

    def create(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        eco = request.data.get('eco')
        share = request.data.get('share')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if eco and share:
            return APIResponse(False, "INVALID_REQUEST").response('', status=400)
        self.perform_create(serializer)
        latest = Comment.objects.latest('id').id
        if eco:
            EcoCarping.objects.get(id=eco).comment.add(Comment.objects.get(id=latest))
        if share:
            Share.objects.get(id=share).comment.add(Comment.objects.get(id=latest))
        response.success = True
        return response.response(data=[serializer.data], status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(CommentViewSet, self).partial_update(request)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=[str(e)], status=200)

        response.success = True
        return response.response(data=[ret.data], status=200)
