from django import forms
from .models import KullaniciProfili
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'style': 'width: 100%; padding: 1rem; border-radius: 12px; background: var(--bg-surface); border: 1px solid var(--border-glass); color: var(--text-primary); font-family: inherit; outline: none; transition: border-color 0.3s ease;'
            }),
            'email': forms.EmailInput(attrs={
                'style': 'width: 100%; padding: 1rem; border-radius: 12px; background: var(--bg-surface); border: 1px solid var(--border-glass); color: var(--text-primary); font-family: inherit; outline: none; transition: border-color 0.3s ease;'
            })
        }


class ProfilGuncellemeForm(forms.ModelForm):
    class Meta:
        model = KullaniciProfili
        fields = ['profil_fotografi', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Kendinizden bahsedin...',
                'style': 'width: 100%; padding: 1rem; border-radius: 12px; background: var(--bg-surface); border: 1px solid var(--border-glass); color: var(--text-primary); font-family: inherit; resize: none; min-height: 100px; outline: none; transition: border-color 0.3s ease;',
            })
        }
