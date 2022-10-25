#import ipfsapi  ### note this is depricated
import ipfshttpclient
import subprocess
import json
import os
import time
from pathlib import Path

# TODO: PIN DATA
# TODO: Configure options for Cache

class IPFSWorker:

    def __init__(self):
        self.api=None
        if not os.path.exists('Cache'):
            os.makedirs('Cache')
       
        self.tryconnect()
        
        self.CIDTracker={}
        self.jsonFileChecker("Cache/CIDTracker.json")
        f=open("Cache/CIDTracker.json","rb")
        self.CIDTracker=json.load(f)
        f.close()
        
        self.PublicKeyCache={}
        self.jsonFileChecker("Cache/PubKeyCache.json")
        f=open("Cache/PubKeyCache.json","rb")
        self.PubKeyCache=json.load(f)
        f.close()

        self.TXCache={}
        self.jsonFileChecker("Cache/TXCache.json")
        f=open("Cache/TXCache.json","rb")
        self.TXCache=json.load(f)
        f.close()

        self.BKCache={}
        self.jsonFileChecker("Cache/BKCache.json")
        f=open("Cache/BKCache.json","rb")
        self.BKXCache=json.load(f)
        f.close()

    def show_peers(self):
        return self.api.bootstrap.list()
    
    def add_peer(self,peer_multiaddress):
        self.api.bootstrap.add(peer_multiaddress)

    def remove_peer(self, peer_multiaddress):
        self.api.bootstrap.rm(peer_multiaddress)
    
    def unpin(self,CID):
        self.api.pin.rm(CID)

    def garbage_collect(self):
        self.api.repo.gc()

    def jsonFileChecker(self,filePath):
        fileName = Path(filePath)
        try:
            f=open(filePath,'r')
            f.close()
        except:
            print("FILE DOES NOT EXIST, CREATING: ", filePath)
            fileName.touch(exist_ok=True)
            f=open(fileName,'wb')
            f.write(b'{}')
            f.close()


    def updateCacheCIDTracker(self):
        content=json.dumps(self.CIDTracker)
        self.jsonFileChecker("Cache/CIDTracker.json")
        f=open("Cache/CIDTracker.json",'wb')
        f.write(content.encode('utf-8'))
        f.close()

    def addPublicKeyCache(self,CID,Content):
        if not isinstance(Content, str):
            self.PubKeyCache[CID]=Content.decode()
        else:
            self.PubKeyCache[CID]=Content
        content=json.dumps(self.PubKeyCache)
        f=open("Cache/PubKeyCache.json",'wb')
        f.write(content.encode('utf-8'))
        f.close()

    def addTXCache(self,CID,Content):
        if not isinstance(Content, str):
            self.TXCache[CID]=Content.decode()
        else:
            self.TXCache[CID]=Content
        content=json.dumps(self.TXCache)
        f=open("Cache/TXCache.json",'wb')
        f.write(content.encode('utf-8'))
        f.close()

    def addBKCache(self,CID,Content):
        if not isinstance(Content, str):
            self.BKCache[CID]=Content.decode()
        else:
            self.BKCache[CID]=Content
        content=json.dumps(self.BKCache)
        f=open("Cache/BKCache.json",'wb')
        f.write(content.encode('utf-8'))
        f.close()

    def addFileByPath(self,filePath):
        CID=self.api.add(filePath,only_hash=True)
        self.api.add(filePath)
        return CID["Hash"]
        
    def addfile(self,dataToAdd,dataType):
        filename = Path("Cache/tempdata")
        filename.touch(exist_ok=True)
        f= open(filename, 'wb')
        if isinstance(dataToAdd,str):
            f.write(dataToAdd.encode('utf-8'))
        else:
            f.write(dataToAdd)
        f.close()
        CID=self.api.add("Cache/tempdata",only_hash=True)
        
        existsInCache=self.checkCache(CID["Hash"],dataType)
    #    print("DONE CHECKING HASH", existsInCache, CID["Hash"])
        if not existsInCache:
            self.api.add("Cache/tempdata")
            if dataType=="BK":
  #              print("SELECTED AS BK")
                self.addBKCache(CID["Hash"],dataToAdd.encode('utf-8'))
            elif dataType=="TX":
  #              print("SELECTED AS TX")
                self.addTXCache(CID["Hash"],dataToAdd.encode('utf-8'))
            elif dataType=="PK":
                if isinstance(dataToAdd,str):
                    self.addPublicKeyCache(CID["Hash"],dataToAdd.encode('utf-8'))
                else:
                    self.addPublicKeyCache(CID["Hash"],dataToAdd)
            else:
                print("record not cached:", dataType)
        self.CIDTracker[CID["Hash"]]=dataType
        self.updateCacheCIDTracker()
        return CID["Hash"]


    def getCID(self, fileName):
        CID=self.api.add(fileName,only_hash=True)
     #   print("CID: ::", CID["Hash"])
        return CID["Hash"]

    def getCIDAndAdd(self, fileName,fileType):
        CID=self.api.add(fileName,only_hash=True)
        self.api.add(fileName)
        self.CIDTracker["Hash"]=fileType
        self.updateCacheCIDTracker()
        return CID["Hash"]
   
    def checkCache(self,CID,fileType):
        if CID in self.CIDTracker:
            if self.CIDTracker[CID]==fileType:
                return True
        return False

    def getContent(self,CID, dataType):
        if dataType=="PK":
            if CID in self.PubKeyCache:
             #   print("IN PK CACHE")
                return self.PubKeyCache[CID].encode('utf-8')
        elif dataType=="TX":
            if CID in self.TXCache:
                return self.TXCache[CID].encode('utf-8')

        elif dataType=="BK":
            if CID in self.BKCache:
                return self.BKCache[CID].encode('utf-8')
        try:
            content=self.api.cat(CID)
            if dataType=="PK":
                self.addPublicKeyCache(CID,content)
            elif dataType=="TX":
                self.addTXCache(CID,content)
            elif dataType=="BK":
                self.addBKCache(CID,content)

            return self.api.cat(CID)
        except ipfshttpclient.exceptions.TimeoutError:
            return ""  ### Return empty if no value found 

    def close(self):  # Call this when you're done
        self.api.close()

    def checkfile(self,CID,fileType):
        #print("IN CHECKFILE " , CID, fileType)
        if self.checkCache(CID,fileType):
            return True
        try:
            a=self.api.cat(CID)
            self.CIDTracker[CID]=fileType
            self.updateCacheCIDTracker()

       #     self.api.block.stat(CID)
            return True
        except ipfshttpclient.exceptions.TimeoutError:
            return False

    def tryconnect(self):
        # Connect to local node
        try:
            print("ESTABLISHING CONNECTION TO IPFS DAEMON")
            api = ipfshttpclient.connect(timeout=20)
            print("CONNECTION SUCCESSFUL")
            self.api=api
            
        except ipfshttpclient.exceptions.ConnectionError as ce:
            print("***** ERROR ******")
            print(str(ce))
            print()
            f=open("Config.json","r")
            jsonContent=f.read()
            jsonConfig=json.loads(jsonContent)
            f.close()    
            print(jsonConfig)
            print(jsonConfig["IPFSPath"])
         
            cmd =str(jsonConfig["IPFSPath"])+" daemon &"
            print("COMMAND: ", cmd)
            os.system(cmd) # returns the exit status
            #subprocess.Popen(cmd,close_fds=True)
           
          #  os.spawnl(os.P_NOWAIT, [cmd,'daemon'])
            time.sleep(5)
            self.tryconnect()
            


if __name__ == '__main__':
    api=IPFSWorker.tryconnect()
    res = api.add('test.txt')
    print(res)
    print("HASH:",res['Hash'])
    print(api.cat(res['Hash']))
