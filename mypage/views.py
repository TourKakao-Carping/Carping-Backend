from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from django.utils.translation import ugettext_lazy as _
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from accounts.models import Profile, User
from bases.response import APIResponse
from bases.s3 import S3Client
from bases.utils import paginate, check_str_digit
from camps.models import AutoCamp, CampSite
from mypage.serializers import MyAutoCampSerializer, MyPageSerializer, ScrapCampSiteSerializer, \
    MyEcoSerializer, InfoSerializer, MyShareSerializer, UserPostStatusSerializer
from posts.models import EcoCarping, Share, UserPostInfo


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
                qs = AutoCamp.objects.annotate(bookmark_count=Count("bookmark")).filter(
                    user=user).order_by('-created_at')
                queryset = self.filter_queryset(qs)
                paginate(self, queryset)

                serializer = MyAutoCampSerializer(qs, many=True)

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=serializer.data)

            elif subsort == 'scrap':
                user_lat = data.get('lat')
                user_lon = data.get('lon')

                if not check_str_digit(user_lat) or not check_str_digit(user_lon):
                    response.code = 400
                    return response.response(error_message="check lat, lon")

                qs1 = CampSite.objects.annotate(bookmark_count=Count("bookmark")).filter(bookmark=user)
                qs2 = AutoCamp.objects.annotate(bookmark_count=Count("bookmark")).filter(bookmark=user)

                serializer1 = self.get_serializer(qs1, many=True).data
                serializer2 = MyAutoCampSerializer(qs2, many=True).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[{'campsite': serializer1}, {'autocamp': serializer2}])

            else:
                return response.response(error_message="INVALID_SUBSORT - choices are <my, scrap>")

        # if sort == 'post':
        #     # 발행 / 구매 / 스크랩

        if sort == 'share':
            # 마이 / 좋아요
            subsort = self.request.data.get('subsort', None)

            if subsort == 'my':
                qs = Share.objects.annotate(
                    like_count=Count("like")).filter(user=user).order_by('-created_at')
            elif subsort == 'like':
                qs = Share.objects.annotate(
                    like_count=Count("like")).filter(like=user).order_by('-created_at')
            else:
                return response.response(error_message="INVALID_SUBSORT - choices are <my, like>")
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=MyShareSerializer(queryset, many=True).data)

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


class ProfileUpdateViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = InfoSerializer
    queryset = Profile.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        try:
            ret = super(ProfileUpdateViewSet, self).retrieve(request)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=[ret.data])

        except Exception as e:
            response.success = False
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))

    def partial_update(self, request, pk=None, *args, **kwargs):
        response = APIResponse(success=False, code=400)
        my_info = Profile.objects.get(id=request.user.id)
        interest = request.data.get('interest')
        username = request.data.get('username')
        bio = request.data.get('bio')
        image = request.data.get('image')

        try:
            serializer = InfoSerializer(my_info, data=request.data, partial=True)

            # 개인정보 수정 - 이름, 한줄소개, 관심키워드 변경 가능
            if not image:
                User.objects.filter(id=my_info.user.id).update(username=username)
                my_info.user.profile.update(bio=bio, interest=interest)
                ret = super(ProfileUpdateViewSet, self).retrieve(request)

                response.code = 200
                response.success = True
                return response.response(data=[ret.data])

            # 프로필 사진 변경
            if serializer.is_valid():
                s3 = S3Client()
                obj = self.get_object()
                if obj.image:
                    s3.delete_file(str(obj.image))
                    obj.image = None
                ret = super(ProfileUpdateViewSet, self).partial_update(request)

                response.code = 200
                response.success = True
                return response.response(data=[ret.data])

        except Exception as e:
            response.code = HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


class PostStatusView(GenericAPIView):
    serializer_class = UserPostStatusSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user
        sort = data.get('sort')

        if sort == 0:
            qs = UserPostInfo.objects.filter(author=user, is_approved=0)
        elif sort == 1:
            qs = UserPostInfo.objects.filter(author=user, is_approved=1)
        else:
            return response.response(error_message=
                                     "INVALID_SORT - choices are <0, 1>")
        queryset = self.filter_queryset(qs)
        paginate(self, queryset)

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=self.get_serializer(queryset, many=True).data)

    @swagger_auto_schema(
        operation_id=_("User-Post Status"),
        operation_description=_("포스트 현황"),
        request_body=MyPageSerializer,
        tags=[_("mypage"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)
