from database.DAO import DAO


class Model:
    def __init__(self):
        pass
    def dao_min_max_pollution(self,dt, pollutant):
        return DAO.get_min_max_pollution(dt, pollutant)