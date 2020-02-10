#include <stdio.h>
#include <time.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
# include <math.h>
// char* getTime()
// {
//     time_t rawtime = time(NULL);;
//     char * buffer;
//     struct tm * timeinfo;
//     timeinfo = localtime ( &rawtime );
//     sprintf(buffer, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
//     buffer[strlen(buffer)-1] = '\0';
//     char currTime[strlen(buffer)]=buffer;
//     return currTime;
// }

struct timetuple {
        int hours;
        int minutes;
        float seconds;
};
struct serverTime{
    struct timetuple receive;
    struct timetuple send;
};

int main()
{
	struct serverTime  sT;
	struct timeval tv;
    struct tm * timeinfo;

	gettimeofday(&tv, NULL); 
    timeinfo = localtime(&tv.tv_sec);
    sT.receive.hours = timeinfo->tm_hour;
    sT.receive.minutes = timeinfo->tm_min;
    sT.receive.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));

    gettimeofday(&tv, NULL); 
    timeinfo = localtime(&tv.tv_sec);
    sT.send.hours = timeinfo->tm_hour;
    sT.send.minutes = timeinfo->tm_min;
    sT.send.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));

	// struct timeval tv;
	// char output[30];
	// struct tm * timeinfo;

	// gettimeofday(&tv, NULL); 
	// timeinfo = localtime(&tv.tv_sec);
	// sprintf(output, "%d:%d:%d.%ld", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
	
	// printf("Current Time : %s\n", output);


	// struct timeval tv;
	// char * output;
	// gettimeofday( &tv , NULL);
	// sprintf(output, "%ld:%ld", tv.tv_sec, tv.tv_usec);
	// printf("Current Time : %s\n", output);
	// time_t rawtime = time(NULL);
	// char * output;
	// struct tm * timeinfo;
	// timeinfo = localtime ( &rawtime );
	// sprintf(output, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
	// printf("Current Time : %s\n", output);
	return 0;
}