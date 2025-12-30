from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.category_list, name="category_list"),
    path("thread/<int:pk>/", views.thread_detail, name="thread_detail"),
    path("thread/<int:thread_id>/reply/", views.reply_create, name="reply_create"),
    path("reply/<int:reply_id>/delete/", views.reply_delete, name="reply_delete"),
    path("thread/<int:thread_id>/like/", views.toggle_thread_like, name="thread_like"),
    path("reply/<int:reply_id>/like/", views.toggle_reply_like, name="reply_like"),
    path("thread/<int:pk>/report/", views.report_thread, name="report_thread"),
    path("reply/<int:pk>/report/", views.report_reply, name="report_reply"),
    path("reports/", views.report_list, name="report_list"),
    path("thread/<int:pk>/lock/", views.toggle_thread_lock, name="thread_lock"),
    path("tags/<slug:slug>/", views.tag_threads, name="tag_threads"),
    path("search/", views.search_threads, name="search_threads"),
    
    path("<slug:slug>/", views.thread_list, name="thread_list"),
    path("<slug:slug>/new/", views.thread_create, name="thread_create"),
]
