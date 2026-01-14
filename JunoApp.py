import kivy
from kivy.config import Config

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty


class MeniuNavigare(DropDown):
    def mergi_la(self, screen_name):
        App.get_running_app().root.current = screen_name
        self.dismiss()


class JunoMainLayout(BoxLayout):
    meniu_dropdown = ObjectProperty(None)

    def deschide_meniu(self, widget_buton):
        if not self.meniu_dropdown:
            self.meniu_dropdown = MeniuNavigare()
        self.meniu_dropdown.open(widget_buton)


class HomeScreen(Screen):
    pass


class MeniuScreen(Screen):
    pass


class RezervaScreen(Screen):
    pass


class GalerieScreen(Screen):
    pass


class JunoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(MeniuScreen(name="meniu"))
        sm.add_widget(RezervaScreen(name="rezerva"))
        sm.add_widget(GalerieScreen(name="galerie"))
        return sm


if __name__ == '__main__':
    JunoApp().run()
