import socket 
import _thread as thread
import os

def forwardMsg(msgTo,clients,msgFrom,msg):
    while not (msgTo in clients):
        continue    #do nothing
    clients[msgTo].send((msgFrom + ':' + msg).encode())

def replyMsg(client,message):
    client.send((message+"'s'").encode())
    msg = client.recv(1024).decode()
    if msg == 'resend':
        client.send((message+"'s'").encode())
        msg = client.recv(1024).decode()

def sendFile(msgTo,clients,msgFrom,fileName):

    while not (msgTo in clients):
        continue
    clients[msgTo].send((msgFrom + ':' + fileName + "'f'").encode())

    sendFile = open(fileName, "rb")
    sRead = sendFile.read(1024)
    while sRead:
        clients[msgTo].send(sRead)
        sRead = sendFile.read(1024)
    sendFile.close()
    clients[msgTo].send(("'''D'''").encode())

def receiveFile(client,fileName):
    rData = "Temp"
    rData = client.recv(1024).decode()
    recFile = open(fileName, 'wb')
    while rData:
        if "'''D'''" in rData:
            recFile.write(rData[:-7])
            break
        recFile.write(rData)
        rData = client.recv(1024).decode()
    recFile.close()

def func(client, addr, name, clients):
    print("connected to:  ", name,addr)
    print("ACTIVE USERS: ", clients.keys())

    while True:
        string = client.recv(1024).decode()

        users = open('userData.txt', 'r')
        userList = users.readlines()
        for i in range(len(userList)):
            userList[i] = userList[i][:-1]
        users.close()

        if string == 'disconnect':
            print(name,addr, " disconnected")
            del clients[name]
            client.close()
            print("ACTIVE USERS: " ,clients.keys(),'\n')
            break
        elif string == 'getStatus':
            status=''
            for user in userList:
                if user!=name:
                    if user in clients:
                        status=status+user+'(Online)\n'
                    else:
                        status=status+user+'(Offline)\n'
            replyMsg(client,status)
            continue
        elif string == 'newGroup':
            group = client.recv(1024).decode()
            i = group.index(':')
            grpNme = group[:i]
            members=(group[i+1:]).split()
            g = open(grpNme+'.txt','w')
            for i in range(len(members)):
                members[i]=members[i] + '\n'
            g.write(name+'(admin)\n')
            g.writelines(members)
            g.close()
            replyMsg(client, 'Group created')
            continue
        elif string == 'getGroup':
            grpNme = client.recv(1024).decode()
            if (grpNme+'.txt') not in os.listdir('C:/Users/Hashim zaidi/PycharmProjects/.idea/server'):
                replyMsg(client,'No group found')
                continue
            g = open(grpNme +'.txt','r')
            members=g.read()
            g.close()
            if name in members:
                replyMsg(client, members)
            else:
                replyMsg(client, 'No group found')
                continue

            g = open(grpNme + '.txt', 'w')
            while True:
                msg = client.recv(1024).decode()
                if(msg=='Exit'):
                    break
                elif msg == 'leaveGroup':
                    if (name+'(admin)') in members:
                        members=members.replace(name+'(admin)\n','')
                        if 'admin' not in members and len(members)!=0:
                            i=members.index('\n')
                            newAdmin=members[:i]+'(admin)'
                            members=members.replace(members[:i],newAdmin)
                    else:
                        members=members.replace(name+'\n','')
                    break
                elif msg =='addRemoveMember':
                    while True:
                        msg = client.recv(1024).decode()
                        if msg=='Exit':
                            break
                        i = msg.index(':')
                        op = msg[:i]
                        member = msg[i+1:]
                        if member not in userList:
                            replyMsg(client,'User not found')
                            continue
                        if op == 'Add':
                            if member in members:
                                replyMsg(client,'Already a member')
                                continue
                            members=members+member+'\n'
                            replyMsg(client,'You added '+member)
                        elif op == 'Remove':
                            if member not in members:
                                replyMsg(client,'Already not a member')
                                continue
                            if (member + '(admin)') in members:
                                members = members.replace(member + '(admin)\n', '')
                            else:
                                members = members.replace(member + '\n', '')
                            replyMsg(client,'You removed '+member)
                elif msg =='makeAdmin':
                    while True:
                        ad = client.recv(1024).decode()
                        if ad =='Exit':
                            break
                        if (ad+'(admin)') in members:
                            replyMsg(client,'Already an admin')
                        elif ad in members:
                            members=members.replace(ad,ad+'(admin)')
                            replyMsg(client,ad+' is now an admin')
                        else:
                            replyMsg(client,'Member not found')

            g.write(members)
            g.close()
            if len(members)==0:
                os.remove('C:/Users/Hashim zaidi/PycharmProjects/.idea/server/'+grpNme+'.txt')
            continue

        i = string.index(':')
        msg=string[i+1:]
        string=string[:i]

        if "'m'" in msg:
            if string in clients and string != name:
                clients[string].send((name+':' +msg).encode())
                replyMsg(client,'Sent')
            elif (string in userList) and string!=name:
                thread.start_new_thread(forwardMsg,(string,clients,name,msg))
                replyMsg(client,'Sent')
            elif (string+'.txt') in os.listdir('C:/Users/Hashim zaidi/PycharmProjects/.idea/server'):
                g = open(string + '.txt', 'r')
                members = g.read()
                g.close()
                if name in members:
                    members = members.replace('(admin)','')
                    members = members.replace(name,'')
                    members = members.replace('\n',' ')
                    members = members.split()
                    msg=name+':'+msg
                    for member in members:
                        thread.start_new_thread(forwardMsg, (member, clients, string, msg))
                    replyMsg(client, 'Sent')
                else:
                    replyMsg(client, 'Error sending message')
            else:
                replyMsg(client,'Error sending message')
        elif "'f'" in msg:
            if string in clients and string != name:
                fileName = msg[:-3]
                receiveFile(client,fileName)
                sendFile(string,clients,name,fileName)
                replyMsg(client,'Sent')
            elif (string in userList) and string!=name:
                fileName = msg[:-3]
                receiveFile(client,fileName)
                thread.start_new_thread(sendFile,(string,clients,name,fileName))
                replyMsg(client,'Sent')
            elif (string+'.txt') in os.listdir('C:/Users/Hashim zaidi/PycharmProjects/.idea/server'):
                g = open(string + '.txt', 'r')
                members = g.read()
                g.close()
                if name in members:
                    fileName = msg[:-3]
                    receiveFile(client, fileName)
                    members = members.replace('(admin)', '')
                    members = members.replace(name, '')
                    members = members.replace('\n', ' ')
                    members = members.split()
                    string=name+'('+string+')'
                    for member in members:
                        thread.start_new_thread(sendFile, (member, clients, string, fileName))
                    replyMsg(client, 'Sent')
                else:
                    replyMsg(client, 'Error sending file')
            else:
                replyMsg(client,'Error sending file')


def Main():
        host='127.0.0.1'
        port=8000
        clients={}

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host,port))
        s.listen(5) # max number of connections
        print("Waiting for new connections")

        while True:
                client, addr = s.accept()
                
                users = open("userData.txt", "a+")
                newUser = 1
                client_name = client.recv(1024).decode()
                fRead = users.readline()
                while(fRead):
                    if fRead[:-1]==client_name:
                        newUser=0
                        break
                    fRead = users.readline()
                if(newUser):
                    users.seek(0,2)
                    users.write(client_name+'\n')

                clients[client_name]=client
                thread.start_new_thread(func,(client,addr,client_name,clients))
                users.close()

if __name__=="__main__":
    Main()
