from enigma import eConsoleAppContainer, eTimer
from Tools.BoundFunction import boundFunction
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.config import config

class dbpConsole(Screen):
	skin = """
		<screen position="340,200" size="600,350" >
			<widget name="text" position="20,20" size="560,270" font="Regular;18"/>
			<eLabel position="0,309" size="600,2" backgroundColor="grey" zPosition="5"/>
			<widget name="canceltext" position="0,310" zPosition="1" size="600,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />
			<widget name="oktext" position="0,310" zPosition="1" size="600,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />
		</screen>"""
		
	EVENT_DONE = 10
	EVENT_KILLED = 5
	EVENT_CURR = 0
	
	def __init__(self, session, cmd, Wtitle, large = False):
		Screen.__init__(self, session)
		lang = config.osd.language.getText()
		self.cmd = cmd
		self.Wtitle = Wtitle
		self.callbackList = []
		if large:
			self.skinName = ["dbpConsole", "dbpConsoleL" ]
		self["text"] = ScrollLabel("")
		self["oktext"] = Label(_("OK"))
		self["canceltext"] = Label(_("Cancel"))
		self["actions"] = ActionMap(["WizardActions", "DirectionActions",'ColorActions'], 
		{
			"ok": self.cancel,
			"back": self.cancel,
			"up": self["text"].pageUp,
			"down": self["text"].pageDown,
			"red": self.stop,
			"green": self.cancel
		}, -1)
		self["oktext"].hide()
		self.autoCloseTimer = eTimer()
		self.autoCloseTimer.timeout.get().append(self.cancel)
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(self.Wtitle)
	
	def startRun(self):
		print "Console: executing in run the command:", self.cmd
		if self.container.execute(self.cmd):
			self.runFinished(-1)

	def runFinished(self, retval):
		self.EVENT_CURR = self.EVENT_DONE
		self["text"].setText(self["text"].getText() + _('Done') + '\n')
		self["text"].setText(self["text"].getText() + _('Please Press OK Button to close windows!') + '\n')
		self["oktext"].show()
		self["canceltext"].hide()
		if config.dbp.autocloseconsole.value:
			if int(config.dbp.autocloseconsoledelay.value) != 0:
				self.autoCloseTimer.startLongTimer(int(config.dbp.autocloseconsoledelay.value))
			else:
				self.cancel()
	
	def stop(self):
		if self.isRunning():
			self.EVENT_CURR = self.EVENT_KILLED
			self["text"].setText(self["text"].getText() + _('Action killed by user') + '\n')
			self.container.kill()
			self["oktext"].show()
			self["canceltext"].hide()
			if config.dbp.autocloseconsole.value:
				if int(config.dbp.autocloseconsoledelay.value) != 0:
					self.autoCloseTimer.startLongTimer(int(config.dbp.autocloseconsoledelay.value))
				else:
					self.cancel()
	
	def cancel(self):
		if not self.isRunning():
			if self.autoCloseTimer.isActive():
				self.autoCloseTimer.stop()
			del self.autoCloseTimer
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)
			del self.container.dataAvail[:]
			del self.container.appClosed[:]
			del self.container
			self.close(self.EVENT_CURR)

	def dataAvail(self, str):
		self["text"].setText(self["text"].getText() + str)

	def isRunning(self):
		return self.container.running()
