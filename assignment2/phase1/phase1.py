'''
Creators: Nirvan S P Theethira, Zach Allen McGrath
Date: 3/6/2020
Purpose: Used to run a member of the group of replicated
FTQueue database.

SAMPLE RUN LINUX: 
python phaseO.py --uniAddr 127.0.0.1 --uniPort 8080 --memberNumber 0

SAMPLE RUN MACOS: 
python phaseO.py --uniAddr <Private IP Address> --uniPort 8080 --memberNumber 0 --IS_MACOS True

SAMPLE HELP RUN:
python phaseO.py --help

Note: Change uniPort and memberNumber when staring new members.
'''

import queue
import socket
import struct
import regex as re
import threading 
import os, sys
import time
import argparse
import pickle
import codecs
import uuid
import copy
import random

class FTQueue:
    '''
    Class to maintain, update and query the FTQueue data structure
    '''
    def __init__(self):
        '''
        Initialized FTQueue to empty dictionary
        FTQueue dictionary structure:
            {<queue_id>: {'que': <queue.Queue object at 0x7ff4dc191110>, 'label': <label>} ...}
        Sample FTQueue dictionary:
            {0: {'que': <queue.Queue object at 0x7ff4dc191110>, 'label': 12} , 1: ...}

        '''
        self.Q = {}
        
    def qCreate(self, label):
        '''
        If a queue with the label does not exist create one and return its queue_id
        else return queue_id of existing queue with the label
        Params:
            label: int
        Return: 
            -1 or int
        '''
        qid = self.qId(label)
        if qid==-1:
            qid = max(list(self.Q.keys())+[-1])+1
            self.Q[qid] = {'que':queue.Queue(),'label':label}
        return qid
        
    def qId(self, label):
        '''
        Gives the queue_id of the queue with the label if it exists
        Otherwise return -1
        Params:
            label: int
        Return: 
            -1 or int
        '''
        for k,v in self.Q.items():
            if v['label'] == label:
                return k
        return -1
    
    def qPush(self, queue_id, item):
        '''
        Pushes item into queue with queue_id if it exists.
        Params:
            queue_id: int
            item: int
        Return: 
            None
        '''
        try:
            self.Q[queue_id]['que'].put(item)
        except:
            pass
        
    def qPop(self, queue_id):
        '''
        Pops item from queue with queue_id in FIFO order if it exists.
        Params:
            queue_id: int
        Return: 
            int or -1
        '''
        if self.qSize(queue_id)!=-1 and self.qSize(queue_id)!=0:
            return self.Q[queue_id]['que'].get(False)
        else:
            return -1
    
    def qTop(self, queue_id):
        '''
        Gives top item of queue with queue_id in FIFO order if it exists.
        Params:
            queue_id: int
        Return: 
            int or -1
        '''
        if self.qSize(queue_id)!=-1 and self.qSize(queue_id)!=0:
            return self.Q[queue_id]['que'].queue[0]
        else:
            return -1
    
    def qSize(self, queue_id):
        '''
        Gives queue size of queue with queue_id in FIFO order if it exists.
        Params:
            queue_id: int
        Return: 
            int or -1
        '''
        try:
            return self.Q[queue_id]['que'].qsize()
        except: 
            return -1
    
    def qDestroy(self, queue_id):
        '''
        Discards queue with queue_id in FIFO order if it exists.
        Params:
            queue_id: int
        Return: 
            None
        '''
        try:
            del self.Q[queue_id]
        except:
            pass

def updateQueue(ftq, upComm):
    '''
    Process valid FTQueue operations sent by the client
    Params:
        ftq: FTQueue
            Instance of FTQueue to operate on.
        upComm: list
            structure:[<valid-Opperation>, <queue_id>, <item>]
            sample: ['qPush', '0', '10']
    Return:
        None or int    
    '''
    print("Running queue operation {}".format(upComm))
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

def mutiListner(multiRunning, commands, mcast_sock, uniAddrPort):
    '''
    Thread to listen to group socket for incomming data packets.
    Params:
        multiRunning: list
            Used as flag to terminate while loop of multiThread
            thread terminates when the len of multiRunning is greater than 0. aka insert element
            cannot use bool type for this as it is immutable
            https://robertheaton.com/2014/02/09/pythons-pass-by-object-reference-as-explained-by-philip-k-dick/
        commands: list
            Buffer stores data packets received by multiThread thread and uniThread thread
        mcast_sock: socket.socket
            Multicast socket
        uniAddrPort: tuple
            Unicast socket address. eg: ("127.0.0.1", 8080)
    '''
    print("Running Multicast Listner")
    while(len(multiRunning)==0):
        try:
            data, addr = mcast_sock.recvfrom(10240)
            # Messages broadcasted to the group addr will be sent back to the server
            # prevent processing messages sent by this server by checking if sender address equals your address.
            # Prevents infinte processing loops.
            if addr!=uniAddrPort:
                command = data.decode().split(',')
                print("Received {} from {}".format(command, addr))
                commands.append((command, addr))
        except:
            continue

def uniListner(uniRunning, commands, ucast_sock, uniAddrPort):
    '''
    Listens to unicast socket for messages
    Params:
        uniRunning: list
            Used as flag to terminate while loop of uniThread
            thread terminates when the len of uniRunning is greater than 0. aka insert element
            cannot use bool type for this as it is immutable
            https://robertheaton.com/2014/02/09/pythons-pass-by-object-reference-as-explained-by-philip-k-dick/
        commands: list
            Buffer stores data packets received by multiThread thread and uniThread thread
        ucast_sock: socket.socket
            Unicast socket
        uniAddrPort: tuple
            Unicast socket address. eg: ("127.0.0.1", 8080)
    '''
    print("Running Unicast Listner")
    while(len(uniRunning)==0):
        try:
            data, addr = ucast_sock.recvfrom(10240)
            if addr!=uniAddrPort:
                command = data.decode().split(',')
                print("Received {} from {}".format(command, addr))
                commands.append((command, addr))
        except:
            continue

def middlewareThread(midRunning, globalSeq, memberNumber, viewMemberNumber, groupID, logs,
    groupMembers, FTq, commands, messages, seqNumsSent, 
    ucast_sock, ucastAddrPort, multiAddrPort, nakCount, nakAllowance):
    '''
    THREAD to check if commands have been received by the sockets by checking commands buffer.
    Pops item from commands buffer in FIFO order and process it.
    Params:
        midRunning: list
            Used as flag to terminate while loop of midThread
            thread terminates when the len of midRunning is greater than 0. aka insert element
            cannot use bool type for this as it is immutable
            https://robertheaton.com/2014/02/09/pythons-pass-by-object-reference-as-explained-by-philip-k-dick/
        globalSeq: list
            List contains a single element at 0 that holds the global sequence number and is incremented.
            Only first element is ever used and no elemets are ever added. 
            Cannot use int type for this as it is immutable.
        memberNumber: int
            Unique number of this group member. Does not change
        viewMemberNumber: int
            Unique number for this view. Updated as members drop/join
        groupID: UUID
            Group number. Changed with every member update
        logs: list
            List to keep track of logs
        groupMembers: dict
            Group member numbers and their addresses. Updated when new members join
            Sample: {0: {address: ('127.0.0.1', 8080), memberNumber: 0}, 1: {address: ('127.0.0.1', 8081), memberNumber: 3}, ...}
        ftq: FTQueue
            Instance of FTQueue to operate on.
        commands: list
            Buffer containing data packets received by multiThread thread and uniThread thread
        messages: dict 
            Buffer to store messages sent by client. Done so it can be run when a sequence message
            is recived from another server
            structure: {<message id>: ([<queue-operation>], (<client addr>)),}
            sample: {'f86a7de6-b673-4579-ab6c-daecc36459d6': (['qPush', '0', '10'], ('127.0.0.1', 20001)), ...}
        seqNumsSent: dict
            all sequence numbers assigned/generated by this server
            used to resend sequence number when NAK is sent from other servers
            structure: {<seq-no>: '<message id>'}
            sample: {1: '20462544-f02d-4b49-ba93-c55f6bad7d0d'}
        ucast_sock: socket.socket
            Unicast socket
        multiAddrPort: tuple
            Multicast socket address. eg: ('224.0.0.1', 5050)
        nakCount: int 
            Counter to keep track of number of nak messages sent
        nakAllowance: int
            Number of nak messages allowed to be sent before assuming a member is dead
    '''
    partitionMsgCountDown = 3
    isPartitioned = False
    while(len(midRunning)==0):
        time.sleep(0.01)
        if len(commands):
            print('')
            c = commands.pop(0)
            command = c[0]
            addr = c[1]
            incomingGroupID = str(command[1]) if len(command) > 1 else None
            print("Processing command {} from {}".format(command,addr))
            # if another member sends a join request to already existing group
            if command[0]=='joinRequest':
                # sample: (['joinRequest', '1', '0'], ('127.0.0.1', 8081))
                #(['joinRequest', memberNumber, groupID])
                newMemberNum = int(command[2])
                print("Received join request from {}".format(newMemberNum))
                
                # check to see that I should reply
                if globalSeq[0]%len(groupMembers) == viewMemberNumber:
                    print('Adding new member to group')
                    # check to see what member number was requested
                    # if the proposed number is in the existing members, choose max + 1
                    memberNumbers = [x['memberNumber'] for _, x in groupMembers.items()]
                    if newMemberNum in memberNumbers:
                        newMemberNum = max(memberNumbers) + 1
                    # give the new member number view member the max + 1 of the keys of groupMembers
                    newViewMemberNumber = len(groupMembers) 
                    groupMembers[newViewMemberNumber] = {
                        'address': addr,
                        'memberNumber': newMemberNum
                    }
                    oldGroupID = copy.deepcopy(groupID)
                    groupID = str(uuid.uuid4())
                    print('New member accepted with memberNumber {} and viewMemberNumber {}'.format(newMemberNum, newViewMemberNumber))
                    print('New group ID is {}'.format(groupID))
                    # Update the new member with the existing members
                    # joinConfirm message will be of the following form
                    # (['joinConfirm', <sender memberNumber>, <groupMmembers>, 
                    # <assigned new member number>, globalSeq], (<sender UCAST_IP>, <sender UCAST_PORT>))
                    # groupMembers has to be encoded to avoid being split on string
                    confJoin = ('joinConfirm', 
                                groupID,
                                memberNumber, 
                                codecs.encode(pickle.dumps(groupMembers), "base64").decode(), 
                                newViewMemberNumber, 
                                globalSeq[0]
                               )
                    confJoin = ",".join(map(lambda x: str(x),confJoin))
                    ucast_sock.sendto(str.encode(confJoin), addr)
                    # send a member update to all members so that they have the updated groupMembers
                    memberUpdateMsg = ('membershipUpdate', oldGroupID, groupID, codecs.encode(pickle.dumps(groupMembers), "base64").decode(), groupID)
                    memberUpdateMsg = ','.join(map(lambda x: str(x), memberUpdateMsg))
                    ucast_sock.sendto(str.encode(memberUpdateMsg), multiAddrPort)

            # collect confirmation messages sent by other group members.
            # collect member numbers and addresses.
            elif command[0]=='joinConfirm':
                # sample: (['joinConfirm', '0', groupMembersDictionary, newViewMemberNumber, globalSeqNum], ('127.0.0.1', 8080))
                print("Received join confirmation from {}".format(int(command[2])))
                groupID = incomingGroupID
                # update myself with the current member list, my assigned member number, and the globalSeq
                groupMembers = pickle.loads(codecs.decode(command[3].encode(), "base64"))
                viewMemberNumber = int(command[4])
                memberNumber = groupMembers[viewMemberNumber]['memberNumber']
                globalSeq[0] = int(command[5])
                print('GROUP MEMBERSHIP AFTER JOINING:')
                print(groupMembers)
                print('Joined group number {}'.format(groupID))
                # send a request to the sender for updated logs
                logReqMsg = ('logsRequest', groupID)
                logReqMsg = ','.join(map(lambda x: str(x), logReqMsg))
                ucast_sock.sendto(str.encode(logReqMsg), addr)

            # the sender requested the logs to update their own queues
            elif command[0] == 'logsRequest':
                #PARTITION TESTING
                if incomingGroupID != groupID:
                    continue
                # (logsDeliver, <comma separated logs>)
                print('Requesting logs from {}'.format(str(addr)))
                logDeliverMsg = ('logsDeliver', groupID, ','.join(logs))
                logDeliverMsg = ",".join(map(lambda x: str(x),logDeliverMsg))
                ucast_sock.sendto(str.encode(logDeliverMsg), addr)
                
            # get update on logs requested if a new member
            elif command[0] == 'logsDeliver':
                #PARTITION TESTING
                if incomingGroupID != groupID:
                    continue
                # iterate through all of the values and update queue   
                logs = copy.deepcopy(command[2:])
                print('\nCopied logs. Saved logs:')
                print(logs)
                for i in range(len(command[2:])):
                    if command[2 + i] == '' or command[2 + i] is None:
                        continue
                    logEntry = command[2 + i].split(':')
                    logEntry = logEntry[1:]
                    op = logEntry[0]
                    params = logEntry[1:]
                    print('Next log update is:')
                    print([op] + params)
                    updateQueue(FTq, [op] + params)
                
            # someone died or partion, someone sent a membership update
            elif command[0] == 'membershipUpdate':
                #PARTITION TESTING
                if incomingGroupID != groupID:
                    print('\n NOT SAME GROUP IDS IN MEMBERSHIP UPDATE')
                    print('incomingGroupID')
                    print(incomingGroupID)
                    print('groupID')
                    print(groupID)
                    continue
                nakCount = 0
                print('MEMBERSHIP UPDATE OCCURED. RECIEVED FROM {}'.format(addr))
                # decode message 
                # message format: ('membershipUpdate', oldGroupID, newGroupID, groupMembers(encoded))
                groupMembers = pickle.loads(codecs.decode(command[3].encode(), "base64"))
                # new groupID is the command[2]
                groupID = str(command[2])
                # find our new membership number by looking in the dictionary
                for viewNum, membership in groupMembers.items():
                    if membership['memberNumber'] == memberNumber:
                        viewMemberNumber = viewNum
                print('New groupID: {}'.format(groupID))
                print('Group members after update:')
                print(groupMembers)
                print('member number {} has new view number {}'.format(memberNumber, viewMemberNumber))

            # if sequence number is received for a message
            elif command[0]=='seq':
                # PARTITION TESTING
                if incomingGroupID != groupID:
                    print('\noof not taking this sequence from {}\n'.format(addr))
                    continue
                # if we sent a reseq we want to clear the count
                nakCount = 0
                # sample: (['seq', groupID, '20462544-f02d-4b49-ba93-c55f6bad7d0d', '1'], ('127.0.0.1', 8081))
                msgid = command[2]
                seqNo = int(command[3])
                print("Received sequence number {} from {}".format(seqNo, seqNo%len(groupMembers)))
                # if recived seq number equal this servers global seq process the message 
                # corresponding to the sequence message.
                if seqNo==globalSeq[0]:
                    print("Sequence number {} EQUALS {}".format(seqNo,globalSeq[0]))
                    globalSeq[0] = seqNo + 1
                    updateQueue(FTq, messages[msgid][0])
                    logUpdate = ':'.join([groupID] + messages[msgid][0])
                    logs.append(logUpdate)
                    del messages[msgid]
                    print("Incrementing global seq number to {}".format(globalSeq[0]))
                    print("Message {} processed and un buffered".format(msgid))
                else:
                    # if its greater then this server has missed something.
                    # the `elif len(messages)` handles this by checking message buffer
                    # and sends NAK
                    print("Dropped sequence message {} TOO BIG".format(seqNo))
                            
            # if a msg is recived from the client
            elif command[0]=='msg':
                # PARTITION TESTING
                if isPartitioned:
                    if partitionMsgCountDown <= 0 and globalSeq[0]%len(groupMembers) == viewMemberNumber:
                        #since msg is sent to all partitions (as its on the same machine) sleep for a second
                        time.sleep(1)
                        isPartitioned = False 
                        # send a group message join if lowest group member 
                        print('\nCounter for partition rejoining at 0. Requesting to rejoin')
                        # send them the logs so that they update
                        groupJoinReqMsg = ('groupJoinReq', groupID, ','.join(logs))
                        groupJoinReqMsg = ','.join(map(lambda x: str(x), groupJoinReqMsg))
                        ucast_sock.sendto(str.encode(groupJoinReqMsg), multiAddrPort)
                        continue
                    else:
                        print('Decrementing partition message counter from {} to {}'.format(partitionMsgCountDown, partitionMsgCountDown-1))
                        partitionMsgCountDown -= 1
                
                # sample: (['msg', 'f93cf88d-ed6c-48f4-85d0-b483e589afb0', 'qCreate', '12'], ('127.0.0.1', 20001))
                if command[1] not in messages.keys():
                    print("Received msg {} with id {}".format(command[2:],command[1]))
                    # check if this sever is the sequencer
                    if globalSeq[0]%len(groupMembers) == viewMemberNumber:
                        print("SEQUENCING MESSAGE as {}".format(globalSeq[0]))
                        seqNumsSent[globalSeq[0]] = command[1]
                        # send sequence number and message id to other members
                        segM = ('seq', groupID, command[1], globalSeq[0])
                        segM = ",".join(map(lambda x: str(x),segM))
                        ucast_sock.sendto(str.encode(segM), multiAddrPort)
                        globalSeq[0] = globalSeq[0] + 1
                        print("Incrementing global seq number to {}".format(globalSeq[0]))
                        ret = updateQueue(FTq, command[2:])
                        logUpdate = ':'.join([groupID] + command[2:])
                        logs.append(logUpdate)
                        print('Updated logs. Appended new command: {}'.format(logUpdate))
                        if ret!=None:
                            print("Sending: {}".format(ret))
                            ucast_sock.sendto(str.encode(str(ret)), addr)
                    else:
                        # if this server is not the sequencer,
                        # buffer message and wait for sequence message.
                        print("NOT SEQUENCING MESSAGE")
                        messages[command[1]] = (command[2:],addr)
                        
            elif command[0] == 'groupJoinReq':
                # have a group of processes join a group
                isPartitioned = False
                # only reply if its my turn to reply
                print('\ngroupJonReq with viewMemberNumber {} and globalSeq {} mod len groupMembers {}\n'.format(viewMemberNumber, globalSeq[0], len(groupMembers)))
                if globalSeq[0]%len(groupMembers) == viewMemberNumber:
                    # take in the logs from the other partition
                    otherPartitionLogs = command[2:]
                    # iterate through their logs and our logs to see which logs we share. 
                    # Arbitrarily take the lower groupID logs first at the split
                    # MERGING THE TWO LOGS
                    totalLog = []
                    for i in range(max(len(logs), len(otherPartitionLogs))):
                        log = logs[i].split(':') if i < len(logs) else []
                        otherLog = otherPartitionLogs[i].split(':') if i < len(otherPartitionLogs) else []
                        if len(otherLog) > 0 and len(log) > 0 and otherLog[0] == log[0]:
                            totalLog.append(logs[i])
                        elif len(otherLog) > 0 and len(log) > 0 and otherLog[0] < log[0]:
                            totalLog += otherPartitionLogs[i:]
                            totalLog += logs[i:]
                            break
                        elif len(otherLog) > 0 and len(log) > 0:
                            totalLog += logs[i:]
                            totalLog += otherPartitionLogs[i:]
                            break
                        elif len(otherLog) == 0 and len(log) > 0:
                            totalLog += logs[i:]
                            break
                        elif len(otherLog) > 0 and len(log) == 0:
                            totalLog += otherPartitionLogs[i:]
                            break
                    # we now have the total logs
                    # clear our queues and do these log updates
                    print('Updated logs to be')
                    print(totalLog)
                    FTq = None
                    FTq = FTQueue()
                    for log in totalLog:
                        l = log.split(':')
                        updateQueue(FTq, l)
                    # update our logs to be the totalLogs
                    logs = None
                    logs = copy.deepcopy(totalLog)
                    # create a new groupID
                    groupID = str(uuid.uuid4())
                    # broadcast this to everyone so that everyone can update their logs
                    groupJoinConfirmMsg = ('groupJoinConfirm', groupID, ','.join(logs))
                    groupJoinConfirmMsg = ','.join(map(lambda x: str(x), groupJoinConfirmMsg))
                    # send back the confrim to the current sequencer of the other
                    ucast_sock.sendto(str.encode(groupJoinConfirmMsg), multiAddrPort)
                    
            elif command[0] == 'groupJoinConfirm':
                print('Processing groupJoinConfirm')
                print('Joining new group with groupID {}'.format(groupID))
                groupID = command[1]
                totalLogs = command[2:]
                FTq = None
                FTq = FTQueue()
                for log in totalLogs:
                    l = log.split(':')
                    updateQueue(FTq, l)
                        
            ############################################################
            #                  MOCKING PARTITION
            ############################################################
            elif command[0] == 'partitionSetup':
                # recieving a partition setup message means that I will
                # change my UUID to the recieved one in order to mock a partition
                # only change if my viewMemberNumber is odd
                if viewMemberNumber % 2 == 1:
                    # get the new membership and find my veiwMemberNumber
                    print('Changing to new group (partitioned) with groupID {}'.format(incomingGroupID))
                    isPartitioned = True
                    groupMembers = pickle.loads(codecs.decode(command[2].encode(), "base64"))
                    groupID = incomingGroupID
                    # find our new membership number by looking in the dictionary
                    for viewNum, membership in groupMembers.items():
                        if membership['memberNumber'] == memberNumber:
                            viewMemberNumber = viewNum
                    print('Group members after partition:')
                    print(groupMembers)
                    print('member number {} has new view number {}'.format(memberNumber, viewMemberNumber))
                    
                    
            elif command[0] == 'mockPartition':
                # for the sake of mocking a partition, we will make all
                # odd numbered viewMemberNumber processes have a new UUID
                # the lowest numbered odd one will send a message to all
                # other odd numbered ones with the new UUID
                if viewMemberNumber == 1:
                    isPartitioned = True
                    # get a new groupID to send to others
                    groupID = str(uuid.uuid4())
                    print('Setting up the mock partition')
                    # need to setup new membership
                    
                    # delete the member from the group
                    for i in range(len(groupMembers)):
                        if i%2 == 0:
                            del groupMembers[i]
                    # update all group members by decrementing their number
                    memberNums = sorted([int(x) for x in groupMembers.keys()])
                    lastNum = -1
                    for num in memberNums:
                        if num != lastNum + 1:
                            thisNumServer = groupMembers[num]
                            # update my own memberNumber if decremented
                            if num == viewMemberNumber:
                                viewMemberNumber = lastNum + 1
                            del groupMembers[num]
                            groupMembers[lastNum + 1] = thisNumServer
                        lastNum += 1
                    print('New group membership (partitioned membership)')
                    print(groupMembers)        
                    groupID = str(uuid.uuid4())
                    
                    partitionSetupMsg = (
                        'partitionSetup', 
                        groupID,
                        codecs.encode(pickle.dumps(groupMembers), "base64").decode()
                    )
                    partitionSetupMsg = ','.join(map(lambda x: str(x), partitionSetupMsg))
                    ucast_sock.sendto(str.encode(partitionSetupMsg), multiAddrPort)
                    
            #############################################################
            # if some group member misses sequenceing a message
            # it asks for a retransmission of that sequence message
            # from the memeber responsible for creating the sequence
            # the member responsible for sequenceing the message
            # uses seqNumsSent to find and resend sequence number
            elif command[0]=='reseq':
                #PARTITION TESTING
                if incomingGroupID != groupID:
                    continue
                # sample: (['reseq', '2'], ('127.0.0.1', 8081))
                seqNum = int(command[2])
                print("Received reseq message for seq num {}".format(seqNum))
                if seqNum in list(seqNumsSent.keys()):
                    seqM = ('seq', groupID, seqNumsSent[seqNum], seqNum)
                    seqM = ":".join(map(lambda x: str(x),seqM))
                    ucast_sock.sendto(str.encode(seqM), addr)
                
            else:
                print("Invalid Command")
            print('')
        # messages end up being bufferd due to seq message losses from other servers
        # Negative acknowledgement has to sent in this case     
        elif len(messages):
            print('')
            seqsrNum = (globalSeq[0])%len(groupMembers)
            print('SEQSRNUM {} FROM GLOBAL SEQ {} MOD LEN GROUP MEMBERS {}'.format(seqsrNum, globalSeq[0], len(groupMembers)))
            if seqsrNum == viewMemberNumber:
                # After sending NAK for a few messages in the buffer
                # and getting seq reply and clearing these messages from buffer
                # Then find out that next message in the buffer is yours to sequence
                # Pick a message in the buffer and sequence it 
                rndMsg = list(messages.keys())[0]
                print("Caught up with message losses. SQUENCING {}".format(rndMsg))
                seqNumsSent[globalSeq[0]] = rndMsg
                seqM = ('seq', groupID, rndMsg, globalSeq[0])
                seqM = ",".join(map(lambda x: str(x),seqM))
                ucast_sock.sendto(str.encode(seqM), multiAddrPort)
                globalSeq[0] = globalSeq[0] + 1
                ret = updateQueue(FTq, messages[rndMsg][0])
                logUpdate = ':'.join([groupID] + messages[rndMsg][0])
                logs.append(logUpdate)
                if ret!=None:
                    print("Caught up. Sending: {}".format(ret))
                    addr = messages[rndMsg][1]
                    ucast_sock.sendto(str.encode(str(ret)), addr)
                del messages[rndMsg]
                print("All caught up. Message {} un buffered".format(msgid))
                print('global sequence number is now {}'.format(globalSeq[0]))
            else:
                # send NAK and ask for sequence number to be retransmitted 
                # from process that generated it
                print('seqsrNum')
                print(seqsrNum)
                print('GROUP MEMBERS')
                print(groupMembers)
                seqsrAddr = groupMembers[seqsrNum]['address']
                # if we've hit our allowance, then reset nak count and say its dead
                if nakCount > nakAllowance:
                    nakCount = 0
                    print('SERVER {} DEAD'.format(str(seqsrAddr)))
                    # delete the member from the group
                    del groupMembers[seqsrNum]
                    # update all group members by decrementing their number
                    memberNums = sorted([int(x) for x in groupMembers.keys()])
                    lastNum = -1
                    for num in memberNums:
                        if num != lastNum + 1:
                            thisNumServer = groupMembers[num]
                            # update my own memberNumber if decremented
                            if num == viewMemberNumber:
                                viewMemberNumber = lastNum + 1
                            del groupMembers[num]
                            groupMembers[lastNum + 1] = thisNumServer
                        lastNum += 1
                    print('New group membership')
                    print(groupMembers)  
                    oldGroupID = copy.deepcopy(groupID)
                    groupID = str(uuid.uuid4())
                    print('New groupID: {}'.format(groupID))
                    # broadcast a membership update command
                    membershipUpdateM = (
                        'membershipUpdate', 
                        oldGroupID,
                        groupID,
                        codecs.encode(pickle.dumps(groupMembers), "base64").decode()
                    )
                    membershipUpdateM = ','.join(map(lambda x: str(x), membershipUpdateM))
                    ucast_sock.sendto(str.encode(membershipUpdateM), multiAddrPort)
                    # set a timeout to let other processes process the message
                    time.sleep(.5)
                else:
                    # send reseq message
                    print("Re requesting seguence number {} from group member {}"
                            .format(globalSeq[0],seqsrNum))
                    reseqM = ('reseq', groupID, globalSeq[0])
                    reseqM = ",".join(map(lambda x: str(x),reseqM))
                    ucast_sock.sendto(str.encode(reseqM), seqsrAddr)
                    nakCount += 1
                    sleepTime = float(random.randint(1, 20))/float(10)
                    time.sleep(sleepTime)
            print('')

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='FTQueue replicated across server group')

    parser.add_argument('--uniAddr', type=str, help='Address of unicast socket. Unique for each group member')

    parser.add_argument('--multiAddr', type=str, help='Address of multicast socket. Should be the same for all group members')
    parser.add_argument('--multiPort', type=int, help='Port number of multicast socket. Should be the same for all group members')

    parser.add_argument('--IS_MACOS', type=bool, help='Pass `True` for MACOS', default=False)

    args = parser.parse_args()

    #setting up unicast socket to listen to
    if args.uniAddr!=None:
        UCAST_IP = args.uniAddr
        UCAST_P = 8080
    else:
        print("Nessessary arguments not provide for group member.")
        print("Run `python phaseO.py --help` for more information.")
        os._exit(0)

    #setting up multicast socket to listen to
    if args.multiAddr!=None and args.multiPort!=None:
        MCAST_GRP = args.multiAddr
        MCAST_PORT = args.multiPort
    else:
        MCAST_GRP = '224.0.0.1'
        MCAST_PORT = 5050
        print("Using default muticast address: {}".format((MCAST_GRP, MCAST_PORT)))


    #setting up multicast socket to listen to
    multiAddrPort = (MCAST_GRP, MCAST_PORT)

    LOCAL_HOST = True
    IS_MACOS = args.IS_MACOS
    reuse_option = socket.SO_REUSEADDR if not IS_MACOS else socket.SO_REUSEPORT
    level_option = socket.IP_ADD_MEMBERSHIP if not LOCAL_HOST else socket.IP_MULTICAST_LOOP
    mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mcast_sock.setsockopt(socket.SOL_SOCKET, reuse_option, 1)

    mcast_sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    mcast_sock.setsockopt(socket.IPPROTO_IP, level_option, mreq)
    mcast_sock.settimeout(1.0)
    print("Multicasting on {}".format((MCAST_GRP, MCAST_PORT)))

    successfulPort = False
    while not successfulPort:
        try:
            uniAddrPort = (UCAST_IP, UCAST_P)
            ucast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ucast_sock.bind(uniAddrPort)
            successfulPort = True
        except:
            UCAST_P += 1
            continue
    ucast_sock.settimeout(1.0)
    print("Unicasting on {}".format(uniAddrPort))
    memberNumber = UCAST_P
    viewMemberNumber = 0

    # to be processed by middlewareThread 
    #buffers all unicast and multicast messages
    commands = []

    # Tread to listen for multicast messages
    print("Starting Multicast socket listner thread")
    # used as flag to terminate while loop of multiThread
    # thread terminates when the len of multiRunning is greater than 0
    # aka insert element
    # cannot use bool type for this as it is immutable
    multiRunning = []
    multiThread = threading.Thread(target=mutiListner, name='multicast', 
        args=(multiRunning, commands, mcast_sock, uniAddrPort))
    multiThread.daemon = True
    multiThread.start()

    # Tread to listen for unicast messages
    print("Starting Unicast socket listner thread")
    # used as flag to terminate while loop of uniThread
    # thread terminates when the len of uniRunning is greater than 0
    # aka insert element
    # cannot use bool type for this as it is immutable
    uniRunning = []
    uniThread = threading.Thread(target=uniListner, name='unicast', 
        args=(uniRunning, commands, ucast_sock, uniAddrPort))
    uniThread.daemon = True
    uniThread.start()

    # ALL GLOBAL VARIABLES
    # the global sequence number maintained by this server
    globalSeq = [0]
    # stores all memebers of the group
    # members are added when join request confirmation is received
    groupMembers = {
        viewMemberNumber:{
            'address': uniAddrPort,
            'memberNumber': memberNumber
        }
    }
    # FTQueue instance for this server
    FTq = FTQueue()
    # message buffer
    messages = {}
    # all sequence numbers assigned/generated by this server
    # used to resend sequence number when NAK is sent from other servers
    seqNumsSent = {}
    # list to keep track of operations done to the queue
    # each log is of the form '<op>:<params>''
    logs = []
    # keep track of the number of NAKS we've sent
    nakCount = 0
    # the number of allowed NAKS
    nakAllowance = 5
    # initial group ID. Changed as new members are added
    groupID = str(uuid.uuid4())

    # middleware thread process command coming from both unicast and multicast sockets
    print("Starting middleware command processor thread")
    # used as flag to terminate while loop of midThread
    # thread terminates when the len of midRunning is greater than 0
    # aka insert element 
    # cannot use bool type for this as it is immutable       
    midRunning = []
    midThread = threading.Thread(target=middlewareThread, name='middleware', 
        args=(midRunning, globalSeq, memberNumber, viewMemberNumber, groupID, logs, groupMembers,
            FTq, commands, messages, seqNumsSent, 
            ucast_sock, uniAddrPort, multiAddrPort, nakCount, nakAllowance))
    midThread.daemon = True
    midThread.start()

    # checking to see if member number is unique to the group
    # if a group member with this number exists request is denied
    # another number has to choosen
    print("Joining group as member number {}".format(memberNumber))
    joinM = ('joinRequest', groupID, memberNumber)
    joinM = ",".join(map(lambda x: str(x),joinM))
    ucast_sock.sendto(str.encode(joinM), (MCAST_GRP, MCAST_PORT))

    _ = input("\n******* HIT ENTER TO EXIT PROGRAM **********\n")
    # adding elemets to each list terminates 
    # while loop of respective threads
    # cannot use bool type for this as it is immutable
    # https://robertheaton.com/2014/02/09/pythons-pass-by-object-reference-as-explained-by-philip-k-dick/
    multiRunning.append(0)
    uniRunning.append(0)
    midRunning.append(0)

    multiThread.join()
    uniThread.join()
    midThread.join()




