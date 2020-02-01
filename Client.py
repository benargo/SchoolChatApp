#client side script
from socket import AF_INET, socket, SOCK_STREAM
from threading import *
import tkinter, time
from tkinter import messagebox
import sys, hashlib

lastUpIndicator = 0
isUp = False

DoCustom = input("Do you want to do default or custom setup? C/D > ")

if DoCustom == "C":
    DoCustom = True

elif DoCustom == "D":
    DoCustom = False

else:
    DoCustom = False
    print("Non Y/N answer, defaulting to default")

if DoCustom:
    allowRemoteAccess = input("Do you want to allow admins to remotely shut down or wipe if teachers come? Y/N > ")

    if allowRemoteAccess == "Y":
        allowRemoteAccess = True

    elif allowRemoteAccess == "N":
        allowRemoteAccess = False

    else:
        allowRemoteAccess = True
        print("Non Y/N answer, defaulting to yes")

        
def CalculateAuthCode():
    authCode = int(int(time.time()) / int(10))
    authCode = hashlib.sha512(bytes(str(authCode), "utf8")).hexdigest()
    authCode = str(authCode)
    SetLabelStatus("Auth code is " + authCode)
    return authCode

def ReceiveFromServer():
    while True:
        try:
            message = client_socket.recv(Buffer_size).decode("utf8")

            if "Enter authorisation" in message or "password required" in message:
                print("Set entry mode to auth")
                SetLabelStatus("Enter password")
                entry_field["show"] = "*"

            else:
                entry_field["show"] = ""

            if "Closing connection" in message or "Closed connection" in message:
                SetLabelStatus("Seems like you were kicked!")

            if "-- EXIT AUTHORISE --" in message and allowRemoteAccess == True:
                SetLabelStatus("Received remote close, verifying auth code")
                print("Received auth message...")
                
                if CalculateAuthCode() in message:
                    SetLabelStatus("Auth code correct. Exiting...")
                    print("Auth correct. Exiting.")
                    WipeList()
                    top.destroy()
                    sys.exit()

                else:
                    print("Auth incorrect. Not responded.")
                    SetLabelStatus("Auth incorrect.")

            if "-- WIPE AUTHORISE --" in message and allowRemoteAccess == True:
                print("Received auth message...")
                SetLabelStatus("Received remote wipe, verifying auth code")
                authCode = int(int(time.time()) / int(10))
                if CalculateAuthCode() in message:
                    SetLabelStatus("Auth correct, wiping.")
                    print("Auth correct. Wiping..")
                    WipeList()
                    message_list.delete(0)
                    SetLabelStatus("Wipe process complete.")

                else:
                    SetLabelStatus("Auth incorrect.")
                    print("Auth incorrect. Not responded.")

            if "[INTERNAL SET LABEL MESSAGE]" in message:
                SetLabelStatus(message[28:])

            if "[SEMI-INTERNAL] Auth code is:" in message:
                AuthCode = CalculateAuthCode()
                if message[:29] == AuthCode:
                    SetLabelStatus("[CLIENT MESSAGE] Auth correct")
                    message_list.insert(tkinter.END, "Client: Auth correct")

            if not "-- WIPE AUTHORISE --" in message and not "-- EXIT AUTHORISE --" in message and not "[INTERNAL SET LABEL MESSAGE]" in message:
                message_list.insert(tkinter.END, message)

            if message_list.size() > backlogLength:
                message_list.delete(0)
            
        except OSError: #may be a client exit
            break
        

def send(event=None): #event passed by buttons
    #handles sending of messages
    SetLabelStatus("Sending.")
    message = my_message.get()
    my_message.set("")

    client_socket.send(bytes(message, "utf8"))

    SetLabelStatus("Sent.")

    if message == "/wipe":
        SetLabelStatus("Received, wiping")
        WipeList()
        SetLabelStatus("Wipe process complete.")
    
    if message == "/exit":
        SetLabelStatus("Quitting.")
        WipeList()
        client_socket.close()
        top.destroy()
        top.quit()
        sys.exit()

    if message == "/verify":
        message_list.insert(tkinter.END, "Client auth: " + CalculateAuthCode())

    if message == "/help":
        SetLabelStatus("Here's some help.")
        WipeList()

        message_list.insert(tkinter.END, "If nothing you type is appearing in the list, it's")
        message_list.insert(tkinter.END, "cause you have a broken connection.")
        message_list.insert(tkinter.END, "Local commands:")
        message_list.insert(tkinter.END, "/wipe - wipes text locally")
        message_list.insert(tkinter.END, "/exit - exits application")
        message_list.insert(tkinter.END, "/verify - tells server to return auth and returns client side")
        message_list.insert(tkinter.END, "... is for debug, not security, because the server can pretend")
        message_list.insert(tkinter.END, "...to be the client")
        message_list.insert(tkinter.END, "Admin commands: ")
        message_list.insert(tkinter.END, "/wipe -a - wipes everyone's text")
        message_list.insert(tkinter.END, "/exit -a - closes everyone's application")
        message_list.insert(tkinter.END, "These will only work if you have authenticated.")
        message_list.insert(tkinter.END, "To authenticate, put admin somewhere in your name")
        message_list.insert(tkinter.END, "next time and enter the password.")
        message_list.insert(tkinter.END, "This will only work on people with remote enabled")

    
    
def on_closing():
    #called when window closed
    WipeList()
    my_message.set("{quit}")
    send()
    top.destroy()
    sys.exit()

def WipeList():
    message_list.delete(0, tkinter.END)

def SetLabelStatus(text):
    statusLabel["text"] = text
    
top = tkinter.Tk()

top.title("Frontend V0.1")

messages_frame = tkinter.Frame(top)

my_message = tkinter.StringVar()
my_message.set("")

scrollbar = tkinter.Scrollbar(messages_frame)

if DoCustom == True:
    listHeight = int(input("List height? 20 is sensible> "))
    listWidth = int(input("List width? 50 is sensible... > "))

else:
    listHeight = 20
    listWidth = 50
message_list = tkinter.Listbox(messages_frame, height = listHeight, width = listWidth, yscrollcommand=scrollbar.set)

scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_message)
entry_field.bind("<Return>", send)
entry_field.pack()

send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

statusLabel = tkinter.Label(top, text="-")
statusLabel.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

if DoCustom == True:
    backlogLength = int(input("What length should the backlog be before removing the end? > "))
    host = input("Enter host: ")
    port = input("Enter port: ")

else:
    backlogLength = 20
    #host = "127.0.0.1"
    #host = "86.31.133.208"
    host = "192.168.0.35"
    port = 34000
    allowRemoteAccess = True

if not port:
    port = 34000

else:
    port = int(port)

Buffer_size = 1024
Address = (host, port)
client_socket = socket(AF_INET, SOCK_STREAM)

tries = 0

while True:
    if tries < 20:
       tries = tries + 1
       
    try:
        SetLabelStatus("Attempting to connect.")
        client_socket.connect(Address)
        print("Succesful connection established.")
        SetLabelStatus("Succesful connection established.")
        break
        
    except ConnectionRefusedError:
        print("Connection refused. Retrying in " + str(tries) + " seconds.")
        SetLabelStatus("Error. Retrying in " + str(tries) + " seconds.")
        time.sleep(tries)
        continue

SetLabelStatus("Starting receive thread.")
receive_thread = Thread(target=ReceiveFromServer)
receive_thread.start()
SetLabelStatus("Done!")

tkinter.mainloop()  # Starts GUI execution.
