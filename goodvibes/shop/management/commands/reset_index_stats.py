from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset PostgreSQL statistics (pg_stat_reset)."

    def handle(self, *args, **options):
        with connection.cursor() as cur:
            cur.execute("SELECT pg_stat_reset();")
        self.stdout.write(self.style.SUCCESS("pg_stat_reset() executed."))


