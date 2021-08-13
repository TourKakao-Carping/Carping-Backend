from rest_framework.generics import GenericAPIView
from rest_framework import viewsets, mixins

from posts.models import EcoCarping, Post
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSerializer


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()


class GetAutoCampPostForWeekend(mixins.ListModelMixin, GenericAPIView):
    serializer_class = AutoCampPostForWeekendSerializer

    def get_queryset(self):
        data = self.request.data
        count = data.get('count')

        if count == 0:
            qs = Post.objects.all().order_by('-created_at')
        else:
            qs = Post.objects.all().order_by('-views')[:count]
        return qs

    def post(self, request):
        return self.list(request)
