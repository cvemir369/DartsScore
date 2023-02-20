from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    """ CustomUser, based off AbstractUser, can signup, login, etc. """
    pass

    def __str__(self):
        return self.email


class Player(models.Model):
    """ Players are owned by CustomUser, one CustomUser can have many Players """
    name = models.CharField(max_length=20)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # standard_all_time_average = models.PositiveIntegerField(default=0)
    # standard_all_time_tries = models.PositiveIntegerField(default=0)
    # standard_number_of_180s = models.PositiveBigIntegerField(default=0)
    # standard_highest_checkout = models.PositiveIntegerField(default=0)
    # cricket_all_time_average
    # cricket_lowest_round_win
    
    def __str__(self):
        return self.name
    
    """
    implement new features: Player stats...
    
    standard_all_time_average = load current from db
    standard_all_time_tries = load current from db

    new_avg = (standard_all_time_average * standard_all_time_tries + player_points) / (standard_all_time_tries + 1)

    standard_all_time_tries += 1
    standard_all_time_average = new_avg
    save to db
    """