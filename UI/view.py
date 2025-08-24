from datetime import datetime

import flet as ft
from flet_core import Alignment

from database.DAO import DAO


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self.txt_result = None
        self._btnGrafo = None
        self._btnReset = None
        self._btnCerca = None
        self._timeInfoTxt = None
        self._timeSel = None
        self._dateSel = None
        self._pollutionSlider = None
        self._pollutantDD = None
        self._btnCal1 = None
        self._page = page
        self._page.title = "Qualità dell'aria"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # self._page.bgcolor = "#dfdfdf"
        self._page.window_height = 800
        self._page.window_width = 900

        page.window_center()
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self._txt_name = None
        self._txt_result = None

    def load_interface(self):
        # title
        self._title = ft.Text("Progetto tesi: qualità dell'aria", color="blue", size=24)
        self._page.controls.append(self._title)
        self._dateSel = ft.DatePicker(
            first_date=datetime(year=2021, month=9, day=1),
            last_date=datetime(year=2023, month=9, day=1),
            current_date=datetime(year=2021, month=9, day=1),
            on_change=self._controller.handle_dataSel,
            on_dismiss=lambda e: print("Data non selezionata")
        )
        self._timeSel = ft.Slider(divisions=23, max=23, label="{value}:00", on_change=self._controller.handle_timeSel)
        self._timeInfoTxt = ft.Text("\n--:--",
                                    size=24,
                                    text_align=ft.TextAlign.CENTER,
                                    selectable=False, )
        self._btnCal1 = ft.ElevatedButton("Seleziona data:",
                                          icon=ft.icons.CALENDAR_MONTH,
                                          on_click=lambda _: self._dateSel.pick_date())
        self._page.overlay.append(self._dateSel)
        self._btnReset = ft.ElevatedButton(text="Reset", on_click=self._controller.handle_reset, disabled=True)
        row1 = ft.Row(
            [
                self._btnCal1,
                ft.Text("               Ora del giorno:\n "),
                self._timeSel,
                self._timeInfoTxt,
                ft.Container(expand=True),
                self._btnReset
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.END)
        self._pollutantDD = ft.Dropdown(label="Seleziona l'inquinante", width=250, disabled=True)
        self._pollutionSlider = ft.Slider(divisions=100, min=0, max=1, label="{value} μg/m3", disabled=True)
        self._btnGrafo = ft.ElevatedButton(text="Crea Grafo", on_click=self._controller.handleCreaGrafo)
        row2 = ft.Row(
            [
                self._pollutantDD,
                ft.Text("         Soglia dell'inquinante:\n "),
                self._pollutionSlider,
                ft.Container(expand=True),
                self._btnGrafo
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.END
        )

        self.txt_budget = ft.TextField(label="Budget interventi", hint_text="Inserisci il numero di interventi massimo",
                                       width=200)
        self._btnRicorsione = ft.ElevatedButton(text="Ottimizza interventi",
                                                on_click=self._controller.handle_ricorsione, disabled=True)
        rowRicorsione = ft.Row([self.txt_budget, self._btnRicorsione],
                               alignment=ft.MainAxisAlignment.CENTER)
        col1 = ft.Column([row1, row2])
        cont1 = ft.Container(content=col1, padding=20)
        self._page.add(ft.Card(content=cont1, color='#e6f2ff'))
        self._controller.fillDDPollution()
        # leggo direttamente dal dao
        lat_min, lat_max, lon_min, lon_max = DAO.get_min_max_coord()
        self._slider_lat = ft.Slider(
            min=lat_min,
            max=lat_max,
            label="Lat: {value}",
        )

        self._slider_lon = ft.Slider(
            min=lon_min,
            max=lon_max,
            label="Lon: {value}",
        )

        self._btn_aggiungi = ft.ElevatedButton(
            text="Aggiungi obiettivo",
            on_click=self._controller.handle_obiettivi
        )

        rowObiettivi = ft.Row([ft.Text("Latitudine"), self._slider_lat, ft.Text("Longitudine"),
                               self._slider_lon, self._btn_aggiungi])
        self._page.controls.append(rowObiettivi)
        self._page.controls.append(rowRicorsione)
        self.txt_result = ft.ListView(width=400, expand=1, spacing=10, padding=20, auto_scroll=False)
        self.txt_result_ricorsione = ft.ListView(width=400, expand=1, spacing=10, padding=20, auto_scroll=False)

        container1 = ft.Container(
            content=self.txt_result,
            margin=10,
            padding=10,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.GREY_200,
            width=400,
            height=350,
            border_radius=10,
        )
        container2 = ft.Container(
            content=self.txt_result_ricorsione,
            margin=10,
            padding=10,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.GREY_200,
            width=400,
            height=350,
            border_radius=10,
        )

        row_results = ft.Row([container1, container2],
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      spacing=50)
        self._page.controls.append(row_results)

        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    # per aprire messaggi di informazione
    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()
