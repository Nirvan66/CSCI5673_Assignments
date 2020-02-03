//client
#include <sys/time.h>
#include <time.h>

#define QUERY_MINUTES 60
#define SLEEP_SECS 1
#define MAXLINE 1024 

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
	sprintf(sendTime, "%d:%d:%d.%ld", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
    sendTime[strlen(sendTime)] = '\0';
    printf("\nTime of request : %s\n", sendTime);

	result_1 = time_1((void*)&time_1_arg, clnt);
	if (result_1 == (timetuple *) NULL) {
		clnt_perror (clnt, "call failed");
	}else {
        gettimeofday(&tv, NULL); 
		timeinfo = localtime(&tv.tv_sec);
		sprintf(replyTime, "%d:%d:%d.%ld", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
        replyTime[strlen(replyTime)] = '\0';

        sprintf(serverTime, "%d:%d:%d", result_1->hours, result_1->minutes, result_1->seconds);
        serverTime[strlen(serverTime)] = '\0';

        printf("Server time: %s\n", serverTime);
        printf("Time of reply : %s\n", replyTime);

        fprintf (fp, "%s,%s,%s\n",sendTime,serverTime,replyTime);
        sleep(SLEEP_SECS);
	}
}



//server
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
