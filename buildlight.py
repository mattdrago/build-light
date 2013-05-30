import httplib
import time
from usbled import UsbLedFinder

class HudsonBuildLight:
	def __init__(self, host, port, jobs, ledAddress=None):
		self.host = host
		self.port = port
		self.jobs = jobs
		self.usbled = UsbLedFinder(ledAddress).get_usbled()
		
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
