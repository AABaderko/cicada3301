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

from image_detection import found_img_in_database
from place_data import places_data

init()

CAPTION_BEST_BUILDING_NAMELIST = ["ЛУЧШИЕ", "АРХИТЕКТУРНЫЕ СООРУЖЕНИЯ"]
PHOTO_SAVE_PATH = 'photos/'


#Screensize for pc debugging
from kivy.core.window import Window
Window.size = (301, 655)

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
            frame = self.preview.frame
            buf = cv2.flip(frame, 0).tobytes()
            buf_size = (frame.shape[1], frame.shape[0])
            texture = Texture.create(size=buf_size, colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            img = ImagePIL.frombytes('RGB', buf_size, buf[::-1], 'raw')

            id_obj = place_analyzer_pictures(img)
            if id_obj:
                app_screen = self.parent.parent
                app_screen.release_camera()
                app_screen.open_takedphoto()

                data_obj = places_data[id_obj]

                taked_photo_w = app_screen.children[0]
                taked_photo_w.ids.taked_photo.source = data_obj.get("img")
                taked_photo_w.ids.place_category.text = ""
                
                taked_photo_w.ids.place_name.text = data_obj.get("name")
                taked_photo_w.ids.place_name.font_size = max(250 / len(data_obj.get("name")), 10)
                taked_photo_w.ids.place_year.text = data_obj.get("year")

                taked_photo_w.ids.place_information.text = data_obj.get("description")

                image_number = [f for f in os.listdir(PHOTO_SAVE_PATH) if isfile(join(PHOTO_SAVE_PATH, f))]
                image_number = len(image_number)+1
                img.save(f'photos/image{image_number}.jpg')

class TakedPhotoPreview(Image):
    def __init__(self, **kwargs):
        super(TakedPhotoPreview, self).__init__(**kwargs)

class Filechooser(BoxLayout):
    def select(self, *args):
        try: self.label.text = args[1][0]
        except: pass
    
    def click(self):
        id_obj = found_img_in_database(ImagePIL.open(self.label.text))
        if id_obj:
            app_screen = self.parent
            app_screen.open_takedphoto()

            data_obj = places_data[id_obj]

            taked_photo_w = app_screen.children[0]
            taked_photo_w.ids.taked_photo.source = data_obj.get("img")
            taked_photo_w.ids.place_category.text = ""
            
            taked_photo_w.ids.place_name.text = data_obj.get("name")
            taked_photo_w.ids.place_name.font_size = max(250 / len(data_obj.get("name")), 10)
            taked_photo_w.ids.place_year.text = data_obj.get("year")

            taked_photo_w.ids.place_information.text = data_obj.get("description")

def place_analyzer_pictures(loaded_pic):
    return 2
    # loaded_pic.thumbnail(IMAGE_SIZE)
    # for obj in places_data:
    #     data_pic = ImagePIL.open(obj.get("img"))
    #     data_pic.thumbnail(IMAGE_SIZE)
    #     if check_pictures(loaded_pic, data_pic):
    #         print(obj.get("img"))

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

class LabelSizable(Label):
    def __init__(self, **kwargs):
        super(LabelSizable, self).__init__(**kwargs)
        self.size_hint = (1, 1)
    
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
        self.add_widget(MainWidgets())
        # self.add_widget(TakedPhotoWidgets())
        # self.add_widget(Filechooser())
    
    def release_camera(self):
        widget = self.children[0]
        widget.ids.camera_preview.release()

    def switch_scene(self, cls):
        self.remove_widget(self.children[0])
        self.add_widget(cls())
 
    open_camera = lambda self: self.switch_scene(CameraWidgets)
    open_mainpage = lambda self: self.switch_scene(MainWidgets)
    open_takedphoto = lambda self: self.switch_scene(TakedPhotoWidgets)
    open_explorer = lambda self: self.switch_scene(Filechooser)
        

class Application(MDApp):
    def build(self):
        return AppScreen()

if __name__ == '__main__':
    place_analyzer_pictures(ImagePIL.open("place_photos/domGRES.jpg"))
    Application().run()