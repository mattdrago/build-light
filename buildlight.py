import httplib
import time
from usbled import UsbLedFinder

class BuildColor:
	color_map = {}

	def __init__(self, color, led_color, rank):
		self.color = color
		self.led_color = led_color
		self.rank = rank

		BuildColor.color_map[color] = self

def get_build_color(color):
	if color in BuildColor.color_map.keys():
		return BuildColor.color_map[color]
	else:
		return BuildColor.DEFAULT

BuildColor.RED_FLASH = BuildColor('red_anime', 'red_flash', 0)
BuildColor.RED = BuildColor('red', 'red', 1)
BuildColor.YELLOW_FLASH = BuildColor('yellow_anime', 'red_flash', 2)
BuildColor.YELLOW = BuildColor('yellow', 'red', 3)
BuildColor.BLUE_FLASH = BuildColor('blue_anime', 'green_flash', 4)
BuildColor.BLUE = BuildColor('blue', 'green', 5)
BuildColor.GREY_FLASH = BuildColor('grey_anime', 'off', 6)
BuildColor.GREY = BuildColor('grey', 'off', 7)

BuildColor.DEFAULT = BuildColor.RED

class HudsonBuildLight:
	def __init__(self, host, port, jobs, ledAddress=None):
		self.host = host
		self.port = port
		self.jobs = jobs
		self.usbled = UsbLedFinder(ledAddress).get_usbled()
		
	def get_job_color(self,job):
		try:
			conn = httplib.HTTPConnection(self.host, self.port)
			conn.request('GET','/job/%s/api/python' % job)
			jobdata = eval(conn.getresponse().read())
		except Exception:
			return BuildColor.DEFAULT
		
		return get_build_color(jobdata['color'])

	def get_color(self):
		colors = map((lambda job: self.get_job_color(job)),self.jobs)
		if(all(colors[0] == i for i in colors)):
			return colors[0]
		else:
			return BuildColor.DEFAULT

	def loop(self):
		last_color = None
		while True:
			color = self.get_color()
			if color != last_color:
				self.usbled.set_color(color.led_color)
				last_color = color
			time.sleep(1)
