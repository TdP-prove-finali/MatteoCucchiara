import copy
import random

import networkx as nx
from geopy.distance import geodesic

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph=nx.Graph()
        self._obiettivi=[]
    def dao_min_max_pollution(self,dt, pollutant):
        return DAO.get_min_max_pollution(dt, pollutant)
    def crea_grafo(self, timestamp, pollutant, treshold):
        self._graph.clear()
        nodi=DAO.get_measures(timestamp)
        #aggiungo al grafo solo i nodi che superano la soglia.
        for n in nodi:
            if pollutant == "NO2" and n.NO2 is not None and n.NO2>treshold:
                self._graph.add_node(n)
            if pollutant == "O3" and n.O3 is not None and n.O3>treshold:
                self._graph.add_node(n)
            if pollutant == "PM2_5" and n.PM2_5 is not None and n.PM2_5>treshold:
                self._graph.add_node(n)
            if pollutant == "PM10" and n.PM10 is not None and n.PM10>treshold:
                self._graph.add_node(n)
        for n in self._graph.nodes:
            # uso come fattore meteo quello del vento
            for other in self._graph.nodes:
                if n is not other:
                    #peso=abs(n.windspeed()-other.windspeed())
                    peso=0
                    if pollutant == "NO2":
                        peso=abs(n.NO2-other.NO2)
                    if pollutant == "O3":
                        peso=abs(n.O3-other.O3)
                    if pollutant == "PM2_5":
                        peso=abs(n.PM2_5-other.PM2_5)
                    if pollutant == "PM10":
                        peso=abs(n.PM10-other.PM10)
                    self._graph.add_edge(n,other,weight=peso)


        return self._graph.number_of_nodes(), self._graph.number_of_edges()

    def sorted_edges(self):
        return sorted(self._graph.edges(data=True), key=lambda edge: edge[2]['weight'])

    def crea_obiettivi_random(self, timestamp, Nobiettivi):
        self._obiettivi=self.random_points(timestamp, Nobiettivi)
        return self._obiettivi

    def ottimizza_interventi(self, budget):
        self._soluzioni=[]
        # NB: scelgo le stazioni di misura nelle quali effettuare gli interventi
        # solo in quelle che superano la soglia (in pratica i nodi del grafo).
        # Questa è una approssimazione ma riduce il numero di step di ricorsione
        # evitando di far esplodere il problema.
        self._candidati=self._graph.nodes()
        self._ricorsione([], budget)
        #lo scopo è quello di trovare la soluzione con l'esposizione totale più bassa possibile
        best_score=99999999
        best_soluzione=[]
        for s in self._soluzioni:
            p=self.calcola_punteggio(s,self._obiettivi)
            if p<best_score:
                best_score=p
                best_soluzione=s
        return best_soluzione, best_score


    def _ricorsione(self, parziale, budget):
        # condizione terminale: quando parziale ha un numero di interventi pari al budget
        if len(parziale) == budget:
            print(parziale)
            self._soluzioni.append(copy.deepcopy(parziale))
        # caso ricorsivo
        else:
            for i in self._candidati:
                if i not in parziale:
                    parziale.append(i)
                    # vado avanti nella ricorsione
                    self._ricorsione(parziale, budget)
                    # backtracking
                    parziale.pop()
        return
    def calcola_punteggio(self, soluzione, obiettivi):
        """
        step per calcolare il punteggio: genero una copia del grafo con i valori dell'inquinamento ridotte del
        20% sulle stazioni scelte nella soluzione. In seguito, definisco lo score come la media
        dell' esposizione all' inquinamento sugli obiettivi. Per definire l'esposizione all'inquinamento di
        ogni obiettivo, faccio la sommatoria di tutte le misurazioni dell'inquinante scelto delle centraline
        tenendo conto della distanza centralina-obiettivo con la formula I/distanza: ad es, se misuro 10 mg/m^3 su
        una centralina distante 100m, quella misura aumenta di 10/100 l'esposizione su quell'obiettivo.
        """
        #ricalcolo il grafo:
        grafo_aggiornato=copy.deepcopy(self._graph)
        for n in grafo_aggiornato:
            for s in soluzione:
                if s.STATION_ID==n.STATION_ID:
                    #riduco del 20% il valore di PM10
                    n.PM10=n.PM10*0.8
        esposizione_totale=0.0
        for o in obiettivi:
            esposizione=0.0
            for n in grafo_aggiornato:
                distanza=self.calcola_distanza(o, (n.LATITUDE, n.LONGITUDE))
                esposizione+= (n.PM10/distanza)
            esposizione_totale+=esposizione
        return esposizione_totale


    def random_points(self,timestamp, N):
        """
        Genera N punti random in modo che si trovino all'interno dell'area delimitata dalle massime
        e minime longitudini e latitudini di tutte le stazioni di misurazione che hanno misurato un valore
        in un dato timestamp. Restituisce una lista di tuple contenenti latitudine e longitudine dei
        punti generati.
        """
        nodi=DAO.get_measures(timestamp)
        punti=[]
        (Lat_min, Lat_max) = (999, 0)
        (Lon_min, Lon_max) = (999, 0)
        for n in nodi:
            #sembrerebbe che che le coordinate geografiche nel db sono tutte presenti (non NULL) e corrette...
            if n.LATITUDE<Lat_min:
                Lat_min=n.LATITUDE
            if n.LATITUDE>Lat_max:
                Lat_max=n.LATITUDE
            if n.LONGITUDE<Lon_min:
                Lon_min=n.LONGITUDE
            if n.LONGITUDE>Lon_max:
                Lon_max=n.LONGITUDE
        #uso random.uniform per generare un float contenuto tra due estremi di tipo float
        for i in range (1, N+1):
            rand_lat=random.uniform(Lat_min, Lat_max)
            rand_lon=random.uniform(Lon_min, Lon_max)
            print(f'Ho generato il punto N.{i} con coordinate {rand_lat} LAT; {rand_lon} LON')
            punti.append((rand_lat, rand_lon))
        return punti
    """
    funzione per calcolare la distanza in metri tra due punti geografici 
    Input: Point(LAT,LON)
    """
    def calcola_distanza(self, punto1, punto2):
        return geodesic(punto1,punto2).meters


