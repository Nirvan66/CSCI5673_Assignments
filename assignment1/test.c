#include <stdio.h>
#include <time.h>
#include <string.h>
#include<unistd.h>

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
	time_t rawtime = time(NULL);
	char * output;
	struct tm * timeinfo;
	timeinfo = localtime ( &rawtime );
	sprintf(output, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
	output[strlen(output)-1] = '\0';
	printf("Current Time : %s\n", output);
	return 0;
}