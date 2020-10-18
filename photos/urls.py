from django.urls import path

from . import views

app_name = "photos"

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("", views.index, name='index'),
    path('feed', views.FeedView.as_view(), name='feed'),
    path("user/<int:pk>", views.UserView.as_view(), name="user"),
    path("search", views.SearchView.as_view(), name="search"),

    path("post", views.CreatePost.as_view(), name='create_post'),
    path("post/<int:pk>", views.PostView.as_view(), name="post"),
    path("post/<int:pk>/edit", views.UpdatePost.as_view(), name='update_post'),
    path("post/<int:pk>/delete", views.DeletePost.as_view(), name='delete_post'),

    path("post/<int:post_pk>/like", views.like, name='like'),
    path("post/<int:post_pk>/dislike", views.dislike, name='dislike'),

    path("post/<int:post_pk>/comment",
         views.CreateComment.as_view(), name='create_comment'),
    path("comment/<int:pk>/edit",
         views.UpdateComment.as_view(), name='update_comment'),
    path("comment/<int:pk>/delete",
         views.DeleteComment.as_view(), name='delete_comment'),
]
