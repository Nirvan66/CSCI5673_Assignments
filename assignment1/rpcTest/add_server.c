/*
 * This is sample code generated by rpcgen.
 * These are only templates and you can use them
 * as a guideline for developing your own functions.
 */

#include "add.h"

int *
add_1_svc(intpair *argp, struct svc_req *rqstp)
{
	static int  result;

	/*
	 * insert server code here
	 */
	printf("add function called\n");
	printf("parameters: %d, %d\n", argp->a, argp->b);
	result = argp->a + argp->b;
	printf("returning: %d\n", result);
	return &result;
}
