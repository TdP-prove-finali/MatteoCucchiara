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

    # ATTENZIONE: nel database non abbiamo un id univoco per ogni misurazione. Se fosse necessario, bisognerebbe
    # crearlo combinando il timestamp e l'id della stazione. Tuttavia, per gli algoritmi trattati non è necessario
    # farlo perchè vengono analizzati i dati in un timestamp specifico per ottenere tutte le misurazioni delle
    # stazioni, pertanto è possibile usare semplicemente l'id della stazione.

    def __hash__(self):
        return hash(self.STATION_ID)
    def location(self):
        return Point(self.LATITUDE, self.LONGITUDE)
    def windspeed(self):
        return sqrt(pow(self.WINDSPEED_U,2)+pow(self.WINDSPEED_V,2))