=========================================================
Cronmanager for Dreambox 7025 2.2 by gutemine from 01.05.2008
=========================================================
Cronmanager is FREEWARE, but this means also that nobody takes 
responsibility if anything goes wrong ;-)
=========================================================
Version History
=========================================================
Version 1.5     add /var/spool fix for newer images
Version 1.6     minor changes for OE 1.4 compatibility
Version 1.7     add neutrino code to cronmanager.sh
Version 2.0     enable/disable during ipkg install/remove
Version 2.1     add timezone support and system time changing option
Version 2.2     just some housekeeping
=========================================================
Thanks to ThomasLa for sorting the timezones
=========================================================
Der Englische Text ist unterhalb des Deutschen Text !
The English text is below the German text !
=========================================================
HOW-TO-CRONMANAGER 
=========================================================

Das enigma2-plugin-extensions-cronmanager*.ipk File auf /tmp deiner
Dreambox 7025 FTPen.

Dann entweder Manual Install im BP Falls das Image eines hat, oder 
in die Dreambox mit Telnet einloggen und folgendes eingeben 

cd /
ipkg install /tmp/enigma2-plugin-extensions-cronmanager*.ipk

Und falls man es wieder entfernen will:

ipkg remove enigma2-plugin-extensions-cronmanager

Nach dem install sollten im Menu Spiele/Erweiterungen der Dreambox 
bereits das Cronmanager addon auftauchen. 

Derzeit gibt es folgende eigentlich selbsterklaerende optionen des
cronmanagers:

list     .... gibt den Inhalt der crontab aus
add      .... fuegt Kommandos zur crontab hinzu mit Zeit
delay    .... fuegt Kommandos zur crontab hinzu mit Verzoegerung
delete   .... loescht die crontab
info     .... zeigt ob der cron dameon läuft
time     .... zeigt die system Zeit an die der cron dameon verwendet
start    .... startet den cron dameon
stop     .... stoppt den cron dameon
restart  .... restartet den cron daemon
reload   .... laesst den cron dameon die crontab neu laden
reboot   .... rebootet die Dreambox
halt     .... stoppt die Dreambox
kill     .... restartet enigma
readme   .... zeigt das readme.txt vom cronmanager

Der ganze cronmanager wird auf /etc/cron installiert und die crontab wird
von /var/spool/cron dorthin verlinked !

Cronmanager gibt es als addon im Spiele/Erweiterunge Menu und als script
cronmanager.sh auf /etc/cron

Man kann jetzt mit ein paar kleinen testscripts die auf /etc/cron/examples 
liegen den cronmanager testen:

slt.sh

Das ist ein script fuer einen simplen sleeptimer, im Moment macht 
es eigentlich nur ein shutdown -h now ohne irgendwelche checks
Aufpassen wenn man das zu oft mit (*) bei den minuten einplant hat
man Spass !

rmc.sh

Das ist ein kleines script das praktisch nur die enigma crashes auf 
/media/hdd entfernt. Zum Testen von rmc.sh evt. einfach dummy 
crashes mit touch anlegen und sehen wie es verschwindet wenn 
rmc.sh eingeplant ist:

touch /media/hdd/enigma2_crashes_dummy
ls /media/hdd/enigma2_crashes_* 

Das einfach vor und nach 8:30 wiederholen bzw. Zeitpunkt 
entsprechend anpassen.

iup.sh

Das ist ein kleines script das ein ipkg update & upgrade durchfuehrt
um ueber das Internet das Image mit den neuesten ipkg Files upzudaten.

fsc.sh

Das is ein kleines script das einen reboot macht bei dem ein
Filesystemcheck erzwungen wird (tut der Harddisk ab und an sicher gut)

e2r.sh

Ist ein kleines Beispielscript das mit init 2 und init 3 enigma restartet.

liv.sh

Einfach ein kleines script das auf /tmp ein alive file schreibt

Wenn man cronmanager command verwenden will, so uebergibt man als
parameter nach dem Kommando das man ausfuehren will (muss derzeit 
ein script auf /etc/cron sein) auch noch den 
Zeitpunkt fuer das ausfuehren nach folgender Syntax:

* * * * * 
- - - - -
| | | | |
| | | | ----- Tag der Woche (0 - 6) (Sonntag=0)
| | | ------- Monat (1 - 12)
| | --------- Tag des Monats (1 - 31)
| ----------- Stunde (0 - 23)
------------- Minute (0 - 59)

Das add command interface menu bietet derzeit einfach an das rmc.sh um
8:30 ausgefuehrt wird und dann die enigma crashes aufräumt.

Das Equivalent an das cronmanager shell script uebergeben waere:

/etc/cron/cronmanager.sh add /etc/cron/examples/rmc.sh 30 8

Shutdown um 23:30 waere dann:

/etc/cron/cronmanager.sh add /etc/cron/examples/slt.sh 30 23

Shutdown in 2 Stunden waere dann:

/etc/cron/cronmanager.sh delay /etc/cron/examples/slt.sh 120

Um * als eine Zeitvariable zu uebergeben, entweder %* benutzen oder
"" da * das default ist wenn kein parameter uebergeben wird.

=========================================================
Viel Spass beim Ausfuehren von cron jobs auf Deiner DM 7025 !
=========================================================
Here comes the English Version of the Documentation ...
=========================================================
HOW-TO-CRONMANAGER
=========================================================

Simply FTP the enigma2-plugin-extensions-cronmanager*.ipk file
to /tmp.

Then either do a Manual Install n BP if you Image offers one.
Or logon via telnet to your Dreambox and excute the follwing
commands.

cd /
ipkg install enigma2-plugin-extensions-cronmanager*.ipk

if you want to remove the cronmanager:

ipkg remove enigma2-plugin-extensions-cronmanager

Then in games/plugin menu of the Dreambox the Cronmanager menu should
be already showing up.

At the moment there are the following options of cronmanager available
which are more or less self explaining.

list     .... lists crontab content
add      .... adds command to crontab with time
delay    .... adds command to crontab with delay
delete   .... deletes the crontab
info     .... shows if the cron dameon is running
time     .... shows system time used by cron daemon
start    .... starts the cron dameon
stop     .... stopps the cron dameon
restart  .... restarts the cron daemon
reload   .... lets the cron dameon reload the crontab
reboot   .... reboots Dreambox
halt     .... halts Dreambox
kill     .... restarts enigma
readme   .... shows the readme.txt of cronmanager

The whole cronmanager is installed at /etc/cron and the crontab
is linke there from /var/spool/cron !

cronmanager is available as addon in games/Plugin menu and as script
cronmanager.sh at /etc/cron

You can test the cronmanager with a few small testsripts which are 
placed at /etc/cron/examples:

slt.sh

This is a script for implementing a sleeptimer, at the moment it simply 
does a shutdown -h now. Take care, if you plan this too often in cron  
you will have fun !

rmc.sh

This is a small script which simply removes the enigma crash 
dumps at /media/hdd.
For Testing rmc.sh simply create dummy crashes with touch 
and see them dissappear regulary when rmc.sh is sheduled:

touch /media/hdd/enigma2_crash_dummy
ls /media/hdd/enigma2_crash_* 

Repeat before and after 8:30 - or change the time accordingly.

iup.sh

This is a small script which does an ipkg update & upgrade for upgrading
via the internet with the latest ipkg packages.

fsc.sh

This is a small script which does a reboot with a forced filesystemcheck. 
Which is from time-to-time not bad for your harddisk.

e2r

This is a small example for restarting enigma with init 2 and init 3.

When using the command option, then after the command to be executed
you have to specify the follwoing syntax for the time when it will 
be executed:

* * * * * 
- - - - -
| | | | |
| | | | ----- day of week (0 - 6) (Sunday=0)
| | | ------- month (1 - 12)
| | --------- day of month (1 - 31)
| ----------- hour (0 - 23)
------------- min (0 - 59)

The add command in menu interface simply offers /etc/cron/rmc.sh 30 8 
which means that it will run everyday at 8:30 and
will then clean the enigma crashes.

The equivalen with the crontabmanager script would be:

/etc/cron/cronmanager.sh add /etc/cron/examples/rmc.sh 30 8

Shutdown at 23:30 would be:

/etc/cron/cronmanager.sh add /etc/cron/examples/slt.sh 30 23

Shutdown in 2 hours would be:

/etc/cron/cronmanager.sh delay /etc/cron/examples/slt.sh 120

For passing * as a timevariable either use %* or "" as 
this is the default if no argument is passed !

=========================================================
Have fun executing cron jobs on your DM 7025 !
=========================================================

