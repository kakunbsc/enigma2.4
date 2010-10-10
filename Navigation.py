from enigma import eServiceCenter, eServiceReference, pNavigation, getBestPlayableServiceReference, iPlayableService
from Components.ParentalControl import parentalControl
from Tools.BoundFunction import boundFunction
from Tools.DreamboxHardware import setFPWakeuptime, getFPWakeuptime, getFPWasTimerWakeup, clearFPWasTimerWakeup
from time import time
import RecordTimer
import SleepTimer
import Screens.Standby
import NavigationInstance
import ServiceReference

# TODO: remove pNavgation, eNavigation and rewrite this stuff in python.
class Navigation:
	def __init__(self, nextRecordTimerAfterEventActionAuto=False):
		if NavigationInstance.instance is not None:
			raise NavigationInstance.instance
		
		NavigationInstance.instance = self
		self.ServiceHandler = eServiceCenter.getInstance()
		
		import Navigation as Nav
		Nav.navcore = self
		
		self.pnav = pNavigation()
		self.pnav.m_event.get().append(self.dispatchEvent)
		self.pnav.m_record_event.get().append(self.dispatchRecordEvent)
		self.event = [ ]
		self.record_event = [ ]
		self.currentlyPlayingServiceReference = None
		self.currentlyPlayingService = None
		self.RecordTimer = RecordTimer.RecordTimer()
		if getFPWasTimerWakeup():
			clearFPWasTimerWakeup()
			if getFPWasTimerWakeup(): # sanity check to detect if the FP driver is working correct!
				print "buggy fp driver detected!!! please update drivers.... ignore timer wakeup!"
			elif nextRecordTimerAfterEventActionAuto and (len(self.getRecordings()) or abs(self.RecordTimer.getNextRecordingTime() - time()) <= 360):
				if not Screens.Standby.inTryQuitMainloop: # not a shutdown messagebox is open
					RecordTimer.RecordTimerEntry.TryQuitMainloop(False) # start shutdown handling
		self.SleepTimer = SleepTimer.SleepTimer()

	def dispatchEvent(self, i):
		for x in self.event:
			x(i)
		if i == iPlayableService.evEnd:
			self.currentlyPlayingServiceReference = None
			self.currentlyPlayingService = None

	def dispatchRecordEvent(self, rec_service, event):
#		print "record_event", rec_service, event
		for x in self.record_event:
			x(rec_service, event)

	def playService(self, ref, checkParentalControl = True):
		oldref = self.currentlyPlayingServiceReference
		if ref and oldref and ref == oldref:
			print "ignore request to play already running service"
			return 0
		print "playing", ref and ref.toString()
		if ref is None:
			self.stopService()
			return 0
		if not checkParentalControl or parentalControl.isServicePlayable(ref, boundFunction(self.playService, checkParentalControl = False)):
			if ref.flags & eServiceReference.isGroup:
				if not oldref:
					oldref = eServiceReference()
				playref = getBestPlayableServiceReference(ref, oldref)
				if not playref or (checkParentalControl and not parentalControl.isServicePlayable(playref, boundFunction(self.playService, checkParentalControl = False))):
					self.stopService()
					return 0
			else:
				playref = ref
			if self.pnav and not self.pnav.playService(playref):
				self.currentlyPlayingServiceReference = playref
				return 0
		else:
			self.stopService()
		return 1
	
	def getCurrentlyPlayingServiceReference(self):
		return self.currentlyPlayingServiceReference
	
	def recordService(self, ref, simulate=False):
		service = None
		print "recording service: %s" % (str(ref))
		if isinstance(ref, ServiceReference.ServiceReference):
			ref = ref.ref
		if ref:
			if ref.flags & eServiceReference.isGroup:
				ref = getBestPlayableServiceReference(ref, eServiceReference(), simulate)
			service = ref and self.pnav and self.pnav.recordService(ref, simulate)
			if service is None:
				print "record returned non-zero"
		return service

	def stopRecordService(self, service):
		ret = self.pnav and self.pnav.stopRecordService(service)
		return ret

	def getRecordings(self, simulate=False):
		return self.pnav and self.pnav.getRecordings(simulate)

	def getCurrentService(self):
		if not self.currentlyPlayingService:
			self.currentlyPlayingService = self.pnav and self.pnav.getCurrentService()
		return self.currentlyPlayingService

	def stopService(self):
		print "stopService"
		if self.pnav:
			self.pnav.stopService()

	def pause(self, p):
		return self.pnav and self.pnav.pause(p)

	def shutdown(self):
		self.RecordTimer.shutdown()
		self.ServiceHandler = None
		self.pnav = None

	def stopUserServices(self):
		self.stopService()
