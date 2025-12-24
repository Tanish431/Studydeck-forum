from django.contrib import admin
from .models import Category, Thread, Reply, Report, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "created_at", "is_locked")
    list_filter = ("category", "is_locked")
    search_fields = ("title", "content")
    filter_horizontal = ("tags",)

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("thread", "author", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("content",)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "thread", "reply", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reason",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)