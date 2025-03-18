from django.shortcuts import render, get_object_or_404
from .models import Game, UserScore, UserLocation

# Create your views here.
# game/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("GeoDeer!")

def create(request):
    return render(request, 'game/create.html')

def monitor(request, pk):
    game = get_object_or_404(Game, pk=pk)

    user_scores = UserScore.objects.filter(game=game).select_related('user')
    user_locations = UserLocation.objects.filter(game=game).select_related('user')
    
    location_map = {}
    for loc in user_locations:
        uid = loc.user.user_id
    
        if uid not in location_map or loc.pk > location_map[uid].pk:
            location_map[uid] = loc

    players = []
    for score in user_scores:
        uid = score.user.user_id
        loc = location_map.get(uid)
        player = {
            'id': uid,
            'name': score.user.username,
            'score': score.total_score,
            'lat': loc.lat if loc else None,  
            'lng': loc.lon if loc else None,
        }
        players.append(player)
    
    sorted_players = sorted(players, key=lambda p: p['id'])
    available_colors = ['cyan', 'red', 'purple', 'yellow']
    for i, player in enumerate(sorted_players):
        player['icon'] = available_colors[i % len(available_colors)]
    
    return render(request, 'game/monitor.html', {'players': sorted_players})