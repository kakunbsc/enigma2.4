from Tools.HardwareInfo import HardwareInfo

from config import config, ConfigSubsection, ConfigSelection, ConfigFloat, \
	ConfigSatlist, ConfigYesNo, ConfigInteger, ConfigSubList, ConfigNothing, \
	ConfigSubDict, ConfigOnOff, ConfigDateTime

from enigma import eDVBSatelliteEquipmentControl as secClass, \
	eDVBSatelliteLNBParameters as lnbParam, \
	eDVBSatelliteDiseqcParameters as diseqcParam, \
	eDVBSatelliteSwitchParameters as switchParam, \
	eDVBSatelliteRotorParameters as rotorParam, \
	eDVBResourceManager, eDVBDB

from time import localtime, mktime
from datetime import datetime

def getConfigSatlist(orbpos, satlist):
	default_orbpos = None
	for x in satlist:
		if x[0] == orbpos:
			default_orbpos = orbpos
			break
	return ConfigSatlist(satlist, default_orbpos)

def tryOpen(filename):
	try:
		procFile = open(filename)
	except IOError:
		return None
	return procFile

class SecConfigure:
	def getConfiguredSats(self):
		return self.configuredSatellites

	def addSatellite(self, sec, orbpos):
		sec.addSatellite(orbpos)
		self.configuredSatellites.add(orbpos)

	def addLNBSimple(self, sec, slotid, diseqcmode, toneburstmode = diseqcParam.NO, diseqcpos = diseqcParam.SENDNO, orbpos = 0, longitude = 0, latitude = 0, loDirection = 0, laDirection = 0, turningSpeed = rotorParam.FAST, useInputPower=True, inputPowerDelta=50, fastDiSEqC = False, setVoltageTone = True, diseqc13V = False):
		if orbpos is None or orbpos == 3601:
			return
		#simple defaults
		sec.addLNB()
		tunermask = 1 << slotid
		if self.equal.has_key(slotid):
			for slot in self.equal[slotid]:
				tunermask |= (1 << slot)
		if self.linked.has_key(slotid):
			for slot in self.linked[slotid]:
				tunermask |= (1 << slot)
		sec.setLNBSatCR(-1)
		sec.setLNBNum(1)
		sec.setLNBLOFL(9750000)
		sec.setLNBLOFH(10600000)
		sec.setLNBThreshold(11700000)
		sec.setLNBIncreasedVoltage(lnbParam.OFF)
		sec.setRepeats(0)
		sec.setFastDiSEqC(fastDiSEqC)
		sec.setSeqRepeat(0)
		sec.setCommandOrder(0)

		#user values
		sec.setDiSEqCMode(diseqcmode)
		sec.setToneburst(toneburstmode)
		sec.setCommittedCommand(diseqcpos)
		sec.setUncommittedCommand(0) # SENDNO
		#print "set orbpos to:" + str(orbpos)

		if 0 <= diseqcmode < 3:
			self.addSatellite(sec, orbpos)
			if setVoltageTone:
				if diseqc13V:
					sec.setVoltageMode(switchParam.HV_13)
				else:
					sec.setVoltageMode(switchParam.HV)
				sec.setToneMode(switchParam.HILO)
			else:
				sec.setVoltageMode(switchParam._14V)
				sec.setToneMode(switchParam.OFF)
		elif (diseqcmode == 3): # diseqc 1.2
			if self.satposdepends.has_key(slotid):
				for slot in self.satposdepends[slotid]:
					tunermask |= (1 << slot)
			sec.setLatitude(latitude)
			sec.setLaDirection(laDirection)
			sec.setLongitude(longitude)
			sec.setLoDirection(loDirection)
			sec.setUseInputpower(useInputPower)
			sec.setInputpowerDelta(inputPowerDelta)
			sec.setRotorTurningSpeed(turningSpeed)

			for x in self.NimManager.satList:
				print "Add sat " + str(x[0])
				self.addSatellite(sec, int(x[0]))
				if diseqc13V:
					sec.setVoltageMode(switchParam.HV_13)
				else:
					sec.setVoltageMode(switchParam.HV)
				sec.setToneMode(switchParam.HILO)
				sec.setRotorPosNum(0) # USALS
		
		sec.setLNBSlotMask(tunermask)

	def setSatposDepends(self, sec, nim1, nim2):
		print "tuner", nim1, "depends on satpos of", nim2
		sec.setTunerDepends(nim1, nim2)

	def linkNIMs(self, sec, nim1, nim2):
		print "link tuner", nim1, "to tuner", nim2
		sec.setTunerLinked(nim1, nim2)
		
	def getRoot(self, slotid, connto):
		visited = []
		while (self.NimManager.getNimConfig(connto).configMode.value in ("satposdepends", "equal", "loopthrough")):
			connto = int(self.NimManager.getNimConfig(connto).connectedTo.value)
			if connto in visited: # prevent endless loop
				return slotid
			visited.append(connto)
		return connto

	def update(self):
		sec = secClass.getInstance()
		self.configuredSatellites = set()
		sec.clear() ## this do unlinking NIMs too !!
		print "sec config cleared"

		self.linked = { }
		self.satposdepends = { }
		self.equal = { }

		nim_slots = self.NimManager.nim_slots

		used_nim_slots = [ ]

		for slot in nim_slots:
			if slot.type is not None:
				used_nim_slots.append((slot.slot, slot.description, slot.config.configMode.value != "nothing" and True or False, slot.isCompatible("DVB-S2")))
		eDVBResourceManager.getInstance().setFrontendSlotInformations(used_nim_slots)

		for slot in nim_slots:
			x = slot.slot
			nim = slot.config
			if slot.isCompatible("DVB-S"):
				# save what nim we link to/are equal to/satposdepends to.
				# this is stored in the *value* (not index!) of the config list
				if nim.configMode.value == "equal":
					connto = self.getRoot(x, int(nim.connectedTo.value))
					if not self.equal.has_key(connto):
						self.equal[connto] = []
					self.equal[connto].append(x)
				elif nim.configMode.value == "loopthrough":
					self.linkNIMs(sec, x, int(nim.connectedTo.value))
					connto = self.getRoot(x, int(nim.connectedTo.value))
					if not self.linked.has_key(connto):
						self.linked[connto] = []
					self.linked[connto].append(x)
				elif nim.configMode.value == "satposdepends":
					self.setSatposDepends(sec, x, int(nim.connectedTo.value))
					connto = self.getRoot(x, int(nim.connectedTo.value))
					if not self.satposdepends.has_key(connto):
						self.satposdepends[connto] = []
					self.satposdepends[connto].append(x)

		for slot in nim_slots:
			x = slot.slot
			nim = slot.config
			hw = HardwareInfo()
			if slot.isCompatible("DVB-S"):
				print "slot: " + str(x) + " configmode: " + str(nim.configMode.value)
				if nim.configMode.value in ( "loopthrough", "satposdepends", "nothing" ):
					pass
				else:
					sec.setSlotNotLinked(x)
					if nim.configMode.value == "equal":
						pass
					elif nim.configMode.value == "simple":		#simple config
						print "diseqcmode: ", nim.diseqcMode.value
						if nim.diseqcMode.value == "single":			#single
							if nim.simpleSingleSendDiSEqC.value:
								self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcA.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.AA, diseqc13V = nim.diseqc13V.value)
							else:
								self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcA.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.NONE, diseqcpos = diseqcParam.SENDNO, diseqc13V = nim.diseqc13V.value)
						elif nim.diseqcMode.value == "toneburst_a_b":		#Toneburst A/B
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcA.orbital_position, toneburstmode = diseqcParam.A, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.SENDNO, diseqc13V = nim.diseqc13V.value)
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcB.orbital_position, toneburstmode = diseqcParam.B, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.SENDNO, diseqc13V = nim.diseqc13V.value)
						elif nim.diseqcMode.value == "diseqc_a_b":		#DiSEqC A/B
							fastDiSEqC = nim.simpleDiSEqCOnlyOnSatChange.value
							setVoltageTone = nim.simpleDiSEqCSetVoltageTone.value
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcA.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.AA, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcB.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.AB, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
						elif nim.diseqcMode.value == "diseqc_a_b_c_d":		#DiSEqC A/B/C/D
							fastDiSEqC = nim.simpleDiSEqCOnlyOnSatChange.value
							setVoltageTone = nim.simpleDiSEqCSetVoltageTone.value
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcA.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.AA, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcB.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.AB, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcC.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.BA, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
							self.addLNBSimple(sec, slotid = x, orbpos = nim.diseqcD.orbital_position, toneburstmode = diseqcParam.NO, diseqcmode = diseqcParam.V1_0, diseqcpos = diseqcParam.BB, fastDiSEqC = fastDiSEqC, setVoltageTone = setVoltageTone, diseqc13V = nim.diseqc13V.value)
						elif nim.diseqcMode.value == "positioner":		#Positioner
							if nim.latitudeOrientation.value == "north":
								laValue = rotorParam.NORTH
							else:
								laValue = rotorParam.SOUTH
							if nim.longitudeOrientation.value == "east":
								loValue = rotorParam.EAST
							else:
								loValue = rotorParam.WEST
							inputPowerDelta=nim.powerThreshold.value
							useInputPower=False
							turning_speed=0
							if nim.powerMeasurement.value:
								useInputPower=True
								turn_speed_dict = { "fast": rotorParam.FAST, "slow": rotorParam.SLOW }
								if turn_speed_dict.has_key(nim.turningSpeed.value):
									turning_speed = turn_speed_dict[nim.turningSpeed.value]
								else:
									beg_time = localtime(nim.fastTurningBegin.value)
									end_time = localtime(nim.fastTurningEnd.value)
									turning_speed = ((beg_time.tm_hour+1) * 60 + beg_time.tm_min + 1) << 16
									turning_speed |= (end_time.tm_hour+1) * 60 + end_time.tm_min + 1
							self.addLNBSimple(sec, slotid = x, diseqcmode = 3,
								longitude = nim.longitude.float,
								loDirection = loValue,
								latitude = nim.latitude.float,
								laDirection = laValue,
								turningSpeed = turning_speed,
								useInputPower = useInputPower,
								inputPowerDelta = inputPowerDelta,
								diseqc13V = nim.diseqc13V.value)
					elif nim.configMode.value == "advanced": #advanced config
						self.updateAdvanced(sec, x)
		print "sec config completed"

	def updateAdvanced(self, sec, slotid):
		lnbSat = {}
		for x in range(1,37):
			lnbSat[x] = []

		#wildcard for all satellites ( for rotor )
		for x in range(3601, 3605):
			lnb = int(config.Nims[slotid].advanced.sat[x].lnb.value)
			if lnb != 0:
				for x in self.NimManager.satList:
					print "add", x[0], "to", lnb
					lnbSat[lnb].append(x[0])

		for x in self.NimManager.satList:
			lnb = int(config.Nims[slotid].advanced.sat[x[0]].lnb.value)
			if lnb != 0:
				print "add", x[0], "to", lnb
				lnbSat[lnb].append(x[0])

		for x in range(1,37):
			if len(lnbSat[x]) > 0:
				currLnb = config.Nims[slotid].advanced.lnb[x]
				sec.addLNB()

				if x < 33:
					sec.setLNBNum(x)

				tunermask = 1 << slotid
				if self.equal.has_key(slotid):
					for slot in self.equal[slotid]:
						tunermask |= (1 << slot)
				if self.linked.has_key(slotid):
					for slot in self.linked[slotid]:
						tunermask |= (1 << slot)

				if currLnb.lof.value != "unicable":
					sec.setLNBSatCR(-1)

				if currLnb.lof.value == "universal_lnb":
					sec.setLNBLOFL(9750000)
					sec.setLNBLOFH(10600000)
					sec.setLNBThreshold(11700000)
				elif currLnb.lof.value == "unicable":
					sec.setLNBLOFL(9750000)
					sec.setLNBLOFH(10600000)
					sec.setLNBThreshold(11700000)
					if currLnb.unicable.value == "unicable_user":
						sec.setLNBSatCR(currLnb.satcruser.index)
						sec.setLNBSatCRvco(currLnb.satcrvcouser[currLnb.satcruser.index].value*1000)
					elif currLnb.unicable.value == "unicable_matrix":
						manufacturer_name = currLnb.unicableMatrixManufacturer.value
						manufacturer = currLnb.unicableMatrix[manufacturer_name]
						product_name = manufacturer.product.value
						sec.setLNBSatCR(manufacturer.scr[product_name].index)
						sec.setLNBSatCRvco(manufacturer.vco[product_name][manufacturer.scr[product_name].index].value*1000)
					elif currLnb.unicable.value == "unicable_lnb":
						manufacturer_name = currLnb.unicableLnbManufacturer.value
						manufacturer = currLnb.unicableLnb[manufacturer_name]
						product_name = manufacturer.product.value
						sec.setLNBSatCR(manufacturer.scr[product_name].index)
						sec.setLNBSatCRvco(manufacturer.vco[product_name][manufacturer.scr[product_name].index].value*1000)
				elif currLnb.lof.value == "c_band":
					sec.setLNBLOFL(5150000)
					sec.setLNBLOFH(5150000)
					sec.setLNBThreshold(5150000)
				elif currLnb.lof.value == "user_defined":
					sec.setLNBLOFL(currLnb.lofl.value * 1000)
					sec.setLNBLOFH(currLnb.lofh.value * 1000)
					sec.setLNBThreshold(currLnb.threshold.value * 1000)

#				if currLnb.output_12v.value == "0V":
#					pass # nyi in drivers
#				elif currLnb.output_12v.value == "12V":
#					pass # nyi in drivers

				if currLnb.increased_voltage.value:
					sec.setLNBIncreasedVoltage(lnbParam.ON)
				else:
					sec.setLNBIncreasedVoltage(lnbParam.OFF)

				dm = currLnb.diseqcMode.value
				if dm == "none":
					sec.setDiSEqCMode(diseqcParam.NONE)
				elif dm == "1_0":
					sec.setDiSEqCMode(diseqcParam.V1_0)
				elif dm == "1_1":
					sec.setDiSEqCMode(diseqcParam.V1_1)
				elif dm == "1_2":
					sec.setDiSEqCMode(diseqcParam.V1_2)

					if self.satposdepends.has_key(slotid):
						for slot in self.satposdepends[slotid]:
							tunermask |= (1 << slot)

				if dm != "none":
					if currLnb.toneburst.value == "none":
						sec.setToneburst(diseqcParam.NO)
					elif currLnb.toneburst.value == "A":
						sec.setToneburst(diseqcParam.A)
					elif currLnb.toneburst.value == "B":
						sec.setToneburst(diseqcParam.B)

					# Committed Diseqc Command
					cdc = currLnb.commitedDiseqcCommand.value

					c = { "none": diseqcParam.SENDNO,
						"AA": diseqcParam.AA,
						"AB": diseqcParam.AB,
						"BA": diseqcParam.BA,
						"BB": diseqcParam.BB }

					if c.has_key(cdc):
						sec.setCommittedCommand(c[cdc])
					else:
						sec.setCommittedCommand(long(cdc))

					sec.setFastDiSEqC(currLnb.fastDiseqc.value)

					sec.setSeqRepeat(currLnb.sequenceRepeat.value)

					if currLnb.diseqcMode.value == "1_0":
						currCO = currLnb.commandOrder1_0.value
					else:
						currCO = currLnb.commandOrder.value

						udc = int(currLnb.uncommittedDiseqcCommand.value)
						if udc > 0:
							sec.setUncommittedCommand(0xF0|(udc-1))
						else:
							sec.setUncommittedCommand(0) # SENDNO

						sec.setRepeats({"none": 0, "one": 1, "two": 2, "three": 3}[currLnb.diseqcRepeats.value])

					setCommandOrder = False

					# 0 "committed, toneburst",
					# 1 "toneburst, committed",
					# 2 "committed, uncommitted, toneburst",
					# 3 "toneburst, committed, uncommitted",
					# 4 "uncommitted, committed, toneburst"
					# 5 "toneburst, uncommitted, commmitted"
					order_map = {"ct": 0, "tc": 1, "cut": 2, "tcu": 3, "uct": 4, "tuc": 5}
					sec.setCommandOrder(order_map[currCO])

				if dm == "1_2":
					latitude = currLnb.latitude.float
					sec.setLatitude(latitude)
					longitude = currLnb.longitude.float
					sec.setLongitude(longitude)
					if currLnb.latitudeOrientation.value == "north":
						sec.setLaDirection(rotorParam.NORTH)
					else:
						sec.setLaDirection(rotorParam.SOUTH)
					if currLnb.longitudeOrientation.value == "east":
						sec.setLoDirection(rotorParam.EAST)
					else:
						sec.setLoDirection(rotorParam.WEST)

					if currLnb.powerMeasurement.value:
						sec.setUseInputpower(True)
						sec.setInputpowerDelta(currLnb.powerThreshold.value)
						turn_speed_dict = { "fast": rotorParam.FAST, "slow": rotorParam.SLOW }
						if turn_speed_dict.has_key(currLnb.turningSpeed.value):
							turning_speed = turn_speed_dict[currLnb.turningSpeed.value]
						else:
							beg_time = localtime(currLnb.fastTurningBegin.value)
							end_time = localtime(currLnb.fastTurningEnd.value)
							turning_speed = ((beg_time.tm_hour + 1) * 60 + beg_time.tm_min + 1) << 16
							turning_speed |= (end_time.tm_hour + 1) * 60 + end_time.tm_min + 1
						sec.setRotorTurningSpeed(turning_speed)
					else:
						sec.setUseInputpower(False)

				sec.setLNBSlotMask(tunermask)

				sec.setLNBPrio(int(currLnb.prio.value))

				# finally add the orbital positions
				for y in lnbSat[x]:
					self.addSatellite(sec, y)
					if x > 32:
						satpos = x > 32 and (3604-(36 - x)) or y
					else:
						satpos = y
					currSat = config.Nims[slotid].advanced.sat[satpos]
					if currSat.voltage.value == "polarization":
						if config.Nims[slotid].diseqc13V.value:
							sec.setVoltageMode(switchParam.HV_13)
						else:
							sec.setVoltageMode(switchParam.HV)
					elif currSat.voltage.value == "13V":
						sec.setVoltageMode(switchParam._14V)
					elif currSat.voltage.value == "18V":
						sec.setVoltageMode(switchParam._18V)

					if currSat.tonemode.value == "band":
						sec.setToneMode(switchParam.HILO)
					elif currSat.tonemode.value == "on":
						sec.setToneMode(switchParam.ON)
					elif currSat.tonemode.value == "off":
						sec.setToneMode(switchParam.OFF)
						
					if not currSat.usals.value and x < 34:
						sec.setRotorPosNum(currSat.rotorposition.value)
					else:
						sec.setRotorPosNum(0) #USALS

	def __init__(self, nimmgr):
		self.NimManager = nimmgr
		self.configuredSatellites = set()
		self.update()

class NIM(object):
	def __init__(self, slot, type, description, has_outputs = True, internally_connectable = None):
		self.slot = slot

		if type not in ("DVB-S", "DVB-C", "DVB-T", "DVB-S2", None):
			print "warning: unknown NIM type %s, not using." % type
			type = None

		self.type = type
		self.description = description
		self.has_outputs = has_outputs
		self.internally_connectable = internally_connectable

	def isCompatible(self, what):
		compatible = {
				None: (None,),
				"DVB-S": ("DVB-S", None),
				"DVB-C": ("DVB-C", None),
				"DVB-T": ("DVB-T", None),
				"DVB-S2": ("DVB-S", "DVB-S2", None)
			}
		return what in compatible[self.type]
	
	def connectableTo(self):
		connectable = {
				"DVB-S": ("DVB-S", "DVB-S2"),
				"DVB-C": ("DVB-C",),
				"DVB-T": ("DVB-T",),
				"DVB-S2": ("DVB-S", "DVB-S2")
			}
		return connectable[self.type]

	def getSlotName(self):
		# get a friendly description for a slot name.
		# we name them "Tuner A/B/C/...", because that's what's usually written on the back
		# of the device.
		return _("Tuner ") + chr(ord('A') + self.slot)

	slot_name = property(getSlotName)

	def getSlotID(self):
		return chr(ord('A') + self.slot)
	
	def hasOutputs(self):
		return self.has_outputs
	
	def internallyConnectableTo(self):
		return self.internally_connectable

	slot_id = property(getSlotID)

	def getFriendlyType(self):
		return {
			"DVB-S": "DVB-S", 
			"DVB-T": "DVB-T",
			"DVB-S2": "DVB-S2",
			"DVB-C": "DVB-C",
			None: _("empty")
			}[self.type]

	friendly_type = property(getFriendlyType)

	def getFriendlyFullDescription(self):
		nim_text = self.slot_name + ": "
			
		if self.empty:
			nim_text += _("(empty)")
		else:
		 	nim_text += self.description + " (" + self.friendly_type + ")"
		
		return nim_text

	friendly_full_description = property(getFriendlyFullDescription)
	config_mode = property(lambda self: config.Nims[self.slot].configMode.value)
	config = property(lambda self: config.Nims[self.slot])
	empty = property(lambda self: self.type is None)

class NimManager:
	def getConfiguredSats(self):
		return self.sec.getConfiguredSats()

	def getTransponders(self, pos):
		if self.transponders.has_key(pos):
			return self.transponders[pos]
		else:
			return []

	def getTranspondersCable(self, nim):
		nimConfig = config.Nims[nim]
		if nimConfig.configMode.value != "nothing" and nimConfig.cable.scan_type.value == "provider":
			return self.transponderscable[self.cablesList[nimConfig.cable.scan_provider.index][0]]
		return [ ]

	def getTranspondersTerrestrial(self, region):
		return self.transpondersterrestrial[region]
	
	def getCableDescription(self, nim):
		return self.cablesList[config.Nims[nim].scan_provider.index][0]

	def getCableFlags(self, nim):
		return self.cablesList[config.Nims[nim].scan_provider.index][1]

	def getTerrestrialDescription(self, nim):
		return self.terrestrialsList[config.Nims[nim].terrestrial.index][0]

	def getTerrestrialFlags(self, nim):
		return self.terrestrialsList[config.Nims[nim].terrestrial.index][1]

	def getSatDescription(self, pos):
		return self.satellites[pos]

	def readTransponders(self):
		# read initial networks from file. we only read files which we are interested in,
		# which means only these where a compatible tuner exists.
		self.satellites = { }
		self.transponders = { }
		self.transponderscable = { }
		self.transpondersterrestrial = { }
		db = eDVBDB.getInstance()
		if self.hasNimType("DVB-S"):
			print "Reading satellites.xml"
			db.readSatellites(self.satList, self.satellites, self.transponders)
#			print "SATLIST", self.satList
#			print "SATS", self.satellites
#			print "TRANSPONDERS", self.transponders

		if self.hasNimType("DVB-C"):
			print "Reading cables.xml"
			db.readCables(self.cablesList, self.transponderscable)
#			print "CABLIST", self.cablesList
#			print "TRANSPONDERS", self.transponders

		if self.hasNimType("DVB-T"):
			print "Reading terrestrial.xml"
			db.readTerrestrials(self.terrestrialsList, self.transpondersterrestrial)
#			print "TERLIST", self.terrestrialsList
#			print "TRANSPONDERS", self.transpondersterrestrial

	def enumerateNIMs(self):
		# enum available NIMs. This is currently very dreambox-centric and uses the /proc/bus/nim_sockets interface.
		# the result will be stored into nim_slots.
		# the content of /proc/bus/nim_sockets looks like:
		# NIM Socket 0:
		#          Type: DVB-S
		#          Name: BCM4501 DVB-S2 NIM (internal)
		# NIM Socket 1:
		#          Type: DVB-S
		#          Name: BCM4501 DVB-S2 NIM (internal)
		# NIM Socket 2:
		#          Type: DVB-T
		#          Name: Philips TU1216
		# NIM Socket 3:
		#          Type: DVB-S
		#          Name: Alps BSBE1 702A
		
		#
		# Type will be either "DVB-S", "DVB-S2", "DVB-T", "DVB-C" or None.

		# nim_slots is an array which has exactly one entry for each slot, even for empty ones.
		self.nim_slots = [ ]

		nimfile = tryOpen("/proc/bus/nim_sockets")

		if nimfile is None:
			return

		current_slot = None

		entries = {}
		for line in nimfile.readlines():
			if line == "":
				break
			if line.strip().startswith("NIM Socket"):
				parts = line.strip().split(" ")
				current_slot = int(parts[2][:-1])
				entries[current_slot] = {}
			elif line.strip().startswith("Type:"):
				entries[current_slot]["type"] = str(line.strip()[6:])
			elif line.strip().startswith("Name:"):
				entries[current_slot]["name"] = str(line.strip()[6:])
			elif line.strip().startswith("Has_Outputs:"):
				input = str(line.strip()[len("Has_Outputs:") + 1:])
				entries[current_slot]["has_outputs"] = (input == "yes")
			elif line.strip().startswith("Internally_Connectable:"):
				input = int(line.strip()[len("Internally_Connectable:") + 1:])
				entries[current_slot]["internally_connectable"] = input 
			elif line.strip().startswith("empty"):
				entries[current_slot]["type"] = None
				entries[current_slot]["name"] = _("N/A")
		nimfile.close()
		
		for id, entry in entries.items():
			if not (entry.has_key("name") and entry.has_key("type")):
				entry["name"] =  _("N/A")
				entry["type"] = None
			if not (entry.has_key("has_outputs")):
				entry["has_outputs"] = True
			if not (entry.has_key("internally_connectable")):
				entry["internally_connectable"] = None
			self.nim_slots.append(NIM(slot = id, description = entry["name"], type = entry["type"], has_outputs = entry["has_outputs"], internally_connectable = entry["internally_connectable"]))

	def hasNimType(self, chktype):
		for slot in self.nim_slots:
			if slot.isCompatible(chktype):
				return True
		return False
	
	def getNimType(self, slotid):
		return self.nim_slots[slotid].type
	
	def getNimDescription(self, slotid):
		return self.nim_slots[slotid].friendly_full_description

	def getNimListOfType(self, type, exception = -1):
		# returns a list of indexes for NIMs compatible to the given type, except for 'exception'
		list = []
		for x in self.nim_slots:
			if x.isCompatible(type) and x.slot != exception:
				list.append(x.slot)
		return list

	def __init__(self):
		self.satList = [ ]
		self.cablesList = []
		self.terrestrialsList = []
		self.enumerateNIMs()
		self.readTransponders()
		InitNimManager(self)	#init config stuff

	# get a list with the friendly full description
	def nimList(self):
		list = [ ]
		for slot in self.nim_slots:
			list.append(slot.friendly_full_description)
		return list
	
	def getSlotCount(self):
		return len(self.nim_slots)
	
	def hasOutputs(self, slotid):
		return self.nim_slots[slotid].hasOutputs()
	
	def canConnectTo(self, slotid):
		slots = []
		if self.nim_slots[slotid].internallyConnectableTo() is not None:
			slots.append(self.nim_slots[slotid].internallyConnectableTo())
		for type in self.nim_slots[slotid].connectableTo(): 
			for slot in self.getNimListOfType(type, exception = slotid):
				if self.hasOutputs(slot):
					slots.append(slot)
		# remove nims, that have a conntectedTo reference on
		for testnim in slots[:]:
			for nim in self.getNimListOfType("DVB-S", slotid):
				nimConfig = self.getNimConfig(nim)
				if nimConfig.content.items.has_key("configMode") and nimConfig.configMode.value == "loopthrough" and int(nimConfig.connectedTo.value) == testnim:
					slots.remove(testnim)
					break 
		slots.sort()
		
		return slots
	
	def canEqualTo(self, slotid):
		type = self.getNimType(slotid)
		if type == "DVB-S2":
			type = "DVB-S"
		nimList = self.getNimListOfType(type, slotid)
		for nim in nimList[:]:
			mode = self.getNimConfig(nim)
			if mode.configMode.value == "loopthrough" or mode.configMode.value == "satposdepends":
				nimList.remove(nim)
		return nimList

	def canDependOn(self, slotid):
		type = self.getNimType(slotid)
		if type == "DVB-S2":
			type = "DVB-S"
		nimList = self.getNimListOfType(type, slotid)
		positionerList = []
		for nim in nimList[:]:
			mode = self.getNimConfig(nim)
			nimHaveRotor = mode.configMode.value == "simple" and mode.diseqcMode.value == "positioner"
			if not nimHaveRotor and mode.configMode.value == "advanced":
				for x in range(3601, 3605):
					lnb = int(mode.advanced.sat[x].lnb.value)
					if lnb != 0:
						nimHaveRotor = True
						break
				if not nimHaveRotor:
					for sat in mode.advanced.sat.values():
						lnb_num = int(sat.lnb.value)
						diseqcmode = lnb_num and mode.advanced.lnb[lnb_num].diseqcMode.value or ""
						if diseqcmode == "1_2":
							nimHaveRotor = True
							break
			if nimHaveRotor:
				alreadyConnected = False
				for testnim in nimList:
					testmode = self.getNimConfig(testnim)
					if testmode.configMode.value == "satposdepends" and int(testmode.connectedTo.value) == int(nim):
						alreadyConnected = True
						break
				if not alreadyConnected:
					positionerList.append(nim)
		return positionerList
	
	def getNimConfig(self, slotid):
		return config.Nims[slotid]
	
	def getSatName(self, pos):
		for sat in self.satList:
			if sat[0] == pos:
				return sat[1]
		return _("N/A")

	def getSatList(self):
		return self.satList

	def getSatListForNim(self, slotid):
		list = []
		if self.nim_slots[slotid].isCompatible("DVB-S"):
			nim = config.Nims[slotid]
			#print "slotid:", slotid

			#print "self.satellites:", self.satList[config.Nims[slotid].diseqcA.index]
			#print "diseqcA:", config.Nims[slotid].diseqcA.value
			configMode = nim.configMode.value

			if configMode == "equal":
				slotid = int(nim.connectedTo.value)
				nim = config.Nims[slotid]
				configMode = nim.configMode.value
			elif configMode == "loopthrough":
				slotid = self.sec.getRoot(slotid, int(nim.connectedTo.value))
				nim = config.Nims[slotid]
				configMode = nim.configMode.value

			if configMode == "simple":
				dm = nim.diseqcMode.value
				if dm in ("single", "toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
					if nim.diseqcA.orbital_position != 3601:
						list.append(self.satList[nim.diseqcA.index-1])
				if dm in ("toneburst_a_b", "diseqc_a_b", "diseqc_a_b_c_d"):
					if nim.diseqcB.orbital_position != 3601:
						list.append(self.satList[nim.diseqcB.index-1])
				if dm == "diseqc_a_b_c_d":
					if nim.diseqcC.orbital_position != 3601:
						list.append(self.satList[nim.diseqcC.index-1])
					if nim.diseqcD.orbital_position != 3601:
						list.append(self.satList[nim.diseqcD.index-1])
				if dm == "positioner":
					for x in self.satList:
						list.append(x)
			elif configMode == "advanced":
				for x in range(3601, 3605):
					if int(nim.advanced.sat[x].lnb.value) != 0:
						for x in self.satList:
							list.append(x)
				if not list:
					for x in self.satList:
						if int(nim.advanced.sat[x[0]].lnb.value) != 0:
							list.append(x)
		return list

	def getRotorSatListForNim(self, slotid):
		list = []
		if self.nim_slots[slotid].isCompatible("DVB-S"):
			#print "slotid:", slotid
			#print "self.satellites:", self.satList[config.Nims[slotid].diseqcA.value]
			#print "diseqcA:", config.Nims[slotid].diseqcA.value
			configMode = config.Nims[slotid].configMode.value
			if configMode == "simple":
				if config.Nims[slotid].diseqcMode.value == "positioner":
					for x in self.satList:
						list.append(x)
			elif configMode == "advanced":
				nim = config.Nims[slotid]
				for x in range(3601, 3605):
					if int(nim.advanced.sat[x].lnb.value) != 0:
						for x in self.satList:
							list.append(x)
				if not list:
					for x in self.satList:
						lnbnum = int(nim.advanced.sat[x[0]].lnb.value)
						if lnbnum != 0:
							lnb = nim.advanced.lnb[lnbnum]
							if lnb.diseqcMode.value == "1_2":
								list.append(x)
		return list

def InitSecParams():
	config.sec = ConfigSubsection()

	x = ConfigInteger(default=25, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_CONT_TONE_DISABLE_BEFORE_DISEQC, configElement.value))
	config.sec.delay_after_continuous_tone_disable_before_diseqc = x

	x = ConfigInteger(default=10, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_FINAL_CONT_TONE_CHANGE, configElement.value))
	config.sec.delay_after_final_continuous_tone_change = x

	x = ConfigInteger(default=10, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_FINAL_VOLTAGE_CHANGE, configElement.value))
	config.sec.delay_after_final_voltage_change = x

	x = ConfigInteger(default=120, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_BETWEEN_DISEQC_REPEATS, configElement.value))
	config.sec.delay_between_diseqc_repeats = x

	x = ConfigInteger(default=50, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_LAST_DISEQC_CMD, configElement.value))
	config.sec.delay_after_last_diseqc_command = x

	x = ConfigInteger(default=50, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_TONEBURST, configElement.value))
	config.sec.delay_after_toneburst = x

	x = ConfigInteger(default=20, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS, configElement.value))
	config.sec.delay_after_change_voltage_before_switch_command = x

	x = ConfigInteger(default=200, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_SWITCH_CMDS, configElement.value))
	config.sec.delay_after_enable_voltage_before_switch_command = x

	x = ConfigInteger(default=700, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_BETWEEN_SWITCH_AND_MOTOR_CMD, configElement.value))
	config.sec.delay_between_switch_and_motor_command = x

	x = ConfigInteger(default=500, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MEASURE_IDLE_INPUTPOWER, configElement.value))
	config.sec.delay_after_voltage_change_before_measure_idle_inputpower = x

	x = ConfigInteger(default=750, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_MOTOR_CMD, configElement.value))
	config.sec.delay_after_enable_voltage_before_motor_command = x

	x = ConfigInteger(default=500, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_MOTOR_STOP_CMD, configElement.value))
	config.sec.delay_after_motor_stop_command = x

	x = ConfigInteger(default=500, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MOTOR_CMD, configElement.value))
	config.sec.delay_after_voltage_change_before_motor_command = x

	x = ConfigInteger(default=70, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_BEFORE_SEQUENCE_REPEAT, configElement.value))
	config.sec.delay_before_sequence_repeat = x

	x = ConfigInteger(default=360, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.MOTOR_RUNNING_TIMEOUT, configElement.value))
	config.sec.motor_running_timeout = x

	x = ConfigInteger(default=1, limits = (0, 5))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.MOTOR_COMMAND_RETRIES, configElement.value))
	config.sec.motor_command_retries = x

	x = ConfigInteger(default=50, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_DISEQC_RESET_CMD, configElement.value))
	config.sec.delay_after_diseqc_reset_cmd = x

	x = ConfigInteger(default=150, limits = (0, 9999))
	x.addNotifier(lambda configElement: secClass.setParam(secClass.DELAY_AFTER_DISEQC_PERIPHERIAL_POWERON_CMD, configElement.value))
	config.sec.delay_after_diseqc_peripherial_poweron_cmd = x

# TODO add support for satpos depending nims to advanced nim configuration
# so a second/third/fourth cable from a motorized lnb can used behind a
# diseqc 1.0 / diseqc 1.1 / toneburst switch
# the C(++) part should can handle this
# the configElement should be only visible when diseqc 1.2 is disabled

def InitNimManager(nimmgr):
	InitSecParams()
	hw = HardwareInfo()

	config.Nims = ConfigSubList()
	for x in range(len(nimmgr.nim_slots)):
		config.Nims.append(ConfigSubsection())

	lnb_choices = {
		"universal_lnb": _("Universal LNB"),
		"unicable": _("Unicable"),
		"c_band": _("C-Band"),
		"user_defined": _("User defined")}

	lnb_choices_default = "universal_lnb"

	unicablelnbproducts = {
		"Humax": {"150 SCR":("1210","1420","1680","2040")},
		"Inverto": {"IDLP-40UNIQD+S":("1680","1420","2040","1210")},
		"Kathrein": {"UAS481":("1400","1516","1632","1748")},
		"Kreiling": {"KR1440":("1680","1420","2040","1210")},
		"Radix": {"Unicable LNB":("1680","1420","2040","1210")},
		"Wisi": {"OC 05":("1210","1420","1680","2040")}}
	UnicableLnbManufacturers = unicablelnbproducts.keys()
	UnicableLnbManufacturers.sort()

	unicablematrixproducts = {
		"Ankaro": {
			"UCS 51440":("1400","1632","1284","1516"),
			"UCS 51820":("1400","1632","1284","1516","1864","2096","1748","1980"),
			"UCS 51840":("1400","1632","1284","1516","1864","2096","1748","1980"),
			"UCS 52240":("1400","1632"),
			"UCS 52420":("1400","1632","1284","1516"),
			"UCS 52440":("1400","1632","1284","1516"),
			"UCS 91440":("1400","1632","1284","1516"),
			"UCS 91820":("1400","1632","1284","1516","1864","2096","1748","1980"),
			"UCS 91840":("1400","1632","1284","1516","1864","2096","1748","1980"),
			"UCS 92240":("1400","1632"),
			"UCS 92420":("1400","1632","1284","1516"),
			"UCS 92440":("1400","1632","1284","1516")},
		"DCT Delta": {
			"SUM518":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"SUM918":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"SUM928":("1284","1400","1516","1632","1748","1864","1980","2096")},
		"Inverto": {
			"IDLP-UST11O-CUO1O-8PP":("1076","1178","1280","1382","1484","1586","1688","1790")},
		"Kathrein": {
			"EXR501":("1400","1516","1632","1748"),
			"EXR551":("1400","1516","1632","1748"),
			"EXR552":("1400","1516")},
		"ROTEK": {
			"EKL2/1":("1400","1516"),
			"EKL2/1E":("0","0","1632","1748")},
		"Smart": {
			"DPA 51":("1284","1400","1516","1632","1748","1864","1980","2096")},
		"Technisat": {
			"TechniRouter 5/1x8 G":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"TechniRouter 5/1x8 K":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"TechniRouter 5/2x4 G":("1284","1400","1516","1632"),
			"TechniRouter 5/2x4 K":("1284","1400","1516","1632")},
		"Telstar": {
			"SCR 5/1x8 G":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"SCR 5/1x8 K":("1284","1400","1516","1632","1748","1864","1980","2096"),
			"SCR 5/2x4 G":("1284","1400","1516","1632"),
			"SCR 5/2x4 K":("1284","1400","1516","1632")}}
	UnicableMatrixManufacturers = unicablematrixproducts.keys()
	UnicableMatrixManufacturers.sort()

	unicable_choices = {
		"unicable_lnb": _("Unicable LNB"),
		"unicable_matrix": _("Unicable Martix"),
		"unicable_user": "Unicable "+_("User defined")}
	unicable_choices_default = "unicable_lnb"

	advanced_lnb_satcruser_choices = [ ("1", "SatCR 1"), ("2", "SatCR 2"), ("3", "SatCR 3"), ("4", "SatCR 4"),
					("5", "SatCR 5"), ("6", "SatCR 6"), ("7", "SatCR 7"), ("8", "SatCR 8")]

	prio_list = [ ("-1", _("Auto")) ]
	prio_list += [(str(prio), str(prio)) for prio in range(65)+range(14000,14065)+range(19000,19065)]

	advanced_lnb_csw_choices = [("none", _("None")), ("AA", _("AA")), ("AB", _("AB")), ("BA", _("BA")), ("BB", _("BB"))]
	advanced_lnb_csw_choices += [(str(0xF0|y), "Input " + str(y+1)) for y in range(0, 16)]

	advanced_lnb_ucsw_choices = [("0", _("None"))] + [(str(y), "Input " + str(y)) for y in range(1, 17)]

	diseqc_mode_choices = [
		("single", _("Single")), ("toneburst_a_b", _("Toneburst A/B")),
		("diseqc_a_b", _("DiSEqC A/B")), ("diseqc_a_b_c_d", _("DiSEqC A/B/C/D")),
		("positioner", _("Positioner"))]

	positioner_mode_choices = [("usals", _("USALS")), ("manual", _("manual"))]

	diseqc_satlist_choices = [(3601, _('nothing connected'), 1)] + nimmgr.satList
	
	longitude_orientation_choices = [("east", _("East")), ("west", _("West"))]
	latitude_orientation_choices = [("north", _("North")), ("south", _("South"))]
	turning_speed_choices = [("fast", _("Fast")), ("slow", _("Slow")), ("fast epoch", _("Fast epoch"))]
	
	advanced_satlist_choices = nimmgr.satList + [
		(3601, _('All Satellites')+' 1', 1), (3602, _('All Satellites')+' 2', 1),
		(3603, _('All Satellites')+' 3', 1), (3604, _('All Satellites')+' 4', 1)]
	advanced_lnb_choices = [("0", "not available")] + [(str(y), "LNB " + str(y)) for y in range(1, 33)]
	advanced_voltage_choices = [("polarization", _("Polarization")), ("13V", _("13 V")), ("18V", _("18 V"))]
	advanced_tonemode_choices = [("band", _("Band")), ("on", _("On")), ("off", _("Off"))]
	advanced_lnb_toneburst_choices = [("none", _("None")), ("A", _("A")), ("B", _("B"))]
	advanced_lnb_allsat_diseqcmode_choices = [("1_2", _("1.2"))]
	advanced_lnb_diseqcmode_choices = [("none", _("None")), ("1_0", _("1.0")), ("1_1", _("1.1")), ("1_2", _("1.2"))]
	advanced_lnb_commandOrder1_0_choices = [("ct", "committed, toneburst"), ("tc", "toneburst, committed")]
	advanced_lnb_commandOrder_choices = [
		("ct", "committed, toneburst"), ("tc", "toneburst, committed"),
		("cut", "committed, uncommitted, toneburst"), ("tcu", "toneburst, committed, uncommitted"),
		("uct", "uncommitted, committed, toneburst"), ("tuc", "toneburst, uncommitted, commmitted")]
	advanced_lnb_diseqc_repeat_choices = [("none", _("None")), ("one", _("One")), ("two", _("Two")), ("three", _("Three"))]
	advanced_lnb_fast_turning_btime = mktime(datetime(1970, 1, 1, 7, 0).timetuple());
	advanced_lnb_fast_turning_etime = mktime(datetime(1970, 1, 1, 19, 0).timetuple());

	def configLOFChanged(configElement):
		if configElement.value == "unicable":
			x = configElement.slot_id
			lnb = configElement.lnb_id
			nim = config.Nims[x]
			lnbs = nim.advanced.lnb
			section = lnbs[lnb]
			if isinstance(section.unicable, ConfigNothing):
				if lnb == 1:
					section.unicable = ConfigSelection(unicable_choices, unicable_choices_default)
				elif lnb == 2:
					section.unicable = ConfigSelection(choices = {"unicable_matrix": _("Unicable Martix"),"unicable_user": "Unicable "+_("User defined")}, default = "unicable_matrix")
				else:
					section.unicable = ConfigSelection(choices = {"unicable_user": _("User defined")}, default = "unicable_user")

				if lnb < 3:
					section.unicableMatrix = ConfigSubDict()
					section.unicableMatrixManufacturer = ConfigSelection(choices = UnicableMatrixManufacturers, default = UnicableMatrixManufacturers[0])
					for y in unicablematrixproducts:
						products = unicablematrixproducts[y].keys()
						products.sort()
						tmp = ConfigSubsection()
						tmp.product = ConfigSelection(choices = products, default = products[0])
						tmp.scr = ConfigSubDict()
						tmp.vco = ConfigSubDict()
						for z in products:
							scrlist = []
							vcolist = unicablematrixproducts[y][z]
							tmp.vco[z] = ConfigSubList()
							for cnt in range(1,1+len(vcolist)):
								vcofreq = int(vcolist[cnt-1])
								if vcofreq == 0:
									scrlist.append(("%d" %cnt,"SCR %d " %cnt +_("not used")))
								else:
									scrlist.append(("%d" %cnt,"SCR %d" %cnt))
								tmp.vco[z].append(ConfigInteger(default=vcofreq, limits = (vcofreq, vcofreq)))
							tmp.scr[z] = ConfigSelection(choices = scrlist, default = scrlist[0][0])
						section.unicableMatrix[y] = tmp

				if lnb < 2:
					section.unicableLnb = ConfigSubDict()
					section.unicableLnbManufacturer = ConfigSelection(UnicableLnbManufacturers, UnicableLnbManufacturers[0])
					for y in unicablelnbproducts:
						products = unicablelnbproducts[y].keys()
						products.sort()
						tmp = ConfigSubsection()
						tmp.product = ConfigSelection(choices = products, default = products[0])
						tmp.scr = ConfigSubDict()
						tmp.vco = ConfigSubDict()
						for z in products:
							scrlist = []
							vcolist = unicablelnbproducts[y][z]
							tmp.vco[z] = ConfigSubList()
							for cnt in range(1,1+len(vcolist)):
								scrlist.append(("%d" %cnt,"SCR %d" %cnt))
								vcofreq = int(vcolist[cnt-1])
								tmp.vco[z].append(ConfigInteger(default=vcofreq, limits = (vcofreq, vcofreq)))
							tmp.scr[z] = ConfigSelection(choices = scrlist, default = scrlist[0][0])
						section.unicableLnb[y] = tmp

				section.satcruser = ConfigSelection(advanced_lnb_satcruser_choices, default="1")
				tmp = ConfigSubList()
				tmp.append(ConfigInteger(default=1284, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1400, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1516, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1632, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1748, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1864, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=1980, limits = (0, 9999)))
				tmp.append(ConfigInteger(default=2096, limits = (0, 9999)))
				section.satcrvcouser = tmp 

	def configDiSEqCModeChanged(configElement):
		section = configElement.section
		if configElement.value == "1_2" and isinstance(section.longitude, ConfigNothing):
			section.longitude = ConfigFloat(default = [5,100], limits = [(0,359),(0,999)])
			section.longitudeOrientation = ConfigSelection(longitude_orientation_choices, "east")
			section.latitude = ConfigFloat(default = [50,767], limits = [(0,359),(0,999)])
			section.latitudeOrientation = ConfigSelection(latitude_orientation_choices, "north")
			section.powerMeasurement = ConfigYesNo(default=True)
			section.powerThreshold = ConfigInteger(default=hw.get_device_name() == "dm8000" and 15 or 50, limits=(0, 100))
			section.turningSpeed = ConfigSelection(turning_speed_choices, "fast")
			section.fastTurningBegin = ConfigDateTime(default=advanced_lnb_fast_turning_btime, formatstring = _("%H:%M"), increment = 600)
			section.fastTurningEnd = ConfigDateTime(default=advanced_lnb_fast_turning_etime, formatstring = _("%H:%M"), increment = 600)

	def configLNBChanged(configElement):
		x = configElement.slot_id
		nim = config.Nims[x]
		if isinstance(configElement.value, tuple):
			lnb = int(configElement.value[0])
		else:
			lnb = int(configElement.value)
		lnbs = nim.advanced.lnb
		if lnb and lnb not in lnbs:
			section = lnbs[lnb] = ConfigSubsection()
			section.lofl = ConfigInteger(default=9750, limits = (0, 99999))
			section.lofh = ConfigInteger(default=10600, limits = (0, 99999))
			section.threshold = ConfigInteger(default=11700, limits = (0, 99999))
#			section.output_12v = ConfigSelection(choices = [("0V", _("0 V")), ("12V", _("12 V"))], default="0V")
			section.increased_voltage = ConfigYesNo(False)
			section.toneburst = ConfigSelection(advanced_lnb_toneburst_choices, "none")
			section.longitude = ConfigNothing()
			if lnb > 32:
				tmp = ConfigSelection(advanced_lnb_allsat_diseqcmode_choices, "1_2")
				tmp.section = section
				configDiSEqCModeChanged(tmp)
			else:
				tmp = ConfigSelection(advanced_lnb_diseqcmode_choices, "none")
				tmp.section = section
				tmp.addNotifier(configDiSEqCModeChanged)
			section.diseqcMode = tmp
			section.commitedDiseqcCommand = ConfigSelection(advanced_lnb_csw_choices)
			section.fastDiseqc = ConfigYesNo(False)
			section.sequenceRepeat = ConfigYesNo(False)
			section.commandOrder1_0 = ConfigSelection(advanced_lnb_commandOrder1_0_choices, "ct")
			section.commandOrder = ConfigSelection(advanced_lnb_commandOrder_choices, "ct")
			section.uncommittedDiseqcCommand = ConfigSelection(advanced_lnb_ucsw_choices)
			section.diseqcRepeats = ConfigSelection(advanced_lnb_diseqc_repeat_choices, "none")
			section.prio = ConfigSelection(prio_list, "-1")
			section.unicable = ConfigNothing()
			tmp = ConfigSelection(lnb_choices, lnb_choices_default)
			tmp.slot_id = x
			tmp.lnb_id = lnb
			tmp.addNotifier(configLOFChanged, initial_call = False)
			section.lof = tmp

	def configModeChanged(configMode):
		slot_id = configMode.slot_id
 		nim = config.Nims[slot_id]
		if configMode.value == "advanced" and isinstance(nim.advanced, ConfigNothing):
			# advanced config:
			nim.advanced = ConfigSubsection()
			nim.advanced.sat = ConfigSubDict()
			nim.advanced.sats = getConfigSatlist(192, advanced_satlist_choices)
			nim.advanced.lnb = ConfigSubDict()
			nim.advanced.lnb[0] = ConfigNothing()
			for x in nimmgr.satList:
				tmp = ConfigSubsection()
				tmp.voltage = ConfigSelection(advanced_voltage_choices, "polarization")
				tmp.tonemode = ConfigSelection(advanced_tonemode_choices, "band")
				tmp.usals = ConfigYesNo(True)
				tmp.rotorposition = ConfigInteger(default=1, limits=(1, 255))
				lnb = ConfigSelection(advanced_lnb_choices, "0")
				lnb.slot_id = slot_id
				lnb.addNotifier(configLNBChanged, initial_call = False)
				tmp.lnb = lnb
				nim.advanced.sat[x[0]] = tmp
			for x in range(3601, 3605):
				tmp = ConfigSubsection()
				tmp.voltage = ConfigSelection(advanced_voltage_choices, "polarization")
				tmp.tonemode = ConfigSelection(advanced_tonemode_choices, "band")
				tmp.usals = ConfigYesNo(default=True)
				tmp.rotorposition = ConfigInteger(default=1, limits=(1, 255))
				lnbnum = 33+x-3601
				lnb = ConfigSelection([("0", "not available"), (str(lnbnum), "LNB %d"%(lnbnum))], "0")
				lnb.slot_id = slot_id
				lnb.addNotifier(configLNBChanged, initial_call = False)
				tmp.lnb = lnb
				nim.advanced.sat[x] = tmp

	for slot in nimmgr.nim_slots:
		x = slot.slot
		nim = config.Nims[x]
		if slot.isCompatible("DVB-S"):
			nim.diseqc13V = ConfigYesNo(False)
			nim.diseqcMode = ConfigSelection(diseqc_mode_choices, "diseqc_a_b")
			nim.connectedTo = ConfigSelection([(str(id), nimmgr.getNimDescription(id)) for id in nimmgr.getNimListOfType("DVB-S") if id != x])
			nim.simpleSingleSendDiSEqC = ConfigYesNo(False)
			nim.simpleDiSEqCSetVoltageTone = ConfigYesNo(True)
			nim.simpleDiSEqCOnlyOnSatChange = ConfigYesNo(False)
			nim.diseqcA = getConfigSatlist(192, diseqc_satlist_choices)
			nim.diseqcB = getConfigSatlist(130, diseqc_satlist_choices)
			nim.diseqcC = ConfigSatlist(list = diseqc_satlist_choices)
			nim.diseqcD = ConfigSatlist(list = diseqc_satlist_choices)
			nim.positionerMode = ConfigSelection(positioner_mode_choices, "usals")
			nim.longitude = ConfigFloat(default=[5,100], limits=[(0,359),(0,999)])
			nim.longitudeOrientation = ConfigSelection(longitude_orientation_choices, "east")
			nim.latitude = ConfigFloat(default=[50,767], limits=[(0,359),(0,999)])
			nim.latitudeOrientation = ConfigSelection(latitude_orientation_choices, "north")
			nim.powerMeasurement = ConfigYesNo(True)
			nim.powerThreshold = ConfigInteger(default=hw.get_device_name() == "dm8000" and 15 or 50, limits=(0, 100))
			nim.turningSpeed = ConfigSelection(turning_speed_choices, "fast")
			btime = datetime(1970, 1, 1, 7, 0);
			nim.fastTurningBegin = ConfigDateTime(default = mktime(btime.timetuple()), formatstring = _("%H:%M"), increment = 900)
			etime = datetime(1970, 1, 1, 19, 0);
			nim.fastTurningEnd = ConfigDateTime(default = mktime(etime.timetuple()), formatstring = _("%H:%M"), increment = 900)
			config_mode_choices = [ ("nothing", _("nothing connected")),
				("simple", _("simple")), ("advanced", _("advanced"))]
			if len(nimmgr.getNimListOfType(slot.type, exception = x)) > 0:
				config_mode_choices.append(("equal", _("equal to")))
				config_mode_choices.append(("satposdepends", _("second cable of motorized LNB")))
			if len(nimmgr.canConnectTo(x)) > 0:
				config_mode_choices.append(("loopthrough", _("loopthrough to")))
			nim.advanced = ConfigNothing()
			tmp = ConfigSelection(config_mode_choices, "nothing")
			tmp.slot_id = x
			tmp.addNotifier(configModeChanged, initial_call = False)
			nim.configMode = tmp
		elif slot.isCompatible("DVB-C"):
			nim.configMode = ConfigSelection(
				choices = {
					"enabled": _("enabled"),
					"nothing": _("nothing connected"),
					},
				default = "enabled")
			list = [ ]
			n = 0
			for x in nimmgr.cablesList:
				list.append((str(n), x[0]))
				n += 1
			nim.cable = ConfigSubsection()
			possible_scan_types = [("bands", _("Frequency bands")), ("steps", _("Frequency steps"))]
			if n:
				possible_scan_types.append(("provider", _("Provider")))
				nim.cable.scan_provider = ConfigSelection(default = "0", choices = list)
			nim.cable.scan_type = ConfigSelection(default = "bands", choices = possible_scan_types)
			nim.cable.scan_band_EU_VHF_I = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_MID = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_VHF_III = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_UHF_IV = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_UHF_V = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_SUPER = ConfigYesNo(default = True)
			nim.cable.scan_band_EU_HYPER = ConfigYesNo(default = True)
			nim.cable.scan_band_US_LOW = ConfigYesNo(default = False)
			nim.cable.scan_band_US_MID = ConfigYesNo(default = False)
			nim.cable.scan_band_US_HIGH = ConfigYesNo(default = False)
			nim.cable.scan_band_US_SUPER = ConfigYesNo(default = False)
			nim.cable.scan_band_US_HYPER = ConfigYesNo(default = False)
			nim.cable.scan_frequency_steps = ConfigInteger(default = 1000, limits = (1000, 10000))
			nim.cable.scan_mod_qam16 = ConfigYesNo(default = False)
			nim.cable.scan_mod_qam32 = ConfigYesNo(default = False)
			nim.cable.scan_mod_qam64 = ConfigYesNo(default = True)
			nim.cable.scan_mod_qam128 = ConfigYesNo(default = False)
			nim.cable.scan_mod_qam256 = ConfigYesNo(default = True)
			nim.cable.scan_sr_6900 = ConfigYesNo(default = True)
			nim.cable.scan_sr_6875 = ConfigYesNo(default = True)
			nim.cable.scan_sr_ext1 = ConfigInteger(default = 0, limits = (0, 7230))
			nim.cable.scan_sr_ext2 = ConfigInteger(default = 0, limits = (0, 7230))
		elif slot.isCompatible("DVB-T"):
			nim.configMode = ConfigSelection(
				choices = {
					"enabled": _("enabled"),
					"nothing": _("nothing connected"),
					},
				default = "enabled")
			list = []
			n = 0
			for x in nimmgr.terrestrialsList:
				list.append((str(n), x[0]))
				n += 1
			nim.terrestrial = ConfigSelection(choices = list)
			nim.terrestrial_5V = ConfigOnOff()
		else:
			nim.configMode = ConfigSelection(choices = { "nothing": _("disabled") }, default="nothing");
			if slot.type is not None:
				print "pls add support for this frontend type!", slot.type
#			assert False

	nimmgr.sec = SecConfigure(nimmgr)

nimmanager = NimManager()
