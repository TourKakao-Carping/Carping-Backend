from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import ugettext_lazy as _
from rest_framework.status import HTTP_200_OK

from bases.response import APIResponse
from camps.models import AutoCamp, CampSite

from rest_framework.views import APIView
from django.http import JsonResponse

from camps.serializers import AutoCampSerializer, AutoCampMainSerializer


class GetPopularSearchList(APIView):

    def check_popular_views(self, qs1, qs2):
        qs_sum = qs1 | qs2
        qs = qs_sum.order_by('-views')
        return qs

    def get_queryset(self):
        data = self.request.data
        count = data.get('count')

        count = int(count)

        if count == 0:
            count = None
            qs1 = CampSite.objects.autocamp_type(count)
            qs2 = AutoCamp.objects.ordering_views(count)

            qs = self.check_popular_views(qs1, qs2)
            return qs
        else:
            qs1 = CampSite.objects.autocamp_type(count)
            qs2 = AutoCamp.objects.ordering_views(count)

            qs = self.check_popular_views(qs1, qs2)
            print(qs[:3])
            return qs

    def post(self, request):
        print(self.get_queryset())
        return JsonResponse("hi", safe=False)


class AutoCampPartial(APIView):
    filterset_fields = ['count']

    @swagger_auto_schema(
        operation_id=_("auto-camp_list_with_count"),
        operation_description=_("지정한 수만큼 유저들의 차박지를 보여줍니다.(count가 0이면 전체)"),
        manual_parameters=[
            openapi.Parameter('count', openapi.IN_QUERY, type='int')],
        responses={200: openapi.Response(_("OK"), AutoCampMainSerializer)},
        tags=[_("camps"), ]
    )
    def post(self, request, *args, **kwargs):
        count = int(request.query_params.get('count', None))
        if count == 0:
            qs = AutoCamp.objects.all().order_by('-created_at')
        elif count > 0:
            qs = AutoCamp.objects.all().order_by('-created_at')[:count]

        response = APIResponse(False, "")
        response.success = True
        return response.response(status=HTTP_200_OK, data=AutoCampMainSerializer(qs, many=True).data)
