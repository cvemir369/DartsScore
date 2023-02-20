from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import CustomUser, Player

# Needed for admin
class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username',)

        
# Needed for admin
class CustomUserChangeForm(UserChangeForm):
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username',)
        

class PlayerForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Player
        exclude = ('owner',)
    
    def clean_name(self):
        """Don't allow duplicate names"""
        data = self.cleaned_data['name']
        if Player.objects.filter(name=data, owner=self.request.user).exists():
            raise forms.ValidationError('Player with that name already exists.')
        return data