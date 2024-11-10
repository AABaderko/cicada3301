from kivy.app import App
from kivy.app import Widget
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.image import Image
from kivy.graphics import (RoundedRectangle, BoxShadow)
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ObjectProperty

import cv2
import os
from os.path import isfile, join

from colorama import Fore
from colorama import init
from PIL import Image as ImagePIL, ImageChops

from place_data import places_data

init()

CAPTION_BEST_BUILDING_NAMELIST = ["ЛУЧШИЕ", "АРХИТЕКТУРНЫЕ СООРУЖЕНИЯ"]
PHOTO_SAVE_PATH = 'photos/'


#Screensize for pc debugging
from kivy.core.window import Window
Window.size = (301, 655)

#Checking identity of images
def check_pictures(loaded_pic, data_pic):

    loaded_pic.thumbnail((400, 300))
    data_pic.thumbnail((400, 300))
    
    res = ImageChops.difference(loaded_pic, data_pic).getbbox()
    if res is None:
        print(Fore.GREEN + f'\nВозможно совпадение\n{"-"*50}')
        print(Fore.YELLOW + f'   - {pic1}')
        print(Fore.CYAN + f'   - {pic2}')
        with open('result_diff.txt', 'a', encoding='utf-8') as file:
            file.write(f'Возможно совпадение\n{"-"*50}\n   - {pic1}\n   - {pic2}\n\n')
    return



class MainWidgets(Widget):
    pass

class CameraWidgets(Widget):
    pass

class TakedPhotoWidgets(Widget):
    pass

class CameraPreview(Image):
    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        #Connect to 0th camera
        self.capture = cv2.VideoCapture(0)
        #Set drawing interval
        Clock.schedule_interval(self.update, 1.0 / 30)

    #Drawing method to execute at intervals
    def update(self, dt):
        #Load frame
        ret, self.frame = self.capture.read()
        #Convert to Kivy Texture
        if not (self.frame is None):
            buf = cv2.flip(self.frame, 0).tobytes()
            texture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            #Change the texture of the instance
            self.texture = texture

    def release(self):
        self.capture.release()

class TakePhoto(ButtonBehavior, Image):
    preview = ObjectProperty(None)

    #Execute when the button is pressed
    def on_press(self):
        if not (self.preview.frame is None):
            app_screen = self.parent.parent
            app_screen.release_camera()
            app_screen.open_takedphoto()

            image = app_screen.children[0].ids.taked_photo
            
            frame = self.preview.frame
            buf = cv2.flip(frame, 0).tobytes()
            buf_size = (frame.shape[1], frame.shape[0])
            texture = Texture.create(size=buf_size, colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            img = ImagePIL.open("icons/button_back.png")
            img = ImagePIL.frombytes('RGB', buf_size, buf[::-1], 'raw')

            image_number = [f for f in os.listdir(PHOTO_SAVE_PATH) if isfile(join(PHOTO_SAVE_PATH, f))]
            image_number = len(image_number)+1
            img.save(f'photos/image{image_number}.jpg')

            image.texture = texture

class TakedPhotoPreview(Image):
    def __init__(self, **kwargs):
        super(TakedPhotoPreview, self).__init__(**kwargs)


class ImageButton(ButtonBehavior, Image):
    pass

class Text(Label):
    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.size_hint = (1, 1)
        self.halign = 'left'
        self.valign = 'top'
    
    def on_size(self, *args):
        self.text_size = self.size

class CaptionBestBuildings(FloatLayout):
    def __init__(self, **kwargs):
        super(CaptionBestBuildings, self).__init__(**kwargs)
        # self.size_hint = (.5, .2)

        font_size = 35

        upper_label = Label(
            font_name = "fonts/a_FuturaOrtoTitulInln.ttf",
            text = CAPTION_BEST_BUILDING_NAMELIST[0],
            color = (1, 1, 1, 1),
            font_size = font_size,
            pos_hint = {'x': 0, 'y': 0.1},
        )

        lower_label = Label(
            font_name = "fonts/a_FuturaOrtoTitulInln.ttf",
            text = CAPTION_BEST_BUILDING_NAMELIST[1],
            color = (1, 1, 1, 1),
            font_size = font_size * 0.285,
            pos_hint = {'x': 0, 'y': -0.1},
        )

        self.add_widget(upper_label)
        self.add_widget(lower_label)


class AppScreen(Screen):
    def __init__(self, **kwargs):
        super(AppScreen, self).__init__(**kwargs)
        # self.add_widget(MainWidgets())
        self.add_widget(TakedPhotoWidgets())
    
    def release_camera(self):
        widget = self.children[0]
        widget.ids.camera_preview.release()

    def switch_scene(self, cls):
        self.remove_widget(self.children[0])
        self.add_widget(cls())
 
    open_camera = lambda self: self.switch_scene(CameraWidgets)
    open_mainpage = lambda self: self.switch_scene(MainWidgets)
    open_takedphoto = lambda self: self.switch_scene(TakedPhotoWidgets)
        

class Application(MDApp):
    def build(self):
        return AppScreen()

if __name__ == '__main__':
    Application().run()