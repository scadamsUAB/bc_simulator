
from abc import ABCMeta
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_private_key,load_pem_public_key

from os import path,kill
from threading import Thread
from IPFSCallHelper import IPFSWorker
from Miner import miner
import Miner

import ipfshttpclient
import subprocess
import json
import os
import time
import transaction
from transaction import Transaction
import hashlib
#import psutil
#import signal

def TestNonBlocking():

    command="NonBlocking.py"
    #a=subprocess.Popen(command)
    a=subprocess.Popen(command,shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE)
    print(a.pid)
    x=2
    for i in range(0,50000):
        if i%2==0:
            x=x+1
            print(x)
    print(a.pid,os.getpid())

    subprocess.call(['taskkill', '/F', '/T', '/PID', str(os.getpid())])
#print("*")
#subprocess.call(['taskkill', '/F', '/T', '/PID', str(a.pid)])

def TestWorker():
    tester=IPFSWorker()
    #.tryconnect()
    while tester.api==None:
        time.sleep(1)
        print("waiting for IPFS Startup to Complete...")
        print(tester.test)
    res = tester.api.add('test.txt')
    print("***")
    res2=tester.api.add('test.txt',only_hash=True)
    print(res)
    print(res2)
    print("HASH:",res['Hash'])
    
    print("CAT:", tester.api.cat(res['Hash']))    


    print("KEY TESTING")
    print()

    myKey = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
    pem = myKey.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
    with open("keyTest", 'wb') as pem_out:
        pem_out.write(pem)
    pubkey=myKey.public_key()
    pub=pubkey.public_bytes( encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)  
    f=open("PubTest","wb")
    f.write(pub)
    f.close()

    print("TESTING IPFS WITH KEY")
    res = tester.api.add('PubTest')
    print("***")
    res2=tester.api.add('PubTest',only_hash=True)
    print("FULL PUSH",res)
    print("PART PUSH",res2)
    print("HASH:",res['Hash'])
    x=tester.api.cat(res['Hash']) 


    print()
    print("******")
    print("TESTING PULLING FILE THAT DOES EXIST")

    testfileID="QmRXchq8giK7wiNAq4pLpZVoGSiLhGUxyEFauycTVwBL1w"
    if tester.checkfile(testfileID):
        testFile=tester.api.cat(testfileID)
        print(testFile)
    else:
        print("FILE DOES NOT EXIST")

    print()
    print("******")
    print("TESTING PULLING FILE THAT DOES NOT EXIST")
    try:
        testfileID="QmRXchq765K7wiNAq4pLpZVoGSiGPGUxyEFwwycvVwbL1w"
   # testFile=tester.api.block.get(testfileID)
    #print(testFile)
        print(tester.api.block.stat(testfileID))
    except: 
        print("File Not Found in Timeout Period")

    text=b"abcd"
    signature=myKey.sign(data=text,padding=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), algorithm=hashes.SHA256() )
        
    
    print("***************************************")

    print()
    f=open("PubTest2","rb")
    y=f.read()
    print("pulled from local file")
    print(y)

    print()
    print("Value pulled from CID using CAT and storing in variable")
    print(x)
    print(x.decode())
    #print("CAT:", tester.api.cat(res['Hash'])) 
    
    abc=   tester.api.cat(res['Hash'])


    f=open("PubTest2","wb")
    f.write(abc)
    f.close()


    print("CHECKING KEY LOADED")
    loadedPubKey=load_pem_public_key(x,backend=default_backend())   
    try:
        loadedPubKey.verify( signature, text, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        print("VALID")
    except InvalidSignature:
        print("INVALID")
        return False
    
    print("CLOSING INSTANCE")
    tester.close()

print("STARTING TEST WORKER")
#TestWorker()

#tester=IPFSWorker()
#tester2=IPFSWorker()
#tester3=IPFSWorker()
#print(tester.api.add("test2.txt",only_hash=True))
#tester.api.add("test2.txt")

#print(tester3.checkfile("QmXCdaS6GtL9zwoY4ZN1mmuVvG1BrVAgRefndfUX9dQcP9"))
#f=open("test3.txt","wb")
#f.write(tester.api.cat("QmXCdaS6GtL9zwoY4ZN1mmuVvG1BrVAgRefndfUX9dQcP9"))
#f.close()

#QmNUkt8Ni6tZpPFJK3gpcGno5rwEVgxu4FmGTT7a6XXHFX
#print(tester.api.add("69f5cad94435a066bfe670f18f618167a5ce107d10528a1a6ae13e3ec5077559",only_hash=True))
#tester.api.add("69f5cad94435a066bfe670f18f618167a5ce107d10528a1a6ae13e3ec5077559")

#f=open("file2","wb")
#f.write(tester.api.cat("QmNUkt8Ni6tZpPFJK3gpcGno5rwEVgxu4FmGTT7a6XXHFX"))
#f.close()
        
#f=open("file2","rb")
#x=json.load(f)
#print(x)
#print(x["To"])
#print("CALLING TRANSACTION STATIC METHOD")
#a=transaction.loadFromFile("QmNUkt8Ni6tZpPFJK3gpcGno5rwEVgxu4FmGTT7a6XXHFX")
#print(a.sig)
#tester.close()
#tester2.close()
#tester3.close()

#var1='abc'
#var2='123'
#var3=234
#print(str(var1).isnumeric())
#print(str(var2).isnumeric())
#print(str(var3).isnumeric())

#print(float(var2))
#print(float(var3))
#print(float(var3)>=234.0)
def altDataStreamTest():
    
    #ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb
    f=open("testalt1.txt","rb")
    a=f.read()
    print(a)
    f.close()

    b=hashlib.sha256(a).hexdigest()
    #e2d0fe1585a63ec6009c8016ff8dda8b17719a637405a4e23c0ff81339148249
    print(b)

    f=open("testalt1.txt:alt","rb")
    a=f.read()
    print(a)
    f.close()

def MinerTests():
    testMiner=miner()
    a=Miner.GetLatestTx()
    print(a)


#MinerTests()
#TestWorker()
    def JSONTesting():
        print()
        print("**************")
        print("Testing ability to handle json from cid")
        tester=IPFSWorker()
        hashvalue=(tester.api.add("testbk.json",only_hash=True))
        tester.api.add("testbk.json")
        print("JSON FILE ADDED ", hashvalue["Hash"])
        a=tester.api.cat(hashvalue["Hash"])
        print()
        print("Value pulled from CAT")
        print(a)
        ajson=json.loads(a.decode())
        print("HEADER:")
        print(ajson["Header"])
        print("HEADER HEIGHT")
        print(ajson["Header"]["Height"])

        y=tester.api.cat(hashvalue["Hash"])
        print(y)

def LineReadTest():
    val=2
    f=open("transactionlog.txt","r")
    lines=f.readlines()
    f.close()
    for x in range(val,len(lines)):
        print(lines[x])
    

#f = open("./conf/comitteeNodes.json", "r")
#raw_list = f.read()
#f.close()
#print(raw_list)
#committee_members=json.loads(raw_list)
#print(committee_members)

#abc = ("1.2.3.4.", 8000)
#print(abc)
#print(abc[0])
#altDataStreamTest()
#LineReadTest()

newIpfsAPIInstance=IPFSWorker()
#print("RUNNING GARBAGE COLLECTION")
#newIpfsAPIInstance.garbage_collect()
#print("GARBAGE COLLECTION COMPLETE")
#print()

peers = newIpfsAPIInstance.show_peers()
print(peers)
test_peer ="/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
new_peer ="/ip4/3.13.252.251/tcp/4001/p2p/12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY"
print(new_peer)
print()
newIpfsAPIInstance.remove_peer(test_peer)
peers = newIpfsAPIInstance.show_peers()
print(peers)
print()
newIpfsAPIInstance.add_peer(test_peer)
peers = newIpfsAPIInstance.show_peers()
print(peers)

print()
newIpfsAPIInstance.add_peer(new_peer)
peers = newIpfsAPIInstance.show_peers()
print(peers)

#x = newIpfsAPIInstance.getContent("QmZdA7fQZS22wXmuwmVdZ4PaQbAgdWJbYLcef7vpjimc61","NA")
#print(x)
#print()

#newIpfsAPIInstance.remove_peer(new_peer)
#peers = newIpfsAPIInstance.show_peers()
#print(peers)
#print()

#print("STARTING UNPIN")
#newIpfsAPIInstance.unpin("QmZdA7fQZS22wXmuwmVdZ4PaQbAgdWJbYLcef7vpjimc61")
#print("UNPINNED")
#print()
x = newIpfsAPIInstance.getContent("QmZdA7fQZS22wXmuwmVdZ4PaQbAgdWJbYLcef7vpjimc61","NA")
print(x)
print()


print()
print()
print("TESTING COMMITTEE SETUP")
committee_id="QmWnVdrVQqB87RPtcqhNMv4Qdi94VTvY4bB5sxfsYRBvWK"
committee_content = newIpfsAPIInstance.getContent(committee_id,"NA")
committee_json = json.loads(committee_content)
print("COMMITTEE JSON",committee_json)
members_list = committee_json["members"]
print()
print("MEMBERS LIST" , members_list)
for i in range(0,len(members_list)):
    print()
    print(i)
    #/ip4/3.13.252.251/tcp/4001/p2p/12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY
    member_json = members_list[i]
    print("MEMBER JSON: ", i, member_json)
    ip_address = member_json["server"].split(",")[0]
    connection_string = "/ip4/" + ip_address + "/tcp/4001/p2p/" + member_json["ipfs"]
    print("CONNECTION STRING" )
    print(connection_string)
    newIpfsAPIInstance.add_peer(connection_string)


