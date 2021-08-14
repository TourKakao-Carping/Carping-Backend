from django.http.response import JsonResponse
from rest_framework.generics import GenericAPIView
from rest_framework import viewsets, mixins

from posts.models import EcoCarping, Post
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSerializer

from bases.utils import check_data_key, check_str_digit


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()


class GetAutoCampPostForWeekend(mixins.ListModelMixin, GenericAPIView):
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

    def post(self, request):
        data = request.data
        count = data.get('count')

        if not check_data_key(count) or not check_str_digit(count):
            return JsonResponse({"message": "Invalid Key"}, status=400)

        return self.list(request)
