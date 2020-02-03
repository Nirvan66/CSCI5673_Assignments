#include <stdio.h>
#include <time.h>
#include <string.h>
#include<unistd.h>
#include <sys/time.h>

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

int main()
{
	struct timeval tv;
	char output[30];
	struct tm * timeinfo;

	gettimeofday(&tv, NULL); 
	timeinfo = localtime(&tv.tv_sec);
	sprintf(output, "%d:%d:%d.%ld", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec, tv.tv_usec);
	
	printf("Current Time : %s\n", output);


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