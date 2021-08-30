import socket, time, threading  # I am not the creator of the 'socket', 'time', and 'threading' modules.

#  This script creates both the "Host" and "Client" classes, which are used to interact with another player

'''
r = regular
c = castle
e = en passant
p = promote

Ex: u.c.00.01  # This means: 'this is a regular (u) move, it leads to check, the piece on 0,0 goes to 0,1'
#x: c.s.40.60.70.50  : 'this is a castle, it is safe, piece on 4,0 goes to 6,0. the piece on 7,0 goes to 5,0
Ex: e.s.31.42.41  : 'this is an en passant, it is safe, piece on 3,1 goes to 4,2. 4,1 is captured
Ex: r.c.06.07  : 'this is a promotion to rook, it leads to check, piece on 0,6 goes to 0,7
Ex: n.s.26.17  : 'this is a promotion to night, it is safe, piece on 2,6 goes to 1,7
Ex: j.s.26.15  : 'jumping'
Ex: forfeit  : if there is a disonnection or if the player forfeits
Ex: draw  : player has asked for a draw
Ex: draw.accepted : player has accepted the draw
Ex: checkmate : sent to inform the player that checkmate has been achieved
Ex: stalemate : sent to inform the player that stalemate has been achieved
Ex: deny  : player cannot join because 2 players are already playing
'''

name_of_computer = socket.gethostname()
host_computer = 'DESKTOP-UDMK7AI'  # A computer must always be considered the 'host' computer.
are_we_host = True if name_of_computer == host_computer else False

PORT = 5050  # A specific port must be allocated for this interaction
IP = '192.168.1.40'  # I am currently only connecting through my local network, but this can be modified to allow for play through public addresses
ADDR = (IP, PORT)

FORMAT = 'utf-8'
HEADER = 15

DISCONNECT_MESSAGE = '!DISCONNECT'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

if are_we_host:  # If we are the host, then let us bind the socket to our computer. We must call this outside of the Host class because we can only bind once.
    sock.bind(ADDR)
    sock.listen()  # immediately begin listening for incoming connections

sock.setblocking(0)  # Very important!  Instead of blocking, blocking_commands will instead error if it takes too long.

class Host:
    def __init__(self):
        self.player_conn, self.player_addr = False, False
        self.connected = False
        self.ending = False

        thread1 = threading.Thread(target=self.start)
        thread1.start()

    def receive(self):  # Waits until we receive a message
        msg = False

        while not msg:
            while True:
                try:
                    msg = self.player_conn.recv(HEADER).decode(FORMAT)
                except:
                    continue
                break

        msg = msg.rstrip()

        if msg == DISCONNECT_MESSAGE or msg == 'forfeit' or msg == 'draw.accepted':  # If we get any of these messages, then we expect there to be no more reponses, so we close the connection
            self.ending = True
            self.connected = False

            self.send(DISCONNECT_MESSAGE)

            self.player_conn.close()  # Closing the connection

        return msg

    def send(self, msg, conn=False):  # Used to send a message to player
        fmsg = msg.encode(FORMAT) + b' ' * (HEADER - len(msg))
        self.player_conn.send(fmsg) if not conn else conn.send(fmsg)

    def start(self):  # In this part of the process, we wait until we get a connection, then we start the receiving, sending process.
        print(f"[LISTENING] Server is listening on {IP}")

        while True:
            try:
                self.player_conn, self.player_addr = sock.accept()  # Try and accept connection.
                time.sleep(1)  # VERY IMPORTANT, if we do not wait, we are unable to catch any reponse.

                try:  # Receive 'joining' message
                    msg = self.player_conn.recv(HEADER).decode(FORMAT)

                    if not msg:  # We will only ever receive nothing if it is a dead connection.
                        self.player_conn.close()
                        continue
                    elif 'joining' in msg:  # If we get the joining msg, then check to see if we have a 'left' msg.
                        try:
                            msg = self.player_conn.recv(HEADER).decode(FORMAT)
                            if 'left' in msg:  # If the player had left before ever getting connected, then they would have left a 'left' msg.
                                continue
                        except:  # In the case that we have recevied a 'joining' message but not a 'left' message, then we connect to them and break the loop
                            break
                except:  # If we cannot immediately get msg, then we abort it and continue
                    self.player_conn.close()
                    continue
            except:  # If we were unable to catch a connection, then just try again
                if self.ending:  # However, if we are in the process of ending, then we want to end this.
                    return

        if self.player_addr[0] == '192.168.1.40':  # The only time that we have connected to ourselves is to leave the network. We cannot say we are self.connected or else the deny loop will start
            return

        self.connected = True

        thread2 = threading.Thread(target=self.deny)
        thread2.start()

    def deny(self):  # The 'deny' loop accepts any additional connections and immediately 'denies' them. This is because we already have a player connection, so this new connection cannot join our game
        while self.connected:
            try:
                conn, addr = sock.accept()
                self.send('deny', conn)
                conn.close()
            except:
                continue

    def end(self):  # End process: if we instigate it, we send them the other player a disconnect message, then they send it back, then we close the connection (found in the 'receive' function).
        self.ending = True
        if not self.connected:  # If we have already disconnected, then we don't need to do anything
            pass
        else:
            self.connected = False
            self.send(DISCONNECT_MESSAGE)  # Send other player the disconnect_message

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Since we aren't binding the socket to anything, then we must create a new socket every time we want to make a new connection

        self.connected = False
        self.ending = False
        self.first_message = False

        thread1 = threading.Thread(target=self.start)
        thread1.start()

    def start(self):
        while True:
            try:
                self.sock.connect(ADDR)  # Try and connect
                break
            except:  # If failed, keep trying.
                if self.ending:  # However, if we are ending, then we exit the loop
                    return

        self.sock.setblocking(0)  # Very important

        self.send('joining')  # send host a 'joining message'

        thread1 = threading.Thread(target=self.receive)  # This is for receiving the first message
        thread1.start()

    def receive(self):  # For receiving messages
        msg = False
        while True:
            try:
                msg = self.sock.recv(HEADER).decode(FORMAT)  # I don't know if we are receiving from sock!!!
                if bool(msg):  # If the message is NOT empty, then we break
                    break

            except ConnectionError:  # If we were unable to receive a message because the connection had been lost, then we will try and reconnect
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.sock.setblocking(1)  # Blocking must be enabled in order for the connect command to work

                while True:
                    try:
                        self.sock.connect(ADDR)  # Try and REconnect
                        break
                    except:  # If reconnection failed, keep trying
                        if self.ending:  # However, if we are ending, then return
                            return

                self.sock.setblocking(0)  # Once we have reconnected, disable blocking
                self.send('joining')  # resend 'joining'

            except BlockingIOError:  # If we were unable to receive a message because it timed out, then just try again
                if self.ending:  # However, if we are ending, then we will return
                    if self.connected:  # If we have a connection, then send a 'forfeit' message
                        self.send('forfeit')
                    else:
                        self.send('left')  # If we haven't connected yet, then send a 'left' message
                    return

        msg = msg.rstrip()

        if not self.first_message:  # If we don't already have a first message, then make the message we just received the first message (the first message will always be the player's color)
            self.first_message = msg
            self.connected = True
            return
        if msg == DISCONNECT_MESSAGE or msg == 'forfeit' or msg == 'draw.accepted' or msg == '':  # Elif if the msg == disconnect, forfeit, or draw.accepted, then we will being the end process (we aren't intending to receive any more messages)
            self.ending = True
            self.send(DISCONNECT_MESSAGE)
            self.connected = False

        return msg

    def send(self, msg, conn=False):  # Used for formatting and sending messages
        fmsg = msg.encode(FORMAT) + b' ' * (HEADER -  len(msg))
        self.sock.send(fmsg)

    def end(self):
        self.ending = True
