from django.contrib import admin
from posts.models import *


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


class PostInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_post']


admin.site.register(Post)
admin.site.register(EcoCarping)
admin.site.register(Share)
admin.site.register(Region)
admin.site.register(Store)
admin.site.register(UserPostInfo, PostInfoAdmin)
admin.site.register(UserPost, PostAdmin)
admin.site.register(UserPostPaymentRequest)
