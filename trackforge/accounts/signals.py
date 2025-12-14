# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser

# This decorator tells Django: "Run this function after a CustomUser is saved"
@receiver(post_save, sender=CustomUser)
def assign_group_based_on_role(sender, instance, created, **kwargs):
    """
    Assign the user to a group based on their role when a new user is created.
    """
    if created:  # Only run this for newly created users
        role_to_group = {
            'admin': 'admin',
            'manager': 'manager',
            'staff': 'staff',
            'user': 'user',
        }

        # Get the group name corresponding to the user's role
        group_name = role_to_group.get(instance.role)

        if group_name:
            # Try to find the group in the database
                group = Group.objects.get(name=group_name)
                # Add the user to this group
                instance.groups.add(group)
