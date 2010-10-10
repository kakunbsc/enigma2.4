 /*
 ****************************************************************************************************
 N E M E S I S
 Public sources
 Author: Gianathem
 Copyright (C) 2009  Nemesis - Team
 http://www.genesi-project.it/forum
 Please if you use this source, refer to Nemesis -Team

 A part of this code is based from: enigma cvs

edit db-project 2010
 ****************************************************************************************************
 */
#include "nemtool.h"

nemTool *nemTool::instance;

void nemTool::readPortNumber(char * port)
{
	if (!instance)
		instance=this;
	char buf[256];
	FILE *in = fopen("/var/etc/dbp.cfg", "r");
	if(in)
	{	
		while (fgets(buf, 256, in))
		{
			if (strstr(buf ,"daemon_port="))
			{	
				fclose(in);
				char * pch;
				pch = strtok(buf,"=");
				pch = strtok(NULL,"=");
				strncpy(port,pch,strlen(pch));
				return;
			}
		}
		fclose(in);
	}	
	strncpy(port,"1888",4);
	return;
}

void nemTool::getRegKey(const char * key, char * ris)
{
	if (!instance)
		instance=this;
	char buf[256];
	FILE *in = fopen("settings", "rt");
	if(in)
	{	
		while (fgets(buf, 256, in))
		{
			if (strstr(buf ,key))
			{	
				char  *pch;
				fclose(in);
				pch = strtok(buf,"=");
				pch = strtok(NULL,"=");
				strcpy(ris,pch);
				return;
			}
		}
		fclose(in);
	}	
	strcpy(ris,"None");
	return;
}

bool nemTool::sendCmd(char *command)
{
	if (!instance)
		instance=this;
	bool ret = true;
	int sockfd, portno, n;
	char *strCmd;
	char buffer[256];

	struct sockaddr_in serv_addr;
	struct hostent *server;

	char port[6] = "";
	readPortNumber(port);
	portno = atoi(port);
	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0)	
		ret = false;
	else
	{	server = gethostbyname("127.0.0.1");
		if (server == NULL) 
			ret = false;
		else
		{	bzero((char *) &serv_addr, sizeof(serv_addr));
			serv_addr.sin_family = AF_INET;
			bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
			serv_addr.sin_port = htons(portno);
			if (connect(sockfd, (struct sockaddr *)&serv_addr,sizeof(serv_addr)) < 0) 
				ret = false;
			else
			{	strCmd  = command;
				n = write(sockfd,strCmd,strlen(strCmd));
				if (n < 0) ret = false;
				bzero(buffer,256);
				n = read(sockfd,buffer,255);
				if (n < 0) ret = false;
			}
			close(sockfd);
		}
	}
	return ret;
}

int nemTool::getVarSpace()
{
	if (!instance)
		instance=this;
	struct statfs s;
	char fnPath[128];
	int ris;
	strcpy(fnPath, "/");
	if((statfs(fnPath,&s)) < 0 )
		ris = -1;
	else
		ris = s.f_bfree * (s.f_bsize / 1024) - 50;
	return ris;
}

int nemTool::getVarSpacePer()
{
	if (!instance)
		instance=this;
	struct statfs s;
	char fnPath[128];
	int ris;
	strcpy(fnPath, "/");
	if((statfs(fnPath,&s)) < 0 )
		ris = 0;
	else {
		float pp = (float)s.f_bfree / (float)s.f_blocks * 100;
		char po [50];
		sprintf(po,"%f", pp);
		ris = atoi(po);
	}
	return ris;
}

nemTool::~nemTool()
{
	if (instance==this)
		instance=0;
}
