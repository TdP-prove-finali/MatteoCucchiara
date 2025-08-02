import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph=nx.Graph()
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