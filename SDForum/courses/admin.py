from django.contrib import admin
from .models import Course, Resource

@admin.register(Course)
class CouseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department")
    search_fields = ("code", "title", "department")

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "resource_type", "course")
    list_filter = ("resource_type", "course")
    search_fields = ("title", "course")