import time 
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

class LowLevelCommunications():
    #for before the client is logged in
    def Encode(Text):
        try:
            Text = str(Text)
            return bytes(Text, 'utf8')
        except:
            PrintLog("Error encoding")

    def SendServerPM(connection, text):
        time.sleep(0.2)
        text = str(text)
        try:
            ToSend = "[SERVER INTERNAL-LOW LEVEL-PM MESSAGE]" + text
            connection.send(LowLevelCommunications.Encode(ToSend))
            PrintLog(ToSend)
        except:
            PrintLog("Error sending low level message PM")
            connection.close()

        time.sleep(0.2)
        

    def SendInternalMessage(connection, text):
        time.sleep(0.2)
        text = str(text)
        try:
            ToSend = "[SERVER INTERNAL-LOW LEVEL-INTERNAL]" + text
            connection.send(LowLevelCommunications.Encode(ToSend))
            PrintLog(ToSend)

        except:
            PrintLog("Error sending low level internal PM, exiting")
            connection.close()
            pass

        time.sleep(0.2)

    
class HighLevelCommunications():
    def PrivateMessageFromServer(Username, Text):
        hadError = False
        Text = str(Text)
        Username = str(Username)
        PrintLog("Sending to " + Username + " : " + Text)
        try:
            Connection = Accounts.GetAccountData(Username, "ConnectionObject")
        except:
            PrintLog("Could not get connection for Server PM name, passing and not sending")
            hadError = True
            pass

        try:
            if hadError == False:
                toSend = "[SERVER INTERNAL-PM MESSAGE]" + Text
                Connection.send(HighLevelCommunications.Encode(toSend))
            else:
                PrintLog("Had error earlier, not sending")
        except:
            PrintLog("Error sending PM")
            Accounts.IncreaseErrorCount(Username)
    
    def Broadcast(Text):
        Text = str(Text)
        #try:
        for account in Accounts.AccountList:
            try:
                if Accounts.GetAccountDataFromObject(account, "isOnline") == True:
                    Connection = Accounts.GetAccountDataFromObject(account, "ConnectionObject")
                    ToSend = HighLevelCommunications.Encode("[SERVER INTERNAL-BROADCAST]" + str(Text))
                    Connection.send(ToSend)
            except:
                PrintLog("Error in broadcast : loop")
                try:
                    Username = Accounts.GetAccountDataFromObject(account, "Username")
                    Accounts.IncreaseErrorCount(Username)
                except:
                    PrintLog("Error increasing error count")
                continue

        PrintLog("Broadcasted " + Text)
        #except:
        #    PrintLog("Error in broadcast")
        #    pass


    def InternalMessage(Username, Text):
        hadError = False
        Text = str(Text)
        Username = str(Username)
        PrintLog("Sending internal message to " + Username + " : " + Text)
        try:
            Connection = Accounts.GetAccountData(Username, "ConnectionObject")
        except:
            PrintLog("Could not get connection for internal message name, passing and not sending")
            hadError = True
            Accounts.IncreaseErrorCount(Username)

        try:
            if hadError == False:
                toSend = "[SERVER INTERNAL-INTERNAL]" + Text
                Connection.send(HighLevelCommunications.Encode(toSend))
            else:
                PrintLog("Had error earlier, not sending")
        except:
            PrintLog("Error sending internal message")
            Accounts.IncreaseErrorCount(Username)

    def Encode(Text):
        try:
            Text = str(Text)
            PrintLog("Encoding: " + Text)
            return bytes(Text, 'utf8')
        except:
            PrintLog("Error encoding")

class Accounts():
    AccountList = []
    #Account specifications:
    #A example account
    #{
    #    Username : 'Alex'
    #    Password : 'sjfhjsbfh9w8fn028h02n etc',
    #    PendingPms : {Sender: 'Luke', Message : 'Hello!'},
    #    isAdmin : True,
    #    isOnline : True,
    #    ConnectionObject: {IP : 127.0.0.1, PROTOCOL : TCP, NOTES : 'I am not copying an entire sockets connection object'}
    #}

    def NewAccount(UsernameInput, PasswordInput, isAdminInput):
        try:
            UsernameInput = str(UsernameInput)
            PasswordInput = str(PasswordInput)
            isAdminInput = str(isAdminInput)

            #Accounts.ReadAccountList()
            Accounts.AccountList.append({'Username' : UsernameInput, 'Password' : PasswordInput, 'isAdmin' : isAdminInput, 'isOnline' : False})
            #Accounts.SaveAccountListToFile
        except:
            try:
                PrintLog("Error creating new account, username: " + str(UsernameInput))
            except:
                PrintLog("Error creating new account, error printing username")

    def GetAccountDataFromObject(Account, Key):
        #Accounts.ReadAccountList()
        try:
            Key = str(Key)
            toReturn = Account.get(Key)
            return toReturn
        
        except:
            PrintLog("Error getting account data from object")

    def GetAccountData(UsernameInput, key):
        try:
            returned = False
            UsernameInput = str(UsernameInput)
            key = str(key)

            #Accounts.ReadAccountList()
            for account in Accounts.AccountList:
                if account.get('Username') == UsernameInput:
                    returned = True
                    return account.get(key)

            if returned == False:
                PrintLog("Could not find data when searching " + str(UsernameInput) + " for " + str(key))
                return ""

            #Accounts.SaveAccountListToFile

        except:
            try:
                PrintLog("Error getting account data for " + str(UsernameInput))
            except:
                PrintLog("Error getting account data, error printing name")

    def IncreaseErrorCount(UsernameInput):
        CurrentErrorCount = Accounts.GetAccountData(UsernameInput, "ErrorCount")
        if not CurrentErrorCount == None:
            Accounts.PushAccountData(UsernameInput, "ErrorCount", (CurrentErrorCount + 1))

    def PushAccountData(UsernameInput, key, value):
        #Accounts.ReadAccountList()
        UsernameInput = str(UsernameInput)
        key = str(key)
        for account in Accounts.AccountList:
            if account.get('Username') == UsernameInput:
                account.update({key : value})

        #Accounts.SaveAccountListToFile

    def DeleteAccount(UsernameInput, PasswordInput):
        UsernameInput = str(UsernameInput)
        PasswordInput = str(PasswordInput)

        #Accounts.ReadAccountList()
        AccountListB = Accounts.AccountList
        for account in Accounts.AccountList:
            if account.get('Username') == UsernameInput:
                if account.get('Password') == PasswordInput:
                    AccountListB.remove(account)
        
        Accounts.AccountList = AccountListB
        #Accounts.SaveAccountListToFile

    def InitAccountList():
        Accounts.PopulateFile()
        Accounts.ReadAccountList()
        print(str(len(Accounts.AccountList)))

class Main():
    def ManageClientHighLevel(Username):
        NoError = True
        try:
            HighLevelCommunications.PrivateMessageFromServer(Username, "Welcome to the chatroom.")
        except:
            PrintLog("Error at start of high level manage client")
            NoError = False

        Accounts.PushAccountData(Username, "LastSeen", time.time())
        Accounts.PushAccountData(Username, "isOnline", True)

        while NoError == True and Accounts.GetAccountData(Username, "ErrorCount") < 10 and Accounts.GetAccountData(Username, "isOnline") == True:
            try:
                connection = Accounts.GetAccountData(Username, "ConnectionObject")
                message = connection.recv(BufferSize).decode("utf8")

                if message:
                    if message == "[PING: REPLY URGENTLY]":
                        #Yes I kind of cheated by circumventing the rest of the script and delays to prevent message concat, but...
                        #I didn't divide it by 2, so it's fair, OK?
                        connection.send(bytes("[PING: URGENT REPLY]", "utf8"))

                    Accounts.PushAccountData(Username, "LastSeen", time.time())
                    Accounts.PushAccountData(Username, "isOnline", True)

                    if "/everyonefake" in message:
                        HighLevelCommunications.Broadcast("EVERYONE OPEN FAKETEXT, ID CODE: e325482c26c995caad73f1987ff5c1b8c94fb9e68f9608f87949b81c5dfb2255f7939e8aaef8e0e82db45a293a1c61d79262bd05d2d72ec06e6bb7ee88d4d1af")

                    elif "/everyoneclose" in message:
                        HighLevelCommunications.Broadcast("EVERYONE EXIT NOW, ID CODE: e325482c26c995caad73f1987ff5c1b8c94fb9e68f9608f87949b81c5dfb2255f7939e8aaef8e0e82db45a293a1c61d79262bd05d2d72ec06e6bb7ee88d4d1af")

                    elif"/pm" in message:
                        HighLevelCommunications.PrivateMessageFromServer(Username, "Who do you want to send the PM to?")
                        ToSendPmTo = "[CLIENT PING UPDATE]!"
                        while "[CLIENT PING UPDATE]" in ToSendPmTo:
                            ToSendPmTo = connection.recv(BufferSize).decode("utf8")

                        ToSendExists = False
                        ToSendOnline = False

                        for account in Accounts.AccountList:
                            if Accounts.GetAccountDataFromObject(account, "Username") == ToSendPmTo:
                                ToSendExists = True
                                if Accounts.GetAccountDataFromObject(account, "isOnline") == True:
                                    ToSendOnline = True

                        if ToSendExists == False:
                            HighLevelCommunications.PrivateMessageFromServer(Username, "User does not exist.")

                        if ToSendExists == True and ToSendOnline == False:
                            HighLevelCommunications.PrivateMessageFromServer(Username, "User exists, but is not online")

                        if ToSendExists == True and ToSendOnline == True:
                            HighLevelCommunications.PrivateMessageFromServer(Username, "What do you want to send?")
                            PmToSend = "[CLIENT PING UPDATE]"

                            while "[CLIENT PING UPDATE]" in message:
                                PmToSend = connection.recv(BufferSize).decode("utf8")

                            Accounts.PushAccountData(ToSendPmTo, "PendingPms", {"Sender" : Username, "Message" : PmToSend, "HasAnswered" : False})

                            HighLevelCommunications.PrivateMessageFromServer(Username, "Added to buffer.")

                    elif "/exit" in message or "/quit" in message:
                        Accounts.PushAccountData(Username, "isOnline", False)
                        break

                    elif not "[CLIENT PING UPDATE]" in message and not "[PING: REPLY URGENTLY]" in message:
                        PrintLog(Username + ": " + message)
                        HighLevelCommunications.Broadcast(Username + ": " + message)

            except:
                PrintLog("Error in manage client, exiting")
                break

        connection = Accounts.GetAccountData(Username, "ConnectionObject")
        connection.close()
        Accounts.PushAccountData(Username, "ConnectionObject", "")

    def AcceptIncomingConnections():
        while True:
            connection, address = server.accept()
            str(connection)
            PrintLog("Accepted connection from " + str(address) + " , referring")
            Thread(target=Main.WelcomeNewConnections, args=(connection, address)).start()

    def WelcomeNewConnections(connection, address):
        try:
            LowLevelCommunications.SendServerPM(connection, "Make a new account (M) or sign in (S)")
            ContinueConnectionProcess = True
        except:
            PrintLog("Error sending to new client. Removing client.")
            connection.close()
            ContinueConnectionProcess = False
        
        try:
            if ContinueConnectionProcess == True:
                response = connection.recv(BufferSize).decode("utf8")
                if response == "M":
                    Thread(target=Main.NewAccountProcess, args=(connection, address)).start()
                else:
                    Thread(target=Main.SignInProcess, args=(connection, address)).start()


        except:
            PrintLog("Error in welcome new connections. Removing client")
            connection.close()

    def SignInProcess(connection, address):
        PrintLog("Started sign in process thread")
        try:
            while True:
                try:
                    PrintLog("Begun loop")
                    LowLevelCommunications.SendServerPM(connection, "Please enter username, be careful about whitespace: ")
                    Username = connection.recv(BufferSize).decode("utf8")

                    DoesAccountExist = False

                    for account in Accounts.AccountList:
                        if Accounts.GetAccountDataFromObject(account, "Username") == Username:
                            DoesAccountExist = True

                    if DoesAccountExist == True:
                        break

                    else:
                        LowLevelCommunications.SendServerPM(connection, "That account doesn't exist.")

                except:
                    PrintLog("Error in sign in : Username pick loop, closing connection")
                    connection.close()
                    break
            
            #Double negative because it sometimes returns "none"
            if not Accounts.GetAccountData(Username, "isOnline") == True and DoesAccountExist == True:
                while True:
                    LowLevelCommunications.SendInternalMessage(connection, "PASSWORD ENTRY FIELD")
                    time.sleep(0.2)
                    LowLevelCommunications.SendServerPM(connection, "Enter password, be careful about whitespace.")

                    Password = connection.recv(BufferSize).decode("utf8")
                    PrintLog("Received [Hashed] password: " + str(Password))

                    #Doesn't work if you just don't send your captured pw on or change it, but it's worth it anyway
                    if len(Password) < 50:
                        PrintLog("PASSWORD IS LESS THAN 50 CHARACTERS: PASSWORD MAY NOT BE HASHED: LINK MAY BE COMPROMISED.")
                        PrintLog("COMPROMISE TIME: " + time.time())
                        while True:
                            LowLevelCommunications.SendServerPM(connection, "YOUR LINK TO THE SERVER MAY BE COMPROMISED \nIF YOU USE THIS PASSWORD ANYWHERE ELSE, CHANGE IT.")
                            time.sleep(5)

                    
                    if Accounts.GetAccountData(Username, "Password") == Password:
                        Accounts.PushAccountData(Username, "ConnectionObject", connection)
                        HighLevelCommunications.PrivateMessageFromServer(Username, "If you can read this, you successfully identified. Type 'continue' to continue.")
                        reply = connection.recv(BufferSize).decode("utf8")
                        print(str(Username))
                        if reply == "continue":
                            Accounts.PushAccountData(Username, "ErrorCount", 0)
                            Thread(target=Main.ManageClientHighLevel, args=(Username,)).start()
                            break

                        else:
                            connection.close()

                    else:
                        LowLevelCommunications.SendServerPM(connection, "Password incorrect.")

            else:
                LowLevelCommunications.SendServerPM(connection, "You are online somewhere else.")
                connection.close()
        except:
            PrintLog("Error in signin")
            connection.close()

    def NewAccountProcess(connection, address):
        try:
            LowLevelCommunications.SendInternalMessage(connection, "Enter auth to access")
            response = connection.recv(BufferSize).decode("utf8")
        except:
            PrintLog("Error in NewAccountProcess, closing connection")
            connection.close()

        #try:
        if "RESPONSE, SERVER CLIENT CONTAINS REMOTE SHUTDOWN AND LENGTH LIMIT AND NEWLINE PARSE." in response:
            try:
                while True:
                    InUse = False
                    LowLevelCommunications.SendServerPM(connection, "Please enter your new username: ")
                    response = connection.recv(BufferSize).decode("utf8")
                    Username = response

                    if " " in Username:
                        InUse = True
                        LowLevelCommunications.SendServerPM(connection, "Remove that whitespace!")

                    for account in Accounts.AccountList:
                        if Accounts.GetAccountDataFromObject(account, "Username") == Username:
                            LowLevelCommunications.SendServerPM(connection, "Sorry! That username is already in use.")
                            InUse = True

                    #banned words is for "bad" ones, for various reasons
                    bannedWords = ["Marlwood is great", "Admin", "Server"]

                    #banned names is for my friends, this is to force codenames.
                    bannedNames = ["LUKE", "ALEX", "LEWIS", "JOEL"]
                    bannedNameSuggestions = {"LUKE" : "SquireLostWood", "ALEX" : "Alpha", "LEWIS" : "Phantom", "JOEL" : "Death, Omega, Whisper"}

                    for word in bannedWords:
                        if word.upper() in Username.upper():
                            LowLevelCommunications.SendServerPM(connection, "Username is in a blacklist.")
                            InUse = True
                    
                    for word in bannedNames:
                        if word.upper() in Username.upper():
                            LowLevelCommunications.SendServerPM(connection, "Please use codenames. Suggestion:")
                            LowLevelCommunications.SendServerPM(connection, bannedNameSuggestions[word.upper()])
                            InUse = True

                    if "42" in Username:
                        LowLevelCommunications.SendServerPM(connection, "42! Nice!")
                    if InUse == False:
                        break

            except:
                PrintLog("Error")
                connection.close()

            try:
                LowLevelCommunications.SendServerPM(connection, "Username received: " + Username)

                if InUse == False:
                    LowLevelCommunications.SendInternalMessage(connection, "PASSWORD ENTRY FIELD")
                    LowLevelCommunications.SendServerPM(connection, "Please enter your new password: ")
                    response = connection.recv(BufferSize).decode("utf8")
                    Password = response
                    PrintLog("Received [Hashed] password: " + str(Password))

                    #Doesn't work if you just don't send your captured pw on or change it, but it's worth it anyway
                    if len(Password) < 50:
                        PrintLog("PASSWORD IS LESS THAN 50 CHARACTERS: PASSWORD MAY NOT BE HASHED: LINK MAY BE COMPROMISED.")
                        PrintLog("COMPROMISE TIME: " + time.time())
                        while True:
                            LowLevelCommunications.SendServerPM(connection, "YOUR LINK TO THE SERVER MAY BE COMPROMISED \nIF YOU USE THIS PASSWORD ANYWHERE ELSE, CHANGE IT.")
                            time.sleep(5)


                    time.sleep(0.5)
                    LowLevelCommunications.SendServerPM(connection, "Creating account...")
                    #waits for a bit to stop spamming
                    Accounts.NewAccount(Username, Password, False)
                    Accounts.PushAccountData(Username, "ConnectionObject", connection)
                    Accounts.PushAccountData(Username, "isOnline", False)
                    HighLevelCommunications.PrivateMessageFromServer(Username, "If you can read this, your account creation worked.\nEnter the word 'continue' to enter")
                    try:
                        response = connection.recv(BufferSize).decode("utf8")
                    except:
                        PrintLog("Error getting response from client")
                        connection.close()

                    if response == "continue":
                        PrintLog("Referring main thread")
                        Accounts.PushAccountData(Username, "ErrorCount", 0)
                        Thread(target=Main.ManageClientHighLevel, args=(Username,)).start()
                    else:
                        PrintLog("Didn't enter 'continue'")
                        connection.close()
            except:
                connection.close()
                PrintLog("Error in account creation")

        else:
            LowLevelCommunications.SendServerPM(connection, "Upgrade your client")
            time.sleep(5)
            connection.close()
    #except:
    #    PrintLog("Error in account creation, exiting")
    #    connection.close()

class PMManager:
    def PMManager():
        PrintLog("PM Manager started")
        while True:
            try:
                time.sleep(5)
                for Account in Accounts.AccountList:
                    if not Accounts.GetAccountDataFromObject(Account, "PendingPms") == None:
                        if Accounts.GetAccountDataFromObject(Account, "isOnline") == True:
                            Username = Accounts.GetAccountDataFromObject(Account, "Username")
                            PendingPMobject = Accounts.GetAccountData(Username, "PendingPms")
                            if PendingPMobject.get("HasAnswered") == False:
                                HighLevelCommunications.PrivateMessageFromServer(Username, "-- BEGIN PRIVATE MESSAGE -- \nSENDER: " + str(PendingPMobject.get("Sender")) + "\n--MESSAGE FOLLOWS -- \n" + str(PendingPMobject.get("Message")))
                                HighLevelCommunications.PrivateMessageFromServer(Username, "-- END PRIVATE MESSAGE --")
                                Accounts.PushAccountData(Username, "PendingPms", None)

                            else:
                                PrintLog("PM MANAGER: Already answered")

                        else:
                            PrintLog("Not online, not sending PM")

            except TypeError:
                continue
            except:
                PrintLog("Error in PM manager, can not increase log")

#NOTE Not in any class because I want it to be readily accessed and it doesn't belong to any in particular
def PrintLog(text):
    text = str(text)
    text = str(time.time()) + " : " + text
    print(text)
    LogFile = open('log.txt', 'a')
    LogFile.write(text + "\n")

class PingManager:
    def PingManager():
        while True:
            time.sleep(10)
            for account in Accounts.AccountList:
                if Accounts.GetAccountDataFromObject(account, "isOnline") == True:
                    lastSeen = Accounts.GetAccountDataFromObject(account, "LastSeen")
                    difference = time.time() - lastSeen

                    if difference > 30:
                        Username = Accounts.GetAccountDataFromObject(account, "Username")
                        Accounts.PushAccountData(Username, "isOnline", False)

server = socket(AF_INET, SOCK_STREAM)
Port = input("Port: ")
if not Port:
    Port = 34000
    PrintLog("Defaulted")

else:
    Port = int(Port)
    PrintLog("Port set to " + str(Port))

Host = ""
BufferSize = 2048
try:
    server.bind((Host, Port))
except:
    if Port == 34000:
        Port = 34001
        PrintLog("Set port to 34001 due to error")

    elif Port == 34001:
        Port = 34000
        PrintLog("Set port to 34000 due to error")

    server.bind((Host, Port))
server.listen(1000)

PrintLog("--SCRIPT RESTART-- SERVER VERSION: 3 -- TIME: " + str(time.time()))

Thread(target=PMManager.PMManager).start()

Thread(target=PingManager.PingManager).start()

#Thread(target=PrintPeriodic).start()

Main.AcceptIncomingConnections()