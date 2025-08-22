from database.DB_connect import DBConnect
from model.measure import Measure

class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_min_max_date():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor()
        query = """select min(ad.MEASURE_DATETIME), max(ad.MEASURE_DATETIME)
                    from ancona_data ad """
        cursor.execute(query)
        for row in cursor:
            result = row
        cursor.close()
        conn.close()
        return result


    @staticmethod
    def get_min_max_pollution(dt, pollutant):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor()
        inquinanti_cons = {"NO2", "O3", "PM2_5", "PM10"}
        if pollutant in inquinanti_cons:
            query = f"""
                SELECT MIN(ad.{pollutant}), MAX(ad.{pollutant})
                FROM ancona_data ad
                WHERE ad.MEASURE_DATETIME = %s
            """
        else:
            print('Errore nel valore passato alla query')
            return None
        cursor.execute(query, (dt,))
        for row in cursor:
            result=row
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_min_max_coord():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor()
        query="""
        select min(ad.LATITUDE), max(ad.LATITUDE), min(ad.LONGITUDE), max(ad.LONGITUDE)
        from ancona_data ad
        """
        cursor.execute(query)
        for row in cursor:
            result = row
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_measures(dt):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
        select ad.STATION_NAME, ad.STATION_ID, ad.MEASURE_DATETIME as TIMESTAMP,
                ad.LATITUDE, ad.LONGITUDE, 
                ad.NO2, ad.O3, ad.PM2_5, ad.PM10,
                ad.TOTAL_PRECIPITATION, ad.VEGITATION_H, ad.WINDSPEED_U,  ad.WINDSPEED_V
                from ancona_data ad 
                where ad.MEASURE_DATETIME = %s and ad.PM10 is not NULL and ad.PM2_5 is not NULL 
                and ad.O3 is not NULL and ad.NO2 is not NULL
        """
        cursor.execute(query, (dt,))
        for row in cursor:
            result.append(Measure(**row))
        cursor.close()
        conn.close()
        return result
