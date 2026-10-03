from django import forms
from django.contrib import admin, messages

from .models import DeviceSession, Student, generate_code


class StudentForm(forms.ModelForm):
    new_code = forms.CharField(label="Yangi kod", required=False,
                               help_text="Bo'sh qoldirilsa, yangi o'quvchi uchun kod avtomatik yaratiladi.")

    class Meta:
        model = Student
        fields = ["full_name", "phone", "is_active", "expires_at", "max_devices"]


class SessionInline(admin.TabularInline):
    model = DeviceSession
    fields = ["device_id", "ip", "user_agent", "created_at", "last_seen", "expires_at", "revoked"]
    readonly_fields = ["device_id", "ip", "user_agent", "created_at", "last_seen", "expires_at"]
    extra = 0
    can_delete = False


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = ["full_name", "phone", "code_hint", "is_active", "expires_at", "max_devices"]
    list_filter = ["is_active"]
    search_fields = ["full_name", "phone", "code_hint"]
    inlines = [SessionInline]
    actions = ["revoke_sessions"]

    def save_model(self, request, obj, form, change):
        code = form.cleaned_data.get("new_code")
        if code or not change:
            code = code or generate_code()
            obj.set_code(code)
            # Kod faqat bir marta ko'rsatiladi — bazada faqat HMAC saqlanadi.
            messages.warning(request, f"{obj.full_name} uchun kirish kodi: {code}  (qayta ko'rsatilmaydi)")
            if change:
                obj.sessions.update(revoked=True)
        super().save_model(request, obj, form, change)

    @admin.action(description="Barcha qurilmalardan chiqarish")
    def revoke_sessions(self, request, queryset):
        n = DeviceSession.objects.filter(student__in=queryset, revoked=False).update(revoked=True)
        self.message_user(request, f"{n} ta sessiya bekor qilindi.")
