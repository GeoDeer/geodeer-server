from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry

import random
from datetime import datetime
from django.utils import timezone
from django.contrib.gis.geos import Point

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=12, unique=True)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    
class Game(models.Model):
    game_id = models.BigAutoField(primary_key=True)
    game_name = models.CharField(max_length=255)
    start_date_time = models.DateTimeField()
    number_of_players = models.FloatField()
    time = models.FloatField()
    invite_id = models.CharField(max_length=10, blank=True)
    game_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')

    def __str__(self):
        return self.game_name

    def format_two_digits(self, value):
        return str(value).zfill(2)[-2:]

    def generate_invite_id(self):
        game_id_part = self.format_two_digits(self.game_id)
        date_part = self.format_two_digits(self.start_date_time.day)
        rand_part = self.format_two_digits(random.randint(0, 9999))
        return f"#{game_id_part}{date_part}{rand_part}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.invite_id:
            self.invite_id = self.generate_invite_id()
            super().save(update_fields=['invite_id'])
            
class Waypoint(models.Model):
    waypoint_id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='waypoints')
    waypoint_name = models.CharField(max_length=255)
    is_last = models.BooleanField(default=False)
    lat = models.FloatField()
    lon = models.FloatField()
    height = models.FloatField(null=True, blank=True)
    hint = models.TextField()
    question = models.TextField()
    answer = models.TextField()
    ques_dif_level = models.FloatField()
    waypoint_geom = models.PointField(null=True, blank=True)
    waypoint_buffer = models.PolygonField(null=True, blank=True)

    def __str__(self):
        return self.waypoint_name

    def create_buffer(self, buffer_distance=5):
        geom = self.waypoint_geom
        if geom.srid is None:
            raise ValueError("SRID not defined.")

        geom_proj = GEOSGeometry(geom.wkt, geom.srid)
        geom_proj.transform(3857)

        buff = geom_proj.buffer(buffer_distance, quadsegs=8)
        buff.transform(4326)
        return buff

    def save(self, *args, **kwargs):
        if not self.waypoint_geom:
            self.waypoint_geom = GEOSGeometry(f'POINT({self.lon} {self.lat})', srid=4326)
        self.waypoint_buffer = self.create_buffer(buffer_distance=5)

        super().save(*args, **kwargs)
       
        self.update_is_last_flag()
        self.create_question()

    def update_is_last_flag(self):
        waypoints = Waypoint.objects.filter(game=self.game)

        last_waypoint = waypoints.order_by('-waypoint_id').first()

        for wp in waypoints:
            wp_is_last = (wp.pk == last_waypoint.pk)
            if wp.is_last != wp_is_last:
                wp.is_last = wp_is_last
                super(Waypoint, wp).save(update_fields=['is_last'])

    def create_question(self):
        if not Question.objects.filter(waypoint=self).exists():  
            Question.objects.create(
                game=self.game,
                user=self.game.game_creator,  
                waypoint=self,
                ques_dif_level=self.ques_dif_level,  
                answer_time=0, 
                is_correct=False  
            )
    
class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='locations')
    lat = models.FloatField()
    lon = models.FloatField()
    location_geom = models.PointField(blank=True, null=True)
    time_stamp = models.DateTimeField(default=timezone.now)
    time_diff = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.location_geom and self.lat is not None and self.lon is not None:
            self.location_geom = Point(self.lon, self.lat, srid=4326)

        is_new = self.pk is None
        if is_new:
            previous = (
                UserLocation.objects
                .filter(user=self.user, game=self.game)
                .order_by('-time_stamp')
                .first()
            )
            if previous:
                delta = self.time_stamp - previous.time_stamp
                self.time_diff = delta.total_seconds() / 3600.0
                
                prev_geom = previous.location_geom.clone()
                prev_geom.srid = 4326
                prev_geom.transform(3857)

                curr_geom = self.location_geom.clone()
                curr_geom.srid = 4326
                curr_geom.transform(3857)

                self.distance = prev_geom.distance(curr_geom)

                if self.time_diff and self.time_diff > 0:
                    self.speed = (self.distance / 1000) / self.time_diff
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Location for {self.user.username} at {self.time_stamp}"


# class UserDistance(models.Model):
#     user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='distances')
#     game= models.ForeignKey(Game, on_delete=models.CASCADE, related_name='distances')
#     distance = models.FloatField()
#     time_diff = models.FloatField() # birimlerine göre değiştirilebilir sadece bu değil bütün floatfieldlar için geçerli

#     def __str__(self):
#         return self.user

class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    location_score = models.FloatField()
    time_score = models.FloatField()
    ques_score = models.FloatField()
    total_score = models.FloatField()
    is_disqualified = models.BooleanField(default=False)

    def __str__(self):
        return f"Score for {self.user.username} in {self.game.game_name}" 

class Question(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    waypoint = models.ForeignKey(Waypoint, on_delete=models.CASCADE, related_name='questions')
    ques_dif_level = models.FloatField() 
    answer_time = models.FloatField(default=0)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.ques_dif_level and self.waypoint:
            self.ques_dif_level = self.waypoint.ques_dif_level 

        if not self.game:
            self.game = self.waypoint.game  
        if not self.user:
            self.user = self.waypoint.game.game_creator 

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Question for {self.user.username} at {self.waypoint.waypoint_name}"
