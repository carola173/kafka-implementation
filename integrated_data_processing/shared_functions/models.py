import datetime

import faust
from faust.models.fields import DatetimeField


class TripRecord(faust.Record):
    id: int
    vendor_id: int
    passenger_count: int
    pickup_longitude: float
    pickup_latitude: float
    dropoff_latitude: float
    drop_longitude: float
    store_and_fwd_flag: str
    pickup_datetime: datetime = DatetimeField(coerce=False)
