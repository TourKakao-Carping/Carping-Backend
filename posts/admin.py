from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from posts.models import *

from jet.admin import CompactInline

from django.utils.translation import ugettext_lazy as _


class UserPostInfoInline(CompactInline):
    model = UserPostInfo
    readonly_fields = ('id', 'category', 'pay_type', 'point', 'trade_fee', 'platform_fee', 'withholding_tax',
                       'vat', 'final_point', 'bank', 'info', 'kakao_openchat_url', 'recommend_to', 'check_approved', 'approve_post', 'views')

    extra = 0

    def check_approved(self, obj):
        if obj.is_approved:
            return _("승인")
        else:
            return _("미승인")
    # def has_add_permission(self, request: HttpRequest, obj) -> bool:
    #     return False

    # def has_change_permission(self, request: HttpRequest, obj):

    #     return False

    def approve_post(self, obj):
        # approve = u'<input type="hidden" name="approve" value="1" id="form_action"><input type="button" value="활성화" class="default" name="approve_button" onclick="formSubmit(\'success\')">'
        # unapprove = u'<input type="hidden" name="action" value="action" id="form_action"><input type="button" value="비활성화" class="default" name="KYC_complete" onclick="formSubmit(\'success\')">'

        approve = '<input type="button" value="승인"  name="_customaction" onclick="location.href=\'{% url \'customeroverview\' %}\'"'
        return format_html(approve)

    approve_post.short_description = _("승인 여부")


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
