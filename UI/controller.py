from datetime import time, datetime

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
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
        self._currentP=None
        self._currentDatetime=None
        self._currentDate=None
        self._view._timeSel.value=0
        self._view._timeInfoTxt.value='\n--:--'
        self._view.update_page()
        return

    def handleCreaGrafo(self, e):
        self._view.txt_result.controls.clear()
        if self._currentDatetime is None:
            self._view.create_alert("Seleziona prima un timestamp")
        #Creo un grafo con le misurazioni, tuttavia devo controllare che è stato selezionato l'inquinante per
        #il peso degli archi
        nn,na=self._model.crea_grafo(self._currentDatetime, self._currentP, self._view._pollutionSlider.value)
        self._view.txt_result.controls.append(ft.Text(f"Numero di vertici: {nn}\nNumero di archi:{na}"))
        archi=self._model.sorted_edges()
        if nn==1: #se ho solo una stazione fuori soglia, non posso visualizzare i dettagli del grafo
            self._view.txt_result.controls.append(
                ft.Text(f"Solo una stazione ha rilevato una concentrazione di inquinante sopra la soglia impostata."))
        if nn==0: #idem
            self._view.txt_result.controls.append(
                ft.Text(f"Nessuna stazione ha rilevato un valore superiore alla soglia impostata"))
        elif nn>1:
            self._view.txt_result.controls.append(ft.Text(f"Le coppie di nodi con la minor differenza della concentrazione di {self._currentP} sono:"))
            for a in archi:
                self._view.txt_result.controls.append(
                    ft.Text(f"{a[0].STATION_NAME} ↔ {a[1].STATION_NAME}\nDifferenza: {a[2]['weight']} μg/m3"))
        self._view.update_page()
    def handle_obiettivi_random(self,e):
        try:
            N_obiettivi=int(self._view.txt_Nobiettivi.value)
        except:
            self._view.create_alert("Formato non corretto!")
            return
        if N_obiettivi is not None:
            obiettivi_gen=self._model.crea_obiettivi_random(self._currentDatetime, N_obiettivi)
        self._view._btnRicorsione.disabled=False
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Numero di obiettivi random generati: {N_obiettivi}"))
        for o in obiettivi_gen:
            self._view.txt_result.controls.append(
                ft.Text(f"{o}"))
        self._view.update_page()
        return

    def handle_ricorsione(self,e):
        #NB: il budget l'ho fissato a 3... modifico dopo.
        sol, score = self._model.ottimizza_interventi(4)
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"La soluzione migliore ha peso {score}\nLe stazioni selezionate per gli interventi sono:"))
        self._view.update_page()
        for s in sol:
            self._view.txt_result.controls.append(
                ft.Text(f"{s.STATION_NAME}, con una concentrazione di PM10 pari a {s.PM10}"))
        self._view.update_page()
        return
    def handleCerca(self, e):
        pass


    def handleRicorsione(self, e):
        pass
