from database.DB_connect import DBConnect


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_min_max_pollution(dt, pollutant):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor()
        query=""
        if pollutant=='NO2':
            query = """ select min(ad.NO2), max(ad.NO2)
                        from ancona_data ad 
                        where ad.MEASURE_DATETIME = %s"""
        elif pollutant=='O3':
            query = """ select min(ad.O3), max(ad.O3)
                        from ancona_data ad 
                        where ad.MEASURE_DATETIME = %s"""
        elif pollutant=='PM2_5':
            query = """ select min(ad.PM2_5), max(ad.PM2_5)
                        from ancona_data ad 
                        where ad.MEASURE_DATETIME = %s"""
        elif pollutant=='PM10':
            query = """ select min(ad.PM10), max(ad.PM10)
                        from ancona_data ad 
                        where ad.MEASURE_DATETIME = %s"""
        cursor.execute(query, (dt,))
        for row in cursor:
            result=row
        cursor.close()
        conn.close()
        return result