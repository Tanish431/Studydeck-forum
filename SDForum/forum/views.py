from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Count
from .models import Category, Thread, Reply, ThreadLike, ReplyLike, Report, Tag, Mention
from .email_utils import send_notification_email
from .utils import extract_mentions
from courses.models import Course

#List all the categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, "forum/category_list.html", {
        "categories": categories
    })

#List threads in a category
def thread_list(request, slug):
    category = get_object_or_404(Category, slug = slug)
    sort = request.GET.get("sort", "latest")
    threads = category.threads.filter(is_deleted=False) # type: ignore

    #Sorting
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

#View thread details
def thread_detail(request, pk):
    thread = get_object_or_404(
        Thread.objects.select_related("author", "category"),
        pk = pk
    )
    if thread.is_deleted:
        return HttpResponseForbidden("Thread deleted")

    replies_qs = (
        thread.replies # type: ignore
        .select_related("author")
        .filter(is_deleted=False)
    )

    paginator = Paginator(replies_qs, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    #Check if user liked
    user_thread_like = False 
    if request.user.is_authenticated:
        user_thread_like = thread.likes.filter(user=request.user).exists() # type: ignore

    return render(request, "forum/thread_detail.html", {
        "thread": thread,
        "page_obj": page_obj,
        "user_thread_like": user_thread_like,
    })

#List all tags
def tag_list(request):
    tags = Tag.objects.all()

    return render(request, "forum/tag_list.html", {
        "tags":tags
    })

#Create a new thread
@login_required
def thread_create(request, slug):
    category = get_object_or_404(Category, slug=slug)
    courses = Course.objects.all().order_by("code")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        tag_names = request.POST.get("tags", "")
        course_id = request.POST.get("course")

        course = None
        if course_id:
            course = Course.objects.filter(id=course_id).first()
            
        if title and content:
            thread = Thread.objects.create(
                category = category,
                author = request.user,
                title = title,
                content = content,
                course=course
            )
            #Tag creation
            for name in tag_names.split(","):
                name = name.strip().lower().lstrip()
                if name:
                    tag, _ = Tag.objects.get_or_create(
                        name=name,
                        defaults={"slug": name.replace(" ", "-")}
                    )
                    thread.tags.add(tag)
            #Handling mention
            mentioned_users = extract_mentions(content)
            for user in mentioned_users:
                if user != request.user:
                    Mention.objects.create(
                        mentioned_user=user,
                        thread=thread
                    )
            emails = [
                user.email
                for user in mentioned_users
                if user != request.user and user.email
            ]
            send_notification_email(
                subject="You were mentioned on SDForum",
                message=f"You were mentioned by {request.user.username}.",
                recipients=emails,
            )
            return redirect("forum:thread_list", slug=category.slug)
    return render (request, "forum/thread_create.html", {
        "category":category,
        "courses":courses
    })

#Create a reply 
@login_required
def reply_create(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.is_locked:
        return HttpResponseForbidden("Thread is locked.")
    
    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            reply = Reply.objects.create(
                thread = thread,
                author = request.user,
                content = content
            )
            #Email notification to thread author
            if thread.author != request.user and thread.author.email:
                send_notification_email(
                    subject="New reply to your thread",
                    message=(
                        f"{request.user.username} replied to your thread:\n\n"
                        f"{thread.title}"
                    ),
                    recipients=[thread.author.email],
                )
            #Handling mention 
            mentioned_users = extract_mentions(content)
            for user in mentioned_users:
                if user != request.user:
                    Mention.objects.create(
                        mentioned_user=user,
                        reply=reply
                    )
            emails = [
                user.email
                for user in mentioned_users
                if user != request.user and user.email
            ]
            send_notification_email(
                subject="You were mentioned on SDForum",
                message=f"You were mentioned by {request.user.username}.",
                recipients=emails,
            )
            #Redirect to the last page of replies
            reply_count = thread.replies.filter(is_deleted=False).count() # type: ignore
            last_page = (reply_count - 1) // 10 + 1

            return redirect(
                f"{reverse('forum:thread_detail', kwargs={'pk': thread.pk})}?page={last_page}"
            )
    return redirect("forum:thread_detail", pk = thread.pk)

#Delete a thread
@login_required
def thread_delete(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    #Check permissions
    profile = getattr(request.user, "profile")
    is_moderator = profile.is_moderator if profile else False

    if thread.author != request.user and not is_moderator:
        return HttpResponseForbidden("Not allowed")
    
    thread.is_deleted = True
    thread.save()

    return redirect("forum:thread_list", slug=thread.category.slug)

#Delete a reply
@login_required
def reply_delete(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)

    #Check permissions
    profile = getattr(request.user, "profile")
    is_moderator = profile.is_moderator if profile else False

    if reply.author != request.user and not is_moderator:
        return HttpResponseForbidden("Not allowed")
    
    reply.is_deleted = True
    reply.save()

    return redirect("forum:thread_detail", pk=reply.thread.pk)

#Like system for a thread
@login_required
def toggle_thread_like(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)

    like, created = ThreadLike.objects.get_or_create(
        thread=thread,
        user=request.user
    )

    #Toggling like
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

#Reporting system
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

#Reporting a reply
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

#List all reports (for moderators)
@login_required
def report_list(request):
    #Check permission
    profile = getattr(request.user, "profile")
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden("Not Allowed")

    reports = Report.objects.filter(status="PENDING")

    return render(request, "forum/report_list.html", {
        "reports": reports
    })

@login_required
def resolve_report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)

    profile=getattr(request.user, "profile")
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden()
    
    if report.thread:
        report.thread.is_deleted = True
        report.thread.save()
    if report.reply:
        report.reply.is_deleted = True
        report.reply.save()
    
    report.status="RESOLVED"
    report.save()

    return redirect("forum:report_list")

@login_required
def resolve_report_safe(request, pk):
    report = get_object_or_404(Report, pk=pk)

    profile=getattr(request.user, "profile")
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden()
    
    report.status="RESOLVED"
    report.save()

    return redirect("forum:report_list")
#Locking system
@login_required
def toggle_thread_lock(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    profile = getattr(request.user, "profile")
    if not profile or not profile.is_moderator:
        return HttpResponseForbidden("Not allowed")

    thread.is_locked = not thread.is_locked
    thread.save()

    return redirect("forum:thread_detail", pk=thread.pk)

#List threads by tag
def tag_threads(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    threads = tag.threads.select_related("author", "category") # type: ignore

    return render(request, "forum/tag_threads.html", {
        "tag": tag,
        "threads": threads,
    })

#List threads by course
def course_threads(request, slug):
    course = get_object_or_404(Course, slug=slug)
    threads = course.threads.filter(is_deleted=False)
    
    return HttpResponse("COURSE VIEW HIT")


def course_list(request):
    courses = Course.objects.all().order_by("code")
    return render(request, "forum/course_list.html", {
        "courses": courses
    })
#Search system
def search_threads(request):
    query = request.GET.get("q", "").strip()
    threads = Thread.objects.filter(is_deleted=False)

    if query:
        threads = (
            threads.annotate(
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