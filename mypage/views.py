from django.db.models import Count, Q
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from django.utils.translation import ugettext_lazy as _
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from accounts.models import Profile, User
from bases.response import APIResponse
from bases.s3 import S3Client
from bases.utils import paginate, check_str_digit
from camps.models import AutoCamp, CampSite
from mypage.serializers import MyAutoCampSerializer, MyPageSerializer, ScrapCampSiteSerializer, \
    MyEcoSerializer, InfoSerializer, MyShareSerializer, UserPostStatusSerializer, UserPostPayStatusSerializer
from posts.constants import CATEGORY_DEACTIVATE
from posts.models import EcoCarping, Share, UserPostInfo, UserPost, UserPostPaymentRequest


class MyPageView(GenericAPIView):
    serializer_class = ScrapCampSiteSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = request.data
        user = request.user
        sort = data.get('sort')

        if sort == 'autocamp':
            # 등록 / 스크랩
            subsort = data.get('subsort', None)

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

        if sort == 'post':
            # 발행 / 구매 / 좋아요
            subsort = data.get('subsort', None)
            buy_post = []

            if subsort == 'my':
                qs = UserPostInfo.objects.filter(author=user).exclude(
                    category=CATEGORY_DEACTIVATE).order_by('-created_at')
                serializer = UserPostStatusSerializer(qs, many=True)

            elif subsort == 'buy':
                for post in UserPost.objects.all().exclude(Q(userpostinfo__category=CATEGORY_DEACTIVATE) |
                                                           Q(userpostinfo__author=user)):
                    for i in range(len(post.approved_user.values())):
                        if user.id == post.approved_user.values()[i].get('id'):
                            buy_post.append(post.userpostinfo_set.get())
                serializer = UserPostStatusSerializer(buy_post, many=True)

            elif subsort == 'like':
                qs = UserPostInfo.objects.filter(like=user).exclude(
                    category=CATEGORY_DEACTIVATE).order_by('-created_at')
                serializer = UserPostStatusSerializer(qs, many=True)

            else:
                return response.response(error_message="INVALID_SUBSORT - choices are <my, buy, like>")

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer.data)

        if sort == 'share':
            # 마이 / 좋아요
            subsort = data.get('subsort', None)

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
            subsort = data.get('subsort', None)

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


class ProfileView(RetrieveModelMixin, APIView):
    def get_object(self, pk):
        try:
            return Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        response = APIResponse(success=False, code=400)

        profile = self.get_object(pk)
        serializer = InfoSerializer(profile)

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=[serializer.data])


class ProfileUpdateViewSet(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    serializer_class = InfoSerializer
    queryset = Profile.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Profile.objects.get(user_id=request.user.pk)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def patch(self, request, pk):
        response = APIResponse(success=False, code=400)
        my_info = Profile.objects.get(user_id=pk)
        interest = request.data.get('interest')
        username = request.data.get('username')
        bio = request.data.get('bio')
        image = request.data.get('image')

        try:
            serializer = InfoSerializer(my_info, data=request.data, partial=True)

            # 개인정보 수정 - 이름, 한줄소개, 관심키워드 변경 가능
            if not image:
                User.objects.filter(id=pk).update(username=username)
                my_info.user.profile.update(bio=bio, interest=interest)
                serializer = InfoSerializer(my_info)

                response.code = 200
                response.success = True
                return response.response(data=[serializer.data])

            # 프로필 사진 변경
            if serializer.is_valid():
                s3 = S3Client()
                if my_info.image:
                    s3.delete_file(str(my_info.image))
                    my_info.image = None
                ret = self.partial_update(request)

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
        pay_status = []

        if sort == 0:
            qs = UserPostInfo.objects.filter(author=user, is_approved=0).exclude(category=CATEGORY_DEACTIVATE)
        elif sort == 1:
            qs = UserPostInfo.objects.filter(author=user, is_approved=1).exclude(category=CATEGORY_DEACTIVATE)
        elif sort == 2:
            for post_info in UserPostInfo.objects.filter(author=user, pay_type=1).exclude(category=CATEGORY_DEACTIVATE):
                for i in range(len(UserPostPaymentRequest.objects.filter(userpost__userpostinfo=post_info, status=1))):
                    pay_status.append(UserPostPaymentRequest.objects.filter(
                        userpost__userpostinfo=post_info, status=1)[i])
            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=UserPostPayStatusSerializer(pay_status, many=True).data)

        else:
            return response.response(error_message=
                                     "INVALID_SORT - choices are <0, 1, 2>")
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
