from multiprocessing import current_process
from secrets import compare_digest
from pqcrypto.sign.falcon_512 import generate_keypair, sign, verify
import base64
import json
import os.path
from os import path
from IPFSCallHelper import IPFSWorker
from block import MetaBlock
from transaction import Transaction
from pathlib import Path
import socket
import block

##################################################################################

private_key=None
pubAddress=None
ipfsAPIInstance=IPFSWorker()

##################################################################################
#### SERVER/GATEWAY FUNCTIONS
def get_address_from_gateway(client_socket,pubkey):
    try:
         
        message=b'tx01'
        client_socket.send(message) 
    
        data = client_socket.recv(10) 
        if data.decode('utf-8') =="ACK--tx01":
            message=pubkey.encode("utf-8")
            client_socket.send(message)
            data=client_socket.recv(46)
            ## Send address back
            return data.decode('utf-8')
    except:
            print("THE SERVER  IS DOWN")
    client_socket.close()

##################################################################################
### CONFIG FINCTIONS

def create_config():
    print("Initial Config Creation")
    config = {}
    valid_response = False
    while valid_response != True:
        print()
        print("Please Select from one of the following options: ")
        print("1: Use Local Node")
        print("2: Connect to Remote Gateway")
        response = input(">>> ")
        if response == "1" or response =="2":
            valid_response = True
        
    if response == "1":
        config["use_gateway"] = False 
        config["gateway_address"] = "127.0.0.1"
    else:
        result = input("Please enter the IP address of the gateway you would like to use: ")
        config["use_gateway"] = True
        config["gateway_address"] = result
        
    config["gateway_port"] = 8101
    config["wallet_address"]=""
    save_config(config)
    return config

def save_config(config):
    content = json.dumps(config)
    f = open("WalletConfig.json", "w")
    f.write(content)
    f.close()    
    
def load_config():
    try: 
        f = open("WalletConfig.json", "r")
        content = f.read()
        f.close()
        config = json.loads(content)
        return config
    except: 
        print("Failed to Load Config")
        return None

def handle_invalid_config():
    valid_input = False
    while valid_input == False:
        print("Invalid Config Values Found")
        result = input("Would you like to reinitialize the config file (Y/N)? >>> ")
        if result == "Y" or result == "N":
            valid_input  = True
    if result == "Y":
        print("Running Process To Recreate Config File")
        create_config()
        return False
    else:
        print("WARNING:  Config File Is Invalid. Wallet Will Not Function Until Errors Are Resolved. Exiting Process")
        return False

def validate_config(config):
    print("VALIDATING CONFIG", config)
    use_gateway_valid = False
    gateway_address_valid = False
    gateway_port_valid = False
    address_valid = False

### Check if use_gateway field is valid
    try:
        print("Validating use_gateway value")
        current_value = config["use_gateway"]
        if current_value == True or current_value == False:
            use_gateway_valid = True
        else:
            print("use_gateway value is invalid")
    except:
        handle_invalid_config()
### Check if Gateway IP Address is not empty
    try: 
        print("Validating gateway_address value")
        current_value = config["gateway_address"]
        gateway_address_valid = True
    except:
        handle_invalid_config()

### Check if Gateway IP Port is valid
    try: 
        print("Validating gateway_port value")
        current_value = config["gateway_port"]
        if int(current_value) > 0 and int(current_value) < 65535:
            gateway_port_valid = True
        else:
            print("Invalid Port Number")
    except:
        handle_invalid_config()

### Check if Address is Valid
    try: 
        print("Validating wallet_address")
        current_value = config["wallet_address"]
        if len(current_value) == 41:
            address_valid = True
        else: 
            print("Possible invalid address")
       
    except:
        handle_invalid_config()

    return use_gateway_valid & gateway_address_valid & gateway_port_valid & address_valid

def update_config():
    print("Update Config")
    config = load_config()
    print()
    print("CURRENT CONFIG VALUES: ", config)
    print
    valid_response = False
    while valid_response != True:
        print()
        print("Which field would you like to update: ")
        print("1: Toggle Using External or Local Gateway")
        print("2: Update Gateway Address")
        print("3: Update Gateway Port")
        print("4: Manually enter your Wallet Address")

        response = input(">>> ")
        if response == "1" or response =="2" or response =="3" or response =="4":
            valid_response = True
    
    if response =="1":
        current_value = config["use_gateway"]
        print("Current value: " + str(current_value))
        valid_response = False
        while valid_response ==False:
            print("Please Enter T to use a remote gateway or F to use a local one")
            result = input(">>> ")
            if result =="T" or result =="F":
                valid_response = True
        if result == " T":
            config["use_gateway"] = True
            config["gateway_address"] = "127.0.0.1"
        else: 
            result = input("Please enter the IP address of the gateway you would like to use: ")
            config["use_gateway"] = True
            config["gateway_address"] = result
    elif response =="2":
        current_value = config["gateway_address"]
        print("Current value " + str(current_value))
        result = input("Please enter the IP address of the gateway you would like to use: ")
        config["gateway_address"] = result
    elif response =="3":
        current_value = config["gateway_port"]
        print("Current value " + str(current_value))
        valid_response == False
        while valid_response == False:

            result = input("Please enter the Port of the gateway you would like to use: ")
            if int(result) < 1 or int(result) > 65535:
                print("Invalid Port Number")
            else:
                valid_response = True
        config["gateway_port"] = result

    elif response =="4":
        print("NOTICE: Address must match the CID value of the public key stored on IPFS.  Entering a CID value that is not linked to your public key will result in failed transactions")
        print("It is recommended the users do not manually update their address")
        valid_response == False
        while valid_response == False:
            result = input("Would you like to continue? (Y/N )>>> ")
            if result =="Y" or result == "N":
                valid_response = True
        if result == "N":
            print("Aborting address update")
        else:
            valid_response == False
            while valid_response == False:
                result = input("Please enter your address >>> ")
                if len(result) != 41:
                    print("Invalid Address Format")
                else:
                    config["wallet_address"] = result
    
    save_config(config)

def setup_gateway_connection(address, port):
    server=(address,port)
    client_socket=socket.socket() 
    client_socket.settimeout(15)
    client_socket.connect(server)
    return client_socket


def getKeys(keyExists=True):
    if keyExists:
        print("KEY EXISTS..LOADING")
        private_key, pubAddress=load_key()
    else:
        print("KEY DOES NOT EXIST.. ")
        private_key,pubAddress=save_key()
       
    return private_key,pubAddress

def save_key():
    ## GENERATE NEW PRIVATE KEY AND SAVE TO LOCAL KEY CHAIN FOLDER
    public_key, secret_key = generate_keypair()
    if not os.path.exists('Local/KeyChain'):
        os.makedirs('Local/KeyChain')
    filename = Path("Local/KeyChain/PrivateKey.key")
    filename.touch(exist_ok=True)
    ## CONVERT KEY BYTES TO BASE64 THEN TO ASCII STRING
    b64SK=base64.encodebytes(secret_key)
    print("BASE 64 ",b64SK)
    print()
    b64PubKey=base64.encodebytes(public_key)
    asciiSK=b64SK.decode('utf-8')

    asciiPubKey=b64PubKey.decode('utf-8')
    f= open(filename, 'wb')
    f.write(asciiSK.encode('utf-8'))
    f.close()

    filename = Path("Local/KeyChain/PublicKey.key")
    filename.touch(exist_ok=True)
    f= open(filename, 'wb')
    f.write(asciiPubKey.encode('utf-8'))
    f.close()

    ## UPLOAD THE PUBLIC KEY FILE TO IPFS
    pubAddress=ipfsAPIInstance.addfile(asciiPubKey,"PK")
    return secret_key,pubAddress
   
def load_key():
    ### KEYS ARE STORED AS ASCII
    ### CONVERT TO BYTES(SHOULD BE BASE 64) THEN CONVERT FROM BASE64 BYTES TO GET KEY VALUE BYTES
    with open("Local/KeyChain/PrivateKey.key", 'rb') as privKey_in:
        private_KeyASCII = privKey_in.read()
        secret_key=base64.decodebytes(private_KeyASCII)

    with open("Local/KeyChain/PublicKey.key", 'rb') as pubKey_in:
        pubASCII = pubKey_in.read()      
        
    ## UPLOAD THE PUBLIC KEY FILE TO IPFS
 #   pubAddress= ipfsAPIInstance.api.add("Local/KeyChain/PublicKey.key",only_hash=True)
    pubAddress=ipfsAPIInstance.addfile(pubASCII,"PK")
    return secret_key ,pubAddress

def getTXDetails():
    ToAddres=input("Enter The Address You Want To Send To")
    Amount=float(input("Enter the Amount"))
    return ToAddres,Amount

def createTransaction(myAddress,privateKey):
    To,Amount=getTXDetails()
    tx=Transaction(To,myAddress, Amount)
    print("PREPARING TO SIGN")
    print("TYPE OF PRIVKEY: ",type(privateKey))
    cid=tx.sign(privateKey,ipfsAPIInstance)
    sendTXToChain(cid)
   
def sendTXToChain(txCID):
    print("SENDING TX", txCID)
    success=False
    f = open("./conf/nodes.conf", "r")
    content_list = f.readline()
    f.close()
    addr=content_list.split(',')
    server=(str(addr[0]), int(addr[1].replace('\n','')))
    s=socket.socket()
    print("trying to connect to server",server)
    s.connect(server)
    
    message='2tx'
    try:
        s.send(message.encode('UTF-8')) 
        data = s.recv(10) 
        if data.decode('utf-8') =="ACK----2tx":
            message=str(txCID).encode("utf-8")
            s.send(message)
            data=s.recv(10)
            print("RECEIVED ",data.decode("utf-8"))
            success=True
    except:
        print("THE SERVER "+ str(server) + " IS DOWN")
        success=False
    
    s.close()
    return success	


def startup():
    filename = Path("blocklog.txt")
    filename.touch(exist_ok=True)
    filename = Path("transactionlog.txt")
    filename.touch(exist_ok=True)
    load_config()
    ### Start up load keys
    private_key,myAddress=getKeys(path.exists("Local/KeyChain/PrivateKey.key"))
    return private_key,myAddress

def getBalance(address):
    ### TODO: Error handle if config not set up or no other nodes known. 
    f = open("./conf/comitteeNodes.json", "r")
    content_list = f.read()
    f.close()
    content = json.loads(content_list)
    f.close()
    for m in content["members"]:
        if m["address"] == address:
            addr=m["server"].split(',')
            
  
    server=(str(addr[0]), int(addr[1].replace('\n','')))
    s=socket.socket()
    s.settimeout(15)
    s.connect(server)
    
    s.send(b'1qy')
    resp=s.recv(10)
    if resp.decode('utf-8') =="ACK----1qy":
        pass
    else:
        print("FAILED TO GET CORRECT RESPONSE")
        s.close()
        return 0
    
    s.send(b'LAST---BLK')
    myblock=s.recv(46)
    print(myblock)
    s.send(b"BLK---RECV")
    resp=s.recv(10)
    if resp.decode('utf-8') =="ACK---DONE":
        pass
    else:
        print("FAILED TO GET CORRECT RESPONSE")
        s.close()
        return 0

    blockString=myblock.decode('utf-8')
    latest_block :MetaBlock= block.create_metablock_from_CID(ipfsAPIInstance, blockString)
    account_state = latest_block.get_account_state()
    bal = account_state[address]
    try:
        return bal
    except:
        print("INVALID ACCOUNT")
        return 0    

    
if __name__ == "__main__":
  #  print("ESTABLISHING CONNECTION")
    ## Start the P2P Server as a background process
   ## command="python NonBlocking.py"
  ##  subprocess.Popen(command,shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE)
    #subprocess.Popen(command,shell=True,creationflags=subprocess.STARTF_USESHOWWINDOW)
    
    #
    config = load_config()
    if config == None:
        print("Running Code to Create Config File")
        config = create_config()
    valid_config = validate_config(config)
    print("VALID CONFIG ", valid_config)
    if valid_config == False:
        print("Config File Has Invalid Values. Executing Process To Update Config Values")
        update_config()
    

    privateKey,myAddress=startup()
    getInput=True
    print()
    print("My Address: ", myAddress)
    print("Choose an Option")
    print("1) Check My Balance")
    print("2) Check Other Balance (Other Miner)")
    print("3) Make Transfer")
    print("4) Quit")


    while getInput:

        result=input("->")
        if(result=="1"):
           myBalance= getBalance(myAddress)
           print("BALANCE: ", myBalance)
        elif(result=="2"):
           address=input("Please Enter An Account")
           balance= getBalance(address)
           print("BALANCE: ", balance)
        elif(result=="3"):
            createTransaction(myAddress,privateKey)
        elif(result=="4"):
            getInput=False
        else:
            print("Invalid Selection")
            print()
            print("My Address: ", myAddress)
            print("Choose an Option")
            print("1) Check My Balance")
            print("2) Check Other Balance (Other Miner)")
            print("3) Make Transfer")
            print("4) Quit")


##    subprocess.call(['taskkill', '/F', '/T', '/PID', str(os.getpid())])

