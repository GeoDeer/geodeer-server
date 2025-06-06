from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from game.models import User   # senin özel modelin
import logging

logger = logging.getLogger(__name__)

# Diğer importlarınız (serializer, modeller vb.)
from game.models import *
from .serializer import (
    UserSerializer,
    GameSerializer,
    WaypointSerializer,
    UserLocationSerializer,
    UserScoreSerializer,
    QuestionSerializer,
)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def api_login(request):

    print(">>> /api/login/ body:", request.body) 
    print(">>> /api/login/ data:", request.data)
    
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'detail': 'Kullanıcı adı veya şifre hatalı.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not check_password(password, user.password):
        return Response({'detail': 'Kullanıcı adı veya şifre hatalı.'},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'user_id': user.user_id,   # özel modelde id alanının adı böyleyse
        'username': user.username,
        'email':    user.email,
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def api_register(request):
    """
    POST ile gelen {username, email, password, password2} verilerini alır,
    doğrulama yapar, yeni kullanıcı oluşturur.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    pw1 = request.data.get('password')
    pw2 = request.data.get('password2')

    if not all([username, email, pw1, pw2]):
        return Response(
            {'detail': 'Tüm alanlar zorunlu.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if pw1 != pw2:
        return Response(
            {'detail': 'Şifreler uyuşmuyor.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Bu kullanıcı adı zaten kayıtlı.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'Bu e-posta zaten kayıtlı.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(pw1)
    )
    return Response(
        {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
def get_user(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(user_id=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_game(request):
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_game(request):
    serializer = GameSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def game_detail(request, pk):
    try:
        game = Game.objects.get(game_id=pk)
    except Game.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GameSerializer(game)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GameSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_waypoint(request):
    waypoints = Waypoint.objects.all()
    serializer = WaypointSerializer(waypoints, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_waypoint(request):
    serializer = WaypointSerializer(data=request.data)
    if serializer.is_valid():
        waypoint = serializer.save()
        return Response(WaypointSerializer(waypoint).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def waypoint_detail(request, pk):
    try:
        waypoint = Waypoint.objects.get(waypoint_id=pk)
    except Waypoint.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WaypointSerializer(waypoint)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WaypointSerializer(waypoint, data=request.data)
        if serializer.is_valid():
            waypoint = serializer.save()
            return Response(WaypointSerializer(waypoint).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        waypoint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_user_location(request):
    user_locations = UserLocation.objects.all()
    serializer = UserLocationSerializer(user_locations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user_location(request):
    print("→ create_user_location payload:", request.data)  
    ser = UserLocationSerializer(data=request.data)
    if not ser.is_valid():
        print("!! serializer errors:", ser.errors)    
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    instance = ser.save()                          
    print("→ instance.id after save:", instance.id)  
    out_ser  = UserLocationSerializer(instance)    
    return Response(out_ser.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def user_location_detail(request, pk):
    try:
        user_location = UserLocation.objects.get(id=pk)
    except UserLocation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserLocationSerializer(user_location)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserLocationSerializer(user_location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user_location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET'])
# def get_user_distance(request):
#     user_distances = UserDistance.objects.all()
#     serializer = UserDistanceSerializer(user_distances, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def create_user_distance(request):
#     serializer = UserDistanceSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def user_distance_detail(request, pk):
#     try:
#         user_distance = UserDistance.objects.get(id=pk)
#     except UserDistance.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = UserDistanceSerializer(user_distance)
#         return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = UserDistanceSerializer(user_distance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         user_distance.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_user_score(request):
    user_scores = UserScore.objects.all()
    serializer = UserScoreSerializer(user_scores, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user_score(request):
    serializer = UserScoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_score_detail(request, pk):
    try:
        user_score = UserScore.objects.get(id=pk)
    except UserScore.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserScoreSerializer(user_score)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserScoreSerializer(user_score, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user_score.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
def get_question(request):
    questions = Question.objects.all() 
    serializer = QuestionSerializer(questions, many=True) 
    return Response(serializer.data)

@api_view(['POST'])
def create_question(request):
    serializer = QuestionSerializer(data=request.data)  
    if serializer.is_valid(): 
        serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)  
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['GET', 'PUT', 'DELETE'])
def question_detail(request, waypoint_id):
    try:
        question = Question.objects.get(waypoint_id=waypoint_id)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@csrf_exempt                              # 1) CSRF filtresini devre dışı
@authentication_classes([])               # 2) Session / Token auth yok
@permission_classes([AllowAny])           # 3) Her isteğe izin ver
@api_view(['POST'])
def join_game(request):
    game_id = request.data.get('game')
    user_id = request.data.get('user')
    if not game_id or not user_id:
        return Response({'detail': 'game ve user alanı zorunlu'}, status=400)

    try:
        game = Game.objects.get(game_id=game_id)
        user = User.objects.get(user_id=user_id)
    except (Game.DoesNotExist, User.DoesNotExist):
        return Response({'detail': 'Game veya User bulunamadı'}, status=404)

    score, _ = UserScore.objects.get_or_create(
        user=user, game=game, defaults={'total_score': 0}
    )
    return Response(UserScoreSerializer(score).data, status=201)