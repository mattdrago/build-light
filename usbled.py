import time
import os
import sys
import atexit

try:
	import usb.core
	import usb.util
except Exception:
	pass # only required for mac os

class UsbLed:
	def __init__(self, device):
		self.color_method_map = { 'red':self.red, 'green':self.green, 'blue':self.blue, 'off':self.off }
		self.dev = device
		self.__register_device()
		atexit.register(self.off)

	def __register_device(self):
		if self.dev is None:
			raise ValueError('Device must be supplied')

		if self.dev.is_kernel_driver_active(0) is True:
			self.dev.detach_kernel_driver(0)

		self.dev.set_configuration()

	def red(self):
		self.led_on(0x02)

	def green(self):
		self.led_on(0x01)

	def blue(self):
		self.led_on(0x04)

	def red_flash(self):
		self.led_flash(0x02)

	def green_flash(self):
		self.led_flash(0x01)

	def blue_flash(self):
		self.led_flash(0x04)

	def off(self):
		self.all_off()

	def set_color(self, color):
		if color in self.color_method_map.keys():
			self.color_method_map[color]()

class UsbLedGen1(UsbLed):
	
	def __init__(self, device):
		UsbLed.__init__(self, device)

		# set up the flash cycle duties
		self.send(major_command=0x0a, minor_command=0x15, msb=0x21, lsb=0x2f)
		self.send(major_command=0x0a, minor_command=0x16, msb=0x21, lsb=0x2f)
		self.send(major_command=0x0a, minor_command=0x17, msb=0x21, lsb=0x2f)

	def send(self, major_command, minor_command, msb, lsb):
		try:
			self.dev.ctrl_transfer(bmRequestType=0xc8,
					bRequest= 0x12,
					wValue=(minor_command * 0x100) + major_command,
					wIndex=(lsb * 0x100) + msb,
					data_or_wLength=0x00000008)
		
		# a pipe error is thrown even if the operation is successful
		except usb.core.USBError:
			pass

	def led_on(self, color):
		self.all_off()
		self.send(major_command=0x0a, minor_command=0x0c, msb=color, lsb=0xff)

	def all_off(self):
		self.send(major_command=0x0a, minor_command=0x0c, msb=0x00, lsb=0xff)
		self.send(major_command=0x0a, minor_command=0x14, msb=0xff, lsb=0x00)

	def led_flash(self, color):
		self.all_off()
		self.send(major_command=0x0a, minor_command=0x14, msb=0x00, lsb=color)

class UsbLedGen2(UsbLed):
	
	def __init__(self, device):
		UsbLed.__init__(self, device)

	def send(self, color):
		try:
			self.dev.ctrl_transfer(bmRequestType=0x21,
					bRequest= 0x09,
					wValue=0x0635,
					wIndex=0x000,
					data_or_wLength='\x65\x0c' + chr(color) + '\xff\x00\x00\x00\x00')
		
		# a pipe error is thrown even if the operation is successful
		except usb.core.USBError:
			pass

	def led_on(self, color):
		self.send(color)

	def all_off(self):
		self.send(0x00)

	def led_flash(self, color):
		self.all_off()
		self.send(color)

class UsbLedFinder:
	def __init__(self, ledAddress):
		self.supported_platforms = ['darwin', 'linux']
		self.current_platform = os.uname()[0].lower()
		self.idVendor = 0x0fc5
		self.supportedIdProductsMap = { 0x1223: UsbLedGen1, 0xb080: UsbLedGen2 }
		self.ledAddress = ledAddress

	def is_current_platform_supported(self):
		return platform in self.supported_platforms

	def get_usbled(self):
		if(self.is_current_platform_supported):
			device = self.attached_device()
			if device.idProduct in self.supportedIdProductsMap:
				return self.supportedIdProductsMap[device.idProduct](device)
		else:
			print 'This platform (%s) is not supported' % self.platform
			sys.exit(1)

	def attached_device(self):
		if self.ledAddress is None:
			devices = usb.core.find(find_all=True, idVendor=self.idVendor)
		else:
			devices = usb.core.find(find_all=True, idVendor=self.idVendor, address=self.ledAddress)

		if len(devices) == 0:
			print 'No devices found.  Exiting'
			sys.exit(1)
		else:
			return devices[0]
