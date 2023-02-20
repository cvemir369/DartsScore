from .checkouts import checkouts

def calculate_average(game_win_points, player_points, player_total_darts_thrown):
    """Calculates player's average, takes in 301, 501 or 701 as game win points, player's current points left and total number of darts thrown"""
    # Average = Total points scored divided by the number of darts thrown multiplied by 3.
    player_total_points_scored = game_win_points - player_points
    player_average = round(player_total_points_scored / player_total_darts_thrown * 3, 1)
    return player_average


def calculate_total_average(player_total_points_scored, player_total_darts_thrown):
    """Calculates player's total average, takes in total points scored in a game session and a total number of darts thrown in same session"""
    player_total_average = round(player_total_points_scored / player_total_darts_thrown * 3, 1)
    return player_total_average


def checkout_check(player_points):
    """Show possible checkout"""
    if player_points > 170:
        checkout = ''
        checkout_show = False
    elif str(player_points) in checkouts:
        checkout = checkouts[str(player_points)]
        checkout_show = True
    elif player_points == 0:
        checkout = 'Win!'
        checkout_show = True
    elif player_points < 0:
        checkout = 'Bust!'
        checkout_show = True
    else:
        checkout = 'No possible checkout'
        checkout_show = True
    return checkout, checkout_show


def temp_checkout_calculated(player_points, current_sum):
    '''Show calculated checkout'''
    temp_score = player_points - current_sum
    temp_checkout, temp_checkout_show = checkout_check(temp_score)
    return temp_checkout, temp_checkout_show