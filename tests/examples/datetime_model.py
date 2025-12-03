from datetime import date, time, timedelta

from pydantic import BaseModel


class Event(BaseModel):
    event_date: date
    start_time: time
    duration: timedelta
