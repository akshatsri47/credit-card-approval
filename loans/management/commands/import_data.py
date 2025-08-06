# loans/management/commands/import_data.py
from django.core.management.base import BaseCommand
from loans.tasks import import_customers_and_loans

class Command(BaseCommand):
    help = "Trigger background import via Celery"

    def handle(self, *args, **options):
        result = import_customers_and_loans.delay()
        self.stdout.write(self.style.SUCCESS(
            f"Enqueued import task (Celery id: {result.id})"
        ))
