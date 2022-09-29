#from cryptography.hazmat.primitives import serialization, hashes
from pqcrypto.sign.falcon_512 import sign, verify
import json
import base64
#from IPFSCallHelper import IPFSWorker
from pathlib import Path

def loadFromFile(CID, ipfsAPIInstance):
#    print("CID: ", CID)
    f=open("TX/"+CID,"wb")
    f.write(ipfsAPIInstance.getContent(CID,"TX"))
    f.close()
    
    f=open("TX/"+CID,"rb")
    jsonData=json.load(f)
    newTx=Transaction(jsonData["To"],jsonData["From"],jsonData["Amount"])
    newTx.sig=jsonData["signature"]
    newTx.full["signature"]=jsonData["signature"]
   
    return newTx

def createCoinbaseTX(address,blockNum):
    print("IN CREATE COINBASE: ", address,blockNum)
    tx=Transaction(address,"COINBASE_"+str(blockNum),10)
    return tx


class Transaction():

    def __init__(self, To,From,Amount):
        self.header={}
        self.full={}
        self.header["To"]=To
        self.header["From"]=From
        self.header["Amount"]=Amount
        self.sig=''
        self.full["To"]=To
        self.full["From"]=From
        self.full["Amount"]=Amount
        

    def sign(self,privKey,ipfsAPIInstance):
        message=json.dumps(self.header)
        message=message.encode('utf-8')
        signature = sign(privKey,message)
        self.sig=signature.hex()
        self.full["signature"]=self.sig
        filname=self.writeToFile(ipfsAPIInstance)
        return filname

    def writeToFile(self,ipfsAPIInstance):
        content=json.dumps(self.full)
        filename = Path("TX/TempTX.json")
        filename.touch(exist_ok=True)
        
        f= open(filename, 'wb')
        f.write(content.encode())
        f.close()
    #    ipfsAPIInstance=IPFSWorker()

        CID=ipfsAPIInstance.api.add("TX/TempTX.json",only_hash=True)
        print("TX FILE NAME",CID["Hash"])
        filename = Path("TX/"+CID["Hash"]+".json")
        filename.touch(exist_ok=True)
        f=open(filename,"wb")
        f.write(content.encode())
        f.close()
        ipfsAPIInstance.api.add(filename)
    #    ipfsAPIInstance.close()
        return CID["Hash"]
    

    def validateNumericField(self,value):
        if(str(value).isnumeric):
            if(float(value)>=0):
                return True
        return False

    def validateAddressExists(self,address,ipfsAPIInstance):
   #     ipfsAPIInstance=IPFSWorker()
        return ipfsAPIInstance.checkfile(address,"PK")

## TODO: Dynamic way to get expected miner
    def validate_miner(self,miner,expectedMiner):
        print("VALIDATING MINER")
        print(self.full["To"], miner, expectedMiner)
        return miner.strip()==expectedMiner.strip() and self.full["To"].strip()==miner.strip()

    def validateCoinbase(self,address,blockNum,ipfsAPIInstance,expectedMiner):  
        print("VALIDATING COINBASE")
        expectedMiner=expectedMiner.strip()
        ##validTo=self.validateAddressExists(self.full["To"],ipfsAPIInstance)
        print(" ADDRESS / EXPECTED MINER  ", address,expectedMiner)
        validMiner=self.validate_miner(address,expectedMiner)
        print("VALID MINNER: ", validMiner)
        validAmount=self.full["Amount"]==10.0
        fullFromString="COINBASE_"+str(blockNum)
        validFrom=self.full["From"]==fullFromString

        validSignature=False
        try:
            signature=bytes.fromhex(self.sig)
            content=json.dumps(self.header)
 #           print("CONTENT",content)
            content=content.encode('utf-8')
            pubkey=self.loadPublicKey(ipfsAPIInstance,True)
            
            verify(pubkey,content, signature)
            validSignature=True
        except:
            print("SIGNATURE VALIDATION ERROR")
            validSignature=False

        if validMiner and validFrom and validSignature and validAmount:
            print("VALID COINBASE")
            return True
        print("INVALID COINBASE")
        return False
    
    def loadPublicKey(self,ipfsAPIInstance,isCoinbase=False):
      #  ipfsAPIInstance=IPFSWorker()
        if isCoinbase:
              pubKeyContent= ipfsAPIInstance.getContent(self.header["To"],"PK")
               
        else:
              pubKeyContent= ipfsAPIInstance.getContent(self.header["From"],"PK")
        publicKey=base64.decodebytes(pubKeyContent)

      #  loadedPubKey=load_pem_public_key(pubKeyContent,backend=default_backend())   
       # return loadedPubKey
        return publicKey


    def validate(self,pubkey,ipfsAPIInstance):

        validTo=self.validateAddressExists(self.full["To"],ipfsAPIInstance)
 ##       print("VALID TO")
        validFrom=self.validateAddressExists(self.full["From"],ipfsAPIInstance)
 ##       print("VALID FROM")
        validAmount=self.validateNumericField(self.full["Amount"])
 ##       print("NUMERIC AMOUNT")
        validSignature=False
        try:
            signature=bytes.fromhex(self.full["signature"])
            content=json.dumps(self.header)
        #    print("CONTENT",content)
            content=content.encode('utf-8')
            verify(pubkey,content, signature)
           # pubkey.verify( signature, content, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
            validSignature=True
 #           print("VALID SIG")
        except:
            validSignature=False
            print("AN ERROR OCCURRED")
  #      except InvalidSignature:
  #          validSignature=False
 #           print("INVALID SIG")
        if validTo and validFrom and validSignature and validAmount:
            return True
        return False
