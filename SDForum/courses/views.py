from forum.models import Thread
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course

def course_detail(request, code):
    course = get_object_or_404(Course, code=code)
    threads = course.threads.filter(is_deleted=False)[:5]

    return render(request, "courses/course_detail.html", {
        "course": course,
        "threads": threads,
    })
