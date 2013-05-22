import httplib
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
    def __init__(self):
        self.color_method_map = { 'red':self.red, 'green':self.green, 'blue':self.blue, 'off':self.off }

	atexit.register(self.off)

    def red(self):
        self.send(0x02)

    def green(self):
        self.send(0x01)

    def blue(self):
        self.send(0x04)

    def off(self):
        self.send(0x00)

    def set_color(self, color):
        if color in self.color_method_map.keys():
	    self.color_method_map[color]()

class UsbLedGen1(UsbLed):
    
    def __init__(self):
        UsbLed.__init__(self)
        self.dev = usb.core.find(idVendor=0x0fc5, idProduct=0x1223)
        if self.dev is None:
            raise ValueError('Device not found')

        if self.dev.is_kernel_driver_active(0) is True:
            self.dev.detach_kernel_driver(0)

        self.dev.set_configuration()

    def send(self, color):
        try:
            self.dev.ctrl_transfer(bmRequestType=0x000000c8,
                                   bRequest= 0x00000012,
                                   wValue=(0x02 * 0x100) + 0x0a,
                                   wIndex=0xff & (~color),
                                   data_or_wLength=0x00000008)
        
        # a pipe error is thrown even if the operation is successful
        except usb.core.USBError:
            pass

class UsbLedGen2(UsbLed):
    
    def __init__(self):
        UsbLed.__init__(self)
        self.dev = usb.core.find(idVendor=0x0fc5, idProduct=0xb080)
        if self.dev is None:
            raise ValueError('Device not found')

        if self.dev.is_kernel_driver_active(0) is True:
            self.dev.detach_kernel_driver(0)

        self.dev.set_configuration()

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

class UsbLedFinder:
    def __init__(self):
        self.supported_platforms = ['darwin', 'linux']
	self.current_platform = os.uname()[0].lower()
	self.idVendor = 0x0fc5
	self.supportedIdProductsMap = { 0x1223: UsbLedGen1, 0xb080: UsbLedGen2 }

    def is_current_platform_supported(self):
	return platform in self.supported_platforms

    def get_usbled(self):
        if(self.is_current_platform_supported):
	    deviceProductId = self.attached_device_product_id()
	    if deviceProductId in self.supportedIdProductsMap:
	        return self.supportedIdProductsMap[deviceProductId]()
        else:
	    print 'This platform (%s) is not supported' % self.platform
	    sys.exit(1)

    def attached_device_product_id(self):
        device = usb.core.find(idVendor=0x0fc5)

	if device is None:
	    print 'No devices found.  Exiting'
	    sys.exit(1)
	else:
	    return device.idProduct

class HudsonBuildLight:
    def __init__(self, host, port, jobs):
        self.host = host
        self.port = port
        self.jobs = jobs
        self.usbled = UsbLedFinder().get_usbled()
        
        # not mapped colors will default to blue
        # other colors returned by hudson: blue_anime red_anime grey grey_anime aborted
        self.color_map = { 'blue':'green', 'blue_anime':'green', 'red':'red', 'red_anime':'red', 'green':'green' }
        self.default_color = 'red'

    def get_job_color(self,job):
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
            conn.request('GET','/job/%s/api/python' % job)
            jobdata = eval(conn.getresponse().read())
        except Exception:
            return self.default_color
        
        job_color = jobdata['color']
        if self.color_map.has_key(job_color):
            return self.color_map[job_color]
        else:
            return self.default_color

    def get_color(self):
        colors = map((lambda job: self.get_job_color(job)),self.jobs)
        if(all(colors[0] == i for i in colors)):
            return colors[0]
        else:
	    return self.default_color

    def loop(self):
        self.usbled.set_color(self.default_color)
        last_color = self.get_color()
        self.usbled.set_color(last_color)
        while True:
            color = self.get_color()
            if color != last_color:
                self.usbled.set_color(color)
                last_color = color
            time.sleep(1)
