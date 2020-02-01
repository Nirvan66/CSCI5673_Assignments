// Client side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <time.h>
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
  
#define PORT     8080 
#define MAXLINE 1024 
#define QUERY_MINUTES 60
#define SLEEP_SECS 1

// Driver code 
int main() { 
    int sockfd; 
    char serverTime[MAXLINE]; 
    char *timeRequest = "Time please!";  
    struct sockaddr_in     servaddr; 
  
    // Creating socket file descriptor
    // domain = AF_INET for IPv4/ AF_INET6 for IPv6
    // type = SOCK_STREAM for TCP / SOCK_DGRAM for UDP
    // 
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
  
    memset(&servaddr, 0, sizeof(servaddr)); 
      
    // Filling server information 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_port = htons(PORT); 
    servaddr.sin_addr.s_addr = INADDR_ANY; 
      
    int n, len; 
    time_t rawtime;
    char sendTime[MAXLINE];
    struct tm * timeinfo;
    char replyTime[MAXLINE];
    FILE * fp;
    fp = fopen ("udp_output.txt","w");
    
    for (int i = 0; i < QUERY_MINUTES; ++i)
    {
        //request time
        rawtime = time(NULL);
        timeinfo = localtime ( &rawtime );
        sprintf(sendTime, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
        sendTime[strlen(sendTime)] = '\0';
        printf("\nTime of request : %s\n", sendTime);

        sendto(sockfd, (const char *)timeRequest, strlen(timeRequest), 
            MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
                sizeof(servaddr));
              
        n = recvfrom(sockfd, (char *)serverTime, MAXLINE,  
                    MSG_WAITALL, (struct sockaddr *) &servaddr, 
                    &len);
        serverTime[n] = '\0';

        //time of reply
        rawtime = time(NULL);
        timeinfo = localtime ( &rawtime );
        sprintf(replyTime, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
        replyTime[strlen(replyTime)] = '\0';
        printf("Time of reply : %s\n", replyTime);

        printf("Server time: %s\n", serverTime);
        fprintf (fp, "%s,%s,%s\n",sendTime,replyTime,serverTime);
        sleep(SLEEP_SECS);
    }
    fclose (fp);
    close(sockfd); 
    return 0; 
} 