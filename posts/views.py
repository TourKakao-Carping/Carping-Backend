import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

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


class EcoCarpingPartial(APIView):
    filterset_fields = ['count']

    @swagger_auto_schema(
        operation_id=_("eco-carping_list_with_count"),
        operation_description=_("지정한 수만큼 에코카핑을 보여줍니다. (count가 0이면 전체)"),
        manual_parameters=[
            openapi.Parameter('count', openapi.IN_QUERY, type='int')],
        responses={200: openapi.Response(_("OK"), EcoCarpingSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request, *args, **kwargs):
        count = int(request.query_params.get('count', None))
        if count == 0:
            qs = EcoCarping.objects.all().order_by('-created_at')
        elif count > 0:
            qs = EcoCarping.objects.all().order_by('-created_at')[:count]

        today_count = EcoCarping.objects.filter(
            created_at__contains=datetime.date.today()).count()
        response = APIResponse(False, "")
        response.success = True
        return response.response(status=HTTP_200_OK, data={"today_count": today_count,
                                                           "ecocarping": EcoCarpingSerializer(qs, many=True).data})
