from django.contrib import admin
from django.db import models
from django.contrib.admin import widgets
import datetime
from .models import SocialWorker, ActivityCategory, Activity

# Register your models here.

@admin.register(SocialWorker)
class SocialWorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'staff_id', 'department')
    search_fields = ('name', 'staff_id')

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'social_worker', 'activity_date', 'participant_num')
    list_filter = ('activity_date', 'categories')
    date_hierarchy = 'activity_date'
    formfield_overrides = {
        models.DateField: {'widget': widgets.AdminDateWidget},
    }
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['activity_date'].initial = datetime.date.today()
        return form
