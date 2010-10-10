 /*
 ****************************************************************************************************
 N E M E S I S
 Public sources
 Author: Gianathem
 Copyright (C) 2009  Nemesis - Team
 http://www.genesi-project.it/forum
 Please if you use this source, refer to Nemesis -Team

 A part of this code is based from: enigma cvs
 ****************************************************************************************************
 */
#ifndef __nemtool_h
#define __nemtool_h

#include <dirent.h>
#include <sys/vfs.h>
#include <stdio.h>
#include <string.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <lib/base/object.h>
#include <lib/base/ebase.h>

class nemTool: public eApplication, public Object
{
	static nemTool *instance;
public:
	static nemTool *getInstance() { return instance; }
	void getRegKey(const char * key, char * ris);
	void readPortNumber(char * port);
	bool sendCmd(char *command);
	int getVarSpace();
	int getVarSpacePer();
	nemTool() {}
	~nemTool();
};

#endif
