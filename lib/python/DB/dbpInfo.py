from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfo
from Screens.About import About
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from os import system, remove
from dbpTool import ListboxE1, GetSkinPath
from enigma import eConsoleAppContainer
from Components.PluginComponent import plugins
from Components.PluginList import *
from Plugins.Plugin import PluginDescriptor

def getUnit(val):
	if val >= 1048576:
		return '%.1f%s' % (float(val)/1048576,' Gb')
	return '%.1f%s' % (float(val)/1024,' Mb')

def getSize(a,b,c):
	return getUnit(a),getUnit(b),getUnit(c)

class NInfo(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#ff2525" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def getPlugins(self):
		plist = []
		pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_EXTENSIONSMENU)
		for plugin in pluginlist:
			plist.append(PluginEntryComponent(plugin))
		for p in plist:
			if (p[0].name.find("CCcam Info") != -1):
				self.cccmaplugyn = p[0]
			if (p[0].name.find("Gbox Suite") != -1):
				self.gboxplugyn = p[0]
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = ListboxE1(self.list)
		self["key_red"] = Label(_("Exit"))
		self["title"] = Label(_("System Information"))
		self.cccmaplugyn = self.gboxplugyn = ''
		self.getPlugins()
		self.infoMenuList = [
			('GboxInfo',_('Gbox Suite'),'icons/cams.png',self.gboxplugyn),
			('CInfo',_('CCcam Info'),'icons/cams.png',self.cccmaplugyn),
			('DInfo',_('Show Device Status'),'icons/space.png',True),
			('PInfo',_('Show Active Process'),'icons/process.png',True),
			('SInfo',_('Show Service Info'),'icons/service.png',True),
			('EInfo',_('Show Enigma Settings'),'icons/enigma.png',True),
			('About',_('DB-PROJECT Firmware Info'),'icons/about.png',True)
			]
		c = eConsoleAppContainer()
		c.execute('df > /tmp/info_df.tmp && free > /tmp/info_mem.tmp')
		del c
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			'back': self.close
		})
		self.onLayoutFinish.append(self.updateList)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("System Information"))
	
	def updateList(self):
		self.list = []
		skin_path = GetSkinPath()
		for i in self.infoMenuList:
			if i[3]:
				res = [i[0]]
				res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=i[1]))
				res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=LoadPixmap(skin_path + i[2])))
				self.list.append(res)
		self['list'].l.setList(self.list)

	def KeyOk(self):
		self.sel = self["list"].getCurrent()[0]
		if (self.sel == "GboxInfo"):
			if self.gboxplugyn:
				self.gboxplugyn(session=self.session, servicelist=self)
		elif (self.sel == "CInfo"):
			if self.cccmaplugyn:
				self.cccmaplugyn(session=self.session, servicelist=self)
		elif (self.sel == "DInfo"):
				self.session.open(showDevSpaceInfo)
		elif (self.sel == "PInfo"):
				self.session.open(showRunProcessInfo)
		elif (self.sel == "SInfo"):
				self.session.open(ServiceInfo)
		elif (self.sel == "EInfo"):
				self.session.open(showEnigmaInfo)
		elif (self.sel == "About"):
				self.session.open(About)

class showRunProcessInfo(Screen):
	__module__ = __name__
	skin = """
		<screen position="70,110" size="580,380">
			<ePixmap position="0,0" pixmap="skin_default/shout_back2.png" size="580,380" alphatest="on" />
			<widget name="titlebar" zPosition="2" position="10,1" size="560,30" font="Regular;18" valign="center" transparent="1" foregroundColor="white" backgroundColor="white" />
			<widget name="psinfo" position="20,50" size="560,320" font="Regular;18" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self['titlebar'] = Label(' PID \t Uid \t Command')
		self['psinfo'] = ScrollLabel('')
		self['actions'] = ActionMap(['WizardActions',
			'DirectionActions'], {'ok': self.close,
			'back': self.close,
			'up': self['psinfo'].pageUp,
			'left': self['psinfo'].pageUp,
			'down': self['psinfo'].pageDown,
			'right': self['psinfo'].pageDown})
		
		self.onLayoutFinish.append(self.writepslist)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Active Process Information"))

	def writepslist(self):
		p = ''
		system('ps > /tmp/ninfo.tmp')
		if fileExists('/tmp/ninfo.tmp'):
			f = open('/tmp/ninfo.tmp', 'r')
			for line in f.readlines():
				x = line.strip().split()
				if (x[0] == 'PID'):
					continue
				p += (x[0] + '\t')
				p += (x[1] + '\t')
				if len(x) > 4:
					p += x[4] + '\n'
				else:
					p += x[3] + '\n'
			f.close()
			remove('/tmp/ninfo.tmp')
		self['psinfo'].setText(p)

class showDevSpaceInfo(Screen):
	__module__ = __name__
	skin = """
		<screen position="339,135" size="602,480">	
		<widget name="flsp" position="40,25" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="f1" position="150,20" size="410,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="f2" position="40,45" size="520,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="cfp" position="40,85" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="c1" position="150,80" size="410,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="c2" position="40,105" size="520,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="usbp" position="40,145" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="u1" position="150,140" size="410,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="u2" position="40,165" size="520,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="hddp" position="40,205" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="h1" position="150,200" size="410,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="h2" position="40,225" size="520,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="totp" position="40,265" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="t1" position="150,260" size="410,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="t2" position="40,285" size="520,30" font="Regular;18" valign="center" />
		<widget name="rrpr" position="40,325" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="rr1" position="150,320" size="190,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="rr2" position="40,345" size="470,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="rspr" position="40,385" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="rs1" position="150,380" size="190,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="rs2" position="40,405" size="470,30" font="Regular;18" valign="center" transparent="1" />
		<widget name="rtpr" position="40,445" pixmap="skin_default/slider/slider_main.png" size="100,15" borderWidth="2" borderColor="#3366cc" transparent="1" />
		<widget name="rt1" position="150,440" size="190,30" font="Regular;18" valign="center" transparent="1" foregroundColor="#3366cc" />
		<widget name="rt2" position="40,465" size="580,30" font="Regular;18" valign="center" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		labelList = [
			('f1' , ''), ('f2' , ''),
			('c1' , _('Compact Flash Not Found')), ('c2' , 'N/A'),
			('u1' , _('Usb Not Found')), ('u2' , 'N/A'),
			('h1' , _('Hard Disk Not Found')), ('h2' , 'N/A'),
			('t1' , 'N/A'),('t2' , 'N/A'),
			('rr1' , 'Ram: '),('rr2' , ''),
			('rs1' , 'Swap: '),('rs2' , ''),
			('rt1' , 'Total: '),('rt2' , '')]
		progrList = ['rrpr','rspr','rtpr','flsp','cfp','usbp','hddp','totp']
		
		for x in labelList:
			self[x[0]] = Label(x[1])
		for x in progrList:
			self[x] = ProgressBar()
		
		self['actions'] = ActionMap(['WizardActions'],
		{
			'ok': self.close,
			'back': self.close
		})
		self.onLayoutFinish.append(self.writelist)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Usage Device Status"))
	
	def writelist(self):
		fls = 0
		cf = [0,0,0,0]
		usb = [0,0,0,0]
		hdd = [0,0,0,0]
		tot = [0,0,0,0]
		if fileExists('/tmp/info_df.tmp'):
				f = open('/tmp/info_df.tmp', 'r')
				for line in f.readlines():
					line = line.replace('part1', ' ')
					x = line.strip().split()
					if x[0] == '/dev/root':
						fls = int(x[4].replace('%', ''))
						s = getUnit(int(x[1]))
						self['f1'].setText('Flash: %s  in use: %s' % (s, x[4]))
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['f2'].setText('Flash: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
					elif x[len(x)-1] == '/media/cf':
						cf[0] = int(x[4].replace('%', ''))
						cf[1] = int(x[1])
						cf[2] = int(x[2])
						cf[3] = int(x[3])
						s = getUnit(int(x[1]))
						self['c1'].setText('CF: %s  in use: %s' % (s, x[4]))
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['c2'].setText('CF: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
					elif x[len(x)-1] == '/media/usb':
						usb[0] = int(x[4].replace('%', ''))
						usb[1] = int(x[1])
						usb[2] = int(x[2])
						usb[3] = int(x[3])
						s = getUnit(int(x[1]))
						self['u1'].setText('USB: %s  in use: %s' % (s, x[4]))
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['u2'].setText('USB: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
					elif x[len(x)-1] == '/media/hdd':
						hdd[0] = int(x[4].replace('%', ''))
						hdd[1] = int(x[1])
						hdd[2] = int(x[2])
						hdd[3] = int(x[3])
						s = getUnit(int(x[1]))
						self['h1'].setText('HDD: %s  in use: %s' % (s, x[4]))
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['h2'].setText('HDD: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
				f.close()
				tot[0] = cf[1] + usb[1] + hdd[1] # Total Memory
				tot[1] = cf[2] + usb[2] + hdd[2] # Used Memory
				tot[2] = cf[3] + usb[3] + hdd[3] # Free Memory
				if (tot[0] > 100):
					tot[3] = tot[1] * 100 / tot[0]
				self['t1'].setText('Total Space: %s  in use: %d%%' % (getUnit(tot[0]), tot[3]))
				s = getSize(tot[0],tot[1],tot[2])
				self['t2'].setText('Total: %s  Used: %s  Free: %s' % (s[0],s[1],s[2]))
				self['flsp'].setValue(fls)
				self['cfp'].setValue(cf[0])
				self['usbp'].setValue(usb[0])
				self['hddp'].setValue(hdd[0])
				self['totp'].setValue(tot[3])
		
		r = [0,0,0]
		if fileExists('/tmp/info_mem.tmp'):
				f = open('/tmp/info_mem.tmp', 'r')
				for line in f.readlines():
					x = line.strip().split()
					if (x[0] == 'Mem:'):
						r[0] = int(int(x[2]) * 100 / int(x[1]))
						self['rr1'].setText('Ram in use: %d%%' %  r[0])
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['rr2'].setText('Ram: %s Used: %s Free: %s Shared: %s Buf: %s' % (s[0],s[1],s[2],getUnit(int(x[4])),getUnit(int(x[5]))))
					elif (x[0] == 'Swap:'):
						if int(x[1]) > 1:
							r[1] = int(int(x[2]) * 100 / int(x[1]))
						self['rs1'].setText('Swap in use: %d%%' %  r[1])
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['rs2'].setText('Swap: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
					elif (x[0] == 'Total:'):
						r[2] = int(int(x[2]) * 100 / int(x[1]))
						self['rt1'].setText('Total Memory:  %s  in use:: %d%%' % (getUnit(int(x[1])), r[2]))
						s = getSize(int(x[1]),int(x[2]),int(x[3]))
						self['rt2'].setText('Total: %s\tUsed: %s\tFree: %s' % (s[0],s[1],s[2]))
				f.close()
				self['rrpr'].setValue(r[0])
				self['rspr'].setValue(r[1])
				self['rtpr'].setValue(r[2])

class showEnigmaInfo(Screen):
	__module__ = __name__
	skin = """
		<screen position="110,95" size="500,405">
		<widget name="infotext" position="10,10" size="480,380" font="Regular;18" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self['infotext'] = ScrollLabel('')
		self['actions'] = ActionMap(['WizardActions',
			'DirectionActions'], {'ok': self.close,
			'back': self.close,
			'up': self['infotext'].pageUp,
			'left': self['infotext'].pageUp,
			'down': self['infotext'].pageDown,
			'right': self['infotext'].pageDown})
		self.onLayoutFinish.append(self.updatetext)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Enigma Setting Info"))

	def updatetext(self):
		strview = ''
		if fileExists('/etc/enigma2/settings'):
				f = open('/etc/enigma2/settings', 'r')
				for line in f.readlines():
					strview += line
				f.close()
				self['infotext'].setText(strview)
