from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Count
from .models import Category, Thread, Reply, ThreadLike, ReplyLike, Report, Tag, Mention
from .utils import extract_mentions

def category_list(request):
    categories = Category.objects.all()
    return render(request, "forum/category_list.html", {
        "categories": categories
    })

def thread_list(request, slug):
    category = get_object_or_404(Category, slug = slug)
    sort = request.GET.get("sort", "latest")
    threads = category.threads.select_related("author") # type: ignore

    if sort == "popular":
        threads = threads.annotate(
            like_count = Count("likes")
        ).order_by("-like_count", "-created_at")

    paginator = Paginator(threads, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "forum/thread_list.html", {
        "category":category,
        "page_obj":page_obj,
        "sort":sort,
    })

def thread_detail(request, pk):
    thread = get_object_or_404(
        Thread.objects.select_related("author", "category"),
        pk = pk
    )
    replies_qs = (
        thread.replies # type: ignore
        .select_related("author")
        .filter(is_deleted=False)
    )

    paginator = Paginator(replies_qs, 10)  # 10 replies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_thread_like = False
    if request.user.is_authenticated:
        user_thread_like = thread.likes.filter(user=request.user).exists() # type: ignore

    return render(request, "forum/thread_detail.html", {
        "thread": thread,
        "page_obj": page_obj,
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
            mentioned_users = extract_mentions(content)
            for user in mentioned_users:
                if user != request.user:
                    Mention.objects.create(
                        mentioned_user=user,
                        thread=thread
                    )
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
            mentioned_users = extract_mentions(content)
            for user in mentioned_users:
                if user != request.user:
                    Mention.objects.create(
                        mentioned_user=user,
                        reply=reply
                    )
            reply_count = thread.replies.filter(is_deleted=False).count()
            last_page = (reply_count - 1) // 10 + 1

            return redirect(
                f"{reverse('forum:thread_detail', kwargs={'pk': thread.pk})}?page={last_page}"
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
        return HttpResponseForbidden("Not Allowed")

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
    threads = tag.threads.select_related("author", "category") # type: ignore

    return render(request, "forum/tag_threads.html", {
        "tag": tag,
        "threads": threads,
    })

def search_threads(request):
    query = request.GET.get("q", "").strip()
    threads = Thread.objects.filter(is_deleted=False)

    if query:
        threads = (
            threads
            .annotate(
                similarity=(
                    TrigramSimilarity("title", query) +
                    TrigramSimilarity("content", query)
                )
            )
            .filter(similarity__gt=0.2)
            .order_by("-similarity")
        )
    return render(request, "forum/search_results.html", {
        "query": query,
        "threads": threads,
    })