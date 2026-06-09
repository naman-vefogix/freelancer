from activity.context import current_user
from activity.models import UserActivity
from .models import Job, Applications

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from activity.utils import log_activity

print("SIGNALS LOADED")


@receiver(pre_save, sender=Job)
def job_pre_save(sender, instance, **kwargs):
    if instance.pk:
        instance._old_data = Job.objects.filter(pk=instance.pk).values().first()
    else:
        instance._old_data = None

@receiver(post_save, sender=Job)
def job_post_save(sender, instance, created, **kwargs):
    if created:
        log_activity(
            event_type="marketplace",
            action_type="created",
            entity_name="job",
            entity_id=instance.id,
            extra_metadata={
                "title": instance.title,
                "description": instance.description,
                "client_id": instance.client_id,
            }
        )
    else:
        old = getattr(instance, '_old_data', {})
        log_activity(
            event_type="marketplace",
            action_type="updated",
            entity_name="job",
            entity_id=instance.id,
            extra_metadata={
                "title": instance.title,
                "old_title": old.get("title") if old else None,
            }
        )


@receiver(post_delete, sender=Job)
def job_post_delete(sender, instance, **kwargs):
    log_activity(
        event_type="marketplace",
        action_type="deleted",
        entity_name="job",
        entity_id=instance.id,
        extra_metadata={
            "title": instance.title,
            "client_id": instance.client_id,
        }
    )


@receiver(post_save, sender=Applications)
def application_post_save(sender, instance, created, **kwargs):
    if created:
        log_activity(
            event_type="marketplace",
            action_type="created",
            entity_name="application",
            entity_id=instance.id,
            extra_metadata={
                "job_id": instance.job_id,
                "job_title": instance.job.title,
                "freelancer_id": instance.freelancer_id,
                "cover_letter": instance.cover_letter,
            }
        )