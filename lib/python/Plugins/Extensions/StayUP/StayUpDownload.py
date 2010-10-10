#######################
# SubRoutine Download #
#######################
from Components.config import config, ConfigText, ConfigYesNo, ConfigClock, ConfigSubsection, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from StayUpLog import writeLog
from enigma import eDVBDB, eEPGCache, eTimer
from md5 import md5
import os

def download(self):
	writeLog("100 Subprocess called")
	self.location_download="http://www.wallsite.com/Dream/misc/"
	self.EpgFile="epg.dat.save"
	self.EpgSignature=self.EpgFile + ".SIGNATURE"
	self.PiconFile=config.plugins.StayUP.PiconType.value + ".ipk"
	self.PiconSignature=config.plugins.StayUP.PiconType.value + ".SIGNATURE"
	self.SettingsFile=config.plugins.StayUP.SettingsType.value + ".ipk"
	self.SettingsSignature=config.plugins.StayUP.SettingsType.value + ".SIGNATURE"
	self.AutoUpdateFile="enigma2-stayUP-r10.ipk"
	self.AutoUpdateSignature=self.AutoUpdateFile + ".MASTERSIGNATURE"
	if not config.plugins.StayUP.PiconType.value == "disabled_picon":
		writeLog("110 Picon Refresh Enabled")
		os.system ("touch /usr/log/" + self.PiconSignature)
		os.system ("wget -O /tmp/" + self.PiconSignature + " " + self.location_download + self.PiconSignature)
		self.fname_A = "/tmp/" + self.PiconSignature
		self.sig_A = md5(open(self.fname_A, "rb").read()).hexdigest()
		self.fname_B = "/usr/log/" + self.PiconSignature
		self.sig_B = md5(open(self.fname_B, "rb").read()).hexdigest()
		if not self.sig_A == self.sig_B:
			writeLog("120 Downloading Picon")
			os.system ("ipkg install " + self.location_download + self.PiconFile)
			os.system ("mv " + self.fname_A + " " + self.fname_B) 
		else:
			writeLog("130 Picons are already up to date")

	if not config.plugins.StayUP.SettingsType.value == "disabled_settings":
		writeLog("150 Settings Refresh Enabled")
		os.system ("touch /usr/log/" + self.SettingsSignature)
		os.system ("wget -O /tmp/" + self.SettingsSignature + " " + self.location_download + self.SettingsSignature)
		self.fname_A = "/tmp/" + self.SettingsSignature
		self.sig_A = md5(open(self.fname_A, "rb").read()).hexdigest()
		self.fname_B = "/usr/log/" + self.SettingsSignature
		self.sig_B = md5(open(self.fname_B, "rb").read()).hexdigest()
		if not self.sig_A == self.sig_B:
			writeLog("160 Installing Settings")
			os.system ("ipkg install " + self.location_download + self.SettingsFile + " -force-overwrite")
			os.system ("mv " + self.fname_A + " " + self.fname_B) 
			self.eDVBDB = eDVBDB.getInstance()
			self.eDVBDB.reloadServicelist()
			self.eDVBDB.reloadBouquets()
		else:
			writeLog("170 Settings are already up to date")

	if config.plugins.StayUP.Epg.value:
		writeLog("200 EPG Refresh Enabled")
		os.system ("touch /usr/log/" + self.EpgSignature)
		os.system ("wget -O /tmp/" + self.EpgSignature + " " + self.location_download + self.EpgSignature)
		self.fname_A = "/tmp/" + self.EpgSignature
		self.sig_A = md5(open(self.fname_A, "rb").read()).hexdigest()
		self.fname_B = "/usr/log/" + self.EpgSignature
		self.sig_B = md5(open(self.fname_B, "rb").read()).hexdigest()
		if not self.sig_A == self.sig_B:
			writeLog("210 Downloading Epg")
			self.Destination="/tmp/"
                        if os.path.ismount("/media/usb"):
                                self.Destination="/media/usb/"
                        elif os.path.isfile("/media/usb/epg.dat"):
                                writeLog("211 Trace Found")
                                self.Destination="/media/usb/"
                        elif os.path.isfile("/media/usb/epg.dat.save"):
                                writeLog("212 Trace Found")
                                self.Destination="/media/usb/"
                        elif os.path.ismount("/media/cf"):
                                self.Destination="/media/cf/"
                        elif os.path.isfile("/media/cf/epg.dat"):
                                writeLog("213 Trace Found")
                                self.Destination="/media/cf/"
                        elif os.path.isfile("/media/cf/epg.dat.save"):
                                writeLog("214 Trace Found")
                                self.Destination="/media/cf/"
                        elif os.path.ismount("/media/hdd"):
                                self.Destination="/media/hdd/"
                        elif os.path.isfile("/media/hdd/epg.dat"):
                                writeLog("215 Trace Found")
                                self.Destination="/media/hdd"
                        elif os.path.isfile("/media/hdd/epg.dat.save"):
                                writeLog("216 Trace Found")
                                self.Destination="/media/hdd"
			else:
				writeLog("225 No suitable path found for EPG Downloading")

                        if not (self.Destination == "/tmp/"):
                                os.system ("wget -O " + self.Destination + "epg.dat " + self.location_download + self.EpgFile)
                                os.system ("mv " + self.fname_A + " " + self.fname_B)
                                epg = eEPGCache.getInstance()
                                epg.reloadEpg()
                                epg.saveEpg()
                                writeLog("220 Epg Download in " + self.Destination )
                        else:
                                writeLog("225 No suitable path found for EPG Downloading")

		else:
			writeLog("230 Epg is already up to date")

	if config.plugins.StayUP.AutoUpdate.value:
		writeLog("250 AutoUpdate Enabled")
		os.system ("touch /usr/lib/enigma2/python/Plugins/Extensions/StayUP/" + self.AutoUpdateSignature)
		os.system ("wget -O /tmp/" + self.AutoUpdateSignature + " " + self.location_download + self.AutoUpdateSignature)
# aggiungere controllo return code o su esistenza files
		self.fname_A = "/tmp/" + self.AutoUpdateSignature
		self.sig_A = md5(open(self.fname_A, "rb").read()).hexdigest()
		self.fname_B = "/usr/lib/enigma2/python/Plugins/Extensions/StayUP/" + self.AutoUpdateSignature
		self.sig_B = md5(open(self.fname_B, "rb").read()).hexdigest()
		if not self.sig_A == self.sig_B:
			writeLog("260 Installing new version, please restart Enigma2" )
			os.system ("ipkg install " + self.location_download + self.AutoUpdateFile + " -force-overwrite")
			os.system ("mv " + self.fname_A + " " + self.fname_B) 
		else:
			writeLog("270 stayUP is already up to date")
