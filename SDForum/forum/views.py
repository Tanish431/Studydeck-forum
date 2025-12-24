from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import Category, Thread, Reply, ThreadLike, ReplyLike, Report, Tag

def category_list(request):
    categories = Category.objects.all()
    return render(request, "forum/category_list.html", {
        "categories": categories
    })

def thread_list(request, slug):
    category = get_object_or_404(Category, slug = slug)
    threads = category.threads.select_related("author") # type: ignore

    paginator = Paginator(threads, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "forum/thread_list.html", {
        "category":category,
        "page_obj":page_obj,
    })

def thread_detail(request, pk):
    thread = get_object_or_404(
        Thread.objects.select_related("author", "category"),
        pk = pk
    )
    replies = thread.replies.select_related("author") # type: ignore

    user_thread_like = None
    if request.user.is_authenticated:
        user_thread_like = thread.likes.filter(user=request.user).exists()

    return render(request, "forum/thread_detail.html", {
        "thread": thread,
        "replies": replies,
        "user_thread_like": user_thread_like,
    })

@login_required
def thread_create(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        tag_names = request.POST.get("tags", "")

        if title and content:
            thread = Thread.objects.create(
                category = category,
                author = request.user,
                title = title,
                content = content
            )
            for name in tag_names.split(","):
                name = name.strip().lower()
                if name:
                    tag, _ = Tag.objects.get_or_create(
                        name=name,
                        defaults={"slug": name.replace(" ", "-")}
                    )
                    thread.tags.add(tag)
            return redirect("forum:thread_list", slug=category.slug)
    return render (request, "forum/thread_create.html", {
        "category":category
    })

@login_required
def reply_create(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if thread.is_locked:
        return HttpResponseForbidden("Thread is locked.")
    
    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            Reply.objects.create(
                thread = thread,
                author = request.user,
                content = content
            )
    return redirect("forum:thread_detail", pk = thread.pk)

@login_required
def reply_delete(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)

    profile = getattr(request.user, "profile", None)
    is_moderator = profile.is_moderator if profile else False

    if reply.author != request.user and not is_moderator:
        return HttpResponseForbidden("Not allowed")
    
    reply.is_deleted = True
    reply.save()

    return redirect("forum:thread_detail", pk=reply.thread.pk)

@login_required
def toggle_thread_like(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)

    like, created = ThreadLike.objects.get_or_create(
        thread=thread,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect("forum:thread_detail", pk=thread.pk)

@login_required
def toggle_reply_like(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)

    like, created = ReplyLike.objects.get_or_create(
        reply=reply,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect("forum:thread_detail", pk=reply.thread.pk)

@login_required
def report_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    if request.method == "POST":
        reason = request.POST.get("reason")
        if reason:
            Report.objects.create(
                reporter=request.user,
                thread=thread,
                reason=reason
            )
            return redirect("forum:thread_detail", pk=thread.pk)

    return render(request, "forum/report_form.html", {
        "target": thread,
        "type": "thread",
    })

@login_required
def report_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)

    if request.method == "POST":
        reason = request.POST.get("reason")
        if reason:
            Report.objects.create(
                reporter=request.user,
                reply=reply,
                reason=reason
            )
            return redirect("forum:thread_detail", pk=reply.thread.pk)

    return render(request, "forum/report_form.html", {
        "target": reply,
        "type": "reply",
    })

@login_required
def report_list(request):
    profile = getattr(request.user, "profile", None)
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden()

    reports = Report.objects.filter(status="PENDING")

    return render(request, "forum/report_list.html", {
        "reports": reports
    })

@login_required
def toggle_thread_lock(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    profile = getattr(request.user, "profile", None)
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden("Not allowed")

    thread.is_locked = not thread.is_locked
    thread.save()

    return redirect("forum:thread_detail", pk=thread.pk)

def tag_threads(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    threads = tag.threads.select_related("author", "category")

    return render(request, "forum/tag_threads.html", {
        "tag": tag,
        "threads": threads,
    })

