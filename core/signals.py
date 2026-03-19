from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .seed import seed_initial_data


@receiver(post_migrate)
def seed_on_migrate(sender, **kwargs):
    if sender.name != 'core':
        return
    seed_initial_data()
