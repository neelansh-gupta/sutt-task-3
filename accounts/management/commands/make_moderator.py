from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Make a user a moderator or remove moderator status'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the user'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove moderator status instead of adding it'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all current moderators'
        )

    def handle(self, *args, **options):
        if options.get('list'):
            moderators = User.objects.filter(is_moderator=True)
            staff = User.objects.filter(is_staff=True, is_moderator=False)
            superusers = User.objects.filter(is_superuser=True, is_moderator=False, is_staff=False)
            
            self.stdout.write(self.style.SUCCESS('\n=== Current Moderators ==='))
            
            if moderators:
                self.stdout.write('\nExplicit Moderators (is_moderator=True):')
                for user in moderators:
                    self.stdout.write(f'  • {user.email} - {user.get_display_name()}')
            
            if staff:
                self.stdout.write('\nStaff Members (is_staff=True):')
                for user in staff:
                    self.stdout.write(f'  • {user.email} - {user.get_display_name()}')
            
            if superusers:
                self.stdout.write('\nSuperusers (is_superuser=True):')
                for user in superusers:
                    self.stdout.write(f'  • {user.email} - {user.get_display_name()}')
            
            total = moderators.count() + staff.count() + superusers.count()
            self.stdout.write(f'\nTotal users with moderation privileges: {total}')
            return

        email = options['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email "{email}" not found'))
            return
        
        if options.get('remove'):
            user.is_moderator = False
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Removed moderator status from {user.email}'
            ))
            if user.is_staff or user.is_superuser:
                self.stdout.write(self.style.WARNING(
                    f'Note: User still has moderation privileges due to is_staff={user.is_staff}, is_superuser={user.is_superuser}'
                ))
        else:
            user.is_moderator = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Made {user.email} a moderator!'
            ))
            self.stdout.write(f'   Name: {user.get_display_name()}')
            self.stdout.write(f'   Can moderate: {user.can_moderate()}')
