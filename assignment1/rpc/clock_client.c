/*
 * This is sample code generated by rpcgen.
 * These are only templates and you can use them
 * as a guideline for developing your own functions.
 */

#include "clock.h"

#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#define QUERY_MINUTES 60
#define SLEEP_SECS 1
#define MAXLINE 1024 


void
time_prog_1(char *host)
{
	CLIENT *clnt;
	timetuple  *result_1;
	char *time_1_arg;

#ifndef	DEBUG
	clnt = clnt_create (host, TIME_PROG, TIME_VERS, "udp");
	if (clnt == NULL) {
		clnt_pcreateerror (host);
		exit (1);
	}
#endif	/* DEBUG */
	struct timeval tv;
	struct tm * timeinfo;
	char sendTime[MAXLINE];
	char replyTime[MAXLINE];
	char serverTime[MAXLINE];

	FILE * fp;
	fp = fopen ("rpc_output.txt","w");
	for (int i = 0; i < QUERY_MINUTES; ++i)
	{
		gettimeofday(&tv, NULL); 
		timeinfo = localtime(&tv.tv_sec);
		sprintf(sendTime, "%d:%d:%d.%ld", 
			timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
	    sendTime[strlen(sendTime)] = '\0';
	    printf("\nTime of request : %s\n", sendTime);

		result_1 = time_1((void*)&time_1_arg, clnt);
		if (result_1 == (timetuple *) NULL) {
			clnt_perror (clnt, "call failed");
		}else {
	        gettimeofday(&tv, NULL); 
			timeinfo = localtime(&tv.tv_sec);
			sprintf(replyTime, "%d:%d:%d.%ld", 
				timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
	        replyTime[strlen(replyTime)] = '\0';

	        sprintf(serverTime, "%d:%d:%d.%ld", 
	        	result_1->hours, result_1->minutes, result_1->seconds, result_1->u_seconds);
	        serverTime[strlen(serverTime)] = '\0';

	        printf("Server time: %s\n", serverTime);
	        printf("Time of reply : %s\n", replyTime);

	        fprintf (fp, "%s,%s,%s\n",sendTime,serverTime,replyTime);
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

	if (argc < 2) {
		printf ("usage: %s server_host\n", argv[0]);
		exit (1);
	}
	host = argv[1];
	time_prog_1 (host);
exit (0);
}