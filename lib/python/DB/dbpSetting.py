from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap, ActionMap
from Components.config import config, ConfigNothing, ConfigFile
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from dbpTool import ListboxE1, GetSkinPath, createProxy, createInadynConf, createIpupdateConf
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer
#import os
import xml.etree.cElementTree

setupfile = file('/usr/share/enigma2/dbp.xml', 'r')
setupdom = xml.etree.cElementTree.parse(setupfile)
setupfile.close()
configfile = ConfigFile()

class NSetupSummary(Screen):
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self["title"] = Label(_("System Settings"))
		self["key_red"] = Label(_("Exit"))
		self['conn'] = Label("")
		self['conn'].hide()
		skin_path = GetSkinPath()
		xmldata = setupdom.getroot()
		for x in xmldata.findall("setup"):
			res = [x.get("key")]
			res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=_(x.get("title", "").encode("UTF-8"))))
			png = LoadPixmap(skin_path + 'icons/setup.png')
			res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=png))
			self.list.append(res)
		self['list'] = ListboxE1(self.list)
		self["actions"] = ActionMap(['WizardActions','ColorActions'],
		{
			"ok": self.okbuttonClick,
			"red": self.close,
			'back': self.close
		})
		self.activityTimer = eTimer()
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("System Settings"))

	def okbuttonClick(self):
		self.indice = self["list"].getCurrent()[0]
		self.session.openWithCallback(self.saveConfig, NSetup, self.indice)
	
	def saveConfig(self, *ret):
		if ret:
			self['conn'].show()
			self['conn'].setText(_('Saving Setting.\nPlease wait...'))
			self.activityTimer.timeout.get().append(self.saveConf(ret[0]))
			self.activityTimer.start(100, False)
		
	def saveConf(self, ret):
		self.activityTimer.stop()
		if ret == "proxy":
			createProxy()
		elif ret == "inadyn":
			createInadynConf()
		elif ret == "ipupdate":
			createIpupdateConf()
		configfile.save()
		self['conn'].hide()

class NSetup(ConfigListScreen, Screen):

	ALLOW_SUSPEND = True
	
	skin = """
		<screen name="NSetup" position="330,130" size="620,500">
			<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="config" position="10,10" size="590,440" scrollbarMode="showOnDemand" />
			<eLabel position="0,459" size="620,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="10,460" zPosition="1" size="300,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="310,460" zPosition="1" size="300,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""
	

	def refill(self, list):
		xmldata = setupdom.getroot()
		for x in xmldata.findall("setup"):
			if x.get("key") != self.setup:
				continue
			self.addItems(list, x);
			self.setup_title = x.get("title", "").encode("UTF-8")

	def __init__(self, session, setup):
		Screen.__init__(self, session)

		self.onChangedEntry = [ ]

		self.setup_title = ""
		self.setup = setup
		list = []
		self.refill(list)
		self["oktext"] = Label(_("OK"))
		self["canceltext"] = Label(_("Exit"))
		
		self["actions"] = NumberActionMap(["SetupActions"], 
			{
				"cancel": self.keyCancel,
				"save": self.okPress,
			}, -2)

		ConfigListScreen.__init__(self, list, session = session, on_change = self.changedEntry)

		self.changedEntry()
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_(self.setup_title))
	
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	
	def addItems(self, list, parentNode):
		for x in parentNode:
			if x.tag == 'item':
				item_level = int(x.get("level", 0))
				item_text = _(x.get("text", "??").encode("UTF-8"))
				b = eval(x.text or "");
				if b == "":
					continue
				item = b
				if not isinstance(item, ConfigNothing):
					list.append( (item_text, item) )
	
	def okPress(self):
		self.saveAll()
		self.close(self.setup)
