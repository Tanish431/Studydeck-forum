from django.core.management.base import BaseCommand
from django.utils.text import slugify
from courses.models import Course

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
                defaults={"title": title, "slug": slugify(code), "department": dept}
            )
            if created:
                self.stdout.write(f"Written Successfully")
            else:
                self.stdout.write(f"{code} already exists")
