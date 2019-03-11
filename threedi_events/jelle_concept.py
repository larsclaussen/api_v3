




from django.db import models
from django.contrib.auth.models import User
from dataclasses import dataclass
from typing import List
from datetime import datetime
import serialization


class Organization(object):
    pass


@dataclass
class Event:
    offset: float
    duration: float


@dataclass
class RadarRainEvent(Event):
    layer: str  # The layer of the radar rain event
    resolution: float  # Time resolution of the radar rain
    multiplier: float  # Value to multiply radarEvent by


@dataclass
class ConstantRainEvent(Event):
    intensity: float  # Value to multiply radarEvent by


@dataclass
class Simulation1:
    events: List[Event]


serialization.register(Event)
serialization.register(RadarRainEvent)
serialization.register(ConstantRainEvent)
serialization.register(Simulation1)


class DataclassQueryset(models.QuerySet):
    def to_dataclasses(self):
        queryset = self.model.get_dataclass_queryset(self)
        return [item.dataclass for item in queryset]


class DataclassManager(models.Manager):
    def get_queryset(self):
        return DataclassQueryset(self.model, using=self._db)


class DataclassModel(models.Model):
    # Custom manager
    objects = DataclassManager()

    @property
    def dataclass(self):
        raise NotImplementedError("Function should be implemented!!")

    @classmethod
    def get_dataclass_queryset(cls, queryset):
        # Override this method if you need todo select related, only or
        # other queryset actions
        return queryset

    class Meta:
        abstract = True


class Simulation(DataclassModel):
    # organization = models.ForeignKey(Organization)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Meta fields
    created = models.DateTimeField(auto_now_add=True)

    @property
    def dataclass(self):
        return Simulation1(
            events=self.apievent_set.all().to_dataclasses()
        )


class APIEvent(DataclassModel):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    active_from = models.DateTimeField()
    active_till = models.DateTimeField()

    @classmethod
    def get_dataclass_queryset(cls, queryset):
        return queryset.select_related(
            'apiradarrainevent', 'apiconstantrainevent')

    @property
    def dataclass(self):
        if hasattr(self, 'apiradarrainevent'):
            event = self.apiradarrainevent.dataclass
        elif hasattr(self, 'apiconstantrainevent'):
            event = self.apiconstantrainevent.dataclass
        else:
            event = None

        return event


class APIConstantRainEvent(APIEvent):
    """
    API Radar rain event model
    """
    start = models.DateTimeField(null=True)  # Null is start of simulation
    intensity = models.FloatField()

    @property
    def dataclass(self):
        return ConstantRainEvent(
            self.active_from.timestamp(),
            self.active_till.timestamp(),
            self.intensity,
        )


class APIRadarRainEvent(APIEvent):
    """
    API Radar rain event model
    """
    multiplier = models.FloatField()
    start = models.DateTimeField(null=True)  # Null is start of simulation
    layer = models.CharField(max_length=64)

    # Fill this in automatically when checking if the layer exists
    resolution = models.FloatField()

    @property
    def dataclass(self):
        return RadarRainEvent(
            self.active_from.timestamp(),
            self.active_till.timestamp(),
            self.layer,
            self.resolution,
            self.multiplier,
        )

    @classmethod
    def to_dataclass(cls, queryset):
        # Optional: Strip unnecessary fields here!!!
        # TODO: fix the 'get' case

        rain_events = []
        for rain_event in queryset:
            rain_events.append(
                rain_event.dataclass
            )

        return rain_events


def get_data():
    User
    if Simulation.objects.count() == 0:
        user = User.objects.all()[0]
        simulation = Simulation.objects.create(
            owner=user)
    else:
        simulation = Simulation.objects.all()[0]

    if APIRadarRainEvent.objects.count() == 0:
        event = APIRadarRainEvent.objects.create(
            simulation=simulation,
            active_from=datetime.now(),
            active_till=datetime.now(),
            multiplier=3.0,
            resolution=300,
            start=datetime.now(),
            layer='d6c2347d-7bd1-4d9d-a1f6-b342c865516f')
    else:
        event = APIRadarRainEvent.objects.all()[0]

    return simulation, event


# sim, event = get_data()
