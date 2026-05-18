from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Doctor


@receiver(m2m_changed, sender=User.groups.through)
def create_doctor_profile(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        doctor_group = Group.objects.get(name='doctor')
        if doctor_group and doctor_group.pk in pk_set:
            Doctor.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_doctor_on_user_save(sender, instance, created, **kwargs):
    if not created:  # Only for existing users being updated
        if instance.groups.filter(name="doctor").exists():
            Doctor.objects.get_or_create(user=instance)
