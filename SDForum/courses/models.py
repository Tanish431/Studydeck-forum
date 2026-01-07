from django.db import models
from django.utils.text import slugify

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)
    department = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title}"
    
class Resource(models.Model):
    RESOURCE_TYPES = [
        ("PDF", "PDF"),
        ("VIDEO", "Video"),
        ("LINK", "Link"),
    ]

    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    link = models.URLField()
    course = models.ForeignKey(
            Course, 
            on_delete= models.CASCADE,
            related_name = "resources",
            null=True,
            blank=True
        )

    def __str__(self):
        return self.title