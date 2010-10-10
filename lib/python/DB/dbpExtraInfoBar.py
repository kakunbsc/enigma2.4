from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config
from enigma import eTimer, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable
from dbpTool import dbpTool, parse_ecm
import os
import re

t = dbpTool()

class dbpEI(Screen):
	__module__ = __name__
	
	def readEcmFile(self):
		emuActive = t.readEmuActive()
		return t.readEcmInfoFile(emuActive)
	
	def readEmuName(self):
		emuActive = t.readEmuActive()
		return t.readEmuName(emuActive)
	
	def readCsName(self):
		csActive = t.readSrvActive()
		return t.readSrvName(csActive)
	
	def showEmuName(self):
		self["emuname"].setText(self.readEmuName())
		csName = self.readCsName()
		if csName != 'None':
			self["emuname"].setText(self["emuname"].getText() + " / " + csName )
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.systemCod = [
				"beta_no", "beta_emm", "beta_ecm",
				"seca_no", "seca_emm", "seca_ecm",
				"irdeto_no", "irdeto_emm", "irdeto_ecm",
				"cw_no", "cw_emm", "cw_ecm",
				"nagra_no", "nagra_emm", "nagra_ecm", 
				"nds_no", "nds_emm", "nds_ecm",
				"via_no", "via_emm", "via_ecm", "conax_no",
				"conax_emm", "conax_ecm",
				"b_fta" , "b_card", "b_emu", "b_spider"
				]
		
		self.systemCaids = {
				"06" : "irdeto", "01" : "seca", "18" : "nagra",
				"05" : "via", "0B" : "conax", "17" : "beta",
				"0D" : "cw", "4A" : "irdeto", "09" : "nds"
				}
		
		for x in self.systemCod:
			self[x] = Label()
		self["TunerInfo"] = Label()
		self["EmuInfo"] = Label()
		self["ecmtime"] = Label()
		self["netcard"] = Label()
		self["emuname"] = Label()
		
		self.count = 0
		self.ecm_timer = eTimer()
		self.ecm_timer.timeout.get().append(self.__updateEmuInfo)
		self.emm_timer = eTimer()
		self.emm_timer.timeout.get().append(self.__updateEMMInfo)
		self.__evStart()
		
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evStart: self.__evStart,
				iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
				iPlayableService.evTunedIn: self.__evTunedIn,
			})
			
		self.onShow.append(self.showEmuName)
	
	def __evStart(self):
		if self.emm_timer.isActive():
			self.emm_timer.stop()
		if self.ecm_timer.isActive():
			self.ecm_timer.stop()
		self.count = 0
		self.displayClean()	
		
	def __evTunedIn(self):
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if info is not None:
			self.emm_timer.start(config.dbp.emminfodelay.value)
			self.ecm_timer.start(config.dbp.ecminfodelay.value)
	
	def __updateEMMInfo(self):
		self.emm_timer.stop()
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if info is not None:
			self.showEMM(info.getInfoObject(iServiceInformation.sCAIDs))
	
	def __updateEmuInfo(self):
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if info is not None:
			if info.getInfo(iServiceInformation.sIsCrypted):
				if self.count < 4:
					self.count = self.count + 1
				else:
					self.ecm_timer.changeInterval(10000)
				info = parse_ecm(self.readEcmFile())
				#print info
				if info != 0:
					caid = info[0]
					pid = info[1]
					provid = info[2]
					ecmtime = info[3]
					source = info[4]
					addr = info[5]
					port = info[6]
					hops = info[7]
					
					if ecmtime > 0:
						self["ecmtime"].setText("ECM Time: " + str(ecmtime) + " msec")
					if provid !='':
						self["EmuInfo"].setText("Provider: " + provid)
					if pid !='':
						self["EmuInfo"].setText(self["EmuInfo"].getText() + " Pid: " + pid)
					
					self["b_fta"].hide()
					self["b_card"].hide()
					self["b_emu"].hide()
					self["b_spider"].hide()
					
					if source == 0:
						self["netcard"].setText("Decode: Unsupported!")
					elif source == 1:
						self["b_emu"].show()
						self["netcard"].setText("Decode: Internal")
					elif source == 2:
						if addr !='':
							if (addr.find('127.0.0.1') or addr.find('localhost')) >= 0:
								self["netcard"].setText("Decode: Internal")
								self["b_card"].show()
							else:		
								self["b_spider"].show()
								if config.dbp.shownetdet.value:
										self["netcard"].setText("Source: " + addr + ":" + port)
										if hops > 0:
											self["netcard"].setText(self["netcard"].getText() + " Hops: " + str(hops))
						else:
							self["b_spider"].show()
							self["netcard"].setText("Decode: Network")
					elif source == 4:
						self["b_card"].show()
						self["netcard"].setText("Decode: slot-1")
					elif source == 5:
						self["b_card"].show()
						self["netcard"].setText("Decode: slot-2")
					
					if caid !='':
						self["EmuInfo"].setText(self["EmuInfo"].getText() + " Ca ID:" + caid)
						self.showECM(caid)
			else:
				self["EmuInfo"].setText("")
				self["ecmtime"].setText("")
				self["netcard"].setText("")
				self["b_fta"].show()

	def showECM(self, caid):
		caid = caid.lower()
		if caid.__contains__("x"):
			idx = caid.index("x")
			caid = caid[idx+1:]
			if len(caid) == 3:
				caid = "0%s" % caid
			caid = caid[:2]
			caid = caid.upper()
			if self.systemCaids.has_key(caid):
				system = self.systemCaids.get(caid)
				self[system + "_emm"].hide()
				self[system + "_ecm"].show()
	
	def int2hex(self, int):
		return "%x" % int
	
	def showEMM(self, caids):
		if caids:
			if len(caids) > 0:
				for caid in caids:
					caid = self.int2hex(caid)
					if len(caid) == 3:
						caid = "0%s" % caid
					caid = caid[:2]
					caid = caid.upper()
					if self.systemCaids.has_key(caid):
						system = self.systemCaids.get(caid)
						self[system + "_no"].hide()
						self[system + "_emm"].show()
	
	def displayClean(self):
		self["EmuInfo"].setText("")
		self["ecmtime"].setText("")
		self["netcard"].setText("")
		for x in self.systemCod:
			self[x].hide()
			if x.find('_no') >= 0:
				self[x].show()

	def __evUpdatedInfo(self):
		self["TunerInfo"].setText("")
		service = self.session.nav.getCurrentService()
		frontendInfo = service.frontendInfo()
		frontendData = frontendInfo and frontendInfo.getAll(True)
		if frontendData is not None:
			tuner_type = frontendData.get("tuner_type", "None")
			sr = str(int(frontendData.get("symbol_rate", 0) / 1000))
			freq = str(int(frontendData.get("frequency", 0) / 1000))
			if tuner_type == "DVB-S":
				try:
					orb = {
									3590:'Thor/Intelsat (1.0W)',3560:'Amos (4.0W)',3550:'Atlantic Bird (5.0W)',3530:'Nilesat/Atlantic Bird (7.0W)',
									3520:'Atlantic Bird (8.0W)',3475:'Atlantic Bird (12.5W)',3460:'Express (14.0W)', 3450:'Telstar (15.0W)',
									3420:'Intelsat (18.0W)',3380:'Nss (22.0W)',3355:'Intelsat (24.5W)', 3325:'Intelsat (27.5W)',3300:'Hispasat (30.0W)',
									3285:'Intelsat (31.5W)',3170:'Intelsat (43.0W)',3150:'Intelsat (45.0W)',
									750:'Abs (75.0E)',720:'Intelsat (72.0E)',705:'Eutelsat W5 (70.5E)',685:'Intelsat (68.5E)',620:'Intelsat 902 (62.0E)',
									600:'Intelsat 904 (60.0E)',570:'Nss (57.0E)',530:'Express AM22 (53.0E)',480:'Eutelsat 2F2 (48.0E)',450:'Intelsat (45.0E)',
									420:'Turksat 2A (42.0E)',400:'Express AM1 (40.0E)',390:'Hellas Sat 2 (39.0E)',380:'Paksat 1 (38.0E)',
									360:'Eutelsat Sesat (36.0E)',335:'Astra 1M (33.5E)',330:'Eurobird 3 (33.0E)',	328:'Galaxy 11 (32.8E)',
									315:'Astra 5A (31.5E)',310:'Turksat (31.0E)',305:'Arabsat (30.5E)',285:'Eurobird 1 (28.5E)',
									284:'Eurobird/Astra (28.2E)',282:'Eurobird/Astra (28.2E)',
									260:'Badr 3/4 (26.0E)',255:'Eurobird 2 (25.5E)',235:'Astra 1E (23.5E)',215:'Eutelsat (21.5E)',
									216:'Eutelsat W6 (21.6E)',210:'AfriStar 1 (21.0E)',192:'Astra 1F (19.2E)',160:'Eutelsat W2 (16.0E)',
									130:'Hot Bird 6,7A,8 (13.0E)',100:'Eutelsat W1 (10.0E)',90:'Eurobird 9 (9.0E)',70:'Eutelsat W3A (7.0E)',
									50:'Sirius 4 (5.0E)',48:'Sirius 4 (4.8E)',30:'Telecom 2 (3.0E)'
								}[frontendData.get("orbital_position", "None")]
				except:
					orb = 'Unsupported SAT: %s' % str([frontendData.get("orbital_position", "None")])
				pol = {
								eDVBFrontendParametersSatellite.Polarisation_Horizontal : "H",
								eDVBFrontendParametersSatellite.Polarisation_Vertical : "V",
								eDVBFrontendParametersSatellite.Polarisation_CircularLeft : "CL",
								eDVBFrontendParametersSatellite.Polarisation_CircularRight : "CR"
							}[frontendData.get("polarization", eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
				fec = {
								eDVBFrontendParametersSatellite.FEC_None : "None",
								eDVBFrontendParametersSatellite.FEC_Auto : "Auto",
								eDVBFrontendParametersSatellite.FEC_1_2 : "1/2",
								eDVBFrontendParametersSatellite.FEC_2_3 : "2/3",
								eDVBFrontendParametersSatellite.FEC_3_4 : "3/4",
								eDVBFrontendParametersSatellite.FEC_5_6 : "5/6",
								eDVBFrontendParametersSatellite.FEC_7_8 : "7/8",
								eDVBFrontendParametersSatellite.FEC_3_5 : "3/5",
								eDVBFrontendParametersSatellite.FEC_4_5 : "4/5",
								eDVBFrontendParametersSatellite.FEC_8_9 : "8/9",
								eDVBFrontendParametersSatellite.FEC_9_10 : "9/10"
							}[frontendData.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)]
				self["TunerInfo"].setText( "Freq: " + freq + " MHz, Pol: " + pol + ", Fec: " + fec + ", SR: " + sr + ", Satellite: " + orb)
			elif tuner_type == "DVB-C":
				fec = {
								eDVBFrontendParametersCable.FEC_None : "None",
								eDVBFrontendParametersCable.FEC_Auto : "Auto",
								eDVBFrontendParametersCable.FEC_1_2 : "1/2",
								eDVBFrontendParametersCable.FEC_2_3 : "2/3",
								eDVBFrontendParametersCable.FEC_3_4 : "3/4",
								eDVBFrontendParametersCable.FEC_5_6 : "5/6",
								eDVBFrontendParametersCable.FEC_7_8 : "7/8",
								eDVBFrontendParametersCable.FEC_8_9 : "8/9"
							}[frontendData.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)]
				self["TunerInfo"].setText( "Freq: " + freq + " MHz, Fec: " + fec + ", SR: " + sr )
			else:
				self["TunerInfo"].setText( "Freq: " + freq + " MHz, SR: " + sr )
