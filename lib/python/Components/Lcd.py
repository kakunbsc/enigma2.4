from config import config, ConfigSubsection, ConfigSlider, ConfigYesNo, ConfigNothing
from enigma import eDBoxLCD
from Components.SystemInfo import SystemInfo

class LCD:
	def __init__(self):
		pass

	def setBright(self, value):
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def setContrast(self, value):
		value *= 63
		value /= 20
		if value > 63:
			value = 63
		eDBoxLCD.getInstance().setLCDContrast(value)

	def setInverted(self, value):
		if value:
			value = 255
		eDBoxLCD.getInstance().setInverted(value)

	def isOled(self):
		return eDBoxLCD.getInstance().isOled()

def InitLcd():
	detected = eDBoxLCD.getInstance().detected()
	SystemInfo["Display"] = detected
	config.lcd = ConfigSubsection();
	if detected:
		def setLCDbright(configElement):
			ilcd.setBright(configElement.value);

		def setLCDcontrast(configElement):
			ilcd.setContrast(configElement.value);

		def setLCDinverted(configElement):
			ilcd.setInverted(configElement.value);

		ilcd = LCD()

		config.lcd.lcdbri = ConfigSlider(default=3, limits=(0, 10))
		config.lcd.lcdbri.addNotifier(setLCDbright);
		config.lcd.lcdbri.apply = lambda : setLCDbright(config.lcd.lcdbri)
		config.lcd.lcdbri.callNotifiersOnSaveAndCancel = True
		
		config.lcd.standby = ConfigSlider(default=0, limits=(0, 10))
		config.lcd.standby.addNotifier(setLCDbright);
		config.lcd.standby.apply = lambda : setLCDbright(config.lcd.standby)

		config.lcd.bright = ConfigSlider(default=5, limits=(0, 10))
		config.lcd.bright.addNotifier(setLCDbright);
		config.lcd.bright.apply = lambda : setLCDbright(config.lcd.bright)
		config.lcd.bright.callNotifiersOnSaveAndCancel = True

		if not ilcd.isOled():
			config.lcd.contrast = ConfigSlider(default=5, limits=(0, 20))
			config.lcd.contrast.addNotifier(setLCDcontrast);
		else:
			config.lcd.contrast = ConfigNothing()

		config.lcd.invert = ConfigYesNo(default=False)
		config.lcd.invert.addNotifier(setLCDinverted);
	else:
		def doNothing():
			pass
		config.lcd.contrast = ConfigNothing()
		config.lcd.bright = ConfigNothing()
		config.lcd.standby = ConfigNothing()
		config.lcd.bright.apply = lambda : doNothing()
		config.lcd.standby.apply = lambda : doNothing()
