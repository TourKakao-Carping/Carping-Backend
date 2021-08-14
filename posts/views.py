import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from accounts.models import User, EcoLevel
from posts.models import EcoCarping
from posts.serializers import EcoCarpingSerializer, EcoRankingSerializer


# 4. 실시간 에코리뷰 api - 최근 3개 (사진, 제목, 내용, 시간, 리뷰날짜, pk, 오늘에코리뷰 인증 수 )
class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        today_count = EcoCarping.objects.filter(created_at__contains=datetime.date.today()).count()
        return Response(status=HTTP_200_OK, data={"today_count": today_count,
                                                  "results": self.get_serializer(queryset, many=True).data})


# 5. 에코랭킹 api - 상위 7개 (프사, 뱃지, 아이디, 순위, 에카포스트 수)
class EcoRankingView(APIView):
    allowed_method = ["GET"]

    @swagger_auto_schema(
        operation_id=_("Get Eco-Ranking"),
        operation_description=_("메인화면 - 에코카핑에서 보여질 에코 랭킹 뷰입니다."),
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='integer')],
        responses={200: openapi.Response(_("OK"), EcoRankingSerializer, )},
        tags=[_("에코카핑"), ],
    )
    def get(self, request):
        eco = User.objects.all()
        today = datetime.date.today() + relativedelta(days=1)
        pre_month = today - relativedelta(months=1)
        current_user = User.objects.get(id=1)

        if current_user.eco.count() <= 3:
            current_user.profile.update(level=EcoLevel.objects.get(id=1))
        elif current_user.eco.count() <= 8:
            current_user.profile.update(level=EcoLevel.objects.get(id=2))
        elif current_user.eco.count() >= 9:
            current_user.profile.update(level=EcoLevel.objects.get(id=3))

        eco_percentage = current_user.eco.count() * 10
        monthly_eco_count = EcoCarping.objects.filter(user_id=current_user.id,
                                                      created_at__range=[pre_month, today]).count()

        return Response(status=HTTP_200_OK, data={"current_user": [EcoRankingSerializer(current_user).data,
                                                                   {"eco_percentage": eco_percentage,
                                                                    "monthly_eco_count": monthly_eco_count}],
                                                  "results": EcoRankingSerializer(eco, many=True).data})
