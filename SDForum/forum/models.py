from django.db import models
from django.conf import settings
from courses.models import Course

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Thread(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="threads"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="threads"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="threads",
        blank=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="threads"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    is_locked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
class Reply(models.Model):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "replies"
    )

    content = models.TextField()

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Reply by {self.author} on {self.thread}"
    
class ThreadLike(models.Model):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="thread_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("thread", "user")

    def __str__(self):
        return f"{self.user} likes {self.thread}"

class ReplyLike(models.Model):
    reply = models.ForeignKey(
        Reply,
        on_delete = models.CASCADE,
        related_name = "likes"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reply_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("reply", "user")
    
    def __str__(self):return f"{self.user} likes reply {self.reply.pk}"

class Report(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RESOLVED", "Resolved")
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_made"
    )

    thread = models.ForeignKey(
        Thread,
        on_delete = models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    reply = models.ForeignKey(
        Reply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.thread or self.reply
        return f"Report by {self.reporter} on {target}"

class Mention(models.Model):
    mentioned_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mentions"
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mentions"
    )
    reply = models.ForeignKey(
        Reply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mentions"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.thread or self.reply
        return f"{self.mentioned_user} mentioned in {target}"