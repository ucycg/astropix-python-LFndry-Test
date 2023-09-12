import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from ttkbootstrap import Style

import re
from bitstring import BitArray

from modules.asic import Asic
from modules.voltageboard import Voltageboard
from modules.injectionboard import Injectionboard
from modules.nexysio import Nexysio

class AstropixGui:

    def __init__(self) -> None:
        self._handle = 0
        self.diconfig_variable = []

        self.inj = 0
        self.asic = Asic(0)

    def opennexys(self):
        nexys = Nexysio()

        # Open FTDI Device with Index 0
        #handle = nexys.open(0)
        self._handle = nexys.autoopen()

        self.asic = Asic(self._handle)
        print("Func open nexys")

    def closenexys(self):
        if self._handle != 0:
            self._handle.close()
            print("Func close nexys")
        else:
            print("Func close nexys: not open")

    def loadconfig(self):
        print("Func load config")
        filename = filedialog.askopenfile(mode='r', defaultextension=".json", filetypes=(("JSON", "*.json"), ("All Files", "*.*")))

    def saveconfig(self):
        print("Func save config")
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".json", filetypes=(("JSON", "*.json"), ("All Files", "*.*")))

    def update_asic(self):
        for values in dac_variable:
            if(values.get() > 63):
                values.set(63)
            elif(values.get() < 0):
                values.set(0)

            print(int(values.get()))

        for index, (key, value) in enumerate(self.asic.dacs.items()):
            self.asic.dacs[key] = int(dac_variable[index].get())

        print(self.asic.dacs)
        self.asic.update_asic()

    def update_digconf(self):

        print(self.diconfig_variable)

        for index, (key, value) in enumerate(self.asic.dacs.items()):
           self.asic.dacs[key] = int(dac_variable[index].get())

        print(self.asic.dacs)
        self.asic.update_asic()

    def updatevb(self):
        for values in vdac_variable:
            if(float(values.get())> 1.8):
                values.set(1.8)
            elif(float(values.get()) < 0):
                values.set(0)

            print(f"DAC val: {values.get()}")

        vboard1 = Voltageboard(self._handle, 4, (8, [0, 0, float(vdac_variable[0].get()), float(vdac_variable[1].get()), 0, 0, float(vdac_variable[2].get()), float(vdac_variable[3].get())]))
        vboard1.update_vb()

    def updateinj(self):
        injvoltage = Voltageboard(self._handle, 3, (2, [0.3, 0.0]))
        #injvoltage.vcal = vboard1.vcal
        injvoltage.update_vb()

        self.inj = Injectionboard(self._handle)

        # Set Injection Params for 330MHz patgen clock
        self.inj.period = int(inj_variable2[0].get())
        self.inj.clkdiv = int(inj_variable2[1].get())
        self.inj.initdelay = int(inj_variable2[2].get())
        self.inj.cycle = int(inj_variable2[3].get())
        self.inj.pulsesperset = int(inj_variable2[4].get())
        print(f"Func update inj: {float(inj_var1.get())} {int(inj_var2.get())} {self.inj.period}")

    def start_inj(self):

        self.updateinj()
        self.inj.start()
        print(f"Func update inj: Start")

    def stop_inj(self):
        self.inj.stop()
        print(f"Func update inj: Stop")

    def about(self):
        tk.messagebox.showinfo(title=None, message='Astropix-python GUI\nVersion 1.0\n\n© 2022 Nicolas Striebig')


    def create_digconfig_widget(self, digconf_labelframe) -> None:

        global row_number, col_number

        colconfig = BitArray(uint=self.asic.recconfig["ColConfig0"], length=38)

        self.diconfig_variable = []
        for index, values in enumerate(colconfig):
            if index != 0 and index != 1 and index != 37:
                values = not values

            print(f"Enumerate colconfig{index}: {values}")
            self.diconfig_variable.append(tk.IntVar(value=int(values)))

        index_bits = 34

        #for index, (dac, value) in enumerate(asic.recconfig.items()):
        for index, bits in enumerate(colconfig):
            print(f'Index: {index} DAC: {bits}\n')

            col_number = 10 * (index % 10)
            row_number = int(index / 10)

            if(index == 0):
                digconf_spin1 = ttk.Checkbutton(digconf_labelframe, text=f'En1', takefocus=0, variable=self.diconfig_variable[index])
            elif(index == 1):
                digconf_spin1 = ttk.Checkbutton(digconf_labelframe, text=f'En2', takefocus=0, variable=self.diconfig_variable[index])
            elif(index == 37):
                digconf_spin1 = ttk.Checkbutton(digconf_labelframe, text=f'En3', takefocus=0, variable=self.diconfig_variable[index])
            else:
                digconf_spin1 = ttk.Checkbutton(digconf_labelframe, text=f'Comp{index_bits}', takefocus=0, variable=self.diconfig_variable[index])
                index_bits = index_bits - 1

            digconf_spin1.grid(row=row_number, column=col_number, padx=10, pady=5)



    def create_dac_widget(self, dacs: list, dac_variables: list, dac_labelframe, increment=1, from_val=0, to_val=63) -> None:

        global row_number, col_number
        dac_labels = []
        dac_spins = []

        pattern = re.compile("nu\d+$")
        index_display = 0

        for index, (dac, value) in enumerate(dacs.items()):
            print(f'Index: {index} DAC: {dac}\n')

            if not pattern.match(dac): #hide unused dacs
                col_number = 2 * (index_display % 2)
                row_number = int(index_display / 2)

                dac_labels.append(ttk.Label(dac_labelframe, text=dac))
                dac_labels[index_display].grid(row=row_number, column=col_number, padx=10, pady=5)
                dac_spins.append(ttk.Spinbox(dac_labelframe, from_=from_val, to=to_val, increment=increment, textvariable=dac_variables[index]))
                dac_spins[index_display].grid(row=row_number, column=1+col_number, padx=10, pady=5)
                #dac_spins2.append(ttk.Scale(dac_labelframe, from_=0, to=63, variable=dac_variables[index], command=accept_whole_number_only))
                #dac_spins2[index_display].grid(row=row_number, column=2+col_number, padx=10, pady=5)
                index_display = index_display + 1

row_number = 0
col_number = 0

gui = AstropixGui()

style = Style(theme='darkly')
main_window = style.master
main_window.title("AstroPix GUI")

inj_var1 = tk.DoubleVar(value=0.3)
inj_var2 = tk.IntVar(value=100)
inj_var3 = tk.IntVar(value=100)
inj_var4 = tk.IntVar(value=100)
inj_var5 = tk.IntVar(value=100)
dac1, dac2 = tk.IntVar(value=5), tk.IntVar(value=5)
vdac1, vdac2, vdac3, vdac4 = tk.DoubleVar(value=1.0), tk.DoubleVar(value=1.0), tk.DoubleVar(value=1.0), tk.DoubleVar(value=1.0)
digconf_check1, digconf_check2 = tk.IntVar(), tk.IntVar()

# asic = Asic(0)
# print(asic.dacs)

#
# Menu
#
menu = tk.Menu(main_window)
main_window.config(menu=menu)
filemenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Load...", command=gui.loadconfig)
filemenu.add_command(label="Save...", command=gui.saveconfig)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=main_window.quit)

helpmenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=gui.about)

#
# Top Button Frame
#
buttons_frame = tk.Frame(main_window)
buttons_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.N)

opennexys_button = ttk.Button(buttons_frame, text="Open Nexys", command=gui.opennexys)
opennexys_button.grid(row=0, column=0, padx=(10), pady=5, sticky=tk.W+tk.E)

closenexys_button = ttk.Button(buttons_frame, text="Close Nexys", command=gui.closenexys)
closenexys_button.grid(row=0, column=1, padx=(10), pady=5, sticky=tk.W+tk.E)

loadconfig_button = ttk.Button(buttons_frame, text="Load Config", command=gui.loadconfig)
loadconfig_button.grid(row=0, column=2, padx=(10), pady=5, sticky=tk.W+tk.E)

saveconfig_button = ttk.Button(buttons_frame, text="Save Config", command=gui.saveconfig)
saveconfig_button.grid(row=0, column=3, padx=(10), pady=5, sticky=tk.W+tk.E)

#
# Digital Config
#
digconf_frame = tk.Frame(main_window)
digconf_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.N)

digconf_labelframe = ttk.Labelframe(digconf_frame, text='Col0 Config')
digconf_labelframe.grid(column=0, row=0, padx=8, pady=4, sticky=tk.W)

gui.create_digconfig_widget(digconf_labelframe)
update_digconfig_button = ttk.Button(digconf_labelframe, text="Update ColConfig", command=gui.update_digconf)
#print(row_number)
update_digconfig_button.grid(row=row_number+1, column=0, columnspan=4, padx=10, pady=10, sticky=tk.E+tk.W+tk.N+tk.S)

#
# Top DAC Frame
#
dacs_frame = tk.Frame(main_window)
dacs_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)

dac_labelframe = ttk.Labelframe(dacs_frame, text='ASIC')
dac_labelframe.grid(column=0, row=0, padx=8, pady=4, sticky=tk.W+tk.E)

dac_variable = []
for index, (item,value) in enumerate(gui.asic.dacs.items()):
    dac_variable.append(tk.IntVar(value=int(value)))

#print(f"Dac variables: {dac_variable[1]}")

#declare the spinbox widget by assigning values to from_, to and increment
#dac_list = [("DAC1", 1), ("DAC2", 2), ("DAC3", 3), ("DAC4", 4), ("DAC3", 3), ("DAC4", 4), ("DAC3", 3), ("DAC4", 4)]
gui.create_dac_widget(gui.asic.dacs, dac_variable, dac_labelframe)


update_button = ttk.Button(dac_labelframe, text="Update ASIC", command=gui.update_asic)
print(row_number)
update_button.grid(row=row_number+1, column=0, columnspan=4, padx=10, pady=10, sticky=tk.E+tk.W+tk.N+tk.S)

#
# VDAC Frame
#
vdacs_frame = tk.Frame(main_window)
vdacs_frame.grid(row=3, column=0, sticky="nsew")

#vdac_toplabel = ttk.Label(vdacs_frame, text="VDAC")
#vdac_toplabel.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

vdac_labelframe = ttk.Labelframe(vdacs_frame, text='VB')
vdac_labelframe.grid(column=0, row=0, padx=8, pady=4, sticky=tk.W)

#declare the spinbox widget by assigning values to from_, to and increment
    # 3 = Vcasc2, 4=BL, 7=Vminuspix, 8=Thpix

vdac_variable = []
vdacs = {"Vcasc2": 1.10, "BL": 1.0,"Vminuspix": 1.0,"Thpix": 1.10}
for key, values in vdacs.items():
    vdac_variable.append(tk.DoubleVar(value=float(values)))

gui.create_dac_widget(vdacs, vdac_variable, vdac_labelframe, 0.01, from_val=0, to_val=1.8)

updatevdac_button = ttk.Button(vdac_labelframe, text="Update VB", command=gui.updatevb)
updatevdac_button.grid(row=row_number+1, column=0, columnspan=4, padx=(10), pady=10, sticky=tk.E+tk.W+tk.N+tk.S)

#
# Injection Frame
#
inj_frame = tk.Frame(main_window)
inj_frame.grid(row=4, column=0, sticky="nsew")

inj_labelframe = ttk.Labelframe(inj_frame, text='Injection')
inj_labelframe.grid(column=0, row=0, padx=8, pady=4, sticky=tk.W)


inj_labelframe2 = ttk.Labelframe(inj_frame, text='Injection')
inj_labelframe2.grid(column=0, row=1, padx=8, pady=4, sticky=tk.W)

inj_variable1 = []
inj_variable2 = []
injs1 = {"injvoltage": 1}
injs2 = {"inj1": 1, "inj2": 1,"inj3": 5,"inj4": 1,"inj5": 1}
for key, values in injs2.items():
    inj_variable2.append(tk.IntVar(value=int(values)))

inj_variable1.append(tk.DoubleVar(value=float(injs1["injvoltage"])))
gui.create_dac_widget(injs1, inj_variable1, inj_labelframe, 0.01, 0, 1.8)
gui.create_dac_widget(injs2, inj_variable2, inj_labelframe2)

updateinj_button = ttk.Button(inj_labelframe, text="Start Inj", command=gui.start_inj)
updateinj_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.N+tk.S)
print(f"Row number: {row_number}")
updateinj_button = ttk.Button(inj_labelframe, text="Stop Inj", command=gui.stop_inj)
updateinj_button.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.N+tk.S)
print(f"Row number: {row_number}")
#To show the content in the window

main_window.rowconfigure(0, weight=1)
main_window.rowconfigure(1, weight=1)
main_window.rowconfigure(2, weight=1)
main_window.rowconfigure(3, weight=1)
main_window.rowconfigure(4, weight=1)
main_window.columnconfigure(0, weight=1)
main_window.columnconfigure(1, weight=1)

main_window.mainloop()
