import time
#from time import datetime
from Tools import Directories, Notifications, ASCIItranslit

from Components.config import config
import timer
import xml.etree.cElementTree

from enigma import eEPGCache, getBestPlayableServiceReference, \
	eServiceReference, iRecordableService, quitMainloop, eConsoleAppContainer, eTimer

from Screens.MessageBox import MessageBox
from Components.TimerSanityCheck import TimerSanityCheck
import NavigationInstance

import Screens.Standby

from time import localtime

from Tools.XMLTools import stringToXML
from ServiceReference import ServiceReference
import os

# ok, for descriptions etc we have:
# service reference  (to get the service name)
# name               (title)
# description        (description)
# event data         (ONLY for time adjustments etc.)


# parses an event, and gives out a (begin, end, name, duration, eit)-tuple.
# begin and end will be corrected

epg = eEPGCache.getInstance()

from Tools.Directories import fileExists
import string

class timerEpgDownload():
	
	def getSid(self,sid):
		EPG_CHANNEL_INFO_sid="%X" % int(string.split(sid,":")[0],16)
		temp="%X" % int(string.split(sid,":")[1],16)
		EPG_CHANNEL_INFO_tsid="%X" % int(string.split(sid,":")[2],16)
		EPG_CHANNEL_INFO_onid="%X" % int(string.split(sid,":")[3],16)
		return '1:0:1:'+EPG_CHANNEL_INFO_sid+':'+EPG_CHANNEL_INFO_tsid+':'+EPG_CHANNEL_INFO_onid+':'+temp+':0:0:0:'
	
	def writeLog(self,msg):
		os.system("echo `date` '" + msg + "' >> /usr/log/crossepg.log")
		print "[TIMER] " + msg 

	def __init__(self):
		self.STATE_DOWN_IT = False
		self.STATE_DOWN_UK = False
		self.STATE_CONVERTED = False
		self.ref = None
		self.myEpgDownloader = "sleep " + config.nemepg.zapdelay.value + " && /usr/crossepg/download_epg.sh"
		self.myEpgConverter = "sleep " + config.nemepg.zapdelay.value + " && /usr/crossepg/convert_epg.sh"
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
	
	def prepare(self):
		self.writeLog('Prepare EPG environement...')
		self.STATE_DOWN_IT = False
		self.STATE_DOWN_UK = False
		self.STATE_CONVERTED = False
		self.ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
	
	def EpgDownload(self):
		if config.nemepg.downskyit.value and (not self.STATE_DOWN_IT):
			self.writeLog('Start Download EPG for SKY-IT')
			NavigationInstance.instance.playService(eServiceReference(self.getSid(config.nemepg.skyitch.value)))
			self.container.execute(self.myEpgDownloader + ' skyitalia >> /usr/log/crossepg.log')
			self.STATE_DOWN_IT = True
		elif config.nemepg.downskyuk.value and (not self.STATE_DOWN_UK):
			self.writeLog('Start Download EPG for SKY-UK')
			NavigationInstance.instance.playService(eServiceReference(self.getSid(config.nemepg.skyitch.value)))
			self.container.execute(self.myEpgDownloader + ' skyuk  >> /usr/log/crossepg.log')
			self.STATE_DOWN_UK = True
		elif self.STATE_DOWN_UK or self.STATE_DOWN_IT and (not self.STATE_CONVERTED):
			self.writeLog('Start Conversion EPG File')
			NavigationInstance.instance.playService(self.ref)
			if fileExists('/tmp/crossepg.headers.db') and fileExists('/tmp/crossepg.descriptors.db'):
				self.container.execute(self.myEpgConverter + ' >> /usr/log/crossepg.log')
			else:
				self.writeLog('File /tmp/crossepg.descriptors.db or /tmp/crossepg.headers.db not found!')
			self.STATE_CONVERTED = True
		elif self.STATE_CONVERTED:
			if fileExists('/tmp/ext.epg.dat'):
				os.system("rm -f /tmp/crossepg*")
				os.system("mv /tmp/ext.epg.dat " + config.nemepg.path.value + "/epg.dat")
				if config.nemepg.clearcache.value:
					self.writeLog('Clear enigma EPG cache')
					epg.clearEpg()
				self.writeLog('Load EPG in a cache')
				epg.reloadEpg()
				self.writeLog('Save EPG backup')
				epg.saveEpg()
				if fileExists(config.nemepg.path.value + "/epg.dat"):
					os.system("mv " + config.nemepg.path.value + "/epg.dat " + config.nemepg.path.value + "/epg.dat.save")
				self.writeLog('Download EPG finished!')
			else:
				self.writeLog('File /tmp/ext.epg.dat not found!')
		else:
			self.writeLog('Download EPG Nothing to do!')
	
	def runFinished(self,retval):
		self.EpgDownload()
	
	def cancel(self):
		if self.container.running():
			self.container.kill()
			self.writeLog('Download EPG Killed due a timeout!')
		self.writeLog('Close timerEpgDownload Classes!')
		del self.container.appClosed[:]
		del self.container

def parseEvent(ev, description = True):
	if description:
		name = ev.getEventName()
		description = ev.getShortDescription()
	else:
		name = ""
		description = ""
	begin = ev.getBeginTime()
	end = begin + ev.getDuration()
	eit = ev.getEventId()
	begin -= config.recording.margin_before.value * 60
	end += config.recording.margin_after.value * 60
	return (begin, end, name, description, eit)

class AFTEREVENT:
	NONE = 0
	STANDBY = 1
	DEEPSTANDBY = 2
	AUTO = 3

# please do not translate log messages
class RecordTimerEntry(timer.TimerEntry, object):
######### the following static methods and members are only in use when the box is in (soft) standby
	receiveRecordEvents = False

	@staticmethod
	def shutdown():
		quitMainloop(1)

	@staticmethod
	def staticGotRecordEvent(recservice, event):
		if event == iRecordableService.evEnd:
			print "RecordTimer.staticGotRecordEvent(iRecordableService.evEnd)"
			recordings = NavigationInstance.instance.getRecordings()
			if not recordings: # no more recordings exist
				rec_time = NavigationInstance.instance.RecordTimer.getNextRecordingTime()
				if rec_time > 0 and (rec_time - time.time()) < 360:
					print "another recording starts in", rec_time - time.time(), "seconds... do not shutdown yet"
				else:
					print "no starting records in the next 360 seconds... immediate shutdown"
					RecordTimerEntry.shutdown() # immediate shutdown
		elif event == iRecordableService.evStart:
			print "RecordTimer.staticGotRecordEvent(iRecordableService.evStart)"

	@staticmethod
	def stopTryQuitMainloop():
		print "RecordTimer.stopTryQuitMainloop"
		NavigationInstance.instance.record_event.remove(RecordTimerEntry.staticGotRecordEvent)
		RecordTimerEntry.receiveRecordEvents = False

	@staticmethod
	def TryQuitMainloop(default_yes = True):
		if not RecordTimerEntry.receiveRecordEvents:
			print "RecordTimer.TryQuitMainloop"
			NavigationInstance.instance.record_event.append(RecordTimerEntry.staticGotRecordEvent)
			RecordTimerEntry.receiveRecordEvents = True
			# send fake event.. to check if another recordings are running or
			# other timers start in a few seconds
			RecordTimerEntry.staticGotRecordEvent(None, iRecordableService.evEnd)
			# send normal notification for the case the user leave the standby now..
			Notifications.AddNotification(Screens.Standby.TryQuitMainloop, 1, onSessionOpenCallback=RecordTimerEntry.stopTryQuitMainloop, default_yes = default_yes)
#################################################################

	def __init__(self, serviceref, begin, end, name, description, eit, disabled = False, justplay = 0, afterEvent = AFTEREVENT.AUTO, checkOldTimers = False, dirname = None, tags = None):
		timer.TimerEntry.__init__(self, int(begin), int(end))

		if checkOldTimers == True:
			if self.begin < time.time() - 1209600:
				self.begin = int(time.time())
		
		if self.end < self.begin:
			self.end = self.begin
		
		assert isinstance(serviceref, ServiceReference)
		
		self.service_ref = serviceref
		self.eit = eit
		self.dontSave = False
		self.name = name
		self.description = description
		self.disabled = disabled
		self.timer = None
		self.__record_service = None
		self.start_prepare = 0
		self.justplay = justplay
		self.afterEvent = afterEvent
		self.dirname = dirname
		self.dirnameHadToFallback = False
		self.autoincrease = False
		self.autoincreasetime = 3600 * 24 # 1 day
		self.tags = tags or []

		self.log_entries = []
		self.resetState()
	
	def log(self, code, msg):
		self.log_entries.append((int(time.time()), code, msg))
		print "[TIMER]", msg

	def calculateFilename(self):
		service_name = self.service_ref.getServiceName()
		begin_date = time.strftime("%Y%m%d %H%M", time.localtime(self.begin))
		
		print "begin_date: ", begin_date
		print "service_name: ", service_name
		print "name:", self.name
		print "description: ", self.description
		
		filename = begin_date + " - " + service_name
		if self.name:
			filename += " - " + self.name

		if config.recording.ascii_filenames.value:
			filename = ASCIItranslit.legacyEncode(filename)

		if self.dirname and not Directories.fileExists(self.dirname, 'w'):
			self.dirnameHadToFallback = True
			self.Filename = Directories.getRecordingFilename(filename, None)
		else:
			self.Filename = Directories.getRecordingFilename(filename, self.dirname)
		self.log(0, "Filename calculated as: '%s'" % self.Filename)
		#begin_date + " - " + service_name + description)

	def tryPrepare(self):
		if self.justplay == 1:
			return True
		if self.justplay == 2:
			if Screens.Standby.inStandby:
				#Screens.Standby.inStandby.prev_running_service = self.service_ref.ref
				Screens.Standby.inStandby.Power()
			os.system("echo `date` '[TIMER] EPG Initilize....' > /usr/log/crossepg.log")
			self.t = timerEpgDownload()
			return True
		elif self.justplay == 0:
			self.calculateFilename()
			rec_ref = self.service_ref and self.service_ref.ref
			if rec_ref and rec_ref.flags & eServiceReference.isGroup:
				rec_ref = getBestPlayableServiceReference(rec_ref, eServiceReference())
				if not rec_ref:
					self.log(1, "'get best playable service for group... record' failed")
					return False
				
			self.record_service = rec_ref and NavigationInstance.instance.recordService(rec_ref)

			if not self.record_service:
				self.log(1, "'record service' failed")
				return False

			if self.repeated:
				epgcache = eEPGCache.getInstance()
				queryTime=self.begin+(self.end-self.begin)/2
				evt = epgcache.lookupEventTime(rec_ref, queryTime)
				if evt:
					self.description = evt.getShortDescription()
					event_id = evt.getEventId()
				else:
					event_id = -1
			else:
				event_id = self.eit
				if event_id is None:
					event_id = -1

			prep_res=self.record_service.prepare(self.Filename + ".ts", self.begin, self.end, event_id, self.name.replace("\n", ""), self.description.replace("\n", ""), ' '.join(self.tags))
			if prep_res:
				if prep_res == -255:
					self.log(4, "failed to write meta information")
				else:
					self.log(2, "'prepare' failed: error %d" % prep_res)
				NavigationInstance.instance.stopRecordService(self.record_service)
				self.record_service = None
				return False
			return True

	def do_backoff(self):
		if self.backoff == 0:
			self.backoff = 5
		else:
			self.backoff *= 2
			if self.backoff > 100:
				self.backoff = 100
		self.log(10, "backoff: retry in %d seconds" % self.backoff)

	def activate(self):
		next_state = self.state + 1
		if self.justplay != 2:
			self.log(5, "activating state %d" % next_state)
		
		if next_state == self.StatePrepared:
			if self.tryPrepare():
				self.log(6, "prepare ok, waiting for begin")
				# fine. it worked, resources are allocated.
				self.next_activation = self.begin
				self.backoff = 0
				return True

			self.log(7, "prepare failed")
			if self.first_try_prepare:
				self.first_try_prepare = False
				cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				if cur_ref and not cur_ref.getPath():
					if not config.recording.asktozap.value:
						self.log(8, "asking user to zap away")
						Notifications.AddNotificationWithCallback(self.failureCB, MessageBox, _("A timer failed to record!\nDisable TV and try again?\n"), timeout=20)
					else: # zap without asking
						self.log(9, "zap without asking")
						Notifications.AddNotification(MessageBox, _("In order to record a timer, the TV was switched to the recording service!\n"), type=MessageBox.TYPE_INFO, timeout=20)
						self.failureCB(True)
				elif cur_ref:
					self.log(8, "currently running service is not a live service.. so stop it makes no sense")
				else:
					self.log(8, "currently no service running... so we dont need to stop it")

			self.do_backoff()
			# retry
			self.start_prepare = time.time() + self.backoff
			return False
		elif next_state == self.StateRunning:
			# if this timer has been cancelled, just go to "end" state.
			if self.cancelled:
				return True

			if self.justplay == 1:
				if Screens.Standby.inStandby:
					self.log(11, "wakeup and zap")
					#set service to zap after standby
					Screens.Standby.inStandby.prev_running_service = self.service_ref.ref
					#wakeup standby
					Screens.Standby.inStandby.Power()
				else:
					self.log(11, "zapping")
					NavigationInstance.instance.playService(self.service_ref.ref)
				return True
			elif self.justplay == 2:
				os.system("echo '[TIMER] Download EPG Start' >> /usr/log/crossepg.log")
				self.log(11, "Download EPG")
				if config.nemepg.enatimer.value:
					self.t.prepare()
					self.t.EpgDownload()
				return True
			elif self.justplay == 0:
				self.log(11, "start recording")
				cmd = "/bin/touch /tmp/.recording"
				os.system(cmd)
				record_res = self.record_service.start()
				
				if record_res:
					self.log(13, "start record returned %d" % record_res)
					self.do_backoff()
					# retry
					self.begin = time.time() + self.backoff
					return False

				return True
		elif next_state == self.StateEnded:
			old_end = self.end
			if self.setAutoincreaseEnd():
				self.log(12, "autoincrase recording %d minute(s)" % int((self.end - old_end)/60))
				self.state -= 1
				return True
			cmd = "/bin/rm -rf /tmp/.recording"
			os.system(cmd)
			if self.justplay == 0:
				self.log(12, "stop recording")
				NavigationInstance.instance.stopRecordService(self.record_service)
				self.record_service = None
			elif self.justplay == 2:
				self.t.cancel()
				del self.t
				self.log(12, "stop EPG Download")
				os.system("echo `date` '[TIMER] stop EPG Download' >> /usr/log/crossepg.log")
			if self.afterEvent == AFTEREVENT.STANDBY:
				if not Screens.Standby.inStandby: # not already in standby
					Notifications.AddNotificationWithCallback(self.sendStandbyNotification, MessageBox, _("A finished record timer wants to set your\nDreambox to standby. Do that now?"), timeout = 20)
			elif self.afterEvent == AFTEREVENT.DEEPSTANDBY:
				if not Screens.Standby.inTryQuitMainloop: # not a shutdown messagebox is open
					if Screens.Standby.inStandby: # in standby
						RecordTimerEntry.TryQuitMainloop() # start shutdown handling without screen
					else:
						Notifications.AddNotificationWithCallback(self.sendTryQuitMainloopNotification, MessageBox, _("A finished record timer wants to shut down\nyour Dreambox. Shutdown now?"), timeout = 20)
			return True

	def setAutoincreaseEnd(self, entry = None):
		if not self.autoincrease:
			return False
		if entry is None:
			new_end =  int(time.time()) + self.autoincreasetime
		else:
			new_end = entry.begin -30

		dummyentry = RecordTimerEntry(self.service_ref, self.begin, new_end, self.name, self.description, self.eit, disabled=True, justplay = self.justplay, afterEvent = self.afterEvent, dirname = self.dirname, tags = self.tags)
		dummyentry.disabled = self.disabled
		timersanitycheck = TimerSanityCheck(NavigationInstance.instance.RecordTimer.timer_list, dummyentry)
		if not timersanitycheck.check():
			simulTimerList = timersanitycheck.getSimulTimerList()
			new_end = simulTimerList[1].begin
			del simulTimerList
			new_end -= 30				# 30 Sekunden Prepare-Zeit lassen
		del dummyentry
		if new_end <= time.time():
			return False
		self.end = new_end
		return True
	
	
	def sendStandbyNotification(self, answer):
		if answer:
			Notifications.AddNotification(Screens.Standby.Standby)

	def sendTryQuitMainloopNotification(self, answer):
		if answer:
			Notifications.AddNotification(Screens.Standby.TryQuitMainloop, 1)

	def getNextActivation(self):
		if self.state == self.StateEnded:
			return self.end
		
		next_state = self.state + 1
		
		return {self.StatePrepared: self.start_prepare, 
				self.StateRunning: self.begin, 
				self.StateEnded: self.end }[next_state]

	def failureCB(self, answer):
		if answer == True:
			self.log(13, "ok, zapped away")
			#NavigationInstance.instance.stopUserServices()
			NavigationInstance.instance.playService(self.service_ref.ref)
		else:
			self.log(14, "user didn't want to zap away, record will probably fail")

	def timeChanged(self):
		old_prepare = self.start_prepare
		self.start_prepare = self.begin - self.prepare_time
		self.backoff = 0
		
		if int(old_prepare) != int(self.start_prepare):
			self.log(15, "record time changed, start prepare is now: %s" % time.ctime(self.start_prepare))

	def gotRecordEvent(self, record, event):
		# TODO: this is not working (never true), please fix. (comparing two swig wrapped ePtrs)
		if self.__record_service.__deref__() != record.__deref__():
			return
		self.log(16, "record event %d" % event)
		if event == iRecordableService.evRecordWriteError:
			print "WRITE ERROR on recording, disk full?"
			# show notification. the 'id' will make sure that it will be
			# displayed only once, even if more timers are failing at the
			# same time. (which is very likely in case of disk fullness)
			Notifications.AddPopup(text = _("Write error while recording. Disk full?\n"), type = MessageBox.TYPE_ERROR, timeout = 0, id = "DiskFullMessage")
			# ok, the recording has been stopped. we need to properly note 
			# that in our state, with also keeping the possibility to re-try.
			# TODO: this has to be done.
		elif event == iRecordableService.evStart:
			text = _("A record has been started:\n%s") % self.name
			if self.dirnameHadToFallback:
				text = '\n'.join((text, _("Please note that the previously selected media could not be accessed and therefore the default directory is being used instead.")))

			if config.usage.show_message_when_recording_starts.value:
				Notifications.AddPopup(text = text, type = MessageBox.TYPE_INFO, timeout = 3)

	# we have record_service as property to automatically subscribe to record service events
	def setRecordService(self, service):
		if self.__record_service is not None:
			print "[remove callback]"
			NavigationInstance.instance.record_event.remove(self.gotRecordEvent)

		self.__record_service = service

		if self.__record_service is not None:
			print "[add callback]"
			NavigationInstance.instance.record_event.append(self.gotRecordEvent)

	record_service = property(lambda self: self.__record_service, setRecordService)

def createTimer(xml):
	begin = int(xml.get("begin"))
	end = int(xml.get("end"))
	serviceref = ServiceReference(xml.get("serviceref").encode("utf-8"))
	description = xml.get("description").encode("utf-8")
	repeated = xml.get("repeated").encode("utf-8")
	disabled = long(xml.get("disabled") or "0")
	justplay = long(xml.get("justplay") or "0")
	afterevent = str(xml.get("afterevent") or "nothing")
	afterevent = {
		"nothing": AFTEREVENT.NONE,
		"standby": AFTEREVENT.STANDBY,
		"deepstandby": AFTEREVENT.DEEPSTANDBY,
		"auto": AFTEREVENT.AUTO
		}[afterevent]
	eit = xml.get("eit")
	if eit and eit != "None":
		eit = long(eit);
	else:
		eit = None
	location = xml.get("location")
	if location and location != "None":
		location = location.encode("utf-8")
	else:
		location = None
	tags = xml.get("tags")
	if tags and tags != "None":
		tags = tags.encode("utf-8").split(' ')
	else:
		tags = None

	name = xml.get("name").encode("utf-8")
	#filename = xml.get("filename").encode("utf-8")
	entry = RecordTimerEntry(serviceref, begin, end, name, description, eit, disabled, justplay, afterevent, dirname = location, tags = tags)
	entry.repeated = int(repeated)
	
	for l in xml.findall("log"):
		time = int(l.get("time"))
		code = int(l.get("code"))
		msg = l.text.strip().encode("utf-8")
		entry.log_entries.append((time, code, msg))
	
	return entry

class RecordTimer(timer.Timer):
	def __init__(self):
		timer.Timer.__init__(self)
		
		self.Filename = Directories.resolveFilename(Directories.SCOPE_CONFIG, "timers.xml")
		
		try:
			self.loadTimer()
		except IOError:
			print "unable to load timers from file!"
			
	def isRecording(self):
		isRunning = False
		for timer in self.timer_list:
			if timer.isRunning() and not timer.justplay:
				isRunning = True
		return isRunning
	
	def loadTimer(self):
		# TODO: PATH!
		try:
			doc = xml.etree.cElementTree.parse(self.Filename)
		except SyntaxError:
			from Tools.Notifications import AddPopup
			from Screens.MessageBox import MessageBox

			AddPopup(_("The timer file (timers.xml) is corrupt and could not be loaded."), type = MessageBox.TYPE_ERROR, timeout = 0, id = "TimerLoadFailed")

			print "timers.xml failed to load!"
			try:
				import os
				os.rename(self.Filename, self.Filename + "_old")
			except (IOError, OSError):
				print "renaming broken timer failed"
			return
		except IOError:
			print "timers.xml not found!"
			return

		root = doc.getroot()

		# put out a message when at least one timer overlaps
		checkit = True
		for timer in root.findall("timer"):
			newTimer = createTimer(timer)
			if (self.record(newTimer, True, True) is not None) and (checkit == True):
				from Tools.Notifications import AddPopup
				from Screens.MessageBox import MessageBox
				AddPopup(_("Timer overlap in timers.xml detected!\nPlease recheck it!"), type = MessageBox.TYPE_ERROR, timeout = 0, id = "TimerLoadFailed")
				checkit = False # at moment it is enough when the message is displayed one time

	def saveTimer(self):
		#root_element = xml.etree.cElementTree.Element('timers')
		#root_element.text = "\n"

		#for timer in self.timer_list + self.processed_timers:
			# some timers (instant records) don't want to be saved.
			# skip them
			#if timer.dontSave:
				#continue
			#t = xml.etree.cElementTree.SubElement(root_element, 'timers')
			#t.set("begin", str(int(timer.begin)))
			#t.set("end", str(int(timer.end)))
			#t.set("serviceref", str(timer.service_ref))
			#t.set("repeated", str(timer.repeated))			
			#t.set("name", timer.name)
			#t.set("description", timer.description)
			#t.set("afterevent", str({
			#	AFTEREVENT.NONE: "nothing",
			#	AFTEREVENT.STANDBY: "standby",
			#	AFTEREVENT.DEEPSTANDBY: "deepstandby",
			#	AFTEREVENT.AUTO: "auto"}))
			#if timer.eit is not None:
			#	t.set("eit", str(timer.eit))
			#if timer.dirname is not None:
			#	t.set("location", str(timer.dirname))
			#t.set("disabled", str(int(timer.disabled)))
			#t.set("justplay", str(int(timer.justplay)))
			#t.text = "\n"
			#t.tail = "\n"

			#for time, code, msg in timer.log_entries:
				#l = xml.etree.cElementTree.SubElement(t, 'log')
				#l.set("time", str(time))
				#l.set("code", str(code))
				#l.text = str(msg)
				#l.tail = "\n"

		#doc = xml.etree.cElementTree.ElementTree(root_element)
		#doc.write(self.Filename)

		list = []

		list.append('<?xml version="1.0" ?>\n')
		list.append('<timers>\n')
		
		for timer in self.timer_list + self.processed_timers:
			if timer.dontSave:
				continue

			list.append('<timer')
			list.append(' begin="' + str(int(timer.begin)) + '"')
			list.append(' end="' + str(int(timer.end)) + '"')
			list.append(' serviceref="' + stringToXML(str(timer.service_ref)) + '"')
			list.append(' repeated="' + str(int(timer.repeated)) + '"')
			list.append(' name="' + str(stringToXML(timer.name)) + '"')
			list.append(' description="' + str(stringToXML(timer.description)) + '"')
			list.append(' afterevent="' + str(stringToXML({
				AFTEREVENT.NONE: "nothing",
				AFTEREVENT.STANDBY: "standby",
				AFTEREVENT.DEEPSTANDBY: "deepstandby",
				AFTEREVENT.AUTO: "auto"
				}[timer.afterEvent])) + '"')
			if timer.eit is not None:
				list.append(' eit="' + str(timer.eit) + '"')
			if timer.dirname is not None:
				list.append(' location="' + str(stringToXML(timer.dirname)) + '"')
			if timer.tags is not None:
				list.append(' tags="' + str(stringToXML(' '.join(timer.tags))) + '"')
			list.append(' disabled="' + str(int(timer.disabled)) + '"')
			list.append(' justplay="' + str(int(timer.justplay)) + '"')
			list.append('>\n')
			
			if config.recording.debug.value:
				for time, code, msg in timer.log_entries:
					list.append('<log')
					list.append(' code="' + str(code) + '"')
					list.append(' time="' + str(time) + '"')
					list.append('>')
					list.append(str(stringToXML(msg)))
					list.append('</log>\n')
			
			list.append('</timer>\n')

		list.append('</timers>\n')

		file = open(self.Filename, "w")
		for x in list:
			file.write(x)
		file.close()

	def getNextZapTime(self):
		now = time.time()
		for timer in self.timer_list:
			if not timer.justplay or timer.begin < now:
				continue
			return timer.begin
		return -1

	def getNextRecordingTime(self):
		now = time.time()
		for timer in self.timer_list:
			if timer.justplay or timer.begin < now:
				continue
			return timer.begin
		return -1

	def isNextRecordAfterEventActionAuto(self):
		now = time.time()
		t = None
		for timer in self.timer_list:
			if timer.justplay or timer.begin < now:
				continue
			if t is None or t.begin == timer.begin:
				t = timer
				if t.afterEvent == AFTEREVENT.AUTO:
					return True
		return False

	def record(self, entry, ignoreTSC=False, dosave=True):		#wird von loadTimer mit dosave=False aufgerufen
		timersanitycheck = TimerSanityCheck(self.timer_list,entry)
		if not timersanitycheck.check():
			if ignoreTSC != True:
				print "timer conflict detected!"
				print timersanitycheck.getSimulTimerList()
				return timersanitycheck.getSimulTimerList()
			else:
				print "ignore timer conflict"
		elif timersanitycheck.doubleCheck():
			print "ignore double timer"
			return None
		entry.timeChanged()
		print "[Timer] Record " + str(entry)
		entry.Timer = self
		self.addTimerEntry(entry)
		if dosave:
			self.saveTimer()
		return None

	def isInTimer(self, eventid, begin, duration, service):
		time_match = 0
		chktime = None
		chktimecmp = None
		chktimecmp_end = None
		end = begin + duration
		refstr = str(service)
		for x in self.timer_list:
			check = x.service_ref.ref.toString() == refstr
			if not check:
				sref = x.service_ref.ref
				parent_sid = sref.getUnsignedData(5)
				parent_tsid = sref.getUnsignedData(6)
				if parent_sid and parent_tsid: # check for subservice
					sid = sref.getUnsignedData(1)
					tsid = sref.getUnsignedData(2)
					sref.setUnsignedData(1, parent_sid)
					sref.setUnsignedData(2, parent_tsid)
					sref.setUnsignedData(5, 0)
					sref.setUnsignedData(6, 0)
					check = sref.toCompareString() == refstr
					num = 0
					if check:
						check = False
						event = eEPGCache.getInstance().lookupEventId(sref, eventid)
						num = event and event.getNumOfLinkageServices() or 0
					sref.setUnsignedData(1, sid)
					sref.setUnsignedData(2, tsid)
					sref.setUnsignedData(5, parent_sid)
					sref.setUnsignedData(6, parent_tsid)
					for cnt in range(num):
						subservice = event.getLinkageService(sref, cnt)
						if sref.toCompareString() == subservice.toCompareString():
							check = True
							break
			if check:
				if x.repeated != 0:
					if chktime is None:
						chktime = localtime(begin)
						chktimecmp = chktime.tm_wday * 1440 + chktime.tm_hour * 60 + chktime.tm_min
						chktimecmp_end = chktimecmp + (duration / 60)
					time = localtime(x.begin)
					for y in (0, 1, 2, 3, 4, 5, 6):
						if x.repeated & (2 ** y) and (x.begin <= begin or begin <= x.begin <= end):
							timecmp = y * 1440 + time.tm_hour * 60 + time.tm_min
							if timecmp <= chktimecmp < (timecmp + ((x.end - x.begin) / 60)):
								time_match = ((timecmp + ((x.end - x.begin) / 60)) - chktimecmp) * 60
							elif chktimecmp <= timecmp < chktimecmp_end:
								time_match = (chktimecmp_end - timecmp) * 60
				else: #if x.eit is None:
					if begin <= x.begin <= end:
						diff = end - x.begin
						if time_match < diff:
							time_match = diff
					elif x.begin <= begin <= x.end:
						diff = x.end - begin
						if time_match < diff:
							time_match = diff
				if time_match:
					break
		return time_match

	def removeEntry(self, entry):
		print "[Timer] Remove " + str(entry)
		
		# avoid re-enqueuing
		entry.repeated = False

		# abort timer.
		# this sets the end time to current time, so timer will be stopped.
		entry.autoincrease = False
		entry.abort()
		
		if entry.state != entry.StateEnded:
			self.timeChanged(entry)
		
		print "state: ", entry.state
		print "in processed: ", entry in self.processed_timers
		print "in running: ", entry in self.timer_list
		# autoincrease instanttimer if possible
		if not entry.dontSave:
			for x in self.timer_list:
				if x.setAutoincreaseEnd():
					self.timeChanged(x)
		# now the timer should be in the processed_timers list. remove it from there.
		self.processed_timers.remove(entry)
		self.saveTimer()

	def shutdown(self):
		self.saveTimer()
