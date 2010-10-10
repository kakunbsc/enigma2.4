from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ParentalControlSetup import ParentalControlSetup
from Screens.PluginBrowser import PluginBrowser
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.ConfigList import ConfigList
from Components.config import ConfigSelection, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.Pixmap import Pixmap
from dbpTool import *
from dbpShowPanel import dbpShowPanel
from dbpConsole import dbpConsole
from dbpInfo import NInfo
from dbpUtility import NUtility
from dbpSetting import NSetupSummary
from dbpAddons import NAddons
import os

from enigma import eTimer, eDVBCI_UI, nemTool,iServiceInformation

t = dbpTool()
tool = nemTool()

class dbpBluePanel(Screen):
	
	skin = """
	<screen name="dbpBluePanel" position="0,0" size="500,720" flags="wfNoBorder">
		<widget name="title" position="50,40" size="300,32" font="Regular;40" halign="center" foregroundColor="#53a9ff" backgroundColor="transpBlack" transparent="1"/>
		<widget name="info_use" position="50,110" zPosition="2" size="340,30" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="#1f771f" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="config" position="50,150" size="340,50" zPosition="2" />
		<widget name="key_1" position="50,220" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="#9f1313" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_2" position="50,250" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="#9f1313" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_3" position="50,280" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;21" transparent="1" backgroundColor="#9f1313" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_blue" position="50,320" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="#6565ff" backgroundColor="#1f771f" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_yellow" position="50,350" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="#bab329" backgroundColor="#1f771f" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="50,380" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="#389416" backgroundColor="#1f771f" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_red" position="50,410" zPosition="2" size="300,30" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="#ff2525" backgroundColor="#9f1313" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="ecmtext" position="50,460" size="340,240" font="Regular;18" zPosition="2" backgroundColor="#333333" transparent="1"/>
	</screen>"""
	
	DBPVER = "DB-PROJECT"
	DBPVERDATE = "22-07-2009"
	CVSDATE = "2.6Exp 22-07-2009"
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['config'] = ConfigList(self.list)
		self["title"] = Label(_("DB Panel"))
		self["ecmtext"] = ScrollLabel("")
		self["key_blue"] = Label(_("Addons Manager"))
		self["key_yellow"] = Label(_("System Settings"))
		self["key_green"] = Label(_("System Information"))
		self["key_red"] = Label(_("System Utility"))
		self["key_1"] = Label(_("DB News"))
		self["key_2"] = Label(_("Parental Control Setup"))
		self["key_3"] = Label(_("About DB"))
		self["info_use"] = Label(_("Use arrows < > to select"))
		self["actions"] = NumberActionMap(["ColorActions", "CiSelectionActions","WizardActions","SetupActions"],
			{
				"left": self.keyLeft,
				"right": self.keyRight,
				"blue": self.naddons,
				"green": self.ninfo,
				"yellow": self.nsetting,
				"red": self.nutility,
				"ok": self.ok_pressed,
				"back": self.close,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal
			},-1)
		self.activityTimer = eTimer()
		self.ecmTimer = eTimer()
		self.ecmTimer.timeout.get().append(self.readEcmInfo)
		self.ecmTimer.start(10000, True)
		self.readEcmInfo()
		self.onLayoutFinish.append(self.loadEmuList)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("DB Blue Panel"))
	
	def loadEmuList(self):
		emu = []
		crd = []
		emu.append("None")
		crd.append("None")
		self.emu_list = {}
		self.crd_list = {}
		self.emu_list["None"] = "None"
		self.crd_list["None"] = "None"
		emufilelist = FileList("/usr/script", matchingPattern = "_em.*")
		srvfilelist = FileList("/usr/script", matchingPattern = "_cs.*")
		
		for x in emufilelist.getFileList():
			if x[0][1] != True:
				emuName = t.readEmuName(x[0][0][:-6]) 
				emu.append(emuName)
				self.emu_list[emuName] = x[0][0][:-6]
		softcam = ConfigSelection(default = t.readEmuName(t.readEmuActive()), choices = emu)
		
		for x in srvfilelist.getFileList():
			if x[0][1] != True:
				srvName = t.readSrvName(x[0][0][:-6])
				crd.append(srvName)
				self.crd_list[srvName] = x[0][0][:-6]
		cardserver = ConfigSelection(default = t.readSrvName(t.readSrvActive()), choices = crd)
		
		del self.list[:]
		self.list.append(getConfigListEntry(_('SoftCam (%s) :') % str(len(emu)-1), softcam))
		self.list.append(getConfigListEntry(_('CardServer (%s) :') % str(len(crd)-1), cardserver))
		self['config'].list = self.list
		self['config'].l.setList(self.list)
	
	def keyLeft(self):
		self["config"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["config"].handleKey(KEY_RIGHT)
	
	def ok_pressed(self):
		if self["config"].getCurrentIndex() == 0:
			self.newemu = self.emu_list[self["config"].getCurrent()[1].getText()]
			self.ss_sc()
		else:
			self.newsrv = self.crd_list[self["config"].getCurrent()[1].getText()]
			self.ss_srv()
	
	def keyNumberGlobal(self, number):
		if number == 1:
			if config.proxy.isactive.value:
				system("/var/etc/proxy.sh")
			cmd = "wget " + t.readAddonsUrl() + "info.txt -O /tmp/info.txt"
			self.session.openWithCallback(self.executedScript, dbpConsole, cmd, _('Downloading DB-PROJECT info...'))
		elif number == 2:
			self.session.open(ParentalControlSetup)
		elif number == 3:
			self.message = "EDG-Nemesis Version " +  self.DBVER + "\nBased on cvs from " +  self.CVSDATE + " (Fixed by Gianathem)\n(c) " + self.DBVERDATE + " by EDG-Nemesis Group\n\nhttp://www.edg-nemesis.tv/"
			self.mbox = self.session.open(MessageBox, self.message, MessageBox.TYPE_INFO)
			self.mbox.setTitle("About DB " + self.DBVER)
	
	def executedScript(self, *answer):
		self.session.open(dbpShowPanel, "/tmp/info.txt" ,_('DB Info'))
		
	def naddons(self):
		self.session.openWithCallback(self.loadEmuList, NAddons)
	
	def nsetting(self):
		self.session.openWithCallback(self.loadEmuList, NSetupSummary)
		
	def ninfo(self):
		self.session.openWithCallback(self.loadEmuList, NInfo)
		
	def nutility(self):
		self.session.openWithCallback(self.loadEmuList, NUtility)
	
	def readEcmInfo(self):
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if info is not None:
			if info.getInfo(iServiceInformation.sIsCrypted):
				self["ecmtext"].setText(t.readEcmInfo())
			else:
				self["ecmtext"].setText("Free To Air")
		else:
			self["ecmtext"].setText("")
	
	def ss_sc(self):
		self.emuactive = t.readEmuActive()
		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		if self.emuactive != "None" and self.newemu != "None" and self.emuactive != self.newemu:
			self.mbox = self.session.open(MessageBox, _("Stopping %s and starting %s.") % (t.readEmuName(self.emuactive), t.readEmuName(self.newemu)), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.restart_emu)
			self.activityTimer.start(250, False)
			return
		if self.emuactive != "None" and self.newemu != "None" and self.emuactive == self.newemu:
			self.mbox = self.session.open(MessageBox, _("Restarting %s.") % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.restart_emu)
			self.activityTimer.start(250, False)
			return
		if self.emuactive != "None":
			self.mbox = self.session.open(MessageBox, _("Stopping %s.") % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.stop_emu)
			self.activityTimer.start(250, False)
			return
		if self.newemu != "None":
			self.session.nav.stopService()
			self.mbox = self.session.open(MessageBox, _("Starting %s.") % t.readEmuName(self.newemu), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.start_emu)
			self.activityTimer.start(250, False)
		
	def restart_emu(self):
		self.activityTimer.stop()
		tool.sendCmd('/var/script/' + self.emuactive + '_em.sh stop')
		self.session.nav.stopService()
		tool.sendCmd('/var/script/' + self.newemu + '_em.sh start')
		os.system ( "echo " + self.newemu + " > /var/bin/emuactive" )
		self.session.nav.playService(self.oldref)
		self.mbox.close()
		self.close()
	
	def stop_emu(self):
		self.activityTimer.stop()
		tool.sendCmd('/var/script/' + self.emuactive + '_em.sh stop')
		os.system ( "rm -f /var/bin/emuactive" )
		self.mbox.close()
	
	def start_emu(self):
		self.activityTimer.stop()
		self.session.nav.stopService()
		tool.sendCmd('/var/script/' + self.newemu + '_em.sh start')
		os.system ( "echo " + self.newemu + " > /var/bin/emuactive" )
		self.session.nav.playService(self.oldref)
		self.mbox.close()
		self.close()
	
	def ss_srv(self):
		self.serveractive = t.readSrvActive()
		if self.serveractive == "None" and self.newsrv == "None":
			return
		self.emuactive = t.readEmuActive()
		if self.emuactive != "None" and self.serveractive == "None":
			msg = _("Please stop %s\nbefore start cardserver!") % t.readEmuName(self.emuactive)
			self.box = self.session.open( MessageBox, msg , MessageBox.TYPE_INFO)
			self.box.setTitle(_("Start Cardserver"))
			return	
		if self.serveractive != "None" and self.newsrv != "None" and self.serveractive == self.newsrv:
			self.mbox = self.session.open(MessageBox, _("Restarting %s.") % t.readSrvName(self.serveractive), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.restart_cs)
			self.activityTimer.start(250, False)
			return
		if self.serveractive != "None" and self.newsrv != "None" and self.serveractive != self.newsrv:
			self.mbox = self.session.open(MessageBox, _("Stopping %s and starting %s.") % (t.readSrvName(self.serveractive), t.readSrvName(self.newsrv)), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.restart_cs)
			self.activityTimer.start(250, False)
			return
		if self.serveractive != "None":
			self.mbox = self.session.open(MessageBox, _("Stopping %s.") % t.readSrvName(self.serveractive), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.stop_cs)
			self.activityTimer.start(250, False)
			return
		if self.newsrv != "None":
			self.mbox = self.session.open(MessageBox, _("Starting  %s.") % t.readSrvName(self.newsrv), MessageBox.TYPE_INFO)
			self.mbox.setTitle(_("Running.."))
			self.activityTimer.timeout.get().append(self.start_cs)
			self.activityTimer.start(250, False)
	
	def restart_cs(self):
		self.activityTimer.stop()
		tool.sendCmd("/var/script/" + self.serveractive + "_cs.sh stop")
		tool.sendCmd("/var/script/" + self.newsrv + "_cs.sh start")
		os.system ( "echo " + self.newsrv + " > /var/bin/csactive" )
		self.mbox.close()
	
	def stop_cs(self):
		self.activityTimer.stop()
		tool.sendCmd('/var/script/' + self.serveractive + '_cs.sh stop')
		os.system ( "rm -f /var/bin/csactive" )
		self.mbox.close()
	
	def start_cs(self):
		self.activityTimer.stop()
		tool.sendCmd('/var/script/' + self.newsrv + '_cs.sh start')
		os.system ( "echo " + self.newsrv + " > /var/bin/csactive" )
		self.mbox.close()


class dbpBluePanelOpen():
	__module__ = __name__
	
	def __init__(self):
		self['dbpBluePanelOpen'] = ActionMap(['InfobarExtensions'], {'dbpBpanel': self.dbpBpOpen})
	
	def dbpBpOpen(self):
		self.session.open(dbpBluePanel)

class dbpPluginsPanelOpen():
	__module__ = __name__
	
	def __init__(self):
		self['dbpPluginsPanelOpen'] = ActionMap(['InfobarTimeshiftActions','InfobarAudioSelectionActions'], {'dbpOPlugins': self.dbpPluginsOpen})
	
	def dbpPluginsOpen(self):
		self.session.open(PluginBrowser)
		
