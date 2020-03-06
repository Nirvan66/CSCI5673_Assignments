#  Programming Assignment  Part 1

## Running

This program uses python3. It will not work with python2.

Running this program is a multi-step process. First you should start up the number of servers you want in your system. The steps for doing so are below in the "server" section. 

Secondly you will start the client. For our implementation, we made the client a jupyter notebook. This allows us to send messages incrementally.

__IMPORTANT__: make sure when adding the next server via command line you increment the properties ```--memberNumber``` and ```--uniPort```. An example is shown below. When incrementing member numbers, DO NOT SKIP numbers. A valid set of member numbers would be [0, 1, 2, 3]. An invalid set of member numbers would be [0, 1, 3, 4].

### Server
#### Linux
```
python phaseO.py --uniAddr 127.0.0.1 --uniPort 8080 --memberNumber 0
```
#### macOS
```
python phaseO.py --uniAddr <Private IP Address> --uniPort 8080 --memberNumber 0 --IS_MACOS True
```
For macOS, the Private IP Address can be found in 

System Preferences -> Network -> Advanced -> TCP/IP -> IPv4A Adress

You have to run this program with this address instead of the localhost addres to get it to work.

#### Example run
We will start 2 servers here. 

Server 1
```
python phaseO.py --uniAddr 127.0.0.1 --uniPort 8080 --memberNumber 0
```

Server 2
```
python phaseO.py --uniAddr 127.0.0.1 --uniPort 8081 --memberNumber 1
```

Notice how server 2 incremented its port number and member number. 

You will see some messages pass between the two servers, accepting eachother into the group. This can be ignored. 

__IMPORTANT__: Again remember when adding the next server via command line you increment the properties ```--memberNumber``` and ```--uniPort```. An example is shown below. When incrementing member numbers, DO NOT SKIP numbers. A valid set of member numbers would be [0, 1, 2, 3]. An invalid set of member numbers would be [0, 1, 3, 4].
### Client
The client is in the attached ```.ipyn``` file. Start jupyter notebook. If you are running on macOS, be sure to change the IP address for the ```clientAddrPort``` variable to the same Private IP Address used when starting the servers. You should then be able to click play on each cell. 

You will observe the two servers communicating in the terminals that you started the servers in and replies to the client in the jupyter notebook.


## What works and what doesn't

Everything described in Part 1 works. Some basic group membership protocol also works, thus the need to increment your group number and the send of the 'join' messages when servers start. 

## Sources of potential errors

Its important to set the IP Address to your Private IP Address when running on macOS otherwise it will not run. 

If you skip numbers when incrementing member numbers, the program will stall out and it will not make progress after a certain point.

## Note
* There is a small change form the architecture discussed in class. 
* In class we discussed that the client contacts a single server and the server fowards this message to other servers and
the servers then run the sequencing algorithm
* To avoid this extra broadcast step, the client uses server group address to send messages to all servers in the group. The servers use the consensus algorithm to sequence the message among themselves and a single reply from the server choosen to be the sequencer is sent to the client (if a reply is needed, eg: `qTop` function returns int).