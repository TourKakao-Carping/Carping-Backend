from django.contrib import admin
from django.utils.html import format_html

from posts.models import *

from jet.admin import CompactInline

from django.utils.translation import ugettext_lazy as _


class UserPostInfoInline(CompactInline):
    fields = ('id', 'pay_type', 'point', 'trade_fee', 'platform_fee', 'withholding_tax',
              'vat', 'final_point', 'bank', 'info', 'kakao_openchat_url', 'recommend_to', 'is_approved', 'category', 'approve_post_list', 'rejected_reason', 'unapprove_post', 'views')
    readonly_fields = fields
    model = UserPostInfo

    extra = 0

    def approve_post_list(self, obj):
        """
        1. 고객 정보 불일치
        2. 포스트 신뢰도 미충족
        3. 포스트 가격 조건 미충족
        4. 포스트 내용 및 이미지 누락
        5. 기타
        """

        if not obj.is_approved and not obj.category == CATEGORY_DEACTIVATE:
            approve_1 = f'<input type="button" value="활성화" class="default" onclick="approve({obj.pk}, 0)">'
        else:
            if obj.is_approved:
                approve_1 = _("이미 활성화된 포스트입니다.")
            else:
                approve_1 = _("이미 비활성화된 포스트입니다.")

        return format_html(approve_1)

    approve_post_list.short_description = _("카테고리별 활성화 버튼")

    def unapprove_post(self, obj):
        rejected_reason = obj.rejected_reason
        if rejected_reason == 0 and not obj.is_approved:
            unapprove_1 = f'<input type="button" value="고객 정보 불일치" class="default" onclick="approve({obj.pk}, 1)">'
            unapprove_2 = f'<input type="button" value="포스트 신뢰도 미충족" class="default" onclick="approve({obj.pk}, 2)">'
            unapprove_3 = f'<input type="button" value="포스트 가격 조건 미충족" class="default" onclick="approve({obj.pk}, 3)">'
            unapprove_4 = f'<input type="button" value="포스트 내용 및 이미지 누락" class="default" onclick="approve({obj.pk}, 4)">'
            unapprove_5 = f'<input type="button" value="기타" class="default" onclick="approve({obj.pk}, 5)">'

            return format_html(unapprove_1 + unapprove_2 + unapprove_3 + unapprove_4 + unapprove_5)

        if obj.is_approved:
            return _("이미 활성화된 포스트입니다.")
        else:
            return _("이미 비활성화된 포스트입니다.")

    unapprove_post.short_description = _("비활성화 버튼")


@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    change_form_template = 'admin/custom_change_form.html'
    inlines = (UserPostInfoInline, )
    search_fields = ('title', 'id')
    list_display = ('post_title',)
    readonly_fields = ('title', 'thumbnail', 'sub_title1', 'text1', 'image1', 'sub_title2', 'text2', 'image2',
                       'sub_title3', 'text3', 'image3', 'sub_title4', 'text4', 'image4', 'sub_title5', 'text5', 'image5', 'approved_user',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj):
        return super().get_readonly_fields(request, obj=obj)

    def post_title(self, obj):
        post_name = f"{obj.pk}. {obj.title}"

        userpost = obj.userpostinfo_set.get()
        if userpost.is_approved:
            post_name += f" | 승인"
        elif not userpost.rejected_reason == 0:
            post_name += f" | 거절"
        else:
            post_name += f" | 미승인"

        return post_name


# admin.site.register(Post)
# admin.site.register(EcoCarping)
# admin.site.register(Share)
# admin.site.register(Region)
# admin.site.register(Store)
# admin.site.register(UserPostInfo, PostInfoAdmin)
# admin.site.register(UserPost, PostAdmin)
# admin.site.register(UserPostPaymentRequest)
