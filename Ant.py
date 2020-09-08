# -*- coding: utf-8 -*-
"""
Created on Fri Feb 09 18:17:43 2018

@author: alecw
"""

import numpy as np
import pylab
import matplotlib.pyplot as plt
from Tkinter import *
import matplotlib
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from numba import jit
import matplotlib.animation as animation
from random import randint,shuffle,random
#import cmath
import time
import glob
import cmath

#@jit
#@jit(nopython=True)

class App:
    def __init__(self,master):
        self.master = master
        self._job = None
        self.frame = Frame(self.master)
        self.menubar = Menu(self.master)
        master.config(menu=self.menubar)
        self.menubar.add_command(label="Start!", command=self.progress)
        self.flag_menu = Menu(self.menubar)
        self.menubar.add_cascade(label="Coloring",menu=self.flag_menu)
        self.frame.grid(row=0,column=0,sticky=W)
        self.low_frame = Frame(self.master)
        self.low_frame.grid(row=1,column=0,sticky=W)
        self.nav_frame = Frame(self.low_frame)
        self.nav_frame.grid(row=0,column=9,sticky=E)
        print (self.master.winfo_screenwidth()*9/1920.0,self.master.winfo_screenheight()*9/1080.0)
        self.Fig = matplotlib.figure.Figure(figsize=(self.master.winfo_screenwidth()*9/1920.0,self.master.winfo_screenheight()*9/1080.0),dpi=100,tight_layout=True,frameon=False)
        self.FigSubPlot = self.Fig.add_subplot(111)  
        self.canvas = FigureCanvasTkAgg(self.Fig, master=self.frame)
        self.canvas.show()
        self.background = self.canvas.get_tk_widget()
        self.background.pack(fill=BOTH)
        self.toolbar = NavigationToolbar(self.canvas, self.nav_frame)
#   
#        self.eqn_list = [0]
#        self.d = 2
#        self.eqn_list_str = ["z**%s+c"%self.d,"z**d+c","(|z.real|+|z.imag|*i)**2 + c","exp(z) + c","cos(z) + c","c*z*(1-z)"]

        self.ani_flag = 0
        self.iter_var = IntVar()
        self.iter_var.set(200)
        self.resolution = 7
        self.menubar.add_command(label=self.iter_var.get())
        self.menubar.add_command(label="Options",command=self.options)
        self.zoom_menu = Menu(self.menubar)
        self.menubar.add_command(label='Animate',command=self.animate)

        self.iter_menu = Menu(self.menubar)

        self.chan_menu = Menu(self.menubar)
        
#        self.xy,self.xrange = (-0.77935557422765123, -0.13446256411143759),[-0.77935704110987425, -0.77935482514883669]
#        self.xy,self.xrange = (-0.75222388519157268, -0.040965152572997689),[-0.75222388519159378, -0.75222388519155148]
#        self.xy,self.xrange = [-0.10228392078305387, -0.10228392078297188],(-0.1022839207830129, -0.94626442954727208)
#        self.xy,self.xrange = (-0.90788399028954736, -0.26752268187573769),[-0.90788399028955979, -0.90788399028953526]
#        self.iter_var.trace('w',self.slider_iter)
#        self.xy,self.xrange =(-1.1476766998672108, 0.27721359784019722),[-1.1476766998672145, -1.1476766998672074]
#        self.xy,self.xrange = (0.92210302746896, -0.069229029462414271),[-2.0, 1.0]
#        self.xy,self.xrange = (0.74781121734121658, -0.12741123251340625),[-0.67097267147858242, 2.3290273285214176]
        self.prev_iter = None
        self.color_var = StringVar()
        self.color_var.set('Greys')
#        self.color_trace = self.color_var.trace('w',self.graph_update)
        for string in ['viridis','inferno','plasma','magma','Blues','BuGn','BuPu','GnBu','Greens','Greys','Oranges','OrRd','PuBu','PuBuGn','PuRd','Purples','RdPu','Reds','YlGn','YlGnBu','YlOrBr','YlOrRd','afmhot','autumn','bone','cool','copper','gist_heat','gray','hot','pink','spring','summer','winter','BrBG','bwr','coolwarm','PiYG','PRGn','PuOr','RdBu','RdGy','RdYlBu','RdYlGn','Spectral','seismic','Accent','Dark2','Paired','Pastel1','Pastel2','Set1','Set2','Set3','gist_earth','terrain','ocean','gist_stern','brg','CMRmap','cubehelix','gnuplot','gnuplot2','gist_ncar','nipy_spectral','jet','rainbow','gist_rainbow','hsv','flag','prism']:
            self.flag_menu.add_radiobutton(label=string, variable=self.color_var)

        self.xlim = [-1.0,1.0]
        self.ylim = [-1.0,1.0]

        self.ant_loc = (int(self.resolution/2.0),int(self.resolution/2.0))
#        self.seq = 'RRLLLRLLLRRR'
#        self.seq = 'RRLL'
        self.seq = 'RLLR'
        self.state_fun()
        self.image = np.zeros((self.resolution, self.resolution), dtype=np.uint8)
        for x in range(self.resolution):
            for y in range(self.resolution):
                color = 0
                self.image[y, x] = color
#        self.FigSubPlot.axis('off')
        
        self.im = self.FigSubPlot.imshow(self.image,cmap=self.color_var.get(),animated=True,interpolation='none')
        self.arrow = self.FigSubPlot.plot(3,3,marker='<',markersize=588/self.resolution,color='green')

        
        self.FigSubPlot.axis('off')
        self.canvas.draw()
        self.mod = 77.2*11.0/self.resolution
        self.offset = (35,16)
        self.prog_count = 0
        self.direct = '4'
        self.ant_move()
        self.rxlim = [self.FigSubPlot.get_xlim()[0],self.FigSubPlot.get_xlim()[1]]
        self.rylim = [self.FigSubPlot.get_ylim()[0],self.FigSubPlot.get_ylim()[1]]
#        self.master.bind("<ButtonRelease-1>",self.pan_update)
#        self.master.bind("<ButtonRelease-3>",self.pan_update)
#        self.master.bind("<MouseWheel>",self._on_mousewheel)
#        self.canvas.callbacks.connect('button_press_event',self.set_coords)
    def state_fun(self):
        self.state_col = [0]
        if len(self.seq) > 2:
            for it in range(1,len(self.seq)-1):
                self.state_col.append(0+255*(it)/(len(self.seq)-1))
        self.state_col.append(255)
    def rescale(self):
        self.resolution += 2
        self.mod = 77.2*11.0/self.resolution
        self.scale_image = np.zeros((self.resolution, self.resolution), dtype=np.uint8)
        for x in range(self.resolution):
            for y in range(self.resolution):
                if x == 0 or x == self.resolution-1 or y == 0 or y == self.resolution-1:
                    color = 0
                else:
                    color = self.image[y-1,x-1]
                self.scale_image[y, x] = color
        self.image = self.scale_image
        self.ant_loc = (self.ant_loc[0]+1,self.ant_loc[1]+1)
    def ant_move(self):
        self.marker_dic = {'1':'^','2':'>','3':'v','4':'<'}
#        self.coord_dic = {'1':(self.ant_loc[0]*self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.mod/2.0+self.offset[0], self.ant_loc[1]*self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod+self.offset[1]),
#                          '3':((self.ant_loc[0])*self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.mod/2.0+self.offset[0], self.ant_loc[1]*self.mod+self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.offset[1]),
#                          '2':((self.ant_loc[0])*self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod/2.0+self.offset[1], self.ant_loc[0]*self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod+self.offset[1]),
#                          '4':((self.ant_loc[0])*self.mod+self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.offset[1], self.ant_loc[0]*self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod/2.0+self.offset[1], self.ant_loc[0]*self.mod+self.mod+self.offset[0], self.ant_loc[1]*self.mod+self.mod+self.offset[1])}
#        self.ant = self.background.create_polygon(self.coord_dic[self.direct], fill="red")
        self.arrow.pop(0).remove()
        self.arrow = self.FigSubPlot.plot(self.ant_loc[0],self.ant_loc[1],marker=self.marker_dic[self.direct],markersize=600/self.resolution,color='red')
        
    def progress(self):
        if self.ant_loc[0] == 1 or self.ant_loc[1] == 1 or self.ant_loc[0] == self.resolution-2 or self.ant_loc[1] == self.resolution-2:
            self.rescale()         
   
        for state_num in range(0,len(self.state_col)):         
            if self.image[self.ant_loc[1],self.ant_loc[0]] == self.state_col[state_num]:
                if self.seq[state_num] == 'R':
                    if int(self.direct) != 4:
                        self.direct = '%s'%(int(self.direct)+1)
                    else:
                        self.direct = '1'
                elif self.seq[state_num] == 'L':
                    if int(self.direct) != 1:
                        self.direct = '%s'%(int(self.direct)-1)
                    else:
                        self.direct = '4'
                if self.state_col[state_num] != 255:
                    self.image[self.ant_loc[1],self.ant_loc[0]] = self.state_col[state_num+1]
                else:
                    self.image[self.ant_loc[1],self.ant_loc[0]] = self.state_col[0]
                self.walk()
#                self.background.delete(self.ant)
                self.ant_move()
                break
        if self.ani_flag == 0:
            self.skip = 1000.0
            if self.prog_count/self.skip == int(self.prog_count/self.skip):
                self.im = self.FigSubPlot.imshow(self.image,cmap=self.color_var.get(),animated=True,interpolation='none')
                self.canvas.draw()
            self.prog_count += 1
            self.master.after(10,self.progress) 
        else:
            self.image_set.append(self.image)
    def walk(self):
        if self.direct == '1':
            self.ant_loc = (self.ant_loc[0],self.ant_loc[1]-1)
        elif self.direct == '3':
            self.ant_loc = (self.ant_loc[0],self.ant_loc[1]+1)
        elif self.direct == '4':
            self.ant_loc = (self.ant_loc[0]-1,self.ant_loc[1])
        elif self.direct == '2':
            self.ant_loc = (self.ant_loc[0]+1,self.ant_loc[1])
#    def check_rand(self):
#            self.randomize()
#            self.window.destroy()
#            self.eqn_list_str = ["z**%s+c"%self.d,"z**d+c","(|z.real|+|z.imag|*i)**2 + c","exp(z) + c","cos(z) + c","c*z*(1-z)"]
#            self.options()

    def options(self):
        self.window = Toplevel(self.master)
        self.window.geometry("%dx%d%+d%+d" % (200, 70, 50, 50))
        self.window.attributes('-topmost', True)
        frame = Frame(self.window)
        self.eqn_listbox = Listbox(frame)
        self.eqn_listbox.pack(fill=BOTH)
        for eqn in self.eqn_list:
            self.eqn_listbox.insert(END,self.eqn_list_str[eqn])
        frame.pack(fill=BOTH)
        
    def animate(self): 
        self.mac_flag = 1
        self.save_freq = 180
        self.frame_num = 10
        self.ani_dpi = 120
        self.print_freq = 20
        self.ani_flag = 1
        self.image_set = []

        Writer = animation.writers['ffmpeg']
        self.writer = Writer(fps=6, metadata=dict(artist='Me'), bitrate=-1)
        self.start = time.time()   
        if self.mac_flag == 1:
            for it in range(0,self.frame_num):
                self.progress()
                if int((time.time()-self.start)/self.save_freq) == (time.time()-self.start)/float(self.save_freq) or it == self.frame_num-1:
                    np.save('data%s.npy'%(it+1),self.image_set)
                    print "save", it+1, time.time()-self.start
        print "Animation start:", time.time()-self.start
        self.frame_count = 0
        self.ani = animation.FuncAnimation(self.Fig,self.ani_update,repeat=False,frames=self.frame_num)
        self.ani.save('test.mp4',writer=self.writer,dpi=self.ani_dpi)
        print time.time()-self.start,"done"
        self.ani_flag = 0
            

    
    def ani_update(self,*args):
        if self.frame_count < self.frame_num:
            self.im.set_array(self.image_set[self.frame_count])
            if int(self.frame_count/self.print_freq) == self.frame_count/float(self.print_freq):
                print time.time()-self.start, self.frame_count
            self.frame_count += 1
        else:
            pass
#        if self.frame_count/10.0 == float(int(self.frame_count/10.0)):
#            self.canvas.show()
#        return self.im

    def _on_mousewheel(self,event):
        if self._job != None:
            self.master.after_cancel(self._job)
            self._job = None
        inc = int((event.delta/120)*(1.0/2.0)*np.log(self.iter_var.get())**2)
        val = self.iter_var.get() + inc
        if val < 5 and np.sign(inc) == -1:
            self._job = None
            return
        elif val < 5 and np.sign(inc) == 1:
            self.iter_var.set(self.iter_var.get()+1)
        else:
            self.iter_var.set(val)
        self.menubar.entryconfigure(3,label=self.iter_var.get())
        self._job = self.master.after(400, self.graph_update)
        
    def pan_update(self,event):
#        print [self.FigSubPlot.get_xlim()[0],self.FigSubPlot.get_xlim()[1]],self.rxlim, [self.FigSubPlot.get_ylim()[0],self.FigSubPlot.get_ylim()[1]],self.rylim
        if [self.FigSubPlot.get_xlim()[0],self.FigSubPlot.get_xlim()[1]] != self.rxlim or [self.FigSubPlot.get_ylim()[0],self.FigSubPlot.get_ylim()[1]] != self.rylim:   
            self.graph_update()
        else:
            return
    
#    def slider_iter(self,*args):
#        if self.iter_var.get() == self.prev_iter:
#            self.graph_update()
#        else:
#            self.prev_iter = self.iter_var.get()
#            self.master.after(1000,self.slider_iter)

    def graph_update(self,*args):
        dimensions = (self.FigSubPlot.get_xlim()[1]-self.FigSubPlot.get_xlim()[0], self.FigSubPlot.get_ylim()[0]-self.FigSubPlot.get_ylim()[1])
        self.xlim = [(self.FigSubPlot.get_xlim()[0]*(self.xlim[1]-self.xlim[0])/(self.rxlim[1]-self.rxlim[0]))+self.xlim[0],(self.FigSubPlot.get_xlim()[1]*(self.xlim[1]-self.xlim[0])/(self.rxlim[1]-self.rxlim[0]))+self.xlim[0]]
#        print (self.rylim[0]-self.FigSubPlot.get_ylim()[0])
        self.ylim = [self.ylim[0]-((self.rylim[0]-self.FigSubPlot.get_ylim()[0])*(self.ylim[1]-self.ylim[0])/(self.rylim[1]-self.rylim[0])),self.ylim[0]-((self.rylim[0]-self.FigSubPlot.get_ylim()[1])*(self.ylim[1]-self.ylim[0])/(self.rylim[1]-self.rylim[0]))]
#        print self.ylim
        if dimensions[0]/dimensions[1] >= 2:
            #x bigger
            size = (int(dimensions[1]*2000/dimensions[0]),2000)
        else:
            size = (1000,int(dimensions[0]*1000/dimensions[1]))
        self.FigSubPlot.clear()
        image = np.zeros(size, dtype=np.uint8)
#
        self.create_ant(self.xlim[0], self.xlim[1], -self.ylim[1], -self.ylim[0], image, self.iter_var.get(),self.eqn_list,self.d)
#        self.im.set_array(image)
        self.FigSubPlot.axis('off')
        self.im = self.FigSubPlot.imshow(image,cmap=self.color_var.get())
        self.canvas.show()    
        self.rxlim = [self.FigSubPlot.get_xlim()[0],self.FigSubPlot.get_xlim()[1]]
        self.rylim = [self.FigSubPlot.get_ylim()[0],self.FigSubPlot.get_ylim()[1]]

class NavigationToolbar(NavigationToolbar2TkAgg):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2TkAgg.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

root = Tk()
screen_resolution = (root.winfo_screenwidth(),0.98*root.winfo_screenheight())
root.geometry("%dx%d+%d+%d" % (screen_resolution[0]/2, 
                               screen_resolution[1]-75,
                               -10,0))

app=App(root)
root.mainloop()
