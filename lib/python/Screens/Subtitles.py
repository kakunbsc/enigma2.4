from Screen import Screen
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigNothing
from enigma import iPlayableService

from Tools.ISO639 import LanguageCodes

class Subtitles(Screen, ConfigListScreen):
	def __init__(self, session, infobar=None):
		Screen.__init__(self, session)
        
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.ok,
			"cancel": self.cancel,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.infobar = infobar or self.session.infobar
		self.fillList()

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evUpdatedInfo: self.__updatedInfo
			})
		self.cached_subtitle_checked = False
		self.__selected_subtitle = None

	def fillList(self):
		list = self.list
		del list[:]
		print "self.list", list
		if self.subtitlesEnabled():
			list.append(getConfigListEntry(_("Disable Subtitles"), ConfigNothing(), None))
			sel = self.infobar.selected_subtitle
		else:
			sel = None
		for x in self.getSubtitleList():
			if sel and sel[:4] == x[:4]: #ignore Language code in compare
				text = _("Running")
			else:
				text = _("Enable")
			if x[0] == 0:
				if LanguageCodes.has_key(x[4]):
					list.append(getConfigListEntry(text+" DVB "+LanguageCodes[x[4]][0], ConfigNothing(), x))
				else:
					list.append(getConfigListEntry(text+" DVB "+x[4], ConfigNothing(), x))
			elif x[0] == 1:
				if x[4] == 'und': #undefined
					list.append(getConfigListEntry(text+" TTX "+_("Page")+" %x%02x"%(x[3],x[2]), ConfigNothing(), x))
				else:
					if LanguageCodes.has_key(x[4]):
						list.append(getConfigListEntry(text+" TTX "+_("Page")+" %x%02x"%(x[3],x[2])+" "+LanguageCodes[x[4]][0], ConfigNothing(), x))
					else:
						list.append(getConfigListEntry(text+" TTX "+_("Page")+" %x%02x"%(x[3],x[2])+" "+x[4], ConfigNothing(), x))
			elif x[0] == 2:
				types = (" UTF-8 text "," SSA / AAS "," .SRT file ")
				if x[4] == 'und': #undefined
					list.append(getConfigListEntry(text+types[x[2]]+_("Subtitles")+" %d" % x[1], ConfigNothing(), x))
				else:
					if LanguageCodes.has_key(x[4]):
						list.append(getConfigListEntry(text+types[x[2]]+_("Subtitles") + ' ' + LanguageCodes[x[4]][0], ConfigNothing(), x))
					else:
						list.append(getConfigListEntry(text+types[x[2]]+_("Subtitles")+" %d " % x[1] +x[4], ConfigNothing(), x))
#		return _("Disable subtitles")
		self["config"].list = list
		self["config"].l.setList(list)

	def __updatedInfo(self):
		self.fillList()

	def getSubtitleList(self):
		s = self.infobar and self.infobar.getCurrentServiceSubtitle()
		l = s and s.getSubtitleList() or [ ]
		return l

	def subtitlesEnabled(self):
		return self.infobar.subtitles_enabled

	def enableSubtitle(self, subtitles):
		if self.infobar.selected_subtitle != subtitles:
			self.infobar.subtitles_enabled = False
			self.infobar.selected_subtitle = subtitles
			if subtitles:
				self.infobar.subtitles_enabled = True

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def ok(self):
		if self.list:
			cur = self["config"].getCurrent()
			self.enableSubtitle(cur[2])
		self.close(1)

	def cancel(self):
		self.close()
