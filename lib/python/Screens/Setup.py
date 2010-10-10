from Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.config import config, ConfigNothing
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap

import xml.etree.cElementTree

# FIXME: use resolveFile!
# read the setupmenu
try:
	# first we search in the current path
	setupfile = file('data/setup.xml', 'r')
except:
	# if not found in the current path, we use the global datadir-path
	setupfile = file('/usr/share/enigma2/setup.xml', 'r')
setupdom = xml.etree.cElementTree.parse(setupfile)
setupfile.close()

class SetupError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return self.msg

class SetupSummary(Screen):
	skin = """
	<screen position="6,0" size="120,64">
		<widget name="SetupTitle" position="6,0" size="120,16" font="Regular;12" />
		<widget name="SetupEntry" position="6,16" size="120,32" font="Regular;12" />
		<widget name="SetupValue" position="6,48" size="120,16" font="Regular;12" />
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["SetupTitle"] = Label(_(parent.setup_title))
		self["SetupEntry"] = Label("")
		self["SetupValue"] = Label("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)
		
	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()
	
	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)
		self.parent["config"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["SetupEntry"].text = self.parent.getCurrentEntry()
		self["SetupValue"].text = self.parent.getCurrentValue()

class Setup(ConfigListScreen, Screen):

	ALLOW_SUSPEND = True

	def removeNotifier(self):
		config.usage.setup_level.notifiers.remove(self.levelChanged)

	def levelChanged(self, configElement):
		list = []
		self.refill(list)
		self["config"].setList(list)

	def refill(self, list):
		xmldata = setupdom.getroot()
		for x in xmldata.findall("setup"):
			if x.get("key") != self.setup:
				continue
			self.addItems(list, x);
			self.setup_title = x.get("title", "").encode("UTF-8")

	def __init__(self, session, setup):
		Screen.__init__(self, session)

		# for the skin: first try a setup_<setupID>, then Setup
		self.skinName = ["setup_" + setup, "Setup" ]

		self.onChangedEntry = [ ]

		self.setup = setup
		list = []
		self.refill(list)

		#check for list.entries > 0 else self.close
		self["title"] = Label(_(self.setup_title))

		self["oktext"] = Label(_("OK"))
		self["canceltext"] = Label(_("Cancel"))
		self["ok"] = Pixmap()
		self["cancel"] = Pixmap()
		
		self["actions"] = NumberActionMap(["SetupActions"], 
			{
				"cancel": self.keyCancel,
				"save": self.keySave,
			}, -2)

		ConfigListScreen.__init__(self, list, session = session, on_change = self.changedEntry)

		self.changedEntry()

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		return SetupSummary

	def addItems(self, list, parentNode):
		for x in parentNode:
			if x.tag == 'item':
				item_level = int(x.get("level", 0))

				if not self.levelChanged in config.usage.setup_level.notifiers:
					config.usage.setup_level.notifiers.append(self.levelChanged)
					self.onClose.append(self.removeNotifier)

				if item_level > config.usage.setup_level.index:
					continue

				requires = x.get("requires")
				if requires and not SystemInfo.get(requires, False):
					continue;

				item_text = _(x.get("text", "??").encode("UTF-8"))
				b = eval(x.text or "");
				if b == "":
					continue
				#add to configlist
				item = b
				# the first b is the item itself, ignored by the configList.
				# the second one is converted to string.
				if not isinstance(item, ConfigNothing):
					list.append( (item_text, item) )

def getSetupTitle(id):
	xmldata = setupdom.getroot()
	for x in xmldata.findall("setup"):
		if x.get("key") == id:
			return x.get("title", "").encode("UTF-8")
	raise SetupError("unknown setup id '%s'!" % repr(id))
