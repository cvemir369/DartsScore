from django.db import models
from user.models import Player
from django.contrib.auth import get_user_model
    
    
class GameChoices(models.IntegerChoices):
    """ Game choices: 301, 501, Cricket, etc. """
    DARTS301 = 0, 'Standard 301'
    DARTS501 = 1, 'Standard 501'
    DARTS701 = 2, 'Standard 701'
    CRICKET = 3, 'Cricket'
    CRICKETCUT = 4, 'Cricket Cut Throat'


class GameSession(models.Model):    
    """ GameSessions are owned by CustomUser, one CustomUser can have many game sessions """
    game_type = models.IntegerField(choices=GameChoices.choices, default=GameChoices.DARTS501)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, related_name='game_session')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    current_sum = models.IntegerField(default=0)
    scores = models.TextField()
    undo = models.TextField(default='{}')
    
    def __str__(self):
        return f'id:{self.id} owner:{self.owner} game_type:{self.game_type}'