from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from game.models import User, Game, Waypoint, UserLocation, UserScore

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        return super().update(instance, validated_data)

class GameSerializer(serializers.ModelSerializer):
      game_creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

      class Meta:
          model = Game
          fields = '__all__'
          read_only_fields = ['invite_id']

class WaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waypoint
        fields = '__all__'

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = [
            'id', 'user', 'game',
            'lat', 'lon', 'location_geom',
            'time_stamp', 'time_diff', 'distance', 'speed',
        ]
        read_only_fields = [
            'time_stamp', 'time_diff', 'distance', 'speed',
        ]

# class UserDistanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserDistance
#         fields = '__all__'

class UserScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserScore
        fields = '__all__'
