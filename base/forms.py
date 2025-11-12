from django import forms
from django.contrib.auth.models import User
from .models import Profile, Room, Message

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'topic', 'description']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']