from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label

class dbpShowPanel(Screen):
	__module__ = __name__

	def __init__(self, session, file, Wtitle):
		Screen.__init__(self, session)
		
		self.file = file
		self.Wtitle = Wtitle
		self.list = []
		self["close"] = Label(_("Close"))

		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
			'red': self.close,
			'ok': self.openDetails,
			'back': self.close,
			})
		
		self.loadData()
		self["list"] = List(self.list)
		
		self.onShown.append(self.setWindowTitle)
	
	def setWindowTitle(self):
		self.setTitle(self.Wtitle)
	
	def loadData(self):
		try:
			f = open(self.file, 'r')
			for line in f.readlines():
				self.list.append(line)
			f.close()
		except:
			mess = _('File: %s not found!') % self.file
			self.list.append(mess)
	
	def openDetails(self):
		message = self["list"].getCurrent()
		if message:
			mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
			mbox.setTitle(_("Details"))
