from Components.ActionMap import ActionMap
from Components.config import config, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from enigma import eDVBDB, eEPGCache, eTimer
from time import strftime, time, localtime
from StayUpLog import writeLog
from StayUpDownload import download
import os

##############################################################################


config.plugins.StayUP = ConfigSubsection()
config.plugins.StayUP.Enabled = ConfigYesNo(default=False)
config.plugins.StayUP.Epg = ConfigYesNo(default=False)
config.plugins.StayUP.PiconType = ConfigSelection(
                                [("enigma2-BlackPiconBig-TopItalia-r01", "BlackPicon by Claudio72"),
                                ("disabled_picon", "Disabled")
                                ], "disabled_picon")
config.plugins.StayUP.SettingsType = ConfigSelection(
                                [("enigma2_settings_stayUP", "Dual by vHannibal"),
                                ("enigma2_settings_motor_marcus", "Motor 68E-45W by marcus206"),
                                ("disabled_settings", "Disabled")
                                ], "disabled_settings")
config.plugins.StayUP.DebugMode = ConfigYesNo(default=True)
config.plugins.StayUP.AutoUpdate = ConfigYesNo(default=False)

##############################################################################


class StayUPBackgroundWorker():
	def __init__(self):
		writeLog("000 stayUP init BackgroundWorker mainloop")
        	self.loop = eTimer()
        	self.loop.callback.append(self.ExecTask)
		if config.plugins.StayUP.Enabled.value:
			writeLog("010 Background execution Enabled")
		else:
			writeLog("015 Background execution Disabled")
	
	def startTimer(self):
		if config.plugins.StayUP.Enabled.value:
			writeLog("020 Plugin Master Enabled")
		else:
			writeLog("025 Plugin Master Disabled")
      	 	self.loop.start(1, 1)

	def ExecTask(self):
		writeLog("030 Execution Called")
		self.loop.stop()
		if config.plugins.StayUP.Enabled.value:
			writeLog("035 Looking for new files...")
			download(self)
        	self.loop.start(480 * 60 * 1000, 1)
		writeLog("040 Next check in 8 hours...")

# Function Called via Autostart, Enigma2 Loading Level
StayLoop=StayUPBackgroundWorker()

class StayUPConfigFunction(ConfigListScreen, Screen):
	skin = """
		<screen position="80,170" size="560,270" title="StayUP">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="0,45" size="560,220" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = Label(_("About"))
		self["key_green"] = Label(_("Save"))
		self["key_blue"] = Label(_("Execute"))
		self["key_yellow"] = Label(_("View Log"))
		list = []
                list.append(getConfigListEntry(_("Enable Plugin:"), config.plugins.StayUP.Enabled))
                list.append(getConfigListEntry(_("EPG Download:"), config.plugins.StayUP.Epg))
#               list.append(getConfigListEntry(_("Enable Picon Download:"), config.plugins.StayUP.PiconType))
                list.append(getConfigListEntry(_("Picon Type:"), config.plugins.StayUP.PiconType))
                list.append(getConfigListEntry(_("Settings Type:"), config.plugins.StayUP.SettingsType))
                list.append(getConfigListEntry(_("Enable Debug:"), config.plugins.StayUP.DebugMode))
                list.append(getConfigListEntry(_("Enable stayUP Autoupdate:"), config.plugins.StayUP.AutoUpdate))
#		ConfigListScreen.__init__(self, [getConfigListEntry(_("Enable Plugin:"), config.plugins.StayUP.onoff)])
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "HelpActions"], {"displayHelp": self.helpscreen, "red": self.about, "yellow": self.logviewer, "green": self.save, "blue": self.execute, "cancel": self.exit}, -1)

	def helpscreen(self):
		writeLog("050 Help Key Pressed")
		os.system ("rm /usr/log/*.SIGNATURE")
		self.session.open(Console, "stayUP", ["cat /usr/lib/enigma2/python/Plugins/Extensions/StayUP/help.txt"])
	def about(self):
		writeLog("051 Red Key Pressed")
		self.session.open(MessageBox, (_("StayUP")), MessageBox.TYPE_INFO)
	def execute(self):
		writeLog("052 Blue Key Pressed")
		if config.plugins.StayUP.Epg.value:
			if not os.path.exists("/usr/bin/dbpd"):
				self.session.open(MessageBox,("Auto EPG really works only on a pure DB IMAGE"), MessageBox.TYPE_INFO)
				config.plugins.StayUP.Epg.value = False
		download(self)

	def logviewer(self):
		writeLog("053 Yellow Key Pressed")
		self.session.open(Console, "stayUP", ["cat /tmp/StayUpPlugin.log"])

	def save(self):
		writeLog("054 Red Key Pressed")
		if config.plugins.StayUP.Epg.value:
			if not os.path.exists("/usr/bin/dbpd"):
				self.session.open(MessageBox,("Auto EPG really works only on a pure DB IMAGE"), MessageBox.TYPE_INFO)
				config.plugins.StayUP.Epg.value = False
		for x in self["config"].list:
			x[1].save()
		writeLog("060 Configuration Saved")
		self.close()

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		writeLog("065 Configuration not Saved")
		self.close()


##############################################################################

def autostart(reason, **kwargs):
       if reason == 0 :
          StayLoop.startTimer()

def main(session, **kwargs):
	session.open(StayUPConfigFunction)

def Plugins(**kwargs):
	return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart),
	PluginDescriptor(
	name="StayUP",
	description="For Lazy People",
	where=PluginDescriptor.WHERE_PLUGINMENU,
	icon="plugin-fs8.png",
	fnc=main)]
