import socket
from threading import Thread


class user:
    def __init__(self, n):
        self.name = n

    def getName(self):
        return self.name

    def goOnline(self, ip, port):
        s = socket.socket()
        s.connect((ip, port))
        s.send(self.getName())
        print "***You are now Online***\n"
        return s

    def goOffline(self, s):
        print 'Going Offline...'
        s.send("disconnect")


def receive(s):
    while True:
        string = s.recv(1024)
        if len(string) == 0:
            return

        if "'s'" in string:
            s.send('resend')
            continue

        i = string.index(':')

        if "'f'" in string:
            fileFrom = string[:i]
            fileName = string[i + 1:-3]
            rData = "Temp"
            rData = s.recv(1024)
            recFile = open(fileName, 'wb')
            while rData:
                if "'''D'''" in rData:
                    recFile.write(rData[:-7])
                    break
                recFile.write(rData)
                rData = s.recv(1024)
            recFile.close()
            print fileFrom + " sent " + fileName
            continue
        elif "'m'" in string:
            msg = string[i + 1:-3] + '\n'
            msgFrom = string[:i]
            fileName = msgFrom + ".txt"
            user = open(fileName, "a")
            if ':' in msg:
                j=msg.index(':')
                name = msg[:j]
                msgFrom = name + '(' + msgFrom + ')'
            else:
                msg = string[:-3] + '\n'
            user.write(msg)
            print  "New message from " + msgFrom 
            user.close()


def Main():
    U = user('user1')
    ip = '127.0.0.1'
    port = 8000

    s = U.goOnline(ip, port)
    t1 = Thread(target=receive, args=(s,))
    t1.start()
    while True:
        print "Enter 1 to send message\n"
              + "Enter 2 to send file\n"
              + "Enter 3 to view messages\n"
              + "Enter 4 to create/view group(s)\n"
              + "Enter 5 to view who's online/offline\n"
              + "Enter 6 to exit"
        choice = raw_input()

        if (choice == '1'):
            print  "Enter in the following format:\n" +
                   "'Name:Message'\n" +
                   "or Enter Exit to the main menu"
            while True:
                text = raw_input()

                if text == 'Exit':
                    break
                else:
                    s.send(text+ "'m'")
                    string = s.recv(1024)
                    s.send("OK")
                    print string[:-3]
                    if string[:-3]=='Sent':
                        i=text.index(':')
                        msgTo=text[:i]
                        msg=text[i+1:] + '\n'
                        f = open(msgTo+'.txt','a')
                        f.write('Me:'+msg)
                        f.close()
        elif (choice == '2'):
            print  "Enter in the following format:\n" +
                   "'Name:File_Name'\n" +
                   "or Enter Exit to main menu" 
            while True:
                fileName = raw_input()

                if fileName == 'Exit':
                    break

                s.send(fileName + "'f'")

                i = fileName.index(':')
                fileName = fileName[i + 1:]

                sendFile = open(fileName, "rb")
                sRead = sendFile.read(1024)
                while sRead:
                    s.send(sRead)
                    sRead = sendFile.read(1024)
                sendFile.close()
                s.send("'''D'''")
                string = s.recv(1024)
                s.send("OK")
                print  string[:-3] 
        elif (choice == '3'):
            print  "Enter the name of the person/group\n" +
                   "who's messages you want to view\n" +
                   "or Enter Exit to main menu" 
            while True:
                p_name = raw_input()
                if p_name == 'Exit':
                    break
                else:
                    f = open(p_name + '.txt', 'r')
                    msgs = f.readline()
                    while (msgs):
                        print  msgs[:-1] 
                        msgs = f.readline()
                    print  ''  
        elif (choice == '4'):
            while True:
                print  "Enter 1 to create a new group\n" \
                      +"Enter 2 to view an existing group\n" \
                       +"or Enter Exit to main menu" 
                opt=raw_input()
                if opt=='1':
                    s.send('newGroup')
                    print  "Enter a name for the new group\n" \
                          +"in the following format\n" \
                           +"GroupName:Member1(space)Member2..." 
                    group = raw_input()
                    s.send(group)
                    ack = s.recv(1024)
                    s.send('ack')
                    print  ack[:-3] 
                elif opt=='2':
                    s.send('getGroup')
                    print  "Enter the name of the\n" \
                        +"group you want to view" 
                    groupName =raw_input()
                    s.send(groupName)
                    members = s.recv(1024)
                    s.send('ack')
                    print  members[:-3] 
                    if members == "No group found's'":
                        continue
                    while True:
                        print  "Enter 1 to leave group" 
                        if (U.getName()+'(admin)') in members:
                            print  "Enter 2 to add/remove a member\n" \
                                 +"Enter 3 to make another member an admin" 
                        print  "Enter Exit to go back" 
                        ch = raw_input()
                        if ch=='1':
                            s.send('leaveGroup')
                            print  'You left the group' 
                            break
                        elif ch=="Exit":
                            s.send('Exit')
                            break

                        if (U.getName() + '(admin)') in members:
                            if  ch=='2':
                                s.send('addRemoveMember')
                                print  "Enter the name of the friend you\n" \
                                      +"want to add/remove in/from the\n" \
                                      +" group in the following format:\n" \
                                      +"Add/Remove:MemberName\n" \
                                      +"or Enter Exit to go back" 
                                while True:
                                    m = raw_input()
                                    if m=='Exit':
                                        s.send('Exit')
                                        break
                                    s.send(m)
                                    ack = s.recv(1024)
                                    s.send('ack')
                                    print  ack[:-3] 
                            elif ch=='3':
                                s.send('makeAdmin')
                                print  "Enter the name of the member\n" \
                                      +"you want to make admin of the\n" \
                                      +"group or Enter Exit to go back" 
                                while True:
                                    c= raw_input()
                                    if c=='Exit':
                                        s.send('Exit')
                                        break
                                    s.send(c)
                                    ack = s.recv(1024)
                                    s.send('ack')
                                    print  ack[:-3] 
                        else:
                            print  "Invalid Input!" 
                elif opt=='Exit':
                    break
        elif (choice == '5'):
            s.send("getStatus")
            status = s.recv(1024)
            s.send("OK")
            print  status[:-3] 
            print "Enter Exit to go back" 
            opt='temp'
            while opt!='Exit':
                opt = raw_input()

        elif (choice == '6'):
            U.goOffline(s)
            t1.join()
            break

    s.close()


if __name__ == "__main__":
    Main()
