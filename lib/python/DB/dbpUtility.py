from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Console import Console
from Components.FileList import FileList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigYesNo, NoSave, config, ConfigFile, ConfigNothing, ConfigSelection
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from os import system, remove as os_remove
from dbpTool import ListboxE1, GetSkinPath, ListboxE4, dbpTool
from dbpConsole import dbpConsole
from dbpShowPanel import dbpShowPanel
from enigma import eTimer
from Tools.Directories import fileExists

t = dbpTool()
configfile = ConfigFile()

def checkDev():
	try:
		mydev = []
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if (line.find('/cf') != -1):
				mydev.append(('/media/cf/','COMPACT FLASH'))
			if (line.find('/media/usb') != -1):
				mydev.append(('/media/usb/','USB PEN'))
			if (line.find('/hdd') != -1):
				mydev.append(('/media/hdd/','HARD DISK'))
		f.close()
		if mydev:
			return mydev
	except:
		return None

class NUtility(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self.menuList = [
			('Services',_('Start/Stop Services'),'icons/enigma.png'),
			('Module',_('Manage Kernel Modules'),'icons/module.png'),
			('Ssetup',_('Manage Startup Services'),'icons/log.png'),
			('Slog',_('View Services Logs'),'icons/setup.png'),
			('Ccommand',_('Execute commands'),'icons/terminal.png'),
			('NUserScript',_('Execute Users Scripts'),'icons/user.png'),
			('NSwap',_('Manage Swap File'),'icons/swapsettings.png'),
			('Csave',_('Save Enigma Setting'),'icons/save.png')
			]
		self["title"] = Label(_("System Utility"))
		self['list'] = ListboxE1(self.list)
		self["key_red"] = Label(_("Exit"))
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			'back': self.close
		})
		self.saveConfTimer = eTimer()
		self.saveConfTimer.timeout.get().append(self.saveConf)
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.updateList)
	
	def setWindowTitle(self):
		self.setTitle(_("System Utility"))
	
	def KeyOk(self):
		self.sel = self["list"].getCurrent()[0]
		if (self.sel == "Services"):
			self.session.open(NServices)
		elif (self.sel == "Module"):
			self.session.open(NModule)
		elif (self.sel == "Ssetup"):
			self.session.open(NServicesSetup)
		elif (self.sel == "Slog"):
			self.session.open(NServicesLog)
		elif (self.sel == "Ccommand"):
			self.session.open(NCommand)
		elif (self.sel == "NUserScript"):
			self.session.open(NUserScript)
		elif (self.sel == "NSwap"):
			if checkDev() == None:
				msg = _('No device for swap found!')
				confBox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				confBox.setTitle(_("Swap Error"))
			else:
				self.session.open(NSwap)
		elif (self.sel == "Csave"):
			msg = _('Saving Enigma Setting\nPlease Wait...')
			self.confBox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.confBox.setTitle(_("Saving"))
			self.saveConfTimer.start(50, False)
		
	def saveConf(self):
		self.saveConfTimer.stop()
		configfile.save()
		self.confBox.close()
	
	def updateList(self):
		del self.list[:]
		skin_path = GetSkinPath()
		for men in self.menuList:
			res = [men[0]]
			res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=men[1]))
			res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=LoadPixmap(skin_path + men[2])))
			self.list.append(res)
		self['list'].l.setList(self.list)

class NCommand(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,65" size="540,340" scrollbarMode="showOnDemand"/>
			<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self["title"] = Label(_("Execute commands"))
		self['list'] = ListboxE4(self.list)
		self["key_red"] = Label(_("Exit"))
		self["key_yellow"] = Label(_("Custom"))
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			"yellow": self.openCustom,
			'back': self.close
		})
		self.onLayoutFinish.append(self.updateList)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Execute Commands"))

	def KeyOk(self):
		cmd = self["list"].getCurrent()[0]
		self.runCommand(cmd)	
	
	def updateList(self):
		del self.list[:]
		if fileExists('/etc/custom_command'):
			f = open('/etc/custom_command', 'r')
			for line in f.readlines():
				a = line.split(":")
				res = [a[1].strip()]
				res.append(MultiContentEntryText(pos=(0, 0), size=(340, 25), font=0, text=a[0].strip()))
				self.list.append(res)
		else:
			res = ["None"]
			res.append(MultiContentEntryText(pos=(0, 0), size=(340, 25), font=0, text=_("File /etc/custom_command  not found!")))
			self.list.append(res)
		self['list'].l.setList(self.list)

	def openCustom(self):
		if config.dbp.usevkeyboard.value:
			self.session.openWithCallback(self.runCommand, VirtualKeyBoard, title = (_("Enter command to run:")), text = "")
		else:
			self.session.openWithCallback(self.runCommand,InputBox, title = _("Enter command to run:"), windowTitle = _("Execute Commands"), text="")

	def runCommand(self, cmd):
		if cmd is not None:
			self.session.open(Console, title = (_('Execute command: ')) + cmd, cmdlist = [cmd])

class NUserScript(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,65" size="540,340" scrollbarMode="showOnDemand"/>
			<widget name="key_red" position="0,510" size="510,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self["title"] = Label(_("Execute Users Scripts"))
		self['list'] = ListboxE4(self.list)
		self["key_red"] = Label(_("Exit"))
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			'back': self.close
		})
		self.onLayoutFinish.append(self.updateList)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle("Execute Users Scripts")
	
	def KeyOk(self):
		cmd = self["list"].getCurrent()[0]
		if cmd:
			self.runCommand("/usr/script/" + cmd + "_user.sh")	
	
	def updateList(self):
		del self.list[:]
		filelist = FileList("/usr/script", matchingPattern = "_user.sh")
		for x in filelist.getFileList():
			if x[0][1] != True:
				scriptName = t.getScriptName(x[0][0][:-8]) 
				res = [x[0][0][:-8]]
				res.append(MultiContentEntryText(pos=(0, 0), size=(340, 25), font=0, text=scriptName))
				self.list.append(res)
		if len(self.list) == 0:
			res = ["None"]
			res.append(MultiContentEntryText(pos=(0, 0), size=(340, 25), font=0, text=_("No Users Script Found!")))
			self.list.append(res)
		self['list'].l.setList(self.list)

	def runCommand(self, cmd):
		if cmd is not None:
			self.session.open(Console, title = (_('Execute script: ')) + cmd, cmdlist = [cmd])

class NServices(Screen):
	__module__ = __name__

	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,65" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		self.servicesList = [
			('nfs','/etc/init.d/nfsserver','[nfsd]','NFS Server'),
			('smb','/etc/init.d/samba','/usr/sbin/smbd','Samba'),
			('autofs','/etc/init.d/autofs','/usr/sbin/automount','Automount'),
			('vpn','/etc/init.d/openvpn','/usr/sbin/openvpn','OpenVPN'),
			('ipudate','/etc/init.d/ipupdate','/usr/bin/ez-ipupdate','IpUpdate'),
			('inadyn','/etc/init.d/inadyn','inadyn','InaDyn'),
			('ssh','/etc/init.d/dropbear','dropbear','Dropbear (SSH)'),
			('vsftpd','/etc/init.d/vsftpd','/usr/sbin/vsftpd','FTP Server'),
			('crond','/etc/init.d/busybox-cron','/usr/sbin/crond','Crontab')
			]
		self.servicestatus = {}
		self["title"] = Label(_("Manage Services"))
		self["key_red"] = Label(_("Exit"))
		self["key_yellow"] = Label(_("Setup"))
		self['list'] = ListboxE1(self.list)
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"yellow": self.openSetting,
			"red": self.close,
			'back': self.close
		})
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.updateList)
	
	def setWindowTitle(self):
		self.setTitle(_("Manage services"))

	def openSetting(self):
		self.session.open(NServicesSetup)
	
	def KeyOk(self):
		ser = self['list'].getCurrent()[0]
		if ser:
			for s in self.servicesList:
				if s[0] == ser:
					cmd = {True:s[1] + ' stop',False:s[1] + ' start'}[self.servicestatus.get(s[0])]
			self.session.openWithCallback(self.executedScript, dbpConsole, cmd, _('Execute command: ') + cmd)

	def executedScript(self, *answer):
		self.updateList()
	
	def readStatus(self):
		for ser in self.servicesList:
			self.servicestatus[ser[0]] = False
		system("ps -ef > /tmp/status.log")
		f = open('/tmp/status.log', 'r')
		for line in f.readlines():
			for ser in self.servicesList:
				if (line.find(ser[2]) != -1):
					self.servicestatus[ser[0]] = True
		f.close()
		
	def updateList(self):
		self.readStatus()
		del self.list[:]
		skin_path = GetSkinPath() + 'menu/'
		for ser in self.servicesList:
			res = [ser[0]]
			res.append(MultiContentEntryText(pos=(5, 5), size=(250, 32), font=0, text={False: _('Start'),True: _('Stop')}[self.servicestatus.get(ser[0])] + ' ' + ser[3]))
			png = LoadPixmap({ True:skin_path + 'menu_on.png',False:skin_path + 'menu_off.png' }[self.servicestatus.get(ser[0])])
			res.append(MultiContentEntryPixmapAlphaTest(pos=(260, 6), size=(80, 23), png=png))
			self.list.append(res)
		self['list'].l.setList(self.list)

class NModule(Screen):
	__module__ = __name__

	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,65" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.modules = [
			('sr_mod','USB CD/DVD'),
			('usbhid','USB Human Int. Device'),
			('ftdi_sio','USB Serial (FTDI Smargo)'),
			('pl2303','USB Serial (PL2303)'),
			('tun','TUN (OpenVPN)'),
			('rt73','WLAN Usb Adapter RT73'),
			('zd1211b','WLAN Usb Adapter ZD1211B'),
			('isofs','ISOFS (CD/DVD)'),
			('cdfs','CDFS (Audio-CD)'),
			('udf','UDF (CD/DVD)'),
			('ntfs','NTFS (Windows)'),
			('smbfs','SMBFS (Windows)')
			]
		self.modstatus = {}
		self.list = []
		self["title"] = Label(_("Manage Modules"))
		self["key_red"] = Label(_("Exit"))
		self['list'] = ListboxE1(self.list)
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			'back': self.close
		})
		
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.updateList)
	
	def setWindowTitle(self):
		self.setTitle(_("Manage Modules"))
	
	def KeyOk(self):
		sel = self['list'].getCurrent()[0]
		if sel:
			cmd = "modprobe " + {True:'-rv ',False:'-v '}[self.modstatus.get(sel)] + sel
			self.session.openWithCallback(self.executedScript, dbpConsole, cmd, _('Execute command: ') + sel)

	def executedScript(self, *answer):
		self.updateList()
		
	def saveStatus(self):
		out = open('/etc/dbp.modules', 'w')
		for mod in self.modules:
			if self.modstatus.get(mod[0]):
				out.write(mod[0] + '\n')
		out.close()
	
	def readStatus(self):
		for mod in self.modules:
			self.modstatus[mod[0]] = False
		system("lsmod > /tmp/status.log")
		f = open('/tmp/status.log', 'r')
		for line in f.readlines():
			for mod in self.modules:
				if (line.find(mod[0]) != -1):
					self.modstatus[mod[0]] = True
		f.close()
		self.saveStatus()
		
	def updateList(self):
		self.readStatus()
		del self.list[:]
		skin_path = GetSkinPath()
		for mod in self.modules:
			res = [mod[0]]
			res.append(MultiContentEntryText(pos=(5, 5), size=(250, 32), font=0, text=mod[1]))
			png = LoadPixmap({ True:skin_path + 'menu/menu_on.png',False:skin_path + 'menu/menu_off.png' }[self.modstatus.get(mod[0])])
			res.append(MultiContentEntryPixmapAlphaTest(pos=(260, 6), size=(80, 23), png=png))
			self.list.append(res)
		
		self['list'].l.setList(self.list)

class NServicesSetup(Screen, ConfigListScreen):
	__module__ = __name__
	
	skin = """
		<screen position="330,160" size="620,440" title="Manage Startup">
			<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />
			<widget name="conn" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" backgroundColor="#6565ff" />
			<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self.initPath = ['/etc/rc2.d','/etc/rc3.d','/etc/rc4.d','/etc/rc4.d','/etc/rc5.d']
		self.servicesList = [
			('nfsserver','S20nfsserver',_('Activate NFS Server at boot?')),
			('samba','S20samba',_('Activate Samba Server at boot?')),
			('autofs','S21autofs',_('Activate Automount at boot?')),
			('openvpn','S30openvpn',_('Activate OpenVPN at boot?')),
			('ipupdate','S20ipupdate',_('Activate IpUpdate at boot?')),
			('inadyn','S30inadyn',_('Activate InaDyn at boot?')),
			('dropbear','S10dropbear',_('Activate Dropbear (SSH) at boot?')),
			('vsftpd','S20vsftpd',_('Activate FTP Server at boot?')),
			('busybox-cron','S99cron',_('Activate Crontab at boot?'))
			]
		self.serviceconfig = {}
		ConfigListScreen.__init__(self, self.list)
		self["oktext"] = Label(_("OK"))
		self["canceltext"] = Label(_("Exit"))
		self['conn'] = Label("")
		self['conn'].hide()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], 
		{
			"red": self.close,
			"back": self.close,
			"green": self.saveSetting
		})
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.loadSetting)
		
	def setWindowTitle(self):
		self.setTitle(_("Manage Startup Services"))
	
	def loadSetting(self):
		del self.list[:]
		for s in self.servicesList:
			self.serviceconfig[s[0]] = NoSave(ConfigYesNo(default = False))
			self.list.append(getConfigListEntry(s[2], self.serviceconfig[s[0]]))
			if fileExists('/etc/rc3.d/' + s[1]):
				self.serviceconfig[s[0]].value = True
			self['config'].list = self.list
			self['config'].l.setList(self.list)
	
	def saveSetting(self):
		self['conn'].show()
		self['conn'].setText(_('Saving Setting. Please wait...'))
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.saveConf)
		self.activityTimer.start(300, False)
		
	def saveConf(self):
		self.activityTimer.stop()
		for p in self.initPath:
			for s in self.servicesList:
				system({True:'ln -s ../init.d/%s %s/%s' % (s[0],p,s[1]),False:'rm -f %s/%s' % (p,s[1])}[self.serviceconfig[s[0]].value])
		self.close()

class NServicesLog(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430" title="Addons">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self.logsList = [
			('inadyn',config.inadyn.log.value.strip() +'/inadyn.log',_('Show InaDyn Log')),
			('smb','/var/log/log.smbd',_('Show SMB Server Log')),
			('nmb','/var/log/log.nmbd',_('Show NMB Log')),
			('vsftpd','/var/log/vsftpd.log',_('Show FTP Server Log')),
			('openvpn','/etc/openvpn/openvpn.log',_('Show OpenVPN Log'))
			]
		self["title"] = Label(_("Services Logs"))
		self['list'] = ListboxE1(self.list)
		self["key_red"] = Label(_("Exit"))
		self["key_yellow"] = Label(_("Clear log"))
		self.updateList()
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"yellow": self.deleteLog,
			"red": self.close,
			'back': self.close
		})
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Services Logs"))

	def KeyOk(self):
		log = self["list"].getCurrent()[0]
		if log:
			for l in self.logsList:
				if l[0] == log:
					cmd = l
			self.session.open(dbpShowPanel, cmd[1] ,cmd[0] + _(' logged info')) 
	
	def deleteLog(self):
		self.session.open(deleteLog)
	
	def updateList(self):
		del self.list[:]
		skin_path = GetSkinPath()
		for log in self.logsList:
			res = [log[0]]
			res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=log[2]))
			res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=LoadPixmap(skin_path + 'icons/log.png')))
			self.list.append(res)
		self['list'].l.setList(self.list)

class deleteLog(Screen, ConfigListScreen):
	__module__ = __name__
	
	skin = """
		<screen position="330,160" size="620,440" title="Delete log files">
			<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />
			<widget name="conn" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" backgroundColor="#6565ff" />
			<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self.logsList = [
			('inadyn',config.inadyn.log.value.strip() +'/inadyn.log',_('Delete InaDyn log file?')),
			('smb','/var/log/log.smbd',_('Delete SMB log file?')),
			('nmb','/var/log/log.nmbd',_('Delete NMB log file?')),
			('vsftpd','/var/log/vsftpd.log',_('Delete FTP log file?')),
			('openvpn','/etc/openvpn/openvpn.log',_('Delete OpenVPN log file?')),
			('enigma','/hdd/*.log',_('Delete Enigma Crash log file?'))
			]
		self.logconfig = {}
		ConfigListScreen.__init__(self, self.list)
		self["oktext"] = Label(_("Delete"))
		self["canceltext"] = Label(_("Exit"))
		self['conn'] = Label("")
		self['conn'].hide()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], 
		{
			"red": self.close,
			"back": self.close,
			"green": self.delLog
		})
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.loadSetting)
		
	def setWindowTitle(self):
		self.setTitle(_("Delete Log Files"))
	
	def loadSetting(self):
		del self.list[:]
		for l in self.logsList:
			self.logconfig[l[0]] = NoSave(ConfigYesNo(default = False))
			self.list.append(getConfigListEntry(l[2], self.logconfig[l[0]]))
			self['config'].list = self.list
			self['config'].l.setList(self.list)
	
	def delLog(self):
		self['conn'].show()
		self['conn'].setText(_('Deleting log files. Please wait...'))
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.DLog)
		self.activityTimer.start(300, False)
		
	def DLog(self):
		self.activityTimer.stop()
		for l in self.logsList:
			if self.logconfig[l[0]].value:
				system("rm -f " + l[1])
		self.close()

class NSwap(Screen, ConfigListScreen):
	__module__ = __name__
	
	skin = """
		<screen position="330,160" size="620,440">
			<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />
			<widget name="conn" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" backgroundColor="#6565ff" />
			<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["oktext"] = Label(_("Save"))
		self["canceltext"] = Label(_("Exit"))
		self['conn'] = Label("")
		self['conn'].hide()
		self.active = False
		self.loc = ''
		self.size = 0
		self.activityTimer = eTimer()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], 
		{
			"red": self.close,
			"back": self.close,
			"green": self.saveSwap
		})
		self.loadSetting()
		self.onShown.append(self.setWindowTitle)
		
	def setWindowTitle(self):
		self.setTitle(_("Manage Swap File"))
	
	def loadSetting(self):
		self.mydev = checkDev()
		mystat = self.findSwap()
		del self.list[:]
		self.loc = self.mydev[0][0]
		self.size = 32768
		if mystat != None:
			self.active = True
			self.loc = mystat[0]
			self.size = mystat[1] + 8
		
		self.swap_active = NoSave(ConfigYesNo(default = self.active))
		self.list.append(getConfigListEntry(_('Activate Swap File?'), self.swap_active))
		self.swap_size = NoSave(ConfigSelection(default = self.size, choices =[
												(8192,'8 MB'), (16384,'16 MB'), (32768,'32 MB'),
												(65536,'64 MB'), (131072,'128 MB'), (262144,'256 MB')]))
		self.list.append(getConfigListEntry(_('Swap file size'), self.swap_size))
		self.swap_location = NoSave(ConfigSelection(default = self.loc, choices = self.mydev))
		self.list.append(getConfigListEntry(_('Swap file location'), self.swap_location))
		self['config'].list = self.list
		self['config'].l.setList(self.list)
	
	def saveSwap(self):
		self['conn'].show()
		self['conn'].setText(_('Saving swap config. Please wait...'))
		self.activityTimer.timeout.get().append(self.Dsave)
		self.activityTimer.start(500, False)
		
	def Dsave(self):
		self.activityTimer.stop()
		swapfile = self.swap_location.value.strip() + 'swapfile'
		cmd = ''
		if (self.swap_active.value) and (not self.active):
			cmd += "echo 'Creating swap file...'"
			cmd += ' && '
			cmd += 'dd if=/dev/zero of=' + swapfile + ' bs=1024 count=' + str(self.swap_size.value)
			cmd += ' && '
			cmd += "echo 'Creating swap device...'"
			cmd += ' && '
			cmd += 'mkswap ' + swapfile
			cmd += ' && '
			cmd += "echo 'Activating swap device...'"
			cmd += ' && '
			cmd += 'swapon ' + swapfile
			self.session.openWithCallback(self.scriptReturn, dbpConsole, cmd, _('Creating Swap file...'))
		elif (not self.swap_active.value) and (self.active):
			cmd += "echo 'Dectivating swap device...'"
			cmd += ' && '
			cmd += 'swapoff ' + swapfile
			cmd += ' && '
			cmd += "echo 'Removing swap file...'"
			cmd += ' && '
			cmd += 'rm -f ' + swapfile
			self.session.openWithCallback(self.scriptReturn, dbpConsole, cmd, _('Deleting Swap file...'))
		else:
			self['conn'].setText(_('Nothing to do!'))
	
	def scriptReturn(self, *answer):
		if answer[0] == dbpConsole.EVENT_DONE:
			self['conn'].setText(_('Swap process completed successfully!'))
		else:
			self['conn'].setText(_('Swap process killed by user!'))
		self.loadSetting()

	def findSwap(self):
		try:
			myswap = []
			f = open('/proc/swaps', 'r')
			for line in f.readlines():
				if (line.find('/swapfile') != -1):
					myswap = line.strip().split()
			f.close()
			if myswap:
				return '/media/' + myswap[0].split("/")[2] + "/", int(myswap[2])
		except:
			return None

