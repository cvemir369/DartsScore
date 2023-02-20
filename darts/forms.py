from django import forms
from django.forms import CheckboxSelectMultiple, ChoiceField
from .models import GameSession, GameChoices
from user.models import Player


class GameCreateForm(forms.ModelForm):
            
    game_type = ChoiceField(choices=GameChoices.choices)
    
    class Meta:
        model = GameSession
        fields = ('game_type', 'players',)
        widgets = {
            'players': CheckboxSelectMultiple(choices=Player.objects.all()),
        }

    def clean_players(self):
        data = self.cleaned_data['players']
        if len(data) != 2:
            raise forms.ValidationError('Two players must be selected to play!')
        return data
    
    def clean_game_type(self):
        data = int(self.cleaned_data['game_type'])
        if data == 3 or data == 4:
            raise forms.ValidationError('Cricket games are not implemented yet.')
        return data