from django.db import models
from api.simulations.events.models import BaseEvent
from api.simulations.events.models import TimeseriesEvent
from api.threedimodels.models import Raster


class RasterEditEvent(BaseEvent):
    raster = models.ForeignKey(Raster, on_delete=models.CASCADE)
    value = models.FloatField(
        help_text="Absolute height (in meters) to use for the polygon")
    polygon_wkt = models.PolygonField(
        srid=4326, help_text="The polygon to use for the raster edit in WKT format, new must be WGS84")


