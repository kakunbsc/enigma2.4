from Components.config import ConfigSubsection, config
from Tools.LoadPixmap import LoadPixmap

config.plugins = ConfigSubsection()

class PluginDescriptor:
	"""An object to describe a plugin."""
	
	# where to list the plugin. Note that there are different call arguments,
	# so you might not be able to combine them.
	
	# supported arguments are:
	#   session
	#   servicereference
	#   reason
	
	# you have to ignore unknown kwargs!
	
	# argument: session
	WHERE_EXTENSIONSMENU = 0
	WHERE_MAINMENU = 1
	WHERE_PLUGINMENU  = 2
	# argument: session, serviceref (currently selected)
	WHERE_MOVIELIST = 3
	# argument: menuid. Fnc must return list with menuitems (4-tuple of name, fnc to call, entryid or None, weight or None)
	WHERE_MENU = 4
	
	# reason (0: start, 1: end)
	WHERE_AUTOSTART = 5
	
	# start as wizard. In that case, fnc must be tuple (priority,class) with class being a screen class!
	WHERE_WIZARD = 6
	
	# like autostart, but for a session. currently, only session starts are 
	# delivered, and only on pre-loaded plugins
	WHERE_SESSIONSTART = 7
	
	# start as teletext plugin. arguments: session, serviceref
	WHERE_TELETEXT = 8
	
	# file-scanner, fnc must return a list of Scanners
	WHERE_FILESCAN = 9
	
	# fnc must take an interface name as parameter and return None if the plugin supports an extended setup
	# or return a function which is called with session and the interface name for extended setup of this interface
	WHERE_NETWORKSETUP = 10
	
	# show up this plugin (or a choicebox with all of them) for long INFO keypress
	# or return a function which is called with session and the interface name for extended setup of this interface
	WHERE_EVENTINFO = 11

	# reason (True: Networkconfig read finished, False: Networkconfig reload initiated )
	WHERE_NETWORKCONFIG_READ = 12

	def __init__(self, name = "Plugin", where = [ ], description = "", icon = None, fnc = None, wakeupfnc = None, internal = False):
		self.name = name
		self.internal = internal
		if isinstance(where, list):
			self.where = where
		else:
			self.where = [ where ]
		self.description = description

		if icon is None or isinstance(icon, str):
			self.iconstr = icon
			self.icon = None
		else:
			self.icon = icon

		self.wakeupfnc = wakeupfnc

		self.__call__ = fnc

	def updateIcon(self, path):
		if isinstance(self.iconstr, str):
			self.icon = LoadPixmap('/'.join((path, self.iconstr)))
		else:
			self.icon = None

	def getWakeupTime(self):
		return self.wakeupfnc and self.wakeupfnc() or -1

	def __eq__(self, other):
		return self.__call__ == other.__call__
