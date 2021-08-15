import datetime
from rest_framework.status import HTTP_200_OK
from rest_framework import viewsets
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer
from posts.models import EcoCarping, Post
from bases.response import APIResponse


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
    serializer_class = AutoCampPostSerializer
    queryset = Post.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).list(request)

            response.success = True
            return response.response(data=ret.data, status=200)
        except Exception as e:
            response.code = "EXCEPTION_ERROR"
            return response.response(data=e, status=500)

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=ret.data, status=200)
        except Exception as e:
            response.code = "EXCEPTION_ERROR"
            return response.response(data=e, status=500)
