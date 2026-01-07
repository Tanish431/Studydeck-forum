from django.core.management.base import BaseCommand
from courses.models import Course
from django.utils.text import slugify

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        courses = [
            ("CS F111", "Computer Programming", "Computer Science"),
            ("MATH F101", "Multivariable Calculus", "Mathematics"),
            ("BIO F101", "Introduction to Biology", "Biology"),
        ]

        for code, title, dept in courses:
            obj, created = Course.objects.get_or_create(
                code=code,
                defaults={"title": title, "department": dept, "slug": slugify(code)}
            )
            if created:
                self.stdout.write(f"Written Successfully")
            else:
                self.stdout.write(f"{code} already exists")
