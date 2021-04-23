from django.contrib import admin

from main.models import Comment, Like
from .models import MyUser

admin.site.register(MyUser)
admin.site.register(Comment)
admin.site.register(Like)