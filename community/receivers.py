from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Completed
from django.utils import timezone


@receiver(post_save, sender=Completed)
def create_get_completedcount(sender, instance, created, **kwargs):
    today = timezone.now().date()
    if created:
        completed = Completed.objects.filter(
            writer=instance.writer, created_at__date=today
        )
        if completed.count() == 1:
            instance.writer.profile.completed_cnt += 1
            instance.writer.profile.save()


@receiver(pre_delete, sender=Completed)
def delete_get_completedcount(sender, instance, **kwargs):
    if instance.created_at.month == timezone.now().month:
        completed = Completed.objects.filter(
            writer=instance.writer, created_at__date=instance.created_at.date()
        )
        if completed.count() == 1:
            instance.writer.profile.completed_cnt -= 1
            instance.writer.profile.save()
