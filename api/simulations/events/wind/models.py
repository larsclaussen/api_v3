from django.db import models
from api.simulations.events.models import BaseEvent
from api.simulations.events.models import TimeseriesEvent


class Wind(BaseEvent):
    speed = models.PositiveSmallIntegerField(help_text="speed in m/s (0-120)")
    direction = models.PositiveSmallIntegerField(help_text="direction in degrees (0-360) from north - meteorlogical standard")
    drag_coefficient = models.PositiveSmallIntegerField(help_text="drag coefficient (0-100)")


# todo: complexer than other timeseries because has lot of paramters, e.g [(x,x,x,x), (x,x,x,x), (x,x,x,x)]
# class TimeseriesWind(TimeseriesEvent):
#     pass
