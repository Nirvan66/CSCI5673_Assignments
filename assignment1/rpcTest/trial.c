//client
add_1_arg.a = 123;
add_1_arg.b = 22;
result_1 = add_1(&add_1_arg, clnt);
if (result_1 == (intpair *) NULL) {
	clnt_perror (clnt, "call failed");
}
else {
printf("returning: %d,%d\n", result_1->a,result_1->b);
}

//server
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
