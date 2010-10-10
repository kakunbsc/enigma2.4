from Components.config import ConfigSubsection, ConfigYesNo, config, ConfigSelection, \
	ConfigText, ConfigNumber, ConfigSet, ConfigLocations, ConfigSlider, ConfigText, \
	ConfigEnableDisable, ConfigDateTime

def InitdbpConfig():
#system
	config.dbp = ConfigSubsection();
	config.dbp.einfo = ConfigYesNo(default = True)
	config.dbp.einfotimeout = ConfigNumber(default = 500)
	config.dbp.shownetdet = ConfigYesNo(default = True)
	config.dbp.emminfodelay = ConfigNumber(default = 400)
	config.dbp.ecminfodelay = ConfigNumber(default = 1000)
	config.dbp.picontype = ConfigSelection(default = "Reference", choices = [ ("Name","Name"), ("Reference","Reference") ])
	config.dbp.piconlcd = ConfigYesNo(default = False)
	config.dbp.piconlcdtype = ConfigSelection(default = "Reference", choices = [ ("Name","Name"), ("Reference","Reference") ])
	config.dbp.usevkeyboard = ConfigEnableDisable(default = False)
	config.dbp.autocloseconsole = ConfigYesNo(default = True)
	config.dbp.autocloseconsoledelay = ConfigSelection(default = "1", choices = [
		("0", _("No Delay")),("1", "1 " + _("second")),("2", "2 " + _("seconds")), 
		("3", "3 " + _("seconds")),("4", "4 " + _("seconds")),("5", "5 " + _("seconds")),
		("6", "6 " + _("seconds")),("7", "7 " + _("seconds")),("8", "8 " + _("seconds"))])
	config.dbp.usepiconinhdd = ConfigYesNo(default = False)
#inadyn
	config.inadyn = ConfigSubsection();
	config.inadyn.user = ConfigText(default = "myuser", fixed_size = False)
	config.inadyn.password = ConfigText(default = "mypassword", fixed_size = False)
	config.inadyn.alias = ConfigText(default = "mydomain.com", fixed_size = False)
	config.inadyn.period = ConfigNumber(default = 60)
	config.inadyn.system = ConfigSelection(default = "dyndns@dyndns.org", choices = [
		"dyndns@dyndns.org", "statdns@dyndns.org", "default@zoneedit.com",
		"default@no-ip.com", "custom@dyndns.org", "default@freedns.afraid.org" ])
	config.inadyn.log = ConfigSelection(default = "/var/log", choices = [
		"/tmp", "/var/log", "/usr/log" ])
#ipupdate
	config.ipupdate = ConfigSubsection();
	config.ipupdate.user = ConfigText(default = "myuser", fixed_size = False)
	config.ipupdate.password = ConfigText(default = "mypassword", fixed_size = False)
	config.ipupdate.alias = ConfigText(default = "www.mydomain.com", fixed_size = False)
	config.ipupdate.server = ConfigText(default = "mydomain.com", fixed_size = False)
	config.ipupdate.period = ConfigNumber(default = 60)
	config.ipupdate.system = ConfigSelection(default = "ezip", choices = [
		"ezip", "pgpow", "dhs", "dyndns", "dyndns-static", "ods", "tzo",
		"gnudip", "easydns", "justlinux", "dyns", "hn", "zoneedit" ])
	config.ipupdate.log = ConfigSelection(default = "/var/log", choices = [
		"/tmp", "/var/log", "/usr/log" ])
#Proxy
	config.proxy = ConfigSubsection();
	config.proxy.isactive = ConfigYesNo(default = False)
	config.proxy.server = ConfigText(default = "myserver.mydomain.com", fixed_size = False)
	config.proxy.port = ConfigNumber(default = 8080)
	config.proxy.user = ConfigText(default = "myuser", fixed_size = False)
	config.proxy.password = ConfigText(default = "mypassword", fixed_size = False)
#EPG	
	config.nemepg = ConfigSubsection();
	config.nemepg.path = ConfigSelection(default = "/media/usb", choices = [
		"/media/usb", "/media/cf", "/media/hdd"])
	config.nemepg.elemnum = ConfigNumber(default = 48)
	config.nemepg.zapdelay = ConfigSelection(default = "2", choices = [
		("1", "1 " + _("second")), ("2", "2 " + _("seconds")), ("3", "3 " + _("seconds")),("4", "4 " + _("seconds")), 
		("5", "5 " + _("seconds")), ("6", "6 " + _("seconds")), ("7", "7 " + _("seconds")), ("8", "8 " + _("seconds")), 
		("9", "9 " + _("seconds")), ("10", "10 " + _("seconds")), ("11", "11 " + _("seconds")), ("12", "12 " + _("seconds")),
		("13", "13 " + _("seconds")), ("14", "14 " + _("seconds")), ("15", "15 " + _("seconds"))])
	config.nemepg.downskyit = ConfigYesNo(default = True)
	config.nemepg.skyitch = ConfigSelection(default = "0e31:00820000:16a8:fbff:1:0", choices = [
		("0e31:00820000:16a8:fbff:1:0", "Marcopolo"), 
		("0e33:00820000:16a8:fbff:1:0", "Fox +1"), 
		("0e30:00820000:16a8:fbff:1:0", "Nuvolari")])
	config.nemepg.downskyuk = ConfigYesNo(default = False)
	config.nemepg.skyukch = ConfigSelection(default = "0fd1:011a0000:07d4:0002:2:0", choices = [
		("0fd1:011a0000:07d4:0002:2:0", "Hip Hop"), 
		("0fd0:011a0000:07d4:0002:2:0", "The Alternative-GER"), 
		("0fd2:011a0000:07d4:0002:2:0", "Rewind (80s-90s)")])
	config.nemepg.clearcache = ConfigYesNo(default = True)
	config.nemepg.clearbackup = ConfigYesNo(default = False)
	config.nemepg.enatimer = ConfigEnableDisable(default = True)

