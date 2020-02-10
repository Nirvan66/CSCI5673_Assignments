// Server side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <time.h>
#include <sys/time.h>
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <math.h>

#define PORT     8080 
#define MAXLINE 1024 

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
int main() { 
    int sockfd; 
    char buffer[MAXLINE]; 
    struct sockaddr_in servaddr, cliaddr;
      
    // Creating socket file descriptor 
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
      
    memset(&servaddr, 0, sizeof(servaddr));
    memset(&cliaddr, 0, sizeof(cliaddr)); 
      
    // Filling server information 
    servaddr.sin_family = AF_INET; // IPv4 
    servaddr.sin_addr.s_addr = INADDR_ANY; //inet_addr("127.0.0.1");
    servaddr.sin_port = htons(PORT); 
      
    // Bind the socket with the server address 
    if ( bind(sockfd, (const struct sockaddr *)&servaddr,  
            sizeof(servaddr)) < 0 ) 
    { 
        perror("bind failed"); 
        exit(EXIT_FAILURE); 
    } 
    
    printf("Server started at: PORT: %d, ADDRESS: %d \n",
        servaddr.sin_port, servaddr.sin_addr.s_addr);
    
    int len, n; 
    struct timeval tv;
    struct tm * timeinfo;
    struct serverTime sT;

    // char serverTime[MAXLINE];
    while(1)
    {
        len = sizeof(cliaddr);
        //Wait for time request
        n = recvfrom(sockfd, (char *)buffer, MAXLINE,  
                    MSG_WAITALL, ( struct sockaddr *) &cliaddr, 
                    &len);
        gettimeofday(&tv, NULL); 
        timeinfo = localtime(&tv.tv_sec);
        sT.receive.hours = timeinfo->tm_hour;
        sT.receive.minutes = timeinfo->tm_min;
        sT.receive.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));
        
        printf("Server receive time: %d:%d:%f\n", 
            sT.receive.hours, sT.receive.minutes, sT.receive.seconds);

        //get local time
        gettimeofday(&tv, NULL); 
        timeinfo = localtime(&tv.tv_sec);
        sT.send.hours = timeinfo->tm_hour;
        sT.send.minutes = timeinfo->tm_min;
        sT.send.seconds = timeinfo->tm_sec + (tv.tv_usec/pow(10,6));

        printf("Server send time: %d:%d:%f\n", 
            sT.send.hours, sT.send.minutes, sT.send.seconds);

        sendto(sockfd, (const struct serverTime *)&sT, sizeof(sT),  
            MSG_CONFIRM, (const struct sockaddr *) &cliaddr, 
                len);
    } 
    return 0; 
} 