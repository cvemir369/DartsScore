from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from .models import GameSession, Player
from .forms import GameCreateForm
from .utils import calculate_average, calculate_total_average, checkout_check, temp_checkout_calculated

import ast, copy


@login_required
def home_view(request):
    """Home page for the logged in user with list of all game sessions"""
    # show all users game sessions
    games = GameSession.objects.filter(owner=request.user).order_by('-time_modified')
    players = Player.objects.filter(owner=request.user).order_by('name')
    players_count = len(players)
    games_count = False if len(games)==0 else True
    context = {'games':games, 'players':players, 'games_count':games_count, 'players_count':players_count,}
    return render(request, 'home.html', context=context)


class GameCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Creates a new game session"""
    model = GameSession
    form_class = GameCreateForm
    template_name = 'game_create.html'
    success_url = '/play/{id}'
    success_message = 'Game session created successfully'
    
    def form_valid(self, form):
        '''Auto set logged in user to owner and set scores dict to correct game type'''
        form.instance.owner = self.request.user
        
        if form.instance.game_type == 0:
            points = 301
        elif form.instance.game_type == 1:
            points = 501
        elif form.instance.game_type == 2:
            points = 701
        else:
            # cricket not implemented yet!
            raise NotImplementedError('Cricket is not implemented yet.')
        
        form.instance.scores = {
            'points': {'player1':points, 'player2':points,},
            'games': {'player1':0, 'player2':0,},
            'turn': {'player1':True, 'player2':False},
            'darts': {'player1':0, 'player2':0},
            'darts_total': {'player1':0, 'player2':0},
            'total_points_scored': {'player1':0, 'player2':0},
            'average': {'player1':0, 'player2':0},
            'average_total': {'player1':0, 'player2':0},
            }
        form.instance.undo = form.instance.scores
        return super().form_valid(form)
        
    def get_form(self, *args, **kwargs):
        '''Show only players owned by logged in user'''
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        form.fields['players'].queryset = Player.objects.filter(owner=self.request.user).order_by('name')
        return form
        

class GameDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = GameSession
    template_name = 'game_delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'game'
    success_message = 'Game session deleted successfully'
    
    def get_queryset(self):
        '''Show only if owned by logged in user'''
        return self.model.objects.filter(owner_id=self.request.user)


@login_required
def reset_game_view(request, pk):
    """Reset Game Session by pk. Resets players' scores and round"""
    active_game = get_object_or_404(GameSession, owner_id=request.user, pk=pk)
    
    if active_game.game_type == 0:
        game_win_points = 301
    elif active_game.game_type == 1:
        game_win_points = 501
    elif active_game.game_type == 2:
        game_win_points = 701
    else:
        # Game Type is Cricket, not implemented
        pass
    
    if request.method == 'POST':
        scores_def = {
            'points': {'player1':game_win_points, 'player2':game_win_points,},
            'games': {'player1':0, 'player2':0,},
            'turn': {'player1':True, 'player2':False},
            'darts': {'player1':0, 'player2':0},
            'darts_total': {'player1':0, 'player2':0},
            'total_points_scored': {'player1':0, 'player2':0},
            'average': {'player1':0, 'player2':0},
            'average_total': {'player1':0, 'player2':0},
        }
        
        active_game.scores = scores_def
        active_game.undo = scores_def
        active_game.save()
        return redirect('play', pk=active_game.id)
    context = {'game': active_game}
    return render(request, 'game_reset.html', context=context)


@login_required
def play_game_view(request, pk):
    """Gameplay view to show the active game by pk"""
    
    active_game = get_object_or_404(GameSession, owner_id=request.user, pk=pk)
    
    # Check game type (301 or 501 or 701, etc.)
    if active_game.game_type == 0:
        game_win_points = 301
    elif active_game.game_type == 1:
        game_win_points = 501
    elif active_game.game_type == 2:
        game_win_points = 701
        
    players = active_game.players.all().order_by('name')
    scores_dict = ast.literal_eval(active_game.scores)
    
    p1_real_name = players[0]
    p2_real_name = players[1]
    p1_points = scores_dict['points']['player1']
    p2_points = scores_dict['points']['player2']
    p1_games = scores_dict['games']['player1']
    p2_games = scores_dict['games']['player2']
    p1_turn = scores_dict['turn']['player1']
    p2_turn = scores_dict['turn']['player2']
    p1_game_darts_thrown = scores_dict['darts']['player1']
    p2_game_darts_thrown = scores_dict['darts']['player2']
    p1_total_darts_thrown = scores_dict['darts_total']['player1']
    p2_total_darts_thrown = scores_dict['darts_total']['player2']
    p1_total_points_scored = scores_dict['total_points_scored']['player1']
    p2_total_points_scored = scores_dict['total_points_scored']['player2']
    p1_average = scores_dict['average']['player1']
    p2_average = scores_dict['average']['player2']
    p1_average_total = scores_dict['average_total']['player1']
    p2_average_total = scores_dict['average_total']['player2']
    numeric_pressed = False
    
    #checkout
    if p1_turn:
        checkout, checkout_show = checkout_check(p1_points)
        temp_checkout, temp_checkout_show = checkout_check(p1_points)
    elif p2_turn:
        checkout, checkout_show = checkout_check(p2_points)
        temp_checkout, temp_checkout_show = checkout_check(p2_points)
    
    if request.method == 'GET':
        # reset current_sum to 0 on first page entry from home page
        active_game.current_sum = 0
        active_game.save()

    if request.method == 'POST':
        
        if request.POST.get('bust'):
            # "Bust" button pressed
            active_game.undo = copy.deepcopy(scores_dict) # save last state for undo
            active_game.current_sum = 0
            # calculate average, but check who is playing:
            if scores_dict['turn']['player1']:
                # player1 turn
                p1_game_darts_thrown += 3
                p1_total_darts_thrown += 3
                p1_average = calculate_average(game_win_points, p1_points, p1_game_darts_thrown)
                p1_average_total = calculate_total_average(p1_total_points_scored, p1_total_darts_thrown)
                scores_dict['darts']['player1'] = p1_game_darts_thrown
                scores_dict['darts_total']['player1'] = p1_total_darts_thrown
                scores_dict['total_points_scored']['player1'] = p1_total_points_scored
                scores_dict['average']['player1'] = p1_average
                scores_dict['average_total']['player1'] = p1_average_total
                scores_dict['turn']['player1'] = False
                scores_dict['turn']['player2'] = True
            else:
                # player2 turn
                p2_game_darts_thrown += 3
                p2_total_darts_thrown += 3
                p2_average = calculate_average(game_win_points, p2_points, p2_game_darts_thrown)
                p2_average_total = calculate_total_average(p2_total_points_scored, p2_total_darts_thrown)
                scores_dict['darts']['player2'] = p2_game_darts_thrown
                scores_dict['darts_total']['player2'] = p2_total_darts_thrown
                scores_dict['total_points_scored']['player2'] = p2_total_points_scored
                scores_dict['average']['player2'] = p2_average
                scores_dict['average_total']['player2'] = p2_average_total
                scores_dict['turn']['player1'] = True
                scores_dict['turn']['player2'] = False
            
        elif request.POST.get('next'):
            # "Switch player" button pressed. Switch players' turn without affecting average scores
            scores_dict['turn']['player1'] = False if scores_dict['turn']['player1'] else True
            scores_dict['turn']['player2'] = False if scores_dict['turn']['player2'] else True
            active_game.current_sum = 0
            messages.success(request, 'Player switched.')

        elif request.POST.get('score_manual') or request.POST.get('submit_score'):
            active_game.undo = copy.deepcopy(scores_dict) # save last state for undo
            
            try:
                # check if any input typed in "Enter score manually" input field
                score = int(request.POST.get('score_manual'))
                if score <= 180:
                    active_game.current_sum = score # manually typed score always overtakes calculated score
            except:
                pass
            try:
                score = active_game.current_sum # try setting the score to manually typed score input field's value
                if score <= 180:
                    # score can't be more than 180

                    if scores_dict['turn']['player1']:
                        p_name = 'player1'
                        p_real_name = players[0]
                        p_points = scores_dict['points'][p_name]
                        p_game_darts_thrown = p1_game_darts_thrown
                        p_total_darts_thrown = p1_total_darts_thrown
                        p_total_points_scored = p1_total_points_scored
                    elif scores_dict['turn']['player2']:
                        p_name = 'player2'
                        p_real_name = players[1]
                        p_points = scores_dict['points'][p_name]
                        p_game_darts_thrown = p2_game_darts_thrown
                        p_total_darts_thrown = p2_total_darts_thrown
                        p_total_points_scored = p2_total_points_scored
                    
                    result = p_points - score
                    p_game_darts_thrown += 3
                    p_total_darts_thrown += 3
                    if result < 0 or result == 1:
                        # Result can't be less than 0 or 1 (double out rule)
                        # Bust!
                        score = scores_dict['points'][p_name]
                        p_average = calculate_average(game_win_points, score, p_game_darts_thrown)
                        p_average_total = calculate_total_average(p_total_points_scored, p_total_darts_thrown)
                    elif result == 0:
                        # Game Won!
                        p_total_points_scored += score
                        # checkout darts used for stats
                        checkout_darts_used = int(request.POST.get('checkout_darts_used'))
                        if checkout_darts_used == 1:
                            p_game_darts_thrown -= 2
                            p_total_darts_thrown -= 2
                        elif checkout_darts_used == 2:
                            p_game_darts_thrown -= 1
                            p_total_darts_thrown -= 1
                        p_average = calculate_average(game_win_points, result, p_game_darts_thrown)
                        p_average_total = calculate_total_average(p_total_points_scored, p_total_darts_thrown)
                        # Win message:
                        messages.success(request, f'{p_real_name} has won the game with {p_game_darts_thrown} darts thrown and average score of {p_average}!')
                        # reset scores for both players
                        scores_dict['points']['player1'] = game_win_points
                        scores_dict['points']['player2'] = game_win_points
                        # add 1 game to player1
                        scores_dict['games'][p_name] += 1
                        game_won = True
                    else:
                        # Legal result scored
                        scores_dict['points'][p_name] = result
                        p_total_points_scored += score
                        p_average = calculate_average(game_win_points, result, p_game_darts_thrown)
                        p_average_total = calculate_total_average(p_total_points_scored, p_total_darts_thrown)
                    
                    if p_name == 'player1':
                        scores_dict['turn']['player1'] = False
                        scores_dict['turn']['player2'] = True
                        scores_dict['darts']['player1'] = p_game_darts_thrown
                        scores_dict['darts_total']['player1'] = p_total_darts_thrown
                        scores_dict['total_points_scored']['player1'] = p_total_points_scored
                        scores_dict['average']['player1'] = p_average
                        scores_dict['average_total']['player1'] = p_average_total
                    elif p_name == 'player2':
                        scores_dict['turn']['player1'] = True
                        scores_dict['turn']['player2'] = False
                        scores_dict['darts']['player2'] = p_game_darts_thrown
                        scores_dict['darts_total']['player2'] = p_total_darts_thrown
                        scores_dict['total_points_scored']['player2'] = p_total_points_scored
                        scores_dict['average']['player2'] = p_average
                        scores_dict['average_total']['player2'] = p_average_total
                    
                    if game_won:
                        scores_dict['darts']['player1'] = 0
                        scores_dict['darts']['player2'] = 0
 
                if p1_turn:
                    checkout, checkout_show = checkout_check(p1_points)
                elif p2_turn:
                    checkout, checkout_show = checkout_check(p2_points)
            except:
                pass
            active_game.current_sum = 0

        # Buttons pressed to calculate score:
        elif request.POST.get('1'):
            numeric_pressed_value = 1
            numeric_pressed = True
        elif request.POST.get('2'):
            numeric_pressed_value = 2
            numeric_pressed = True
        elif request.POST.get('3'):
            numeric_pressed_value = 3
            numeric_pressed = True
        elif request.POST.get('4'):
            numeric_pressed_value = 4
            numeric_pressed = True
        elif request.POST.get('5'):
            numeric_pressed_value = 5
            numeric_pressed = True
        elif request.POST.get('6'):
            numeric_pressed_value = 6
            numeric_pressed = True
        elif request.POST.get('7'):
            numeric_pressed_value = 7
            numeric_pressed = True
        elif request.POST.get('8'):
            numeric_pressed_value = 8
            numeric_pressed = True
        elif request.POST.get('9'):
            numeric_pressed_value = 9
            numeric_pressed = True
        elif request.POST.get('10'):
            numeric_pressed_value = 10
            numeric_pressed = True
        elif request.POST.get('11'):
            numeric_pressed_value = 11
            numeric_pressed = True
        elif request.POST.get('12'):
            numeric_pressed_value = 12
            numeric_pressed = True
        elif request.POST.get('13'):
            numeric_pressed_value = 13
            numeric_pressed = True
        elif request.POST.get('14'):
            numeric_pressed_value = 14
            numeric_pressed = True
        elif request.POST.get('15'):
            numeric_pressed_value = 15
            numeric_pressed = True
        elif request.POST.get('16'):
            numeric_pressed_value = 16
            numeric_pressed = True
        elif request.POST.get('17'):
            numeric_pressed_value = 17
            numeric_pressed = True
        elif request.POST.get('18'):
            numeric_pressed_value = 18
            numeric_pressed = True
        elif request.POST.get('19'):
            numeric_pressed_value = 19
            numeric_pressed = True
        elif request.POST.get('20'):
            numeric_pressed_value = 20
            numeric_pressed = True
        elif request.POST.get('25'):
            numeric_pressed_value = 25
            numeric_pressed = True

        if numeric_pressed:
            active_game.current_sum += numeric_pressed_value
            if p1_turn:
                temp_checkout, temp_checkout_show = temp_checkout_calculated(p1_points, active_game.current_sum)
            else:
                temp_checkout, temp_checkout_show = temp_checkout_calculated(p2_points, active_game.current_sum)

        elif request.POST.get('reset_counter'):
            active_game.current_sum = 0
            
        elif request.POST.get('undo'):
            if active_game.scores != active_game.undo:
                scores_dict = ast.literal_eval(active_game.undo)

        active_game.scores = scores_dict
        active_game.save()
        p1_points = scores_dict['points']['player1']
        p2_points = scores_dict['points']['player2']
        p1_games = scores_dict['games']['player1']
        p2_games = scores_dict['games']['player2']
        p1_turn = scores_dict['turn']['player1']
        p2_turn = scores_dict['turn']['player2']
        p1_game_darts_thrown = scores_dict['darts']['player1']
        p2_game_darts_thrown = scores_dict['darts']['player2']
        p1_total_darts_thrown = scores_dict['darts_total']['player1']
        p2_total_darts_thrown = scores_dict['darts_total']['player2']
        p1_total_points_scored = scores_dict['total_points_scored']['player1']
        p2_total_points_scored = scores_dict['total_points_scored']['player2']
        p1_average = scores_dict['average']['player1']
        p2_average = scores_dict['average']['player2']
        p1_average_total = scores_dict['average_total']['player1']
        p2_average_total = scores_dict['average_total']['player2']
        numeric_pressed = False
        
        if p1_turn:
            checkout, checkout_show = checkout_check(p1_points)
            temp_checkout, temp_checkout_show = checkout_check(p1_points - active_game.current_sum)
        elif p2_turn:
            checkout, checkout_show = checkout_check(p2_points)
            temp_checkout, temp_checkout_show = checkout_check(p2_points - active_game.current_sum)

    context = {
        'active_game': active_game,
        'players': players,
        'p1_real_name': p1_real_name,
        'p2_real_name': p2_real_name,
        'p1_points': p1_points,
        'p1_games': p1_games,
        'p1_turn': p1_turn,
        'p2_points': p2_points,
        'p2_games': p2_games,
        'p2_turn': p2_turn,
        'p1_average': p1_average,
        'p2_average': p2_average,
        'p1_average_total': p1_average_total,
        'p2_average_total': p2_average_total,
        'current_sum': active_game.current_sum,
        'checkout': checkout,
        'checkout_show': checkout_show,
        'temp_checkout': temp_checkout,
        'temp_checkout_show': temp_checkout_show,
    }
    return render(request, 'play.html', context=context)