from datetime import time, datetime

import flet as ft

import model.model


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._nn = None
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._currentDate=None
        self._currentP=None
        self._currentDatetime=None

    def slider_to_time(self,t):
        # Arrotonda al numero intero più vicino e limita ai valori validi (0–23)
        rounded_t = int(round(t)) % 24
        return time(hour=rounded_t, minute=0, second=0)

    def handle_dataSel(self, e):
        self._currentDate=self._view._dateSel.value.date()
        print (self._currentDate)
        return
    def handle_timeSel(self, e):
        if self._currentDate is None:
            self._view.create_alert("Seleziona prima una data!")
            return
        rounded_t=self.slider_to_time(self._view._timeSel.value)
        if rounded_t<time(hour=6):
            self._view._timeInfoTxt.value = f'🌌\n{rounded_t.strftime('%H:%M')}'
        elif rounded_t<time(hour=9):
            self._view._timeInfoTxt.value = f'🌄\n{rounded_t.strftime('%H:%M')}'
        elif rounded_t<time(hour=18):
            self._view._timeInfoTxt.value = f'🏙️\n{rounded_t.strftime('%H:%M')}'
        elif rounded_t<time(hour=21):
            self._view._timeInfoTxt.value = f'🌅\n{rounded_t.strftime('%H:%M')}'
        elif rounded_t <= time(hour=23):
            self._view._timeInfoTxt.value = f'🌌\n{rounded_t.strftime('%H:%M')}'
        #Dato che per conoscere gli estremi dell'intervallo di inquinante tra tutte le stazioni
        #mi serve il timestamp, abilito i controlli delle soglie per l'inquinante da analizzare
        #solo dopo che 'utente definisce la data e l'ora delle misurazioni da analizzare.
        self._view._pollutantDD.disabled=False
        self._view.update_page()
        #Per la query al db avrò bisogno di un timestamp composto da data e ora, quindi devo combinare
        #la data selezionata e l'ora selezionata in un oggetto di tipo Datetime
        self._currentDatetime=datetime.combine(self._currentDate, rounded_t)
        return

    def fillDDPollution(self):
        self._view._pollutantDD.options.append(ft.dropdown.Option(text='PM10 (polveri sottili)', data='PM10', on_click = self.handlePollutantSel))
        self._view._pollutantDD.options.append(ft.dropdown.Option(text='PM2.5 (polveri sottili)', data='PM2_5', on_click = self.handlePollutantSel))
        self._view._pollutantDD.options.append(ft.dropdown.Option(text='Ossidi di azoto', data='NO2', on_click = self.handlePollutantSel))
        self._view._pollutantDD.options.append(ft.dropdown.Option(text='Ozono', data='O3', on_click = self.handlePollutantSel))
        self._view.update_page()
        return

    def handlePollutantSel(self, e):
        self._currentP=e.control.data
        estremi=self._model.dao_min_max_pollution(self._currentDatetime, self._currentP)
        print(f'Ho selezionato {self._currentP} come inquinante. I valori minori e maggiori '
              f'tra le varie stazioni in questo timestamp sono rispettivamente {estremi[0]} ed {estremi[1]}')
        self._view._pollutionSlider.min=estremi[0]
        self._view._pollutionSlider.max=estremi[1]
        self._view._pollutionSlider.value=estremi[0]
        if estremi[0] is None or estremi[1] is None:
            self._view.create_alert("Non ci sono dati per questo inquinante nella data e l'ora selezionata!")
            return
        self._view._pollutionSlider.disabled=False
        self._view._btnReset.disabled=False
        self._view._btnCal1.disabled=True
        self._view._timeSel.disabled=True
        self._view.update_page()
        return
    def handle_reset(self, e):
        self._view._pollutionSlider.disabled=True
        self._view._pollutantDD.disabled=True
        self._view._btnReset.disabled=True
        self._view._btnCal1.disabled=False
        self._view._timeSel.disabled=False
        self._view._btnGrafo.text="Crea grafo"
        self._currentP=None
        self._currentDatetime=None
        self._currentDate=None
        self._view._timeSel.value=0
        self._view._timeInfoTxt.value='\n--:--'
        self._view.update_page()
        self._model.model_reset()
        return

    def handleCreaGrafo(self, e):
        self._view.txt_result.controls.clear()
        if self._currentDatetime is None:
            self._view.create_alert("Seleziona prima un timestamp")
        #Creo un grafo con le misurazioni, tuttavia devo controllare che è stato selezionato l'inquinante per
        #il peso degli archi
        self._nn,na=self._model.crea_grafo(self._currentDatetime, self._currentP, self._view._pollutionSlider.value)
        self._view.txt_result.controls.append(ft.Text(f"Numero di vertici: {self._nn}\nNumero di archi:{na}"))
        archi=self._model.sorted_edges()
        if self._nn==1: #se ho solo una stazione fuori soglia, non posso visualizzare i dettagli del grafo
            self._view.txt_result.controls.append(
                ft.Text(f"Solo una stazione ha rilevato una concentrazione di inquinante sopra la soglia impostata."))
        if self._nn==0: #idem
            self._view.txt_result.controls.append(
                ft.Text(f"Nessuna stazione ha rilevato un valore superiore alla soglia impostata"))
        elif self._nn>1:
            self._view.txt_result.controls.append(ft.Text(f"Le coppie di nodi con la minor differenza della concentrazione di {self._currentP} sono:"))
            for a in archi:
                self._view.txt_result.controls.append(
                    ft.Text(f"{a[0].STATION_NAME} ↔ {a[1].STATION_NAME}\nDifferenza: {a[2]['weight']} μg/m3"))
        #Una volta che ho il grafo posso procedere con il 2 punto
        self._view._btnRicorsione.disabled=False
        self._view._btnGrafo.text="Ricalcola grafo"
        self._view.update_page()
        return 


    def handle_ricorsione(self,e):
        self._view._btnRicorsione.disabled=False
        self._view.txt_result_ricorsione.controls.clear()
        self._view.txt_result_ricorsione.controls.append(
            ft.Text(f"Numero di obiettivi: {len(self._model._obiettivi)}"))
        if len(self._model._obiettivi)==0:
            self._view.create_alert("Definisci almeno un obiettivo!")
            return
        try:
            budget = int(self._view.txt_budget.value)
        except:
            self._view.create_alert("Inserire un valore per il budget valido!")
            return
        # Importante, il budget non può essere maggiore al numero di nodi totali del grafo.
        if budget<=self._nn:
            start_time = datetime.now()
            sol, score = self._model.ottimizza_interventi(budget)
            end_time =  datetime.now()
            print(f"Elapsed time: {end_time - start_time}")
        elif self._nn is None or self._nn == 0:
            self._view.create_alert(f"Attenzione! il grafo ha 0 nodi o non è stato definito. Riprova dopo aver creato il grafo")
            return
        else:
            self._view.create_alert(f"Attenzione: il budget ha un valore più alto del numero di nodi del grafo. Impostare un valore <= a {self._nn}")
            return
        self._view.txt_result_ricorsione.controls.append(
            ft.Text(f"La soluzione migliore ha peso {score}\nLe stazioni selezionate per gli interventi sono:"))
        for s in sol:
            self._view.txt_result_ricorsione.controls.append(
                ft.Text(f"📍{s.STATION_NAME}, con una concentrazione di {self._currentP} pari a {getattr(s, self._currentP, 'N/A')}"))
        self._view.update_page()
        return
    def handle_obiettivi(self, e):
        try:
            lat = self._view._slider_lat.value
            lon = self._view._slider_lon.value
        except:
            self._view.create_alert("Assicurati di aver usato entrambi gli slider delle coordinate per aggiungere "
                                    "un nuovo obiettivo!")
            return

        self._view.txt_result_ricorsione.controls.append(
            ft.Text(
                f"🗺️Ho aggiunto un obiettivo: Lat: {lat}, Lon: {lon}"))
        self._view.update_page()
        self._model.aggiungi_obiettivo(lat, lon)

        return
    def handleCerca(self, e):
        pass


    def handleRicorsione(self, e):
        pass
