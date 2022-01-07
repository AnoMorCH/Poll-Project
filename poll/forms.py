from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Candidate, AdminData

User = get_user_model()


class CreateCandidateForm(ModelForm):
    class Meta:
        model = Candidate

        fields = [
            'name',
            'fraction',
            'telephone',
            'targets',
            'email',
            'biography',
            'avatar',
        ]

        widgets = {
            'biography': forms.Textarea(attrs={'rows': 3}),
        }


class ModerateCandidateForm(ModelForm):
    class Meta:
        model = Candidate

        fields = [
            'refusal_reason',
        ]

        widgets = {
            'refusal_reason': forms.Textarea(attrs={'rows': 3}),
        }


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class EditModeratorInstruction(ModelForm):
    class Meta:
        model = AdminData

        fields = [
            'instruction',
        ]

        widgets = {
            'instruction': forms.Textarea(attrs={'rows': 3}),
        }