import pyautogui as pyg
import pyperclip, pygame, pyxhook
import keyboard
import time

import tkinter as tk
from tkinter import *
from functools import partial

from gpt4all.gpt4all import GPT4All

pyg.PAUSE = 0.05

def highlight():
    pyg.hotkey('alt','/')
    pyg.write("highlight color: none")
    time.sleep(.15)
    pyg.hotkey('enter')


functions = ['p`alt /\nhighlight color: none\nw`0.15\np`enter\nc`',
             'p`alt /\nhighlight color: light blue 3\nw`0.15\np`enter\nc`',
             'p`alt /\nhighlight color: light green 3\nw`0.15\np`enter\nc`',
             'p`alt /\nhighlight color: light red 3\nw`0.15\np`enter\nc`',
             '',
             '',
             '',
             '',
             '',
             '']

    

def fun(i):
    try:
        commands = functions[i-1].split('\n')
        for cmd in commands:
            if cmd.strip() == '': continue
            if '`' not in cmd:
                pyg.write(cmd)
                continue
            f,arg = cmd.split('`')
            arg = arg.strip().replace('  ',' ')
            if f == 'p':
                pyg.hotkey(*arg.split(' '))
            if f == 'w':
                time.sleep(float(arg))
            if f == 'c':
                if not arg: pyg.click()
                else: pyg.click(*[int(n) for n in arg.split(' ')])
            if f == 'm':
                pyg.moveTo(*[int(n) for n in arg.split(' ')])
            if f == 'd': pyg.keyDown(arg)
            if f == 'u': pyg.keyUp(arg)
    except Exception as e:
        print(e)



class BigWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

        self.option_add('*font','Calibri')

        self.pages = (Smol,Select,Coding,Chat)
        self.index = 0

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in self.pages:
            page_name = F.__name__
            frame = F(parent=container,controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0,column=0,sticky='nsew')
        
        # windowsize + position
        self.geometry('50x50+2485+1450')
        self.overrideredirect(True)
        self.lift()

        self.showFrame('Smol')

    def showFrame(self,win,*args):
        self.frames[win].tkraise()
        if win == 'Coding':
            self.frames[win].setIdx(*args)
            self.frames[win].activate()
        else:
            self.frames['Coding'].deactivate()
        if win == 'Smol': self.geometry('50x50+2485+1450')
        else: self.geometry('400x600+2160+920')

    def close(self):
        self.destroy()


class Smol(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.option_add('*font','Calibri')

        self.b_open = tk.Button(self,text='<',bg='Slategray2',height=4,width=4,
                                command = partial(controller.showFrame,'Select'))
        self.b_open.pack(side=TOP)

        
class Select(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        
        self.buttons = []
        for y in range(3):
            for x in range(3):
                self.buttons.append(tk.Button(self, text=str(x+y*3+1),bg='Slategray2',height=2,width=6,font=('Calibri',15),command=partial(self.pressed,x+y*3)))
                self.buttons[-1].place(x=(x-1.5)*125+210,y=y*125+100)

        self.b_open = tk.Button(self,text='>',bg='Slategray2',height=2,width=4,
                                command = partial(controller.showFrame,'Smol'))
        self.b_open.pack(side=BOTTOM,anchor=SW)

        self.b_chat = tk.Button(self,text='chat',bg='Slategray3',height=2,width=8,
                                command = partial(controller.showFrame,'Chat'))
        self.b_chat.pack(side=BOTTOM, pady=0)

    def pressed(self,button):
        self.controller.showFrame('Coding',button)


class Coding(tk.Frame):
    idx = 0
    active = False
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.title = tk.Label(self,text="Alt-1",font=('Calibri',15))
        self.title.pack(side=TOP,anchor=W,padx=20,pady=20)

        self.textbox = tk.Text(self,width=25,height=15,font=('Calibri',12))
        self.textbox.place(x=200,y=75,anchor=N)

        self.mousepos = tk.Label(self,text='x=0,y=0',font=('Calibri',12))
        self.mousepos.place(relx=.95,y=20,anchor=NE)
        
        self.b_exit = tk.Button(self,text='✘',bg='salmon1',height=2,width=4,
                                command = partial(self.controller.showFrame,'Select'))
        self.b_exit.place(x=350,y=600,anchor=SE)

        self.b_confirm = tk.Button(self,text='✓',bg='DarkSeaGreen2',height=2,width=4,
                                command = self.update)
        self.b_confirm.place(x=400,y=600,anchor=SE)

        self.b_open = tk.Button(self,text='>',bg='Slategray2',height=2,width=4,
                                command = partial(controller.showFrame,'Smol'))
        self.b_open.pack(side=BOTTOM,anchor=SW)

    def activate(self):
        self.active = True
        self.mouseEvent()

    def deactivate(self):
        self.active = False

    def mouseEvent(self):
        posx,posy = pyg.position()
        self.mousepos.config(text = f'x={posx},y={posy}')
        if self.active: self.after(100,self.mouseEvent)

    def update(self):
        global functions
        functions[self.idx] = self.textbox.get('1.0','end-1c')
        self.controller.showFrame('Select')

    def setIdx(self,i):
        self.idx = i
        self.title.config(text = f'Alt-{i+1}')
        self.textbox.delete('1.0',END)
        self.textbox.insert('1.0',functions[i])

class Chat(tk.Frame):
    delimeter = '\n===================================\n'
    def __init__(self, parent, controller):
        self.model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
        self.chat = []
        
        tk.Frame.__init__(self,parent)
        self.controller = controller

        #self.title = tk.Label(self,text="Bob",font=('Calibri',15))
        #self.title.pack(side=TOP,anchor=W,padx=20,pady=20)

        self.textbox = tk.Text(self,width=35,height=20,wrap=WORD,font=('Calibri',10))
        self.textbox.place(x=200,y=20,anchor=N)

        self.send = tk.Button(self,text='➤',bg='Slategray2',height=2,width=4,
                                command = self.getResponse)
        self.send.place(x=200,y=600,anchor=SE)
        self.copy = tk.Button(self,text='⎘',bg='Slategray2',height=2,width=4,
                                command = self.copyResponse)
        self.copy.place(x=200,y=600,anchor=SW)

        self.b_back = tk.Button(self,text='<',bg='Slategray2',height=2,width=4,
                                command = partial(controller.showFrame,'Select'))
        self.b_back.place(x=400,y=600,anchor=SE)

        self.b_close = tk.Button(self,text='>',bg='Slategray2',height=2,width=4,
                                command = partial(controller.showFrame,'Smol'))
        self.b_close.pack(side=BOTTOM,anchor=SW)

    def copyResponse(self):
        self.chat = []
        for n,item in enumerate(self.textbox.get('1.0','end-1c').split(self.delimeter)):
            self.chat.append((['user','assistant'][n%2],item))
        for name,resp in self.chat[::-1]:
            if name == 'assistant':
                pyperclip.copy(resp)
                return
        pyperclip.copy('')

    def formatResponse(self,name,resp):
        return f'<|im_start|>{name}\n{resp}<|im_end|>\n'

    def formatChat(self):
        toreturn = ''
        for content in self.chat:
            toreturn += self.formatResponse(*content)
        return toreturn

    def getResponse(self,*args):
        self.chat = []
        for n,item in enumerate(self.textbox.get('1.0','end-1c').split(self.delimeter)):
            self.chat.append((['user','assistant'][n%2],item))
        #usr = self.textbox.get('1.0','end-1c').split(self.delimeter)[-1]
        #self.chat.append(('user',usr))
        response = self.model.generate(self.formatChat() + f'<|im_start|>assistant',max_tokens=250)
        response = response.strip().replace('<|im_end|>','').split('<|im_start|>')[0]
        self.textbox.insert(END,self.delimeter+response+self.delimeter)
        #self.chat.append(('assistant',response))


def main():
    
    for i in range(1,10): keyboard.add_hotkey(f"alt+{i}", partial(fun, i))

    root = BigWindow()
    keyboard.add_hotkey("alt+0", partial(root.showFrame,'Chat'))
    root.attributes('-topmost', True)
    root.mainloop()


if __name__ == "__main__": main()


