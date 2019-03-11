from django.db import models
# from lizard_auth_client.models import Organisation
from .event_utils import get_offset
from .event_utils import get_duration
from .event_utils import _current_request_dt
from datetime import datetime
from dataclasses import dataclass
import uuid
from django.contrib.postgres.fields import ArrayField

# class EventManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(role='A')
from django.core.validators import MaxValueValidator, MinValueValidator

def test():
    from datetime import datetime
    from threedi_events.models import RainRadarEvent
    from threedi_events.models import SimulationMeta
    import pytz
    start = datetime(2016, 10, 20, 13, 0, tzinfo=pytz.UTC)
    end = datetime(2016, 10, 20, 15, 0, tzinfo=pytz.UTC)
    active_from = datetime(2016, 10, 20, 13, 0, tzinfo=pytz.UTC)
    active_till = datetime(2016, 10, 20, 14, 0, tzinfo=pytz.UTC)
    sim_data = SimulationMeta(model_slug='my-model', start=start, end=end, simulation_name='ha')
    raev = RainRadarEvent(simulation=sim_data, active_from=active_from, active_till=active_till, type='radar', start=start)

@dataclass
class RainRadar:
    """
    Radar rain event internal data structure
    """
    multiplier: float  # value to multiply the radar data by
    layer_name: bytes  # name of the radar layer
    model_slug: bytes  # Slug of the 3Di model
    request_start: datetime  # datetime object of the radar start time
    origin_offset: int
    start_timestep: int  # Start timestep in simulation
    end_timestep: int  # End timestep or None if no end timestep
    resolution: float  # resolution of the values of the event


class DEMMeta(models.Model):
    projection
    epsg
    extent
    dimensions    


class ModelMeta(models.Model):
    dem_meta = models.ForeignKey(DEMMeta, 
        on_delete=models.CASCADE,    
    )
    extent_one_d = 
    extent_zero_d
    nodes_count = 
    lines_count = 


class Breaches(models.Model):
    model_meta = models.ForeignKey(
        ModelMeta, on_delete=models.CASCADE
    )
    connected_pnt_id = models.IntegerField()





class SimulationMeta(models.Model):
    organisation_uuid = models.ForeignKey(Organisation,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey()
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    model_slug = models.SlugField(max_length=120)
    start = models.DateTimeField()
    end = models.DateTimeField()
    name = models.CharField(max_length=80)
    email = models.EmailField()


class BaseEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ('timeseries', 'timeseries'),
        ('constant', 'constant'),
        ('radar', 'radar'),
        ('design', 'design'),
    )
    simulation = models.ForeignKey(SimulationMeta, 
        on_delete=models.CASCADE,
    )
    active_from	= models.DateTimeField(help_text="Start of event in simulation (ISO 8601 format)")
    active_till = models.DateTimeField(null=True, help_text="End of event in simulation (ISO 8601 format)")
    type = models.CharField(max_length=80, choices=EVENT_TYPE_CHOICES)

    @property
    def duration(self):
        _duration = None
        if self.active_till is not None:
            _duration = get_duration(self.active_from, self.active_till)
        return _duration


class TimeseriesEvent(BaseEvent):
    values = ArrayField(models.FloatField(), size=300)  # TODO what is a realistic size constraint?

    @property
    def timeseries(self):
        start_timestep = get_offset(self.simulation.start, self.active_from)
        _timeseries = [(x[0] + start_timestep, x[1]) for x in self.values]
        if self.duration:
            end_timestep = start_timestep + self.duration
            _timeseries.extend([(end_timestep, 0)])
        return _timeseries


class RainDesignEvent(BaseEvent):

    number = models.PositiveSmallIntegerField(null=False)


class RainLocalEvent(TimeseriesEvent):

    point = models.PointField(srid=4326)
    diameter = models.IntegerField()





class ReferenceEvent(BaseEvent):
    """reference an event hosted on a specific location"""
    # base class holds the type information
    reference = models.CharField(max_length=80, help_text="reference")
    reference_uuid = models.CharField(max_length=40)
    start = models.DateTimeField()   

class LizardRadarEvent(ReferenceEvent):

    multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.5), MaxValueValidator(5.0)])
    interval = models.IntegerField()
    # last_value_timestamp = models.IntegerField(),  # TODO still needed?
    origin_offset = models.IntegerField()
    store_path = models.CharField(max_length=80)
    # check how to use dynamic managers
    objects = # some custom manager, e.g LizardRadarManager() 


class ReferenceTimeseriesEvent(TimeseriesEvent):
    """reference a timeseries hosted on a specific location"""
    start = models.DateTimeField()   
    objects = # some custom manager, e.g LizardTimeseriesManager() 


class ReferenceRainEvent(BaseEvent):

    multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.5), MaxValueValidator(5.0)])
    layer = models.UUIDField(help_text="UUID of the raster-store rain layer")
    start =	models.DateTimeField(help_text="The radar rain start time in ISO 8601 format")
    interval = models.IntegerField()
    source = models.CharField(max_length=80)  # new: same as timeseries, e.g lizard
    # last_value_timestamp = models.IntegerField(),  # TODO still needed?
    origin_offset = models.IntegerField()
    store_path = models.CharField(max_length=80)
    # check how to use dynamic managers
    objects = LizardReferenceManager() 

    @property
    def datacls(self):
        resolution = 300
        origin_offset = 0
        start_timestep = get_offset(self.simulation.start, self.active_from)
        if self.duration:
            end_timestep = start_timestep + self.duration
        else:
            end_timestep = None
        request_start = _current_request_dt(
            self.start, resolution, origin_offset)

        return RainRadar(
            multiplier=self.multiplier, 
            layer_name=self.layer,
            model_slug=self.simulation.model_slug,
            request_start=request_start,
            origin_offset=origin_offset,
            start_timestep=start_timestep,
            end_timestep=end_timestep,
            resolution=resolution
        )




class LizardReferenceManager(models.Manager):

    def get_ref_info(self, layer, username):
        """
        Validate and return layer info (interval and store path) from Lizard.
        :param layer: rain layer (= UUID in Lizard)
        :param username: name of the user requesting info
        :
        """
        resp_data = self.make_layer_request(layer, username)
        # Obstype code check
        # NOTE: observation type isn't a required field
        obstype = resp_data.get('observation_type', {})
        obstype_code = obstype.get('code')
        if obstype_code not in settings.PRECIPITATION_CODES:
            raise serializers.ValidationError(
                "Invalid layer (observation type: %s)" % obstype_code)

        interval = resp_data['interval']
        dt_format = '%H:%M:%S'
        try:
            t_interval = datetime.datetime.strptime(interval, dt_format)
            t_initial = datetime.datetime.strptime("00:00:00", dt_format)
        except ValueError:
            raise serializers.ValidationError(
                "Can't convert interval %s" % interval)

        interval = (t_interval - t_initial).total_seconds()
        store_path = resp_data['wms_info']['layer']
        origin_offset = iso8601.parse_date(resp_data["origin"]).minute
        last_value_timestamp = resp_data['last_value_timestamp']
        # add last_value_timestamp
        return dict(
            store_path=store_path,
            interval=interval,
            # last_value_timestamp=last_value_timestamp,  # TODO still needed?
            origin_offset=origin_offset,
        )

    @staticmethod
    def generate_lizard_auth_object(username):
        """Generate a JWT auth object with 'username' and 'exp' payload."""
        expiry_dt = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=JWT_EXPIRY_SECONDS)
        payload = dict(username=username, exp=expiry_dt)
        token = JWTAuthentication.encode(
            payload, settings.LIZARD_SHARED_SECRET,
            algorithm='HS256').decode('ascii')
        return JWTAuthRequest(token)

    @staticmethod
    def make_layer_request(layer, username):
        """
        :param layer: rain layer (= UUID in Lizard)
        :param username: name of the user requesting info
        :return: dict containing response data from lizard
        """
        auth = self.generate_lizard_auth_object(username)
        # Make request with JWT auth
        url = LIZARD_RASTERS_URL_TEMPLATE.format(uuid=layer)
        resp = request_and_handle_errors(url, auth=auth)
        resp_data = resp.json()
        return resp_data

    def create_event(self, layer, user):
        layer_info = get_layer_info_from_lizard(layer, user.username)
        new_event = self.model(**layer_info)
        new_event.save()
        return new_event
 



class RainTimeseriesEvent(TimeseriesEvent):
    units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")
    interpolate = models.BooleanField()  # TODO also desirable here?


class WindEvent(BaseEvent):
    speed = models.PositiveSmallIntegerField(help_text="speed in m/s (0-120)")
    direction = models.PositiveSmallIntegerField(help_text="direction in degrees (0-360) from north - meteorlogical standard")
    drag_coefficient = models.PositiveSmallIntegerField(help_text="drag coefficient (0-100)")    


class TimeseriesSourcesSinksEvent(TimeseriesEvent):
    units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")
    interpolate = models.BooleanField()

class SourcesSinksConstantEvent(TimeseriesEvent):
    units = models.CharField(max_length=12, help_text="'m/s' (only option for now)")
    interpolate = models.BooleanField()
    # values then should be something like [(0, 0.0007)]

class SourcesSinksReferenceEvent(ReferenceEvent):
    # see LizardRadarEvent for possible fields


class SourcesSinksPointEvent(TimeseriesEvent):
    point = models.PointField(srid=4326)


class DischargePointEvent(TimeseriesEvent):
    point = models.PointField(srid=4326)


class BreachEvent(BaseEvent):
    connected_pnt_id = models.IntegerField(help_text="id from the 'connected_pnt' database table")
    # duration = help_text="duration till maximum depth in seconds"
    start =	models.DateTimeField(help_text="moment of breach in ISO 8601 format")
    width =	models.FloatField(help_text="initial width in meters")


class RasterEditEvent(BaseEvent):
    layer = models.CharField(max_length=120, help_text="Layername, for now only 'dem' is allowed") 
    value = models.FloatField(help_text="Absolute height (in meters) to use for the polygon")
    polygon_wkt = models.PolygonField(srid=4326, help_text="The polygon to use for the raster edit in WKT format, new must be WGS84")

class BoundaryCondition(TimeseriesEvent):
    BOUNDARY_TYPE_CHOICES = (
        ('waterlevel', 'waterlevel'),
        ('discharge', 'discharge'),
    )
    type = models.CharField(max_length=20, choices=BOUNDARY_TYPE_CHOICES)
    boundary_id = models.IntegerField()


class StructureControlEvent(TimeseriesEvent):
    structure_id = models.IntegerField()
    structure_type = models.CharField(max_length=50)
    property_name = models.CharField(max_length=50)

class FloodfillEvent(BaseEvent):
    point = models.PointField(srid=4326)
    waterlevel = models.FloatField()
    is_absolute = models.BooleanField(
        blank=False, 
        help_text="Apply the waterlevel of the event either as absolute or relative value"
    )    
    




# @dataclass
# class StageRainRadar(BaseStage):
#     _start: datetime
#     _active_from: datetime
#     multiplier: float
#     layer_name: bytes  # name of the radar layer
#     _request_start: datetime
#     model_slug: bytes  # Slug of the 3Di model
#     resolution: int
#     origin_offset: int
#     start_timestep: int = field(init=False)
#     end_timestep: int = field(init=False)
#     request_start: int = field(init=False)
#     uid: bytes = field(init=False)
#     _active_till: datetime = None

#     def __post_init__(self):
#         self.start_timestep = get_offset(self._start, self._active_from)
#         _duration = None
#         if self._active_till is not None:
#             _duration = get_duration(self._active_from, self._active_till)
#         if _duration:
#             self.end_timestep = self.start_timestep + _duration
#         else:
#             self.end_timestep = None
#         self.request_start = _current_request_dt(
#             self._request_start, self.resolution, self.origin_offset)




class Test:
    def __init__(self): 
        self.b = None
        self.c = 1
        self.d = ''


def has_attrs(inst, *args):
    """
    checks if the instance has all attributes 
    as specified in *args and if they not falsy   
    
    :param inst: obj instance
    :param args: attribute names of the object
    """
    for a in args:
        try:
            if not getattr(inst, a, None)
                return False
        except AttributeError:
            return False
    return True

@property
def _action_table(self):
    _action_table = self.action_table

    if hasattr(self, "action_table" ) and self.action_table:
        levels = self.action_table.split('#')[0]
        capacities_list = str(self.action_table.split('#')[1]).split(';')
        capacities = ";".join([str(float(q)*factor)
                                for q in capacities_list])
        _action_table = "#".join([levels, capacities]) 
    return _action_table   