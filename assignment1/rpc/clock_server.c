#include "clock.h"
#include <sys/time.h>
#include <time.h>
#include <math.h>

serverTime *
time_1_svc(void *argp, struct svc_req *rqstp)
{
	static serverTime  result;

	/*
	 * insert server code here
	 */
	struct timeval tv;
	struct tm * timeinfo;

	gettimeofday(&tv, NULL); 
	timeinfo = localtime(&tv.tv_sec);
	result.receive.hours = timeinfo->tm_hour;
	result.receive.minutes = timeinfo->tm_min;
	result.receive.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));

	printf("\nServer receive time: %d:%d:%f\n", 
            result.receive.hours, result.receive.minutes, result.receive.seconds);


    gettimeofday(&tv, NULL); 
    timeinfo = localtime(&tv.tv_sec);
    result.send.hours = timeinfo->tm_hour;
    result.send.minutes = timeinfo->tm_min;
    result.send.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));
    
    printf("Server send time: %d:%d:%f\n", 
            result.send.hours, result.send.minutes, result.send.seconds);

	return &result;
}