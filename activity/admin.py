# from django.contrib import admin

# from activity.models import UserActivity
# from django.contrib.auth import get_user_model
# import json

# # Register your models here.

# class ActivityDBAdminMixin:
#     using = "activity"

#     def get_queryset(self, request):
#         return super().get_queryset(request).using(self.using)

#     def save_model(self, request, obj, form, change):
#         obj.save(using=self.using)

#     def delete_model(self, request, obj):
#         obj.delete(using=self.using)


# User = get_user_model() 
# @admin.register(UserActivity)
# class UserActivityAdmin(admin.ModelAdmin):

#     list_display = (
#         "id",
#         "user_name",
#         "event_type",
#         "action_type",
#         "entity_name",
#         "created_at",
#     )

#     list_filter = (
#         "event_type",
#         "action_type",
#         "created_at",
#     )

#     search_fields = (
#         "user_id",
#         "entity_name",
#     )

#     readonly_fields = (
#         "user_id",
#         "event_type",
#         "action_type",
#         "entity_name",
#         "formatted_metadata",
#         "created_at",
#     )

#     ordering = ("-created_at",)

#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False
    
    
#     @admin.display(description="User")
#     def user_name(self, obj):
#         try:
#             return User.objects.get(id=obj.user_id).email
#         except User.DoesNotExist:
#             return f"Deleted User ({obj.user_id})"
        
#     @admin.display(description="Metadata")
#     def formatted_metadata(self, obj):
#         return json.dumps(obj.metadata, indent=2)
    
import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html, format_html_join

from activity.models import UserActivity

User = get_user_model()


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def prettify_key(key):
    """'response_time_ms' -> 'Response Time Ms'"""
    return str(key).replace("_", " ").replace(",", ", ").strip().title()


def fmt_val(value):
    if value in (None, "None", ""):
        return "—"
    return str(value)


NOISE_KEYS = {
    "ip", "user_agent", "device_type", "method", "path",
    "status_code", "response_time_ms", "changes",
}


def make_case_insensitive_filter(field_name, title):
    """Logs come from multiple sources and aren't always consistent about
    casing ('marketplace' vs 'Payments' vs 'User'). This filter buckets
    values case-insensitively so the dropdown doesn't fragment as new event
    types/casings get added over time."""

    class _Filter(admin.SimpleListFilter):
        parameter_name = field_name

        def lookups(self, request, model_admin):
            qs = model_admin.get_queryset(request)
            values = qs.values_list(field_name, flat=True)
            seen = {}
            for v in values:
                if not v:
                    continue
                seen.setdefault(v.lower(), v)
            return sorted((k, v.title()) for k, v in seen.items())

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(**{f"{field_name}__iexact": self.value()})
            return queryset

    _Filter.title = title
    return _Filter


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

class ActivityDBAdminMixin:
    using = "activity"

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)


@admin.register(UserActivity)
class UserActivityAdmin(ActivityDBAdminMixin, admin.ModelAdmin):

    # ---- list view -------------------------------------------------------

    list_display = (
        "id",
        "created_at",
        "user_display",
        "event_badge",
        "action_badge",
        "entity_display",
        "summary",
    )

    list_filter = (
        make_case_insensitive_filter("event_type", "Event Type"),
        make_case_insensitive_filter("action_type", "Action Type"),
        "created_at",
    )

    search_fields = (
        "user_id",
        "entity_name",
        "=entity_id",
    )

    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ("-created_at",)

    # ---- detail (read-only) view ------------------------------------------

    readonly_fields = (
        "created_at",
        "user_display",
        "event_badge",
        "action_badge",
        "entity_display",
        "changes_table",
        "metadata_table",
        "raw_metadata",
    )

    fieldsets = (
        ("Event", {
            "fields": ("created_at", "user_display", "event_badge", "action_badge", "entity_display"),
        }),
        ("What Changed", {
            "fields": ("changes_table",),
        }),
        ("Other Metadata", {
            "fields": ("metadata_table",),
        }),
        ("Raw Data", {
            "fields": ("raw_metadata",),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # ---- user resolution (batched per page to avoid N+1) ------------------

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self._user_cache = {}
        return qs

    def _get_user_email(self, user_id):
        if user_id is None:
            return None
        if user_id not in self._user_cache:
            try:
                self._user_cache[user_id] = User.objects.get(id=user_id).email
            except User.DoesNotExist:
                self._user_cache[user_id] = None
        return self._user_cache[user_id]

    @admin.display(description="User")
    def user_display(self, obj):
        if obj.user_id is None:
            return "System"
        email = self._get_user_email(obj.user_id)
        if email is None:
            return f"Deleted user (#{obj.user_id})"
        return email

    # ---- event / action -------------------------------------------------

    @admin.display(description="Event")
    def event_badge(self, obj):
        return (obj.event_type or "-").title()

    @admin.display(description="Action")
    def action_badge(self, obj):
        return (obj.action_type or "-").title()

    @admin.display(description="Entity")
    def entity_display(self, obj):
        entity_id = getattr(obj, "entity_id", None)
        if entity_id:
            return format_html("<strong>{}</strong> #{}", obj.entity_name or "-", entity_id)
        return obj.entity_name or "-"

    # ---- summary column (list view) ------------------------------------

    @admin.display(description="Summary")
    def summary(self, obj):
        metadata = obj.metadata if isinstance(obj.metadata, dict) else {}

        changes = metadata.get("changes")
        if isinstance(changes, dict) and changes:
            fields = list(changes.keys())
            shown = ", ".join(prettify_key(f) for f in fields[:3])
            more = f" +{len(fields) - 3} more" if len(fields) > 3 else ""
            return f"Changed: {shown}{more}"

        if metadata.get("path"):
            method = metadata.get("method", "")
            status = metadata.get("status_code", "")
            rt = metadata.get("response_time_ms")
            rt_s = f" • {rt}ms" if rt is not None else ""
            return f"{method} {metadata.get('path')} → {status}{rt_s}"

        extra = {k: v for k, v in metadata.items() if k not in NOISE_KEYS}
        if extra:
            parts = [f"{prettify_key(k)}: {fmt_val(v)}" for k, v in list(extra.items())[:2]]
            return ", ".join(parts)

        return "-"

    # ---- detail view tables ------------------------------------------

    @admin.display(description="Changes")
    def changes_table(self, obj):
        metadata = obj.metadata if isinstance(obj.metadata, dict) else {}
        changes = metadata.get("changes")
        if not isinstance(changes, dict) or not changes:
            return "No field changes recorded"

        def row_values(field, val):
            if isinstance(val, dict):
                old, new = val.get("old"), val.get("new")
            else:
                old, new = "", val
            return prettify_key(field), fmt_val(old), fmt_val(new)

        rows = format_html_join(
            "\n",
            '<tr>'
            '<td style="padding:8px 14px;font-weight:600;border-bottom:1px solid #e5e7eb;white-space:nowrap;">{}</td>'
            '<td style="padding:8px 14px;border-bottom:1px solid #e5e7eb;">{}</td>'
            '<td style="padding:8px 14px;text-align:center;border-bottom:1px solid #e5e7eb;">→</td>'
            '<td style="padding:8px 14px;border-bottom:1px solid #e5e7eb;">{}</td>'
            '</tr>',
            (row_values(field, val) for field, val in changes.items()),
        )
        return format_html(
            '<table style="border-collapse:collapse;width:100%;font-size:13px;">'
            '<thead><tr>'
            '<th style="text-align:left;padding:8px 14px;border-bottom:2px solid #d1d5db;">Field</th>'
            '<th style="text-align:left;padding:8px 14px;border-bottom:2px solid #d1d5db;">Old</th><th></th>'
            '<th style="text-align:left;padding:8px 14px;border-bottom:2px solid #d1d5db;">New</th>'
            '</tr></thead><tbody>{}</tbody></table>',
            rows,
        )

    @admin.display(description="Other Metadata")
    def metadata_table(self, obj):
        metadata = obj.metadata if isinstance(obj.metadata, dict) else {}
        extra = {k: v for k, v in metadata.items() if k != "changes"}
        if not extra:
            return "—"

        rows = format_html_join(
            "\n",
            '<tr>'
            '<td style="padding:8px 14px;font-weight:600;border-bottom:1px solid #e5e7eb;vertical-align:top;white-space:nowrap;">{}</td>'
            '<td style="padding:8px 14px;border-bottom:1px solid #e5e7eb;word-break:break-word;">{}</td>'
            '</tr>',
            ((prettify_key(k), fmt_val(v)) for k, v in extra.items()),
        )
        return format_html(
            '<table style="border-collapse:collapse;width:100%;font-size:13px;"><tbody>{}</tbody></table>',
            rows,
        )

    @admin.display(description="Raw Metadata (JSON)")
    def raw_metadata(self, obj):
        pretty = json.dumps(obj.metadata, indent=2, default=str)
        return format_html(
            '<pre style="background:#000000;padding:14px;border-radius:6px;'
            'overflow:auto;max-height:400px;font-size:12px;">{}</pre>',
            pretty,
        )