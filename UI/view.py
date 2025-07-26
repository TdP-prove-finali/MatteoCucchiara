from datetime import datetime

import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self.txt_result = None
        self._btnRicorsione = None
        self._btnReset = None
        self._btnCerca = None
        self._timeInfoTxt = None
        self._timeSel = None
        self._dateSel = None
        self._pollutionSlider = None
        self._pollutantDD = None
        self._btnCal1 = None
        self._page = page
        self._page.title = "TESI - prova "
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.bgcolor = "#ebf4f4"
        self._page.window_height = 800
        page.window_center()
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self._txt_name = None
        self._txt_result = None

    def load_interface(self):
        # title
        self._title = ft.Text("TESI - prova", color="blue", size=24)
        self._page.controls.append(self._title)

        self._pollutantDD=ft.Dropdown(label="Seleziona l'inquinante", width=250, disabled=True)
        self._pollutionSlider=ft.Slider(divisions=100, min=0, max=1, label="{value} μg/m3", disabled=True)
        row1=ft.Row([self._pollutantDD, self._pollutionSlider], alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END)

        self._dateSel = ft.DatePicker(
            on_change=self._controller.handle_dataSel,
            on_dismiss=lambda e: print("Data non selezionata")
        )
        self._timeSel=ft.Slider(divisions=23, max=23, label="{value}:00", on_change=self._controller.handle_timeSel)
        self._timeInfoTxt=ft.Text("\n--:--",
                                        size=24,
                                        text_align=ft.TextAlign.CENTER,
                                        selectable=False,)
        self._btnCal1 = ft.ElevatedButton("Select date:",
                                              icon=ft.icons.CALENDAR_MONTH,
                                              on_click=lambda _: self._dateSel.pick_date())
        self._page.overlay.append(self._dateSel)

        self._btnReset = ft.ElevatedButton(text="Reset", on_click=self._controller.handle_reset, disabled=True)
        cont = ft.Container((self._btnCal1), width=150, alignment=ft.alignment.top_left)
        row2 = ft.Row([cont, self._timeSel, self._timeInfoTxt, self._btnReset], alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.END)


        self._btnCerca = ft.ElevatedButton(text="Ricorsivo",
                                           on_click=self._controller.handleCerca)

        self._btnRicorsione = ft.ElevatedButton(text="Ricorsione",
                                           on_click=self._controller.handleRicorsione)

        row3 = ft.Row([ft.Container(self._btnRicorsione, width=250)
                       ], alignment=ft.MainAxisAlignment.CENTER)

        self._page.controls.append(row2)
        self._controller.fillDDPollution()
        self._page.controls.append(row1)
        self._page.controls.append(row3)
        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(self.txt_result)
        self._page.update()


    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    #per aprire messaggi di informazione
    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()