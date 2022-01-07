from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Candidate, User


class CandidateAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal info', {'fields': ['name', 'fraction', 'telephone', 'email', 'author', 'avatar']}),
        ("Moderator's info", {'fields': ['moderated', 'refusal_reason']}),
        ('About person', {'fields': ['biography', 'targets']}),
        ('Rating', {'fields': ['votes']}),
    ]


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        ('Additional Data', {'fields': ['role', 'checked_by_moderator']}),
    )


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(User, CustomUserAdmin)