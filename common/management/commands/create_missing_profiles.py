from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from common.models import Profile

class Command(BaseCommand):
    help = 'Create profiles for users that do not have them'

    def handle(self, *args, **options):
        users_without_profiles = []
        total_users = User.objects.count()

        self.stdout.write(f'Checking {total_users} users for missing profiles...')

        # Find users without profiles
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                users_without_profiles.append(user)

        # Create profiles for users without them
        if users_without_profiles:
            self.stdout.write(f'Found {len(users_without_profiles)} users without profiles. Creating profiles...')
            for user in users_without_profiles:
                Profile.objects.create(user=user)
                self.stdout.write(f'Created profile for user: {user.username}')
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(users_without_profiles)} profiles.'))
        else:
            self.stdout.write(self.style.SUCCESS('All users have profiles. No action needed.'))
