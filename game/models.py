from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry

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
    invite_id = models.CharField(max_length=10)
    game_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')

    def __str__(self):
        return self.game_name

class Waypoint(models.Model):
    waypoint_id = models.BigAutoField(primary_key=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, related_name='waypoints')
    waypoint_name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()
    height = models.FloatField()
    hint = models.TextField()
    question = models.TextField()
    answer = models.TextField()
    ques_dif_level = models.FloatField()
    waypoint_geom = models.PointField()
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
        self.waypoint_buffer = self.create_buffer(buffer_distance=5)
        super().save(*args, **kwargs)
    
class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='locations')
    lat = models.FloatField()
    lon = models.FloatField()
    location_geom = models.PointField()

    def __str__(self):
        return  self.user_id

class UserDistance(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='distances')
    game= models.ForeignKey(Game, on_delete=models.CASCADE, related_name='distances')
    distance = models.FloatField()
    time_diff = models.FloatField() # birimlerine göre değiştirilebilir sadece bu değil bütün floatfieldlar için geçerli

    def __str__(self):
        return self.user

class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    location_score = models.FloatField()
    time_score = models.FloatField()
    ques_score = models.FloatField()
    total_score = models.FloatField()
    is_disqualified = models.BooleanField(default=False)

    def __str__(self):
        return self.user
