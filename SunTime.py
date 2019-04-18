import datetime
from astral import Astral, GoogleGeocoder
#from astral import *
import time
from time import localtime, strftime
import pytz


def SunUpDown(location):
    a = Astral()
    a.solar_depression = 'civil'
    timezone = location.timezone
    Now = strftime("%H:%M", localtime())
    dt = datetime.datetime.fromtimestamp(time.mktime(localtime()))
    tz = pytz.timezone("Europe/Berlin")
    dtn = tz.localize(dt)
    dtnT = dtn + datetime.timedelta(days=1)
    sun = location.sun(dtn, local=True)
    sunT = location.sun(dtnT, local=True)
    if (sun['sunrise'].hour < 10):
        Sunrise = '0' + str(sun['sunrise'].hour) + ':'
    else:
        Sunrise = str(sun['sunrise'].hour) + ':'
    if (sun['sunrise'].minute < 10):
        Sunrise = Sunrise + '0' + str(sun['sunrise'].minute)
    else:
        Sunrise = Sunrise + str(sun['sunrise'].minute)

    if (sunT['sunrise'].hour < 10):
        SunriseT = '0' + str(sunT['sunrise'].hour) + ':'
    else:
        SunriseT = str(sunT['sunrise'].hour) + ':'        
    if (sunT['sunrise'].minute < 10):
        SunriseT = SunriseT + '0' + str(sunT['sunrise'].minute)
    else:
        SunriseT = SunriseT + str(sunT['sunrise'].minute)

    if (sun['sunset'].hour < 10):
        Sunset = '0' + str(sun['sunset'].hour) + ':'
    else:
        Sunset = str(sun['sunset'].hour) + ':'
    if (sun['sunset'].minute < 10):
        Sunset = Sunset + '0' + str(sun['sunset'].minute)
    else:
        Sunset = Sunset + str(sun['sunset'].minute)

    if (sunT['sunset'].hour < 10):
        SunsetT = '0' + str(sunT['sunset'].hour) + ':'
    else:
        SunsetT = str(sunT['sunset'].hour) + ':'
    if (sunT['sunset'].minute < 10):
        SunsetT = SunsetT + '0' + str(sunT['sunset'].minute)
    else:
        SunsetT = SunsetT + str(sunT['sunset'].minute)
    '''
    print sun['sunrise'], sun['sunset']
    print
    print sunT['sunrise'], sunT['sunset']
    print '-------------'
    '''
    return Sunrise, Sunset, SunriseT, SunsetT, sun['sunrise'], sun['sunset'], ((dtn > sun['sunrise']) and (dtn < sun['sunset']))

