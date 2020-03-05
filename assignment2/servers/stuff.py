def processCommand(command, addr):
    # if another member sends a join request to already existing group
    if command[0]=='joinRequest':
        newMemberNum = int(command[1])
        if addr not in groupMembers and addr!=uniAddrPort:
            # if number already exists denie join reques
            if newMemberNum in groupMembers.keys():
                denJoin = ('joinDenied',)
                denJoin = ",".join(map(lambda x: str(x),denJoin))
                ucast_sock.sendto(str.encode(denJoin), addr)
            # if member number does not exist accept join request
            # send conformation with your member number
            else:
                groupMembers[newMemberNum] = addr
                confJoin = ('joinConfirm', memberNumber)
                confJoin = ",".join(map(lambda x: str(x),confJoin))
                ucast_sock.sendto(str.encode(confJoin), addr)
    # collect confirmation messages sent by other group members.
    # collect member numbers and addresses.
    elif command[0]=='joinConfirm':
        if addr not in groupMembers and addr!=uniAddrPort:
            groupMembers[int(command[1])] = addr
            
    # if denied exit for now     
    elif command[0]=='joinDenied':
        print("MEMBER NUMBER {} ALREADY EXISTS. PICK ANOTHER".format(memberNumber))
        os._exit(0)
        
    # if sequence number is received for a message
    elif command[0]=='seq':
        sequences.append(command[1:])
        
    # if a msg is recived from the client
    elif command[0]=='msg': 
        messages[command[1]] = command[2:]