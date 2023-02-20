from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .forms import PlayerForm
from .models import Player


class PassRequestToFormViewMixin:
    '''Mixin Class to pass the request to the form'''
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class PlayerCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    form_class = PlayerForm
    template_name = 'players_create.html'
    success_url = reverse_lazy('players')
    success_message = 'Player was created successfully'
    
    def form_valid(self, form):
        # auto save player's owner
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    
class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template_name = 'players_list.html'
    context_object_name = 'players'
    
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user).order_by('name')
    

class PlayerUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    form_class = PlayerForm
    template_name = 'players_update.html'
    context_object_name = 'player'
    queryset = Player.objects.all()
    success_url = reverse_lazy('players')
    success_message = 'Player updated successfully'
    

class PlayerDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Player
    template_name = 'players_delete.html'
    context_object_name = 'player'
    success_url = reverse_lazy('players')
    success_message = 'Player deleted successfully'
    
    def form_valid(self, form, *args, **kwargs):
        # Delete all related player's game sessions
        player = Player.objects.get(id=self.kwargs['pk'])
        player_game_sessions = player.game_session.all()
        for session in player_game_sessions:
            session.delete()
        return super().form_valid(form, *args, **kwargs)