import threading
import os
from pyxelate import Pyx
from skimage import io
from functools import partial
from plyer import filechooser

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout

class PixelateApp(App):
    def build(self):
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon = os.path.join(self.app_dir, 'icon.png')
        self.image_path = os.path.join(self.app_dir, 'temp.png')

        self.image = io.imread(self.image_path)
        self.factor = 14
        self.dither = 'none'
        self.progress_notification = 'Ready'

        main_layout = BoxLayout(orientation='horizontal')

        self.image_widget = Image(source=self.image_path, allow_stretch=True, mipmap=True)

        main_layout.add_widget(self.image_widget)
        print(type(self.image))
        layout = BoxLayout(orientation='vertical')

        button_layout = GridLayout(cols=2)
        button_layout.add_widget(Button(text='Load Image', on_press=self.load_image))
        button_layout.add_widget(Button(text='Save Image', on_press=self.save_image))

        layout.add_widget(button_layout)

        self.factor_label = Label(text=f'Factor: {self.factor}')
        self.slider = Slider(min=1, max=20, step=1, value=self.factor)
        self.slider.bind(value=self.on_slider_value_change)

        slider_factor_layout = GridLayout(cols=2)
        slider_factor_layout.add_widget(self.factor_label)
        slider_factor_layout.add_widget(self.slider)

        layout.add_widget(slider_factor_layout)

        dither_layout = GridLayout(cols=2)
        for dither_option in ['none', 'naive', 'bayer', 'floyd', 'atkinson']:
            radio_button = CheckBox(group='dither', active=(dither_option == 'none'))
            radio_button.bind(active=partial(self.on_radio_button_active, dither_option=dither_option))
            dither_layout.add_widget(radio_button)
            dither_layout.add_widget(Label(text=dither_option))

        layout.add_widget(Label(text='Choose dither option:'))
        layout.add_widget(dither_layout)

        self.progress_label = Label(text=self.progress_notification)
        layout.add_widget(self.progress_label)

        layout.add_widget(Button(text='Pyxelate Image', on_press=self.on_button_press))

        main_layout.add_widget(layout)

        return main_layout

    def on_slider_value_change(self, instance, value):
        self.progress_notification = 'Ready'
        self.progress_label.text = self.progress_notification
        self.factor = int(value)
        self.factor_label.text = f'Factor: {self.factor}'

    def on_radio_button_active(self, instance, value, dither_option):
        if value:
            self.progress_notification = 'Ready'
            self.progress_label.text = self.progress_notification
            self.dither = dither_option

    def on_button_press(self, instance):
        self.progress_notification = 'In progress...'
        self.progress_label.text = self.progress_notification
        threading.Thread(target=self.process_image).start()

    def process_image(self):
        pyx = Pyx(factor=self.factor, palette=7, upscale=self.factor, dither=self.dither)
        pyx.fit(self.image)
        new_image = pyx.transform(self.image)
        io.imsave(self.image_path, new_image)
        self.image_path = self.image_path
        self.progress_notification = 'Done!'
        self.progress_label.text = self.progress_notification
        Clock.schedule_once(self.update_image)

    def load_image(self, instance):
        path = filechooser.open_file(title="Choose Image..",
                                     filters=[("Image file types", "*.png;*.jpg")])
        if path:
            self.image = io.imread(path[0])
            self.image_widget.source = path[0]
            self.image_widget.reload()
            self.progress_label.text = 'Image loaded'

    def save_image(self, instance):
        path = filechooser.save_file(title="Save Image As..",
                                 filters=[("PNG Image", "*.png")])
        if path:
            processed_image = io.imread(self.image_path)
            io.imsave(path[0]+'.png', processed_image)
            self.progress_label.text = 'Image saved'

    def update_image(self, dt):
        self.image_widget.source = self.image_path
        self.image_widget.reload()

if __name__ == '__main__':
    PixelateApp().run()
