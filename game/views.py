from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Game, UserScore, UserLocation

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.
# game/views.py
from django.http import HttpResponse

def auth(request):
    return render(request, 'game/auth.html')

# Kullanıcı girişi
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")  # Giriş başarılıysa ana sayfaya git
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")
            return redirect("auth_page")  # Tekrar auth sayfasına

    return redirect("auth_page")

# Kullanıcı kaydı
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Şifreler eşleşmiyor.")
            return redirect("auth_page")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten var.")
            return redirect("auth_page")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu e-posta zaten kayıtlı.")
            return redirect("auth_page")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
        return redirect("auth_page")

    return redirect("auth_page")











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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'players': sorted_players})
    
    return render(request, 'game/monitor.html', {'players': sorted_players, 'game': game})