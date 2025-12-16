import kivy
from kivy.config import Config

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty


class MeniuNavigare(DropDown):
    pass


class JunoMainLayout(BoxLayout):
    meniu_dropdown = ObjectProperty(None)

    def deschide_meniu(self, widget_buton):
        if not self.meniu_dropdown:
            self.meniu_dropdown = MeniuNavigare()


        self.meniu_dropdown.open(widget_buton)

class JunoApp(App):
    def build(self):
        return JunoMainLayout()

if __name__ == '__main__':
    JunoApp().run()