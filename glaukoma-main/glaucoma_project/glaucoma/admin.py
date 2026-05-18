from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from glaucoma.models import PatientImage, DoctorImageAnalysis


class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'groups'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(PatientImage)
class PatientImageAdmin(admin.ModelAdmin):
    list_display = ('patient', 'eye', 'date_taken', 'image_tag')
    list_filter = ('patient', 'eye', 'date_taken')
    # Предположим, что у модели Patient определены поля first_name и last_name;
    # если нет, скорректируйте параметры поиска согласно вашим моделям.
    search_fields = ['patient__first_name', 'patient__last_name', 'eye', 'date_taken']

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return 'No Image'
    image_tag.short_description = 'Image'


@admin.register(DoctorImageAnalysis)
class DoctorImageAnalysisAdmin(admin.ModelAdmin):
    list_display = ('patient_image', 'doctor', 'cdr', 'notes', 'description', 'updated_at')
    search_fields = ['patient_image__id', 'doctor__id', 'notes']
