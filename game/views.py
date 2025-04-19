from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils import timezone
from .models import Game, UserScore, UserLocation, Waypoint, User

import datetime
import json

def auth(request):
    return render(request, 'game/auth.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                login(request, user) 
                return redirect("index")
            else:
                messages.error(request, "Incorrect username or password.")
                return redirect("auth_page")
        except User.DoesNotExist:
            messages.error(request, "Incorrect username or password.")
            return redirect("auth_page")

    return redirect("auth_page")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("auth_page")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("auth_page")

        if User.objects.filter(email=email).exists():
            messages.error(request, "E-mail already exists.")
            return redirect("auth_page")

        hashed_password = make_password(password1)
        user = User(username=username, email=email, password=hashed_password)
        user.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect("auth_page")

    return redirect("auth_page")

def main_menu(request, creator_id):
    if request.method == 'POST':
        if 'delete_game' in request.POST:
            game_id = request.POST.get('delete_game')
            Game.objects.filter(
                game_id=game_id,
                game_creator_id=creator_id
            ).delete()
            return redirect('main_menu', creator_id=creator_id)
        
        new_game = Game.objects.create(
            game_creator_id=creator_id,
            game_name=f'game_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}',
            start_date_time=datetime.datetime.now(),
            number_of_players=2,
            time=3600
        )
        return redirect('create_manage', creator_id=creator_id, game_id=new_game.game_id)

    games = Game.objects.filter(game_creator_id=creator_id).order_by('-start_date_time')
    return render(request, 'game/main_menu.html', {
        'games': games,
        'creator_id': creator_id
    })

import json
import datetime
from django.shortcuts import get_object_or_404, redirect, render
from .models import Game, Waypoint
from django.contrib.auth.models import User

def create_manage(request, creator_id, game_id):
    game = Game.objects.filter(game_id=game_id, game_creator_id=creator_id).first()

    if request.method == 'POST':
        game_name = request.POST.get('game_name', '').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        start_time_str = request.POST.get('start_time', '').strip()
        number_of_players_str = request.POST.get('number_of_players', '0').strip()
        time_str = request.POST.get('time', '').strip()

        start_dt = None
        if start_date_str and start_time_str:
            try:
                start_dt = datetime.datetime.strptime(
                    f"{start_date_str} {start_time_str}",
                    "%Y/%m/%d %H:%M:%S"
                )
            except ValueError:
                start_dt = None
                
        try:
            number_of_players = float(number_of_players_str)
        except ValueError:
            number_of_players = 0
        try:
            time_float = float(time_str)
        except ValueError:
            time_float = 0
            
        if game:
            game.game_name = game_name
            if start_dt:
                game.start_date_time = start_dt
            game.number_of_players = number_of_players
            game.time = time_float
            game.save()
        else:
            creator = get_object_or_404(User, id=creator_id)
            game = Game.objects.create(
                game_name = game_name,
                start_date_time = start_dt,
                number_of_players = number_of_players,
                time = time_float,
                game_creator = creator,
            )

        waypoints_data = request.POST.get('waypoints_data', '[]')
        try:
            wps = json.loads(waypoints_data)
        except json.JSONDecodeError:
            wps = []

        deleted_ids = json.loads(request.POST.get('deleted_ids', '[]'))
        if deleted_ids:
            Waypoint.objects.filter(
                game=game,
                waypoint_id__in=deleted_ids
            ).delete()

        Waypoint.objects.filter(game=game).update(is_last=False)

        kept_ids = set()
        for wp in wps:
            wp_id   = wp.get('id')
            is_last = bool(wp.get('is_last', False))

            if wp_id:
                waypoint = Waypoint.objects.filter(pk=wp_id, game=game).first()
                if waypoint:
                    waypoint.waypoint_name  = wp.get('name', '')
                    waypoint.hint           = wp.get('hint', '')
                    waypoint.question       = wp.get('question', '')
                    waypoint.answer         = wp.get('answer', '')
                    waypoint.ques_dif_level = float(wp.get('difficulty') or 0)
                    waypoint.lat            = float(wp.get('lat'))
                    waypoint.lon            = float(wp.get('lon'))
                    waypoint.is_last        = is_last
                    waypoint.save()
                    kept_ids.add(waypoint.pk)
            else:
                new_wp = Waypoint.objects.create(
                    game            = game,
                    waypoint_name   = wp.get('name', ''),
                    lat             = float(wp.get('lat')),
                    lon             = float(wp.get('lon')),
                    hint            = wp.get('hint', ''),
                    question        = wp.get('question', ''),
                    answer          = wp.get('answer', ''),
                    ques_dif_level  = float(wp.get('difficulty') or 0),
                    is_last         = is_last,
                )
                kept_ids.add(new_wp.pk)

        game.waypoints.exclude(pk__in=kept_ids).delete()

        return redirect('create_manage', creator_id=creator_id, game_id=game.game_id)
    
    context = {
        'creator_id':      creator_id,
        'game_id':         game_id,
        'game':            game,
        'waypoint_count':  game.waypoints.count(),
        'last_point_count':game.waypoints.filter(is_last=True).count(),
    }
    return render(request, 'game/create_manage.html', context)

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

def monitor(request, pk, creator_id):
    game = get_object_or_404(Game, pk=pk, game_creator_id=creator_id)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        player_id = request.POST.get('player_id')
        user = get_object_or_404(User, user_id=player_id)
        score = get_object_or_404(UserScore, game=game, user=user)
        score.is_disqualified = True
        score.save()
        return JsonResponse({"status": "success"})

    user_scores = UserScore.objects.filter(game=game).select_related('user')
    players = []
    
    for score in user_scores:
        uid = score.user.user_id
        user_locs = list(UserLocation.objects.filter(game=game, user=score.user).order_by('-pk')[:10])
        user_locs.reverse()  
        latest = user_locs[-1] if user_locs else None
        path = [{'lat': loc.lat, 'lon': loc.lon} for loc in user_locs]  
        player = {
            'id': uid,
            'name': score.user.username,
            'score': score.total_score,
            'lat': latest.lat if latest else None,
            'lon': latest.lon if latest else None,  
            'path': path,
            'disqualified': score.is_disqualified
        }
        players.append(player)

    sorted_players = sorted(players, key=lambda p: p['id'])
    available_colors = ['cyan', 'red', 'purple', 'yellow']
    
    for i, player in enumerate(sorted_players):
        player['icon'] = available_colors[i % len(available_colors)]

    waypoints_qs = game.waypoints.all().order_by('waypoint_id')
    waypoints = []
    
    for index, wp in enumerate(waypoints_qs):
        if index == 0:
            label = "Start Location"
            marker_color = "#296B45"
        elif index == len(waypoints_qs) - 1:
            label = "Last Waypoint"
            marker_color = "#A52A2A"
        else:
            label = f"{ordinal(index)} Waypoint"
            marker_color = "#B3D8E7"
        
        waypoints.append({
            'id': wp.waypoint_id,
            'name': wp.waypoint_name,
            'lat': wp.lat,
            'lon': wp.lon, 
            'label': label,
            'marker_color': marker_color,
        })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'players': sorted_players, 'waypoints': waypoints})
    
    return render(request, 'game/monitor.html', {
        'players': sorted_players,
        'game': game,
        'waypoints': waypoints
    })

def results(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user_scores = UserScore.objects.filter(game=game).select_related('user')
    players = []
    
    for score in user_scores:
        uid = score.user.user_id
        user_locs = list(UserLocation.objects.filter(game=game, user=score.user).order_by('-pk')[:10])
        user_locs.reverse()  
        latest = user_locs[-1] if user_locs else None
        path = [{'lat': loc.lat, 'lon': loc.lon} for loc in user_locs]  
        player = {
            'id': uid,
            'name': score.user.username,
            'score': score.total_score,
            'lat': latest.lat if latest else None,
            'lon': latest.lon if latest else None,  
            'path': path,
            'disqualified': score.is_disqualified
        }
        players.append(player)

    sorted_players = sorted(players, key=lambda p: p['id'])
    available_colors = ['cyan', 'red', 'purple', 'yellow']
    
    for i, player in enumerate(sorted_players):
        player['icon'] = available_colors[i % len(available_colors)]

    return render(request, 'game/results.html', {
        'players': sorted_players,
        'game': game
    })