import socket 
import os
from _thread import *
import threading 
import time
import hashlib
from block import ValidationBlock, Block, MetaBlock
import Miner
from Miner import miner
import serverLogger
import traceback
import os.path
from pathlib import Path
import json
from filelock import FileLock

class NonBlockingClient:
    def __init__(self,targetHost,targetPort):
        self.__server=(targetHost,targetPort)
        self.__logger=serverLogger.serverLogger("Logs.txt",False)
        
        
    def sendtx(self,hashmessage,server):
        self.__clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.__clientsocket.settimeout(15)
        self.__logger.appendLog('STARTING PROCESS TO SEND TRANSACTION TO ' + str(self.__server)+" : " +str(hashmessage))
        try:
            self.__clientsocket.connect(self.__server) 
            message=b'2tx'
            self.__clientsocket.send(message) 
        
            data = self.__clientsocket.recv(10) 
            self.__logger.appendLog('Received from the server :' +str(data.decode('utf-8')))
            if data.decode('utf-8') =="ACK----2tx":
                self.__logger.appendLog("Proper Response Recieved")
            #### Send Hash
                message=hashmessage.encode("utf-8")
                self.__logger.appendLog("SENDING " +str(message))
                self.__clientsocket.send(message)
                data=self.__clientsocket.recv(10)
                self.__logger.appendLog("RECIEVED: "+ str(data.decode('utf-8')))

        except:
                self.__logger.appendLog("THE SERVER "+ str(self.__server)+ " IS DOWN")
        self.__clientsocket.close()
        

    def sendbk(self,message,server):
        self.__logger.appendLog('STARTING PROCESS TO SEND BLOCK TO ' + str(server)+" : " +message)
        self.__clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        connected=False
        self.__clientsocket.settimeout(15)
        try:
            self.__clientsocket.connect(server)
            connected=True 
        #self.__logger.appendLog('STARTING PROCESS TO SEND BLOCK TO ' + str(self.__server)+" : " +str(data.decode('utf-8')))
        except:
            self.__logger.appendLog("THE SERVER "+ str(server)+ " IS DOWN")
            connected=False

        if(connected):
            startmessage=b'3bk'
            self.__clientsocket.sendall(startmessage) 
            try:
                data = self.__clientsocket.recv(10) 
                self.__logger.appendLog('Received from the server :' +str(data.decode('utf-8')))
                if data.decode('utf-8') =="ACK----3bk":
                    self.__logger.appendLog("Proper Response Recieved")
                #### Send Hash
                    message=message.encode('utf-8')
                    self.__logger.appendLog("SENDING " +str(message))
                    self.__clientsocket.send(message)
                    data=self.__clientsocket.recv(10)

                    self.__logger.appendLog("RECEIVED MESSAGE" +str(data.decode('utf-8')))
                    if data.decode('utf-8') =="ACK---DONE":
                        self.__logger.appendLog("SUCCESSFULY SENT FILE")
                    else:
                        self.__logger.appendLog("SOMETHING WENT WRONG")
                else:
                    self.__logger.appendLog("SOMETHING WENT WRONG")

            except:
                    self.__logger.appendLog("THE SERVER "+ str(self.__clientsocket)+ " IS DOWN")
            self.__clientsocket.close()

class NonBlockingServer:
    def __init__(self):
        self.__logger=serverLogger.serverLogger("Logs.txt")
        self.__addr, self.__port,self.__knownServers=self.getConfig()
        self.__serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__serverSocket.bind((self.__addr,self.__port))
        self.__serverSocket.settimeout(10)
        self.__serverSocket.listen(5) 
        self.setup_miner()

    def setup_miner(self):
        miner_index = Miner.get_miner_index()
        print()
        print("********MINER INDEX ", miner_index)
        time.sleep(5)
        print()

        self.__miner=miner(miner_index)
        self.__miner.printBlockChain()

    def getConfig(self):
        

        self.__logger.appendLog("GETTING CONFIG FILE DATA FROM ./conf/nodes.conf")
        my_file = open("./conf/nodes.conf", "r")
        content_list = my_file.readlines()
        my_file.close()
        knownServers=[]
        for s in content_list:
            addr=s.split(',')
            server=(str(addr[0]), int(addr[1].replace('\n','')))
            knownServers.append(server)
        host=knownServers[0][0]
        port=knownServers[0][1]
        return host,port,knownServers[1:]

    # thread function 
    def threaded(self,c,addr,senderID):
        try:               
            data = c.recv(3)    
            self.__logger.appendLog("DATA RECIEVED: "+ str(data))
            message=data.decode('utf-8')
            ## HANDLE QUERY MESSAGE TYPE
            if message=='1qy':
                self.__logger.appendLog("QUERY MESSAGE TYPE RECIEVED FROM " + str(addr))
                c.send(b"ACK----1qy")
                self.__logger.appendLog("SENDING ACK----1qy")
                data=c.recv(10)
                querytype=data.decode('utf-8')
                self.__logger.appendLog("RECIEVED QUERY TYPE: " + str(querytype))
                
                if str(querytype) == "LAST---BLK":
                    lastBlock=Miner.getLastBlock()
                    self.__logger.appendLog("SENDING BLOCK TO CLIENT ")
                    c.send(str(lastBlock).encode('utf-8'))
                    self.__logger.appendLog("GETTING MESSAGE FROM CLIENT ")
                    data = c.recv(10)
                    self.__logger.appendLog("MESSAGE FROM CLIENT: " + str(data.decode('utf-8')))
                    message=data.decode('utf-8')
                    if message == "BLK---RECV":
                        self.__logger.appendLog("SENDING ACK---DONE")
                        c.send(b'ACK---DONE')
                        self.__logger.appendLog("CLOSING CONNECTION")
                        c.close()
                    else:
                        self.__logger.appendLog("ERROR: DID NOT RECIEVE BLK---RECV MESSAGE")
                        c.close()
                
                elif str(querytype) == "FULL---CHN":
                    currentChain=Miner.getCurrentChain()
                    self.__logger.appendLog("SENDING "+str(currentChain))
                    print("CURRENT CHAIN", currentChain)
                    c.send(str(currentChain).encode('utf-8'))
                    data=c.recv(10)
                    message=data.decode('utf-8')
                    self.__logger.appendLog("MESSAGE FROM CLIENT: " + str(message))
                    
                    if message == "CHAIN-RECV":
                        self.__logger.appendLog("SENDING ACK---DONE")
                        c.send(b'ACK---DONE')
                        self.__logger.appendLog("CLOSING CONNECTION")
                        c.close()
                    else:
                        self.__logger.appendLog("ERROR: DID NOT RECIEVE CHAIN-RECV MESSAGE")
                        c.close()
                else:
                    self.__logger.appendLog("ERROR: UNEXPECTED QUERY MESSAGE TYPE" +str(message))
                    c.close()

            ## HANDLE TRANSACTION MESSAGE TYPE
            elif data.decode('utf-8')=='2tx':
                self.__logger.appendLog("TRANSACTION MESSAGE TYPE RECIEVED FROM " + str(addr))
                c.send(b"ACK----2tx")
                self.__logger.appendLog("SENDING ACK----2tx")
                data=c.recv(46)
                hashvalue=data.decode('utf-8')
                self.__logger.appendLog("HASH RECIEVED " + str(hashvalue))
                result=self.checkHash(hashvalue,"TX")
                self.__logger.appendLog("SENDING ACK---DONE")
                c.send(b'ACK---DONE')
                self.__logger.appendLog("CLOSING CONNECTION")
                c.close()
                if result==False:
                    self.propogateMessage(hashvalue,"TX")
                    self.addhash(hashvalue,"TX")
                else:
                    self.__logger.appendLog("HASH PREVIOUSLY RECIEVED " + str(hashvalue))

            ## HANDLE BLOCKK MESSAGE TYPE		
            elif data.decode('utf-8')=='3bk':
                msgType='3bk'
                self.__logger.appendLog("BLOCK MESSAGE TYPE RECIEVED FROM " + str(addr))
                self.__logger.appendLog("SENDING ACK----3bk")
                c.send(b"ACK----3bk")
                data=c.recv(46)
                hashvalue=data.decode('utf-8')
                self.__logger.appendLog("HASH RECIEVED " + str(hashvalue))
                result=self.checkHash(hashvalue,"BK")
                self.__logger.appendLog("SENDING ACK---DONE")
                c.send(b'ACK---DONE')
                self.__logger.appendLog("CLOSING CONNECTION")
                c.close() 
                if result==False:
                    self.download_block_locally(hashvalue)
                    self.addhash(hashvalue,"BK")
                    self.__miner.record_transactions(hashvalue)
                    self.propogateMessage(hashvalue,"BK")
                    
                    
                else:
                    self.__logger.appendLog("HASH PREVIOUSLY RECIEVED " + str(hashvalue))
            ## HANDLE BLOCKK MESSAGE TYPE		
            elif data.decode('utf-8')=='4vb':
                print()
                print()
                print()
                print("RECIEVED VALIDATION BLOCK FROM MINER")
                print()
                print()
                print()
                self.__logger.appendLog("BLOCK MESSAGE TYPE RECIEVED FROM " + str(addr))
                self.__logger.appendLog("SENDING ACK----4vb")
                c.send(b"ACK----4vb")
                data=c.recv(64)
                sender_address=data.decode('utf-8')
                self.__logger.appendLog("HASH RECIEVED " + str(sender_address))
                self.__logger.appendLog("SENDING ACK---ADDR")
                c.send(b'ACK---ADDR')
                data=c.recv(64)
                hashvalue=data.decode('utf-8')
                self.__logger.appendLog("HASH RECIEVED " + str(hashvalue))
                self.__logger.appendLog("SENDING ACK---DONE")
                c.send(b'ACK---DONE')
                self.__logger.appendLog("CLOSING CONNECTION")
                c.close() 
                print()
                valid_Block, reason = self.__miner.validate_block(hashvalue)
                print("VALID BLOCK VALUE: ", valid_Block)
                print()
                print("ORIGINATOR: ",sender_address)
                print("****************************************")
                print()
                print()
                vote={}
                block_height = self.__miner.get_block_height(hashvalue)
                vote["block_height"] = block_height
                vote["block_id"] = hashvalue
                if valid_Block:
                    vote["vote"] = "Accept"
                else:
                    vote["vote"] = "Reject"
                    
                vote["reason"] = reason
         #       print()
         #       print("VOTE", vote)
           #     print("REASON " , reason )
                print()
                vote["member"] = self.__miner.address
                CID = self.__miner.sign_vote(vote)
                print("CID ", CID)
                self.__miner.respond_To_Committee(CID,sender_address)
        


                ## GET VALIDATION BLOCK
        #        validation_block :ValidationBlock = self.__miner.get_validation_block(hashvalue)
        #        block_CID = validation_block.get_block_ref()
                ## GET BLOCK FROM VALIDATION BLOCK REFERENCE
         #       if validation_block.validate_block_sync() == False:
         #           pass
         #       else:

                    
            elif data.decode('utf-8')=='4re':
                print("RESPONSE RECEIVED!!!!" )
                msgType='4re'
                self.__logger.appendLog("RESPONSE TYPE RECIEVED FROM " + str(addr))
                self.__logger.appendLog("SENDING ACK----4re")
                c.send(b"ACK----4re")
                data=c.recv(64)
                hashvalue=data.decode('utf-8')
                self.__logger.appendLog("HASH RECIEVED " + str(hashvalue))
                #result=self.checkHash(hashvalue,"BK")
                self.__logger.appendLog("SENDING ACK---DONE")
                c.send(b'ACK---DONE')
                self.__logger.appendLog("CLOSING CONNECTION")
                c.close() 
                sender_address =str(addr[0]) + ",8000"
                print("SENDER IP ADDRESS", sender_address)
                sender_address = self.__miner.get_address_from_ip(sender_address)
                print("SENDER ADDRESS")
                self.__miner.store_vote(hashvalue, sender_address)
                self.__miner.collect_vote(hashvalue, sender_address)

            else:
                self.__logger.appendLog("UNEXPECTED REQUEST RECIEVED" +str(data.decode('utf-8')))
                c.close()

        except:
            traceback.print_exc()
            self.__logger.appendLog("ERROR:  CLIENT SERVER COMMUNICATION FAILED")
            c.close()

    def checkHash(self,msg,msgtype):
        self.__logger.appendLog('CHECKING HASH AGAINST LOCAL RECORDS ('+str(msg)+')')
        if msgtype=="TX":
            filename="transactionlog.txt"
        else:
            filename="blocklog.txt"
        my_file = open(filename, "r")
        content = my_file.readlines()
        my_file.close()
        found=False
        for item in content:
            item=item.replace("\n","")
            if item==msg:
                self.__logger.appendLog('A RECORD FOR THIS ITEM HAS BEEN FOUND')
                found=True
        if not found:
            self.__logger.appendLog('A RECORD FOR THIS ITEM HAS NOT BEEN FOUND')
        return found

    def addhash(self,msg,msgtype):
        if msgtype=="TX":
            self.__logger.appendLog('ADDING RECORD '+ str(msg)+ ' TO transactionlog.txt')
            filename="transactionlog.txt"
        else:
            self.__logger.appendLog('ADDING RECORD '+ str(msg)+ ' TO blocklog.txt')
            filename="blocklog.txt"
        
        lockfile = filename
        lock = FileLock(lockfile + ".lock")
        exists = False
        with lock:
            ### Read First 
            my_file = open(filename, "r")
            txs = my_file.readlines()
            
            for tx in txs:
                if tx.strip() == str(msg).strip():
                    exists =True
            my_file.close()
            if not exists:
                my_file = open(filename, "a")
                my_file.write("\n"+msg)
                my_file.close()

    def propogateMessage(self,message,messageType):
        self.__logger.appendLog('BEGINING PROCESS TO PROGATE MESSAGE TO PEERS')
        print("KNOWN SERVERS: ", self.__knownServers)
        for n in self.__knownServers:
            self.__logger.appendLog('CONNECTING TO '+str(n))
            myclient=NonBlockingClient(str(n[0]),n[1])
            if(messageType=="TX"):
                myclient.sendtx(message,n)
            elif(messageType=="BK"):
                myclient.sendbk(message,n)

    def download_block_locally(self,message):
        print("DOWNLOADING BLOCK LOCALLY ")
        content = self.__miner.get_block(message)
        f =open("Blocks/"+str(message)+".json","w")
        f.write(content.decode())
        f.close()
       
        self.__miner.append_block(message)

    def run_minner(self):
        ## INITIAL SET UP OF DEFAULT COMMITTEE
    
        f=open("MinerFiles/minerList.txt","r")
        miners = f.readlines()
        f.close()
        mining = False
        while True:
            if mining == False:

                print("WAITING 5 SECONDS TO CHECK IF NEXT BLOCK IS READY")
                print()
                time.sleep(5)
                print("Getting last block")
                blockData=Miner.getLastBlockData()
                print("PREVIOUS BLOCK HEIGHT: ",blockData["Data"]["Height"])
                print("PREVIOUS BLOCK TIMESTAMP:",blockData["Data"]["Timestamp"])
                null_block = False
                ## SPECIAL CASE TO IGNORE DELAY FOR GENESIS BLOCK
                if blockData["Data"]["Height"] > 0:

                    previous_timestamp=blockData["Data"]["Timestamp"]
                    
                    if(previous_timestamp + 90 < time.time()):
                        expected_miner_index = (blockData["Data"]["Height"]+2) %(len(miners))
                        null_block=True
                    else:
                        expected_miner_index = (blockData["Data"]["Height"]+1) %(len(miners))
                else:
                    expected_miner_index = (blockData["Data"]["Height"]+1) %(len(miners))
                    self.__miner.connect_to_committee(blockData["Data"]["CommitteeID"])
                print("INDEX: ", expected_miner_index)
                print("EXPECTED MINER: ", expected_miner_index, miners[expected_miner_index].strip())
                print("MINER ", miners[expected_miner_index].strip(), self.__miner.address)
                time.sleep(5)
                if miners[expected_miner_index].strip()==self.__miner.address.strip():
                    print("THIIS USER WILL MINE")
                    mining = True
                    self.__miner.mine(null_block)
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("***********************************************************************************")
                    print("SETTING MINING TO FALSE")
                    mining = False
                else:
                    print("NOT TIME TO MINE THIS BLOCK")
            else:
                print("LOGGING PASS FOR MINING")

    def run(self):
    
        self.__logger.appendLog("STARTING SERVER:" + str(self.__addr) + " , "+ str(self.__port))
        while True: 
            try:
                c, addr = self.__serverSocket.accept() 
                self.__logger.appendLog('Connected to :'+ str(addr[0])+ ':'+ str(addr[1]))
                x = threading.Thread(target=self.threaded,args=(c,addr,self.__miner.address,))
                x.start()
            except:
                time.sleep(1)
        self.__serverSocket.close() 


def Main(): 
#	host = '127.0.0.1'
    filename = Path("blocklog.txt")
    filename.touch(exist_ok=True)
    filename = Path("transactionlog.txt")
    filename.touch(exist_ok=True)

    myserver=NonBlockingServer()
    x = threading.Thread(target=myserver.run)
    x.start()
    myserver.run_minner()
  
    print("SETUP COMPLETE")
 
    

if __name__ == '__main__': 
    Main() 