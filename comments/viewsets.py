from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from bases.response import APIResponse
from camps.models import AutoCamp
from comments.models import Review
from comments.serializers import ReviewSerializer


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
