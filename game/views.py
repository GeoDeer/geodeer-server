from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import Game, UserScore, UserLocation
from .models import User

def auth(request):
    return render(request, 'game/auth.html')

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

def create(request):
    return render(request, 'game/create.html')

def monitor(request, pk):
    game = get_object_or_404(Game, pk=pk)

    user_scores = UserScore.objects.filter(game=game).select_related('user')
    
    players = []
    for score in user_scores:
        uid = score.user.user_id
        
        user_locs = list(UserLocation.objects.filter(game=game, user=score.user).order_by('-pk')[:6])
        user_locs.reverse()  
        
        latest = user_locs[-1] if user_locs else None
       
        path = [{'lat': loc.lat, 'lng': loc.lon} for loc in user_locs]
        
        player = {
            'id': uid,
            'name': score.user.username,
            'score': score.total_score,
            'lat': latest.lat if latest else None,
            'lng': latest.lon if latest else None,
            'path': path,
        }
        players.append(player)
   
    sorted_players = sorted(players, key=lambda p: p['id'])
    available_colors = ['cyan', 'red', 'purple', 'yellow']
    
    for i, player in enumerate(sorted_players):
        player['icon'] = available_colors[i % len(available_colors)]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'players': sorted_players})
    
    return render(request, 'game/monitor.html', {'players': sorted_players, 'game': game})
