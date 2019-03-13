from django.db import models
import uuid


class Repository(models.Model):

    # organisation = models.ForeignKey(Organisation, blank=True, null=True)
    slug = models.SlugField(
        help_text='do not change', max_length=255, unique=True)


class Revision(models.Model):
    """
    Because other models have a relation with this table but the hash
    is not (yet) known at all times (once the repo still has to be
    cloned for instance) dummy defaults are defined
    """
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    number = models.IntegerField(default=0, null=False, blank=False)
    hash = models.CharField(
        default='', null=False, blank=False, max_length=200,
        help_text='unique identifier for changeset'
    )
    is_pinned = models.BooleanField(null=False, blank=False, default=False)


class InpyVersion(models.Model):

    threedi_version = models.CharField(max_length=80)
    threedicore_version = models.CharField(max_length=80)


class ModelMeta(models.Model):
    extent_two_d = models.LineString(srid=4326)
    extent_one_d = models.LineString(srid=4326)
    extent_zero_d = models.LineString(srid=4326)
    nodes_count = models.IntegerField(null=True, blank=True)
    lines_count = models.IntegerField(null=True, blank=True)


class Raster(models.Model):
    # todo: collect all names from code base
    RASTER_NAME_CHOICES = (
        ('dem', 'dem'),
        ('infiltration', 'infiltration'),
        ('friction', 'friction'),
    )
    name = models.CharField(max_length=40, choices=RASTER_NAME_CHOICES)
    model_meta = models.ForeignKey(ModelMeta, on_delete=models.CASCADE)


class Breach(models.Model):
    model_meta = models.ForeignKey(
        ModelMeta, on_delete=models.CASCADE
    )
    connected_pnt_id = models.IntegerField()


class BoundaryCondition(models.Model):
    BOUNDARY_TYPE_CHOICES = (
        ('velocity', 'velocity'),
        ('sommerfeldt', 'sommerfeldt'),
        ('riemann', 'riemann'),
        ('water_level', 'water_level'),
        ('discharge', 'discharge'),
    )
    BOUNDARY_DIMENSION_CHOICES = (
        ('one_d', 'one_d'),
        ('two_d', 'two_d'),
    )

    model_meta = models.ForeignKey(
        ModelMeta, on_delete=models.CASCADE
    )
    type = models.CharField(max_length=40, choices=BOUNDARY_TYPE_CHOICES)
    # todo: is this a good name? definition?
    boundary_id = models.IntegerField()
    dimension = models.CharField(
        max_length=40, choices=BOUNDARY_DIMENSION_CHOICES)


class ThreediModel(models.Model):

    inpy_version = models.ForeignKey(InpyVersion, on_delete=models.CASCADE)
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE)

    name = models.CharField(max_length=80)  # auto generate if not given
    slug = models.SlugField(max_length=255)

    disabled = models.BooleanField(
        blank=False, null=False, default=False,
        help_text='Disable the model.')

    epsg = models.IntegerField()

    inp_success = models.NullBooleanField(
        default=None,
        help_text="signals success of generate inp/sewerage_inp/..."
    )

    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        null=True, blank=True, default='',
        help_text='Please describe the model here...'
    )

    storage_space = models.BigIntegerField(
        default=0, help_text='Automatically filled after inp generation.')

    meta = models.ForeignKey(ModelMeta, on_delete=models.CASCADE)


class FlowState(models.Model):

    threedi_model = models.ForeignKey(ThreediModel, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=80)  # auto generate if not given
    # tag = TODO: add tag field
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(null=True, blank=True)


class StableFlowState(FlowState):
    pass


class StableVariable(models.Model):
    VAR_CHOICES = (
        ('s1', 'flow rate(m/s)'),
        ('u1', 'water level(m)'),
    )
    variable_name = models.CharField(max_length=25, choices=VAR_CHOICES)
    flow_state = models.ForeignKey(StableFlowState, on_delete=models.CASCADE)


class StableThreshold(models.Model):
    flow_state = models.ForeignKey(StableFlowState, on_delete=models.CASCADE)
    variable_name = models.CharField(max_length=8)
    value = models.FloatField()


class TimedFlowState(FlowState):
    timestep = models.IntegerField(blank=False, null=False)


