from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0009_thread_course"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        )
    ]
