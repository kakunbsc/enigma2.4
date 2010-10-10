from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap,NumberActionMap
from Components.config import config
from Components.config import config, getConfigListEntry, ConfigInteger, ConfigSubsection, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText


config.plugins.fancontrols = ConfigSubsection()
config.plugins.fancontrols.standbymode = ConfigSelection(default = "off", choices = [
	("off", _("off")), ("on", _("on"))])
config.plugins.fancontrols.usetimer = ConfigSelection(default = "off", choices = [
	("off", _("no")), ("on", _("yes"))])
config.plugins.fancontrols.fanontime = ConfigInteger(default = 5, limits = (1, 100))
config.plugins.fancontrols.fanofftime = ConfigInteger(default = 60, limits = (1, 100))

class FancontrolConfiguration(Screen, ConfigListScreen):
	skin = """
		<screen name="FancontrolConfiguration" position="center,center" size="560,300" title="Standbymode Fancontrol settings" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ececec" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ececec" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" zPosition="2" position="5,50" size="550,200" scrollbarMode="showOnDemand" transparent="1" />
		</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.standbyEntry = None
		self.usetimerEntry = None
		self.fanontimeEntry = None
		self.fanofftimeEntry = None

		self["shortcuts"] = ActionMap(["ShortcutActions", "SetupActions" ],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list,session = self.session)
#		self.getFaninfo()
		self.createSetup()

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()

	def getFaninfo(self):
		try:
			value=int(open('/proc/stb/system/standby_fan_off','r').read())
			if value is 0:
				config.plugins.fancontrols.standbymode.value="on"
			else:
				config.plugins.fancontrols.standbymode.value="off"
			value=int(open('/proc/stb/system/use_fan_timer','r').read())
			if value is 0:
				config.plugins.fancontrols.usetimer.value = "off"
			else:
				config.plugins.fancontrols.usetimer.value = "on"
			time=int(open('/proc/stb/system/fan_on_time','r').read())
			if time > 0 and time < 101:
				config.plugins.fancontrols.fanontime.value = time
			else:
				config.plugins.fancontrols.fanontime.value = 1
			time=int(open('/proc/stb/system/fan_off_time','r').read())
			if time > 0 and time < 101:
				config.plugins.fancontrols.fanofftime.value = time
			else:
				config.plugins.fancontrols.fanofftime.value = 1
		except:
			print 'Error read proc of fan'
	

	def createSetup(self):
		self.list = []
		self.standbyEntry = getConfigListEntry(_("Fan basic action"), config.plugins.fancontrols.standbymode)
		self.usetimerEntry = getConfigListEntry(_("Use Fan timer"), config.plugins.fancontrols.usetimer)
		self.fanontimeEntry = getConfigListEntry(_("Fan on duration time"), config.plugins.fancontrols.fanontime)
		self.fanofftimeEntry = getConfigListEntry(_("Fan off duration time"), config.plugins.fancontrols.fanofftime)

		self.list.append( self.standbyEntry )
		if config.plugins.fancontrols.standbymode.value is "off":
			self.list.append( self.usetimerEntry )
			if config.plugins.fancontrols.usetimer.value is not "off":
				self.list.append( self.fanontimeEntry )
				self.list.append( self.fanofftimeEntry )
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)

	def newConfig(self):
		if self["config"].getCurrent() == self.usetimerEntry or self["config"].getCurrent() == self.standbyEntry:
			self.createSetup()

	def selectionChanged(self):
		current = self["config"].getCurrent()
		print current

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close()

			
	def keyCancel(self):
		print "cancel"
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

	def keySave(self):
		ConfigListScreen.keySave(self)
		try:
			if config.plugins.fancontrols.standbymode.value is "on":
				open('/proc/stb/system/standby_fan_off','w').write('0')
			else:
				open('/proc/stb/system/standby_fan_off','w').write('1')
				if config.plugins.fancontrols.usetimer.value is "off":
					open('/proc/stb/system/use_fan_timer','w').write('0')
				else:
					open('/proc/stb/system/use_fan_timer','w').write('1')
					open('/proc/stb/system/fan_on_time','w').write('%s'%config.plugins.fancontrols.fanontime.value)
					open('/proc/stb/system/fan_off_time','w').write('%s'%config.plugins.fancontrols.fanofftime.value)
		except:
			print 'Error write proc of fan'
		
	
def openconfig(session, **kwargs):
	session.open(FancontrolConfiguration)

def selSetup(menuid, **kwargs):
	if menuid != "system":
		return [ ]

	return [(_("Fan Control"), openconfig, "fancontrol_config", 70)]

def setfancontrol(reason, **kwargs):
	try:
		if config.plugins.fancontrols.standbymode.value is "on":
			open('/proc/stb/system/standby_fan_off','w').write('0')
		else:
			open('/proc/stb/system/standby_fan_off','w').write('1')
			if config.plugins.fancontrols.usetimer.value is "off":
				open('/proc/stb/system/use_fan_timer','w').write('0')
			else:
				open('/proc/stb/system/use_fan_timer','w').write('1')
				open('/proc/stb/system/fan_on_time','w').write('%s'%config.plugins.fancontrols.fanontime.value)
				open('/proc/stb/system/fan_off_time','w').write('%s'%config.plugins.fancontrols.fanofftime.value)
	except:
		print 'Error to set fan control'

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Fancontrols", description = "check Fan Control settings", where = PluginDescriptor.WHERE_AUTOSTART, fnc = setfancontrol),
	PluginDescriptor(name=_("Fan control"), description="Fan Control", where = PluginDescriptor.WHERE_MENU, fnc=selSetup)]
