from django.db import models
from api.threedimodels.models import ThreediModel
from api.simulations.models import Simulation
from django.contrib.postgres.fields import ArrayField



class BaseEvent(models.Model):
    simulation = models.ForeignKey(Simulation,
        on_delete=models.CASCADE,
    )
    active_from	= models.IntegerField(help_text="Start of event in simulation in seconds")
    active_till = models.IntegerField(null=True, help_text="End of event in simulation in seconds")


# todo: store as binary file? size? needs to be chunked?
class TimeseriesEvent(BaseEvent):
    # todo: we want this format [(x,x),(x,x),(x,x)]
    values = ArrayField(models.FloatField(), size=300)  # TODO what is a realistic size constraint?
    interpolate = models.BooleanField(default=False)


class LizardReference(BaseEvent):
    """reference an event hosted on a specific location"""
    # base class holds the type information
    reference_uuid = models.CharField(max_length=40)
    start = models.DateTimeField()


class LizardRaster(LizardReference):

    interval = models.IntegerField()
    origin_offset = models.IntegerField()
    store_path = models.CharField(max_length=80)
    # check how to use dynamic managers
    multiplier = models.FloatField(default=1.0)
