from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from django.utils.translation import ugettext_lazy as _
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from bases.response import APIResponse
from bases.utils import paginate
from camps.models import AutoCamp, CampSite
from mypage.serializers import MyAutoCampSerializer, MyPageSerializer, ScrapCampSiteSerializer
from posts.models import EcoCarping
from posts.serializers import EcoCarpingSortSerializer


# 작업 중
class MyPageView(GenericAPIView):
    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = self.request.data
        user = self.request.user
        sort = data.get('sort')

        if sort == 'autocamp':
            # 등록 / 스크랩
            if not 'scrap' in self.request.data:
                return response.response(error_message="'scrap' field is required")
            scrap = bool(self.request.data.get('scrap', None))

            # 스크랩에서는 차박지 캠핑장 같이 보여줘야 되나???
            if scrap:
                qs = CampSite.objects.filter(bookmark=user)
                queryset = self.filter_queryset(qs)
                paginate(self, queryset)

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=ScrapCampSiteSerializer(queryset, many=True).data)
            if not scrap:
                qs = AutoCamp.objects.filter(user=user).order_by('-created_at')
                queryset = self.filter_queryset(qs)
                paginate(self, queryset)

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=MyAutoCampSerializer(queryset, many=True).data)

        # if sort == 'post':
        #     # 발행 / 구매 / 좋아요
        #
        # if sort == 'share':
        #     # 마이 / 좋아요

        if sort == 'eco':
            # 마이 / 좋아요
            if not 'like' in self.request.data:
                return response.response(error_message="'like' field is required")
            like = bool(self.request.data.get('like', None))

            if like:
                qs = EcoCarping.objects.filter(like=user).order_by('-created_at')
            if not like:
                qs = EcoCarping.objects.filter(user=user).order_by('-created_at')
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=EcoCarpingSortSerializer(queryset, many=True).data)

        else:
            return response.response(error_message="INVALID_SORT - choices are <recent, distance, popular>")

    @swagger_auto_schema(
        operation_id=_("Sort MyPage lists(autocamp/post/share/eco)"),
        operation_description=_("마이페이지를 정렬합니다."),
        request_body=MyPageSerializer,
        tags=[_("mypage"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)
