from django.db import models
from api.simulations.events.models import BaseEvent
from api.threedimodels.models import Breach


class BreachEvent(BaseEvent):
    breach = models.ForeignKey(Breach, on_delete=models.CASCADE)
    duration = models.IntegerField(help_text="duration till maximum depth in seconds")
    start =	models.IntegerField(help_text="moment of breach in seconds")
    width =	models.FloatField(help_text="initial width in meters")
