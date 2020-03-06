import queue
import socket
import struct
import regex as re
import threading 
import os, sys
import time

class FTQueue:
    def __init__(self):
        self.Q = {}
        
    def qCreate(self, label):
        qid = self.qId(label)
        if qid==-1:
            qid = max(list(self.Q.keys())+[-1])+1
            self.Q[qid] = {'que':queue.Queue(),'label':label}
        return qid
        
    def qId(self, label):
        for k,v in self.Q.items():
            if v['label'] == label:
                return k
        return -1
    
    def qPush(self, queue_id, item):
        self.Q[queue_id]['que'].put(item)
        
    def qPop(self, queue_id):
        return self.Q[queue_id]['que'].get(False)
    
    def qTop(self, queue_id):
        return self.Q[queue_id]['que'].queue[0]
    
    def qSize(self, queue_id):
        return self.Q[queue_id]['que'].qsize()
    
    def qDestroy(self, queue_id):
        del self.Q[queue_id]

def updateQueue(ftq, upComm):
    print("Recived queue update command {}".format(upComm))
    if upComm[0]=='qCreate':
        label = int(upComm[1])
        return ftq.qCreate(label)
        
    elif upComm[0]=='qId':
        label = int(upComm[1])
        return ftq.qId(label)
        
    elif upComm[0]=='qPush':
        queue_id = int(upComm[1])
        item = int(upComm[2])
        ftq.qPush(queue_id, item)
        
    elif upComm[0]=='qPop':
        queue_id = int(upComm[1])
        return ftq.qPop(queue_id)
        
    elif upComm[0]=='qTop':
        queue_id = int(upComm[1])
        return ftq.qTop(queue_id)
        
    elif upComm[0]=='qSize':
        queue_id = int(upComm[1])
        return ftq.qSize(queue_id)
        
    elif upComm[0]=='qDestroy':
        queue_id = int(upComm[1])
        ftq.qDestroy(queue_id)

def mutiListner():
    '''
    Listens to group socket for messages
    '''
    print("Running Multicast Listner")
    while(multiRunning):
        data, addr = mcast_sock.recvfrom(10240)
        if addr!=uniAddrPort:
            command = data.decode().split(',')
            print("Received {} from {}".format(command, addr))
            commands.append((command, addr))

def uniListner():
    '''
    Listens to unicast socket for messages
    '''
    print("Running Unicast Listner")
    while(uniRunning):
        data, addr = ucast_sock.recvfrom(10240)
        if addr!=uniAddrPort:
            command = data.decode().split(',')
            print("Received {} from {}".format(command, addr))
            commands.append((command, addr))

def middlewareThread():
    global globalSeq
    while(comRunning):
        time.sleep(0.5)
        if len(commands):
            c = commands.pop(0)
            command = c[0]
            addr = c[1]
            print("Processing command {} from {}".format(command,addr))
            # if another member sends a join request to already existing group
            if command[0]=='joinRequest':
                newMemberNum = int(command[1])
                print("Received join request from {}".format(newMemberNum))
                # if number already exists denie join request
                if newMemberNum in groupMembers.keys():
                    print("Member request for {} denied".format(newMemberNum))
                    denJoin = ('joinDenied',)
                    denJoin = ",".join(map(lambda x: str(x),denJoin))
                    ucast_sock.sendto(str.encode(denJoin), addr)
                # if member number does not exist accept join request
                # send conformation with your member number
                else:
                    print("Member request for {} accepted".format(newMemberNum))
                    groupMembers[newMemberNum] = addr
                    confJoin = ('joinConfirm', memberNumber)
                    confJoin = ",".join(map(lambda x: str(x),confJoin))
                    ucast_sock.sendto(str.encode(confJoin), addr)

            # collect confirmation messages sent by other group members.
            # collect member numbers and addresses.
            elif command[0]=='joinConfirm':
                print("Received join confirmation from {}".format(int(command[1])))
                groupMembers[int(command[1])] = addr

            # if denied exit for now     
            elif command[0]=='joinDenied':
                print("MEMBER NUMBER {} ALREADY EXISTS. PICK ANOTHER".format(memberNumber))
                time.sleep(0.5)
                os._exit(0)

            # if sequence number is received for a message
            elif command[0]=='seq':
                msgid = command[1]
                seqNo = int(command[2])
                print("Received sequence number {} from {}".format(seqNo, seqNo%len(groupMembers)))
                if seqNo==globalSeq:
                    print("Sequence number {} EQUALS {}".format(seqNo,globalSeq))
                    globalSeq = seqNo + 1
                    updateQueue(FTq, messages[msgid][0])
                    del messages[msgid]
                    print("Message {} processed and un buffered".format(msgid))
                else:
                    print("Dropped sequence message {} TOO BIG".format(seqNo))
                            
            # if a msg is recived from the client
            elif command[0]=='msg':
                if command[1] not in messages.keys():
                    print("Received msg {} with id {}".format(command[2:],command[1]))
                    if globalSeq%len(groupMembers) == memberNumber:
                        print("SEQUENCING MESSAGE")
                        seqNumsSent[globalSeq] = command[1]
                        # if globalSeq not in testLostMessages:       #TESTING STUFF
                        segM = ('seq', command[1], globalSeq)
                        segM = ",".join(map(lambda x: str(x),segM))
                        ucast_sock.sendto(str.encode(segM), (MCAST_GRP, MCAST_PORT))
                        globalSeq = globalSeq + 1
                        ret = updateQueue(FTq, command[2:])
                        if ret!=None:
                            print("Sending: {}".format(ret))
                            ucast_sock.sendto(str.encode(str(ret)), addr)
                    else:
                        print("NOT SEQUENCING MESSAGE")
                        messages[command[1]] = (command[2:],addr)
            # if some group member misses sequenceing a message
            # it asks for a retransmission of that sequence message
            # from the memeber responsible for creating the sequence.
            elif command[0]=='reseq':
                seqNum = int(command[1])
                print("Received reseq message for seq num {}".format(seqNum))
                seqM = ('seq', seqNumsSent[seqNum], seqNum)
                seqM = ",".join(map(lambda x: str(x),seqM))
                ucast_sock.sendto(str.encode(seqM), addr)
                
            else:
                print("Invalid Command")
        # messages end up being buffer due to message losses
        # handles Negative acknowledgement     
        elif len(messages):
            seqsrNum = (globalSeq)%len(groupMembers)
            # if not testBuildup:                           #TESTING STUFF
            if seqsrNum == memberNumber:
                rndMsg = messages.keys()[0]
                print("Caught up with message losses. SQUENCING {}".format(rndMsg))
                seqNumsSent[globalSeq] = rndMsg
                seqM = ('seq', rndMsg, globalSeq)
                seqM = ",".join(map(lambda x: str(x),seqM))
                ucast_sock.sendto(str.encode(seqM), (MCAST_GRP, MCAST_PORT))
                globalSeq = globalSeq + 1
                ret = updateQueue(FTq, messages[rndMsg][0])
                if ret!=None:
                    print("Caught up. Sending: {}".format(ret))
                    addr = messages[rndMsg][1]
                    ucast_sock.sendto(str.encode(str(ret)), addr)
                del messages[rndMsg]
                print("All caught up. Message {} un buffered".format(msgid))
            else:
                seqsrAddr = groupMembers[seqsrNum]
                print("Re requesting seguence number {} from group member {}"
                      .format(globalSeq,seqsrNum))
                reseqM = ('reseq', globalSeq)
                reseqM = ",".join(map(lambda x: str(x),reseqM))
                ucast_sock.sendto(str.encode(reseqM), seqsrAddr)

if __name__=="__main__":
    #buffers all unicast and multicast messages
    # to be processed by middlewareThread 
    commands = []

    # Tread to listen for multicast messages
    multiRunning = True
    multiThread = threading.Thread(target=mutiListner, name='multicast')
    multiThread.daemon = True
    multiThread.start()

    # Tread to listen for unicast messages
    uniRunning = True
    uniThread = threading.Thread(target=uniListner, name='unicast')
    uniThread.daemon = True
    uniThread.start()