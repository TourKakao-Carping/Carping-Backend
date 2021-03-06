from bases.email import send_email
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from dateutil.relativedelta import relativedelta
from django.http.response import JsonResponse
from rest_framework.exceptions import PermissionDenied
from posts.messages import ALREADY_DEACTIVATED
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.models import Profile
import datetime
from django.db import transaction

from bases.fee import compute_final
from comments.serializers import ReviewSerializer
from posts.constants import A_TO_Z_LIST_NUM, CATEGORY_DEACTIVATE, CATEGORY_TO_STR, POST_INFO_CATEGORY_LIST_NUM
from posts.permissions import AuthorOnlyAccessPermission, UserPostAccessPermission

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.db.models import Count, F, Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from bases.payment import KakaoPayClient
from bases.serializers import MessageSerializer
from posts.models import EcoCarping, Post, Share, Region, Store, UserPost, UserPostInfo
from posts.serializers import AutoCampPostForWeekendSerializer, EcoCarpingSortSerializer, PostLikeSerializer, \
    ShareCompleteSerializer, ShareSortSerializer, SigunguSearchSerializer, DongSearchSerializer, StoreSerializer, \
    UserPostAddProfileSerializer, UserPostInfoDetailSerializer, UserPostListSerializer, UserPostDetailSerializer, \
    UserPostMoreReviewSerializer, UserPostCreateSerializer, PreUserPostCreateSerializer, ComputeFeeSerializer

from bases.utils import check_data_key, check_str_digit, paginate
from bases.response import APIResponse


class GetAutoCampPostForWeekend(GenericAPIView):
    """
    ???????????? ??????????????? ?????????
    ?????? ????????? ??? ???????????? ?????? ??? ????????? ???????????? ????????????
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
        response = APIResponse(success=False, code=400)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=serializer.data)

    def post(self, request):
        response = APIResponse(success=False, code=400)

        data = request.data
        count = data.get('count')

        if not check_data_key(count) or not check_str_digit(count):
            return response.response(error_message='Invalid Count')

        return self.list(request)


class EcoCarpingSort(GenericAPIView):
    serializer_class = EcoCarpingSortSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = self.request.data
        sort = data.get('sort')

        if sort == 'recent':
            if not 'count' in self.request.data:
                return response.response(error_message="'count' field is required")
            count = int(self.request.data.get('count', None))

            if count == 0:
                qs = EcoCarping.objects.all().order_by('-created_at')
            elif count > 0:
                qs = EcoCarping.objects.all().order_by('-created_at')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            today_count = EcoCarping.objects.filter(
                created_at__contains=datetime.date.today()).count()
            serializer.insert(0, {"today_count": today_count})

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'popular':
            qs = EcoCarping.objects.annotate(
                like_count=Count('like')).order_by('-like_count')
            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True)

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer.data)

        else:
            return response.response(error_message="INVALID_SORT - choices are <recent, popular>")

    @swagger_auto_schema(
        operation_id=_("Sort EcoCarping(recent/distance/popular)"),
        operation_description=_("??????????????? ???????????????."),
        request_body=EcoCarpingSortSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)


class EcoLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Eco"),
        operation_description=_("???????????? ???????????? ?????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                post_to_like = EcoCarping.objects.get(
                    id=serializer.validated_data["post_to_like"])
                user.eco_like.add(post_to_like)
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Like Eco"),
        operation_description=_("???????????? ??? ???????????? ???????????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.eco_like.through.objects.filter(
                    user=user, ecocarping=serializer.validated_data["post_to_like"]).delete()
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")


# ????????????
class ShareSort(GenericAPIView):
    serializer_class = ShareSortSerializer

    def list(self, request, *args, **kwargs):
        response = APIResponse(success=False, code=400)

        data = self.request.data
        sort = data.get('sort')

        if not 'count' in self.request.data:
            return response.response(error_message="'count' field is required")
        count = int(self.request.data.get('count', None))

        today = datetime.date.today() + relativedelta(days=1)
        pre_month = today - relativedelta(months=1)

        if sort == 'recent':
            if count == 0:
                qs = Share.objects.annotate(
                    like_count=Count("like")).order_by('-created_at')
            elif count > 0:
                qs = Share.objects.annotate(like_count=Count(
                    "like")).order_by('-created_at')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            more_info = {}

            total_share = Share.objects.all().count()
            monthly_share_count = Share.objects.filter(user=request.user,
                                                       created_at__range=[pre_month, today]).count()

            more_info['total_share'] = total_share
            more_info['monthly_share_count'] = monthly_share_count

            serializer.insert(0, more_info)  # ????????? ?????? ?????? ??????

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        if sort == 'popular':
            if count == 0:
                qs = Share.objects.annotate(
                    like_count=Count("like")).order_by('-like_count')
            elif count > 0:
                qs = Share.objects.annotate(like_count=Count(
                    "like")).order_by('-like_count')[:count]

            queryset = self.filter_queryset(qs)
            paginate(self, queryset)
            serializer = self.get_serializer(
                queryset, many=True).data

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=serializer)

        else:
            return response.response(error_message="INVALID_SORT")

    @swagger_auto_schema(
        operation_id=_("Sort Share-Posts(recent/distance)"),
        operation_description=_("???????????? ???????????? ???????????????."),
        request_body=EcoCarpingSortSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request, *args, **kwargs):
        return self.list(request)


class ShareLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like Share"),
        operation_description=_("???????????? ???????????? ?????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                post_to_like = Share.objects.get(
                    id=serializer.validated_data["post_to_like"])
                user.share_like.add(post_to_like)
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Like Share"),
        operation_description=_("???????????? ??? ???????????? ???????????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.share_like.through.objects.filter(
                    user=user, share=serializer.validated_data["post_to_like"]).delete()
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")


class ShareCompleteView(APIView):
    @swagger_auto_schema(
        operation_id=_("Share Complete"),
        operation_description=_("?????? ?????? ????????? ??????"),
        request_body=ShareCompleteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        serializer = ShareCompleteSerializer(data=request.data)

        if serializer.is_valid():
            try:
                Share.objects.filter(
                    id=serializer.validated_data["share_to_complete"]).update(is_shared=True)
                data = MessageSerializer({"message": _("?????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'share_to_complete' field is required.")

    @swagger_auto_schema(
        operation_id=_("Cancel Share Complete"),
        operation_description=_("?????? ?????? ??????"),
        request_body=ShareCompleteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        serializer = ShareCompleteSerializer(data=request.data)

        if serializer.is_valid():
            try:
                Share.objects.filter(
                    id=serializer.validated_data["share_to_complete"]).update(is_shared=False)

                data = MessageSerializer({"message": _("?????? ?????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'share_to_complete' field is required.")


# ?????? ?????? api
class RegionSearchView(APIView):
    @swagger_auto_schema(
        operation_id=_("Search region in Share"),
        operation_description=_("???????????? ?????? ??????"),
        request_body=SigunguSearchSerializer,
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)

        sido = request.data.get('sido')
        sigungu = request.data.get('sigungu')

        sido_list = [_("?????????"), _("?????????"), _("????????????"), _("????????????"), _("???????????????"),
                     _("???????????????"), _("???????????????"), _("???????????????"),
                     _("???????????????"), _("?????????????????????"),
                     _("???????????????"), _("???????????????"),
                     _("????????????"), _("????????????"), _("?????????????????????"),
                     _("????????????"), _("????????????"), ]

        if 'sigungu' in request.data:
            if sigungu == "":
                qs = Region.objects.filter(sido=sido)
            else:
                qs = Region.objects.filter(sigungu=sigungu)

            data = DongSearchSerializer(qs, many=True).data

            response.success = True
            response.code = HTTP_200_OK
            return response.response(data=data)

        else:
            if sido in sido_list:
                qs = Region.objects.filter(sido=f"{sido}")
                data = SigunguSearchSerializer(qs, many=True).data

                result = []

                for i in range(len(data)):
                    if data[i] in result:
                        pass
                    else:
                        result.append(data[i])

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=result)

            else:
                return response.response(error_message="???????????? ?????????????????????.")


# ????????? ????????? ?????? api
class StoreListView(APIView):
    def get(self, request):
        response = APIResponse(success=False, code=400)

        items = Store.objects.all()

        data = StoreSerializer(items, many=True).data

        response.success = True
        response.code = HTTP_200_OK
        return response.response(data=data)


class UserPostInfoListAPIView(ListModelMixin, GenericAPIView):
    # (A?????? Z, ?????? ????????? ?????????, ????????????)
    # serializer_class = UserPostListSerializer

    def get_serializer_class(self):
        data = self.request.data

        type = int(data.get('type'))

        if type == 1:
            return UserPostAddProfileSerializer
        else:
            return UserPostListSerializer

    def get_queryset(self):
        """
        type
        1 : A?????? Z?????? ????????? (?????? 10???)
        2 : ?????? ????????? ????????? ????????? (???????????????) -> 1 : ?????? TOP3, 2 :?????? ???????????? ?????? ?????????, 3 :????????? ?????? ?????? ???, 4 : ?????? ?????? ????????????
        3 : ??? ???????????? ?????????
        """

        user = self.request.user
        data = self.request.data

        type = int(data.get('type'))

        try:
            category = int(data.get('category'))
        except TypeError:
            category = 1

        if type == 1:
            qs_type = UserPostInfo.objects.random_qs(A_TO_Z_LIST_NUM)
        elif type == 2:
            qs = UserPostInfo.objects.category_qs(
                POST_INFO_CATEGORY_LIST_NUM, user.pk)

            return qs
        else:
            qs_type = UserPostInfo.objects.filter(
                category=category).order_by('-created_at')

        qs = qs_type.like_qs(user.pk).exclude(Q(is_approved=False) |
                                              Q(category=CATEGORY_DEACTIVATE) |
                                              Q(author__is_active=False))

        return qs

    def post(self, request):
        data = request.data

        response = APIResponse(success=False, code=400)

        type = data.get('type')

        if not check_str_digit(type):
            response.code = status.HTTP_400_BAD_REQUEST
            return response.response(error_message=_("Invalid type"))

        try:
            list = super().list(request)
            response.code = 200
            response.success = True
            return response.response(data=list.data)
        except:
            return response.response(data=[])


class UserPostInfoDetailAPIView(RetrieveModelMixin, GenericAPIView):
    # queryset = UserPostInfo.objects.user_post_info_detail()
    serializer_class = UserPostInfoDetailSerializer

    def get_queryset(self):
        user = self.request.user
        pk = user.pk
        qs_info_qs = UserPostInfo.objects.all().filter(
            is_approved=True).exclude(category=CATEGORY_DEACTIVATE).annotate(title=F('user_post__title'))

        qs = qs_info_qs.like_qs(pk)

        return qs

    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        # try:
        ret = super().retrieve(request)
        response.success = True
        response.code = 200

        data = ret.data

        category = data["category"]

        same_category_qs = UserPostInfo.objects.filter(
            category=category, is_approved=True)

        random_qs = same_category_qs.random_qs(3, data["id"])

        context = {}
        context["request"] = request
        recommend_serializer = UserPostListSerializer(
            random_qs, many=True, context=context)

        data["recommend_posts"] = recommend_serializer.data

        review = data.pop('review')
        review = review[:3]
        data["review"] = review

        return response.response(data=[data])

        # except BaseException as e:
        # return response.response(error_message=str(e))


class UserPostMoreReviewAPIView(RetrieveModelMixin, GenericAPIView):
    serializer_class = ReviewSerializer

    def post(self, request, pk):
        response = APIResponse(success=False, code=400)
        sort = request.data.get('sort')
        star = {}

        try:
            user_post = UserPostInfo.objects.get(pk=pk)
            star["star1_avg"] = user_post.star1_avg()
            star["star2_avg"] = user_post.star2_avg()
            star["star3_avg"] = user_post.star3_avg()
            star["star4_avg"] = user_post.star4_avg()
            star["total_star_avg"] = user_post.total_star_avg()
            if sort == 'recent':
                review = user_post.review.order_by('-created_at')
            elif sort == 'popular':
                review = user_post.review.annotate(
                    like_count=Count("like")).order_by('-like_count')
            else:
                return response.response(error_message="INVALID SORT - choices are <recent, popular>")

            serializer = self.get_serializer(review, many=True)
            response.success = True
            response.code = 200

            return response.response(data=[star, serializer.data])

        except BaseException as e:
            return response.response(error_message=str(e))


class UserPostDetailAPIView(RetrieveModelMixin, GenericAPIView):
    queryset = UserPost.objects.all()
    serializer_class = UserPostDetailSerializer
    permission_classes = (UserPostAccessPermission, IsAuthenticated)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        try:
            ret = super().retrieve(request)
            response.success = True
            response.code = 200
            return response.response(data=[ret.data])

        except BaseException as e:
            return response.response(error_message=str(e))


class UserPostDeactivateAPIView(RetrieveModelMixin, GenericAPIView):
    queryset = UserPost.objects.all()
    permission_classes = (AuthorOnlyAccessPermission, IsAuthenticated)

    def post(self, request, pk):

        response = APIResponse(success=False, code=400)

        try:
            post = self.get_object()

            post_info = post.userpostinfo_set.get()

            if post_info.category == CATEGORY_DEACTIVATE:
                return response.response(error_message=ALREADY_DEACTIVATED)

            post_info.category = CATEGORY_DEACTIVATE
            post_info.is_approved = False

            post_info.save()

            response.success = True
            response.code = 200

            return response.response()
        except PermissionDenied as e:
            return response.response(error_message=str(e))


# ????????? ?????? API
class UserPostAdminActionAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, pk, type):
        try:
            post_info = UserPostInfo.objects.get(id=pk)

            if type == 0:
                post_info.is_approved = True
            else:
                post_info.is_approved = False
                post_info.category = CATEGORY_DEACTIVATE
                post_info.rejected_reason = type

            post_info.save(
                update_fields=['is_approved', 'category', 'rejected_reason'])

            author = post_info.author
            post_title = post_info.user_post.title
            post_category = CATEGORY_TO_STR[post_info.category]

            send_email(post_info.is_approved, type,
                       author, post_title, post_category)

            # send_email(True, type,
            #            author, post_title, post_category)
            return JsonResponse(_("???????????? ???????????? ??????????????????."), safe=False)

        except UserPostInfo.DoesNotExist:
            return JsonResponse("?????? ????????? ????????? ?????? ??? ????????????.", safe=False)

        except BaseException as e:
            print(str(e))
            return JsonResponse(str(e), safe=False)


# ?????? ?????? ????????? ?????? ??? ???????????? ????????? ???????????? & ??????????????? ??????
class PreUserPostCreateAPIView(ListModelMixin, GenericAPIView):
    serializer_class = PreUserPostCreateSerializer

    def get(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user

        pre_post = UserPostInfo.objects.filter(
            author=user).order_by('-id').first()
        serializer = self.get_serializer(pre_post)

        response.success = True
        response.code = 200
        return response.response(data=[serializer.data])


class ComputeFeeView(CreateModelMixin, GenericAPIView):
    serializer_class = ComputeFeeSerializer

    def post(self, request):
        response = APIResponse(success=False, code=400)
        data = request.data
        user = request.user

        point = data.get('point')
        if not check_data_key(point):
            return response.response(error_message="No input - check 'point' value.")

        values = compute_final(user, point)

        response.success = True
        response.code = 200
        return response.response(data=[{"trade_fee": values[0]}, {"platform_fee": values[1]},
                                       {"withholding_tax": values[2]}, {
                                           "vat": values[3]},
                                       {"final_point": values[4]}])


# ?????? ????????? ?????? ???
class UserPostCreateAPIView(CreateModelMixin, GenericAPIView):
    serializer_class = UserPostCreateSerializer

    def post(self, request):
        response = APIResponse(success=False, code=400)
        data = request.data
        user = request.user

        author_comment = data.get('author_comment')
        kakao_openchat_url = data.get('kakao_openchat_url')

        category = data.get('category')
        info = data.get('info')
        recommend_to = data.get('recommend_to')
        pay_type = data.get('pay_type')
        point = data.get('point')

        bank = data.get('bank')
        account_num = data.get('account_num')

        if not check_data_key(author_comment) or not check_data_key(kakao_openchat_url):
            return response.response(error_message="check pre-post values(author_comment, kakao_openchat_url)")

        try:
            validate = URLValidator()
            validate(kakao_openchat_url)
        except ValidationError as e:
            return response.response(error_message=str(e))

        if not check_data_key(category) or not check_data_key(info) or not check_data_key(recommend_to) \
                or not check_data_key(pay_type) or not check_data_key(point):
            return response.response(error_message="check post-info values(category, info, "
                                                   "recommend_to, pay_type, point)")

        if check_str_digit(pay_type):
            pay_type = int(pay_type)

        # ?????? ???????????? ?????? ?????? ?????? ??????
        if pay_type == 0:
            is_approved = True
        else:
            is_approved = False

        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    # UserPost ?????? ??????
                    self.perform_create(serializer)
                latest = UserPost.objects.latest('id')

                latest.approved_user.add(user)
                latest.save()

                # UserPostInfo ?????? ??????
                UserPostInfo.objects.create(author=user, user_post=latest,
                                            category=category, pay_type=pay_type,
                                            point=point, info=info,
                                            kakao_openchat_url=kakao_openchat_url,
                                            recommend_to=recommend_to,
                                            is_approved=is_approved)
                info_latest = UserPostInfo.objects.latest('id')

                if pay_type == 1:
                    if not check_data_key(bank) or not check_data_key(account_num):
                        raise Exception(
                            "check values for payment-post(bank, account_num)")

                    values = compute_final(user, point)
                    UserPostInfo.objects.filter(id=info_latest.id).update(trade_fee=values[0],
                                                                          platform_fee=values[1],
                                                                          withholding_tax=values[2],
                                                                          vat=values[3], final_point=values[4],
                                                                          bank=bank)
                    # ?????? ?????? ????????????
                    Profile.objects.filter(user=user).update(
                        account_num=account_num)

                # ????????? ?????????(?????? ??????) ????????????
                Profile.objects.filter(user=user).update(
                    author_comment=author_comment)

                response.success = True
                response.code = 200
                return response.response(data=[{"post_id": UserPost.objects.latest('id').id},
                                               {"pay_type": pay_type}])

        except Exception as e:
            return response.response(error_message=str(e))


class FreeUserPostBuyAPIView(GenericAPIView):
    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        try:
            userpost = UserPostInfo.objects.get(id=pk)
            userpost.user_post.approved_user.add(request.user)

            response.success = True
            response.code = 200
            return response.response(data=[{"message": "????????? ?????? ??????????????? 0??? ?????? ??????"}])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


class UserPostPaymentReadyAPIView(APIView):

    def post(self, request, pk):

        kakao_pay = KakaoPayClient()
        response = APIResponse(success=False, code=400)

        user = request.user

        userpost_qs = UserPost.objects.filter(id=pk)

        if not userpost_qs.exists():
            response.code = 404
            return response.response(error_message=_("UserPostInfo Not Found"))

        userpost = userpost_qs.first()

        # ??????????????? ???????????? API ??????
        success, ready_process = kakao_pay.ready(user, userpost)

        if success:
            response.success = True
            response.code = 200
            return response.response(data=[ready_process])
        else:
            return response.response(error_message=ready_process)


class UserPostLike(APIView):
    @swagger_auto_schema(
        operation_id=_("Add Like User-Post"),
        operation_description=_("????????? ?????? ???????????? ???????????? ?????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                post_to_like = UserPostInfo.objects.get(
                    id=serializer.validated_data["post_to_like"])
                user.userpost_like.add(post_to_like)
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")

    @swagger_auto_schema(
        operation_id=_("Delete Like User-Post"),
        operation_description=_("?????? ???????????? ??? ???????????? ???????????????."),
        request_body=PostLikeSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("posts"), ]
    )
    def delete(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        serializer = PostLikeSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user.userpost_like.through.objects.filter(
                    user=user, userpostinfo=serializer.validated_data["post_to_like"]).delete()
                data = MessageSerializer({"message": _("????????? ????????? ??????")}).data

                response.success = True
                response.code = HTTP_200_OK
                return response.response(data=[data])

            except Exception as e:
                response.code = status.HTTP_404_NOT_FOUND
                return response.response(error_message=str(e))
        else:
            return response.response(error_message="'post_to_like' field is required.")
