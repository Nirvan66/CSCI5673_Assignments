// Client side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <time.h>
#include <sys/time.h>
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <math.h>

#define PORT     8080 
#define MAXLINE 1024 
#define QUERY_MINUTES 120
#define SLEEP_SECS 60

struct timetuple {
        int hours;
        int minutes;
        float seconds;
};
struct serverTime{
    struct timetuple receive;
    struct timetuple send;
};

// Driver code 
int main(int argc, char * argv[]) { 
    int sockfd; 
    char *timeRequest = "Time please!";  
    struct sockaddr_in     servaddr;
    char * server_address;
    char * saveFile;

    if (argc == 3){
       server_address = argv[1];
       saveFile = argv[2];
    }
    else{
        printf("Please provide server address and save file name. \neg: ./client 0 udp_ouptut.txt \n");
        exit(1);
    }
  
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
    if (server_address == "0")  {
        servaddr.sin_addr.s_addr = INADDR_ANY;
    }
    else servaddr.sin_addr.s_addr = inet_addr(server_address);
    printf("Server address: %d, Save File: %s\n", servaddr.sin_addr.s_addr, saveFile);

    // time_t rawtime;
    // struct tm * timeinfo;
    // rawtime = time(NULL);
    // timeinfo = localtime ( &rawtime );
    // sprintf(sendTime, "%d:%d:%d", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);

    int n, len; 
    struct timeval tv;
    struct tm * timeinfo;
    char clientSend[MAXLINE];
    char serverReceive[MAXLINE];
    char serverSend[MAXLINE];
    char clientReceive[MAXLINE];
    struct serverTime sT;

    FILE * fp;
    fp = fopen (saveFile,"w");
    fprintf (fp, "Client_Send,Server_Receive,Server_Send,Client_Receive\n");
    
    for (int i = 0; i < QUERY_MINUTES; ++i)
    {
        //request time
        gettimeofday(&tv, NULL); 
        timeinfo = localtime(&tv.tv_sec);
        sprintf(clientSend, "%d:%d:%f", 
            timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec + (tv.tv_usec/pow(10,6)));
        clientSend[strlen(clientSend)] = '\0';
        printf("\nClient send time: %s\n", clientSend);

        sendto(sockfd, (const char *)timeRequest, strlen(timeRequest), 
            MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
                sizeof(servaddr));
              
        n = recvfrom(sockfd, (struct serverTime *)&sT, sizeof(sT),  
                    MSG_WAITALL, (struct sockaddr *) &servaddr, 
                    &len);

        //time of reply
        gettimeofday(&tv, NULL); 
        timeinfo = localtime(&tv.tv_sec);
        sprintf(clientReceive, "%d:%d:%f", 
            timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec + (tv.tv_usec/pow(10,6)));
        clientReceive[strlen(clientReceive)] = '\0';

        //Extract Server times
        sprintf(serverReceive, "%d:%d:%f",
         sT.receive.hours, sT.receive.minutes, sT.receive.seconds);
        serverReceive[strlen(serverReceive)] = '\0';

        sprintf(serverSend, "%d:%d:%f", 
            sT.send.hours, sT.send.minutes, sT.send.seconds);
        serverSend[strlen(serverSend)] = '\0';

        printf("Server receive time: %s\n", serverReceive);
        printf("Server send time: %s\n", serverSend);
        printf("Client receive time: %s\n", clientReceive);

        fprintf (fp, "%s,%s,%s,%s\n",clientSend,serverReceive,serverSend,clientReceive);
        sleep(SLEEP_SECS);
    }
    fclose (fp);
    close(sockfd);
    return 0; 
} 