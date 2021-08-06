from django.contrib import admin
from comments.models import Review, Comment, Like, BookMark

admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(BookMark)
