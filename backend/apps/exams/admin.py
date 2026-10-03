from django.contrib import admin

from .models import Attempt


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "kind", "correct", "total", "started_at", "finished_at"]
    list_filter = ["kind"]
    search_fields = ["student__full_name"]
    readonly_fields = [f.name for f in Attempt._meta.fields]

    def has_add_permission(self, request):
        return False
