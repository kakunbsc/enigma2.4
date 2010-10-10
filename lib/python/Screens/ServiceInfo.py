from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from ServiceReference import ServiceReference
from enigma import eListboxPythonMultiContent, eListbox, gFont, iServiceInformation, eServiceCenter
from Tools.Transponder import ConvertToHumanReadable

RT_HALIGN_LEFT = 0

TYPE_TEXT = 0
TYPE_VALUE_HEX = 1
TYPE_VALUE_DEC = 2
TYPE_VALUE_HEX_DEC = 3
TYPE_SLIDER = 4

def to_unsigned(x):
	return x & 0xFFFFFFFF

def ServiceInfoListEntry(a, b, valueType=TYPE_TEXT, param=4):
	print "b:", b
	if not isinstance(b, str):
		if valueType == TYPE_VALUE_HEX:
			b = ("0x%0" + str(param) + "x") % to_unsigned(b)
		elif valueType == TYPE_VALUE_DEC:
			b = str(b)
		elif valueType == TYPE_VALUE_HEX_DEC:
			b = ("0x%0" + str(param) + "x (%dd)") % (to_unsigned(b), b)
		else:
			b = str(b)

	return [
		#PyObject *type, *px, *py, *pwidth, *pheight, *pfnt, *pstring, *pflags;
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 200, 30, 0, RT_HALIGN_LEFT, ""),
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 200, 25, 0, RT_HALIGN_LEFT, a),
		(eListboxPythonMultiContent.TYPE_TEXT, 220, 0, 350, 25, 0, RT_HALIGN_LEFT, b)
	]

class ServiceInfoList(HTMLComponent, GUIComponent):
	def __init__(self, source):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.list = source
		self.l.setList(self.list)
		self.l.setFont(0, gFont("Regular", 23))
		self.l.setItemHeight(25)

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		self.instance.setContent(self.l)

TYPE_SERVICE_INFO = 1
TYPE_TRANSPONDER_INFO = 2

class ServiceInfo(Screen):
	def __init__(self, session, serviceref=None):
		Screen.__init__(self, session)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"red": self.information,
			"green": self.pids,
			"yellow": self.transponder,
			"blue": self.tuner
		}, -1)

		if serviceref:
			self.type = TYPE_TRANSPONDER_INFO
			self["red"] = Label()
			self["green"] = Label()
			self["yellow"] = Label()
			self["blue"] = Label()
			info = eServiceCenter.getInstance().info(serviceref)
			self.transponder_info = info.getInfoObject(serviceref, iServiceInformation.sTransponderData)
			# info is a iStaticServiceInformation, not a iServiceInformation
			self.info = None
			self.feinfo = None
		else:
			self.type = TYPE_SERVICE_INFO
			self["red"] = Label(_("Serviceinfo"))
			self["green"] = Label(_("PIDs"))
			self["yellow"] = Label(_("Transponder"))
			self["blue"] = Label(_("Tuner status"))
			service = session.nav.getCurrentService()
			if service is not None:
				self.info = service.info()
				self.feinfo = service.frontendInfo()
				print self.info.getInfoObject(iServiceInformation.sCAIDs);
			else:
				self.info = None
				self.feinfo = None

		tlist = [ ]

		self["infolist"] = ServiceInfoList(tlist)
		self.onShown.append(self.information)

	def information(self):
		if self.type == TYPE_SERVICE_INFO:
			if self.session.nav.getCurrentlyPlayingServiceReference():
				name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
				refstr = self.session.nav.getCurrentlyPlayingServiceReference().toString()
			else:
				name = "N/A"
				refstr = "N/A"
			aspect = self.getServiceInfoValue(iServiceInformation.sAspect)
			if aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ):
				aspect = "4:3"
			else:
				aspect = "16:9"
			width = self.info and self.info.getInfo(iServiceInformation.sVideoWidth) or -1
			height = self.info and self.info.getInfo(iServiceInformation.sVideoHeight) or -1
			if width != -1 and height != -1:
				Labels = ( ("Name", name, TYPE_TEXT),
						   ("Provider", self.getServiceInfoValue(iServiceInformation.sProvider), TYPE_TEXT),
						   ("Videoformat", aspect, TYPE_TEXT),
						   ("Videosize", "%dx%d" %(width, height), TYPE_TEXT),
						   ("Namespace", self.getServiceInfoValue(iServiceInformation.sNamespace), TYPE_VALUE_HEX, 8),
						   ("Service Reference", refstr, TYPE_TEXT))
			else:
				Labels = ( ("Name", name, TYPE_TEXT),
						   ("Provider", self.getServiceInfoValue(iServiceInformation.sProvider), TYPE_TEXT),
						   ("Videoformat", aspect, TYPE_TEXT),
						   ("Namespace", self.getServiceInfoValue(iServiceInformation.sNamespace), TYPE_VALUE_HEX, 8),
						   ("Service Reference", refstr, TYPE_TEXT))
			self.fillList(Labels)
		else:
			if self.transponder_info:
				tp_info = ConvertToHumanReadable(self.transponder_info)
				conv = { "tuner_type" 		: _("Transponder Type"),
						 "system"			: _("System"),
						 "modulation"		: _("Modulation"),
						 "orbital_position" : _("Orbital Position"),
						 "frequency"		: _("Frequency"),
						 "symbol_rate"		: _("Symbolrate"),
						 "bandwidth"		: _("Bandwidth"),
						 "polarization"		: _("Polarization"),
						 "inversion"		: _("Inversion"),
						 "pilot"			: _("Pilot"),
						 "rolloff"			: _("Rolloff"),
						 "fec_inner"		: _("FEC"),
						 "code_rate_lp"		: _("Coderate LP"),
						 "code_rate_hp"		: _("Coderate HP"),
						 "constellation"	: _("Constellation"),
						 "transmission_mode": _("Transmission Mode"),
						 "guard_interval" 	: _("Guard Interval"),
						 "hierarchy_information": _("Hierarchy Information") }
				Labels = [(conv[i], tp_info[i], TYPE_VALUE_DEC) for i in tp_info.keys()]
				self.fillList(Labels)

	def pids(self):
		if self.type == TYPE_SERVICE_INFO:
			Labels = ( ("VideoPID", self.getServiceInfoValue(iServiceInformation.sVideoPID), TYPE_VALUE_HEX_DEC, 4),
					   ("AudioPID", self.getServiceInfoValue(iServiceInformation.sAudioPID), TYPE_VALUE_HEX_DEC, 4),
					   ("PCRPID", self.getServiceInfoValue(iServiceInformation.sPCRPID), TYPE_VALUE_HEX_DEC, 4),
					   ("PMTPID", self.getServiceInfoValue(iServiceInformation.sPMTPID), TYPE_VALUE_HEX_DEC, 4),
					   ("TXTPID", self.getServiceInfoValue(iServiceInformation.sTXTPID), TYPE_VALUE_HEX_DEC, 4),
					   ("TSID", self.getServiceInfoValue(iServiceInformation.sTSID), TYPE_VALUE_HEX_DEC, 4),
					   ("ONID", self.getServiceInfoValue(iServiceInformation.sONID), TYPE_VALUE_HEX_DEC, 4),
					   ("SID", self.getServiceInfoValue(iServiceInformation.sSID), TYPE_VALUE_HEX_DEC, 4))
			self.fillList(Labels)
	
	def showFrontendData(self, real):
		if self.type == TYPE_SERVICE_INFO:
			frontendData = self.feinfo and self.feinfo.getAll(real)
			Labels = self.getFEData(frontendData)
			self.fillList(Labels)
	
	def transponder(self):
		if self.type == TYPE_SERVICE_INFO:
			self.showFrontendData(True)
		
	def tuner(self):
		if self.type == TYPE_SERVICE_INFO:
			self.showFrontendData(False)

	def getFEData(self, frontendDataOrg):
		if frontendDataOrg and len(frontendDataOrg):
			frontendData = ConvertToHumanReadable(frontendDataOrg)
			if frontendDataOrg["tuner_type"] == "DVB-S":
				return (("NIM", ('A', 'B', 'C', 'D')[frontendData["tuner_number"]], TYPE_TEXT),
							("Type", frontendData["system"], TYPE_TEXT),
							("Modulation", frontendData["modulation"], TYPE_TEXT),
							("Orbital position", frontendData["orbital_position"], TYPE_VALUE_DEC),
							("Frequency", frontendData["frequency"], TYPE_VALUE_DEC),
							("Symbolrate", frontendData["symbol_rate"], TYPE_VALUE_DEC),
							("Polarization", frontendData["polarization"], TYPE_TEXT),
							("Inversion", frontendData["inversion"], TYPE_TEXT),
							("FEC inner", frontendData["fec_inner"], TYPE_TEXT),
							("Pilot", frontendData.get("pilot", None), TYPE_TEXT),
							("Rolloff", frontendData.get("rolloff", None), TYPE_TEXT))
			elif frontendDataOrg["tuner_type"] == "DVB-C":
				return (("NIM", ('A', 'B', 'C', 'D')[frontendData["tuner_number"]], TYPE_TEXT),
						("Type", frontendData["tuner_type"], TYPE_TEXT),
						("Frequency", frontendData["frequency"], TYPE_VALUE_DEC),
						("Symbolrate", frontendData["symbol_rate"], TYPE_VALUE_DEC),
						("Modulation", frontendData["modulation"], TYPE_TEXT),
						("Inversion", frontendData["inversion"], TYPE_TEXT),
						("FEC inner", frontendData["fec_inner"], TYPE_TEXT))
			elif frontendDataOrg["tuner_type"] == "DVB-T":
				return (("NIM", ('A', 'B', 'C', 'D')[frontendData["tuner_number"]], TYPE_TEXT),
						("Type", frontendData["tuner_type"], TYPE_TEXT),
						("Frequency", frontendData["frequency"], TYPE_VALUE_DEC),
						("Inversion", frontendData["inversion"], TYPE_TEXT),
						("Bandwidth", frontendData["bandwidth"], TYPE_VALUE_DEC),
						("CodeRateLP", frontendData["code_rate_lp"], TYPE_TEXT),
						("CodeRateHP", frontendData["code_rate_hp"], TYPE_TEXT),
						("Constellation", frontendData["constellation"], TYPE_TEXT),
						("Transmission Mode", frontendData["transmission_mode"], TYPE_TEXT),
						("Guard Interval", frontendData["guard_interval"], TYPE_TEXT),
						("Hierarchy Inform.", frontendData["hierarchy_information"], TYPE_TEXT))
		return [ ]

	def fillList(self, Labels):
		tlist = [ ]

		for item in Labels:
			if item[1] is None:
				continue;
			value = item[1]
			if len(item) < 4:
				tlist.append(ServiceInfoListEntry(item[0]+":", value, item[2]))
			else:
				tlist.append(ServiceInfoListEntry(item[0]+":", value, item[2], item[3]))

		self["infolist"].l.setList(tlist)

	def getServiceInfoValue(self, what):
		if self.info is None:
			return ""
		
		v = self.info.getInfo(what)
		if v == -2:
			v = self.info.getInfoString(what)
		elif v == -1:
			v = "N/A"

		return v
