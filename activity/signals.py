from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .utils import log_activity


def register_activity_signals(model, event_type, entity_name, extra_fields=None):
    """
    Call this once per model to auto-wire pre_save, post_save, post_delete.
    extra_fields: list of field names to include in metadata e.g. ['title', 'client_id']
    """

    @receiver(pre_save, sender=model, weak=False)
    def handle_pre_save(sender, instance, **kwargs):
        if instance.pk:
            instance._old_data = sender.objects.filter(pk=instance.pk).values().first()
        else:
            instance._old_data = None

    @receiver(post_save, sender=model, weak=False)
    def handle_post_save(sender, instance, created, **kwargs):
        old = getattr(instance, '_old_data', None)

        # build extra metadata from specified fields
        metadata = {}
        if extra_fields:
            for field in extra_fields:
                metadata[field] = str(getattr(instance, field, None))

        # find what changed
        if not created and old:
            changes = {}
            for field in instance._meta.fields:
                new_val = str(getattr(instance, field.attname, None))
                old_val = str(old.get(field.attname))
                if new_val != old_val:
                    changes[field.name] = {"old": old_val, "new": new_val}
            if changes:
                metadata["changes"] = changes

        log_activity(
            event_type=event_type,
            action_type="created" if created else "updated",
            entity_name=entity_name,
            entity_id=instance.pk,
            extra_metadata=metadata,
        )

    @receiver(post_delete, sender=model, weak=False)
    def handle_post_delete(sender, instance, **kwargs):
        metadata = {}
        if extra_fields:
            for field in extra_fields:
                metadata[field] = str(getattr(instance, field, None))

        log_activity(
            event_type=event_type,
            action_type="deleted",
            entity_name=entity_name,
            entity_id=instance.pk,
            extra_metadata=metadata,
        )

def register_all():
    from jobs.models import Job, Applications

    register_activity_signals(
        model=Job,
        event_type="marketplace",
        entity_name="job",
        extra_fields=["title", "description", "client_id"]
    )
    register_activity_signals(
        model=Applications,
        event_type="marketplace",
        entity_name="application",
        extra_fields=["job_id", "freelancer_id", "cover_letter"]
    )