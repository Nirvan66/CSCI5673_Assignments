/*
Creators: Nirvan S.P. Theethira, Zach McGrath
Date: 02/10/2020
Purpose: CSCI5673 Assignment 1
Description: Client side implementation of RPC client-server model

Sample Build:
    make
Sample Run:
    ./clock_client localhost test.txt
Note: run server on the same address before client
*/

#include "clock.h"
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define QUERY_MINUTES 120
#define SLEEP_SECS 60
#define MAXLINE 1024


void
time_prog_1(char *host, char * saveFile)
{
	CLIENT *clnt;
	serverTime  *result_1;
	char *time_1_arg;

#ifndef	DEBUG
	clnt = clnt_create (host, TIME_PROG, TIME_VERS, "udp");
	if (clnt == NULL) {
		clnt_pcreateerror (host);
		exit (1);
	}
#endif	/* DEBUG */
	printf("Server address: %s, Save File: %s\n",host,saveFile);
	struct timeval tv;
	struct tm * timeinfo;
	char clientSend[MAXLINE];
    char serverReceive[MAXLINE];
    char serverSend[MAXLINE];
    char clientReceive[MAXLINE];

    FILE * fp;
	fp = fopen (saveFile,"w");
	fprintf (fp, "Client_Send,Server_Receive,Server_Send,Client_Receive\n");
	for (int i = 0; i < QUERY_MINUTES; ++i)
    {	//time of client send
    	gettimeofday(&tv, NULL); 
        timeinfo = localtime(&tv.tv_sec);
        sprintf(clientSend, "%d:%d:%f", 
            timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec + (tv.tv_usec/pow(10,6)));
        clientSend[strlen(clientSend)] = '\0';
        printf("\nClient send time: %s\n", clientSend);

		result_1 = time_1((void*)&time_1_arg, clnt);
		if (result_1 == (serverTime *) NULL) {
			clnt_perror (clnt, "call failed");
		}else{
			//time of client receive
			gettimeofday(&tv, NULL); 
	        timeinfo = localtime(&tv.tv_sec);
	        sprintf(clientReceive, "%d:%d:%f", 
	            timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec + (tv.tv_usec/pow(10,6)));
	        clientReceive[strlen(clientReceive)] = '\0';


	        //Extract Server times
	        sprintf(serverReceive, "%d:%d:%f",
	         result_1->receive.hours, result_1->receive.minutes, result_1->receive.seconds);
	        serverReceive[strlen(serverReceive)] = '\0';

	        sprintf(serverSend, "%d:%d:%f", 
	            result_1->send.hours, result_1->send.minutes, result_1->send.seconds);
	        serverSend[strlen(serverSend)] = '\0';

	        printf("Server receive time: %s\n", serverReceive);
	        printf("Server send time: %s\n", serverSend);
	        printf("Client receive time: %s\n", clientReceive);

	        fprintf (fp, "%s,%s,%s,%s\n",clientSend,serverReceive,serverSend,clientReceive);
	        sleep(SLEEP_SECS);
		}
	}
#ifndef	DEBUG
	clnt_destroy (clnt);
#endif	 /* DEBUG */
}


int
main (int argc, char *argv[])
{
	char *host;
	char *saveFile;

	if (argc < 3) {
		printf("Please provide server address and save file name. \neg: ./clock_client localhost rpc_ouptut.txt \n");
		exit (1);
	}
	host = argv[1];
	saveFile = argv[2];
	time_prog_1 (host,saveFile);
exit (0);
}