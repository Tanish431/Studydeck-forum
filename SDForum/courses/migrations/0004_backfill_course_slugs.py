# courses/migrations/000X_backfill_course_slugs.py
from django.db import migrations
from django.utils.text import slugify

def backfill_slugs(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    for course in Course.objects.all():
        if not course.slug:
            course.slug = slugify(course.code)
            course.save(update_fields=["slug"])

class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_alter_course_slug"),
    ]

    operations = [
        migrations.RunPython(backfill_slugs),
    ]
