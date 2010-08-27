from django.core.management.base import BaseCommand, CommandError

"""
note: crontab can take environment vars before tab, so
PYTHONPATH=/Users/derek/dev_django:/Users/derek/dev_django/shared_apps:/Users/derek/dev_django/external_apps
should work
"""
class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'
    # option_list = BaseCommand.option_list + (
    #     make_option('--delete',
    #         action='store_true',
    #         dest='delete',
    #         default=False,
    #         help='Delete poll instead of closing it'),
    #     )

    def handle(self, *args, **options):
        """args is tuple of strings following"""
        self.stdout.write('%s\n' % str(args))
        self.stdout.write('%s\n' % str(options))
        self.stdout.write('Successfully done it\n')
