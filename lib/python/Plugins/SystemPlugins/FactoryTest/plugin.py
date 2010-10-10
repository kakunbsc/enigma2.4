from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.MenuList import MenuList
from Tools.Directories import fileExists
from Components.ServiceList import ServiceList
from Components.ActionMap import ActionMap,NumberActionMap
from Components.config import config
from os import system,access,F_OK,R_OK,W_OK
from Components.Label import Label
from Components.AVSwitch import AVSwitch
from time import sleep
from Components.Console import Console
from enigma import eTimer
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonStringContent, eListbox, gFont, eServiceCenter, eDVBResourceManager
from enigma import eServiceReference
from enigma import eMemtest
from enigma import eSctest
from enigma import eDVBDB
from Components.NimManager import nimmanager
from enigma import eDVBCI_UI,eDVBCIInterfaces

class TestResultList(HTMLComponent, GUIComponent):
	def __init__(self, source):
		GUIComponent.__init__(self)
		self.l = eListboxPythonStringContent()
		self.list = source
		self.l.setList(self.list)

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		self.instance.setSelectionEnable(0)
		self.instance.setContent(self.l)

	def updateList(self,list):
		self.l.setList(list)

class FactoryTest(Screen):
	skin = """
		<screen position="120,125" size="440,400" title="Test Menu" >
			<widget name="testlist" position="10,0" size="340,350" />
			<widget name="resultlist" position="370,0" size="60,350" />
			<widget name="testdate" position="20,350" size="150,25" font="Regular;22" />
			<widget name="testversion" position="20,375" size="150,25" font="Regular;22" />
			<widget name="mactext" position="180,350" size="230,25" font="Regular;22" />			
		</screen>"""
	def __init__(self, session):

		self["actions"] = NumberActionMap(["OkCancelActions","WizardActions","NumberActions","ColorActions",],
		{
			"left": self.nothing,
			"right":self.nothing,
			"ok": self.TestAction,
			"testexit": self.keyCancel,
			"agingstart": self.Agingmode,
			"up": self.keyup,
			"down": self.keydown,
			"0": self.numberaction,
			"1": self.numberaction,	
			"2": self.numberaction,			
			"3": self.numberaction,			
			"4": self.numberaction,			
			"5": self.numberaction,			
			"6": self.numberaction,			
			"7": self.numberaction,			
			"8": self.numberaction,			
			"9": self.numberaction,			
			"red": self.shutdownaction,
		}, -2)

		Screen.__init__(self, session)
		TESTPROGRAM_DATE = "2010-06-25"
		TESTPROGRAM_VERSION = "Version 00.01"

		self.model = 0
		self.getModelInfo()
		
		self["testdate"]=Label((TESTPROGRAM_DATE))
		self["testversion"]=Label(("Loading version..."))
		self["mactext"]=Label(("Loading mac address..."))
		nimConfig = nimmanager.getNimConfig(0)
		nimConfig.configMode.slot_id=0
		nimConfig.configMode.value= "simple"
		nimConfig.diseqcMode.value="diseqc_a_b"
		nimConfig.diseqcA.value="160"
		nimConfig.diseqcB.value="100"
		if self.model == 0:
			nimConfig = nimmanager.getNimConfig(1)
			nimConfig.configMode.slot_id=1		
			nimConfig.configMode.value= "simple"
			nimConfig.diseqcMode.value="diseqc_a_b"
			nimConfig.diseqcA.value="130"
			nimConfig.diseqcB.value="192"
		nimmanager.sec.update()		
		
		system("cp /usr/lib/enigma2/python/Plugins/SystemPlugins/FactoryTest/testdb /etc/enigma2/lamedb")
		db = eDVBDB.getInstance()
		db.reloadServicelist()

		tlist = []
		if self.model == 0:
			self.satetestIndex=0
			tlist.append((" 0. Sata & extend hdd test",self.satetestIndex))
			self.usbtestIndex=1
			tlist.append((" 1. USB test",self.usbtestIndex))
			self.fronttestIndex=2
			tlist.append((" 2. Front test",self.fronttestIndex))
			self.smarttestIndex=3
			tlist.append((" 3. Smartcard test",self.smarttestIndex))
			self.tuner1_1testIndex=4
			tlist.append((" 4. T1 H 22K x 4:3 CVBS",self.tuner1_1testIndex))
			self.tuner1_2testIndex=5
			tlist.append((" 5. T1 V 22k o 16:9 RGB",self.tuner1_2testIndex))
			self.tuner2_1testIndex=6
			tlist.append((" 6. T2 H 22k x 4:3 YC",self.tuner2_1testIndex))
			self.tuner2_2testIndex=7
			tlist.append((" 7. T2 V 22k o 16:9 CVBS CAM",self.tuner2_2testIndex))
			self.scarttestIndex=8
			tlist.append((" 8. VCR Scart loop",self.scarttestIndex))
			self.rs232testIndex=9
			tlist.append((" 9. RS232 test",self.rs232testIndex))
			self.ethernettestIndex=10
			tlist.append(("10. Ethernet & mac test",self.ethernettestIndex))
#		tlist.append(("11. DRAM test",11))
#		tlist.append(("12. Flash test",12))
#		tlist.append(("13. DRAM+Flash test",13))
			self.fdefaultIndex=11
			tlist.append(("11. Factory default",self.fdefaultIndex))
			self.shutdownIndex=12
			tlist.append(("12. Shutdown",self.shutdownIndex))
		elif self.model == 1:
#			tlist.append((" 0. Sata & extend hdd test",self.satetestIndex=0))
			self.satetestIndex = -1
			self.scarttestIndex = -1



			self.usbtestIndex=0
			tlist.append((" 0. USB test",self.usbtestIndex))
			self.fronttestIndex=1
			tlist.append((" 1. Front test",self.fronttestIndex))
			self.smarttestIndex=2
			tlist.append((" 2. Smartcard test",self.smarttestIndex))
			self.tuner1_1testIndex=3
			tlist.append((" 3. T1 H 22K x 4:3 CVBS",self.tuner1_1testIndex))
			self.tuner1_2testIndex=4
			tlist.append((" 4. T1 V 22k o 16:9 RGB CAM",self.tuner1_2testIndex))
			self.tuner2_2testIndex=4
#			tlist.append((" 6. T2 H 22k x 4:3 YC",self.tuner2_1testIndex=6))
#			tlist.append((" 7. T2 V 22k o 16:9 CVBS CAM",self.tuner2_2testIndex=7))
#			tlist.append((" 8. VCR Scart loop",self.scarttestIndex=8))
			self.rs232testIndex=5
			tlist.append((" 5. RS232 test",self.rs232testIndex))
			self.ethernettestIndex=6
			tlist.append((" 6. Ethernet & mac test",self.ethernettestIndex))
#		tlist.append(("11. DRAM test",11))
#		tlist.append(("12. Flash test",12))
#		tlist.append(("13. DRAM+Flash test",13))
			self.fdefaultIndex=7
			tlist.append((" 7. Factory default",self.fdefaultIndex))
			self.shutdownIndex=8
			tlist.append((" 8. Shutdown",self.shutdownIndex))
		self.menulength= len(tlist)-1
		self["testlist"] = MenuList(tlist)
		self.rlist = []
#		for x in range(15):
#		for x in range(12):
		for x in range(self.menulength):
			self.rlist.append((".."))
		self["resultlist"] = TestResultList(self.rlist)
		self.NetworkState = 0
		self.first = 0

		self.avswitch = AVSwitch()
		self.memTest = eMemtest()
		self.scTest= eSctest()
		
		self.feid=0
		self.agingmode=0
		self.testing = 0

		self.servicelist = ServiceList()
		self.oldref = session.nav.getCurrentlyPlayingServiceReference()
		print "oldref",self.oldref
		session.nav.stopService() # try to disable foreground service
		
		self.tunemsgtimer = eTimer()
		self.tunemsgtimer.callback.append(self.tunemsg)

		self.camstep = 1
		self.camtimer = eTimer()
		self.camtimer.callback.append(self.cam_state)
		self.getmacaddr()
		self.getversion()
		
		self.tunerlock = 0
		self.tuningtimer = eTimer()
		self.tuningtimer.callback.append(self.updateStatus)

		self.satatry = 8
		self.satatimer = eTimer()
		self.satatimer.callback.append(self.sataCheck)

	def getModelInfo(self):
		info = open("/proc/stb/info/version").read()
		print info,info[:2]
		if info[:2] == "14":
			self.model = 1
		elif info[:2] == "12":
			self.model= 0
		

	def nothing(self):
		print "nothing"

	def keyup(self):
		if self.testing==1:
			return
		if self["testlist"].getCurrent()[1]==0:
			self["testlist"].moveToIndex(self.menulength)
		else:
			self["testlist"].up()


	def keydown(self):
		if self.testing==1:
			return
		if self["testlist"].getCurrent()[1]==(self.menulength):
			self["testlist"].moveToIndex(0)
		else:
			self["testlist"].down()

	def numberaction(self, number):
		if self.testing==1:
			return
		index = int(number)
		self["testlist"].moveToIndex(index)


	def updateStatus(self):
		index = self["testlist"].getCurrent()[1]
		if index ==self.tuner1_1testIndex or index==self.tuner1_2testIndex:
			tunno = 1
			result = eSctest.getInstance().getFrontendstatus(0)
		else:
			tunno = 2
			result = eSctest.getInstance().getFrontendstatus(1)

		if self.agingmode == 1:
			tunno = 1
			result = eSctest.getInstance().getFrontendstatus(0)
			hv = "Ver"
			
		if index == self.tuner1_2testIndex or index==self.tuner2_2testIndex:
			hv = "Ver"
		else:
			hv = "Hor"
			
		print "eSctest.getInstance().getFrontendstatus - %d"%result
		if result == 0:
			self.tunerlock = 0
			self.tunemsgtimer.stop()
			self.session.nav.stopService()
			self.session.open( MessageBox, _("Tune%d %s Locking Fail..."%(tunno,hv)), MessageBox.TYPE_ERROR)	
			if self.agingmode==0:
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			self.agingmode = 0
		else :
			self.tunerlock = 1
			if self.agingmode==1:
				self.session.openWithCallback(self.checkaging,AgingTest)			

	def getversion(self):
		try:
			fd = open("/proc/stb/info/version","r")
			version = fd.read()
			self["testversion"].setText(("Version %s"%version))
		except:
			self["testversion"].setText(("Version no load"))
			

	def readmac(self, result, retval,extra_args=None):
		(statecallback) = extra_args
		if self.macConsole is not None:
			if retval == 0:
				self.macConsole = None
				content =result.splitlines()
                                for x in content:
                                        if x.startswith('0x00000010:'):
                                                macline = x.split()
                                if len(macline) < 10:
                                        print 'mac dump read error'
                                        retrun
				mac = macline[5]+":"+macline[6]+":"+macline[7]+":"+macline[8]+":"+macline[9]+":"+macline[10]
				self["mactext"].setText(("MAC : "+mac))
 	
	def getmacaddr(self):
		try:
			cmd = "nanddump -b -o -l 64 -p /dev/mtd4"
			self.macConsole = Console()	
			self.macConsole.ePopen(cmd, self.readmac)	
		except:
			return
		
	def TestAction(self):
#
#			tlist.append((" 0. Sata & extend hdd test",self.satetestIndex=0))
#			tlist.append((" 1. USB test",self.usbtestIndex=1))
#			tlist.append((" 2. Front test",self.fronttestIndex=2))
#			tlist.append((" 3. Smartcard test",self.smarttestIndex=3))
#			tlist.append((" 4. T1 H 22K x 4:3 CVBS",self.tuner1_1testIndex=4))
#			tlist.append((" 5. T1 V 22k o 16:9 RGB",self.tuner1_2testIndex=5))
#			tlist.append((" 6. T2 H 22k x 4:3 YC",self.tuner2_1testIndex=6))
#			tlist.append((" 7. T2 V 22k o 16:9 CVBS CAM",self.tuner2_2testIndex=7))
#			tlist.append((" 8. VCR Scart loop",self.scarttestIndex=8))
#			tlist.append((" 9. RS232 test",self.rs232testIndex=9))
#			tlist.append(("10. Ethernet & mac test",self.ethernettestIndex=10))
#		tlist.append(("11. DRAM test",11))
#		tlist.append(("12. Flash test",12))
#		tlist.append(("13. DRAM+Flash test",13))
#			tlist.append(("11. Factory default",self.fdefaultIndex=11))
#			tlist.append(("12. Shutdown",self.shutdownIndex=12))
#
		if self.testing==1:
			return
		print "line - ",self["testlist"].getCurrent()[1]
		index = self["testlist"].getCurrent()[1]
		result = 0
		if index==self.satetestIndex:
			self.Test0()
		elif index==self.fronttestIndex:
			self.Test1()
		elif index>=self.tuner1_1testIndex and index<=self.tuner2_2testIndex:
			self.TestTune(index)
		elif index==self.scarttestIndex:
			self.Test6()
		elif index==self.rs232testIndex:
			self.Test7()
		elif index==self.usbtestIndex:
			self.Test8()
		elif index==self.ethernettestIndex:
			self.Test9()
		elif index == self.smarttestIndex:
			self.Test10()
#		elif index == 11:
#			self.Test11()
#		elif index ==12:
#			self.Test12()
#		elif index==13:
#			self.Test13()
		elif index==self.fdefaultIndex:
			self.Test14()
#		elif index==self.shutdownIndex:
#			self.Test15()

	def shutdownaction(self):
		if self["testlist"].getCurrent()[1] == self.shutdownIndex:
			self.Test15()


	def Test0(self):
		self.satatry = 8
		self.satatimer.start(100,True)

	def sataCheck(self):
#		print "try", self.satatry
		if self.satatry == 0:
			displayerror = 1
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="try %d"%self.satatry
			self["resultlist"].updateList(self.rlist)
			self.satatry -= 1
			displayerror = 0
		result = 0
		checktab=0
		try:
			mtab = open('/etc/mtab','r')
			while(1):
				disk = mtab.readline().split(' ')
				if len(disk) < 2:
					break
				if disk[1].startswith('/media/hdd'):
					checktab+=1
				elif disk[1].startswith('/media/sdb1'):
					checktab+=10
				if checktab==11:
					break
		except:
			checktab = 0

		if checktab==0:
			if displayerror==1:
				self.session.open( MessageBox, _("Sata & extend hdd test error"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			else:
				self.satatimer.start(1100,True)
			return
		elif checktab < 11:
			if displayerror==1:
				self.session.open( MessageBox, _("one hdd test error"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			else:
				self.satatimer.start(1100,True)
			return

		try:
			if fileExists("/media/sdb1"):
				if access("/media/sdb1",F_OK|R_OK|W_OK):
					dummy=open("/media/sdb1/dummy03","w")
					dummy.write("complete")
					dummy.close()
					dummy=open("/media/sdb1/dummy03","r")
					if dummy.readline()=="complete":
						print "complete"
					else:
						result = 1
					dummy.close()
					system("rm /media/sdb1/dummy03")
				else:
					result = 1
			else:
				result = 1
		except:
			result = 1
		try:
			if fileExists("/media/hdd"):
				if access("/media/hdd",F_OK|R_OK|W_OK):
					dummy=open("/media/hdd/dummy03","w")
					dummy.write("complete")
					dummy.close()
					dummy=open("/media/hdd/dummy03","r")
					if dummy.readline()=="complete":
						print "complete"
					else:
						result += 1
					dummy.close()
					system("rm /media/hdd/dummy03")
				else:
					result = 1
			else:
				result += 1
		except:
			result += 1
			
		if result ==0:
			self.session.open( MessageBox, _("Sata & extend hdd test pass"), MessageBox.TYPE_INFO)
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		elif result == 1:
			if displayerror==1:
				self.session.open( MessageBox, _("one hdd test error"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			else:
				self.satatimer.start(1100,True)
		else:
			if displayerror==1:
				self.session.open( MessageBox, _("Sata & extend hdd test error"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			else:
				self.satatimer.start(1100,True)

	def Test1(self):
		if self.model== 0:
			self.session.openWithCallback(self.displayresult ,FrontTest)
		elif self.model == 1:
			self.session.openWithCallback(self.displayresult ,FrontTest_solo)		

	def displayresult(self):
		global fronttest
		if fronttest == 1:
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"

	INTERNAL_PID_STATUS_NOOP = 0
	INTERNAL_PID_STATUS_WAITING = 1
	INTERNAL_PID_STATUS_SUCCESSFUL = 2
	INTERNAL_PID_STATUS_FAILED = 3

	def TestTune(self,index):	
		if self.oldref is None:
			eref = eServiceReference("1:0:19:1324:3EF:1:C00000:0:0:0")
			serviceHandler = eServiceCenter.getInstance()
			servicelist = serviceHandler.list(eref)
			if not servicelist is None:
				ref = servicelist.getNext()
			else:
				ref = self.getCurrentSelection()
				print "servicelist none"
		else:
			ref = self.oldref
		self.session.nav.stopService() # try to disable foreground service
		if index==self.tuner1_1testIndex:
			ref.setData(0,1)
			ref.setData(1,0x6D3)
			ref.setData(2,0x3)
			ref.setData(3,0xA4)
			ref.setData(4,0xA00000)
			self.session.nav.playService(ref)
			self.avswitch.setColorFormat(0)
			self.avswitch.setAspectRatio(0)
		elif index==self.tuner1_2testIndex:
			if self.model == 1:
				self.camstep = 1
				self.camtimer.start(100,True)
			ref.setData(0,0x19)
			ref.setData(1,0x1325)
			ref.setData(2,0x3ef)
			ref.setData(3,0x1)
			ref.setData(4,0x64af79)
#		ref.setData(0,0x19)
#		ref.setData(1,0x83)
#		ref.setData(2,0x6)
#		ref.setData(3,0x85)
#		ref.setData(4,0x640000)
			self.session.nav.playService(ref)
			self.avswitch.setColorFormat(1)
			self.avswitch.setAspectRatio(6)			
		elif index==self.tuner2_1testIndex:
#			self.camstep = 1
#			self.camtimer.start(100,True)
			ref.setData(0,1)
			ref.setData(1,0x6D3)
			ref.setData(2,0x3)
			ref.setData(3,0xA4)
			ref.setData(4,0x820000)
			self.session.nav.playService(ref)
			self.avswitch.setColorFormat(2)			
			self.avswitch.setAspectRatio(0)			
		elif index==self.tuner2_2testIndex:
			self.camstep = 1
			self.camtimer.start(100,True)
#			ref.setData(0,0x19)
#			ref.setData(1,0x83)
#			ref.setData(2,0x6)
#			ref.setData(3,0x85)
#		ref.setData(4,0xC00000)
#	ikseong - for 22000 tp ( /home/ikseong/share/lamedb_ORF)
			ref.setData(0,0x19)
			ref.setData(1,0x1325)
			ref.setData(2,0x3ef)
			ref.setData(3,0x1)
			ref.setData(4,0xC00000)
			self.session.nav.playService(ref)
			self.avswitch.setColorFormat(0)			
			self.avswitch.setAspectRatio(6)
		self.tuningtimer.start(2000,True)
		self.tunemsgtimer.start(3000, True)

	def cam_state(self):
		if self.camstep == 1:
			slot = 0
			state = eDVBCI_UI.getInstance().getState(slot)
			print '-1-stat',state
			if state > 0:
				self.camstep=2
				self.camtimer.start(100,True)
			else:
				self.session.nav.stopService()
				self.session.open( MessageBox, _("CAM1_NOT_INSERTED\nPress exit!"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
				self.tunemsgtimer.stop()
#				self.rlist[index]="fail"
#				self["resultlist"].updateList(self.rlist)
		elif self.camstep == 2:
			slot = 0
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			print 'appname',appname
			if appname is None:
				self.session.nav.stopService()
				self.session.open( MessageBox, _("NO_GET_APPNAME\nPress exit!"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
				self.tunemsgtimer.stop()				
			else:
				self.camstep=3
				self.camtimer.start(100,True)		
		elif self.camstep==3:
			slot = 1
			state = eDVBCI_UI.getInstance().getState(slot)
			print '-2-stat',state
			if state > 0:
				self.camstep=4
				self.camtimer.start(100,True)
			else:
				self.session.nav.stopService()
				self.session.open( MessageBox, _("CAM2_NOT_INSERTED\nPress exit!"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
				self.tunemsgtimer.stop()				
#				self.rlist[index]="fail"
#				self["resultlist"].updateList(self.rlist)
		elif self.camstep == 4:
			slot = 1
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			print 'appname',appname
			if appname is None:
				self.session.nav.stopService()
				self.session.open( MessageBox, _("NO_GET_APPNAME\nPress exit!"), MessageBox.TYPE_ERROR)
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
				self.tunemsgtimer.stop()				
			else:
				self.setSource()
				self.camstep = 5
#				self.session.open( MessageBox, _("CAM OK!"), MessageBox.TYPE_INFO,2)

#	ikseong - for 22000 tp
	def setSource(self):
		filename = ("/proc/stb/tsmux/ci0_input")
		fd = open(filename,'w')
		fd.write('B')
#		fd.write('A')
		fd.close()
#		filename = ("/proc/stb/tsmux/ci1_input")
#		fd = open(filename,'w')
#		fd.write('CI0')
#		fd.close()
		fd=open("/proc/stb/tsmux/input1","w")
#		fd=open("/proc/stb/tsmux/input0","w")
		fd.write("CI0")
		fd.close()
		print "CI loop test!!!!!!!!!!!!!!"
			
	def resetSource(self):
		fd=open("/proc/stb/tsmux/input1","w")
		fd.write("B")
		fd.close()
		print "CI loop test end!!!!!!!!!!!!!!"
		
	def tunemsg(self):
		self.tuningtimer.stop()
		self.session.openWithCallback(self.tuneback, MessageBox, _("%s ok?" %(self["testlist"].getCurrent()[0])), MessageBox.TYPE_YESNO)

	def tuneback(self,yesno):
		self.session.nav.stopService() # try to disable foreground service
		if yesno:
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
			if self.tunerlock == 0:
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
			elif self["testlist"].getCurrent()[1] == 7 and self.camstep < 5:
				self.rlist[self["testlist"].getCurrent()[1]]="fail"
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"
		if self["testlist"].getCurrent()[1] == 6:
			self.avswitch.setColorFormat(0)			
		self.resetSource()
		self["resultlist"].updateList(self.rlist)
				
	def Test6(self):
		self.avswitch.setInput("SCART")
		sleep(2)
		self.session.openWithCallback(self.check6, MessageBox, _("Scart loop ok?"), MessageBox.TYPE_YESNO)

	def check6(self,yesno):
		if yesno:
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"
		self.avswitch.setInput("ENCODER")

	def check7(self):
		global rstest
		if rstest == 1:
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"

	def Test7(self):
		self.session.openWithCallback(self.check7,RS232Test)

	def Agingmode(self):
		if self.testing==1:
			return
		if self.oldref is None:
			eref = eServiceReference("1:0:19:1324:3EF:1:C00000:0:0:0")
			serviceHandler = eServiceCenter.getInstance()
			servicelist = serviceHandler.list(eref)
			if not servicelist is None:
				ref = servicelist.getNext()
			else:
				ref = self.getCurrentSelection()
				print "servicelist none"
		else:
			ref = self.oldref
		self.session.nav.stopService() # try to disable foreground service
		ref.setData(0,0x19)
		ref.setData(1,0x1325)
		ref.setData(2,0x3ef)
		ref.setData(3,0x1)
		ref.setData(4,0x64af79)
#		ref.setData(0,1)
#		ref.setData(1,0x6D3)
#		ref.setData(2,0x3)
#		ref.setData(3,0xA4)
#		ref.setData(4,0xA00000)
		self.session.nav.playService(ref)
		self.avswitch.setColorFormat(0)
		self.avswitch.setAspectRatio(0)
		self.tuningtimer.start(2000,True)
		self.agingmode = 1

	def checkaging(self):
		global Agingresult
		if(Agingresult ==1):
			self["testlist"].moveToIndex(self.fdefaultIndex)
			self.Test14()
			self["testlist"].moveToIndex(self.shutdownIndex)
		self.agingmode = 0
#			self["testlist"].instance.moveSelection(self["testlist"].instance.moveDown)
			
		

	def Test8(self):
		if self.model==0:			
			try:
				result = 0
				mtab = open('/etc/mtab','r')
				while(1):
					disk = mtab.readline().split(' ')
					if len(disk) < 2:
						break
					if disk[1].startswith('/media/hdd'):
						continue
					elif disk[1].startswith('/media/sdb1'):
						continue
					elif disk[1].startswith('/media/sd'):
						result=result +1

				if result < 0 :
					result = 0
				if result == 3:
					self.session.open( MessageBox, _("USB test pass %d devices\nPress OK!"%result), MessageBox.TYPE_INFO)			
					self.rlist[self["testlist"].getCurrent()[1]]="pass"
				else:
					self.session.open( MessageBox, _("USB test error : Success-%d"%result+" Fail-%d\nPress EXIT!"%(3-result)), MessageBox.TYPE_ERROR)
					self.rlist[self["testlist"].getCurrent()[1]]="fail"
			except:
				if result < 0 :
					result = 0
				if result == 3:
					self.session.open( MessageBox, _("USB test pass %d devices\nPress OK!"%result), MessageBox.TYPE_INFO)			
					self.rlist[self["testlist"].getCurrent()[1]]="pass"
				else:
					self.session.open( MessageBox, _("USB test error : Success-%d"%result+" Fail-%d\nPress EXIT!"%(3-result)), MessageBox.TYPE_ERROR)
					self.rlist[self["testlist"].getCurrent()[1]]="fail"
		elif self.model==1:
			try:
				result = 0
				mtab = open('/etc/mtab','r')
				while(1):
					disk = mtab.readline().split(' ')
					if len(disk) < 2:
						break
					if disk[1].startswith('/media/'):
						result=result +1

				if result < 0 :
					result = 0
				if result == 2:
					self.session.open( MessageBox, _("USB test pass %d devices\nPress OK!"%result), MessageBox.TYPE_INFO)			
					self.rlist[self["testlist"].getCurrent()[1]]="pass"
				else:
					self.session.open( MessageBox, _("USB test error : Success-%d"%result+" Fail-%d\nPress EXIT!"%(2-result)), MessageBox.TYPE_ERROR)
					self.rlist[self["testlist"].getCurrent()[1]]="fail"
			except:
				if result < 0 :
					result = 0
				if result == 2:
					self.session.open( MessageBox, _("USB test pass %d devices\nPress OK!"%result), MessageBox.TYPE_INFO)			
					self.rlist[self["testlist"].getCurrent()[1]]="pass"
				else:
					self.session.open( MessageBox, _("USB test error : Success-%d"%result+" Fail-%d\nPress EXIT!"%(2-result)), MessageBox.TYPE_ERROR)
					self.rlist[self["testlist"].getCurrent()[1]]="fail"
		

	def pingtest(self):
		self.testing = 1
#		system("/etc/init.d/networking stop")
		system("ifconfig eth0 192.168.0.10")
#		system("/etc/init.d/networking start")
		cmd1 = "ping -c 1 192.168.0.100"
		self.PingConsole = Console()
		self.PingConsole.ePopen(cmd1, self.checkNetworkStateFinished,self.NetworkStatedataAvail)
		
	def checkNetworkStateFinished(self, result, retval,extra_args):
		(statecallback) = extra_args
		if self.PingConsole is not None:
			if retval == 0:
				self.PingConsole = None
				content = result.splitlines()
#				print 'content',content
				x = content[4].split()
#				print 'x',x
				if x[0]==x[3]:
					statecallback(1)
				else:
					statecallback(0)					
			else:
				statecallback(0)


	def NetworkStatedataAvail(self,data):
		global ethtest
		if data == 1:
			ethtest = 1
			print "success"
#			self.session.open( MessageBox, _("Ping test pass"), MessageBox.TYPE_INFO,2)
			self.session.openWithCallback(self.openMacConfig ,MessageBox, _("Ping test pass"), MessageBox.TYPE_INFO,2)
		
		else:
			ethtest = 0
			print "fail"
			self.session.open( MessageBox, _("Ping test fail\nPress exit"), MessageBox.TYPE_ERROR)
			self.macresult()

	def Test9(self):
		self.pingtest()

	def openMacConfig(self, ret=False):
		self.session.openWithCallback(self.macresult ,MacConfig)	
			
	def macresult(self):
		global ethtest
		if ethtest == 1:
			self.rlist[self.ethernettestIndex]="pass"		
#			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		else:
			self.rlist[self.ethernettestIndex]="fail"		
#			self.rlist[self["testlist"].getCurrent()[1]]="fail"
		self.getmacaddr()
		self.testing = 0			
	
	def MemTest(self, which):
		index = which
		result = 0
		if index==0:
			result = eMemtest.getInstance().dramtest()
		elif index==1:
			result = eMemtest.getInstance().flashtest()
			result = 0	#	temp
		else:
			result = eMemtest.getInstance().dramtest()
			result = eMemtest.getInstance().flashtest()
			result = 0	#	temp
			
		index = index+10
		
		if result == 0:
			print index,self.rlist[index]
			self.rlist[index]="pass"
		else:
			print index,self.rlist[index]
			self.rlist[index]="fail"
		self["resultlist"].updateList(self.rlist)
			
	def scciresult(self):
		global smartcardtest
		if smartcardtest == 1:
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
		else:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"

	def Test10(self):
		self.session.openWithCallback(self.scciresult ,SmartCardTest)	

	def Test11(self):
		self.MemTest(1)
		
	def Test12(self):
		self.MemTest(2)

	def Test13(self):
		self.MemTest(3)	


	def Test14(self):
		try:
			system("rm -R /etc/enigma2")
			system("cp -R /usr/share/enigma2/defaults /etc/enigma2")
			self.rlist[self["testlist"].getCurrent()[1]]="pass"
			self["resultlist"].updateList(self.rlist)
		except:
			self.rlist[self["testlist"].getCurrent()[1]]="fail"
			self["resultlist"].updateList(self.rlist)
			self.session.open( MessageBox, _("Factory reset fail"), MessageBox.TYPE_ERROR)

	def Test15(self):
		self.session.openWithCallback(self.shutdown ,MessageBox, _("Do you want to shut down?"), MessageBox.TYPE_YESNO)

	def shutdown(self, yesno):
		if yesno :
			from os import _exit
			system("/usr/bin/showiframe /boot/backdrop.mvi")
			_exit(1)
		else:
			return
		
	def keyCancel(self):
		if self.testing==1:
			return
		print "exit"
		self.close()

ethtest = 0
class MacConfig(Screen):
	skin = """
		<screen position="100,250" size="520,100" title="Mac Config" >
			<eLabel text="Mac Address " position="10,15" size="200,40" font="Regular;30" />		
			<widget name="text" position="230,15" size="230,40" font="Regular;30" />
			<widget name="text1" position="470,15" size="40,40" font="Regular;30" />		
			<eLabel text=" " position="5,55" zPosition="-1" size="510,5" backgroundColor="#02e1e8e6" />		
			<widget name="stattext" position="30,75" size="400,25" font="Regular;20" />
		</screen>"""

	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions","OkCancelActions"],
		{
			"ok": self.keyOk,
			"left": self.keyleft,
			"right": self.keyright,
			"cancel": self.keyCancel,
		}, -2)

		Screen.__init__(self, session)
	
		self.result = 0
		self.macfd = 0
		self.macaddr = "000000000000"
		self.NetworkState = 0
		self["text"]=Label((self.macaddr))
		self["text1"]= Label(("< >"))
		self["stattext"]= Label((""))
		self.displaymac()
		self.loadmacaddr()
		self.getmacaddr()
		self.pingok=1
		global ethtest
		ethtest = 1

	def loadmacaddr(self):
		try:
			result = 0
			self.macfd = 0
			mtab = open('/etc/mtab','r')
			while(1):
				disk = mtab.readline().split(' ')
				if len(disk) < 2:
					break
				if disk[1].startswith('/media/sd') or disk[1].startswith('/media/hdd'):
					print 'try..',disk[1]
					if  fileExists(disk[1]+"/macinfo.txt"):
						self.macfd = open(disk[1]+"/macinfo.txt","r+")
						break
			if self.macfd == 0:
				self["text"].setText(("cannot read usb!!"))
				self["text1"].setText((" "))
				self["stattext"].setText((" Press Exit Key."))
				self.NetworkState=0
				return
			
			macaddr=self.macfd.readline().split(":")
			self.macaddr=macaddr[1]+macaddr[2]+macaddr[3]+macaddr[4]+macaddr[5]+macaddr[6]
			self.displaymac()
			self.NetworkState = 1
		except:
			self["text"].setText(("cannot read usb!!"))
			self["text1"].setText((" "))
			self["stattext"].setText((" Press Exit Key."))
			self.NetworkState=0
#			self.session.open( MessageBox, _("Mac address fail"), MessageBox.TYPE_ERROR)

	def readmac(self, result, retval,extra_args=None):
		(statecallback) = extra_args
		if self.macConsole is not None:
			if retval == 0:
				self.macConsole = None
				content =result.splitlines()
                                for x in content:
                                        if x.startswith('0x00000010:'):
                                                macline = x.split()
                                if len(macline) < 10:
                                        print 'mac dump read error'
                                        retrun
				mac = macline[5]+":"+macline[6]+":"+macline[7]+":"+macline[8]+":"+macline[9]+":"+macline[10]
				self["stattext"].setText(("now : "+mac))
 	
	def getmacaddr(self):
		if self.NetworkState==0:
			return
		try:
			cmd = "nanddump -b -o -l 64 -p /dev/mtd4"
			self.macConsole = Console()	
			self.macConsole.ePopen(cmd, self.readmac)	
		except:
			return
			
	def keyleft(self):
		if self.NetworkState==0 or self.pingok<1:
			return
		macaddress = long(self.macaddr,16)-1
		if macaddress < 0 :
			macaddress = 0xffffffffffff
		self.macaddr = "%012x"%macaddress
		self.displaymac()

	def keyright(self):
		if self.NetworkState==0 or self.pingok<1:
			return
		macaddress = long(self.macaddr,16)+1
		if macaddress > 0xffffffffffff:
			macaddress = 0
		self.macaddr = "%012x"%macaddress
		self.displaymac()

	def displaymac(self):
		macaddr= self.macaddr
		self["text"].setText(("%02x:%02x:%02x:%02x:%02x:%02x"%(int(macaddr[0:2],16),int(macaddr[2:4],16),int(macaddr[4:6],16),int(macaddr[6:8],16),int(macaddr[8:10],16),int(macaddr[10:12],16))))

	def keyOk(self):
		if self.NetworkState==0 or self.pingok<1:
			return
		try:
			macaddr = self.macaddr
#make_mac_sector 00-99-99-99-00-00 > /tmp/mac.sector
#flash_eraseall /dev/mtd4
#nandwrite /dev/mtd4 /tmp/mac.sector -p			
			cmd = "make_mac_sector %02x-%02x-%02x-%02x-%02x-%02x > /tmp/mac.sector"%(int(macaddr[0:2],16),int(macaddr[2:4],16),int(macaddr[4:6],16),int(macaddr[6:8],16),int(macaddr[8:10],16),int(macaddr[10:12],16))
			system(cmd)
			system("flash_eraseall /dev/mtd4")
			system("nandwrite /dev/mtd4 /tmp/mac.sector -p")
			macaddress = long(macaddr,16)+1
			if macaddress > 0xffffffffffff:
				macaddress = 0
			macaddr = "%012x"%macaddress
			macwritetext = "MAC:%02x:%02x:%02x:%02x:%02x:%02x"%(int(macaddr[0:2],16),int(macaddr[2:4],16),int(macaddr[4:6],16),int(macaddr[6:8],16),int(macaddr[8:10],16),int(macaddr[10:12],16))
			self.macfd.seek(0)
			self.macfd.write(macwritetext)
                        self.macfd.close()
                        system("sync")
			self.macaddr = macaddr
			self.close()
		except:
			self.session.open( MessageBox, _("Mac address fail"), MessageBox.TYPE_ERROR)
			global ethtest
			ethtest = 0
			self.close()		

	def keyCancel(self):
		if self.pingok == -1:
			return
		if self.macfd != 0:
			self.macfd.close()
		global ethtest
		ethtest = 0
		self.close()


sccitest = 0

class ScCiTest(Screen):
	skin = """
		<screen position="120,225" size="440,200" title="CI Smartcard Test" >
			<widget name="testlist" position="10,0" size="340,120" />
			<widget name="resultlist" position="370,0" size="60,120" />
			<eLabel text=" " position="5,125" zPosition="-1" size="430,5" backgroundColor="#02e1e8e6" />		
			<widget name="text" position="10,140" size="420,50" font="Regular;25" />
		</screen>"""
	step=1
	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions","OkCancelActions"],
		{
			"ok": self.keyOk,
			"up": self.up,
			"down":self.down,
			"cancel": self.keyCancel,
		}, -2)

		Screen.__init__(self, session)
		tlist = []
		tlist.append(("Smartcard 1 Test",0))
		tlist.append(("Smartcard 2 Test",1))
		tlist.append(("CI 1 Test",2))
		tlist.append(("CI 2 Test",3))
		self["testlist"] = MenuList(tlist)
		self.rlist = []
		for x in range(4):
			self.rlist.append((".."))
		self["resultlist"] = TestResultList(self.rlist)
		self.result = 0
		self.removecard = eTimer()
		self.removecard.callback.append(self.remove_card)
		self["text"]=Label(("Press OK Key"))
		self.camstate= eTimer()
		self.camstate.callback.append(self.cam_state)
		self.camtry = 5
		self.camstep = 0

	def keyCancel(self):
		global sccitest
		print "result ", self.result
		if self.result==15:
			sccitest=1
		self.resetSource()
		self.close()

	def up(self):
		self["text"].setText(_("Press OK Key"))
		self["testlist"].instance.moveSelection(self["testlist"].instance.moveUp)
		
	def down(self):
		self["text"].setText(_("Press OK Key"))
		self["testlist"].instance.moveSelection(self["testlist"].instance.moveDown)
		
	def keyOk(self):
		print "line - ",self["testlist"].getCurrent()[1]
		index = self["testlist"].getCurrent()[1]
		result = 0
		if index==0 or index==1:		
			self["text"].setText(_("Insert Card?"))
			self.ScTest(True)
		elif index ==2 or index==3:
			self["text"].setText(_("Insert Cam"))
			self.CamTest()

	def CamTest(self):
		self.camtry = 10
		self.camstep = 1
		self.camstate.start(1000,True)		

	def setSource(self, cislot):
		filename = ("/proc/stb/tsmux/ci%d_input"%cislot)
		fd = open(filename,'w')
		fd.write('A')
		fd.close()

	def setInputSource(self, cislot):
		fd=open("/proc/stb/tsmux/input0","w")
		if cislot==0:
			fd.write("CI0")
		else:
			fd.write("CI1")
		fd.close()
			
	def resetSource(self):
		fd=open("/proc/stb/tsmux/input0","w")
		fd.write("A")
		fd.close()
#		fd = open("/proc/stb/tsmux/ci0_input","w")
#		fd.write("CI0")
#		fd.close()
#		fd = open("/proc/stb/tsmux/ci1_input","w")
#		fd.write("CI1")
#		fd.close()

	def channelstart(self):
		ref = eServiceReference("1:0:19:1324:3EF:1:C00000:0:0:0")
		ref.setData(0,0x19)
		ref.setData(1,0x83)
		ref.setData(2,0x6)
		ref.setData(3,0x85)
		ref.setData(4,0x640000)
		self.session.nav.playService(ref)

	def channelstop(self):
		self.session.nav.stopService() # try to disable foreground service		
	
	def cam_state(self):
		index = self["testlist"].getCurrent()[1] 
		if (index-2)==0:
			slot = 1
		else:
			slot = 0
		print 'cam_state', self.camstep,self.camtry
		if self.camstep == 1:
			state = eDVBCI_UI.getInstance().getState(slot)
			print 'stat',state
			if state == 1:
				self.camstep=2
				self.camtry=10
				self["text"].setText(_("Getting Cam name...."))
				self.camstate.start(5000,True)
			else:
				self.camtry-=1
				if self.camtry>0:
					self.camstate.start(1000,True)
				else:
					self.session.open( MessageBox, _("NO_NOT_INSERTED"), MessageBox.TYPE_ERROR)
					self.rlist[index]="fail"
					self["resultlist"].updateList(self.rlist)

		elif self.camstep == 2:
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			print 'appname',appname
			if appname is None:
				self.camtry-=1
				if self.camtry>0:
					self.camstate.start(1000,True)
				else:
					self.session.open( MessageBox, _("NO_GET_APPNAME"), MessageBox.TYPE_ERROR)
					self.rlist[index]="fail"
					self["resultlist"].updateList(self.rlist)
			else:
				self["text"].setText(_("Get Cam name : %s"%appname+". \n Remove Cam!"))
				self.channelstart()
				self.setInputSource(slot)
				self.setSource(slot)
				self.camstep=3
				self.camtry=30
				self.camstate.start(1000,True)		
		elif self.camstep==3:
			state = eDVBCI_UI.getInstance().getState(slot)
			print 'stat', state
			if state == 0:
				self.channelstop()
				self.result += (1<<index)
				print self.result
				self.rlist[index]="pass"
				self["text"].setText(_("Press OK Key"))
				self["resultlist"].updateList(self.rlist)				
				if index==2:
					self.down()
				elif index == 3:
					self.keyCancel()
			else:
				self.camtry-=1
				if self.camtry>0:
					self.camstate.start(1000,True)
				else:
					self.channelstop()
					self.session.open( MessageBox, _("NO_REMOVE_CAM"), MessageBox.TYPE_ERROR)
					self.rlist[index]="fail"
					self["resultlist"].updateList(self.rlist)

	def check_smart_card(self,which):
		index = which
		result  = 0
		if which==0:
			result = eSctest.getInstance().check_smart_card("/dev/sci0")
		elif which ==1:
			result = eSctest.getInstance().check_smart_card("/dev/sci1")
		else:
			result = -1

		print result			
		
		if result == 0:
			print 'pass'
		else:
			if result ==-1:
				self.session.open( MessageBox, _("1:NO_DEV_FOUND"), MessageBox.TYPE_ERROR)
			elif result == -2:
				self.session.open( MessageBox, _("1:SC_NOT_INSERTED"), MessageBox.TYPE_ERROR)
			elif result == -3:
				self.session.open( MessageBox, _("1:SC_NOT_VALID_ATR"), MessageBox.TYPE_ERROR)
			elif result == -5:
				self.session.open( MessageBox, _("1:SC_READ_TIMEOUT"), MessageBox.TYPE_ERROR)
			self.rlist[which]="fail"
			self["resultlist"].updateList(self.rlist)
		return result
		
	def remove_card(self):
		index = self["testlist"].getCurrent()[1]
		if index==0:
			result = eSctest.getInstance().eject_smart_card("/dev/sci0")	
		elif index==1:
			result = eSctest.getInstance().eject_smart_card("/dev/sci1")	
		print 'remove result' ,result
		if result == 0:
			self.rlist[index]="pass"
			self.result += (1<<index)
		else:
			if result ==-1:
				self.session.open( MessageBox, _("2:NO_DEV_FOUND"), MessageBox.TYPE_ERROR)
			elif result == -2:
				self.session.open( MessageBox, _("2:SC_NOT_INSERTED"), MessageBox.TYPE_ERROR)
			elif result == -3:
				self.session.open( MessageBox, _("2:SC_NOT_VALID_ATR"), MessageBox.TYPE_ERROR)
			elif result == -4:
				self.session.open( MessageBox, _("2:SC_NOT_REMOVED"), MessageBox.TYPE_ERROR)
			self.rlist[index]="fail"
		self["resultlist"].updateList(self.rlist)
		self["text"].setText(_("Press OK Key"))
		self.down()
		return result
	

	def ScTest(self, yesno):
		if yesno==False:
			return
		index = self["testlist"].getCurrent()[1]
		result = self.check_smart_card(index)
		if result==0:
			self.removecard.start(100,True)
			self["text"].setText(_("Read Ok. Remove Card!"))
		else:
			return

smartcardtest = 0

class SmartCardTest(Screen):
	skin = """
		<screen position="300,240" size="160,120" title="SmartCard Test" >
			<widget name="text" position="10,10" size="140,100" font="Regular;22" />
		</screen>"""

	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions"],
		{
			"cancel": self.keyCancel,
			"ok" : self.keyCancel
		}, -2)

		Screen.__init__(self, session)
#		self["text"]=Label(("Press Key LEFT"))
		self["text"]=Label(("Testing Smartcard 1..."))
		self.step = 0
		self.smartcardtimer = eTimer()
		self.smartcardtimer.callback.append(self.check_smart_card)
		self.smartcardtimer.start(100,True)
		self.closetimer = eTimer()
		self.closetimer.callback.append(self.close)
		self.smartcard=0
		global smartcardtest
		smartcardtest = 0
		self.Testmode = 0
		self.model = 0
		self.check_mode()

	def check_mode(self):
		try:
			fd = open("/proc/stb/info/version","r")
			version = fd.read()
			if int(version,16) <= 0x1200A3:
				self.Testmode = 0
			else:
				self.Testmode = 1
			if int(version,16) < 0x130000:
				self.model = 0
			elif int(version,16) > 0x140000:
				self.model = 1
		except:
			self.Testmode = 0

	def check_smart_card(self):
		global smartcardtest
		index = self.smartcard
		result  = 0
		if index==0:
			if self.Testmode==0:
				result = eSctest.getInstance().check_smart_card("/dev/sci0")
			else:
				result = eSctest.getInstance().n_check_smart_card("/dev/sci0")			
		elif index ==1:
			if self.Testmode==0:
				result = eSctest.getInstance().check_smart_card("/dev/sci1")
			else:
				result = eSctest.getInstance().n_check_smart_card("/dev/sci1")			
		else:
			result = -1

		print result			
		
		if result == 0:
			print 'pass'
			if(index== 0 and self.model== 0):
				self.smartcard = 1
				self["text"].setText(_("Testing Smartcard 2..."))
				self.smartcardtimer.start(100,True)
				return
			elif (index==1 or self.model==1):
				smartcardtest = 1
#				self.session.open( MessageBox, _("Smart Card OK!!"), MessageBox.TYPE_INFO,2)
				self.step = 1
				self["text"].setText(_("Smart Card OK!!"))
				self.closetimer.start(2000,True)
				self.smartcardtimer.stop()
#			self.session.openWithCallback(self.check6, MessageBox, _("Scart loop ok?"), MessageBox.TYPE_INFO)
		else:
#			if result ==-1:
#				self.session.open( MessageBox, _("%d:NO_DEV_FOUND"%(index+1)), MessageBox.TYPE_ERROR)
#			elif result == -2:
#				self.session.open( MessageBox, _("%d:SC_NOT_INSERTED"%(index+1)), MessageBox.TYPE_ERROR)
#			elif result == -3:
#				self.session.open( MessageBox, _("%d:SC_NOT_VALID_ATR"%(index+1)), MessageBox.TYPE_ERROR)
#			elif result == -5:
#				self.session.open( MessageBox, _("%d:SC_READ_TIMEOUT"%(index+1)), MessageBox.TYPE_ERROR)
			if(index==0):
				self["text"].setText(_("Smart Card 1 Error!\nerrorcode=%d"%result))
			elif (index==1):
				self["text"].setText(_("Smart Card 2 Error!\nerrorcode=%d"%result))
			self.closetimer.start(2000,True)
			self.smartcardtimer.stop()

				
	def keyCancel(self):
		self.close()

	

fronttest = 0

class FrontTest(Screen):
	skin = """
		<screen position="260,240" size="200,180" title="Front Test" >
			<widget name="text" position="10,10" size="180,160" font="Regular;22" />
		</screen>"""

	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions"],
		{
			"ok": self.keyOk,
			"up":self.keyUp,
			"down":self.keyDown,			
			"cancel": self.keyCancel,
		}, -2)

		Screen.__init__(self, session)
		self["text"]=Label(("Wheel LEFT"))
		self.step = 1
		
		self.fronttimer= eTimer()
		self.fronttimer.callback.append(self.FrontAnimate)
		self.frontturnonoff = 0
		eSctest.getInstance().VFD_Open()
		self.keytimeout = eTimer()
		self.keytimeout.callback.append(self.KeyTimeOut)
		self.keytimeout.start(5000,True)

	def KeyTimeOut(self):
		if self.step == 1:
			self["text"].setText(("Wheel LEFT ERROR"))
		elif self.step ==2 :
			self["text"].setText(("Wheel RIGHT ERROR"))
		elif self.step == 3:
			self["text"].setText(("Wheel BUTTON ERROR"))
		self.step = 0
#		self.keyCancel()
				
	def keyCancel(self):
		global fronttest
		self.fronttimer.stop()
		eSctest.getInstance().VFD_Close()
		if self.step==4:
			fronttest = 1
		else:
			fronttest = 0
		self.close()

	def keyDown(self):
		if self.step==2:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step = 3
			self["text"].setText(_("Press Front Wheel"))

	def keyUp(self):
		if self.step==1:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step=2
			self["text"].setText(_("Wheel RIGHT"))
#		else:
#			print ""

	def keyOk(self):
		if self.step == 3:
			self.keytimeout.stop()
			self.step =4
			self.fronttimer.start(1000,True)
			self["text"].setText(("Front Test OK!\nPress Exit Key"))
#		elif self.step==4:
#			global fronttest
#			self.fronttimer.stop()
#			eSctest.getInstance().VFD_Close()
#			fronttest = 1
#			self.close()

	def FrontAnimate(self):
		if (self.frontturnonoff==0):
			eSctest.getInstance().turnon_VFD()
			self.frontturnonoff = 1
		else:
			self.frontturnonoff = 0
			eSctest.getInstance().turnoff_VFD()
		self.fronttimer.start(1000,True)
		

class FrontTest_solo(Screen):
	skin = """
		<screen position="260,240" size="200,180" title="Front Test" >
			<widget name="text" position="10,10" size="180,160" font="Regular;22" />
		</screen>"""

	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions","GlobalActions"],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
			"left": self.keyleft,
			"right": self.keyright,
			"power_down": self.keypower,
			"volumeUp": self.keyvolup,
			"volumeDown": self.keyvoldown,
		}, -2)

		Screen.__init__(self, session)
		self["text"]=Label(("Press Front STANDBY"))
		self.step = 1
		
		self.fronttimer= eTimer()
		self.fronttimer.callback.append(self.FrontAnimate)
		self.frontturnonoff = 0
		eSctest.getInstance().VFD_Open()
		self.keytimeout = eTimer()
		self.keytimeout.callback.append(self.KeyTimeOut)
		self.keytimeout.start(5000,True)

	def KeyTimeOut(self):
		if self.step == 1:
			self["text"].setText(("Front STANDBY ERROR\nPress exit!"))
		elif self.step == 2 :
			self["text"].setText(("Front CH - ERROR\nPress exit!"))
		elif self.step == 3:
			self["text"].setText(("Front CH + ERROR\nPress exit!"))
		elif self.step == 4 :
			self["text"].setText(("Front VOL - ERROR\nPress exit!"))
		elif self.step == 5:
			self["text"].setText(("Front VOL + ERROR\nPress exit!"))
			
		self.step = 0
#		self.keyCancel()

	def keypower(self):
		if self.step== 1:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step = 2
			self["text"].setText(_("Press Front CH -"))
			
	def keyright(self):
		if self.step== 3:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step = 4
			self["text"].setText(_("Press Front VOL -"))
			
	def keyleft(self):
		if self.step== 2:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step = 3
			self["text"].setText(_("Press Front CH +"))

	def keyvolup(self):
		if self.step== 5:
			self.keytimeout.stop()
			self.step = 6
			self.fronttimer.start(1000,True)
			self["text"].setText(_("Front LED OK?\n\nyes-ok\nno-exit"))			
#			self["text"].setText(("Front Test OK!\nPress Exit Key"))
		
	def keyvoldown(self):
		if self.step== 4:
			self.keytimeout.stop()
			self.keytimeout.start(5000,True)
			self.step = 5
			self["text"].setText(_("Press Front VOL +"))

	def checkled(self, yesno):
		if yesno :
			self.step=6
		else:
			self.step=0
		self.keyCancel()
			
	def keyCancel(self):
		global fronttest
		self.fronttimer.stop()
		eSctest.getInstance().VFD_Close()
		fronttest = 0
		self.close()

	def keyOk(self):
		global fronttest
		self.fronttimer.stop()
		eSctest.getInstance().VFD_Close()
		if self.step == 6:
			fronttest = 1
		self.close()

	def FrontAnimate(self):
		if (self.frontturnonoff==0):
			eSctest.getInstance().turnon_VFD()
			self.frontturnonoff = 1
		else:
			self.frontturnonoff = 0
			eSctest.getInstance().turnoff_VFD()
		self.fronttimer.start(1000,True)


	

rstest = 0

import select

class RS232Test(Screen):
	skin = """
		<screen position="300,240" size="160,100" title="RS232 Test" >
			<widget name="text" position="10,10" size="140,80" font="Regular;22" />
		</screen>"""
	step=1
	def __init__(self, session):
		self["actions"] = ActionMap(["DirectionActions", "OkCancelActions"],
		{
			"cancel": self.keyCancel,
		}, -2)

		Screen.__init__(self, session)
		self["text"]=Label(("Press \"Enter\" Key"))
		self.timer = eTimer()
		self.timer.callback.append(self.checkrs232)
		self.timer.start(100, True)

	def checkrs232(self):
		global rstest
		try:
			rs=open('/dev/ttyS0','r')
			rd = [rs]
			r,w,e = select.select(rd, [], [], 10)
			if r:
				input = rs.read(1)
				if input == "\n":
#				if input == "m":
					rstest = 1
				else:
					rstest = 0 
			else:
				rstest = 0
		except:
			print 'error'
			rstest = 0
		self.close()

	def keyCancel(self):
		self.close()

Agingresult = 0

class AgingTest(Screen):
	skin = """
		<screen position="200,240" size="250,100" title="Aging Test" >
			<widget name="text1" position="10,10" size="230,40" font="Regular;22" />
			<widget name="text2" position="10,50" size="230,40" font="Regular;22" />
		</screen>"""
	step=1
	def __init__(self, session):
		self["actions"] = ActionMap(["WizardActions","GlobalActions"],
		{
			"agingend": self.keyEnd,
			"agingfinish": self.keyFinish,
			"volumeUp": self.nothing,
			"volumeDown": self.nothing,
			"volumeMute": self.nothing,		
		}, -2)

		Screen.__init__(self, session)
		self["text1"]=Label(("Exit - Press Pause Key"))
		self["text2"]=Label(("Reset - Press Stop Key"))
#		self.servicelist = ServiceList()
#		self.oldref = session.nav.getCurrentlyPlayingServiceReference()
#		print "oldref",self.oldref
#		session.nav.stopService() # try to disable foreground service
#		self.chstart()
		self.tunerlock = 0
		self.tuningtimer = eTimer()
		self.tuningtimer.callback.append(self.updateStatus)
#		self.tuningtimer.start(2000,True)


	def updateStatus(self):
		result = eSctest.getInstance().getFrontendstatus(0)		
		hv = "Ver"
			
		print "eSctest.getInstance().getFrontendstatus - %d"%result
		if result == 0:
			self.tunerlock = 0
			self.session.nav.stopService()
			self.session.open( MessageBox, _("Tune 1 Ver Locking Fail..."), MessageBox.TYPE_ERROR)	
		elif result==1 :
			self.tunerlock = 1
		else:
			self.tunerlock = 0
			self.session.nav.stopService()
			self.session.open( MessageBox, _("Tune 1 Ver Error %d..."%result), MessageBox.TYPE_ERROR)	


	def nothing(self):
		print "nothing"

	def chstart(self):
		if self.oldref is None:
			eref = eServiceReference("1:0:19:1324:3EF:1:C00000:0:0:0")
			serviceHandler = eServiceCenter.getInstance()
			servicelist = serviceHandler.list(eref)
			if not servicelist is None:
				ref = servicelist.getNext()
			else:
				ref = self.getCurrentSelection()
				print "servicelist none"
		else:
			ref = self.oldref
		self.session.nav.stopService() # try to disable foreground service
		ref.setData(0,0x19)
		ref.setData(1,0x83)
		ref.setData(2,0x6)
		ref.setData(3,0x85)
		ref.setData(4,0x640000)
		self.session.nav.playService(ref)

	def keyEnd(self):
		global Agingresult
		Agingresult = 0
		self.session.nav.stopService() # try to disable foreground service
		self.close()

	def keyFinish(self):
		global Agingresult
		Agingresult = 1
		self.session.nav.stopService() # try to disable foreground service
		self.close()
		
session = None

	
def cleanup():
	global Session
	Session = None
	global Servicelist
	Servicelist = None

def main(session, servicelist, **kwargs):
	global Session
	Session = session
	global Servicelist
	Servicelist = servicelist
	bouquets = Servicelist.getBouquetList()
	global bouquetSel
	bouquetSel = Session.openWithCallback(cleanup, FactoryTest)

#def Plugins(**kwargs):
#	return PluginDescriptor(name=_("Factory Test"), description="Test App for Factory", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
