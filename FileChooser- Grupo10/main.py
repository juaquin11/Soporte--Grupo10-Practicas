from kivy.app import App
from kivy.lang import Builder


class MiApp(App):
    def build(self):
        return Builder.load_file("mi.kv")


if __name__ == "__main__":
    MiApp().run()