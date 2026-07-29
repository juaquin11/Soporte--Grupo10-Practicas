import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class CalculatorScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""

    def on_button_press(self, button_text):
        if button_text == '=':
            try:
                calc_expression = self.expression.replace('x', '*').replace('÷', '/')
                result = str(eval(calc_expression))
                self.ids.display.text = result
                self.expression = result
            except:
                self.ids.display.text = 'Error'
                self.expression = ''
                
        elif button_text == 'ON':
            self.expression = ''
            self.ids.display.text = '0'
            
        elif button_text == 'OFF':
            App.get_running_app().stop()
            
        else:
            if self.ids.display.text == '0' or self.ids.display.text == 'Error':
                self.ids.display.text = ''

            self.expression += button_text
            self.ids.display.text = self.expression

class widgets_button(App):
    def build(self):
        return CalculatorScreen()

if __name__ == '__main__':
    widgets_button().run()