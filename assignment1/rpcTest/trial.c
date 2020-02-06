//client
#include <sys/time.h>
#include <time.h>

#define QUERY_MINUTES 60
#define SLEEP_SECS 1
#define MAXLINE 1024 

struct timetuple {
        int hours;
        int minutes;
        int seconds;
        long int u_seconds;
};
struct serverTime{
    struct timetuple receive;
    struct timetuple send;
};


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
	printf("Server address: %s, Save File: %s",host,saveFile);
	struct timeval tv;
	struct tm * timeinfo;
	char sendTime[MAXLINE];
	char replyTime[MAXLINE];
	char serverTime[MAXLINE];

	FILE * fp;
	fp = fopen (saveFile,"w");
	fprintf (fp, "Sent_Time,Server_Time,Reply_Time\n");
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

//main###############################################################
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

//server###############################################################
static timetuple  result;

/*
 * insert server code here
 */
struct timeval tv;
struct tm * timeinfo;
gettimeofday(&tv, NULL); 
timeinfo = localtime(&tv.tv_sec);

result.hours = timeinfo->tm_hour;
result.minutes = timeinfo->tm_min;
result.seconds = timeinfo->tm_sec;
result.u_seconds = tv.tv_usec;
printf("Server time sent: %d:%d:%d.%ld\n", result.hours,result.minutes,result.seconds,result.u_seconds);

return &result;


