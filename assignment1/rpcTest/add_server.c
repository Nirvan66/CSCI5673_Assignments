/*
 * This is sample code generated by rpcgen.
 * These are only templates and you can use them
 * as a guideline for developing your own functions.
 */

#include "add.h"
#include <time.h>

intpair *
add_1_svc(void *argp, struct svc_req *rqstp)
{
	static intpair  result;

	/*
	 * insert server code here
	 */
	time_t rawtime;
	struct tm * timeinfo;
	rawtime = time(NULL);
	timeinfo = localtime ( &rawtime );
	result.a = timeinfo->tm_hour;
	result.b = timeinfo->tm_min;
	printf("returning: %d,%d\n", result.a,result.b);

	return &result;
}
