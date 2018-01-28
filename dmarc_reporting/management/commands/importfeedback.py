"""django-admin command to import aggregated feedback reports"""
from django.core.management.base import BaseCommand

from dmarc_reporting.ingest.feedback import import_feedback_report


class Command(BaseCommand):
    """Import aggregated feedback reports"""

    help = "Import aggregated feedback reports"

    def add_arguments(self, parser):
        parser.add_argument(
            'xml_file',
            help="XML report to import"
        )

    def handle(self, *args, **options):
        with open(options['xml_file']) as f_xml:
            import_feedback_report(f_xml.read())
