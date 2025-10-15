from django.urls import path

from . import views


urlpatterns = [
    # ex: /polls/
    path("", views.HomeView.as_view(), name="home"),
    path("create-blog/", views.CreateBlogView.as_view(), name="create-blog"),
    path('blog-detail/<int:blog_id>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blog-like/<int:blog_id>/', views.BlogLikeView.as_view(), name='blog-like'),
    path('comment-like/<int:comment_id>/', views.CommentLikeView.as_view(), name='comment-like'),
    path('blog-bookmark/<int:blog_id>/', views.BlogBookmarkToggleView.as_view(), name='blog-bookmark'),
    path("report/<int:blog_id>/", views.ReportBlogView.as_view(), name="report_blog"),
    path("delete-blog/<int:blog_id>/", views.DeleteBlogView.as_view(), name="delete-blog"),
    path("edit-blog/<int:blog_id>/", views.EditBlogView.as_view(), name="edit-blog"),
    path('category-detail/<str:name>/', views.CategoryDetailView.as_view(), name='category-detail'),
    # path('tag-detail/<int:tag_id>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('category-detail/<str:name>/<int:tag_id>/',  views.CategoryDetailView.as_view(), name='category-detail-tag'),
]