from django.db import models
from api.simulations.events.models import BaseEvent
from api.simulations.events.models import TimeseriesEvent
from api.simulations.events.models import LizardReference
from api.simulations.events.models import LizardRaster


class LizardTimeseriesRain(LizardReference):
    pass


class LizardRasterRain(LizardRaster):
    pass



class DesignRain(BaseEvent):

    number = models.PositiveSmallIntegerField(null=False)


class LocalRain(TimeseriesEvent):

    point = models.PointField(srid=4326)
    diameter = models.IntegerField()

# todo: implement constant rain as a timeseries with a single value pair --> will get its own API view
class TimeseriesRain(TimeseriesEvent):
    units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")


