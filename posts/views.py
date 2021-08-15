from rest_framework.generics import GenericAPIView

from posts.models import EcoCarping, Post
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSerializer

from bases.utils import check_data_key, check_str_digit
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
        response = APIResponse(False, "")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        response.success = True
        return response.response(data=serializer.data, status=200)

    def post(self, request):
        data = request.data

        count = data.get('count')

        if not check_data_key(count) or not check_str_digit(count):
            return APIResponse(False, "INVALID_COUNT").response('', status=400)
        return self.list(request)
