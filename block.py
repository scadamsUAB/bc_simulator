from curses import meta
import hashlib
from importlib.metadata import metadata
import json
import base64
from logging.config import valid_ident
import os
import os.path
from os import path, write
from pathlib import Path
#from Miner import miner
import transaction
from pqcrypto.sign.falcon_512 import sign, verify
import time

def create_metablock_from_CID(IPFS_API_instance, CID):

    blockRaw = IPFS_API_instance.getContent(CID,"BK")
    blockData = json.loads(blockRaw)
    print("META BLOCK DATA ")
    print(blockData)
    metablock = MetaBlock(blockData["Data"]["Timestamp"], blockData["Data"]["Height"], blockData["Data"]["Miner"], blockData["Data"]["BlockRef"], blockData["Data"]["ValidationRef"], blockData["Data"]["PreviousMetaBlock"], blockData["Data"]["PreviousBlock"], blockData["Data"]["PreviousValidation"], blockData["Data"]["AccountState"], blockData["Data"]["RewardState"], IPFS_API_instance, blockData["Data"]["CommitteeID"], blockData["Signature"])        
    
    print()
    print()
    print(metablock.block)
    metablock.block = blockData
    if metablock.validate_signature(IPFS_API_instance):
        print("VALID SIGNATURE")
        ## CHECK IF NEW CID MATCHES EXISTING CID PASSED IN
        new_CID=metablock.writeBlock(IPFS_API_instance)
        print("NEW CID", new_CID)
        if new_CID == CID :
            print("CID MATCH")
            return metablock
    return None

def create_validationblock_from_CID(IPFS_API_instance, CID):
    print()
    print("LOG CREATING VALIDATION BLOCK FROM CID", CID)
    blockRaw = IPFS_API_instance.getContent(CID,"BK")
    blockData = json.loads(blockRaw)
    
    validationBlock =  ValidationBlock(blockData["Data"]["Timestamp"], blockData["Data"]["Height"],blockData["Data"]["Miner"],blockData["Data"]["Block"], blockData["Signature"], blockData["Data"]["Votes"], blockData["Data"]["Status"])
    validationBlock.status = blockData["Data"]["Status"]
    validationBlock.add_votes_CID_creation(IPFS_API_instance,   validationBlock.get_block_height(),validationBlock.get_block_ref())
    if validationBlock.validate_signature(IPFS_API_instance):
        return validationBlock
    return None


def create_block_from_CID(IPFS_API_instance, CID):
    print()
    print("IN CREATE BLOCK FROM CID")
    print("CID: ", CID)
    try:
        blockRaw=IPFS_API_instance.getContent(CID,"BK")
        blockData=json.loads(blockRaw)
    #   print("BLOCK DATA ")
    #    print(blockData)
        block : Block  = Block(blockData["Body"]["Transactions"], blockData["Header"]["Height"], blockData["Header"]["PreviousBlock"], blockData["Header"]["PreviousMetaID"], blockData["Header"]["Timestamp"], blockData["Header"]["Miner"], IPFS_API_instance, blockData["Header"]["AccountStateHash"],blockData["Body"]["Signature"], False)
        if block.validate_signature(IPFS_API_instance):
            return block
        return None
    except:
        print("ERROR CREATING BLOCK FROM CID: ", CID)
        return None
        

def getLatestHeight():
    latestblockHeight=-1
    for root, dirs, files in os.walk("./Blocks/", topdown=False):
        for name in files:
            f=open(os.path.join(root, name))
            block=json.load(f)
            f.close()
            blockHeight=block["Header"]["Height"]
            if blockHeight > latestblockHeight:
                latestblockHeight=blockHeight
                latestHash=name[:-5]
    return latestHash


def retrieveAccountStateFromIPFS(ipfsAPIInstance,CID):
    blockRaw=ipfsAPIInstance.getContent(CID,"BK")
    blockData=json.loads(blockRaw)
    return blockData["Body"]["AccountState"]

def validate_block_signature(block, ipfsInstance):
    miner = block["Header"]["Miner"]
    pubKeyContent = ipfsInstance.getContent(str(miner),"PK")
    publicKey=base64.decodebytes(pubKeyContent)
    content = block["Header"]
    try:
        signature=bytes.fromhex(block["Body"]["Signature"])
        content=content.encode('utf-8')
        verify(publicKey,content, signature)

        return True
    except:
        print("SIGNATURE VALIDATION FAILURE")
        return False

def validate_validation_block_signature(block,IPFS_API_instance):
    miner = block["Data"]["Miner"]
    public_key_content = IPFS_API_instance.getContent(str(miner),"PK")
    public_key=base64.decodebytes(public_key_content)
    content = block["Data"]
    try:
        signature=bytes.fromhex(block["Signature"])
        content=content.encode('utf-8')
        verify(public_key,content, signature)
        return True
    except:
        print("SIGNATURE VALIDATION FAILURE")
        return False

def createFromPreviousBlock(prevBlockhash, transactions_in, miner, ipfsAPIInstance, previous_expected_miner):
    print ("    IN CREATE FROM PREVIOUS BLOCK ")
    meta_block : MetaBlock  = create_metablock_from_CID(ipfsAPIInstance, prevBlockhash)
    print("META BLOCK CREATED ")
    previous_block : Block = create_block_from_CID(ipfsAPIInstance, meta_block.get_refrence_block_ID() )
    print("PREVIOUS BLOCK CREATED ")
    #print("PREVIOUS ACCOUNT STATE ID: ",meta_block.get_account_state_CID() )
    newBlock = Block(transactions_in, previous_block.get_block_height() +1, meta_block.get_refrence_block_ID(), prevBlockhash, time.time(), miner, ipfsAPIInstance, meta_block.get_account_state_CID())

    return newBlock

def create_null_from_previous_block(prevBlockhash,miner,ipfsAPIInstance,previous_expected_miner):
    tx = []
    meta_block : MetaBlock  = create_metablock_from_CID(ipfsAPIInstance, prevBlockhash)
    previous_block : Block = create_block_from_CID(ipfsAPIInstance, meta_block.get_refrence_block_ID() )
    newBlock = Block(tx, previous_block.get_block_height() +1, meta_block.get_refrence_block_ID(), prevBlockhash, time.time(), miner, ipfsAPIInstance,previous_block.get_account_state_ID())
    newBlock.null_block(ipfsAPIInstance)
 
       
    try:
        newBlock.accountState=json.loads(previous_block.get_account_state_ID())
    except:
        print("ERROR LOADING ACCOUNT STATE")
        newBlock.accountState=previous_block.get_account_state_ID()

    return newBlock

class ValidationBlock():
    def __init__(self, timestamp, height, miner_id, block_ref, signature = "", votes = None, status = "Pending"):
        self.__block_height=height
        self.__miner = miner_id
        self.__block_ref = block_ref
        self.__timestamp = timestamp
        if votes == None:
            self.__votes = {}
        else:
            self.__votes = votes
        self.__vote_count = 0
        self.__accept_votes = 0
        self.__reject_votes = 0
        self.__disconnected_votes = 0
        self.__status = status
        self.__data = {"Timestamp": self.__timestamp, "Height": self.__block_height, "Miner": self.__miner, "Block": self.__block_ref, "Status": self.__status, "Votes": self.__votes } 
        self.__signature = signature
        self.block={}

    def writeBlock(self,IPFS_API_instance):
        print("IN VALIDATION BLOCK WRITE BLOCK")
        self.block = {"Data":  self.__data, "Signature": self.__signature } 
        content = json.dumps(self.block)
      #  print("CONTENT" , content)
        CID = IPFS_API_instance.addfile(content,"BK")
        f = open("Blocks/Temp/"+str(CID)+".json","w")
        f.write(content)
        f.close()

        f = open("Blocks/"+str(CID)+".json","w")
        f.write(content)
        f.close()
        return str(CID)
    
    def get_block_height(self):
        return self.__block_height

    def get_block_ref(self):
        return self.__block_ref
    
    def get_timestamp(self):
        return self.__timestamp
    
    def get_votes(self):
        return self.__votes

    def get_miner(self):
        return self.__miner

    def get_signature(self):
        return self.__signature
        
    def get_data(self):
        return self.__data

    def get_status(self):
        return self.__status

    def validate_block_sync(self):
        block : Block = create_block_from_CID(self.__block_ref)
        height_match = block.get_block_height() == self.__block_height
        miner_match = block.get_miner() == self.__miner
        committee_member = False
        ## CHECK MINER IS IN COMMITTEE
        f = open("./conf/comitteeNodes.json", "r")
        raw_list = f.read()
        f.close()
        json_list = json.loads(raw_list)
        for v in json_list["members"]:
            if block.get_miner() in v["address"]:
                committee_member = True
        return height_match and miner_match and committee_member

    def add_votes_CID_creation(self, IPFS_API_instance, block_number, block_ID):
        self.__vote_count = len(self.__votes)
        for v in self.__votes:

            vote_content = IPFS_API_instance.getContent(self.__votes[v], "NA")
            vote = json.loads(vote_content)
     #       print("Vote",vote)

            if self.validate_vote(self.__votes[v],vote["Vote"]["member"],IPFS_API_instance, block_number, block_ID):
                if vote["Vote"]["vote"] == "Accept":
                    self.__accept_votes = self.__accept_votes +1
                else:
                    self.__reject_votes == self.__reject_votes

    def add_vote(self, sender_address, vote_CID, IPFS_API_instance, block_number):
        ## CHECK IF VOTE ALREADY RECEIVED
        if sender_address in self.__votes:
            print("SENDER ALREADY SUPPLIED VOITE")
            print("CURRENT VOTES: ", self.__accept_votes, self.__reject_votes, self.__disconnected_votes, self.__vote_count, self.__votes)
            pass
        else:
            vote_content = IPFS_API_instance.getContent(vote_CID, "NA")
            vote = json.loads(vote_content)
            #validate_vote(self, vote_CID, sender_address, IPFS_API_instance, block_number, block_ID):
            if self.validate_vote(vote_CID, sender_address, IPFS_API_instance, block_number, vote["Vote"]["block_id"]):
                print("VOTE IS VALID")
                if vote["Vote"]["vote"] == "Accept":
                    self.__accept_votes = self.__accept_votes +1
                elif vote["Vote"]["vote"] =="Reject":
                    self.__reject_votes == self.__reject_votes +1
                elif vote["Vote"]["vote"] == "Disconnected":
                    self.__disconnected_votes = self.__disconnected_votes + 1
                self.__votes[sender_address] = vote_CID
                self.__vote_count = self.__vote_count + 1
              
            else:
                print("INVALID VOTE")
        self.update_status()
        self.finalize()

    def validate_block(self, IPFS_API_instance):
        if self.__status =="Pending":
            return False
        if self.__status in ["Accept", "Reject", "Fault"]:
            valid_votes = True
            for vote in self.__votes:
                vote_content = IPFS_API_instance.getContent(vote, "NA")
                vote = json.loads(vote_content)
                valid_votes = valid_votes & self.validate_vote(vote, vote["Vote"]["member"], IPFS_API_instance, self.__block_height, self.__block_ref)            

            block_ref : Block = create_block_from_CID(self.__block_ref)
            if block_ref.get_block_height != self.__block_height:
                return False
            if block_ref.get_miner() != self.__miner:
                return False
            if block_ref.get_timestamp >= self.__timestamp:
                return False
            if self.validate_signature(IPFS_API_instance) == False:
                return False
            return valid_votes        
        else:
            return False

    def validate_vote(self, vote_CID, sender_address, IPFS_API_instance, block_number, block_ID):
        vote_content = IPFS_API_instance.getContent(vote_CID, "NA")
        vote = json.loads(vote_content)

        if vote["Vote"]["member"] == sender_address and vote["Vote"]["block_height"] == block_number and vote["Vote"]["block_id"] == block_ID:
            print("VOTE REQUIREMENTS MET")
        ## IF THE VOTE IS A DISCONNECTED VOTE VALIDATE SIGNATURE USING MINER PUBLIC KEY
            if vote["Vote"]["vote"]=="Disconnected":
                print("DISCONNECTED VOTE... USING MINER PUBLIC KEY", self.__miner)
                pub_key = IPFS_API_instance.getContent(self.__miner,"PK")
            else:
                print("REGULAR VOTE... USING SENDER  KEY",sender_address)
                pub_key = IPFS_API_instance.getContent(sender_address,"PK")
            signature = vote["Signature"]    
            signature=bytes.fromhex(signature)
            public_key=base64.decodebytes(pub_key)
            content = vote["Vote"]
            message = json.dumps(content)
 #           print("VALIDATING MESSAGE:", message)
 #           print("SIGATURE: ", signature)
            message_bytes=message.encode('utf-8')

            try:
                verify(public_key,message_bytes, signature)
                if vote["Vote"]["vote"] == "Accept":
                    return True
                if vote["Vote"]["vote"]=="Reject":
                    return True
                if vote["Vote"]["vote"] == "Disconnected":
                    return True
                return False
                  
            except:
                print("VERIFY ERROR")
                return False
    
    def validate_signature(self, IPFS_API_instance):
        valid_signature=False
        try:
            signature=bytes.fromhex(self.__signature)
            content=json.dumps(self.__data)
            content=content.encode('utf-8')
            public_key_content= IPFS_API_instance.getContent(self.__miner, "PK")
            public_key=base64.decodebytes(public_key_content)
            verify(public_key,content, signature)
            valid_signature=True
        except:
            print("SIGNATURE VALIDATION FAILURE")
            valid_signature=False
        return valid_signature  
                      
    def sign(self, signer, private_key, IPFS_API_instance):
        print("LOG   IN VALIDATION BLOCK SIGN")
        print("CREATING REFERENCE BLOCK INSTANCE")
        reference_block = create_block_from_CID(IPFS_API_instance, self.__block_ref)
        print()
        print("LOG DONE CREATING REFERENCE BLOCK")
        if signer == reference_block.get_miner():
  #          print("SIGNER" , signer)
            signature_tester = "test value"
            signature_tester = signature_tester.encode('utf-8')
            signature = sign(private_key, signature_tester)
            signature = signature.hex()
            
            ## CHECK THE TEST VALUE SIGNATURE CAN BE VALIDATED WITH THE PUBLIC KEY OF THE MINER OF THE REFERENCE BLOCK
            valid_signature = False
            try:
                print()
                print("VALIDATING TEST SIGNATURE")
                signature = bytes.fromhex(signature)
                pubKeyContent= IPFS_API_instance.getContent(signer, "PK")
                publicKey=base64.decodebytes(pubKeyContent)
                verify(publicKey, signature_tester, signature)
                valid_signature = True
            except:
                print("SIGNATURE VALIDATION FAILURE")
                valid_signature = False

            if valid_signature:
                message = json.dumps(self.__data)
                message = message.encode('utf-8')
                signature = sign(private_key, message)
                self.__signature = signature.hex()
                CID = self.writeBlock(IPFS_API_instance)
                return CID
                
    def update_status(self):
        print("IN UPDATING STATUS")
        if self.__vote_count <3 :
            print("STILL PENDING ")
            self.__status = "Pending"
        else:

            if self.__accept_votes > self.__reject_votes + self.__disconnected_votes:
                print("STATUS ACCEPT")
                self.__status = "Accept"
            elif self.__reject_votes > self.__accept_votes + self.__disconnected_votes:
                print("STATUS REJECT")
                self.__status = "Reject"
            else:
                print("FAULTY STATUS", self.__status, self.__accept_votes, self.__accept_votes, self.__reject_votes)
                self.__status = "Fault"


    def finalize(self):
        print("IN FINALIZE VOTES")
        if self.__status == "Pending": 
            print("STATUS STILL PENDING")
            pass
        else:
            print("STATUS IS NOT PENDING: ", self.__status)
            self.__data={"Timestamp": self.__timestamp, "Height": self.__block_height,"Miner": self.__miner, "Block": self.__block_ref, "Status": self.__status, "Votes": self.__votes} 
        

class MetaBlock():
    def __init__(self, timestamp, height, miner_id, block_ref, validation_ref, previous_meta_block, previous_block, previous_validation, account_state, reward_state, IPFS_API_instance, committee, signature = "" ):
        self.__block_height = height 
        self.__previous_meta_hash = previous_meta_block
        self.__previous_block_hash = previous_block
        self.__previous_validation_hash = previous_validation
        self.__block_hash = block_ref
        self.__validation_hash = validation_ref
        self.__timestamp = timestamp
        self.__miner = miner_id
        self.__accountState_CID = account_state
        self.__rewardState_CID = reward_state
        self.__accountState = {}
        self.__set_account_state_from_CID(self.__accountState_CID, IPFS_API_instance)
        self.__rewardState = {}
        self.__set_reward_state_from_CID(self.__rewardState_CID, IPFS_API_instance)
        self.__committee = committee
        self.__data = {"Timestamp": self.__timestamp, "Height":self.__block_height, "Miner":self.__miner, "BlockRef":self.__block_hash, "ValidationRef":self.__validation_hash, "PreviousMetaBlock" :self.__previous_meta_hash, "PreviousBlock":self.__previous_block_hash, "PreviousValidation":self.__previous_validation_hash, "AccountState": self.__accountState_CID, "RewardState": self.__rewardState_CID,"CommitteeID":self.__committee}
        self.__signature = signature
        self.block = {"Data": self.__data, "Signature": self.__signature}
    
    def get_block_height(self):
        return self.__block_height
    
    def get_previous_meta_ID(self):
        return self.__previous_meta_hash
    
    def get_previous_block_ID(self):
        return self.__previous_block_hash
    
    def get_previous_validation_ID(self):
        return self.__previous_validation_hash
    
    def get_refrence_block_ID(self):
        return self.__block_hash
    
    def get_validation_ID(self):
        return self.__validation_hash
    
    def get_timestamp(self):
        return self.__timestamp
    
    def get_miner(self):
        return self.__miner    
    
    def get_signature(self):
        return self.__signature

    def get_account_state(self):
        return self.__accountState
    
    def get_reward_state(self):
        return self.__rewardState

    def get_account_state_CID(self):
        return self.__accountState_CID
    
    def get_reward_state_CID(self):
        return self.__rewardState_CID

    def get_data(self):
        return self.__data

    def get_committee(self):
        return self.__committee

    def writeBlock(self, IPFS_API_instance):
        self.block = {"Data": self.__data , "Signature": self.__signature }
        content = json.dumps(self.block)
        CID = IPFS_API_instance.addfile(content,"BK")
        f = open("Blocks/Temp/"+str(CID)+".json","wb")
        f.write(content.encode())
        f.close()
        return str(CID)

    def validate_signature(self, IPFS_API_instance):
        valid_signature=False
        try:
            signature=bytes.fromhex(self.__signature)
            content=json.dumps(self.__data)
            content=content.encode('utf-8')
            public_key_content= IPFS_API_instance.getContent(self.__miner, "PK")
            public_key=base64.decodebytes(public_key_content)
            verify(public_key, content, signature)
            valid_signature=True
        except:
            print("SIGNATURE VALIDATION FAILURE")
            valid_signature=False
        return valid_signature  
    
    def __set_reward_state_from_CID(self, CID, IPFS_API_instance):
        print("IN SET REWARD STATE ", CID )
        if CID == "" or CID == None:
            ## GET THE PREVIOUS META BLOCK AND EXTRACT PREVIOUS REWARD STATE
            previous_meta = create_metablock_from_CID(IPFS_API_instance, self.__previous_meta_hash)
            if previous_meta.get_reward_state() == None:
                self.__rewardState = {}
            else:
                reward_state_content = IPFS_API_instance.getContent(previous_meta.get_reward_state(),"NA")
                self.__rewardState = json.loads(reward_state_content)
        else:
                print("CID NOT NULL", CID)
                reward_state_content = IPFS_API_instance.getContent(CID, "NA")
        #        print("REWARD STATE FROM CID SET ")
         #       print("CONTENT", reward_state_content)
                self.__rewardState = json.loads(reward_state_content)
         #       print(self.__rewardState)
    
    def __set_account_state_from_CID(self, CID, IPFS_API_instance):
      #  print("IN SET ACCOUNT STATE ", CID )
        
        if CID == "" or CID == None:
            ## GET THE PREVIOUS META BLOCK AND EXTRACT PREVIOUS ACCOUNT STATE
            previous_meta = create_metablock_from_CID(IPFS_API_instance, self.__previous_meta_hash)
            if previous_meta.get_reward_state() == None:
      #          print("SETTING DEFAULT STATE")
                self.__accountState = {}
            else:
                account_state_content = IPFS_API_instance.getContent(previous_meta.get_reward_state(),"NA")
     #           print("NEW STATE SET ")
     #           print(account_state_content)
                self.__accountState = json.loads(account_state_content)
        else:
   #         print("CID NOT NULL", CID)
            account_state_content = IPFS_API_instance.getContent(CID, "NA")
     #       print("ACCOUNT STATE FROM CID SET ")
    #       print("CONTENT", account_state_content)
            self.__accountState = json.loads(account_state_content)
     #       print(self.__accountState)

                
    def __update_reward_state_CID(self, IPFS_API_instance):
        
 #       print()
 #       print("*****" , self.__rewardState)
        #json_content = json.loads(self.__rewardState)
        string_content = json.dumps(self.__rewardState)
        CID = IPFS_API_instance.addfile(string_content, "NA")
  #      print("**************************")
  #      print("DEBUG:    CID:  ", CID)
        return str(CID)

 
## TODO: Check if disconnected ones work here as well
    def __reward_accept(self, validation_content, IPFS_API_instance):
  #      print(" IN REWARD ACCEPT ")
 #       print("REWARD STATE: ", self.__rewardState)
 #       print("VALIDATION CONTENT", validation_content)
        votes = validation_content["Votes"]
 #       print("VOTES: ", votes)
        for vote in votes: 

            vote_content = IPFS_API_instance.getContent(votes[vote],"NA")
            v = json.loads(vote_content)
  #          print("PROCESSING VOTE REWARDS  ",v)
            if v["Vote"]["vote"] == "Accept":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] +.01
                else:
                    self.__rewardState[vote] = .01
            elif v["Vote"]["vote"] == "Reject":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] -.01
                else:
                    self.__rewardState[vote] = -.01
            elif v["Vote"]["vote"] == "Disconnected":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] -.01
                else:
                    self.__rewardState[vote] = -.01

    def __reward_reject(self, validation_content, IPFS_API_instance):
   #     print(" IN REWARD REJECT ")
        votes = validation_content["Votes"]
  #      print("VOTES: ", votes)
        for vote in votes: 

            vote_content = IPFS_API_instance.getContent(votes[vote],"NA")
            v = json.loads(vote_content)
            if v["Vote"]["vote"] == "Reject":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] +.01
                else:
                    self.__rewardState[vote] = .01

            elif v["Vote"]["vote"] == "Disconnected":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] -.01
                else:
                    self.__rewardState[vote] = -.01

            elif v["Vote"]["vote"] == "Accept":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] -.01
                else:
                    self.__rewardState[vote] = -.01

    def __handle_fault(self, validation_content, IPFS_API_instance):
 #       print(" IN HANDLE FAULT ")
        votes = validation_content["Votes"]
  #      print("VOTES: ", votes)
        for vote in votes: 

            vote_content = IPFS_API_instance.getContent(votes[vote],"NA")
            v = json.loads(vote_content)

            if v["Vote"]["vote"] == "Disconnected":
                if vote in self.__rewardState:
                    self.__rewardState[vote] = self.__rewardState[vote] -.01
                else:
                    self.__rewardState[vote] = -.01
    

    def update_states(self, IPFS_API_instance):
  #      print ("IN META BLOCK UPDATE STATES")
   #     print("VALIDATION STATE: ", self.__validation_hash)
        validation_content = IPFS_API_instance.getContent(self.__validation_hash,"BK")
        validation = json.loads(validation_content)
        validation_status = validation["Data"]["Status"]

        if validation_status == "Accept":
  #          print("ACCEPT STATE ")
            self.__reward_accept(validation["Data"],IPFS_API_instance)
            block_content = IPFS_API_instance.getContent(self.__block_hash,"BK")
            ref_block = json.loads(block_content)
   #         print("REF BLOCK ", ref_block)
            self.__accountState_CID = ref_block["Header"]["AccountStateHash"]
            self.__rewardState_CID = self.__update_reward_state_CID(IPFS_API_instance)
        elif validation_status == "Reject":
   #         print("REJECT STATE ")
            previous_meta = create_metablock_from_CID(IPFS_API_instance, self.__previous_meta_hash)
            self.__reward_reject(validation["Data"], IPFS_API_instance)
            self.__rewardState_CID = self.__update_reward_state_CID(IPFS_API_instance)
            self.__accountState_CID = previous_meta.get_account_state_CID()
        ## ELSE A FAULT OCCURED
        else:
    #        print("FAULT STATE")
            previous_meta = create_metablock_from_CID(IPFS_API_instance, self.__previous_meta_hash)
            self.__handle_fault(validation["Data"], IPFS_API_instance)
            self.__rewardState_CID = self.__update_reward_state_CID(IPFS_API_instance)
            self.__accountState_CID = previous_meta.get_account_state_CID()

    def validate_block(self, IPFS_API_instance):
        block_ref : Block = create_block_from_CID(self.__block_hash)
        validation_block : ValidationBlock = create_validationblock_from_CID(self.__validation_hash)
        previous_meta_block : MetaBlock = create_metablock_from_CID(self.__previous_meta_hash)
        if previous_meta_block.get_refrence_block_ID() != self.__previous_block_hash:
            return False
        if previous_meta_block.get_validation_ID != self.__previous_validation_hash:
            return False
        if block_ref.get_block_height != self.__block_height:
            return False
        if validation_block.get_block_height() != self.__block_height:
            return False
        if block_ref.get_miner() != self.__miner:
            return False
        if validation_block.get_miner() != self.__miner:
            return False
        if block_ref.get_timestamp >= self.__timestamp:
            return False
        if validation_block.get_timestamp() >= self.__timestamp:
            return False
        if self.validate_signature(IPFS_API_instance) == False:
            return False
        if validation_block.validate_block(IPFS_API_instance) == False:
          return False
        if block_ref.validate_block(IPFS_API_instance) == False: 
            return False
 
    def sign(self, signer, private_key, IPFS_API_instance):
   #     print("***** IN SIGN META BLOCK  ", self.__block_hash)
        reference_block = create_block_from_CID(IPFS_API_instance, self.__block_hash)
        if signer == reference_block.get_miner():
            signature_tester = "test value"
            signature_tester = signature_tester.encode('utf-8')
            signature = sign(private_key, signature_tester)
            signature = signature.hex()
            
            ## CHECK THE TEST VALUE SIGNATURE CAN BE VALIDATED WITH THE PUBLIC KEY OF THE MINER OF THE REFERENCE BLOCK
            valid_signature = False
            try:
                signature = bytes.fromhex(signature)
                public_key_content = IPFS_API_instance.getContent(signer, "PK")
                public_key = base64.decodebytes(public_key_content)
                verify(public_key,signature_tester, signature)
                valid_signature=True
            except:
      #          print("SIGNATURE VALIDATION FAILURE")
                valid_signature=False
                return None

            if valid_signature:
                self.__data["AccountState"] = self.__accountState_CID
                self.__data["RewardState"] = self.__rewardState_CID
      
                message = json.dumps(self.__data)
       #         print("WHAT WILL BE SIGNED ", message)
                message = message.encode('utf-8')
                signature = sign(private_key, message)
                self.__signature = signature.hex()
                CID = self.writeBlock(IPFS_API_instance)
                return CID
                
class Block():

    def __init__(self, transactions_in, height, previous_block, previous_meta_block, timestamp, miner, IPFS_API_instance, account_state_ID = "", signature ="", new_block = True):
        self.__block_height = height
        self.__transactions = transactions_in
        self.__transaction_counter = len(transactions_in)
        self.__previous_hash = previous_block
        self.__timestamp = timestamp
        self.__previous_meta_block = previous_meta_block
        self.__miner = miner
        self.__merkleHeight=0
        self.__header={}
        self.__body={}
        self.__accountState={}
        self.__accountState_ID = account_state_ID
        self.__load_account_state(self.__accountState_ID, IPFS_API_instance)
        self.__signature = signature
        self.__hash_root = self.generateMerkleTree(IPFS_API_instance,self.__miner,self.__block_height, new_block)
        self.__load_account_state(self.__accountState_ID, IPFS_API_instance)
        self.__header = {"Height": self.__block_height, "PreviousBlock": self.__previous_hash, "Timestamp": self.__timestamp, "HashRoot": self.__hash_root, "AccountStateHash": self.__accountState_ID, "Miner": self.__miner, "PreviousMetaID": self.__previous_meta_block }
 
        self.block={}
    def get_hash_root(self):
        return self.__hash_root

    def get_block_height(self):
        return self.__block_height
    
    def get_transactions(self):
        return self.__transactions
    
    def get_previous_hash(self):
        return self.__previous_hash
    
    def get_timestamp(self):
        return self.__timestamp

    def get_previous_meta_ID(self):
        return self.__previous_meta_block
    
    def get_miner(self):
        return self.__miner
    
    def get_account_state_ID(self):
        return self.__accountState_ID
    
    def get_account_state(self):
        return self.__accountState

    def validate_transaction_amounts(self,state, expected_miner, IPFS_API_instance):
    #    print("VALIDATING TX AMOUNTS")
        isValid = True
        isCoinbase = False
        valid = True
        for i in range (0, len(self.__transactions)):
            t = transaction.loadFromFile(self.__transactions[i],IPFS_API_instance)
            if i==0:
                if t.header["To"] == expected_miner:
                    if t.header["Amount"] ==10:
                        
                        isCoinbase = True
                        
                isValid = isValid & isCoinbase
            else:
                balance = state[t.header["From"]]
                if t.header["Amount"] <= balance:
                    valid = True
                else:
                    return False, i
                isValid = valid & isValid
        return isValid, -1
    
    def validate_transactions(self, block_num,expected_miner, IPFS_API_instance):
   #     print("VALIDATING TRANSACTIONS")
        isValid = True
        for i in range (0, len(self.__transactions)):
            t = transaction.loadFromFile(self.__transactions[i], IPFS_API_instance)
            if i==0:
                txPubKey=t.loadPublicKey(IPFS_API_instance, True)
            else:
                txPubKey=t.loadPublicKey(IPFS_API_instance)
            if i > 0:
                valid= t.validate(txPubKey, IPFS_API_instance)
            else:
                valid = t.validateCoinbase(t.header["To"], block_num, IPFS_API_instance, expected_miner)
            if valid == False:
                return False,i
            isValid = valid & isValid
        return isValid,"Valid Format"


    def validate_block(self, IPFS_API_Instance):
        ## FIRST CHECK IF IT IS A NULL BLOCK
        ## NULL BLOCKS OCCUR IF THE PRIMARY MINER FAILED TO PRODUCE AN ACCEPTABLE BLOCK
        f=open("MinerFiles/minerList.txt","r")
        miners = f.readlines()
        f.close()
        valid_Block = False
    #    print("IN VALIDATE BLOCK ")
    #    print()
        previous_block : Block = create_block_from_CID(IPFS_API_Instance, self.__previous_hash)
        
        previous_ID_match=False
        height_correct= False
        miner_correct = False
     #   print("CREATING PREVIOUS META BLOCK")
        previous_meta_block : MetaBlock = create_metablock_from_CID(IPFS_API_Instance,self.__previous_meta_block)
       
        if previous_meta_block.get_refrence_block_ID() != self.__previous_hash:
            return False, "Previous Block Mismatch"

        
        if previous_block.get_block_height() == self.__block_height -1:
            height_correct = True
        else:
            ## BLOCK HEIGHT IS INCORRECT (IGNORE BLOCK)
            return False, "Invalid Height Data"

        previous_block_timestamp = previous_block.get_timestamp()
        if previous_block_timestamp + 200 < time.time() and previous_block.get_block_height() >0:

            if previous_meta_block.get_account_state() != account_state_hash: 
                return False, "Account State Error"

            backup_miner_index = (previous_block.get_block_height()+1 % len(miners))
            expectedMiner = miners[backup_miner_index].strip()

            ## PERFORM VALIDATION OF NULL BLOCK
            account_state_valid = previous_block.get_account_state_ID() == self.__accountState_ID

            
            null_transactions = len(self.__transactions ) == 0


            valid_miner = self.__miner == expectedMiner
            valid_hashroot = self.__hash_root  == "0000000000000000000000000000000000000000000000000000000000000000"
            valid_signature = self.validate_signature(IPFS_API_Instance)
            if valid_miner and valid_hashroot and null_transactions and account_state_valid and valid_signature:
                return True, "Valid"
            else:
                return False, "Invalid Sender Data"

        else:

            expected_miner_index = self.__block_height %(len(miners))
            expectedMiner = miners[expected_miner_index].strip()       
            previoius_account_state = previous_block.get_account_state()
            previous_account_state_ID =  previous_block.get_account_state_ID()


            ## GET PREVIOUS STATE
            try: 
                previous_account_state_object = json.loads(previoius_account_state)
            except:

                previous_account_state_object = previoius_account_state


            validate_TX_format = self.validate_transactions(self.__block_height, expectedMiner,IPFS_API_Instance)


            if validate_TX_format == False:
                return False, "Invalid TX Format"
            
            validate_TX_amounts, tx_index = self.validate_transaction_amounts(previoius_account_state, expectedMiner, IPFS_API_Instance)
            if validate_TX_amounts ==False:
                return False,"Invalid TX "+str(tx_index)

            if self.__miner == expectedMiner:
                miner_correct = True
            
            else:
                ## NOT EXPECTED MINER (IGNORE BLOCK)
                return False,"Incorrect Miner"
        
            
            ### IF ALL OTHER INFORMATION IS VALID CHECK THE MERKLE ROOT (WHICH WILL GIVE NEW STATE VALUE) AND VALIDATE SIGNATURE
            merkle_root, txs, state_CID = self.checkMerkleTree(IPFS_API_Instance, expectedMiner,self.__block_height,previous_account_state_ID)

            if merkle_root == self.__hash_root:
                account_state_hash = self.get_account_state_hash(IPFS_API_Instance, self.__accountState)
                if account_state_hash == self.__accountState_ID:
                    valid_Block = True, "Valid"
                else:
                    return False,"Invalid Account State Hash -- "+str(account_state_hash)
            else:
                return False, "Invalid Merkle Root"
        return valid_Block,"Valid"


    def __set_account_state_hash(self, IPFS_API_instance, state):
        f = open("MinerFiles/Temp.json","w")
        f.write(json.dumps(state))
        f.close()
        CID = IPFS_API_instance.addFileByPath("MinerFiles/Temp.json")
        self.__accountState_ID = CID      
#  CID = IPFS_API_instance.getCID("MinerFiles/Temp.json")
        return CID

    def get_account_state_hash(self, IPFS_API_instance, state):
        f = open("MinerFiles/Temp.json","w")
        f.write(json.dumps(state))
        f.close()
        #CID = IPFS_API_instance.addFileByPath("MinerFiles/Temp.json")
        #self.__accountState_ID = CID      
        CID = IPFS_API_instance.getCID("MinerFiles/Temp.json")
        return CID

    def __load_account_state(self, CID, IPFS_API_instance):
        if self.__accountState_ID =="":
            previous_block = create_block_from_CID(IPFS_API_instance, self.__previous_hash)
            CID = previous_block.get_account_state_ID()

        content = IPFS_API_instance.getContent(CID,"NA")
        self.__accountState = json.loads(content)
#        print("ACCOUNT STATE NOW: ", self.__accountState)

    def null_block(self, IPFS_API_instance):
       self.__transactions = []
       self.__hash_root = "0000000000000000000000000000000000000000000000000000000000000000"
       previous_block : Block = create_block_from_CID(IPFS_API_instance,  self.__previous_hash)
       self.__accountState_ID = previous_block.get_account_state_ID()
       self.__accountState = previous_block.get_account_state()

    def sign(self,privKey,ipfsAPIInstance):
        #"Height": 0, "PreviousBlock": null, "Timestamp": 1640995200.0, "HashRoot": "0000000000000000000000000000000000000000000000000000000000000000", "AccountStateHash": "QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW", "Miner": "QmaHx8iHzKWMx4mGsPstPFcE4xnViuzLzJQ6NvhfuoLst7"
 #       print("IN SIGN:  ")
        self.__header = {"Height": self.__block_height, "PreviousBlock": self.__previous_hash, "Timestamp": self.__timestamp, "HashRoot": self.__hash_root, "AccountStateHash": self.__accountState_ID, "Miner": self.__miner, "PreviousMetaID": self.__previous_meta_block }
  #      print(self.__header)
 #       print()
        message = json.dumps(self.__header)
        message = message.encode('utf-8')
        signature = sign(privKey, message)
        self.__signature = signature.hex()
        self.__body["Signature"] = signature.hex()
        CID=self.writeBlock(ipfsAPIInstance)
        return CID
    
    def validate_signature(self, IPFS_API_instance):
  #      print("IN VALIDATE SIGNATURE: ")
        valid_signature = False
        try:
            signature=bytes.fromhex(self.__signature)
            content=json.dumps(self.__header)
  #          print("CHECKING CONTENT FOR SIGNATURE: ", content)
            content=content.encode('utf-8')
            public_key_content= IPFS_API_instance.getContent(self.__miner, "PK")
            public_key=base64.decodebytes(public_key_content)
            verify(public_key, content, signature)
            valid_signature=True
        except:
            print("SIGNATURE VALIDATION FAILURE")
            valid_signature=False
        return valid_signature  
                
    def generateMerkleTree(self,ipfsAPIInstance,expectedMiner, block_height, update_states = True):
 #       print("LOG:   IN GENERATE MERKLE TREE")
        self.__hash_root=""
        if block_height==0:
            return "",[]
        else:
            hashes=[]
            txID=[]
            coinbaseCount=0
            for t in self.__transactions:
                if t=="":
                    print("NO TX")
                    pass
                else:
                    tx=transaction.loadFromFile(t,ipfsAPIInstance) 
                    if  tx.header["From"]=="COINBASE_"+str(self.__block_height):
     #                       print("COINBASE   PRE ACCOUNT STATE CHANGE", self.__accountState)
                            validCoinbase=tx.validateCoinbase(self.__miner,self.__block_height,ipfsAPIInstance,expectedMiner)
                            if validCoinbase and coinbaseCount ==0:
                                coinbaseCount = coinbaseCount + 1
                                if tx.header["To"] in self.__accountState:
                                    if update_states:
                                        self.__accountState[tx.header["To"]]+=tx.header["Amount"]
                                else:
                                    if update_states:
                                        self.__accountState[tx.header["To"]]=tx.header["Amount"]
                                hashes.append(t)
                                txID.append(t)
   #                             print("DONE ADDING COINBASE", self.__accountState)
                            else:
                                print("COINBASE NOT ADDED")
                                break
                                
                    else:
  #                      print("NON COINBASE TX ADDED")
 #                       
            #           ## CHECK AGAINST ACCOUNT STATE FOR SENDER
      #                  print("CHECKING IF SENDER HAS BALANCE")
                        if tx.header["From"] in self.__accountState:
                            if tx.header["Amount"]<= self.__accountState[tx.header["From"]]:

                                txPubKey=tx.loadPublicKey(ipfsAPIInstance)
                                if tx.validate(txPubKey,ipfsAPIInstance): 
                                    self.__accountState[tx.header["From"]]-=tx.header["Amount"]
                                    if tx.header["To"] in self.__accountState:
                                        if update_states:
                                            self.__accountState[tx.header["To"]] += tx.header["Amount"]
                                    else:
                                        if update_states:
                                            self.__accountState[tx.header["To"]] = tx.header["Amount"]
                                    hashes.append(t)
                                    txID.append(t)
                                else:
                                    print("NOT VALID FORMAT")
                            else:
                                print("NOT ENOUGH FUNDS")
                        else:
                            print("ACCOUNT NOT RECOGNIZED")
            hashes=self.generatMerkleRow(hashes)
            while (len(hashes)>1):
                hashes=self.generatMerkleRow(hashes)
            self.__set_account_state_hash(ipfsAPIInstance, self.__accountState)
            if len(hashes)==0:
                self.__hash_root = "0000000000000000000000000000000000000000000000000000000000000000"
                self.__transactions = []
                return "0000000000000000000000000000000000000000000000000000000000000000", []
            else:
                self.__hash_root = hashes[0]
                self.__transactions = txID
                return hashes[0],txID

              
    def checkMerkleTree(self,ipfsAPIInstance,expectedMiner, block_height, previous_account_state_ID):
 #       print("LOG IN CHECK MERKLE TREE")
        hash_root=""
        previous_account_state = ipfsAPIInstance.getContent(previous_account_state_ID,"NA")
        previous_account_state = json.loads(previous_account_state.decode())
        if block_height==0:
            return"0000000000000000000000000000000000000000000000000000000000000000", []
        else:
            hashes=[]
            txID=[]
            coinbaseCount=0
            for t in self.__transactions:
                if t=="":
                    print("NO TX")
                    pass
                else:
      #              print("TX: ",t)
      #              print("DOING VALIDATION")
                    tx=transaction.loadFromFile(t,ipfsAPIInstance) ### Use transaction.py method to create a memory object of the TX
      #              print("TX:::: ", tx.full)
  #                  print("CHECKING MERKLE TREE")
  #                  print("PREVIOUS STATE: ", previous_account_state)
                    if  tx.header["From"]=="COINBASE_"+str(self.__block_height):
  #                          print("COINBASE")
                            validCoinbase=tx.validateCoinbase(self.__miner,self.__block_height,ipfsAPIInstance,expectedMiner)
                            if validCoinbase and coinbaseCount ==0:
                                coinbaseCount = coinbaseCount + 1
                                if tx.header["To"] in previous_account_state:
                                    
                                        previous_account_state[tx.header["To"]]+=tx.header["Amount"]
                                else:
                                        previous_account_state[tx.header["To"]]=tx.header["Amount"]
                                hashes.append(t)
                                txID.append(t)
   #                             print("DONE ADDING COINBASE")
                            else:
                                print("COINBASE NOT ADDED")
                                break
                                
                    else:
     #                   print("NON COINBASE TX ADDED")
                        
            #           ## CHECK AGAINST ACCOUNT STATE FOR SENDER
    #                    print("CHECKING IF SENDER HAS BALANCE")
                        if tx.header["From"] in self.__accountState:
                            if tx.header["Amount"]<= self.__accountState[tx.header["From"]]:

                                txPubKey=tx.loadPublicKey(ipfsAPIInstance)
                                if tx.validate(txPubKey,ipfsAPIInstance): 
                                    previous_account_state[tx.header["From"]]-=tx.header["Amount"]
                                    if tx.header["To"] in self.__accountState:
                                        previous_account_state[tx.header["To"]]+=tx.header["Amount"]
                                    else:
                                        previous_account_state[tx.header["To"]]=tx.header["Amount"]
                                    hashes.append(t)
                                    txID.append(t)
                                else:
                                    print("NOT VALID FORMAT")
                            else:
                                print("NOT ENOUGH FUNDS")
                        else:
                            print("ACCOUNT NOT RECOGNIZED")
            hashes=self.generatMerkleRow(hashes)
            while (len(hashes)>1):
                hashes=self.generatMerkleRow(hashes)
           
    #        print("HASHING STATE", previous_account_state)
            f = open("MinerFiles/Temp.json","w")
            f.write(json.dumps(previous_account_state))
            f.close()
            CID = ipfsAPIInstance.addFileByPath("MinerFiles/Temp.json")
  
          
            if len(hashes)==0:
                self.__hash_root = "0000000000000000000000000000000000000000000000000000000000000000"
                self.__transactions = []
                return "0000000000000000000000000000000000000000000000000000000000000000", [], CID
            else:
                self.__hash_root = hashes[0]
                self.__transactions = txID
                return hashes[0],txID, CID


    def validateCoinbase(self,tx,ipfsAPIInstance):  
        validTo=tx.validateAddressExists(tx.full["To"])
        validToIsMiner=tx.full["To"]==self.header["Miner"]
        validAmount=tx.full["Amount"]==10.0
        validSignature=False
        try:
            signature=bytes.fromhex(tx.sig)
            content=json.dumps(tx.header)
 #           print("CONTENT",content)
            content=content.encode('utf-8')
            pubkey=tx.loadPublicKey(ipfsAPIInstance)
            verify(pubkey,content, signature)
  
        #    pubkey.verify( signature, content, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
            validSignature=True
        except:
            print("SIGNATURE VALIDATION FAILURE")
            validSignature=False

        if validTo and  validToIsMiner and validAmount and validSignature:
            return True
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

    def writeBlock(self,ipfsHelper):
        self.block= {"Header": self.__header ,"Body": {"Transactions": self.__transactions,  "Signature": self.__signature}}
        
        x=json.dumps(self.block)
        CID=ipfsHelper.addfile(x,"BK")
        f=open("Blocks/Temp/"+str(CID)+".json","wb")
        f.write(x.encode())
        f.close()

        f=open("Blocks/"+str(CID)+".json","wb")
        f.write(x.encode())
        f.close()
        return str(CID)



class GenesisBlock():
    def __init__(self, signer, IPFS_API_instance):
        self.__block_height = 0
        self.__miner = "QmaHx8iHzKWMx4mGsPstPFcE4xnViuzLzJQ6NvhfuoLst7"
        self.__transactions = []
        self.__transaction_counter = 0
        self.__previous_hash = None
        self.__timestamp = 1640995200.0
        self.__signature=""
        self.__previous_meta = None
        self.__header={}
        self.__body={}
        self.__accountState={}
        self.__header["Height"]=self.__block_height
        self.__header["PreviousBlock"]=self.__previous_hash
        self.__header["Timestamp"]=self.__timestamp
        self.__header["HashRoot"]="0000000000000000000000000000000000000000000000000000000000000000"
        self.__header["AccountStateHash"]="QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW"
        self.__header["Miner"]=self.__miner
        self.__header["PreviousMetaID"] = self.__previous_meta
        self.__body["AccountState"]={}
        self.__body["Transactions"]=[]
        self.block = {}
        self.block["Header"]=json.dumps(self.__header)
        self.block["Body"]=json.dumps(self.__body)
#    block = Block(blockData["Body"]["Transactions"], blockData["Header"]["Height"], blockData["Header"]["PreviousBlock"], blockData["Header"]["PreviousMeta"], blockData["Header"]["Timestamp"], blockData["Header"]["Miner"], IPFS_API_instance, blockData["Header"]["AccountStateID"], blockData["Body"["Signature"]])
        ## CHECK IF GENESIS MINTER IS ORIGINAL MINTER OR OTHER MINER  
        f=open("Local/KeyChain/PrivateKey.key", 'rb')
        private_Key = f.read()
        f.close()
        secretKey = base64.decodebytes(private_Key)
        self.__sign(signer, secretKey, IPFS_API_instance)
    
    def __sign(self, signer, private_key, IPFS_API_instance):
        if self.__miner == signer:
            response = input("Would you like to create a new genesis block?")
            if response =="YES":
                signature_tester = "test value"
                signature_tester= signature_tester.encode('utf-8')
                signature = sign(private_key, signature_tester)
                signature = signature.hex()
                
                ## CHECK THE TEST VALUE SIGNATURE CAN BE VALIDATED WITH THE PUBLIC KEY OF THE MINER OF THE REFERENCE BLOCK
                valid_signature=False
                try:
                    signature=bytes.fromhex(signature)
                    pubKeyContent= IPFS_API_instance.getContent(signer,"PK")
                    publicKey=base64.decodebytes(pubKeyContent)
                    verify(publicKey,signature_tester, signature)
                    valid_signature=True
                except:
                    print("INVALID SIGNATURE")
                    valid_signature=False

                if valid_signature:
   #                 print("HEADER:::::: ")
    #                print(self.__header)
                    message = json.dumps(self.__header)
                    message = message.encode('utf-8')
                    signature = sign(private_key, message)
                    self.__signature = signature.hex()
                    self.__body["Signature"] = self.__signature
            else:
                self.__signature = "39f4f78f6cf15d3c5b8dbaf3f364969092275a2c2da4cce2140fcf71f6de91e47263b9909b6dcf6d0527d8db15771cd7419269947313184aa538b7c781c93ddaf8b7eb279c14bc2a078371f5f90c4bb888ec897ed60cca21507f4c5df5862f901ffc4240e23906de259370d1d437fd94e3f119120a776e0b359d6e32a9b410eeb4a853a0a8e518787781a54d3e2eb14698f7a7ed86aa451c461aaa75a8d90834ad0112074756519fac6950dacbde9c83e280352b1678d63be83b9fb185c46aca3e5ec2d6dc9a8f52e3cb8948d2066ad6d81dc8a9a612526ed80d76721ade2c139fdb36e85db6c0e8be190312e032ef56be4f8647883894b1fefd7a843be9ee2c9e6a84986369d377168edbc6a8b41a563dc8e9e2f858ba1af77f5436ce42b4c54635f4d77b7c699788ba35e36e1047b779e2b34e481b8254bd525c753524925057bb86807a1a879a7d112d5e1c947214971b9690c772b5ac9ad530bff33458b711fd90c55e795e39cb91ab09d240ece62fb82db2d8f50a15d889b0be171311af14fadcc0ba2d5d0a07456437718b1c67bcac4b9ea20c61e36a46ed3675dc45be06ea25f8ba0aa1f3d16edae2b9c38a33680ee4e07ce0e5da2decd44fd0f2a91f7434c3c25027b89ee98993a347618dfb420adb56833cf39b9b34543fe68dacd75ef6a43b32a7f063d949d1d99441aa2c92cf1593c7bb3c7edd65bf6916c8a348cb27fb7e709cb484856ad9c55ae44317a9576c0b8c6a996db095eec53db09f53171e090ccd7010fe1db7666b2c9ec984a6c3a4a96dfa17a3553426e73e2d2270dade173d80674e05318128d09b8b0f07c1ee15b53ff0fafe5b5bdfff7ff0677ef7edfb2b1fc588fce657ab7acf57b78aae0b1bcc881dbd5cc44edc929bc99c312cff3e1390cf330dd62bcd2a222659fd8c8e6c"
                self.__body["Signature"] = "39f4f78f6cf15d3c5b8dbaf3f364969092275a2c2da4cce2140fcf71f6de91e47263b9909b6dcf6d0527d8db15771cd7419269947313184aa538b7c781c93ddaf8b7eb279c14bc2a078371f5f90c4bb888ec897ed60cca21507f4c5df5862f901ffc4240e23906de259370d1d437fd94e3f119120a776e0b359d6e32a9b410eeb4a853a0a8e518787781a54d3e2eb14698f7a7ed86aa451c461aaa75a8d90834ad0112074756519fac6950dacbde9c83e280352b1678d63be83b9fb185c46aca3e5ec2d6dc9a8f52e3cb8948d2066ad6d81dc8a9a612526ed80d76721ade2c139fdb36e85db6c0e8be190312e032ef56be4f8647883894b1fefd7a843be9ee2c9e6a84986369d377168edbc6a8b41a563dc8e9e2f858ba1af77f5436ce42b4c54635f4d77b7c699788ba35e36e1047b779e2b34e481b8254bd525c753524925057bb86807a1a879a7d112d5e1c947214971b9690c772b5ac9ad530bff33458b711fd90c55e795e39cb91ab09d240ece62fb82db2d8f50a15d889b0be171311af14fadcc0ba2d5d0a07456437718b1c67bcac4b9ea20c61e36a46ed3675dc45be06ea25f8ba0aa1f3d16edae2b9c38a33680ee4e07ce0e5da2decd44fd0f2a91f7434c3c25027b89ee98993a347618dfb420adb56833cf39b9b34543fe68dacd75ef6a43b32a7f063d949d1d99441aa2c92cf1593c7bb3c7edd65bf6916c8a348cb27fb7e709cb484856ad9c55ae44317a9576c0b8c6a996db095eec53db09f53171e090ccd7010fe1db7666b2c9ec984a6c3a4a96dfa17a3553426e73e2d2270dade173d80674e05318128d09b8b0f07c1ee15b53ff0fafe5b5bdfff7ff0677ef7edfb2b1fc588fce657ab7acf57b78aae0b1bcc881dbd5cc44edc929bc99c312cff3e1390cf330dd62bcd2a222659fd8c8e6c"
        
        else:
            self.__signature = "39f4f78f6cf15d3c5b8dbaf3f364969092275a2c2da4cce2140fcf71f6de91e47263b9909b6dcf6d0527d8db15771cd7419269947313184aa538b7c781c93ddaf8b7eb279c14bc2a078371f5f90c4bb888ec897ed60cca21507f4c5df5862f901ffc4240e23906de259370d1d437fd94e3f119120a776e0b359d6e32a9b410eeb4a853a0a8e518787781a54d3e2eb14698f7a7ed86aa451c461aaa75a8d90834ad0112074756519fac6950dacbde9c83e280352b1678d63be83b9fb185c46aca3e5ec2d6dc9a8f52e3cb8948d2066ad6d81dc8a9a612526ed80d76721ade2c139fdb36e85db6c0e8be190312e032ef56be4f8647883894b1fefd7a843be9ee2c9e6a84986369d377168edbc6a8b41a563dc8e9e2f858ba1af77f5436ce42b4c54635f4d77b7c699788ba35e36e1047b779e2b34e481b8254bd525c753524925057bb86807a1a879a7d112d5e1c947214971b9690c772b5ac9ad530bff33458b711fd90c55e795e39cb91ab09d240ece62fb82db2d8f50a15d889b0be171311af14fadcc0ba2d5d0a07456437718b1c67bcac4b9ea20c61e36a46ed3675dc45be06ea25f8ba0aa1f3d16edae2b9c38a33680ee4e07ce0e5da2decd44fd0f2a91f7434c3c25027b89ee98993a347618dfb420adb56833cf39b9b34543fe68dacd75ef6a43b32a7f063d949d1d99441aa2c92cf1593c7bb3c7edd65bf6916c8a348cb27fb7e709cb484856ad9c55ae44317a9576c0b8c6a996db095eec53db09f53171e090ccd7010fe1db7666b2c9ec984a6c3a4a96dfa17a3553426e73e2d2270dade173d80674e05318128d09b8b0f07c1ee15b53ff0fafe5b5bdfff7ff0677ef7edfb2b1fc588fce657ab7acf57b78aae0b1bcc881dbd5cc44edc929bc99c312cff3e1390cf330dd62bcd2a222659fd8c8e6c"
            self.__body["Signature"] = "39f4f78f6cf15d3c5b8dbaf3f364969092275a2c2da4cce2140fcf71f6de91e47263b9909b6dcf6d0527d8db15771cd7419269947313184aa538b7c781c93ddaf8b7eb279c14bc2a078371f5f90c4bb888ec897ed60cca21507f4c5df5862f901ffc4240e23906de259370d1d437fd94e3f119120a776e0b359d6e32a9b410eeb4a853a0a8e518787781a54d3e2eb14698f7a7ed86aa451c461aaa75a8d90834ad0112074756519fac6950dacbde9c83e280352b1678d63be83b9fb185c46aca3e5ec2d6dc9a8f52e3cb8948d2066ad6d81dc8a9a612526ed80d76721ade2c139fdb36e85db6c0e8be190312e032ef56be4f8647883894b1fefd7a843be9ee2c9e6a84986369d377168edbc6a8b41a563dc8e9e2f858ba1af77f5436ce42b4c54635f4d77b7c699788ba35e36e1047b779e2b34e481b8254bd525c753524925057bb86807a1a879a7d112d5e1c947214971b9690c772b5ac9ad530bff33458b711fd90c55e795e39cb91ab09d240ece62fb82db2d8f50a15d889b0be171311af14fadcc0ba2d5d0a07456437718b1c67bcac4b9ea20c61e36a46ed3675dc45be06ea25f8ba0aa1f3d16edae2b9c38a33680ee4e07ce0e5da2decd44fd0f2a91f7434c3c25027b89ee98993a347618dfb420adb56833cf39b9b34543fe68dacd75ef6a43b32a7f063d949d1d99441aa2c92cf1593c7bb3c7edd65bf6916c8a348cb27fb7e709cb484856ad9c55ae44317a9576c0b8c6a996db095eec53db09f53171e090ccd7010fe1db7666b2c9ec984a6c3a4a96dfa17a3553426e73e2d2270dade173d80674e05318128d09b8b0f07c1ee15b53ff0fafe5b5bdfff7ff0677ef7edfb2b1fc588fce657ab7acf57b78aae0b1bcc881dbd5cc44edc929bc99c312cff3e1390cf330dd62bcd2a222659fd8c8e6c"
        CID = self.writeBlock(IPFS_API_instance)
        return CID

    def writeBlock(self,ipfsHelper):
  
        self.block["Header"] = self.__header
        self.block["Body"] = self.__body
        self.block = {"Header": self.__header , "Body": self.__body }

        x = json.dumps(self.block)
        CID=ipfsHelper.addfile(x,"BK")
        filename = Path("MinerFiles/blockchainOrderRef")
        if(not path.exists("MinerFiles/blockchainOrderRef")):
            filename.touch(exist_ok=True)  
        f=open("Blocks/"+str(CID)+".json","wb")
        f.write(x.encode('UTF-8'))
        f.close()
        return str(CID)


class GenesisValidationBlock():
    def __init__(self, signer, IPFS_API_instance):
        self.__block_height = 0
        self.__miner = "QmaHx8iHzKWMx4mGsPstPFcE4xnViuzLzJQ6NvhfuoLst7"
        self.__block_ref = "QmZJhTkdvVCQyPFez7XQYENxC4rYvS8tqYSzEzzneCfksK"
        self.__timestamp = 1640995201.0
        self.__votes = ["QmaRqE82TBsMhkNFgtsM6MAUo4wzaEXktr7xFVEiV8CQbA"]
        self.__vote_count = 1
        self.__accept_votes = 1
        self.__reject_votes = 0
        self.__status = "Accepted"
        
        self.__data = {"Timestamp": self.__timestamp, "Height":self.__block_height, "Miner": self.__miner, "Block": self.__block_ref, "Status": self.__status, "Votes": self.__votes} 
      #  self.__signature = 
        self.block={}

        ## CHECK IF GENESIS MINTER IS ORIGINAL MINTER OR OTHER MINER  
        f=open("Local/KeyChain/PrivateKey.key", 'rb')
        private_Key = f.read()
        f.close()
        secretKey = base64.decodebytes(private_Key)
        self.__sign(signer, secretKey, IPFS_API_instance)
        
    def __sign(self, signer, private_key, IPFS_API_instance):
        if self.__miner == signer:
            response = input("Would you like to create a new genesis validation block?")
            if response =="YES":
                signature_tester = "test value"
                signature_tester= signature_tester.encode('utf-8')
                signature = sign(private_key, signature_tester)
                signature = signature.hex()
                
                ## CHECK THE TEST VALUE SIGNATURE CAN BE VALIDATED WITH THE PUBLIC KEY OF THE MINER OF THE REFERENCE BLOCK
                valid_signature=False
                try:
                    signature=bytes.fromhex(signature)
                    pubKeyContent= IPFS_API_instance.getContent(signer,"PK")
                    publicKey=base64.decodebytes(pubKeyContent)
                    verify(publicKey,signature_tester, signature)
                    valid_signature=True
                except:
                    valid_signature=False

                if valid_signature:
                    message = json.dumps(self.__data)
    #                print(message)
                    message = message.encode('utf-8')
                    signature = sign(private_key, message)
                    self.__signature = signature.hex()
                    self.block["Signature"] = self.__signature
            else:
                self.__signature = "3930c62acab89a325306c1f198127c1c54a4c2d781d0fbde44f716bbdd7171b6e5c5087c08849140e4523d7147d5ca57b7ee18e0c7bc1ee57567c4fbd89e0a3b486f08df9147c46fd6d654cdbb0ddcc8efc378484ea30789c61f8f7aa85264db44198673f4145dd4915eb54cb239bfdc9f9781a01c48eeef3887e82914afdda10858d802f1144010d5d6205d8d4eba3414d60761439cfd9b9218e3bd7e78160b035c375b1f53514659ca83539f17444f849ea8dbac033aa38ce39eb622d84f3f2775bd54ffd9ee5a5cea6b3676dd3e3ba7a99b53b12319b8537365876e82e09cdae37443e77d0b94cc3352e8d201d689604ebacfbb5d565b9dea2f094df7cc825e8030cdf93a70d05c432cc4a9bee501f2bef767d39ddd16a464b61dea16f50852e13e068c8ac775333d7b14c9d791c435f48ae5eb119b131f3a6e884bb0e576baacc58dc5d2c19c8d862ab0b3ecf45e5b47c1a1125bb4de1959dd5f2a5b5bf385063957ead26137759c0f5afb08ed53e3cb4114791153cd3de1d08890781fc8430fc8cc404a84c5f63cdf5951514ef54856018c5799ccb1a928affb894cd23ef29fa9db4aad3b16732f58932e95432651364ad3145379f107c6bb505f18619277ccc8ea2dd34dc8eda26673b50032d8b256cb5288b3b0f9721abef5593cdaafa82904aab191887b85ce7c3a6d9b9f2c8a73dd8a0c43cd93ea539427922c9cb5af76786525794a6750f07cf53164657524487d06e584565058b9fe593e39ebdc063a47d8bfded129687c09074e3d0e43611a2882789aea3dd204d94c862390e8fcae6a4eb3d18404fea1bad4932cdfd7107f196c7d63edf21b74f67034344632eb865f9b2373908240d333512625088460c710035ea54c53978f43d259bdb44d66191c364e3a0781568646b91de2b60d8c"
                self.block["Signature"] = "3930c62acab89a325306c1f198127c1c54a4c2d781d0fbde44f716bbdd7171b6e5c5087c08849140e4523d7147d5ca57b7ee18e0c7bc1ee57567c4fbd89e0a3b486f08df9147c46fd6d654cdbb0ddcc8efc378484ea30789c61f8f7aa85264db44198673f4145dd4915eb54cb239bfdc9f9781a01c48eeef3887e82914afdda10858d802f1144010d5d6205d8d4eba3414d60761439cfd9b9218e3bd7e78160b035c375b1f53514659ca83539f17444f849ea8dbac033aa38ce39eb622d84f3f2775bd54ffd9ee5a5cea6b3676dd3e3ba7a99b53b12319b8537365876e82e09cdae37443e77d0b94cc3352e8d201d689604ebacfbb5d565b9dea2f094df7cc825e8030cdf93a70d05c432cc4a9bee501f2bef767d39ddd16a464b61dea16f50852e13e068c8ac775333d7b14c9d791c435f48ae5eb119b131f3a6e884bb0e576baacc58dc5d2c19c8d862ab0b3ecf45e5b47c1a1125bb4de1959dd5f2a5b5bf385063957ead26137759c0f5afb08ed53e3cb4114791153cd3de1d08890781fc8430fc8cc404a84c5f63cdf5951514ef54856018c5799ccb1a928affb894cd23ef29fa9db4aad3b16732f58932e95432651364ad3145379f107c6bb505f18619277ccc8ea2dd34dc8eda26673b50032d8b256cb5288b3b0f9721abef5593cdaafa82904aab191887b85ce7c3a6d9b9f2c8a73dd8a0c43cd93ea539427922c9cb5af76786525794a6750f07cf53164657524487d06e584565058b9fe593e39ebdc063a47d8bfded129687c09074e3d0e43611a2882789aea3dd204d94c862390e8fcae6a4eb3d18404fea1bad4932cdfd7107f196c7d63edf21b74f67034344632eb865f9b2373908240d333512625088460c710035ea54c53978f43d259bdb44d66191c364e3a0781568646b91de2b60d8c"
        
        else:
            self.__signature = "3930c62acab89a325306c1f198127c1c54a4c2d781d0fbde44f716bbdd7171b6e5c5087c08849140e4523d7147d5ca57b7ee18e0c7bc1ee57567c4fbd89e0a3b486f08df9147c46fd6d654cdbb0ddcc8efc378484ea30789c61f8f7aa85264db44198673f4145dd4915eb54cb239bfdc9f9781a01c48eeef3887e82914afdda10858d802f1144010d5d6205d8d4eba3414d60761439cfd9b9218e3bd7e78160b035c375b1f53514659ca83539f17444f849ea8dbac033aa38ce39eb622d84f3f2775bd54ffd9ee5a5cea6b3676dd3e3ba7a99b53b12319b8537365876e82e09cdae37443e77d0b94cc3352e8d201d689604ebacfbb5d565b9dea2f094df7cc825e8030cdf93a70d05c432cc4a9bee501f2bef767d39ddd16a464b61dea16f50852e13e068c8ac775333d7b14c9d791c435f48ae5eb119b131f3a6e884bb0e576baacc58dc5d2c19c8d862ab0b3ecf45e5b47c1a1125bb4de1959dd5f2a5b5bf385063957ead26137759c0f5afb08ed53e3cb4114791153cd3de1d08890781fc8430fc8cc404a84c5f63cdf5951514ef54856018c5799ccb1a928affb894cd23ef29fa9db4aad3b16732f58932e95432651364ad3145379f107c6bb505f18619277ccc8ea2dd34dc8eda26673b50032d8b256cb5288b3b0f9721abef5593cdaafa82904aab191887b85ce7c3a6d9b9f2c8a73dd8a0c43cd93ea539427922c9cb5af76786525794a6750f07cf53164657524487d06e584565058b9fe593e39ebdc063a47d8bfded129687c09074e3d0e43611a2882789aea3dd204d94c862390e8fcae6a4eb3d18404fea1bad4932cdfd7107f196c7d63edf21b74f67034344632eb865f9b2373908240d333512625088460c710035ea54c53978f43d259bdb44d66191c364e3a0781568646b91de2b60d8c"
            self.block["Signature"] = "3930c62acab89a325306c1f198127c1c54a4c2d781d0fbde44f716bbdd7171b6e5c5087c08849140e4523d7147d5ca57b7ee18e0c7bc1ee57567c4fbd89e0a3b486f08df9147c46fd6d654cdbb0ddcc8efc378484ea30789c61f8f7aa85264db44198673f4145dd4915eb54cb239bfdc9f9781a01c48eeef3887e82914afdda10858d802f1144010d5d6205d8d4eba3414d60761439cfd9b9218e3bd7e78160b035c375b1f53514659ca83539f17444f849ea8dbac033aa38ce39eb622d84f3f2775bd54ffd9ee5a5cea6b3676dd3e3ba7a99b53b12319b8537365876e82e09cdae37443e77d0b94cc3352e8d201d689604ebacfbb5d565b9dea2f094df7cc825e8030cdf93a70d05c432cc4a9bee501f2bef767d39ddd16a464b61dea16f50852e13e068c8ac775333d7b14c9d791c435f48ae5eb119b131f3a6e884bb0e576baacc58dc5d2c19c8d862ab0b3ecf45e5b47c1a1125bb4de1959dd5f2a5b5bf385063957ead26137759c0f5afb08ed53e3cb4114791153cd3de1d08890781fc8430fc8cc404a84c5f63cdf5951514ef54856018c5799ccb1a928affb894cd23ef29fa9db4aad3b16732f58932e95432651364ad3145379f107c6bb505f18619277ccc8ea2dd34dc8eda26673b50032d8b256cb5288b3b0f9721abef5593cdaafa82904aab191887b85ce7c3a6d9b9f2c8a73dd8a0c43cd93ea539427922c9cb5af76786525794a6750f07cf53164657524487d06e584565058b9fe593e39ebdc063a47d8bfded129687c09074e3d0e43611a2882789aea3dd204d94c862390e8fcae6a4eb3d18404fea1bad4932cdfd7107f196c7d63edf21b74f67034344632eb865f9b2373908240d333512625088460c710035ea54c53978f43d259bdb44d66191c364e3a0781568646b91de2b60d8c"
        CID = self.writeBlock(IPFS_API_instance)
        return CID
        
    def writeBlock(self,ipfsHelper):
        self.block={"Data": self.__data, "Signature":self.__signature}

        self.block = json.dumps(self.block)
        CID = ipfsHelper.addfile(self.block,"BK")
        filename = Path("MinerFiles/blockchainOrderRef")
        if(not path.exists("MinerFiles/blockchainOrderRef")):
            filename.touch(exist_ok=True)  
        f=open("Blocks/"+str(CID)+".json","wb")
        f.write(self.block.encode())
        f.close()
        return str(CID)


class GenesisMetaBlock():
    def __init__(self, signer, IPFS_API_instance):
        self.__block_height = 0 
        self.__previous_meta_hash = None
        self.__previous_block_hash = None
        self.__previous_validation_hash = None
        self.__block_hash = "QmZJhTkdvVCQyPFez7XQYENxC4rYvS8tqYSzEzzneCfksK"
        self.__validation_hash = "QmTaxJNFCMj8YBHVG3AX3uACLnu24jgTBryUJMKwn9kbpP"
        self.__timestamp = 1640995202.0
        self.__miner = "QmaHx8iHzKWMx4mGsPstPFcE4xnViuzLzJQ6NvhfuoLst7"
        self.__accountState_CID = "QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW"
        self.__rewardState_CID = "QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW"
        self.__accountState = {}
        self.__rewardState = {}
        self.__committee="QmWnVdrVQqB87RPtcqhNMv4Qdi94VTvY4bB5sxfsYRBvWK"
        self.__data = {"Timestamp": self.__timestamp, "Height":self.__block_height, "Miner":self.__miner, "BlockRef":self.__block_hash, "ValidationRef":self.__validation_hash, "PreviousMetaBlock" :self.__previous_meta_hash, "PreviousBlock":self.__previous_block_hash, "PreviousValidation":self.__previous_validation_hash, "AccountState": self.__accountState_CID, "RewardState": self.__rewardState_CID, "CommitteeID":self.__committee}
        self.__signature = ""
        self.block = {}

        ## CHECK IF GENESIS MINTER IS ORIGINAL MINTER OR OTHER MINER  
        f=open("Local/KeyChain/PrivateKey.key", 'rb')
        private_Key = f.read()
        f.close()
        secretKey = base64.decodebytes(private_Key)
        self.__sign(signer, secretKey, IPFS_API_instance)
        
    def __sign(self, signer, private_key, IPFS_API_instance):
        if self.__miner == signer:
            response = input("Would you like to create a new genesis validation block?")
            if response =="YES":
                signature_tester = "test value"
                signature_tester= signature_tester.encode('utf-8')
                signature = sign(private_key, signature_tester)
                signature = signature.hex()
                
                ## CHECK THE TEST VALUE SIGNATURE CAN BE VALIDATED WITH THE PUBLIC KEY OF THE MINER OF THE REFERENCE BLOCK
                valid_signature=False
                try:
                    signature=bytes.fromhex(signature)
                    pubKeyContent= IPFS_API_instance.getContent(signer,"PK")
                    publicKey=base64.decodebytes(pubKeyContent)
                    verify(publicKey,signature_tester, signature)
                    valid_signature=True
                except:
                    valid_signature=False

                if valid_signature:
                    message = json.dumps(self.__data)
                    print(message)
                    message = message.encode('utf-8')
                    signature = sign(private_key, message)
                    self.__signature = signature.hex()
                    self.block["Signature"] = self.__signature
            else:
                self.__signature = "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"
                self.block["Signature"] = "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"
        
        else:
            self.__signature = "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"
            self.block["Signature"] = "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"
        CID = self.writeBlock(IPFS_API_instance)
        return CID
        
    def writeBlock(self,ipfsHelper):
        self.block={"Data": self.__data, "Signature":self.__signature}

        self.block = json.dumps(self.block)
        CID = ipfsHelper.addfile(self.block,"BK")
        filename = Path("MinerFiles/blockchainOrderRef")
        if(not path.exists("MinerFiles/blockchainOrderRef")):
            filename.touch(exist_ok=True)  
        f=open("Blocks/"+str(CID)+".json","wb")
        f.write(self.block.encode())
        f.close()
        return str(CID)


