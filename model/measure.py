from dataclasses import dataclass
from datetime import datetime
from math import sqrt

from geopy.point import Point


@dataclass
class Measure:
    STATION_NAME:str
    STATION_ID:int
    TIMESTAMP:datetime
    LATITUDE:float
    LONGITUDE:float
    NO2:float
    O3:float
    PM2_5:float
    PM10:float
    TOTAL_PRECIPITATION:float
    VEGITATION_H:float
    WINDSPEED_U:float
    WINDSPEED_V:float

    def __hash__(self):
        return hash(self.STATION_ID)
    def location(self):
        return Point(self.LATITUDE, self.LONGITUDE)
    def windspeed(self):
        return sqrt(pow(self.WINDSPEED_U,2)+pow(self.WINDSPEED_V,2))