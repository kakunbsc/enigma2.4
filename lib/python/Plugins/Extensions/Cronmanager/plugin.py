#
# cronmanager plugin by gutemine
#
from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
#from Screens.ImageWizard import ImageWizard
from Plugins.Plugin import PluginDescriptor

import os

from time import *
import time
import datetime

cronmanager_path = "/etc/cron"
cronmanager_script = "/etc/cron/cronmanager.sh"
cronmanager_readme = "/usr/lib/enigma2/python/Plugins/Extensions/Cronmanager/readme.txt"

# versionstring
cronmanager_pluginversion = "2.2"

def main(session,**kwargs):
    try:    
     	session.open(Cronmanager)
    except:
        print "[CRONMANAGER] Pluginexecution failed"

def autostart(reason,**kwargs):
    if reason == 0:
        print "[CRONMANAGER] no autostart"

def Plugins(**kwargs):
    return PluginDescriptor(
        name=_("Cronmanager"), 
        description=_("plugin to do cron daemon management"), 
        where = PluginDescriptor.WHERE_PLUGINMENU,
        icon = "cronmanager.png",
        fnc = main
        )
###############################################################################

class Cronmanager(Screen):
    skin = """
        <screen position="100,100" size="500,400" title="Cronmanager Menu">
            <widget name="menu" position="10,10" size="490,390" scrollbarMode="showOnDemand" />
        </screen>""" 
        
    def __init__(self, session, args = 0):
        self.skin = Cronmanager.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
        list = []
        list.append((_("list crontab"), "list"))        
        list.append((_("add command to crontab with time"), "addwizzard"))
        list.append((_("add command to crontab with delay"), "laterwizzard"))
        list.append((_("delete crontab"), "delete"))        
        list.append((_("reload crontab"), "reload"))        
        list.append((_("info if cron daemon is running"), "info"))        
        list.append((_("show system time"), "time"))        
        list.append((_("change system time"), "changetime"))        
        list.append((_("restart options"), "restartwizzard"))
        list.append((_("help"), "help"))        
        list.append((_("readme.txt"), "readme"))        
        list.append((_("about"), "about"))        
        self["menu"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],{"ok": self.go,"back": self.close,}, -1)
        
    def go(self):
        returnValue = self["menu"].l.getCurrentSelection()[1]
        if returnValue is not None:
           if returnValue is "addwizzard":
               AddCommandWizzard(self.session)
           elif returnValue is "laterwizzard":
               LaterCommandWizzard(self.session)
           elif returnValue is "list":
             self.session.open(Console,_("Listing crontab"),["%s list" % cronmanager_script])
           elif returnValue is "delete":
             self.session.open(Console,_("Deleting crontab"),["%s delete" % cronmanager_script])
           elif returnValue is "reload":
             self.session.open(Console,_("Reloading crontab"),["%s reload" % cronmanager_script])
           elif returnValue is "info":
             self.session.open(Console,_("showing Cronmanager Info"),["%s info" % cronmanager_script])
           elif returnValue is "time":
             self.session.open(Console,_("showing system time "),["%s time" % cronmanager_script])
           elif returnValue is "changetime":
               ChangeTimeWizzard(self.session)
           elif returnValue is "restartwizzard":
               RestartWizzard(self.session)
           elif returnValue is "readme":
             self.session.open(Console,_("readme.txt of Cronmanager"),["cat %s" % cronmanager_readme])
           elif returnValue is "help":
             self.session.open(Console,_("short help on Cronmanager commands"),["%s" % cronmanager_script])
           elif returnValue is "about":
             self.session.open(MessageBox,_("Cronmanager Enigma2 Plugin Version %s by gutemine" % cronmanager_pluginversion), MessageBox.TYPE_INFO)

###############################################################################

class AddCommandWizzard(Screen):
    def __init__(self, session):

        self.session = session
        self.askForCommand()

    def askForCommand(self):
	       self.session.openWithCallback(self.processingCommand,InputBox, title=_("Enter a script to execute at time"), text="/etc/cron/examples/rmc.sh 30 8" , maxSize=False, type=Input.TEXT)

    def processingCommand(self,targetname):
        if targetname is None:
            self.skipCommand(_("Script for adding to crontab is NONE, skipping crontab add command"))
        else:
            self.targetname = targetname
            self.session.openWithCallback(self.DoCommand,MessageBox,_("are you sure to add this script to crontab: %s ?" % (self.targetname)), MessageBox.TYPE_YESNO)

    def DoCommand(self,answer):
        if answer is None:
            self.skipCommand(_("answer is None"))
        if answer is False:
            self.skipCommand(_("you were not confirming"))
        else:
            title = _("adding script %s to crontab with time") %(self.targetname)
            cmd = "%s add %s" % (cronmanager_script,self.targetname)
            self.session.open(Console,_(title),[cmd])
            
    def skipCommand(self,reason):
        self.session.open(MessageBox,_("add script to crontab was canceled, because %s") % reason, MessageBox.TYPE_WARNING)
        
###############################################################################

class LaterCommandWizzard(Screen):
    def __init__(self, session):

        self.session = session
        self.askForLaterCommand()

    def askForLaterCommand(self):
	       self.session.openWithCallback(self.processingLaterCommand,InputBox, title=_("Enter a script to execute with delay"), text="/etc/cron/examples/slt.sh 60" , maxSize=False, type=Input.TEXT)

    def processingLaterCommand(self,targetname):
        if targetname is None:
            self.skipLaterCommand(_("Script for adding to crontab is NONE, skipping crontab delay command"))
        else:
            self.targetname = targetname
            self.session.openWithCallback(self.DoLaterCommand,MessageBox,_("are you sure to add this script to crontab: %s ?") % self.targetname, MessageBox.TYPE_YESNO)

    def DoLaterCommand(self,answer):
        if answer is None:
            self.skipLaterCommand(_("answer is None"))
        if answer is False:
            self.skipLaterCommand(_("you were not confirming"))
        else:
            title = _("adding script %s to crontab with delay") %(self.targetname)
            cmd = "%s delay %s" % (cronmanager_script,self.targetname)
            self.session.open(Console,_(title),[cmd])
            
    def skipLaterCommand(self,reason):
        self.session.open(MessageBox,_("delay script to crontab was canceled, because %s") % reason, MessageBox.TYPE_WARNING)
        
###############################################################################

class RestartWizzard(Screen):
    def __init__(self, session):
        self.session = session
        self.askForRestart()
        
    def askForRestart(self):
            self.session.openWithCallback(self.askForCommand,ChoiceBox,_("select restart command to be executed"),self.getCommandList())

    def askForCommand(self,source):
        if source is None:
            self.skipRestart(_("no command passed, skipping restart"))
        else:
            self.source = source [1]
            self.session.openWithCallback(self.restartCommand,MessageBox,_("are you sure to %s") % self.source, MessageBox.TYPE_YESNO)
            
    def restartCommand(self,answer):
        if answer is None:
            self.skipRestart(_("answer is None"))
        if answer is False:
            self.skipRestart(_("you were not confirming"))
        else:
            title = _("executing command on Dreambox")
            cmd = "%s %s"  % (cronmanager_script,self.source)
            self.session.open(Console,_(title),[cmd])
            
    def skipRestart(self,reason):
        self.session.open(MessageBox,_("restart was canceled, because %s") % reason, MessageBox.TYPE_WARNING)
        
    def getCommandList(self):
        images = []
        images.append((_("info if cron daemon is running"),"info"))
        images.append((_("start cron daemon"),"start"))
        images.append((_("stop cron daemon"),"stop"))
        images.append((_("restart cron daemon"),"restart"))
        images.append((_("reboot Dreambox"),"reboot"))
        images.append((_("halt Dreambox"),"halt"))
        images.append((_("restart Enigma on Dreambox"),"kill"))
        return images

###############################################################################

class ChangeTimeWizzard(Screen):
    def __init__(self, session):

        self.session = session

        jetzt = time.time()
        timezone = datetime.datetime.utcnow()
        delta = (jetzt - time.mktime(timezone.timetuple())) 
        print "delta: %i" % delta
        print "oldtime: %i" % jetzt
        # always add 1 min so that there is time for typing
        self.oldtime = strftime("%Y:%m:%d %H:%M",localtime())
        self.session.openWithCallback(self.askForNewTime,InputBox, title=_("Enter new Systemtime - OK will restart enigma2 !"), text="%s" % (self.oldtime), maxSize=16, type=Input.NUMBER)

    def askForNewTime(self,newclock):
        try:
           length=len(newclock)
        except:
           length=0
        if newclock is None:
            self.skipChangeTime(_("no new time"))
        elif (length == 16) is False:
           self.skipChangeTime(_("new time string too short"))
        elif (newclock.count(" ") < 1) is True:
            self.skipChangeTime(_("invalid format"))
        elif (newclock.count(":") < 3) is True:
            self.skipChangeTime(_("invalid format"))
        else:
            full=[]
            full=newclock.split(" ",1)
            newdate=full[0]
            newtime=full[1]
            print "newdate %s newtime %s" % (newdate, newtime)
            parts=[]
            parts=newdate.split(":",2)
            newyear=parts[0]
            newmonth=parts[1]
            newday=parts[2]
            parts=newtime.split(":",1)
            newhour=parts[0]
            newmin=parts[1]
            #
            # da some checks to make sure that date & time are OK !
            #
            maxmonth = 31
            if (int(newmonth) == 4) or (int(newmonth) == 6) or (int(newmonth) == 9) or (int(newmonth) == 11) is True:
               maxmonth=30
            elif (int(newmonth) == 2) is True:
               if ((4*int(int(newyear)/4)) == int(newyear)) is True:
                  maxmonth=28
               else:
                  maxmonth=27
            if (int(newyear) < 2007) or (int(newyear) > 2027)  or (len(newyear) < 4) is True:
	       self.skipChangeTime(_("invalid year %s") %newyear)
            elif (int(newmonth) < 0) or (int(newmonth) >12) or (len(newmonth) < 2) is True:
               self.skipChangeTime(_("invalid month %s") %newmonth)
            elif (int(newday) < 1) or (int(newday) > maxmonth) or (len(newday) < 2) is True:
               self.skipChangeTime(_("invalid day %s") %newday)
            elif (int(newhour) < 0) or (int(newhour) > 23) or (len(newhour) < 2) is True:
	       self.skipChangeTime(_("invalid hour %s") %newhour)
            elif (int(newmin) < 0) or (int(newmin) > 59) or (len(newmin) < 2) is True:
	       self.skipChangeTime(_("invalid minute %s") %newmin)
            else:
#		self.newtime = mktime(strptime(newtime,"%Y:%m:%d %H:%M"))
	       self.newtime = "%s%s%s%s%s" %(newmonth,newday,newhour,newmin,newyear)
	       print "date %s" % self.newtime
	       self.session.openWithCallback(self.DoChangeTimeRestart,MessageBox,_("Enigma2 will restart to change Systemtime - OK ?"), MessageBox.TYPE_YESNO)

    def DoChangeTimeRestart(self,answer):
        if answer is None:
            self.skipChangeTime(_("answer is None"))
        if answer is False:
            self.skipChangeTime(_("you were not confirming"))
        else:
            os.system("date %s" % (self.newtime))
            quitMainloop(3)

    def skipChangeTime(self,reason):
        self.session.open(MessageBox,_("Change Systemtime was canceled, because %s") % reason, MessageBox.TYPE_WARNING)

