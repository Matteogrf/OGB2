
import sys
from config import options
from TargetControl import Bot

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import gui_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    gui_support.set_Tk_var()
    top = ControlTarget (root)
    gui_support.init(root, top)
    root.mainloop()

w = None
def create_ControlTarget(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel (root)
    gui_support.set_Tk_var()
    top = ControlTarget (w)
    gui_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_ControlTarget():
    global w
    w.destroy()
    w = None

class ControlTarget:
    def __init__(self,top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#ececec' # Closest X11 color: 'gray92' 
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("507x801+650+8")
        top.title("ControlTarget")
        top.configure(background="#d9d9d9")

        self.lblCredentials = tk.Label(top)
        self.lblCredentials.place(relx=0.0, rely=0.0, height=46, width=506)
        self.lblCredentials.configure(background="#d9d9d9")
        self.lblCredentials.configure(disabledforeground="#a3a3a3")
        self.lblCredentials.configure(foreground="#000000")
        self.lblCredentials.configure(text='''CREDENZIALI''')
        self.lblCredentials.configure(width=506)

        self.lblServer = tk.Label(top)
        self.lblServer.place(relx=0.079, rely=0.087, height=26, width=127)
        self.lblServer.configure(anchor='w')
        self.lblServer.configure(background="#d9d9d9")
        self.lblServer.configure(disabledforeground="#a3a3a3")
        self.lblServer.configure(foreground="#000000")
        self.lblServer.configure(text='''Server''')
        self.lblServer.configure(width=127)

        self.lblUserName = tk.Label(top)
        self.lblUserName.place(relx=0.079, rely=0.137, height=26, width=75)
        self.lblUserName.configure(background="#d9d9d9")
        self.lblUserName.configure(disabledforeground="#a3a3a3")
        self.lblUserName.configure(foreground="#000000")
        self.lblUserName.configure(text='''UserName''')

        self.lblPassword = tk.Label(top)
        self.lblPassword.place(relx=0.079, rely=0.187, height=26, width=68)
        self.lblPassword.configure(background="#d9d9d9")
        self.lblPassword.configure(disabledforeground="#a3a3a3")
        self.lblPassword.configure(foreground="#000000")
        self.lblPassword.configure(text='''Password''')

        self.lblPlayerId = tk.Label(top)
        self.lblPlayerId.place(relx=0.079, rely=0.237, height=26, width=59)
        self.lblPlayerId.configure(background="#d9d9d9")
        self.lblPlayerId.configure(disabledforeground="#a3a3a3")
        self.lblPlayerId.configure(foreground="#000000")
        self.lblPlayerId.configure(text='''PlayerId''')

        self.lblSettings = tk.Label(top)
        self.lblSettings.place(relx=0.0, rely=0.3, height=26, width=507)
        self.lblSettings.configure(background="#d9d9d9")
        self.lblSettings.configure(disabledforeground="#a3a3a3")
        self.lblSettings.configure(foreground="#000000")
        self.lblSettings.configure(text='''IMPOSTAZIONI''')
        self.lblSettings.configure(width=507)

        self.lblSeed = tk.Label(top)
        self.lblSeed.place(relx=0.079, rely=0.487, height=26, width=39)
        self.lblSeed.configure(background="#d9d9d9")
        self.lblSeed.configure(cursor="fleur")
        self.lblSeed.configure(disabledforeground="#a3a3a3")
        self.lblSeed.configure(foreground="#000000")
        self.lblSeed.configure(text='''Seed''')

        self.lblInterval = tk.Label(top)
        self.lblInterval.place(relx=0.079, rely=0.537, height=26, width=55)
        self.lblInterval.configure(background="#d9d9d9")
        self.lblInterval.configure(disabledforeground="#a3a3a3")
        self.lblInterval.configure(foreground="#000000")
        self.lblInterval.configure(text='''Interval''')

        self.TSeparator1 = ttk.Separator(top)
        self.TSeparator1.place(relx=-0.02, rely=0.062, relwidth=1.045)
        self.TSeparator1.configure(cursor="fleur")

        self.TSeparator2 = ttk.Separator(top)
        self.TSeparator2.place(relx=-0.02, rely=0.287, relwidth=1.026)

        self.TSeparator3 = ttk.Separator(top)
        self.TSeparator3.place(relx=-0.02, rely=0.35, relwidth=1.026)

        self.eSeed = tk.Entry(top)
        self.eSeed.place(relx=0.335, rely=0.487, height=24, relwidth=0.619)
        self.eSeed.configure(background="white")
        self.eSeed.configure(disabledforeground="#a3a3a3")
        self.eSeed.configure(font="TkFixedFont")
        self.eSeed.configure(foreground="#000000")
        self.eSeed.configure(insertbackground="black")
        self.eSeed.configure(width=314)
        self.eSeed.insert(0, options['general']['seed'])

        self.eInterval = tk.Entry(top)
        self.eInterval.place(relx=0.335, rely=0.537, height=24, relwidth=0.619)
        self.eInterval.configure(background="white")
        self.eInterval.configure(disabledforeground="#a3a3a3")
        self.eInterval.configure(font="TkFixedFont")
        self.eInterval.configure(foreground="#000000")
        self.eInterval.configure(insertbackground="black")
        self.eInterval.configure(width=314)
        self.eInterval.insert(0, options['general']['check_interval'])

        self.mSettings = tk.Message(top)
        self.mSettings.place(relx=0.059, rely=0.362, relheight=0.1
                , relwidth=0.88)
        self.mSettings.configure(background="#d9d9d9")
        self.mSettings.configure(foreground="#000000")
        self.mSettings.configure(highlightbackground="#d9d9d9")
        self.mSettings.configure(highlightcolor="black")
        self.mSettings.configure(text='''Formula Calcolo Tempo di riposo in secondi:
t=random(seed-random(0,interval),seed+random(0,interval))
Es. seed=800,interval=50
t=numero compreso tra 750 e 850''')
        self.mSettings.configure(width=446)

        self.TSeparator4 = ttk.Separator(top)
        self.TSeparator4.place(relx=0.0, rely=0.587, relwidth=1.006)

        self.lblTarget = tk.Label(top)
        self.lblTarget.place(relx=0.0, rely=0.599, height=26, width=509)
        self.lblTarget.configure(background="#d9d9d9")
        self.lblTarget.configure(disabledforeground="#a3a3a3")
        self.lblTarget.configure(foreground="#000000")
        self.lblTarget.configure(text='''TARGET''')
        self.lblTarget.configure(width=509)

        self.TSeparator5 = ttk.Separator(top)
        self.TSeparator5.place(relx=-0.02, rely=0.637, relwidth=1.026)

        self.mTarget = tk.Message(top)
        self.mTarget.place(relx=0.039, rely=0.662, relheight=0.037
                , relwidth=0.939)
        self.mTarget.configure(background="#d9d9d9")
        self.mTarget.configure(foreground="#000000")
        self.mTarget.configure(highlightbackground="#d9d9d9")
        self.mTarget.configure(highlightcolor="black")
        self.mTarget.configure(text='''Inserire i nomi dei target separati da && (2&)''')
        self.mTarget.configure(width=476)

        self.eServer = tk.Entry(top)
        self.eServer.place(relx=0.335, rely=0.087,height=24, relwidth=0.619)
        self.eServer.configure(background="white")
        self.eServer.configure(disabledforeground="#a3a3a3")
        self.eServer.configure(font="TkFixedFont")
        self.eServer.configure(foreground="#000000")
        self.eServer.configure(insertbackground="black")
        self.eServer.configure(width=314)
        self.eServer.insert(0, options['credentials']['server'])

        self.eUserName = tk.Entry(top,textvariable=options['credentials']['username'])
        self.eUserName.place(relx=0.335, rely=0.137,height=24, relwidth=0.619)
        self.eUserName.configure(background="white")
        self.eUserName.configure(disabledforeground="#a3a3a3")
        self.eUserName.configure(font="TkFixedFont")
        self.eUserName.configure(foreground="#000000")
        self.eUserName.configure(insertbackground="black")
        self.eUserName.configure(width=314)
        self.eUserName.insert(0,options['credentials']['username'])

        self.ePassword = tk.Entry(top)
        self.ePassword.place(relx=0.335, rely=0.187,height=24, relwidth=0.619)
        self.ePassword.configure(background="white")
        self.ePassword.configure(disabledforeground="#a3a3a3")
        self.ePassword.configure(font="TkFixedFont")
        self.ePassword.configure(foreground="#000000")
        self.ePassword.configure(insertbackground="black")
        self.ePassword.configure(width=314)
        self.ePassword.insert(0,options['credentials']['password'])

        self.ePlayerId = tk.Entry(top)
        self.ePlayerId.place(relx=0.335, rely=0.237,height=24, relwidth=0.619)
        self.ePlayerId.configure(background="white")
        self.ePlayerId.configure(disabledforeground="#a3a3a3")
        self.ePlayerId.configure(font="TkFixedFont")
        self.ePlayerId.configure(foreground="#000000")
        self.ePlayerId.configure(insertbackground="black")
        self.ePlayerId.configure(width=314)
        self.ePlayerId.insert(0,options['credentials']['player_id'])

        self.eTargets = tk.Entry(top)
        self.eTargets.place(relx=0.039, rely=0.82,height=34, relwidth=0.915)
        self.eTargets.configure(background="white")
        self.eTargets.configure(disabledforeground="#a3a3a3")
        self.eTargets.configure(font="TkFixedFont")
        self.eTargets.configure(foreground="#000000")
        self.eTargets.configure(insertbackground="black")
        self.eTargets.configure(width=464)
        self.eTargets.insert(0,options['targets']['name'])

        self.btStart = tk.Button(top)
        self.btStart.place(relx=0.039, rely=0.894, height=53, width=226)
        self.btStart.configure(activebackground="#ececec")
        self.btStart.configure(activeforeground="#000000")
        self.btStart.configure(background="#d9d9d9")
        self.btStart.configure(command=self.startBot)
        self.btStart.configure(disabledforeground="#a3a3a3")
        self.btStart.configure(foreground="#000000")
        self.btStart.configure(highlightbackground="#d9d9d9")
        self.btStart.configure(highlightcolor="black")
        self.btStart.configure(pady="0")
        self.btStart.configure(text='''Start''')
        self.btStart.configure(width=226)

        self.btSave = tk.Button(top)
        self.btSave.place(relx=0.513, rely=0.894, height=53, width=226)
        self.btSave.configure(activebackground="#ececec")
        self.btSave.configure(activeforeground="#000000")
        self.btSave.configure(background="#d9d9d9")
        self.btSave.configure(command=self.saveConfig)
        self.btSave.configure(disabledforeground="#a3a3a3")
        self.btSave.configure(foreground="#000000")
        self.btSave.configure(highlightbackground="#d9d9d9")
        self.btSave.configure(highlightcolor="black")
        self.btSave.configure(pady="0")
        self.btSave.configure(text='''Salva''')
        self.btSave.configure(width=226)

    def saveConfig(self):
        options.updateValue('credentials', 'server', self.eServer.get())
        options.updateValue('credentials', 'username', self.eUserName.get())
        options.updateValue('credentials', 'password', self.ePassword.get())
        options.updateValue('credentials', 'player_id', self.ePlayerId.get())
        options.updateValue('general', 'seed', self.eSeed.get())
        options.updateValue('general', 'check_interval', self.eInterval.get())
        options.updateValue('targets', 'name', self.eTargets.get())

    def startBot(self):
        self.saveConfig()
        bot = Bot(options['credentials']['username'], options['credentials']['password'], options['credentials']['server'])
        bot.start()


if __name__ == '__main__':
    vp_start_gui()




