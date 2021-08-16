import datetime
from rest_framework import viewsets
from rest_framework.status import *
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer
from posts.models import EcoCarping, Post
from bases.response import APIResponse
from rest_framework.exceptions import MethodNotAllowed

# 4. 실시간 에코리뷰 api - 최근 3개 (사진, 제목, 내용, 시간, 리뷰날짜, pk, 오늘에코리뷰 인증 수 )


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        today_count = EcoCarping.objects.filter(
            created_at__contains=datetime.date.today()).count()
        response = APIResponse(False, "")
        response.success = True
        return response.response(status=HTTP_200_OK, data={"today_count": today_count,
                                                           "ecocarping": self.get_serializer(queryset, many=True).data})


class AutoCampPostForWeekendViewSet(viewsets.ModelViewSet):
    """
    이번주말 이런차박지 어때요 상세페이지 가져오기 API
    """
    serializer_class = AutoCampPostSerializer
    queryset = Post.objects.all().order_by('-created_at')

    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=str(e), status=404)
