from django.db import models
from api.simulations.events.models import BaseEvent
from api.simulations.events.models import TimeseriesEvent
from api.simulations.events.models import LizardReference
from api.simulations.events.models import LizardRaster
from api.threedimodels.models import BoundaryCondition


class TimeseriesBoundary(TimeseriesEvent):

    boundary_condition = models.ForeignKey(
        BoundaryCondition, on_delete=models.CASCADE)
    # TODO: unit must be dynamic. that is, depending on the type of the boundary
    # units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")



