# coding: utf-8
#from __future__ import print_function
from scene import *
import sound
import urllib
import requests
import os
import errno
import console
import time

class Game(Scene):
	
	def parseMusicData(self, url):
		smFile = urllib.urlopen(url + '.sm')
		started = False
		if not os.path.exists(self.smdir + self.title + '.data'):
			f = open(self.smdir + self.title + '.data', 'w+')
			for temp, line in enumerate(smFile):
				if started == True and ';' in line:
					f.close()
					print('done')
					return
				if started == False and '0000' in line:
					if line.index('0000') == 0:
						started = True
				if started == True:
					f.write(line)
				
	def load_file(self, base_url):
		file = urllib.urlopen(base_url + '.sm')
		startloc = 0
		started = False
		for line in file:
			if '#TITLE:' in line:
				self.title = line[7:-3]
				self.smdir = 'Offline Data/' + self.title + '/'
				try:
					os.makedirs('Offline Data/' + self.title)
				except OSError as exception:
					if exception.errno != errno.EEXIST:
						raise		
			if '#BACKGROUND:' in line:
				if not os.path.exists(self.smdir + line[12:-3]):
					with open(self.smdir + line[12:-3], 'wb') as out_file:
						bg_url = base_url
						while bg_url[-1] != '/':
							bg_url = bg_url[:-1]
						out_file.write(requests.get(bg_url+line[12:-3]).content)
				self.bg_pic = SpriteNode(self.smdir + line[12:-3])
				self.bg_pic.alpha = 0.35
				ratio = self.size.w/self.bg_pic.size.w
				self.bg_pic.size = (self.size.w, self.bg_pic.size.h*ratio)
				self.bg_pic.position = (self.size.w/2, self.size.h/2)
			if '#MUSIC:' in line:
				if not os.path.exists(self.smdir + line[7:-3]):
					with open(self.smdir + line[7:-3], 'wb') as out_file:
						path = base_url
						while path[-1] != '/':
							path = path[:-1]
						path = path+line[7:-3].replace(' ', '%20')
						out_file.write(requests.get(path).content)
				else:
					print('skipped')
				self.music = sound.Player(self.smdir + line[7:-3])
			if 'BPMS:' in line:
				loc = line.index('=') + 1
				self.bps = 60/float(line[loc:])
		self.parseMusicData(base_url)

	def setup(self):
		self.load_file(url)
		
		self.background = Node(parent=self)
		self.controls = Node(parent=self)
		left = SpriteNode('res/default_arrow.PNG')
		left.size = (100,100)
		left.rotation = math.pi/2
		left.position = (200,560)
		up = SpriteNode('res/default_arrow.PNG')
		up.size = (100, 100)
		up.position = (320,560)
		down = SpriteNode('res/default_arrow.PNG')
		down.size = (100,100)
		down.rotation = math.pi
		down.position = (440,560)
		right = SpriteNode('res/default_arrow.PNG')
		right.size = (100,100)
		right.rotation = -math.pi/2
		right.position = (560,560)
		self.background.add_child(self.bg_pic)
		self.controls.add_child(up)
		self.controls.add_child(down)
		self.controls.add_child(left)
		self.controls.add_child(right)
		
		self.uiElements = Node(parent=self)
		healthbar = SpriteNode('res/healthbar.PNG')
		healthbar.size = (460, 50)
		healthbar.position = (380,650)
		self.health = SpriteNode('res/health.PNG')
		self.health.anchor_point = (0,0.5)
		self.health.size = (0, 32)
		self.health.position = (150, 650)
		self.uiElements.add_child(healthbar)
		self.uiElements.add_child(self.health)
		self.healthVal = 50
		
		self.delay = time.time() + 650.0/120.0
		self.started = False
		self.scrollSpd = 2
		self.current_line = 0
		self.totalTime = 0
		self.lastFrameTime = time.time()
		self.current_measure = []
		self.linesInMeasure = 0
		self.entities = []
		
	def isTime(self):	
		if self.totalTime >= self.bps:
			self.totalTime = 0
			return True
		self.currentTime = time.time()
		dt = self.currentTime - self.lastFrameTime 
		self.totalTime = self.totalTime + dt

	def updateTimer(self):
		no_fill()
		stroke_weight(2)
		stroke(255, 0, 0)
		yoffset = 150
		h = 500
		rect(20, yoffset, 10, h)
		for i in range(1,4):
			line(20, h*i/4 + yoffset, 30, h*i/4 + yoffset)
		percent = self.music.current_time / self.music.duration
		fill(255, 0, 0)
		rect(20, yoffset, 10, h*percent)
	def drawHealth(self):
		self.health.size = (450*(self.healthVal/100.0), 32)
		self.health.position = (158, 650)
	
	def read_measure(self):
		with open(self.smdir + self.title +'.data') as f:
			for i, line in enumerate(f):
				line = line.strip()
				if i >= self.current_line:
					if ',' in line:
						self.current_line += self.linesInMeasure + 1
						return
					else:
						self.current_measure.append(line)
						self.linesInMeasure += 1
	def draw_line(self):
		line = self.current_measure.pop(0)	
		for i, c in enumerate(line):
			if int(c) > 0:
				temp = SpriteNode('res/default_arrow.PNG')
				temp.size = (100,100)	
				if i == 0:
					pos = (200,0)
					temp.rotation = math.pi/2
				elif i == 1:
					pos = (320,0)	
				elif i == 3:
					pos = (440,0)
					temp.rotation = math.pi
				else:
					pos = (560,0)
					temp.rotation = -math.pi/2
				temp.position = pos
				self.entities.append(temp)
				self.add_child(temp)

	def destroyObjects(self):
		for obj in list(self.entities):
			if not obj.parent:
				self.entities.remove(obj)

	def waitForDelay(self):
		if time.time() >= self.delay:
			self.started = True
			self.music.play()
		
	def update(self):
		if self.started == False:
			print "%.2f"%(self.delay-time.time())
			self.waitForDelay()
		self.updateTimer()
		self.drawHealth()
		if self.isTime():
			if self.current_measure == []:
				self.linesInMeasure = 0
				self.read_measure()
			self.draw_line()
		self.lastFrameTime = self.currentTime
		for obj in self.entities:
			obj.position = (obj.position.x, obj.position.y+self.scrollSpd)
		self.destroyObjects()
	
	def stop(self):
		self.entities = []
		self.music.stop()

# AMERICAN POP
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/Cake%20By%20The%20Ocean/Cake%20By%20The%20Ocean'
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/Call%20Me%20Maybe/Call%20Me%20Maybe'
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/Chandelier/Chandelier'
url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/Uptown%20Funk!/Uptown%20Funk!'

# WEEB SHIT
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/(AnTiHoLiDaYs)%20Black%20Bullet/Black%20Bullet'
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/(Jubo)%20Kyoukai%20no%20Kanata%20%5BKyoukai%20no%20Kanata%20OP%5D/Kyoukai%20no%20Kanata'
#url = 'https://raw.githubusercontent.com/jezhou8/iosSMhost/master/Cantarella%20~grace%20edition~%20%5BGpop%5D/Cantarella'


if __name__ == '__main__':
	console.clear()
	run(Game(), show_fps=True)
