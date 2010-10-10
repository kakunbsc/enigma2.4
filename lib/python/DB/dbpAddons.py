from Screens.Screen import Screen
from enigma import eTimer, eDVBDB, eConsoleAppContainer
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config
from Components.PluginComponent import plugins
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from os import system, remove as os_remove, listdir, chdir, getcwd
from dbpTool import dbpTool, ListboxE1, GetSkinPath , ListboxE3
from dbpConsole import dbpConsole
from Tools import Notifications
import xml.etree.cElementTree as x

t = dbpTool()

class util:
	pluginIndex = -1
	pluginType = ''
	typeDownload = 'A'
	addonsName = ''
	filename = ''
	dir = ''
	size = -1
	check = 0
	
	def removeSetting(self):
		print "Remove settings"
		#system("rm -f /etc/tuxbox/satellites.xml")
		system("rm -f /etc/enigma2/bouque*")
		system("rm -f /etc/enigma2/service*")
		system("rm -f /etc/enigma2/lamedb")
		system("rm -f /etc/enigma2/blacklist")
		system("rm -f /etc/enigma2/userbouq*")
	
	def reloadSetting(self):
		print "Reload settings"
		self.eDVBDB = eDVBDB.getInstance()
		self.eDVBDB.reloadServicelist()
		self.eDVBDB.reloadBouquets()

u = util()

class loadXml:
	
	tree_list = []
	plugin_list = []
	
	def load(self,filename):
		del self.tree_list[:]
		del self.plugin_list[:]
		tree = x.parse(filename)
		root = tree.getroot()
		c = 0
		for tag in root.getchildren(): 
			self.tree_list.append([c, tag.tag])
			c1 = 0
			for b in tree.find(tag.tag):
				self.plugin_list.append([c,tag.tag,b.find("filename").text,b.find("desc").text,b.find("dir").text,b.find("size").text,b.find("check").text,c1])
				c1 +=1
			c +=1

loadxml = loadXml()

class loadTmpDir:
	
	tmp_list = []
	
	def load(self):
		del self.tmp_list[:]
		pkgs = listdir('/tmp')
		count = 0
		for fil in pkgs:
			if (fil.find('.ipk') != -1 or fil.find('.tbz2') != -1):
				self.tmp_list.append([count,fil])
				count +=1

loadtmpdir = loadTmpDir()

class loadUniDir:
	
	uni_list = []
	
	def load(self):
		del self.uni_list[:]
		pkgs = listdir('/usr/uninstall')
		count = 0
		for fil in pkgs:
			if (fil.find('_remove.sh') != -1 or fil.find('_delete.sh') != -1):
				self.uni_list.append([count,fil])
				count +=1

loadunidir = loadUniDir()

class NAddons(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430" title="Addons">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self["title"] = Label(_("Addons Manager"))
		self['list'] = ListboxE1(self.list)
		self['conn'] = Label("")
		self["key_red"] = Label(_("Cancel"))
		self['conn'].hide()
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.cancel,
			'back': self.cancel
		})
		self.onLayoutFinish.append(self.updateList)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Addons Manager"))

	def KeyOk(self):
		if not self.container.running():
			self['conn'].setText(_("Connetting to addons server.\nPlease wait..."))
			self.sel = self["list"].getCurrent()[0]
			if (self.sel == "NAddons"):
				self['conn'].show()
				self.container.execute({True:'/var/etc/proxy.sh && ',False:''}[config.proxy.isactive.value] + "wget " + t.readAddonsUrl() + "/addons800.xml -O /tmp/addons.xml")
			elif (self.sel == "NExtra"):
				self['conn'].show()
				self.container.execute({True:'/var/etc/proxy.sh && ',False:''}[config.proxy.isactive.value] + "wget " + t.readExtraUrl() + "e2extra.xml -O /tmp/addons.xml")
			elif (self.sel == "NManual"):
				self.session.open(RManual)
			elif (self.sel == "NRemove"):
				self.session.open(RRemove)

	def runFinished(self, retval):
		if fileExists('/tmp/addons.xml'):
			try:
				loadxml.load('/tmp/addons.xml')
				system('rm -f /tmp/addons.xml')
				self['conn'].hide()
				self.session.open(RAddons,{"NAddons": _('Download Addons'),"NExtra": _('Download Extra')}[self.sel],{'NAddons': 'A','NExtra': 'E'}[self.sel])
			except:
				self['conn'].setText(_("File xml is not correctly formatted!."))
		else:
			self['conn'].setText(_("Server not found!\nPlease check internet connection."))
	
	def cancel(self):
		if not self.container.running():
			del self.container.appClosed[:]
			del self.container
			self.close()
		else:
			self.container.kill()
			system('rm -f /tmp/addons.xml')
			self['conn'].setText(_('Process Killed by user\nServer Not Connected!'))
	
	def updateList(self):
		del self.list[:]
		skin_path = GetSkinPath()
		res = ['NAddons']
		res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=_("Download Addons")))
		png = LoadPixmap(skin_path + 'icons/network.png')
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=png))
		self.list.append(res)
		if fileExists('/etc/extra.url'):
			res = ['NExtra']
			res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=_("Download Extra")))
			png = LoadPixmap(skin_path + 'icons/network.png')
			res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=png))
			self.list.append(res)
		res = ['NManual']
		res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=_("Manual Package Install")))
		png = LoadPixmap(skin_path + 'icons/manual.png')
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=png))
		self.list.append(res)
		res = ['NRemove']
		res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=_("Remove Addons")))
		png = LoadPixmap(skin_path + 'icons/remove.png')
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=png))
		self.list.append(res)
		
		self['list'].l.setList(self.list)

class	RAddons(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session, wtitle, typeDownload):
		Screen.__init__(self, session)
		self.wtitle = wtitle
		u.typeDownload = typeDownload
		self.list = []
		self['list'] = ListboxE1(self.list)
		self["title"] = Label(self.wtitle)
		self['conn'] = Label("")
		self["key_red"] = Label(_("Cancel"))
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.close,
			'back': self.close
		})
		self.onLayoutFinish.append(self.loadData)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(self.wtitle)

	def KeyOk(self):
		u.pluginIndex = self['list'].getSelectionIndex() 
		self.session.open(RAddonsDown)
	
	def loadData(self):
		del self.list[:]
		for tag in loadxml.tree_list: 
			res = [tag [0]]
			res.append(MultiContentEntryText(pos=(0, 5), size=(340, 32), font=0, text=tag [1] ))
			self.list.append(res)
		self['list'].l.setList(self.list)

class	RAddonsDown(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,530" title="Download">
			<widget name="type" position="0,0" size="560,35" font="Regular;26" valign="center" halign="center" backgroundColor="#0064c7"/>
			<widget name="list" position="10,40" size="540,420" scrollbarMode="showOnDemand" />
			<widget name="conn" position="0,460" size="560,50" font="Regular;20" halign="center" valign="center" backgroundColor="#0064c7" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = ListboxE3(self.list)
		self['conn'] = Label(_("Loading elements.\nPlease wait..."))
		self['type'] = Label("")
		self["key_red"] = Label(_("Cancel"))
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		for tag in loadxml.tree_list: 
			if tag [0] == u.pluginIndex:
				u.pluginType = tag [1]
				self['type'].setText(_("Download ") + u.pluginType)

		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.cancel,
			'back': self.cancel
		})
		self.onLayoutFinish.append(self.loadPlugin)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Download ") + u.pluginType)
	
	def KeyOk(self):
		if not self.container.running():
			self['conn'].hide()
			self.sel = self['list'].getSelectionIndex() 
			if (u.size > t.getVarSpace() and u.check == 1):
				msg = _('Not enough space!\nPlease delete addons before install new.')
				self.session.open(MessageBox, msg , MessageBox.TYPE_INFO)
				return
			for tag in loadxml.plugin_list: 
				if tag [0] == u.pluginIndex:
					if tag [7] == self.sel:
						u.addonsName = tag [3]
						self.downloadAddons()
						return
			self.close()
			
	def loadPlugin(self):
		del self.list[:]
		for tag in loadxml.plugin_list: 
			if tag [0] == u.pluginIndex:
				res = [tag [3]]
				res.append(MultiContentEntryText(pos=(0, 5), size=(340, 30), font=0, text=tag [3] ))
				self.list.append(res)
		self['list'].l.setList(self.list)
		self['conn'].hide()

	def downloadAddons(self):
		self.getAddonsPar()
		url = {'E':t.readExtraUrl(),'A':t.readAddonsUrl()}[u.typeDownload]
		cmd = {True:'/var/etc/proxy.sh && ',False:''}[config.proxy.isactive.value]
		cmd += "wget " + url +  u.dir + "/" + u.filename + " -O /tmp/" + u.filename
		self.session.openWithCallback(self.executedScript, dbpConsole, cmd, _('Download: ') + u.filename)
		
	def executedScript(self, *answer):
		if answer[0] == dbpConsole.EVENT_DONE:
			if fileExists('/tmp/' + u.filename):
				msg = 'Do you want install the addon:\n' + u.addonsName + '?'
				box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
				box.setTitle(_('Install Addon'))
			else:
				msg = _('Addons: %s not found!\nPLease check your internet connection') % u.filename
				self.session.open(MessageBox, msg , MessageBox.TYPE_INFO)
	
	def installAddons(self, answer):
		if (answer is True):
			self['conn'].setText(_('Installing addons.\nPlease Wait...'))
			self['conn'].show()
			if (u.filename.find('.ipk') != -1):
				self.container.execute("ipkg install /tmp/" + u.filename)
			elif (u.filename.find('.tbz2') != -1):
				if (u.pluginType == 'Settings') or (u.pluginType == 'e2Settings'):
					u.removeSetting()	
				self.container.execute("tar -jxvf /tmp/" + u.filename + " -C /")
			else:
				self['conn'].setText(_('File: %s\nis not a valid package!') % u.filename)
		else:
			system("rm -f /tmp/" + u.filename)
	
	def runFinished(self, retval):
		system("rm -f /tmp/" + u.filename)
		if (u.pluginType == 'Settings') or (u.pluginType == 'e2Settings'):
			u.reloadSetting()
		elif (u.pluginType == 'Plugins') or (u.pluginType == 'e2Plugins'):
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self['conn'].setText(_("Addon installed succesfully!"))
		if fileExists('/tmp/.restartE2'):
			system('rm -f /tmp/.restartE2')
			msg = _('Enigma2 will be now hard restarted to complete package installation.\nDo You want restart enigma2 now?')
			box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg , MessageBox.TYPE_YESNO)
			box.setTitle(_('Restart Enigma2'))
	
	def cancel(self):
		if not self.container.running():
			del self.container.appClosed[:]
			del self.container
			self.close()
		else:
			self.container.kill()
			self['conn'].setText(_('Process Killed by user.\nAddon not installed correctly!'))
	
	def restartEnigma2(self, answer):
		if (answer is True):
			system('killall -9 enigma2')
	
	def getAddonsPar(self):
		for tag in loadxml.plugin_list: 
			if tag [0] == u.pluginIndex:
				if tag [3] == u.addonsName:
					u.filename  = tag [2] 
					u.dir  = tag [4] 
					u.size  = tag [5] 
					u.check  = tag [6] 

class	RManual(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />
			<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = ListboxE1(self.list)
		self['conn'] = Label("")
		self["title"] = Label(_("Manual Installation"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Reload /tmp"))
		self['conn'].hide()
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"yellow": self.readTmp,
			"red": self.cancel,
			'back': self.cancel
		})
		self.onLayoutFinish.append(self.readTmp)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Manual Installation"))
	
	def readTmp(self):
		del self.list[:]
		loadtmpdir.load()
		if len(loadtmpdir.tmp_list) > 0:
			for fil in loadtmpdir.tmp_list: 
				res = [fil]
				res.append(MultiContentEntryText(pos=(0, 5), size=(340, 32), font=0, text=fil[1]))
				self.list.append(res)
		else:	
			self['conn'].show()
			self['conn'].setText(_("Put your plugin xxx.tbz2 or xxx.ipk\nvia FTP in /tmp."))
		self['list'].l.setList(self.list)
	
	def KeyOk(self):
		if not self.container.running():
			if len(loadtmpdir.tmp_list) > 0:
				self.sel = self['list'].getSelectionIndex() 
				for p in loadtmpdir.tmp_list: 
					if (p [0] == self.sel):
						u.filename = p [1]
				msg = _('Do you want install the addon:\n%s?') % u.filename
				box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
				box.setTitle(_('Install Addon'))
			else:
				self.close()
	
	def installAddons(self, answer):
		if (answer is True):
			self['conn'].show()
			self['conn'].setText(_('Installing: %s.\nPlease wait...') % u.filename)
			if (u.filename.find('.ipk') != -1):
				self.container.execute("ipkg install /tmp/" + u.filename)
			elif (u.filename.find('.tbz2') != -1):
				self.container.execute("tar -jxvf /tmp/" + u.filename + " -C /")
			else:
				self['conn'].setText(_('File: %s\nis not a valid package!') % u.filename)
	
	def runFinished(self, retval):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		system("rm -f /tmp/" + u.filename);
		self['conn'].setText(_("Addon: %s\ninstalled succesfully!") % u.filename)
		self.readTmp()
		if fileExists('/tmp/.restartE2'):
			system('rm -f /tmp/.restartE2')
			msg = 'Enigma2 will be now hard restarted to complete package installation.\nDo You want restart enigma2 now?'
			box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg , MessageBox.TYPE_YESNO)
			box.setTitle('Restart enigma')
	
	def cancel(self):
		if not self.container.running():
			del self.container.appClosed[:]
			del self.container
			self.close()
		else:
			self.container.kill()
			self['conn'].setText(_('Process Killed by user.\nAddon not installed correctly!'))
	
	def restartEnigma2(self, answer):
		if (answer is True):
			system('killall -9 enigma2')

class	RRemove(Screen):
	__module__ = __name__
	skin = """
		<screen position="80,95" size="560,430" title="Addons">
			<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>
			<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />
			<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />
			<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = ListboxE1(self.list)
		self['conn'] = Label("")
		self["title"] = Label(_("Remove Addons"))
		self["key_red"] = Label(_("Cancel"))
		self['conn'].hide()
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			"red": self.cancel,
			'back': self.cancel
		})
		self.onLayoutFinish.append(self.readTmp)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(_("Remove Addons"))

	def readTmp(self):
		loadunidir.load()
		del self.list[:]
		if len(loadunidir.uni_list) > 0:
			for fil in loadunidir.uni_list: 
				res = [fil]
				res.append(MultiContentEntryText(pos=(0, 5), size=(340, 32), font=0, text=fil [1] [:-10]))
				self.list.append(res)
		else:
			self['conn'].show()
			self['conn'].setText(_("Nothing to uninstall!"))
		self['list'].l.setList(self.list)
	
	def KeyOk(self):
		if not self.container.running():
			if len(loadunidir.uni_list) > 0:
				self.sel = self['list'].getSelectionIndex() 
				for p in loadunidir.uni_list: 
					if (p [0] == self.sel):
						u.filename = p [1]
				msg = _('Do you want remove the addon:\n%s?') % u.filename[:-10]
				box = self.session.openWithCallback(self.removeAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
				box.setTitle('Remove Addon')
			else:
				self.close()
	
	def removeAddons(self, answer):
		if (answer is True):
			self['conn'].show()
			self['conn'].setText(_('Removing: %s.\nPlease wait...') % u.filename[:-10])
			self.container.execute("/usr/uninstall/" + u.filename)
	
	def runFinished(self, retval):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.readTmp()
		self['conn'].setText(_('Addons: %s\nremoved succeffully.') % u.filename[:-10])

	def cancel(self):
		if not self.container.running():
			del self.container.appClosed[:]
			del self.container
			self.close()
		else:
			self.container.kill()
			self['conn'].setText(_('Process Killed by user.\nAddon not removed completly!'))
