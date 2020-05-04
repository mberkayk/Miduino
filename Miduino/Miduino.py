#!/usr/bin/env python3
import tkinter
import rtmidi
import serial
import serial.tools.list_ports
import threading
import pystray
import PIL.Image
import time
import os

class UsbFrame(tkinter.LabelFrame):
	def __init__(self, parent, text, app):
		tkinter.LabelFrame.__init__(self, parent, text=text)
		self.parent = parent
		self.app = app

		self.usbList = tkinter.Listbox(self, selectmode=tkinter.SINGLE)
		self.no_dvc_lbl = tkinter.Label(self, text="No device found!")
		self.slctBtn = tkinter.Button(self, text="Connect --->", command=self.port_selected)

		self.rfshBtn = tkinter.Button(self, text="Refresh", command=self.list_serial_ports)

	def port_selected(self):
		slctd_serial_port = self.usbList.get(tkinter.ACTIVE)[1:].split(':')[0]
		self.app.switch_to_serial_frame(slctd_serial_port)

	def list_serial_ports(self):
		serial_ports = serial.tools.list_ports.comports()
		if serial_ports:
			self.usbList.delete(0, tkinter.END)
			for p in serial_ports:
				self.usbList.insert(tkinter.END, "\'"+p.name +": "+ p.description+"\'" + " at " + "\'"+p.location+"\'")
			self.no_dvc_lbl.pack_forget()
			self.usbList.pack(expand=1,fill=tkinter.X)
			self.slctBtn.pack()
			self.rfshBtn.pack()
		else:
			self.usbList.pack_forget()
			self.slctBtn.pack_forget()
			self.no_dvc_lbl.pack(side="top")
			self.rfshBtn.pack()

class SerialFrame(tkinter.Frame):
	def __init__(self, parent):
		tkinter.Frame.__init__(self, parent.window)
		self.parent = parent

		self.midiout = rtmidi.MidiOut()
		available_midi_ports = self.midiout.get_ports()
		if available_midi_ports:
			self.midiout.open_port(0, name="MIDUINO Keyboard")
		else:
			self.midiout.open_virtual_port("MIDUINO Keyboard V")

		self.slct_usb_btn = tkinter.Button(self, text="<---Select another usb port", command=self.parent.switch_to_usb_frame)
		self.slct_usb_btn.pack(side="bottom")

		self.run_lbl = tkinter.Label(self, text="Running on " + self.midiout.get_port_name(0))
		self.run_lbl.pack()

	def start_conn(self, dvc_name):
		self.run_lbl.config(text="Running on " + self.midiout.get_port_name(0))

		###   SERIAL ###
		s = serial.Serial("/dev/"+dvc_name, 57600, timeout=3)
		self.thread = threading.Thread(target=self.get_and_send, args=(s,), daemon=True)
		self.connected = True
		self.thread.start()

	def get_and_send(self, s):
		while self.connected:
			input = s.readline()
			if input != b'':
				input = int(input)
				print(input)
				if(input < 2):
					self.midiout.send_message([0x90, 48 + input, 60])# note_on
				else:
					self.midiout.send_message([0x80, 56 + input, 0])# note_off
		s.close()

class AppIcon(pystray.Icon):

	def __init__(self, app):
		dirname = os.path.dirname(__file__)
		filename = os.path.join(dirname, 'midi_keyboard_white.ico')
		img = PIL.Image.open(filename, 'r')
		print(filename)

		pystray.Icon.__init__(self, "Miduino", img, "Miduino")

		self.app = app
		
		max_btn = pystray.MenuItem("Maximize window", self.max_win)
		quit_btn = pystray.MenuItem("Quit", self.quit_app)
		self.menu = pystray.Menu(max_btn, quit_btn)

	def max_win(self):
		self.stop()
		self.app.window.deiconify()

	def quit_app(self):
		self.app.window.destroy()
		self.stop()

	def run(self):
		pystray.Icon.run(self)

class MiduinoApp():
	def __init__(self):
		self.icon = AppIcon(self)

		self.serialThread = None
		self.setup_window()
		self.window.mainloop()

	def setup_window(self):
		self.window = tkinter.Tk()
		self.window.geometry('400x400+500+50')
		self.window.title("Miduino")
		dirname = os.path.dirname(__file__)
		filename = os.path.join(dirname, 'midi_keyboard.png')
		# self.window.iconbitmap(filename)
		self.window.iconphoto(False, tkinter.PhotoImage(file=filename))
		self.serialFrame = SerialFrame(self)
		if self.serialThread != None and self.serialThread.is_alive():
			self.serialFrame = SerialFrame(app.window)
			self.serialFrame.pack()
		else:
			self.usbFrame = UsbFrame(self.window, text = "Choose usb port", app = self)
			self.usbFrame.pack(expand=1,fill=tkinter.X)
			self.usbFrame.list_serial_ports()
		self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

	def switch_to_serial_frame(self, device_name):
		self.usbFrame.pack_forget()
		self.serialFrame.pack()

		self.serialFrame.start_conn(device_name)

	def switch_to_usb_frame(self):
		self.serialFrame.pack_forget()
		self.usbFrame.pack(expand=1,fill=tkinter.X)
		self.usbFrame.list_serial_ports()

		self.serialFrame.conected = False
		self.serialFrame.thread.join()

	def on_closing(self):
		self.window.withdraw()
		self.icon.visible = True
		self.icon.run()

if __name__ == "__main__":
	app = MiduinoApp()
