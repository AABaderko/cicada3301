from kivy.app import App
from kivy.app import Widget
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label

from kivy.uix.image import Image
from kivy.graphics import (RoundedRectangle, BoxShadow)
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ObjectProperty

import cv2

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
            app_screen = self.parent.parent
            app_screen.release_camera()
            app_screen.open_takedphoto()

            image = app_screen.children[0].ids.taked_photo
            
            frame = self.preview.frame
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            image.texture = texture

class TakedPhotoPreview(Image):
    def __init__(self, **kwargs):
        super(TakedPhotoPreview, self).__init__(**kwargs)


class ImageButton(ButtonBehavior, Image):
    pass


class AppScreen(Screen):
    def __init__(self, **kwargs):
        super(AppScreen, self).__init__(**kwargs)
        self.add_widget(MainWidgets())
    
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