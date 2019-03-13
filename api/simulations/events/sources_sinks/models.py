from django.db import models
from api.simulations.events.models import BaseEvent
from api.simulations.events.models import TimeseriesEvent
from api.simulations.events.models import LizardReference
from api.simulations.events.models import LizardRaster


# todo: implement constant source and sinks as a timeseries with a single value pair --> will get its own API view
class TimeseriesSourcesSinks(TimeseriesEvent):
    units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")


class LizardTimeseriesSourcesSinks(LizardReference):
    pass


class LizardRasterSourcesSinks(LizardRaster):
    pass


class PointSourcesSinks(TimeseriesEvent):
    point = models.PointField(srid=4326)

