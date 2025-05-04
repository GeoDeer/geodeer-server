from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils import timezone
import pytz
from .models import Game, UserScore, UserLocation, Waypoint, User, Question
from .services.score_calculator import calculate_scores_for_game
from datetime import timedelta

import datetime
import json

# def auth(request):
#     return render(request, 'game/auth.html')

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         try:
#             user = User.objects.get(username=username)
#             if check_password(password, user.password):
#                 login(request, user) 
#                 return redirect("index")
#             else:
#                 messages.error(request, "Incorrect username or password.")
#                 return redirect("auth_page")
#         except User.DoesNotExist:
#             messages.error(request, "Incorrect username or password.")
#             return redirect("auth_page")

#     return redirect("auth_page")

# def register_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")

#         if password1 != password2:
#             messages.error(request, "Passwords do not match.")
#             return redirect("auth_page")

#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists.")
#             return redirect("auth_page")

#         if User.objects.filter(email=email).exists():
#             messages.error(request, "E-mail already exists.")
#             return redirect("auth_page")

#         hashed_password = make_password(password1)
#         user = User(username=username, email=email, password=hashed_password)
#         user.save()
#         messages.success(request, "Registration successful! You can now log in.")
#         return redirect("auth_page")

#     return redirect("auth_page")

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
            start_date_time=timezone.now(),
            number_of_players=2,
            time=3600
        )
        return redirect('create_manage', creator_id=creator_id, game_id=new_game.game_id)

    games = Game.objects.filter(game_creator_id=creator_id).order_by('-start_date_time')
    return render(request, 'game/main_menu.html', {
        'games': games,
        'creator_id': creator_id, 
    })

def create_manage(request, creator_id, game_id):
    game = Game.objects.filter(game_id=game_id, game_creator_id=creator_id).first()
    waypoints = game.waypoints.all().order_by('waypoint_id')
    
    if request.method == 'POST':
        game_name = request.POST.get('game_name', '').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        start_time_str = request.POST.get('start_time', '').strip()
        number_of_players_str = request.POST.get('number_of_players', '0').strip()
        time_str = request.POST.get('time', '').strip()
        user_timezone_name = request.POST.get('user_timezone')

        naive_start_dt = None
        aware_start_dt = None

        if start_date_str and start_time_str:
            try:
                naive_start_dt = datetime.datetime.strptime(
                    f"{start_date_str} {start_time_str}",
                    "%Y/%m/%d %H:%M:%S"
                )
                user_tz = None
                if user_timezone_name:
                    try:
                        user_tz = pytz.timezone(user_timezone_name)
                    except pytz.UnknownTimeZoneError:
                        print(f"Warning: Unknown timezone received: {user_timezone_name}. Using Django default.")
                        user_tz = timezone.get_current_timezone()
                else:
                    print(f"Warning: User timezone info not found. Using Django default ({timezone.get_current_timezone_name()}).")
                    user_tz = timezone.get_current_timezone()

                aware_start_dt = user_tz.localize(naive_start_dt)
            except ValueError:
                aware_start_dt = None
                print(f"Error: Invalid date/time format: {start_date_str} {start_time_str}")
                messages.error(request, "Invalid date/time format provided.")

        # Debug time information
        # print(f"--- Debug Time Info Start ---")
        # print(f"Received Date Str: {start_date_str}")
        # print(f"Received Time Str: {start_time_str}")
        # print(f"Received Timezone Name: {user_timezone_name}")
        # if 'user_tz' in locals(): 
        #      print(f"Pytz Timezone Object: {user_tz}")
        # else:
        #      print("Pytz Timezone Object: Not Created (check errors above)")
        # print(f"Naive Datetime: {naive_start_dt}")
        # print(f"Aware Datetime (Before Save): {aware_start_dt}")
        # print(f"--- Debug Time Info End ---")
        
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
            if aware_start_dt:
                game.start_date_time = aware_start_dt
            game.number_of_players = number_of_players
            game.time = time_float
            game.save()
        else:
            creator = get_object_or_404(User, id=creator_id)
            game = Game.objects.create(
                game_name=game_name,
                start_date_time=aware_start_dt if aware_start_dt else timezone.now(),
                number_of_players=number_of_players,
                time=time_float,
                game_creator=creator,
            )

        waypoints_data = request.POST.get('waypoints_data', '[]')
    
        try:
            wps = json.loads(waypoints_data)
        except json.JSONDecodeError:
            wps = []

        deleted_ids = json.loads(request.POST.get('deleted_ids', '[]'))
        if deleted_ids:
            Waypoint.objects.filter(game=game, waypoint_id__in=deleted_ids).delete()

        kept_ids = set()
        for wp in wps:
            wp_id = wp.get('id')

            if wp_id:
                waypoint = Waypoint.objects.filter(pk=wp_id, game=game).first()
                if waypoint:
                    waypoint.waypoint_name = wp.get('name', '')
                    waypoint.hint = wp.get('hint', '')
                    waypoint.question = wp.get('question', '')
                    waypoint.answer = wp.get('answer', '')
                    waypoint.ques_dif_level = float(wp.get('difficulty') or 0)
                    waypoint.lat = float(wp.get('lat'))
                    waypoint.lon = float(wp.get('lon'))
                    waypoint.save()
                    kept_ids.add(waypoint.pk)
            else:
                new_wp = Waypoint.objects.create(
                    game=game,
                    waypoint_name=wp.get('name', ''),
                    lat=float(wp.get('lat')),
                    lon=float(wp.get('lon')),
                    hint=wp.get('hint', ''),
                    question=wp.get('question', ''),
                    answer=wp.get('answer', ''),
                    ques_dif_level=float(wp.get('difficulty') or 0),
                )
                kept_ids.add(new_wp.pk)

        game.waypoints.exclude(pk__in=kept_ids).delete()

        return redirect('create_manage', creator_id=creator_id, game_id=game.game_id)

    context = {
        'creator_id': creator_id,
        'game_id': game_id,
        'game': game,
        'waypoints': waypoints,
        'waypoint_count': game.waypoints.count(),
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
    now = timezone.now()

    game_state = "not_started"
    remaining_seconds_until_end = 0
    end_time = None

    try:
        duration_seconds = int(game.time)
        end_time = game.start_date_time + timedelta(seconds=duration_seconds)
    except (TypeError, ValueError):
        
        print(f"Warning: Invalid game duration found for game {game.game_id}: {game.time}")
        end_time = None 

    if game.start_date_time > now:
        game_state = "not_started"
    elif end_time and now < end_time:
        game_state = "running"
        remaining_seconds_until_end = max(0, int((end_time - now).total_seconds()))
    elif end_time and now >= end_time:
        game_state = "finished"
    else:
        game_state = "unknown" 

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
        user_locs = list(
            UserLocation.objects
                .filter(game=game, user=score.user)
                .order_by('-pk')[:100]
        )
        user_locs.reverse()
        latest = user_locs[-1] if user_locs else None

        path = [{'lat': loc.lat, 'lon': loc.lon} for loc in user_locs]

        players.append({
            'id': score.user.user_id,
            'name': score.user.username,
            'score': score.total_score,
            'lat': latest.lat if latest else None,
            'lon': latest.lon if latest else None,
            'path': path,
            'disqualified': score.is_disqualified,
            'speed': latest.speed if latest and latest.speed is not None else 0, 
        })

    sorted_players = sorted(players, key=lambda p: p['id'])
    # available_colors = ['cyan', 'red', 'purple', 'yellow']
    for i, player in enumerate(sorted_players):
        # player['icon'] = available_colors[i % len(available_colors)]     for demo
        if player['id'] == 1:
            player['icon'] = 'red'
        elif player['id'] == 3:
            player['icon'] = 'yellow'
        elif player['id'] == 4:
            player['icon'] = 'purple'
        elif player['id'] == 5:
            player['icon'] = 'cyan'
        elif player['id'] == 6:
            player['icon'] = 'cyan'

    waypoints_qs = game.waypoints.all().order_by('waypoint_id')
    waypoints = []
    for idx, wp in enumerate(waypoints_qs):
        if idx == 0:
            label = "Start Location"
            marker_color = "#296B45"
        elif idx == len(waypoints_qs) - 1:
            label = f"{ordinal(idx)} Waypoint"
            marker_color = "#A52A2A"
        else:
            label = f"{ordinal(idx)} Waypoint"
            marker_color = "#B3D8E7"
        waypoints.append({
            'id': wp.waypoint_id,
            'name': wp.waypoint_name,
            'lat': wp.lat,
            'lon': wp.lon,
            'label': label,
            'marker_color': marker_color,
        })

    # --- AJAX Response için Güncelleme ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX istekleri için de durumu ve kalan saniyeyi gönderelim
        now_ajax = timezone.now() # Tekrar alalım ki en güncel olsun
        if game_state == "running": # Durum değişmiş olabilir
             remaining_seconds_ajax = max(0, int((end_time - now_ajax).total_seconds())) if end_time else 0
        else:
             remaining_seconds_ajax = 0

        return JsonResponse({
            'players': sorted_players,
            'waypoints': waypoints,
            'game_state': game_state, # AJAX cevabına ekle
            'remaining_seconds': remaining_seconds_ajax, # AJAX cevabına ekle
            # Eski remaining_seconds kaldırıldı, yerine yukarıdakiler geldi
        })
    # --- AJAX Response için Güncelleme Bitiş ---

    # --- Normal Render Context Güncelleme ---
    context = {
        'players': sorted_players,
        'game': game,
        'creator_id': creator_id,
        'waypoints': waypoints,
        # 'now', 'remaining_td' artık doğrudan kullanılmayacak
        'game_state': game_state,
        'remaining_seconds_until_end': remaining_seconds_until_end, # Sadece çalışan oyunlar için anlamlı
    }
    return render(request, 'game/monitor.html', context)
    # --- Normal Render Context Güncelleme Bitiş ---
    
def results(request, game_id, creator_id):
    game = get_object_or_404(Game, pk=game_id, game_creator_id=creator_id)
    user_scores = UserScore.objects.filter(game=game).select_related('user')

    players = [{
        'id': score.user.user_id,
        'name': score.user.username,
        'score': score.total_score,
        'disqualified': score.is_disqualified
    } for score in user_scores]

    sorted_players = sorted(players, key=lambda p: p['score'], reverse=True)

    available_colors = ['cyan', 'red', 'purple', 'yellow']
    for i, p in enumerate(sorted_players):
        p['icon'] = available_colors[i % len(available_colors)]

    all_times = UserLocation.objects.filter(game=game) \
                    .order_by('time_stamp') \
                    .values_list('time_stamp', flat=True)
    speed_data = {'labels': [], 'players': []}
    if all_times:
        first_time = all_times[0]
        last_time  = all_times.reverse()[0]
        speed_data['labels'] = [
            first_time.strftime('%H:%M'),
            last_time.strftime('%H:%M'),
        ]

    for p in sorted_players:
        locs = UserLocation.objects.filter(game=game, user__user_id=p['id']) \
                                   .order_by('time_stamp')
        if locs:
            speeds = [locs.first().speed or 0, locs.last().speed or 0]
        else:
            speeds = [0, 0]
            
        speed_data['players'].append({
            'name':   p['name'],
            'speeds': speeds,
            'icon':   p['icon']
        })
        
    return render(request, 'game/results.html', {
        'players': sorted_players,
        'game': game,
        'date':  game.start_date_time.strftime('%Y-%m-%d %H:%M'),
        'winner':  sorted_players[0] if sorted_players else None,
        'speed_data': json.dumps(speed_data),
    })

def calculate_scores(request, game_id, creator_id):
    game = get_object_or_404(Game, pk=game_id, game_creator_id=creator_id)
    calculate_scores_for_game(game)
    return redirect('results', game_id=game_id, creator_id=creator_id)