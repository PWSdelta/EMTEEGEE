"""
Empty migration file to satisfy Django's migration system.
Since we're using MongoDB, we don't need actual migrations.
"""

from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
