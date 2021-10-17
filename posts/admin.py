from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from posts.models import *

from jet.admin import CompactInline

from django.utils.translation import ugettext_lazy as _


class UserPostInfoInline(CompactInline):
    model = UserPostInfo
    readonly_fields = ('id', 'category', 'pay_type', 'point', 'trade_fee', 'platform_fee', 'withholding_tax',
                       'vat', 'final_point', 'bank', 'info', 'kakao_openchat_url', 'recommend_to', 'check_approved', 'unapprove_post', 'approve_post_list', 'views')

    extra = 0

    def check_approved(self, obj):
        if obj.is_approved:
            return _("승인")
        else:
            return _("미승인")

    def unapprove_post(self, obj):
        unapprove = f'<input type="button" value="비활성화" class="default" onclick="approve({obj.pk}, 5)">'
        return format_html(unapprove)

    unapprove_post.short_description = _("비활성화")

    def approve_post_list(self, obj):

        # 차박, 차박을 위한, 차에 맞는, 인기 TOP 3
        approve_1 = f'<input type="button" value="차박 초보" class="default" onclick="approve({obj.pk}, 1)">'
        approve_2 = f'<input type="button" value="차박을 위한" class="default" onclick="approve({obj.pk}, 2)">'
        approve_3 = f'<input type="button" value="차에 맞는" class="default" onclick="approve({obj.pk}, 3)">'
        approve_4 = f'<input type="button" value="인기 TOP3" class="default" onclick="approve({obj.pk}, 4)">'

        return format_html(approve_1 + approve_2 + approve_3 + approve_4)


@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    change_form_template = 'admin/custom_change_form.html'
    inlines = (UserPostInfoInline, )
    search_fields = ('title', 'id')
    list_display = ('post_title',)
    readonly_fields = ('title', 'thumbnail', 'sub_title1', 'text1', 'image1', 'sub_title2', 'text2', 'image2',
                       'sub_title3', 'text3', 'image3', 'sub_title4', 'text4', 'image4', 'sub_title5', 'text5', 'image5', 'approved_user',)

    def get_readonly_fields(self, request, obj):
        return super().get_readonly_fields(request, obj=obj)

    def post_title(self, obj):
        post_name = f"{obj.pk}. {obj.title}"

        userpost = obj.userpostinfo_set.get()
        if userpost.is_approved:
            post_name += f" | O"
        else:
            post_name += f" | X"

        return post_name

    def response(self, request, obj):
        print(obj)
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        # print("1")
        # if request.POST:
        #     print(request.POST)
        return super(UserPost, self).response_change(request, obj)
        # return super().response_action(request, obj)


# admin.site.register(Post)
# admin.site.register(EcoCarping)
# admin.site.register(Share)
# admin.site.register(Region)
# admin.site.register(Store)
# admin.site.register(UserPostInfo, PostInfoAdmin)
# admin.site.register(UserPost, PostAdmin)
# admin.site.register(UserPostPaymentRequest)


# @admin.register(Token)
# class AuditContractInputContents(admin.ModelAdmin):
#     search_fields = ('id' ,'symbol')
#     list_display = ('audit_contract', )
#     readonly_fields= ('request_type', 'request_user', 'functions_1',)
#     fields = ('coin', 'total_supply', 'symbol', 'request_type', 'request_user', 'contract_address')
#     inlines = [AuditContractInline, DocsInline, TestCaseInline, VulnerabilityInline, ConclusionInline]

#     def functions_1(self, obj):
#         docs = obj.docs_set.filter(type=1)
#         value = docs.values('title', 'content')
#         return value

#     def request_type(self, obj):
#         audit = obj.auditcontract_set.get()
#         return TYPE_INT_TO_STR[audit.type]

#     request_type.short_description = _("신청 타입")

#     def request_user(self, obj):
#         audit = obj.auditcontract_set.get()
#         return audit.user.username

#     request_user.short_description = _("신청 유저")


#     def audit_contract(self, obj):
#         audit_name = "Audit | "

#         audit = obj.auditcontract_set.get()


#         audit_name += f"{audit.name}"
#         return audit_name
