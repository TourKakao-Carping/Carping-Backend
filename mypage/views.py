from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from django.utils.translation import ugettext_lazy as _
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from accounts.models import User, Profile
from bases.response import APIResponse
from bases.utils import paginate, check_str_digit
from camps.models import AutoCamp, CampSite
from mypage.serializers import MyAutoCampSerializer, MyPageSerializer, ScrapCampSiteSerializer, \
    MyEcoSerializer, InfoSerializer
from posts.models import EcoCarping


# 작업 중
class MyPageView(GenericAPIView):
    serializer_class = ScrapCampSiteSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user
        sort = data.get('sort')

        if sort == 'autocamp':
            # 등록 / 스크랩
            subsort = self.request.data.get('subsort', None)

            if subsort == 'my':
                qs = AutoCamp.objects.filter(user=user).order_by('-created_at')
                queryset = self.filter_queryset(qs)
                paginate(self, queryset)

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=MyAutoCampSerializer(queryset, many=True).data)

            elif subsort == 'scrap':
                user_lat = data.get('lat')
                user_lon = data.get('lon')

                if not check_str_digit(user_lat) or not check_str_digit(user_lon):
                    response.code = 400
                    return response.response(error_message="check lat, lon")

                qs1 = CampSite.objects.filter(bookmark=user)
                qs2 = AutoCamp.objects.filter(bookmark=user)

                serializer1 = self.get_serializer(qs1, many=True).data
                serializer2 = MyAutoCampSerializer(qs2, many=True).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[{'campsite': serializer1}, {'autocamp': serializer2}])

            else:
                return response.response(error_message="INVALID_SUBSORT - choices are <my, scrap>")

        # if sort == 'post':
        #     # 발행 / 구매 / 스크랩
        #
        # if sort == 'share':
        #     # 마이 / 좋아요

        if sort == 'eco':
            # 마이 / 좋아요
            subsort = self.request.data.get('subsort', None)

            if subsort == 'my':
                qs = EcoCarping.objects.filter(user=user).order_by('-created_at')
            elif subsort == 'like':
                qs = EcoCarping.objects.filter(like=user).order_by('-created_at')
            else:
                return response.response(error_message="INVALID_SUBSORT - choices are <my, like>")
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=MyEcoSerializer(queryset, many=True).data)

        else:
            return response.response(error_message=
                                     "INVALID_SORT - choices are <autocamp, post, share, eco>")

    @swagger_auto_schema(
        operation_id=_("Sort MyPage lists(autocamp/post/share/eco)"),
        operation_description=_("마이페이지를 정렬합니다."),
        request_body=MyPageSerializer,
        tags=[_("mypage"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)


# class MyProfileView(APIView):
#
#     def get(self, request):
#         response = APIResponse(success=False, code=400)
#         my_info = Profile.objects.get(user=request.user.id)
#         serializer = MyProfileSerializer(my_info)
#         response.code = 200
#         response.success = True
#         return response.response(data=[serializer.data])
#
#     @swagger_auto_schema(
#         operation_id=_("Change My Profile"),
#         operation_description=_("프로필을 편집합니다."),
#         request_body=MyProfileSerializer,
#         tags=[_("mypage"), ]
#     )
#     # 프로필 수정 작업 중
#     def patch(self, request):
#         response = APIResponse(success=False, code=400)
#         my_profile = Profile.objects.get(user=request.user.id)
#
#         image = self.request.data.get('image', None)
#         phone = self.request.data.get('phone', None)
#         # alarm = self.request.data.get('alarm', None)
#
#         serializer = MyProfileSerializer(my_profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             if image:
#                 my_profile.image = image
#             if phone:
#                 my_profile.phone = phone
#
#             response.code = 200
#             response.success = True
#             return response.response(data=serializer.data)
#
#         return response.response(error_message=str(serializer.errors))


class MyInfoView(APIView):

    def get(self, request):
        response = APIResponse(success=False, code=400)
        my_info = Profile.objects.get(user=request.user.id)
        serializer = InfoSerializer(my_info)
        response.code = 200
        response.success = True
        return response.response(data=serializer.data)

    @swagger_auto_schema(
        operation_id=_("Change Personal Info"),
        operation_description=_("프로필 및 개인정보를 수정합니다."),
        request_body=InfoSerializer,
        tags=[_("mypage"), ]
    )
    def patch(self, request):
        response = APIResponse(success=False, code=400)
        my_profile = Profile.objects.get(user=request.user.id)

        username = self.request.data.get('username', None)
        email = self.request.data.get('email', None)

        serializer = InfoSerializer(my_profile, data=request.data, partial=True)
        if serializer.is_valid():
            if username:
                my_profile.user.username = username
            if email:
                my_profile.user.email = email

            serializer.save()

            response.code = 200
            response.success = True
            return response.response(data=serializer.data)

        return response.response(error_message=str(serializer.errors))
