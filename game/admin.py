from django.contrib import admin
from .models import User, Game, Waypoint, UserScore, UserLocation
# Register your models here.

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Waypoint)
admin.site.register(UserScore)
admin.site.register(UserLocation)
# admin.site.register(UserDistance)