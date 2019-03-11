from datetime import timedelta
from math import floor


def get_offset(dt, dt_start):
    """
    calculate the offset of dt from dt_start in seconds

    :param dt: datetime instance to calculate the offset for
    :param dt_start: datetime instance of the start time
    """
    offset = (dt_start - dt).total_seconds()
    assert offset >= 0, "offset can not be negative"
    return int(offset)


def get_duration(start_dt, end_dt):
    """
    calculate the duration from start_dt to end_dt in seconds

    Raises AssertionError when the duration is negative

    :param start_dt: datetime instance of the start time
    :param end_dt: datetime instance of the end time
    :returns duration in seconds

    """

    duration = (end_dt - start_dt).total_seconds()
    assert duration >= 0, "duration can not be negative (start_dt %s / end_dt %s )" % (start_dt, end_dt)
    return int(duration)


def get_request_dt_strings(start_dt, duration, interval, origin_offset=0):
    """
    generator that produces string representations of datetime instances
    based on a start date, the event duration and its temporal resolution


    :param start_dt: datetime instance for start time (in UTC)
    :param duration: duration of the event in seconds
    :param interval: resolution of the event in seconds
    :param origin_offset: offset in the origin  in minutes
    :returns (iso-)formatted string of the datetime representation

    Raises AssertionError when the duration or the interval
        parameter is smaller 1
    """
    assert duration > 0, "duration must be greater 0 %s %s %s " % (
        start_dt, duration, interval
    )

    assert interval > 0, "interval must be greater 0"

    request_dt = _current_request_dt(start_dt, interval, origin_offset)
    # yield the first dt immediately
    yield _as_official(request_dt)
    while all([duration > 0, not duration <= interval]):
        _dt_next = start_dt + timedelta(seconds=interval)
        dt_next = _current_request_dt(_dt_next, interval, origin_offset)
        yield _as_official(dt_next)
        start_dt = _dt_next
        duration -= interval


def _current_request_dt(dt, interval, dest_offset=0):
    """
    aligns the given datetime dt to the expected request dt
    :param dt: datetime instance
    :param interval: (int) temporal resolution of the destination
        layer in seconds
    :param dest_offset: offset of the destination layer in minutes
    :returns a datetime object that is snapped to next bigger start time of
    an interval based on the temporal resolution. If the temporal resolution
    is one hour that means

        dt = datetime(2016, 10, 20, 16, 2, tzinfo=pytz.UTC)

    will return (when no destination offset is given)

        datetime(2016, 10, 20, 17, 2, tzinfo=pytz.UTC)

    If the resolution is 10 minutes

        dt = datetime(2016, 10, 20, 16, 2, tzinfo=pytz.UTC)

    will return (when no destination offset is given)

        datetime(2016, 10, 20, 16, 10, tzinfo=pytz.UTC)

    Raises ValueError if the interval is greater than an hour
    but not a full hour, e.g. 7500
    """

    interval_min = interval / 60.0
    #
    if interval_min > 59:
        _check = interval_min / 60.0
        if not _check.is_integer():
            raise ValueError(
                "A temporal resolution for fraction of hours can not "
                "be calculated"
            )
        n_dt = _snap_to_full_hour(dt, interval_min)
        if dest_offset:
            n_dt += timedelta(minutes=dest_offset)
        return n_dt
    _offset = dest_offset + interval_min
    dt_min = int(floor(dt.minute / interval_min) * interval_min)
    n_dt = dt.replace(minute=dt_min)
    return n_dt + timedelta(minutes=_offset)


def _snap_to_full_hour(dt, interval_min=60):
    """
    helper function that manipulates the given datetime object by
    rounding to it to the next full hour
    :param dt: datetime object to manipulate
    :returns the datetime object rounded to the full hour

    Example:

       dt = datetime(2016, 10, 20, 16, 2, tzinfo=pytz.UTC)
       _snap_to_nxt_full_hour(dt)
       datetime.datetime(2016, 10, 20, 17, 0, tzinfo=<UTC>)
    """
    n_dt = dt.replace(minute=0)
    return n_dt + timedelta(minutes=interval_min)


def _as_official(dt):
    dt = dt.isoformat()
    try:
        dt_rep, _ = dt.split("+")
    except ValueError:
        dt_rep = dt
    return dt_rep