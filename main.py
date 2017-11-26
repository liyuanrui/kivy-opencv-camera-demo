#coding=utf-8
#qpy:kivy

import os
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from camera import Camera2
from kivy.clock import Clock
import cv2
import time
from kivymd.theming import ThemeManager
from kivy.core.text import LabelBase                      
LabelBase.register(name='Roboto',fn_regular='droid.ttf')

class MyLayout(BoxLayout):pass

class MainApp(App):
    # 定义主题,辅助变量,参数以及提醒邮箱
    theme_cls=ThemeManager()
    precount,oldcount,starttime=0,0,0
    pixelcount=100 # 白色像素个数
    warncount=5    # 连续几次才提醒
    timecount=5    # 每次的间隔秒数
    warntime=1     # 提醒的间隔分钟
    email='i@example.comm'

    def build(self):
        self.theme_cls.theme_style='Dark'
        return MyLayout()

    def on_start(self):
        self.root.ids.sm.current='index'
        if os.path.exists('log.json'):
            with open('log.json') as f:
                r=f.read().split()
            self.root.ids.pixelcount.text,self.root.ids.warncount.text,self.root.ids.timecount.text,self.root.ids.warntime.text,self.root.ids.email.text=r

    def start(self):
        self.pixelcount=int(self.root.ids.pixelcount.text)
        self.warncount= int(self.root.ids.warncount.text)
        self.timecount= int(self.root.ids.timecount.text)
        self.warntime=  int(self.root.ids.warntime.text)
        self.email=self.root.ids.email.text
        with open('log.json','w') as f:
            f.write('%s\n%s\n%s\n%s\n%s'%(self.pixelcount,
                                          self.warncount,
                                          self.timecount,
                                          self.warntime,
                                          self.email))
        Clock.schedule_interval(self.quilt,self.timecount)

    def quilt(self,nap):
        image=self.root.ids.camera.image
        self.threshold(image)

    def threshold(self,image):
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret,th=cv2.threshold(gray,250,255,cv2.THRESH_BINARY)
        #th1=th[25:]
        lightcount=0
        for t in th:lightcount+=640-list(t).count(0)
        # 白色像素点大于阀值次数叠加
        if lightcount >= self.pixelcount:
            if self.oldcount==0:   # 初始状态
                self.oldcount=1
                self.precount+=1
            elif self.oldcount==1: # 上一次True
                self.precount+=1
            else:                  # 上一次False
                self.oldcount=1
                self.precount=1
        else:
            if self.oldcount==0:   # 初始状态
                pass
            else:
                self.oldcount=-1
                self.precount=0
        # precount叠加次数到达提醒阀值
        if self.precount >= self.warncount:
            if self.starttime == 0: # 初始
                print('warn!')
                self.root.ids.labelshow.text+='warn!\n'
                self.precount=0
                self.starttime=time.time()
            else:
                # 提醒间隔分钟
                if int(time.time()-self.starttime)>=self.warntime*60:
                    print('warn!')
                    self.root.ids.labelshow.text+='warn!\n'
                    self.precount=0
                    self.starttime=time.time()



if __name__ == '__main__':
    MainApp().run()

