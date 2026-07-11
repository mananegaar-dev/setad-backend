import jdatetime
from django.utils import timezone 

def to_jalali(time):
    """Change shamsi to jalali date"""
    jalali_date = jdatetime.date.fromgregorian(date=time)
    return jalali_date.strftime("%Y/%m/%d")


def iso_to_jalali(dt, fmt="%Y/%m/%d %H:%M"):
    """
    change shmasi iso foramt to jalai date
    """
    local_dt = timezone.localtime(dt)
    return jdatetime.datetime.fromgregorian(datetime=local_dt).strftime(fmt)
