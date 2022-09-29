## TODO: HANDLE DISCONNECTS
## TODO: SEND BLOCK TO SUBSET OF PEERS
from asyncio import format_helpers
from ctypes.wintypes import HENHMETAFILE
import json
from posixpath import expanduser
from pqcrypto.sign.falcon_512 import sign, verify
#from pqcrypto.sign.falcon_512 import generate_keypair, sign, verify
import time
import base64
from IPFSCallHelper import IPFSWorker
import block
from block import GenesisBlock,Block, GenesisMetaBlock, GenesisValidationBlock, MetaBlock, ValidationBlock
import transaction
from transaction import Transaction
import socket
from os import path
import os.path
from pathlib import Path
from _thread import *
import threading 
import hashlib
from filelock import FileLock
####from filelock import FileLock




def GetLatestTx():
    f=open("transactionlog.txt","r") 
    alltx=f.readlines()
    f.close()
    return alltx[-1]

def getLastBlock():
    filename = Path("MinerFiles/blockchainOrderRef")
    if(not path.exists("MinerFiles/blockchainOrderRef")):
        filename.touch(exist_ok=True)  
    f=open("MinerFiles/blockchainOrderRef","r") 
    blockChain=f.read().splitlines()
    f.close()
    return blockChain[-1]

def getCurrentChain():
    print("GETTING CURRENT CHAIN")
    newIpfsAPIInstance=IPFSWorker()
    return newIpfsAPIInstance.addFileByPath("MinerFiles/blockchainOrderRef")

def get_miner_index():
    print("GETTING MINER INDEX")
    newIpfsAPIInstance=IPFSWorker()
    
    miner_ID = newIpfsAPIInstance.getCID("Local/KeyChain/PublicKey.key")
    print("MINER ID: ", miner_ID)
    f = open("MinerFiles/minerList.txt")
    miners=f.readlines()
    f.close()
    index=0
    for m in miners:
        if m.strip() == miner_ID:
            return index
        else:
            index = index + 1

def getLastBlockData():
    blockFileName = "Blocks/"+str(getLastBlock())+".json"
    f = open(blockFileName,"r")
    raw_Data=f.read()
    blockData=json.loads(raw_Data)
    return blockData



class miner():
    def __init__(self, id):
        self.__pendingTX = {} ### Tx that still need to be added (dictionary for easy lookukp)
        self.__proposedTX = [] ### Tx that are projected to be added in next block
        self.__addedTX = {} ### Tx that exist in current blocks (dictionary points to block added to)
        self.__blocks = {} ### All blocks that are known (dictionary points to status index in blockChain if included)
        self.__validation_blocks = {}### All Validation blocks that are known (dictionary points to status index in blockChain if included)
        self.__meta_blocks = {}### All meta blocks that are known (dictionary points to status index in blockChain if included)
        self.__blockChain = [] ### local reference to the official blockchain
        self.__myBlocks = [] ### Blocks that have been added to the chain by this miner (CID only)
        self.__my_ValidationBlocks = [] ### Validation Blocks that have been added to the chain by this Miner (CID only)
        self.__lastLinePointer=0 ### Placeholder to keep track of the last line added to transactions.txt
        self.ipfsAPIInstance=IPFSWorker()
        self.__privKey=None
        self.address=None
        self.__privKey,self.address=self.load_key()
        self.id=id
        self.votes=[]
        self.__received_voters = []
        self.__validation_block_CID = ""
        self.__collectedVotes = {}
        self.__collected_vote_count = 0


        self.startup()

    def decodeKey(self, keyvalue):
        return base64.decodebytes(keyvalue)

    def connect_to_committee(self,committee_CID):
        committee_content = self.ipfsAPIInstance.getContent(committee_CID,"NA")
        committee_json = json.loads(committee_content)
        members_list = committee_json["members"]
        for i in range(0,len(members_list)):
            #/ip4/3.13.252.251/tcp/4001/p2p/12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY
            try:
                member_json = json.loads(members_list[i])
            except:
                print("Already dictionary.  skipping json loads")
                member_json = members_list[i]
            ip_address = member_json["server"].split(",")[0]
            connection_string = "/ip4/" + ip_address + "/tcp/4001/p2p/" + member_json["ipfs"]
            self.ipfsAPIInstance.add_peer(connection_string)


## TODO:  Add a way to get latest meta block
 #   def get_block_at_height(self,block_height):


    def sign_vote(self,content):
 #       print()
 #       print("IN SIGNING VOTES")cd 
 #       print("CONTENT: ",content)
        message = json.dumps(content)
        message_bytes = message.encode('utf-8')
        signature = sign(self.__privKey, message_bytes)
        signature = signature.hex()
        new_data = {}
        try: 
            new_data["Vote"] = json.loads(content)
        except:
            new_data["Vote"] = content
        new_data["Signature"] = signature
 #       print("NEW DATA: ", new_data)
        message = json.dumps(new_data)
        f=open("MinerFiles/Temp.json","w")
        f.write(message)
        f.close()     
        CID = self.ipfsAPIInstance.getCIDAndAdd("MinerFiles/Temp.json","NA")
 #       print()
 #       print("ADDING VOTE CID ", CID)
 #       print()
        return CID
    

    def load_key(self):
        if not self.__privKey is None and not self.address is None:
            return self.__privKey, self.address
        else:
            try:
                f=open("Local/KeyChain/PrivateKey.key", 'rb')
                private_Key = f.read()
                secretKey=self.decodeKey(private_Key)
                f.close()
                
                f=open("Local/KeyChain/PublicKey.key", 'rb') 
                pub = f.read()
                pubKey=self.decodeKey(pub)
                f.close()
                pubAddress= self.ipfsAPIInstance.addfile(pub,"PK")
                self.__privKey = secretKey
                self.address = pubAddress
                return self.__privKey, pubAddress
            except:
                print()
                print()
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("ERROR! You must first initialize a wallet before running the Miner Program")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                exit(0)
    


    def append_block(self,CID):
        print()
        print()
        print("IN APPEND BLOCK")

        self.addBlock(CID)
        self.writeToDisk()
        
      
        
    ### TODO: Change to APPEND instead of Write
    def writeToDisk(self):
        print("****************")
        print(self.__blockChain)
        f=open("MinerFiles/blockchainOrderRef","w")
        for blk in self.__blockChain:
            f.write(str(blk)+"\n")
        f.close()
        blockDictJson = json.dumps(self.__meta_blocks)
        addedTxJson = json.dumps(self.__addedTX)
        f=open("MinerFiles/blockDict.json","w")
        f.write(blockDictJson)
        f.close()
        f=open("MinerFiles/addedTX.json","w")
        f.write(addedTxJson)
        f.close()


    def add_to_blocklog(CID):
        f=open("blocklog.txt","a")
        f.write(CID+str("\n"))
        f.close()

## TODO: Optimize this?
    def addNewTXToPending(self):
        f=open("transactionlog.txt","r") 
        alltx=f.read().splitlines()
        f.close()
    #    if len(alltx) > self.__lastLinePointer:
    #         for line in range(self.__lastLinePointer,len(alltx)):
        for tx in alltx:
            if tx in self.__addedTX:
               if tx in self.__pendingTX:
                    self.__pendingTX[tx].pop()
            else:
                self.__pendingTX[tx]="na"
    #self.__lastLinePointer=len(alltx)-1

    def startup(self):
        print("STARTING")
        #### Initialize The Transaction Log
        filename = Path("transactionlog.txt")
        if(not path.exists("transactionlog.txt")):
            filename.touch(exist_ok=True)
        f=open("transactionlog.txt","r") 
        alltx=f.read().splitlines()
        f.close()

       ##### Check if supporting folders are present.  If not create them. 
        
        if not path.exists('MinerFiles'):
            os.makedirs('MinerFiles')
        
        if not path.exists('Blocks'):
            os.makedirs('Blocks')

        if not path.exists('TX'):
            os.makedirs('TX')
#### Loads transactions into either added or pending dict
        self.__lastLinePointer=len(alltx)
        filename = Path("MinerFiles/addedTX.json")
        if(not path.exists("MinerFiles/addedTX.json")):
            filename.touch(exist_ok=True) 
            f=open("MinerFiles/addedTX.json","w")
            f.write("{}")
            f.close()   
        f=open("MinerFiles/addedTX.json","r")
        self.__addedTX=json.load(f)
        f.close()
        print()
        print("PENDING TRANSACTIONS ",self.__pendingTX)
        for tx in alltx:
            if tx in self.__addedTX:
                pass
            else:
                self.__pendingTX[tx]="na"

        #### Load Blockchain
        filename = Path("MinerFiles/blockchainOrderRef")
        if(not path.exists("MinerFiles/blockchainOrderRef")):
            filename.touch(exist_ok=True)  
        f=open("MinerFiles/blockchainOrderRef","r") 
        self.__blockChain=f.read().splitlines()
        f.close()
        #### Load Block Dictionary into memory from disk
        filename = Path("MinerFiles/blockDict.json")
        if(not path.exists("MinerFiles/blockDict.json")):
            filename.touch(exist_ok=True)  
            f=open("MinerFiles/blockDict.json","w")
            f.write("{}")
            f.close()   
        f=open("MinerFiles/blockDict.json","r")
        self.__meta_blocks=json.load(f)
        f.close()

        if self.crossReferenceBlockData():
            print("GOOD BLOCKCHAIN")
        else:
            print("BAD CHAIN")

    def crossReferenceBlockData(self):
        ### Iterate over array and compare values with block dictionary. 
        for index in range(len(self.__blockChain)):
            if self.__blockChain[index] == self.__blocks[self.__blockChain[index]]:
                print("Block ", index," matches")
            else:
                print("BLOCK HEIGHT MISMATCH AT INDEX ", index)
        #### Verify the last block has a clear path back to Genesis Block
        print("SIZE OF BLOCKCHAIN: ",len(self.__blockChain))
        if len(self.__blockChain) == 0:
            print("NO BLOCKS..")
            print("BUILDING GENESIS BLOCK")
            gb = GenesisBlock(self.address, self.ipfsAPIInstance)
            block_CID = gb.writeBlock(self.ipfsAPIInstance)
            gv = GenesisValidationBlock(self.address, self.ipfsAPIInstance)
            validataion_CID = gv.writeBlock(self.ipfsAPIInstance)
            gm = GenesisMetaBlock(self.address, self.ipfsAPIInstance)
            meta_CID = gm.writeBlock(self.ipfsAPIInstance)


            print("DONE WRITING BLOCKS ")
            self.addBlock(meta_CID)
            self.writeToDisk()
            
            
            return True
        else:

            print("LATEST BLOCK", self.__blockChain[-1])    
            finalID=[self.__blockChain[-1]]
            print("FINALID: ",finalID)
            if self.verifyReverseOrder(finalID[0]):
                print("VALIDATED TO GENESIS BLOCK")
                return True
                
            else:
                print("SOMETHING WENT WRONG")
                return False


    def generatMerkleRow(self, rowData):
        hashes=[]
        toDo=int(len(rowData)/2)
        index=0
        for i in range(int(toDo)):
            nextLevelUp=self.hashTransactions(rowData[index],rowData[index+1])
            index=index+2
            hashes.append(nextLevelUp)

        if(index==(len(rowData)-1)):
            nextLevelUp=self.hashTransactions(rowData[index],rowData[index])
            hashes.append(nextLevelUp)
        return hashes    

    def hashTransactions(self,transaction1, transaction2):
        hasher = hashlib.sha256()
        hasher.update(transaction1.encode('utf-8'))
        hasher.update(transaction2.encode('utf-8'))
        combinedHash=hasher.hexdigest()
        return combinedHash

    def validate_block(self, CID):
        should_continue = True
        while should_continue:
            print(" TRYING TO VALIDE BLOCK ", CID)
            try:
                ref_block : Block = block.create_block_from_CID(self.ipfsAPIInstance,CID)
                if ref_block == None:
                    should_continue = True
                else:
                    should_continue = False
            except: 
                print("CID NOT RECIEVED YET", CID)
                time.sleep(2)
        valid, reason = ref_block.validate_block(self.ipfsAPIInstance) 
        return valid, reason
  
    def verifyReverseOrder(self, lastBlockID):
        blockHeight=100
        while blockHeight>0:

            blockContent= self.ipfsAPIInstance.getContent(lastBlockID, "BK")
            bkJson=json.loads(blockContent)

            blockHeight=bkJson["Header"]["Height"]
            if blockHeight==0:
                break
            lastBlockID=bkJson["Header"]["PreviousBlock"]

        print("REACHED GENESIS BLOCK", blockHeight, lastBlockID)
        return lastBlockID==self.__blockChain[0]

    def printTransactions(self, txType):
        if txType=="pending":
            print(self.__pendingTX)
        if txType=="added":
            print(self.__addedTX)

    def txList(self):
        txList=[]
        for tx in self.__pendingTX:
            txList.append(tx)
        return txList
    
    def printBlockChain(self):
        print("PRINTING BLOCKCHAIN")
        for bk in self.__blockChain:
            print(bk)
    ########################################################################################################################
    def record_transactions(self,BlockCID):
        print("IN RECORD TRANSACTIONS")
        meta_block :MetaBlock = block.create_metablock_from_CID(self.ipfsAPIInstance, BlockCID)
        ref_block :Block = block.create_block_from_CID(self.ipfsAPIInstance, meta_block.get_refrence_block_ID())
        txs = ref_block.get_transactions()
        print()
        print("PENDING ", self.__pendingTX)
        print("ADDED ", self.__addedTX)
        for tx in txs:
        
            self.__addedTX[tx]=BlockCID
            if tx in self.__pendingTX:
                self.__pendingTX.pop(tx)
            


    def addBlock(self,BlockCID):
        print()
        print()
        print()
        print("IN ADD BLOCK")
        print()
 #       if len(self.__blockChain) == 0:
 #           print("GENESIS BLOCKCHAIN")
 #           self.__blockChain.append(BlockCID)
 #           self.__blocks[BlockCID]=(len(self.__blockChain)-1)

#        else:
        with lock:
            print("IN LOCK")
            print("BLOCK CID: ", BlockCID)
            print("BLOCKS: ",self.__blocks)
            if BlockCID not in self.__blocks:
                meta_block : MetaBlock = block.create_metablock_from_CID(self.ipfsAPIInstance, BlockCID.strip())
                
                print(type(meta_block))
                if len(self.__blockChain) >= 1:
                    last = self.__blockChain[-1]
                    print("LAST ", last)
                else: 
                    last =""
                if last.strip() != BlockCID.strip():
                    self.__blockChain.append(BlockCID)
                    self.__blocks[BlockCID] = {"Height": (len(self.__blockChain)-1), "Validation" : meta_block.get_validation_ID(), "Block" : meta_block.get_refrence_block_ID()}
                last = self.__blockChain[-1]
    
    def get_address_from_ip(self,addr):
        f = open("./conf/comitteeNodes.json", "r")
        raw_list = f.read()
        f.close()
        committee_members=json.loads(raw_list)
        for m in committee_members["members"]:
            if m["server"] == addr:
                return m["address"]

    def respond_To_Committee(self,CID,originator):
        print("**********************************")
        print("*************************************")
        print("Responding to Committee")
        print()
        print()
        f = open("./conf/comitteeNodes.json", "r")
        print("ORIGINATOR", originator)
        print("RECEIVED CID: ", CID)
        raw_list = f.read()
        f.close()
        server = originator
        committee_members=json.loads(raw_list)
        print("COMMITTEE MEMBERS: ", committee_members)
        for member in committee_members["members"]:
            print("CHECKING MEMBER ", member["address"],originator)
            if member["address"]==originator:
                addr=member["server"].split(',')
                server=(str(addr[0]), int(addr[1].replace('\n','')))
                
        s=None
        success=False
        print("SERVER: ", server)
        s=socket.socket()
        s.settimeout(15)
        s.connect(server)
        try:
            message='4re'
            print()
            print("SENDING ", message)
            s.send(message.encode('UTF-8'))
            print("GETTING DATA")
            data = s.recv(10) 
            print("GOT " + str(data.decode()))
            if data.decode('utf-8') =="ACK----4re":
                print("RECIEVED ACK MESSAGE")
                message=str(CID).encode("utf-8")
                print("SENDING CID", message)
                s.send(message)
                print("WAITING TO RECEIVE RESPONSE")
                data=s.recv(10)
                print("RECEIVED " + str(data.decode()))
                if data.decode('utf-8')=="ACK---DONE":
                    success=True
                    s.close()
                    print("CLOSING CONNECTION FROM SUCCESS")
                else:
                    print("UNEXPECTED FINAL MESSAGE. CLOSING CONNECTION")
                    s.close()
        except:
            print("THE SERVER "+ str(server) + " IS DOWN")
            success=False
            s.close()
            print("CLOSING CONNECTION FROM FAILURE")
        
        return success	

    def __validate_vote(self,vote):
        valid_member = False
        print("VOTE:", vote)
        ref_block : Block = block.create_block_from_CID(self.ipfsAPIInstance, vote["Vote"]["block_id"])
        if ref_block == None:
            return False
        if vote["Vote"]["block_height"] != ref_block.get_block_height():
            return False
        if vote["Vote"]["vote"] not in ["Accept", "Reject", "Disconnected"]:
            return False
        
        f = open("conf/comitteeNodes.json","r")
        file_content = f.read()
        committee_json = json.loads(file_content)
        for member in committee_json["members"]:
            if vote["Vote"]["member"] == member["address"]:
                valid_member = True
        
        if valid_member:
            if vote["Vote"]["member"] in self.__received_voters:
                return False

            ### CHECK SIGNATURE
            content = json.dumps(vote)

            ### SPECIAL CASE:  IF VOTE WAS DISCONNECTED SIGNATURE SHOULD BE FROM THE MINER
            if vote["Vote"]["vote"] == "Disconnected":
                public_key_content = self.ipfsAPIInstance.getContent(self.address, "PK")
            else:
                public_key_content = self.ipfsAPIInstance.getContent(str(vote["Vote"]["member"]),"PK")
            
            public_key = base64.decodebytes(public_key_content)
            try:
                signature = bytes.fromhex(vote["Signature"])
                content=content.encode('utf-8')
                verify(public_key, content, signature)

                return True
            except:
                print("SIGNATURE VALIDATION FAILURE")
                return False
                
    def store_vote(self,vote,addr):
        print()
        print()
        print("IN STORE VOTE")
        print("vote: ", vote)
        print("ADDRESS", addr)
        print()
        print()

        if str(addr) in self.__collectedVotes:
            pass
        else:
            stored_vote = {}
            stored_vote["vote"] = vote
            stored_vote["status"] = "new"
            self.__collectedVotes[str(addr)] = stored_vote 
            self.__collected_vote_count = self.__collected_vote_count  + 1
            print("END RESULTS: ", self.__collectedVotes)
               
    def collect_vote(self, vote, addr):
        print("COLLECTING VOTES ", vote, addr)
    
        if self.__collectedVotes[str(addr)]["status"] == "new":
        
            try:
                vote_content = self.ipfsAPIInstance.getContent(vote,"NA")
                v = json.loads(vote_content)
                if v["Vote"]["member"] in self.__received_voters:
                    pass
                else:
                    if self.__validate_vote(v):
                        self.votes.append(vote)
                        self.__received_voters.append(v["Vote"]["member"])
                        self.__collectedVotes[str(vote)]["status"] = "processed"
                    else:
                        self.__collectedVotes[str(vote)]["status"] = "invalid"
            except:
                print("ERROR", vote)
        self.__process_votes()

    def __process_votes(self):
        print("LOG IN PROCESSING VOTES")
        if len(self.votes) == 3:
            if self.result =="Accept":
                pass
            elif self.result =="Reject":
                pass
            elif self.result =="Disconnected":
                pass
            else:    
                print("3 VOTES RECIEVED")
            #    print("FIRST VOTE: ", self.votes[0])
                first_vote_content = self.ipfsAPIInstance.getContent(self.votes[0],"NA")
           #     print()
                
          #      print("FIRST VOTE CONTENT: ")
          #      print(first_vote_content)
                vote = json.loads(first_vote_content)
                block_height = vote["Vote"]["block_height"]
                block_ID = vote["Vote"]["block_id"]
           #     print()
                print("LOG  CREATING VALIDATION BLOCK")
                validation_block = ValidationBlock(time.time(), block_height, self.address, block_ID)      
                print() 
          #      print("DONE CREATING VALIDATION BLOCK TEMPLATE", validation_block.get_votes())  
                print()
                print(validation_block.get_data())   
                print()
                accept_count = 0
                reject_count = 0
                disconnect_count = 0
                print()
                print("LOG ITERATING THROUGH VOTES")
                for v in self.votes:    
                    print("GETTING VOTE ",v)
                    vote_content = self.ipfsAPIInstance.getContent(v,"NA")
                    vote = json.loads(vote_content)
                    print("VOTE CONTENT: ", vote)
                    print("ADDING VOTE")
                    validation_block.add_vote(vote["Vote"]["member"], v, self.ipfsAPIInstance, validation_block.get_block_height())
                    print()

                    if vote["Vote"]["vote"] == "Accept":
                        accept_count = accept_count + 1
                    elif vote["Vote"]["vote"]== "Reject":
                        reject_count = reject_count + 1
                    elif vote["Vote"]["vote"] == "Disconnected":
                        disconnect_count = disconnect_count + 1
                print("LOG DETERMINING VOTE STATUS")
                if accept_count > reject_count + disconnect_count:
                    self.result = "Accept"
                elif reject_count > accept_count + disconnect_count:
                    self.result = "Reject"
                else:
                    self.result = "Fault"
                print()
                print("*************************")
                print("VOTE: STATUS", self.result)
                print()
          #      print("LOG  PREPARING TO SIGN VALIDATION BLOCK", validation_block.get_status())
    
                self.__validation_block_CID = validation_block.sign(self.address, self.__privKey,self. ipfsAPIInstance)
           #     print("VALIDATION CID = " , self.__validation_block_CID)
                ## TODO: Create MetaBlock
        else:
            print("NOT ENOUGH VOTES YET")


    def send_to_committee_member(self,member,bkCID):
        print("IN TO SEND TO COMMITTEE MEMBER")
        success = False
        addr=member["server"].split(',')
        server=(str(addr[0]), int(addr[1].replace('\n','')))
        s=socket.socket()
        s.settimeout(15)
        print("trying to connect to server",server)
        try:
            s.connect(server)

            message='4vb'
            try:
                print("SENDING ", message)
                s.send(message.encode('UTF-8')) 
                print("GETTING DATA")
                data = s.recv(10) 
                print("GOT " + str(data.decode()))
                if data.decode('utf-8') =="ACK----4vb":
                    print("RECIEVED ACK MESSAGE")
                    message=str(self.address).encode("utf-8")
                    print("SENDING ADDRESS ", message)
                    s.send(message)
                    print("WAITING TO RECEIVE RESPONSE")
                    data=s.recv(10)
                    print("RECEIVED " + str(data.decode()))
                    if data.decode('utf-8')=="ACK---ADDR":
                            
                        print("RECIEVED ACK ADDRRESS")
                        message=str(bkCID).encode("utf-8")
                        print("SENDING BLOCK ID", message)
                        s.send(message)
                        print("WAITING TO RECEIVE RESPONSE")
                        data=s.recv(10)
                        print("RECEIVED " + str(data.decode()))
                        if data.decode('utf-8')=="ACK---DONE":
                            success=True
                            
                            s.close()
                            print("CLOSING CONNECTION FROM SUCCESS")
                            return success
                            
                        else:
                            print("UNEXPECTED FINAL MESSAGE. CLOSING CONNECTION")
                            s.close()
            except:
                print("ERROR SENDING DATA")
                success = False
                return success
        except:
            print("CONNECTION FAILED")
            print("THE SERVER "+ str(server) + " IS DOWN")
            success=False
            
            s.close()
            return success
        
            print("CLOSING CONNECTION FROM FAILURE")
        print("RETURNING: ",success)
        return success

    def sendToCommittee(self,bkCID):
        print()
        print()
        print()
        print("SENDING TO COMMITTEE:  ", bkCID)
        self.votes=[]
        self.__received_voters = []
        self.votes.append(self.__create_my_vote(bkCID))
        self.store_vote(self.votes[0],self.address)
        self.__collected_vote_count = 1
        
        res = []
        members = []
        print("SENDING BLOCK TO COMITTEE", bkCID)
    #    s=None
    #    success=False
        f = open("./conf/comitteeNodes.json", "r")
        raw_list = f.read()
        f.close()
        committee_members=json.loads(raw_list)
     #   print("COMMITTEE MEMBERS: ", committee_members)
        for member in committee_members["members"]:
            print("MEMBER ", member)
            res.append(False)
            members.append(member)
        res[self.id]=True
        print("RES: ", res)
  #      print("MEMBERS: ", members)
        count = 0
        should_continue = True
    
       
        
        for i in range(0,len(res)):
            print("MEMBER ",i , members[i])
            should_continue = True
            count =0 
            while should_continue:
                self.__process_votes()
                time.sleep(2)
                print("RES: ", res[i])
                if res[i] !=True:
                    if members[i]["address"] != self.address:
                        print(" TRYING TO GET RESPONSE FROM ",members[i] )
                        res[i]=self.send_to_committee_member(members[i],bkCID)
                        should_continue = True
                        if count == 7:
                            print()
                            print()
                            print("MAX ATTEMPT COUNT RECIEVED")
                            print("APPENDING DISCONNECTED VOTE")
                            vote_CID = self.__create_disconnect_vote(members[i]["address"],bkCID)
                            self.__collected_vote_count = 1
                            self.store_vote(vote_CID, members[i]["address"])
                            self.votes.append(vote_CID)
                            print("LOG:  DONE APPENDING VOTE", vote_CID)
                            print("LOG: PROCESSING VOTES")
                            should_continue = False
                            self.__process_votes()
                            
                    count = count +1
                else:
                    should_continue = False
                    self.__process_votes()
                    
            
    def __create_my_vote(self, block_ID):
        vote = {}
        block_data : Block = block.create_block_from_CID(self.ipfsAPIInstance, block_ID)
        vote["block_height"] = block_data.get_block_height()
        vote["block_id"] = block_ID
        vote["vote"] = "Accept"
        vote["member"] = str(self.address)
        content = json.dumps(vote)
        print("MY VOTE CONTENT:  ", content)
        vote_CID = self.sign_vote(content)
        return vote_CID

    def __create_disconnect_vote(self, address, block_ID):
        vote = {}
        print()
        print("LOG:   CREATING BLOCK FROM CREATE DISCONECT VOTE")
        block_data : Block = block.create_block_from_CID(self.ipfsAPIInstance, block_ID)
        print()
        print("LOG:    DONE CREATING BLOCK FROM CID IN CREATE DISCONNECT VOTE")

        print()
        print("LOG:   ADDING VOTE VALUES")
        vote["block_height"] = block_data.get_block_height()
        vote["block_id"] = block_ID
        vote["vote"] = "Disconnected"
        vote["member"] = str(address)

        content = json.dumps(vote)

        print()
    #    print("LOG:    VOTE CONTENT: ", content)

        print()
        print("SIGNING VOTE: ")
        vote_CID = self.sign_vote(content)
        print("RETURNING VOTE CID ", vote_CID)
        return vote_CID

    def sendBKToChain(self,bkCID):
    
       
        print("SENDING BLOCK", bkCID)

        s=None
        success=False
        f = open("./conf/nodes.conf", "r")
        content_list = f.readline()
        print("CONTENT_LIST",content_list)
        f.close()
        addr=content_list.split(',')
        server=(str(addr[0]), int(addr[1].replace('\n','')))
        s=socket.socket()
        s.settimeout(15)
        print("trying to connect to server",server)
        try:
            s.connect(server)
        except:
            print("CONNECTION FAILED")
        message='3bk'
        try:
            print("SENDING ", message)
            s.send(message.encode('UTF-8')) 
            print("GETTING DATA")
            data = s.recv(10) 
            print("GOT " + str(data.decode()))
            if data.decode('utf-8') =="ACK----3bk":
                print("RECIEVED ACK MESSAGE")
                message=str(bkCID).encode("utf-8")
                print("SENDING BLOCK ID", message)
                s.send(message)
                print("WAITING TO RECEIVE RESPONSE")
                data=s.recv(10)
                print("RECEIVED " + str(data.decode()))
                if data.decode('utf-8')=="ACK---DONE":
                    success=True
                    s.close()
                    print("CLOSING CONNECTION FROM SUCCESS")
                else:
                    print("UNEXPECTED FINAL MESSAGE. CLOSING CONNECTION")
                    s.close()
        except:
            print("THE SERVER "+ str(server) + " IS DOWN")
            success=False
            s.close()
            print("CLOSING CONNECTION FROM FAILURE")
        
        return success	

    def get_block(self,cid):
        print("GETTING BLOCK DATA: ", cid)
        blockContent= self.ipfsAPIInstance.getContent(cid, "BK")
        return blockContent

    def get_full_block(self,cid):
        proposed_block : Block = block.create_block_from_CID(self.ipfsAPIInstance, cid)
        return proposed_block
    
    def get_validation_block(self,cid):
        validation_block : ValidationBlock = block.create_validationblock_from_CID(self.ipfsAPIInstance, cid)
        return validation_block
    
    def get_block_height(self,cid):
        proposed_block : Block = block.create_block_from_CID(self.ipfsAPIInstance, cid)
        return proposed_block.get_block_height() 
    

    def add_block_mined_by_other(self, BlockCID):
                
        if BlockCID not in self.__blockChain:
            meta_block : MetaBlock = block.create_metablock_from_CID(self.ipfsAPIInstance, BlockCID)
            self.__blockChain.append(BlockCID)
            self.__blocks[BlockCID] = {"Height": (len(self.__blockChain)-1), "Validation" : meta_block.get_validation_ID(), "Block" : meta_block.get_refrence_block_ID()}
            self.writeToDisk()
        self.sendBKToChain(BlockCID)


    def add_other_block(self,CID):
        f=open("blocklog.txt","r")
        lines = f.readlines()
        print(CID)
        print(lines)
        f.close()
        if CID in lines:
            pass
        else:
            meta_block : MetaBlock = block.create_metablock_from_CID(CID)
            valid_meta = meta_block.validate_block(self.ipfsAPIInstance)
            validation_block : ValidationBlock = block.create_validationblock_from_CID(meta_block.get_validation_ID())
            valid_validation = validation_block.validate_block_sync() and validation_block.validate_block(self.ipfsAPIInstance)
            ref_block : Block = block.create_block_from_CID(meta_block.get_refrence_block_ID())
            valid_ref_block = ref_block.validate_block()
            if valid_meta & valid_validation & valid_ref_block:
                if CID not in self.__blockChain:
                    self.__blockChain.append(CID)
                    self.__blocks[CID] = {"Height": (len(self.__blockChain)-1), "Validation" : meta_block.get_validation_ID(), "Block" : meta_block.get_refrence_block_ID()}
                    self.writeToDisk()
                    self.sendBKToChain(CID)

   
    def mine(self,null_block=False):
        self.__validation_block_CID = ""
        self.votes = []
        self.__received_voters = []
        self.__collectedVotes = {}
        self.__collected_vote_count = 0

        self.result="PENDING"
        self.addNewTXToPending()
        
        print()
        print("GETTING PENDINGN TRANSACTIONS.. SLEEPING TO MAKE IT EASY TO READ")
        time.sleep(10)
        print()
        print()
        print("PENDING TRANSACTIONS:  ", self.__pendingTX)
        print()
        print()
        time.sleep(10)
        blockData = getLastBlockData()
        print("CREATING NEW BLOCK")
        f=open("MinerFiles/minerList.txt","r")
        miners=f.readlines()
        f.close()
        
        if null_block == False:
                
            tempTxList=self.txList()
            ### ADD COINBASE TO TRANSACTIONS:
            print("ADDING COINBASE")
            print(self.__blockChain)
            coinbase=transaction.createCoinbaseTX(self.address,len(self.__blockChain))
            coinbaseCID=coinbase.sign(self.__privKey,self.ipfsAPIInstance)
            tempTxList.insert(0,coinbaseCID)
            self.__pendingTX[coinbaseCID]="na"          
            
            expected_miner_index=(blockData["Data"]["Height"]+1) % (len(miners))
            expectedMiner = miners[expected_miner_index]
            print("EXPECTED MINER: ", expectedMiner)
            print()
            time.sleep(5)

            print()
            print("LAST BLOCK: ", self.__blockChain[-1])

         #   meta_block : MetaBlock = block.create_metablock_from_CID(self.ipfsAPIInstance, self.__blockChain[-1])
            newBlock = block.createFromPreviousBlock(self.__blockChain[-1], tempTxList,self.address, self.ipfsAPIInstance,expectedMiner)

           
            ### UPDATE TX THAT ARE PENDING
        else:
            expected_miner_index=(blockData["Data"]["Height"]+2) % (len(miners))
            expectedMiner = miners[expected_miner_index]
            print("EXPECTED MINER (OVERRIDE): ", expectedMiner)
            newBlock :Block = block.create_null_from_previous_block(self.__blockChain[-1], self.address,self.ipfsAPIInstance,expectedMiner)
        
        blockCID = newBlock.sign(self.__privKey, self.ipfsAPIInstance)

        ## CREATE VALIDATION BLOCK 
        validation_block = ValidationBlock(time.time(), newBlock.get_block_height(), self.address, blockCID, self.ipfsAPIInstance)
        print()
        print()
        print("GETTING READY TO SEND TO COMMITTEE")
        print()
        print()
        self.sendToCommittee(blockCID)

        while len(self.__collectedVotes) < 3:
            print("Waiting on status from committee")
            print(self.__collectedVotes)
            time.sleep(2)

        print()
        print()
        print("COLLECTED VOTES RECIEVED")
        print("CHECKING VOTES")

        print(self.__collectedVotes)
    
        for v in self.__collectedVotes:
            self.collect_vote(self.__collectedVotes[v]["vote"], v)
        print()
        print("VALIDATION BLOCK", self.__validation_block_CID, self.result)

            
        validation_block : ValidationBlock = block.create_validationblock_from_CID(self.ipfsAPIInstance, self.__validation_block_CID)
        validation_block.finalize()
        validation_CID = validation_block.sign(self.address, self.__privKey, self.ipfsAPIInstance)

        print("VALIDATION BLOCK done")

        print("PREVIOUS META: ", newBlock.get_previous_meta_ID())


        previous_meta_block : MetaBlock = block.create_metablock_from_CID(self.ipfsAPIInstance, newBlock.get_previous_meta_ID())
        updated_block : Block = block.create_block_from_CID(self.ipfsAPIInstance, blockCID)
        previous_account_state = previous_meta_block.get_account_state_CID()
        previous_reward_state = previous_meta_block.get_reward_state_CID()
        print("Previous States", previous_account_state, previous_reward_state)

      
        ### CHECK IF NEW COMMITTEE NEEDED:
        ### NEW COMMITTEE WHEN block height mod 10 = 0
        if (previous_meta_block.get_block_height() +1) % 10 ==0:
            ### NEW COMMITTEE NEEDED
            ### PLACEHOLODER SET TO CURRENT COMMITTEE FOR NOW
            committee = previous_meta_block.get_committee()
        else:
            ### USE SAME COMMITTEE
            committee = previous_meta_block.get_committee()
            
        meta_block = MetaBlock(time.time(), newBlock.get_block_height(), self.address, blockCID, validation_CID, newBlock.get_previous_meta_ID(), newBlock.get_previous_hash(), previous_meta_block.get_validation_ID(),previous_account_state, previous_reward_state, self.ipfsAPIInstance, committee) 
        meta_block.update_states(self.ipfsAPIInstance)
        
       # validation_block :ValidationBlock = block.create_validationblock_from_CID(self.ipfsAPIInstance, meta_block.get_validation_ID())
        #validation_block.finalize()
        
        meta_CID = meta_block.sign(self.address, self.__privKey, self.ipfsAPIInstance)
  #      block_ref :Block = block.create_block_from_CID(self.ipfsAPIInstance, meta_block.get_refrence_block_ID())
    #    block_ref.writeBlock(self.ipfsAPIInstance)
       
        print("META_CID", meta_CID)
        if validation_block.get_status() == "Accept":
            print("BLOCK STATE WAS ACCEPT")
            for tx in newBlock.get_transactions():
                self.__pendingTX.pop(tx)
                self.__addedTX[tx]=meta_CID

            
        
        else:   
            print("BLOCK STATE WAS NOT ACCEPT")
        print("WRITING TO DISK")
        self.__myBlocks.append(meta_CID)
        self.__blockChain.append(meta_CID)
        self.__blocks[blockCID]={"Height": meta_block.get_block_height(),"Validation" : meta_block.get_validation_ID(), "Block": meta_block.get_refrence_block_ID()}
        self.__meta_blocks[meta_CID] = meta_block.get_block_height()
        print("MY BLOCKS: ", self.__myBlocks)
        print("BLOCKCHAIN" , self.__blockChain)
        print("BLOCKS: ", self.__blocks)
        print("META_BLOCKS" , self.__meta_blocks)
        self.writeToDisk()
       
        
        print("SENDING META BLOCK")
        self.sendBKToChain(meta_CID)
        print("DONE")
        self.votes=[]

global lock
lock = threading.Lock()
