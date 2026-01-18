import kivy
from kivy.config import Config
import sqlite3

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty, ListProperty
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty, ListProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
import webbrowser
import os
from kivy.network.urlrequest import UrlRequest
import json
import time

MENIU_DATA = {
    "VINURI LA PAHAR": [
        {"nume": "Vin Alb (Crama Săptămânii)", "pret": "28 RON", "desc": "150ml, Selecție Săptămânală, Sec"},
        {"nume": "Vin Rosé (Crama Săptămânii)", "pret": "28 RON", "desc": "150ml, Selecție Săptămânală, Sec"},
        {"nume": "Vin Roșu (Crama Săptămânii)", "pret": "28 RON", "desc": "150ml, Selecție Săptămânală, Sec"},
    ],
    "BAR & COCKTAILS": [
        {"nume": "Aperol Spritz", "pret": "32 RON", "desc": "Aperol, Prosecco, Soda, Portocală"},
        {"nume": "Hugo", "pret": "32 RON", "desc": "Sirop soc, Prosecco, Mentă, Lime"},
        {"nume": "Gin Tonic Premium", "pret": "38 RON", "desc": "Hendrick's, Apă Tonică, Castravete"},
        {"nume": "Limonadă Juno", "pret": "22 RON", "desc": "400ml, Mentă și Miere"},
        {"nume": "Cafea Espresso", "pret": "12 RON", "desc": "100% Arabica"},
    ],
    "FOOD (Gustări)": [
        {"nume": "Platou Brânzeturi locale", "pret": "58 RON", "desc": "Selecție de brânzeturi, nuci, fructe"},
        {"nume": "Hummus Clasic", "pret": "34 RON", "desc": "Servit cu pită caldă și măsline"},
        {"nume": "Zacuscă de casă", "pret": "32 RON", "desc": "Rețetă tradițională, pâine prăjită"},
        {"nume": "Năut copt", "pret": "18 RON", "desc": "Gustare crocantă cu mirodenii"},
    ]

}

class MeniuNavigare(DropDown):
    def mergi_la(self, screen_name):
        App.get_running_app().root.current = screen_name
        self.dismiss()

    def logout(self):
        # Trimite utilizatorul la ecranul de login
        App.get_running_app().root.current = "login"
        self.dismiss()


class JunoMainLayout(BoxLayout):
    meniu_dropdown = ObjectProperty(None)

    def deschide_meniu(self, widget_buton):
        if not self.meniu_dropdown:
            self.meniu_dropdown = MeniuNavigare()
        self.meniu_dropdown.open(widget_buton)


    def initializare_db():
        conn = sqlite3.connect('utilizatori.db')
        cursor = conn.cursor()
        cursor.execute('''

                   CREATE TABLE IF NOT EXISTS useri (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL
                   )
                   ''')
    # Introducem un user de test (admin/1234) dacă tabela e goală
        cursor.execute('SELECT * FROM useri WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO useri (username, password) VALUES (?, ?)', ('admin', '1234'))

        conn.commit()
        conn.close()

# Apelăm funcția la pornirea scriptului
        initializare_db()

class LoginScreen(Screen):
    def verifica_login(self, username, password):
        conn = sqlite3.connect('utilizatori.db')
        cursor = conn.cursor()

        # Căutăm userul și parola în baza de date
        cursor.execute('SELECT * FROM useri WHERE username = ? AND password = ?', (username, password))
        utilizator = cursor.fetchone()
        conn.close()

        if utilizator:
            self.ids.error_label.text = ""
            self.ids.user_input.text = ""
            self.ids.pass_input.text = ""
            self.manager.current = "home"
        else:
            self.ids.error_label.text = "Username or password are incorrect!"
    def creeaza_cont(self, username, password):
        if not username or not password:
            self.ids.error_label.text = "Fill up the blanks!"
            return

        try:
            conn = sqlite3.connect('utilizatori.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO useri (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            self.ids.error_label.text = "Account created!"
            self.ids.error_label.color = (0, 0, 0, 1)
        except sqlite3.IntegrityError:
            self.ids.error_label.text = "User already exists!"
            self.ids.error_label.color = (1, 0, 0, 1) # Mesaj roșu
        except Exception as e:
            self.ids.error_label.text = f"Eroare: {str(e)}"


class HomeScreen(Screen):
    pass

class BackButton(Button):
    pass

class BackButton(Button):
    pass

class MasaButton(Button):
    numar = StringProperty("")
    # Stări: 'liber', 'selectat', 'rezervat'
    stare = StringProperty("liber")

class MeniuScreen(Screen):
    def on_enter(self):
        """Această funcție se rulează automat când intri pe ecranul Meniu"""
        container = self.ids.container_produse
        container.clear_widgets()

        for categorie, produse in MENIU_DATA.items():
            # Adăugăm titlul categoriei (folosind un widget definit în KV)
            titlu = Factory.LabelCategorie(text=categorie)
            container.add_widget(titlu)

            # Adăugăm produsele
            for p in produse:
                item = Factory.ProdusItem()
                item.nume = p['nume']
                item.pret = p['pret']
                item.desc = p['desc']
                item.callback = app.adauga_in_cos
                container.add_widget(item)


class RezervaScreen(Screen):
    stare_mese = DictProperty({str(i): True for i in range(1, 11)})
    selectie_temporara = ListProperty([])
    mesaj_status = StringProperty("Selectați Masa, Ora și Durata")
    confirmare_activa = BooleanProperty(False)

    interval_selectat = StringProperty("")
    # Nou: Proprietate pentru durata (1h sau 2h)
    durata_selectata = StringProperty("")

    def selecteaza_timp(self, interval):
        self.interval_selectat = interval
        self.valideaza_selectia()

    def selecteaza_durata(self, durata):
        self.durata_selectata = durata
        self.valideaza_selectia()

    def gestioneaza_click_masa(self, buton):
        if not self.stare_mese[buton.numar]:
            self.mesaj_status = f"Masa {buton.numar} ocupată!"
            return

        if buton.numar in self.selectie_temporara:
            self.selectie_temporara.remove(buton.numar)
            buton.stare = "liber"
        else:
            self.selectie_temporara.append(buton.numar)
            buton.stare = "selectat"

        self.valideaza_selectia()

    def valideaza_selectia(self):
        # Activăm confirmarea DOAR dacă avem: Masă + Oră + Durată
        conditie = len(self.selectie_temporara) > 0 and \
                   self.interval_selectat != "" and \
                   self.durata_selectata != ""

        self.confirmare_activa = conditie

        if conditie:
            self.mesaj_status = "Toate detaliile sunt gata!"
        else:
            self.mesaj_status = "Lipsesc detalii (Masa/Ora/Durata)"

    def confirma_rezervarea(self):
        if not self.confirmare_activa:
            return

        for numar in self.selectie_temporara:
            self.stare_mese[numar] = False
            for child in self.ids.grid_mese.children:
                if isinstance(child, MasaButton) and child.numar == numar:
                    child.stare = "rezervat"

        self.mesaj_status = f"Rezervat {self.durata_selectata} la {self.interval_selectat}!"

        # Resetare pentru următoarea rezervare
        self.selectie_temporara = []
        self.interval_selectat = ""
        self.durata_selectata = ""
        self.confirmare_activa = False

class CatalogMeniuScreen(Screen):
    def on_enter(self):
        # Folosim un try/except ca să nu se mai închidă aplicația dacă e o eroare
        try:
            container = self.ids.container_produse
            container.clear_widgets()
            app = App.get_running_app()

            for categorie, produse in MENIU_DATA.items():
                # Adăugăm titlul categoriei
                container.add_widget(Factory.LabelCategorie(text=categorie))

                for p in produse:
                    item = Factory.ProdusItem()
                    item.nume = p['nume']
                    item.pret = p['pret']
                    item.desc = p['desc']
                    item.callback = app.adauga_in_cos
                    container.add_widget(item)
        except Exception as e:
            print(f"Eroare la încărcarea meniului: {e}")

class CosScreen(Screen):
    def on_enter(self):
        container = self.ids.produse_cos
        container.clear_widgets()
        app = App.get_running_app()
        total = 0

        for item in app.shopping_cart:
            # Creăm un rând cu înălțime fixă și padding ca să nu atingă marginile ecranului
            row = BoxLayout(size_hint_y=None, height='50dp', padding=[15, 5], spacing=10)

            # Eticheta pentru Nume
            nume_label = Label(
                text=item['nume'],
                color=(0, 0, 0, 1),
                halign='left',      # Aliniere orizontală la stânga
                valign='middle',    # Aliniere verticală la mijloc
                size_hint_x=0.7     # Ocupă 70% din lățimea rândului
            )
            # Această linie este crucială: forțează textul să se alinieze în interiorul etichetei
            nume_label.bind(size=nume_label.setter('text_size'))

            # Eticheta pentru Preț
            pret_label = Label(
                text=item['pret'],
                color=(0.1, 0.5, 0.1, 1),
                bold=True,
                halign='right',     # Aliniere la dreapta
                valign='middle',
                size_hint_x=0.3     # Ocupă restul de 30%
            )
            pret_label.bind(size=pret_label.setter('text_size'))

            row.add_widget(nume_label)
            row.add_widget(pret_label)
            container.add_widget(row)

            # Calcul total
            try:
                pret_numeric = int(''.join(filter(str.isdigit, item['pret'])))
                total += pret_numeric
            except: pass

        self.ids.total_label.text = f"TOTAL: {total} RON"

    def sterge_cos(self):
        App.get_running_app().shopping_cart.clear()
        self.on_enter() # Refresh ecran

    # Nu mai avem nevoie de URL

    total_curent = 0

    def on_enter(self):
        self.actualizeaza_afisare()

    def actualizeaza_afisare(self):
        # ... (Această parte rămâne neschimbată, exact ca înainte) ...
        container = self.ids.produse_cos
        container.clear_widgets()
        app = App.get_running_app()
        self.total_curent = 0

        for item in app.shopping_cart:
            row = BoxLayout(size_hint_y=None, height='50dp', padding=[15, 5], spacing=10)
            nume_label = Label(text=item['nume'], color=(0,0,0,1), halign='left', valign='middle', size_hint_x=0.7)
            nume_label.bind(size=nume_label.setter('text_size'))
            pret_label = Label(text=item['pret'], color=(0.1,0.5,0.1,1), bold=True, halign='right', valign='middle', size_hint_x=0.3)
            pret_label.bind(size=pret_label.setter('text_size'))
            row.add_widget(nume_label)
            row.add_widget(pret_label)
            container.add_widget(row)
            try:
                pret_numeric = int(''.join(filter(str.isdigit, item['pret'])))
                self.total_curent += pret_numeric
            except: pass
        self.ids.total_label.text = f"TOTAL: {self.total_curent} RON"

    def sterge_cos(self):
        App.get_running_app().shopping_cart.clear()
        self.actualizeaza_afisare()

    def trimite_comanda(self):
        app = App.get_running_app()
        if not app.shopping_cart:
            return

            # 1. Datele noii comenzi
        noua_comanda = {
            "masa": "Masa Client",
            "produse": app.shopping_cart,
            "total": self.total_curent,
            "data": datetime.now().strftime("%H:%M:%S")
        }

        # 2. CITIM comenzile vechi (dacă există) din fișierul JSON auxiliar
        lista_comenzi = []
        try:
            if os.path.exists("istoric_comenzi.json"):
                with open("istoric_comenzi.json", "r") as f:
                    lista_comenzi = json.load(f)
        except:
            lista_comenzi = []

        # 3. Adăugăm comanda nouă
        lista_comenzi.append(noua_comanda)

        # 4. SALVĂM înapoi în JSON (pentru păstrare)
        with open("istoric_comenzi.json", "w") as f:
            json.dump(lista_comenzi, f)

        # 5. TRUCUL MAGIC: Salvăm și într-un fișier .JS pe care site-ul îl poate citi
        # Scriem: window.date_comenzi = [ ... lista ... ];
        continut_js = "window.date_comenzi = " + json.dumps(lista_comenzi) + ";"

        with open("date_comenzi.js", "w", encoding="utf-8") as f:
            f.write(continut_js)

        # 6. Succes și deschidere browser
        self.succes_comanda()

    def succes_comanda(self):
        print("Salvat local cu succes!")
        self.sterge_cos()

        # Deschide site-ul
        fisier_html = "index.html"
        try:
            cale_completa = "file://" + os.path.abspath(fisier_html)
            webbrowser.open(cale_completa)
        except Exception as e:
            print(f"Eroare browser: {e}")

        # Popup
        popup = Popup(title='Succes', content=Label(text='Order sent!', halign='center'),
                      size_hint=(None, None), size=('250dp', '150dp'))
        popup.open()



def trimite_comanda_la_bucatarie(self):
    if not self.lista_produse_cos:
        return

    # Luăm numele primului produs pentru titlul cardului
    nume_principal = self.lista_produse_cos[0]['nume']

    # Cream UN SINGUR obiect de comandă care conține TOATĂ lista de produse
    noua_comanda = {
        "id": nume_principal,
        "masa": self.masa_selectata,
        "produse": self.lista_produse_cos, # Aici salvăm toată lista (ex: 5 produse)
        "total": self.total_plata,
        "data": time.strftime("%H:%M:%S")
    }

    # Citim comenzile vechi și adăugăm noua comandă (grupul de produse)
    comenzi_existente = self.citeste_date_js()
    comenzi_existente.append(noua_comanda)

    with open('date_comenzi.js', 'w', encoding='utf-8') as f:
        f.write(f"window.date_comenzi = {json.dumps(comenzi_existente, indent=4, ensure_ascii=False)};")
class JunoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CatalogMeniuScreen(name="meniu"))
        sm.add_widget(RezervaScreen(name="rezerva"))
        sm.add_widget(CosScreen(name="cos"))
        return sm

    shopping_cart = []  # Lista unde salvăm produsele

    def adauga_in_cos(self, nume_produs, pret_produs):
        # Salvăm ca dicționar pentru a gestiona ușor datele
        self.shopping_cart.append({'nume': nume_produs, 'pret': pret_produs})
        print(f"Adăugat: {nume_produs}. Total produse: {len(self.shopping_cart)}")
        continut = Label(
            text=f"Added to cart:\n{nume_produs}",
            halign='center',
            color=(1, 1, 1, 1)
        )
        popup = Popup(
            title='Success',
            content=continut,
            size_hint=(None, None),
            size=('250dp', '150dp'),
            separator_color=(1, 1, 1, 1), # Linie verde sub titlu
            auto_dismiss=True
        )


        popup.open()


        Clock.schedule_once(popup.dismiss, 1)
    def on_start(self):
        # Pornim verificarea la fiecare 1.5 secunde
        Clock.schedule_interval(self.verifica_notificari_server, 1.5)

    def verifica_notificari_server(self, dt):
        cale = 'notificare_client.txt'
        if os.path.exists(cale):
            try:
                with open(cale, 'r', encoding='utf-8') as f:
                    date = f.read()

                if "GATA" in date:
                    parti = date.split('|')
                    if len(parti) >= 3:
                        titlu = parti[1]      # Comanda #14:35:01
                        produse = parti[2]    # Produs1, Produs2
                        self.afiseaza_popup_final(titlu, produse)

                os.remove(cale) # Stergem fisierul imediat
            except:
                pass

    def afiseaza_popup_final(self, titlu, produse_string):
        lista_bullet = produse_string.replace(", ", "\n• ")
        text_popup = f"[size=22sp][b]{titlu}[/b][/size]\n\nYour order is ready!:\n[b]• {lista_bullet}[/b]\n\nWe are waiting for you at the bar!"

        p = Popup(
            title='Juno Wine Garden',
            content=Label(text=text_popup, markup=True, halign='center', line_height=1.2),
            size_hint=(None, None),
            size=('400dp', '350dp')
        )
        p.open()
class MainApp(App):
    def on_start(self):
        # Verifică la fiecare 5 secunde dacă avem comenzi gata
        Clock.schedule_interval(self.verifica_notificari, 5)

    def verifica_notificari(self, dt):
        # Aici interoghezi serverul sau verifici un fișier "notificari.txt"
        comanda_gata = True # Exemplu simulat
        if comanda_gata:
            self.arata_popup("Comanda ta este gata! 🍷")

    def arata_popup(self, mesaj):
        popup = Popup(title='Juno Notification',
                      content=Label(text=mesaj),
                      size_hint=(None, None), size=(400, 200))
        popup.open()


if __name__ == '__main__':
    JunoApp().run()

