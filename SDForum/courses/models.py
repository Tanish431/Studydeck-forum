from django.db import models

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=30)
    department = models.CharField(max_length=100)

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