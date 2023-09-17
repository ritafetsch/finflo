from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from .models import GroupPermission

# Assign default permissions to groups
@receiver(post_save, sender=Group)
def assign_default_permissions(sender, instance, created, **kwargs):
    if created:
        default_permissions = Permission.objects.filter(codename__startswith='default_group_permission_')
        for permission in default_permissions:
            GroupPermission.objects.create(group=instance, permission=permission)
