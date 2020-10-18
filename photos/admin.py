from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import  UserCreationForm, UserChangeForm
from .models import User, Post, Comment, Like


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ("email", "firstname", "lastname", "is_superuser")
    list_filter = ["is_superuser"]
    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["firstname", "lastname"]}),
        ("Social", {"fields": ["profile_photo",
                               "description", "website", "following"]}),
        ("Permissions", {"fields": [
         "is_superuser", "groups", "user_permissions"]}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ["wide"],
                "fields": ("email", "firstname", "lastname", "password1", "password2"),
            },
        ),
    )
    search_fields = ["email", "firstname", "lastname"]
    ordering = ["email"]
    filter_horizontal = ()


class PostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'created_timestamp',
                    'last_modified_timestamp', 'image']
    date_hierarchy = 'created_timestamp'
    list_filter = ['user',
                   'created_timestamp', "last_modified_timestamp"]
    search_fields = ['user__email', "user__firstname",
                     "user__lastname",  'content']
    autocomplete_fields = ['user']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'post',
                    'created_timestamp', 'last_modified_timestamp']
    date_hierarchy = 'created_timestamp'
    list_filter = ['user', "post",
                   'created_timestamp', "last_modified_timestamp"]
    search_fields = ['user__email', "user__firstname",
                     "user__lastname", "post__content" 'content']
    autocomplete_fields = ["user", "post"]


class LikeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'post',
                    'like', 'created_timestamp', "last_modified_timestamp"]
    list_filter = ['user', 'post', 'like',
                   'created_timestamp', "last_modified_timestamp"]
    search_fields = ['user__email', "user__firstname",
                     "user__lastname", "post__content"]
    autocomplete_fields = ["user", "post"]


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
