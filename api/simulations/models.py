from django.db import models
from api.threedimodels.models import ThreediModel

import uuid


class Simulation(models.Model):
    # organisation_uuid = models.ForeignKey(Organisation,
    #     on_delete=models.CASCADE,
    # )
    # user = models.ForeignKey()
    threedi_model = models.ForeignKey(ThreediModel, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    start = models.DateTimeField()
    end = models.DateTimeField()
    name = models.CharField(max_length=80)  # auto generate if not given
    created = models.DateTimeField(auto_now_add=True)


class SimulationState(models.Model):
    # TODO define good choices
    STATE_CHOICES = (
        ('created', 'created'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('crashed', 'crashed'),
    )
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, choices=STATE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

