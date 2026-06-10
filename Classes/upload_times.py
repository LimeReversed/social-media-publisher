import datetime
from Classes.config import UploadTime

class UploadTimes:
    def __init__(self, upload_times: list[UploadTime]):
        self.upcoming_times: list[datetime.datetime] = [next_upload_datetime(upload_time) for upload_time in upload_times]

    def _replace(self, old_time: datetime.datetime, new_time: datetime.datetime):
        for i, time in enumerate(self.upcoming_times):
            if time == old_time:
                self.upcoming_times[i] = new_time
                break
            
    def get_next(self) -> datetime.datetime:      
        return min(self.upcoming_times)
    
    def pop(self) -> datetime.datetime:
        """Returns the next upload time and replaces the one in the array with the next upload time for the same day of the week."""
        next_time = self.get_next()
        self._replace(next_time, next_time + datetime.timedelta(days=7))
        return next_time
    
def next_weekday(start_date: datetime.date, target_weekday: int) -> datetime.date:
    # Monday=0, Tuesday=1, Wednesday=2, ..., Sunday=6
    days_ahead = (target_weekday - start_date.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    return start_date + datetime.timedelta(days=days_ahead)

def next_upload_datetime(upload_time: UploadTime, now: datetime.datetime | None = None) -> datetime.datetime:
    now = now or datetime.datetime.now()

    # day uses Python weekday numbering: Monday=0, ..., Sunday=6
    target_weekday = upload_time.day % 7

    target_date = next_weekday(now.date(), target_weekday)
    
    target_dt = datetime.datetime.combine(
        target_date,
        datetime.time(hour=upload_time.hour, minute=upload_time.minute, second=0),
    )

    if target_dt <= now:
        target_dt += datetime.timedelta(days=7)

    return target_dt