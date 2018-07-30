from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
import boto3

from ...utils.crawler_data import (
    full_mongo_import)


class Command(BaseCommand):
    help = 'Populate database with data from mongo'
    placeholders_dir = r'products/saleor/static/placeholders/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--withoutimages',
            action='store_true',
            dest='withoutimages',
            default=False,
            help='Don\'t create product images')
        parser.add_argument(
            '--withoutsearch',
            action='store_true',
            dest='withoutsearch',
            default=False,
            help='Don\'t update search index')

    def make_database_faster(self):
        """Sacrifice some of the safeguards of sqlite3 for speed.

        Users are not likely to run this command in a production environment.
        They are even less likely to run it in production while using sqlite3.
        """
        if 'sqlite3' in connection.settings_dict['ENGINE']:
            cursor = connection.cursor()
            cursor.execute('PRAGMA temp_store = MEMORY;')
            cursor.execute('PRAGMA synchronous = OFF;')

    def populate_search_index(self):
        if settings.ES_URL:
            call_command('search_index', '--rebuild', force=True)

    def handle(self, *args, **options):
        self.make_database_faster()

        for msg in full_mongo_import(self.placeholders_dir):
            self.stdout.write(msg)

        if not options['withoutsearch']:
            self.populate_search_index()
