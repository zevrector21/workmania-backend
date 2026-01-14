from django.contrib import admin
from core.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
import json


# admin.site.register(Organization)

class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'first_name', 'last_name',
    ]
    ordering = ['-created']
    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Password', {
            'fields': ('password',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')  # okay here if readonly
        }),
    )
    # Make date_joined visible but not editable
    readonly_fields = ('date_joined',)
admin.site.register(User, UserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
admin.site.register(Profile, ProfileAdmin)

class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['client', 'title', 'description', 'skills', 'category', 'type', 'size', 'duration', 'experience_level', 'price', 'languages', 'developers_needed', 'is_active', 'status']
admin.site.register(JobPosting, JobPostingAdmin)


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job_posting', 'freelancer', 'cover_letter', 'price', 'duration', 'status', 'attachments']
admin.site.register(JobApplication, JobApplicationAdmin)


class JobInvitationAdmin(admin.ModelAdmin):
    list_display = ['job_posting', 'freelancer', 'description', 'status']
admin.site.register(JobInvitation, JobInvitationAdmin)


class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['job_posting', 'freelancer', 'price', 'status']
admin.site.register(JobOffer, JobOfferAdmin)


class JobMilestoneAdmin(admin.ModelAdmin):
    list_display = ['job_offer', 'title', 'description', 'price', 'status', 'due_date']
admin.site.register(JobMilestone, JobMilestoneAdmin)


class JobReviewAdmin(admin.ModelAdmin):
    list_display = ['job_offer', 'user', 'rating', 'description']
admin.site.register(JobReview, JobReviewAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'description', 'status']
admin.site.register(Notification, NotificationAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'description', 'status']
admin.site.register(Message, MessageAdmin)


class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'duration']
admin.site.register(Plan, PlanAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'status']
admin.site.register(Subscription, SubscriptionAdmin)
