from Screen import Screen

from enigma import eConsoleAppContainer

from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap

from time import time

class PluginBrowser(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["red"] = Label(_("Remove Plugins"))
		self["green"] = Label(_("Download Plugins"))
		
		self.list = []
		self["list"] = PluginList(self.list)
		self.updateList()
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.save,
			"back": self.close,
			"red": self.delete,
			"green": self.download
		})
		self.onExecBegin.append(self.checkWarnings)
	
	def checkWarnings(self):
		if len(plugins.warnings):
			text = _("Some plugins are not available:\n")
			for (pluginname, error) in plugins.warnings:
				text += _("%s (%s)\n") % (pluginname, error)
			plugins.resetWarnings()
			self.session.open(MessageBox, text = text, type = MessageBox.TYPE_WARNING)

	def save(self):
		#self.close()
		self.run()
	
	def run(self):
		plugin = self["list"].l.getCurrentSelection()[0]
		
		plugin(session=self.session)
		
	def updateList(self):
		self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		self.list = [PluginEntryComponent(plugin) for plugin in self.pluginlist]

		self["list"].l.setList(self.list)

	def delete(self):
		self.session.openWithCallback(self.updateList, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE)
	
	def download(self):
		self.session.openWithCallback(self.updateList, PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD)

class PluginDownloadBrowser(Screen):
	DOWNLOAD = 0
	REMOVE = 1
	lastDownloadDate = None

	def __init__(self, session, type):
		Screen.__init__(self, session)
		
		self.type = type
		
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
		
		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		
		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		elif self.type == self.REMOVE:
			self["text"] = Label(_("Getting plugin information. Please wait..."))
		
		self.run = 0

		self.remainingdata = ""

		self["actions"] = ActionMap(["WizardActions"], 
		{
			"ok": self.go,
			"back": self.close,
		})
		
	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		sel = sel[0]
		if isinstance(sel, str): # category
			if sel in self.expanded:
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
		else:
			if self.type == self.DOWNLOAD:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to download\nthe plugin \"%s\"?") % sel.name)
			elif self.type == self.REMOVE:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to REMOVE\nthe plugin \"%s\"?") % sel.name)

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				self.session.openWithCallback(self.installFinished, Console, cmdlist = ["ipkg install " + "enigma2-plugin-" + self["list"].l.getCurrentSelection()[0].name])
			elif self.type == self.REMOVE:
				self.session.openWithCallback(self.installFinished, Console, cmdlist = ["ipkg remove " + "enigma2-plugin-" + self["list"].l.getCurrentSelection()[0].name])

	def setWindowTitle(self):
		if self.type == self.DOWNLOAD:
			self.setTitle(_("Downloadable new plugins"))
		elif self.type == self.REMOVE:
			self.setTitle(_("Remove plugins"))

	def startIpkgListInstalled(self):
		self.container.execute("ipkg list_installed enigma2-plugin-*")

	def startRun(self):
		self["list"].instance.hide()
		if self.type == self.DOWNLOAD:
			if not PluginDownloadBrowser.lastDownloadDate or (time() - PluginDownloadBrowser.lastDownloadDate) > 3600:
				# Only update from internet once per hour
				self.container.execute("ipkg update")
				PluginDownloadBrowser.lastDownloadDate = time()
			else:
				self.startIpkgListInstalled()
		elif self.type == self.REMOVE:
			self.run = 1
			self.startIpkgListInstalled()

	def installFinished(self):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.container.appClosed.remove(self.runFinished)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def runFinished(self, retval):
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			if self.type == self.DOWNLOAD:
				self.startIpkgListInstalled()
		elif self.run == 1 and self.type == self.DOWNLOAD:
			self.run = 2
			self.container.execute("ipkg list enigma2-plugin-*")
		else:
			if len(self.pluginlist) > 0:
				self.updateList()
				self["list"].instance.show()
			else:
				self["text"].setText("No new plugins found")

	def dataAvail(self, str):
		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		lines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			#remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""

		for x in lines:
			plugin = x.split(" - ")
			if len(plugin) == 3:
				if self.run == 1 and self.type == self.DOWNLOAD:
					self.installedplugins.append(plugin[0])
				else:
					if plugin[0] not in self.installedplugins:
						plugin.append(plugin[0][15:])

						self.pluginlist.append(plugin)
	
	def updateList(self):
		list = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/verticalline-plugins.png"))
		
		self.plugins = {}
		for x in self.pluginlist:
			split = x[3].split('-', 1)
			if len(split) < 2:
				continue
			if not self.plugins.has_key(split[0]):
				self.plugins[split[0]] = []
				
			self.plugins[split[0]].append((PluginDescriptor(name = x[3], description = x[2], icon = verticallineIcon), split[1]))
			
		for x in self.plugins.keys():
			if x in self.expanded:
				list.append(PluginCategoryComponent(x, expandedIcon))
				list.extend([PluginDownloadComponent(plugin[0], plugin[1]) for plugin in self.plugins[x]])
			else:
				list.append(PluginCategoryComponent(x, expandableIcon))
		self.list = list
		self["list"].l.setList(list)

