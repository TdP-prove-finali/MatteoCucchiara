import copy
import random

import networkx as nx
from geopy.distance import geodesic

from database.DAO import DAO


class Model:
    def __init__(self):
        self._current_pollutant = None
        self._graph=nx.Graph()
        self._obiettivi=[]
    def dao_min_max_pollution(self,dt, pollutant):
        return DAO.get_min_max_pollution(dt, pollutant)
    def crea_grafo(self, timestamp, pollutant, treshold):
        self._graph.clear()
        self._current_pollutant=pollutant
        nodi=DAO.get_measures(timestamp)
        #aggiungo al grafo solo i nodi che superano la soglia.
        for n in nodi:
            val = getattr(n, pollutant, None)
            if val is not None and val > treshold:
                self._graph.add_node(n)

        for n in self._graph.nodes:
            # uso come fattore meteo quello del vento
            for other in self._graph.nodes:
                if n is not other:
                    #peso=abs(n.windspeed()-other.windspeed())
                    try:
                        peso = abs(getattr(n, pollutant) - getattr(other, pollutant))
                    except AttributeError:
                        return None

                    self._graph.add_edge(n,other,weight=peso)


        return self._graph.number_of_nodes(), self._graph.number_of_edges()

    def sorted_edges(self):
        return sorted(self._graph.edges(data=True), key=lambda edge: edge[2]['weight'])

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

    def aggiungi_obiettivo(self, lat, lon):
        self._obiettivi.append((lat, lon))
        print(f"Obiettivo aggiunto: ({lat}, {lon})")
    def model_reset(self):
        self._graph.clear()
        self._obiettivi=[]
        self._current_pollutant=None
        return
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
                    #riduco del 50% il valore di inquinante. Ho dovuto usare settatr per gestire i 4 casi
                    setattr(n, self._current_pollutant, getattr(n, self._current_pollutant, 0) * 0.5)
        esposizione_totale=0.0
        for o in obiettivi:
            esposizione=0.0
            for n in grafo_aggiornato:
                distanza=self.calcola_distanza(o, (n.LATITUDE, n.LONGITUDE))
                #uso gettatr per gestire i 4 casi (i 4 inquinanti analizzati)
                esposizione += getattr(n, self._current_pollutant, 0) / distanza
            esposizione_totale+=esposizione
        return esposizione_totale

    """
    funzione per calcolare la distanza in metri tra due punti geografici 
    Input: Point(LAT,LON)
    """
    def calcola_distanza(self, punto1, punto2):
        return geodesic(punto1,punto2).meters


