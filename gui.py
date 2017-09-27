# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:19:26 2017

@author: vinntec
"""
from tkinter import Tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import FALSE, Canvas, N, Frame, Label, Text
from tkinter import SUNKEN, Menu, StringVar, IntVar, END
import os
import platform
import config
import parm_ng, parm_mn
from netgen import NetGen
from report import writeReport
if platform.machine() == "armv7l":
    import dispy
    from pv_utils import get_nodes
else:
    from copy import deepcopy

FINFINITY = 1.7976931348623157e+308
app = None

# Input information passed to Mentor
class DesignIn:
    def __init__(self, nn):
#        self.dist      = [[0.0 for j in range(nn)] for i in range(nn)]
        self.MN_BIFUR  = False  # Bifurcate traffic - split flow onto multiple routes?
        self.MN_CAPS   = [0.0 for i in range(5)]
        self.MN_DIST1  = 0.0
        self.MN_DUPLEX = 'H'
        self.MN_FXCD   = [0.0 for i in range(5)]
        self.MN_MSGLEN = 8000
        self.MN_NCAP   = 5
        self.MN_TRACE  = False
        self.MN_UTIL   = 0.0
        self.MN_VCD_1  = [0.0 for i in range(5)]
        self.MN_VCD_2  = [0.0 for i in range(5)]
        self.nn        = nn
        self.Nname     = ["XX" for i in range(nn)]
        self.req       = [[0.0 for j in range(nn)] for i in range(nn)]
        self.Xcoor     = [0 for i in range(nn)]
        self.Ycoor     = [0 for i in range(nn)]

# Results from Mentor
class Results:
    def __init__(self, model_ix, nl, NetCost, Parms):
        self.model_ix = model_ix # Original job number
        self.nl = nl             # Number of lines in design
        self.NetCost = NetCost   # Network cost
        self.alpha = Parms[0]    # Parameters for this run
        self.slack = Parms[1]
        self.dparm = Parms[2]
        self.rparm = Parms[3]
        self.wparm = Parms[4]
    
#class DesignOut:
#    def __init__(self, nn):
#        np = ( nn * (nn-1) ) // 2
#        self.nl       = 0
#        self.End1     = [0 for i in range(np)]
#        self.End2     = [0 for i in range(np)]
#        self.Lcap     = [0.0 for i in range(np)]
#        self.Lcost    = [0.0 for i in range(np)]
#        self.Ldelay12 = [0.0 for i in range(np)]
#        self.Ldelay21 = [0.0 for i in range(np)]
#        self.Lreq12   = [0.0 for i in range(np)]
#        self.Lreq21   = [0.0 for i in range(np)]
#        self.Lmult    = [0 for i in range(np)]
#        self.Ltree    = [False for i in range(np)]
#        self.Ltype    = [0 for i in range(np)]
#        self.Lutil12  = [0.0 for i in range(np)]
#        self.Lutil21  = [0.0 for i in range(np)]
#        self.Ncap     = [0.0 for i in range(nn)]
#        self.Ndelay   = [0.0 for i in range(nn)]
#        self.Nmsgrate = [0.0 for i in range(nn)]
#        self.Ntype    = ['X' for i in range(nn)]
#        self.Nutil    = [0.0 for i in range(nn)]
#        self.NetCost  = 0.0
#        self.Parms    = []
#        self.Weight   = [0.0 for i in range(nn)]
#
def compute(model_ix, inp, alpha, slack, dparm, rparm, wparm):
    import sys
    sys.path.insert(0, '/home/pi/tetrapi')
    from mentor import Mentor
    (nl, NetCost) = Mentor(model_ix, inp, alpha, slack, dparm, rparm, wparm)
    Parms = [alpha, slack, dparm, rparm, wparm]
    dispy_send_file("Design%d.net" % (model_ix))
    return(nl, NetCost, Parms)

def PVcompute(model_ix, inp, alpha, slack, dparm, rparm, wparm):
    from mentor import Mentor
    (nl, NetCost) = Mentor(model_ix, inp, alpha, slack, dparm, rparm, wparm)
    Parms = [alpha, slack, dparm, rparm, wparm]
    return(nl, NetCost, Parms)

class PVJob:
    def __init__(self, model_ix, inp, alpha, slack, dparm, rparm, wparm):
        self.id  = model_ix
        self.inp = deepcopy(inp)
        self.alpha = alpha
        self.slack = slack
        self.dparm = dparm
        self.rparm = rparm
        self.wparm = wparm

class PVCluster:
    def __init__(self):
        self.job = None

    def submit(self, model_ix, inp, alpha, slack, dparm, rparm, wparm):
        self.job = PVJob(model_ix, inp, alpha, slack, dparm, rparm, wparm)
        return self.job
    
    def print_status(self):
        pass
    
    def close(self):
        pass

class Gui:

    def __init__(self):
        # Set screen dimensions depending on platform
        self.set_Netgen_defaults()
        parm_ng.setNG()
        if (platform.machine() == "armv7l") and config.NG_KERSH:
            # AKER (V&H) coords on TetraPi
            config.canvasWidth = 800
            config.canvasHeight = 500
            config.controlWidth = 20
        elif platform.machine() == "armv7l":
            # PV (random) coords on TetraPi
            config.canvasWidth = 1100
            config.canvasHeight = 650
            config.controlWidth = 20
        elif config.NG_KERSH:
            # Windows AKER coords
            config.canvasWidth = 1500
            config.canvasHeight = 900
            config.controlWidth = 20
        else:
            # Windows PV coords
            config.canvasWidth = 1700
            config.canvasHeight = 900
            config.controlWidth = 20
        self.root = Tk()
        self.root.title("Mentor")
        self.root.option_add('*tearOff', FALSE)
        self.canvas = Canvas(self.root, width=config.canvasWidth, height=config.canvasHeight, background='navy')
        self.canvas.grid(row=0, column=0, sticky=N)
        self.myframe = Frame(self.root, bd=2, relief=SUNKEN)
        self.myframe.grid(row=0, column=1, sticky=N)
        self.spacer = Label(self.myframe, text='Information', fg='blue', width=config.controlWidth)
        self.spacer.grid(row=0, column=1, sticky=N)
        self.info = Text(self.myframe, width=config.controlWidth)
        self.info.grid(row=1, column=1, sticky=N)
        # Allocate data used for Mentor runs
        self.inp = []
        self.cheapest     = FINFINITY
        self.cheapest_ix  = -1
        self.counter      = 0
        self.current      = -1
        self.results = []
        self.utilColor12 = []
        self.utilColor21 = []
        self.LtypeCol = ["blue", "purple", "cyan", "green", "yellow", "red", "magenta", "white"] # line colour code
        # Current model Node data
        self.Nix = None
        self.Ntype = None
        self.Ncap  = None
        self.Nmsgrate = None
        self.Nutil = None
        self.Ndelay = None
        self.Weight = None
        # Current model Line data
        self.Lix = None
        self.End1 = None
        self.End2 = None
        self.Ltype = None
        self.Lmult = None
        self.Lcost = None
        self.Lcap = None
        self.Lreq12 = None
        self.Lreq21 = None
        self.Lmps12 = None
        self.Lmps21 = None
        self.Lutil12 = None
        self.Lutil21 = None
        self.Ldist = None
        self.Lts = None
        self.Ltp = None
        self.Ltw12 = None
        self.Ltw21 = None
        self.Ldelay12 = None
        self.Ldelay21 = None
        self.Ltree = None
        # prepare for zooming
        self.scale = [1.0, 1.0]
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None
        # Create Menu
        self.menubar = Menu(self.root)
        self.root['menu'] = self.menubar
        
        self.menu_net = Menu(self.menubar)
        self.menubar.add_cascade(label='Network', menu = self.menu_net)
        self.menu_net.add_command(label='Generate Network', command = self.doNetgen)

        self.menu_net.add_command(label='Edit NG Parameters', command=self.doEditng)
        self.menu_net.add_command(label='Load Network', command=self.doLoadnet)
        self.menu_net.add_command(label='Save Network', command=self.doSavenet)
        
        self.menu_des = Menu(self.menubar)
        self.menubar.add_cascade(label='Design', menu = self.menu_des)
        self.menu_des.add_command(label='Mentor', command=self.doMentor)
        self.menu_des.add_command(label='Edit MN Parameters', command=self.doEditmn)
        self.menu_des.add_command(label='Load Design', command=self.doLoaddes)
        self.menu_des.add_command(label='Save Design', command=self.doSavedes)

        # Create Map menu
        self.show_nodes = StringVar()
        self.show_nodes.set("A")
        self.menu_map = Menu(self.menubar)
        self.menubar.add_cascade(label="Map", menu=self.menu_map)
        self.menu_map.add_separator()
        self.menu_map.add_radiobutton(label="Node ALL" , variable=self.show_nodes, value="A", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Node Backbone" , variable=self.show_nodes, value="B", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Node Terminals", variable=self.show_nodes, value="T", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Node None", variable=self.show_nodes, value="N", command=self.draw_network)

        self.menu_map.add_separator()
        self.show_names = StringVar()
        self.show_names.set("A")
        self.menu_map.add_radiobutton(label="Name ALL", variable=self.show_names, value="A", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Name Backbone", variable=self.show_names, value="B", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Name Terminal", variable=self.show_names, value="T", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Name None", variable=self.show_names, value="N", command=self.draw_network)

        self.menu_map.add_separator()
        self.show_lines = StringVar()
        self.show_lines.set("A")
        self.menu_map.add_radiobutton(label="Line ALL", variable=self.show_lines, value="A", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Line Backbone", variable=self.show_lines, value="B", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Line Clusters", variable=self.show_lines, value="C", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Line Direct", variable=self.show_lines, value="D", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Line None", variable=self.show_lines, value="N", command=self.draw_network)

        self.menu_map.add_separator()
        self.show_info = StringVar()
        self.show_info.set("M")
        self.menu_map.add_radiobutton(label="Multiples", variable=self.show_info, value="M", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Utilisation", variable=self.show_info, value="U", command=self.draw_network)
        self.menu_map.add_radiobutton(label="Delay", variable=self.show_info, value="D", command=self.draw_network)

        self.menu_map.add_separator()
        self.line_annotate = IntVar()
        self.line_annotate.set(0)
        self.menu_map.add_checkbutton(label="Line Annotate", onvalue=1, offvalue=0, variable=self.line_annotate, command=self.draw_network)
        self.node_annotate = IntVar()
        self.node_annotate.set(0)
        self.menu_map.add_checkbutton(label="Node Annotate", onvalue=1, offvalue=0, variable=self.node_annotate, command=self.draw_network)
        self.tree = IntVar()
        self.tree.set(0)
        self.menu_map.add_checkbutton(label="Show Tree", onvalue=1, offvalue=0, variable=self.tree, command=self.draw_network)

        self.menubar.add_command(label='Report', command=self.doReport)

        self.menubar.add_command(label='Cheapest', command=self.doCheapest)
        self.menubar.add_command(label='First', command=self.doFirst)
        self.menubar.add_command(label='Last', command=self.doLast)
        self.menubar.add_command(label='Next', command=self.doNext)
        self.menubar.add_command(label='Prev', command=self.doPrev)

        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.mainloop()

    def doReport(self):
        if config.design_present:
            writeReport(self)

    def doCheapest(self):
        if config.design_present:
            self.current = self.cheapest_ix
            self.draw_network()
 
    def doFirst(self):
        if config.design_present:
            self.current = 0
            self.draw_network()

    def doLast(self):
        if config.design_present:
            self.current = self.counter - 1
            self.draw_network()

    def doNext(self):
        if config.design_present:
            if self.current < (self.counter - 1):
                self.current += 1
                self.draw_network()
    
    def doPrev(self):
        if config.design_present:
            if self.current > 0:
                self.current -= 1
                self.draw_network()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red')
    
    def on_right_button_press(self, event):
        w = config.canvasWidth
        h = config.canvasHeight
        self.canvas.configure(scrollregion = (0, 0, w-1, h-1))
        self.scale = [1.0, 1.0]
        # clear the drawing area
        self.canvas.delete("all")
        # redraw the map
        if config.network_present:
            self.draw_network()
        self.start_x = self.start_y = None
        
    def on_move_press(self, event):
        if self.start_x == None: # ignore other mouse uses
            return
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)    

    def on_button_release(self, event):
        if self.start_x == None: # ignore other mouse uses
            return
        # save final coords
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        # remove the rectangle
        self.canvas.delete(self.rect)
        self.rect = None
        # determine the ratio of old width/height to new width/height
        divisor = max(curX - self.start_x, curY - self.start_y)
        w = config.canvasWidth
        h = config.canvasHeight
        self.scale[0] = w / divisor
        self.scale[1] = h / divisor
        # rescale all the drawing objects and focus window on selected area
        self.canvas.scale("all", 0, 0, self.scale[0], self.scale[1])
        self.canvas.configure(scrollregion = (self.start_x * self.scale[0], self.start_y * self.scale[1], 
                                              curX * self.scale[0], curY * self.scale[1]))

    def close_window(self):
        """
        close main window and application itself
        """
        if messagebox.askokcancel(" Quit", "Really want to quit?"): 
            # close the logging and reporting files before closing down
            self.root.destroy()

    def updateInfo(self):
        self.info.delete(1.0, END)
        if config.design_present:
            result = self.results[self.current]
            self.info.insert(END, "Cost :  %8d\n"   % (result.NetCost))
            self.info.insert(END, "Alpha:  %8.2f\n" % (result.alpha))
            self.info.insert(END, "Slack:  %8.2f\n" % (result.slack))
            self.info.insert(END, "Dparm:  %8.2f\n" % (result.dparm))
            self.info.insert(END, "Rparm:  %8.2f\n" % (result.rparm))
            self.info.insert(END, "Wparm:  %8.2f\n" % (result.wparm))
            self.info.insert(END, "Bifur:  %8s\n"   % (self.inp.MN_BIFUR))
            self.info.insert(END, "Design: %8d\n"   % (self.current))
            self.info.insert(END, "Designs:%8d\n"   % (self.counter))
            self.info.tag_config("cheap", foreground="red")
            if self.current == self.cheapest_ix:
                self.info.insert(END, "CHEAPEST\n", "cheap")
            if self.show_info.get() == 'U':
                self.info.insert(END, "UTILISATION\n")
                self.info.tag_config("over", foreground="white", background="red")
                self.info.tag_config("high", foreground="black", background="orange")
                self.info.tag_config("equal", foreground="black", background="yellow")
                self.info.tag_config("ok", foreground="white", background="green")
                self.info.tag_config("low", foreground="white", background="blue")
                self.info.insert(END, ">= 100%\n", "over")
                self.info.insert(END, "> %d%%\n" % (self.inp.MN_UTIL * 100), "high")
                self.info.insert(END, "= %d%%\n" % (self.inp.MN_UTIL * 100), "equal")
                self.info.insert(END, "10%% - %d%%\n" % (self.inp.MN_UTIL * 100), "ok")
                self.info.insert(END, "< 10%\n", "low")
            elif self.show_info.get() == 'M':
                self.info.insert(END, "MULTIPLES\n")
                self.info.tag_config("type0", foreground="white", background="blue")
                self.info.tag_config("type1", foreground="white", background="purple")
                self.info.tag_config("type2", foreground="black", background="cyan")
                self.info.tag_config("type3", foreground="white", background="green")
                self.info.tag_config("type4", foreground="black", background="yellow")
                self.info.tag_config("type5", foreground="white", background="red")
                self.info.tag_config("type6", foreground="black", background="magenta")
                self.info.tag_config("type7", foreground="black", background="white")
                self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[0]), "type0")
                if self.inp.MN_NCAP > 1:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[1]), "type1")
                if self.inp.MN_NCAP > 2:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[2]), "type2")
                if self.inp.MN_NCAP > 3:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[3]), "type3")
                if self.inp.MN_NCAP > 4:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[4]), "type4")
                if self.inp.MN_NCAP > 5:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[5]), "type5")
                if self.inp.MN_NCAP > 6:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[6]), "type6")
                if self.inp.MN_NCAP > 7:
                    self.info.insert(END, "%8d\n" % (self.inp.MN_CAPS[7]), "type7")
            elif self.show_info.get() == 'D':
                self.info.insert(END, "DELAY\n")
                self.info.tag_config("d0", foreground="black", background="red")
                self.info.tag_config("d1", foreground="black", background="deep pink")
                self.info.tag_config("d2", foreground="black", background="orange")
                self.info.tag_config("d3", foreground="black", background="gold")
                self.info.tag_config("d4", foreground="black", background="yellow")
                self.info.tag_config("d5", foreground="black", background="green2")
                self.info.tag_config("d6", foreground="black", background="pale green")
                self.info.tag_config("d7", foreground="white", background="dark green")
                self.info.tag_config("d8", foreground="black", background="cyan")
                self.info.tag_config("d9", foreground="black", background="sky blue")
                self.info.tag_config("da", foreground="white", background="blue")
                self.info.insert(END, "> 1.0s\n", "d0")
                self.info.insert(END, "> 0.9s\n", "d1")
                self.info.insert(END, "> 0.8s\n", "d2")
                self.info.insert(END, "> 0.7s\n", "d3")
                self.info.insert(END, "> 0.6s\n", "d4")
                self.info.insert(END, "> 0.5s\n", "d5")
                self.info.insert(END, "> 0.4s\n", "d6")
                self.info.insert(END, "> 0.3s\n", "d7")
                self.info.insert(END, "> 0.2s\n", "d8")
                self.info.insert(END, "> 0.1s\n", "d9")
                self.info.insert(END, "> 0.0s\n", "da")
            if self.scale != [1.0, 1.0]: # Zoomed
                self.on_right_button_press(None)

    def draw_nodes(self):
        radius = 5
        if config.network_present and config.design_present == False:
            for i in range(self.inp.nn):
                self.canvas.create_oval(self.inp.Xcoor[i]-radius, self.inp.Ycoor[i]-radius, self.inp.Xcoor[i]+radius, self.inp.Ycoor[i]+radius, fill='cyan', width=0)
                self.canvas.create_text(self.inp.Xcoor[i]+4*radius, self.inp.Ycoor[i]-2*radius, fill='cyan', text=self.inp.Nname[i], font=('Helvetica', '16'))
        elif config.network_present and config.design_present:
            note = ""
            for i in range(self.inp.nn):
                colour = "black"
                if ((self.show_nodes.get() == 'A')
                or (self.show_nodes.get() == 'B' and self.Ntype[i] in ['C', 'M'])
                or (self.show_nodes.get() == 'T' and self.Ntype[i] in ['T'])):
                    if self.show_info.get() == 'M':
                        colour = self.setNtypeCol(self.Ntype[i])
                        note = "%d" % (self.Ncap[i])
                    elif self.show_info.get() == 'D':
                        colour = self.setDelayCol(self.Ndelay[i])
                        note = "%5.3f" % (self.Ndelay[i])
                    elif self.show_info.get() == 'U':
                        colour = self.setUtilCol(self.Nutil[i])
                        note = "%d%%" % (self.Nutil[i] * 100) 
                    self.canvas.create_oval(self.inp.Xcoor[i]-radius, self.inp.Ycoor[i]-radius, self.inp.Xcoor[i]+radius, self.inp.Ycoor[i]+radius, fill=colour, width=0)
                    if self.node_annotate.get() == 1:
                        self.canvas.create_text(self.inp.Xcoor[i]+4*radius, self.inp.Ycoor[i]+2*radius, fill=colour, text=note, font=('Helvetica', '16'))
                    if ((self.show_names.get() == 'A')
                    or (self.show_names.get() == 'B' and self.Ntype[i] in ['C', 'M'])
                    or (self.show_names.get() == 'T' and self.Ntype[i] in ['T'])):
                        self.canvas.create_text(self.inp.Xcoor[i]+4*radius, self.inp.Ycoor[i]-2*radius, fill=colour, text=self.inp.Nname[i], font=('Helvetica', '16'))
                    
    def setNtypeCol(self, Ntype):
        if Ntype == 'C':
            return('red')
        elif Ntype == 'M':
            return('yellow')
        else:
            return('blue')

    def setLtypeCol(self, Ltype):
        return(self.LtypeCol[Ltype])
        
    def setUtilCol(self, util):
        colour = ''
        if util >= 1.0:
            colour = 'red'
        elif util > self.inp.MN_UTIL:
            colour = 'orange'
        elif util == self.inp.MN_UTIL:
            colour = 'yellow'
        elif util < 0.1:
            colour = 'blue'
        else:
            colour = 'green'
        return colour
    
    def setDelayCol(self, delay):
        colour = ''
        if delay > 1.0 or delay < 0.0:
            colour = 'red'
        elif delay > 0.9:
            colour = 'deep pink'
        elif delay > 0.8:
            colour = 'orange'
        elif delay > 0.7:
            colour = 'gold'
        elif delay > 0.6:
            colour = 'yellow'
        elif delay > 0.5:
            colour = 'green2'
        elif delay > 0.4:
            colour = 'pale green'
        elif delay > 0.3:
            colour = 'dark green'
        elif delay > 0.2:
            colour = 'cyan'
        elif delay > 0.1:
            colour = 'sky blue'
        else:
            colour = 'blue'
        return colour

    def draw_lines(self):
        if config.design_present:
            for i in range(self.results[self.current].nl):
                if ((self.show_lines.get() == 'A') # All
                or (self.show_lines.get() == 'B' # BB
                    and self.Ntype[self.End1[i]] in ['C', 'M']
                    and self.Ntype[self.End2[i]] in ['C', 'M'])
                or (self.show_lines.get() == 'C' # Clusters
                    and self.Ltree[i] == True
                    and (self.Ntype[self.End1[i]] in ['T']
                    or   self.Ntype[self.End2[i]] in ['T']))
                or (self.show_lines.get() == 'D' # Direct
                    and self.Ltree[i] == False
                    and (self.Ntype[self.End1[i]] in ['T']
                    or   self.Ntype[self.End2[i]] in ['T']))):
                    midx = (self.inp.Xcoor[self.End1[i]] + self.inp.Xcoor[self.End2[i]]) // 2
                    midy = (self.inp.Ycoor[self.End1[i]] + self.inp.Ycoor[self.End2[i]]) // 2
                    if self.show_info.get() == 'M':
                        if self.tree.get() == 1 and self.Ltree[i] == True:
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i] * (self.Ltype[i] + 1), fill="red")
                        else:
                            colour = self.setLtypeCol(self.Ltype[i])
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill=colour)
                        if self.line_annotate.get() == 1:
                            lt = "%dk/%d" % (self.inp.MN_CAPS[self.Ltype[i]] / 1000.0, self.Lmult[i])
                            self.canvas.create_text(midx, midy, fill='red', text=lt, font=('Helvetica', '16'))
                    elif self.show_info.get() == 'U': 
                        if self.tree.get() == 1 and self.Ltree[i] == True:
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               midx, midy,
                                               width=self.Lmult[i] * (self.Ltype[i] + 1), fill="red")
                            self.canvas.create_line(midx, midy,
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill="red")
                        else:
                            colour = self.setUtilCol(self.Lutil12[i])
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               midx, midy,
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill=colour)
                            colour = self.setUtilCol(self.Lutil21[i])
                            self.canvas.create_line(midx, midy,
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill=colour)
                        if self.line_annotate.get() == 1:
                            outline = "%d%%-%d%%" % (self.Lutil12[i] * 100, self.Lutil21[i] * 100)
                            self.canvas.create_text(midx, midy, fill='red', text=outline, font=('Helvetica', '16'))
                    elif self.show_info.get() == 'D': 
                        if self.tree.get() == 1 and self.Ltree[i] == True:
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i] * (self.Ltype[i] + 1), fill="red")
                        else:
                            colour = self.setDelayCol(self.Ldelay12[i])
                            self.canvas.create_line(self.inp.Xcoor[self.End1[i]], self.inp.Ycoor[self.End1[i]],
                                               midx, midy,
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill=colour)
                            colour = self.setDelayCol(self.Ldelay21[i])
                            self.canvas.create_line(midx, midy,
                                               self.inp.Xcoor[self.End2[i]], self.inp.Ycoor[self.End2[i]],
                                               width=self.Lmult[i]* (self.Ltype[i] + 1), fill=colour)
                        if self.line_annotate.get() == 1:
                            outline = "%5.3f-%5.3f" % (self.Ldelay12[i], self.Ldelay21[i])
                            self.canvas.create_text(midx, midy, fill='red', text=outline, font=('Helvetica', '16'))

    def read_network(self, model_ix):
        self.Nix      = []
        self.Ntype    = []
        self.Ncap     = []
        self.Nmsgrate = []
        self.Nutil    = []
        self.Ndelay   = []
        self.Lix      = []
        self.End1     = []
        self.End2     = []
        self.Ltype    = []
        self.Lmult    = []
        self.Lcost    = []
        self.Lcap     = []
        self.Lreq12   = []
        self.Lreq21   = []
        self.Lmps12   = []
        self.Lmps21   = []
        self.Lutil12  = []
        self.Lutil21  = []
        self.Ldist    = []
        self.Lts      = []
        self.Ltp      = []
        self.Ltw12    = []
        self.Ltw21    = []
        self.Ldelay12 = []
        self.Ldelay21 = []
        self.Ltree    = []
        self.Weight   = []
        with open("Design%d.net" % (model_ix)) as f:
            for inar in f:
                word_list = inar.rsplit(sep=',')
                if word_list[0] == 'N':
                    # Node data
                    self.Nix.append(int(word_list[1]))
                    self.Ntype.append(word_list[2])
                    self.Ncap.append(float(word_list[3]))
                    self.Nmsgrate.append(float(word_list[4]))
                    self.Nutil.append(float(word_list[5]))
                    self.Ndelay.append(float(word_list[6]))
                    self.Weight.append(float(word_list[7]))
                elif word_list[0] == 'L':
                    self.Lix.append(int(word_list[1]))
                    self.End1.append(int(word_list[2]))
                    self.End2.append(int(word_list[3]))
                    self.Ltype.append(int(word_list[4]))
                    self.Lmult.append(int(word_list[5]))
                    self.Lcost.append(float(word_list[6]))
                    self.Lcap.append(float(word_list[7]))
                    self.Lreq12.append(float(word_list[8]))
                    self.Lreq21.append(float(word_list[9]))
                    self.Lmps12.append(float(word_list[10]))
                    self.Lmps21.append(float(word_list[11]))
                    self.Lutil12.append(float(word_list[12]))
                    self.Lutil21.append(float(word_list[13]))
                    self.Ldist.append(float(word_list[14]))
                    self.Lts.append(float(word_list[15]))
                    self.Ltp.append(float(word_list[16]))
                    self.Ltw12.append(float(word_list[17]))
                    self.Ltw21.append(float(word_list[18]))
                    self.Ldelay12.append(float(word_list[19]))
                    self.Ldelay21.append(float(word_list[20]))
                    self.Ltree.append(bool(word_list[21]))
        Nlen = len(self.Nix)
        Llen = len(self.Lix)
        if Nlen != self.inp.nn:
            print("ERROR - Nodes read in %d is not the same as nn %d" % (Nlen, self.inp.nn))
        if Llen != self.results[self.current].nl:
            print("ERROR - Lines read in %d is not the same as nl %d" % (Llen, self.results[self.current].nl))

    def draw_network(self):
        if config.design_present:
            self.read_network(self.results[self.current].model_ix)
        self.canvas.delete("all")
        self.updateInfo()
        self.draw_nodes()
        self.draw_lines()
    
    def kill_network(self):
        if config.design_present:            
            config.design_present = False
            for i in range(self.counter):
                self.results[i].End1     = None
                self.results[i].End2     = None
                self.results[i].Lcap     = None
                self.results[i].Lcost    = None
                self.results[i].Ldelay12 = None
                self.results[i].Ldelay21 = None
                self.results[i].Lreq12   = None
                self.results[i].Lreq21   = None
                self.results[i].Lmult    = None
                self.results[i].Ltree    = None
                self.results[i].Ltype    = None
                self.results[i].Lutil12  = None
                self.results[i].Lutil21  = None
                self.results[i].Nmsgrate = None
                self.results[i].Ncap     = None
                self.results[i].Ndelay   = None
                self.results[i].Ntype    = None
                self.results[i].Nutil    = None
                self.results[i].Parms    = None
                self.results[i].Weight   = None
                self.results[i] = None
            self.results = []
        if config.network_present:
            config.network_present = False
#            self.inp.dist = None
            self.inp.MN_CAPS = None
            self.inp.MN_FXCD = None
            self.inp.MN_VCD_1 = None
            self.inp.MN_VCD_2 = None
            self.inp.Nname = None
            self.inp.req = None
            self.inp.Xcoor = None
            self.inp.Ycoor = None
            self.inp = None

    def set_Netgen_defaults(self):
        config.NG_CFNAME  = "CITY.DAT" # name of file with specific cities
        config.NG_FXTRF   = 2000.0     # fixed traf/pair
        config.NG_KERSH   = True       # Use AKER's NetGen
        config.NG_NHOST   = 0          # number of host centres (first n if set)
        config.NG_NMODEL  = 'F'        # node model SFRL
        config.NG_NN      = 8          # number of nodes
        config.NG_RNTRF   = 0.0        # random traf/pair 0-1
        config.NG_VTRFD   = 0.0        # variable traf/dist 0-1
        config.NG_VTRFP   = 0.0        # variable traf/pop 0-1

    def doNetgen(self):
        self.kill_network()
        self.set_Netgen_defaults()
        parm_ng.setNG()
        self.inp = DesignIn(config.NG_NN)
#        self.set_Mentor_defaults()
#        parm_mn.setMN(self.inp) # set parameters for this run
        # Generate network
        NetGen(self.inp)
        if (platform.machine() == "armv7l") and config.NG_KERSH:
            for i in range(self.inp.nn):
                self.inp.Xcoor[i] = self.inp.Xcoor[i] // 2
                self.inp.Ycoor[i] = self.inp.Ycoor[i] // 2
        self.draw_network()
    
    def doLoadnet(self):
        filename = filedialog.askopenfilename(title = "Open network file",
                                              defaultextension = '.inp',
                                              filetypes = (("network files","*.inp"),("all files","*.*")))
        if filename == "":
            return
        self.kill_network()
        with open(filename) as f:
            for inar in f:
                word_list = inar.rsplit(sep=',')
                if word_list[0] == 'P':
                    # Parameters
                    config.NG_CFNAME = word_list[1]
                    config.NG_FXTRF  = float(word_list[2])
                    config.NG_KERSH  = bool(word_list[3])
                    config.NG_NHOST  = int(word_list[4])
                    config.NG_NMODEL = word_list[5]
                    config.NG_NN     = int(word_list[6])
                    config.NG_RNTRF  = float(word_list[7])
                    config.NG_VTRFD  = float(word_list[8])
                    config.NG_VTRFP  = float(word_list[9])
                    config.np        = int(word_list[10])
                    self.inp = DesignIn(config.NG_NN)
                elif word_list[0] == 'N':
                    # Node
                    i = int(word_list[1])
                    self.inp.Nname[i] = word_list[2]
                    self.inp.Xcoor[i] = int(word_list[3])
                    self.inp.Ycoor[i] = int(word_list[4])
                elif word_list[0] == 'R':
                    # Requirement
                    i = int(word_list[1])
                    j = int(word_list[2])
                    self.inp.req[i][j] = float(word_list[3])
        if (platform.machine() == "armv7l") and config.NG_KERSH:
            for i in range(self.inp.nn):
                self.inp.Xcoor[i] = self.inp.Xcoor[i] // 2
                self.inp.Ycoor[i] = self.inp.Ycoor[i] // 2
        config.network_present = True
        self.draw_network()
    
    def doSavenet(self):
        if config.network_present != True:
            messagebox.showerror("No network present", "You cannot save a network unless there is one present", icon = "warning")
            return
        filename = filedialog.asksaveasfilename(title = "Set network file",
                                                defaultextension = '.inp',
                                                filetypes = (("network files","*.inp"),("all files","*.*")))
        if filename == "":
            return
        nn = self.inp.nn        
        inp_file = open(filename, 'w')
        inp_file.write("P,%s,%f,%s,%d,%s,%d,%f,%f,%f,%d,\n" % (config.NG_CFNAME, config.NG_FXTRF,
                                                               str(config.NG_KERSH), config.NG_NHOST,
                                                               config.NG_NMODEL, config.NG_NN,
                                                               config.NG_RNTRF, config.NG_VTRFD,
                                                               config.NG_VTRFP, config.np))
        for i in range(nn):
            inp_file.write("N,%d,%s,%d,%d,\n" % (i, self.inp.Nname[i], self.inp.Xcoor[i], self.inp.Ycoor[i]))
        for i in range(nn):
            for j in range(nn):
                if self.inp.req[i][j] != 0.0:
                    # Don't write 0 requirements
                    inp_file.write("R,%d,%d,%f,\n" % (i, j, self.inp.req[i][j]))
        inp_file.close()
    
    def doEditng(self):
        pass
    
    def set_Mentor_defaults(self):
        # BT Kilostream/Megastream 1990s per month over 5 years
        self.inp.MN_BIFUR = False        # Bifurcate traffic - split flow onto multiple routes?
        self.inp.MN_CAPS  = [64000.0, 128000.0, 256000.0, 512000.0, 1024000.0, 2048000.0, 8448000.0, 34368000.0] # line speeds
        self.inp.MN_DIST1 = 15.0         # line cost distance for VCD_1 costs
        self.inp.MN_DUPLEX = "H"         # Line duplexity
        self.inp.MN_FXCD  = [171.67, 423.33, 463.33, 543.33, 703.33, 269.43, 919.97, 5761.07] # fixed line cost
        self.inp.MN_MSGLEN = 8000        # avg msg length in bits
        self.inp.MN_NCAP  = 8            # number of line capacities
        self.inp.MN_TRACE = False        # write trace to log file?
        self.inp.MN_UTIL  = 0.6          # max line utilisation
        self.inp.MN_VCD_1 = [9.33, 1.50, 3.0, 6.0, 12.0, 44.11, 127.39, 100.0] # variable line cost up to MN_DIST1
        self.inp.MN_VCD_2 = [0.56, 1.50, 3.0, 6.0, 12.0, 12.5,   37.5,  100.0] # variable line cost above MN_DIST1

    def doMentor(self):
        self.set_Mentor_defaults()
        parm_mn.setMN(self.inp) # set parameters for this run
        self.cheapest     = FINFINITY
        self.cheapest_ix  = -1
        self.counter      = 0
        self.current      = -1
        runs         = 0
        discards     = 0
        fails        = 0
        COST_FILTER  = 2000.0
        jobs  = []
        costs = []  # temp storage
    
        if platform.machine() == "armv7l":
#            cluster = dispy.JobCluster(compute, nodes = get_nodes(), depends=[DesignIn, DesignOut], recover_file = "recovery_file")
            cluster = dispy.JobCluster(compute, nodes = get_nodes(), depends=[DesignIn], recover_file = "recovery_file")
            cluster.set_node_cpus("192.168.1.31", 2)
            cluster.set_node_cpus("192.168.1.32", 2)
            cluster.set_node_cpus("192.168.1.33", 2)
            cluster.set_node_cpus("192.168.1.34", 2)
#            cluster = dispy.JobCluster(compute, nodes = ["192.168.1.31"], depends=[DesignIn, DesignOut], recover_file = "recovery_file")
#            cluster.set_node_cpus("192.168.1.31", 2)
        else:
            cluster = PVCluster()
    
        test = False
        running = True
        MN_ALPHA = parm_mn.MN_ALPHA_min
        while (MN_ALPHA <= parm_mn.MN_ALPHA_max) and running:
            MN_SLACK = parm_mn.MN_SLACK_min
            while (MN_SLACK <= parm_mn.MN_SLACK_max) and running:
                MN_DPARM = parm_mn.MN_DPARM_min
                while (MN_DPARM <= parm_mn.MN_DPARM_max) and running:
                    MN_RPARM = parm_mn.MN_RPARM_min
                    while (MN_RPARM <= parm_mn.MN_RPARM_max) and running:
                        MN_WPARM = parm_mn.MN_WPARM_min
                        while (MN_WPARM <= parm_mn.MN_WPARM_max) and running:
                            job = cluster.submit(runs, self.inp, MN_ALPHA, MN_SLACK, 
                                                 MN_DPARM, MN_RPARM, MN_WPARM)
                            job.id = runs
                            jobs.append(job)
                            runs += 1
                            if test:
                                running = False
                            MN_WPARM += parm_mn.MN_WPARM_inc
                        MN_RPARM += parm_mn.MN_RPARM_inc
                    MN_DPARM += parm_mn.MN_DPARM_inc
                MN_SLACK += parm_mn.MN_SLACK_inc
            MN_ALPHA += parm_mn.MN_ALPHA_inc
    
        for job in jobs:
            if platform.machine() == "armv7l":
                (nl, NetCost, Parms) = job() # wait for job to finish
            else:
                (nl, NetCost, Parms) = PVcompute(job.id, job.inp, job.alpha, job.slack, job.dparm, job.rparm, job.wparm)
            if nl != 0:
                if (NetCost <= (self.cheapest + COST_FILTER)) and (NetCost not in costs):
                    costs.append(NetCost)
                    self.results.append(Results(job.id, nl, NetCost, Parms)) # save results
                    if NetCost < self.cheapest:
                        self.cheapest_ix = self.counter
                        self.cheapest = NetCost
                        print("New cheapest found ix: %4d  cost: %8.0f  save: %4d" 
                              % (job.id, self.cheapest, self.counter))
                    else:
                        print("Within COST_FILTER ix: %4d  cost: %8.0f  save: %4d" % (job.id, NetCost, self.counter))
                    self.counter += 1
                else:
                    print("Discarding........ ix: %4d  cost: %8.0f  disc: %4d" % (job.id, NetCost, discards))
                    os.remove("Design%d.net" % (job.id))
                    discards += 1
            else:
                print("FAILED............ ix: %4d  cost: %8.0f  fail: %4d" % (job.id, NetCost, fails))
                fails += 1 # fails will have nl == 0
        if platform.machine() == "armv7l":
            cluster.print_status()
            cluster.close()
        print(runs)    
        print("Pass: %5d  Discard: %5d  Fail: %5d  Total: %5d" % (self.counter, discards, fails, (self.counter + discards + fails)))

        self.current = self.cheapest_ix
        config.design_present = True
        self.draw_network()
    
    def doLoaddes(self):
        pass
    
    def doSavedes(self):
        if config.design_present != True:
            messagebox.showerror("No design present", "You cannot save a design unless there is one present", icon = "warning")
            return
        filename = filedialog.asksaveasfilename(title = "Set design file",
                                                defaultextension = '.net',
                                                filetypes = (("design files","*.net"),("all files","*.*")))
        if filename == "":
            return
        model_ix = self.results[self.current].model_ix
        with open("Design%d.net" % (model_ix)) as f:
            with open(filename, "w") as f1:
                for line in f:
                    f1.write(line)    

    def doEditmn(self):
        pass

if __name__ == '__main__':
    app = Gui()
