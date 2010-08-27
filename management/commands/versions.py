from ct_template.version import commit_versions
from django.core.management.base import BaseCommand, CommandError

"""
note: crontab can take environment vars before tab, so
PYTHONPATH=/Users/derek/dev_django:/Users/derek/dev_django/shared_apps:/Users/derek/dev_django/external_apps
should work
"""
class Command(BaseCommand):
    args = '<path_to_version_files>'
    help = 'process path dir, commits *.xml, then renames all others to xml and commits. Git push to finish'
    # option_list = BaseCommand.option_list + (
    #     make_option('--delete',
    #         action='store_true',
    #         dest='delete',
    #         default=False,
    #         help='Delete poll instead of closing it'),
    #     )

    def handle(self, *args, **options):
        """args is tuple of strings following"""
        
        try:
            commit_versions(args[0])
        except IndexError:
            raise CommandError('Needs argument <path_to_version_files>')
